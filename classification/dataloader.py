import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, csv_file, tokenizer):
        self.data = pd.read_csv(csv_file)
        self.tokenizer =tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        text, label = row["obfuscated_text"], row["toxic_label"]

        encoding = self.tokenizer(text, padding="max_length", max_length=256)
        input_ids = encoding['input_ids']
        attention_mask = encoding['attention_mask']
        input_ids = torch.tensor(input_ids, dtype=torch.long)
        attention_mask = torch.tensor(attention_mask, dtype=torch.long)
        label = torch.tensor(label, dtype=torch.long)

        return {
            "input_ids": input_ids,
            "label": label,
            "attention_mask": attention_mask
        }

def collate_fn(batch):
    input_ids = torch.stack([item["input_ids"] for item in batch])
    labels = torch.stack([item["label"] for item in batch])
    attention_mask = torch.stack([item["attention_mask"] for item in batch])

    return {
        "input_ids": input_ids,
        "labels": labels,
        "attention_mask": attention_mask
    }

def get_dataloader(csv_file, tokenizer, batch_size=16, shuffle=True):
    print("---Start dataload---")
    dataset = CustomDataset(csv_file, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn, generator=g)
    print("---End dataload---")
    
    return dataloader