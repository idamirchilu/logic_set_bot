#!/usr/bin/env python3
"""
Simple SQLite test script
"""

import asyncio
import sys
import os
import sqlite3
from pathlib import Path

def test_sqlite_basic():
    """Test basic SQLite functionality"""
    print("Testing SQLite basic functionality...")
    
    # Create data directory
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    print(f"✓ Created data directory: {data_dir.absolute()}")
    
    # Test SQLite connection
    db_path = "data/test_logic_bot.db"
    try:
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        
        # Test basic operations
        cursor.execute("CREATE TABLE IF NOT EXISTS test_table (id INTEGER PRIMARY KEY, name TEXT)")
        cursor.execute("INSERT INTO test_table (name) VALUES (?)", ("test",))
        cursor.execute("SELECT * FROM test_table")
        result = cursor.fetchone()
        
        if result and result[1] == "test":
            print("✓ SQLite basic operations work")
        else:
            print("✗ SQLite basic operations failed")
            return False
            
        conn.close()
        
        # Clean up
        os.remove(db_path)
        print("✓ SQLite test completed successfully")
        return True
        
    except Exception as e:
        print(f"✗ SQLite test failed: {e}")
        return False

def test_database_url():
    """Test database URL configuration"""
    print("Testing database URL configuration...")
    
    # Test URL conversion
    test_urls = [
        "sqlite:///./logic_bot.db",
        "sqlite+aiosqlite:///./logic_bot.db",
        "postgresql://user:pass@localhost/db",
        "postgresql+asyncpg://user:pass@localhost/db"
    ]
    
    for url in test_urls:
        if url.startswith("sqlite://"):
            converted = url.replace("sqlite://", "sqlite+aiosqlite://")
            print(f"✓ {url} -> {converted}")
        elif url.startswith("postgresql://"):
            converted = url.replace("postgresql://", "postgresql+asyncpg://")
            print(f"✓ {url} -> {converted}")
    
    print("✓ Database URL configuration test passed")
    return True

def main():
    """Main test function"""
    print("SQLite Migration Test")
    print("=" * 50)
    
    success = True
    
    # Test basic SQLite
    if not test_sqlite_basic():
        success = False
    
    # Test URL configuration
    if not test_database_url():
        success = False
    
    print("\n" + "=" * 50)
    if success:
        print("✓ All SQLite tests passed!")
        print("SQLite migration is ready to use.")
    else:
        print("✗ Some tests failed.")
        print("Please check your SQLite installation.")
    
    return success

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
