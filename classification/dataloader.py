import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader

class CustomDataset(Dataset):
    def __init__(self, csv_file, tokenizer):
        if 'ihc' in csv_file:
            self.data = pd.read_csv(csv_file, delimiter='\t')
        else:
            self.data = pd.read_csv(csv_file)
        self.csv_file = csv_file
        self.tokenizer = tokenizer

    def __len__(self):
        return len(self.data)

    def __getitem__(self, idx):
        row = self.data.iloc[idx]
        if 'KObfus' in self.csv_file and 'test' in self.csv_file:
            text, label, obfuscated_label, difficulty = row["text"], row["label"], row["obfuscated_labels"], row['difficulty']
        else:    
            text, label = row["text"], row["label"]

        encoding = self.tokenizer(
            text, 
            padding="max_length", 
            max_length=256, 
            truncation=True,
            return_tensors="pt"
        )
        input_ids = encoding['input_ids'].squeeze(0)
        attention_mask = encoding['attention_mask'].squeeze(0)
        label = torch.tensor(label, dtype=torch.long)

        if 'KObfus' in self.csv_file and 'test' in self.csv_file:
            return {
                "input_ids": input_ids,
                "label": label,
                "attention_mask": attention_mask,
                "obfuscated_label": obfuscated_label,
                "difficulty": difficulty,
                "input_text": text
            }
        else:
            return {
                "input_ids": input_ids,
                "label": label,
                "attention_mask": attention_mask,
            }

def collate_fn(batch):
    input_ids = torch.stack([item["input_ids"] for item in batch])
    labels = torch.stack([item["label"] for item in batch])
    attention_mask = torch.stack([item["attention_mask"] for item in batch])
    if batch[0]["obfuscated_label"]:
        obfuscated_labels = [item["obfuscated_label"] for item in batch]
        difficulties = [item["difficulty"] for item in batch]
        input_text = [item["input_text"] for item in batch]
    
        return {
            "input_ids": input_ids,
            "labels": labels,
            "attention_mask": attention_mask,
            "obfuscated_labels": obfuscated_labels,
            "difficulties": difficulties,
            "input_text": input_text
        }
    else:
        return {
            "input_ids": input_ids,
            "labels": labels,
            "attention_mask": attention_mask,
        }

def get_dataloader(csv_file, tokenizer, batch_size=16, shuffle=True):
    print("---Start dataload---")
    dataset = CustomDataset(csv_file, tokenizer)
    dataloader = DataLoader(dataset, batch_size=batch_size, shuffle=shuffle, collate_fn=collate_fn)
    print("---End dataload---")
    
    return dataloader