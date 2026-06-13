import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, random_split
import torch.nn.functional as F
from sentence_transformers import SentenceTransformer, models
import numpy as np
import pandas as pd
import time
import pathlib

device = 'cuda' if torch.cuda.is_available() else 'cpu'
print(f"Running on: {device}")

current_file_dir = pathlib.Path(__file__).parent.resolve()
print(f"Current Directory: {current_file_dir}")
og_model_name = 'BAAI/bge-base-en-v1.5'
inter_dims = 364
target_dims = 6
physical_batch_size = 256
accumulation_steps = 4  
num_epochs = 50

base_model = SentenceTransformer(og_model_name, device=device)

og_dims = base_model.get_sentence_embedding_dimension()

dense_layer_1 = models.Dense(
    in_features=og_dims,
    out_features=inter_dims, 
    activation_function=torch.nn.GELU()
)

dense_layer_2 = models.Dense(
    in_features=inter_dims, 
    out_features=target_dims
)

class STModuleWrapper(nn.Module):
    def __init__(self, module):
        super().__init__()
        self.module = module

    def forward(self, features):
        emb = features['sentence_embedding']
        emb = self.module(emb)
        features.update({'sentence_embedding': emb})
        return features
    
norm_layer = STModuleWrapper(nn.LayerNorm(inter_dims))

modules_with_reduction = [base_model] + [dense_layer_1, norm_layer, dense_layer_2]
model = SentenceTransformer(modules=modules_with_reduction)
model.to(device)

parent_dir = current_file_dir.parent
training_data = pd.read_csv(parent_dir / 'mixed_questions_total_train_dataset.csv')
validation_data = pd.read_csv(parent_dir / 'mixed_questions_total_val_dataset.csv')
test_data = pd.read_csv(parent_dir / 'mixed_questions_total_test_dataset.csv')

for param in model[0].parameters():
    param.requires_grad = False

import torch
import torch.nn as nn
import torch.nn.functional as F

class LogCoshLoss(nn.Module):
    def __init__(self):
        super(LogCoshLoss, self).__init__()

    def forward(self, pred, target):
        diff = pred - target
        # STABILITY FIX: Pure torch.cosh overflows for diff > 88. 
        # Use Softplus approximation for large values.
        return torch.mean(diff + F.softplus(-2. * diff) - torch.log(torch.tensor(2.)))

class CosineSimilarityLoss(nn.Module):
    def __init__(self):
        super(CosineSimilarityLoss, self).__init__()

    def forward(self, pred, target):
        # DIMENSION FIX: Explicitly specify dim=1 to compare vectors row-by-row
        cosine_sim = F.cosine_similarity(pred, target, dim=1)
        return torch.mean(1 - cosine_sim)

class SupCRLoss(nn.Module):
    def __init__(self, temperature=0.1, threshold=0.3): # Tuned defaults
        super(SupCRLoss, self).__init__()
        self.temperature = temperature
        self.threshold = threshold 

    def forward(self, features, targets):
        """
        features: [batch_size, dim] (Your predicted vectors)
        targets:  [batch_size, dim] (Your ground truth vectors)
        """
        # Ensure features are normalized for contrastive learning
        features = F.normalize(features, dim=1)
        
        device = features.device
        batch_size = features.shape[0]

        # --- BUG FIX START ---
        # The original code flattened targets to (Batch*Dim, 1). 
        # We must keep them as (Batch, Dim) to calculate vector-to-vector distance.
        if len(targets.shape) == 1:
            targets = targets.view(-1, 1)
        # --- BUG FIX END ---

        # 1. Create "Positive" Mask based on Vector Distance (L1 or L2)
        # cdist computes distance between every pair of vectors in the batch
        # p=1 (Manhattan) is often robust for 'feature degrees'
        target_dist = torch.cdist(targets, targets, p=1) 
        
        # Mask: 1 if vector_i is close to vector_j
        mask = torch.le(target_dist, self.threshold).float().to(device)

        # Remove self-contrast (diagonals)
        logits_mask = torch.scatter(
            torch.ones_like(mask),
            1,
            torch.arange(batch_size).view(-1, 1).to(device),
            0
        )
        mask = mask * logits_mask

        # 2. Compute Contrastive Logits
        anchor_dot_contrast = torch.div(
            torch.matmul(features, features.T),
            self.temperature
        )
        
        # Stability shift
        logits_max, _ = torch.max(anchor_dot_contrast, dim=1, keepdim=True)
        logits = anchor_dot_contrast - logits_max.detach()

        # 3. Compute Loss
        exp_logits = torch.exp(logits) * logits_mask
        log_prob = logits - torch.log(exp_logits.sum(1, keepdim=True) + 1e-6)

        # Calculate Mean of Positives
        mask_pos_pairs = mask.sum(1)
        # Avoid division by zero for anchors with no positives
        mask_pos_pairs = torch.where(mask_pos_pairs < 1e-6, 1.0, mask_pos_pairs)
        
        mean_log_prob_pos = (mask * log_prob).sum(1) / mask_pos_pairs

        # If an anchor has NO positives, we don't want it to contribute 0 to the mean, 
        # we want to ignore it or it drags loss down artificially.
        # But standard implementation often just leaves it as is.
        loss = - mean_log_prob_pos
        return loss.mean()

class CompositeLoss(nn.Module):
    def __init__(self, alpha=1.0, beta=1.0, gamma=0.1):
        super(CompositeLoss, self).__init__()
        self.alpha = alpha   # Weight for Magnitude (LogCosh)
        self.beta = beta     # Weight for Direction (Cosine)
        self.gamma = gamma   # Weight for Clustering (SupCR)
        
        self.log_cosh = LogCoshLoss()
        self.cosine = CosineSimilarityLoss()
        self.supcr = SupCRLoss(threshold=0.5) # Needs tuning based on your data scale

    def forward(self, pred, target):
        loss_mag = self.log_cosh(pred, target)
        loss_dir = self.cosine(pred, target)
        
        # SupCR usually works on the latent features, but here we enforce
        # clustering on the OUTPUT vectors themselves.
        loss_clust = self.supcr(pred, target)
        
        return (self.alpha * loss_mag) + (self.beta * loss_dir) + (self.gamma * loss_clust)

loss_fn = CompositeLoss()
optimizer = torch.optim.AdamW(filter(lambda p: p.requires_grad, model.parameters()), lr=2e-5)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.5, patience=3)
scaler = torch.amp.GradScaler() 

class TextVectorDataset(Dataset):
    def __init__(self, dataframe):
        # We assume the first column is text, and the last 6 are the vector
        self.texts = dataframe.iloc[:, 0].values
        # Get the last 6 columns and convert to float32 (standard for PyTorch)
        self.vectors = dataframe.iloc[:, -6:].values.astype('float32')

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        vector = self.vectors[idx]
        return text, vector

# Initialize Datasets
train_ds = TextVectorDataset(training_data)
val_ds = TextVectorDataset(validation_data)

train_loader = DataLoader(train_ds, batch_size=physical_batch_size, shuffle=True)
val_loader = DataLoader(val_ds, batch_size=physical_batch_size, shuffle=False)
output_dir = parent_dir / 'models'
output_dir.mkdir(parents=True, exist_ok=True)

def train_model(model, train_loader, val_loader, optimizer, loss_fn, num_epochs):
    model.train() # Set model to training mode
    best_val_loss = float('inf')
    
    for epoch in range(num_epochs):
        start_time = time.time()
        total_train_loss = 0
        optimizer.zero_grad() # Reset gradients at start of epoch
        
        print(f"--- Epoch {epoch+1}/{num_epochs} ---")
        
        for step, (texts, target_vectors) in enumerate(train_loader):
            
            # 1. Prepare Inputs
            # SentenceTransformer expects a specific input format (tokenized dictionary)
            inputs = model.tokenize(texts)
            
            # Move inputs to GPU
            inputs = {key: val.to(device) for key, val in inputs.items()}
            target_vectors = target_vectors.to(device)
            
            # 2. Mixed Precision Forward Pass
            with torch.amp.autocast(device): # Use 'cpu' if not using cuda
                # The model returns a dictionary. We want the embedding output.
                output = model(inputs)
                prediction_vectors = output['sentence_embedding']
                
                loss = loss_fn(prediction_vectors, target_vectors)
                loss_log_cosh = loss_fn.log_cosh(prediction_vectors, target_vectors)
                loss_cos = loss_fn.cosine(prediction_vectors, target_vectors)
                loss_supcr = loss_fn.supcr(prediction_vectors, target_vectors)
                # Print only once per epoch to check scales
                if step == 0:
                    print(f"Initial Loss Components - LogCosh: {loss_log_cosh.item():.4f}, Cosine: {loss_cos.item():.4f}, SupCR: {loss_supcr.item():.4f}")

                # Normalize loss for gradient accumulation
                loss = loss / accumulation_steps

            # 4. Backward Pass (Scale the loss)
            scaler.scale(loss).backward()
            
            total_train_loss += loss.item() * accumulation_steps # Track actual loss

            # 5. Optimizer Step (Gradient Accumulation)
            if (step + 1) % accumulation_steps == 0:
                scaler.step(optimizer)
                scaler.update()
                optimizer.zero_grad()
        
        # --- Validation Step ---
        model.eval() 
        total_val_loss = 0
        
        with torch.no_grad():
            for texts, target_vectors in val_loader:
                inputs = model.tokenize(texts)
                inputs = {k: v.to(device) for k, v in inputs.items()}
                target_vectors = target_vectors.to(device)
                
                # Validation also benefits from autocast for speed
                with torch.amp.autocast(device_type=device):
                    output = model(inputs)
                    pred = output['sentence_embedding']
                    loss = loss_fn(pred, target_vectors)
                
                total_val_loss += loss.item()

        # --- AFTER the loop: Epoch-level logic ---
        avg_val_loss = total_val_loss / len(val_loader)
        
        # 1. Update the learning rate based on the average validation loss
        scheduler.step(avg_val_loss)
        
        model.train() # Reset to train mode
        
        avg_train_loss = total_train_loss / len(train_loader)
        
        print(f"Epoch {epoch+1} Complete. Train Loss: {avg_train_loss} | Val Loss: {avg_val_loss}")

        if avg_val_loss < best_val_loss:
            best_val_loss = avg_val_loss
    
            # 1. Get the names of the parameters that are actually trainable
            #    (We look at model.named_parameters(), not the state_dict values)
            trainable_keys = [name for name, param in model.named_parameters() if param.requires_grad]
            
            # 2. Filter the state_dict to only include those keys
            trainable_state = {k: v for k, v in model.state_dict().items() if k in trainable_keys}
            
            torch.save(trainable_state, output_dir / "best_model.pth")
            print(f"New Best Model Saved (Loss: {best_val_loss:.6f})")

        # 2. Strategy: Milestone Checkpoints (Keep history)
        # Save every 5 epochs so you can compare "Epoch 10" vs "Epoch 30" behavior
        if (epoch + 1) % 5 == 0:
            torch.save(trainable_state, output_dir / f"model_epoch_{epoch+1}.pth")
            print(f"Milestone Model Saved at Epoch {epoch+1}")

# def monitor_frozen_output(module, input, output):
#     # output['sentence_embedding'] contains the vector because 
#     # the base SentenceTransformer module returns a dict
#     embedding = output['sentence_embedding']
    
#     print(f"Captured output shape from frozen base model: {embedding.shape}")
#     return None

# # 2. Register the hook specifically to index 0
# # model[0] is your "base_model" variable
# hook_handle = model[0].register_forward_hook(monitor_frozen_output)

# print("Hook registered on frozen base model.")

# Run the training
train_model(model, train_loader, val_loader, optimizer, loss_fn, num_epochs)