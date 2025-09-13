#!/usr/bin/env python3
"""
Database initialization script
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import db_manager

async def main():
    """Initialize the database"""
    print("Initializing database...")
    await db_manager.init_db()
    print("Database initialized successfully")

if __name__ == "__main__":
    asyncio.run(main())