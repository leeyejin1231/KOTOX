# Evaluation Configuration
dataset = ["KObfus/no_obfus", "KObfus/easy", "KObfus/medium", "KObfus/hard", "KObfus/total"] 

tuning_param  = ["dataset"] ## list of possible paramters to be tuned

model_type = "GroNLP/hateBERT"
# model_type = "unitary/multilingual-toxic-xlm-roberta"
# model_type = "textdetox/xlmr-large-toxicity-classifier-v2"

SEED = 42

model_path = f"./save/KObfus/easy/{model_type}/{SEED}/best_model.pth"  # trained model path

eval_batch_size = 16
hidden_size = 768

param = {
    "dataset": dataset,
    "model_path": model_path,
    "eval_batch_size": eval_batch_size,
    "hidden_size": hidden_size,
    "model_type": model_type,
    "SEED": SEED
}
