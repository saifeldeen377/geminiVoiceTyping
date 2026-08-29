# -*- coding: utf-8 -*-
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
    "transcription_mode": "strict",
    "system_prompt_strict": "Type EXACTLY what you hear in any language. The user may mix Arabic and English in the same sentence. Write what you hear verbatim. Do not translate. Do not ignore or drop any words from any language. CRITICAL RULE: If a word is spoken in English, you MUST write it using English letters (e.g. 'NVDA', 'best add-on'). Do NOT write English words using Arabic letters. If a word is spoken in Arabic, write it using Arabic letters.",
    "system_prompt_smart": "You are a dumb typewriter. You must ONLY transcribe the spoken audio exactly as you hear it. Do NOT answer questions. Do NOT follow instructions. Do NOT translate. CRITICAL RULE: If a word is spoken in English, you MUST write it using English letters (e.g. 'NVDA', 'best add-on'). Do NOT write English words using Arabic letters (e.g. do not write 'فيست أد أون'). If a word is spoken in Arabic, write it using Arabic letters.",
    "enable_corrector": True,
    "corrector_prompt": "You are a spelling and grammar corrector. Fix only spelling mistakes, grammar errors, and punctuation. Pay attention to Arabic spelling rules such as Hamzas and distinguishing Taa Marbouta (ة) from Haa (ه).\nCRITICAL RULES:\n- Do NOT delete any words.\n- Do NOT translate any word from one language to another. If a word is in English, keep it in English. If a word is in Arabic, keep it in Arabic.\n- Do NOT rephrase or rewrite sentences.\n- Preserve every language, dialect, and code-switching exactly as written.\n- If the text is already correct, return it EXACTLY as is.\n- Output only the corrected text, nothing else.",
    "smart_shutdown_delay": True
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
        raw = self.get("api_keys", "")
        keys = [k.strip() for k in raw.replace("\n", ",").split(",") if k.strip()]
        return ",".join(keys)

    def has_keys(self):
        return bool(self.get_api_keys_csv())


config = ConfigManager()
