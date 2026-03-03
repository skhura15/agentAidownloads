"""
Azure OpenAI Client Wrapper

Provides a robust wrapper around Azure OpenAI with retry logic,
token management, and error handling.
"""

import asyncio
import os
import time
from typing import Any, AsyncIterator, Dict, List, Optional, Union
import logging
from datetime import datetime
import tiktoken

from openai import AsyncAzureOpenAI, AzureOpenAI, AsyncOpenAI
from openai.types.chat import ChatCompletion, ChatCompletionChunk
from azure.identity import DefaultAzureCredential, get_bearer_token_provider  # type: ignore

from core.config_manager import ConfigManager
from core.logging_service import LoggingService


class TokenManager:
    """Manages token counting and usage tracking"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        try:
            self.encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            self.encoding = tiktoken.get_encoding("cl100k_base")
        
        self.total_prompt_tokens = 0
        self.total_completion_tokens = 0
        self.total_cost = 0.0
    
    def count_tokens(self, text: str) -> int:
        """Count tokens in text"""
        return len(self.encoding.encode(text))
    
    def count_messages_tokens(self, messages: List[Dict[str, str]]) -> int:
        """Count tokens in message list"""
        num_tokens = 0
        for message in messages:
            num_tokens += 4  # Every message follows <im_start>{role/name}\n{content}<im_end>\n
            for key, value in message.items():
                num_tokens += self.count_tokens(str(value))
        num_tokens += 2  # Every reply is primed with <im_start>assistant
        return num_tokens
    
    def update_usage(self, prompt_tokens: int, completion_tokens: int) -> None:
        """Update token usage statistics"""
        self.total_prompt_tokens += prompt_tokens
        self.total_completion_tokens += completion_tokens
        
        # Approximate cost calculation (update with actual pricing)
        prompt_cost = (prompt_tokens / 1000) * 0.03  # $0.03 per 1K tokens
        completion_cost = (completion_tokens / 1000) * 0.06  # $0.06 per 1K tokens
        self.total_cost += prompt_cost + completion_cost
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get usage statistics"""
        return {
            "total_prompt_tokens": self.total_prompt_tokens,
            "total_completion_tokens": self.total_completion_tokens,
            "total_tokens": self.total_prompt_tokens + self.total_completion_tokens,
            "estimated_cost_usd": round(self.total_cost, 4)
        }


class AzureOpenAIClient:
    """
    Wrapper for Azure OpenAI with advanced features:
    - Automatic retry logic with exponential backoff
    - Token counting and management
    - Rate limiting
    - Error handling and logging
    - Support for streaming and non-streaming responses
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        logger: Optional[logging.Logger] = None,
        max_retries: int = 3,
        timeout: int = 60
    ):
        """
        Initialize Azure OpenAI client.
        
        Args:
            config_manager: Configuration manager instance
            logger: Optional custom logger
            max_retries: Maximum number of retry attempts
            timeout: Request timeout in seconds
        """
        self.config_manager = config_manager
        self.logger = logger or LoggingService.get_logger("azure_openai_client")
        self.max_retries = max_retries
        self.timeout = timeout
        
        # Get configuration
        azure_config = self.config_manager.get("azure_openai", {})
        self.endpoint = azure_config.get("endpoint")
        self.api_key = azure_config.get("api_key")
        self.api_version = azure_config.get("api_version", "2024-02-15-preview")
        self.deployment_name = azure_config.get("deployment_name")
        self.model = azure_config.get("model", "gpt-4")
        
        # Check USE_OLLAMA flag - automatically configures Ollama endpoint
        use_ollama = os.environ.get("USE_OLLAMA", "").lower() in ("true", "1", "yes")
        
        if use_ollama:
            # Auto-configure for Ollama - user just needs to set USE_OLLAMA=true
            ollama_base_url = os.environ.get("OLLAMA_BASE_URL", "http://localhost:11434")
            ollama_model = os.environ.get("OLLAMA_MODEL", "mistral")
            
            self.client = AsyncOpenAI(
                base_url=f"{ollama_base_url}/v1",
                api_key="ollama",  # Ollama accepts any key
                timeout=self.timeout
            )
            self.model = ollama_model
            self.deployment_name = ollama_model
            self.logger.info(f"Using Ollama at {ollama_base_url} with model: {ollama_model}")
        elif self.api_key:
            # Use Azure OpenAI with API key
            self.client = AsyncAzureOpenAI(
                azure_endpoint=self.endpoint,
                api_key=self.api_key,
                api_version=self.api_version,
                timeout=self.timeout
            )
            self.logger.info(f"Using Azure OpenAI at {self.endpoint}")
        else:
            # Use Azure AD authentication
            credential = DefaultAzureCredential()
            token_provider = get_bearer_token_provider(
                credential,
                "https://cognitiveservices.azure.com/.default"
            )
            self.client = AsyncAzureOpenAI(
                azure_endpoint=self.endpoint,
                azure_ad_token_provider=token_provider,
                api_version=self.api_version,
                timeout=self.timeout
            )
            self.logger.info(f"Using Azure OpenAI (Azure AD) at {self.endpoint}")
        
        # Initialize token manager
        self.token_manager = TokenManager(self.model)
        
        # Rate limiting
        self.last_request_time = 0
        self.min_request_interval = 0.1  # Minimum seconds between requests
    
    async def _wait_for_rate_limit(self) -> None:
        """Enforce rate limiting"""
        current_time = time.time()
        time_since_last_request = current_time - self.last_request_time
        
        if time_since_last_request < self.min_request_interval:
            wait_time = self.min_request_interval - time_since_last_request
            await asyncio.sleep(wait_time)
        
        self.last_request_time = time.time()
    
    async def _retry_with_backoff(self, func, *args, **kwargs):
        """Execute function with exponential backoff retry logic"""
        for attempt in range(self.max_retries):
            try:
                await self._wait_for_rate_limit()
                return await func(*args, **kwargs)
            except Exception as e:
                if attempt == self.max_retries - 1:
                    self.logger.error(f"Max retries reached. Error: {str(e)}")
                    raise
                
                wait_time = (2 ** attempt) + (asyncio.get_event_loop().time() % 1)
                self.logger.warning(
                    f"Request failed (attempt {attempt + 1}/{self.max_retries}). "
                    f"Retrying in {wait_time:.2f}s. Error: {str(e)}"
                )
                await asyncio.sleep(wait_time)
    
    async def chat_completion(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        stream: bool = False,
        **kwargs
    ) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
        """
        Create a chat completion.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            stream: Whether to stream the response
            **kwargs: Additional parameters
            
        Returns:
            ChatCompletion or async iterator of chunks
        """
        try:
            # Count input tokens
            input_tokens = self.token_manager.count_messages_tokens(messages)
            self.logger.info(f"Sending request with {input_tokens} input tokens")
            
            async def _make_request():
                return await self.client.chat.completions.create(
                    model=self.deployment_name,
                    messages=messages,
                    temperature=temperature,
                    max_tokens=max_tokens,
                    stream=stream,
                    **kwargs
                )
            
            response = await self._retry_with_backoff(_make_request)
            
            # Update token usage for non-streaming
            if not stream and hasattr(response, 'usage'):
                self.token_manager.update_usage(
                    response.usage.prompt_tokens,
                    response.usage.completion_tokens
                )
                self.logger.info(
                    f"Completion tokens: {response.usage.completion_tokens}, "
                    f"Total cost: ${self.token_manager.total_cost:.4f}"
                )
            
            return response
            
        except Exception as e:
            self.logger.error(f"Error in chat completion: {str(e)}", exc_info=True)
            raise
    
    async def chat_completion_streaming(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[str]:
        """
        Create a streaming chat completion.
        
        Args:
            messages: List of message dictionaries
            temperature: Sampling temperature
            max_tokens: Maximum tokens to generate
            **kwargs: Additional parameters
            
        Yields:
            Content chunks from the stream
        """
        try:
            stream = await self.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=True,
                **kwargs
            )
            
            full_content = ""
            async for chunk in stream:
                if chunk.choices[0].delta.content:
                    content = chunk.choices[0].delta.content
                    full_content += content
                    yield content
            
            # Estimate token usage for streaming
            completion_tokens = self.token_manager.count_tokens(full_content)
            input_tokens = self.token_manager.count_messages_tokens(messages)
            self.token_manager.update_usage(input_tokens, completion_tokens)
            
        except Exception as e:
            self.logger.error(f"Error in streaming completion: {str(e)}", exc_info=True)
            raise
    
    def get_usage_stats(self) -> Dict[str, Any]:
        """Get token usage statistics"""
        return self.token_manager.get_usage_stats()
    
    def reset_usage_stats(self) -> None:
        """Reset usage statistics"""
        self.token_manager = TokenManager(self.model)
        self.logger.info("Usage statistics reset")
