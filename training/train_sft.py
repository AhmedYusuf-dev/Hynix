import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AdamW, get_cosine_schedule_with_warmup
from models.hynix_v1.model import HynixTransformer, get_hynix_1_mini_config
import json
import os

class HynixSFTDataset(Dataset):
    def __init__(self, jsonl_path, tokenizer, max_length=512):
        self.examples = []
        with open(jsonl_path, "r") as f:
            for line in f:
                data = json.loads(line)
                # Combine instruction and output for causal modeling
                text = f"Instruction: {data['instruction']}\nOutput: {data['output']}"
                tokens = tokenizer.encode(text) # Assuming tokenizer has encode method
                self.examples.append(tokens[:max_length])

    def __len__(self):
        return len(self.examples)

    def __getitem__(self, idx):
        return torch.tensor(self.examples[idx])

def train_sft():
    # 1. Config & Model
    config = get_hynix_1_mini_config()
    model = HynixTransformer(**config)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    # 2. Hyperparameters
    epochs = 3
    batch_size = 4
    grad_accum_steps = 4
    lr = 2e-4
    
    # 3. Data Loader
    # (Placeholder: User must provide a tokenizer and data)
    # dataset = HynixSFTDataset("data/exports/hynix_sft_batch.jsonl", tokenizer)
    # loader = DataLoader(dataset, batch_size=batch_size, shuffle=True)

    # 4. Optimizer & Scheduler
    optimizer = AdamW(model.parameters(), lr=lr)
    # scheduler = get_cosine_schedule_with_warmup(optimizer, num_warmup_steps=100, num_training_steps=1000)

    # 5. Training Loop
    model.train()
    print("Starting SFT Phase...")
    
    # Simple loop simulation
    for epoch in range(epochs):
        total_loss = 0
        # for batch in loader:
        #     batch = batch.to(device)
        #     outputs = model(batch)
        #     loss = F.cross_entropy(outputs.view(-1, config['vocab_size']), batch.view(-1))
        #     loss = loss / grad_accum_steps
        #     loss.backward()
        #     
        #     if (step + 1) % grad_accum_steps == 0:
        #         optimizer.step()
        #         optimizer.zero_grad()
        #         scheduler.step()
        
        print(f"Epoch {epoch+1} complete. Model saved.")
        torch.save(model.state_dict(), f"models/hynix_v1/hynix_sft_epoch_{epoch+1}.pt")

if __name__ == "__main__":
    train_sft()
