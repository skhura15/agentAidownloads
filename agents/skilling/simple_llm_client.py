"""
Simple LLM Client for Skilling Agents

A lightweight wrapper that provides chat completion functionality
using Azure OpenAI directly, without requiring the Agent Framework.

This is used as a fallback when Agent Framework is not configured,
and for simpler use cases where the full Agent Framework is not needed.
"""

import logging
from typing import Optional, List, Dict, Any

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from core.azure_openai_client import AzureOpenAIClient


class SimpleLLMClient:
    """
    Simple LLM client for skilling agents.
    
    Uses Azure OpenAI directly without Agent Framework overhead.
    Supports streaming and non-streaming completions.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        logger: Optional[logging.Logger] = None
    ):
        self.config = config_manager
        self.logger = logger or LoggingService.get_logger("SimpleLLMClient")
        
        # Initialize the Azure OpenAI client
        self.client = AzureOpenAIClient(config_manager)
        self.logger.info("SimpleLLMClient initialized")
    
    async def chat(
        self,
        system_prompt: str,
        user_message: str,
        conversation_history: Optional[List[Dict[str, str]]] = None,
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Send a chat message and get a response.
        
        Args:
            system_prompt: The system instructions
            user_message: The user's message
            conversation_history: Optional prior messages
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            
        Returns:
            The assistant's response text
        """
        # Build messages
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history if provided
        if conversation_history:
            messages.extend(conversation_history)
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        try:
            response = await self.client.chat_completion(
                messages=messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}", exc_info=True)
            raise
    
    async def chat_with_history(
        self,
        system_prompt: str,
        messages: List[Dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1000
    ) -> str:
        """
        Chat with full message history control.
        
        Args:
            system_prompt: The system instructions
            messages: Full list of messages (role/content dicts)
            temperature: Sampling temperature
            max_tokens: Maximum response tokens
            
        Returns:
            The assistant's response text
        """
        full_messages = [{"role": "system", "content": system_prompt}]
        full_messages.extend(messages)
        
        try:
            response = await self.client.chat_completion(
                messages=full_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                stream=False
            )
            
            return response.choices[0].message.content or ""
            
        except Exception as e:
            self.logger.error(f"Chat completion failed: {e}", exc_info=True)
            raise
