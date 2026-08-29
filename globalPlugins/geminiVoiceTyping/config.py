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
    "system_prompt_strict": "Type EXACTLY what you hear in any language. The user may mix Arabic and English in the same sentence. Write what you hear verbatim. Do not translate. Do not ignore or drop any words. Do NOT swap or replace any words. You may correct basic spelling and grammar, and add punctuation, but the vocabulary and word order MUST remain exactly as spoken. CRITICAL RULE: If a word is spoken in English, you MUST write it using English letters (e.g. 'for NVDA'). Do NOT write English words using Arabic letters. Never write 'فور' when the user means 'for'.",
    "system_prompt_smart": "You are an expert transcriptionist. You must ONLY transcribe the spoken audio exactly as you hear it. Do NOT answer questions. Do NOT translate. CRITICAL RULES:\n1. Do NOT swap or replace any words. You may correct spelling, grammar, and add punctuation, but keep the exact vocabulary and word order as spoken.\n2. The user frequently mixes Arabic and English. You MUST write English words using English letters, and Arabic words using Arabic letters.\n3. Pay special attention to short English prepositions like 'for', 'in', 'on' - do NOT write them as Arabic words. Do not write 'فور' for 'for'.\n4. If the audio contains only silence, background noise, or unintelligible sounds, you MUST output an empty string. Do NOT hallucinate text. Output nothing but the verbatim transcript.",
    "enable_corrector": True,
    "corrector_prompt": "You are a spelling and grammar corrector for mixed Arabic-English text. Fix spelling mistakes and punctuation.\nCRITICAL RULES:\n- Do NOT delete words.\n- Do NOT translate.\n- Fix Arabizi/transliteration errors: If an English word is written in Arabic letters (e.g. 'فيست' -> 'best', 'أد أون' -> 'add-on', 'فور' -> 'for'), you MUST correct it to English letters.\n- E.g. 'The best add-on فور NVDA' MUST become 'The best add-on for NVDA'.\n- If text is correct, return it EXACTLY as is.\n- Output ONLY the corrected text.",
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
