import openai
import logging
import re
from app.config import config

logger = logging.getLogger(__name__)

class OpenAIService:
    def __init__(self):
        openai.api_key = config.openai_api_key
    
    async def get_response(self, text: str) -> str:
        """Get response from OpenAI API with mathematical focus"""
        if not config.openai_api_key or config.openai_api_key == "your_openai_api_key_here":
            return self.get_fallback_response(text)
        
        try:
            system_prompt = """
            شما یک دستیار آموزشی تخصصی در زمینه منطق ریاضی و نظریه مجموعه‌ها هستید.
            لطفاً به زبان فارسی پاسخ دهید و بر مفاهیم زیر تمرکز کنید:

            **منطق ریاضی:**
            - جبر بولی و گزاره‌ها
            - عملگرهای منطقی: ∧ (و), ∨ (یا), ¬ (نقیض), → (شرطی), ↔ (دوشرطی)
            - قوانین دمورگان، توزیعی، جذب و سایر قوانین منطقی
            - جدول درستی و ارزش‌گذاری
            - ساده‌سازی عبارات منطقی
            - استنتاج و برهان

            **نظریه مجموعه‌ها:**
            - عملگرهای مجموعه‌ای: ∪ (اجتماع), ∩ (اشتراک), - (تفاضل), ′ (مکمل)
            - روابط مجموعه‌ای: ⊆ (زیرمجموعه), ⊂ (زیرمجموعه سره), ∈ (عضویت)
            - مجموعه‌های خاص: ∅ (تهی), ℕ (طبیعی), ℤ (صحیح), ℝ (حقیقی)
            - مجموعه توانی و کاردینالیتی
            - حاصلضرب کارتزین و روابط

            **راهنمایی پاسخ‌دهی:**
            - پاسخ‌ها باید دقیق، آموزشی و به زبان فارسی باشند
            - از نمادهای استاندارد ریاضی استفاده کنید
            - مثال‌های کاربردی ارائه دهید
            - اگر سوال خارج از حوزه است، مؤدبانه بیان کنید
            - برای عبارات پیچیده، راه حل گام به گام ارائه دهید
            """
            
            completion = openai.ChatCompletion.create(
                model=config.openai_model,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": text}
                ],
                max_tokens=config.openai_max_tokens,
                temperature=config.openai_temperature
            )
            
            return completion.choices[0].message["content"]
            
        except openai.error.AuthenticationError:
            logger.error("OpenAI authentication failed. Check your API key.")
            return self.get_fallback_response(text)
            
        except openai.error.RateLimitError:
            logger.error("OpenAI rate limit exceeded.")
            return "متأسفم در حال حاضر به دلیل محدودیت نرخ نمی‌توانم پاسخ دهم. لطفاً稍后重试."
            
        except openai.error.InsufficientQuota:
            logger.error("OpenAI quota exceeded.")
            return "سهمیه API من تمام شده است. لطفاً از ویژگی‌های داخلی ربات استفاده کنید یا稍后重试."
            
        except openai.error.APIError as e:
            logger.error(f"OpenAI API error: {e}")
            return self.get_fallback_response(text)
            
        except Exception as e:
            logger.error(f"Error calling OpenAI: {e}")
            return self.get_fallback_response(text)
    
    def get_fallback_response(self, text: str) -> str:
        """Get fallback response when OpenAI is not available"""
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

# Global OpenAI service instance
openai_service = OpenAIService()