# Ollama Integration for Multi-AI-Agents

## 🚀 Overview

This integration adds **Ollama support** to your Multi-AI-Agents project, allowing you to use **local open-source LLMs** instead of Azure OpenAI.

**Key Benefits:**
- ✅ **No Azure costs** - Run locally for free
- ✅ **Data privacy** - Everything stays on your machine
- ✅ **Offline capable** - Works without internet
- ✅ **Easy switching** - Toggle between Ollama and Azure OpenAI with env vars
- ✅ **No new files** - Uses existing `azure_openai_client.py` with OpenAI-compatible endpoint
- ✅ **ngrok support** - Expose local Ollama to the internet

---

## 📋 Quick Start

### 1️⃣ Install Ollama (5 minutes)

**Option A: Direct Download**
- Visit https://ollama.ai
- Download and run installer for your OS

**Option B: Docker**
```bash
docker run -d -p 11434:11434 ollama/ollama
```

**Option C: Package Manager**
```bash
# macOS
brew install ollama

# Linux (add repo)
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2️⃣ Pull a Model (2-5 minutes)

```bash
# Recommended for development
ollama pull mistral

# Or try others:
ollama pull neural-chat
ollama pull openchat
ollama pull llama2
```

Verify with:
```bash
curl http://localhost:11434/api/tags
```

### 3️⃣ Use Ollama in Your App

**Just set one flag:**
```powershell
# Windows (PowerShell)
$env:USE_OLLAMA = "true"
python -m uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

```bash
# Linux/Mac
USE_OLLAMA=true uvicorn api.main:app --reload --host 0.0.0.0 --port 8000
```

**Optional: Customize model or endpoint:**
```powershell
$env:USE_OLLAMA = "true"
$env:OLLAMA_MODEL = "neural-chat"  # Optional, defaults to "mistral"
$env:OLLAMA_BASE_URL = "http://localhost:11434"  # Optional, this is the default
python -m uvicorn api.main:app --reload
```

**Via ngrok (Remote Access):**
```bash
# Terminal 1: Start Ollama
ollama serve

# Terminal 2: Expose with ngrok
ngrok http 11434

# Terminal 3: Use the ngrok URL
$env:USE_OLLAMA = "true"
$env:OLLAMA_BASE_URL = "https://abc123.ngrok.io"  # Your ngrok URL
python -m uvicorn api.main:app --reload
```

✅ **Done!** Your app now uses Ollama instead of Azure OpenAI.

**Access the API:**
- API Docs: https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/docs
- API Health: https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/health

---

## 🔧 How It Works

The existing `azure_openai_client.py` checks for the `USE_OLLAMA` flag:

```python
# If USE_OLLAMA=true, automatically use Ollama
# Otherwise, use Azure OpenAI

# Priority order:
# 1. USE_OLLAMA=true → Uses AsyncOpenAI with Ollama endpoint
# 2. Azure API key → Uses AsyncAzureOpenAI with API key
# 3. No API key → Uses AsyncAzureOpenAI with Azure AD
```

**Just one flag!** No need to set multiple environment variables.

---

## 🔧 Configuration

### Environment Variables
```bash
# Enable Ollama (required)
USE_OLLAMA=true

# Optional: Customize Ollama settings
OLLAMA_BASE_URL=http://localhost:11434  # Default
OLLAMA_MODEL=mistral                     # Default
```

### Switch Back to Azure OpenAI
```powershell
# Windows - Just remove the flag
Remove-Item Env:USE_OLLAMA -ErrorAction SilentlyContinue
python -m uvicorn api.main:app --reload
```

```bash
# Linux/Mac
unset USE_OLLAMA
uvicorn api.main:app --reload
```

---

## 🤖 Model Recommendations

| Model | Speed | Quality | VRAM | Notes |
|-------|-------|---------|------|-------|
| `openchat` | ⚡⚡⚡ | Good | 4GB | Best for dev, very fast |
| `mistral` | ⚡⚡ | Good | 5GB | **Recommended** |
| `neural-chat` | ⚡⚡ | Excellent | 5GB | Great balance |
| `llama2` | ⚡ | Excellent | 7GB | High quality |
| `dolphin-mixtral` | 🐢 | Best | 30GB+ | Large, needs GPU |

**For Development**: `mistral` or `neural-chat`
**For Production**: `neural-chat` or `dolphin-mixtral` (with GPU)
**For Speed**: `openchat` or `mistral`

---

## ✅ Testing Your Setup

### 1. Quick Health Check
```bash
curl http://localhost:11434/api/tags
```

### 2. Test with FastAPI
```powershell
# Windows
$env:OPENAI_BASE_URL = "http://localhost:11434/v1"
$env:OPENAI_MODEL = "mistral"
python -m uvicorn api.main:app --reload
# Visit https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/docs
```

---

## 🔄 Switching Between Providers

### Use Ollama (Local)
```powershell
# Windows - Just set the flag
$env:USE_OLLAMA = "true"
python -m uvicorn api.main:app --reload
```

### Use Ollama (via ngrok)
```powershell
# Windows
$env:USE_OLLAMA = "true"
$env:OLLAMA_BASE_URL = "https://your-ngrok-url.ngrok.io"
python -m uvicorn api.main:app --reload
```

### Use Azure OpenAI (Default)
```powershell
# Windows - Remove the flag to use Azure
Remove-Item Env:USE_OLLAMA -ErrorAction SilentlyContinue
python -m uvicorn api.main:app --reload
```

---

## 🐳 Docker Setup

### Simple Docker Compose
```bash
# Start services
docker-compose -f docker-compose.ollama.yml up -d

# Check status
docker-compose -f docker-compose.ollama.yml logs -f

# Stop
docker-compose -f docker-compose.ollama.yml down
```

### Pull Models in Container
```bash
docker exec multi-ai-ollama ollama pull mistral
docker exec multi-ai-ollama ollama pull neural-chat
```

### With GPU Support
```bash
# Install nvidia-docker first
# Then uncomment GPU lines in docker-compose.ollama.yml
docker-compose -f docker-compose.ollama.yml up -d
```

---

## 🐛 Troubleshooting

### Ollama Not Running
```bash
# Start Ollama
ollama serve

# Or check if already running
ps aux | grep ollama
```

### Connection Refused
```bash
# Verify Ollama is listening
curl -v http://localhost:11434/api/tags

# If not working, restart
pkill ollama
ollama serve
```

### Model Not Found
```bash
# List models
ollama list

# Pull model
ollama pull mistral

# Verify
ollama list
```

### Out of Memory
```bash
# Use smaller model
ollama pull openchat  # 4GB VRAM

# Or reduce max tokens
export OLLAMA_MAX_TOKENS=500
python api/main.py
```

### Slow Responses
```bash
# Try faster model
export OLLAMA_MODEL=mistral
python api/main.py

# Or reduce timeout
export OLLAMA_MAX_TOKENS=500
```

### GPU Not Used
- Check GPU support in Ollama docs: https://ollama.ai
- Install NVIDIA drivers
- Use `nvidia-smi` to verify GPU available
- Restart Ollama after GPU changes

---

## 📊 Performance Metrics

### Token Generation Speed
```
Model          GPU      CPU      Quality
mistral        100+     50       Good
neural-chat    90+      40       Excellent
llama2         80+      30       Excellent
openchat       150+     80       Good
```

(Approximate tokens/sec)

---

## 🔐 Security & Privacy

### Ollama (Local)
✅ All data stays on your machine
✅ No network requests to process queries
✅ No credential storage needed
✅ Works offline

### Azure OpenAI
✅ Enterprise security
✅ Compliance certifications
✅ Monitoring & logging
⚠️ Data sent to Azure cloud

---

## 📚 More Resources

### External
- 🌐 Ollama: https://ollama.ai
- 📦 Models: https://ollama.ai/library
- 🐳 Docker: https://hub.docker.com/r/ollama/ollama
- 💬 Community: https://github.com/ollama/ollama
- 🔗 ngrok: https://ngrok.com

---

## ❓ FAQ

**Q: Will this break my existing Azure OpenAI setup?**
A: No! The existing code works unchanged. Just don't set OPENAI_BASE_URL.

**Q: How much VRAM do I need?**
A: For `mistral` (recommended): 5GB. For `llama2`: 7GB. For smaller models: 3-4GB.

**Q: Can I use GPU?**
A: Yes! Ollama supports NVIDIA, AMD, and Apple Metal. See Ollama docs.

**Q: Can I access my Ollama from anywhere?**
A: Yes! Use ngrok to expose your local Ollama and set OPENAI_BASE_URL to the ngrok URL.

**Q: What files were modified?**
A: Only `core/azure_openai_client.py` - added support for OpenAI-compatible endpoints.

**Q: Can I run Ollama on a different machine?**
A: Yes! Set `OPENAI_BASE_URL=http://other-machine:11434/v1`

---

## 🎉 That's It!

You now have a fully integrated local LLM setup. Enjoy! 🚀

**Quick Start:**
```powershell
# 1. Install Ollama from https://ollama.ai
# 2. Pull a model
ollama pull mistral

# 3. Start with Ollama - just one flag!
$env:USE_OLLAMA = "true"
python -m uvicorn api.main:app --reload

# 4. (Optional) Expose via ngrok for remote access
ngrok http 11434
$env:OLLAMA_BASE_URL = "https://your-ngrok-url.ngrok.io"
```

For questions or issues, see the Ollama documentation.
