"""
ChromaDB Vector Store Implementation

Local vector database for development and POC.
Supports multiple embedding providers: Ollama (recommended), Sentence Transformers, or default.
"""

import math
import os
import logging
import requests
from typing import List, Dict, Any, Optional

from core.uta_vectorstore_base import (
    VectorStore,
    Document,
    SearchResult,
    DocumentType,
)

logger = logging.getLogger(__name__)


class OllamaEmbeddingFunction:
    """
    Custom embedding function that uses Ollama for generating embeddings.
    
    Ollama runs locally and supports embedding models like:
    - nomic-embed-text (recommended, 768 dimensions)
    - mxbai-embed-large (1024 dimensions)
    - all-minilm (384 dimensions)
    
    Setup:
        1. Install Ollama: https://ollama.ai
        2. Pull embedding model: ollama pull nomic-embed-text
        3. Ollama runs automatically on http://localhost:11434
    """
    
    def __init__(
        self,
        model_name: str = "nomic-embed-text",
        base_url: str = "http://localhost:11434",
    ):
        self.model_name = model_name
        self.base_url = base_url.rstrip("/")
        self._verify_connection()
    
    def name(self) -> str:
        """Return the name of this embedding function (required by ChromaDB)."""
        return f"ollama-{self.model_name}"
    
    def _verify_connection(self) -> None:
        """Verify Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m.get("name", "").split(":")[0] for m in models]
            
            if self.model_name not in model_names:
                logger.warning(
                    f"Model '{self.model_name}' not found in Ollama. "
                    f"Available models: {model_names}. "
                    f"Run: ollama pull {self.model_name}"
                )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts (used by ChromaDB for documents and queries)."""
        logger.debug(f"OllamaEmbeddingFunction.__call__ called with {len(input)} texts")
        return self._get_embeddings(input)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents (alias for __call__)."""
        logger.debug(f"OllamaEmbeddingFunction.embed_documents called with {len(texts)} texts")
        return self._get_embeddings(texts)
    
    def embed_query(self, text: str = None, *, input: str = None) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Accepts both positional 'text' argument and keyword 'input' argument
        for compatibility with different ChromaDB versions.
        """
        # Handle both 'text' and 'input' parameter names for compatibility
        query_text = text if text is not None else input
        if query_text is None:
            raise ValueError("Either 'text' or 'input' must be provided")
        logger.debug(f"OllamaEmbeddingFunction.embed_query called with text: {query_text[:50]}...")
        embeddings = self._get_embeddings([query_text])
        return embeddings[0] if embeddings else []
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Internal method to get embeddings from Ollama."""
        embeddings = []
        
        for text in texts:
            try:
                response = requests.post(
                    f"{self.base_url}/api/embeddings",
                    json={
                        "model": self.model_name,
                        "prompt": text,
                    },
                    timeout=60,
                )
                response.raise_for_status()
                embedding = response.json().get("embedding", [])
                embeddings.append(embedding)
            except requests.exceptions.RequestException as e:
                logger.error(f"Ollama embedding request failed: {e}")
                raise
        
        return embeddings


class ChromaVectorStore(VectorStore):
    """
    ChromaDB implementation of the VectorStore interface.
    
    Features:
    - Local storage (no cloud dependency)
    - Multiple embedding options: Azure OpenAI, Ollama, Sentence Transformers, or default
    - Persistent storage option
    - Fast similarity search
    
    Usage with Azure OpenAI (recommended for production):
        store = ChromaVectorStore(
            collection_name="uta_knowledge",
            persist_directory="./chroma_data",
            embedding_provider="azure_openai",
            embedding_model="text-embedding-3-large",
            azure_openai_endpoint="https://myresource.openai.azure.com/",
            azure_openai_key="your-api-key",
        )
        
    Usage with Ollama (recommended for local dev):
        store = ChromaVectorStore(
            collection_name="uta_knowledge",
            persist_directory="./chroma_data",
            embedding_provider="ollama",
            embedding_model="nomic-embed-text"
        )
        store.initialize()
        store.add_documents([doc1, doc2])
        results = store.search("calls not routing")
    """
    
    def __init__(
        self,
        collection_name: str = "uta_knowledge",
        persist_directory: Optional[str] = None,
        embedding_provider: str = "ollama",  # "azure_openai", "foundry", "ollama", "sentence_transformers", or "default"
        embedding_model: str = "nomic-embed-text",  # Azure: text-embedding-3-large, Ollama: nomic-embed-text
        ollama_base_url: str = "http://localhost:11434",
        # Azure OpenAI / Foundry settings
        azure_openai_endpoint: Optional[str] = None,
        azure_openai_key: Optional[str] = None,
        azure_openai_dimensions: Optional[int] = None,  # None = use model default
        use_foundry: Optional[bool] = None,  # None = auto-detect, True = use DefaultAzureCredential
    ):
        """
        Initialize ChromaDB vector store.
        
        Args:
            collection_name: Name of the collection to use
            persist_directory: Path to persist data (None for in-memory)
            embedding_provider: "azure_openai"/"foundry" (production), "ollama" (local), "sentence_transformers", or "default"
            embedding_model: Model/deployment name for the chosen provider
            ollama_base_url: Ollama server URL (default: http://localhost:11434)
            azure_openai_endpoint: Azure OpenAI/Foundry endpoint (or env vars)
            azure_openai_key: Azure OpenAI API key (not needed for Foundry)
            azure_openai_dimensions: Optional dimension reduction for embedding-3 models
            use_foundry: True to use Azure AI Foundry with DefaultAzureCredential
        """
        self.collection_name = collection_name
        self.persist_directory = persist_directory
        self.embedding_provider = embedding_provider
        self.embedding_model = embedding_model
        self.ollama_base_url = ollama_base_url
        # Azure OpenAI / Foundry settings
        self.azure_openai_endpoint = azure_openai_endpoint
        self.azure_openai_key = azure_openai_key
        self.azure_openai_dimensions = azure_openai_dimensions
        # Handle "foundry" as a provider alias
        if embedding_provider == "foundry":
            self.embedding_provider = "azure_openai"
            self.use_foundry = True
        else:
            self.use_foundry = use_foundry
        self._client = None
        self._collection = None
        self._embedding_function = None
    
    def initialize(self) -> None:
        """Initialize ChromaDB client and collection."""
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError(
                "ChromaDB not installed. Run: pip install chromadb"
            )
        
        logger.info(f"Initializing ChromaDB with collection: {self.collection_name}")
        
        # Configure client
        if self.persist_directory:
            # Persistent storage
            os.makedirs(self.persist_directory, exist_ok=True)
            self._client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info(f"Using persistent storage at: {self.persist_directory}")
        else:
            # In-memory storage
            self._client = chromadb.Client(
                settings=Settings(anonymized_telemetry=False)
            )
            logger.info("Using in-memory storage")
        
        # Set up embedding function
        self._setup_embedding_function()
        
        # Get or create collection
        self._collection = self._client.get_or_create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_function,
            metadata={"description": "UTA Knowledge Base"}
        )
        
        logger.info(f"ChromaDB initialized. Documents in collection: {self._collection.count()}")
    
    def _setup_embedding_function(self) -> None:
        """Set up the embedding function based on the configured provider."""
        
        if self.embedding_provider == "azure_openai":
            # Use Azure OpenAI / Foundry for embeddings (best quality, recommended for production)
            try:
                from core.uta_azure_openai_embeddings import AzureOpenAIEmbeddingFunction
                
                self._embedding_function = AzureOpenAIEmbeddingFunction(
                    endpoint=self.azure_openai_endpoint,
                    api_key=self.azure_openai_key,
                    deployment_name=self.embedding_model,
                    dimensions=self.azure_openai_dimensions,
                    use_foundry=self.use_foundry,
                )
                provider_name = "Azure AI Foundry" if self.use_foundry else "Azure OpenAI"
                logger.info(f"Using {provider_name} embeddings with deployment: {self.embedding_model}")
            except ImportError as e:
                logger.error(f"Failed to import Azure embeddings: {e}")
                raise
            except ValueError as e:
                logger.error(f"Azure configuration error: {e}")
                raise
        
        elif self.embedding_provider == "ollama":
            # Use Ollama for embeddings (recommended for local/dev)
            try:
                self._embedding_function = OllamaEmbeddingFunction(
                    model_name=self.embedding_model,
                    base_url=self.ollama_base_url,
                )
                logger.info(f"Using Ollama embeddings with model: {self.embedding_model}")
            except ConnectionError as e:
                logger.error(str(e))
                raise
                
        elif self.embedding_provider == "sentence_transformers":
            # Use sentence transformers (fallback)
            try:
                from chromadb.utils import embedding_functions
                self._embedding_function = embedding_functions.SentenceTransformerEmbeddingFunction(
                    model_name=self.embedding_model
                )
                logger.info(f"Using Sentence Transformers with model: {self.embedding_model}")
            except Exception as e:
                logger.warning(f"Could not load sentence transformer: {e}")
                self._embedding_function = None
                
        else:
            # Use default ChromaDB embedding function
            logger.info("Using default ChromaDB embedding function")
            self._embedding_function = None
    
    def add_documents(self, documents: List[Document]) -> List[str]:
        """Add documents to ChromaDB."""
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        if not documents:
            return []
        
        ids = []
        contents = []
        metadatas = []
        
        for doc in documents:
            ids.append(doc.id)
            contents.append(doc.content)
            
            # Prepare metadata (ChromaDB requires flat structure)
            metadata = {
                "doc_type": doc.doc_type.value,
                **{k: str(v) if not isinstance(v, (str, int, float, bool)) else v 
                   for k, v in doc.metadata.items()}
            }
            metadatas.append(metadata)
        
        # Add to collection
        self._collection.add(
            ids=ids,
            documents=contents,
            metadatas=metadatas
        )
        
        logger.info(f"Added {len(documents)} documents to ChromaDB")
        return ids
    
    def search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        doc_types: Optional[List[DocumentType]] = None,
    ) -> List[SearchResult]:
        """Search for similar documents."""
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        # Build where clause for filtering
        where = None
        where_conditions = []
        
        if filters:
            for key, value in filters.items():
                where_conditions.append({key: {"$eq": value}})
        
        if doc_types:
            type_values = [dt.value for dt in doc_types]
            if len(type_values) == 1:
                where_conditions.append({"doc_type": {"$eq": type_values[0]}})
            else:
                where_conditions.append({"doc_type": {"$in": type_values}})
        
        if len(where_conditions) == 1:
            where = where_conditions[0]
        elif len(where_conditions) > 1:
            where = {"$and": where_conditions}
        
        # Execute search - compute embedding manually to avoid ChromaDB internal issues
        try:
            # Generate query embedding using our embedding function
            if self._embedding_function:
                logger.info(f"Generating embedding for query: {query[:50]}...")
                query_embedding = self._embedding_function.embed_query(query)
                logger.info(f"Embedding generated, length: {len(query_embedding)}")
                results = self._collection.query(
                    query_embeddings=[query_embedding],
                    n_results=top_k,
                    where=where,
                    include=["documents", "metadatas", "distances"]
                )
                logger.info(f"ChromaDB query returned {len(results.get('ids', [[]])[0])} results")
            else:
                # Fallback to query_texts if no embedding function
                results = self._collection.query(
                    query_texts=[query],
                    n_results=top_k,
                    where=where,
                    include=["documents", "metadatas", "distances"]
                )
        except Exception as e:
            logger.error(f"Search error: {e} in query.")
            return []
        
        # Convert to SearchResult objects
        search_results = []
        
        if results and results["ids"] and results["ids"][0]:
            # Calculate score normalization based on distance distribution
            distances = results["distances"][0] if results["distances"] else []
            min_dist = min(distances) if distances else 0
            max_dist = max(distances) if distances else 1
            dist_range = max_dist - min_dist if max_dist > min_dist else 1
            
            for i, doc_id in enumerate(results["ids"][0]):
                # ChromaDB returns distances (L2), convert to similarity score
                distance = results["distances"][0][i] if results["distances"] else 0
                
                # Improved score conversion:
                # 1. Normalize distance to 0-1 range based on result set
                # 2. Use cosine-style conversion for embedding distances
                # For normalized embeddings, L2 distance range is roughly [0, 2]
                # We use a combination of relative ranking and absolute distance
                
                # Relative score within result set (ensures good relative ordering)
                if dist_range > 0:
                    relative_score = 1 - ((distance - min_dist) / dist_range)
                else:
                    relative_score = 1.0
                
                # Absolute score based on typical L2 distance range for embeddings
                # L2 distance of 0 = identical, ~1.4 = orthogonal, ~2 = opposite
                absolute_score = max(0, 1 - (distance / 2.0))
                
                # Combine both: use weighted average (favors relative ranking)
                score = 0.6 * relative_score + 0.4 * absolute_score
                score = max(0.0, min(1.0, score))  # Clamp to [0, 1]
                
                content = results["documents"][0][i] if results["documents"] else ""
                metadata = results["metadatas"][0][i] if results["metadatas"] else {}
                
                # Extract doc_type from metadata
                doc_type_str = metadata.pop("doc_type", "kb_article")
                try:
                    doc_type = DocumentType(doc_type_str)
                except ValueError:
                    doc_type = DocumentType.KB_ARTICLE
                
                doc = Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    doc_type=doc_type
                )
                
                search_results.append(SearchResult(
                    document=doc,
                    score=score
                ))
        
        logger.debug(f"Search for '{query[:50]}...' returned {len(search_results)} results")
        return search_results
    
    def get_document(self, doc_id: str) -> Optional[Document]:
        """Retrieve a document by ID."""
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            result = self._collection.get(
                ids=[doc_id],
                include=["documents", "metadatas"]
            )
            
            if result and result["ids"]:
                content = result["documents"][0] if result["documents"] else ""
                metadata = result["metadatas"][0] if result["metadatas"] else {}
                
                doc_type_str = metadata.pop("doc_type", "kb_article")
                try:
                    doc_type = DocumentType(doc_type_str)
                except ValueError:
                    doc_type = DocumentType.KB_ARTICLE
                
                return Document(
                    id=doc_id,
                    content=content,
                    metadata=metadata,
                    doc_type=doc_type
                )
        except Exception as e:
            logger.error(f"Error retrieving document {doc_id}: {e}")
        
        return None
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID."""
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        try:
            self._collection.delete(ids=[doc_id])
            logger.info(f"Deleted document: {doc_id}")
            return True
        except Exception as e:
            logger.error(f"Error deleting document {doc_id}: {e}")
            return False
    
    def clear(self) -> None:
        """Clear all documents from the collection."""
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        # Delete and recreate collection
        self._client.delete_collection(self.collection_name)
        self._collection = self._client.create_collection(
            name=self.collection_name,
            embedding_function=self._embedding_function,
            metadata={"description": "UTA Knowledge Base"}
        )
        logger.info("Cleared all documents from ChromaDB")
    
    def count(self) -> int:
        """Get document count."""
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        return self._collection.count()
    
    def get_all_ids(self) -> List[str]:
        """Get all document IDs in the collection."""
        if not self._collection:
            raise RuntimeError("Vector store not initialized. Call initialize() first.")
        
        result = self._collection.get(include=[])
        return result["ids"] if result else []
    
    def hybrid_search(
        self,
        query: str,
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None,
        doc_types: Optional[List[DocumentType]] = None,
        use_query_expansion: bool = True,
    ) -> List[SearchResult]:
        """
        Hybrid search combining semantic search with keyword matching and query expansion.
        
        This method:
        1. Expands the query into multiple semantic variations
        2. Extracts error codes and performs exact matching  
        3. Performs semantic search with multiple query variations
        4. Merges and re-ranks results using Reciprocal Rank Fusion (RRF)
        
        Args:
            query: Search query
            top_k: Number of results to return
            filters: Additional filters
            doc_types: Filter by document types
            use_query_expansion: Whether to use multi-query expansion
            
        Returns:
            List of SearchResult with improved relevance through fusion
        """
        import re
        
        # Extract potential error codes from query (patterns like ERR-XXX-NNN, LIC-NNN, etc.)
        error_code_pattern = r'\b(ERR-[A-Z]+-\d{3}|LIC-\d{3}|CONN-\d{3}|INT-\d{3}|API-\d{3})\b'
        error_codes = re.findall(error_code_pattern, query.upper())
        
        logger.debug(f"Extracted error codes from query: {error_codes}")
        
        # Get query variations for multi-query search
        queries_to_search = [query]
        if use_query_expansion:
            try:
                from core.uta_query_enhancer import QueryEnhancer
                enhancer = QueryEnhancer(use_llm=False)  # Rule-based for speed
                enhanced = enhancer.enhance(query)
                queries_to_search = enhanced.expanded_queries[:3]  # Limit to 3 queries
                logger.debug(f"Expanded query into {len(queries_to_search)} variations")
            except ImportError:
                logger.debug("Query enhancer not available, using original query")
        
        # Perform semantic search for each query variation
        all_results = []
        for q in queries_to_search:
            results = self.search(
                query=q,
                top_k=max(top_k * 2, 10),  # Get more results for fusion
                filters=filters,
                doc_types=doc_types,
            )
            all_results.append(results)
        
        # Use Reciprocal Rank Fusion to merge results from multiple queries
        result_map = self._reciprocal_rank_fusion(all_results)
        
        # Handle keyword matches for error codes
        if error_codes:
            for code in error_codes:
                doc_id = f"error_codes_error_{code}"
                doc = self.get_document(doc_id)
                if doc:
                    if doc_id in result_map:
                        # Boost existing result
                        existing_score = result_map[doc_id]["score"]
                        result_map[doc_id]["score"] = min(existing_score + 0.3, 1.0)
                    else:
                        # Add new result with high score
                        result_map[doc_id] = {
                            "document": doc,
                            "score": 0.85  # High score for direct keyword match
                        }
                    logger.debug(f"Applied keyword boost for {code}")
        
        # Convert to SearchResult and sort
        final_results = [
            SearchResult(document=r["document"], score=r["score"])
            for r in result_map.values()
        ]
        final_results.sort(key=lambda x: x.score, reverse=True)
        
        return final_results[:top_k]
    
    def _reciprocal_rank_fusion(
        self,
        result_lists: List[List[SearchResult]],
        k: int = 60,
    ) -> Dict[str, Dict]:
        """
        Merge multiple ranked lists using Reciprocal Rank Fusion (RRF).
        
        RRF is a robust fusion method that combines rankings from multiple
        queries or retrieval methods. It's less sensitive to score scaling issues.
        
        Formula: score(d) = sum(1 / (k + rank(d, q))) for each query q
        
        Args:
            result_lists: List of result lists from different queries
            k: Constant to prevent high scores for top-ranked docs (default 60)
            
        Returns:
            Dictionary mapping doc_id to {document, score}
        """
        fused_scores: Dict[str, Dict] = {}
        
        for results in result_lists:
            for rank, result in enumerate(results, 1):
                doc_id = result.document.id
                rrf_score = 1.0 / (k + rank)
                
                if doc_id in fused_scores:
                    fused_scores[doc_id]["score"] += rrf_score
                else:
                    fused_scores[doc_id] = {
                        "document": result.document,
                        "score": rrf_score,
                    }
        
        # Normalize scores to 0-1 range
        if fused_scores:
            max_score = max(r["score"] for r in fused_scores.values())
            for doc_id in fused_scores:
                fused_scores[doc_id]["score"] /= max_score
        
        return fused_scores
