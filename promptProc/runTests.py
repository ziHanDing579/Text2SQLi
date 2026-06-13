import torch
from torch import nn
from torch.utils.data import DataLoader, Dataset, random_split
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

new_weights_path = current_file_dir.parent / 'models' / 'checkpoint_epoch_50.pth'  # Adjust path as needed
inter_dims = [128, 64, 32]
dense_intermediate_layers = []
target_dims = 6
physical_batch_size = 4
accumulation_steps = 4
num_epochs = 50
base_model = SentenceTransformer(og_model_name, device=device)
og_dims = base_model.get_sentence_embedding_dimension()
for inter_dim in inter_dims:
    dense_intermediate_layers.append(
        models.Dense(
            in_features=og_dims if not dense_intermediate_layers else dense_intermediate_layers[-1].out_features,
            out_features=inter_dim,
            activation_function=torch.nn.GELU()
        )
    )

dense_layer_2 = models.Dense(
    in_features=inter_dims[-1],
    out_features=target_dims,
    activation_function=torch.nn.Identity()
)
norm_layer = models.Normalize()
modules_with_reduction = [base_model] + dense_intermediate_layers + [dense_layer_2, norm_layer]
model = SentenceTransformer(modules=modules_with_reduction)
model.to(device)

# Load the saved weights
checkpoint = torch.load(new_weights_path, map_location=device)
model[1].load_state_dict(checkpoint['dense_1'])
model[2].load_state_dict(checkpoint['dense_2'])

parent_dir = current_file_dir.parent
training_data = pd.read_csv(parent_dir / 'mixed_questions_bal_labeled_train_dataset.csv')
validation_data = pd.read_csv(parent_dir / 'mixed_questions_bal_labeled_val_dataset.csv')
test_data = pd.read_csv(parent_dir / 'mixed_questions_bal_labeled_test_dataset.csv')

class TextVectorDataset(Dataset):
    def __init__(self, dataframe):
        # We assume the first column is text, and the last 5 are the vector
        self.texts = dataframe.iloc[:, 0].values
        # Get the last 5 columns and convert to float32 (standard for PyTorch)
        self.vectors = dataframe.iloc[:, -6:].values.astype('float32')

    def __len__(self):
        return len(self.texts)

    def __getitem__(self, idx):
        text = self.texts[idx]
        vector = self.vectors[idx]
        return text, vector
    
test_ds = TextVectorDataset(test_data)
test_loader = DataLoader(test_ds, batch_size=physical_batch_size, shuffle=False)

class LogMSELoss(nn.Module):
    def __init__(self, epsilon=1):
        super(LogMSELoss, self).__init__()
        self.mse = nn.MSELoss()
        self.epsilon = epsilon

    def forward(self, pred, target):
        # Step 1: Add epsilon and take the log
        log_pred = torch.log(pred + self.epsilon)
        log_target = torch.log(target + self.epsilon)
        
        # Step 2: Calculate MSE on the transformed values
        return self.mse(log_pred, log_target)

def evaluate_model(model, data_loader):
    model.eval()
    total_loss = 0.0
    loss_fn = LogMSELoss(epsilon=1).to(device)
    with torch.no_grad():
        for texts, vectors in data_loader:
            texts = list(texts)
            vectors = vectors.to(device)

            embeddings = model.encode(texts, convert_to_tensor=True, device=device)

            target = torch.ones(embeddings.size(0)).to(device)

            loss = loss_fn(embeddings, vectors)
            total_loss += loss.item() * embeddings.size(0)
    avg_loss = total_loss / len(data_loader.dataset)
    return avg_loss

test_loss = evaluate_model(model, test_loader)
print(f"Test Loss (Loss): {test_loss:.4f}")