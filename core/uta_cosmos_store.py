"""
Azure Cosmos DB Vector Store Implementation

Uses Cosmos DB for NoSQL with vector search capability.
Suitable for Azure-native deployments with moderate scale.
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


class CosmosVectorStore(VectorStore):
    """
    Azure Cosmos DB implementation of the VectorStore interface.
    
    Features:
    - Azure-native integration
    - Combined document + vector storage
    - Automatic scaling
    - Global distribution capability
    
    Prerequisites:
    - Azure Cosmos DB account with vector search enabled
    - Database and container created with vector index
    
    Usage:
        store = CosmosVectorStore(
            endpoint="https://your-account.documents.azure.com:443/",
            key="your-key",
            database_name="uta",
            container_name="knowledge"
        )
        store.initialize()
        store.add_documents([doc1, doc2])
        results = store.search("calls not routing")
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        key: Optional[str] = None,
        database_name: str = "uta",
        container_name: str = "knowledge",
        embedding_model: str = "text-embedding-ada-002",
    ):
        """
        Initialize Cosmos DB vector store.
        
        Args:
            endpoint: Cosmos DB endpoint URL
            key: Cosmos DB access key
            database_name: Name of the database
            container_name: Name of the container
            embedding_model: Azure OpenAI embedding model name
        """
        self.endpoint = endpoint
        self.key = key
        self.database_name = database_name
        self.container_name = container_name
        self.embedding_model = embedding_model
        
        self._client = None
        self._database = None
        self._container = None
        self._embedding_client = None
    
    def initialize(self) -> None:
        """Initialize Cosmos DB client and container."""
        # Check for required dependencies
        try:
            from azure.cosmos import CosmosClient, PartitionKey
            from azure.cosmos.exceptions import CosmosResourceExistsError
        except ImportError:
            raise ImportError(
                "Azure Cosmos DB SDK not installed. Run: pip install azure-cosmos"
            )
        
        if not self.endpoint or not self.key:
            raise ValueError(
                "Cosmos DB endpoint and key are required. "
                "Set COSMOS_ENDPOINT and COSMOS_KEY environment variables "
                "or pass them to the constructor."
            )
        
        logger.info(f"Initializing Cosmos DB connection to: {self.endpoint}")
        
        # Create client
        self._client = CosmosClient(self.endpoint, credential=self.key)
        
        # Get or create database
        self._database = self._client.create_database_if_not_exists(
            id=self.database_name
        )
        logger.info(f"Using database: {self.database_name}")
        
        # Get or create container with vector index
        # Note: Vector index configuration should be set up in Azure Portal
        # or via ARM template for proper DiskANN index
        try:
            self._container = self._database.create_container_if_not_exists(
                id=self.container_name,
                partition_key=PartitionKey(path="/doc_type"),
                offer_throughput=400  # Minimum RU/s for dev
            )
        except CosmosResourceExistsError:
            self._container = self._database.get_container_client(self.container_name)
        
        logger.info(f"Using container: {self.container_name}")
        
        # Initialize embedding client
        self._setup_embedding_client()
        
        logger.info("Cosmos DB vector store initialized successfully")
    
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
                    "Embeddings will not be generated."
                )
        except ImportError:
            logger.warning("OpenAI SDK not installed. Embeddings will not be generated.")
    
    def _generate_embedding(self, text: str) -> Optional[List[float]]:
        """Generate embedding vector for text."""
        if not self._embedding_client:
            logger.warning("Embedding client not available")
            return None
        
        try:
            response = self._embedding_client.embeddings.create(
                model=self.embedding_model,
                input=text
            )
            return response.data[0].embedding
        except Exception as e:
            logger.error(f"Error generating embedding: {e}")
            return None
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to Cosmos DB."""
        if not self._container:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        added_ids = []
        
        for doc in documents:
            # Generate embedding
            embedding = doc.embedding or self._generate_embedding(doc.content)
            
            # Prepare document for Cosmos DB
            cosmos_doc = {
                "id": doc.id,
                "content": doc.content,
                "doc_type": doc.doc_type.value,
                "metadata": doc.metadata,
                "embedding": embedding,
            }
            
            try:
                self._container.upsert_item(cosmos_doc)
                added_ids.append(doc.id)
                logger.debug(f"Added document: {doc.id}")
            except Exception as e:
                logger.error(f"Error adding document {doc.id}: {e}")
        
        logger.info(f"Added {len(added_ids)} documents to Cosmos DB")
        return added_ids
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        doc_types: Optional[List[DocumentType]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents using vector search."""
        if not self._container:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        # Generate query embedding
        query_embedding = self._generate_embedding(query)
        if not query_embedding:
            logger.error("Could not generate query embedding")
            return []
        
        # Build query with vector search
        # Note: This uses Cosmos DB vector search syntax
        # Actual implementation may vary based on your vector index configuration
        
        # Build filter conditions
        filter_conditions = []
        if doc_types:
            type_values = [dt.value for dt in doc_types]
            type_filter = " OR ".join([f"c.doc_type = '{t}'" for t in type_values])
            filter_conditions.append(f"({type_filter})")
        
        if filters:
            for key, value in filters.items():
                filter_conditions.append(f"c.metadata.{key} = '{value}'")
        
        where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"
        
        # Vector search query using VectorDistance function
        query_text = f"""
            SELECT TOP {top_k}
                c.id,
                c.content,
                c.doc_type,
                c.metadata,
                VectorDistance(c.embedding, @queryVector) AS score
            FROM c
            WHERE {where_clause}
            ORDER BY VectorDistance(c.embedding, @queryVector)
        """
        
        try:
            results = list(self._container.query_items(
                query=query_text,
                parameters=[{"name": "@queryVector", "value": query_embedding}],
                enable_cross_partition_query=True
            ))
        except Exception as e:
            logger.error(f"Vector search error: {e}")
            # Fallback to regular query if vector search fails
            logger.info("Falling back to text-based search")
            return self._fallback_search(query, top_k, filters, doc_types)
        
        # Convert to SearchResult objects
        search_results = []
        for item in results:
            try:
                doc_type = DocumentType(item.get("doc_type", "kb_article"))
            except ValueError:
                doc_type = DocumentType.KB_ARTICLE
            
            doc = Document(
                id=item["id"],
                content=item["content"],
                metadata=item.get("metadata", {}),
                doc_type=doc_type
            )
            
            # VectorDistance returns distance, convert to similarity
            distance = item.get("score", 1.0)
            score = 1 / (1 + distance)
            
            search_results.append(SearchResult(document=doc, score=score))
        
        return search_results
    
    def _fallback_search(
        self,
        query: str,
        top_k: int,
        filters: Optional[Dict[str, Any]],
        doc_types: Optional[List[DocumentType]],
    ) -> List[SearchResult]:
        """Fallback text-based search when vector search is unavailable."""
        # Build filter conditions
        filter_conditions = []
        if doc_types:
            type_values = [dt.value for dt in doc_types]
            type_filter = " OR ".join([f"c.doc_type = '{t}'" for t in type_values])
            filter_conditions.append(f"({type_filter})")
        
        if filters:
            for key, value in filters.items():
                filter_conditions.append(f"c.metadata.{key} = '{value}'")
        
        where_clause = " AND ".join(filter_conditions) if filter_conditions else "1=1"
        
        # Simple CONTAINS search
        query_text = f"""
            SELECT TOP {top_k} c.id, c.content, c.doc_type, c.metadata
            FROM c
            WHERE {where_clause} AND CONTAINS(LOWER(c.content), LOWER(@searchTerm))
        """
        
        try:
            results = list(self._container.query_items(
                query=query_text,
                parameters=[{"name": "@searchTerm", "value": query.lower()}],
                enable_cross_partition_query=True
            ))
            
            search_results = []
            for i, item in enumerate(results):
                try:
                    doc_type = DocumentType(item.get("doc_type", "kb_article"))
                except ValueError:
                    doc_type = DocumentType.KB_ARTICLE
                
                doc = Document(
                    id=item["id"],
                    content=item["content"],
                    metadata=item.get("metadata", {}),
                    doc_type=doc_type
                )
                
                # Simple relevance score based on position
                score = 1.0 - (i * 0.1)
                search_results.append(SearchResult(document=doc, score=max(score, 0.1)))
            
            return search_results
        except Exception as e:
            logger.error(f"Fallback search error: {e}")
            return []
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        if not self._container:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            # Query across partitions to find the document
            query = "SELECT * FROM c WHERE c.id = @id"
            results = list(self._container.query_items(
                query=query,
                parameters=[{"name": "@id", "value": doc_id}],
                enable_cross_partition_query=True
            ))
            
            if results:
                item = results[0]
                try:
                    doc_type = DocumentType(item.get("doc_type", "kb_article"))
                except ValueError:
                    doc_type = DocumentType.KB_ARTICLE
                
                return Document(
                    id=item["id"],
                    content=item["content"],
                    metadata=item.get("metadata", {}),
                    doc_type=doc_type
                )
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
        
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if not self._container:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            # First find the document to get its partition key
            doc = self.get_document(doc_id)
            if doc:
                self._container.delete_item(
                    item=doc_id,
                    partition_key=doc.doc_type.value
                )
                logger.info(f"Deleted document: {doc_id}")
                return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
        
        return False
    
    def clear(self) -> None:
        """Clear all documents from the container."""
        if not self._container:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            # Query all document IDs
            query = "SELECT c.id, c.doc_type FROM c"
            items = list(self._container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            
            # Delete each document
            for item in items:
                try:
                    self._container.delete_item(
                        item=item["id"],
                        partition_key=item["doc_type"]
                    )
                except Exception as e:
                    logger.warning(f"Error deleting {item['id']}: {e}")
            
            logger.info(f"Cleared {len(items)} documents from Cosmos DB")
        except Exception as e:
            logger.error(f"Error clearing container: {e}")
    
    def count(self) -> int:
        """Get document count."""
        if not self._container:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            query = "SELECT VALUE COUNT(1) FROM c"
            results = list(self._container.query_items(
                query=query,
                enable_cross_partition_query=True
            ))
            return results[0] if results else 0
        except Exception as e:
            logger.error(f"Error getting count: {e}")
            return 0
