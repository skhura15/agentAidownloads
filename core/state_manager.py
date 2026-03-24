"""
State Manager

Manages conversation and agent state with support for:
- In-memory state storage
- Redis for distributed state (optional)
- State persistence and retrieval
"""

from typing import Any, Dict, Optional
import json
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict


class StateManager:
    """
    Manages agent and conversation state.
    Supports both in-memory and Redis-based storage.
    """
    
    def __init__(
        self,
        use_redis: bool = False,
        redis_host: Optional[str] = None,
        redis_port: int = 6379,
        redis_password: Optional[str] = None,
        ttl_seconds: int = 3600
    ):
        """
        Initialize state manager.
        
        Args:
            use_redis: Whether to use Redis for state storage
            redis_host: Redis host
            redis_port: Redis port
            redis_password: Redis password
            ttl_seconds: Time-to-live for state entries
        """
        self.use_redis = use_redis
        self.ttl_seconds = ttl_seconds
        
        # In-memory storage
        self.agent_states: Dict[str, Dict[str, Any]] = {}
        self.conversation_states: Dict[str, Dict[str, Any]] = {}
        self.state_timestamps: Dict[str, datetime] = {}
        
        # Redis client (initialized if needed)
        self.redis_client = None
        if use_redis:
            self._init_redis(redis_host, redis_port, redis_password)
        
        # Start cleanup task
        self._cleanup_task = asyncio.create_task(self._cleanup_expired_states())
    
    def _init_redis(
        self,
        host: Optional[str],
        port: int,
        password: Optional[str]
    ) -> None:
        """Initialize Redis client"""
        try:
            import redis.asyncio as redis  # type: ignore
            self.redis_client = redis.Redis(
                host=host,
                port=port,
                password=password,
                decode_responses=True
            )
        except ImportError:
            print("Warning: redis package not installed. Using in-memory storage.")
            self.use_redis = False
        except Exception as e:
            print(f"Warning: Failed to connect to Redis: {str(e)}. Using in-memory storage.")
            self.use_redis = False
    
    async def update_agent_state(
        self,
        agent_id: str,
        state: Dict[str, Any]
    ) -> None:
        """
        Update agent state.
        
        Args:
            agent_id: Agent identifier
            state: State data to update
        """
        if self.use_redis and self.redis_client:
            await self._update_redis_state(f"agent:{agent_id}", state)
        else:
            if agent_id not in self.agent_states:
                self.agent_states[agent_id] = {}
            self.agent_states[agent_id].update(state)
            self.state_timestamps[f"agent:{agent_id}"] = datetime.utcnow()
    
    async def get_agent_state(
        self,
        agent_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get agent state.
        
        Args:
            agent_id: Agent identifier
            
        Returns:
            Agent state or None
        """
        if self.use_redis and self.redis_client:
            return await self._get_redis_state(f"agent:{agent_id}")
        else:
            return self.agent_states.get(agent_id)
    
    async def clear_agent_state(self, agent_id: str) -> None:
        """
        Clear agent state.
        
        Args:
            agent_id: Agent identifier
        """
        if self.use_redis and self.redis_client:
            await self.redis_client.delete(f"agent:{agent_id}")
        else:
            if agent_id in self.agent_states:
                del self.agent_states[agent_id]
            key = f"agent:{agent_id}"
            if key in self.state_timestamps:
                del self.state_timestamps[key]
    
    async def update_conversation_state(
        self,
        conversation_id: str,
        state: Dict[str, Any]
    ) -> None:
        """
        Update conversation state.
        
        Args:
            conversation_id: Conversation identifier
            state: State data to update
        """
        if self.use_redis and self.redis_client:
            await self._update_redis_state(f"conversation:{conversation_id}", state)
        else:
            if conversation_id not in self.conversation_states:
                self.conversation_states[conversation_id] = {}
            self.conversation_states[conversation_id].update(state)
            self.state_timestamps[f"conversation:{conversation_id}"] = datetime.utcnow()
    
    async def get_conversation_state(
        self,
        conversation_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        Get conversation state.
        
        Args:
            conversation_id: Conversation identifier
            
        Returns:
            Conversation state or None
        """
        if self.use_redis and self.redis_client:
            return await self._get_redis_state(f"conversation:{conversation_id}")
        else:
            return self.conversation_states.get(conversation_id)
    
    async def clear_conversation_state(self, conversation_id: str) -> None:
        """
        Clear conversation state.
        
        Args:
            conversation_id: Conversation identifier
        """
        if self.use_redis and self.redis_client:
            await self.redis_client.delete(f"conversation:{conversation_id}")
        else:
            if conversation_id in self.conversation_states:
                del self.conversation_states[conversation_id]
            key = f"conversation:{conversation_id}"
            if key in self.state_timestamps:
                del self.state_timestamps[key]
    
    async def _update_redis_state(self, key: str, state: Dict[str, Any]) -> None:
        """Update state in Redis"""
        try:
            await self.redis_client.setex(
                key,
                self.ttl_seconds,
                json.dumps(state)
            )
        except Exception as e:
            print(f"Error updating Redis state: {str(e)}")
    
    async def _get_redis_state(self, key: str) -> Optional[Dict[str, Any]]:
        """Get state from Redis"""
        try:
            data = await self.redis_client.get(key)
            return json.loads(data) if data else None
        except Exception as e:
            print(f"Error getting Redis state: {str(e)}")
            return None
    
    async def _cleanup_expired_states(self) -> None:
        """Periodically clean up expired states from memory"""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                
                if not self.use_redis:
                    now = datetime.utcnow()
                    expired_keys = [
                        key for key, timestamp in self.state_timestamps.items()
                        if now - timestamp > timedelta(seconds=self.ttl_seconds)
                    ]
                    
                    for key in expired_keys:
                        if key.startswith("agent:"):
                            agent_id = key.split(":", 1)[1]
                            if agent_id in self.agent_states:
                                del self.agent_states[agent_id]
                        elif key.startswith("conversation:"):
                            conv_id = key.split(":", 1)[1]
                            if conv_id in self.conversation_states:
                                del self.conversation_states[conv_id]
                        
                        del self.state_timestamps[key]
            except Exception as e:
                print(f"Error in cleanup task: {str(e)}")
    
    async def close(self) -> None:
        """Clean up resources"""
        self._cleanup_task.cancel()
        if self.redis_client:
            await self.redis_client.close()
