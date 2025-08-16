#!/usr/bin/env python3
"""
Test script for the video processor to verify YouTube download and video clipping work correctly.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add the backend directory to the Python path
sys.path.append(str(Path(__file__).parent / "backend"))

from video_processor import VideoProcessor

async def test_video_processing():
    """Test the video processing functionality"""
    
    # Test YouTube URL (using a more accessible video)
    test_url = "https://www.youtube.com/watch?v=jNQXAC9IVRw"  # "Me at the zoo" - first YouTube video
    
    # Create a unique job ID
    job_id = f"test_{int(asyncio.get_event_loop().time())}"
    
    print(f"Starting video processing test with job ID: {job_id}")
    print(f"Testing URL: {test_url}")
    
    # Initialize video processor
    processor = VideoProcessor(job_id)
    
    def progress_callback(progress: int, step: str):
        print(f"Progress: {progress}% - {step}")
    
    try:
        # Process the video
        result = await processor.process_video(
            youtube_url=test_url,
            instructions="Find the most engaging moments in this video",
            progress_callback=progress_callback
        )
        
        print("\n✅ Video processing completed successfully!")
        print(f"Output video: {result['video_path']}")
        print(f"Number of clips: {len(result['clips'])}")
        
        # Print clip information
        for i, clip in enumerate(result['clips']):
            print(f"Clip {i+1}: {clip['timeframe']} ({clip['duration']})")
        
        # Check if output file exists and has content
        output_path = Path(result['video_path'])
        if output_path.exists():
            file_size = output_path.stat().st_size
            print(f"Output file size: {file_size} bytes")
            if file_size > 0:
                print("✅ Output video file is valid and has content")
            else:
                print("❌ Output video file is empty")
        else:
            print("❌ Output video file does not exist")
            
    except Exception as e:
        print(f"\n❌ Video processing failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # Run the test
    asyncio.run(test_video_processing()) 