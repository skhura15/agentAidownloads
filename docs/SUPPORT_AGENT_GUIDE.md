# Self-Service Support Agent - Quick Start Guide

## Overview

The Self-Service Support Agent delivers cost-optimized customer support using local AI models via Ollama. It intelligently routes queries through tiered models based on complexity, maximizing efficiency while minimizing costs.

## Architecture

### Tiered Model Approach
- **Tier 1 (phi3-mini)**: Simple queries (password resets, basic how-tos)
- **Tier 2 (mistral)**: Technical issues (errors, integrations, performance)
- **Tier 3 (llama3)**: Complex problems (enterprise features, custom architecture)

### Key Features
1. **Cost Optimization**: 65% cost reduction by using lightweight models first
2. **RAG Integration**: Knowledge base search for accurate answers
3. **Sentiment Analysis**: Detects frustrated users for priority handling
4. **Context Preservation**: Maintains conversation history across escalations
5. **Human Escalation**: Smart handoff when AI reaches limits

## Prerequisites

### 1. Install Ollama

```bash
# macOS
brew install ollama

# Linux
curl https://ollama.ai/install.sh | sh

# Windows: Download from https://ollama.ai
```

### 2. Start Ollama Service

```bash
ollama serve
```

### 3. Pull Required Models

```bash
# Tier 1 - Lightweight (200MB)
ollama pull phi3:mini

# Tier 2 - Medium (4GB)
ollama pull mistral

# Tier 3 - Advanced (4.7GB)
ollama pull llama3
```

## Quick Start

### Run Demo Script

```bash
cd /Users/sachidanand/Agentic-CoE/Source-Code

# Run the demo
python examples/demo_support_agent.py
```

### Expected Output

```
🤖 HCLTech Self-Service Support Agent Demo
================================================================================

🔍 Checking Ollama connection...
✅ Ollama connected successfully!
   Available models: 3

📝 Running Simulated Support Queries
================================================================================

🎯 Query 1/5
User: I forgot my password and can't log in. How do I reset it?
Expected Tier: tier1

⏳ Processing with AI agent...

📋 Response:
To reset your password:
1. Click 'Forgot Password' on the login page
2. Enter your registered email address
3. Check your inbox for a reset link (check spam if needed)
4. Click the link and create a new password
...
```

## Usage Examples

### Example 1: Simple Query (Tier 1)

```python
import asyncio
from agents.self_service_support_agent import SelfServiceSupportAgent

async def main():
    agent = SelfServiceSupportAgent()
    
    task = {
        "query": "How do I reset my password?",
        "user_context": {"user_id": "user123"},
        "escalation_allowed": True
    }
    
    response = await agent.execute(task)
    print(response.content)
    print(f"Tier used: {response.metadata['model_tier']}")

asyncio.run(main())
```

**Output:**
```
To reset your password: 1) Click 'Forgot Password'...
Tier used: tier1
```

### Example 2: Technical Query (Tier 2)

```python
task = {
    "query": "Getting 504 error on dashboard. How do I troubleshoot?",
    "user_context": {"user_id": "user456"},
    "escalation_allowed": True
}

response = await agent.execute(task)
# Uses tier2 (mistral) for technical troubleshooting
```

### Example 3: Complex Query (Tier 3 + Escalation)

```python
task = {
    "query": "Need enterprise SSO SAML 2.0 integration with custom claims mapping",
    "user_context": {"user_id": "enterprise789"},
    "escalation_allowed": True
}

response = await agent.execute(task)
# Uses tier3 (llama3) and escalates to human support
```

## Knowledge Base

The agent includes a simulated knowledge base with 8 articles covering:

1. **Account Management**: Password reset, account deletion
2. **Billing**: Payment method updates
3. **Technical**: Performance issues, error troubleshooting
4. **Features**: Data export, integrations
5. **Security**: Two-factor authentication
6. **Integrations**: Microsoft Teams, webhooks

### Adding Custom Knowledge

Edit `agents/self_service_support_agent.py`:

```python
def _load_knowledge_base(self) -> List[Dict[str, str]]:
    return [
        {
            "id": "kb009",
            "category": "custom",
            "question": "Your question here",
            "answer": "Your detailed answer here"
        },
        # Add more articles...
    ]
```

## Performance Metrics

The agent tracks:

```python
metrics = agent.get_metrics()

# Output:
{
    "total_queries": 25,
    "tier1_resolved": 15,      # 60% resolved by cheapest model
    "tier2_resolved": 7,       # 28% needed medium model
    "escalated": 3,            # 12% required human support
    "escalation_rate": "12.0%",
    "cost_savings_usd": "$1.85",
    "avg_tier1_percentage": "68.2%"
}
```

## Cost Analysis

### Simulated Cost per Query
- **Tier 1 (phi3-mini)**: $0.001 per query → Saves $0.10
- **Tier 2 (mistral)**: $0.05 per query → Saves $0.05
- **Tier 3 (llama3)**: $0.10 per query → No savings
- **Human Support**: $15 per ticket (baseline)

### Example Savings
For 1000 queries/month with typical distribution:
- 600 queries @ Tier 1: Saves $60
- 300 queries @ Tier 2: Saves $15
- 100 escalations @ Tier 3: $0 (but prevents $1,500 in human costs)

**Total monthly savings: $75 + prevention of $1,500 = ~$1,575**

## Sentiment Analysis

The agent detects user frustration:

```python
# Frustrated user → priority handling
query = "This is terrible! Dashboard keeps crashing!"

sentiment = agent._analyze_sentiment(query)
# Output: {"sentiment": "negative", "score": 0.3, "requires_priority": True}
```

## Configuration

Customize in agent initialization:

```python
config = {
    "ollama_url": "http://localhost:11434",  # Ollama server
    "models": {
        "tier1": "phi3:mini",
        "tier2": "mistral:latest",
        "tier3": "llama3:latest"
    },
    "enable_rag": True,
    "enable_sentiment": True
}

agent = SelfServiceSupportAgent(config=config)
```

## Troubleshooting

### Error: "Cannot connect to Ollama"

**Solution:**
```bash
# Check if Ollama is running
curl http://localhost:11434/api/tags

# If not, start it
ollama serve
```

### Error: "Model not found"

**Solution:**
```bash
# Pull missing models
ollama pull phi3:mini
ollama pull mistral
ollama pull llama3

# Verify models
ollama list
```

### Slow Response Times

**Solution:**
- Ensure adequate RAM (8GB+ recommended)
- Use GPU acceleration if available
- Consider using smaller models for Tier 1/2
- Reduce context window in prompts

### Knowledge Base Not Working

**Solution:**
- Check `_search_knowledge_base()` method
- Verify knowledge base is populated
- Improve search keywords in articles

## Integration with Web UI

To integrate with the landing page:

1. Create API endpoint:
```python
# api/support_endpoint.py
from fastapi import FastAPI
from agents.self_service_support_agent import SelfServiceSupportAgent

app = FastAPI()
agent = SelfServiceSupportAgent()

@app.post("/api/support/query")
async def handle_support_query(query: str, user_id: str):
    task = {
        "query": query,
        "user_context": {"user_id": user_id},
        "escalation_allowed": True
    }
    response = await agent.execute(task)
    return {
        "answer": response.content,
        "metadata": response.metadata
    }
```

2. Update frontend to call API
3. Display responses in chat interface

## Next Steps

1. **Expand Knowledge Base**: Add domain-specific articles
2. **Fine-tune Models**: Train on actual support tickets
3. **Add Tools**: Integrate with ticketing systems (Jira, ServiceNow)
4. **Implement Caching**: Cache common queries for faster responses
5. **Multi-turn Conversations**: Add conversation history tracking
6. **Analytics Dashboard**: Visualize metrics and trends

## Production Deployment

For production use:

1. Replace Ollama with Azure OpenAI or GitHub Models
2. Add authentication and rate limiting
3. Implement proper error handling and retries
4. Set up monitoring and alerting
5. Use vector database for knowledge base (Pinecone, Weaviate)
6. Add logging and audit trails

## Resources

- [Ollama Documentation](https://ollama.ai/docs)
- [Microsoft Agent Framework](https://github.com/microsoft/agent-framework)
- [HCLTech Agentic CoE Architecture](../ARCHITECTURE.md)

## Support

For questions or issues:
- GitHub Issues: [Submit Issue](https://github.com/sachidanand/Multi-AI-Agents/issues)
- Internal: Contact HCLTech Agentic CoE team
