# KOTOX: A Korean Toxic Text for Obfuscation and Detoxification

<span style="color: red">❗️***Warning**: this document contains content that may be offensive or upsetting.*</span>

> **KOTOX**, the first Korean dataset for deobfuscation and detoxification, was built using linguistically grounded transformation rules to create three difficulty levels (easy, normal, and hard) for handling obfuscated toxic expressions.

## About KOTOX
<p align="center">
  <img src="./assets/motivation.png" alt="KOTOX motivation" width="350"/>
</p>

**KOTOX** is the first Korean dataset designed for deobfuscation and detoxification of toxic language. Built from linguistically grounded transformation rules, it introduces three difficulty levels—easy, normal, and hard—to model how users disguise offensive expressions in Korean. Unlike previous datasets that focus mainly on English or clean toxic text, KOTOX captures diverse obfuscation patterns specific to Hangul and Korean phonology, such as phonological, iconological, transliteration-based, syntactic, and pragmatic variations. It supports three complementary tasks—obfuscated toxic text classification, neutral text deobfuscation, and toxic text sanitization—providing a unified benchmark to evaluate the robustness of language models against obfuscated toxic content and to advance safer language technologies for low-resource languages.

## Dataset Construction

<p align="center">
  <img src="./assets/overview.png" alt="KOTOX overview" width="650"/>
</p>

### Base Corpus
- Started from [K/DA](https://github.com/minkyeongjeon/kda) - 7.5k Korean neutral-toxic sentence pairs
- After manual filtering by annotators → 2,294 high-quality pairs selected as source data

### Obfuscation Rules

| Approach | Transformation rule |  Example  |  
|--|---|---|  
| **Phonological** | Initial consonant repacement | 한국인 → 한꾹인 |
|  | Medial vowel replacement| 해수욕장 → 헤수욕장 |
|  | Final consonant replacement | 한국인 → 핝굮읹 |
|  | Ortographic reyllabification | 한국인 → 한구긴 |
|  | Initial consonant insertion | 한국인 → 한국긴 |
|  | Medial vowel insertion | 한국인 → 환궉윈 |
|  | Final consonant insertion | 바깥 → 박깥 |
|  | Liaison | 할 짓이가 → 할찌시가 |
| **Iconological** | Hanguel look-alike | 귀엽다 → 커엽다 |
|  | Cross-script substitution | 쭈꾸미 → 卒꾸口I |
|  | Rotation-based variation | 논문 → 곰국 |
| **Transliteration** | Phonetic substitution (Latin) | 망했어 → mang했어 |
|  | Phonetic substitution (CJK) | 수상해 → 水상해 |
|  | Semantic substitution | 가지마세요 → 돈트고쿠다사이 |
| **Synatatic** | Spacing perturbation | 화장실 더럽고 별로 → 화장 실더럽 고별로 |
|  | Syllable anagram | 오랜만에 외국여행을 → 오만랜에 외여국행을 |
|  | Symbol/emoji insertion | 돈을 쓰는 호갱 → 돈을°♡ 쓰는《호..갱》≥ㅅ≤ |

### Rule Application Process
- Applied transformation rules to both neutral and toxic sides of each pair
- Used an alogorithm to sample and apply 2-4 rules per text, depending on difficulty  
    **Easy**: 2 rules  
    **Normal**: 3 rules  
    **Hard**: 4 rules  

### Dataset Cmoposition
- Final dataset: 6.9k neutral-toxic-pairs + corresponding obfuscated counterparts
- Split into train/validation/test = 8:1:1 ratio for each difficulty level

## ⚒️ Usage
### Datasets

```bash
└── data
    ├── KOTOX
    │   ├── easy
    │   ├── normal
    │   ├── hard
    │   └── total
    └── KOTOX_classification
        ├── easy
        ├── normal
        ├── hard
        └── total
``` 
**KOTOX**: obfuscation, detoxification  
**KOTOX_classification**: toxic text detection

### Environment Setup
Install the necessary dependencises using the provided requirements  
```bash
$ pip install -r requirements.txt
```

Add .env file for using OpenAI API
```.env
OPENAI_API_KEY= <Your OpenAPI Key>
```
Git colne [G2P](https://github.com/seongmin-mun/KoG2Padvanced.git)
```bash
$ git clone https://github.com/seongmin-mun/KoG2Padvanced.git
```

### Augmentation

```bash
$ python augmentation.py
```

### Classification 
#### Train
Modify the `classification/train_config.py` file.   
```bash
$ cd classification
$ python train.py
```

#### Evaluation
Modify the `classification/eval_config.py` file.   
```bash
$ cd classification
$ python eval.py
```





