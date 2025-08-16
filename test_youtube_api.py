#!/usr/bin/env python3
"""
Test script for YouTube API key
Run this to verify your API key is working correctly
"""

import os
import asyncio
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv('backend/.env')

# Add backend to path
sys.path.insert(0, 'backend')

from youtube_api_client import YouTubeAPIClient

async def test_api():
    """Test the YouTube API key"""
    print("🧪 Testing YouTube API Key...")
    print("=" * 50)
    
    # Check if API key is set
    api_key = os.getenv('YOUTUBE_API_KEY')
    if not api_key:
        print("❌ YOUTUBE_API_KEY environment variable not found!")
        print("\n📋 To set it locally:")
        print("export YOUTUBE_API_KEY='your_api_key_here'")
        print("\nOr add it to Railway Variables tab")
        return False
    
    print(f"✅ API Key found: {api_key[:10]}...")
    
    # Test API client
    try:
        client = YouTubeAPIClient()
        
        # Test with a public video (Rick Roll)
        test_video_id = "dQw4w9WgXcQ"
        print(f"\n🔍 Testing with video ID: {test_video_id}")
        
        info = await client.get_video_info(test_video_id)
        
        if info:
            print("✅ API working correctly!")
            print(f"📹 Video title: {info.get('title', 'Unknown')}")
            print(f"👁️ View count: {info.get('view_count', 'Unknown')}")
            print(f"⏱️ Duration: {info.get('duration', 'Unknown')}")
            print(f"🔞 Age restricted: {info.get('age_restricted', False)}")
            return True
        else:
            print("❌ API returned no data")
            return False
            
    except Exception as e:
        print(f"❌ API test failed: {str(e)}")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_api())
    
    if success:
        print("\n🎉 Your YouTube API key is working!")
        print("You can now deploy to Railway with confidence.")
    else:
        print("\n⚠️ API key test failed. Please check your setup.")
        print("See YOUTUBE_API_SETUP.md for detailed instructions.")
