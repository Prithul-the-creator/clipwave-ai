#!/usr/bin/env python3
"""
Railway-specific start script for ClipWave AI Backend
"""
import os
import sys
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get port from Railway environment
    port = int(os.getenv("PORT", 8000))
    host = "0.0.0.0"
    
    print(f"🚀 Starting ClipWave AI Backend on {host}:{port}")
    print(f"📁 Current directory: {os.getcwd()}")
    print(f"🐍 Python version: {sys.version}")
    
    # Add backend to Python path
    backend_path = os.path.join(os.getcwd(), "backend")
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
        print(f"✅ Added {backend_path} to Python path")
    else:
        print(f"❌ Backend directory not found at {backend_path}")
    
    try:
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info"
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        sys.exit(1)
