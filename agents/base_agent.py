"""
Base Agent Class for Agentic CoE

This module provides the foundation for all agents in the system,
including common functionality for initialization, execution, logging,
error handling, and state management.

Uses Microsoft Agent Framework for production-ready agentic patterns.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Callable, AsyncIterator
from datetime import datetime
import logging
import uuid
import asyncio
from enum import Enum

from core.logging_service import LoggingService
from core.state_manager import StateManager
from core.config_manager import ConfigManager
from core.agent_framework_client import AgentFrameworkClient


class AgentStatus(Enum):
    """Agent execution status"""
    IDLE = "idle"
    PROCESSING = "processing"
    WAITING = "waiting"
    COMPLETED = "completed"
    ERROR = "error"


class AgentResponse:
    """Standardized agent response format"""
    
    def __init__(
        self,
        content: str,
        agent_id: str,
        agent_name: str,
        status: AgentStatus = AgentStatus.COMPLETED,
        metadata: Optional[Dict[str, Any]] = None,
        tools_used: Optional[List[str]] = None,
        handoff_to: Optional[str] = None,
        error: Optional[str] = None
    ):
        self.content = content
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.status = status
        self.metadata = metadata or {}
        self.tools_used = tools_used or []
        self.handoff_to = handoff_to
        self.error = error
        self.timestamp = datetime.utcnow().isoformat()
        self.response_id = str(uuid.uuid4())
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert response to dictionary"""
        return {
            "response_id": self.response_id,
            "content": self.content,
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "status": self.status.value,
            "metadata": self.metadata,
            "tools_used": self.tools_used,
            "handoff_to": self.handoff_to,
            "error": self.error,
            "timestamp": self.timestamp
        }


class BaseAgent(ABC):
    """
    Base class for all agents in the Agentic CoE system.
    
    All agents should inherit from this class and implement the required methods.
    Provides common functionality for agent lifecycle management, logging, and state handling.
    """
    
    def __init__(
        self,
        agent_id: str,
        agent_name: str,
        description: str,
        capabilities: List[str],
        config_manager: ConfigManager,
        state_manager: StateManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize the base agent.
        
        Args:
            agent_id: Unique identifier for the agent
            agent_name: Human-readable name
            description: What the agent does
            capabilities: List of agent capabilities
            config_manager: Configuration manager instance
            state_manager: State manager instance
            logger: Optional custom logger
        """
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.description = description
        self.capabilities = capabilities
        self.config_manager = config_manager
        self.state_manager = state_manager
        self.logger = logger or LoggingService.get_logger(f"agent.{agent_id}")
        
        self.status = AgentStatus.IDLE
        self.tools = []
        self.conversation_history = []
        self.metadata = {
            "created_at": datetime.utcnow().isoformat(),
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0
        }
        
        self.logger.info(f"Initialized agent: {self.agent_name} ({self.agent_id})")
    
    async def initialize(self) -> None:
        """
        Initialize agent resources and connections.
        Override this method to set up Azure clients, load prompts, etc.
        """
        try:
            self.logger.info(f"Initializing agent: {self.agent_name}")
            await self._load_configuration()
            await self._setup_tools()
            self.logger.info(f"Agent {self.agent_name} initialized successfully")
        except Exception as e:
            self.logger.error(f"Error initializing agent {self.agent_name}: {str(e)}")
            raise
    
    @abstractmethod
    async def _load_configuration(self) -> None:
        """Load agent-specific configuration"""
        pass
    
    @abstractmethod
    async def _setup_tools(self) -> None:
        """Set up agent-specific tools"""
        pass
    
    async def execute(
        self,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> Union[AgentResponse, AsyncIterator[str]]:
        """
        Execute agent logic with the given input.
        
        Args:
            user_input: User's message or request
            context: Additional context for the request
            stream: Whether to stream the response
            
        Returns:
            AgentResponse or async iterator for streaming
        """
        self.status = AgentStatus.PROCESSING
        self.metadata["total_requests"] += 1
        context = context or {}
        
        try:
            self.logger.info(f"Agent {self.agent_name} processing request")
            
            # Add to conversation history
            self.conversation_history.append({
                "role": "user",
                "content": user_input,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            # Update state
            await self.state_manager.update_agent_state(
                self.agent_id,
                {"status": "processing", "last_input": user_input}
            )
            
            # Execute agent logic
            if stream:
                return self._execute_streaming(user_input, context)
            else:
                response = await self._execute_logic(user_input, context)
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "content": response.content,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                self.metadata["successful_requests"] += 1
                self.status = AgentStatus.COMPLETED
                
                return response
                
        except Exception as e:
            self.logger.error(f"Error in agent {self.agent_name}: {str(e)}", exc_info=True)
            self.metadata["failed_requests"] += 1
            self.status = AgentStatus.ERROR
            
            return AgentResponse(
                content=f"I encountered an error while processing your request.",
                agent_id=self.agent_id,
                agent_name=self.agent_name,
                status=AgentStatus.ERROR,
                error=str(e)
            )
    
    @abstractmethod
    async def _execute_logic(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> AgentResponse:
        """
        Implement agent-specific logic here.
        
        Args:
            user_input: User's message
            context: Additional context
            
        Returns:
            AgentResponse with the result
        """
        pass
    
    async def _execute_streaming(
        self,
        user_input: str,
        context: Dict[str, Any]
    ) -> AsyncIterator[str]:
        """
        Stream agent responses in real-time.
        Override this method for streaming support.
        
        Args:
            user_input: User's message
            context: Additional context
            
        Yields:
            Chunks of the response
        """
        # Default: yield complete response
        response = await self._execute_logic(user_input, context)
        yield response.content
    
    async def cleanup(self) -> None:
        """Clean up agent resources"""
        self.logger.info(f"Cleaning up agent: {self.agent_name}")
        self.status = AgentStatus.IDLE
    
    def get_info(self) -> Dict[str, Any]:
        """Get agent information"""
        return {
            "agent_id": self.agent_id,
            "agent_name": self.agent_name,
            "description": self.description,
            "capabilities": self.capabilities,
            "status": self.status.value,
            "tools": [tool.__class__.__name__ for tool in self.tools],
            "metadata": self.metadata
        }
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get conversation history"""
        return self.conversation_history
    
    async def reset(self) -> None:
        """Reset agent state"""
        self.logger.info(f"Resetting agent: {self.agent_name}")
        self.conversation_history = []
        self.status = AgentStatus.IDLE
        await self.state_manager.clear_agent_state(self.agent_id)


# Type hints for async iterator
from typing import AsyncIterator
