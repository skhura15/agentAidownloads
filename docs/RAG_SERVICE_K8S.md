# RAG Service - Standalone Microservice Architecture

This document describes how to deploy the RAG (Retrieval-Augmented Generation) functionality as a standalone Kubernetes service.

## Overview

The RAG service is extracted from the UTA Agent into an independent microservice that provides:
- **Knowledge base search** (semantic + keyword + query expansion)
- **Context building** for LLM prompts
- **RAG-augmented generation** (search + LLM)
- **Document ingestion** for knowledge base updates

## Architecture Comparison

### Before: Embedded RAG
```
┌─────────────────────────────────────────────────┐
│                   UTA Agent                      │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │
│  │ RAG Service │  │ Vector Store│  │   LLM    │ │
│  │   (local)   │  │  (ChromaDB) │  │ (Ollama) │ │
│  └─────────────┘  └─────────────┘  └──────────┘ │
└─────────────────────────────────────────────────┘
```

### After: Standalone RAG Service
```
┌────────────────────────┐      ┌─────────────────────────────────┐
│      Agent Pod         │      │       RAG Service Pod           │
│  ┌──────────────────┐  │      │  ┌─────────────────────────────┐│
│  │   UTA Agent K8s  │──┼──────┼──│      RAG Service API        ││
│  │  (RAG Client)    │  │ HTTP │  │  ┌───────────┐ ┌──────────┐ ││
│  └──────────────────┘  │      │  │  │VectorStore│ │   LLM    │ ││
└────────────────────────┘      │  │  │(ChromaDB) │ │(Azure/   │ ││
                                │  │  │           │ │ Ollama)  │ ││
┌────────────────────────┐      │  │  └───────────┘ └──────────┘ ││
│    Other Agent Pods    │──────┼──│                             ││
└────────────────────────┘      │  └─────────────────────────────┘│
                                └─────────────────────────────────┘
```

## Pros and Cons

### ✅ Pros

| Benefit | Description |
|---------|-------------|
| **Independent Scaling** | Scale RAG pods based on embedding/search load separately from agent pods |
| **Resource Isolation** | GPU/memory-intensive embedding operations don't compete with agent logic |
| **Shared Knowledge Base** | Multiple agents share the same indexed knowledge without duplication |
| **Easier Updates** | Update RAG models/indexes without redeploying agents |
| **Multi-tenant Support** | Easier to implement tenant isolation and rate limiting |
| **Specialized Infrastructure** | RAG service can run on GPU nodes; agents on CPU nodes |
| **Caching Benefits** | Centralized caching for embeddings and search results |
| **Observability** | Dedicated metrics, tracing, and logging for RAG operations |
| **Technology Flexibility** | Can swap vector stores (Chroma → Qdrant → Azure AI Search) without agent changes |

### ❌ Cons

| Drawback | Description |
|----------|-------------|
| **Network Latency** | Additional HTTP hop adds ~5-50ms per RAG request |
| **Operational Complexity** | More services to deploy, monitor, and maintain |
| **Failure Modes** | RAG service outage affects all dependent agents |
| **Data Consistency** | Need to handle vector store synchronization across replicas |
| **Cost** | Additional infrastructure and load balancer costs |
| **Cold Start** | Embedding models may need warm-up time |
| **Debugging Complexity** | Distributed tracing required for end-to-end debugging |

## When This Architecture Makes Sense

✅ **Good fit when:**
- Multiple agents need access to the same knowledge base
- RAG and agent workloads have different scaling profiles
- You need to update knowledge independently of agent code
- Running in Kubernetes with proper service mesh

❌ **Not ideal when:**
- Single agent deployment
- Low latency is critical (<10ms response time)
- Simple deployment without Kubernetes
- Development/testing environments

## Quick Start

### 1. Build the RAG Service Image

```bash
docker build -f rag_service/Dockerfile -t rag-service:latest .
```

### 2. Deploy to Kubernetes

```bash
# Create secrets for Azure AI Foundry (if using)
kubectl create secret generic rag-service-secrets \
  --from-literal=foundry_endpoint="https://your-endpoint.openai.azure.com" \
  --from-literal=foundry_api_key="your-api-key"

# Deploy
kubectl apply -f rag_service/kubernetes/deployment.yaml
```

### 3. Configure Agents to Use Remote RAG

Set the `RAG_SERVICE_URL` environment variable:

```yaml
env:
  - name: RAG_SERVICE_URL
    value: "http://rag-service:8001"
```

Or use the Kubernetes-ready agent:

```python
from agents.uta_agent_k8s import UTAAgentK8s

agent = UTAAgentK8s(rag_service_url="http://rag-service:8001")
await agent.initialize()
```

### 4. Run Locally (Development)

```bash
# Start RAG service
uvicorn rag_service.app:app --host 0.0.0.0 --port 8001

# In another terminal, run agent
export RAG_SERVICE_URL=http://localhost:8001
python -m api.main
```

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Comprehensive health check |
| `/ready` | GET | Kubernetes readiness probe |
| `/live` | GET | Kubernetes liveness probe |
| `/search` | POST | Search knowledge base |
| `/context` | POST | Build RAG context |
| `/generate` | POST | RAG-augmented generation |
| `/ingest` | POST | Ingest documents |
| `/metrics` | GET | Prometheus metrics |

## Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `RAG_SERVICE_HOST` | `0.0.0.0` | Service host |
| `RAG_SERVICE_PORT` | `8001` | Service port |
| `VECTOR_PROVIDER` | `chroma` | Vector store provider |
| `VECTOR_COLLECTION` | `uta_knowledge` | Collection name |
| `VECTOR_PERSIST_DIR` | `./data/chroma` | Data directory |
| `USE_FOUNDRY` | `false` | Use Azure AI Foundry |
| `FOUNDRY_PROJECT_ENDPOINT` | - | Foundry endpoint |
| `FOUNDRY_API_KEY` | - | Foundry API key |
| `RAG_TOP_K` | `5` | Default search results |
| `RAG_MIN_SCORE` | `0.05` | Minimum relevance score |

## Files Structure

```
rag_service/
├── __init__.py          # Package exports
├── app.py               # FastAPI application
├── models.py            # Pydantic models
├── client.py            # HTTP client for agents
├── Dockerfile           # Container image
└── kubernetes/
    └── deployment.yaml  # K8s manifests
```

## Migration Guide

### Updating Existing Agents

Replace `UTAAgent` with `UTAAgentK8s`:

```python
# Before
from agents.uta_agent import UTAAgent
agent = UTAAgent()

# After
from agents.uta_agent_k8s import UTAAgentK8s
agent = UTAAgentK8s(rag_service_url="http://rag-service:8001")
```

The `UTAAgentK8s` automatically falls back to local RAG if the remote service is unavailable.

## Monitoring

The service exposes Prometheus metrics at `/metrics`:

- `rag_service_uptime_seconds` - Service uptime
- `rag_service_document_count` - Documents indexed
- `rag_service_searches_total` - Total search requests
- `rag_service_generations_total` - Total generations
- `rag_service_search_latency_ms` - Search latency

## Best Practices

1. **Use connection pooling** - The client uses `httpx` with connection pooling
2. **Implement circuit breakers** - Client has built-in circuit breaker
3. **Add Redis caching** - Cache frequent queries to reduce latency
4. **Use gRPC for lower latency** - Consider gRPC instead of REST for production
5. **Enable distributed tracing** - Add OpenTelemetry for end-to-end visibility
6. **Set proper resource limits** - Embedding operations are memory-intensive
