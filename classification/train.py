import torch.optim as optim
import torch
import json
import os
import numpy as np
import torch.nn as nn
import torch.optim as optim
from sklearn.metrics import accuracy_score, f1_score
from tqdm import tqdm
import random
from transformers import AutoTokenizer, XLMRobertaTokenizer
from model import CustomBERT
import config as train_config
from easydict import EasyDict as edict
from dataloader import get_dataloader
from utils import iter_product

device = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')

def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)

    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def train_step(dataloader, model, optimizer, criterion, step_count=0):
    print("---Start train!---")
    model.train()
    total_loss = 0
    current_step = step_count

    for batch in tqdm(dataloader):
        input_ids = batch["input_ids"].to(device)
        attention_mask = batch["attention_mask"].to(device)
        labels = batch["labels"].to(device)

        optimizer.zero_grad()
        outputs = model(input_ids, attention_mask)
        loss = criterion(outputs, labels)

        loss.backward()
        optimizer.step()
        total_loss += loss.item()
        current_step += 1

    return total_loss / len(dataloader), current_step

def evaluate(dataloader, model):
    print("---Start Valid!---")
    model.eval()
    predictions, true_labels = [], []

    with torch.no_grad():
        for batch in tqdm(dataloader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)

            outputs = model(input_ids, attention_mask)
            preds = torch.softmax(outputs, dim=1)[:, 1]

            predictions.extend(preds.cpu())
            true_labels.extend(labels.cpu().numpy())

    y_pred = (np.array(predictions) >= 0.5).astype(int)
    acc = accuracy_score(true_labels, y_pred)
    f1 = f1_score(true_labels, y_pred, average="macro")
    accuracy, f1 = float(acc), float(f1)
    
    return accuracy, f1


def train(log):
    set_seed(log.param.SEED)

    try:
        tokenizer = AutoTokenizer.from_pretrained(log.param.model_type)
    except:
        print(f"AutoTokenizer failed, trying XLMRobertaTokenizer for {log.param.model_type}")
        tokenizer = XLMRobertaTokenizer.from_pretrained(log.param.model_type)
    os.makedirs(f"./save/{log.param.dataset}/{log.param.model_type}/{log.param.SEED}", exist_ok=True)
    
    os.makedirs(f"./save/{log.param.dataset}/{log.param.model_type}/{log.param.SEED}", exist_ok=True)
    MODEL_SAVE_PATH = f"./save/{log.param.dataset}/{log.param.model_type}/{log.param.SEED}/best_model.pth"
    criterion = nn.CrossEntropyLoss()

    train_loader = get_dataloader(f"../data/{log.param.dataset}/train.csv", tokenizer, batch_size=log.param.train_batch_size)
    valid_loader = get_dataloader(f"../data/{log.param.dataset}/valid.csv", tokenizer, batch_size=log.param.train_batch_size)

    model = CustomBERT(log.param.model_type, hidden_dim=log.param.hidden_size).to(device)
    optimizer = optim.AdamW(model.parameters(), lr=log.param.learning_rate)

    best_f1_score = 0.0
    num_epochs = log.param.nepoch
    df = {"param":{}, "train":{"loss":[], "f1":[], "threshold":[], "step":[]}}
    df["param"]["dataset"] = log.param.dataset
    df["param"]["train_batch_size"] = log.param.train_batch_size
    df["param"]["learning_rate"] = log.param.learning_rate
    df["param"]["SEED"] = log.param.SEED
    
    current_step = 0
    eval_interval = 25  # 25 step마다 평가
    
    for epoch in range(num_epochs):
        print(f"epoch {epoch+1}")
        train_loss, current_step = train_step(train_loader, model, optimizer, criterion, current_step)
        
        # 10 step마다 평가 및 저장
        if current_step % eval_interval == 0:
            acc, f1 = evaluate(valid_loader, model)
            print(f"Step {current_step}, Loss: {train_loss:.4f}, Accuracy: {acc:.4f}, F1-Score: {f1:.4f}")
            
            df["train"]["loss"].append(train_loss)
            df["train"]["f1"].append(f1)
            df["train"]["step"].append(current_step)

            if f1 > best_f1_score:
                best_f1_score = f1
                torch.save(model.state_dict(), MODEL_SAVE_PATH)
                df["stop_step"] = current_step
                df["valid_f1_score"] = f1
                df["valid_loss"] = train_loss
                print(f"=== Model saved at step {current_step} with F1-score: {f1:.4f} ===")
    
    # 마지막에 한 번 더 평가
    acc, f1 = evaluate(valid_loader, model)
    print(f"Final Step {current_step}, Loss: {train_loss:.4f}, Accuracy: {acc:.4f}, F1-Score: {f1:.4f}")
    
    if f1 > best_f1_score:
        best_f1_score = f1
        torch.save(model.state_dict(), MODEL_SAVE_PATH)
        df["stop_step"] = current_step
        df["valid_f1_score"] = f1
        df["valid_loss"] = train_loss
        print(f"=== Final model saved at step {current_step} with F1-score: {f1:.4f} ===")
    
    with open(f"./save/{log.param.dataset}/{log.param.model_type}/{log.param.SEED}/log.json", 'w') as file:
        json.dump(df, file)

if __name__ == '__main__':
    tuning_param = train_config.tuning_param
    
    param_list = [train_config.param[i] for i in tuning_param]
    param_list = [tuple(tuning_param)] + list(iter_product(*param_list)) ## [(param_name),(param combinations)]

    for param_com in param_list[1:]: # as first element is just name
        log = edict()
        log.param = train_config.param

        for num,val in enumerate(param_com):
            log.param[param_list[0][num]] = val

        train(log)