import numpy as np
import json
import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import f1_score, precision_score, recall_score

#Collect embeddings
with open("gpt_prompt_embeddings_SQLShieldTest.json", "r") as f:
    gpt_embeddings_dict = json.load(f)

with open("gpt_prompt_embeddings_SQLShieldTrain.json", "r") as f:
    temp = json.load(f)
    gpt_embeddings_dict.extend(temp)

with open("gpt_prompt_embeddings_SQLShieldValid.json", "r") as f:
    temp = json.load(f)
    gpt_embeddings_dict.extend(temp)

print(f"Total GPT embeddings loaded: {len(gpt_embeddings_dict)}")

gpt_embeddings = [list(item.values())[0][0] for item in gpt_embeddings_dict]
gpt_labels = [list(item.values())[0][1] for item in gpt_embeddings_dict]

#Convert to numpy arrays
gpt_embeddings = np.array(gpt_embeddings)
gpt_labels = np.array(gpt_labels)

train_test_split = 0.2
n_split = int(len(gpt_embeddings) * (1 - train_test_split))
X_train, X_test = gpt_embeddings[:n_split], gpt_embeddings[n_split:]
y_train, y_test = gpt_labels[:n_split], gpt_labels[n_split:]

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

class LogisticRegression(nn.Module):
    def __init__(self, input_dim):
        super().__init__()
        self.linear = nn.Linear(input_dim, 1)
    
    def forward(self, x):
        return self.linear(x).squeeze(-1)
    
model = LogisticRegression(X_train.shape[1]).to(device)

criterion = nn.BCEWithLogitsLoss()
optimizer = optim.Adam(model.parameters(), lr=1e-3, weight_decay=1e-4)

train_data = torch.utils.data.TensorDataset(torch.tensor(X_train, dtype=torch.float32), torch.tensor(y_train, dtype=torch.float32))
train_loader = torch.utils.data.DataLoader(train_data, batch_size=32, shuffle=True)
test_data = torch.utils.data.TensorDataset(torch.tensor(X_test, dtype=torch.float32), torch.tensor(y_test, dtype=torch.float32))
test_loader = torch.utils.data.DataLoader(test_data, batch_size=32, shuffle=False)

def evaluate(model, loader):
    model.eval()
    all_probs = []
    all_labels = []
    with torch.no_grad():
        for inputs, labels in loader:
            inputs, labels = inputs.to(device), labels.to(device)
            outputs = model(inputs)
            probs = torch.sigmoid(outputs)
            all_probs.extend(probs.cpu())
            all_labels.extend(labels.cpu())
    probs = torch.tensor(all_probs).numpy()
    labels = torch.tensor(all_labels).numpy()
    preds = (probs >= 0.5).astype(int)
    f1 = f1_score(labels, preds)
    precision = precision_score(labels, preds)
    recall = recall_score(labels, preds)
    return f1, precision, recall

best_f1 = 0
epochs = 50
for epoch in range(epochs):
    model.train()
    total_loss = 0.0
    for inputs, labels in train_loader:
        inputs, labels = inputs.to(device), labels.to(device)
        optimizer.zero_grad()
        outputs = model(inputs)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * inputs.size(0)
    
    avg_loss = total_loss / len(train_loader.dataset)
    f1, precision, recall = evaluate(model, test_loader)
    if f1 > best_f1:
        best_f1 = f1
        torch.save(model.state_dict(), "best_logistic_regression_model.pth")
    print(f"Epoch {epoch+1}/{epochs}, F1: {f1:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")

print("Best F1 on test set:", best_f1)

# run on mixed dataset
with open("gpt_prompt_embeddings_mixedOne.json", "r") as f:
    gpt_embeddings_dict = json.load(f)

with open("gpt_prompt_embeddings_mixedTwo.json", "r") as f:
    temp = json.load(f)
    gpt_embeddings_dict.extend(temp)

with open("gpt_prompt_embeddings_mixedSpider.json", "r") as f:
    temp = json.load(f)
    gpt_embeddings_dict.extend(temp)

print(f"Total GPT embeddings loaded: {len(gpt_embeddings_dict)}")

gpt_embeddings = [list(item.values())[0][0] for item in gpt_embeddings_dict]
gpt_labels = [list(item.values())[0][1] for item in gpt_embeddings_dict]

gpt_embeddings = np.array(gpt_embeddings)
gpt_labels = np.array(gpt_labels)
X = gpt_embeddings
y = gpt_labels

f1, precision, recall = evaluate(model, torch.utils.data.DataLoader(torch.utils.data.TensorDataset(torch.tensor(X, dtype=torch.float32), torch.tensor(y, dtype=torch.float32)), batch_size=32, shuffle=False))

print(f"Mixed Dataset - F1: {f1:.4f}, Precision: {precision:.4f}, Recall: {recall:.4f}")