"""
Azure OpenAI / Azure AI Foundry Embedding Function

Provides high-quality embeddings using Azure OpenAI or Azure AI Foundry.
Supports both deployment models:
- Azure OpenAI: Direct Azure OpenAI Service endpoint
- Azure AI Foundry: Project-based inference endpoint

Models available:
- text-embedding-3-large: 3072 dimensions, best quality
- text-embedding-3-small: 1536 dimensions, good balance of quality/cost
- text-embedding-ada-002: 1536 dimensions, legacy model

Setup for Azure AI Foundry:
1. Create/access your Azure AI Foundry project
2. Deploy an embedding model (text-embedding-3-large recommended)
3. Set environment variables:
   - FOUNDRY_PROJECT_ENDPOINT: https://<project>.inference.ai.azure.com/
   - AZURE_OPENAI_EMBEDDING_DEPLOYMENT: your-deployment-name
   (Uses DefaultAzureCredential - no API key needed)

Setup for Azure OpenAI:
1. Create Azure OpenAI resource in Azure Portal
2. Deploy an embedding model
3. Set environment variables:
   - AZURE_OPENAI_ENDPOINT: https://<resource>.openai.azure.com/
   - AZURE_OPENAI_API_KEY: your-api-key
   - AZURE_OPENAI_EMBEDDING_DEPLOYMENT: your-deployment-name
"""

import os
import logging
from typing import List, Optional
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class AzureOpenAIEmbeddingConfig:
    """Configuration for Azure OpenAI/Foundry embeddings."""
    endpoint: str
    deployment_name: str
    api_key: Optional[str] = None  # None = use DefaultAzureCredential (Foundry)
    api_version: str = "2024-02-01"
    dimensions: Optional[int] = None  # None = use model default (3072 for large)
    batch_size: int = 16  # Max texts per API call
    timeout: int = 60
    use_foundry: bool = False  # True for Foundry, False for Azure OpenAI


class AzureOpenAIEmbeddingFunction:
    """
    Azure OpenAI / Azure AI Foundry embedding function compatible with ChromaDB.
    
    Supports both Azure OpenAI and Azure AI Foundry endpoints.
    Uses the official openai package with Azure configuration.
    Provides significantly better embedding quality than local models.
    
    Usage with Azure AI Foundry (recommended):
        embedding_fn = AzureOpenAIEmbeddingFunction(
            endpoint="https://your-project.inference.ai.azure.com/",
            deployment_name="text-embedding-3-large",
            use_foundry=True,  # Uses DefaultAzureCredential
        )
    
    Usage with Azure OpenAI:
        embedding_fn = AzureOpenAIEmbeddingFunction(
            endpoint="https://myresource.openai.azure.com/",
            api_key="your-key",
            deployment_name="text-embedding-3-large",
        )
        
        # For ChromaDB
        collection = client.create_collection(
            name="my_collection",
            embedding_function=embedding_fn,
        )
        
        # Direct usage
        embeddings = embedding_fn(["text1", "text2"])
        query_embedding = embedding_fn.embed_query("search query")
    """
    
    def __init__(
        self,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        deployment_name: Optional[str] = None,
        api_version: str = "2024-02-01",
        dimensions: Optional[int] = None,
        batch_size: int = 16,
        timeout: int = 60,
        use_foundry: Optional[bool] = None,  # None = auto-detect
    ):
        """
        Initialize Azure OpenAI/Foundry embedding function.
        
        Args:
            endpoint: Azure endpoint URL. For Foundry: FOUNDRY_PROJECT_ENDPOINT, 
                      For Azure OpenAI: AZURE_OPENAI_ENDPOINT
            api_key: API key (only for Azure OpenAI, Foundry uses DefaultAzureCredential)
            deployment_name: Deployment name (AZURE_OPENAI_EMBEDDING_DEPLOYMENT env var)
            api_version: API version to use
            dimensions: Output dimensions (None = model default)
            batch_size: Max texts per API call
            timeout: Request timeout in seconds
            use_foundry: True for Foundry (DefaultAzureCredential), False for Azure OpenAI (API key)
                        None = auto-detect based on endpoint or USE_FOUNDRY env var
        """
        # Detect endpoint - prefer Foundry if available
        self.endpoint = endpoint or os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("FOUNDRY_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
        self.deployment_name = deployment_name or os.getenv("AZURE_OPENAI_EMBEDDING_DEPLOYMENT", "text-embedding-3-large")
        self.api_version = api_version
        self.dimensions = dimensions
        self.batch_size = batch_size
        self.timeout = timeout
        
        # Auto-detect Foundry vs Azure OpenAI
        if use_foundry is None:
            use_foundry_env = os.getenv("USE_FOUNDRY", "").lower()
            if use_foundry_env == "true":
                self.use_foundry = True
            elif use_foundry_env == "false":
                self.use_foundry = False
            elif self.endpoint and "inference.ai.azure.com" in self.endpoint:
                self.use_foundry = True
            else:
                self.use_foundry = False
        else:
            self.use_foundry = use_foundry
        
        self._client = None
        self._validate_config()
        self._init_client()
    
    def _validate_config(self) -> None:
        """Validate configuration."""
        if not self.endpoint:
            raise ValueError(
                "Azure endpoint not provided. "
                "Set FOUNDRY_PROJECT_ENDPOINT (for Foundry) or AZURE_OPENAI_ENDPOINT (for Azure OpenAI)."
            )
        if not self.use_foundry and not self.api_key:
            raise ValueError(
                "Azure OpenAI API key not provided. "
                "Set AZURE_OPENAI_API_KEY environment variable or use Foundry with USE_FOUNDRY=true."
            )
        # For Foundry: API key is optional (can use DefaultAzureCredential or API key)
        if not self.deployment_name:
            raise ValueError(
                "Embedding deployment name not provided. "
                "Set AZURE_OPENAI_EMBEDDING_DEPLOYMENT environment variable."
            )
    
    def _init_client(self) -> None:
        """Initialize the Azure OpenAI client."""
        try:
            from openai import AzureOpenAI
            
            if self.use_foundry and not self.api_key:
                # Azure AI Foundry without API key - use DefaultAzureCredential
                try:
                    from azure.identity import DefaultAzureCredential, get_bearer_token_provider
                    
                    credential = DefaultAzureCredential()
                    token_provider = get_bearer_token_provider(
                        credential, 
                        "https://cognitiveservices.azure.com/.default"
                    )
                    
                    self._client = AzureOpenAI(
                        azure_endpoint=self.endpoint,
                        azure_ad_token_provider=token_provider,
                        api_version=self.api_version,
                        timeout=self.timeout,
                    )
                    logger.info(f"Azure AI Foundry client initialized with DefaultAzureCredential: {self.deployment_name}")
                    
                except ImportError:
                    raise ImportError(
                        "azure-identity package not installed. Run: pip install azure-identity"
                    )
            else:
                # Azure OpenAI or Foundry with API key - use API key auth
                self._client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version,
                    timeout=self.timeout,
                )
                provider = "Azure AI Foundry" if self.use_foundry else "Azure OpenAI"
                logger.info(f"{provider} client initialized with API key: {self.deployment_name}")
            
        except ImportError:
            raise ImportError(
                "openai package not installed. Run: pip install openai>=1.0.0"
            )
    
    def name(self) -> str:
        """Return the name of this embedding function (required by ChromaDB)."""
        provider = "foundry" if self.use_foundry else "azure-openai"
        return f"{provider}-{self.deployment_name}"
    
    def __call__(self, input: List[str]) -> List[List[float]]:
        """Generate embeddings for a list of texts (ChromaDB interface)."""
        return self._get_embeddings(input)
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate embeddings for documents."""
        return self._get_embeddings(texts)
    
    def embed_query(self, text: str = None, *, input: str = None) -> List[float]:
        """
        Generate embedding for a single query text.
        
        Accepts both 'text' and 'input' parameter names for compatibility.
        """
        query_text = text if text is not None else input
        if query_text is None:
            raise ValueError("Either 'text' or 'input' must be provided")
        
        embeddings = self._get_embeddings([query_text])
        return embeddings[0] if embeddings else []
    
    def _get_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Get embeddings from Azure OpenAI API."""
        if not texts:
            return []
        
        all_embeddings = []
        
        # Process in batches
        for i in range(0, len(texts), self.batch_size):
            batch = texts[i:i + self.batch_size]
            
            try:
                # Prepare API call parameters
                kwargs = {
                    "model": self.deployment_name,
                    "input": batch,
                }
                
                # Add dimensions if specified (only for embedding-3 models)
                if self.dimensions is not None:
                    kwargs["dimensions"] = self.dimensions
                
                response = self._client.embeddings.create(**kwargs)
                
                # Extract embeddings from response
                batch_embeddings = [item.embedding for item in response.data]
                all_embeddings.extend(batch_embeddings)
                
                logger.debug(f"Generated {len(batch_embeddings)} embeddings (batch {i // self.batch_size + 1})")
                
            except Exception as e:
                logger.error(f"Azure OpenAI embedding request failed: {e}")
                raise
        
        return all_embeddings
    
    def get_embedding_dimension(self) -> int:
        """Get the embedding dimension for this model."""
        if self.dimensions:
            return self.dimensions
        
        # Default dimensions by model
        model_dimensions = {
            "text-embedding-3-large": 3072,
            "text-embedding-3-small": 1536,
            "text-embedding-ada-002": 1536,
        }
        
        for model_name, dim in model_dimensions.items():
            if model_name in self.deployment_name.lower():
                return dim
        
        return 3072  # Default to large model dimensions


def create_azure_openai_embedding(
    endpoint: Optional[str] = None,
    api_key: Optional[str] = None,
    deployment_name: Optional[str] = None,
    dimensions: Optional[int] = None,
) -> AzureOpenAIEmbeddingFunction:
    """
    Factory function to create Azure OpenAI embedding function.
    
    Reads from environment variables if parameters not provided:
    - AZURE_OPENAI_ENDPOINT
    - AZURE_OPENAI_API_KEY  
    - AZURE_OPENAI_EMBEDDING_DEPLOYMENT
    
    Args:
        endpoint: Azure OpenAI endpoint
        api_key: API key
        deployment_name: Deployment name for embedding model
        dimensions: Optional dimension reduction (for embedding-3 models)
        
    Returns:
        Configured AzureOpenAIEmbeddingFunction
    """
    return AzureOpenAIEmbeddingFunction(
        endpoint=endpoint,
        api_key=api_key,
        deployment_name=deployment_name,
        dimensions=dimensions,
    )
