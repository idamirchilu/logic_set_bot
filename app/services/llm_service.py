import logging
import os
import asyncio
import httpx
from app.config import config

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        api_key = os.getenv("OPENROUTER_API_KEY")
        if not api_key:
            raise ValueError("OPENROUTER_API_KEY environment variable is not set")
        self.api_key = api_key
        self.model = "mistralai/mistral-7b-instruct"  # You can change to other OpenRouter models
        self.api_url = "https://openrouter.ai/api/v1/chat/completions"

    async def get_response(self, text: str) -> str:
        """Get response from OpenRouter API via HTTP."""
        prompt = self._create_prompt(text)
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/idamirchilu/logic_set_bot",  # required by OpenRouter
            "X-Title": "Logic Set Bot"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": "You are a helpful assistant for mathematical logic and set theory. Always respond in Persian (Farsi)."},
                {"role": "user", "content": prompt}
            ]
        }
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(self.api_url, headers=headers, json=payload, timeout=60)
                response.raise_for_status()
                data = response.json()
                result = data["choices"][0]["message"]["content"].strip()
                return result
        except Exception as e:
            logger.error(f"Error calling OpenRouter API: {e}")
            return "پاسخ دریافت نشد."

    async def close(self):
        pass  # No session to close for OpenRouter

    def _create_prompt(self, text: str) -> str:
        """Create system prompt for mathematical logic with clear instructions"""
        return f"""You are a specialized educational assistant in mathematical logic and set theory.\nRole: Mathematics and Logic Tutor\nLanguage: Persian (Farsi)\nStyle: Educational, precise, and step-by-step explanations\n\nGuidelines:\n1. Always respond in Persian (Farsi)\n2. For mathematical expressions, use standard notation (∧, ∨, ¬, →, ∪, ∩, etc.)\n3. If solving a problem, show steps clearly\n4. Use formal mathematical language when appropriate\n5. Provide examples when helpful\n\nQuestion/Task:\n{text}\n\nPlease provide a clear, educational response in Persian."""

    def get_fallback_response(self, text: str) -> str:
        import re
        text_lower = re.sub(r'[•·∙‣⁃]', ' ', text.lower())
        text_lower = re.sub(r'\s+', ' ', text_lower).strip()
        if any(word in text_lower for word in ["ساده کن", "ساده سازی", "کوچک کن"]):
            return "لطفاً عبارت منطقی را برای ساده‌سازی وارد کنید. مثال: 'ساده کن (p ∧ q) ∨ (p ∧ ¬q)'"
        elif any(word in text_lower for word in ["جدول درستی", "جدول"]):
            return "لطفاً عبارت منطقی را برای ایجاد جدول درستی وارد کنید. مثال: 'جدول درستی برای p → q'"
        elif any(word in text_lower for word in ["اجتماع", "اشتراک", "مکمل", "تفاضل", "مجموعه"]):
            return "لطفاً عبارت مجموعه‌ای را برای محاسبه وارد کنید. مثال: 'محاسبه کن A ∪ B که A={1,2}, B={2,3}'"
        elif any(word in text_lower for word in ["زیرمجموعه", "فرا مجموعه", "عضو", "تعلق"]):
            return "لطفاً رابطه مجموعه‌ای را برای بررسی وارد کنید. مثال: 'آیا A زیرمجموعه B است که A={1,2}, B={1,2,3}'"
        elif any(word in text_lower for word in ["تمرین", "مسئله", "سوال", "کوییز"]):
            return "برای ایجاد تمرین، از منوی اصلی گزینه 'ایجاد تمرین' را انتخاب کنید."
        elif any(word in text_lower for word in ["دمورگان", "قانون"]):
            return "قوانین دمورگان:\n¬(P ∧ Q) ≡ ¬P ∨ ¬Q\n¬(P ∨ Q) ≡ ¬P ∧ ¬Q\nاین قوانین نحوه توزیع نقیض روی عطف و فصل را توصیف می‌کنند."
        elif any(word in text_lower for word in ["معادل", "همارز"]):
            return "برای بررسی همارزی عبارات منطقی، لطفاً هر دو عبارت را وارد کنید. مثال: 'آیا (p ∨ q) ∧ ¬p معادل q است؟'"
        else:
            return (
                "متأسفم در حال حاضر نمی‌توانم به سوال شما پاسخ دهم. "
                "لطفاً از منوی اصلی استفاده کنید یا سوالات زیر را امتحان کنید:\n\n"
                "• ساده‌سازی عبارات منطقی\n"
                "• عملیات روی مجموعه‌ها\n"
                "• ایجاد تمرین آموزشی\n"
                "• توضیح مفاهیم پایه"
            )

llm_service = LLMService()
