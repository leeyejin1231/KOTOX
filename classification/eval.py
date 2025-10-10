import torch
import json
import os
import numpy as np
import torch.nn as nn
import pandas as pd
from sklearn.metrics import accuracy_score, f1_score, precision_score, recall_score, classification_report, confusion_matrix
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
    """모델 평가 함수"""
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
            preds = probs[:, 1]  # 클래스 1에 대한 확률

            predictions.extend(preds.cpu().numpy())
            true_labels.extend(labels.cpu().numpy())
            obfuscated_labels.extend(obf_labels)
            difficulties.extend(difficulty)
            input_texts.extend(input_text)
            
    # 임계값 0.5로 예측값 생성
    y_pred = (np.array(predictions) >= 0.5).astype(int)
    y_true = np.array(true_labels)
    y_obf = np.array(obfuscated_labels)
    y_diff = np.array(difficulties)
    y_input_text = np.array(input_texts)
    # 메트릭 계산
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
    """평가 결과를 CSV 파일로 저장"""
    # 결과를 DataFrame으로 변환
    df = pd.DataFrame({
        'input_text': results['input_text'],
        'predicted_label': results['predictions'],
        'true_label': results['true_labels'],
        'obfuscated_label': results['obfuscated_labels'],
        'difficulty': results['difficulties'],
    })
    
    # 결과 디렉토리 생성
    output_dir = f"./eval_results/{dataset_name}/{model_type}"
    os.makedirs(output_dir, exist_ok=True)
    
    # CSV 파일 저장
    csv_filename = f"{output_dir}/evaluation_results_seed{seed}.csv"
    df.to_csv(csv_filename, index=False, encoding='utf-8')
    
    print(f"평가 결과가 CSV 파일로 저장되었습니다: {csv_filename}")
    return csv_filename


def evaluate(log):
    """메인 평가 함수"""
    set_seed(log.param.SEED)
    
    # 토크나이저 로드
    tokenizer = AutoTokenizer.from_pretrained(log.param.model_type)
    
    # 모델 경로 설정
    model_path = log.param.model_path.format(dataset=log.param.dataset)
    
    # 모델 파일 존재 확인
    if not os.path.exists(model_path):
        print(f"모델 파일을 찾을 수 없습니다: {model_path}")
        return
    
    test_loader = get_dataloader(f"../data/{log.param.dataset}/test.csv", tokenizer, batch_size=log.param.eval_batch_size)
    
    # 모델 초기화 및 로드
    model = CustomBERT(log.param.model_type, hidden_dim=log.param.hidden_size).to(device)
    model.load_state_dict(torch.load(model_path, map_location=device))
    
    # print(f"모델 로드 완료: {model_path}")
    # print(f"평가 데이터셋: {log.param.dataset}")
    # print(f"디바이스: {device}")
    
    # 평가 실행
    results = evaluate_model(test_loader, model)
    
    # 결과 출력
    print(f"\n=== 평가 결과 ({log.param.dataset}) ===")
    print(f"F1-Score:  {results['f1_score']:.4f}")
    print(f"Accuracy:  {results['accuracy']:.4f}")
    print(f"Precision: {results['precision']:.4f}")
    print(f"Recall:    {results['recall']:.4f}")
    
    # CSV 파일로 결과 저장
    save_results_to_csv(results, log.param.dataset, log.param.model_type, log.param.SEED)
    
    # # 상세 분류 리포트 출력
    # print("\n=== Classification Report ===")
    # print(classification_report(results['true_labels'], results['predictions'], 
    #                           target_names=['Class 0', 'Class 1']))
    
    # # 혼동 행렬 출력
    # print("\n=== Confusion Matrix ===")
    # cm = confusion_matrix(results['true_labels'], results['predictions'])
    # print(cm)
    
    # # 결과를 JSON 파일로 저장
    # eval_results = {
    #     "dataset": log.param.dataset[0],
    #     "model_path": model_path,
    #     "metrics": {
    #         "accuracy": results['accuracy'],
    #         "f1_score": results['f1_score'],
    #         "precision": results['precision'],
    #         "recall": results['recall']
    #     },
    #     "classification_report": classification_report(results['true_labels'], results['predictions'], output_dict=True),
    #     "confusion_matrix": cm.tolist(),
    #     "predictions": results['predictions'][:100],  # 처음 100개만 저장 (메모리 절약)
    #     "true_labels": results['true_labels'][:100],
    #     "probabilities": results['probabilities'][:100]
    # }
    
    # 결과 저장
    # os.makedirs(f"./eval_results/{log.param.dataset[0]}/{log.param.model_type}/{log.param.SEED}", exist_ok=True)
    # with open(f"./eval_results/{log.param.dataset[0]}/{log.param.model_type}/evaluation_results.json", 'w', encoding='utf-8') as f:
    #     json.dump(eval_results, f, ensure_ascii=False, indent=2)
    
    # print(f"\n평가 결과가 저장되었습니다: ./eval_results/{log.param.dataset[0]}/{log.param.model_type}/evaluation_results.json")


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
