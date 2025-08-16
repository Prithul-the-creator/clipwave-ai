import yt_dlp
import tempfile
import os
import re
import ast
import subprocess
import asyncio
from openai import OpenAI
from typing import Callable, Optional, Dict, Any, List, Tuple
import threading
import time
from pathlib import Path


class VideoProcessor:
    def __init__(self, job_id: str, storage_dir: str = "storage/videos"):
        self.job_id = job_id
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        
        # Create temp folder for this job
        self.temp_dir = Path(tempfile.mkdtemp())
        self.video_path = self.temp_dir / "input.mp4"
        self.output_path = self.storage_dir / f"{job_id}.mp4"
        
        # OpenAI API key from environment variables
        self.openai_key = os.getenv("OPENAI_API_KEY")
        if not self.openai_key:
            raise ValueError("OPENAI_API_KEY environment variable is required")
    
    async def process_video(self, youtube_url: str, instructions: str = "", 
                          progress_callback: Optional[Callable[[int, str], None]] = None) -> Dict[str, Any]:
        """Process a YouTube video with progress updates"""
        
        def update_progress(progress: int, step: str):
            if progress_callback:
                progress_callback(progress, step)
        
        try:
            # Step 1: Download video (0-50%)
            update_progress(0, "Downloading video...")
            await self._download_youtube_video(youtube_url, str(self.video_path))
            update_progress(50, "Video downloaded successfully")
            
            # Step 2: Create a simple clip (50-100%)
            update_progress(50, "Creating video clip...")
            clips_info = await self._create_simple_clip(str(self.video_path))
            update_progress(100, "Video processing completed")
            
            # Clean up temp files
            self._cleanup_temp_files()
            
            return {
                "video_path": str(self.output_path),
                "clips": clips_info,
                "transcript": [("Demo transcript - ML features coming soon", 0.0, 10.0)]
            }
            
        except Exception as e:
            self._cleanup_temp_files()
            raise e
    
    async def _download_youtube_video(self, youtube_url: str, output_path: str):
        """Download YouTube video"""
        def download():
            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                'outtmpl': output_path,
                'merge_output_format': 'mp4',
                # Add cookie handling
                'cookiesfrombrowser': ('chrome',),  # Try to get cookies from Chrome
                # Alternative cookie sources
                'cookiefile': 'cookies.txt',  # If you have a cookies.txt file
                # Add user agent to avoid bot detection
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                },
                # Retry options
                'retries': 3,
                'fragment_retries': 3,
                # Skip age-restricted content if possible
                'age_limit': 18,
                # Verbose output for debugging
                'verbose': True
            }
            
            try:
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([youtube_url])
            except Exception as e:
                print(f"Download failed with cookies: {e}")
                # Fallback: try without cookies
                ydl_opts_fallback = {
                    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                    'outtmpl': output_path,
                    'merge_output_format': 'mp4',
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    },
                    'retries': 3,
                    'fragment_retries': 3,
                    'verbose': True
                }
                with yt_dlp.YoutubeDL(ydl_opts_fallback) as ydl:
                    ydl.download([youtube_url])
        
        # Run download in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download)
    
    async def _create_simple_clip(self, video_path: str) -> List[Dict[str, Any]]:
        """Create a simple clip using ffmpeg"""
        def create_clip():
            # Get video duration using ffprobe
            try:
                import json
                result = subprocess.run([
                    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path
                ], capture_output=True, text=True)
                duration = float(json.loads(result.stdout)["format"]["duration"])
            except:
                duration = 60.0  # Default duration
            
            # Create a simple clip (first 30 seconds or half the video)
            clip_duration = min(30.0, duration / 2)
            
            # Use ffmpeg to create clip
            cmd = [
                "ffmpeg", "-y", "-i", video_path,
                "-ss", "0", "-t", str(clip_duration),
                "-c", "copy", str(self.output_path)
            ]
            subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            
            return [{
                "id": "1",
                "title": "Demo Clip",
                "duration": f"{clip_duration:.1f}s",
                "timeframe": f"0.0s - {clip_duration:.1f}s",
                "start": 0.0,
                "end": clip_duration
            }]
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, create_clip)
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temp files: {e}")
