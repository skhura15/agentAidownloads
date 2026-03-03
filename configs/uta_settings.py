"""
UTA Configuration Settings

Handles loading and validation of configuration from YAML files and environment variables.
"""

import os
import re
from pathlib import Path
from typing import Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class VectorStoreConfig:
    """Vector store configuration."""
    provider: str = "chroma"
    collection_name: str = "uta_knowledge"
    persist_directory: str = "./data/chroma"
    embedding_model: str = "all-MiniLM-L6-v2"
    # Cosmos DB
    cosmos_endpoint: Optional[str] = None
    cosmos_key: Optional[str] = None
    cosmos_database: str = "uta"
    cosmos_container: str = "knowledge"
    # Azure AI Search
    azure_search_endpoint: Optional[str] = None
    azure_search_key: Optional[str] = None
    azure_search_index: str = "uta-knowledge"
    use_semantic_search: bool = True


@dataclass
class IngestionConfig:
    """Document ingestion configuration."""
    chunk_size: int = 1000
    chunk_overlap: int = 200
    min_chunk_size: int = 100
    supported_extensions: list = field(default_factory=lambda: [".md", ".json", ".yaml", ".yml", ".txt"])


@dataclass 
class AzureOpenAIConfig:
    """Azure OpenAI configuration."""
    endpoint: Optional[str] = None
    api_key: Optional[str] = None
    api_version: str = "2024-02-01"
    embeddings_deployment: str = "text-embedding-ada-002"
    chat_deployment: str = "gpt-4"
    temperature: float = 0.3
    max_tokens: int = 4000


@dataclass
class SearchConfig:
    """Search configuration."""
    default_top_k: int = 5
    max_top_k: int = 20
    min_score_threshold: float = 0.3


@dataclass
class APIConfig:
    """API server configuration."""
    host: str = "0.0.0.0"
    port: int = 8000
    cors_origins: list = field(default_factory=lambda: ["http://localhost:3000", "http://localhost:5173"])


@dataclass
class UTAConfig:
    """Main UTA configuration."""
    app_name: str = "Unified Troubleshooting Assistant"
    version: str = "0.1.0"
    debug: bool = True
    log_level: str = "INFO"
    
    vector_store: VectorStoreConfig = field(default_factory=VectorStoreConfig)
    ingestion: IngestionConfig = field(default_factory=IngestionConfig)
    azure_openai: AzureOpenAIConfig = field(default_factory=AzureOpenAIConfig)
    search: SearchConfig = field(default_factory=SearchConfig)
    api: APIConfig = field(default_factory=APIConfig)
    
    knowledge_base_path: str = "./uta/knowledge"


def _resolve_env_vars(value: str) -> str:
    """Replace ${VAR} patterns with environment variable values."""
    if not isinstance(value, str):
        return value
    
    pattern = r'\$\{(\w+)\}'
    
    def replace(match):
        var_name = match.group(1)
        return os.getenv(var_name, "")
    
    return re.sub(pattern, replace, value)


def _process_config_dict(config: Dict[str, Any]) -> Dict[str, Any]:
    """Recursively process config dict to resolve environment variables."""
    result = {}
    for key, value in config.items():
        if isinstance(value, dict):
            result[key] = _process_config_dict(value)
        elif isinstance(value, list):
            result[key] = [_resolve_env_vars(v) if isinstance(v, str) else v for v in value]
        elif isinstance(value, str):
            result[key] = _resolve_env_vars(value)
        else:
            result[key] = value
    return result


def load_config(config_path: Optional[str] = None) -> UTAConfig:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Path to config file. If None, looks for:
            1. UTA_CONFIG environment variable
            2. ./configs/uta.config.dev.yaml
            3. ./configs/uta.config.yaml
            
    Returns:
        UTAConfig instance
    """
    # Determine config path
    if config_path is None:
        config_path = os.getenv("UTA_CONFIG")
    
    if config_path is None:
        # Look for default config files
        candidates = [
            "./configs/uta.config.dev.yaml",
            "./configs/uta.config.yaml",
            "./config.yaml",
        ]
        for candidate in candidates:
            if Path(candidate).exists():
                config_path = candidate
                break
    
    if config_path and Path(config_path).exists():
        try:
            import yaml
            
            with open(config_path, "r") as f:
                raw_config = yaml.safe_load(f)
            
            # Process environment variables
            config_dict = _process_config_dict(raw_config or {})
            
            return _dict_to_config(config_dict)
            
        except ImportError:
            print("PyYAML not installed. Using default configuration.")
        except Exception as e:
            print(f"Error loading config from {config_path}: {e}")
    
    # Return default config
    return UTAConfig()


def _dict_to_config(config_dict: Dict[str, Any]) -> UTAConfig:
    """Convert config dictionary to UTAConfig object."""
    config = UTAConfig()
    
    # App settings
    app = config_dict.get("app", {})
    config.app_name = app.get("name", config.app_name)
    config.version = app.get("version", config.version)
    config.debug = app.get("debug", config.debug)
    config.log_level = app.get("log_level", config.log_level)
    
    # Vector store settings
    vs = config_dict.get("vector_store", {})
    config.vector_store.provider = vs.get("provider", config.vector_store.provider)
    
    chroma = vs.get("chroma", {})
    config.vector_store.collection_name = chroma.get("collection_name", config.vector_store.collection_name)
    config.vector_store.persist_directory = chroma.get("persist_directory", config.vector_store.persist_directory)
    config.vector_store.embedding_model = chroma.get("embedding_model", config.vector_store.embedding_model)
    
    cosmos = vs.get("cosmos", {})
    config.vector_store.cosmos_endpoint = cosmos.get("endpoint")
    config.vector_store.cosmos_key = cosmos.get("key")
    config.vector_store.cosmos_database = cosmos.get("database_name", config.vector_store.cosmos_database)
    config.vector_store.cosmos_container = cosmos.get("container_name", config.vector_store.cosmos_container)
    
    azure_search = vs.get("azure_search", {})
    config.vector_store.azure_search_endpoint = azure_search.get("endpoint")
    config.vector_store.azure_search_key = azure_search.get("api_key")
    config.vector_store.azure_search_index = azure_search.get("index_name", config.vector_store.azure_search_index)
    config.vector_store.use_semantic_search = azure_search.get("use_semantic_search", config.vector_store.use_semantic_search)
    
    # Ingestion settings
    ing = config_dict.get("ingestion", {})
    config.ingestion.chunk_size = ing.get("chunk_size", config.ingestion.chunk_size)
    config.ingestion.chunk_overlap = ing.get("chunk_overlap", config.ingestion.chunk_overlap)
    config.ingestion.min_chunk_size = ing.get("min_chunk_size", config.ingestion.min_chunk_size)
    
    # Azure OpenAI settings
    aoai = config_dict.get("azure_openai", {})
    config.azure_openai.endpoint = aoai.get("endpoint")
    config.azure_openai.api_key = aoai.get("api_key")
    config.azure_openai.api_version = aoai.get("api_version", config.azure_openai.api_version)
    config.azure_openai.embeddings_deployment = aoai.get("embeddings_deployment", config.azure_openai.embeddings_deployment)
    config.azure_openai.chat_deployment = aoai.get("chat_deployment", config.azure_openai.chat_deployment)
    config.azure_openai.temperature = aoai.get("temperature", config.azure_openai.temperature)
    config.azure_openai.max_tokens = aoai.get("max_tokens", config.azure_openai.max_tokens)
    
    # Search settings
    search = config_dict.get("search", {})
    config.search.default_top_k = search.get("default_top_k", config.search.default_top_k)
    config.search.max_top_k = search.get("max_top_k", config.search.max_top_k)
    config.search.min_score_threshold = search.get("min_score_threshold", config.search.min_score_threshold)
    
    # API settings
    api = config_dict.get("api", {})
    config.api.host = api.get("host", config.api.host)
    config.api.port = api.get("port", config.api.port)
    config.api.cors_origins = api.get("cors_origins", config.api.cors_origins)
    
    # Knowledge base path
    knowledge = config_dict.get("knowledge", {})
    config.knowledge_base_path = knowledge.get("base_path", config.knowledge_base_path)
    
    return config
