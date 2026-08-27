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
            
        sys_prompt = "You are a strict text corrector. Your ONLY job is to fix spelling mistakes in the input text. Specifically, you MUST replace every incorrect Haa (ه) at the end of Arabic nouns with a Taa Marbouta (ة). For example, change الاضافه to الإضافة, and مدرسه to مدرسة. Return ONLY the corrected text and nothing else."
        
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
