#!/usr/bin/env python3
"""
Test script for Ollama integration
"""

import asyncio
import sys
import os

# Add the app directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.ollama_service import ollama_service

async def test_ollama():
    """Test Ollama service"""
    print("Testing Ollama integration...")
    print("=" * 50)
    
    # Test cases
    test_cases = [
        "ساده کن (p ∧ q) ∨ (p ∧ ¬q)",
        "جدول درستی برای p → q",
        "محاسبه کن A ∪ B که A={1,2}, B={2,3}",
        "قوانین دمورگان چیست؟",
        "سلام، چطور می‌تونم کمکت کنم؟"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\nTest {i}: {test_case}")
        print("-" * 30)
        
        try:
            response = await ollama_service.get_response(test_case)
            print(f"Response: {response[:200]}{'...' if len(response) > 200 else ''}")
        except Exception as e:
            print(f"Error: {e}")
            print("Falling back to internal response...")
            response = ollama_service.get_fallback_response(test_case)
            print(f"Fallback: {response[:200]}{'...' if len(response) > 200 else ''}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    asyncio.run(test_ollama())
