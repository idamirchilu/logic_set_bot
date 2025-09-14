import logging
import os
import google.generativeai as genai
from google.api_core import retry
from app.config import config

logger = logging.getLogger(__name__)

# Model configuration
GENERATION_CONFIG = {
    "temperature": 0.7,
    "top_p": 0.8,
    "top_k": 40,
    "max_output_tokens": 1024,
}

SAFETY_SETTINGS = [
    {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
    {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
]

class LLMService:
    def __init__(self):
        api_key = os.getenv("GOOGLE_API_KEY")
        if not api_key:
            raise ValueError("GOOGLE_API_KEY environment variable is not set")
            
        # Configure the Gemini API with the key
        genai.configure(api_key=api_key)
        
        try:
            self._model = genai.GenerativeModel(
                model_name="gemini-pro",
                generation_config=GENERATION_CONFIG,
                safety_settings=SAFETY_SETTINGS
            )
        except Exception as e:
            logger.error(f"Failed to initialize Gemini model: {e}")
            raise
            
        self._cache = {}
        self._cache_ttl = 60 * 5  # 5 minutes

    async def get_response(self, text: str) -> str:
        """Get response from Google Gemini (Generative AI)."""
        import time
        try:
            prompt = self._create_prompt(text)
            key = hash(prompt)
            cached = self._cache.get(key)
            if cached:
                ts, val = cached
                if time.time() - ts < self._cache_ttl:
                    return val
                else:
                    del self._cache[key]
            # Add retry logic for API calls
            @retry.Retry(predicate=retry.if_exception_type(Exception))
            async def generate_with_retry():
                return await self._model.generate_content_async(prompt, stream=False)
                
            response = await generate_with_retry()
            
            if not response:
                logger.error("Empty response from Gemini API")
                return "متأسفانه در حال حاضر نمی‌توانم پاسخ دهم. لطفا دوباره تلاش کنید."
                
            if hasattr(response, 'prompt_feedback') and response.prompt_feedback.block_reason:
                logger.warning(f"Content blocked: {response.prompt_feedback.block_reason}")
                return "متأسفانه نمی‌توانم به این سوال پاسخ دهم."

            result = response.text
            self._cache[key] = (time.time(), result)
            return result
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return "پاسخ دریافت نشد."

    async def close(self):
        pass  # No session to close for Gemini

    def _create_prompt(self, text: str) -> str:
        """Create system prompt for mathematical logic with clear instructions"""
        return f"""You are a specialized educational assistant in mathematical logic and set theory.
        Role: Mathematics and Logic Tutor
        Language: Persian (Farsi)
        Style: Educational, precise, and step-by-step explanations
        
        Guidelines:
        1. Always respond in Persian (Farsi)
        2. For mathematical expressions, use standard notation (∧, ∨, ¬, →, ∪, ∩, etc.)
        3. If solving a problem, show steps clearly
        4. Use formal mathematical language when appropriate
        5. Provide examples when helpful
        
        Question/Task:
        {text}
        
        Please provide a clear, educational response in Persian."""

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
