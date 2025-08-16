#!/usr/bin/env python3
"""
Test script to verify backend can start properly
"""
import os
import sys

def test_imports():
    """Test if all required modules can be imported"""
    print("🧪 Testing imports...")
    
    try:
        import fastapi
        print("✅ FastAPI imported successfully")
    except Exception as e:
        print(f"❌ FastAPI import failed: {e}")
        return False
    
    try:
        import uvicorn
        print("✅ Uvicorn imported successfully")
    except Exception as e:
        print(f"❌ Uvicorn import failed: {e}")
        return False
    
    try:
        import openai
        print("✅ OpenAI imported successfully")
    except Exception as e:
        print(f"❌ OpenAI import failed: {e}")
        return False
    
    try:
        import whisper
        print("✅ Whisper imported successfully")
    except Exception as e:
        print(f"❌ Whisper import failed: {e}")
        return False
    
    try:
        import yt_dlp
        print("✅ yt-dlp imported successfully")
    except Exception as e:
        print(f"❌ yt-dlp import failed: {e}")
        return False
    
    try:
        import moviepy
        print("✅ MoviePy imported successfully")
    except Exception as e:
        print(f"❌ MoviePy import failed: {e}")
        return False
    
    return True

def test_backend_imports():
    """Test if backend modules can be imported"""
    print("\n🧪 Testing backend imports...")
    
    # Add backend to path
    backend_path = os.path.join(os.getcwd(), "backend")
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
        print(f"✅ Added {backend_path} to Python path")
    else:
        print(f"❌ Backend directory not found at {backend_path}")
        return False
    
    try:
        from main import app
        print("✅ Backend app imported successfully")
    except Exception as e:
        print(f"❌ Backend app import failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    
    try:
        from video_processor import VideoProcessor
        print("✅ VideoProcessor imported successfully")
    except Exception as e:
        print(f"❌ VideoProcessor import failed: {e}")
        return False
    
    try:
        from job_manager import JobManager
        print("✅ JobManager imported successfully")
    except Exception as e:
        print(f"❌ JobManager import failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    print("🚀 Testing ClipWave AI Backend...")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Test basic imports
    if not test_imports():
        print("❌ Basic imports failed")
        sys.exit(1)
    
    # Test backend imports
    if not test_backend_imports():
        print("❌ Backend imports failed")
        sys.exit(1)
    
    print("\n✅ All tests passed! Backend should start successfully.") 