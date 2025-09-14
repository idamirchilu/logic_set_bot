import logging
import random
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.states import *

# Additional states
CONFIRMING_EXIT = 'CONFIRMING_EXIT'
from app.bot.keyboards import get_main_menu_keyboard, get_back_keyboard, get_exercise_keyboard
from app.database import db_manager
from app.services.parser import LogicSetParser
from app.services.exercise_generator import ExerciseGenerator
from app.services.scoring import ScoringSystem
from app.services.ollama_service import ollama_service
from app.utils import latex_to_image, hash_query, format_progress_message

logger = logging.getLogger(__name__)

# Initialize services
parser = LogicSetParser()
exercise_generator = ExerciseGenerator()
scoring_system = ScoringSystem(db_manager)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and show the main menu"""
    user = update.effective_user
    
    # Initialize user session data
    context.user_data['last_activity'] = datetime.now()
    context.user_data['menu_attempts'] = 0
    context.user_data['current_session'] = True
    
    try:
        success = await db_manager.add_user(user.id, user.username, user.first_name, user.last_name)
        if not success:
            logger.warning(f"Failed to add user {user.id}, but continuing...")
    except Exception as e:
        logger.error(f"Error adding user {user.id}: {e}")
        # Continue anyway to not break the user experience

    starter_text = (
        "👋 به ربات کمک‌آموز منطق و نظریه مجموعه‌ها خوش آمدید!\n\n"
        "من می‌توانم در موارد زیر به شما کمک کنم:\n"
        "• ساده‌سازی عبارات منطقی\n"
        "• حل مسائل نظریه مجموعه‌ها\n"
        "• ایجاد تمرین‌های آموزشی\n"
        "• توضیح مفاهیم به صورت گام به گام\n\n"
        "از منوی زیر استفاده کنید یا سوال خود را مستقیماً تایپ کنید!"
    )

    await update.message.reply_text(starter_text, reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle the main menu selection"""
    text = update.message.text
    user_id = update.effective_user.id
    
    # Session management
    now = datetime.now()
    last_activity = context.user_data.get('last_activity')
    
    # Check for session timeout (30 minutes)
    if last_activity and (now - last_activity) > timedelta(minutes=30):
        await update.message.reply_text(
            "جلسه شما به دلیل عدم فعالیت منقضی شده است. لطفاً دوباره شروع کنید.",
            reply_markup=get_main_menu_keyboard()
        )
        context.user_data.clear()
        context.user_data['last_activity'] = now
        return MAIN_MENU
    
    # Update last activity
    context.user_data['last_activity'] = now
    
    # Anti-spam: Check menu attempts
    menu_attempts = context.user_data.get('menu_attempts', 0)
    if menu_attempts > 10:  # Reset after 10 rapid menu changes
        context.user_data['menu_attempts'] = 0
        await update.message.reply_text(
            "لطفاً کمی صبر کنید و سپس دوباره تلاش کنید.",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU
    
    context.user_data['menu_attempts'] = menu_attempts + 1
    
    # Update user interaction
    try:
        await db_manager.update_user_interaction(user_id)
    except Exception as e:
        logger.error(f"Error updating user interaction: {e}")
        # Continue anyway to not break the user experience

    # Define menu options and their handlers
    menu_options = {
        '🧠 کمک در منطق': {
            'message': "لطفاً عبارت منطقی یا سوال خود را وارد کنید.\n\n"
                      "مثال‌ها:\n"
                      "• ساده کن (p ∧ q) ∨ (p ∧ ¬q)\n"
                      "• جدول درستی برای p → q ایجاد کن\n"
                      "• آیا (p ∨ q) ∧ ¬p معادل q است؟\n\n"
                      "💡 راهنمایی: می‌توانید از علائم ∧ (and)، ∨ (or)، ¬ (not)، → (implies) استفاده کنید.",
            'next_state': LOGIC_INPUT,
            'help_tip': "برای خروج از این بخش، روی دکمه 'بازگشت به منو' کلیک کنید."
        },
        '📚 کمک در نظریه مجموعه‌ها': {
            'message': "لطفاً عبارت نظریه مجموعه‌ها یا سوال خود را وارد کنید.\n\n"
                      "مثال‌ها:\n"
                      "• محاسبه کن A ∪ B که A = {1,2,3}, B = {3,4,5}\n"
                      "• آیا A زیرمجموعه B است؟\n"
                      "• مجموعه توانی {1,2} چیست؟",
            'next_state': SET_INPUT,
            'help_tip': "برای نمایش مجموعه‌ها از کاراکترهای {} استفاده کنید."
        },
        '📝 ایجاد تمرین': {
            'handler': generate_exercise_menu,
            'next_state': EXERCISE_SELECTION
        },
        '📊 پیشرفت من': {
            'handler': lambda u, c: show_progress(u, u.effective_user.id),
            'next_state': MAIN_MENU
        },
        'ℹ️ درباره بات': {
            'message': "🤖 ربات منطق و نظریه مجموعه‌ها\n\n"
                      "این دستیار هوشمند به دانشجویان در یادگیری و تمرین کمک می‌کند:\n"
                      "• منطق گزاره‌ای\n"
                      "• جبر بولی\n"
                      "• عملیات نظریه مجموعه‌ها\n"
                      "• استدلال ریاضی\n\n"
                      "ساخته شده با پایتون، SymPy و Ollama",
            'next_state': MAIN_MENU
        },
        '❓ راهنما': {
            'message': "💡 نحوه استفاده از ربات:\n\n"
                      "1. از منو برای انتخاب دسته مورد نظر استفاده کنید\n"
                      "2. سوال یا عبارت خود را تایپ کنید\n"
                      "3. کمک و توضیحات فوری دریافت کنید\n\n"
                      "همچنین می‌توانید مستقیماً تایپ کنید:\n"
                      "• 'ساده کن (p ∧ q) ∨ (p ∧ ¬q)'\n"
                      "• 'محاسبه کن A ∪ B که A={1,2}, B={2,3}'\n"
                      "• 'ایجاد تمرین منطق'\n"
                      "• 'قوانین دمورگان را توضیح بده'",
            'next_state': MAIN_MENU
        }
    }

    # Handle menu selection
    if text in menu_options:
        option = menu_options[text]
        
        try:
            if 'handler' in option:
                # For options with custom handlers
                await option['handler'](update, context)
            else:
                # For options with simple messages
                await update.message.reply_text(
                    option['message'],
                    reply_markup=get_back_keyboard()
                )
                
                # Send help tip if available
                if 'help_tip' in option:
                    await update.message.reply_text(
                        f"💡 {option['help_tip']}",
                        reply_markup=get_back_keyboard()
                    )
            
            # Reset menu attempts when successfully entering a section
            context.user_data['menu_attempts'] = 0
            return option['next_state']
            
        except Exception as e:
            logger.error(f"Error handling menu option {text}: {e}")
            await update.message.reply_text(
                "متأسفانه در پردازش درخواست شما مشکلی پیش آمد. لطفاً دوباره تلاش کنید.",
                reply_markup=get_main_menu_keyboard()
            )
            return MAIN_MENU
    
    elif text in ['🔙 بازگشت', '🔙 بازگشت به منو']:
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.", 
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

    else:
        # If the message doesn't match any menu option, process it as a general question
        return await handle_general_question(update, context, text)

async def generate_exercise_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generate exercise selection menu"""
    await update.message.reply_text(
        "نوع تمرینی که می‌خواهید تمرین کنید را انتخاب کنید:",
        reply_markup=get_exercise_keyboard()
    )
    return EXERCISE_SELECTION

async def handle_exercise_selection(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle exercise type selection"""
    text = update.message.text
    user_id = update.effective_user.id

    if text == '🔙 بازگشت به منو':
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.", 
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

    # Define valid exercise types
    EXERCISE_TYPES = {
        '🧠 تمرین منطق': 'logic',
        '📚 تمرین نظریه مجموعه‌ها': 'set_theory',
        '🎲 تمرین تصادفی': random.choice(['logic', 'set_theory'])
    }

    # Validate exercise type
    if text not in EXERCISE_TYPES:
        await update.message.reply_text(
            "لطفاً یکی از گزینه‌های موجود را انتخاب کنید.",
            reply_markup=get_exercise_keyboard()
        )
        return EXERCISE_SELECTION

    exercise_type = EXERCISE_TYPES[text]

    # Send loading message
    loading_message = await update.message.reply_text("در حال آماده‌سازی تمرین... ⏳")

    # Get user level for difficulty adjustment
    try:
        progress = await db_manager.get_user_progress(user_id)
        difficulty = min(3, max(1, progress["level"])) if progress else 1
    except Exception as e:
        logger.error(f"Error getting user progress: {e}")
        difficulty = 1

    # Generate exercise
    exercise = exercise_generator.generate_exercise(exercise_type, difficulty)
    # Delete loading message
    await loading_message.delete()

    # Store exercise in context for answer checking
    context.user_data['current_exercise'] = exercise

    await update.message.reply_text(
        f"تمرین (سختی: {difficulty}):\n\n{exercise['question']}",
        reply_markup=get_back_keyboard()
    )

    return WAITING_FOR_ANSWER

async def handle_logic_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle logic expressions from the user"""
    user_text = update.message.text
    user_id = update.effective_user.id

    if user_text == '🔙 بازگشت به منوی اصلی':
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=get_main_menu_keyboard())
        return MAIN_MENU

    # Log the question
    try:
        await db_manager.log_question(user_id, user_text, "logic")
    except Exception as e:
        logger.error(f"Error logging question: {e}")

    # Send loading message
    loading_message = await update.message.reply_text("در حال پردازش درخواست شما... ⏳")

    try:
        # Try to parse and simplify the expression
        expr, variables = parser.parse_logic_expression(user_text)
        simplified = parser.simplify_logic(expr)

        response = f"عبارت ساده شده: {simplified}"
        # Delete loading message
        await loading_message.delete()
        await update.message.reply_text(response)

        # Send as image if it's a complex expression
        from sympy import latex
        img_buffer = latex_to_image(latex(simplified))
        if img_buffer:
            await update.message.reply_photo(photo=img_buffer, caption="نمایش فرمول")

    except ValueError as e:
        # If parsing fails, use Ollama for help
        try:
            response = await ollama_service.get_response(user_text)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error getting Ollama response: {e}")
            await update.message.reply_text("متأسفم، در پردازش عبارت مشکل پیش آمد. لطفاً عبارت را به صورت واضح‌تر وارد کنید.")

    await update.message.reply_text("چه کاری می‌خواهید انجام دهید؟", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def handle_set_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle set theory expressions from the user"""
    user_text = update.message.text
    user_id = update.effective_user.id

    if user_text == '🔙 بازگشت به منوی اصلی':
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=get_main_menu_keyboard())
        return MAIN_MENU

    # Log the question
    try:
        await db_manager.log_question(user_id, user_text, "set_theory")
    except Exception as e:
        logger.error(f"Error logging question: {e}")

    # Send loading message
    loading_message = await update.message.reply_text("در حال پردازش درخواست شما... ⏳")

    try:
        # Try to parse and evaluate the expression
        result = parser.parse_set_expression(user_text)
        response = f"نتیجه: {result}"
        # Delete loading message
        await loading_message.delete()
        await update.message.reply_text(response)

    except ValueError as e:
        # If parsing fails, use Ollama for help
        try:
            response = await ollama_service.get_response(user_text)
            await update.message.reply_text(response)
        except Exception as e:
            logger.error(f"Error getting Ollama response: {e}")
            await update.message.reply_text("متأسفم، در پردازش عبارت مشکل پیش آمد. لطفاً عبارت را به صورت واضح‌تر وارد کنید.")

    await update.message.reply_text("چه کاری می‌خواهید انجام دهید؟", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def check_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Check the user's answer to an exercise"""
    user_answer = update.message.text
    user_id = update.effective_user.id

    if user_answer == '🔙 بازگشت به منوی اصلی':
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=get_main_menu_keyboard())
        return MAIN_MENU

    exercise = context.user_data.get('current_exercise')

    if not exercise:
        await update.message.reply_text("هیچ تمرینی یافت نشد. لطفاً اول یک تمرین ایجاد کنید.", reply_markup=get_main_menu_keyboard())
        return MAIN_MENU

    # Simple answer checking
    is_correct = user_answer.strip().lower() == exercise['answer'].strip().lower()

    # Update user score
    try:
        points = scoring_system.calculate_points(exercise['difficulty'], is_correct, exercise['type'])
        new_score, new_level = await db_manager.update_user_score(user_id, points, exercise['type'])
    except Exception as e:
        logger.error(f"Error updating score: {e}")
        points = 0
        new_score, new_level = 0, 1

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

    await update.message.reply_text("چه کاری می‌خواهید انجام دهید؟", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def handle_general_question(update: Update, context: ContextTypes.DEFAULT_TYPE, text=None):
    """Handle general questions using Ollama"""
    if text is None:
        text = update.message.text

    user_id = update.effective_user.id

    # Check cache first
    query_hash = hash_query(text)
    cached_response = await db_manager.get_cached_response(query_hash)

    if cached_response:
        await update.message.reply_text(cached_response)
        return MAIN_MENU

    # Send loading message
    loading_message = await update.message.reply_text("در حال پردازش سوال شما... ⏳")

    # Use Ollama for all general questions
    response = await ollama_service.get_response(text)
    # Delete loading message
    await loading_message.delete()

    # Cache the response
    try:
        await db_manager.cache_response(query_hash, response)
    except Exception as e:
        logger.error(f"Error caching response: {e}")

    await update.message.reply_text(response)
    return MAIN_MENU

async def show_progress(update: Update, user_id: int):
    """Show user progress"""
    try:
        progress = await db_manager.get_user_progress(user_id)
        if progress:
            message = format_progress_message(progress)
            await update.message.reply_text(message)
        else:
            await update.message.reply_text(
                "هنوز اطلاعات پیشرفتی موجود نیست.",
                reply_markup=get_main_menu_keyboard()
            )
    except Exception as e:
        logger.error(f"Error getting user progress: {e}")
        await update.message.reply_text(
            "خطا در دریافت اطلاعات پیشرفت.",
            reply_markup=get_main_menu_keyboard()
        )

async def confirm_exit(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Ask for confirmation before exiting"""
    keyboard = [
        ['✅ بله، خروج', '❌ خیر، ادامه']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        "آیا مطمئن هستید که می‌خواهید از ربات خارج شوید؟",
        reply_markup=reply_markup
    )
    return CONFIRMING_EXIT

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Cancel the conversation"""
    if update.message.text == '✅ بله، خروج':
        await update.message.reply_text(
            "خدانگهدار! امیدوارم روزی دوباره بتوانیم صحبت کنیم.",
            reply_markup=ReplyKeyboardRemove()
        )
        return ConversationHandler.END
    else:
        await update.message.reply_text(
            "به منوی اصلی بازگشتید.",
            reply_markup=get_main_menu_keyboard()
        )
        return MAIN_MENU

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle any message that doesn't match the conversation handler"""
    # This acts as a fallback for messages that don't match the current state
    return await handle_general_question(update, context)

def setup_handlers(application):
    """Setup all handlers for the application"""
    from telegram.ext import ConversationHandler, CommandHandler, MessageHandler, filters
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            LOGIC_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic_input)],
            SET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_set_input)],
            EXERCISE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exercise_selection)],
            WAITING_FOR_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)],
            CONFIRMING_EXIT: [MessageHandler(filters.TEXT & ~filters.COMMAND, cancel)]
        },
        fallbacks=[
            CommandHandler('cancel', confirm_exit),
            MessageHandler(filters.COMMAND, confirm_exit)
        ],
        allow_reentry=True,
    )
    
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))