import logging
import random
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
)

# Import our modules
from config import TOKEN
from database import DatabaseManager
from nlp_processor import NLPProcessor
from parser import LogicSetParser
from exercise_generator import ExerciseGenerator
from utils import latex_to_image, hash_query, get_cached_response, cache_response, format_progress_message

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Conversation states
(
    MAIN_MENU,
    LOGIC_INPUT,
    SET_INPUT,
    EXERCISE_SELECTION,
    SOLUTION_STEP_BY_STEP,
    WAITING_FOR_ANSWER
) = range(6)


class LogicSetBot:
    def __init__(self):
        self.db_manager = DatabaseManager()
        self.nlp_processor = NLPProcessor()
        self.parser = LogicSetParser()
        self.exercise_generator = ExerciseGenerator()
        self.scoring_system = ScoringSystem(self.db_manager)

        # Create application
        self.application = Application.builder().token(TOKEN).build()

        # Add conversation handler
        conv_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.start)],
            states={
                MAIN_MENU: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.main_menu)
                ],
                LOGIC_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_logic_input)
                ],
                SET_INPUT: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_set_input)
                ],
                EXERCISE_SELECTION: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_exercise_selection)
                ],
                WAITING_FOR_ANSWER: [
                    MessageHandler(filters.TEXT & ~filters.COMMAND, self.check_answer)
                ]
            },
            fallbacks=[CommandHandler('cancel', self.cancel)],
        )

        self.application.add_handler(conv_handler)

        # Add handler for general messages
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message)
        )

    def get_main_menu_keyboard(self):
        """Create the main menu keyboard"""
        keyboard = [
            ['🧠 کمک در منطق', '📚 کمک در نظریه مجموعه‌ها'],
            ['📝 ایجاد تمرین', '📊 پیشرفت من'],
            ['ℹ️ درباره بات', '❓ راهنما', '🔙 بازگشت']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def get_back_keyboard(self):
        """Create a keyboard with back button only"""
        keyboard = [['🔙 بازگشت به منوی اصلی']]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    def get_exercise_keyboard(self):
        """Create exercise selection keyboard"""
        keyboard = [
            ['🧠 تمرین منطق', '📚 تمرین نظریه مجموعه‌ها'],
            ['🎲 تمرین تصادفی', '🔙 بازگشت']
        ]
        return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Start the conversation and show the main menu"""
        user = update.effective_user
        self.db_manager.add_user(user.id, user.username, user.first_name, user.last_name)

        # Starter message in Farsi
        starter_text = (
            "👋 به ربات کمک‌آموز منطق و نظریه مجموعه‌ها خوش آمدید!\n\n"
            "من می‌توانم در موارد زیر به شما کمک کنم:\n"
            "• ساده‌سازی عبارات منطقی\n"
            "• حل مسائل نظریه مجموعه‌ها\n"
            "• ایجاد تمرین‌های آموزشی\n"
            "• توضیح مفاهیم به صورت گام به گام\n\n"
            "از منوی زیر استفاده کنید یا سوال خود را مستقیماً تایپ کنید!"
        )

        await update.message.reply_text(
            starter_text,
            reply_markup=self.get_main_menu_keyboard()
        )

        return MAIN_MENU

    async def main_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the main menu selection"""
        text = update.message.text
        user_id = update.effective_user.id
        self.db_manager.update_user_interaction(user_id)

        if text == '🧠 کمک در منطق':
            await update.message.reply_text(
                "لطفاً عبارت منطقی یا سوال خود را وارد کنید.\n\n"
                "مثال‌ها:\n"
                "• ساده کن (p ∧ q) ∨ (p ∧ ¬q)\n"
                "• جدول درستی برای p → q ایجاد کن\n"
                "• آیا (p ∨ q) ∧ ¬p معادل q است؟",
                reply_markup=self.get_back_keyboard()
            )
            return LOGIC_INPUT

        elif text == '📚 کمک در نظریه مجموعه‌ها':
            await update.message.reply_text(
                "لطفاً عبارت نظریه مجموعه‌ها یا سوال خود را وارد کنید.\n\n"
                "مثال‌ها:\n"
                "• محاسبه کن A ∪ B که A = {1,2,3}, B = {3,4,5}\n"
                "• آیا A زیرمجموعه B است؟\n"
                "• مجموعه توانی {1,2} چیست؟",
                reply_markup=self.get_back_keyboard()
            )
            return SET_INPUT

        elif text == '📝 ایجاد تمرین':
            await self.generate_exercise_menu(update, context)
            return EXERCISE_SELECTION

        elif text == '📊 پیشرفت من':
            progress = self.db_manager.get_user_progress(user_id)
            if progress:
                message = format_progress_message(progress)
                await update.message.reply_text(message)
            else:
                await update.message.reply_text("هنوز اطلاعات پیشرفتی موجود نیست.")
            return MAIN_MENU

        elif text == 'ℹ️ درباره بات':
            about_text = (
                "🤖 ربات منطق و نظریه مجموعه‌ها\n\n"
                "این دستیار هوشمند به دانشجویان در یادگیری و تمرین کمک می‌کند:\n"
                "• منطق گزاره‌ای\n"
                "• جبر بولی\n"
                "• عملیات نظریه مجموعه‌ها\n"
                "• استدلال ریاضی\n\n"
                "ساخته شده با پایتون، SymPy و پردازش زبان طبیعی"
            )
            await update.message.reply_text(about_text)
            return MAIN_MENU

        elif text == '❓ راهنما':
            help_text = (
                "💡 نحوه استفاده از این ربات:\n\n"
                "1. از منو برای انتخاب دسته مورد نظر استفاده کنید\n"
                "2. سوال یا عبارت خود را تایپ کنید\n"
                "3. کمک و توضیحات فوری دریافت کنید\n\n"
                "همچنین می‌توانید مستقیماً تایپ کنید:\n"
                "• 'ساده کن (p ∧ q) ∨ (p ∧ ¬q)'\n"
                "• 'محاسبه کن A ∪ B که A={1,2}, B={2,3}'\n"
                "• 'ایجاد تمرین منطق'\n"
                "• 'قوانین دمورگان را توضیح بده'"
            )
            await update.message.reply_text(help_text)
            return MAIN_MENU

        elif text == '🔙 بازگشت':
            await update.message.reply_text(
                "به منوی اصلی بازگشتید.",
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU

        elif text == '🔙 بازگشت به منوی اصلی':
            await update.message.reply_text(
                "به منوی اصلی بازگشتید.",
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU

        else:
            # If the message doesn't match any menu option, process it as a general question
            return await self.handle_general_question(update, context, text)

    async def generate_exercise_menu(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Generate exercise selection menu"""
        await update.message.reply_text(
            "نوع تمرینی که می‌خواهید تمرین کنید را انتخاب کنید:",
            reply_markup=self.get_exercise_keyboard()
        )
        return EXERCISE_SELECTION

    async def handle_exercise_selection(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle exercise type selection"""
        text = update.message.text
        user_id = update.effective_user.id

        if text == '🔙 بازگشت':
            await update.message.reply_text(
                "به منوی اصلی بازگشتید.",
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU

        # Determine exercise type
        if text == '🧠 تمرین منطق':
            exercise_type = "logic"
        elif text == '📚 تمرین نظریه مجموعه‌ها':
            exercise_type = "set_theory"
        else:  # Random Exercise
            exercise_type = random.choice(["logic", "set_theory"])

        # Get user level for difficulty adjustment
        progress = self.db_manager.get_user_progress(user_id)
        difficulty = min(3, max(1, progress["level"])) if progress else 1

        # Generate exercise
        exercise = self.exercise_generator.generate_exercise(exercise_type, difficulty)

        # Store exercise in context for answer checking
        context.user_data['current_exercise'] = exercise

        await update.message.reply_text(
            f"تمرین (سختی: {difficulty}):\n\n{exercise['question']}",
            reply_markup=self.get_back_keyboard()
        )

        return WAITING_FOR_ANSWER

    async def handle_logic_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle logic expressions from the user"""
        user_text = update.message.text
        user_id = update.effective_user.id

        if user_text == '🔙 بازگشت به منوی اصلی':
            await update.message.reply_text(
                "به منوی اصلی بازگشتید.",
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU

        # Log the question
        self.db_manager.log_question(user_id, user_text, "logic")

        try:
            # Try to parse and simplify the expression
            expr, variables = self.parser.parse_logic_expression(user_text)
            simplified = self.parser.simplify_logic(expr)

            response = f"عبارت ساده شده: {simplified}"
            await update.message.reply_text(response)

            # Send as image if it's a complex expression
            from sympy import latex
            img_buffer = latex_to_image(latex(simplified))
            if img_buffer:
                await update.message.reply_photo(
                    photo=img_buffer,
                    caption="نمایش فرمول"
                )

        except ValueError as e:
            # If parsing fails, try to handle as a general logic question
            response = await self.handle_general_question(update, context, user_text)
            if not response:
                await update.message.reply_text(
                    "نتوانستم عبارت منطقی شما را درک کنم. "
                    "لطفاً دوباره تلاش کنید یا از /help کمک بگیرید."
                )

        await update.message.reply_text(
            "چه کاری می‌خواهید انجام دهید؟",
            reply_markup=self.get_main_menu_keyboard()
        )
        return MAIN_MENU

    async def handle_set_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle set theory expressions from the user"""
        user_text = update.message.text
        user_id = update.effective_user.id

        if user_text == '🔙 بازگشت به منوی اصلی':
            await update.message.reply_text(
                "به منوی اصلی بازگشتید.",
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU

        # Log the question
        self.db_manager.log_question(user_id, user_text, "set_theory")

        try:
            # Try to parse and evaluate the expression
            result = self.parser.parse_set_expression(user_text)
            response = f"نتیجه: {result}"
            await update.message.reply_text(response)

        except ValueError as e:
            # If parsing fails, try to handle as a general set theory question
            response = await self.handle_general_question(update, context, user_text)
            if not response:
                await update.message.reply_text(
                    "نتوانستم عبارت نظریه مجموعه‌ها را درک کنم. "
                    "لطفاً دوباره تلاش کنید یا از /help کمک بگیرید."
                )

        await update.message.reply_text(
            "چه کاری می‌خواهید انجام دهید؟",
            reply_markup=self.get_main_menu_keyboard()
        )
        return MAIN_MENU

    async def check_answer(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Check the user's answer to an exercise"""
        user_answer = update.message.text
        user_id = update.effective_user.id

        if user_answer == '🔙 بازگشت به منوی اصلی':
            await update.message.reply_text(
                "به منوی اصلی بازگشتید.",
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU

        exercise = context.user_data.get('current_exercise')

        if not exercise:
            await update.message.reply_text(
                "هیچ تمرینی یافت نشد. لطفاً اول یک تمرین ایجاد کنید.",
                reply_markup=self.get_main_menu_keyboard()
            )
            return MAIN_MENU

        # Simple answer checking (in a real implementation, this would be more sophisticated)
        is_correct = user_answer.strip().lower() == exercise['answer'].strip().lower()

        # Update user score
        points = self.scoring_system.calculate_points(
            exercise['difficulty'], is_correct, exercise['type']
        )
        new_score, new_level = self.scoring_system.update_user_score(
            user_id, points, exercise['type']
        )

        if is_correct:
            await update.message.reply_text(
                f"✅ صحیح! شما {points} امتیاز کسب کردید.\n"
                f"امتیاز کل شما اکنون {new_score} است (سطح {new_level})."
            )
        else:
            await update.message.reply_text(
                f"❌ غلط. پاسخ صحیح این است: {exercise['answer']}\n"
                f"نگران نباشید، به تمرین ادامه دهید!"
            )

        await update.message.reply_text(
            "چه کاری می‌خواهید انجام دهید؟",
            reply_markup=self.get_main_menu_keyboard()
        )
        return MAIN_MENU

    async def handle_general_question(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text=None):
        """Handle general questions using NLP and cached responses"""
        if text is None:
            text = update.message.text

        user_id = update.effective_user.id

        # Check cache first
        query_hash = hash_query(text)
        cached_response = get_cached_response(self.db_manager, query_hash)

        if cached_response:
            await update.message.reply_text(cached_response)
            return MAIN_MENU

        # Use NLP to extract intent
        intent = self.nlp_processor.extract_intent(text)

        # Handle based on intent
        if intent == "explain_concept":
            response = await self.explain_concept(text)
        elif intent == "general_help":
            response = self.get_help_response()
        else:
            # For other intents or unknown, use internal response
            response = self.get_internal_response(text)

        # Cache the response
        cache_response(self.db_manager, query_hash, response)

        await update.message.reply_text(response)
        return MAIN_MENU


    def get_internal_response(self, text):
        """Get internal response when LLM is not available"""
        # Use NLP to extract intent for more specific responses
        intent = self.nlp_processor.extract_intent(text)

        if intent == "logic_simplify":
            return "لطفاً عبارت منطقی را برای ساده‌سازی وارد کنید. مثال: 'ساده کن (p ∧ q) ∨ (p ∧ ¬q)'"

        elif intent == "logic_truth_table":
            return "لطفاً عبارت منطقی را برای ایجاد جدول درستی وارد کنید. مثال: 'جدول درستی برای p → q'"

        elif intent == "set_operation":
            return "لطفاً عبارت مجموعه‌ای را برای محاسبه وارد کنید. مثال: 'محاسبه کن A ∪ B که A={1,2}, B={2,3}'"

        elif intent == "set_relation":
            return "لطفاً رابطه مجموعه‌ای را برای بررسی وارد کنید. مثال: 'آیا A زیرمجموعه B است که A={1,2}, B={1,2,3}'"

        elif intent == "generate_exercise":
            return "برای ایجاد تمرین، از منوی اصلی گزینه 'ایجاد تمرین' را انتخاب کنید."

        else:
            return (
                "مطمئن نیستم چگونه به این سوال خاص کمک کنم. "
                "سعی کنید از من بخواهید:\n"
                "• یک عبارت منطقی را ساده کنم\n"
                "• عملیات مجموعه‌ای انجام دهم\n"
                "• یک مفهوم را توضیح دهم\n"
                "• یک تمرین ایجاد کنم\n\n"
                "یا از منوی اصلی برای دسترسی به ویژگی‌های مختلف استفاده کنید."
            )

    async def explain_concept(self, concept_query):
        """Explain a concept using available resources"""
        # This would typically integrate with an LLM API like Ollama
        # For now, we'll use a simple lookup

        concept_responses = {
            "دمورگان": "قوانین دمورگان بیان می‌کنند که:\n¬(P ∧ Q) ≡ ¬P ∨ ¬Q\n¬(P ∨ Q) ≡ ¬P ∧ ¬Q\nاین قوانین چگونگی توزیع نقیض را روی عطف و فصل توصیف می‌کنند.",
            "توزیعی": "قوانین توزیعی در منطق بیان می‌کنند که:\nP ∧ (Q ∨ R) ≡ (P ∧ Q) ∨ (P ∧ R)\nP ∨ (Q ∧ R) ≡ (P ∨ Q) ∧ (P ∨ R)",
            "شرطی": "عبارت شرطی P → Q معادل ¬P ∨ Q است",
            "دوشرطی": "عبارت دوشرطی P ↔ Q معادل (P → Q) ∧ (Q → P) است",
            "اجتماع": "اجتماع مجموعه‌های A و B که با A ∪ B نشان داده می‌شود، مجموعه تمام عناصری است که در A، یا در B، یا در هر دو هستند.",
            "اشتراک": "اشتراک مجموعه‌های A و B که با A ∩ B نشان داده می‌شود، مجموعه تمام عناصری است که در هر دو A و B هستند.",
            "مکمل": "مکمل مجموعه A که با A′ یا A^c نشان داده می‌شود، مجموعه تمام عناصر در مجموعه جهانی است که در A نیستند.",
            "تفاضل": "تفاضل مجموعه‌های A و B که با A - B یا A \\ B نشان داده می‌شود، مجموعه تمام عناصری است که در A هستند اما در B نیستند.",
            "مجموعه توانی": "مجموعه توانی یک مجموعه S که با P(S) نشان داده می‌شود، مجموعه تمام زیرمجموعه‌های S است، شامل مجموعه تهی و خود S.",
            "حاصلضرب کارتزین": "حاصلضرب کارتزین مجموعه‌های A و B که با A × B نشان داده می‌شود، مجموعه تمام زوج‌های مرتب (a, b) است که در آن a ∈ A و b ∈ B."
        }

        # Find the best matching concept
        concept_query_lower = concept_query.lower()
        for concept, explanation in concept_responses.items():
            if concept in concept_query_lower:
                return explanation

        # If no specific concept matched, return a general response
        return (
            "می‌توانم مفاهیم مربوط به منطق و نظریه مجموعه‌ها را توضیح دهم. "
            "سعی کنید در مورد مفاهیم خاصی مانند:\n"
            "• قوانین دمورگان\n"
            "• عملیات مجموعه‌ای (اجتماع، اشتراک و غیره)\n"
            "• همارزی‌های منطقی\n"
            "• جدول‌های درستی\n\n"
            "یا از من بخواهید عبارتی را ساده کنم یا مسئله‌ای را حل کنم."
        )

    def get_help_response(self):
        """Return help information"""
        return (
            "💡 نحوه استفاده از این ربات:\n\n"
            "1. از منو برای انتخاب دسته مورد نظر استفاده کنید\n"
            "2. سوال یا عبارت خود را تایپ کنید\n"
            "3. کمک و توضیحات فوری دریافت کنید\n\n"
            "همچنین می‌توانید مستقیماً تایپ کنید:\n"
            "• 'ساده کن (p ∧ q) ∨ (p ∧ ¬q)'\n"
            "• 'محاسبه کن A ∪ B که A={1,2}, B={2,3}'\n"
            "• 'ایجاد تمرین منطق'\n"
            "• 'قوانین دمورگان را توضیح بده'\n\n"
            "از /start برای دیدن منوی اصلی در هر زمان استفاده کنید."
        )

    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle any message that doesn't match the conversation handler"""
        # This acts as a fallback for messages that don't match the current state
        return await self.handle_general_question(update, context)

    async def cancel(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Cancel the conversation"""
        await update.message.reply_text(
            "خدانگهدار! امیدوارم روزی دوباره بتوانیم صحبت کنیم.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END

    def run(self):
        """Run the bot"""
        logger.info("Starting bot...")
        self.application.run_polling()


if __name__ == '__main__':
    bot = LogicSetBot()
    bot.run()