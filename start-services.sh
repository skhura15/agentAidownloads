#!/bin/bash

# HCLTech Self-Service Support Agent - Start All Services
# This script starts both the backend API and frontend UI

echo "🚀 Starting HCLTech Self-Service Support Agent Services..."
echo ""

# Check if Ollama is running
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "⚠️  Warning: Ollama doesn't seem to be running on port 11434"
    echo "   Please start Ollama first: ollama serve"
    echo ""
fi

# Start Backend API
echo "📡 Starting Backend API on port 8000..."
cd /Users/sachidanand/Agentic-CoE/Source-Code
nohup python -m uvicorn api.support_api:app --reload --port 8000 > /tmp/support_api.log 2>&1 &
BACKEND_PID=$!
echo "   Backend PID: $BACKEND_PID"
echo "   Logs: /tmp/support_api.log"
sleep 3

# Check if backend started successfully
if curl -s http://localhost:8000/ > /dev/null 2>&1; then
    echo "   ✅ Backend API is running on http://localhost:8000"
else
    echo "   ❌ Backend API failed to start. Check /tmp/support_api.log"
    exit 1
fi

echo ""

# Start Frontend UI
echo "🎨 Starting Frontend UI on port 3000..."
cd /Users/sachidanand/Agentic-CoE/Source-Code/ui/frontend
nohup npm run dev > /tmp/frontend.log 2>&1 &
FRONTEND_PID=$!
echo "   Frontend PID: $FRONTEND_PID"
echo "   Logs: /tmp/frontend.log"
sleep 5

# Check if frontend started successfully
if curl -s http://localhost:3000/ > /dev/null 2>&1; then
    echo "   ✅ Frontend UI is running on http://localhost:3000"
else
    echo "   ⚠️  Frontend is starting... may take a few more seconds"
fi

echo ""
echo "═══════════════════════════════════════════════════════════"
echo "✅ ALL SERVICES STARTED SUCCESSFULLY!"
echo "═══════════════════════════════════════════════════════════"
echo ""
echo "🌐 Service URLs:"
echo "   • Frontend UI:  http://localhost:3000"
echo "   • Backend API:  http://localhost:8000"
echo "   • API Docs:     http://localhost:8000/docs"
echo "   • Ollama:       http://localhost:11434"
echo ""
echo "📊 Process IDs:"
echo "   • Backend:  $BACKEND_PID"
echo "   • Frontend: $FRONTEND_PID"
echo ""
echo "📝 Log Files:"
echo "   • Backend:  tail -f /tmp/support_api.log"
echo "   • Frontend: tail -f /tmp/frontend.log"
echo ""
echo "🛑 To stop all services:"
echo "   kill $BACKEND_PID $FRONTEND_PID"
echo "   Or run: ./stop-services.sh"
echo ""
echo "🎯 Open http://localhost:3000 in your browser and click the chat button!"
echo "═══════════════════════════════════════════════════════════"
