import logging
import aiohttp
import json
import re
from app.config import config
from time import time

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        # Use HuggingFace free endpoint for Gemma-2b (or other public model)
        self.base_url = "https://api-inference.huggingface.co/models/google/gemma-2b"
        self._session = None
        self._cache = {}
        self._cache_ttl = 60 * 5  # 5 minutes

    async def get_response(self, text: str) -> str:
        """Get response from HuggingFace Inference API (Gemma-2b)."""
        try:
            prompt = self._create_prompt(text)
            key = hash(prompt)
            cached = self._cache.get(key)
            if cached:
                ts, val = cached
                if time() - ts < self._cache_ttl:
                    return val
                else:
                    del self._cache[key]

            # Lazily create aiohttp.ClientSession when needed
            if self._session is None:
                timeout = aiohttp.ClientTimeout(total=15)
                self._session = aiohttp.ClientSession(timeout=timeout)

            payload = {"inputs": prompt}
            headers = {"accept": "application/json"}
            async with self._session.post(self.base_url, json=payload, headers=headers) as response:
                if response.status == 200:
                    try:
                        result = await response.json()
                        # HuggingFace returns a list of dicts with 'generated_text'
                        out = result[0]["generated_text"] if isinstance(result, list) and result and "generated_text" in result[0] else str(result)
                    except Exception:
                        out = await response.text() or "پاسخ دریافت نشد."
                    self._cache[key] = (time(), out)
                    return out
                else:
                    logger.error(f"HF API error: {response.status}")
                    return self.get_fallback_response(text)
        except Exception as e:
            logger.error(f"Error calling HF API: {e}")
            return self.get_fallback_response(text)

    async def close(self):
        """Close the underlying aiohttp session."""
        try:
            if self._session is not None:
                await self._session.close()
        except Exception:
            pass

    def _create_prompt(self, text: str) -> str:
        """Create system prompt for mathematical logic"""
        return f"""
        شما یک دستیار آموزشی تخصصی در زمینه منطق ریاضی و نظریه مجموعه‌ها هستید.
        لطفاً به زبان فارسی پاسخ دهید و بر مفاهیم زیر تمرکز کنید:

        حوزه تخصصی: منطق ریاضی و نظریه مجموعه‌ها
        زبان پاسخ: فارسی
        سبک پاسخ: آموزشی و دقیق

        موضوعات پوشش داده شده:
        - جبر بولی و گزاره‌ها
        - عملگرهای منطقی (∧, ∨, ¬, →, ↔)
        - قوانین دمورگان، توزیعی، جذب
        - جدول درستی
        - ساده‌سازی عبارات منطقی
        - عملیات مجموعه‌ای (∪, ∩, -, ′)
        - روابط مجموعه‌ای (⊆, ⊂, ∈)
        - مجموعه‌های خاص (∅, ℕ, ℤ, ℝ)

        لطفاً به سوال زیر پاسخ دهید:

        {text}
        """

    def get_fallback_response(self, text: str) -> str:
        """Get fallback response when LLM is not available"""
        # Clean the input text
        text_lower = re.sub(r'[•·∙‣⁃]', ' ', text.lower())  # Remove bullet points
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

# Global LLM service instance
llm_service = LLMService()
