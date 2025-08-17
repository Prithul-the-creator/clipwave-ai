# ClipWave AI - YouTube Video Clipping Platform

A full-stack application that automatically clips YouTube videos based on AI-powered content analysis. Users can submit YouTube URLs with custom instructions, and the system will generate engaging clips using GPT-4 and Whisper AI.

## Features

- 🎥 **YouTube Video Processing**: Download and process any YouTube video
- 🤖 **AI-Powered Clipping**: Use GPT-4 to identify the most engaging moments
- 📝 **Custom Instructions**: Specify what type of content to focus on
- 🔄 **Real-time Progress**: Live updates via WebSocket connections
- 📋 **Job Queue System**: Handle multiple processing requests
- 🎬 **Video Preview**: Watch generated clips directly in the browser
- 💾 **Download Support**: Download processed videos in MP4 format
- 🎨 **Modern UI**: Beautiful, responsive interface with dark theme

## Tech Stack

### Backend
- **FastAPI**: High-performance Python web framework
- **yt-dlp**: YouTube video downloading
- **OpenAI Whisper**: Speech-to-text transcription
- **OpenAI GPT-4**: Content analysis and clip identification
- **MoviePy**: Video processing and editing
- **WebSockets**: Real-time progress updates

### Frontend
- **React 18**: Modern React with hooks
- **TypeScript**: Type-safe development
- **Vite**: Fast build tool and dev server
- **Tailwind CSS**: Utility-first styling
- **Shadcn/ui**: Beautiful component library
- **React Query**: Server state management

## Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- OpenAI API key

## Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clipwave-ai-shorts
   ```

2. **Run the setup script (recommended)**
   ```bash
   ./setup.sh
   ```
   
   Or manually install dependencies:
   ```bash
   pip install -r requirements.txt
   npm install
   ```

3. **Set up environment variables**
   Copy the example environment file and add your API keys:
   
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit the .env file with your actual API keys
   nano .env
   ```
   
   Add your API keys to the `.env` file:
   ```env
   # OpenAI API Key (required)
   OPENAI_API_KEY=your_actual_openai_api_key_here
   
   # Supabase Configuration (optional - defaults provided)
   VITE_SUPABASE_URL=your_supabase_url_here
   VITE_SUPABASE_ANON_KEY=your_supabase_anon_key_here
   ```
   
   **Important**: You need a valid OpenAI API key. Get one from https://platform.openai.com/account/api-keys

## Usage

### Quick Start
Run both backend and frontend with a single command:
```bash
./start.sh
```

### Manual Start

1. **Start the backend server**
   ```bash
   cd backend
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```

2. **Start the frontend server** (in a new terminal)
   ```bash
npm run dev
```

3. **Access the application**
   - Frontend: http://localhost:8080
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## How It Works

1. **Submit a YouTube URL**: Enter a YouTube video URL and optional instructions
2. **Video Download**: The system downloads the video (limited to 720p for faster processing)
3. **AI Transcription**: Whisper AI transcribes the video content
4. **Content Analysis**: GPT-4 analyzes the transcript and identifies engaging moments
5. **Video Clipping**: MoviePy creates clips based on the identified timestamps
6. **Real-time Updates**: Progress is tracked and displayed in real-time
7. **Download**: Users can preview and download the generated clips

## API Endpoints

- `POST /api/jobs` - Create a new video processing job
- `GET /api/jobs/{job_id}` - Get job status
- `GET /api/jobs` - List all jobs
- `DELETE /api/jobs/{job_id}` - Delete a job
- `GET /api/videos/{job_id}` - Download processed video
- `WS /ws/{job_id}` - WebSocket for real-time updates

## Project Structure

```
clipwave-ai-shorts/
├── backend/
│   ├── main.py              # FastAPI application
│   ├── job_manager.py       # Job storage and management
│   ├── video_processor.py   # Video processing logic
│   └── storage/             # Processed videos and job data
├── src/
│   ├── components/          # React components
│   ├── hooks/              # Custom React hooks
│   ├── lib/                # API client and utilities
│   └── pages/              # Page components
├── requirements.txt         # Python dependencies
├── package.json            # Node.js dependencies
└── start.sh               # Startup script
```

## Configuration

### Video Quality
Adjust video quality in `backend/video_processor.py`:
```python
'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]'
```

### OpenAI Model
Change the GPT model in `backend/video_processor.py`:
```python
model="gpt-4o"  # or "gpt-3.5-turbo"
```

### Whisper Model
Modify the Whisper model in `backend/video_processor.py`:
```python
model = whisper.load_model("base")  # or "small", "medium", "large"
```

## Troubleshooting

### Common Issues

1. **OpenAI API Key Error**
   - Ensure your API key is valid and has sufficient credits
   - Check the `.env` file is in the root directory and contains your API key

2. **Video Download Failures**
   - Some videos may be restricted or unavailable
   - Check the YouTube URL is valid and accessible

3. **Memory Issues**
   - Large videos may require more RAM
   - Consider reducing video quality or using shorter videos

4. **Processing Time**
   - Video processing can take several minutes depending on length
   - Progress is shown in real-time via WebSocket

### Performance Tips

- Use shorter videos for faster processing
- Limit video quality to 720p or lower
- Ensure sufficient disk space for temporary files
- Close other applications to free up system resources

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For issues and questions:
- Check the troubleshooting section
- Review the API documentation at http://localhost:8000/docs
- Open an issue on GitHub
