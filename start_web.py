#!/usr/bin/env python3
"""
Simple startup script for the Discord Moderation Bot web interface.
This script starts the web server with real-time functionality.
"""

import asyncio
import sys
import os

# Add current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def main():
    """Start the web interface"""
    try:
        from web import serve
        print("🚀 Starting Discord Moderation Bot Web Interface...")
        print("📱 Open your browser and go to: http://localhost:8000")
        print("🔌 Real-time updates will be available via WebSocket")
        print("⏹️  Press Ctrl+C to stop the server")
        print("-" * 50)
        
        await serve()
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("   Make sure all dependencies are installed:")
        print("   pip install -r requirements.txt")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Error starting web interface: {e}")
        sys.exit(1)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 Web interface stopped by user")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
