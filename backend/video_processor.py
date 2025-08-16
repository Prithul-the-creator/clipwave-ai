import yt_dlp
import tempfile
import os
import re
import ast
import subprocess
import asyncio
from openai import OpenAI
from moviepy import VideoFileClip, concatenate_videoclips
from typing import Callable, Optional, Dict, Any, List, Tuple
import threading
import time
from pathlib import Path
from youtube_transcript_api import YouTubeTranscriptApi


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
            
            # Step 2: Get transcript (25-50%)
            update_progress(25, "Getting video transcript...")
            transcript = await self._transcribe_video(youtube_url)
            update_progress(50, "Transcript retrieved")
            
            # Step 3: Process with GPT and identify clips (50-75%)
            update_progress(50, "Analyzing content and identifying clips...")
            timestamps = await self._identify_clips(transcript, instructions)
            update_progress(75, "Clips identified")
            
            # Step 4: Render final video (75-100%)
            update_progress(75, "Rendering final video...")
            clips_info = await self._render_video(str(self.video_path), timestamps)
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
            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',  # Limit to 720p for faster processing
                'outtmpl': output_path,
                'merge_output_format': 'mp4'
            }
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([youtube_url])
        
        # Run download in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download)
    
    async def _transcribe_video(self, youtube_url: str) -> List[Tuple[str, float, float]]:
        """Get transcript using YouTube Transcript API"""
        def get_transcript():
            start_time = time.time()
            print("Getting YouTube transcript...", flush=True)
            
            # Extract video ID from URL
            video_id = self._extract_video_id(youtube_url)
            if not video_id:
                raise ValueError("Could not extract video ID from URL")
            
            # Get transcript
            api = YouTubeTranscriptApi()
            transcript_list = api.fetch(video_id, languages=['en'])
            print("YouTube transcript retrieved successfully.", flush=True)
            
            # Convert to our format
            transcript = []
            for segment in transcript_list:
                text = segment.text
                start_time_sec = segment.start
                end_time_sec = segment.start + segment.duration
                transcript.append((text, start_time_sec, end_time_sec))
            
            end_time = time.time()
            print(f"Transcript retrieval took {end_time - start_time:.2f} seconds")
            print(transcript)
            return transcript
        
        # Run transcript retrieval in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_transcript)
    
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
        """Render the final video with identified clips using ffmpeg for fast stitching"""
        def render():
            clips_info = []
            temp_clips = []
            concat_list_path = self.temp_dir / "concat_list.txt"
            video_duration = None

            # Get video duration using ffprobe
            try:
                import json
                result = subprocess.run([
                    "ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "json", str(video_path)
                ], capture_output=True, text=True)
                video_duration = float(json.loads(result.stdout)["format"]["duration"])
            except Exception:
                video_duration = None

            for i, timestamp in enumerate(timestamps):
                start_time = max(0, timestamp['start'])
                end_time = min(timestamp['end'], video_duration) if video_duration else timestamp['end']
                if end_time <= start_time:
                    continue  # skip invalid clips
                out_clip = self.temp_dir / f"clip_{i+1}.mp4"
                temp_clips.append(out_clip)
                # ffmpeg command to extract subclip
                cmd = [
                    "ffmpeg", "-y", "-i", str(video_path),
                    "-ss", str(start_time), "-to", str(end_time),
                    "-avoid_negative_ts", "make_zero", str(out_clip)
                ]
                subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                clips_info.append({
                    "id": str(i + 1),
                    "title": f"Clip {i + 1}",
                    "duration": f"{end_time - start_time:.1f}s",
                    "timeframe": f"{start_time:.1f}s - {end_time:.1f}s",
                    "start": start_time,
                    "end": end_time
                })

            # Write concat list file
            with open(concat_list_path, "w") as f:
                for clip_path in temp_clips:
                    f.write(f"file '{clip_path}'\n")

            # ffmpeg concat command
            concat_cmd = [
                "ffmpeg", "-y", "-f", "concat", "-safe", "0", "-i", str(concat_list_path),
                "-c", "copy", str(self.output_path)
            ]
            subprocess.run(concat_cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

            # Optionally, cleanup temp clips (but not self.output_path)
            for clip_path in temp_clips:
                if clip_path.exists():
                    try:
                        os.remove(clip_path)
                    except Exception:
                        pass
            if concat_list_path.exists():
                try:
                    os.remove(concat_list_path)
                except Exception:
                    pass

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
            print(f"Warning: Could not clean up temp files: {e}")
    
    def get_video_info(self) -> Dict[str, Any]:
        """Get information about the processed video"""
        if not self.output_path.exists():
            return {}
        
        try:
            with VideoFileClip(str(self.output_path)) as clip:
                return {
                    "duration": clip.duration,
                    "fps": clip.fps,
                    "size": (clip.w, clip.h),
                    "file_size": self.output_path.stat().st_size
                }
        except Exception:
            return {} 
 