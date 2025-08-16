# YouTube API Setup Guide

This guide will help you set up YouTube API authentication to avoid cookie expiration issues.

## 🎯 **Why Use YouTube API Instead of Cookies?**

- ✅ **No expiration issues** - API keys don't expire like cookies
- ✅ **More reliable** - Official Google API with better uptime
- ✅ **Better rate limits** - Higher quotas than cookie-based scraping
- ✅ **Safer** - No risk of account bans
- ✅ **Production-ready** - Designed for automated systems

## 📋 **Step 1: Get YouTube API Key**

1. **Go to Google Cloud Console**
   - Visit: https://console.cloud.google.com/
   - Sign in with your Google account

2. **Create a New Project**
   - Click "Select a project" → "New Project"
   - Name it something like "ClipWave AI"
   - Click "Create"

3. **Enable YouTube Data API v3**
   - Go to "APIs & Services" → "Library"
   - Search for "YouTube Data API v3"
   - Click on it and press "Enable"

4. **Create API Key**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "API Key"
   - Copy the generated API key

5. **Restrict the API Key (Recommended)**
   - Click on the API key you just created
   - Under "Application restrictions" select "HTTP referrers"
   - Add your Railway domain: `*.railway.app`
   - Under "API restrictions" select "Restrict key"
   - Choose "YouTube Data API v3"
   - Click "Save"

## 🔧 **Step 2: Add API Key to Railway**

1. **Go to Railway Dashboard**
   - Visit your project: https://railway.app/dashboard
   - Click on your service

2. **Add Environment Variable**
   - Go to "Variables" tab
   - Click "New Variable"
   - Name: `YOUTUBE_API_KEY`
   - Value: Your API key from step 1
   - Click "Add"

## 🚀 **Step 3: Deploy with New API**

The app will now use the YouTube API for:
- ✅ Video metadata (title, description, duration)
- ✅ Age restriction detection
- ✅ Better error handling
- ✅ Fallback to yt-dlp for downloading

## 📊 **API Quotas**

YouTube Data API v3 provides:
- **10,000 units per day** (free tier)
- **1 unit per video info request**
- **100 units per search request**

This is more than enough for most use cases.

## 🔄 **Fallback Strategy**

If the API fails or hits limits, the app will:
1. Try YouTube API first
2. Fall back to yt-dlp with cookies (if available)
3. Fall back to yt-dlp without cookies
4. Use multiple client strategies (android, mweb, web)

## 🛠 **Testing**

To test if your API key works:

```bash
# Test locally
export YOUTUBE_API_KEY="your_api_key_here"
python -c "
from backend.youtube_api_client import YouTubeAPIClient
import asyncio

async def test():
    client = YouTubeAPIClient()
    info = await client.get_video_info('dQw4w9WgXcQ')
    print('API working:', info is not None)

asyncio.run(test())
"
```

## 🎉 **Benefits**

With this setup, you get:
- ✅ **Reliable video processing** - No more cookie expiration issues
- ✅ **Better error messages** - Clear feedback when videos are restricted
- ✅ **Production stability** - Designed for automated systems
- ✅ **Future-proof** - Uses official Google APIs

## 🔧 **Optional: OAuth Setup (Advanced)**

For even more access, you can set up OAuth:

1. **Create OAuth 2.0 Credentials**
   - Go to "APIs & Services" → "Credentials"
   - Click "Create Credentials" → "OAuth 2.0 Client IDs"
   - Choose "Web application"
   - Add authorized redirect URIs

2. **Download client_secrets.json**
   - Save it in your project root
   - Add to .gitignore

3. **First-time authentication**
   - Run the OAuth flow locally
   - Save the token.pickle file
   - Deploy both files to Railway

This gives you access to private playlists and more features.

---

**Need help?** Check the [YouTube Data API documentation](https://developers.google.com/youtube/v3/docs/) for more details.
