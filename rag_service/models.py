"""
RAG Service API Models

Pydantic models for the RAG Service REST API.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from enum import Enum
from datetime import datetime


# =============================================================================
# Enums
# =============================================================================

class DocumentTypeEnum(str, Enum):
    """Document types in the knowledge base."""
    SOP = "sop"
    PLAYBOOK = "playbook"
    KNOWN_ISSUE = "known_issue"
    TROUBLESHOOTING = "troubleshooting"
    REFERENCE = "reference"
    CONFIG_CHECK = "config_check"
    FAQ = "faq"
    GENERAL = "general"


# =============================================================================
# Common Models
# =============================================================================

class DocumentResult(BaseModel):
    """A single document from search results."""
    id: str
    content: str
    doc_type: str
    score: float
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ServiceMetrics(BaseModel):
    """Service health and performance metrics."""
    total_searches: int = 0
    total_generations: int = 0
    avg_search_latency_ms: float = 0.0
    avg_generation_latency_ms: float = 0.0
    cache_hit_rate: float = 0.0
    document_count: int = 0
    uptime_seconds: float = 0.0


# =============================================================================
# Search API Models
# =============================================================================

class SearchRequest(BaseModel):
    """Request for knowledge base search."""
    query: str = Field(..., description="Search query text")
    top_k: int = Field(default=5, ge=1, le=50, description="Number of results to return")
    min_score: float = Field(default=0.05, ge=0.0, le=1.0, description="Minimum relevance score")
    doc_types: Optional[List[DocumentTypeEnum]] = Field(
        default=None, 
        description="Filter by document types"
    )
    use_query_expansion: bool = Field(
        default=True, 
        description="Expand query for better recall"
    )
    filters: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Additional metadata filters"
    )
    tenant_id: Optional[str] = Field(
        default=None,
        description="Tenant ID for multi-tenant isolation"
    )


class SearchResponse(BaseModel):
    """Response from knowledge base search."""
    query: str
    results: List[DocumentResult]
    total_found: int
    search_time_ms: float
    expanded_queries: Optional[List[str]] = None


# =============================================================================
# Context Building API Models
# =============================================================================

class ContextRequest(BaseModel):
    """Request to build RAG context from search results."""
    query: str = Field(..., description="Query to build context for")
    top_k: int = Field(default=5, ge=1, le=50)
    min_score: float = Field(default=0.05, ge=0.0, le=1.0)
    doc_types: Optional[List[DocumentTypeEnum]] = None
    format_style: str = Field(
        default="default", 
        description="Context format: default, compact, markdown"
    )
    include_scores: bool = Field(default=True)
    include_doc_types: bool = Field(default=True)
    max_tokens: Optional[int] = Field(
        default=None,
        description="Maximum tokens for context (for token-aware truncation)"
    )


class ContextResponse(BaseModel):
    """Response with formatted RAG context."""
    query: str
    formatted_context: str
    document_count: int
    doc_types_found: List[str]
    top_doc_ids: List[str]
    has_context: bool
    build_time_ms: float


# =============================================================================
# Generation API Models
# =============================================================================

class GenerateRequest(BaseModel):
    """Request for RAG-augmented generation."""
    query: str = Field(..., description="User query for generation")
    system_prompt: str = Field(
        default="You are a helpful assistant.",
        description="System prompt for the LLM"
    )
    user_prompt_template: Optional[str] = Field(
        default=None,
        description="Custom user prompt template with {context} and {query} placeholders"
    )
    top_k: int = Field(default=5, ge=1, le=50)
    min_score: float = Field(default=0.05, ge=0.0, le=1.0)
    doc_types: Optional[List[DocumentTypeEnum]] = None
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=2048, ge=1, le=8192)
    stream: bool = Field(default=False, description="Enable streaming response")


class GenerateResponse(BaseModel):
    """Response from RAG-augmented generation."""
    query: str
    response: str
    sources: List[DocumentResult]
    context_used: str
    generation_time_ms: float
    search_time_ms: float
    total_time_ms: float
    model: str
    tokens_used: Optional[int] = None


# =============================================================================
# Document Ingestion API Models
# =============================================================================

class DocumentInput(BaseModel):
    """A document to ingest."""
    id: str = Field(..., description="Unique document ID")
    content: str = Field(..., description="Document content")
    doc_type: DocumentTypeEnum = Field(default=DocumentTypeEnum.GENERAL)
    metadata: Dict[str, Any] = Field(default_factory=dict)


class IngestRequest(BaseModel):
    """Request to ingest documents into the knowledge base."""
    documents: List[DocumentInput] = Field(..., min_length=1)
    collection: str = Field(default="default", description="Collection/namespace")
    upsert: bool = Field(default=True, description="Update if document exists")


class IngestResponse(BaseModel):
    """Response from document ingestion."""
    ingested_count: int
    failed_count: int
    failed_ids: List[str] = Field(default_factory=list)
    collection: str
    total_documents: int
    ingest_time_ms: float


# =============================================================================
# Health & Status API Models
# =============================================================================

class ComponentStatus(BaseModel):
    """Status of a service component."""
    name: str
    status: str  # "healthy", "degraded", "unhealthy"
    message: Optional[str] = None
    latency_ms: Optional[float] = None


class HealthResponse(BaseModel):
    """Service health check response."""
    status: str  # "healthy", "degraded", "unhealthy"
    version: str
    timestamp: datetime
    components: List[ComponentStatus]
    metrics: ServiceMetrics


class ReadinessResponse(BaseModel):
    """Kubernetes readiness probe response."""
    ready: bool
    vector_store_ready: bool
    llm_ready: bool
    message: str


class LivenessResponse(BaseModel):
    """Kubernetes liveness probe response."""
    alive: bool
    uptime_seconds: float
