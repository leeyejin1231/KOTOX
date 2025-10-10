import os
import torch
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score
from tqdm import tqdm
import random
from transformers import AutoTokenizer
from model import CustomBERT
import eval_config as eval_config
from easydict import EasyDict as edict
from dataloader import get_dataloader
from utils import iter_product

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')


def set_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    torch.backends.cudnn.deterministic = True
    torch.backends.cudnn.benchmark = False


def evaluate_model(dataloader, model):
    print("---Start Evaluation!---")
    model.eval()
    predictions, true_labels, obfuscated_labels, difficulties, input_texts = [], [], [], [], []

    with torch.no_grad():
        for batch in tqdm(dataloader):
            input_ids = batch["input_ids"].to(device)
            attention_mask = batch["attention_mask"].to(device)
            labels = batch["labels"].to(device)
            obf_labels = batch["obfuscated_labels"]
            difficulty = batch["difficulties"]
            input_text = batch["input_text"]

            outputs = model(input_ids, attention_mask)
            probs = torch.softmax(outputs, dim=1)
            preds = probs[:, 1]  # probability of class 1

            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
            obfuscated_labels.extend(obf_labels)
            difficulties.extend(difficulty)
            input_texts.extend(input_text)
            
    # generate predictions with threshold 0.5
    y_pred = (np.array(predictions) >= 0.5).astype(int)
    y_true = np.array(true_labels)
    y_obf = np.array(obfuscated_labels)
    y_diff = np.array(difficulties)
    y_input_text = np.array(input_texts)
    
    # calculate metrics
    accuracy = accuracy_score(y_true, y_pred)
    f1 = f1_score(y_true, y_pred, average="macro")
    precision = precision_score(y_true, y_pred, average="macro")
    recall = recall_score(y_true, y_pred, average="macro")
    
    return {
        'accuracy': float(accuracy),
        'f1_score': float(f1),
        'precision': float(precision),
        'recall': float(recall),
        'predictions': y_pred.tolist(),
        'true_labels': y_true.tolist(),
        'obfuscated_labels': y_obf.tolist(),
        'difficulties': y_diff.tolist(),
        'input_text': y_input_text.tolist()
    }


def save_results_to_csv(results, dataset_name, model_type, seed):
    # convert results to DataFrame
    # convert results to DataFrame
    df = pd.DataFrame({
        'input_text': results['input_text'],
        'predicted_label': results['predictions'],
        'true_label': results['true_labels'],
        'obfuscated_label': results['obfuscated_labels'],
        'difficulty': results['difficulties'],
    })
    
    # create result directory
    output_dir = f"./eval_results/{dataset_name}/{model_type}"
    os.makedirs(output_dir, exist_ok=True)
    
    # save results to CSV
    csv_filename = f"{output_dir}/evaluation_results_seed{seed}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    
    print(f"Evaluation results saved to CSV file: {csv_filename}")
    return csv_filename


def evaluate(log):
    set_seed(log.param.SEED)
    
    # load tokenizer
    tokenizer = AutoTokenizer.from_pretrained(log.param.model_type)
    
    # set model path
    model_path = log.param.model_path.format(dataset=log.param.dataset)
    
    # check if model file exists
    if not os.path.exists(model_path):
        print(f"Model file not found: {model_path}")
        return
    
    test_loader = get_dataloader(f"../data/{log.param.dataset}/test.csv", tokenizer, batch_size=log.param.eval_batch_size)
    
    # initialize and load model
    model = CustomBERT(log.param.model_type, hidden_dim=log.param.hidden_size).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    
    # evaluate model
    results = evaluate_model(test_loader, model)
    
    # print results
    print(f"\n=== Evaluation results ({log.param.dataset}) ===")
    print(f"F1-Score:  {results['f1_score']:.4f}")
    print(f"Accuracy:  {results['accuracy']:.4f}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall:    {results['recall']:.4f}")
    
    # save results to CSV
    save_results_to_csv(results, log.param.dataset, log.param.model_type, log.param.SEED)


if __name__ == '__main__':
    tuning_param = eval_config.tuning_param
    
    param_list = [eval_config.param[i] for i in tuning_param]
    param_list = [tuple(tuning_param)] + list(iter_product(*param_list)) ## [(param_name),(param combinations)]

    for param_com in param_list[1:]: # as first element is just name
        log = edict()
        log.param = eval_config.param

        for num,val in enumerate(param_com):
            log.param[param_list[0][num]] = val

        evaluate(log)