#!/usr/bin/env python3
"""
Script to reset the database
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import db_manager

async def reset_database():
    """Reset the database"""
    print("Resetting database...")
    await db_manager.recreate_database()
    print("Database reset successfully")

if __name__ == "__main__":
    asyncio.run(reset_database())