from operator import index
from tkinter import X
from tkinter.constants import FALSE
from augment_funtions import Processing, SyntaticObfuscation, IconicObfuscation, TransliterationalObfuscation, SymbolAddition, PragmaticObfuscation, SociolinguisticObfuscation, PhoneticAddition
import pandas as pd
from tqdm import tqdm
import random
from collections import defaultdict
from typing import List, Dict, Tuple, Any
import argparse


class Augmentation:
    def __init__(self, rng):
        pragmatic_obfuscation = PragmaticObfuscation()
        processing = Processing()
        syntatic_obfuscation= SyntaticObfuscation()
        iconic_obfuscation = IconicObfuscation()
        symbol_addition = SymbolAddition()
        transliterational_obfuscation = TransliterationalObfuscation()
        sociolinguistic_obfuscation = SociolinguisticObfuscation()
        phonetic_addition = PhoneticAddition()
        self.rng = rng

        self.MAP = {
            "1-1": processing.first_power_replace,         # 초성대치
            # "1-2": processing.reverse_first_power_replace,     #역초성대치
            "1-3":processing.vowel_replace,   #모음 대치
            "1-4": processing.last_replace,   #받침 대치
            "1-5": processing.sound_like_replace,   #음운 변동을 반영해서 표기    
            "2-1": phonetic_addition.phonological_addition_semivowel,   #반모음 첨가
            "2-2": phonetic_addition.phonological_addition_adaptive_final_consonant,  #받침 추가 (뒤초성에따라)
            "2-3": phonetic_addition.phonological_addition_initial_consonant,    #초성 추가
            # "2-4": phonetic_addition.phonological_addition_final_consonant,    #받침 추가 (랜덤))
            "3-1": processing.continue_sound,   #연음
            # "3-2": processing.reverse_continue_sound,  #역연음
            "5-1": iconic_obfuscation.yamin_swap, #도상적 대치 (야민)
            # "5-2": iconic_obfuscation.gana_swap, #도상적 대치 (가나다)
            "5-2": iconic_obfuscation.consonant_swap, #도상적 대치(ㄱㄴㄷ,ㅏㅑㅓ)
            "6-1": iconic_obfuscation.rotation_swap, #방향 전환 (90도)
            # "6-2": iconic_obfuscation.rotation_180_swap, #방향 전환 (180도)
            # "7": iconic_obfuscation.compression_swap, #압착
            "8-1": transliterational_obfuscation.iconic_swap,  # 음차
            # "8-2": transliterational_obfuscation.iconic_swap,
            "8-3": transliterational_obfuscation.foreign_iconic_swap,
            "8-2": transliterational_obfuscation.meaning_swap,  #표기대치 (한자)
            "10": syntatic_obfuscation.spacing,  # 띄어쓰기
            "11": syntatic_obfuscation.change_array,  #배열 교란
            "13-2": symbol_addition.comprehensive_symbol_addition   #기호 추가
        }

        # Categories per spec (adjusted for consistency)
        self.ALONE = {"5-1", "11", "6-1"}
        self.FIRST = {"3-1", "8-2", "13-1", "8-3"}
        self.LAST = {"5-2", "10", "13-2", "8-1"}
        self.ANY = {
            "1-3", "1-4", "1-5",
            "2-1", "2-2", "2-3",
        }
        
        self.SENTENCE = {"10", "13-2", "8-1"}
        self.LOW = {"1-3", "2-3", "3-1", "5-1", "6-1", "8-2", "11"}

    # -----------------------
    # 유틸리티
    # -----------------------
    def _tokenize(self, text: str) -> List[str]:
        # 간단 토크나이즈(공백 기준). 필요 시 더 정교한 토크나이저로 교체 가능.
        return text.split()

    def _detokenize(self, text_list):
        result = ""
        for span in text_list:
            result += span['span'][-1] + " "
        return result.rstrip()

    def _apply_rule_to_span(self, text_span, rule):
        apply = self._is_possible(text_span, rule)
        if apply:
            applied_text = self.MAP[rule](text_span['span'][-1])
            if applied_text == text_span['span'][-1]:
                return None
            else:
                return applied_text
        else:
            return None

    def _select_span(self, span_list, apply_ratio, rule):
        if rule in self.LOW:
            apply_ratio = 0.25
        span_candicate = [i for i, span in enumerate(span_list) if span != None]
        # print(f"span_list: {span_list}")
        # print(f"span_candicate: {span_candicate}")
        selected_index_length =  max(int(len(span_list) * apply_ratio),1)
        if len(span_candicate) < selected_index_length:
            return None
        selected_index = self.rng.sample(span_candicate, selected_index_length)
        # print(f"selected_index: {selected_index}")

        return selected_index

    def _is_possible(self, text_span, rule):
        if text_span['applied_rule']:
            for r in text_span['applied_rule']:
                if r in self.LAST:
                    return False
                if r in self.ALONE:
                    return False
            if rule in self.FIRST:
                return False
        else:
            if rule in self.LAST:
                return False
        return True

    def augmentation(self, text, max_count, apply_ratio):
        """
        #### output format ####
        {
            "origin": "original text",
            "obfuscated_rules": ["applied rule", "applied rule", ...],
            "neutral_steps":[
                {"rule": "applied rule", "obfuscated_text": "obfuscated text"},
                {"rule": "applied rule", "obfuscated_text": "obfuscated text"},
                ...
            ]
            "toxic_steps":[
                {"rule": "applied rule", "obfuscated_text": "obfuscated text"},
                {"rule": "applied rule", "obfuscated_text": "obfuscated text"},
                ...
            ]
        }
        """
        current_count = 0
        report = {"origin":text[0],"toxic":text[1],"obfuscated_rules":[], "neutral_steps":[], "toxic_steps":[]}
        
        neutral_text_list = self._tokenize(text[0])
        toxic_text_list = self._tokenize(text[1])
        neutral_text_list = [{'span': [x], 'applied_rule': []} for x in neutral_text_list]
        toxic_text_list = [{'span': [x], 'applied_rule': []} for x in toxic_text_list]

        all_rules = self.MAP.copy()
        constrain = 0
        current_loop = 0
        
        while max_count > current_count:
            current_loop += 1
            if current_loop > 500:
                return {"origin":text[0],"toxic":text[1],"obfuscated_rules":[], "neutral_steps":[], "toxic_steps":[]}

            neutral_after_list = []
            toxic_after_list = []

            # 기법 선택
            selected_rule = self.rng.choice(list(all_rules.keys()))
            # print(len(all_rules))

            if selected_rule in self.SENTENCE:
                if current_count != max_count - 1:
                    continue
                elif current_count == max_count - 1:
                    #띄어쓰기
                    if selected_rule == '10':
                        neutral_after_text = self.MAP[selected_rule](neutral_text_list)
                        toxic_after_text = self.MAP[selected_rule](toxic_text_list)
                        report['obfuscated_rules'].append("10")
                        report['neutral_steps'].append({'rule': "10", "obfuscated_text": neutral_after_text})
                        report['toxic_steps'].append({'rule': "10", "obfuscated_text": toxic_after_text})
                        break
                    #기호 추가
                    else:
                        neutral_text = self._detokenize(neutral_text_list)
                        toxic_text = self._detokenize(toxic_text_list)
                        neutral_after_text = self.MAP[selected_rule](neutral_text)
                        toxic_after_text = self.MAP[selected_rule](toxic_text)
                        report['obfuscated_rules'].append(selected_rule)
                        report['neutral_steps'].append({'rule': selected_rule, "obfuscated_text": neutral_after_text})
                        report['toxic_steps'].append({'rule': selected_rule, "obfuscated_text": toxic_after_text})
                        break
            elif selected_rule in '8-3' and current_count == 0:
                neutral_text = self._detokenize(neutral_text_list)
                toxic_text = self._detokenize(toxic_text_list)
                neutral_after_text = self.MAP[selected_rule](neutral_text)
                toxic_after_text = self.MAP[selected_rule](toxic_text)
                report['obfuscated_rules'].append(selected_rule)
                report['neutral_steps'].append({'rule': selected_rule, "obfuscated_text": neutral_after_text})
                report['toxic_steps'].append({'rule': selected_rule, "obfuscated_text": toxic_after_text})
                neutral_text_list = [{'span': [x], 'applied_rule': []} for x in self._tokenize(neutral_after_text)]
                toxic_text_list = [{'span': [x], 'applied_rule': []} for x in self._tokenize(toxic_after_text)]
                all_rules.pop(selected_rule)
                current_count += 1
                constrain = 0
                continue
            else:
                # 기법 적용
                for span in neutral_text_list:
                    neutral_after = self._apply_rule_to_span(span, selected_rule)
                    neutral_after_list.append(neutral_after)
                for span in toxic_text_list:
                    toxic_after = self._apply_rule_to_span(span, selected_rule)
                    toxic_after_list.append(toxic_after)
                    # print(f"toxic_after: {toxic_after}")
                # print("================")
                # print(f"neutral_text: {report['origin']}")
                # print(f"neutral_after: {neutral_after}")
                # print(f"selected_rule: {selected_rule}")
                # print(f"toxic_after: {report['toxic']}")
                # print(f"toxic_after: {toxic_after}")
                # 스팬 선택
                neutral_selected_span = self._select_span(neutral_after_list, apply_ratio, selected_rule)
                toxic_selected_span = self._select_span(toxic_after_list, apply_ratio, selected_rule)

                # print("+++++++++++++++++++++++++")
                # print(f"neutral_selected_span: {neutral_selected_span}")
                # print(f"toxic_selected_span: {toxic_selected_span}")
                # print("+++++++++++++++++++++++++")
                
                if neutral_selected_span and toxic_selected_span:
                    # 스팬 적용
                    for i in neutral_selected_span:
                        neutral_text_list[i]['applied_rule'].append(selected_rule)
                        neutral_text_list[i]['span'].append(neutral_after_list[i])
                    for i in toxic_selected_span:
                        toxic_text_list[i]['applied_rule'].append(selected_rule)
                        toxic_text_list[i]['span'].append(toxic_after_list[i])

                    neutral_text = self._detokenize(neutral_text_list)
                    toxic_text = self._detokenize(toxic_text_list)

                    
                    # print(f"origin text: {report['origin']}")
                    # print(f"neutral_text: {neutral_text}")
                    # print(f"toxic text: {report['toxic']}")
                    # print(f"toxic_text: {toxic_text}")
                        
                    report['obfuscated_rules'].append(selected_rule)
                    report['neutral_steps'].append({'rule': selected_rule, "obfuscated_text": neutral_text})
                    report['toxic_steps'].append({'rule': selected_rule, "obfuscated_text": toxic_text})
                    all_rules.pop(selected_rule)
                    current_count += 1
                    constrain = 0
                else:
                    # 다시 시도
                    all_rules.pop(selected_rule)
                    constrain += 1
                    # print(f"constrain: {constrain}")
                    if constrain > 15:
                        constrain = 0
                        current_count = 0
                        report = {"origin":text[0],"toxic":text[1],"obfuscated_rules":[], "neutral_steps":[], "toxic_steps":[]}
                        
                        neutral_text_list = self._tokenize(text[0])
                        toxic_text_list = self._tokenize(text[1])
                        neutral_text_list = [{'span': [x], 'applied_rule': []} for x in neutral_text_list]
                        toxic_text_list = [{'span': [x], 'applied_rule': []} for x in toxic_text_list]
                        # all_rules = self.MAP.copy()
                        print("=====re start!!======")
                    continue

        return report

def main(cnt):
    augmentation = Augmentation(random.Random(42))
    df = pd.read_csv("data/ko_obf_length.csv")
    neutral_texts = []
    toxic_texts = []
    obfucated_texts = []
    obfucasted_labels = []

    for i in tqdm(range(597, len(df))):
        report = augmentation.augmentation([df.iloc[i]['neutral'], df.iloc[i]['toxic']], cnt, 0.4)

        # neutral
        neutral_texts.append(report['origin'])
        toxic_texts.append("")
        obfucated_texts.append(report['neutral_steps'][-1]['obfuscated_text'])
        obfucasted_labels.append(report['obfuscated_rules'])

        # toxxic
        neutral_texts.append(report['origin'])
        toxic_texts.append(report['toxic'])
        obfucated_texts.append(report['toxic_steps'][-1]['obfuscated_text'])
        obfucasted_labels.append(report['obfuscated_rules'])

        if i > 10 and i % 3 == 0:
            data = pd.DataFrame()
            data['neutral'] = neutral_texts
            data['toxic'] = toxic_texts
            data['obfucated_texts'] = obfucated_texts
            data['obfucasted_labels'] = obfucasted_labels
            data.to_csv(f"data/ko_obfs_augmented_{cnt}.csv", index=False)

    data = pd.DataFrame()
    data['neutral'] = neutral_texts
    data['toxic'] = toxic_texts
    data['obfucated_texts'] = obfucated_texts
    data['obfucasted_labels'] = obfucasted_labels
    data.to_csv(f"data/ko_obfs_augmented_{cnt}.csv", index=False)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Generate Korean problem.')
    parser.add_argument('-c', '--cnt', required=True, help='count', default='1')
    args = parser.parse_args()

    main(int(args.cnt))