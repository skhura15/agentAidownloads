"""
RAG Service - Standalone Microservice

This package contains the standalone RAG (Retrieval-Augmented Generation) service
designed for Kubernetes deployment.

The service exposes REST/gRPC APIs for:
- Document search and retrieval
- Context building for LLM prompts
- Full RAG generation (search + LLM)
- Document ingestion and indexing

Usage:
    # Run as standalone service
    uvicorn rag_service.app:app --host 0.0.0.0 --port 8001
    
    # Or with Docker
    docker build -f rag_service/Dockerfile -t rag-service:latest .
    docker run -p 8001:8001 rag-service:latest
"""

from rag_service.app import app
from rag_service.client import RAGServiceClient
from rag_service.models import (
    SearchRequest,
    SearchResponse,
    ContextRequest,
    ContextResponse,
    GenerateRequest,
    GenerateResponse,
    IngestRequest,
    IngestResponse,
    HealthResponse,
)

__all__ = [
    "app",
    "RAGServiceClient",
    "SearchRequest",
    "SearchResponse", 
    "ContextRequest",
    "ContextResponse",
    "GenerateRequest",
    "GenerateResponse",
    "IngestRequest",
    "IngestResponse",
    "HealthResponse",
]
