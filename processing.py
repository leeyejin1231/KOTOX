import hgtk
import random
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote
from time import sleep

DEFAULT_COMPOSE_CODE = "ᴥ"

# 1-A 대치
## 초성 예사소리 -> 된소리, 거센소리 대치
power_replace_map = {
    "ㄱ" : ["ㄲ", "ㅋ"],
    "ㄷ" : ["ㄸ", "ㅌ"],
    "ㅂ" : ["ㅃ", "ㅍ"],
    "ㅅ" : ["ㅆ"],
    "ㅈ" : ["ㅉ", "ㅊ"],
}
def first_power_replace(input_span):
    decomposed = [v for v in hgtk.text.decompose(input_span).split(DEFAULT_COMPOSE_CODE) if v]
    result = []
    for i in decomposed:
        if i[0] in power_replace_map:
            result.append(random.choice(power_replace_map[i[0]])+i[1:])
        else:
            result.append(i)
    return hgtk.text.compose(DEFAULT_COMPOSE_CODE.join(result)+DEFAULT_COMPOSE_CODE)

## 초성 된소리, 거센소리 -> 예사소리 대치
reverse_power_replace_map = {
    "ㄲ" : ["ㄱ"],
    "ㅋ" : ["ㄱ"],
    "ㄸ" : ["ㄷ"],
    "ㅌ" : ["ㄷ"],   
    "ㅃ" : ["ㅂ"],
    "ㅍ" : ["ㅂ"],
    "ㅆ" : ["ㅅ"],
    "ㅉ" : ["ㅈ"],
    "ㅊ" : ["ㅈ"]
}
def reverse_first_power_replace(input_span):
    decomposed = [v for v in hgtk.text.decompose(input_span).split(DEFAULT_COMPOSE_CODE) if v]
    result = []
    for i in decomposed:
        if i[0] in reverse_power_replace_map:
            result.append(random.choice(reverse_power_replace_map[i[0]])+i[1:])
        else:
            result.append(i)
    return hgtk.text.compose(DEFAULT_COMPOSE_CODE.join(result)+DEFAULT_COMPOSE_CODE)


## 모음 대치
vowel_replace_map = {
    "ㅐ" : [f"ㅏ{DEFAULT_COMPOSE_CODE}ㅇㅣ", "ㅔ"],
    "ㅔ" : [f"ㅓ{DEFAULT_COMPOSE_CODE}ㅇㅣ", "ㅐ"],
    "ㅚ" : ["ㅙ", "ㅞ"],
    "ㅙ" : ["ㅚ", "ㅞ"],
    "ㅞ" : ["ㅚ", "ㅙ"]
}
def vowel_replace(input_span):
    decomposed = [v for v in hgtk.text.decompose(input_span).split(DEFAULT_COMPOSE_CODE) if v]
    result = []
    for i in decomposed:
        if i[1] in vowel_replace_map:
            result.append(i[0]+random.choice(vowel_replace_map[i[1]])+i[2:])
        else:
            result.append(i)
    return hgtk.text.compose(DEFAULT_COMPOSE_CODE.join(result)+DEFAULT_COMPOSE_CODE)

## 받침 대치
real_sound_map = {
    "ㄱ":"ㄱ",
    "ㄴ":"ㄴ",
    "ㄷ":"ㄷ",
    "ㄹ":"ㄹ",
    "ㅁ":"ㅁ",
    "ㅂ":"ㅂ",
    "ㅅ":"ㄷ",
    "ㅇ":"ㅇ",
    "ㅈ":"ㄷ",
    "ㅊ":"ㄷ",
    "ㅋ":"ㄱ",
    "ㅌ":"ㄷ",
    "ㅍ":"ㅂ",
    "ㅎ":"ㄷ",
    "ㄲ":"ㄱ",
    "ㅆ":"ㄷ",
    "ㄳ":"ㄱ",
    "ㄵ":"ㄴ",
    "ㄶ":"ㄴ",
    "ㄺ":"ㄱ",
    "ㄻ":"ㅁ",
    "ㄼ":"ㄹ",
    "ㄽ":"ㄹ",
    "ㄾ":"ㄹ",
    "ㄿ":"ㅂ",
    "ㅀ":"ㄹ",
    "ㅄ":"ㅂ"
}
last_replace_map = {}
for i in ["ㄱ", "ㄴ", "ㄷ", "ㄹ", "ㅁ", "ㅂ", "ㅇ"]:
    last_replace_map[i] = []
for key in real_sound_map:
    last_replace_map[real_sound_map[key]].append(key)
def last_replace(input_span):
    decomposed = [v for v in hgtk.text.decompose(input_span).split(DEFAULT_COMPOSE_CODE) if v]
    result = []
    for i in decomposed:
        if len(i)>2:
            if i[2] in real_sound_map:
                result.append(i[:2]+random.choice(last_replace_map[real_sound_map[i[2]]]))
            else:
                result.append(i)
        else:
            result.append(i)
    return hgtk.text.compose(DEFAULT_COMPOSE_CODE.join(result)+DEFAULT_COMPOSE_CODE)



# 1-C 연음
## 연음
continue_sound_map = {
    f"ㄱ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄱ",
    f"ㄴ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄴ",
    f"ㄷ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄷ",
    f"ㄹ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄹ",
    f"ㅁ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅁ",
    f"ㅂ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅂ",
    f"ㅅ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅅ",
    f"ㅇ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㅈ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅈ",
    f"ㅊ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅊ",
    f"ㅋ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅋ",
    f"ㅌ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅌ",
    f"ㅍ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅍ",
    f"ㅎ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅎ",
    f"ㄲ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄲ",
    f"ㅆ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㅆ",
    f"ㄳ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄱ",
    f"ㄵ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㄴ{DEFAULT_COMPOSE_CODE}ㅈ",
    f"ㄶ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄴ",
    f"ㄺ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㄹ{DEFAULT_COMPOSE_CODE}ㄱ",
    f"ㄻ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㄹ{DEFAULT_COMPOSE_CODE}ㅁ",
    f"ㄼ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㄹ{DEFAULT_COMPOSE_CODE}ㅂ",
    f"ㄽ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㄹ{DEFAULT_COMPOSE_CODE}ㅆ",
    f"ㄾ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㄹ{DEFAULT_COMPOSE_CODE}ㅌ",
    f"ㄿ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㄹ{DEFAULT_COMPOSE_CODE}ㅍ",
    f"ㅀ{DEFAULT_COMPOSE_CODE}ㅇ" : f"{DEFAULT_COMPOSE_CODE}ㄹ",
    f"ㅄ{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㅂ{DEFAULT_COMPOSE_CODE}ㅆ"
}
def continue_sound(input_span):
    decomposed = hgtk.text.decompose(input_span)
    for key in continue_sound_map:
        decomposed = decomposed.replace(key, continue_sound_map[key])
    return hgtk.text.compose(decomposed)

## 역연음
reverse_continue_sound_without_batchim_map = {
    f"{DEFAULT_COMPOSE_CODE}ㄱ" : f"ㄱ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㄴ" : f"ㄴ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㄷ" : f"ㄷ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㄹ" : f"ㄹ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅁ" : f"ㅁ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅂ" : f"ㅂ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅅ" : f"ㅅ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅇ" : f"ㅇ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅈ" : f"ㅈ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅊ" : f"ㅊ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅋ" : f"ㅋ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅌ" : f"ㅌ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅍ" : f"ㅍ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅎ" : f"ㅎ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㄲ" : f"ㄲ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"{DEFAULT_COMPOSE_CODE}ㅆ" : f"ㅆ{DEFAULT_COMPOSE_CODE}ㅇ",
}
reverse_continue_sound_with_batchim_map = {
    f"ㄴ{DEFAULT_COMPOSE_CODE}ㅈ" : f"ㄵ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㄹ{DEFAULT_COMPOSE_CODE}ㄱ" : f"ㄺ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㄹ{DEFAULT_COMPOSE_CODE}ㅁ" : f"ㄻ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㄹ{DEFAULT_COMPOSE_CODE}ㅂ" : f"ㄼ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㄹ{DEFAULT_COMPOSE_CODE}ㅆ" : f"ㄽ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㄹ{DEFAULT_COMPOSE_CODE}ㅌ" : f"ㄾ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㄹ{DEFAULT_COMPOSE_CODE}ㅍ" : f"ㄿ{DEFAULT_COMPOSE_CODE}ㅇ",
    f"ㅂ{DEFAULT_COMPOSE_CODE}ㅆ" : f"ㅄ{DEFAULT_COMPOSE_CODE}ㅇ"
}
def reverse_continue_sound(input_span):
    # hgtk.checker.has_batchim
    result = input_span
    for i in range(len(input_span)-1):
        if hgtk.checker.has_batchim(result[i]):
            decomposed = hgtk.text.decompose(result[i]+result[i+1])
            for key in reverse_continue_sound_with_batchim_map:
                if key in decomposed:
                    decomposed = decomposed.replace(key, reverse_continue_sound_with_batchim_map[key])
                    break
            result = result[:i]+hgtk.text.compose(decomposed)+result[i+2:]
        else:
            decomposed = hgtk.text.decompose(result[i]+result[i+1])
            for key in reverse_continue_sound_without_batchim_map:
                if key in decomposed:
                    decomposed = decomposed.replace(key, reverse_continue_sound_without_batchim_map[key])
                    break
            result = result[:i]+hgtk.text.compose(decomposed)+result[i+2:]
    return result



if __name__ == "__main__":
    print(first_power_replace("김밥을"))
    print(vowel_replace("팰리스"))
    print(vowel_replace("해외"))
    print(last_replace("학교에"))
    print(sound_like_replace("짓이가"))
    print(sound_like_replace("물난리가"))
    print(continue_sound("짓이가"))
    print(continue_sound("연음"))
    print(continue_sound("닭을"))
    print(continue_sound("발아"))
    print(continue_sound("밟아"))q
    print(reverse_continue_sound("지시가"))
    print(reverse_continue_sound("여늠"))
    print(reverse_continue_sound("피자나라"))
    print(reverse_continue_sound("치킨공주"))