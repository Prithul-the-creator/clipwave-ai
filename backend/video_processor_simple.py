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
from youtube_transcript_api import YouTubeTranscriptApi


def extract_youtube_transcript(video_id: str) -> List[Dict[str, Any]]:
    """
    Extract transcript from YouTube video using youtube_transcript_api
    
    Args:
        video_id (str): YouTube video ID (e.g., 'dQw4w9WgXcQ')
    
    Returns:
        List[Dict[str, Any]]: List of transcript entries with 'text', 'start', 'duration'
    
    Example:
        transcript = extract_youtube_transcript('dQw4w9WgXcQ')
        for entry in transcript:
            print(f"[{entry['start']}s] {entry['text']}")
    """
    try:
        from youtube_transcript_api import YouTubeTranscriptApi
        transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
        return transcript_list
    except Exception as e:
        print(f"Error extracting transcript for video {video_id}: {e}")
        return []


def extract_video_id_from_url(youtube_url: str) -> str:
    """
    Extract video ID from various YouTube URL formats
    
    Args:
        youtube_url (str): YouTube URL (e.g., 'https://youtube.com/watch?v=dQw4w9WgXcQ')
    
    Returns:
        str: Video ID
    
    Example:
        video_id = extract_video_id_from_url('https://youtube.com/watch?v=dQw4w9WgXcQ')
        print(video_id)  # Output: 'dQw4w9WgXcQ'
    """
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, youtube_url)
        if match:
            return match.group(1)
    
    raise ValueError(f"Could not extract video ID from URL: {youtube_url}")


def get_formatted_transcript(video_id: str) -> List[Tuple[str, float, float]]:
    """
    Get formatted transcript with (text, start_time, end_time) tuples
    
    Args:
        video_id (str): YouTube video ID
    
    Returns:
        List[Tuple[str, float, float]]: List of (text, start_time, end_time) tuples
    
    Example:
        formatted = get_formatted_transcript('dQw4w9WgXcQ')
        for text, start, end in formatted:
            print(f"[{start:.1f}s-{end:.1f}s] {text}")
    """
    transcript_list = extract_youtube_transcript(video_id)
    formatted_transcript = []
    
    for entry in transcript_list:
        text = entry['text']
        start_time = entry['start']
        end_time = start_time + entry['duration']
        formatted_transcript.append((text, start_time, end_time))
    
    return formatted_transcript


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
            # Step 1: Get video ID and extract transcript (0-20%)
            update_progress(0, "Extracting transcript...")
            video_id = self._extract_video_id(youtube_url)
            transcript_data = await self._get_transcript(video_id)
            update_progress(20, "Transcript extracted successfully")
            
            # Step 2: Download video (20-60%)
            update_progress(20, "Downloading video...")
            await self._download_youtube_video(youtube_url, str(self.video_path))
            update_progress(60, "Video downloaded successfully")
            
            # Step 3: Analyze transcript and create clips (60-100%)
            update_progress(60, "Analyzing content and creating clips...")
            clips_info = await self._analyze_and_create_clips(str(self.video_path), transcript_data, instructions)
            update_progress(100, "Video processing completed")
            
            # Clean up temp files
            self._cleanup_temp_files()
            
            return {
                "video_path": str(self.output_path),
                "clips": clips_info,
                "transcript": transcript_data
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
    
    def _extract_video_id(self, youtube_url: str) -> str:
        """Extract video ID from YouTube URL"""
        # Handle different YouTube URL formats
        patterns = [
            r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
            r'youtube\.com/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
    
    async def _get_transcript(self, video_id: str) -> List[Tuple[str, float, float]]:
        """Get transcript using YouTube Transcript API"""
        def get_transcript():
            try:
                from youtube_transcript_api import YouTubeTranscriptApi
                transcript_list = YouTubeTranscriptApi.get_transcript(video_id, languages=['en'])
                # Convert to our format: (text, start_time, end_time)
                formatted_transcript = []
                for entry in transcript_list:
                    text = entry['text']
                    start_time = entry['start']
                    end_time = start_time + entry['duration']
                    formatted_transcript.append((text, start_time, end_time))
                return formatted_transcript
            except Exception as e:
                print(f"Error getting transcript: {e}")
                # Return empty transcript if API fails
                return []
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_transcript)
    
    async def _analyze_and_create_clips(self, video_path: str, transcript_data: List[Tuple[str, float, float]], instructions: str) -> List[Dict[str, Any]]:
        """Analyze transcript and create intelligent clips"""
        def analyze_and_create():
            if not transcript_data:
                # Fallback to simple clip if no transcript
                return self._create_simple_clip_sync(video_path)
            
            # Use OpenAI to analyze transcript and find interesting moments
            clips = self._analyze_transcript_with_gpt(transcript_data, instructions)
            
            if not clips:
                # Fallback to simple clip if analysis fails
                return self._create_simple_clip_sync(video_path)
            
            # Create clips based on analysis
            return self._create_clips_from_timestamps(video_path, clips)
        
        # Run in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, analyze_and_create)
    
    def _analyze_transcript_with_gpt(self, transcript_data: List[Tuple[str, float, float]], instructions: str) -> List[Dict[str, Any]]:
        """Use GPT to analyze transcript and find interesting moments"""
        try:
            client = OpenAI(api_key=self.openai_key)
            
            # Prepare transcript text
            transcript_text = "\n".join([f"[{start:.1f}s-{end:.1f}s] {text}" for text, start, end in transcript_data])
            
            # Create prompt for analysis
            prompt = f"""
            Analyze this YouTube video transcript and identify 3-5 most engaging moments that would make good short clips.
            
            User instructions: {instructions if instructions else "Find the most interesting and engaging moments"}
            
            Transcript:
            {transcript_text}
            
            Return a JSON array of clips with this format:
            [
                {{
                    "title": "Brief descriptive title",
                    "start_time": start_time_in_seconds,
                    "end_time": end_time_in_seconds,
                    "reason": "Why this moment is engaging"
                }}
            ]
            
            Keep clips between 10-60 seconds. Focus on moments with clear, engaging content.
            """
            
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[{"role": "user", "content": prompt}],
                temperature=0.7,
                max_tokens=1000
            )
            
            # Parse response
            content = response.choices[0].message.content
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', content, re.DOTALL)
            if json_match:
                clips_data = ast.literal_eval(json_match.group())
                return clips_data
            else:
                print(f"Could not parse GPT response: {content}")
                return []
                
        except Exception as e:
            print(f"Error analyzing transcript with GPT: {e}")
            return []
    
    def _create_clips_from_timestamps(self, video_path: str, clips_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Create video clips from GPT-analyzed timestamps"""
        created_clips = []
        
        for i, clip_info in enumerate(clips_data):
            try:
                start_time = clip_info.get('start_time', 0)
                end_time = clip_info.get('end_time', start_time + 30)
                title = clip_info.get('title', f'Clip {i+1}')
                
                # Ensure reasonable duration
                duration = end_time - start_time
                if duration < 5:
                    end_time = start_time + 30
                elif duration > 60:
                    end_time = start_time + 60
                
                # Create clip filename
                clip_filename = f"{self.job_id}_clip_{i+1}.mp4"
                clip_path = self.storage_dir / clip_filename
                
                # Use ffmpeg to create clip
                cmd = [
                    "ffmpeg", "-y", "-i", video_path,
                    "-ss", str(start_time), "-t", str(duration),
                    "-c", "copy", str(clip_path)
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                created_clips.append({
                    "id": str(i+1),
                    "title": title,
                    "duration": f"{duration:.1f}s",
                    "timeframe": f"{start_time:.1f}s - {end_time:.1f}s",
                    "start": start_time,
                    "end": end_time,
                    "video_path": str(clip_path)
                })
                
            except Exception as e:
                print(f"Error creating clip {i+1}: {e}")
                continue
        
        return created_clips
    
    def _create_simple_clip_sync(self, video_path: str) -> List[Dict[str, Any]]:
        """Synchronous version of simple clip creation"""
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
            "title": "Auto-generated Clip",
            "duration": f"{clip_duration:.1f}s",
            "timeframe": f"0.0s - {clip_duration:.1f}s",
            "start": 0.0,
            "end": clip_duration,
            "video_path": str(self.output_path)
        }]
    
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
