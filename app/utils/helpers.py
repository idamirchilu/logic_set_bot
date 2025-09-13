def format_progress_message(user_progress: dict) -> str:
    """Format user progress into a message"""
    score = user_progress["score"]
    level = user_progress["level"]
    logic_correct = user_progress["logic_correct"]
    set_theory_correct = user_progress["set_theory_correct"]
    total_exercises = user_progress["total_exercises"]

    message = (
        f"📊 پیشرفت شما:\n"
        f"🏆 سطح: {level}\n"
        f"⭐ امتیاز: {score}\n"
        f"🧠 تمرین‌های منطق حل شده: {logic_correct}\n"
        f"📚 تمرین‌های نظریه مجموعه حل شده: {set_theory_correct}\n"
        f"📝 کل تمرین‌های انجام شده: {total_exercises}"
    )

    return message