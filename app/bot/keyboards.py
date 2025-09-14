from telegram import ReplyKeyboardMarkup


def get_main_menu_keyboard():
    """Create the main menu keyboard with categories"""
    keyboard = [
        ['🧠 منطق', '📚 مجموعه‌ها'],
        ['📝 تمرین جدید'],
        ['📊 پیشرفت', 'ℹ️ درباره ربات', '❓ راهنما']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard():
    """Create a keyboard with back button only"""
    keyboard = [['🔙 بازگشت']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_exercise_keyboard():
    """Create exercise selection keyboard"""
    keyboard = [
        ['🧠 تمرین منطق', '📚 تمرین مجموعه‌ها'],
        ['🎲 تمرین تصادفی'],
        ['🔙 بازگشت']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
