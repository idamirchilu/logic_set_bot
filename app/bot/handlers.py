import logging
import random
from datetime import datetime, timedelta
from telegram import Update, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import ContextTypes, ConversationHandler

from app.bot.states import *
import asyncio

# Additional states
CONFIRMING_EXIT = 'CONFIRMING_EXIT'
from app.bot.keyboards import get_main_menu_keyboard, get_back_keyboard, get_exercise_keyboard
from app.services.parser import LogicSetParser
from app.services.exercise_generator import ExerciseGenerator
from app.services.llm_service import llm_service
from app.utils import latex_to_image, hash_query, format_progress_message

logger = logging.getLogger(__name__)

# Initialize services
parser = LogicSetParser()
exercise_generator = ExerciseGenerator()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Start the conversation and show the main menu"""
    user = update.effective_user
    
    # Initialize user session data
    context.user_data['last_activity'] = datetime.now()
    context.user_data['menu_attempts'] = 0
    context.user_data['current_session'] = True
    

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

    # Define menu options and their handlers
    menu_options = {
        '🧠 منطق': {
            'message': "لطفاً عبارت منطقی یا سوال خود را وارد کنید.\n\nمثال‌ها:\n• ساده کن (p ∧ q) ∨ (p ∧ ¬q)\n• جدول درستی برای p → q\n• آیا (p ∨ q) ∧ ¬p معادل q است؟\n\n💡 راهنمایی: می‌توانید از علائم ∧ (and)، ∨ (or)، ¬ (not)، → (implies) استفاده کنید.",
            'next_state': LOGIC_INPUT,
            'help_tip': "برای خروج از این بخش، روی دکمه 'بازگشت به منو' کلیک کنید."
        },
        '📚 مجموعه‌ها': {
            'message': "لطفاً عبارت نظریه مجموعه‌ها یا سوال خود را وارد کنید.\n\nمثال‌ها:\n• محاسبه کن A ∪ B که A = {1,2,3}, B = {3,4,5}\n• آیا A زیرمجموعه B است؟\n• مجموعه توانی {1,2} چیست؟",
            'next_state': SET_INPUT,
            'help_tip': "برای نمایش مجموعه‌ها از کاراکترهای {} استفاده کنید."
        },
        '📝 تمرین جدید': {
            'handler': generate_exercise_menu,
            'next_state': EXERCISE_SELECTION
        },
        '📊 پیشرفت': {
            'handler': lambda u, c: show_progress(u, u.effective_user.id),
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
    difficulty = 1

    # Generate exercise (offload to thread)
    exercise = await asyncio.to_thread(exercise_generator.generate_exercise, exercise_type, difficulty)
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

    # Log the question asynchronously (don't await)

    # Send loading message
    loading_message = await update.message.reply_text("در حال پردازش درخواست شما... ⏳")

    # Always send user prompt to Hugging Face LLM
    try:
        response = await llm_service.get_response(user_text)
        await loading_message.delete()
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        await loading_message.delete()
        await update.message.reply_text("متأسفم، در پردازش عبارت مشکل پیش آمد. لطفاً دوباره تلاش کنید.")
    await update.message.reply_text("چه کاری می‌خواهید انجام دهید؟", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def handle_set_input(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle set theory expressions from the user"""
    user_text = update.message.text
    user_id = update.effective_user.id

    if user_text == '🔙 بازگشت به منوی اصلی':
        await update.message.reply_text("به منوی اصلی بازگشتید.", reply_markup=get_main_menu_keyboard())
        return MAIN_MENU

    # Log the question asynchronously

    # Send loading message
    loading_message = await update.message.reply_text("در حال پردازش درخواست شما... ⏳")

    # Always send user prompt to Hugging Face LLM
    try:
        response = await llm_service.get_response(user_text)
        await loading_message.delete()
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        await loading_message.delete()
        await update.message.reply_text("متأسفم، در پردازش عبارت مشکل پیش آمد. لطفاً دوباره تلاش کنید.")
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

    if is_correct:
        await update.message.reply_text(
            f"✅ صحیح! پاسخ شما درست بود."
        )
    else:
        await update.message.reply_text(
            f"❌ غلط. پاسخ صحیح این است: {exercise['answer']}\n"
            f"نگران نباشید، به تمرین ادامه دهید!"
        )

    await update.message.reply_text("چه کاری می‌خواهید انجام دهید؟", reply_markup=get_main_menu_keyboard())
    return MAIN_MENU

async def handle_general_question(update: Update, context: ContextTypes.DEFAULT_TYPE, text=None):
    """Handle general questions using Hugging Face LLM"""
    if text is None:
        text = update.message.text

    user_id = update.effective_user.id

    # Send loading message
    loading_message = await update.message.reply_text("در حال پردازش سوال شما... ⏳")

    # Always send user prompt to Hugging Face LLM
    try:
        response = await llm_service.get_response(text)
        await loading_message.delete()
        await update.message.reply_text(response)
    except Exception as e:
        logger.error(f"Error getting LLM response: {e}")
        await loading_message.delete()
        await update.message.reply_text("متأسفم، در پردازش سوال مشکل پیش آمد. لطفاً دوباره تلاش کنید.")
    return MAIN_MENU

async def show_progress(update: Update, user_id: int):
    """Show user progress"""
    await update.message.reply_text(
        "پیشرفت شما ذخیره نمی‌شود، اما می‌توانید به تمرین ادامه دهید!",
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