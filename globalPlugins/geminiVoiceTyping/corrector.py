# -*- coding: utf-8 -*-
import os
import json
import logging
import re
try:
    from config import config, CONFIG_FILE
except ImportError:
    from .config import config, CONFIG_FILE

logger = logging.getLogger("geminiVoiceTyping.corrector")

# Attempt to load qalsadi for morphological analysis
try:
    from qalsadi.lemmatizer import Lemmatizer
    lemmer = Lemmatizer()
    HAS_QALSADI = True
except Exception:
    HAS_QALSADI = False

CORRECTION_DICT_FILE = os.path.join(os.path.dirname(CONFIG_FILE), "correction_dict.json")
DEFAULT_DICT = {
    "الاضافه": "الإضافة",
    "اضافه": "إضافة",
    "كلمه": "كلمة",
    "لعبه": "لعبة",
    "مدرسه": "مدرسة",
    "النهارده": "النهاردة",
    "كويسه": "كويسة",
    "شاشه": "شاشة",
    "حاجه": "حاجة",
    "جميله": "جميلة",
    "مربوطه": "مربوطة",
    "عربيه": "عربية",
    "لغه": "لغة"
}

EXCLUSIONS = {"الله", "الوجه", "المنبه", "المشتبه", "الفقه", "السفاهه", "الكنهه", "الآلهه", "المياه", "الافواه", "الاتجاه"}

class Corrector:
    def __init__(self):
        self.d = dict(DEFAULT_DICT)
        self.load()

    def load(self):
        if os.path.exists(CORRECTION_DICT_FILE):
            try:
                with open(CORRECTION_DICT_FILE, 'r', encoding='utf-8-sig') as f:
                    self.d.update(json.load(f))
            except Exception as e:
                logger.error(f"Corrector load error: {e}")
        else:
            self.save()

    def save(self):
        try:
            with open(CORRECTION_DICT_FILE, 'w', encoding='utf-8') as f:
                json.dump(self.d, f, indent=4, ensure_ascii=False)
        except Exception:
            pass

    def add_correction(self, wrong, right):
        self.d[wrong] = right
        self.save()

    def correct_word(self, word):
        if not word:
            return word
            
        clean_word = word.strip('.,!؟،')
        if not clean_word:
            return word
            
        if clean_word in self.d:
            return word.replace(clean_word, self.d[clean_word])
            
        # Regex Rule: Starts with Al, ends with Haa
        if clean_word.startswith("ال") and clean_word.endswith("ه"):
            if clean_word not in EXCLUSIONS:
                corrected = clean_word[:-1] + "ة"
                return word.replace(clean_word, corrected)
                
        # Optional: PyArabic/Qalsadi morphology check
        # We can add more advanced checks here in the future
        
        return word

    def correct_sentence(self, text):
        words = text.split()
        corrected_words = [self.correct_word(w) for w in words]
        return " ".join(corrected_words)

corrector = Corrector()
