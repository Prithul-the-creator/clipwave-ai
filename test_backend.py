#!/usr/bin/env python3
"""
Simple test script to verify the ClipWave AI backend is working.
"""

import requests
import json
import time

BASE_URL = "http://localhost:8000"

def test_backend():
    print("🧪 Testing ClipWave AI Backend...")
    
    # Test 1: Check if server is running
    try:
        response = requests.get(f"{BASE_URL}/")
        if response.status_code == 200:
            print("✅ Backend server is running")
        else:
            print("❌ Backend server returned unexpected status code")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to backend server. Make sure it's running on http://localhost:8000")
        return False
    
    # Test 2: Test job creation
    test_job = {
        "youtube_url": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",  # Rick Roll for testing
        "instructions": "Find the most engaging moments",
        "user_id": "test_user"
    }
    
    try:
        response = requests.post(f"{BASE_URL}/api/jobs", json=test_job)
        if response.status_code == 200:
            job_data = response.json()
            job_id = job_data.get("job_id")
            print(f"✅ Job created successfully with ID: {job_id}")
            
            # Test 3: Check job status
            time.sleep(1)  # Wait a moment for job to be processed
            response = requests.get(f"{BASE_URL}/api/jobs/{job_id}")
            if response.status_code == 200:
                status_data = response.json()
                print(f"✅ Job status retrieved: {status_data.get('status')}")
            else:
                print("❌ Failed to retrieve job status")
                return False
                
        else:
            print(f"❌ Failed to create job: {response.status_code}")
            print(response.text)
            return False
    except Exception as e:
        print(f"❌ Error testing job creation: {e}")
        return False
    
    # Test 4: List jobs
    try:
        response = requests.get(f"{BASE_URL}/api/jobs")
        if response.status_code == 200:
            jobs_data = response.json()
            print(f"✅ Retrieved {len(jobs_data.get('jobs', []))} jobs")
        else:
            print("❌ Failed to list jobs")
            return False
    except Exception as e:
        print(f"❌ Error listing jobs: {e}")
        return False
    
    print("\n🎉 All tests passed! Backend is working correctly.")
    return True

if __name__ == "__main__":
    test_backend() 