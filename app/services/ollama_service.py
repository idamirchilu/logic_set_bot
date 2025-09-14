import logging
import aiohttp
import json
import re
from app.config import config

logger = logging.getLogger(__name__)

class OllamaService:
    def __init__(self):
        self.base_url = config.ollama_base_url
        self.model = config.ollama_model
    
    async def get_response(self, text: str) -> str:
        """Get response from Ollama API"""
        try:
            async with aiohttp.ClientSession() as session:
                payload = {
                    "model": self.model,
                    "prompt": self._create_prompt(text),
                    "stream": False,
                    "options": {
                        "temperature": 0.3,
                        "max_tokens": 800
                    }
                }
                
                async with session.post(f"{self.base_url}/api/generate", json=payload) as response:
                    if response.status == 200:
                        result = await response.json()
                        return result.get("response", "پاسخ دریافت نشد.")
                    else:
                        logger.error(f"Ollama API error: {response.status}")
                        return self.get_fallback_response(text)
                        
        except Exception as e:
            logger.error(f"Error calling Ollama: {e}")
            return self.get_fallback_response(text)
    
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
        """Get fallback response when Ollama is not available"""
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

# Global Ollama service instance
ollama_service = OllamaService()