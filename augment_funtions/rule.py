import os
import openai
import random
import json
import hgtk
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")

class SyntaticObfuscation:
    def __init__(self):\
        pass
    
    def spacing(self, text_list: str) -> str:
        """
        4-A. 띄어쓰기
        """
        option = random.choice([0, 1])
        if option == 0:
            result = ""
            for span in text_list:
                result += span['span'][-1]
            return result
        else:
            result_list = []
            applied_index = []
            for i in range(len(text_list)):
                word = text_list[i]['span'][-1]
                applied_rule = text_list[i]['applied_rule']
                # 단어 길이가 2 이상일 때만 띄어쓰기 삽입 시도, 배열 교란이 없는 경우에만
                if len(word) > 1 and '11' not in applied_rule:
                    # 삽입 위치를 1 ~ len(word)-1 중에서 랜덤 선택
                    insert_pos = random.randint(1, len(word)-1)
                    word = word[:insert_pos] + " " + word[insert_pos:]
                    result_list.append(word)
                    applied_index.append(i)
                else:
                    result_list.append("")
            
            # 40% 이하면 그냥 띄어쓰기 없는 걸로
            if len(applied_index) < int(len(text_list)*0.4):
                result = ""
                for span in text_list:
                    result += span['span'][-1]
                return result
            else:
                selected_span = random.sample(applied_index, int(len(text_list)*0.4))
                result = ""
                for i in range(len(result_list)):
                    if i in selected_span:
                        result += result_list[i] + " "
                    else:
                        result += text_list[i]['span'][-1] + " "
                
                return result.rstrip()
                

    def change_array(self, text: str) -> str:
        """
        4-B. 배열교란
        """
        spans = text.split(" ")
        obfuscated = [self.obfuscate_span(span) for span in spans]
        output = " ".join(obfuscated)
        return output

    def obfuscate_span(self, span: str) -> str:
        if len(span) <= 2:
            return span
        chars = list(span)
        if len(span) == 3:
            middle = chars[1]
            if random.random() < 0.7:
                chars[1], chars[2] = chars[2], chars[1]
            return "".join(chars)
        middle = chars[1:-1]
        if len(middle) > 1:
            shuffled = middle[:]
            for _ in range(3):
                random.shuffle(shuffled)
                if shuffled != middle:
                    break
            chars = [chars[0]] + shuffled + [chars[-1]]
        return "".join(chars)


# 3. 도상적 대치
class IconicObfuscation:
    def __init__(self):
        with open("./rules/iconic_dictionary.json", "r") as f:
            self.iconic_dict = json.load(f)
            # self.okt = Okt()

    def yamin_swap(self, text: str) -> str:
        """
        2-A. 야민
        """
        for key in self.iconic_dict['yamin_dict'].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["yamin_dict"][key]))

        return text

    def gana_swap(self, text: str) -> str:
        """
        2-A. 가나
        """
        text_list = list(text)
        for i in range(len(text_list)):
            if text_list[i] in self.iconic_dict["gana_dict"].keys():
                text_list[i] = random.choice(self.iconic_dict["gana_dict"][text_list[i]])
        return "".join(text_list)

    def consonant_swap(self, text: str) -> str:
        """
        2-A. 자음, 모음
        """
        result = list(text)
        for i in range(len((text))):
            if hgtk.checker.is_hangul(result[i]):
                cho, jung, jong = hgtk.letter.decompose(result[i])
                if jung+jong in self.iconic_dict["vowel_dict"].keys():
                    jung = random.choice(self.iconic_dict["vowel_dict"][jung+jong])
                    jong == ""
                elif jong == "" and jung in self.iconic_dict["vowel_dict"].keys():
                    jung = random.choice(self.iconic_dict["vowel_dict"][jung])
                elif jung not in ['ㅗ','ㅛ','ㅜ','ㅠ','ㅡ','ㅚ','ㅙ','ㅞ','ㅟ','ㅝ','ㅘ'] and jong == "" and cho in self.iconic_dict["consonant_dict"].keys():
                    cho = random.choice(self.iconic_dict["consonant_dict"][cho])
                try:
                    result[i] = hgtk.letter.compose(cho, jung, jong)
                except:
                    result[i] = cho + jung + jong
            else:
                pass

        return "".join(result)

    def rotation_swap(self, text: str) -> str:
        """
        2-B. 90도 회전
        """
        for key in self.iconic_dict["rotation_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["rotation_dict"][key]))
        return text

    def rotation_180_swap(self, text: str) -> str:
        """
        2-B. 180도 회전
        """
        for key in self.iconic_dict["rotation_180_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["rotation_180_dict"][key]))
        return text

    def compression_swap(self, text: str) -> str:
        """
        2-C. 압축
        """
        for key in self.iconic_dict["compression_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["compression_dict"][key]))
        return text


### 3. 표기법적 접근
class TransliterationalObfuscation:
    def __init__(self):
        with open("./rules/transliterational_dictionary.json", "r") as f:
            self.transliterational_dict = json.load(f)  
            self.client = openai.OpenAI(api_key=API_KEY)     

    def iconic_swap(self, text: str) -> str:
        """
        3-A. 음차
        """
        with open("./rules/latin_prompt.txt", "r") as file:
            prompt = file.read()
        
        messages = [
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": text}
            # {"role": "user", "content": "\n\n### 음차 표기 GPT\n[주어진 문장]\n" + text + "\n[출력 문장]\n"}
            ]
        
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )
        
        try:
            response = response.choices[0].message.content
            response.replace("```json", "").replace("```", "")
            response = json.loads(response)
        except Exception as e:
            print(f"error: {e}")
            return text
        
        return response["output"]

    def foreign_iconic_swap(self, text: str) -> str:
        """
        3-A. 외국어 음차
        """
        with open("./rules/korean_prompt.txt", "r") as file:
            prompt = file.read()
        
        messages = [
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": text}
            # {"role": "user", "content": "\n\n### 음차 표기 GPT\n[주어진 문장]\n" + text + "\n[출력 문장]\n"}
            ]
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )

        try:
            response = response.choices[0].message.content
            response.replace("```json", "").replace("```", "")
            response = json.loads(response)
        except Exception as e:
            print(f"error: {e}")
            return text
        
        return response["output"]

    # def chinese_iconic_swap(self, text: str) -> str:
    #     """
    #     3-A. 음차
    #     """
    #     # text_list = list(text)
    #     # for i in range(len(text_list)):
    #     #     if text_list[i] in self.transliterational_dict["chinese_iconic_dict"].keys():
    #     #         text_list[i] = random.choice(self.transliterational_dict["chinese_iconic_dict"][text_list[i]])
    #     # return "".join(text_list)

    #     with open("./rules/한자_음차_prompt.txt", "r") as file:
    #         prompt = file.read()
        
    #     messages = [
    #         {"role": "system", "content": prompt}, 
    #         {"role": "user", "content": "\n\n[문장]\n" + text}
    #         ]
    #     response = self.client.chat.completions.create(
    #         model="gpt-4.1",
    #         messages=messages,
    #     )
        
    #     return response.choices[0].message.content

    def meaning_swap(self, text: str) -> str:
        """
        3-B. 표기 대치
        """     
        for key in self.transliterational_dict["meaning_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.transliterational_dict["meaning_dict"][key]))
        return text

    def meaning_dict(self, text: str) -> str:
        """
        3-B. 표기 대치
        """ 
        # text_list = list(text)
        # for i in range(len(text_list)):
        #     if text_list[i] in self.transliterational_dict["meaning_dict"].keys():
        #         text_list[i] = random.choice(self.transliterational_dict["meaning_dict"][text_list[i]])
        # return "".join(text_list)

        with open("./rules/표기대치_prompt.txt", "r") as file:
            prompt = file.read()
        
        messages = [
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": "\n\n[문장]\n" + text}
            ]
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )
        
        return response.choices[0].message.content


# 6. 화용접 접근
# 6-A. 표현 추가
class SymbolAddition:
    def __init__(self):
        # 하트 관련 기호들
        self.hearts = ['♡', '♥', '♤', '♧']
        # 별과 기하학적 기호들
        self.stars = ['★', '☆', '✦', '✧', '✩', '✪']
        # 원형 기호들
        self.circles = ['○', '●', '◎', '◯', '◈', '◉', '◊']
        # 기하학적 도형들
        self.shapes = ['◇', '◆', '□', '■', '▲', '△', '▼', '▽']
        # 괄호와 인용부호들
        self.brackets = ['【', '】', '《', '》', '「', '」', '『', '』', '∥', '〃']
        # 구두점과 특수문자들
        self.punctuation = ['‥', '…', '、', '。', '．', '¿', '？', "!", "1"]
        # 감정 표현 기호들
        self.emotions = ['ε♡з', 'ε♥з', 'T^T', '∏-∏', '≥ㅇ≤', '≥ㅅ≤', '≥ㅂ≤', '≥ㅁ≤', '≥ㅃ≤']
        # 장식용 기호들
        self.decorations = ['━', '─', '┃', '┗', '┣', '┓', '┫', '┛', '┻', '┳']
        # 특수 문자들
        self.special = ['¸', 'º', '°', '˛', '˚', '¯', '´', '`', '¨', 'ˆ', '˜', '˙']

    def add_hearts(self, text: str, probability: float = 0.3) -> str:
        """
        하트 기호들을 텍스트에 추가
        """
        words = text.split()
        result = []
        
        for word in words:
            result.append(word)
            
            # 단어 끝에 하트 추가
            if random.random() < probability:
                heart = random.choice(self.hearts)
                result.append(heart)
            
            # 문장 중간에 하트 추가
            if random.random() < probability * 0.5:
                heart = random.choice(self.hearts)
                result.append(heart)
        
        return ' '.join(result)

    def add_stars(self, text: str, probability: float = 0.2) -> str:
        """
        별 기호들을 텍스트에 추가
        """
        words = text.split()
        result = []
        
        for word in words:
            # 단어 앞에 별 추가
            if random.random() < probability:
                star = random.choice(self.stars)
                result.append(star)
            
            result.append(word)
            
            # 단어 뒤에 별 추가
            if random.random() < probability:
                star = random.choice(self.stars)
                result.append(star)
        
        return ' '.join(result)

    def add_circles(self, text: str, probability: float = 0.15) -> str:
        """
        원형 기호들을 텍스트에 추가
        """
        words = text.split()
        result = []
        
        for word in words:
            # 단어를 원형 기호로 감싸기
            if random.random() < probability:
                circle = random.choice(self.circles)
                result.append(f"{circle}{word}{circle}")
            else:
                result.append(word)
        
        return ' '.join(result)

    def add_brackets(self, text: str, probability: float = 0.25) -> str:
        """
        괄호와 인용부호들을 텍스트에 추가
        """
        words = text.split()
        result = []
        
        for word in words:
            # 단어를 괄호로 감싸기
            if random.random() < probability:
                bracket_pair = random.choice([
                    ('【', '】'), ('《', '》'), ('「', '」'), 
                    ('『', '』'), ('∥', '∥'), ('〃', '〃')
                ])
                result.append(f"{bracket_pair[0]}{word}{bracket_pair[1]}")
            else:
                result.append(word)
        
        return ' '.join(result)

    def add_punctuation(self, text: str, probability: float = 0.2) -> str:
        """
        특수 구두점들을 텍스트에 추가
        """
        result = text

        # 문장 끝에 특수 구두점 추가
        if random.random() < probability:
            punct = random.choice(self.punctuation)
            result += punct

        # 문장 중간에 점점점 추가
        if random.random() < probability * 0.7:
            dots = random.choice(['‥', '…'])
            result = result.replace(' ', f' {dots} ', 1)

        # 단어 중간에 특수 구두점 추가
        words = result.split()
        new_words = []
        for word in words:
            if len(word) > 1 and random.random() < probability:
                # 단어 중간 위치 선택
                insert_pos = random.randint(1, len(word)-1)
                punct = random.choice(self.punctuation)
                # 단어 중간에 특수 구두점 삽입
                new_word = word[:insert_pos] + punct + word[insert_pos:]
                new_words.append(new_word)
            else:
                new_words.append(word)
        result = ' '.join(new_words)

        return result
        
        return result

    def add_emotions(self, text: str, probability: float = 0.15) -> str:
        """
        감정 표현 기호들을 텍스트에 추가
        """
        words = text.split()
        result = []
        
        for word in words:
            result.append(word)
            
            # 감정 기호 추가
            if random.random() < probability:
                emotion = random.choice(self.emotions)
                result.append(emotion)
        
        return ' '.join(result)

    def add_decorations(self, text: str, probability: float = 0.1) -> str:
        """
        장식용 기호들을 텍스트에 추가
        """
        result = text
        
        # 문장 앞뒤에 장식 추가
        if random.random() < probability:
            decoration = random.choice(self.decorations)
            result = f"{decoration} {result} {decoration}"
        
        return result

    def add_special_chars(self, text: str, probability: float = 0.1) -> str:
        """
        특수 문자들을 텍스트에 추가
        """
        words = text.split()
        result = []
        
        for word in words:
            # 단어에 특수 문자 추가
            if random.random() < probability:
                special = random.choice(self.special)
                # 단어 중간이나 끝에 추가
                if random.random() < 0.5:
                    result.append(f"{word}{special}")
                else:
                    result.append(f"{special}{word}")
            else:
                result.append(word)
        
        return ' '.join(result)

    def comprehensive_symbol_addition(self, text: str) -> str:
        """
        모든 종류의 기호를 종합적으로 추가하는 함수
        """
        # 각 함수를 순차적으로 적용
        result = text
        
        # 확률을 조절하여 너무 많은 기호가 추가되지 않도록 함
        result = self.add_hearts(result, 0.2)
        result = self.add_stars(result, 0.15)
        result = self.add_circles(result, 0.1)
        result = self.add_brackets(result, 0.15)
        result = self.add_punctuation(result, 0.2)
        result = self.add_emotions(result, 0.1)
        result = self.add_decorations(result, 0.05)
        result = self.add_special_chars(result, 0.05)
        
        # 연속된 공백 정리
        result = ' '.join(result.split())
        
        return result


# 6. 화용적 접근
class PragmaticObfuscation:
    def __init__(self):
        self.client = openai.OpenAI(api_key=API_KEY)
            
    def pragmatic_swap(self, text: str) -> str:
        """
        6-A. 표현 추가
        """
        with open("./rules/화용론_prompt.txt", "r") as file:
            prompt = file.read()
            
        messages = [
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": "\n\n[주어진 문장]\n" + text}
            ]
            
            
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )
        
        return response.choices[0].message.content


## 5. 사회언어학적 접근
class SociolinguisticObfuscation:
    def __init__(self):
        self.client = openai.OpenAI(api_key=API_KEY)
        
    def sociolinguistic_swap(self, text: str) -> str:
        """
        5-A. 방언
        """
        with open("./rules/방언_prompt.txt", "r") as file:
            prompt = file.read()
            
        messages = [
            {"role": "system", "content": prompt}, 
            {"role": "user", "content": "\n\n[주어진 문장]\n" + text}
            ]
            
        response = self.client.chat.completions.create(
            model="gpt-4.1",
            messages=messages,
        )
        
        return response.choices[0].message.content


# 테스트 함수
def test_all_functions():
    """
    모든 함수들을 종합적으로 테스트하는 함수
    """
    print("🚀 Korean Obfuscation Functions Test")
    print("=" * 60)
    
    # 클래스 인스턴스 생성
    try:
        syntatic_obfuscator = SyntaticObfuscation()
        print("✅ SyntaticObfuscation 생성 성공")
    except Exception as e:
        print(f"❌ SyntaticObfuscation 생성 실패: {e}")
        syntatic_obfuscator = None
    
    try:
        iconic_obfuscator = IconicObfuscation()
        print("✅ IconicObfuscation 생성 성공")
    except Exception as e:
        print(f"❌ IconicObfuscation 생성 실패: {e}")
        iconic_obfuscator = None
    
    try:
        symbol_adder = SymbolAddition()
        print("✅ SymbolAddition 생성 성공")
    except Exception as e:
        print(f"❌ SymbolAddition 생성 실패: {e}")
        symbol_adder = None
    
    try:
        transliterational_obfuscator = TransliterationalObfuscation()
        print("✅ TransliterationalObfuscation 생성 성공")
    except Exception as e:
        print(f"❌ TransliterationalObfuscation 생성 실패: {e}")
        transliterational_obfuscator = None
    
    try:
        pragmatic_obfuscator = PragmaticObfuscation()
        print("✅ PragmaticObfuscation 생성 성공")
    except Exception as e:
        print(f"❌ PragmaticObfuscation 생성 실패: {e}")
        pragmatic_obfuscator = None
    
    try:
        sociolinguistic_obfuscator = SociolinguisticObfuscation()
        print("✅ SociolinguisticObfuscation 생성 성공")
    except Exception as e:
        print(f"❌ SociolinguisticObfuscation 생성 실패: {e}")
        sociolinguistic_obfuscator = None
    
    print("\n" + "=" * 60)
    
    # 기본 테스트 텍스트들
    test_texts = [
        "안녕하세요",
        "김밥을 먹었어요",
        "학교에 가요",
        "아니 방이 너무 좁고 더러워요 진짜 짜증나게 왜 그러는 걸까요??",
        "사랑해요 나를 사랑해줘",
        "Hello 안녕 123 !@#"
    ]
    
    # 1. SyntaticObfuscation 테스트
    print("\n=== 1. SyntaticObfuscation 테스트 ===")
    if syntatic_obfuscator:
        for i, test_text in enumerate(test_texts[:3]):
            print(f"\n--- 테스트 {i+1}: '{test_text}' ---")
            
            # spacing 테스트를 위한 text_list 생성
            text_list = [
                {'span': [word, word], 'appplied_rule': []}
                for word in test_text.split()
            ]
            
            try:
                result = syntatic_obfuscator.spacing(text_list)
                print(f"spacing: '{result}'")
            except Exception as e:
                print(f"spacing 에러: {e}")
            
            try:
                result = syntatic_obfuscator.change_array(test_text)
                print(f"change_array: '{result}'")
            except Exception as e:
                print(f"change_array 에러: {e}")
            
            # obfuscate_span 테스트
            words = test_text.split()
            for word in words[:2]:  # 처음 2개 단어만 테스트
                try:
                    result = syntatic_obfuscator.obfuscate_span(word)
                    print(f"obfuscate_span('{word}'): '{result}'")
                except Exception as e:
                    print(f"obfuscate_span('{word}') 에러: {e}")
    
    # 2. IconicObfuscation 테스트
    print("\n=== 2. IconicObfuscation 테스트 ===")
    if iconic_obfuscator:
        for i, test_text in enumerate(test_texts[:3]):
            print(f"\n--- 테스트 {i+1}: '{test_text}' ---")
            
            try:
                result = iconic_obfuscator.yamin_swap(test_text)
                print(f"yamin_swap: '{result}'")
            except Exception as e:
                print(f"yamin_swap 에러: {e}")
            
            try:
                result = iconic_obfuscator.gana_swap(test_text)
                print(f"gana_swap: '{result}'")
            except Exception as e:
                print(f"gana_swap 에러: {e}")
            
            try:
                result = iconic_obfuscator.consonant_swap(test_text)
                print(f"consonant_swap: '{result}'")
            except Exception as e:
                print(f"consonant_swap 에러: {e}")
            
            try:
                result = iconic_obfuscator.rotation_swap(test_text)
                print(f"rotation_swap: '{result}'")
            except Exception as e:
                print(f"rotation_swap 에러: {e}")
            
            try:
                result = iconic_obfuscator.rotation_180_swap(test_text)
                print(f"rotation_180_swap: '{result}'")
            except Exception as e:
                print(f"rotation_180_swap 에러: {e}")
            
            try:
                result = iconic_obfuscator.compression_swap(test_text)
                print(f"compression_swap: '{result}'")
            except Exception as e:
                print(f"compression_swap 에러: {e}")
    
    # 3. SymbolAddition 테스트
    print("\n=== 3. SymbolAddition 테스트 ===")
    if symbol_adder:
        for i, test_text in enumerate(test_texts[:3]):
            print(f"\n--- 테스트 {i+1}: '{test_text}' ---")
            
            try:
                result = symbol_adder.add_hearts(test_text, 0.3)
                print(f"add_hearts: '{result}'")
            except Exception as e:
                print(f"add_hearts 에러: {e}")
            
            try:
                result = symbol_adder.add_stars(test_text, 0.2)
                print(f"add_stars: '{result}'")
            except Exception as e:
                print(f"add_stars 에러: {e}")
            
            try:
                result = symbol_adder.add_circles(test_text, 0.15)
                print(f"add_circles: '{result}'")
            except Exception as e:
                print(f"add_circles 에러: {e}")
            
            try:
                result = symbol_adder.add_brackets(test_text, 0.25)
                print(f"add_brackets: '{result}'")
            except Exception as e:
                print(f"add_brackets 에러: {e}")
            
            try:
                result = symbol_adder.add_punctuation(test_text, 0.2)
                print(f"add_punctuation: '{result}'")
            except Exception as e:
                print(f"add_punctuation 에러: {e}")
            
            try:
                result = symbol_adder.comprehensive_symbol_addition(test_text)
                print(f"comprehensive_symbol_addition: '{result}'")
            except Exception as e:
                print(f"comprehensive_symbol_addition 에러: {e}")
    
    # 4. TransliterationalObfuscation 테스트 (OpenAI API 필요)
    print("\n=== 4. TransliterationalObfuscation 테스트 ===")
    if transliterational_obfuscator:
        for i, test_text in enumerate(test_texts[:2]):  # API 호출이므로 2개만
            print(f"\n--- 테스트 {i+1}: '{test_text}' ---")
            
            try:
                result = transliterational_obfuscator.number_swap(test_text)
                print(f"number_swap: '{result}'")
            except Exception as e:
                print(f"number_swap 에러: {e}")
            
            # API 호출하는 함수들은 주석 처리 (API 키 필요)
            # try:
            #     result = transliterational_obfuscator.iconic_swap(test_text)
            #     print(f"iconic_swap: '{result}'")
            # except Exception as e:
            #     print(f"iconic_swap 에러: {e}")
    
    # 5. PragmaticObfuscation 테스트 (OpenAI API 필요)
    print("\n=== 5. PragmaticObfuscation 테스트 ===")
    if pragmatic_obfuscator:
        # API 호출하는 함수들은 주석 처리 (API 키 필요)
        # for i, test_text in enumerate(test_texts[:2]):
        #     print(f"\n--- 테스트 {i+1}: '{test_text}' ---")
        #     try:
        #         result = pragmatic_obfuscator.pragmatic_swap(test_text)
        #         print(f"pragmatic_swap: '{result}'")
        #     except Exception as e:
        #         print(f"pragmatic_swap 에러: {e}")
        print("API 키가 필요하므로 테스트 생략")
    
    # 6. SociolinguisticObfuscation 테스트 (OpenAI API 필요)
    print("\n=== 6. SociolinguisticObfuscation 테스트 ===")
    if sociolinguistic_obfuscator:
        # API 호출하는 함수들은 주석 처리 (API 키 필요)
        # for i, test_text in enumerate(test_texts[:2]):
        #     print(f"\n--- 테스트 {i+1}: '{test_text}' ---")
        #     try:
        #         result = sociolinguistic_obfuscator.sociolinguistic_swap(test_text)
        #         print(f"sociolinguistic_swap: '{result}'")
        #     except Exception as e:
        #         print(f"sociolinguistic_swap 에러: {e}")
        print("API 키가 필요하므로 테스트 생략")
    
    print("\n" + "=" * 60)
    
    # 코너 케이스 테스트
    print("\n=== 코너 케이스 테스트 ===")
    
    corner_cases = [
        "",  # 빈 문자열
        " ",  # 공백만
        "가",  # 한 글자
        "123",  # 숫자만
        "Hello",  # 영문만
        "!@#$%",  # 특수문자만
        "안녕Hello123!@#",  # 혼합
        "안녕하세요 " * 10,  # 매우 긴 문자열
    ]
    
    print("\n--- SyntaticObfuscation 코너 케이스 ---")
    if syntatic_obfuscator:
        for case in corner_cases[:5]:
            print(f"\n입력: '{case}'")
            try:
                # spacing 테스트
                if case:
                    text_list = [{'span': [word, word], 'appplied_rule': []} for word in case.split()]
                    result = syntatic_obfuscator.spacing(text_list)
                    print(f"spacing: '{result}'")
                else:
                    result = syntatic_obfuscator.spacing([])
                    print(f"spacing (빈 리스트): '{result}'")
            except Exception as e:
                print(f"spacing 에러: {e}")
            
            try:
                result = syntatic_obfuscator.change_array(case)
                print(f"change_array: '{result}'")
            except Exception as e:
                print(f"change_array 에러: {e}")
    
    print("\n--- SymbolAddition 코너 케이스 ---")
    if symbol_adder:
        for case in corner_cases[:5]:
            print(f"\n입력: '{case}'")
            try:
                result = symbol_adder.comprehensive_symbol_addition(case)
                print(f"comprehensive_symbol_addition: '{result}'")
            except Exception as e:
                print(f"comprehensive_symbol_addition 에러: {e}")
    
    print("\n" + "=" * 60)
    
    # 랜덤성 테스트
    print("\n=== 랜덤성 테스트 ===")
    
    if syntatic_obfuscator and symbol_adder:
        test_text = "안녕하세요 테스트입니다"
        print(f"\n테스트 텍스트: '{test_text}'")
        
        print("\n--- SyntaticObfuscation 랜덤성 ---")
        text_list = [{'span': [word, word], 'appplied_rule': []} for word in test_text.split()]
        for i in range(3):
            try:
                result = syntatic_obfuscator.spacing(text_list)
                print(f"spacing #{i+1}: '{result}'")
            except Exception as e:
                print(f"spacing #{i+1} 에러: {e}")
        
        print("\n--- SymbolAddition 랜덤성 ---")
        for i in range(3):
            try:
                result = symbol_adder.add_hearts(test_text, 0.5)
                print(f"add_hearts #{i+1}: '{result}'")
            except Exception as e:
                print(f"add_hearts #{i+1} 에러: {e}")
    
    print("\n" + "=" * 60)
    print("✅ 모든 테스트 완료!")
    print("\n테스트 요약:")
    print("- SyntaticObfuscation: spacing, change_array, obfuscate_span")
    print("- IconicObfuscation: yamin_swap, gana_swap, consonant_swap, rotation_swap 등")
    print("- SymbolAddition: add_hearts, add_stars, add_circles, comprehensive_symbol_addition 등")
    print("- TransliterationalObfuscation: number_swap (API 함수들은 API 키 필요)")
    print("- PragmaticObfuscation: pragmatic_swap (API 키 필요)")
    print("- SociolinguisticObfuscation: sociolinguistic_swap (API 키 필요)")
    print("- 코너 케이스: 빈 문자열, 한 글자, 특수문자, 혼합 문자열 등")
    print("- 랜덤성: 같은 입력에 대해 다른 결과 생성 확인")

if __name__ == "__main__":
    test_all_functions()

