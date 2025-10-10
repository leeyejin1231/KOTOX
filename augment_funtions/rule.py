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
        2-A. 가나다
        """
        for key in self.iconic_dict['yamin_dict'].keys():
            if key in text:
                text = text.replace(key, random.choice(self.iconic_dict["yamin_dict"][key]))

        return text

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

    def meaning_swap(self, text: str) -> str:
        """
        3-B. 표기 대치
        """     
        for key in self.transliterational_dict["meaning_dict"].keys():
            if key in text:
                text = text.replace(key, random.choice(self.transliterational_dict["meaning_dict"][key]))
        return text


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
    
if __name__ == "__main__":
    print("=== 한국어 증강 모듈 ===")

