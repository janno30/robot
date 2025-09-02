#!/usr/bin/env python3
"""
Test script to demonstrate real-time counting functionality.
This script simulates moderation actions to show how the web interface updates automatically.
"""

import time
import requests
import json
from database import ModerationDB

def test_realtime_functionality():
    """Test the real-time functionality by performing moderation actions"""
    
    print("🤖 Testing Real-time Moderation Bot Web Interface")
    print("=" * 50)
    
    # Initialize database
    db = ModerationDB()
    
    # Get initial stats
    try:
        response = requests.get("http://localhost:8000/api/stats")
        if response.status_code == 200:
            initial_stats = response.json()
            print(f"✅ Web interface is running at http://localhost:8000")
            print(f"📊 Initial stats: {json.dumps(initial_stats, indent=2)}")
        else:
            print(f"❌ Failed to get stats: {response.status_code}")
            return
    except requests.exceptions.ConnectionError:
        print("❌ Web interface is not running. Please start it first with:")
        print("   python web.py")
        return
    
    print("\n🔄 Simulating moderation actions...")
    print("   Open http://localhost:8000 in your browser to see real-time updates!")
    print("   (Make sure you're connected via WebSocket)")
    
    # Simulate adding a warning
    print("\n1️⃣ Adding a warning...")
    db.add_warning(123456789, 987654321, "Test warning")
    time.sleep(2)
    
    # Simulate adding a mute
    print("2️⃣ Adding a mute...")
    db.add_mute(123456789, 987654321, 300, "Test mute for 5 minutes")
    time.sleep(2)
    
    # Simulate adding a ban
    print("3️⃣ Adding a ban...")
    db.add_ban(123456789, 987654321, "Test ban")
    time.sleep(2)
    
    # Simulate logging a kick
    print("4️⃣ Logging a kick...")
    db.log_kick(123456789, 987654321, "Test kick")
    time.sleep(2)
    
    # Simulate adding another warning
    print("5️⃣ Adding another warning...")
    db.add_warning(987654321, 123456789, "Another test warning")
    time.sleep(2)
    
    # Get final stats
    try:
        response = requests.get("http://localhost:8000/api/stats")
        if response.status_code == 200:
            final_stats = response.json()
            print(f"\n📊 Final stats: {json.dumps(final_stats, indent=2)}")
        else:
            print(f"❌ Failed to get final stats: {response.status_code}")
    except requests.exceptions.ConnectionError:
        print("❌ Web interface connection lost")
    
    print("\n✅ Test completed!")
    print("   The web interface should have updated in real-time for each action.")
    print("   If you didn't see real-time updates, make sure:")
    print("   1. You're viewing http://localhost:8000 in your browser")
    print("   2. The WebSocket connection is established (green dot)")
    print("   3. You're not refreshing the page manually")

if __name__ == "__main__":
    test_realtime_functionality()
