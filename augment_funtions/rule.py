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
    
    def spacing(self, text: str) -> str:
        """
        4-A. 띄어쓰기
        """
        text = text.strip()
        out = []
        for i, ch in enumerate(text):
            out.append(ch)
            if 0xAC00 <= ord(ch) <= 0xD7A3:
                if i < len(text) - 1 and random.random() < 0.25:
                    out.append(" ")
        
        return "".join(out)

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

    def rotation_90_swap(self, text: str) -> str:
        """
        2-B. 90도 회전
        """
        for key in self.iconic_dict["rotation_90_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["rotation_90_dict"][key]))
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
        with open("./rules/음차_prompt.txt", "r") as file:
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

    def foreign_iconic_swap(self, text: str) -> str:
        """
        3-A. 외국어 음차
        """
        with open("./rules/외국어_음차_prompt.txt", "r") as file:
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

    def chinese_iconic_swap(self, text: str) -> str:
        """
        3-A. 음차
        """
        # text_list = list(text)
        # for i in range(len(text_list)):
        #     if text_list[i] in self.transliterational_dict["chinese_iconic_dict"].keys():
        #         text_list[i] = random.choice(self.transliterational_dict["chinese_iconic_dict"][text_list[i]])
        # return "".join(text_list)

        with open("./rules/한자_음차_prompt.txt", "r") as file:
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

    def number_swap(self, text: str) -> str:
        """
        3-B. 표기 대치
        """     
        for key in self.transliterational_dict["number_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.transliterational_dict["number_dict"][key]))
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
def test_symbol_addition():
    """
    기호 추가 함수들을 테스트하는 함수
    """
    symbol_adder = SymbolAddition()
    obfuscator = SyntaticObfuscation()
    iconic_obfuscator = IconicObfuscation()
    transliterational_obfuscator = TransliterationalObfuscation()
    pragmatic_obfuscator = PragmaticObfuscation()
    sociolinguistic_obfuscator = SociolinguisticObfuscation()

    test_text = "방이 너무 더러워요"
    # test_text = "아니 방이 너무 좁고 더러워요 진짜 짜증나게"
    # test_text = "사랑해요 나를 사랑해줘"

    # print("\n=== 종합 기호 추가 ===")
    # print("종합 결과:", symbol_adder.comprehensive_symbol_addition(test_text))

    # print("\n=== 배열 변경 ===")
    # print("띄어쓰기 추가 결과:", obfuscator.spacing(test_text))
    # print("배열 변경 결과:", obfuscator.change_array(test_text))

    # print("\n=== 도상적 대치 ===")
    # print("야민 결과:", iconic_obfuscator.yamin_swap(test_text))
    # print("가나 결과:", iconic_obfuscator.gana_swap(test_text))
    print("자음, 모음 결과:", iconic_obfuscator.consonant_swap("개새끼"))
    # print("90도 회전 결과:", iconic_obfuscator.rotation_90_swap(test_text))
    # print("180도 회전 결과:", iconic_obfuscator.rotation_180_swap(test_text))
    # print("압축 결과:", iconic_obfuscator.compression_swap(test_text))

    # print("\n=== 표기법적 접근 ===")
    # print("음차 결과:", transliterational_obfuscator.iconic_swap(test_text))
    # print("한자음차 결과:", transliterational_obfuscator.chinese_iconic_swap(test_text))
    # print("외국어 음차 결과:", transliterational_obfuscator.foreign_iconic_swap(test_text))
    # print("숫자표기 대치 결과:", transliterational_obfuscator.number_swap(test_text))
    # print("표기 대치 결과:", transliterational_obfuscator.meaning_dict(test_text))

    # print("\n=== 화용적 접근 ===")
    # print("화용적 접근 결과:", pragmatic_obfuscator.pragmatic_swap(test_text))

    # print("\n=== 사회언어학적 접근 ===")
    # print("방언 결과:", sociolinguistic_obfuscator.sociolinguistic_swap(test_text))

if __name__ == "__main__":
    test_symbol_addition()

