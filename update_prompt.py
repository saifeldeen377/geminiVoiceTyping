import os
import re

path = r'globalPlugins\geminiVoiceTyping\config.py'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

old_prompt = '"Read this text and if there is a spelling or grammar error, correct it. CRITICAL: Preserve all languages, colloquial dialects (like Egyptian Arabic), and English words exactly as spoken.\\nIt\\'s normal to find more than 1 language in the same sentence, so don\\'t ignore any text in any language.\\nDo NOT translate. If the text is already correct, error-free, and well-punctuated, return it EXACTLY as is without any changes. Only output the final text, no conversational response."'
new_prompt = '"Read this text and if there is a spelling or grammar error, correct it. CRITICAL: Preserve all languages, colloquial dialects (like Egyptian Arabic), and English words exactly as spoken. HOWEVER, pay strict attention to Arabic spelling rules (such as adding missing Hamzas (أ, إ, ء), and distinguishing between Ha (ه) and Taa Marbouta (ة)).\\nIt\\'s normal to find more than 1 language in the same sentence, so don\\'t ignore any text in any language.\\nDo NOT translate. If the text is already correct, error-free, and well-punctuated, return it EXACTLY as is without any changes. Only output the final text, no conversational response."'

if old_prompt in content:
    content = content.replace(old_prompt, new_prompt)
    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print("SUCCESS")
else:
    print("NOT FOUND")
