"""
Logic and Set Theory Telegram Bot

A comprehensive Telegram bot for helping students learn and practice
mathematical logic and set theory concepts.
"""

__version__ = "1.0.0"
__author__ = "Mohammmad Damirchilu"
__description__ = "Telegram bot for mathematical logic and set theory education"

# Package-level imports for easy access
from app.config import config
from app.database import db_manager

# Export main components for external use
__all__ = [
    'config',
    'db_manager',
    'main'
]

# Import main function for direct execution
from app.main import main