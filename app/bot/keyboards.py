from telegram import ReplyKeyboardMarkup


def get_main_menu_keyboard():
    """Create the main menu keyboard"""
    keyboard = [
        ['🧠 کمک در منطق', '📚 کمک در نظریه مجموعه‌ها'],
        ['📝 ایجاد تمرین', '📊 پیشرفت من'],
        ['ℹ️ درباره بات', '❓ راهنما', '🔙 بازگشت']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard():
    """Create a keyboard with back button only"""
    keyboard = [['🔙 بازگشت به منوی اصلی']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_exercise_keyboard():
    """Create exercise selection keyboard"""
    keyboard = [
        ['🧠 تمرین منطق', '📚 تمرین نظریه مجموعه‌ها'],
        ['🎲 تمرین تصادفی', '🔙 بازگشت']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
