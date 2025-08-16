"""
Hybrid Video Processor
Uses YouTube API for metadata and yt-dlp with fallback strategies for downloading
"""

import yt_dlp
import tempfile
import os
import re
import ast
import asyncio
from openai import OpenAI
from moviepy import VideoFileClip, concatenate_videoclips
from typing import Callable, Optional, Dict, Any, List, Tuple
import time
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi
from .youtube_api_client import YouTubeAPIClient


class HybridVideoProcessor:
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
        
        # Initialize YouTube API client
        self.youtube_api = YouTubeAPIClient()
    
    async def process_video(self, youtube_url: str, instructions: str = "", 
                          progress_callback: Optional[Callable[[int, str], None]] = None) -> Dict[str, Any]:
        """Process a YouTube video with progress updates"""
        
        def update_progress(progress: int, step: str):
            if progress_callback:
                progress_callback(progress, step)
        
        try:
            # Step 0: Get video info using YouTube API (0-5%)
            update_progress(0, "Getting video information...")
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
            
            video_info = await self.youtube_api.get_video_info(video_id)
            if video_info:
                update_progress(5, f"Video info retrieved: {video_info.get('title', 'Unknown')}")
            else:
                update_progress(5, "Video info not available via API, proceeding with download...")
            
            # Step 1: Download video with fallback strategies (5-35%)
            update_progress(5, "Downloading video...")
            await self._download_with_fallbacks(youtube_url, str(self.video_path))
            update_progress(35, "Video downloaded successfully")
            
            # Step 2: Get transcript (35-60%)
            update_progress(35, "Getting video transcript...")
            transcript = await self._transcribe_video(youtube_url)
            update_progress(60, "Transcript retrieved")
            
            # Step 3: Process with GPT and identify clips (60-85%)
            update_progress(60, "Analyzing content and identifying clips...")
            timestamps = await self._identify_clips(transcript, instructions)
            update_progress(85, "Clips identified")
            
            # Step 4: Render final video (85-100%)
            update_progress(85, "Rendering final video...")
            clips_info = await self._render_video(str(self.video_path), timestamps)
            update_progress(100, "Video processing completed")
            
            # Clean up temp files
            self._cleanup_temp_files()
            
            return {
                "video_path": str(self.output_path),
                "clips": clips_info,
                "transcript": transcript,
                "video_info": video_info
            }
            
        except Exception as e:
            self._cleanup_temp_files()
            raise e
    
    async def _download_with_fallbacks(self, youtube_url: str, output_path: str):
        """Download video using multiple fallback strategies"""
        strategies = [
            # Strategy 1: yt-dlp with cookies (if available)
            {
                'name': 'yt-dlp with cookies',
                'config': {
                    'cookiefile': 'cookies.txt' if Path("cookies.txt").exists() else None,
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['android', 'web'],
                            'player_skip': ['webpage', 'configs']
                        }
                    },
                    'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]'
                }
            },
            # Strategy 2: yt-dlp with mweb client
            {
                'name': 'yt-dlp with mweb client',
                'config': {
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['mweb', 'web']
                        }
                    },
                    'format': 'best[height<=720]'
                }
            },
            # Strategy 3: yt-dlp with web client only
            {
                'name': 'yt-dlp with web client',
                'config': {
                    'extractor_args': {
                        'youtube': {
                            'player_client': ['web']
                        }
                    },
                    'format': 'best[height<=720]'
                }
            }
        ]
        
        for i, strategy in enumerate(strategies, 1):
            try:
                print(f"Trying download strategy {i}: {strategy['name']}...", flush=True)
                
                ydl_opts = {
                    'outtmpl': output_path,
                    'merge_output_format': 'mp4',
                    'sleep_interval': 2,
                    'max_sleep_interval': 5,
                    'retries': 2,
                    'fragment_retries': 2,
                    'ignoreerrors': False,
                    'no_warnings': False,
                    'quiet': False,
                    'verbose': True
                }
                
                # Apply strategy config
                config = strategy['config']
                if config.get('cookiefile'):
                    ydl_opts['cookiefile'] = config['cookiefile']
                    print(f"Using cookies: {config['cookiefile']}", flush=True)
                
                ydl_opts['extractor_args'] = config['extractor_args']
                ydl_opts['format'] = config['format']
                
                def download():
                    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                        ydl.download([youtube_url])
                
                # Run download in thread pool
                loop = asyncio.get_event_loop()
                await loop.run_in_executor(None, download)
                
                print(f"Download successful with strategy {i}!", flush=True)
                return  # Success, exit
                
            except Exception as e:
                print(f"Strategy {i} failed: {str(e)}", flush=True)
                if i < len(strategies):
                    print("Trying next strategy...", flush=True)
                else:
                    print("All strategies failed!", flush=True)
                    raise e
    
    async def _transcribe_video(self, youtube_url: str) -> List[Tuple[str, float, float]]:
        """Get transcript using YouTube Transcript API with timeout"""
        def get_transcript():
            start_time = time.time()
            print("Getting YouTube transcript...", flush=True)
            
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
            
            try:
                api = YouTubeTranscriptApi()
                transcript_list = api.fetch(video_id, languages=['en'])
                print("YouTube transcript retrieved successfully.", flush=True)
                
                transcript = []
                for segment in transcript_list:
                    text = segment.text
                    start_time_sec = segment.start
                    end_time_sec = segment.start + segment.duration
                    transcript.append((text, start_time_sec, end_time_sec))
                
                end_time = time.time()
                print(f"Transcript retrieval took {end_time - start_time:.2f} seconds")
                print(f"Found {len(transcript)} transcript segments", flush=True)
                return transcript
                
            except Exception as e:
                print(f"Error getting transcript: {str(e)}", flush=True)
                return []
        
        # Run with timeout
        loop = asyncio.get_event_loop()
        try:
            return await asyncio.wait_for(
                loop.run_in_executor(None, get_transcript),
                timeout=30.0
            )
        except asyncio.TimeoutError:
            print("Transcript retrieval timed out, returning empty transcript", flush=True)
            return []
    
    def _extract_video_id(self, youtube_url: str) -> Optional[str]:
        """Extract video ID from YouTube URL"""
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/shorts\/)([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/embed\/([a-zA-Z0-9_-]{11})',
            r'youtube\.com\/v\/([a-zA-Z0-9_-]{11})'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        return None
    
    async def _identify_clips(self, transcript: List[Tuple[str, float, float]], instructions: str) -> List[Dict[str, float]]:
        """Use GPT to identify relevant clips"""
        def process_with_gpt():
            user_prompt = instructions if instructions else "Find the most engaging and important moments in this video"
            
            prompt = f"""
            Here is the transcript of the video: {transcript}
            
            Instructions: {user_prompt}
            
            Please identify the most relevant time intervals in the video based on the instructions.
            Return only the timestamps in this exact format: [{{'start': 12.4, 'end': 54.6}}, ...]
            """
            
            client = OpenAI(api_key=self.openai_key)
            completion = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {
                        "role": "system",
                        "content": """
You are a precise and efficient video clipping assistant.

Given a transcript of a video and a user request, your job is to extract the most relevant time intervals that match the intent of the request.

Provide just enough context for the user to understand what's happening, but avoid unnecessary filler. Be decisive—separate clips only when the topic, speaker, or scene clearly shifts. Minimize the number of clips while maintaining clarity.

Return only a list of timestamp dictionaries in this exact format:
[{'start': 12.4, 'end': 54.6}, {'start': 110.2, 'end': 132.0}]

Do not include any explanation or commentary—just the list of relevant timestamp ranges.
"""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]
            )
            
            print("GPT RESPONSE:", completion.choices[0].message.content, flush=True)
            
            # Extract timestamps
            match = re.search(r"\[\s*{.*?}\s*\]", completion.choices[0].message.content, re.DOTALL)
            if not match:
                raise ValueError("No valid timestamp list found in GPT response")
            
            return ast.literal_eval(match.group(0))
        
        # Run GPT processing in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, process_with_gpt)
    
    async def _render_video(self, video_path: str, timestamps: List[Dict[str, float]]) -> List[Dict[str, Any]]:
        """Render video clips based on timestamps"""
        def render():
            clips_info = []
            
            with VideoFileClip(video_path) as video:
                for i, timestamp in enumerate(timestamps):
                    start_time = timestamp['start']
                    end_time = timestamp['end']
                    
                    # Create clip
                    clip = video.subclip(start_time, end_time)
                    
                    # Save clip
                    clip_path = self.storage_dir / f"{self.job_id}_clip_{i}.mp4"
                    clip.write_videofile(str(clip_path), codec='libx264', audio_codec='aac')
                    
                    clips_info.append({
                        'path': str(clip_path),
                        'start': start_time,
                        'end': end_time,
                        'duration': end_time - start_time
                    })
                    
                    clip.close()
            
            return clips_info
        
        # Run rendering in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, render)
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            if self.temp_dir.exists():
                import shutil
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Error cleaning up temp files: {e}")
