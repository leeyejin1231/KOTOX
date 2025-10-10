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
    print("=== 한국어 음운 첨가 모듈  ===\n")

