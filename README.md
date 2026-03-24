# Multi-AI-Agents - Agentic CoE

🤖 **Internal Multi-Agent AI System with Microsoft Agent Framework**

**Repository:** https://github.com/sachidanand/Multi-AI-Agents.git

---

*Production-ready framework for building sophisticated multi-agent AI systems using Microsoft Agent Framework, Azure OpenAI, and modern web interfaces.*

**Tech Stack:** Python 3.10+ | Microsoft Agent Framework | FastAPI | React 18 | Streamlit | Azure OpenAI

---

## 🌟 Overview

Agentic CoE is a production-ready framework for building and deploying multi-agent AI systems using **Microsoft Agent Framework**, Azure OpenAI, Azure AI Services, and Microsoft Foundry (formerly Azure AI Foundry). It provides a complete stack including:

- 🏗️ **Microsoft Agent Framework** - Latest agentic patterns from Microsoft
- 🔄 **Multi-Agent Orchestration** - Sequential, parallel, conditional, and hierarchical workflows
- 🎨 **Modern Web UI** - Both Streamlit (quick demos) and React (production)
- 🚀 **FastAPI Backend** - RESTful API with WebSocket support for streaming
- 📊 **Real-time Monitoring** - Token usage, performance metrics, and Application Insights
- 🔧 **Tool Integration** - Native functions, OpenAPI, and Model Context Protocol (MCP)
- 💾 **State Management** - In-memory and Redis-based state persistence
- 🔐 **Enterprise Ready** - Azure Key Vault, security best practices, and production deployment

## 🎯 Why Microsoft Agent Framework?

This repository uses **Microsoft Agent Framework**, the successor to Semantic Kernel and AutoGen, providing:

✅ **Native Azure Integration** - First-class support for Azure OpenAI and Microsoft Foundry  
✅ **Production-Ready** - Built for enterprise deployments with Microsoft support  
✅ **Modern Architecture** - Designed from the ground up for agentic systems  
✅ **Flexible Orchestration** - Group chat, sequential, concurrent, and handoff patterns  
✅ **Tool Ecosystem** - Native functions, OpenAPI, and MCP support  
✅ **Streaming & Async** - Built-in real-time streaming and async operations  
✅ **Cross-Platform** - Both Python and .NET implementations  

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Layer                                 │
│  ┌──────────────────┐              ┌──────────────────┐         │
│  │  Streamlit App   │              │   React Frontend │         │
│  │  (Quick Demos)   │              │   (Production)   │         │
│  └────────┬─────────┘              └────────┬─────────┘         │
└───────────┼────────────────────────────────┼───────────────────┘
            │                                 │
            └─────────────┬───────────────────┘
                          │
┌─────────────────────────▼─────────────────────────────────────────┐
│                      API Layer (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐           │
│  │ REST Endpoints│  │  WebSockets  │  │  Middleware  │           │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘           │
└─────────┼──────────────────┼──────────────────┼───────────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼───────────────────┐
│                   Orchestration Layer                              │
│  ┌────────────────────────────────────────────────────────┐       │
│  │            Agent Orchestrator                          │       │
│  │  • Sequential  • Parallel  • Conditional  • Hierarchical│      │
│  └────────────────────────────────────────────────────────┘       │
└────────────────────────────┬───────────────────────────────────────┘
                             │
┌────────────────────────────▼───────────────────────────────────────┐
│                        Agent Layer                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │  Customer    │  │  Technical   │  │   Custom     │            │
│  │  Support     │  │  Support     │  │   Agents     │            │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘            │
└─────────┼──────────────────┼──────────────────┼────────────────────┘
          │                  │                  │
┌─────────▼──────────────────▼──────────────────▼────────────────────┐
│                       Core Services                                 │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │Azure OpenAI  │  │  Tool        │  │  Prompt      │            │
│  │Client        │  │  Registry    │  │  Manager     │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐            │
│  │Config        │  │  State       │  │  Logging     │            │
│  │Manager       │  │  Manager     │  │  Service     │            │
│  └──────────────┘  └──────────────┘  └──────────────┘            │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Python 3.10+
- Node.js 18+ (for React UI)
- Azure OpenAI account
- Git

### 1. Clone and Setup

```bash
# Clone repository
git clone <repository-url>
cd Source-Code

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

### 1. Installation

```bash
# Clone the repository
git clone https://github.com/sachidanand/Multi-AI-Agents.git
cd Multi-AI-Agents/Source-Code

# Install dependencies (Note: --pre flag required for Agent Framework preview)
pip install agent-framework-azure-ai --pre
pip install -r requirements.txt

# Or use the automated setup script
chmod +x scripts/setup.sh
./scripts/setup.sh
```

### 2. Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and choose your deployment option:

# Option A: Azure OpenAI (Simpler Setup)
USE_FOUNDRY=false
AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4

# Option B: Microsoft Foundry (Recommended for Production)
USE_FOUNDRY=true
FOUNDRY_PROJECT_ENDPOINT=https://your-project.eastus.inference.ai.azure.com
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o
```

### 3. Quick Start with Agent Framework

Try the example customer support agent:

```bash
# Run the Agent Framework demo
python examples/agent_framework_customer_support.py
```

Output:
```
🎯 Customer Support Agent - Microsoft Agent Framework Demo
────────────────────────────────────────────────────────────────
💬 Conversation 1
────────────────────────────────────────────────────────────────
👤 User: Hi! Can you tell me about your return policy?

🤖 Agent: Our return policy allows you to return items within 30 days 
of purchase with a receipt. Is there a specific item you'dnpm like to 
return?

🔧 Tools used: search_knowledge_base
```

### 4. Run the Backend API

```bash
# Start FastAPI server
python -m api.main

# Or with uvicorn directly
uvicorn api.main:app --reload --host 0.0.0.0 --port 8000

# Or use the development script
./scripts/run_dev.sh
```

API will be available at:
- **Backend API**: https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io
- **API Documentation**: https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/docs
- **WebSocket**: wss://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/ws
```

The API will be available at `https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io`
- API Docs: `https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/docs`
- Health Check: `https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/health`

### 4. Run the UI

#### Option A: Streamlit (Quick Demos)

```bash
streamlit run ui/streamlit_app.py
```

Access at `http://localhost:8501`

#### Option B: React (Production)

```bash
cd ui/frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

Access at `http://localhost:3000`

### 5. Run UI Options

**Option A: Streamlit (Quick Demos)**
```bash
streamlit run ui/streamlit_app.py
# Access at: http://localhost:8501
```

**Option B: React (Production UI)**
```bash
cd ui/frontend
npm install
npm run dev (Agent Framework compatible)
│   └── __init__.py
├── core/                   # Core reusable components
│   ├── agent_framework_client.py  # Microsoft Agent Framework wrapper
│   ├── azure_openai_client.py     # Legacy Azure OpenAI client
**Option C: Docker Compose (Everything Together)**
```bash
docker-compose up
# Backend: https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io
# React UI: http://localhost:3000
# Streamlit: http://localhost:8501
```

## 📚 Documentation

### Quick Links
- **[Agent Framework Quick Start](docs/AGENT_FRAMEWORK_QUICKSTART.md)** - Get started with Microsoft Agent Framework
- **[Agent Development Guide](docs/AGENT_DEVELOPMENT_GUIDE.md)** - Build your own agents
- **[Architecture Overview](ARCHITECTURE.md)** - System design and patterns
- **[Team Guidelines](CONTRIBUTING.md)** - Development guidelines and best practices
- **[API Reference](https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io/docs)** - Interactive API documentation

### Core Concepts

#### 1. Microsoft Agent Framework Integration

The repository uses Microsoft Agent Framework for building agents:

```python
from core.agent_framework_client import AgentFrameworkClient
from typing import Annotated

# Initialize client
client = AgentFrameworkClient(config_manager)

# Define tools
def search_kb(query: Annotated[str, "Search query"]) -> str:
    """Search the knowledge base."""
    return f"Results for: {query}"

# Create agent
async with await client.create_chat_agent(
    agent_name="My Agent",
    instructions="You are a helpful assistant.",
    tools=[search_kb]
) as agent:
    # Stream responses
    async for chunk in agent.run_stream("Hello!"):
        if chunk.text:
            print(chunk.text, end="")
```

See [Agent Framework Quick Start](docs/AGENT_FRAMEWORK_QUICKSTART.md) for detailed examples.

## 📁 Project Structure

```
Source-Code/
├── agents/                 # Agent implementations
│   ├── base_agent.py      # Base agent class
│   └── __init__.py
├── core/                   # Core reusable components
│   ├── azure_openai_client.py
│   ├── config_manager.py
│   ├── logging_service.py
│   ├── state_manager.py
│   └── __init__.py
├── orchestration/          # Multi-agent orchestration
│   ├── agent_orchestrator.py
│   └── __init__.py
├── tools/                  # Shared tools and functions
│   ├── tool_registry.py
│   ├── common_tools.py
│   └── __init__.py
├── prompts/                # Prompt templates
│   ├── prompt_manager.py
│   ├── customer_support_system.yaml
│   └── __init__.py
├── configs/                # Configuration files
│   ├── config.yaml
│   ├── config.dev.yaml
│   └── config.prod.yaml
├── api/                    # FastAPI backend
│   ├── main.py
│   ├── models.py
│   ├── dependencies.py
│   ├── middleware.py
│   └── routes/
│       ├── agents.py
│       ├── orchestration.py
│       └── websocket.py
├── ui/                     # User interfaces
│   ├── streamlit_app.py   # Streamlit app
│   └── frontend/          # React app
│       ├── src/
│       ├── package.json
│       └── vite.config.ts
├── examples/               # Example implementations
│   ├── customer_support_agent.py
│   └── run_customer_support.py
├── tests/                  # Unit and integration tests
├── docs/                   # Documentation
├── scripts/                # Setup and deployment scripts
├── requirements.txt        # Python dependencies
├── pyproject.toml         # Project configuration
├── .env.example           # Environment template
└── README.md              # This file
```

## 🎯 Key Features

### 1. Base Agent Framework

All agents inherit from `BaseAgent` which provides:

```python
from agents.base_agent import BaseAgent, AgentResponse

class MyCustomAgent(BaseAgent):
    async def _execute_logic(self, user_input: str, context: dict) -> AgentResponse:
        # Your agent logic here
        return AgentResponse(
            content="Agent response",
            agent_id=self.agent_id,
            agent_name=self.agent_name
        )
```

### 2. Multi-Agent Orchestration

```python
from orchestration import AgentOrchestrator, OrchestrationStrategy

orchestrator = AgentOrchestrator(state_manager)
orchestrator.register_agent(agent1)
orchestrator.register_agent(agent2)

# Sequential execution with handoffs
responses = await orchestrator.orchestrate(
    initial_agent_id="customer_support",
    user_input="I need help",
    strategy=OrchestrationStrategy.SEQUENTIAL
)
```

### 3. Tool Integration

```python
from tools import ToolRegistry

tool_registry = ToolRegistry()

# Register custom tool
tool_registry.register_tool(
    name="search_docs",
    function=search_documentation,
    description="Search documentation",
    parameters={"query": {"type": "string", "required": True}}
)

# Execute tool
result = await tool_registry.execute_tool("search_docs", query="how to deploy")
```

### 4. Prompt Management

```yaml
# prompts/my_prompt.yaml
name: my_system_prompt
version: "1.0.0"
variables:
  - company_name
  - role
template: |
  You are a {role} for {company_name}.
  Help users with their questions.
```

```python
from prompts import PromptManager

pm = PromptManager()
prompt = pm.render_template("my_system_prompt", 
    company_name="Acme Corp",
    role="support agent"
)
```

## 🔌 API Reference

### Agent Endpoints

```bash
# List all agents
GET /agents/

# Get specific agent
GET /agents/{agent_id}

# Chat with agent
POST /agents/{agent_id}/chat
{
  "message": "Hello",
  "context": {},
  "stream": false
}

# Get conversation history
GET /agents/{agent_id}/history

# Reset agent
POST /agents/{agent_id}/reset
```

### Orchestration Endpoints

```bash
# Orchestrate multi-agent workflow
POST /orchestrate/
{
  "message": "I need help",
  "initial_agent_id": "customer_support",
  "strategy": "sequential",
  "max_iterations": 10
}

# Parallel execution
POST /orchestrate/parallel
{
  "agent_ids": ["agent1", "agent2"],
  "message": "Analyze this"
}
```

### WebSocket Endpoints

```bash
# Stream agent responses
WS /ws/agent/{agent_id}

# Stream orchestration
WS /ws/orchestrate
```

## 🎨 UI Features

### Streamlit Features
- 📱 Agent selector and info display
- 💬 Real-time chat interface
- 🔄 Multi-agent orchestration view
- 📊 Token usage and metrics
- 💾 Export conversations
- 🎭 Pre-configured demo scenarios

### React Features
- 🌓 Dark/Light mode
- 📱 Responsive design
- 🔄 Real-time WebSocket streaming
- 📊 Performance dashboard
- 🎨 Modern UI with Tailwind CSS
- 🔍 Agent discovery and selection
- 📈 Analytics and metrics

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=. --cov-report=html

# Run specific test file
pytest tests/test_agents.py

# Run integration tests
pytest tests/integration/
```

## 📚 Documentation

Detailed documentation is available in the `docs/` directory:

- [Agent Development Guide](docs/AGENT_DEVELOPMENT_GUIDE.md)
- [Azure Setup Guide](docs/AZURE_SETUP.md)
- [API Reference](docs/API_REFERENCE.md)
- [Testing Guide](docs/TESTING_GUIDE.md)
- [UI Customization Guide](docs/UI_GUIDE.md)
- [Architecture Overview](ARCHITECTURE.md)
- [Contributing Guidelines](CONTRIBUTING.md)

## 🚢 Deployment

### Docker

```bash
# Build images
docker-compose build

# Run services
docker-compose up

# Run in background
docker-compose up -d
```

### Azure App Service

```bash
# Using deployment script
./scripts/deploy_azure.sh
```

### Kubernetes

```bash
# Apply configurations
kubectl apply -f k8s/
```

See [deployment documentation](docs/DEPLOYMENT.md) for detailed instructions.

## 📚 Additional Resources

- [Microsoft Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Microsoft Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)

## 🔧 Team Development

See [CONTRIBUTING.md](CONTRIBUTING.md) for development guidelines, coding standards, and best practices.

---

**Agentic CoE Team** | Internal Project | 2026

