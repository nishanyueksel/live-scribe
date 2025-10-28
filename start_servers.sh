#!/bin/bash

# Meeting Transcription App - Start Script
# This script starts both the backend and frontend servers

echo "Starting Meeting Transcription App..."
echo ""

# Check if we're in the right directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the hiya_prototype directory"
    echo "   Expected structure: hiya_prototype/backend and hiya_prototype/frontend"
    exit 1
fi

# Function to check if a port is in use
check_port() {
    lsof -i :"$1" >/dev/null 2>&1
}

# Function to kill processes on a port
kill_port() {
    echo "Killing existing processes on port $1..."
    lsof -ti :"$1" | xargs kill -9 2>/dev/null || true
    sleep 2
}

# Check and kill existing processes on our ports
if check_port 8000; then
    kill_port 8000
fi

if check_port 3000; then
    kill_port 3000
fi

# Set up environment variables
export OPENAI_API_KEY=$(cat .env.local 2>/dev/null | grep OPENAI_API_KEY | cut -d'=' -f2)

if [ -z "$OPENAI_API_KEY" ]; then
    echo "Warning: OPENAI_API_KEY not found in .env.local"
    echo "   Summary and action item generation may not work"
    echo ""
fi

# Function to start backend
start_backend() {
    echo "Starting FastAPI Backend on http://127.0.0.1:8000..."
    cd backend
    python3 -m uvicorn app.main:app --reload --port 8000 &
    BACKEND_PID=$!
    cd ..
    echo "   Backend PID: $BACKEND_PID"
}

# Function to start frontend
start_frontend() {
    echo "Starting Next.js Frontend on http://localhost:3000..."
    cd frontend/meeting-summarizer
    bun run dev &
    FRONTEND_PID=$!
    cd ../..
    echo "   Frontend PID: $FRONTEND_PID"
}

# Start both servers
start_backend
sleep 3
start_frontend

echo ""
echo "Both servers are starting up..."
echo ""
echo " Backend API:  http://127.0.0.1:8000"
echo " Frontend UI:  http://localhost:3000"
echo " API Docs:     http://127.0.0.1:8000/docs"
echo ""
echo "🔍 To stop both servers, press Ctrl+C"
echo ""

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "Shutting down servers..."
    kill $BACKEND_PID 2>/dev/null || true
    kill $FRONTEND_PID 2>/dev/null || true
    echo "Servers stopped"
    exit 0
}

# Set up signal handlers
trap cleanup SIGINT SIGTERM

# Wait for user to stop
wait