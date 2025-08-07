#!/usr/bin/env python3
"""
Debug script to check environment variables and API keys
"""
import os
from pathlib import Path

# Add the app directory to Python path
import sys
sys.path.append(str(Path(__file__).parent / "app"))

from app.core.config import settings

def main():
    print("🔍 Environment Variable Debug")
    print("=" * 50)
    
    # Check environment variables directly
    print("📋 Environment Variables:")
    openai_key_env = os.getenv("OPENAI_API_KEY")
    groq_key_env = os.getenv("GROQ_API_KEY")
    
    print(f"OPENAI_API_KEY (from env): {'✅ Set' if openai_key_env else '❌ Not set'}")
    if openai_key_env:
        print(f"   Length: {len(openai_key_env)}")
        print(f"   Starts with: {openai_key_env[:10]}...")
        print(f"   Format check: {'✅ OpenAI format' if openai_key_env.startswith('sk-') and len(openai_key_env) < 100 else '❌ Wrong format'}")
    
    print(f"GROQ_API_KEY (from env): {'✅ Set' if groq_key_env else '❌ Not set'}")
    if groq_key_env:
        print(f"   Length: {len(groq_key_env)}")
        print(f"   Starts with: {groq_key_env[:10]}...")
    
    print("\n📋 Settings Object:")
    print(f"OPENAI_API_KEY (from settings): {'✅ Set' if settings.OPENAI_API_KEY else '❌ Not set'}")
    if settings.OPENAI_API_KEY:
        print(f"   Length: {len(settings.OPENAI_API_KEY)}")
        print(f"   Starts with: {settings.OPENAI_API_KEY[:10]}...")
        print(f"   Format check: {'✅ OpenAI format' if settings.OPENAI_API_KEY.startswith('sk-') and len(settings.OPENAI_API_KEY) < 100 else '❌ Wrong format'}")
    
    print(f"GROQ_API_KEY (from settings): {'✅ Set' if settings.GROQ_API_KEY else '❌ Not set'}")
    if settings.GROQ_API_KEY:
        print(f"   Length: {len(settings.GROQ_API_KEY)}")
        print(f"   Starts with: {settings.GROQ_API_KEY[:10]}...")
    
    print("\n🔧 Configuration:")
    print(f"OpenAI Model: {settings.OPENAI_MODEL}")
    print(f"OpenAI Max Tokens: {settings.OPENAI_MAX_TOKENS}")
    print(f"OpenAI Temperature: {settings.OPENAI_TEMPERATURE}")
    
    print("\n💡 Recommendations:")
    if not openai_key_env:
        print("❌ OPENAI_API_KEY is not set in your .env file")
        print("   Add: OPENAI_API_KEY=your_openai_api_key_here")
    elif openai_key_env and len(openai_key_env) > 100:
        print("❌ Your OPENAI_API_KEY looks like a Groq API key (too long)")
        print("   Please replace it with a proper OpenAI API key")
    elif openai_key_env and not openai_key_env.startswith('sk-'):
        print("❌ Your OPENAI_API_KEY doesn't start with 'sk-'")
        print("   Please check your OpenAI API key format")
    else:
        print("✅ OPENAI_API_KEY looks correct")
    
    if groq_key_env:
        print("⚠️  GROQ_API_KEY is still set - you can remove it if not needed")

if __name__ == "__main__":
    main() 