# KoObs (Korean Obscure)

한국어 텍스트 음운 첨가를 통한 난독화 시스템

## 개요

KoObs는 한국어의 음운학적 특성을 활용하여 텍스트를 변형하는 라이브러리입니다. 4가지 음운 첨가 규칙을 통해 한국어 텍스트를 읽기 어렵게 만들면서도 한국어 화자라면 해석 가능한 형태로 변환합니다.

## 설치

```bash
pip install -r requirements.txt
```

## 주요 기능

### 1. 반모음 첨가 (Semivowel Addition)

**구현 기준:**
- 단모음을 이중모음으로 변환
- 각 글자의 중성(모음)을 분석하여 적용 가능한 반모음 추가

**변환 규칙:**
```
ㅏ → ㅑ, ㅘ
ㅓ → ㅕ, ㅝ  
ㅗ → ㅛ
ㅜ → ㅠ
ㅡ → ㅢ
ㅣ → ㅟ
```

**예시:**
```
거품점수 → 겨품져수
해외여행 → 햬외여향
```

### 2. 초성 추가 (Initial Consonant Addition)

**구현 기준:**
- 앞 글자의 받침에서 추출한 자음을 뒤 글자의 초성에 추가
- 뒤 글자의 초성이 'ㅇ'인 경우에만 적용
- 복자음 받침의 경우 뒤쪽 자음을 활용

**변환 규칙:**
```
단자음: ㄱ→ㅎ, ㄴ→ㄴ, ㄷ→ㄷ, ㄹ→ㄹ, ㅁ→ㅁ, ㅂ→ㅂ, ㅅ→ㅅ
복자음: ㄶ→ㅎ, ㅄ→ㅅ, ㄳ→ㅅ, ㄵ→ㅈ, ㄺ→ㄱ, ㄻ→ㅁ, ㄼ→ㅂ, ㄽ→ㅅ, ㄾ→ㄷ, ㄿ→ㅂ, ㅀ→ㅎ
```

**예시:**
```
많이 → 많휘 (ㄱ + 약한 ㅎ)
침이 → 침미 (ㅁ 반복)
값이 → 갑시 (ㅄ에서 ㅅ 추출)
않을 → 안헐 (ㄶ에서 ㅎ 추출)
```

### 3. 랜덤 받침 추가 (Random Final Consonant Addition)

**구현 기준:**
- 받침이 없는 글자에 임의의 받침 추가
- 단자음과 복자음 비율을 조정 가능 (기본값: 복자음 20%)

**받침 목록:**
```
단자음: ㄱ, ㄴ, ㄷ, ㄹ, ㅁ, ㅂ, ㅅ, ㅇ, ㅈ, ㅊ, ㅋ, ㅌ, ㅍ, ㅎ
복자음: ㄲ, ㄳ, ㄵ, ㄶ, ㄺ, ㄻ, ㄼ, ㄽ, ㄾ, ㄿ, ㅀ, ㅄ
```

**예시:**
```
해외여행 → 핸외역행 (랜덤 받침 추가)
```

### 4. 적응형 받침 추가 (Adaptive Final Consonant Addition)

**구현 기준:**
- 받침이 없는 글자에 다음 글자의 초성을 참조하여 받침 추가
- 한국어 발음 규칙에 따른 자연스러운 변환

**변환 규칙:**
```
직접 매핑: ㄱ→ㄱ, ㄴ→ㄴ, ㄷ→ㄷ, ㄹ→ㄹ, ㅁ→ㅁ, ㅂ→ㅂ, ㅅ→ㅅ, ㅇ→ㅇ
발음 변환: ㅈ→ㄷ, ㅊ→ㄷ, ㅌ→ㄷ, ㅍ→ㅂ, ㅋ→ㄱ, ㅎ→ㅇ
쌍자음: ㄲ→ㄱ, ㄸ→ㄷ, ㅃ→ㅂ, ㅆ→ㅅ, ㅉ→ㄷ
```

**예시:**
```
호스트 → 홋스트 (ㅅ→ㅅ)
백화점 → 벡화점 (ㅋ→ㄱ)
자전거 → 잣전거 (ㅈ→ㄷ)
```

## 사용법

### 기본 사용법

```python
from phonetic_addition import korean_obscure

text = "안녕하세요"

# 개별 기능 적용
result1 = korean_obscure(text, semivowel=True)
result2 = korean_obscure(text, initial_consonant=True)
result3 = korean_obscure(text, final_consonant=True)
result4 = korean_obscure(text, adaptive_final_consonant=True)

# 복합 적용
result = korean_obscure(text, 
                       semivowel=True,
                       initial_consonant=True,
                       adaptive_final_consonant=True)
```

### 매개변수

- `ratio` (float): 청크 단위 적용 비율 (0.0~1.0, 기본값: 0.3)
- `double_consonant_ratio` (float): 복자음 사용 비율 (0.0~1.0, 기본값: 0.2)

```python
# 적용 비율 조정
result = korean_obscure(text, semivowel=True, ratio=0.5)

# 복자음 비율 조정
result = korean_obscure(text, final_consonant=True, double_consonant_ratio=0.5)
```

## 예시

### 입력 텍스트
```
해외여행 중 방문했던 숙박 시설이나 음식점 후기를 남길 때
```

### 출력 결과
```
반모음 첨가: 햬외여향 쥰 방문했뎬 수박 시서리냐 으식져 후기를 냠길 때
초성 추가: 해외여행 중 방문했던 숙박 시서리나 음시기저 후기를 남길 때
적응형 받침: 핻외열행 중 방뭊했떤 숙받 시설이냐 음식졈 후기를 남길 떼
복합 적용: 햬외열향 쥰 방뭊했뎬 숙받 시서리냐 으식져 후기를 냠길 떼
```

## 파일 구조

```
KoObs/
├── requirements.txt
├── phonetic_addition.py
├── README.md
└── test_examples/
```

## 의존성

- `hgtk`: 한글 자모 분해/조합
- `six`: Python 2/3 호환성

## Comment Section

### 초성 추가 기능에 대한 고민

현재 구현된 초성 추가 기능은 한국어의 연음 현상과 상당 부분 겹치는 특성을 가지고 있습니다. 연음은 자연스러운 한국어 발음 현상이므로, 이 기능을 난독화 목적으로 사용할 때 다음과 같은 고민이 있습니다:

1. **자연성 vs 난독화**: 연음은 실제 발음에서 자주 발생하므로 난독화 효과가 제한적일 수 있음
2. **적용 범위**: 모든 연음 가능 상황에 적용할지, 특정 조건에서만 적용할지 결정 필요
3. **다른 기능과의 조합**: 반모음 첨가나 받침 추가와 함께 사용할 때의 상호작용 고려

향후 버전에서는 이러한 자연성을 고려하여 초성 추가 기능의 적용 조건을 더욱 세밀하게 조정하거나, 선택적으로 제외할 수 있는 옵션을 추가하는 것을 고려하고 있습니다.

## 라이선스

MIT License

## 기여

버그 신고나 기능 제안은 GitHub Issues를 통해 해주세요.
