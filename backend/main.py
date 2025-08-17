import asyncio
import json
import os
import uuid
from typing import List, Optional
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse, HTMLResponse
from pydantic import BaseModel
import aiofiles
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from hybrid_video_processor import HybridVideoProcessor
from job_manager import JobManager

app = FastAPI(title="ClipWave AI API", version="1.0.0")

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

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            print(f"Failed to send message to WebSocket: {e}")

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
    instructions: str = ""
    user_id: str

class JobResponse(BaseModel):
    job_id: str
    status: str
    message: str

# Serve static files from the dist directory
@app.get("/")
async def root():
    # Try to serve the frontend index.html
    frontend_paths = [
        Path("dist/index.html"),
        Path("../dist/index.html"),
        Path("./dist/index.html")
    ]
    
    for frontend_path in frontend_paths:
        if frontend_path.exists():
            return FileResponse(frontend_path)
    
    # Fallback to JSON response if frontend not found
    return {"message": "ClipWave AI Backend is running", "frontend": "not found"}

# Serve static assets
@app.get("/assets/{path:path}")
async def serve_assets(path: str):
    asset_paths = [
        Path(f"dist/assets/{path}"),
        Path(f"../dist/assets/{path}"),
        Path(f"./dist/assets/{path}")
    ]
    
    for asset_path in asset_paths:
        if asset_path.exists():
            return FileResponse(asset_path)
    
    raise HTTPException(status_code=404, detail="Asset not found")

@app.post("/api/jobs", response_model=JobResponse)
async def create_job(request: VideoRequest):
    """Create a new video processing job"""
    job_id = str(uuid.uuid4())
    
    # Create job
    job_manager.create_job(job_id, request.youtube_url, request.instructions, request.user_id)
    
    # Start processing in background
    asyncio.create_task(process_video_job(job_id, request.youtube_url, request.instructions))
    
    return JobResponse(
        job_id=job_id,
        status="processing",
        message="Job created successfully"
    )

@app.get("/api/jobs/{job_id}")
async def get_job(job_id: str, user_id: str = Query(...)):
    """Get job status"""
    job = job_manager.get_job(job_id)
    if not job or job.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    return job

@app.get("/api/jobs")
async def list_jobs(user_id: str = Query(...)):
    """List all jobs for a user"""
    jobs = job_manager.list_jobs(user_id)
    return {"jobs": jobs}

@app.delete("/api/jobs/{job_id}")
async def delete_job(job_id: str, user_id: str = Query(...)):
    """Delete a job"""
    job = job_manager.get_job(job_id)
    if not job or job.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    job_manager.delete_job(job_id)
    return {"message": "Job deleted successfully"}

@app.get("/api/videos/{job_id}")
async def get_video(job_id: str, user_id: str = Query(...)):
    """Download processed video"""
    job = job_manager.get_job(job_id)
    if not job or job.get("user_id") != user_id:
        raise HTTPException(status_code=404, detail="Job not found")
    
    if job.get("status") != "completed":
        raise HTTPException(status_code=400, detail="Video not ready")
    
    video_path = Path(f"storage/videos/{job_id}.mp4")
    if not video_path.exists():
        raise HTTPException(status_code=404, detail="Video file not found")
    
    return FileResponse(video_path, media_type="video/mp4", filename=f"{job_id}.mp4")

@app.websocket("/ws/{job_id}")
async def websocket_endpoint(websocket: WebSocket, job_id: str):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        # Send initial status
        job = job_manager.get_job(job_id)
        if job:
            try:
                await manager.send_personal_message(
                    json.dumps({
                        "type": "status",
                        "status": job.get("status"),
                        "progress": job.get("progress"),
                        "message": job.get("current_step")
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

async def process_video_job(job_id: str, youtube_url: str, instructions: str):
    """Process video in background"""
    try:
        # Update job status
        job_manager.update_job(job_id, {
            "status": "processing",
            "progress": 0,
            "current_step": "Starting video processing..."
        })
        
        # Create video processor
        processor = HybridVideoProcessor(job_id)
        
        # Process video with progress updates
        def progress_callback(progress: int, message: str):
            try:
                job_manager.update_job(job_id, {
                    "status": "processing",
                    "progress": progress,
                    "current_step": message
                })
                print(f"Job {job_id} progress: {progress}% - {message}", flush=True)
            except Exception as e:
                print(f"Error updating job progress: {e}", flush=True)
        
        # Process the video
        result = await processor.process_video(youtube_url, instructions, progress_callback)
        
        # Update job with success
        job_manager.update_job(job_id, {
            "status": "completed",
            "progress": 100,
            "current_step": "Video processing completed",
            "video_path": result.get("video_path"),
            "clips": result.get("clips", [])
        })
        
        print(f"Job {job_id} completed successfully!", flush=True)
        
    except Exception as e:
        print(f"Job {job_id} failed with error: {str(e)}", flush=True)
        # Update job with error
        job_manager.update_job(job_id, {
            "status": "failed",
            "progress": 0,
            "current_step": f"Error: {str(e)}",
            "error": str(e)
        })

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000) 