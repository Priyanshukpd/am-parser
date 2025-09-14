#!/usr/bin/env python3
"""
Simple API test script
"""

import requests
import time

def test_api():
    """Test if API is running"""
    try:
        response = requests.get("http://127.0.0.1:8000/health", timeout=5)
        print(f"✅ API Response: {response.json()}")
        return True
    except Exception as e:
        print(f"❌ API Error: {e}")
        return False

if __name__ == "__main__":
    print("🧪 Simple API Test")
    test_api()