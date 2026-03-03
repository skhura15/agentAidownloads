"""
Azure AI Search Vector Store Implementation

Enterprise-grade vector search with hybrid (vector + keyword) capabilities.
Best for production deployments requiring scale and advanced features.
"""

import logging
from typing import List, Dict, Any, Optional

from core.uta_vectorstore_base import (
    VectorStore,
    Document,
    SearchResult,
    DocumentType,
)

logger = logging.getLogger(__name__)


class AzureAISearchStore(VectorStore):
    """
    Azure AI Search implementation of the VectorStore interface.
    
    Features:
    - Enterprise-grade scalability
    - Hybrid search (vector + keyword + semantic ranking)
    - Built-in security (Azure AD, RBAC)
    - Advanced filtering and faceting
    - Integrated with Azure AI Foundry
    
    Prerequisites:
    - Azure AI Search service (Basic tier or higher for vector search)
    - Azure OpenAI for embeddings
    
    Usage:
        store = AzureAISearchStore(
            endpoint="https://your-search.search.windows.net",
            api_key="your-key",
            index_name="uta-knowledge"
        )
        store.initialize()
        store.add_documents([doc1, doc2])
        results = store.search("calls not routing")
    """
    
    # Index schema for UTA knowledge base
    INDEX_SCHEMA = {
        "name": "uta-knowledge",
        "fields": [
            {"name": "id", "type": "Edm.String", "key": True, "filterable": True},
            {"name": "content", "type": "Edm.String", "searchable": True},
            {"name": "doc_type", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "category", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "title", "type": "Edm.String", "searchable": True},
            {"name": "version", "type": "Edm.String", "filterable": True},
            {"name": "severity", "type": "Edm.String", "filterable": True, "facetable": True},
            {"name": "source", "type": "Edm.String", "filterable": True},
            {"name": "metadata", "type": "Edm.String"},  # JSON string
            {"name": "embedding", "type": "Collection(Edm.Single)", 
             "dimensions": 1536, "vectorSearchProfile": "uta-vector-profile"},
        ],
        "vectorSearch": {
            "algorithms": [
                {"name": "uta-hnsw", "kind": "hnsw", 
                 "hnswParameters": {"m": 4, "efConstruction": 400, "efSearch": 500, "metric": "cosine"}}
            ],
            "profiles": [
                {"name": "uta-vector-profile", "algorithm": "uta-hnsw"}
            ]
        },
        "semantic": {
            "configurations": [
                {
                    "name": "uta-semantic-config",
                    "prioritizedFields": {
                        "contentFields": [{"fieldName": "content"}],
                        "titleField": {"fieldName": "title"}
                    }
                }
            ]
        }
    }
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        index_name: str = "uta-knowledge",
        embedding_model: str = "text-embedding-ada-002",
        use_semantic_search: bool = True,
    ):
        """
        Initialize Azure AI Search vector store.
        
        Args:
            endpoint: Azure AI Search endpoint URL
            api_key: Azure AI Search admin key
            index_name: Name of the search index
            embedding_model: Azure OpenAI embedding model deployment name
            use_semantic_search: Enable semantic ranking (requires Semantic Search tier)
        """
        self.endpoint = endpoint
        self.api_key = api_key
        self.index_name = index_name
        self.embedding_model = embedding_model
        self.use_semantic_search = use_semantic_search
        
        self._search_client = None
        self._index_client = None
        self._embedding_client = None
    
    def initialize(self) -> None:
        """Initialize Azure AI Search client and create index if needed."""
        try:
            from azure.search.documents import SearchClient
            from azure.search.documents.indexes import SearchIndexClient
            from azure.core.credentials import AzureKeyCredential
        except ImportError:
            raise ImportError(
                "Azure Search SDK not installed. Run: pip install azure-search-documents"
            )
        
        if not self.endpoint or not self.api_key:
            raise ValueError(
                "Azure AI Search endpoint and api_key are required. "
                "Set AZURE_SEARCH_ENDPOINT and AZURE_SEARCH_KEY environment variables "
                "or pass them to the constructor."
            )
        
        logger.info(f"Initializing Azure AI Search connection to: {self.endpoint}")
        
        credential = AzureKeyCredential(self.api_key)
        
        # Create index client for index management
        self._index_client = SearchIndexClient(
            endpoint=self.endpoint,
            credential=credential
        )
        
        # Create or update index
        self._ensure_index_exists()
        
        # Create search client for document operations
        self._search_client = SearchClient(
            endpoint=self.endpoint,
            index_name=self.index_name,
            credential=credential
        )
        
        # Initialize embedding client
        self._setup_embedding_client()
        
        logger.info("Azure AI Search vector store initialized successfully")
    
    def _ensure_index_exists(self) -> None:
        """Create the search index if it doesn't exist."""
        try:
            from azure.search.documents.indexes.models import (
                SearchIndex,
                SearchField,
                SearchFieldDataType,
                VectorSearch,
                HnswAlgorithmConfiguration,
                VectorSearchProfile,
                SemanticConfiguration,
                SemanticField,
                SemanticPrioritizedFields,
                SemanticSearch,
            )
        except ImportError:
            logger.warning("Could not import Azure Search models. Index creation may fail.")
            return
        
        try:
            # Check if index exists
            existing_indexes = [idx.name for idx in self._index_client.list_indexes()]
            
            if self.index_name in existing_indexes:
                logger.info(f"Index '{self.index_name}' already exists")
                return
            
            # Create new index
            logger.info(f"Creating index: {self.index_name}")
            
            fields = [
                SearchField(name="id", type=SearchFieldDataType.String, key=True, filterable=True),
                SearchField(name="content", type=SearchFieldDataType.String, searchable=True),
                SearchField(name="doc_type", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SearchField(name="category", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SearchField(name="title", type=SearchFieldDataType.String, searchable=True),
                SearchField(name="version", type=SearchFieldDataType.String, filterable=True),
                SearchField(name="severity", type=SearchFieldDataType.String, filterable=True, facetable=True),
                SearchField(name="source", type=SearchFieldDataType.String, filterable=True),
                SearchField(name="metadata", type=SearchFieldDataType.String),
                SearchField(
                    name="embedding",
                    type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                    searchable=True,
                    vector_search_dimensions=1536,
                    vector_search_profile_name="uta-vector-profile"
                ),
            ]
            
            vector_search = VectorSearch(
                algorithms=[
                    HnswAlgorithmConfiguration(name="uta-hnsw"),
                ],
                profiles=[
                    VectorSearchProfile(name="uta-vector-profile", algorithm_configuration_name="uta-hnsw"),
                ],
            )
            
            semantic_config = SemanticConfiguration(
                name="uta-semantic-config",
                prioritized_fields=SemanticPrioritizedFields(
                    content_fields=[SemanticField(field_name="content")],
                    title_field=SemanticField(field_name="title"),
                ),
            )
            
            semantic_search = SemanticSearch(configurations=[semantic_config])
            
            index = SearchIndex(
                name=self.index_name,
                fields=fields,
                vector_search=vector_search,
                semantic_search=semantic_search,
            )
            
            self._index_client.create_or_update_index(index)
            logger.info(f"Index '{self.index_name}' created successfully")
            
        except Exception as e:
            logger.error(f"Error creating index: {e}")
            raise
    
    def _setup_embedding_client(self) -> None:
        """Set up Azure OpenAI client for embeddings."""
        try:
            import os
            from openai import AzureOpenAI
            
            azure_endpoint = os.getenv("AZURE_OPENAI_ENDPOINT")
            api_key = os.getenv("AZURE_OPENAI_API_KEY")
            
            if azure_endpoint and api_key:
                self._embedding_client = AzureOpenAI(
                    azure_endpoint=azure_endpoint,
                    api_key=api_key,
                    api_version="2024-02-01"
                )
                logger.info("Azure OpenAI embedding client initialized")
            else:
                logger.warning(
                    "Azure OpenAI credentials not found. "
                    "Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY."
                )
        except ImportError:
            logger.warning("OpenAI SDK not installed. Run: pip install openai")
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text."""
        if not self._embedding_client:
            return None
        
        try:
            response = self._embedding_client.embeddings.create(
                model=self.embedding_model,
                input=text[:8000]  # Truncate to avoid token limits
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to Azure AI Search."""
        if not self._search_client:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        import json
        
        search_docs = []
        added_ids = []
        
        for doc in documents:
            # Generate embedding
            embedding = doc.embedding or self._generate_embedding(doc.content)
            
            # Prepare document for Azure Search
            search_doc = {
                "id": doc.id,
                "content": doc.content,
                "doc_type": doc.doc_type.value,
                "category": doc.metadata.get("category", ""),
                "title": doc.metadata.get("title", ""),
                "version": doc.metadata.get("version", ""),
                "severity": doc.metadata.get("severity", ""),
                "source": doc.metadata.get("source", ""),
                "metadata": json.dumps(doc.metadata),
                "embedding": embedding,
            }
            
            search_docs.append(search_doc)
            added_ids.append(doc.id)
        
        try:
            # Upload in batches
            batch_size = 100
            for i in range(0, len(search_docs), batch_size):
                batch = search_docs[i:i + batch_size]
                result = self._search_client.upload_documents(documents=batch)
                logger.debug(f"Uploaded batch of {len(batch)} documents")
            
            logger.info(f"Added {len(added_ids)} documents to Azure AI Search")
        except Exception as e:
            logger.error(f"Error uploading documents: {e}")
            raise
        
        return added_ids
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        doc_types: Optional[List[DocumentType]] = None,
    ) -> List[SearchResult]:
        """Search using hybrid (vector + keyword) search."""
        if not self._search_client:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            from azure.search.documents.models import VectorizedQuery
        except ImportError:
            logger.error("Azure Search models not available")
            return []
        
        import json
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        
        # Build filter string
        filter_parts = []
        if doc_types:
            type_values = [f"doc_type eq '{dt.value}'" for dt in doc_types]
            filter_parts.append(f"({' or '.join(type_values)})")
        
        if filters:
            for key, value in filters.items():
                filter_parts.append(f"{key} eq '{value}'")
        
        filter_str = " and ".join(filter_parts) if filter_parts else None
        
        # Build search parameters
        search_params = {
            "search_text": query,
            "top": top_k,
            "filter": filter_str,
            "select": ["id", "content", "doc_type", "title", "metadata"],
        }
        
        # Add vector query if embedding available
        if query_embedding:
            vector_query = VectorizedQuery(
                vector=query_embedding,
                k_nearest_neighbors=top_k,
                fields="embedding"
            )
            search_params["vector_queries"] = [vector_query]
        
        # Add semantic search if enabled
        if self.use_semantic_search:
            search_params["query_type"] = "semantic"
            search_params["semantic_configuration_name"] = "uta-semantic-config"
        
        try:
            results = self._search_client.search(**search_params)
            
            search_results = []
            for result in results:
                # Parse metadata
                metadata = {}
                if result.get("metadata"):
                    try:
                        metadata = json.loads(result["metadata"])
                    except json.JSONDecodeError:
                        pass
                
                # Parse doc_type
                try:
                    doc_type = DocumentType(result.get("doc_type", "kb_article"))
                except ValueError:
                    doc_type = DocumentType.KB_ARTICLE
                
                doc = Document(
                    id=result["id"],
                    content=result.get("content", ""),
                    metadata=metadata,
                    doc_type=doc_type
                )
                
                # Get score (Azure Search uses @search.score)
                score = result.get("@search.score", 0)
                # Normalize to 0-1 range
                normalized_score = min(score / 10, 1.0)
                
                # Get highlights if available
                highlights = None
                if "@search.highlights" in result:
                    highlights = result["@search.highlights"].get("content", [])
                
                search_results.append(SearchResult(
                    document=doc,
                    score=normalized_score,
                    highlights=highlights
                ))
            
            return search_results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        if not self._search_client:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        import json
        
        try:
            result = self._search_client.get_document(key=doc_id)
            
            if result:
                metadata = {}
                if result.get("metadata"):
                    try:
                        metadata = json.loads(result["metadata"])
                    except json.JSONDecodeError:
                        pass
                
                try:
                    doc_type = DocumentType(result.get("doc_type", "kb_article"))
                except ValueError:
                    doc_type = DocumentType.KB_ARTICLE
                
                return Document(
                    id=result["id"],
                    content=result.get("content", ""),
                    metadata=metadata,
                    doc_type=doc_type
                )
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
        
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if not self._search_client:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            self._search_client.delete_documents(documents=[{"id": doc_id}])
            logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all documents from the index."""
        if not self._search_client:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            # Get all document IDs
            results = self._search_client.search(
                search_text="*",
                select=["id"],
                top=1000  # May need pagination for larger datasets
            )
            
            doc_ids = [{"id": r["id"]} for r in results]
            
            if doc_ids:
                # Delete in batches
                batch_size = 100
                for i in range(0, len(doc_ids), batch_size):
                    batch = doc_ids[i:i + batch_size]
                    self._search_client.delete_documents(documents=batch)
                
                logger.info(f"Cleared {len(doc_ids)} documents from Azure AI Search")
            else:
                logger.info("No documents to clear")
                
        except Exception as e:
            logger.error(f"Error clearing index: {e}")
    
    def count(self) -> int:
        """Get document count."""
        if not self._search_client:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            results = self._search_client.search(
                search_text="*",
                include_total_count=True,
                top=0
            )
            return results.get_count() or 0
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0
