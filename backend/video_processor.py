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
import json


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
        
        # Store video ID and cookies path for transcript extraction
        self.video_id = None
        self.cookies_path = None
    
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
            
            # Step 2: Transcribe video (25-50%)
            update_progress(25, "Transcribing video with AI...")
            transcript = await self._transcribe_video(str(self.video_path))
            update_progress(50, "Transcription completed")
            
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
            # Extract video ID from YouTube URL
            import re
            video_id_match = re.search(r'(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]+)', youtube_url)
            if video_id_match:
                self.video_id = video_id_match.group(1)
                print(f"🎥 Video ID extracted: {self.video_id}")
            else:
                print("❌ Could not extract video ID from URL")
            
            # Check if cookies file exists in multiple locations
            import os
            possible_cookie_paths = [
                'cookies.txt',  # Current directory
                '../cookies.txt',  # Parent directory
                '/app/cookies.txt',  # Railway container root
                './cookies.txt',  # Relative to current
                '/app/backend/cookies.txt',  # Backend directory
                '/app/backend/../cookies.txt'  # Parent of backend
            ]
            
            print(f"🔍 Searching for cookies file...")
            print(f"📁 Current directory: {os.getcwd()}")
            print(f"📂 Files in current directory: {os.listdir('.')}")
            
            # Also check if we're in a Docker container
            if os.path.exists('/app'):
                print(f"🐳 Docker container detected")
                print(f"📂 Files in /app directory: {os.listdir('/app')}")
                if os.path.exists('/app/backend'):
                    print(f"📂 Files in /app/backend directory: {os.listdir('/app/backend')}")
            
            cookies_path = None
            for path in possible_cookie_paths:
                print(f"🔍 Checking: {path}")
                if os.path.exists(path):
                    print(f"✅ Cookies file found at: {os.path.abspath(path)}")
                    cookies_path = path
                    self.cookies_path = path  # Store for transcript extraction
                    break
                else:
                    print(f"❌ Not found: {path}")
            
            if not cookies_path:
                print(f"❌ Cookies file not found in any location")
                if os.path.exists('..'):
                    print(f"📂 Files in parent directory: {os.listdir('..')}")
                if os.path.exists('/app'):
                    print(f"📂 Files in /app directory: {os.listdir('/app')}")
            else:
                # Check cookies file content
                try:
                    with open(cookies_path, 'r') as f:
                        content = f.read()
                        lines = content.split('\n')
                        youtube_cookies = [line for line in lines if '.youtube.com' in line]
                        print(f"🍪 Found {len(youtube_cookies)} YouTube cookies")
                        print(f"📄 Cookies file size: {len(content)} bytes")
                        if youtube_cookies:
                            print(f"📋 Sample cookies: {youtube_cookies[:2]}")
                        else:
                            print("⚠️ No YouTube cookies found in file")
                except Exception as e:
                    print(f"❌ Error reading cookies file: {e}")
                    cookies_path = None
            
            ydl_opts = {
                'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',  # Limit to 720p for faster processing
                'outtmpl': output_path,
                'merge_output_format': 'mp4',
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
            
            # Try multiple cookie approaches
            cookie_approaches = []
            
            # Approach 1: Use cookies file if available
            if cookies_path:
                cookie_approaches.append(('cookiefile', cookies_path))
                print(f"🍪 Will try cookies file: {cookies_path}")
            
            # Approach 2: Try to get cookies from browser (if available)
            cookie_approaches.append(('cookiesfrombrowser', ('chrome',)))
            print("🍪 Will try Chrome browser cookies")
            
            # Approach 3: Try Firefox cookies
            cookie_approaches.append(('cookiesfrombrowser', ('firefox',)))
            print("🍪 Will try Firefox browser cookies")
            
            # Approach 4: Try without any cookies (simple approach)
            cookie_approaches.append(('no_cookies', None))
            print("🍪 Will try without cookies")
            
            # Add cookies file if available
            if cookies_path:
                ydl_opts['cookiefile'] = cookies_path
                print(f"🍪 Using cookies file: {cookies_path}")
                print(f"🔧 cookiefile added to yt-dlp options: {cookies_path}")
                
                # Verify cookies file content
                try:
                    with open(cookies_path, 'r') as f:
                        content = f.read()
                        print(f"📄 Cookies file size: {len(content)} bytes")
                        if 'youtube.com' in content:
                            print("✅ Cookies file contains YouTube cookies")
                        else:
                            print("⚠️ Cookies file may not contain YouTube cookies")
                except Exception as e:
                    print(f"❌ Error reading cookies file: {e}")
            else:
                print("❌ No cookies file available")
            
            # Try each cookie approach
            download_success = False
            
            for i, (cookie_type, cookie_value) in enumerate(cookie_approaches):
                try:
                    # Create a copy of options for this attempt
                    current_opts = ydl_opts.copy()
                    
                    if cookie_type == 'no_cookies':
                        # Don't add any cookie options
                        print(f"🔄 Attempt {i+1}: Using no cookies")
                    else:
                        current_opts[cookie_type] = cookie_value
                        print(f"🔄 Attempt {i+1}: Using {cookie_type} = {cookie_value}")
                    
                    print(f"🔧 yt-dlp options: {current_opts}")
                    
                    with yt_dlp.YoutubeDL(current_opts) as ydl:
                        ydl.download([youtube_url])
                    
                    print(f"✅ Download completed successfully with {cookie_type}")
                    download_success = True
                    break
                    
                except Exception as e:
                    print(f"❌ Attempt {i+1} failed with {cookie_type}: {str(e)[:200]}...")
                    continue
            
            # If all cookie approaches failed, try without cookies
            if not download_success:
                print("🔄 All cookie approaches failed, trying without cookies...")
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
                try:
                    with yt_dlp.YoutubeDL(ydl_opts_fallback) as ydl:
                        ydl.download([youtube_url])
                    print("✅ Download completed without cookies (final fallback)")
                except Exception as e:
                    print(f"❌ Final fallback also failed: {str(e)[:200]}...")
                    raise
        
        # Run download in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, download)
    
    async def _transcribe_video(self, video_path: str) -> List[Tuple[str, float, float]]:
        """Get transcript using YouTube's transcript API"""
        def get_transcript():
            start_time = time.time()
            try:
                print("Getting YouTube transcript...", flush=True)
                
                # Extract video ID from the video path or use a placeholder
                # We'll need to pass the original YouTube URL to this method
                video_id = getattr(self, 'video_id', None)
                if not video_id:
                    print("No video ID available, using fallback method", flush=True)
                    return self._fallback_transcript()
                
                # Use yt-dlp to get transcript
                ydl_opts = {
                    'writesubtitles': True,
                    'writeautomaticsub': True,
                    'subtitleslangs': ['en'],
                    'skip_download': True,  # We already have the video
                }
                
                # Add cookies if available
                if hasattr(self, 'cookies_path') and self.cookies_path:
                    ydl_opts['cookiefile'] = self.cookies_path
                    print(f"🍪 Using cookies for transcript: {self.cookies_path}")
                else:
                    print("❌ No cookies available for transcript extraction")
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    # Get video info including transcript
                    info = ydl.extract_info(f"https://www.youtube.com/watch?v={video_id}", download=False)
                    
                    # Try to get manual subtitles first, then automatic
                    transcript = []
                    if 'subtitles' in info and 'en' in info['subtitles']:
                        subtitle_url = info['subtitles']['en'][0]['url']
                        transcript = self._parse_subtitle_url(subtitle_url)
                    elif 'automatic_captions' in info and 'en' in info['automatic_captions']:
                        subtitle_url = info['automatic_captions']['en'][0]['url']
                        transcript = self._parse_subtitle_url(subtitle_url)
                    else:
                        print("No transcript available, using fallback", flush=True)
                        return self._fallback_transcript()
                
                end_time = time.time()
                print(f"YouTube transcript took {end_time - start_time} seconds", flush=True)
                print(f"Found {len(transcript)} transcript segments", flush=True)
                return transcript
                
            except Exception as e:
                print(f"YouTube transcript failed: {e}", flush=True)
                print("Using fallback transcript method", flush=True)
                return self._fallback_transcript()
        
        # Run transcript extraction in thread pool
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(None, get_transcript)
    
    def _parse_subtitle_url(self, subtitle_url: str) -> List[Tuple[str, float, float]]:
        """Parse subtitle URL and convert to transcript format"""
        import urllib.request
        
        try:
            # Download subtitle content
            response = urllib.request.urlopen(subtitle_url)
            subtitle_content = response.read().decode('utf-8')
            
            # Parse VTT format
            transcript = []
            lines = subtitle_content.split('\n')
            current_text = ""
            current_start = 0.0
            current_end = 0.0
            
            for line in lines:
                line = line.strip()
                if '-->' in line:  # Timestamp line
                    # Parse timestamp: 00:00:00.000 --> 00:00:00.000
                    parts = line.split(' --> ')
                    if len(parts) == 2:
                        current_start = self._parse_timestamp(parts[0])
                        current_end = self._parse_timestamp(parts[1])
                elif line and not line.startswith('WEBVTT') and not line.isdigit():
                    # Text line
                    if current_text:
                        current_text += " " + line
                    else:
                        current_text = line
                        # Store the segment
                        if current_text and current_end > current_start:
                            transcript.append((current_text, current_start, current_end))
                            current_text = ""
            
            return transcript
            
        except Exception as e:
            print(f"Error parsing subtitle: {e}", flush=True)
            return self._fallback_transcript()
    
    def _parse_timestamp(self, timestamp: str) -> float:
        """Convert VTT timestamp to seconds"""
        try:
            # Format: 00:00:00.000
            parts = timestamp.split(':')
            hours = int(parts[0])
            minutes = int(parts[1])
            seconds = float(parts[2])
            return hours * 3600 + minutes * 60 + seconds
        except:
            return 0.0
    
    def _fallback_transcript(self) -> List[Tuple[str, float, float]]:
        """Fallback transcript when YouTube transcript is not available"""
        print("Using fallback transcript - creating dummy segments", flush=True)
        # Create dummy transcript segments every 30 seconds
        transcript = []
        for i in range(0, 300, 30):  # Assume 5 minutes max
            transcript.append((f"Segment {i//30 + 1}", float(i), float(i + 30)))
        return transcript
    
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
 