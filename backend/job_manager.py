import os
import json
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any
from pathlib import Path
import tempfile

class JobManager:
    def __init__(self, storage_dir: str = "storage"):
        self.storage_dir = Path(storage_dir)
        self.jobs_file = self.storage_dir / "jobs.json"
        self.videos_dir = self.storage_dir / "videos"
        
        # Create directories if they don't exist
        self.storage_dir.mkdir(exist_ok=True)
        self.videos_dir.mkdir(exist_ok=True)
        
        # Load existing jobs
        self.jobs: Dict[str, Dict[str, Any]] = self._load_jobs()
    
    def _load_jobs(self) -> Dict[str, Dict[str, Any]]:
        """Load jobs from JSON file"""
        if self.jobs_file.exists():
            try:
                with open(self.jobs_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                return {}
        return {}
    
    def _save_jobs(self):
        """Save jobs to JSON file"""
        with open(self.jobs_file, 'w') as f:
            json.dump(self.jobs, f, indent=2, default=str)
    
    def create_job(self, job_id: str, youtube_url: str, instructions: str = "", user_id: str = "anonymous") -> Dict[str, Any]:
        """Create a new job"""
        job = {
            "id": job_id,
            "youtube_url": youtube_url,
            "instructions": instructions,
            "user_id": user_id,
            "status": "queued",
            "progress": 0,
            "current_step": "Queued",
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "video_path": None,
            "video_url": None,
            "clips": [],
            "error": None
        }
        
        self.jobs[job_id] = job
        self._save_jobs()
        return job
    
    def get_job(self, job_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific job by ID"""
        return self.jobs.get(job_id)
    
    def update_job(self, job_id: str, updates: Dict[str, Any]):
        """Update a job with new data"""
        if job_id in self.jobs:
            self.jobs[job_id].update(updates)
            self.jobs[job_id]["updated_at"] = datetime.now().isoformat()
            self._save_jobs()
    
    def list_jobs(self, user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """List all jobs, optionally filtered by user"""
        jobs = list(self.jobs.values())
        if user_id:
            jobs = [job for job in jobs if job.get("user_id") == user_id]
        
        # Sort by creation date (newest first)
        jobs.sort(key=lambda x: x.get("created_at", ""), reverse=True)
        return jobs
    
    def delete_job(self, job_id: str) -> bool:
        """Delete a job and its associated files"""
        if job_id not in self.jobs:
            return False
        
        job = self.jobs[job_id]
        
        # Delete video file if it exists
        video_path = job.get("video_path")
        if video_path and os.path.exists(video_path):
            try:
                os.remove(video_path)
            except OSError:
                pass  # File might already be deleted
        
        # Remove job from storage
        del self.jobs[job_id]
        self._save_jobs()
        return True
    
    def get_job_video_path(self, job_id: str) -> Optional[str]:
        """Get the video file path for a completed job"""
        job = self.get_job(job_id)
        if job and job.get("status") == "completed":
            return job.get("video_path")
        return None
    
    def cleanup_old_jobs(self, days: int = 7):
        """Clean up jobs older than specified days"""
        cutoff_date = datetime.now().timestamp() - (days * 24 * 60 * 60)
        
        jobs_to_delete = []
        for job_id, job in self.jobs.items():
            created_at = job.get("created_at")
            if created_at:
                try:
                    job_timestamp = datetime.fromisoformat(created_at).timestamp()
                    if job_timestamp < cutoff_date:
                        jobs_to_delete.append(job_id)
                except ValueError:
                    # Invalid date format, delete the job
                    jobs_to_delete.append(job_id)
        
        for job_id in jobs_to_delete:
            self.delete_job(job_id)
    
    def get_job_stats(self) -> Dict[str, Any]:
        """Get statistics about jobs"""
        total_jobs = len(self.jobs)
        completed_jobs = len([j for j in self.jobs.values() if j.get("status") == "completed"])
        failed_jobs = len([j for j in self.jobs.values() if j.get("status") == "failed"])
        processing_jobs = len([j for j in self.jobs.values() if j.get("status") == "processing"])
        queued_jobs = len([j for j in self.jobs.values() if j.get("status") == "queued"])
        
        return {
            "total": total_jobs,
            "completed": completed_jobs,
            "failed": failed_jobs,
            "processing": processing_jobs,
            "queued": queued_jobs
        } 