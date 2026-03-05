# 🚀 Quick Start: Support Agent

**Checklist for successful query execution with support_agent.html**

---

## ✅ Prerequisites

- [ ] Python 3.8+ installed
- [ ] Install dependencies: `pip install python-dotenv openai`
- [ ] File `knowledge_graph.json` exists in `Knowledge_Graph_views/`
- [ ] Folder `data/` with documents exists

---

## ✅ LLM Provider Setup

### Option 1: Azure OpenAI (Recommended)

Create `.env` file in **project root** (one level above `Knowledge_Graph_views/`):

```bash
USE_AZURE_OPENAI=true
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
KG_AGENT_MODEL=gpt-4o-mini
```

**Minimum required variables:**
- `AZURE_OPENAI_ENDPOINT` - Your Azure OpenAI endpoint URL
- `AZURE_OPENAI_API_KEY` - Your Azure OpenAI API key
- `KG_AGENT_MODEL` - Deployment name (e.g., gpt-4o-mini, gpt-4, gpt-4o)

**Optional variables:**
- `AZURE_OPENAI_API_VERSION` - API version (default: 2024-02-15-preview)

---

### Option 2: Ollama (Local)

- [ ] Install Ollama from https://ollama.ai
- [ ] Start Ollama service
- [ ] Pull a model: `ollama pull gemma3:4b`
- [ ] Set `USE_AZURE_OPENAI=false` in `.env` (or leave unset)

**Note:** Edit `server.py` to change `OLLAMA_MODEL` if using a different model.

---

## ✅ Start the Server

### Windows PowerShell

**With Azure OpenAI:**
```powershell
cd Knowledge_Graph_views
.\start_with_azure.ps1
```

**With Ollama or manual start:**
```powershell
cd Knowledge_Graph_views
python server.py
```

### Linux/Mac

**With Azure OpenAI:**
```bash
cd Knowledge_Graph_views
export USE_AZURE_OPENAI=true
python server.py
```

**With Ollama:**
```bash
cd Knowledge_Graph_views
python server.py
```

---

## ✅ Open the UI

1. Server should print: `Serving at http://localhost:8080`
2. Open browser: **http://localhost:8080/support_agent.html**
3. Type a query, e.g., "System crashed during call handling"
4. Click **Send**

---

## ✅ Verify Setup

**Check server logs for:**
- `[INFO] Azure OpenAI client initialized: gpt-4o-mini` (if using Azure)
- `Loaded knowledge graph with X nodes` (should see node count)
- `Serving at http://localhost:8080`

**Check browser console (F12) for:**
- No red errors
- Successful connection to `http://localhost:8080/api/chat`

---

## 🐛 Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'openai'` | Run: `pip install openai` |
| `ModuleNotFoundError: No module named 'dotenv'` | Run: `pip install python-dotenv` |
| Azure client not initialized | Check `.env` file location (must be in project root) |
| Connection refused | Ensure server is running on port 8080 |
| Ollama error | Check Ollama is running: `ollama list` |
| Empty responses | Check server console for errors |
| Send button stays disabled | Check browser console, see [BUGFIX_SUMMARY.md](BUGFIX_SUMMARY.md) |

---

## 📂 File Structure

```
kg/
├── .env                           ← Environment variables here
└── Knowledge_Graph_views/
    ├── server.py                  ← Backend server
    ├── support_agent.html         ← Frontend UI
    ├── knowledge_graph.json       ← Knowledge graph data
    ├── start_with_azure.ps1       ← Quick start script (Windows)
    └── data/                      ← Documents referenced in graph
        ├── ReleaseNotes_2025W2.txt
        ├── UserGuide_AgentDesktop.txt
        └── ...
```

---

## 🎯 Next Steps

- **Test queries:** Try different support scenarios
- **Add documents:** Place new `.txt` files in `data/` folder
- **Extend graph:** Edit `knowledge_graph.json` to add nodes/edges
- **Customize prompts:** Edit `server.py` LLM prompts for better responses
- **Deploy:** See deployment docs for production setup

---

## 📖 Related Documentation

- [BUGFIX_SUMMARY.md](BUGFIX_SUMMARY.md) - Recent bug fixes and improvements
- [README_RESOLVE_ISSUE.md](README_RESOLVE_ISSUE.md) - Full setup guide
- [knowledge_graph_connections.json](knowledge_graph_connections.json) - Graph schema reference
