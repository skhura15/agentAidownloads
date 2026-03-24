"""
UTA Core Module Tests

Tests for vector store, LLM client, and ingestion components.
"""

import pytest
from unittest.mock import Mock, patch


class TestVectorStoreFactory:
    """Tests for VectorStoreFactory."""
    
    def test_create_chroma_store(self):
        """Test creating a ChromaDB store."""
        from core import VectorStoreFactory
        
        store = VectorStoreFactory.create(
            provider="chroma",
            config={
                "collection_name": "test_collection",
                "persist_directory": "./data/chroma_test",
                "embedding_provider": "default",
            }
        )
        
        assert store is not None
        assert hasattr(store, "search")
        assert hasattr(store, "add_documents")
    
    def test_invalid_provider_raises_error(self):
        """Test that invalid provider raises ValueError."""
        from core import VectorStoreFactory
        
        with pytest.raises(ValueError):
            VectorStoreFactory.create(provider="invalid_provider")


class TestDocument:
    """Tests for Document dataclass."""
    
    def test_document_creation(self):
        """Test creating a Document."""
        from core import Document, DocumentType
        
        doc = Document(
            id="test-doc-001",
            content="This is test content",
            metadata={"source": "test"},
            doc_type=DocumentType.SOP,
        )
        
        assert doc.id == "test-doc-001"
        assert doc.content == "This is test content"
        assert doc.doc_type == DocumentType.SOP
    
    def test_document_to_dict(self):
        """Test Document.to_dict() method."""
        from core import Document, DocumentType
        
        doc = Document(
            id="test-doc-002",
            content="Test content",
            doc_type=DocumentType.PLAYBOOK,
        )
        
        d = doc.to_dict()
        assert d["id"] == "test-doc-002"
        assert d["doc_type"] == "playbook"


class TestChunkConfig:
    """Tests for ChunkConfig."""
    
    def test_default_config(self):
        """Test default ChunkConfig values."""
        from core import ChunkConfig
        
        config = ChunkConfig()
        assert config.chunk_size == 1000
        assert config.chunk_overlap == 200
        assert config.min_chunk_size == 100


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
