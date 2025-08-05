#!/usr/bin/env python3
"""
Check environment variables for VisaBot
"""
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def check_env():
    """Check if required environment variables are set"""
    print("🔍 Checking VisaBot Environment Variables...\n")
    
    # Required variables
    required_vars = [
        "OPENAI_API_KEY"
    ]
    
    # Optional variables with defaults
    optional_vars = {
        "REDIS_URL": "redis://localhost:6379",
        "OPENAI_MODEL": "gpt-4",
        "OPENAI_MAX_TOKENS": "2000",
        "OPENAI_TEMPERATURE": "0.7"
    }
    
    print("Required Variables:")
    all_good = True
    
    for var in required_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * min(len(value), 10)}...")
        else:
            print(f"❌ {var}: NOT SET")
            all_good = False
    
    print("\nOptional Variables:")
    for var, default in optional_vars.items():
        value = os.getenv(var, default)
        print(f"✅ {var}: {value}")
    
    print("\nEnvironment Check Results:")
    if all_good:
        print("🎉 All required environment variables are set!")
        print("The VisaBot should be able to start successfully.")
    else:
        print("⚠️  Some required environment variables are missing.")
        print("Please set them in your .env file or environment.")
    
    return all_good

if __name__ == "__main__":
    check_env() 