"""
Core Package

This package contains core reusable components for the Agentic CoE system.
"""

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from core.state_manager import StateManager
from core.azure_openai_client import AzureOpenAIClient

# UTA Core Components
from core.uta_vectorstore_base import (
    VectorStore,
    Document,
    DocumentType,
    SearchResult,
)
from core.uta_vectorstore_factory import VectorStoreFactory
from core.uta_chroma_store import ChromaVectorStore
from core.uta_ollama_client import OllamaClient, GenerationConfig
from core.uta_document_loader import (
    DocumentLoader,
    DocumentChunker,
    ChunkConfig,
    KnowledgeBaseIngester,
)

# RAG Service Components
from core.rag_types import (
    RAGContext,
    RAGConfig,
    RAGRequest,
    RAGResponse,
    ContextFormatter,
)
from core.rag_service import RAGService, create_rag_service

__all__ = [
    # Base components
    "ConfigManager",
    "LoggingService",
    "StateManager",
    "AzureOpenAIClient",
    # UTA Vector Store
    "VectorStore",
    "Document",
    "DocumentType",
    "SearchResult",
    "VectorStoreFactory",
    "ChromaVectorStore",
    # UTA LLM
    "OllamaClient",
    "GenerationConfig",
    # UTA Ingestion
    "DocumentLoader",
    "DocumentChunker",
    "ChunkConfig",
    "KnowledgeBaseIngester",
    # RAG Service
    "RAGContext",
    "RAGConfig",
    "RAGRequest",
    "RAGResponse",
    "ContextFormatter",
    "RAGService",
    "create_rag_service",
]
