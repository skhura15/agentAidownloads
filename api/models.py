"""
FastAPI Models

Pydantic models for request/response validation.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime


class ChatMessage(BaseModel):
    """Chat message model"""
    role: str = Field(..., description="Message role (user, assistant, system)")
    content: str = Field(..., description="Message content")
    timestamp: Optional[str] = Field(default=None, description="Message timestamp")


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    message: str = Field(..., description="User message")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    stream: bool = Field(default=False, description="Whether to stream the response")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0, description="Sampling temperature")


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    response_id: str = Field(..., description="Unique response ID")
    content: str = Field(..., description="Agent response content")
    agent_id: str = Field(..., description="Agent that generated the response")
    agent_name: str = Field(..., description="Agent name")
    status: str = Field(..., description="Response status")
    tools_used: List[str] = Field(default_factory=list, description="Tools used by the agent")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    timestamp: str = Field(..., description="Response timestamp")


class AgentInfo(BaseModel):
    """Agent information model"""
    agent_id: str = Field(..., description="Agent unique identifier")
    agent_name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    capabilities: List[str] = Field(default_factory=list, description="Agent capabilities")
    status: str = Field(..., description="Agent status")
    tools: List[str] = Field(default_factory=list, description="Available tools")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")


class OrchestrationRequest(BaseModel):
    """Request model for multi-agent orchestration"""
    message: str = Field(..., description="User message")
    initial_agent_id: str = Field(..., description="Initial agent to handle the request")
    context: Optional[Dict[str, Any]] = Field(default=None, description="Additional context")
    strategy: str = Field(default="sequential", description="Orchestration strategy")
    max_iterations: int = Field(default=10, description="Maximum agent handoff iterations")


class OrchestrationResponse(BaseModel):
    """Response model for orchestration endpoint"""
    responses: List[ChatResponse] = Field(..., description="List of agent responses")
    conversation_id: str = Field(..., description="Conversation identifier")
    total_agents: int = Field(..., description="Number of agents involved")
    completed: bool = Field(..., description="Whether orchestration completed successfully")


class ConversationHistory(BaseModel):
    """Conversation history model"""
    conversation_id: str = Field(..., description="Conversation identifier")
    messages: List[ChatMessage] = Field(default_factory=list, description="Conversation messages")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Conversation metadata")


class HealthResponse(BaseModel):
    """Health check response"""
    status: str = Field(..., description="Service status")
    timestamp: str = Field(..., description="Check timestamp")
    version: str = Field(..., description="API version")
    services: Dict[str, str] = Field(default_factory=dict, description="Service statuses")


class ErrorResponse(BaseModel):
    """Error response model"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(default=None, description="Detailed error information")
    timestamp: str = Field(..., description="Error timestamp")
    request_id: Optional[str] = Field(default=None, description="Request identifier")


class UsageStats(BaseModel):
    """Token usage statistics"""
    total_prompt_tokens: int = Field(..., description="Total prompt tokens")
    total_completion_tokens: int = Field(..., description="Total completion tokens")
    total_tokens: int = Field(..., description="Total tokens")
    estimated_cost_usd: float = Field(..., description="Estimated cost in USD")


class WebSocketMessage(BaseModel):
    """WebSocket message model"""
    type: str = Field(..., description="Message type (text, status, error, complete)")
    content: str = Field(..., description="Message content")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
