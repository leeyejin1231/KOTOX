PROMPTS = {
"deobfuscation_zero_prompt" : """You are an expert in Korean language correction.
The sentence I provide may be non-standard, use internet slang, phonetic spelling, intentional misspellings, or be obfuscated in other ways.
Your task is to translate and normalize the sentence into natural, standard Korean.

Rules:
1. Preserve the original meaning.
2. If the tone is conversational, keep it conversational but in standard Korean.
3. Remove unnecessary emoticons or special characters.
4. Make the sentence grammatically smooth and natural.

Translate:
Input sentence: $input
Output sentence: """,



"deobfuscation_five_prompt" : """You are an expert in Korean language correction.
The sentence I provide may be non-standard, use internet slang, phonetic spelling, intentional misspellings, or be obfuscated in other ways.
Your task is to translate and normalize the sentence into natural, standard Korean.

Rules:
1. Preserve the original meaning.
2. If the tone is conversational, keep it conversational but in standard Korean.
3. Remove unnecessary emoticons or special characters.
4. Make the sentence grammatically smooth and natural.

Examples:
Input sentence 1: $example1_input
Output sentence 1: $example1_output

Input sentence 2: $example2_input
Output sentence 2: $example2_output

Input sentence 3: $example3_input
Output sentence 3: $example3_output

Input sentence 4: $example4_input
Output sentence 4: $example4_output

Input sentence 5: $example5_input
Output sentence 5: $example5_output

Translate:
Input sentence: $input
Output sentence: """,



"detoxification_zero_prompt" : """You are an expert in Korean language correction and detoxification.  
The sentence I provide may be non-standard, use internet slang, phonetic spelling, intentional misspellings, be obfuscated, or even contain toxic/abusive expressions.
Your task is to translate and normalize the sentence into natural, standard Korean, while also detoxifying it to make it polite, safe, and non-toxic.

Rules:
1. Preserve the intended meaning as much as possible, but remove or soften toxic, offensive, or abusive language.
2. If the tone is conversational, keep it conversational but in standard Korean.
3. Remove unnecessary emoticons or special characters.
4. Make the sentence grammatically smooth and natural.
5. Ensure the output is non-toxic, respectful, and safe.

Translate:
Input sentence: $input
Output sentence: """,



"detoxification_five_prompt" : """You are an expert in Korean language correction and detoxification.  
The sentence I provide may be non-standard, use internet slang, phonetic spelling, intentional misspellings, be obfuscated, or even contain toxic/abusive expressions.
Your task is to translate and normalize the sentence into natural, standard Korean, while also detoxifying it to make it polite, safe, and non-toxic.

Rules:
1. Preserve the intended meaning as much as possible, but remove or soften toxic, offensive, or abusive language.
2. If the tone is conversational, keep it conversational but in standard Korean.
3. Remove unnecessary emoticons or special characters.
4. Make the sentence grammatically smooth and natural.
5. Ensure the output is non-toxic, respectful, and safe.

Examples:
Input sentence 1: $example1_input
Output sentence 1: $example1_output

Input sentence 2: $example2_input
Output sentence 2: $example2_output

Input sentence 3: $example3_input
Output sentence 3: $example3_output

Input sentence 4: $example4_input
Output sentence 4: $example4_output

Input sentence 5: $example5_input
Output sentence 5: $example5_output

Translate:
Input sentence: $input
Output sentence: """,
}
