# Running Backend + Frontend Together

## ✅ CURRENT STATUS

**Backend API**: ✅ Running on http://localhost:8000 (Process: 19698)  
**Frontend UI**: ✅ Running on http://localhost:3000 (Terminal: 752e0fc8-a6b9-4682-beeb-cfe92b1e85ac)  
**Ollama**: ✅ Running on http://localhost:11434

## 🚀 Quick Start (Services Already Running)

Your services are **already running**! Just open:
```
http://localhost:3000
```

Click the blue chat button in the bottom-right corner to start chatting with the AI agent.

---

## 🔧 Manual Start (If Services Stopped)

### Option 1: Use the Automated Script (Recommended)

```bash
cd /Users/sachidanand/Agentic-CoE/Source-Code

# Start all services
./start-services.sh

# Stop all services when done
./stop-services.sh
```

### Option 2: Start Services Manually in Separate Terminals

**Terminal 1 - Backend API:**
```bash
cd /Users/sachidanand/Agentic-CoE/Source-Code
python -m uvicorn api.support_api:app --reload --port 8000
```

**Terminal 2 - Frontend UI:**
```bash
cd /Users/sachidanand/Agentic-CoE/Source-Code/ui/frontend
npm run dev
```

**Terminal 3 - Ollama (if not running):**
```bash
ollama serve
```

---

## 🧪 Testing the Integration

### 1. Check Backend Health
```bash
curl http://localhost:8000/health
```

Expected response:
```json
{
  "status": "online",
  "ollama_status": "connected"
}
```

### 2. Test API Query
```bash
curl -X POST http://localhost:8000/api/support/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I reset my password?"}'
```

### 3. Test Frontend
1. Open http://localhost:3000 in your browser
2. Click the blue circular chat button (bottom-right)
3. Type a message: "What are your capabilities?"
4. Verify you get an AI-generated response (not hard-coded)

---

## 📊 Service URLs

| Service | URL | Status |
|---------|-----|--------|
| Frontend UI | http://localhost:3000 | ✅ Running |
| Backend API | http://localhost:8000 | ✅ Running |
| API Docs (Swagger) | http://localhost:8000/docs | ✅ Available |
| Ollama | http://localhost:11434 | ✅ Running |

---

## 🛠️ Troubleshooting

### Frontend shows "Agent is offline"

**Check backend:**
```bash
curl http://localhost:8000/health
```

**Restart backend:**
```bash
# Find and kill the process
lsof -ti:8000 | xargs kill -9

# Start fresh
cd /Users/sachidanand/Agentic-CoE/Source-Code
python -m uvicorn api.support_api:app --reload --port 8000
```

### Port already in use

**Backend (port 8000):**
```bash
lsof -ti:8000 | xargs kill -9
```

**Frontend (port 3000):**
```bash
lsof -ti:3000 | xargs kill -9
```

### Chat returns hard-coded responses

This means the backend is **NOT** the support API. Check what's running:
```bash
curl http://localhost:8000/
```

Should return:
```json
{
  "status": "online",
  "service": "HCLTech Self-Service Support API",
  "version": "1.0.0"
}
```

If it shows "Immigration Legal Bot" or something else, restart the correct backend:
```bash
# Stop wrong API
lsof -ti:8000 | xargs kill -9

# Start correct API
cd /Users/sachidanand/Agentic-CoE/Source-Code
python -m uvicorn api.support_api:app --reload --port 8000
```

### Ollama not responding

**Check if Ollama is running:**
```bash
curl http://localhost:11434/api/tags
```

**Start Ollama:**
```bash
ollama serve
```

**Pull required model:**
```bash
ollama pull llama3
```

---

## 🔍 View Logs

**Backend API logs:**
```bash
tail -f /tmp/support_api.log
```

**Frontend logs:**
```bash
tail -f /tmp/frontend.log
```

**Or check the terminal where services are running**

---

## 🎯 Development Workflow

### Making Backend Changes
1. Edit files in `api/` or `agents/`
2. Backend auto-reloads (uvicorn --reload)
3. Test with curl or Swagger docs

### Making Frontend Changes
1. Edit files in `ui/frontend/src/`
2. Frontend hot-reloads automatically
3. Refresh browser to see changes

### Making Agent Logic Changes
1. Edit `api/support_api.py` (StandaloneSupportAgent class)
2. Backend auto-reloads
3. Test in chat widget

---

## 📦 Dependencies

### Backend
- Python 3.8+
- FastAPI
- Uvicorn
- Requests
- Ollama (running locally)

### Frontend
- Node.js 18+
- React 18.2
- TypeScript 5.0
- Vite 5.4

---

## 🚦 Process Management

### Check Running Processes
```bash
# Backend
ps aux | grep uvicorn | grep support_api

# Frontend
ps aux | grep "npm run dev"

# Ollama
ps aux | grep ollama
```

### Kill Specific Process
```bash
# By PID
kill <PID>

# By port
lsof -ti:8000 | xargs kill
lsof -ti:3000 | xargs kill
```

### Kill All Services
```bash
./stop-services.sh
```

---

## 🎉 Success Indicators

✅ Backend logs show: "Application startup complete"  
✅ Frontend shows: "VITE v5.4.21 ready"  
✅ Chat widget shows: "🟢 Online"  
✅ Messages get AI responses (not hard-coded)  
✅ Response includes sentiment and metadata  

---

## 📝 Notes

- Both services support **hot reload** during development
- Backend runs on port **8000** (FastAPI)
- Frontend runs on port **3000** (Vite dev server)
- Ollama runs on port **11434**
- CORS is configured for localhost:3000 and localhost:5173
- API documentation available at http://localhost:8000/docs

---

## 🔗 Related Documentation

- [SUPPORT_AGENT_GUIDE.md](./SUPPORT_AGENT_GUIDE.md) - Agent setup guide
- [UI_INTEGRATION_GUIDE.md](./UI_INTEGRATION_GUIDE.md) - Full integration guide
- [RUNNING_FROM_UI.md](./RUNNING_FROM_UI.md) - Original running guide

---

**Last Updated**: 5 January 2026  
**Status**: ✅ Both services running and integrated
