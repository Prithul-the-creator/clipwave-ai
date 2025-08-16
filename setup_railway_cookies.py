#!/usr/bin/env python3
"""
Script to help set up YouTube cookies in Railway environment variables.

This script reads your cookies.txt file and formats it for Railway's environment variables.
"""

import os
import sys

def read_cookies_file(file_path='cookies.txt'):
    """Read cookies from file and return as string"""
    try:
        with open(file_path, 'r') as f:
            return f.read()
    except FileNotFoundError:
        print(f"❌ Error: {file_path} not found")
        return None
    except Exception as e:
        print(f"❌ Error reading {file_path}: {e}")
        return None

def main():
    print("🍪 YouTube Cookies Setup for Railway")
    print("=" * 40)
    
    # Read cookies file
    cookies_content = read_cookies_file()
    if not cookies_content:
        print("\n📋 To set up cookies:")
        print("1. Export your cookies from browser using 'Get cookies.txt' extension")
        print("2. Save as 'cookies.txt' in this directory")
        print("3. Run this script again")
        return
    
    # Count YouTube cookies
    youtube_cookies = [line for line in cookies_content.split('\n') 
                      if '.youtube.com' in line and not line.startswith('#')]
    
    print(f"✅ Found {len(youtube_cookies)} YouTube cookies")
    print(f"📋 Total file size: {len(cookies_content)} characters")
    
    # Show sample cookies
    if youtube_cookies:
        print("\n📋 Sample cookies:")
        for i, cookie in enumerate(youtube_cookies[:3]):
            parts = cookie.split('\t')
            if len(parts) >= 6:
                print(f"   {i+1}. {parts[5]}: {parts[6][:20]}...")
    
    print("\n🚀 To set up in Railway:")
    print("1. Go to your Railway project dashboard")
    print("2. Navigate to 'Variables' tab")
    print("3. Add a new variable:")
    print("   - Name: YOUTUBE_COOKIES")
    print("   - Value: [Copy the content below]")
    print("\n" + "=" * 40)
    print("COOKIES CONTENT TO COPY:")
    print("=" * 40)
    print(cookies_content)
    print("=" * 40)
    
    print("\n💡 Tips:")
    print("- Make sure to copy the ENTIRE content including the header")
    print("- The variable will be automatically used by the application")
    print("- You can update cookies anytime by changing this variable")
    print("- No need to rebuild the Docker image!")

if __name__ == "__main__":
    main()
