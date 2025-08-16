from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from typing import List, Optional, Dict, Any
import asyncio
import json
import uuid
import os
import tempfile
from datetime import datetime
import aiofiles
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from video_processor import VideoProcessor
except ImportError:
    from video_processor_simple import VideoProcessor
from job_manager import JobManager

app = FastAPI(title="ClipWave AI Backend", version="1.0.0")

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:8080",
        "http://localhost:5173", 
        "http://localhost:3000",
        "https://clipwave-ai.vercel.app",
        "https://clipwave-ai.railway.app",
        "https://clipwave-ai.onrender.com",
        "*"  # Allow all origins for development
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize job manager
job_manager = JobManager()

# Mount static files for frontend
frontend_path = Path("../frontend")
if not frontend_path.exists():
    frontend_path = Path("./frontend")
if not frontend_path.exists():
    frontend_path = Path("/app/frontend")

if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path / "assets")), name="static")
    print(f"✅ Frontend static files mounted from: {frontend_path}")
else:
    print(f"❌ Frontend directory not found. Tried: {frontend_path}")

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        dead_connections = []
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except Exception as e:
                print(f"Failed to send message to WebSocket: {e}")
                dead_connections.append(connection)
        
        # Remove dead connections
        for dead_connection in dead_connections:
            try:
                self.active_connections.remove(dead_connection)
            except ValueError:
                pass  # Connection already removed

manager = ConnectionManager()

# Pydantic models
class VideoRequest(BaseModel):
    youtube_url: str
    instructions: Optional[str] = ""
    user_id: Optional[str] = "anonymous"

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

class JobStatus(BaseModel):
    job_id: str
    status: str
    progress: int
    current_step: str
    error: Optional[str] = None
    video_url: Optional[str] = None

@app.get("/")
async def root():
    # Try to serve the frontend index.html
    frontend_paths = [
        Path("../frontend/index.html"),
        Path("./frontend/index.html"),
        Path("/app/frontend/index.html")
    ]
    
    for frontend_path in frontend_paths:
        if frontend_path.exists():
            with open(frontend_path, 'r') as f:
                html_content = f.read()
            return HTMLResponse(content=html_content)
    
    # Fallback to JSON response if frontend not found
    return {"message": "ClipWave AI Backend is running", "frontend": "not found"}

@app.post("/api/jobs", response_model=JobResponse)
async def create_job(request: VideoRequest, background_tasks: BackgroundTasks):
    """Create a new video processing job"""
    try:
        job_id = str(uuid.uuid4())
        
        # Create job in manager
        job = job_manager.create_job(
            job_id=job_id,
            youtube_url=request.youtube_url,
            instructions=request.instructions,
            user_id=request.user_id
        )
        
        # Start processing in background
        background_tasks.add_task(process_video_job, job_id)
        
        return JobResponse(
            job_id=job_id,
            status="queued",
            message="Job created successfully"
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/jobs/{job_id}", response_model=JobStatus)
async def get_job_status(job_id: str, user_id: Optional[str] = None):
    """Get the status of a specific job"""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Ensure user can only access their own jobs
    if user_id and job.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    return JobStatus(
        job_id=job_id,
        status=job["status"],
        progress=job["progress"],
        current_step=job["current_step"],
        error=job.get("error"),
        video_url=job.get("video_url")
    )

@app.get("/api/jobs")
async def list_jobs(user_id: Optional[str] = None):
    """List all jobs (optionally filtered by user)"""
    jobs = job_manager.list_jobs(user_id)
    return {"jobs": jobs}

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, user_id: Optional[str] = None):
    """Delete a job and its associated files"""
    job = job_manager.get_job(job_id)
    if not job:
        raise HTTPException(status_code=404, detail="Job not found")
    
    # Ensure user can only delete their own jobs
    if user_id and job.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    success = job_manager.delete_job(job_id)
    if not success:
        raise HTTPException(status_code=404, detail="Job not found")
    return {"message": "Job deleted successfully"}

@app.get("/api/videos/{job_id}")
async def download_video(job_id: str, user_id: Optional[str] = None):
    """Download the processed video file"""
    job = job_manager.get_job(job_id)
    if not job or job["status"] != "completed":
        raise HTTPException(status_code=404, detail="Video not found or not ready")
    
    # Ensure user can only download their own videos
    if user_id and job.get("user_id") != user_id:
        raise HTTPException(status_code=403, detail="Access denied")
    
    video_path = job.get("video_path")
    if not video_path or not os.path.exists(video_path):
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(
        video_path,
        media_type="video/mp4",
        filename=f"clip_{job_id}.mp4"
    )

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time job updates"""
    await manager.connect(websocket)
    try:
        # Send initial status
        job = job_manager.get_job(job_id)
        if job:
            try:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "job_update",
                        "job_id": job_id,
                        "data": job
                    }),
                    websocket
                )
            except Exception as e:
                print(f"Error sending initial status: {e}")
                return
        
        # Keep connection alive and wait for updates
        while True:
            try:
                # Wait for any message from client (ping/pong)
                data = await websocket.receive_text()
                # Echo back to keep connection alive
                await websocket.send_text(data)
            except WebSocketDisconnect:
                break
            except Exception as e:
                print(f"WebSocket error: {e}")
                break
    except WebSocketDisconnect:
        pass
    finally:
        manager.disconnect(websocket)

async def process_video_job(job_id: str):
    """Background task to process video jobs"""
    try:
        job = job_manager.get_job(job_id)
        if not job:
            return
        
        # Update status to processing
        job_manager.update_job(job_id, {
            "status": "processing",
            "progress": 0,
            "current_step": "Initializing..."
        })
        
        # Initialize video processor
        processor = VideoProcessor(job_id)
        
        # Process the video with progress callbacks
        def progress_callback(progress: int, step: str):
            job_manager.update_job(job_id, {
                "progress": progress,
                "current_step": step
            })
            # Broadcast update to WebSocket clients
            asyncio.create_task(manager.broadcast(
                json.dumps({
                    "type": "job_update",
                    "job_id": job_id,
                    "data": job_manager.get_job(job_id)
                })
            ))
        
        # Process the video
        result = await processor.process_video(
            youtube_url=job["youtube_url"],
            instructions=job["instructions"],
            progress_callback=progress_callback
        )
        
        # Update job with results
        job_manager.update_job(job_id, {
            "status": "completed",
            "progress": 100,
            "current_step": "Completed",
            "video_path": result["video_path"],
            "video_url": f"/api/videos/{job_id}",
            "clips": result.get("clips", [])
        })
        
        # Broadcast completion
        asyncio.create_task(manager.broadcast(
            json.dumps({
                "type": "job_update",
                "job_id": job_id,
                "data": job_manager.get_job(job_id)
            })
        ))
        
    except Exception as e:
        # Update job with error
        job_manager.update_job(job_id, {
            "status": "failed",
            "error": str(e),
            "current_step": "Failed"
        })
        
        # Broadcast error
        asyncio.create_task(manager.broadcast(
            json.dumps({
                "type": "job_update",
                "job_id": job_id,
                "data": job_manager.get_job(job_id)
            })
        ))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 