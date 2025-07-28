#!/usr/bin/env python3
"""
Chatore Discord Bot - Main Entry Point
A Discord chatbot powered by Gemini 2.5 Flash with personality and memory
"""

import os
import sys
import asyncio
from dotenv import load_dotenv

# Fix for Windows event loop issue
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Load environment variables
load_dotenv()

from bot.luna_bot import LunaBot

def main():
    """Main entry point for Chatore bot"""
    # Check for required environment variables
    discord_token = os.getenv('DISCORD_TOKEN')
    gemini_key = os.getenv('GEMINI_API_KEY')
    
    if not discord_token:
        print("❌ DISCORD_TOKEN not found in .env file!")
        return
    
    if not gemini_key:
        print("❌ GEMINI_API_KEY not found in .env file!")
        print("💡 You can also add GEMINI_API_KEY_2 and GEMINI_API_KEY_3 for fallback")
        return
    
    # Start keep-alive server for hosting services (optional)
    try:
        from keep_alive import keep_alive
        keep_alive()
        print("🌐 Keep-alive server started for hosting compatibility")
    except ImportError:
        print("ℹ️ Keep-alive server not available (running locally)")
    except Exception as e:
        print(f"⚠️ Keep-alive server failed to start: {e}")
    
    # Initialize and run the bot
    bot = LunaBot()
    
    try:
        print("🍽️ Starting Chatore...")
        bot.run(discord_token)
    except KeyboardInterrupt:
        print("\n👋 Chatore shutting down gracefully...")
    except Exception as e:
        print(f"❌ Error starting Chatore: {e}")

if __name__ == "__main__":
    main()