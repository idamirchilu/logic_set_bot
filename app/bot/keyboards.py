from telegram import ReplyKeyboardMarkup


def get_main_menu_keyboard():
    """Create the main menu keyboard with categories"""
    keyboard = [
        # Main Functions
        ['🧠 کمک در منطق', '📚 کمک در نظریه مجموعه‌ها'],
        ['📝 ایجاد تمرین'],
        # User Info & Help
        ['📊 پیشرفت من', 'ℹ️ درباره بات', '❓ راهنما']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_back_keyboard():
    """Create a keyboard with back button only"""
    keyboard = [['🔙 بازگشت به منو']]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


def get_exercise_keyboard():
    """Create exercise selection keyboard"""
    keyboard = [
        ['🧠 تمرین منطق', '📚 تمرین نظریه مجموعه‌ها'],
        ['🎲 تمرین تصادفی'],
        ['🔙 بازگشت به منو']
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
