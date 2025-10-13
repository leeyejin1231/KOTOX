import argparse
from copy import deepcopy
from pathlib import Path
from datasets import load_dataset  # type: ignore
from peft import LoraConfig
import transformers
from transformers import AutoModelForCausalLM
from transformers import AutoTokenizer
from transformers import BitsAndBytesConfig
from transformers import TrainerCallback
from trl import SFTConfig  # type: ignore
from trl import SFTTrainer  # type: ignore
from PROMPTS import PROMPTS
from string import Template
import random
import numpy as np
import torch
import os
import json
from functools import partial

AutoModelForCausalLM.from_pretrained = partial(AutoModelForCausalLM.from_pretrained, trust_remote_code=True)

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

# Preprocessing dataset
def preprocess(task_name, prompt, data, tokenizer):
    # Getting data
    if task_name == "deobfuscation":
        query = data["neutral_obfuscated_texts"]
        target = data["neutral"]
    elif task_name == "sanitization":
        query = data["toxic_obfuscated_texts"]
        target = data["toxic"]
    else:
        print(f"Undefined task: {task_name}.")
        exit(1)

    # Formatting with instructions
    total_messages = [
        {
            "role":"user",
            "content":prompt.substitute(input=query),
        },
        {
            "role":"assistant",
            "content":target
        }
    ]
    query_messages = [
        {
            "role":"user",
            "content":prompt.substitute(input=query),
        }
    ]

    # Tokenizing query and response
    total_chat = tokenizer.apply_chat_template(total_messages, tokenize=False).rstrip()
    total_tokenized = tokenizer(total_chat, add_special_tokens=False)
    labels = total_tokenized["input_ids"].copy()

    # Tokenizing query
    query_chat = tokenizer.apply_chat_template(query_messages, add_generation_prompt=True, tokenize=False)
    query_len = len(tokenizer(query_chat, add_special_tokens=False)["input_ids"])

    # Masking lables for query
    labels[:query_len] = [-100] * query_len
    total_tokenized["labels"] = labels
    return total_tokenized

class GenerationCallback(TrainerCallback):
    def __init__(self, tokenizer, examples, every_n_steps):
        self.tokenizer = tokenizer
        self.every_n_steps = every_n_steps
        input_ids = []
        attention_masks = []
        queries = []
        answers = []
        for idx, _ in enumerate(examples["input_ids"]):
            query_len = len([i for i in examples["labels"][idx] if i==-100])
            input_ids.append(torch.tensor(examples["input_ids"][idx][:query_len]).reshape(1,-1))
            attention_masks.append(torch.tensor(examples["attention_mask"][idx][:query_len]).reshape(1,-1))
            queries.append(tokenizer.decode(examples["input_ids"][idx]).split("Input sentence: ")[1].split("\nOutput sentence:")[0])
            answers.append(tokenizer.decode(examples["input_ids"][idx][query_len:]))
        self.input_ids = input_ids
        self.queries = queries
        self.attention_masks = attention_masks
        self.answers = answers
    def on_step_end(self, args, state, control, **kwargs):
        if state.global_step % self.every_n_steps == 0 and state.global_step > 0:
            model = kwargs["model"].eval()
            print(f"\n[Step {state.global_step}] Sample generations:")
            for idx, _ in enumerate(self.input_ids):
                with torch.no_grad():
                    outputs = model.generate(
                        input_ids=self.input_ids[idx].to(model.device),
                        attention_mask=self.attention_masks[idx].to(model.device),
                        max_new_tokens=128,
                        do_sample=True,
                        top_p=0.9
                    )
                output = self.tokenizer.decode(outputs[0][len(self.input_ids[idx][0]):])
                print("=" * 16, "Query", "="*16)
                print(self.queries[idx])
                print("=" * 16, "Answer", "="*16)
                print(self.answers[idx])
                print("=" * 16, "Output", "="*16)
                print(output)
                print("=" * 40)
                print("\n")
        return control

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
    parser.add_argument("--max-seq-length", type=int, default=1024)
    parser.add_argument("--gradient_accumulation_steps", type=int, default=16)
    parser.add_argument("--save-steps", type=int, default=25)
    parser.add_argument("--eval-steps", type=int, default=25)
    parser.add_argument("--load-in-4bit", action="store_true", default=False)
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()

    task_name = args.task_name
    model_pretrained = args.model_pretrained
    dataset_level = args.dataset_level
    output_dir = args.output_dir
    epochs = args.epochs
    batch_size = args.batch_size
    learning_rate = args.learning_rate
    weight_decay = args.weight_decay
    max_seq_length = args.max_seq_length
    gradient_accumulation_steps = args.gradient_accumulation_steps
    save_steps = args.save_steps
    eval_steps = args.eval_steps
    load_in_4bit = args.load_in_4bit
    seed = args.seed
    
    # Setting seed
    fix_seed(seed)

    # Setting dataset path
    train_dataset_path = f"data/KOTOX/{dataset_level}/ko_obfs_augmented_{dataset_level}_train.csv"
    val_dataset_path = f"data/KOTOX/{dataset_level}/ko_obfs_augmented_{dataset_level}_val.csv"
    test_dataset_path = f"data/KOTOX/{dataset_level}/ko_obfs_augmented_{dataset_level}_test.csv"

    # Setting model name
    model_name = model_pretrained.split("/")[1]
    new_model_name = model_name + "_finetuned"

    # Setting output dir
    output_dir = Path(args.output_dir) / task_name / dataset_level / model_name / str(seed) / f"epoch{epochs}_batch{batch_size*gradient_accumulation_steps}_lr{learning_rate}_wd{weight_decay}"

    # Loading dataset
    train_dataset = load_dataset("csv", data_files=train_dataset_path, split="train")
    val_dataset = load_dataset("csv", data_files=val_dataset_path, split="train")
    test_dataset = load_dataset("csv", data_files=test_dataset_path, split="train")

    # Loading tokenizer
    tokenizer = AutoTokenizer.from_pretrained(
        model_pretrained,
        trust_remote_code=True,
    )
    tokenizer.padding_side = "left"

    # Preprocessing dataset
    if not f"{task_name}_zero_prompt" in PROMPTS:
        print(f"The zero-shot prompt for {task_name} does not exist.")
        exit(1)
    prompt = Template(PROMPTS[f"{task_name}_zero_prompt"])
    train_preprocessed = train_dataset.map(
        lambda x: preprocess(task_name, prompt, x, tokenizer),
        remove_columns=train_dataset.column_names
    )
    val_preprocessed = val_dataset.map(
        lambda x: preprocess(task_name, prompt, x, tokenizer),
        remove_columns=val_dataset.column_names
    )
    test_preprocessed = test_dataset.map(
        lambda x: preprocess(task_name, prompt, x, tokenizer),
        remove_columns=test_dataset.column_names
    )

    # 4bit quantization config 
    if load_in_4bit:
        bnb_config = BitsAndBytesConfig(  # type: ignore
            load_in_4bit=True,
            bnb_4bit_quant_type="nf4",
        )

    # Loading model
    if load_in_4bit:
        model = AutoModelForCausalLM.from_pretrained(
            model_pretrained,
            trust_remote_code=True,
            quantization_config=bnb_config,
            device_map="auto",
        )
    else:
        model = AutoModelForCausalLM.from_pretrained(
            model_pretrained,
            trust_remote_code=True,
            device_map="auto",
        )
    model.config.use_cache = False
    model.config.pretraining_tp = 1

    model.config.pad_token_id = tokenizer.pad_token_id
    model.config.eos_token_id = tokenizer.eos_token_id
    model.config.bos_token_id = tokenizer.bos_token_id
    model.generation_config.pad_token_id = tokenizer.pad_token_id
    model.generation_config.eos_token_id = tokenizer.eos_token_id
    model.generation_config.bos_token_id = tokenizer.bos_token_id

    # lora config 
    peft_config = LoraConfig(
        lora_alpha=16,
        lora_dropout=0.1,
        r=64,
        bias="none",
        task_type="CAUSAL_LM",
        target_modules=[
            "q_proj",
            "k_proj",
            "v_proj",
            "o_proj",
            "up_proj",
            "down_proj",
            "gate_proj",
        ],
    )

    # SFT config
    training_arguments = SFTConfig(
        # Training Hyperparameters
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        gradient_accumulation_steps=gradient_accumulation_steps,
        optim="paged_adamw_32bit",
        learning_rate=learning_rate,
        weight_decay=weight_decay,
        fp16=False,
        bf16=True,
        max_grad_norm=0.3,
        max_steps=-1,
        warmup_ratio=0.03,
        group_by_length=True,
        lr_scheduler_type="cosine",
        max_length=max_seq_length,
        
        # Logging and evaluation config
        logging_steps=eval_steps,
        eval_strategy="steps",
        eval_steps=eval_steps,
        
        # Tracking best model
        metric_for_best_model = "eval_loss",
        greater_is_better = False,
        load_best_model_at_end=False,
        overwrite_output_dir=True,
        
        # Saving config
        output_dir=output_dir,
        save_strategy="steps",
        save_steps=save_steps,
        save_total_limit=1,
    )

    if save_steps % eval_steps != 0:
        print("\nWarning: the last steps will not be evaluated.")

    trainer = SFTTrainer(
        model=model,
        train_dataset=train_preprocessed,
        eval_dataset=val_preprocessed,
        peft_config=peft_config,
        args=training_arguments,
    )
    trainer.add_callback(GenerationCallback(tokenizer, val_preprocessed[:5], eval_steps))
    trainer.train()
    
    last_dir = output_dir / f"checkpoint-{trainer.state.max_steps}-last"
    trainer.model.save_pretrained(last_dir)
    tokenizer.save_pretrained(last_dir)

if __name__ == "__main__":
    main()
