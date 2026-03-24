"""
Vector Store Factory

Creates the appropriate vector store implementation based on configuration.
Enables seamless switching between backends with a single config change.
"""

import os
import logging
from typing import Optional, Dict, Any

from core.uta_vectorstore_base import VectorStore

logger = logging.getLogger(__name__)


class VectorStoreFactory:
    """
    Factory class for creating vector store instances.
    
    Supported providers:
    - chroma: Local ChromaDB (default, best for development)
    - cosmos: Azure Cosmos DB with vector search
    - azure_search: Azure AI Search (best for production)
    
    Usage:
        # From config dict
        store = VectorStoreFactory.create(
            provider="chroma",
            config={"persist_directory": "./data/chroma"}
        )
        
        # From environment variables
        store = VectorStoreFactory.from_env()
    """
    
    PROVIDERS = ["chroma", "cosmos", "azure_search"]
    
    @classmethod
    def create(
        cls,
        provider: str = "chroma",
        config: Optional[Dict[str, Any]] = None,
        auto_initialize: bool = True,
    ) -> VectorStore:
        """
        Create a vector store instance.
        
        Args:
            provider: The provider to use (chroma, cosmos, azure_search)
            config: Provider-specific configuration
            auto_initialize: Whether to call initialize() automatically
            
        Returns:
            VectorStore instance
            
        Raises:
            ValueError: If provider is not supported
        """
        config = config or {}
        provider = provider.lower()
        
        if provider not in cls.PROVIDERS:
            raise ValueError(
                f"Unknown provider: {provider}. "
                f"Supported providers: {cls.PROVIDERS}"
            )
        
        logger.info(f"Creating vector store with provider: {provider}")
        
        if provider == "chroma":
            store = cls._create_chroma(config)
        elif provider == "cosmos":
            store = cls._create_cosmos(config)
        elif provider == "azure_search":
            store = cls._create_azure_search(config)
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        if auto_initialize:
            store.initialize()
        
        return store
    
    @classmethod
    def from_env(cls, auto_initialize: bool = True) -> VectorStore:
        """
        Create a vector store from environment variables.
        
        Environment Variables:
            UTA_VECTOR_PROVIDER: Provider name (default: chroma)
            
            For ChromaDB:
                CHROMA_PERSIST_DIR: Persistence directory
                CHROMA_COLLECTION: Collection name
                
            For Cosmos DB:
                COSMOS_ENDPOINT: Cosmos DB endpoint
                COSMOS_KEY: Cosmos DB key
                COSMOS_DATABASE: Database name
                COSMOS_CONTAINER: Container name
                
            For Azure AI Search:
                AZURE_SEARCH_ENDPOINT: Search endpoint
                AZURE_SEARCH_KEY: Search admin key
                AZURE_SEARCH_INDEX: Index name
                
        Returns:
            VectorStore instance
        """
        provider = os.getenv("UTA_VECTOR_PROVIDER", "chroma").lower()
        
        if provider == "chroma":
            embedding_provider = os.getenv("EMBEDDING_PROVIDER", "ollama")
            use_foundry = os.getenv("USE_FOUNDRY", "").lower() == "true"
            
            config = {
                "persist_directory": os.getenv("CHROMA_PERSIST_DIR", "./data/chroma"),
                "collection_name": os.getenv("CHROMA_COLLECTION", "uta_knowledge"),
                "embedding_provider": embedding_provider,
                "embedding_model": os.getenv("EMBEDDING_MODEL", "nomic-embed-text"),
                "ollama_base_url": os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
            }
            # Add Azure OpenAI / Foundry settings if using Azure embeddings
            if embedding_provider in ("azure_openai", "foundry") or use_foundry:
                config.update({
                    "embedding_provider": "azure_openai",
                    "embedding_model": os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large"),
                    "azure_openai_endpoint": os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT"),
                    "azure_openai_key": os.getenv("AZURE_OPENAI_API_KEY"),  # None for Foundry
                    "azure_openai_dimensions": int(os.getenv("AZURE_OPENAI_EMBEDDING_DIMENSIONS", "0")) or None,
                    "use_foundry": use_foundry or embedding_provider == "foundry",
                })
        elif provider == "cosmos":
            config = {
                "endpoint": os.getenv("COSMOS_ENDPOINT"),
                "key": os.getenv("COSMOS_KEY"),
                "database_name": os.getenv("COSMOS_DATABASE", "uta"),
                "container_name": os.getenv("COSMOS_CONTAINER", "knowledge"),
            }
        elif provider == "azure_search":
            config = {
                "endpoint": os.getenv("AZURE_SEARCH_ENDPOINT"),
                "api_key": os.getenv("AZURE_SEARCH_KEY"),
                "index_name": os.getenv("AZURE_SEARCH_INDEX", "uta-knowledge"),
            }
        else:
            raise ValueError(f"Unknown provider: {provider}")
        
        return cls.create(provider, config, auto_initialize)
    
    @classmethod
    def from_yaml_config(cls, config: Dict[str, Any], auto_initialize: bool = True) -> VectorStore:
        """
        Create a vector store from a YAML config dictionary.
        
        Expected format:
            vector_store:
                provider: chroma
                chroma:
                    persist_directory: ./data/chroma
                    collection_name: uta_knowledge
                cosmos:
                    endpoint: https://...
                    # etc.
                azure_search:
                    endpoint: https://...
                    # etc.
                    
        Args:
            config: Configuration dictionary
            auto_initialize: Whether to call initialize() automatically
            
        Returns:
            VectorStore instance
        """
        vs_config = config.get("vector_store", {})
        provider = vs_config.get("provider", "chroma")
        provider_config = vs_config.get(provider, {})
        
        return cls.create(provider, provider_config, auto_initialize)
    
    @classmethod
    def _create_chroma(cls, config: Dict[str, Any]) -> VectorStore:
        """Create ChromaDB vector store."""
        from core.uta_chroma_store import ChromaVectorStore
        
        return ChromaVectorStore(
            collection_name=config.get("collection_name", "uta_knowledge"),
            persist_directory=config.get("persist_directory"),
            embedding_provider=config.get("embedding_provider", "ollama"),
            embedding_model=config.get("embedding_model", "nomic-embed-text"),
            ollama_base_url=config.get("ollama_base_url", "http://localhost:11434"),
            # Azure OpenAI / Foundry settings
            azure_openai_endpoint=config.get("azure_openai_endpoint"),
            azure_openai_key=config.get("azure_openai_key"),
            azure_openai_dimensions=config.get("azure_openai_dimensions"),
            use_foundry=config.get("use_foundry"),
        )
    
    @classmethod
    def _create_cosmos(cls, config: Dict[str, Any]) -> VectorStore:
        """Create Cosmos DB vector store."""
        from core.uta_cosmos_store import CosmosVectorStore
        
        return CosmosVectorStore(
            endpoint=config.get("endpoint"),
            key=config.get("key"),
            database_name=config.get("database_name", "uta"),
            container_name=config.get("container_name", "knowledge"),
            embedding_model=config.get("embedding_model", "text-embedding-ada-002"),
        )
    
    @classmethod
    def _create_azure_search(cls, config: Dict[str, Any]) -> VectorStore:
        """Create Azure AI Search vector store."""
        from core.uta_azure_search_store import AzureAISearchStore
        
        return AzureAISearchStore(
            endpoint=config.get("endpoint"),
            api_key=config.get("api_key"),
            index_name=config.get("index_name", "uta-knowledge"),
            embedding_model=config.get("embedding_model", "text-embedding-ada-002"),
            use_semantic_search=config.get("use_semantic_search", True),
        )
    
    @classmethod
    def get_available_providers(cls) -> Dict[str, str]:
        """
        Get information about available providers.
        
        Returns:
            Dict mapping provider names to descriptions
        """
        return {
            "chroma": "Local ChromaDB - Best for development, zero cloud dependency",
            "cosmos": "Azure Cosmos DB - Azure-native, moderate scale",
            "azure_search": "Azure AI Search - Enterprise-grade, hybrid search",
        }
