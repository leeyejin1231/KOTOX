#!/bin/bash

# Task
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name sanitization --seed 42

# Level
python -u evaluation/inference.py --dataset-level easy --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level normal --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level hard --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42

# Model
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level total --model-pretrained LGAI-EXAONE/EXAONE-3.5-7.8B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level total --model-pretrained MLP-KTLim/llama-3-Korean-Bllossom-8B --setting zero --task-name deobfuscation --seed 42

# Setting
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting five --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting sft --task-name deobfuscation --seed 42

# Seed
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 42
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 43
python -u evaluation/inference.py --dataset-level total --model-pretrained Qwen/Qwen2.5-7B-Instruct --setting zero --task-name deobfuscation --seed 44