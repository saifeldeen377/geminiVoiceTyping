# -*- coding: utf-8 -*-
"""
Configuration manager for Gemini Voice Typing.
Stores API keys and settings in a JSON file.
"""

import os
import json
import logging

try:
    import globalVars
    CONFIG_DIR = globalVars.appArgs.configPath
except Exception:
    CONFIG_DIR = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "nvda")

CONFIG_FILE = os.path.join(CONFIG_DIR, "geminiVoiceTyping.json")

DEFAULT_CONFIG = {
    "api_keys": "",
    "python_path": "python",
    "beep_on_key_rotation": False,
    "copy_to_clipboard": False,
    "system_prompt": "You are a highly accurate multilingual voice typing dictation and spell checker tool. You will hear both Arabic and English speech. Your job is to transcribe and correct the user's speech.\n\nCRITICAL RULES:\n1. Strictly follow Arabic spelling rules and orthography. \n2. in Arabic, Pay extremely close attention to the difference between (ة) and (ه) at the end of words (e.g., 'مدرسة' not 'مدرسه', 'كتابة' not 'كتابه'). you must do that, it's not optional. because most of your users are arabs. and this rule is required in formal Arabic and Egyptian Arabic. it is one of spelling basics in primary school. but you are a professional.\n3. If the user's speech is in English, Type it in English. Do not translate.\n4. You may include natural punctuation based on context, but DO NOT add unnecessary trailing dots. \n\nNOTE: The user might speak Arabic and English in the same sentence; this is completely normal, so just transcribe and correct spelling in both languages without getting confused.\n\nOutput ONLY the corrected text. Do not add conversational replies.",
    "corrector_prompt": "Read this text and if there is a spelling or grammar error, correct it. CRITICAL: Preserve all languages, colloquial dialects (like Egyptian Arabic), and English words exactly as spoken.\nIt's normal to find more than 1 language in the same sentence, so don't ignore any text in any language.\nDo NOT translate. If the text is already correct, error-free, and well-punctuated, return it EXACTLY as is without any changes. Only output the final text, no conversational response."
}

logger = logging.getLogger("geminiVoiceTyping.config")


class ConfigManager:
    def __init__(self):
        self.data = dict(DEFAULT_CONFIG)
        self.load()

    def load(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, "r", encoding="utf-8-sig") as f:
                    saved = json.load(f)
                    self.data.update(saved)
            except Exception as e:
                logger.error(f"Failed to load config: {e}")
        else:
            self.save()

    def save(self):
        try:
            os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
            with open(CONFIG_FILE, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=4, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Failed to save config: {e}")

    def get(self, key, default=None):
        return self.data.get(key, default if default is not None else DEFAULT_CONFIG.get(key))

    def set(self, key, value):
        self.data[key] = value
        self.save()

    def get_api_keys_csv(self):
        """Returns the raw comma-separated API keys string."""
        raw = self.get("api_keys", "")
        keys = [k.strip() for k in raw.replace("\n", ",").split(",") if k.strip()]
        return ",".join(keys)

    def has_keys(self):
        return bool(self.get_api_keys_csv())


config = ConfigManager()
