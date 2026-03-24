"""
Vector Store Base Classes and Interfaces

Defines the abstract interface for all vector store implementations.
Allows seamless switching between ChromaDB, Cosmos DB, and Azure AI Search.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum


class DocumentType(Enum):
    """Types of documents in the knowledge base."""
    SOP = "sop"
    PLAYBOOK = "playbook"
    KNOWN_ISSUE = "known_issue"
    ERROR_CODE = "error_code"
    CONFIG_CHECK = "config_check"
    EXPERT_INSIGHT = "expert_insight"
    KB_ARTICLE = "kb_article"


@dataclass
class Document:
    """
    Represents a document to be stored in the vector database.
    
    Attributes:
        id: Unique identifier for the document
        content: The text content of the document
        metadata: Additional metadata (category, version, source, etc.)
        doc_type: Type of document (SOP, playbook, etc.)
        embedding: Optional pre-computed embedding vector
    """
    id: str
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    doc_type: DocumentType = DocumentType.KB_ARTICLE
    embedding: Optional[List[float]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert document to dictionary representation."""
        return {
            "id": self.id,
            "content": self.content,
            "metadata": self.metadata,
            "doc_type": self.doc_type.value,
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Document":
        """Create document from dictionary."""
        return cls(
            id=data["id"],
            content=data["content"],
            metadata=data.get("metadata", {}),
            doc_type=DocumentType(data.get("doc_type", "kb_article")),
            embedding=data.get("embedding"),
        )


@dataclass
class SearchResult:
    """
    Represents a search result from the vector database.
    
    Attributes:
        document: The matched document
        score: Relevance/similarity score (higher is better, normalized 0-1)
        highlights: Optional highlighted text snippets
    """
    document: Document
    score: float
    highlights: Optional[List[str]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert search result to dictionary representation."""
        return {
            "document": self.document.to_dict(),
            "score": self.score,
            "highlights": self.highlights,
        }


class VectorStore(ABC):
    """
    Abstract base class for vector store implementations.
    
    All vector database backends (ChromaDB, Cosmos DB, Azure AI Search)
    must implement this interface to ensure interchangeability.
    """
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the vector store connection and create collections/indexes.
        Should be called before any other operations.
        """
        pass
    
    @abstractmethod
    def add_documents(self, documents: List[Document]) -> List[str]:
        """
        Add documents to the vector store.
        
        Args:
            documents: List of Document objects to add
            
        Returns:
            List of document IDs that were added
        """
        pass
    
    @abstractmethod
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        doc_types: Optional[List[DocumentType]] = None,
    ) -> List[SearchResult]:
        """
        Search for documents similar to the query.
        
        Args:
            query: Search query text
            top_k: Number of results to return
            filters: Optional metadata filters
            doc_types: Optional filter by document types
            
        Returns:
            List of SearchResult objects ordered by relevance
        """
        pass
    
    @abstractmethod
    def get_document(self, doc_id: str) -> Optional[Document]:
        """
        Retrieve a specific document by ID.
        
        Args:
            doc_id: Document ID
            
        Returns:
            Document if found, None otherwise
        """
        pass
    
    @abstractmethod
    def delete_document(self, doc_id: str) -> bool:
        """
        Delete a document from the vector store.
        
        Args:
            doc_id: Document ID to delete
            
        Returns:
            True if deleted, False if not found
        """
        pass
    
    @abstractmethod
    def clear(self) -> None:
        """
        Clear all documents from the vector store.
        Use with caution!
        """
        pass
    
    @abstractmethod
    def count(self) -> int:
        """
        Get the total number of documents in the store.
        
        Returns:
            Document count
        """
        pass
    
    def health_check(self) -> bool:
        """
        Check if the vector store is healthy and accessible.
        
        Returns:
            True if healthy, False otherwise
        """
        try:
            self.count()
            return True
        except Exception:
            return False
    
    def search_by_category(
        self,
        query: str,
        category: str,
        top_k: int = 5,
    ) -> List[SearchResult]:
        """
        Convenience method to search within a specific category.
        
        Args:
            query: Search query text
            category: Category to filter by (e.g., "routing", "licensing")
            top_k: Number of results to return
            
        Returns:
            List of SearchResult objects
        """
        return self.search(
            query=query,
            top_k=top_k,
            filters={"category": category}
        )
    
    def search_sops(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """Search specifically for SOPs."""
        return self.search(
            query=query,
            top_k=top_k,
            doc_types=[DocumentType.SOP]
        )
    
    def search_known_issues(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """Search specifically for known issues."""
        return self.search(
            query=query,
            top_k=top_k,
            doc_types=[DocumentType.KNOWN_ISSUE]
        )
    
    def search_error_codes(self, query: str, top_k: int = 3) -> List[SearchResult]:
        """Search specifically for error codes."""
        return self.search(
            query=query,
            top_k=top_k,
            doc_types=[DocumentType.ERROR_CODE]
        )
