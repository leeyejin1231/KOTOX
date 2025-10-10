from pickletools import read_uint1
import hgtk
import random
import json
import requests
import re
from bs4 import BeautifulSoup
from urllib.parse import quote
from time import sleep
from G2P.KoG2Padvanced import KoG2Padvanced

DEFAULT_COMPOSE_CODE = "ᴥ"

class Processing:
    def __init__(self):
        with open("./rules/replace.json", "r") as f:
            self.replace_dict = json.load(f)
        self.last_replace_map = {}
        for i in ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅇ"]:
            self.last_replace_map[i] = []
        for key in self.replace_dict["real_sound_map"]:
            self.last_replace_map[self.replace_dict["real_sound_map"][key]].append(key)
    
    # 1-A 대치
    ## 초성 예사소리 -> 된소리, 거센소리 대치
    def first_power_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    continue
                if cho in self.replace_dict["power_replace_map"]:
                    candidate = random.choice(self.replace_dict["power_replace_map"][cho])
                    result.append(hgtk.letter.compose(candidate,jung,jong))
                else:
                    result.append(hgtk.letter.compose(cho,jung,jong))
            else:
                result.append(char)
        return ''.join(result) 

    ## 초성 된소리, 거센소리 -> 예사소리 대치
    def reverse_first_power_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                if cho in self.replace_dict["reverse_power_replace_map"]:
                    result.append(hgtk.letter.compose(random.choice(self.replace_dict["reverse_power_replace_map"][cho]), jung, jong))
                else:
                    result.append(hgtk.letter.compose(cho, jung, jong))
            else:
                result.append(char)
        return ''.join(result)

    ## 모음 대치
    def vowel_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                if jung in self.replace_dict["vowel_replace_map"]:
                    result.append(hgtk.letter.compose(cho, random.choice(self.replace_dict["vowel_replace_map"][jung]), jong))
                else:
                    result.append(hgtk.letter.compose(cho, jung, jong))
            else:
                result.append(char)
        return ''.join(result)
    
    ## 받침 대치
    def last_replace(self, input_span):
        result = []
        for char in list(input_span):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                if jong != '' and jong in self.replace_dict["real_sound_map"]:
                    new_jong = random.choice(self.last_replace_map[self.replace_dict["real_sound_map"][jong]])
                    result.append(hgtk.letter.compose(cho, jung, new_jong))
                else:
                    result.append(hgtk.letter.compose(cho, jung, jong))
            else:
                result.append(char)
        return ''.join(result)

    ## 음운 변동 반영
    def sound_like_replace(self, input_span):
        # finditer로 매칭된 부분의 위치를 정확히 파악
        matches = list(re.finditer(r'[가-힣]+', input_span))
        if matches:
            # 뒤에서부터 바꿔야 인덱스가 꼬이지 않음
            result_text = input_span
            for match in reversed(matches):
                start, end = match.span()
                matched_text = match.group()
                # print(f"Matched: {matched_text} at {start}-{end}")
                converted_korean = KoG2Padvanced(matched_text)
                result_text = result_text[:start] + converted_korean + result_text[end:]
            return result_text
        else:
            return input_span
        
        # encoded_word = quote(input_span.encode("euc-kr"))
        # wait_time = [1, 2, 3, 4, 5]
        # url = f"https://pronunciation.cs.pusan.ac.kr/pronunc2.asp?text1={encoded_word}&submit1=확인하기"
        # sleep(random.choice(wait_time))
        # response = requests.get(url)
        # if response.status_code == 200:
        #     response.encoding = "euc-kr"
        #     soup = BeautifulSoup(response.text, "html.parser")
        #     target = soup.select("td.td2")
        #     try:
        #         return target[2].get_text(strip=True)
        #     except Exception as e:
        #         print(f"================error: {e}")
        #         print(f"================input_span: {input_span}")
        #         return input_span
        #     return target[2].get_text(strip=True)
        # else:
        #     return input_span

    # 1-C 연음
    ## 연음
    def continue_sound(self, input_span):
        result = []
        chars = list(input_span)
        flag = False
        
        for i, char in enumerate(chars):
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                if flag:
                    flag = False
                    continue
                
                # Check if there's a next character and if current character has final consonant
                if i < len(chars) - 1 and jong != '' and hgtk.checker.is_hangul(chars[i + 1]):
                    next_cho, next_jung, next_jong = hgtk.letter.decompose(chars[i + 1])
                    if next_jung == '' or next_cho == '':
                        result.append(char)
                        continue

                    # Create the combination pattern
                    combination = jong + 'ᴥ' + next_cho
                    
                    if combination in self.replace_dict["continue_sound_map"]:
                        # Apply continue sound transformation
                        new_combination = self.replace_dict["continue_sound_map"][combination]
                        # print(f"new_next_cho: {cho}, next_jung: {jung}, next_jong: {jong}")
                        
                        new_cur_jong = new_combination.split('ᴥ')[0]
                        new_next_cho = new_combination.split('ᴥ')[1]

                        result.append(hgtk.letter.compose(cho, jung, new_cur_jong))
                        result.append(hgtk.letter.compose(new_next_cho, next_jung, next_jong))
                        
                        # Skip the next character as it's already processed
                        flag = True
                    else:
                        result.append(char)
                else:
                    result.append(char)
            else:
                result.append(char)
        
        if ''.join(result) == input_span:
            return self.reverse_continue_sound(input_span)

        return ''.join(result)

    ## 역연음
    def reverse_continue_sound(self, input_span):
        result = []
        chars = list(input_span)
        
        for i, char in enumerate(chars):
            if chars[i] is None:  # Skip already processed characters
                continue
                
            if hgtk.checker.is_hangul(char):
                cho, jung, jong = hgtk.letter.decompose(char)
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                # Check if there's a next character
                if i < len(chars) - 1 and chars[i + 1] is not None and hgtk.checker.is_hangul(chars[i + 1]):
                    next_cho, next_jung, next_jong = hgtk.letter.decompose(chars[i + 1])
                    if next_jung == '' or next_cho == '':
                        result.append(char)
                        continue
                
                    
                    # Create the combination pattern for reverse continue sound
                    combination = cho + 'ᴥ' + next_cho
                    
                    # Check with batchim map first
                    if hgtk.checker.has_batchim(char) and combination in self.replace_dict["reverse_continue_sound_with_batchim_map"]:
                        candidate = self.replace_dict["reverse_continue_sound_with_batchim_map"][combination]
                        new_next_cho = 'ㅇ'
                        new_jong = candidate.split('ᴥ')[0]
                        new_next_cho = candidate.split('ᴥ')[1]
                        result.append(hgtk.letter.compose(cho, jung, new_jong))
                        result.append(hgtk.letter.compose(new_next_cho, next_jung, next_jong))
                        
                        # Skip the next character as it's already processed
                        chars[i + 1] = None
                    # Check without batchim map
                    elif not hgtk.checker.has_batchim(char) and combination in self.replace_dict["reverse_continue_sound_without_batchim_map"]:
                        candidate = self.replace_dict["reverse_continue_sound_without_batchim_map"][combination]
                        new_next_cho = 'ㅇ'
                        new_jong = candidate.split('ᴥ')[0]
                        new_next_cho = candidate.split('ᴥ')[1]
                        result.append(hgtk.letter.compose(cho, jung, new_jong))
                        result.append(hgtk.letter.compose(new_next_cho, next_jung, next_jong))
                        
                        # Skip the next character as it's already processed
                        chars[i + 1] = None
                    else:
                        result.append(char)
                else:
                    result.append(char)
            else:
                result.append(char)
        
        return ''.join(result)

    # # 1-D
    # ## 탈락
    # def elision(self, input_span):
    #     input_span = list(input_span)
    #     for i in range(len(input_span)):
    #         if hgtk.checker.is_hangul(input_span[i]):
    #             cho, jung, jong = hgtk.letter.decompose(input_span[i])
    #             input_span[i] = hgtk.letter.compose(cho, jung)
        
    #     return "".join(input_span)
        

if __name__ == "__main__":
    processing = Processing()
    
    # print("=== 기본 테스트 ===")
    # print("first_power_replace:", processing.first_power_replace("김밥을"))
    # print("vowel_replace:", processing.vowel_replace("팰리스"))
    # print("vowel_replace:", processing.vowel_replace("해외"))
    # print("last_replace:", processing.last_replace("학교에"))
    # print("sound_like_replace:", processing.sound_like_replace("짓이가"))
    # print("sound_like_replace:", processing.sound_like_replace("물난리가"))
    # print("continue_sound:", processing.continue_sound("짓이가"))
    # print("continue_sound:", processing.continue_sound("연음"))
    # print("continue_sound:", processing.continue_sound("닭을"))
    # print("continue_sound:", processing.continue_sound("발아"))
    # print("continue_sound:", processing.continue_sound("밟아"))
    # print("reverse_continue_sound:", processing.reverse_continue_sound("지시가"))
    # print("reverse_continue_sound:", processing.reverse_continue_sound("여늠"))
    # print("reverse_continue_sound:", processing.reverse_continue_sound("피자나라"))
    # print("reverse_continue_sound:", processing.reverse_continue_sound("치킨공주"))
    
    # print("\n=== 코너케이스 테스트 ===")
    
    # # 1. 빈 문자열
    # print("\n--- 빈 문자열 테스트 ---")
    # print("first_power_replace(''):", processing.first_power_replace(""))
    # print("vowel_replace(''):", processing.vowel_replace(""))
    # print("last_replace(''):", processing.last_replace(""))
    # print("continue_sound(''):", processing.continue_sound(""))
    # print("reverse_continue_sound(''):", processing.reverse_continue_sound(""))
    
    # # 2. 한 글자만
    # print("\n--- 한 글자 테스트 ---")
    # print("first_power_replace('김'):", processing.first_power_replace("김"))
    # print("vowel_replace('가'):", processing.vowel_replace("가"))
    # print("last_replace('강'):", processing.last_replace("강"))
    # print("continue_sound('김'):", processing.continue_sound("김"))
    # print("reverse_continue_sound('가'):", processing.reverse_continue_sound("가"))
    
    # # 3. 한글이 아닌 문자 포함
    # print("\n--- 한글+영문+숫자+특수문자 혼합 ---")
    # test_mixed = "안녕Hello123!@#"
    # print(f"first_power_replace('{test_mixed}'):", processing.first_power_replace(test_mixed))
    # print(f"vowel_replace('{test_mixed}'):", processing.vowel_replace(test_mixed))
    # print(f"last_replace('{test_mixed}'):", processing.last_replace(test_mixed))
    # print(f"continue_sound('{test_mixed}'):", processing.continue_sound(test_mixed))
    # print(f"reverse_continue_sound('{test_mixed}'):", processing.reverse_continue_sound(test_mixed))
    
    # # 4. 받침이 있는/없는 글자들
    # print("\n--- 받침 테스트 ---")
    # batchim_tests = ["가나다", "강남동", "학교에", "책상위", "물병에", "신발을"]
    # for test in batchim_tests:
    #     print(f"last_replace('{test}'):", processing.last_replace(test))
    #     print(f"continue_sound('{test}'):", processing.continue_sound(test))
    #     print(f"reverse_continue_sound('{test}'):", processing.reverse_continue_sound(test))
    
    # # 5. 연음 테스트 케이스들
    # print("\n--- 연음 특수 케이스 ---")
    # liaison_tests = [
    #     "닭을", "밟아", "읽어", "앉아", "젊은",  # 받침+ㅇ
    #     "가나다", "마바사", "자차카",  # 받침 없음
    #     "ㅇㅇㅇ", "ㄱㄴㄷ",  # 자음만
    #     "아이유", "이어서", "우유를"  # 모음 시작
    # ]
    # for test in liaison_tests:
    #     print(f"continue_sound('{test}'):", processing.continue_sound(test))
    #     print(f"reverse_continue_sound('{test}'):", processing.reverse_continue_sound(test))
    
    # # 6. 긴 문장 테스트
    # print("\n--- 긴 문장 테스트 ---")
    # long_sentence = "안녕하세요 저는 한국어를 공부하고 있는 학생입니다. 오늘 날씨가 정말 좋네요!"
    # print(f"first_power_replace: {processing.first_power_replace(long_sentence)}")
    # print(f"vowel_replace: {processing.vowel_replace(long_sentence)}")
    # print(f"last_replace: {processing.last_replace(long_sentence)}")
    
    # # 7. 특수한 한글 문자들
    # print("\n--- 특수 한글 문자 ---")
    # special_hangul = "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ"
    # print(f"first_power_replace('{special_hangul}'):", processing.first_power_replace(special_hangul))
    # print(f"vowel_replace('{special_hangul}'):", processing.vowel_replace(special_hangul))
    
    # # 8. 반복 실행 테스트 (랜덤성 확인)
    # print("\n--- 랜덤성 테스트 (3회 반복) ---")
    # random_test = "김밥을"
    # for i in range(3):
    #     print(f"first_power_replace #{i+1}:", processing.first_power_replace(random_test))
    #     print(f"vowel_replace #{i+1}:", processing.vowel_replace(random_test))
    #     print(f"last_replace #{i+1}:", processing.last_replace(random_test))
    
    # 9. 웹 API 테스트 (sound_like_replace)
    print("\n--- sound_like_replace 테스트 ---")
    web_tests = ["짓이가", "물난리가", "학교에", "책상위", "안녕하세요", "ㅋ", "abc", "    d", "!안녕!!ㅋ", "!안녕하!$안녕,안녕!!ㅋ하세요, 김밥,김밥이"]
    for test in web_tests:
        print(f"sound_like_replace('{test}'):", processing.sound_like_replace(test))
    
    # # 10. 에러 케이스 시뮬레이션
    # print("\n--- 에러 케이스 시뮬레이션 ---")
    # error_cases = [
    #     " ",  # 공백만
    #     "!@#$%^&*()",  # 특수문자만
    #     "123456789",  # 숫자만
    #     "Hello World",  # 영문만
    #     "가나다라마바사아자차카타파하" * 10,  # 매우 긴 문자열
    # ]
    # for test in error_cases:
    #     print(f"continue_sound('{test[:20]}...'):", processing.continue_sound(test))
    #     print(f"reverse_continue_sound('{test[:20]}...'):", processing.reverse_continue_sound(test))
    
    # print("\n=== 모든 테스트 완료 ===")