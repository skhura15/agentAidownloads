"""
RAG Service

Reusable service for Retrieval-Augmented Generation (RAG) operations.
Provides a clean interface for knowledge retrieval and context-aware generation.

This service can be used by any agent that needs RAG capabilities:
- Knowledge search and retrieval
- Context building from search results
- RAG-augmented text generation

Usage:
    from core import RAGService, RAGConfig
    
    # Initialize with vector store and LLM
    rag_service = RAGService(
        vector_store=my_vector_store,
        llm_client=my_llm_client,
        config=RAGConfig(top_k=5, min_score=0.1),
    )
    
    # Search knowledge base
    results = rag_service.search("How to configure routing?")
    
    # Build context for custom prompts
    context = rag_service.build_context("routing configuration issue")
    
    # Generate with RAG
    response = rag_service.generate(
        query="How do I configure call routing?",
        system_prompt="You are a helpful assistant.",
    )
"""

import logging
import os
from datetime import datetime
from typing import Optional, List, Dict, Any, Union, Protocol, runtime_checkable

from core.uta_vectorstore_base import VectorStore, SearchResult, DocumentType
from core.rag_types import (
    RAGContext,
    RAGConfig,
    RAGRequest,
    RAGResponse,
    ContextFormatter,
)

logger = logging.getLogger(__name__)


# =============================================================================
# LLM Client Protocol (for type hints with any LLM client)
# =============================================================================

@runtime_checkable
class LLMClient(Protocol):
    """Protocol for LLM clients (Ollama, Azure OpenAI, etc.)."""
    
    def chat(self, messages: List[Any]) -> str:
        """Generate a chat completion."""
        ...


# =============================================================================
# RAG Service
# =============================================================================

class RAGService:
    """
    Reusable RAG (Retrieval-Augmented Generation) service.
    
    Provides:
    - Knowledge base search with configurable filtering
    - Context building from search results
    - RAG-augmented generation with any compatible LLM
    
    Thread-safe for concurrent use across multiple agents.
    
    Example:
        rag = RAGService(vector_store=store, llm_client=llm)
        
        # Simple search
        results = rag.search("queue timeout configuration")
        
        # Build context for custom use
        context = rag.build_context("routing issue", doc_types=[DocumentType.SOP])
        
        # Full RAG generation
        response = rag.generate(
            query="How do I fix routing errors?",
            system_prompt="You are a CCaaS support expert.",
        )
    """
    
    def __init__(
        self,
        vector_store: Optional[VectorStore] = None,
        llm_client: Optional[LLMClient] = None,
        config: Optional[RAGConfig] = None,
    ):
        """
        Initialize RAG service.
        
        Args:
            vector_store: Vector store for document retrieval
            llm_client: LLM client for generation (Ollama, Azure OpenAI, etc.)
            config: RAG configuration
        """
        self._vector_store = vector_store
        self._llm = llm_client
        self.config = config or RAGConfig()
        
        # Metrics
        self._metrics = {
            "searches": 0,
            "generations": 0,
            "avg_latency_ms": 0.0,
            "cache_hits": 0,
        }
    
    # =========================================================================
    # Properties
    # =========================================================================
    
    @property
    def is_ready(self) -> bool:
        """Check if the service is ready for operations."""
        return self._vector_store is not None
    
    @property
    def can_generate(self) -> bool:
        """Check if the service can perform generation (has LLM)."""
        return self._llm is not None
    
    @property
    def document_count(self) -> int:
        """Get total document count in vector store."""
        if self._vector_store:
            return self._vector_store.count()
        return 0
    
    @property
    def metrics(self) -> Dict[str, Any]:
        """Get service metrics."""
        return self._metrics.copy()
    
    # =========================================================================
    # Component Management
    # =========================================================================
    
    def set_vector_store(self, vector_store: VectorStore) -> None:
        """Set or update the vector store."""
        self._vector_store = vector_store
        logger.info(f"Vector store set with {vector_store.count()} documents")
    
    def set_llm_client(self, llm_client: LLMClient) -> None:
        """Set or update the LLM client."""
        self._llm = llm_client
        logger.info("LLM client updated")
    
    def set_config(self, config: RAGConfig) -> None:
        """Update RAG configuration."""
        self.config = config
    
    # =========================================================================
    # Search Operations
    # =========================================================================
    
    def search(
        self,
        query: str,
        doc_types: Optional[List[DocumentType]] = None,
        top_k: Optional[int] = None,
        min_score: Optional[float] = None,
        use_query_expansion: Optional[bool] = None,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[SearchResult]:
        """
        Search the knowledge base for relevant documents.
        
        Uses hybrid search when available (semantic + keyword + query expansion).
        
        Args:
            query: Search query
            doc_types: Filter by document types
            top_k: Override default top_k
            min_score: Override minimum score threshold
            use_query_expansion: Override query expansion setting
            filters: Additional metadata filters
            
        Returns:
            List of SearchResult objects sorted by relevance
        """
        if not self._vector_store:
            logger.warning("Search attempted without vector store")
            return []
        
        self._metrics["searches"] += 1
        
        # Build filters
        search_filters = filters.copy() if filters else {}
        if doc_types:
            search_filters["doc_type"] = [dt.value for dt in doc_types]
        
        # Use config defaults with overrides
        k = top_k or self.config.top_k
        expand = use_query_expansion if use_query_expansion is not None else self.config.use_query_expansion
        score_threshold = min_score if min_score is not None else self.config.min_score
        
        # Execute search
        try:
            if hasattr(self._vector_store, 'hybrid_search'):
                results = self._vector_store.hybrid_search(
                    query=query,
                    top_k=k,
                    filters=search_filters if search_filters else None,
                    use_query_expansion=expand,
                )
            else:
                results = self._vector_store.search(
                    query=query,
                    top_k=k,
                    filters=search_filters if search_filters else None,
                )
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
        
        # Log raw results
        if results:
            logger.debug(f"Raw search returned {len(results)} results")
            for r in results[:3]:
                logger.debug(f"  - {r.document.id}: score={r.score:.4f}")
        
        # Filter by minimum score
        results = [r for r in results if r.score >= score_threshold]
        
        logger.info(f"Found {len(results)} relevant documents for: {query[:50]}...")
        return results
    
    # =========================================================================
    # Context Building
    # =========================================================================
    
    def build_context(
        self,
        query: str,
        doc_types: Optional[List[DocumentType]] = None,
        format_style: Optional[str] = None,
        **search_kwargs,
    ) -> RAGContext:
        """
        Build RAG context by searching and formatting documents.
        
        Args:
            query: Search query
            doc_types: Filter by document types
            format_style: Context format style ("default", "compact", "markdown")
            **search_kwargs: Additional arguments passed to search()
            
        Returns:
            RAGContext with retrieved documents and formatted context
        """
        results = self.search(query, doc_types=doc_types, **search_kwargs)
        
        if not results:
            return RAGContext(
                documents=[],
                formatted_context=self.config.no_context_message,
                doc_types_found=[],
                query=query,
            )
        
        # Get unique doc types
        doc_types_found = list(set(r.document.doc_type.value for r in results))
        
        # Format context
        style = format_style or self.config.context_format
        formatted = ContextFormatter.format(
            results,
            style=style,
            include_scores=self.config.include_scores,
            include_doc_types=self.config.include_doc_types,
        )
        
        return RAGContext(
            documents=results,
            formatted_context=formatted,
            doc_types_found=doc_types_found,
            query=query,
        )
    
    # =========================================================================
    # Generation
    # =========================================================================
    
    def generate(
        self,
        query: str,
        system_prompt: str,
        user_prompt_template: Optional[str] = None,
        doc_types: Optional[List[DocumentType]] = None,
        context: Optional[RAGContext] = None,
        **search_kwargs,
    ) -> RAGResponse:
        """
        Generate a response using RAG.
        
        Retrieves relevant context (unless provided) and generates a response
        using the configured LLM.
        
        Args:
            query: User query
            system_prompt: System prompt for the LLM
            user_prompt_template: Template with {query} and {context} placeholders
            doc_types: Filter by document types
            context: Pre-built context (skips retrieval if provided)
            **search_kwargs: Additional arguments passed to search()
            
        Returns:
            RAGResponse with generated content and context
        """
        if not self._llm:
            raise RuntimeError("LLM client not configured. Call set_llm_client() first.")
        
        start_time = datetime.utcnow()
        self._metrics["generations"] += 1
        
        # Get context
        if context is None:
            context = self.build_context(query, doc_types=doc_types, **search_kwargs)
        
        # Build prompt
        template = user_prompt_template or "Question: {query}\n\nContext:\n{context}"
        user_prompt = template.format(query=query, context=context.formatted_context)
        
        # Create messages - use dict format for compatibility
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        
        # Check if LLM expects ChatMessage objects
        try:
            # Try to import and use proper message types
            from core.uta_ollama_client import ChatMessage as OllamaChatMessage
            messages = [
                OllamaChatMessage(role="system", content=system_prompt),
                OllamaChatMessage(role="user", content=user_prompt),
            ]
        except ImportError:
            pass
        
        # Generate response
        try:
            content = self._llm.chat(messages)
        except Exception as e:
            logger.error(f"Generation error: {e}")
            raise
        
        # Calculate latency
        latency_ms = (datetime.utcnow() - start_time).total_seconds() * 1000
        self._update_avg_latency(latency_ms)
        
        return RAGResponse(
            content=content,
            context=context,
            latency_ms=latency_ms,
            metadata={"search_kwargs": search_kwargs},
        )
    
    def generate_from_request(self, request: RAGRequest) -> RAGResponse:
        """
        Generate a response from a RAGRequest object.
        
        Useful for standardized request handling across agents.
        
        Args:
            request: RAGRequest with query, prompts, and configuration
            
        Returns:
            RAGResponse with generated content
        """
        # Temporarily override config if request has custom config
        original_config = self.config
        if request.config:
            self.config = request.config
        
        try:
            return self.generate(
                query=request.query,
                system_prompt=request.system_prompt,
                user_prompt_template=request.user_prompt_template,
                doc_types=request.doc_types,
            )
        finally:
            self.config = original_config
    
    # =========================================================================
    # Utility Methods
    # =========================================================================
    
    def _update_avg_latency(self, latency_ms: float) -> None:
        """Update average latency metric."""
        current = self._metrics["avg_latency_ms"]
        count = self._metrics["generations"]
        self._metrics["avg_latency_ms"] = ((current * (count - 1)) + latency_ms) / count
    
    def get_status(self) -> Dict[str, Any]:
        """Get service status information."""
        return {
            "is_ready": self.is_ready,
            "can_generate": self.can_generate,
            "document_count": self.document_count,
            "config": {
                "top_k": self.config.top_k,
                "min_score": self.config.min_score,
                "use_query_expansion": self.config.use_query_expansion,
            },
            "metrics": self.metrics,
        }


# =============================================================================
# Factory Function for Easy Initialization
# =============================================================================

def create_rag_service(
    vector_store_config: Optional[Dict[str, Any]] = None,
    llm_config: Optional[Dict[str, Any]] = None,
    rag_config: Optional[RAGConfig] = None,
) -> RAGService:
    """
    Factory function to create a fully configured RAG service.
    
    Args:
        vector_store_config: Configuration for vector store creation
        llm_config: Configuration for LLM client creation
        rag_config: RAG service configuration
        
    Returns:
        Configured RAGService instance
        
    Example:
        rag = create_rag_service(
            vector_store_config={
                "provider": "chroma",
                "collection_name": "my_knowledge",
                "embedding_provider": "ollama",
            },
            llm_config={
                "provider": "ollama",
                "model": "llama3.1:8b-instruct-q8_0",
            },
        )
    """
    from core import VectorStoreFactory
    
    vector_store = None
    llm_client = None
    
    # Create vector store
    if vector_store_config:
        provider = vector_store_config.pop("provider", "chroma")
        vector_store = VectorStoreFactory.create(provider=provider, config=vector_store_config)
    
    # Create LLM client
    if llm_config:
        llm_provider = llm_config.get("provider", "ollama")
        
        if llm_provider == "ollama":
            from core.uta_ollama_client import OllamaClient, GenerationConfig
            llm_client = OllamaClient(
                model=llm_config.get("model", "llama3.1:8b-instruct-q8_0"),
                base_url=llm_config.get("base_url", "http://localhost:11434"),
                config=GenerationConfig(
                    temperature=llm_config.get("temperature", 0.7),
                    max_tokens=llm_config.get("max_tokens", 2048),
                ),
            )
        elif llm_provider in ("azure", "azure_openai", "foundry"):
            from core.uta_azure_openai_llm import AzureOpenAIClient, GenerationConfig
            llm_client = AzureOpenAIClient(
                model=llm_config.get("model"),
                endpoint=llm_config.get("endpoint"),
                api_key=llm_config.get("api_key"),
                config=GenerationConfig(
                    temperature=llm_config.get("temperature", 0.7),
                    max_tokens=llm_config.get("max_tokens", 2048),
                ),
                use_foundry=llm_config.get("use_foundry", False),
            )
    
    return RAGService(
        vector_store=vector_store,
        llm_client=llm_client,
        config=rag_config or RAGConfig(),
    )
