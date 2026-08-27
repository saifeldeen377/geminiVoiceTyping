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
            
        sys_prompt = "أنت مصحح إملائي محترف. مهمتك الوحيدة هي أخذ نص المستخدم وتصحيحه إملائياً، مع التركيز الصارم جداً على تحويل الهاء (ه) إلى تاء مربوطة (ة) في الكلمات المؤنثة. لا تضف أي شرح أو علامات ترقيم، فقط أعد النص المصحح."
        
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
            logger.error(f"LLM correction failed: {e}")
            return text

corrector = AsyncLLMCorrector()
