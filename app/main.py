import logging
import asyncio
import sys
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ConversationHandler

from app.config import config
from app.bot import (
    start,
    main_menu,
    handle_logic_input,
    handle_set_input,
    handle_exercise_selection,
    check_answer,
    handle_general_question,
    cancel,
    handle_message,
    MAIN_MENU,
    LOGIC_INPUT,
    SET_INPUT,
    EXERCISE_SELECTION,
    WAITING_FOR_ANSWER
)

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, config.log_level.upper())
)
logger = logging.getLogger(__name__)

async def main():
    """Main application entry point"""
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    
    # Create application
    application = Application.builder().token(config.telegram_token).build()
    
    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            MAIN_MENU: [MessageHandler(filters.TEXT & ~filters.COMMAND, main_menu)],
            LOGIC_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_logic_input)],
            SET_INPUT: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_set_input)],
            EXERCISE_SELECTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_exercise_selection)],
            WAITING_FOR_ANSWER: [MessageHandler(filters.TEXT & ~filters.COMMAND, check_answer)]
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    # Start the bot
    logger.info("Starting bot...")
    
    # Use the proper event loop handling for Windows
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    await application.run_polling()

if __name__ == '__main__':
    # Use the proper event loop handling
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")