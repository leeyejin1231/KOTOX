# Evaluation Configuration
dataset = ["KObfus/easy"]  # 평가할 데이터셋
# dataset = ["KObfus/no_obfus", "KObfus/easy", "KObfus/medium", "KObfus/hard", "KObfus/total"]  # 평가할 데이터셋

tuning_param  = ["dataset"] ## list of possible paramters to be tuned

# 모델 타입 (훈련 시와 동일해야 함)
model_type = "GroNLP/hateBERT"
# model_type = "unitary/multilingual-toxic-xlm-roberta"
# model_type = "textdetox/xlmr-large-toxicity-classifier-v2"

# 시드 설정
SEED = 42

# 모델 경로 설정
model_path = f"./save/KObfus/easy/{model_type}/{SEED}/best_model.pth"  # 훈련된 모델 경로

# 평가 파라미터
eval_batch_size = 16
hidden_size = 768

# 평가 설정
param = {
    "dataset": dataset,
    "model_path": model_path,
    "eval_batch_size": eval_batch_size,
    "hidden_size": hidden_size,
    "model_type": model_type,
    "SEED": SEED
}
