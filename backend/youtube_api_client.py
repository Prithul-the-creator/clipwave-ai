"""
YouTube API Client using OAuth authentication
This provides a more reliable alternative to cookie-based authentication
"""

import os
import asyncio
from typing import Dict, Any, List, Optional
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import pickle
from pathlib import Path


class YouTubeAPIClient:
    """YouTube API client using OAuth authentication"""
    
    # YouTube API scopes
    SCOPES = [
        'https://www.googleapis.com/auth/youtube.readonly',
        'https://www.googleapis.com/auth/youtube.force-ssl'
    ]
    
    def __init__(self):
        self.api_key = os.getenv('YOUTUBE_API_KEY')
        self.credentials = None
        self.service = None
        
    async def authenticate(self):
        """Authenticate with YouTube API using OAuth or API key"""
        if self.api_key:
            # Use API key for read-only operations
            self.service = build('youtube', 'v3', developerKey=self.api_key)
            return True
        
        # Try OAuth flow (only if no API key)
        try:
            self.credentials = await self._load_credentials()
            if not self.credentials or not self.credentials.valid:
                if self.credentials and self.credentials.expired and self.credentials.refresh_token:
                    await self._refresh_credentials()
                else:
                    await self._authenticate_oauth()
            
            self.service = build('youtube', 'v3', credentials=self.credentials)
            return True
            
        except Exception as e:
            print(f"OAuth authentication failed: {e}")
            return False
    
    async def _load_credentials(self):
        """Load saved credentials from file"""
        creds = None
        token_path = Path('token.pickle')
        
        if token_path.exists():
            with open(token_path, 'rb') as token:
                creds = pickle.load(token)
        
        return creds
    
    async def _save_credentials(self, creds):
        """Save credentials to file"""
        token_path = Path('token.pickle')
        with open(token_path, 'wb') as token:
            pickle.dump(creds, token)
    
    async def _refresh_credentials(self):
        """Refresh expired credentials"""
        loop = asyncio.get_event_loop()
        await loop.run_in_executor(None, self.credentials.refresh, Request())
        await self._save_credentials(self.credentials)
    
    async def _authenticate_oauth(self):
        """Perform OAuth authentication flow"""
        # This would require client_secrets.json file
        # For now, we'll use API key approach
        raise NotImplementedError("OAuth flow requires client_secrets.json")
    
    async def get_video_info(self, video_id: str) -> Optional[Dict[str, Any]]:
        """Get video information using YouTube API"""
        if not self.service:
            if not await self.authenticate():
                return None
        
        try:
            loop = asyncio.get_event_loop()
            request = self.service.videos().list(
                part='snippet,contentDetails,statistics,status',
                id=video_id
            )
            response = await loop.run_in_executor(None, request.execute)
            
            if response['items']:
                video = response['items'][0]
                return {
                    'id': video['id'],
                    'title': video['snippet']['title'],
                    'description': video['snippet']['description'],
                    'duration': video['contentDetails']['duration'],
                    'view_count': video['statistics'].get('viewCount', 0),
                    'like_count': video['statistics'].get('likeCount', 0),
                    'upload_date': video['snippet']['publishedAt'],
                    'channel_title': video['snippet']['channelTitle'],
                    'tags': video['snippet'].get('tags', []),
                    'category_id': video['snippet']['categoryId'],
                    'default_language': video['snippet'].get('defaultLanguage'),
                    'default_audio_language': video['snippet'].get('defaultAudioLanguage'),
                    'age_restricted': video['contentDetails'].get('contentRating', {}).get('ytRating', '') == 'ytAgeRestricted',
                    'embeddable': video['status']['embeddable'],
                    'public_stats_viewable': video['status']['publicStatsViewable'],
                    'made_for_kids': video['status']['madeForKids']
                }
        except HttpError as e:
            print(f"YouTube API error: {e}")
            return None
        except Exception as e:
            print(f"Error getting video info: {e}")
            return None
        
        return None
    
    async def search_videos(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for videos using YouTube API"""
        if not self.service:
            if not await self.authenticate():
                return []
        
        try:
            loop = asyncio.get_event_loop()
            request = self.service.search().list(
                part='snippet',
                q=query,
                type='video',
                maxResults=max_results,
                order='relevance'
            )
            response = await loop.run_in_executor(None, request.execute)
            
            videos = []
            for item in response['items']:
                videos.append({
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'channel_title': item['snippet']['channelTitle'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnails': item['snippet']['thumbnails']
                })
            
            return videos
            
        except HttpError as e:
            print(f"YouTube API search error: {e}")
            return []
        except Exception as e:
            print(f"Error searching videos: {e}")
            return []
    
    async def get_channel_videos(self, channel_id: str, max_results: int = 50) -> List[Dict[str, Any]]:
        """Get videos from a specific channel"""
        if not self.service:
            if not await self.authenticate():
                return []
        
        try:
            loop = asyncio.get_event_loop()
            request = self.service.search().list(
                part='snippet',
                channelId=channel_id,
                type='video',
                maxResults=max_results,
                order='date'
            )
            response = await loop.run_in_executor(None, request.execute)
            
            videos = []
            for item in response['items']:
                videos.append({
                    'id': item['id']['videoId'],
                    'title': item['snippet']['title'],
                    'description': item['snippet']['description'],
                    'published_at': item['snippet']['publishedAt'],
                    'thumbnails': item['snippet']['thumbnails']
                })
            
            return videos
            
        except HttpError as e:
            print(f"YouTube API channel error: {e}")
            return []
        except Exception as e:
            print(f"Error getting channel videos: {e}")
            return []
