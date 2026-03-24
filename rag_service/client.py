"""
RAG Service Client

HTTP client for communicating with the standalone RAG service.
This replaces the local RAGService when deployed in Kubernetes.

Usage:
    from rag_service.client import RAGServiceClient
    
    # Initialize client
    client = RAGServiceClient(base_url="http://rag-service:8001")
    
    # Search knowledge base
    results = await client.search("How to configure routing?")
    
    # Build context
    context = await client.build_context("routing issue")
    
    # Generate with RAG
    response = await client.generate(
        query="How do I configure call routing?",
        system_prompt="You are a helpful assistant.",
    )
"""

import os
import logging
import asyncio
from typing import Optional, List, Dict, Any
from dataclasses import dataclass, field
from datetime import datetime

import httpx

from rag_service.models import (
    SearchRequest,
    SearchResponse,
    ContextRequest,
    ContextResponse,
    GenerateRequest,
    GenerateResponse,
    DocumentTypeEnum,
    HealthResponse,
)

logger = logging.getLogger(__name__)


@dataclass
class ClientConfig:
    """Configuration for RAG Service client."""
    base_url: str = "http://localhost:8001"
    timeout_seconds: float = 30.0
    max_retries: int = 3
    retry_delay_seconds: float = 0.5
    verify_ssl: bool = True
    api_key: Optional[str] = None
    headers: Dict[str, str] = field(default_factory=dict)


class RAGServiceClient:
    """
    Async HTTP client for the standalone RAG service.
    
    Implements the same interface as local RAGService but communicates
    via HTTP to the Kubernetes-deployed RAG service.
    
    Features:
    - Async HTTP with connection pooling
    - Automatic retries with exponential backoff
    - Circuit breaker pattern for failure handling
    - Health check integration
    
    Example:
        async with RAGServiceClient(base_url="http://rag-service:8001") as client:
            results = await client.search("routing configuration")
            print(f"Found {len(results.results)} documents")
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        config: Optional[ClientConfig] = None,
    ):
        """
        Initialize RAG Service client.
        
        Args:
            base_url: RAG service base URL (overrides config)
            config: Full client configuration
        """
        self.config = config or ClientConfig()
        if base_url:
            self.config.base_url = base_url
        
        # Use environment variable if not specified
        if self.config.base_url == "http://localhost:8001":
            self.config.base_url = os.getenv(
                "RAG_SERVICE_URL", 
                self.config.base_url
            )
        
        self._client: Optional[httpx.AsyncClient] = None
        self._is_healthy = True
        self._last_health_check = None
        
        # Circuit breaker state
        self._failure_count = 0
        self._circuit_open = False
        self._circuit_open_until = None
    
    async def __aenter__(self):
        """Async context manager entry."""
        await self._ensure_client()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.close()
    
    async def _ensure_client(self):
        """Ensure HTTP client is initialized."""
        if self._client is None:
            headers = {"Content-Type": "application/json"}
            headers.update(self.config.headers)
            
            if self.config.api_key:
                headers["Authorization"] = f"Bearer {self.config.api_key}"
            
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout_seconds,
                verify=self.config.verify_ssl,
                headers=headers,
            )
    
    async def close(self):
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None
    
    # =========================================================================
    # Health Check
    # =========================================================================
    
    async def health_check(self) -> HealthResponse:
        """Check RAG service health."""
        await self._ensure_client()
        
        try:
            response = await self._client.get("/health")
            response.raise_for_status()
            self._is_healthy = True
            self._failure_count = 0
            return HealthResponse(**response.json())
        except Exception as e:
            self._is_healthy = False
            logger.error(f"Health check failed: {e}")
            raise
    
    async def is_ready(self) -> bool:
        """Check if service is ready (Kubernetes readiness)."""
        await self._ensure_client()
        
        try:
            response = await self._client.get("/ready")
            return response.status_code == 200
        except Exception:
            return False
    
    # =========================================================================
    # Search Operations
    # =========================================================================
    
    async def search(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.05,
        doc_types: Optional[List[str]] = None,
        use_query_expansion: bool = True,
        filters: Optional[Dict[str, Any]] = None,
    ) -> SearchResponse:
        """
        Search the knowledge base.
        
        Args:
            query: Search query
            top_k: Number of results
            min_score: Minimum relevance score
            doc_types: Filter by document types
            use_query_expansion: Enable query expansion
            filters: Additional filters
            
        Returns:
            SearchResponse with results
        """
        await self._ensure_client()
        
        request = SearchRequest(
            query=query,
            top_k=top_k,
            min_score=min_score,
            doc_types=[DocumentTypeEnum(dt) for dt in doc_types] if doc_types else None,
            use_query_expansion=use_query_expansion,
            filters=filters,
        )
        
        response = await self._make_request("POST", "/search", request.model_dump())
        return SearchResponse(**response)
    
    # =========================================================================
    # Context Operations
    # =========================================================================
    
    async def build_context(
        self,
        query: str,
        top_k: int = 5,
        min_score: float = 0.05,
        doc_types: Optional[List[str]] = None,
        format_style: str = "default",
    ) -> ContextResponse:
        """
        Build formatted RAG context.
        
        Args:
            query: Query for context
            top_k: Number of documents
            min_score: Minimum score
            doc_types: Filter by types
            format_style: Context format
            
        Returns:
            ContextResponse with formatted context
        """
        await self._ensure_client()
        
        request = ContextRequest(
            query=query,
            top_k=top_k,
            min_score=min_score,
            doc_types=[DocumentTypeEnum(dt) for dt in doc_types] if doc_types else None,
            format_style=format_style,
        )
        
        response = await self._make_request("POST", "/context", request.model_dump())
        return ContextResponse(**response)
    
    # =========================================================================
    # Generation Operations
    # =========================================================================
    
    async def generate(
        self,
        query: str,
        system_prompt: str = "You are a helpful assistant.",
        top_k: int = 5,
        min_score: float = 0.05,
        doc_types: Optional[List[str]] = None,
        temperature: float = 0.7,
        max_tokens: int = 2048,
    ) -> GenerateResponse:
        """
        Generate response with RAG.
        
        Args:
            query: User query
            system_prompt: System prompt
            top_k: Number of context documents
            min_score: Minimum score
            doc_types: Filter by types
            temperature: LLM temperature
            max_tokens: Max tokens
            
        Returns:
            GenerateResponse with generated text
        """
        await self._ensure_client()
        
        request = GenerateRequest(
            query=query,
            system_prompt=system_prompt,
            top_k=top_k,
            min_score=min_score,
            doc_types=[DocumentTypeEnum(dt) for dt in doc_types] if doc_types else None,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        
        response = await self._make_request("POST", "/generate", request.model_dump())
        return GenerateResponse(**response)
    
    # =========================================================================
    # Internal Methods
    # =========================================================================
    
    async def _make_request(
        self,
        method: str,
        path: str,
        data: Optional[Dict] = None,
    ) -> Dict:
        """Make HTTP request with retries."""
        await self._ensure_client()
        
        # Check circuit breaker
        if self._circuit_open:
            if datetime.utcnow() < self._circuit_open_until:
                raise ConnectionError("Circuit breaker is open")
            self._circuit_open = False
        
        last_error = None
        
        for attempt in range(self.config.max_retries):
            try:
                if method == "GET":
                    response = await self._client.get(path)
                elif method == "POST":
                    response = await self._client.post(path, json=data)
                else:
                    raise ValueError(f"Unsupported method: {method}")
                
                response.raise_for_status()
                
                # Reset failure count on success
                self._failure_count = 0
                return response.json()
                
            except httpx.HTTPStatusError as e:
                last_error = e
                # Don't retry client errors (4xx)
                if 400 <= e.response.status_code < 500:
                    raise
                logger.warning(f"Request failed (attempt {attempt + 1}): {e}")
                
            except httpx.RequestError as e:
                last_error = e
                logger.warning(f"Request error (attempt {attempt + 1}): {e}")
            
            # Update failure tracking
            self._failure_count += 1
            
            # Open circuit breaker if too many failures
            if self._failure_count >= 5:
                self._circuit_open = True
                self._circuit_open_until = datetime.utcnow()
                logger.error("Circuit breaker opened due to repeated failures")
            
            # Wait before retry
            if attempt < self.config.max_retries - 1:
                delay = self.config.retry_delay_seconds * (2 ** attempt)
                await asyncio.sleep(delay)
        
        raise last_error or Exception("Request failed after retries")


# =============================================================================
# Synchronous Wrapper (for backward compatibility)
# =============================================================================

class RAGServiceClientSync:
    """
    Synchronous wrapper for RAGServiceClient.
    
    Provides the same interface as the local RAGService for
    backward compatibility with synchronous code.
    """
    
    def __init__(
        self,
        base_url: Optional[str] = None,
        config: Optional[ClientConfig] = None,
    ):
        self._async_client = RAGServiceClient(base_url=base_url, config=config)
        self._loop: Optional[asyncio.AbstractEventLoop] = None
    
    def _get_loop(self):
        """Get or create event loop."""
        try:
            self._loop = asyncio.get_event_loop()
        except RuntimeError:
            self._loop = asyncio.new_event_loop()
            asyncio.set_event_loop(self._loop)
        return self._loop
    
    def search(self, *args, **kwargs) -> SearchResponse:
        """Synchronous search."""
        return self._get_loop().run_until_complete(
            self._async_client.search(*args, **kwargs)
        )
    
    def build_context(self, *args, **kwargs) -> ContextResponse:
        """Synchronous context building."""
        return self._get_loop().run_until_complete(
            self._async_client.build_context(*args, **kwargs)
        )
    
    def generate(self, *args, **kwargs) -> GenerateResponse:
        """Synchronous generation."""
        return self._get_loop().run_until_complete(
            self._async_client.generate(*args, **kwargs)
        )
    
    def close(self):
        """Close the client."""
        self._get_loop().run_until_complete(self._async_client.close())
