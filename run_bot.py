#!/usr/bin/env python3
"""
Alternative runner that avoids the event loop issues
"""

import logging
import asyncio
import sys
from telegram.ext import Application

from app.config import config
from app.database import db_manager
from app.bot.handlers import setup_handlers

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def async_main():
    """Async main function"""
    # Validate configuration
    try:
        config.validate()
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
        return
    
    # Initialize database
    await db_manager.init_db()
    logger.info("Database initialized successfully")
    
    # Create and setup application
    application = Application.builder().token(config.telegram_token).build()
    setup_handlers(application)
    
    # Start polling
    logger.info("Starting bot...")
    await application.initialize()
    await application.start()
    await application.updater.start_polling()
    
    logger.info("Bot is now running. Press Ctrl+C to stop.")
    
    # Keep the bot running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping bot...")
    finally:
        await application.updater.stop()
        await application.stop()
        await application.shutdown()

def main():
    """Main entry point"""
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    
    try:
        asyncio.run(async_main())
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Unexpected error: {e}")

if __name__ == '__main__':
    main()