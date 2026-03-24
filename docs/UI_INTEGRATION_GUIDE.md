# Running Self-Service Support Agent from UI

## Quick Start Guide

This guide shows how to run the Support Agent with the web UI interface.

## Architecture

```
┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐
│   React UI      │─────▶│   FastAPI       │─────▶│   Ollama        │
│   (Port 3000)   │      │   (Port 8000)   │      │   (Port 11434)  │
│   Chat Widget   │◀─────│   Support API   │◀─────│   llama3 Model  │
└─────────────────┘      └─────────────────┘      └─────────────────┘
```

## Prerequisites

1. **Ollama installed and running**
   ```bash
   # Install Ollama
   brew install ollama  # macOS
   
   # Start Ollama service
   ollama serve
   
   # Pull llama3 model
   ollama pull llama3
   ```

2. **Python dependencies**
   ```bash
   pip install fastapi uvicorn requests pydantic
   ```

3. **Node.js and React dependencies** (already installed)

## Step-by-Step Setup

### Step 1: Start Ollama (Terminal 1)

```bash
# Start Ollama service
ollama serve
```

Keep this terminal running.

### Step 2: Start FastAPI Backend (Terminal 2)

```bash
cd /Users/sachidanand/Agentic-CoE/Source-Code

# Start the API server
python -m uvicorn api.support_api:app --reload --port 8000
```

You should see:
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
```

**API Endpoints:**
- Health check: http://localhost:8000/health
- API docs: http://localhost:8000/docs
- Support query: http://localhost:8000/api/support/query

### Step 3: Start React Frontend (Terminal 3)

```bash
cd /Users/sachidanand/Agentic-CoE/Source-Code/ui/frontend

# Start React dev server
npm run dev
```

You should see:
```
VITE v5.4.21  ready in 139 ms
➜  Local:   http://localhost:3000/
```

### Step 4: Test the Integration

1. Open browser: http://localhost:3000/

2. Look for the chat widget (blue circle button) in bottom-right corner

3. Click to open chat interface

4. Try sample queries:
   - "How do I reset my password?"
   - "My dashboard is loading slowly"
   - "How do I export my data?"
   - "Help me connect to Microsoft Teams"

## Verification Checklist

✅ **Ollama Status:**
```bash
curl http://localhost:11434/api/tags
# Should return list of models including llama3
```

✅ **API Status:**
```bash
curl http://localhost:8000/health
# Should return: {"api_status":"online","ollama_status":"online",...}
```

✅ **Frontend:**
- Chat widget appears in bottom-right
- Widget shows "🟢 Online" status
- Messages send and receive responses

## Testing the API Directly

### Using curl:

```bash
# Test support query
curl -X POST http://localhost:8000/api/support/query \
  -H "Content-Type: application/json" \
  -d '{"query": "How do I reset my password?"}'
```

### Using the Swagger UI:

1. Open http://localhost:8000/docs
2. Expand `POST /api/support/query`
3. Click "Try it out"
4. Enter query: `{"query": "How do I export my data?"}`
5. Click "Execute"

## UI Features

### Chat Widget Features:

1. **Floating Button**: Click blue circle in bottom-right to open
2. **Real-time Chat**: Send messages and get AI responses
3. **Status Indicator**: Shows if API is online/offline
4. **Sentiment Analysis**: Agent detects user mood
5. **Escalation**: Automatically escalates complex queries
6. **Typing Indicator**: Shows "Agent is thinking..."
7. **Metadata**: Response time and escalation status

### Sample Conversation:

```
User: I forgot my password
Agent: To reset your password: 1) Click 'Forgot Password'...
       ⚠️ Escalated | 5.2s

User: How do I export data?
Agent: Data export: 1) Navigate to Settings > Data Management...
       3.8s
```

## Troubleshooting

### Issue: Chat shows "🔴 Offline"

**Solution:**
```bash
# Check if API is running
curl http://localhost:8000/health

# If not running, start it:
cd /Users/sachidanand/Agentic-CoE/Source-Code
python -m uvicorn api.support_api:app --reload --port 8000
```

### Issue: "Cannot connect to Ollama"

**Solution:**
```bash
# Check Ollama status
curl http://localhost:11434/api/tags

# If offline, start it:
ollama serve

# Pull llama3 if needed:
ollama pull llama3
```

### Issue: CORS errors in browser console

**Solution:** The API already has CORS configured for `http://localhost:3000`. If using different port, update `api/support_api.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:YOUR_PORT"],
    ...
)
```

### Issue: Slow responses (>10 seconds)

**Causes:**
- First query after Ollama start (model loading)
- Large model on limited RAM
- CPU-only inference

**Solutions:**
- Wait for first query to complete (model loads into memory)
- Use smaller model: `ollama pull phi3:mini`
- Update `api/support_api.py` to use phi3:mini instead of llama3

## Production Deployment

For production, replace Ollama with cloud AI:

### Option 1: Azure OpenAI

```python
# In api/support_api.py
from openai import AzureOpenAI

client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_KEY"),
    api_version="2024-02-01",
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT")
)

response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt}
    ]
)
```

### Option 2: GitHub Models

```python
from openai import OpenAI

client = OpenAI(
    base_url="https://models.inference.ai.azure.com",
    api_key=os.getenv("GITHUB_TOKEN")
)

response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[...]
)
```

## Monitoring

### Check API logs:

Terminal 2 shows real-time requests:
```
INFO:     127.0.0.1:52418 - "POST /api/support/query HTTP/1.1" 200 OK
```

### Check Ollama logs:

Terminal 1 shows model inference:
```
[GIN] 2026/01/05 - 12:34:56 | 200 | 5.234567s | POST /api/generate
```

## Next Steps

1. **Add Authentication**: Protect API with API keys or OAuth
2. **Add Rate Limiting**: Prevent abuse
3. **Add Analytics**: Track query patterns and satisfaction
4. **Improve Knowledge Base**: Add more articles
5. **Add Multi-turn Conversations**: Store conversation history
6. **Add Voice Input**: Integrate Web Speech API
7. **Add File Upload**: Support screenshot sharing

## Files Changed

- ✅ `api/support_api.py` - FastAPI backend endpoint
- ✅ `ui/frontend/src/components/SupportChat.tsx` - Chat widget
- ✅ `ui/frontend/src/pages/LandingPage.tsx` - Added widget to page

## Support

Questions? Check:
- API Docs: http://localhost:8000/docs
- Frontend: http://localhost:3000/
- Ollama: https://ollama.ai/docs

## Complete Command Reference

```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Start API
cd /Users/sachidanand/Agentic-CoE/Source-Code
python -m uvicorn api.support_api:app --reload --port 8000

# Terminal 3: Start Frontend
cd /Users/sachidanand/Agentic-CoE/Source-Code/ui/frontend
npm run dev

# Then open: http://localhost:3000/
```

That's it! You now have a fully functional AI support agent integrated with your UI! 🚀
