import argparse
from copy import deepcopy
from pathlib import Path
from datasets import load_dataset  # type: ignore
from peft import LoraConfig
import transformers
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer
from transformers import BitsAndBytesConfig
from peft import PeftModel
from PROMPTS import PROMPTS
from string import Template
from tqdm import tqdm
import random
import numpy as np
import torch
import os
import json

# Seeding
def fix_seed(seed=42):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)
    torch.cuda.manual_seed_all(seed)
    
    torch.backends.cudnn.benchmark = False
    torch.backends.cudnn.deterministic = True
    torch.use_deterministic_algorithms(True)
    
    transformers.set_seed(seed)
    os.environ["PYTHONHASHSEED"] = str(seed)
    os.environ["CUBLAS_WORKSPACE_CONFIG"] = ":16:8"
    os.environ["TF_ENABLE_ONEDNN_OPTS"] = "0"

def main() -> None:
    # Parsing arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--task-name", type=str, default="deobfuscation", choices=["deobfuscation", "sanitization"])
    parser.add_argument("--model-pretrained", type=str, default="Qwen/Qwen2.5-7B-Instruct")
    parser.add_argument("--dataset-level", type=str, default="total", choices=["easy", "normal", "hard", "total"])
    parser.add_argument("--output-dir", type=str, default="finetuned_models")
    parser.add_argument("--epochs", type=int, default=5)
    parser.add_argument("--batch-size", type=int, default=1)
    parser.add_argument("--learning-rate", type=float, default=2e-5)
    parser.add_argument("--weight-decay", type=float, default=1e-2)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=16)
    parser.add_argument("--load-in-4bit", action="store_true", default=False)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--setting", type=str, default="zero", choices=["zero", "five", "sft"])
    parser.add_argument("--max-answer-tokens", default=1024, type=int)
    parser.add_argument("--do-sample", action="store_true", default=True)
    parser.add_argument("--temperature", default=None, type=float)
    parser.add_argument("--top-p", default=None, type=float)
    parser.add_argument("--start-idx", default=0, type=int)
    parser.add_argument("--end-idx", default=2147483647, type=int)
    
    args = parser.parse_args()

    task_name = args.task_name
    model_pretrained = args.model_pretrained
    dataset_level = args.dataset_level
    epochs = args.epochs
    batch_size = args.batch_size
    learning_rate = args.learning_rate
    weight_decay = args.weight_decay
    gradient_accumulation_steps = args.gradient_accumulation_steps
    load_in_4bit = args.load_in_4bit
    seed = args.seed
    setting = args.setting
    max_answer_tokens = args.max_answer_tokens
    do_sample = args.do_sample
    temperature = args.temperature
    top_p = args.top_p
    start_idx = args.start_idx
    end_idx = args.end_idx
    
    # Setting seed
    fix_seed(seed)

    # Setting Output Path
    path = f"result/{task_name}/{setting}/"
    os.makedirs(path, exist_ok=True)

    # Setting model name
    model_name = model_pretrained.split("/")[1]

    # Loading base model
    base_model = AutoModelForCausalLM.from_pretrained(
        model_pretrained,
        trust_remote_code=True,
        dtype=torch.bfloat16,
        device_map="auto",
    )

    # Setting model path
    if setting == "sft":
        model_path = Path(args.output_dir) / task_name / dataset_level / model_name / str(seed) / f"epoch{epochs}_batch{batch_size*gradient_accumulation_steps}_lr{learning_rate}_wd{weight_decay}"
        dirs = os.listdir(model_path)
        for i in dirs:
            if "checkpoint" in i and not "last" in i:
                model_path = model_path / i
                break
        if os.path.exists(model_path) and os.path.isdir(model_path):
            model = PeftModel.from_pretrained(
                base_model,
                model_path,
                trust_remote_code=True,
                is_trainable=False,
                torch_dtype=base_model.dtype,
            )
            model.to(base_model.device)
        else:
            print("The finetuned model does not exist.")
            exit(1)
    else:
        model = base_model
    model.eval()
    
    # Loading tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_pretrained,
        trust_remote_code=True,
    )
    tokenizer.padding_side = "left"

    # Setting Config for Sampling
    model.generation_config.do_sample = do_sample
    if do_sample:
        if temperature != None:
            model.generation_config.temperature = temperature
        if top_p != None:
            model.generation_config.top_p = top_p

    # Output Path
    result_path = path+model_name+f"_{setting}_{dataset_level}_{seed}"
    if do_sample:
        result_path += f"_{model.generation_config.temperature}_{model.generation_config.top_p}"
    if start_idx > 0:
        result_path += f"_{start_idx}"
    result_path += ".jsonl"

    # Setting dataset path
    train_dataset_path = f"data/KOTOX/total/ko_obfs_augmented_total_train.csv"
    test_dataset_path = f"data/KOTOX/total/ko_obfs_augmented_total_test.csv"

    # Loading dataset
    train_dataset = load_dataset("csv", data_files=train_dataset_path, split="train")
    few_shot_examples = random.choices(train_dataset, k=5)
    test_dataset = load_dataset("csv", data_files=test_dataset_path, split="train")
    indices = list(range(len(test_dataset)))
    test_dataset = test_dataset.add_column("idx", indices)

    # Preprocessing dataset
    if not f"{task_name}_zero_prompt" in PROMPTS:
        print(f"The zero-shot prompt for {task_name} does not exist.")
        exit(1)
    
    # Setting Maximum Answer Tokens
    answer_generation_config = deepcopy(model.generation_config)
    answer_generation_config.max_new_tokens = max_answer_tokens
    answer_generation_config.eos_token_id = tokenizer.eos_token_id
    
    # Loading Prompts
    if setting == "zero" or setting == "sft":
        prompt = Template(PROMPTS[f"{task_name}_zero_prompt"])
    elif setting == "five":
        if task_name == "deobfuscation":
            few_shot_queries = [i["neutral_obfuscated_texts"] for i in few_shot_examples]
            few_shot_targets = [i["neutral"] for i in few_shot_examples]
        elif task_name == "sanitization":
            few_shot_queries = [i["toxic_obfuscated_texts"] for i in few_shot_examples]
            few_shot_targets = [i["toxic"] for i in few_shot_examples]
        else:
            print(f"Undefined task: {task_name}.")
            exit(1)
        prompt = Template(PROMPTS[f"{task_name}_five_prompt"])
        prompt = Template(
            prompt.safe_substitute(
                example1_input = few_shot_queries[0],
                example1_output = few_shot_targets[0],
                example2_input = few_shot_queries[1],
                example2_output = few_shot_targets[1],
                example3_input = few_shot_queries[2],
                example3_output = few_shot_targets[2],
                example4_input = few_shot_queries[3],
                example4_output = few_shot_targets[3],
                example5_input = few_shot_queries[4],
                example5_output = few_shot_targets[4],
            )
        )
    else:
        print(f"Undefined setting: {setting}.")
        exit(1)
    
    # Trimming Already Existing Files
    if os.path.exists(result_path):
        with open(result_path, 'r') as f:
            lines = f.readlines()
        temp = [json.loads(i) for i in lines[:-1]]
        try:
            last_line = json.loads(lines[-1])
            temp.append(last_line)
        except:
            pass
        if len(temp)<1:
            os.system(f"rm {result_path}")
        else:
            with open(result_path, "w") as f:
                for i in temp:
                    json.dump(i, f)
                    f.write("\n")
            start_idx = max(start_idx, temp[-1]["idx"]+1)
    end_idx = min(end_idx,len(test_dataset))
    
    # Start Inferencing
    with open(result_path, 'a', encoding="utf-8") as f:
        for idx, x in enumerate(tqdm(test_dataset.select(range(start_idx,end_idx)))):
            # Creating Queries
            if task_name == "deobfuscation":
                query = prompt.substitute(input=x["neutral_obfuscated_texts"])
                target = x["neutral"]
            elif task_name == "sanitization":
                query = prompt.substitute(input=x["toxic_obfuscated_texts"])
                target = x["toxic"]
            else:
                print(f"Undefined task: {task_name}.")
                exit(1)
        
            # Applying Chat Template
            input_template = tokenizer.apply_chat_template([{"role":"user","content":query}], tokenize=False, add_generation_prompt=True)
            
            # Tokenizing
            inputs = tokenizer(input_template, add_special_tokens=False, return_tensors="pt").to(model.device)
            query_length = len(inputs["input_ids"][0])

            # Answer Inference
            output_ids = model.generate(**inputs, generation_config=answer_generation_config, tokenizer=tokenizer)[0]
            answer_length = len(output_ids) - query_length
            
            # Resulting Output
            result = {
                "idx":x["idx"],
                "query":query,
                "answer":target,
            }
            result["generated_answer"] = tokenizer.decode(output_ids[-answer_length:])

            # Saving Output
            json.dump(result, f, ensure_ascii=False)
            f.write("\n")

if __name__ == "__main__":
    main()
