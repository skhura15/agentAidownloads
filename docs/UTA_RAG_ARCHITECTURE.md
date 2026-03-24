# =============================================================================
# UTA RAG Implementation - Architecture Documentation
# =============================================================================

## Overview

This document describes the RAG (Retrieval-Augmented Generation) implementation
for the Unified Troubleshooting Assistant (UTA).

## Directory Structure

```
Multi-AI-Agents/
├── agents/                         # All agents (shared folder)
│   ├── __init__.py
│   ├── base_agent.py               # Base agent class
│   ├── uta_agent.py                # UTA RAG agent core logic
│   └── uta_support_agent.py        # API wrapper for UTA
│
└── uta/                            # UTA-specific resources
    ├── __init__.py                 # Package initialization
    ├── requirements.txt            # UTA dependencies
    │
    ├── config/                     # Configuration
    │   ├── __init__.py
    │   ├── settings.py             # Configuration loader & dataclasses
    │   ├── config.dev.yaml         # Development config (ChromaDB + Ollama)
    │   └── config.example.yaml     # Full config template with all options
    │
    ├── core/                       # Core components
    │   ├── __init__.py             # Exports all core components
    │   ├── base.py                 # Abstract base class & data models
    │   ├── factory.py              # Factory for creating vector stores
    │   ├── chroma_store.py         # ChromaDB implementation (LOCAL/POC)
    │   ├── cosmos_store.py         # Azure Cosmos DB implementation
    │   ├── azure_search_store.py   # Azure AI Search implementation (PROD)
    │   ├── ollama_client.py        # Ollama LLM client
    │   └── document_loader.py      # Load, chunk, and ingest documents
    │
    ├── docs/                       # Documentation
    │   ├── IMPLEMENTATION_PLAN.md  # Full implementation plan
    │   └── RAG_ARCHITECTURE.md     # This file
    │
    ├── examples/                   # Example scripts
    │   ├── ingest_knowledge.py     # CLI script to run ingestion
    │   └── test_rag_pipeline.py    # Test the complete RAG pipeline
    │
    ├── knowledge/                  # Knowledge base content
    │   ├── sample_sops/            # Standard Operating Procedures
    │   ├── sample_playbooks/       # Troubleshooting playbooks
    │   ├── known_issues/           # Known issues repository
    │   ├── error_codes.json        # Error code definitions
    │   ├── configuration_checks.json # Config validation rules
    │   ├── expert_insights.md      # Tribal knowledge from SMEs
    │   └── sample_tickets.json     # Test tickets for validation
    │
    ├── prompts/                    # Prompt templates
    │   ├── __init__.py
    │   └── rag_prompts.py          # RAG prompt templates
    │
    └── tests/                      # Unit tests
        ├── __init__.py
        └── test_core.py            # Core component tests
```

## Component Details

### 1. Core Module (`core/`)

#### Purpose
Provides a unified interface for vector database operations, allowing seamless
switching between different backends (ChromaDB → Cosmos DB → Azure AI Search).

#### Key Classes

```python
# Base interface - all implementations must follow this
class VectorStore(ABC):
    def initialize(self) -> None
    def add_documents(self, documents: List[Document]) -> List[str]
    def search(self, query: str, top_k: int, filters: Dict) -> List[SearchResult]
    def get_document(self, doc_id: str) -> Optional[Document]
    def delete_document(self, doc_id: str) -> bool
    def clear(self) -> None
    def count(self) -> int

# Document model
@dataclass
class Document:
    id: str                          # Unique identifier
    content: str                     # Text content
    metadata: Dict[str, Any]         # Category, version, source, etc.
    doc_type: DocumentType           # SOP, PLAYBOOK, KNOWN_ISSUE, etc.
    embedding: Optional[List[float]] # Pre-computed embedding (optional)

# Search result model
@dataclass
class SearchResult:
    document: Document
    score: float                     # Relevance score (0-1)
    highlights: Optional[List[str]]  # Highlighted snippets
```

#### Factory Pattern

```python
from uta.vectorstore import VectorStoreFactory

# Create from provider name
store = VectorStoreFactory.create("chroma", {"persist_directory": "./data"})

# Create from environment variables
store = VectorStoreFactory.from_env()

# Create from YAML config
store = VectorStoreFactory.from_yaml_config(config_dict)
```

### 2. Implementations

#### ChromaDB (Development/POC)
- **File:** `chroma_store.py`
- **Use:** Local development, zero cloud dependency
- **Embeddings:** Sentence Transformers (all-MiniLM-L6-v2)
- **Storage:** Local filesystem (./data/chroma)
- **Pros:** Free, instant setup, no credentials needed
- **Cons:** Single-node, not production-grade

#### Cosmos DB (Azure Native)
- **File:** `cosmos_store.py`
- **Use:** Azure deployment before Azure AI Search is ready
- **Embeddings:** Azure OpenAI (text-embedding-ada-002)
- **Storage:** Azure Cosmos DB for NoSQL
- **Pros:** Azure-native, pay-per-use, global distribution
- **Cons:** Requires Azure setup, costs money

#### Azure AI Search (Production)
- **File:** `azure_search_store.py`
- **Use:** Production enterprise deployments
- **Embeddings:** Azure OpenAI (text-embedding-ada-002)
- **Features:** Hybrid search, semantic ranking, faceting
- **Pros:** Enterprise-grade, best search quality
- **Cons:** Requires Azure AI Search service (Basic tier+)

### 3. Document Ingestion (`ingestion/`)

#### Pipeline Flow

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  DocumentLoader │────▶│ DocumentChunker │────▶│  VectorStore    │
│  (Load files)   │     │ (Split content) │     │ (Store vectors) │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

#### Document Types

| Type | Enum Value | Example |
|------|------------|---------|
| SOP | `DocumentType.SOP` | SOP-ROUTING-001.md |
| Playbook | `DocumentType.PLAYBOOK` | PLAYBOOK-MIGRATION-001.md |
| Known Issue | `DocumentType.KNOWN_ISSUE` | KI-2025-1145 |
| Error Code | `DocumentType.ERROR_CODE` | ERR-QUEUE-001 |
| Config Check | `DocumentType.CONFIG_CHECK` | CHK-ROUTING-001 |
| Expert Insight | `DocumentType.EXPERT_INSIGHT` | Tribal knowledge |
| KB Article | `DocumentType.KB_ARTICLE` | General articles |

#### Chunking Strategy

```python
ChunkConfig(
    chunk_size=1000,      # ~1000 characters per chunk
    chunk_overlap=200,    # 200 char overlap for context
    min_chunk_size=100,   # Don't create tiny chunks
)
```

**Special handling:**
- Error codes: One document per error code (not chunked)
- Config checks: One document per check (not chunked)
- SOPs/Playbooks: Chunked by section (## headers)

### 4. Configuration (`config/`)

#### Environment Variables

```bash
# Vector store selection
UTA_VECTOR_PROVIDER=chroma    # or cosmos, azure_search

# ChromaDB
CHROMA_PERSIST_DIR=./data/chroma
CHROMA_COLLECTION=uta_knowledge

# Cosmos DB
COSMOS_ENDPOINT=https://your-account.documents.azure.com:443/
COSMOS_KEY=your-key

# Azure AI Search
AZURE_SEARCH_ENDPOINT=https://your-search.search.windows.net
AZURE_SEARCH_KEY=your-admin-key

# Azure OpenAI (for embeddings)
AZURE_OPENAI_ENDPOINT=https://your-openai.openai.azure.com/
AZURE_OPENAI_API_KEY=your-key
```

#### YAML Configuration

```yaml
vector_store:
  provider: "chroma"  # Switch this to change backends
  
  chroma:
    collection_name: "uta_knowledge"
    persist_directory: "./data/chroma"
    
  cosmos:
    endpoint: "${COSMOS_ENDPOINT}"
    key: "${COSMOS_KEY}"
    
  azure_search:
    endpoint: "${AZURE_SEARCH_ENDPOINT}"
    api_key: "${AZURE_SEARCH_KEY}"
```

## Usage Examples

### Quick Start (Development)

```python
from uta.vectorstore import VectorStoreFactory
from uta.ingestion import KnowledgeBaseIngester

# Create ChromaDB store
store = VectorStoreFactory.create("chroma", {
    "persist_directory": "./data/chroma"
})

# Ingest knowledge base
ingester = KnowledgeBaseIngester(store)
stats = ingester.ingest_directory("./uta/knowledge")
print(f"Ingested {stats['chunks']} chunks from {stats['files']} files")

# Search
results = store.search("calls not routing to agents", top_k=5)
for r in results:
    print(f"[{r.score:.2f}] {r.document.doc_type}: {r.document.id}")
```

### Running Ingestion Script

```bash
# Default (ChromaDB)
python -m uta.scripts.ingest_knowledge

# With options
python -m uta.scripts.ingest_knowledge --provider chroma --clear --log-level DEBUG

# For Cosmos DB (when ready)
python -m uta.scripts.ingest_knowledge --provider cosmos
```

### Switching to Production

```python
# Just change the provider - same code works!
store = VectorStoreFactory.create("azure_search", {
    "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
    "api_key": os.getenv("AZURE_SEARCH_KEY"),
})

# Same search API
results = store.search("license error", top_k=5)
```

## Migration Path

```
Phase 1 (Now)          Phase 2 (Optional)      Phase 3 (Production)
┌──────────────┐       ┌──────────────┐        ┌──────────────┐
│   ChromaDB   │  ──▶  │  Cosmos DB   │  ──▶   │ Azure Search │
│   (Local)    │       │   (Azure)    │        │  (Enterprise)│
└──────────────┘       └──────────────┘        └──────────────┘
     FREE               PAY-PER-USE              BEST QUALITY
```

All migrations require only a config change - no code changes needed!

## Next Steps

1. **Install dependencies:** `pip install -r uta/requirements-rag.txt`
2. **Run ingestion:** `python -m uta.scripts.ingest_knowledge`
3. **Build UTA Agent:** Create agents that use the vector store for RAG
4. **Add API endpoints:** Expose search via REST API
5. **Build UI:** Create frontend for ticket analysis
