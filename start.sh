#!/bin/bash

# Start the backend server
echo "Starting ClipWave AI Backend..."
cd backend
python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!

# Wait a moment for backend to start
sleep 3

# Start the frontend server
echo "Starting ClipWave AI Frontend..."
cd ..
npm run dev &
FRONTEND_PID=$!

echo "ClipWave AI is starting up..."
echo "Backend: http://localhost:8000"
echo "Frontend: http://localhost:8080"
echo ""
echo "Press Ctrl+C to stop both servers"

# Wait for user to stop
wait

# Cleanup on exit
echo "Stopping servers..."
kill $BACKEND_PID $FRONTEND_PID 2>/dev/null 