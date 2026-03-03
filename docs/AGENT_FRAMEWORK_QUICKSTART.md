# Microsoft Agent Framework - Quick Start Guide

**Internal guide for the Multi-AI-Agents project.**

This guide will help you get started with the Microsoft Agent Framework integration.

## Installation

### Prerequisites

- Python 3.10 or higher
- Azure OpenAI or Microsoft Foundry (formerly Azure AI Foundry) access
- pip or conda

### Step 1: Install Dependencies

The Agent Framework is currently in preview, so you need the `--pre` flag:

```bash
# Install all requirements including Agent Framework
pip install -r requirements.txt

# Or install Agent Framework separately
pip install agent-framework-azure-ai --pre
```

### Step 2: Configure Your Environment

Copy the example environment file:

```bash
cp .env.example .env
```

Edit `.env` and choose your deployment option:

#### Option A: Azure OpenAI (Simpler Setup)

```bash
USE_FOUNDRY=false

AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
AZURE_OPENAI_API_KEY=your-api-key-here
AZURE_OPENAI_DEPLOYMENT=gpt-4
AZURE_OPENAI_API_VERSION=2024-02-15-preview
```

#### Option B: Microsoft Foundry (Recommended for Production)

```bash
USE_FOUNDRY=true

FOUNDRY_PROJECT_ENDPOINT=https://your-project.eastus.inference.ai.azure.com
FOUNDRY_MODEL_DEPLOYMENT=gpt-4o
```

## Quick Start Examples

### Example 1: Simple Chat Agent

```python
import asyncio
from core.config_manager import ConfigManager
from core.agent_framework_client import AgentFrameworkClient

async def simple_chat():
    # Initialize
    config = ConfigManager(config_dir="configs", environment="dev")
    client = AgentFrameworkClient(config)
    
    # Create agent
    async with await client.create_chat_agent(
        agent_name="Simple Assistant",
        instructions="You are a helpful assistant."
    ) as agent:
        # Chat with streaming
        print("Agent: ", end="", flush=True)
        async for chunk in agent.run_stream("Hello! Who are you?"):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()

asyncio.run(simple_chat())
```

### Example 2: Agent with Tools

```python
from typing import Annotated

# Define a tool
def get_weather(
    location: Annotated[str, "City name"]
) -> str:
    """Get weather for a location."""
    return f"It's sunny and 72°F in {location}"

async def agent_with_tools():
    config = ConfigManager(config_dir="configs", environment="dev")
    client = AgentFrameworkClient(config)
    
    async with await client.create_chat_agent(
        agent_name="Weather Assistant",
        instructions="You help users check the weather.",
        tools=[get_weather]  # Pass tools here
    ) as agent:
        async for chunk in agent.run_stream("What's the weather in Seattle?"):
            if chunk.text:
                print(chunk.text, end="", flush=True)

asyncio.run(agent_with_tools())
```

### Example 3: Multi-turn Conversation

```python
async def conversation():
    config = ConfigManager(config_dir="configs", environment="dev")
    client = AgentFrameworkClient(config)
    
    async with await client.create_chat_agent(
        agent_name="Conversational Assistant",
        instructions="You are a friendly assistant."
    ) as agent:
        # Create a thread for conversation continuity
        thread = agent.get_new_thread()
        
        # First message
        async for chunk in agent.run_stream("My name is John", thread=thread):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print("\n")
        
        # Second message - agent remembers context
        async for chunk in agent.run_stream("What's my name?", thread=thread):
            if chunk.text:
                print(chunk.text, end="", flush=True)
        print()

asyncio.run(conversation())
```

### Example 4: Customer Support Agent (Full Example)

Run the complete customer support agent demo:

```bash
python examples/agent_framework_customer_support.py
```

This demonstrates:
- Multiple tools (search, create ticket, email, order tracking)
- Professional system instructions
- Streaming responses
- Tool call tracking
- Multi-turn conversations

## Key Concepts

### 1. Agent Framework Client

The `AgentFrameworkClient` wraps Microsoft Agent Framework for easy use:

```python
from core.agent_framework_client import AgentFrameworkClient

client = AgentFrameworkClient(config_manager)
```

### 2. Creating Agents

```python
async with await client.create_chat_agent(
    agent_name="My Agent",
    instructions="System instructions",
    tools=[tool1, tool2],
    temperature=0.7
) as agent:
    # Use agent here
    pass
```

### 3. Defining Tools

Tools are Python functions with type hints:

```python
from typing import Annotated

def my_tool(
    param: Annotated[str, "Parameter description"]
) -> str:
    """Tool description for the LLM."""
    return "result"
```

The Agent Framework automatically:
- Extracts function schema
- Passes it to the LLM
- Calls your function when needed
- Returns results to the LLM

### 4. Streaming vs Non-Streaming

**Streaming (Recommended):**
```python
async for chunk in agent.run_stream(user_input, thread=thread):
    if chunk.text:
        print(chunk.text, end="", flush=True)
```

**Non-Streaming:**
```python
result = await agent.run(user_input, thread=thread)
print(result.text)
```

### 5. Thread Management

Threads maintain conversation context:

```python
# Create new thread
thread = agent.get_new_thread()

# Use same thread across calls
await agent.run_stream("First message", thread=thread)
await agent.run_stream("Second message", thread=thread)  # Remembers context
```

## Advanced Features

### MCP (Model Context Protocol) Tools

Connect to external services via MCP:

```python
# Stdio MCP tool
mcp_tool = client.create_mcp_stdio_tool(
    name="Playwright",
    description="Browser automation",
    command="npx",
    args=["-y", "@playwright/mcp@latest"]
)

# HTTP MCP tool
learn_tool = client.create_mcp_http_tool(
    name="Microsoft Learn",
    description="Microsoft documentation",
    url="https://learn.microsoft.com/api/mcp"
)

async with await client.create_chat_agent(
    agent_name="Browser Agent",
    instructions="Help users with web automation",
    tools=[mcp_tool, learn_tool]
) as agent:
    # Agent can now use MCP tools
    pass
```

### Token Tracking

```python
from core.agent_framework_client import TokenManager

token_mgr = TokenManager(model="gpt-4")

# After API calls
token_mgr.update_usage(prompt_tokens=150, completion_tokens=75)

# Get stats
stats = token_mgr.get_stats()
print(f"Total cost: ${stats['estimated_cost']}")
```

## Migration from Semantic Kernel

If you're migrating from Semantic Kernel:

| Semantic Kernel | Agent Framework |
|----------------|-----------------|
| `Kernel` | `ChatAgent` |
| `SKFunction` | Python function with type hints |
| `KernelArguments` | Function parameters |
| `ChatHistory` | Thread |
| `invoke_stream` | `run_stream` |

## Troubleshooting

### Issue: "Module not found: agent_framework"

**Solution:** Install with --pre flag:
```bash
pip install agent-framework-azure-ai --pre
```

### Issue: "Authentication failed"

**Solution:** Check your credentials:
- For Azure OpenAI: Verify `AZURE_OPENAI_API_KEY`
- For Foundry: Ensure `az login` is successful
- Check endpoint URLs are correct

### Issue: "Model deployment not found"

**Solution:** Verify:
1. Model is deployed in your Azure/Foundry project
2. Deployment name matches exactly
3. You have access permissions

## Next Steps

1. **Explore Examples**: Check out `examples/agent_framework_customer_support.py`
2. **Build Your Agent**: Create custom agents in `agents/` directory
3. **Add Tools**: Expand functionality in `tools/` directory
4. **Multi-Agent Orchestration**: See `orchestration/` for workflows
5. **Production Deployment**: Use Docker and CI/CD from the repository

## Resources

- **Repository**: https://github.com/sachidanand/Multi-AI-Agents.git
- [Agent Framework GitHub](https://github.com/microsoft/agent-framework)
- [Microsoft Foundry Documentation](https://learn.microsoft.com/azure/ai-foundry/)
- [Azure OpenAI Documentation](https://learn.microsoft.com/azure/ai-services/openai/)

---

**Multi-AI-Agents Team** | Internal Documentation | 2026
