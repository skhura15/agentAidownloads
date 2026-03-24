"""
Ollama LLM Client

Provides a simple interface for calling Ollama's LLM API for RAG generation.
"""

import logging
import requests
from typing import Optional, List, Dict, Any, Generator
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class ChatMessage:
    """A single chat message."""
    role: str  # "system", "user", or "assistant"
    content: str


@dataclass 
class GenerationConfig:
    """Configuration for LLM generation."""
    temperature: float = 0.7
    max_tokens: int = 2048
    top_p: float = 0.9
    top_k: int = 40
    repeat_penalty: float = 1.1
    stop: Optional[List[str]] = None


class OllamaClient:
    """
    Client for Ollama's LLM API.
    
    Supports both chat completions and raw generation.
    
    Usage:
        client = OllamaClient(model="llama3.1:8b-instruct-q8_0")
        
        # Simple generation
        response = client.generate("What is RAG?")
        
        # Chat completion
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Explain RAG in simple terms."),
        ]
        response = client.chat(messages)
        
        # Streaming
        for chunk in client.generate_stream("Tell me a story"):
            print(chunk, end="", flush=True)
    """
    
    def __init__(
        self,
        model: str = "llama3.1:8b-instruct-q8_0",
        base_url: str = "http://localhost:11434",
        config: Optional[GenerationConfig] = None,
    ):
        """
        Initialize Ollama client.
        
        Args:
            model: Ollama model name (e.g., "llama3.1:8b-instruct-q8_0")
            base_url: Ollama server URL
            config: Generation configuration
        """
        self.model = model
        self.base_url = base_url.rstrip("/")
        self.config = config or GenerationConfig()
        
        self._verify_connection()
    
    def _verify_connection(self) -> None:
        """Verify Ollama is running and model is available."""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            response.raise_for_status()
            models = response.json().get("models", [])
            model_names = [m.get("name", "") for m in models]
            
            # Check if model exists (with or without tag)
            model_base = self.model.split(":")[0]
            if not any(self.model in m or model_base in m for m in model_names):
                logger.warning(
                    f"Model '{self.model}' not found in Ollama. "
                    f"Available: {model_names}. Run: ollama pull {self.model}"
                )
        except requests.exceptions.ConnectionError:
            raise ConnectionError(
                f"Cannot connect to Ollama at {self.base_url}. "
                "Make sure Ollama is running: ollama serve"
            )
    
    def generate(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        Generate a response for a single prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            config: Override generation config
            
        Returns:
            Generated text response
        """
        cfg = config or self.config
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
                "top_p": cfg.top_p,
                "top_k": cfg.top_k,
                "repeat_penalty": cfg.repeat_penalty,
            },
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        if cfg.stop:
            payload["options"]["stop"] = cfg.stop
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        
        return response.json().get("response", "")
    
    def chat(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
    ) -> str:
        """
        Generate a response for a chat conversation.
        
        Args:
            messages: List of ChatMessage objects
            config: Override generation config
            
        Returns:
            Generated assistant response
        """
        cfg = config or self.config
        
        # Convert ChatMessage to dict format
        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": message_dicts,
            "stream": False,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
                "top_p": cfg.top_p,
                "top_k": cfg.top_k,
                "repeat_penalty": cfg.repeat_penalty,
            },
        }
        
        if cfg.stop:
            payload["options"]["stop"] = cfg.stop
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            timeout=120,
        )
        response.raise_for_status()
        
        return response.json().get("message", {}).get("content", "")
    
    def generate_stream(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        config: Optional[GenerationConfig] = None,
    ) -> Generator[str, None, None]:
        """
        Stream a response for a single prompt.
        
        Args:
            prompt: The user prompt
            system_prompt: Optional system prompt
            config: Override generation config
            
        Yields:
            Generated text chunks
        """
        cfg = config or self.config
        
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
                "top_p": cfg.top_p,
                "top_k": cfg.top_k,
                "repeat_penalty": cfg.repeat_penalty,
            },
        }
        
        if system_prompt:
            payload["system"] = system_prompt
        
        response = requests.post(
            f"{self.base_url}/api/generate",
            json=payload,
            stream=True,
            timeout=120,
        )
        response.raise_for_status()
        
        import json
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                if "response" in data:
                    yield data["response"]
                if data.get("done", False):
                    break
    
    def chat_stream(
        self,
        messages: List[ChatMessage],
        config: Optional[GenerationConfig] = None,
    ) -> Generator[str, None, None]:
        """
        Stream a response for a chat conversation.
        
        Args:
            messages: List of ChatMessage objects
            config: Override generation config
            
        Yields:
            Generated text chunks
        """
        cfg = config or self.config
        
        message_dicts = [
            {"role": msg.role, "content": msg.content}
            for msg in messages
        ]
        
        payload = {
            "model": self.model,
            "messages": message_dicts,
            "stream": True,
            "options": {
                "temperature": cfg.temperature,
                "num_predict": cfg.max_tokens,
                "top_p": cfg.top_p,
                "top_k": cfg.top_k,
                "repeat_penalty": cfg.repeat_penalty,
            },
        }
        
        response = requests.post(
            f"{self.base_url}/api/chat",
            json=payload,
            stream=True,
            timeout=120,
        )
        response.raise_for_status()
        
        import json
        for line in response.iter_lines():
            if line:
                data = json.loads(line)
                content = data.get("message", {}).get("content", "")
                if content:
                    yield content
                if data.get("done", False):
                    break
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current model."""
        response = requests.post(
            f"{self.base_url}/api/show",
            json={"name": self.model},
            timeout=10,
        )
        response.raise_for_status()
        return response.json()
