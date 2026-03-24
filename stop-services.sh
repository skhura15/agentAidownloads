#!/bin/bash

# HCLTech Self-Service Support Agent - Stop All Services
# This script stops both the backend API and frontend UI

echo "🛑 Stopping HCLTech Self-Service Support Agent Services..."
echo ""

# Stop Backend API (port 8000)
BACKEND_PIDS=$(lsof -ti:8000)
if [ -n "$BACKEND_PIDS" ]; then
    echo "📡 Stopping Backend API (port 8000)..."
    echo "   PIDs: $BACKEND_PIDS"
    echo "$BACKEND_PIDS" | xargs kill -9 2>/dev/null
    echo "   ✅ Backend stopped"
else
    echo "   ℹ️  No backend process found on port 8000"
fi

echo ""

# Stop Frontend UI (port 3000)
FRONTEND_PIDS=$(lsof -ti:3000)
if [ -n "$FRONTEND_PIDS" ]; then
    echo "🎨 Stopping Frontend UI (port 3000)..."
    echo "   PIDs: $FRONTEND_PIDS"
    echo "$FRONTEND_PIDS" | xargs kill -9 2>/dev/null
    echo "   ✅ Frontend stopped"
else
    echo "   ℹ️  No frontend process found on port 3000"
fi

echo ""

# Stop any node processes related to the project
NODE_PROCS=$(ps aux | grep "npm run dev" | grep -v grep | awk '{print $2}')
if [ -n "$NODE_PROCS" ]; then
    echo "🔧 Cleaning up additional node processes..."
    echo "$NODE_PROCS" | xargs kill -9 2>/dev/null
fi

# Stop any uvicorn processes
UVICORN_PROCS=$(ps aux | grep "uvicorn api.support_api" | grep -v grep | awk '{print $2}')
if [ -n "$UVICORN_PROCS" ]; then
    echo "🔧 Cleaning up additional uvicorn processes..."
    echo "$UVICORN_PROCS" | xargs kill -9 2>/dev/null
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ ALL SERVICES STOPPED"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "ℹ️  Note: Ollama service (port 11434) was not stopped."
echo "   To stop Ollama, run: killall ollama"
echo ""
