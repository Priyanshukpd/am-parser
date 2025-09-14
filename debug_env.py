#!/usr/bin/env python3
"""Debug script to check environment variable loading"""

import os
from dotenv import load_dotenv

print("=== Environment Debug ===")

# Check before loading .env
print(f"Before load_dotenv(): {os.getenv('TOGETHER_API_KEY', 'NOT_SET')}")

# Load .env file
load_dotenv(override=True)

# Check after loading .env
api_key = os.getenv('TOGETHER_API_KEY')
print(f"After load_dotenv(): {api_key}")
print(f"API key length: {len(api_key) if api_key else 0}")

if api_key:
    print(f"First 20 chars: {api_key[:20]}...")
    print(f"Last 10 chars: ...{api_key[-10:]}")

# Check if .env file exists
import pathlib
env_file = pathlib.Path('.env')
print(f".env file exists: {env_file.exists()}")

if env_file.exists():
    print(f".env file size: {env_file.stat().st_size} bytes")
    with open('.env', 'r') as f:
        content = f.read()
        print("=== .env file content ===")
        print(content)