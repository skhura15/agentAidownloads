"""
RAG Types and Data Classes

Shared data structures for RAG (Retrieval-Augmented Generation) functionality.
These types are used across all RAG-enabled agents.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Callable
from enum import Enum

from core.uta_vectorstore_base import SearchResult, DocumentType


@dataclass
class RAGContext:
    """
    Context retrieved for RAG generation.
    
    Attributes:
        documents: List of retrieved search results
        formatted_context: Pre-formatted string for LLM prompt insertion
        doc_types_found: List of document types found in results
        query: Original query used for retrieval
        metadata: Additional context metadata
    """
    documents: List[SearchResult]
    formatted_context: str
    doc_types_found: List[str]
    query: str = ""
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def has_context(self) -> bool:
        """Check if any documents were retrieved."""
        return len(self.documents) > 0
    
    @property
    def document_count(self) -> int:
        """Number of documents retrieved."""
        return len(self.documents)
    
    def get_top_doc_ids(self, n: int = 3) -> List[str]:
        """Get IDs of top N documents."""
        return [r.document.id for r in self.documents[:n]]


@dataclass
class RAGConfig:
    """
    Configuration for RAG operations.
    
    Attributes:
        top_k: Number of documents to retrieve
        min_score: Minimum relevance score threshold (0.0-1.0)
        use_query_expansion: Whether to expand queries for better recall
        context_format: Format template for document context
        no_context_message: Message when no documents found
        include_scores: Whether to include relevance scores in formatted context
        include_doc_types: Whether to include document types in formatted context
    """
    top_k: int = 5
    min_score: float = 0.05
    use_query_expansion: bool = True
    context_format: str = "default"
    no_context_message: str = "No relevant documents found in knowledge base."
    include_scores: bool = True
    include_doc_types: bool = True
    max_context_tokens: Optional[int] = None  # Future: token-aware truncation


@dataclass
class RAGRequest:
    """
    Request for RAG-augmented generation.
    
    Attributes:
        query: User query or input text
        system_prompt: System prompt for the LLM
        user_prompt_template: Template for user prompt (use {context} and {query} placeholders)
        doc_types: Filter by specific document types
        config: RAG configuration overrides
        metadata: Additional request metadata
    """
    query: str
    system_prompt: str
    user_prompt_template: str = "Question: {query}\n\nContext:\n{context}"
    doc_types: Optional[List[DocumentType]] = None
    config: Optional[RAGConfig] = None
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class RAGResponse:
    """
    Response from RAG-augmented generation.
    
    Attributes:
        content: Generated response text
        context: The RAG context used for generation
        model: Model used for generation
        tokens_used: Approximate tokens used (if available)
        latency_ms: Response latency in milliseconds
        metadata: Additional response metadata
    """
    content: str
    context: RAGContext
    model: str = ""
    tokens_used: Optional[int] = None
    latency_ms: Optional[float] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @property
    def sources(self) -> List[str]:
        """Get document IDs used as sources."""
        return self.context.get_top_doc_ids(10)


class ContextFormatter:
    """
    Formats retrieved documents into context strings for LLM prompts.
    
    Supports multiple format styles for different use cases.
    """
    
    @staticmethod
    def default(
        results: List[SearchResult],
        include_scores: bool = True,
        include_doc_types: bool = True,
    ) -> str:
        """
        Default format with clear document separators.
        
        Example output:
            --- Document 1 ---
            Type: SOP
            ID: sop-routing-001
            Relevance: 0.85
            
            [Document content here]
        """
        if not results:
            return ""
            
        parts = []
        for i, result in enumerate(results, 1):
            doc = result.document
            header_parts = [f"--- Document {i} ---"]
            
            if include_doc_types:
                header_parts.append(f"Type: {doc.doc_type.value.upper()}")
            
            header_parts.append(f"ID: {doc.id}")
            
            if include_scores:
                header_parts.append(f"Relevance: {result.score:.2f}")
            
            header = "\n".join(header_parts)
            parts.append(f"{header}\n\n{doc.content}")
        
        return "\n\n".join(parts)
    
    @staticmethod
    def compact(results: List[SearchResult]) -> str:
        """
        Compact format for token-constrained contexts.
        
        Example output:
            [sop-routing-001] Document content here...
        """
        if not results:
            return ""
            
        parts = []
        for result in results:
            doc = result.document
            parts.append(f"[{doc.id}] {doc.content}")
        
        return "\n\n".join(parts)
    
    @staticmethod
    def markdown(results: List[SearchResult]) -> str:
        """
        Markdown format for UI display.
        
        Example output:
            ### sop-routing-001 (SOP) - 85% match
            Document content here...
        """
        if not results:
            return ""
            
        parts = []
        for result in results:
            doc = result.document
            score_pct = int(result.score * 100)
            header = f"### {doc.id} ({doc.doc_type.value.upper()}) - {score_pct}% match"
            parts.append(f"{header}\n{doc.content}")
        
        return "\n\n---\n\n".join(parts)
    
    @staticmethod
    def numbered_list(results: List[SearchResult]) -> str:
        """
        Numbered list format for citation-style contexts.
        """
        if not results:
            return ""
            
        parts = []
        for i, result in enumerate(results, 1):
            doc = result.document
            parts.append(f"[{i}] {doc.id}: {doc.content}")
        
        return "\n\n".join(parts)
    
    @classmethod
    def format(
        cls,
        results: List[SearchResult],
        style: str = "default",
        **kwargs,
    ) -> str:
        """
        Format results using the specified style.
        
        Args:
            results: Search results to format
            style: Format style ("default", "compact", "markdown", "numbered")
            **kwargs: Additional arguments passed to formatter
            
        Returns:
            Formatted context string
        """
        formatters = {
            "default": cls.default,
            "compact": cls.compact,
            "markdown": cls.markdown,
            "numbered": cls.numbered_list,
        }
        
        formatter = formatters.get(style, cls.default)
        
        # Handle kwargs for formatters that accept them
        if style == "default":
            return formatter(results, **kwargs)
        return formatter(results)
