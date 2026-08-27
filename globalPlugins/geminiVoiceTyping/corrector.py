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
        self.client = None

    def setup(self, client):
        self.client = client

    async def correct_sentence(self, text):
        if not text or not self.client:
            return text
            
        sys_prompt = "Read this text and if there is a spelling error, correct it; and if there is a grammar error, correct it too. Ensure incorrect Haa (ه) at the end of nouns is replaced with Taa Marbouta (ة). CRITICAL: Preserve colloquial dialects (like Egyptian Arabic) exactly as spoken, DO NOT translate to Modern Standard Arabic (Fusha). Do NOT translate or remove English words. Only output the corrected text, no additional conversational response needed, just the corrected text."
        
        try:
            from google.genai import types
            response = await self.client.aio.models.generate_content(
                model='gemini-2.5-flash-lite',
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
            print(f"ERROR:LLM correction failed: {e}", flush=True)
            return text

corrector = AsyncLLMCorrector()
