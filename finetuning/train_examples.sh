#!/bin/bash

# Task
python -u finetuning/train.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 42
python -u finetuning/train.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name sanitization --seed 42

# Level
python -u finetuning/train.py --dataset-level easy --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 42
python -u finetuning/train.py --dataset-level normal --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 42
python -u finetuning/train.py --dataset-level hard --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 42
python -u finetuning/train.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 42

# Model
python -u finetuning/train.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 42
python -u finetuning/train.py --dataset-level total --model-pretrained LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct --task-name deobfuscation --seed 42
python -u finetuning/train.py --dataset-level total --model-pretrained MLP-KTLim/llama-3-Korean-Bllossom-8B --task-name deobfuscation --seed 42

# Seed
python -u finetuning/train.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 42
python -u finetuning/train.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 43
python -u finetuning/train.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --task-name deobfuscation --seed 44