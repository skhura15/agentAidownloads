#!/bin/bash

# Run development servers
# This script starts both backend and frontend servers for development

set -e

echo "🚀 Starting Agentic CoE development servers..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run './scripts/setup.sh' first."
    exit 1
fi

# Load environment variables
if [ -f ".env" ]; then
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env file not found. Using default configuration."
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Stopping servers..."
    kill $(jobs -p) 2>/dev/null
    exit 0
}

trap cleanup SIGINT SIGTERM

# Start backend API
echo "🔄 Starting FastAPI backend on port 8000..."
source venv/bin/activate
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 3

# Check if backend is running
if curl -s http://localhost:8000/health > /dev/null; then
    echo "✅ Backend is running"
else
    echo "❌ Backend failed to start"
    kill $BACKEND_PID
    exit 1
fi

# Start Streamlit (if requested)
if [ "$1" == "--streamlit" ] || [ "$1" == "-s" ]; then
    echo "🔄 Starting Streamlit UI on port 8501..."
    streamlit run ui/streamlit_app.py --server.address 0.0.0.0 --server.port 8501 &
    STREAMLIT_PID=$!
fi

# Start React frontend (if Node.js is available)
if command -v node &> /dev/null && [ -d "ui/frontend/node_modules" ]; then
    echo "🔄 Starting React frontend on port 3000..."
    cd ui/frontend
    npm run dev &
    FRONTEND_PID=$!
    cd ../..
else
    echo "⚠️  Skipping React frontend (Node.js or dependencies not found)"
fi

echo ""
echo "✅ Development servers are running:"
echo "   📡 API: http://localhost:8000"
echo "   📚 API Docs: http://localhost:8000/docs"
echo "   🏥 Health: http://localhost:8000/health"

if [ ! -z "$STREAMLIT_PID" ]; then
    echo "   🎨 Streamlit UI: http://localhost:8501"
fi

if [ ! -z "$FRONTEND_PID" ]; then
    echo "   ⚛️  React UI: http://localhost:3000"
fi

echo ""
echo "Press Ctrl+C to stop all servers"
echo ""

# Wait for all background processes
wait
