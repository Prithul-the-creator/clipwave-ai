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
    
    # List files in current directory
    print(f"📂 Files in current directory: {os.listdir('.')}")
    
    # Add backend to Python path
    backend_path = os.path.join(os.getcwd(), "backend")
    if os.path.exists(backend_path):
        sys.path.insert(0, backend_path)
        print(f"✅ Added {backend_path} to Python path")
        print(f"📂 Files in backend directory: {os.listdir(backend_path)}")
    else:
        print(f"❌ Backend directory not found at {backend_path}")
        # Try alternative paths
        alt_paths = ["/app/backend", "./backend", "../backend"]
        for alt_path in alt_paths:
            if os.path.exists(alt_path):
                sys.path.insert(0, alt_path)
                print(f"✅ Added {alt_path} to Python path")
                break
    
    # Check if main.py exists
    main_paths = ["main.py", "backend/main.py", "/app/backend/main.py"]
    main_found = False
    for main_path in main_paths:
        if os.path.exists(main_path):
            print(f"✅ Found main.py at: {main_path}")
            main_found = True
            break
    
    if not main_found:
        print("❌ main.py not found in any expected location")
        sys.exit(1)
    
    try:
        print("🔄 Starting uvicorn server...")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=False,
            log_level="info",
            access_log=True
        )
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
