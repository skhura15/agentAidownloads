"""
RAG Service - FastAPI Application

Standalone microservice for RAG (Retrieval-Augmented Generation) operations.
Designed for Kubernetes deployment with proper health checks and observability.

Run with:
    uvicorn rag_service.app:app --host 0.0.0.0 --port 8001
"""

# Load .env file FIRST before any other imports
from dotenv import load_dotenv
load_dotenv(override=True)

import os
import time
import logging
from datetime import datetime
from typing import Optional, List
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Depends, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import asyncio

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
    ReadinessResponse,
    LivenessResponse,
    DocumentResult,
    ComponentStatus,
    ServiceMetrics,
    DocumentTypeEnum,
)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("rag-service")

# Service state
_start_time = datetime.utcnow()
_rag_service = None
_vector_store = None
_llm_client = None
_metrics = {
    "total_searches": 0,
    "total_generations": 0,
    "avg_search_latency_ms": 0.0,
    "avg_generation_latency_ms": 0.0,
    "cache_hits": 0,
}


# =============================================================================
# Application Lifecycle
# =============================================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager - startup and shutdown."""
    global _rag_service, _vector_store, _llm_client
    
    logger.info("Starting RAG Service...")
    
    try:
        # Load environment
        from dotenv import load_dotenv
        load_dotenv()
    except ImportError:
        pass
    
    # Initialize components
    try:
        await initialize_components()
        logger.info("RAG Service initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG Service: {e}")
        # Continue anyway - health checks will report unhealthy
    
    yield
    
    # Shutdown
    logger.info("Shutting down RAG Service...")
    if _vector_store and hasattr(_vector_store, 'close'):
        _vector_store.close()


async def initialize_components():
    """Initialize RAG service components."""
    global _rag_service, _vector_store, _llm_client
    
    from core import VectorStoreFactory
    from core.rag_service import RAGService
    from core.rag_types import RAGConfig
    
    # Determine embedding provider
    use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
    foundry_endpoint = os.getenv("FOUNDRY_PROJECT_ENDPOINT")
    foundry_api_key = os.getenv("FOUNDRY_API_KEY")
    
    # Vector store configuration
    if use_foundry and foundry_endpoint:
        logger.info("Using Azure AI Foundry for embeddings")
        vector_config = {
            "collection_name": os.getenv("VECTOR_COLLECTION", "uta_knowledge_azure"),
            "persist_directory": os.getenv("VECTOR_PERSIST_DIR", "./data/chroma_azure"),
            "embedding_provider": "azure_openai",
            "embedding_model": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
            "azure_openai_endpoint": foundry_endpoint,
            "azure_openai_key": foundry_api_key,
            "use_foundry": True,
        }
    else:
        logger.info("Using Ollama for embeddings")
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        vector_config = {
            "collection_name": os.getenv("VECTOR_COLLECTION", "uta_knowledge"),
            "persist_directory": os.getenv("VECTOR_PERSIST_DIR", "./data/chroma"),
            "embedding_provider": "ollama",
            "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
            "ollama_base_url": ollama_url,
        }
    
    # Create vector store
    _vector_store = VectorStoreFactory.create(
        provider=os.getenv("VECTOR_PROVIDER", "chroma"),
        config=vector_config,
    )
    
    doc_count = _vector_store.count()
    logger.info(f"Vector store initialized with {doc_count} documents")
    
    # LLM client configuration
    if use_foundry and foundry_endpoint:
        from core.uta_azure_openai_llm import AzureOpenAIClient
        from core.uta_azure_openai_llm import GenerationConfig as AzureGenConfig
        
        _llm_client = AzureOpenAIClient(
            model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o"),
            endpoint=foundry_endpoint,
            api_key=foundry_api_key,
            config=AzureGenConfig(
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")),
            ),
            use_foundry=True,
        )
        logger.info(f"LLM initialized with Azure AI Foundry")
    else:
        from core.uta_ollama_client import OllamaClient, GenerationConfig
        
        _llm_client = OllamaClient(
            model=os.getenv("OLLAMA_LLM_MODEL", "llama3.1:8b-instruct-q8_0"),
            base_url=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            config=GenerationConfig(
                temperature=float(os.getenv("LLM_TEMPERATURE", "0.7")),
                max_tokens=int(os.getenv("LLM_MAX_TOKENS", "2048")),
            ),
        )
        logger.info("LLM initialized with Ollama")
    
    # Create RAG service
    _rag_service = RAGService(
        vector_store=_vector_store,
        llm_client=_llm_client,
        config=RAGConfig(
            top_k=int(os.getenv("RAG_TOP_K", "5")),
            min_score=float(os.getenv("RAG_MIN_SCORE", "0.05")),
            use_query_expansion=os.getenv("RAG_QUERY_EXPANSION", "true").lower() == "true",
        ),
    )
    logger.info("RAG Service initialized successfully")


# =============================================================================
# FastAPI Application
# =============================================================================

app = FastAPI(
    title="RAG Service",
    description="Standalone RAG (Retrieval-Augmented Generation) microservice for knowledge retrieval and augmented generation",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=os.getenv("CORS_ORIGINS", "*").split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =============================================================================
# Health Check Endpoints (Kubernetes probes)
# =============================================================================

@app.get("/health", response_model=HealthResponse, tags=["Health"])
async def health_check():
    """
    Comprehensive health check with component status.
    Use for monitoring dashboards and alerts.
    """
    components = []
    overall_status = "healthy"
    
    # Check vector store
    vs_status = "healthy"
    vs_message = None
    if _vector_store:
        try:
            count = _vector_store.count()
            vs_message = f"{count} documents indexed"
        except Exception as e:
            vs_status = "unhealthy"
            vs_message = str(e)
            overall_status = "degraded"
    else:
        vs_status = "unhealthy"
        vs_message = "Vector store not initialized"
        overall_status = "unhealthy"
    
    components.append(ComponentStatus(
        name="vector_store",
        status=vs_status,
        message=vs_message,
    ))
    
    # Check LLM client
    llm_status = "healthy" if _llm_client else "unhealthy"
    llm_message = "LLM client ready" if _llm_client else "LLM client not initialized"
    if not _llm_client:
        overall_status = "degraded" if overall_status == "healthy" else overall_status
    
    components.append(ComponentStatus(
        name="llm_client",
        status=llm_status,
        message=llm_message,
    ))
    
    # Check RAG service
    rag_status = "healthy" if _rag_service and _rag_service.is_ready else "unhealthy"
    components.append(ComponentStatus(
        name="rag_service",
        status=rag_status,
    ))
    
    uptime = (datetime.utcnow() - _start_time).total_seconds()
    
    return HealthResponse(
        status=overall_status,
        version="1.0.0",
        timestamp=datetime.utcnow(),
        components=components,
        metrics=ServiceMetrics(
            total_searches=_metrics["total_searches"],
            total_generations=_metrics["total_generations"],
            avg_search_latency_ms=_metrics["avg_search_latency_ms"],
            avg_generation_latency_ms=_metrics["avg_generation_latency_ms"],
            document_count=_vector_store.count() if _vector_store else 0,
            uptime_seconds=uptime,
        ),
    )


@app.get("/ready", response_model=ReadinessResponse, tags=["Health"])
async def readiness_check():
    """
    Kubernetes readiness probe.
    Returns 200 if service is ready to accept traffic.
    """
    vector_ready = _vector_store is not None
    llm_ready = _llm_client is not None
    ready = vector_ready  # LLM is optional for search-only operations
    
    if not ready:
        raise HTTPException(status_code=503, detail="Service not ready")
    
    return ReadinessResponse(
        ready=ready,
        vector_store_ready=vector_ready,
        llm_ready=llm_ready,
        message="Service is ready" if ready else "Service not ready",
    )


@app.get("/live", response_model=LivenessResponse, tags=["Health"])
async def liveness_check():
    """
    Kubernetes liveness probe.
    Returns 200 if service is alive.
    """
    uptime = (datetime.utcnow() - _start_time).total_seconds()
    return LivenessResponse(
        alive=True,
        uptime_seconds=uptime,
    )


# =============================================================================
# Search Endpoints
# =============================================================================

@app.post("/search", response_model=SearchResponse, tags=["Search"])
async def search_knowledge(request: SearchRequest):
    """
    Search the knowledge base for relevant documents.
    
    Uses semantic search with optional query expansion for better recall.
    """
    if not _rag_service or not _rag_service.is_ready:
        raise HTTPException(status_code=503, detail="RAG service not ready")
    
    start_time = time.time()
    
    # Convert doc types
    doc_types = None
    if request.doc_types:
        from core.uta_vectorstore_base import DocumentType
        doc_types = [DocumentType(dt.value) for dt in request.doc_types]
    
    # Execute search
    try:
        results = _rag_service.search(
            query=request.query,
            doc_types=doc_types,
            top_k=request.top_k,
            min_score=request.min_score,
            use_query_expansion=request.use_query_expansion,
            filters=request.filters,
        )
    except Exception as e:
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail=f"Search failed: {str(e)}")
    
    elapsed_ms = (time.time() - start_time) * 1000
    _update_metrics("search", elapsed_ms)
    
    return SearchResponse(
        query=request.query,
        results=[
            DocumentResult(
                id=r.document.id,
                content=r.document.content,
                doc_type=r.document.doc_type.value,
                score=r.score,
                metadata=r.document.metadata,
            )
            for r in results
        ],
        total_found=len(results),
        search_time_ms=round(elapsed_ms, 2),
    )


# =============================================================================
# Context Building Endpoints
# =============================================================================

@app.post("/context", response_model=ContextResponse, tags=["Context"])
async def build_context(request: ContextRequest):
    """
    Build formatted RAG context from search results.
    
    Returns pre-formatted context string ready for LLM prompt insertion.
    """
    if not _rag_service or not _rag_service.is_ready:
        raise HTTPException(status_code=503, detail="RAG service not ready")
    
    start_time = time.time()
    
    # Convert doc types
    doc_types = None
    if request.doc_types:
        from core.uta_vectorstore_base import DocumentType
        doc_types = [DocumentType(dt.value) for dt in request.doc_types]
    
    try:
        context = _rag_service.build_context(
            query=request.query,
            doc_types=doc_types,
            top_k=request.top_k,
            min_score=request.min_score,
            format_style=request.format_style,
        )
    except Exception as e:
        logger.error(f"Context building error: {e}")
        raise HTTPException(status_code=500, detail=f"Context building failed: {str(e)}")
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    return ContextResponse(
        query=request.query,
        formatted_context=context.formatted_context,
        document_count=context.document_count,
        doc_types_found=context.doc_types_found,
        top_doc_ids=context.get_top_doc_ids(3),
        has_context=context.has_context,
        build_time_ms=round(elapsed_ms, 2),
    )


# =============================================================================
# Generation Endpoints
# =============================================================================

@app.post("/generate", response_model=GenerateResponse, tags=["Generation"])
async def generate_with_rag(request: GenerateRequest):
    """
    Generate response using RAG (search + LLM).
    
    Retrieves relevant documents and uses them as context for LLM generation.
    """
    if not _rag_service:
        raise HTTPException(status_code=503, detail="RAG service not ready")
    
    if not _rag_service.can_generate:
        raise HTTPException(status_code=503, detail="LLM client not configured")
    
    total_start = time.time()
    
    # Convert doc types
    doc_types = None
    if request.doc_types:
        from core.uta_vectorstore_base import DocumentType
        doc_types = [DocumentType(dt.value) for dt in request.doc_types]
    
    # Build context
    search_start = time.time()
    context = _rag_service.build_context(
        query=request.query,
        doc_types=doc_types,
        top_k=request.top_k,
        min_score=request.min_score,
    )
    search_time = (time.time() - search_start) * 1000
    
    # Generate response
    gen_start = time.time()
    try:
        from core.rag_types import RAGRequest
        
        rag_request = RAGRequest(
            query=request.query,
            system_prompt=request.system_prompt,
            user_prompt_template=request.user_prompt_template,
            doc_types=doc_types,
        )
        
        rag_response = _rag_service.generate(
            query=request.query,
            system_prompt=request.system_prompt,
        )
        response_text = rag_response.content if hasattr(rag_response, 'content') else str(rag_response)
        
    except Exception as e:
        logger.error(f"Generation error: {e}")
        raise HTTPException(status_code=500, detail=f"Generation failed: {str(e)}")
    
    gen_time = (time.time() - gen_start) * 1000
    total_time = (time.time() - total_start) * 1000
    
    _update_metrics("generation", total_time)
    
    return GenerateResponse(
        query=request.query,
        response=response_text,
        sources=[
            DocumentResult(
                id=r.document.id,
                content=r.document.content[:500] + "..." if len(r.document.content) > 500 else r.document.content,
                doc_type=r.document.doc_type.value,
                score=r.score,
                metadata=r.document.metadata,
            )
            for r in context.documents[:5]
        ],
        context_used=context.formatted_context[:1000] if len(context.formatted_context) > 1000 else context.formatted_context,
        generation_time_ms=round(gen_time, 2),
        search_time_ms=round(search_time, 2),
        total_time_ms=round(total_time, 2),
        model=os.getenv("FOUNDRY_MODEL_DEPLOYMENT", os.getenv("OLLAMA_LLM_MODEL", "unknown")),
    )


# =============================================================================
# Document Ingestion Endpoints
# =============================================================================

@app.post("/ingest", response_model=IngestResponse, tags=["Ingestion"])
async def ingest_documents(request: IngestRequest):
    """
    Ingest documents into the knowledge base.
    
    Documents will be embedded and stored in the vector store.
    """
    if not _vector_store:
        raise HTTPException(status_code=503, detail="Vector store not ready")
    
    start_time = time.time()
    
    from core.uta_vectorstore_base import Document, DocumentType
    
    ingested = 0
    failed = []
    
    for doc_input in request.documents:
        try:
            doc = Document(
                id=doc_input.id,
                content=doc_input.content,
                doc_type=DocumentType(doc_input.doc_type.value),
                metadata=doc_input.metadata,
            )
            
            if request.upsert:
                _vector_store.upsert([doc])
            else:
                _vector_store.add([doc])
            
            ingested += 1
            
        except Exception as e:
            logger.error(f"Failed to ingest document {doc_input.id}: {e}")
            failed.append(doc_input.id)
    
    elapsed_ms = (time.time() - start_time) * 1000
    
    return IngestResponse(
        ingested_count=ingested,
        failed_count=len(failed),
        failed_ids=failed,
        collection=request.collection,
        total_documents=_vector_store.count(),
        ingest_time_ms=round(elapsed_ms, 2),
    )


# =============================================================================
# Metrics Endpoints
# =============================================================================

@app.get("/metrics", tags=["Metrics"])
async def get_metrics():
    """
    Get service metrics in Prometheus format.
    """
    uptime = (datetime.utcnow() - _start_time).total_seconds()
    doc_count = _vector_store.count() if _vector_store else 0
    
    # Prometheus format
    lines = [
        f"# HELP rag_service_uptime_seconds Service uptime in seconds",
        f"# TYPE rag_service_uptime_seconds gauge",
        f"rag_service_uptime_seconds {uptime}",
        f"",
        f"# HELP rag_service_document_count Total documents in vector store",
        f"# TYPE rag_service_document_count gauge",
        f"rag_service_document_count {doc_count}",
        f"",
        f"# HELP rag_service_searches_total Total search requests",
        f"# TYPE rag_service_searches_total counter",
        f"rag_service_searches_total {_metrics['total_searches']}",
        f"",
        f"# HELP rag_service_generations_total Total generation requests",
        f"# TYPE rag_service_generations_total counter",
        f"rag_service_generations_total {_metrics['total_generations']}",
        f"",
        f"# HELP rag_service_search_latency_ms Average search latency",
        f"# TYPE rag_service_search_latency_ms gauge",
        f"rag_service_search_latency_ms {_metrics['avg_search_latency_ms']}",
    ]
    
    return "\n".join(lines)


# =============================================================================
# Helper Functions
# =============================================================================

def _update_metrics(operation: str, latency_ms: float):
    """Update service metrics."""
    if operation == "search":
        _metrics["total_searches"] += 1
        count = _metrics["total_searches"]
        avg = _metrics["avg_search_latency_ms"]
        _metrics["avg_search_latency_ms"] = ((avg * (count - 1)) + latency_ms) / count
    elif operation == "generation":
        _metrics["total_generations"] += 1
        count = _metrics["total_generations"]
        avg = _metrics["avg_generation_latency_ms"]
        _metrics["avg_generation_latency_ms"] = ((avg * (count - 1)) + latency_ms) / count


# =============================================================================
# Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    uvicorn.run(
        "rag_service.app:app",
        host=os.getenv("RAG_SERVICE_HOST", "0.0.0.0"),
        port=int(os.getenv("RAG_SERVICE_PORT", "8001")),
        reload=os.getenv("RAG_SERVICE_RELOAD", "false").lower() == "true",
        workers=int(os.getenv("RAG_SERVICE_WORKERS", "1")),
    )
