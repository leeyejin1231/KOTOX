from augment_funtions import Processing, SyntaticObfuscation, IconicObfuscation, TransliterationalObfuscation, SymbolAddition, PragmaticObfuscation, SociolinguisticObfuscation, PhoneticAddition
import pandas as pd
from tqdm import tqdm
import random
from collections import defaultdict
from typing import List, Dict, Tuple, Any


class Augmentation:
    def __init__(self):
        pragmatic_obfuscation = PragmaticObfuscation()
        processing = Processing()
        syntatic_obfuscation= SyntaticObfuscation()
        iconic_obfuscation = IconicObfuscation()
        symbol_addition = SymbolAddition()
        transliterational_obfuscation = TransliterationalObfuscation()
        sociolinguistic_obfuscation = SociolinguisticObfuscation()
        phonetic_addition = PhoneticAddition()

        self.MAP = {
            "1-1": processing.first_power_replace, 
            "1-2": processing.reverse_first_power_replace, 
            "1-3":processing.vowel_replace, 
            "1-4": processing.last_replace, 
            "1-5": processing.sound_like_replace, 
            "2-1": phonetic_addition.phonological_addition_semivowel, 
            "2-2": phonetic_addition.phonological_addition_adaptive_final_consonant, 
            "2-3": phonetic_addition.phonological_addition_initial_consonant, 
            "2-4": phonetic_addition.phonological_addition_final_consonant, 
            "3-1": processing.continue_sound, 
            "3-2": processing.reverse_continue_sound, 
            # "4": processing.elision, 
            "5-1": iconic_obfuscation.yamin_swap, 
            "5-2": iconic_obfuscation.gana_swap, 
            "5-3": iconic_obfuscation.consonant_swap, 
            "6-1": iconic_obfuscation.rotation_90_swap, 
            "6-2": iconic_obfuscation.rotation_180_swap,
            "7": iconic_obfuscation.compression_swap, 
            "8-1": transliterational_obfuscation.chinese_iconic_swap,
            "8-2": transliterational_obfuscation.iconic_swap,
            "8-3": transliterational_obfuscation.foreign_iconic_swap,
            "9-1": transliterational_obfuscation.number_swap,
            "9-2": transliterational_obfuscation.meaning_dict,
            "10": syntatic_obfuscation.spacing,
            "11": syntatic_obfuscation.change_array,
            "12": sociolinguistic_obfuscation.sociolinguistic_swap,
            "13-1": pragmatic_obfuscation.pragmatic_swap,
            "13-2": symbol_addition.comprehensive_symbol_addition
            }

        # Categories per spec (adjusted for consistency)
        self.ALWAYS_FIRST = {"12"}
        self.ALONE = {"5-1", "11", "6-1", "6-2", "7"}
        self.FIRST = {"3-1", "3-2", "8-3", "9-1", "13-1"}
        self.LAST = {"5-2", "5-3", "8-1", "9-2", "10", "13-2"}
        self.ANY = {
            "1-2", "1-3", "1-4", "1-5",
            "2-1", "2-2", "2-3", "2-4",
            # "3-1","3-2","4","8-2",
            "8-2",
        }
        self.SENT_TECHS = {"10", "11", "12", "13-1"}

    # -----------------------
    # 유틸리티
    # -----------------------
    def _prefix(self, code: str) -> str:
        return code.split("-")[0]

    def _is_sentence_tech(self, code: str) -> bool:
        # SENT_TECHS는 '10', '11', '12', '13-1' 처럼 key 그 자체/접두가 포함되어 있음
        # 접두 일치 허용(예: '13-1'은 그대로, '10','11','12'는 그대로)
        return code in self.SENT_TECHS

    def _tokenize(self, text: str) -> List[str]:
        # 간단 토크나이즈(공백 기준). 필요 시 더 정교한 토크나이저로 교체 가능.
        return text.split()

    def _detokenize(self, tokens: List[str]) -> str:
        return " ".join(tokens)

    def _apply_sentence_tech(self, code: str, text: str):
        fn = self.MAP[code]
        if not isinstance(text, str) or text == "":
            return text, False
        try:
            out = fn(text)
            if out is None:
                return text, False
            if not isinstance(out, str):
                out = str(out)
            return out, (out != text)
        except IndexError:
            # 내부 기법이 문자열 길이를 가정하다가 터지는 케이스 방지
            return text, False
        except Exception:
            # 다른 예외도 안전하게 skip
            return text, False

    def _apply_span_tech_to_token(self, code: str, token: str):
        fn = self.MAP[code]
        # 빈 토큰이나 문자열 아닌 경우는 건너뛰기
        if not isinstance(token, str) or len(token) == 0:
            return token, False
        # 필요하면 최소 길이 조건을 두고 싶은 기법을 여기서 분기 가능
        try:
            out = fn(token)
            if out is None:
                return token, False
            if not isinstance(out, str):
                out = str(out)
            return out, (out != token)
        except IndexError:
            # 예: 내부에서 s[1], s[-1] 같은 인덱싱을 했는데 길이가 부족한 경우
            return token, False
        except Exception:
            return token, False

    # -----------------------
    # 기법 시퀀스 생성 (1~3개, 1:1:1)
    #  - prefix(앞 숫자) 중복 금지
    #  - 순서/규칙 검증
    # -----------------------
    def _valid_sequence(self, seq: List[str]) -> bool:
        # prefix 중복 금지
        seen = set()
        for c in seq:
            p = self._prefix(c)
            if p in seen:
                return False
            seen.add(p)

        # ALONE은 (ALWAYS_FIRST 제외) 무조건 혼자
        # => 예외적으로 ALWAYS_FIRST('12')를 앞에 허용: [12, ALONE] 만 허용
        if any(c in self.ALONE for c in seq):
            alones = [c for c in seq if c in self.ALONE]
            if len(alones) != 1:
                return False
            if len(seq) == 1:
                pass
            elif len(seq) == 2 and seq[0] in self.ALWAYS_FIRST and seq[1] in self.ALONE:
                pass
            else:
                return False

        # ALWAYS_FIRST가 있으면 무조건 맨 앞
        if any(c in self.ALWAYS_FIRST for c in seq):
            if seq[0] not in self.ALWAYS_FIRST or sum(c in self.ALWAYS_FIRST for c in seq) != 1:
                return False

        # FIRST는 처음이거나 혼자
        # (여러 개의 FIRST가 함께 있으면 첫 번째만 허용, 나머지는 규칙 위반이므로 배제)
        first_positions = [i for i,c in enumerate(seq) if c in self.FIRST]
        if len(first_positions) > 0:
            # FIRST가 여럿이면 첫 번째를 제외하고는 허용 불가
            if len(first_positions) > 1:
                return False
            # 유일한 FIRST의 위치가 0이거나, 전체가 1개일 때만 허용
            if not (first_positions[0] == 0 or len(seq) == 1):
                return False

        # LAST는 마지막이거나 혼자
        last_positions = [i for i,c in enumerate(seq) if c in self.LAST]
        if len(last_positions) > 0:
            if len(last_positions) > 1:
                return False
            if not (last_positions[0] == len(seq)-1 or len(seq) == 1):
                return False

        # 나머지 ANY는 순서 제한 없음
        return True

    def _sample_sequence(self, k: int, rng: random.Random) -> List[str]:
        codes = list(self.MAP.keys())

        # 시퀀스 후보를 무작위 생성→검증 반복
        for _ in range(200):
            rng.shuffle(codes)

            seq = []
            used_prefix = set()

            # ALONE이 뽑히는 경우를 조금 더 자주 고려(규칙 충족을 쉽게)
            # 단, k>1인 경우 [12, ALONE] 패턴만 가능
            if k == 1 and rng.random() < 0.2:
                alone = rng.choice(list(self.ALONE))
                seq = [alone]
            elif k == 2 and rng.random() < 0.2:
                seq = ["12", rng.choice(list(self.ALONE))]
            else:
                for c in codes:
                    p = self._prefix(c)
                    if p in used_prefix:
                        continue
                    seq.append(c)
                    used_prefix.add(p)
                    # 길이가 k를 넘지 않게 유지
                    if len(seq) == k:
                        break

            # 순서 조정: ALWAYS_FIRST가 있으면 맨 앞으로
            if any(c in self.ALWAYS_FIRST for c in seq):
                seq = [next(c for c in seq if c in self.ALWAYS_FIRST)] + [c for c in seq if c not in self.ALWAYS_FIRST]

            # LAST가 있으면 맨 뒤로
            if any(c in self.LAST for c in seq):
                lasts = [c for c in seq if c in self.LAST]
                non_lasts = [c for c in seq if c not in self.LAST]
                # 하나만 허용
                if len(lasts) == 1:
                    seq = non_lasts + lasts

            # FIRST가 있으면 맨 앞으로(단 ALWAYS_FIRST가 있으면 그 다음)
            if any(c in self.FIRST for c in seq):
                firsts = [c for c in seq if c in self.FIRST]
                non_firsts = [c for c in seq if c not in self.FIRST]
                if len(firsts) == 1:
                    if len(seq) >= 1 and seq[0] in self.ALWAYS_FIRST:
                        seq = [seq[0]] + [firsts[0]] + [c for c in non_firsts if c != seq[0]]
                    else:
                        seq = [firsts[0]] + [c for c in non_firsts]

            if len(seq) == k and self._valid_sequence(seq):
                return seq

        # 최후 수단: 제약을 완화해 하나라도 유효한 걸 반환(안전장치)
        # 가장 간단한 유효 케이스: k=1이고 ALONE 하나
        if k == 1:
            return [list(self.ALONE)[0]]
        # 아니면 ALWAYS_FIRST + ALONE
        if k == 2:
            return ["12", list(self.ALONE)[0]]
        # 기본 폴백: 서로 다른 prefix 3개
        distinct = []
        used = set()
        for c in self.MAP.keys():
            p = self._prefix(c)
            if p in used:
                continue
            used.add(p)
            distinct.append(c)
            if len(distinct) == k:
                break
        return distinct

    # -----------------------
    # 스팬 비율(≈30%) 충족을 위한 적용기
    #  - 문장 기법은 비율 계산에서 제외
    #  - depth 최대 2 (동일/상이 모두 허용)
    #  - 스팬별 depth를 추적, 변화 없으면 다른 스팬/기법 재시도
    # -----------------------
    def _apply_span_tech_over_sentence(
        self,
        text: str,
        tech_code: str,
        rng: random.Random,
        target_to_fill: int,
        per_token_depth: Dict[int, int],
        allow_depth2_partner: str = None
    ) -> Tuple[str, int, List[Tuple[int, List[str]]]]:
        """
        allow_depth2_partner: 다른 기법으로 depth=2를 형성해야 할 때 파트너 코드(선택적).
        반환: (새 문장, 실제로 변경된 토큰 수, [(토큰인덱스, [적용기법1, 적용기법2?])...])
        """
        tokens = self._tokenize(text)
        n = len(tokens)
        if n == 0 or target_to_fill <= 0:
            return text, 0, []

        order = list(range(n))
        rng.shuffle(order)

        changed = 0
        log = []

        for idx in order:
            if changed >= target_to_fill:
                break
            if not tokens[idx]:
                continue
            if per_token_depth.get(idx, 0) >= 2:
                continue

            # 1차 적용
            new_tok, ok1 = self._apply_span_tech_to_token(tech_code, tokens[idx])


            if not ok1:
                continue  # 변화 없으면 다른 스팬 시도

            tokens[idx] = new_tok
            per_token_depth[idx] = per_token_depth.get(idx, 0) + 1
            applied = [tech_code]
            actually_changed = 1  # 스팬 변화 카운트

            # depth=2 시도 (확률적으로): 같은 기법 또는 다른 기법
            if per_token_depth[idx] < 2 and rng.random() < 0.5:
                # 같은 기법 반복 또는 파트너
                partner = allow_depth2_partner if allow_depth2_partner else (tech_code if rng.random() < 0.6 else None)
                if partner:
                    newer_tok, ok2 = self._apply_span_tech_to_token(partner, tokens[idx])
                    if ok2:
                        tokens[idx] = newer_tok
                        per_token_depth[idx] += 1
                        applied.append(partner)
                        # depth=2라도 스팬 카운트는 1개로 유지(한 스팬 내 중첩)
                        # 다만 "다른 기법으로 depth2"라면 아이템의 총 선택 개수 산정에 영향을 줄 수 있음(상위 로직에서 처리)

            changed += actually_changed
            log.append((idx, applied))

        return self._detokenize(tokens), changed, log

    # -----------------------
    # 메인: 데이터 리스트 증강
    # -----------------------
    def augment_items(self, data_list: List[str], seed: int = None) -> List[Dict[str, Any]]:
        """
        주어진 문장 리스트에 대해:
          - 아이템마다 1/2/3개 기법을 1:1:1로 무작위 선택
          - 규칙(순서/ALONE 등) 준수
          - SENT_TECHS는 문장 단위, 나머지는 스팬 단위
          - 스팬은 전체의 ≈30%에 증강이 가해지도록 시도(문장 기법 제외)
          - depth 최대 2 (동일/상이 모두 허용), 스팬별 변화가 없으면 다른 스팬/기법 시도
          - 단계별 결과와 사용된 기법들을 기록
        반환 형식:
          [
            {
              "original": <원문>,
              "steps": [
                {"after": <적용 후 문장>, "techniques": ["12"]},
                {"after": <적용 후 문장>, "techniques": ["1-3"]},
                {"after": <적용 후 문장>, "techniques": ["1-3","3-1"]},  # depth=2 예시
              ]
            },
            ...
          ]
        """
        rng = random.Random(seed)
        reports = []

        for item in data_list:
            original = item
            current = item
            steps = []

            # 1) 이번 아이템에서 사용할 기법 개수 k (1:1:1)
            k = rng.choices([1, 2, 3], weights=[0.3, 0.3, 0.3])[0]

            # 2) 기법 시퀀스 선택(규칙 준수, prefix 겹침 방지)
            seq = self._sample_sequence(k, rng)

            # 문장 길이/스팬 관련 준비
            tokens = self._tokenize(current)
            n_tokens = len(tokens)
            # 목표 스팬 개수 (문장 기법 제외)
            target_spans = max(1, round(0.7 * n_tokens)) if n_tokens > 0 else 0
            # 현재까지 스팬 증강된 수
            spans_augmented = 0
            # 각 토큰의 depth(최대 2)
            per_token_depth = defaultdict(int)

            # depth=2가 다른 기법끼리 적용되면 "그 아이템엔 총 2개가 선택"으로 간주
            # → 이를 반영하려면 실제 적용 과정에서 서로 다른 기법이 한 스팬에 겹칠 때
            #   해당 step에 두 코드를 함께 기록한다(상위 레벨 카운트는 seq로 이미 관리하므로 기록 중심).
            # 구현 상: 필요 시 allow_depth2_partner를 다음 스팬 적용 때 넘겨 depth2를 유도할 수 있음.
            pending_depth2_partner = None

            # 3) 시퀀스대로 적용
            for idx, code in enumerate(seq):
                # 문장 기법?
                if self._is_sentence_tech(code):
                    new_text, changed = self._apply_sentence_tech(code, current)
                    if changed:
                        current = new_text
                        steps.append({"after": current, "techniques": [code]})
                    else:
                        # 변화 없으면 기록 생략
                        pass
                    continue

                # 스팬 기법
                # 남은 스팬 목표
                remaining = max(0, target_spans - spans_augmented)
                if remaining <= 0 and n_tokens > 0:
                    # 목표치를 이미 채웠으면, 그래도 최소 1개는 시도해서
                    # "실제로 적용되었는지" 평가 후 무효라면 스킵
                    remaining = 1

                # depth2 파트너(다른 기법)를 바로 다음 순서에서 유도할지 결정
                # 여기서는 30% 채우기가 더 우선이므로 일단 partner는 비활성(필요 시 확률적으로 부여)
                partner = None
                if pending_depth2_partner:
                    partner = pending_depth2_partner
                    pending_depth2_partner = None
                elif rng.random() < 0.25:
                    # 25% 확률로 '다른' 기법을 같은 스팬 depth2로 시도(ANY 중 임의 선택, prefix 중복 피함)
                    # 단, 현재 code와 같은 prefix는 배제
                    any_candidates = [c for c in self.ANY if self._prefix(c) != self._prefix(code)]
                    if any_candidates:
                        partner = rng.choice(any_candidates)

                # 적용
                new_text, delta, detail = self._apply_span_tech_over_sentence(
                    current, code, rng, remaining, per_token_depth, allow_depth2_partner=partner
                )

                if delta > 0:
                    spans_augmented += delta
                    current = new_text
                    # detail: [(토큰idx, [code] or [code, partner])]
                    # 한 step에 여러 토큰이 바뀔 수 있지만, 단계별 결과를 단순화해
                    # '이번 단계에서 사용된 기법들의 종류'만 요약 기록
                    used_codes = set()
                    for _, applied_list in detail:
                        for c in applied_list:
                            used_codes.add(c)
                    steps.append({"after": current, "techniques": sorted(used_codes)})
                else:
                    # 변화가 없었으면 다른 스팬/기법을 추가로 시도(보정 단계)
                    # -> ANY에서 하나 더 뽑아 30% 달성 보조
                    if n_tokens > 0 and spans_augmented < target_spans:
                        helper = rng.choice(list(self.ANY))
                        helper_remaining = max(1, target_spans - spans_augmented)
                        new_text2, delta2, detail2 = self._apply_span_tech_over_sentence(
                            current, helper, rng, helper_remaining, per_token_depth
                        )
                        if delta2 > 0:
                            spans_augmented += delta2
                            current = new_text2
                            used_codes = set()
                            for _, applied_list in detail2:
                                for c in applied_list:
                                    used_codes.add(c)
                            steps.append({"after": current, "techniques": sorted(used_codes)})

            # 4) 만약 30% 목표를 못 채웠다면, ANY로 마저 채우기(최대 두 번)
            fill_attempts = 0
            while n_tokens > 0 and spans_augmented < target_spans and fill_attempts < 2:
                helper = rng.choice(list(self.ANY))
                helper_remaining = max(1, target_spans - spans_augmented)
                new_text3, delta3, detail3 = self._apply_span_tech_over_sentence(
                    current, helper, rng, helper_remaining, per_token_depth
                )
                if delta3 > 0:
                    spans_augmented += delta3
                    current = new_text3
                    used_codes = set()
                    for _, applied_list in detail3:
                        for c in applied_list:
                            used_codes.add(c)
                    steps.append({"after": current, "techniques": sorted(used_codes)})
                fill_attempts += 1

            reports.append({
                "original": original,
                "steps": steps
            })

        return reports


def main():
    augmentation = Augmentation()
    df = pd.read_csv("data/kda_ko.csv")
    neutral_texts = []
    toxic_texts = []
    obfucated_texts = []
    toxic_labels = []
    obfucasted_labels = []

    temp_neutral_text = df['neutral'][0]
    temp_implicit = []

    # for i in tqdm(range(len(df))):
    for i in tqdm(range(50,3000)):
        if df.iloc[i]['neutral'] == temp_neutral_text:
            temp_implicit.append(df.iloc[i]['implicit'])
        else:
            try:
                result = augmentation.augment_items([temp_neutral_text]+temp_implicit)
            except:
                print(i)
                break
            flag = True
            for r in result:
                neutral_texts.append(result[0]['original'])
                if flag:
                    toxic_texts.append("")
                    toxic_labels.append(0)
                    flag = False
                else:
                    toxic_texts.append(r['original'])
                    toxic_labels.append(1)
                try:
                    obfucated_texts.append(r['steps'][-1]['after'])
                    obfucasted_labels.append(", ".join([s['techniques'][0] for s in r['steps']]))
                except:
                    obfucated_texts.append("")
                    obfucasted_labels.append("0")

            temp_neutral_text = df.iloc[i]['neutral']
            temp_implicit = [df.iloc[i]['implicit']]
        
        if i%50 == 0:
            augmented_data = pd.DataFrame()
            augmented_data['neutral'] = neutral_texts
            augmented_data['toxic'] = toxic_texts
            augmented_data['obfuscated_text'] = obfucated_texts
            augmented_data['toxic_label'] = toxic_labels
            augmented_data['obfuscation_label'] = obfucasted_labels
            
            augmented_data.to_csv("./data/augmented_data.csv")
            print(f"save {i}th data to './data/augmented_data.csv'")

        result = augmentation.augment_items([temp_neutral_text]+temp_implicit)
        flag = True
        for r in result:
            neutral_texts.append(result[0]['original'])
            if flag:
                toxic_texts.append("")
                toxic_labels.append(0)
                flag = False
            else:
                toxic_texts.append(r['original'])
                toxic_labels.append(1)
            obfucated_texts.append(r['steps'][-1]['after'])
            obfucasted_labels.append(", ".join([s['techniques'][0] for s in r['steps']]))

    augmented_data = pd.DataFrame()        
    augmented_data['neutral'] = neutral_texts
    augmented_data['toxic'] = toxic_texts
    augmented_data['obfuscated_text'] = obfucated_texts
    augmented_data['toxic_label'] = toxic_labels
    augmented_data['obfuscation_label'] = obfucasted_labels
    
    augmented_data.to_csv("./data/augmented_data.csv")
    print("save to './data/augmented_data.csv'\nDone!!")


if __name__ == "__main__":
    main()