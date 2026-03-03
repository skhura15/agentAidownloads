"""
Azure OpenAI / Azure AI Foundry LLM Client

Provides chat completion using Azure OpenAI or Azure AI Foundry.
Compatible interface with OllamaClient for easy swapping.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """Chat message for LLM."""
    role: str  # "system", "user", "assistant"
    content: str


@dataclass 
class GenerationConfig:
    """Configuration for text generation."""
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 1.0
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0


class AzureOpenAIClient:
    """
    Azure OpenAI / Azure AI Foundry LLM client.
    
    Compatible interface with OllamaClient for easy swapping.
    
    Usage:
        client = AzureOpenAIClient(
            model="gpt-4o",
            endpoint="https://your-resource.openai.azure.com/",
            api_key="your-key",
        )
        
        response = client.chat([
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello!"),
        ])
    """
    
    def __init__(
        self,
        model: Optional[str] = None,
        endpoint: Optional[str] = None,
        api_key: Optional[str] = None,
        api_version: str = "2024-02-01",
        config: Optional[GenerationConfig] = None,
        use_foundry: Optional[bool] = None,
    ):
        """
        Initialize Azure OpenAI client.
        
        Args:
            model: Deployment name (e.g., gpt-4o)
            endpoint: Azure endpoint URL
            api_key: API key (optional for Foundry with DefaultAzureCredential)
            api_version: API version
            config: Generation configuration
            use_foundry: Use Foundry auth (DefaultAzureCredential if no API key)
        """
        self.model = model or os.getenv("FOUNDRY_MODEL_DEPLOYMENT", "gpt-4o")
        self.endpoint = endpoint or os.getenv("FOUNDRY_PROJECT_ENDPOINT") or os.getenv("AZURE_OPENAI_ENDPOINT")
        self.api_key = api_key or os.getenv("FOUNDRY_API_KEY") or os.getenv("AZURE_OPENAI_API_KEY")
        self.api_version = api_version
        self.config = config or GenerationConfig()
        
        # Auto-detect Foundry
        if use_foundry is None:
            use_foundry_env = os.getenv("USE_FOUNDRY", "").lower()
            self.use_foundry = use_foundry_env == "true" or (
                self.endpoint and "inference.ai.azure.com" in self.endpoint
            )
        else:
            self.use_foundry = use_foundry
        
        self._client = None
        self._init_client()
    
    def _init_client(self) -> None:
        """Initialize the Azure OpenAI client."""
        try:
            from openai import AzureOpenAI
            
            if not self.endpoint:
                raise ValueError("Azure endpoint not provided. Set FOUNDRY_PROJECT_ENDPOINT or AZURE_OPENAI_ENDPOINT.")
            
            if self.use_foundry and not self.api_key:
                # Use DefaultAzureCredential for Foundry
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
                    )
                    logger.info(f"Azure AI Foundry LLM client initialized with DefaultAzureCredential: {self.model}")
                    
                except ImportError:
                    raise ImportError("azure-identity package not installed. Run: pip install azure-identity")
            else:
                # Use API key
                if not self.api_key:
                    raise ValueError("API key not provided. Set FOUNDRY_API_KEY or AZURE_OPENAI_API_KEY.")
                
                self._client = AzureOpenAI(
                    azure_endpoint=self.endpoint,
                    api_key=self.api_key,
                    api_version=self.api_version,
                )
                provider = "Azure AI Foundry" if self.use_foundry else "Azure OpenAI"
                logger.info(f"{provider} LLM client initialized: {self.model}")
                
        except ImportError:
            raise ImportError("openai package not installed. Run: pip install openai>=1.0.0")
    
    def chat(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        Generate a chat completion.
        
        Args:
            messages: List of chat messages
            config: Optional generation config override
            
        Returns:
            Generated response text
        """
        cfg = config or self.config
        
        # Convert ChatMessage objects to dicts
        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        try:
            response = self._client.chat.completions.create(
                model=self.model,
                messages=message_dicts,
                temperature=cfg.temperature,
                max_tokens=cfg.max_tokens,
                top_p=cfg.top_p,
                frequency_penalty=cfg.frequency_penalty,
                presence_penalty=cfg.presence_penalty,
            )
            
            return response.choices[0].message.content
            
        except Exception as e:
            logger.error(f"Azure OpenAI chat completion failed: {e}")
            raise
    
    def generate(self, prompt: str, config: Optional[GenerationConfig] = None) -> str:
        """
        Generate text from a prompt (convenience method).
        
        Args:
            prompt: Text prompt
            config: Optional generation config
            
        Returns:
            Generated text
        """
        return self.chat([ChatMessage(role="user", content=prompt)], config)
