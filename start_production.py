#!/usr/bin/env python3
"""
Production start script for ClipWave AI Backend
"""
import os
import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

if __name__ == "__main__":
    # Get port from environment or default to 8000
    port = int(os.getenv("PORT", 8000))
    host = os.getenv("HOST", "0.0.0.0")
    
    print(f"Starting ClipWave AI Backend on {host}:{port}")
    
    # Add backend to Python path
    import sys
    sys.path.insert(0, os.path.join(os.getcwd(), "backend"))
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=False,  # Disable reload in production
        log_level="info"
    )
