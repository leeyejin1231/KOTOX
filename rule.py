import openai
import random
import json
import hgtk
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("API_KEY")


class Obfuscation:
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
        with open("rule/iconic_dictionary.json", "r") as f:
            self.iconic_dict = json.load(f)

    def text_swap(self, text: str) -> str:
        """
        2-A. 야민
        """
        for i in range(len(text)):
            if text[i] in self.iconic_dict["yamin_dict"].keys():
                text[i] = random.choice(self.iconic_dict["yamin_dict"][text[i]])

        return text

    def gana_swap(self, text: str) -> str:
        """
        2-A. 가나
        """
        for i in range(len(text)):
            if text[i] in self.iconic_dict["gana_dict"].keys():
                text[i] = random.choice(self.iconic_dict["gana_dict"][text[i]])
        return text

    def consonant_swap(self, text: str) -> str:
        """
        2-A. 자음, 모음
        """
        result = [text[i] for i in range(len(text))]
        for i in range(len((text))):
            cho, jung, jong = hgtk.letter.decompose(result[i])
            if jung+jong in self.iconic_dict["vowel_dict"].keys():
                text[i] = cho+random.choice(self.iconic_dict["vowel_dict"][jung+jong])
            elif jung in self.iconic_dict["vowel_dict"].keys():
                text[i] = cho+random.choice(self.iconic_dict["vowel_dict"][jung])+jong
            elif cho in self.iconic_dict["consonant_dict"].keys():
                text[i] = random.choice(self.iconic_dict["consonant_dict"][cho])+jung+jong

        return text

    def rotation_90_swap(self, text: str) -> str:
        """
        2-B. 90도 회전
        """
        for value in self.iconic_dict["rotation_90_dict"].values():
            if value in text:
                text = text.replace(value, random.choice(self.iconic_dict["rotation_90_dict"][value]))
        return text

    def rotation_180_swap(self, text: str) -> str:
        """
        2-B. 180도 회전
        """
        for value in self.iconic_dict["rotation_180_dict"].values():
            if value in text:
                text = text.replace(value, random.choice(self.iconic_dict["rotation_180_dict"][value]))
        return text

    def compression_swap(self, text: str) -> str:
        """
        2-C. 압축
        """
        for value in self.iconic_dict["compression_dict"].values():
            if value in text:
                text = text.replace(value, random.choice(self.iconic_dict["compression_dict"][value]))
        return text


### 3. 표기법적 접근
class TransliterationalObfuscation:
    def __init__(self):
        with open("rule/transliterational_dictionary.json", "r") as f:
            self.transliterational_dict = json.load(f)  
            self.client = openai.OpenAI(api_key=API_KEY)

    def iconic_swap(self, text: str) -> str:
        """
        3-A. 음차
        """
        for i in range(len(text)):
            if text[i] in self.transliterational_dict["chinese_iconic_dict"].keys():
                text[i] = random.choice(self.transliterational_dict["chinese_iconic_dict"][text[i]])
        return text

    def number_swap(self, text: str) -> str:
        """
        3-B. 표기 대치
        """ 
        for i in range(len(text)):
            if text[i] in self.transliterational_dict["number_dict"].keys():
                text[i] = random.choice(self.transliterational_dict["number_dict"][text[i]])
        return text

    def meaning_dict(self, text: str) -> str:
        """
        3-B. 표기 대치
        """ 
        for i in range(len(text)):
            if text[i] in self.transliterational_dict["meaning_dict"].keys():
                text[i] = random.choice(self.transliterational_dict["meaning_dict"][text[i]])
        return text


# 4. 기호 추가
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
        self.punctuation = ['‥', '…', '、', '。', '．', '¿', '？']
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


# 테스트 함수
def test_symbol_addition():
    """
    기호 추가 함수들을 테스트하는 함수
    """
    symbol_adder = SymbolAddition()
    test_text = "사랑해요 나를 사랑해줘"
    
    print("원본 텍스트:", test_text)
    print("\n=== 개별 함수 테스트 ===")
    print("하트 추가:", symbol_adder.add_hearts(test_text))
    print("별 추가:", symbol_adder.add_stars(test_text))
    print("원형 기호 추가:", symbol_adder.add_circles(test_text))
    print("괄호 추가:", symbol_adder.add_brackets(test_text))
    print("구두점 추가:", symbol_adder.add_punctuation(test_text))
    print("감정 기호 추가:", symbol_adder.add_emotions(test_text))
    print("장식 추가:", symbol_adder.add_decorations(test_text))
    print("특수 문자 추가:", symbol_adder.add_special_chars(test_text))
    
    print("\n=== 종합 기호 추가 ===")
    print("종합 결과:", symbol_adder.comprehensive_symbol_addition(test_text))

if __name__ == "__main__":
    test_symbol_addition()

