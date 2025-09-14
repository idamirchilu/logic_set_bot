#!/usr/bin/env python3
"""
SQLite setup script for Logic Set Bot
This script helps users set up SQLite database for the bot
"""

import asyncio
import sys
import os
import sqlite3
from pathlib import Path

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.database import db_manager

def create_data_directory():
    """Create data directory for SQLite database"""
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Created data directory: {data_dir.absolute()}")

def test_sqlite_connection():
    """Test SQLite connection"""
    try:
        # Test basic SQLite connection
        db_path = "data/logic_bot.db"
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("SELECT sqlite_version();")
        version = cursor.fetchone()[0]
        conn.close()
        print(f"✓ SQLite connection successful (version: {version})")
        return True
    except Exception as e:
        print(f"✗ SQLite connection failed: {e}")
        return False

async def initialize_database():
    """Initialize the database with tables"""
    try:
        print("Initializing database tables...")
        await db_manager.init_db()
        print("✓ Database tables created successfully")
        return True
    except Exception as e:
        print(f"✗ Database initialization failed: {e}")
        return False

async def test_database_operations():
    """Test basic database operations"""
    try:
        print("Testing database operations...")
        
        # Test adding a user
        success = await db_manager.add_user(
            user_id=12345,
            username="test_user",
            first_name="Test",
            last_name="User"
        )
        
        if success:
            print("✓ User creation test passed")
        else:
            print("✗ User creation test failed")
            return False
        
        # Test getting user progress
        progress = await db_manager.get_user_progress(12345)
        if progress:
            print("✓ User progress retrieval test passed")
        else:
            print("✗ User progress retrieval test failed")
            return False
        
        # Clean up test data
        await db_manager.clear_database()
        print("✓ Test data cleaned up")
        
        return True
        
    except Exception as e:
        print(f"✗ Database operations test failed: {e}")
        return False

async def main():
    """Main setup function"""
    print("Setting up SQLite for Logic Set Bot...")
    print("=" * 50)
    
    # Create data directory
    create_data_directory()
    
    # Test SQLite connection
    if not test_sqlite_connection():
        print("Failed to connect to SQLite. Please check your setup.")
        return False
    
    # Initialize database
    if not await initialize_database():
        print("Failed to initialize database. Please check your configuration.")
        return False
    
    # Test database operations
    if not await test_database_operations():
        print("Database operations test failed. Please check your setup.")
        return False
    
    print("\n" + "=" * 50)
    print("✓ SQLite setup completed successfully!")
    print("Your bot is ready to use with SQLite database.")
    print(f"Database file: {Path('data/logic_bot.db').absolute()}")
    
    return True

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
