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
import whisper
from moviepy import VideoFileClip, concatenate_videoclips


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
            # Step 1: Download video (0-25%)
            update_progress(0, "Downloading video...")
            await self._download_youtube_video(youtube_url, str(self.video_path))
            update_progress(25, "Video downloaded successfully")
            
            # Step 2: Transcribe video with Whisper (25-50%)
            update_progress(25, "Transcribing video with AI...")
            transcript = await self._transcribe_video(str(self.video_path))
            update_progress(50, "Transcription completed")
            
            # Step 3: Analyze with GPT and identify clips (50-75%)
            update_progress(50, "Analyzing content and identifying clips...")
            timestamps = await self._identify_clips(transcript, instructions)
            update_progress(75, "Clips identified")
            
            # Step 4: Create clips with MoviePy (75-100%)
            update_progress(75, "Creating video clips...")
            clips_info = await self._create_clips(str(self.video_path), timestamps)
            update_progress(100, "Video processing completed")
            
            # Clean up temp files
            self._cleanup_temp_files()
            
            return {
                "video_path": str(self.output_path),
                "clips": clips_info,
                "transcript": transcript
            }
            
        except Exception as e:
            self._cleanup_temp_files()
            raise e
    
    async def _download_youtube_video(self, youtube_url: str, output_path: str):
        """Download YouTube video"""
        def download():
            # Check if cookies file exists in multiple locations
            import os
            possible_cookie_paths = [
                'cookies.txt',  # Current directory
                '../cookies.txt',  # Parent directory
                '/app/cookies.txt',  # Railway container root
                './cookies.txt'  # Relative to current
            ]
            
            cookies_path = None
            for path in possible_cookie_paths:
                if os.path.exists(path):
                    print(f"✅ Cookies file found at: {os.path.abspath(path)}")
                    cookies_path = path
                    break
            
            if not cookies_path:
                print(f"❌ Cookies file not found in any location")
                print(f"📁 Current directory: {os.getcwd()}")
                print(f"📂 Files in current directory: {os.listdir('.')}")
                if os.path.exists('..'):
                    print(f"📂 Files in parent directory: {os.listdir('..')}")
            else:
                # Check cookies file content
                try:
                    with open(cookies_path, 'r') as f:
                        lines = f.readlines()
                        youtube_cookies = [line for line in lines if '.youtube.com' in line]
                        print(f"🍪 Found {len(youtube_cookies)} YouTube cookies")
                        if youtube_cookies:
                            print(f"📋 Sample cookies: {youtube_cookies[:2]}")
                except Exception as e:
                    print(f"❌ Error reading cookies file: {e}")
                    cookies_path = None
            
            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                'outtmpl': output_path,
                'merge_output_format': 'mp4',
                # Use cookies file if available
                'cookiefile': cookies_path,
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
    
    async def _transcribe_video(self, video_path: str) -> List[Tuple[str, float, float]]:
        """Transcribe video using Whisper"""
        def transcribe():
            print("Starting Whisper transcription...")
            model = whisper.load_model("base")
            print("Model loaded.")
            result = model.transcribe(video_path, language="en")
            print("Whisper transcription complete.")
            
            # Extract segments with timestamps
            segments = []
            for segment in result["segments"]:
                segments.append((
                    segment["text"].strip(),
                    segment["start"],
                    segment["end"]
                ))
            return segments
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, transcribe)
    
    async def _identify_clips(self, transcript: List[Tuple[str, float, float]], instructions: str) -> List[Dict[str, Any]]:
        """Use GPT to identify interesting clips based on transcript"""
        client = OpenAI(api_key=self.openai_key)
        
        # Prepare transcript text
        transcript_text = "\n".join([f"[{start:.1f}s-{end:.1f}s] {text}" for text, start, end in transcript])
        
        # Create prompt for GPT
        prompt = f"""
        Analyze this video transcript and identify the most engaging/interesting moments.
        
        Video Transcript:
        {transcript_text}
        
        User Instructions: {instructions if instructions else "Find the most engaging moments"}
        
        Return a JSON array of clips with this format:
        [
            {{
                "start": start_time_in_seconds,
                "end": end_time_in_seconds,
                "title": "Brief description of the clip",
                "reason": "Why this moment is engaging"
            }}
        ]
        
        Limit to 3-5 clips, each 10-30 seconds long. Focus on moments with:
        - Key insights or important information
        - Engaging storytelling
        - Humor or emotional moments
        - Clear explanations
        """
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse GPT response
            content = response.choices[0].message.content
            clips_data = ast.literal_eval(content)
            
            return clips_data
            
        except Exception as e:
            print(f"GPT analysis failed: {e}")
            # Fallback: create simple clips
            return [
                {"start": 0, "end": 30, "title": "Opening", "reason": "Video beginning"},
                {"start": len(transcript) * 0.3, "end": len(transcript) * 0.3 + 30, "title": "Middle", "reason": "Middle section"},
                {"start": len(transcript) * 0.7, "end": len(transcript) * 0.7 + 30, "title": "Ending", "reason": "Video ending"}
            ]
    
    async def _create_clips(self, video_path: str, timestamps: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create video clips using MoviePy"""
        def create_clips():
            clips_info = []
            video = VideoFileClip(video_path)
            
            for i, clip_data in enumerate(timestamps):
                start_time = clip_data["start"]
                end_time = clip_data["end"]
                
                # Ensure timestamps are within video bounds
                start_time = max(0, min(start_time, video.duration - 5))
                end_time = min(end_time, video.duration)
                
                if end_time > start_time:
                    # Extract clip
                    clip = video.subclip(start_time, end_time)
                    
                    # Save clip
                    clip_filename = f"clip_{i+1}_{self.job_id}.mp4"
                    clip_path = self.storage_dir / clip_filename
                    clip.write_videofile(str(clip_path), codec='libx264', audio_codec='aac', verbose=False, logger=None)
                    
                    clips_info.append({
                        "id": str(i + 1),
                        "title": clip_data.get("title", f"Clip {i+1}"),
                        "duration": f"{end_time - start_time:.1f}s",
                        "timeframe": f"{start_time:.1f}s - {end_time:.1f}s",
                        "start": start_time,
                        "end": end_time,
                        "reason": clip_data.get("reason", "AI-selected moment")
                    })
                    
                    clip.close()
            
            video.close()
            return clips_info
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, create_clips)
    
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
