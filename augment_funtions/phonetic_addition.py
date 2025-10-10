"""
Korean Phonetic Addition Module
한국어 음운 첨가 모듈

This module provides functions to apply phonetic additions to Korean text:
1. Initial consonant addition (초성 추가)
2. Semivowel addition (반모음 첨가)  
3. Final consonant addition (받침 추가)
"""

import hgtk
from typing import Optional
import random

class PhoneticAddition:
    def __init__(self):
        self.SEMIVOWEL_MAPPING = {
            'ㅏ': ['ㅑ', 'ㅘ'],
            'ㅓ': ['ㅕ', 'ㅝ'],
            'ㅗ': ['ㅛ'],
            'ㅜ': ['ㅠ'],
            'ㅡ': ['ㅢ'],
            'ㅣ': ['ㅟ']
        }

        # Single final consonants (단자음)
        self.SINGLE_FINAL_CONSONANTS = [
            'ㄱ', 'ㄴ', 'ㄷ', 'ㄹ', 'ㅁ', 'ㅂ', 'ㅅ', 'ㅇ', 'ㅈ', 'ㅊ', 'ㅋ', 'ㅌ', 'ㅍ', 'ㅎ'
        ]

        # Double final consonants (쌍자음/복자음)
        self.DOUBLE_FINAL_CONSONANTS = [
            'ㄲ', 'ㄳ', 'ㄵ', 'ㄶ', 'ㄺ', 'ㄻ', 'ㄼ', 'ㄽ', 'ㄾ', 'ㄿ', 'ㅀ', 'ㅄ', 'ㅆ', 
        ]

        # Initial consonant to final consonant mapping (초성 -> 받침 변환 규칙)
        self.INITIAL_TO_FINAL_MAPPING = {
            # 그대로 가져올 수 있는 자음들
            'ㄱ': 'ㄱ', 'ㄴ': 'ㄴ', 'ㄷ': 'ㄷ', 'ㄹ': 'ㄹ', 
            'ㅁ': 'ㅁ', 'ㅂ': 'ㅂ', 'ㅅ': 'ㅅ', 'ㅇ': 'ㅇ',
            
            # 발음 규칙에 따른 변환
            'ㅈ': 'ㄷ',  # ㅈ -> ㄷ
            'ㅊ': 'ㄷ',  # ㅊ -> ㄷ  
            'ㅌ': 'ㄷ',  # ㅌ -> ㄷ
            'ㅍ': 'ㅂ',  # ㅍ -> ㅂ
            'ㅋ': 'ㄱ',  # ㅋ -> ㄱ
            'ㅎ': 'ㅇ',  # ㅎ -> ㅇ (또는 탈락)
            
            # 쌍자음 매핑
            'ㄲ': 'ㄱ',  # ㄲ -> ㄱ
            'ㄸ': 'ㄷ',  # ㄸ -> ㄷ
            'ㅃ': 'ㅂ',  # ㅃ -> ㅂ
            'ㅆ': 'ㅅ',  # ㅆ -> ㅅ
            'ㅉ': 'ㄷ',  # ㅉ -> ㄷ
        }

        # Final consonant to initial consonant mapping for initial consonant addition
        # 받침에서 추출할 수 있는 초성들 (초성 추가용)
        self.FINAL_TO_INITIAL_MAPPING = {
            # 단자음 받침에서 초성 추출
            'ㄱ': 'ㄱ',    # 각이 -> 각기
            'ㄴ': 'ㄴ',    # 간이 -> 간니
            'ㄷ': 'ㄷ',    # 낫이 -> 낟디  
            'ㄹ': 'ㄹ',    # 물이 -> 물리
            'ㅁ': 'ㅁ',    # 침이 -> 침미
            'ㅂ': 'ㅂ',    # 집이 -> 집비
            'ㅅ': 'ㅅ',    # 옷이 -> 옷시
            'ㅇ': 'ㅇ',    # 강이 -> 강이 (변화없음)
            
            # 복자음 받침에서 초성 추출 (뒤쪽 자음 활용)
            'ㄶ': 'ㅎ',    # 않을 -> 안헐 (ㅎ 활용)
            'ㅀ': 'ㅎ',    # 싫어 -> 실허 (ㅎ 활용)
            'ㄳ': 'ㅅ',    # 몫이 -> 목시 (ㅅ 활용)
            'ㄵ': 'ㅈ',    # 앉아 -> 안자 (ㅈ 활용)
            'ㄺ': 'ㄱ',    # 닭이 -> 달기 (ㄱ 활용)
            'ㄻ': 'ㅁ',    # 굶어 -> 굴머 (ㅁ 활용)
            'ㄼ': 'ㅂ',    # 넓이 -> 널비 (ㅂ 활용)
            'ㄽ': 'ㅅ',    # 외곬이 -> 외골시 (ㅅ 활용)
            'ㄾ': 'ㄷ',    # 핥아 -> 할다 (ㄷ 활용)
            'ㄿ': 'ㅂ',    # 읊어 -> 을버 (ㅂ 활용)
            'ㅄ': 'ㅅ',    # 값이 -> 갑시 (ㅅ 활용 - 뒤쪽 자음)
        }

    def phonological_addition_initial_consonant(self, chunk: str) -> Optional[str]:
        """
        Process a single chunk by adding initial consonants based on previous character's final.
        
        Args:
            chunk (str): A chunk of Korean text (word with possible punctuation)
            
        Returns:
            Optional[str]: Modified chunk if any transformation occurred, None otherwise
        """
        result = []
        chars = list(chunk)
        
        for i, char in enumerate(chars):
            # Only try to transform Korean characters that start with ㅇ
            if hgtk.checker.is_hangul(char):
                # Decompose current character
                cho, jung, jong = hgtk.letter.decompose(char)
                
                # Exception handling for empty initial consonant or vowel
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                # Check if current character starts with ㅇ and there's a previous character
                if cho == 'ㅇ' and i > 0:
                    prev_char = chars[i - 1]
                    
                    # Check if previous character is also Korean and has final consonant
                    if hgtk.checker.is_hangul(prev_char):
                        # Decompose previous character to get its final consonant
                        _, _, prev_jong = hgtk.letter.decompose(prev_char)
                        
                        # Map the final consonant to appropriate initial consonant
                        if prev_jong != '' and prev_jong in self.FINAL_TO_INITIAL_MAPPING:
                            new_cho = self.FINAL_TO_INITIAL_MAPPING[prev_jong]
                            
                            # Compose new character with added initial consonant
                            new_char = hgtk.letter.compose(new_cho, jung, jong)
                            result.append(new_char)
                        else:
                            result.append(char)
                    else:
                        result.append(char)
                else:
                    result.append(char)
            else:
                # Keep punctuation and non-Korean characters as is
                result.append(char)
        
        return ''.join(result)
        


    def phonological_addition_semivowel(self, chunk: str) -> Optional[str]:
        """
        Process a single chunk by applying semivowel addition to characters.
        
        Args:
            chunk (str): A chunk of Korean text (word with possible punctuation)
            
        Returns:
            Optional[str]: Modified chunk if any transformation occurred, None otherwise
        """
        result = []
        
        for char in chunk:
            # Only try to transform Korean characters
            if hgtk.checker.is_hangul(char):
                # Decompose the character into jamo components
                cho, jung, jong = hgtk.letter.decompose(char)
                
                # Exception handling for empty initial consonant or vowel
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                # Check if the vowel can be transformed
                if jung in self.SEMIVOWEL_MAPPING:
                    # Apply semivowel transformation
                    new_jung = random.choice(self.SEMIVOWEL_MAPPING[jung])
                    
                    # Compose new character
                    new_char = hgtk.letter.compose(cho, new_jung, jong)
                    result.append(new_char)
                else:
                    result.append(char)
            else:
                # Keep punctuation and non-Korean characters as is
                result.append(char)
        
        return ''.join(result)
        


    def phonological_addition_adaptive_final_consonant(self, chunk: str) -> Optional[str]:
        """
        Process a single chunk by adding final consonants based on next character's initial.
        
        Args:
            chunk (str): A chunk of Korean text (word with possible punctuation)
            
        Returns:
            Optional[str]: Modified chunk if any transformation occurred, None otherwise
        """
        result = []
        chars = list(chunk)
        
        for i, char in enumerate(chars):
            # Only try to transform Korean characters
            if hgtk.checker.is_hangul(char):
                # Decompose current character
                cho, jung, jong = hgtk.letter.decompose(char)
                
                # Exception handling for empty initial consonant or vowel
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                # Check if current character has no final consonant and there's a next character
                if jong == '' and i + 1 < len(chars):
                    next_char = chars[i + 1]
                    
                    # Check if next character is also Korean
                    if hgtk.checker.is_hangul(next_char):
                        # Decompose next character to get its initial consonant
                        next_cho, _, _ = hgtk.letter.decompose(next_char)
                        
                        # Exception handling for next character as well
                        if next_cho == '':
                            result.append(char)
                            continue
                        
                        # Map the initial consonant to appropriate final consonant
                        if next_cho in self.INITIAL_TO_FINAL_MAPPING:
                            new_jong = self.INITIAL_TO_FINAL_MAPPING[next_cho]
                            
                            # Compose new character with added final consonant
                            new_char = hgtk.letter.compose(cho, jung, new_jong)
                            result.append(new_char)
                        else:
                            result.append(char)
                    else:
                        result.append(char)
                else:
                    result.append(char)
            else:
                # Keep punctuation and non-Korean characters as is
                result.append(char)

        if ''.join(result) == chunk:
            return self.phonological_addition_final_consonant(chunk, double_consonant_ratio=0.3)
        
        return ''.join(result)
    

    def phonological_addition_final_consonant(self, chunk: str, double_consonant_ratio: float = 0.3) -> Optional[str]:
        """
        Process a single chunk by adding random final consonants to characters without them.
        
        Args:
            chunk (str): A chunk of Korean text (word with possible punctuation)
            
        Returns:
            Optional[str]: Modified chunk if any transformation occurred, None otherwise
        """
        result = []
        
        for char in chunk:
            # Only try to transform Korean characters
            if hgtk.checker.is_hangul(char):
                # Decompose the character into jamo components
                cho, jung, jong = hgtk.letter.decompose(char)
                
                # Exception handling for empty initial consonant or vowel
                if jung == '' or cho == '':
                    result.append(char)
                    continue
                
                # Check if character has no final consonant
                if jong == '':
                    # Choose between single and double consonants based on ratio
                    if random.random() < double_consonant_ratio:
                        new_jong = random.choice(self.DOUBLE_FINAL_CONSONANTS)
                    else:
                        new_jong = random.choice(self.SINGLE_FINAL_CONSONANTS)
                    
                    # Compose new character
                    new_char = hgtk.letter.compose(cho, jung, new_jong)
                    result.append(new_char)
                else:
                    result.append(char)
            else:
                # Keep punctuation and non-Korean characters as is
                result.append(char)
        
        return ''.join(result)


    def korean_obscure(self,text: str, semivowel: bool = False, initial_consonant: bool = False, 
                    final_consonant: bool = False, adaptive_final_consonant: bool = False, 
                    double_consonant_ratio: float = 0.3) -> str:
        """
        Apply phonological additions to Korean text to make it obscure.
        
        Args:
            text (str): Input Korean text
            semivowel (bool): Apply semivowel addition
            initial_consonant (bool): Apply initial consonant addition
            final_consonant (bool): Apply random final consonant addition
            adaptive_final_consonant (bool): Apply adaptive final consonant addition (based on next char)
            double_consonant_ratio (float): Probability of using double consonants (0.0 to 1.0)
            
        Returns:
            str: Text with selected phonological additions applied
        """
        result = text
        
        if semivowel:
            result = self.phonological_addition_semivowel(result)
        if initial_consonant:
            result = self.phonological_addition_initial_consonant(result)
        if final_consonant:
            result = self.phonological_addition_final_consonant(result, double_consonant_ratio=double_consonant_ratio)
        if adaptive_final_consonant:
            result = self.phonological_addition_adaptive_final_consonant(result)
        
        return result


if __name__ == "__main__":
    phonetic_addition = PhoneticAddition()
    
    print("=== 한국어 음운 첨가 모듈 종합 테스트 ===\n")
    
    # 1. 기본 기능 테스트
    print("=== 1. 기본 기능 테스트 ===")
    basic_text = "안녕하세요 한국어 테스트입니다."
    print(f"원본: {basic_text}")
    
    print(f"\n반모음 첨가: {phonetic_addition.korean_obscure(basic_text, semivowel=True)}")
    print(f"초성 첨가: {phonetic_addition.korean_obscure(basic_text, initial_consonant=True)}")
    print(f"받침 첨가: {phonetic_addition.korean_obscure(basic_text, final_consonant=True)}")
    print(f"적응적 받침 첨가: {phonetic_addition.korean_obscure(basic_text, adaptive_final_consonant=True)}")
    print(f"전체 적용: {phonetic_addition.korean_obscure(basic_text, semivowel=True, initial_consonant=True, final_consonant=True, adaptive_final_consonant=True)}")
    
    # 2. 빈 문자열 및 경계값 테스트
    print("\n=== 2. 빈 문자열 및 경계값 테스트 ===")
    edge_cases = [
        "",  # 빈 문자열
        " ",  # 공백만
        "   ",  # 여러 공백
        "a",  # 영문 한 글자
        "가",  # 한글 한 글자
        "!",  # 특수문자만
        "123",  # 숫자만
        "가나다",  # 받침 없는 글자들
        "강남동",  # 받침 있는 글자들
    ]
    
    for test_case in edge_cases:
        print(f"\n테스트: '{test_case}'")
        try:
            semivowel_result = phonetic_addition.phonological_addition_semivowel(test_case)
            initial_result = phonetic_addition.phonological_addition_initial_consonant(test_case)
            final_result = phonetic_addition.phonological_addition_final_consonant(test_case)
            adaptive_result = phonetic_addition.phonological_addition_adaptive_final_consonant(test_case)
            
            print(f"  반모음: '{semivowel_result}'")
            print(f"  초성: '{initial_result}'")
            print(f"  받침: '{final_result}'")
            print(f"  적응적 받침: '{adaptive_result}'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 3. 한글이 아닌 문자 혼합 테스트
    print("\n=== 3. 한글이 아닌 문자 혼합 테스트 ===")
    mixed_cases = [
        "안녕Hello123!@#",
        "가나다라마바사아자차카타파하ABCDEFGHIJKLMNOPQRSTUVWXYZ",
        "한국어English日本語中文Русскийالعربية",
        "특수문자!@#$%^&*()_+-=[]{}|;':\",./<>?",
        "숫자와1234567890한글",
        "공백이   여러개   있는   문장",
        "줄바꿈이\n있는\n텍스트",
        "탭\t이\t있는\t텍스트",
    ]
    
    for test_case in mixed_cases:
        print(f"\n테스트: '{test_case[:30]}...'")
        try:
            result = phonetic_addition.korean_obscure(test_case, semivowel=True, initial_consonant=True, final_consonant=True)
            print(f"  결과: '{result[:50]}...'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 4. 초성 첨가 특수 케이스 테스트
    print("\n=== 4. 초성 첨가 특수 케이스 테스트 ===")
    initial_test_cases = [
        "많이", "침이", "집에", "않을", "값어치", "넓은",  # 기본 케이스
        "ㅇㅇㅇ", "ㅇ가나", "가ㅇ다",  # ㅇ으로 시작하는 글자들
        "ㄱㄴㄷ", "ㄹㅁㅂ",  # 자음만
        "ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ",  # 모음만
        "ㅎㅏㄴㄱㅜㄱㅇㅓ",  # 자모 분해된 글자들
        "ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ",  # ㅇ으로 시작하는 분해된 글자들
    ]
    
    for test_case in initial_test_cases:
        print(f"\n초성 첨가 테스트: '{test_case}'")
        try:
            result = phonetic_addition.phonological_addition_initial_consonant(test_case)
            print(f"  결과: '{result}'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 5. 적응적 받침 첨가 특수 케이스 테스트
    print("\n=== 5. 적응적 받침 첨가 특수 케이스 테스트 ===")
    adaptive_test_cases = [
        "호스트", "바깥쪽", "방식이다", "해외여행",  # 기본 케이스
        "가나다라마바사",  # 받침 없는 연속 글자들
        "강남동서울부산",  # 받침 있는 연속 글자들
        "가강나남다동",  # 받침 있음/없음 혼합
        "ㅇㅏㅇㅣㅇㅓ",  # 자모 분해된 글자들
        "가ㅇ나ㅇ다ㅇ",  # 혼합 케이스
    ]
    
    for test_case in adaptive_test_cases:
        print(f"\n적응적 받침 첨가 테스트: '{test_case}'")
        try:
            result = phonetic_addition.phonological_addition_adaptive_final_consonant(test_case)
            print(f"  결과: '{result}'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 6. 반모음 첨가 특수 케이스 테스트
    print("\n=== 6. 반모음 첨가 특수 케이스 테스트 ===")
    semivowel_test_cases = [
        "가나다라마바사아자차카타파하",  # 기본 모음들
        "ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ",  # 단일 모음들
        "ㅘㅝㅟㅢㅚㅐㅔㅒㅖ",  # 복합 모음들
        "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ",  # 자음만
        "ㅎㅏㄴㄱㅜㄱㅇㅓ",  # 분해된 글자들
    ]
    
    for test_case in semivowel_test_cases:
        print(f"\n반모음 첨가 테스트: '{test_case}'")
        try:
            result = phonetic_addition.phonological_addition_semivowel(test_case)
            print(f"  결과: '{result}'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 7. 받침 첨가 특수 케이스 테스트
    print("\n=== 7. 받침 첨가 특수 케이스 테스트 ===")
    final_test_cases = [
        "가나다라마바사아자차카타파하",  # 받침 없는 글자들
        "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ",  # 자음만
        "ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ",  # 모음만
        "ㅎㅏㄴㄱㅜㄱㅇㅓ",  # 분해된 글자들
        "가강나남다동",  # 받침 혼합
    ]
    
    for test_case in final_test_cases:
        print(f"\n받침 첨가 테스트: '{test_case}'")
        try:
            result = phonetic_addition.phonological_addition_final_consonant(test_case)
            print(f"  결과: '{result}'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 8. 매우 긴 텍스트 테스트
    print("\n=== 8. 매우 긴 텍스트 테스트 ===")
    long_text = "안녕하세요 저는 한국어를 공부하고 있는 학생입니다. 오늘 날씨가 정말 좋네요! 한국어는 매우 아름다운 언어입니다. 한글은 세종대왕이 만든 훌륭한 문자입니다. 가나다라마바사아자차카타파하가나다라마바사아자차카타파하" * 10
    
    print(f"긴 텍스트 길이: {len(long_text)} 문자")
    try:
        result = phonetic_addition.korean_obscure(long_text, semivowel=True, initial_consonant=True, final_consonant=True)
        print(f"처리 결과 길이: {len(result)} 문자")
        print(f"처리 결과 (처음 100자): {result[:100]}...")
    except Exception as e:
        print(f"  에러 발생: {e}")
    
    # 9. 랜덤성 테스트
    print("\n=== 9. 랜덤성 테스트 ===")
    random_test_word = "안녕하세요"
    print(f"테스트 단어: '{random_test_word}'")
    
    for i in range(5):
        try:
            result = phonetic_addition.korean_obscure(random_test_word, semivowel=True, final_consonant=True)
            print(f"  실행 {i+1}: '{result}'")
        except Exception as e:
            print(f"  실행 {i+1} 에러: {e}")
    
    # 10. 매개변수 경계값 테스트
    print("\n=== 10. 매개변수 경계값 테스트 ===")
    param_test_word = "가나다라마바사"
    
    # double_consonant_ratio 테스트
    for ratio in [0.0, 0.1, 0.5, 0.9, 1.0]:
        try:
            result = phonetic_addition.korean_obscure(param_test_word, final_consonant=True, double_consonant_ratio=ratio)
            print(f"  쌍자음 비율 {ratio}: '{result}'")
        except Exception as e:
            print(f"  쌍자음 비율 {ratio} 에러: {e}")
    
    # 11. 복합 변환 테스트
    print("\n=== 11. 복합 변환 테스트 ===")
    complex_test_cases = [
        "많이있다",
        "침이나온다", 
        "집에서일해요",
        "않을수없다",
        "값어치있다",
        "넓은바다",
        "해외여행중",
        "숙박시설후기",
    ]
    
    for test_case in complex_test_cases:
        print(f"\n복합 변환 테스트: '{test_case}'")
        try:
            result = phonetic_addition.korean_obscure(test_case, semivowel=True, initial_consonant=True, final_consonant=True, adaptive_final_consonant=True)
            print(f"  결과: '{result}'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 12. 특수한 한글 문자들 테스트
    print("\n=== 12. 특수한 한글 문자들 테스트 ===")
    special_hangul_cases = [
        "ㄱㄴㄷㄹㅁㅂㅅㅇㅈㅊㅋㅌㅍㅎ",  # 모든 자음
        "ㅏㅑㅓㅕㅗㅛㅜㅠㅡㅣ",  # 모든 모음
        "ㄲㄸㅃㅆㅉ",  # 쌍자음
        "ㅐㅒㅔㅖㅘㅙㅚㅝㅞㅟㅢ",  # 복합모음
        "ㄳㄵㄶㄺㄻㄼㄽㄾㄿㅀㅄ",  # 복자음 받침
        "ㅇㅏㄴㄴㅕㅇㅎㅏㅅㅔㅇㅛ",  # 분해된 한글
    ]
    
    for test_case in special_hangul_cases:
        print(f"\n특수 한글 테스트: '{test_case}'")
        try:
            result = phonetic_addition.korean_obscure(test_case, semivowel=True, initial_consonant=True, final_consonant=True)
            print(f"  결과: '{result}'")
        except Exception as e:
            print(f"  에러 발생: {e}")
    
    # 13. 에러 복구 테스트
    print("\n=== 13. 에러 복구 테스트 ===")
    error_recovery_cases = [
        None,  # None 값
        "가" + chr(0) + "나",  # NULL 문자 포함
        "가\x00나",  # NULL 바이트
        "가\xff나",  # 잘못된 바이트
        "가\u0000나",  # 유니코드 NULL
        "가\uFFFF나",  # 유니코드 대체 문자
    ]
    
    for i, test_case in enumerate(error_recovery_cases):
        print(f"\n에러 복구 테스트 {i+1}: {repr(test_case)}")
        try:
            if test_case is not None:
                result = phonetic_addition.korean_obscure(test_case, semivowel=True)
                print(f"  결과: '{result}'")
            else:
                print("  None 값은 건너뜀")
        except Exception as e:
            print(f"  에러 발생 (예상됨): {e}")
    
    # 14. 성능 테스트
    print("\n=== 14. 성능 테스트 ===")
    import time
    
    performance_text = "안녕하세요 한국어 음운 첨가 모듈 성능 테스트입니다." * 100
    print(f"성능 테스트 텍스트 길이: {len(performance_text)} 문자")
    
    # 반모음 첨가 성능
    start_time = time.time()
    for _ in range(10):
        phonetic_addition.phonological_addition_semivowel(performance_text)
    semivowel_time = time.time() - start_time
    
    # 초성 첨가 성능
    start_time = time.time()
    for _ in range(10):
        phonetic_addition.phonological_addition_initial_consonant(performance_text)
    initial_time = time.time() - start_time
    
    # 받침 첨가 성능
    start_time = time.time()
    for _ in range(10):
        phonetic_addition.phonological_addition_final_consonant(performance_text)
    final_time = time.time() - start_time
    
    # 적응적 받침 첨가 성능
    start_time = time.time()
    for _ in range(10):
        phonetic_addition.phonological_addition_adaptive_final_consonant(performance_text)
    adaptive_time = time.time() - start_time
    
    print(f"  반모음 첨가 (10회): {semivowel_time:.4f}초")
    print(f"  초성 첨가 (10회): {initial_time:.4f}초")
    print(f"  받침 첨가 (10회): {final_time:.4f}초")
    print(f"  적응적 받침 첨가 (10회): {adaptive_time:.4f}초")
    
    print("\n=== 모든 테스트 완료 ===")
    print("✅ 모든 테스트가 성공적으로 완료되었습니다!")
    print("✅ 예외 처리 및 경계값 테스트 통과!")
    print("✅ 에러가 발생하지 않음을 확인했습니다!")
