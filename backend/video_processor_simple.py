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
import json
import urllib.parse


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
    
    def _extract_video_id(self, youtube_url: str) -> str:
        """Extract video ID from YouTube URL"""
        # Handle various YouTube URL formats
        patterns = [
            r'(?:youtube\.com\/watch\?v=|youtu\.be\/|youtube\.com\/embed\/)([^&\n?#]+)',
            r'youtube\.com\/watch\?.*v=([^&\n?#]+)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, youtube_url)
            if match:
                return match.group(1)
        
        raise ValueError(f"Could not extract video ID from URL: {youtube_url}")
    
    async def _get_youtube_transcript(self, video_id: str) -> List[Tuple[str, float, float]]:
        """Get transcript from YouTube using Transcript API"""
        def fetch_transcript():
            try:
                # Use yt-dlp to get transcript (more reliable than external API)
                ydl_opts = {
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en'],
                    'skip_download': True,
                    'cookiefile': 'cookies.txt' if os.path.exists('cookies.txt') else None,
                    'http_headers': {
                        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
                    }
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                    
                    # Try to get automatic captions
                    if 'automatic_captions' in info and 'en' in info['automatic_captions']:
                        captions = info['automatic_captions']['en']
                        if captions:
                            # Get the first available format
                            caption_url = captions[0]['url']
                            return self._parse_caption_url(caption_url)
                    
                    # Try manual captions
                    if 'subtitles' in info and 'en' in info['subtitles']:
                        captions = info['subtitles']['en']
                        if captions:
                            caption_url = captions[0]['url']
                            return self._parse_caption_url(caption_url)
                    
                    # Fallback: return empty transcript
                    print(f"⚠️ No captions found for video {video_id}")
                    return []
                    
            except Exception as e:
                print(f"❌ Error fetching transcript: {e}")
                return []
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, fetch_transcript)
    
    def _parse_caption_url(self, caption_url: str) -> List[Tuple[str, float, float]]:
        """Parse caption URL to extract transcript with timestamps"""
        try:
            import requests
            
            response = requests.get(caption_url)
            response.raise_for_status()
            
            # Parse XML caption format
            import xml.etree.ElementTree as ET
            root = ET.fromstring(response.text)
            
            transcript = []
            for text_elem in root.findall('.//text'):
                start = float(text_elem.get('start', 0))
                duration = float(text_elem.get('dur', 0))
                end = start + duration
                text = text_elem.text or ""
                
                if text.strip():
                    transcript.append((text.strip(), start, end))
            
            return transcript
            
        except Exception as e:
            print(f"❌ Error parsing captions: {e}")
            return []
    
    async def process_video(self, youtube_url: str, instructions: str = "", 
                          progress_callback: Optional[Callable[[int, str], None]] = None) -> Dict[str, Any]:
        """Process a YouTube video with progress updates"""
        
        def update_progress(progress: int, step: str):
            if progress_callback:
                progress_callback(progress, step)
        
        try:
            # Step 1: Extract video ID and get transcript (0-20%)
            update_progress(0, "Extracting video information...")
            video_id = self._extract_video_id(youtube_url)
            transcript = await self._get_youtube_transcript(video_id)
            update_progress(20, "Transcript extracted")
            
            # Step 2: Download video (20-60%)
            update_progress(20, "Downloading video...")
            await self._download_youtube_video(youtube_url, str(self.video_path))
            update_progress(60, "Video downloaded successfully")
            
            # Step 3: Create clips based on transcript (60-100%)
            update_progress(60, "Creating video clips...")
            clips_info = await self._create_clips_from_transcript(str(self.video_path), transcript, instructions)
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
    
    async def _create_clips_from_transcript(self, video_path: str, transcript: List[Tuple[str, float, float]], instructions: str) -> List[Dict[str, Any]]:
        """Create clips based on transcript analysis"""
        def create_clips():
            if not transcript:
                # Fallback to simple clip if no transcript
                return self._create_fallback_clip(video_path)
            
            # Get video duration
            try:
                import json
                result = subprocess.run([
                    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path
                ], capture_output=True, text=True)
                video_duration = float(json.loads(result.stdout)["format"]["duration"])
            except:
                video_duration = 60.0
            
            # Analyze transcript to find interesting segments
            clips = self._analyze_transcript_for_clips(transcript, video_duration, instructions)
            
            # Create the first clip (most interesting)
            if clips:
                best_clip = clips[0]
                start_time = best_clip["start"]
                end_time = best_clip["end"]
                duration = end_time - start_time
                
                # Ensure clip is not too long (max 60 seconds)
                if duration > 60:
                    end_time = start_time + 60
                
                # Use ffmpeg to create clip
                cmd = [
                    "ffmpeg", "-y", "-i", video_path,
                    "-ss", str(start_time),
                    "-t", str(end_time - start_time),
                    "-c", "copy", str(self.output_path)
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                
                return [{
                    "id": "1",
                    "title": best_clip["title"],
                    "duration": f"{end_time - start_time:.1f}s",
                    "timeframe": f"{start_time:.1f}s - {end_time:.1f}s",
                    "start": start_time,
                    "end": end_time,
                    "description": best_clip["description"]
                }]
            else:
                # Fallback to simple clip
                return self._create_fallback_clip(video_path)
        
        # Run in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, create_clips)
    
    def _analyze_transcript_for_clips(self, transcript: List[Tuple[str, float, float]], video_duration: float, instructions: str) -> List[Dict[str, Any]]:
        """Analyze transcript to find interesting segments for clips"""
        clips = []
        
        # Group transcript into segments
        segments = self._group_transcript_segments(transcript)
        
        # Score segments based on various factors
        scored_segments = []
        for i, segment in enumerate(segments):
            score = self._score_segment(segment, instructions)
            scored_segments.append({
                "segment": segment,
                "score": score,
                "index": i
            })
        
        # Sort by score and take top segments
        scored_segments.sort(key=lambda x: x["score"], reverse=True)
        
        # Create clips from top segments
        for i, scored in enumerate(scored_segments[:3]):  # Top 3 segments
            segment = scored["segment"]
            start_time = segment["start"]
            end_time = segment["end"]
            
            # Ensure minimum duration (10 seconds)
            if end_time - start_time < 10:
                end_time = min(start_time + 10, video_duration)
            
            clips.append({
                "id": str(i + 1),
                "title": f"Clip {i + 1}: {segment['title'][:50]}...",
                "start": start_time,
                "end": end_time,
                "description": segment["text"][:200] + "..." if len(segment["text"]) > 200 else segment["text"],
                "score": scored["score"]
            })
        
        return clips
    
    def _group_transcript_segments(self, transcript: List[Tuple[str, float, float]]) -> List[Dict[str, Any]]:
        """Group transcript entries into meaningful segments"""
        if not transcript:
            return []
        
        segments = []
        current_segment = {
            "text": "",
            "start": transcript[0][1],
            "end": transcript[0][2],
            "entries": []
        }
        
        for text, start, end in transcript:
            # If gap is more than 3 seconds, start new segment
            if start - current_segment["end"] > 3:
                if current_segment["text"].strip():
                    segments.append(current_segment)
                
                current_segment = {
                    "text": text,
                    "start": start,
                    "end": end,
                    "entries": [(text, start, end)]
                }
            else:
                # Continue current segment
                current_segment["text"] += " " + text
                current_segment["end"] = end
                current_segment["entries"].append((text, start, end))
        
        # Add last segment
        if current_segment["text"].strip():
            segments.append(current_segment)
        
        # Add titles to segments
        for segment in segments:
            words = segment["text"].split()[:5]  # First 5 words
            segment["title"] = " ".join(words)
        
        return segments
    
    def _score_segment(self, segment: Dict[str, Any], instructions: str) -> float:
        """Score a transcript segment based on various factors"""
        score = 0.0
        text = segment["text"].lower()
        
        # Length factor (prefer segments with more content)
        word_count = len(text.split())
        score += min(word_count * 0.1, 5.0)  # Max 5 points for length
        
        # Duration factor (prefer segments 15-45 seconds)
        duration = segment["end"] - segment["start"]
        if 15 <= duration <= 45:
            score += 3.0
        elif 10 <= duration <= 60:
            score += 1.0
        
        # Keyword matching with instructions
        if instructions:
            instruction_words = instructions.lower().split()
            matches = sum(1 for word in instruction_words if word in text)
            score += matches * 2.0
        
        # Position factor (prefer early segments)
        position_ratio = segment["start"] / (segment["end"] + 1)  # Avoid division by zero
        score += (1 - position_ratio) * 2.0
        
        return score
    
    def _create_fallback_clip(self, video_path: str) -> List[Dict[str, Any]]:
        """Create a fallback clip when transcript is not available"""
        try:
            import json
            result = subprocess.run([
                "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", video_path
            ], capture_output=True, text=True)
            duration = float(json.loads(result.stdout)["format"]["duration"])
        except:
            duration = 60.0
        
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
            "description": "Automatically generated clip from the beginning of the video"
        }]
    
    def _cleanup_temp_files(self):
        """Clean up temporary files"""
        try:
            import shutil
            if self.temp_dir.exists():
                shutil.rmtree(self.temp_dir)
        except Exception as e:
            print(f"Warning: Could not clean up temp files: {e}")
