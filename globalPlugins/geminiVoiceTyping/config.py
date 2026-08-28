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
    "system_prompt": "You are a highly accurate, verbatim multilingual dictation tool. You will hear Arabic and English speech. Your ONLY job is to transcribe exactly what the user says, word for word. Do NOT correct grammar. Do NOT translate. Do NOT summarize or drop any words. Preserve all colloquial dialects and English words exactly as spoken. Output exactly what you hear.",
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
