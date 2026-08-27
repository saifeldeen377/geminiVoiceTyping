# -*- coding: utf-8 -*-
import os
import logging
import asyncio
try:
    from config import config
except ImportError:
    from .config import config

logger = logging.getLogger("geminiVoiceTyping.corrector")

class AsyncLLMCorrector:
    def __init__(self):
        self.api_keys = []
        self.current_idx = 0
        self.client = None

    def setup(self, api_keys):
        if not api_keys:
            return
        self.api_keys = api_keys
        self.current_idx = 0
        self._init_client()

    def _init_client(self):
        if self.api_keys:
            from google import genai
            self.client = genai.Client(
                http_options={"api_version": "v1beta"},
                api_key=self.api_keys[self.current_idx]
            )

    async def correct_sentence(self, text):
        if not text or not self.client:
            return text
            
        sys_prompt = "Read this text and if there is a spelling error, correct it; and if there is a grammar error, correct it too. Ensure incorrect Haa (ه) at the end of nouns is replaced with Taa Marbouta (ة). CRITICAL: Preserve colloquial dialects (like Egyptian Arabic) exactly as spoken, DO NOT translate to Modern Standard Arabic (Fusha). Do NOT translate or remove English words. Only output the corrected text, no additional conversational response needed, just the corrected text."
        
        attempts = 0
        while attempts < len(self.api_keys):
            try:
                from google.genai import types
                response = await self.client.aio.models.generate_content(
                    model='gemini-3.5-flash-lite',
                    contents=text,
                    config=types.GenerateContentConfig(
                        system_instruction=sys_prompt,
                        temperature=0.0
                    )
                )
                if response.text:
                    return response.text.strip()
                return text
            except Exception as e:
                err_str = str(e)
                logger.warning(f"LLM correction failed on key idx {self.current_idx}: {err_str}")
                if any(x in err_str for x in ["429", "RESOURCE_EXHAUSTED", "Quota", "400", "403", "PERMISSION_DENIED", "404", "NOT_FOUND"]):
                    attempts += 1
                    if attempts < len(self.api_keys):
                        self.current_idx = (self.current_idx + 1) % len(self.api_keys)
                        self._init_client()
                        continue
                return text
        return text

corrector = AsyncLLMCorrector()
