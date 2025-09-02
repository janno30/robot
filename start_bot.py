#!/usr/bin/env python3
"""
Discord Moderation Bot Startup Script
This script helps you get the bot running quickly.
"""

import os
import sys

def check_env_file():
    """Check if .env file exists and has required content"""
    if not os.path.exists('.env'):
        print("❌ .env file not found!")
        print("\n📝 To create your .env file:")
        print("1. Copy env_template.txt to .env")
        print("2. Edit .env and add your bot token")
        print("3. Run this script again")
        return False
    
    # Check if BOT_TOKEN is set
    with open('.env', 'r') as f:
        content = f.read()
        if 'BOT_TOKEN=your_bot_token_here' in content or 'BOT_TOKEN=' not in content:
            print("❌ BOT_TOKEN not set in .env file!")
            print("\n📝 Please edit your .env file and set:")
            print("BOT_TOKEN=your_actual_bot_token_here")
            return False
    
    print("✅ .env file found and configured!")
    return True

def check_dependencies():
    """Check if required packages are installed"""
    try:
        import discord
        import dotenv
        print("✅ All required packages are installed!")
        return True
    except ImportError as e:
        print(f"❌ Missing package: {e}")
        print("\n📝 To install dependencies, run:")
        print("pip install -r requirements.txt")
        return False

def main():
    """Main startup function"""
    print("🚀 Discord Moderation Bot Startup Check")
    print("=" * 40)
    
    # Check dependencies
    if not check_dependencies():
        return
    
    # Check environment file
    if not check_env_file():
        return
    
    print("\n✅ All checks passed! Starting bot...")
    print("=" * 40)
    
    # Import and run the main bot
    try:
        from main import main as run_bot
        import asyncio
        asyncio.run(run_bot())
    except Exception as e:
        print(f"❌ Failed to start bot: {e}")
        print("\n📝 Troubleshooting:")
        print("1. Make sure your bot token is correct")
        print("2. Check that your bot has proper permissions")
        print("3. Verify your bot is invited to your server")

if __name__ == "__main__":
    main()
