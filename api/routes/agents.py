"""
API Routes for Agent Operations
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid
from datetime import datetime

from api.models import (
    ChatRequest,
    ChatResponse,
    AgentInfo,
    ConversationHistory,
    UsageStats
)
from api.dependencies import get_orchestrator, get_config_manager
from orchestration.agent_orchestrator import AgentOrchestrator
from core.config_manager import ConfigManager

router = APIRouter(prefix="/agents", tags=["agents"])


@router.get("/", response_model=List[AgentInfo])
async def list_agents(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    List all available agents.
    
    Returns:
        List of agent information
    """
    try:
        agents_info = orchestrator.get_registered_agents()
        return agents_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}", response_model=AgentInfo)
async def get_agent(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get information about a specific agent.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Agent information
    """
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    return agent.get_info()


@router.post("/{agent_id}/chat", response_model=ChatResponse)
async def chat_with_agent(
    agent_id: str,
    request: ChatRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Send a message to a specific agent.
    
    Args:
        agent_id: Agent identifier
        request: Chat request with message and context
        
    Returns:
        Agent response
    """
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    try:
        # Execute agent
        response = await agent.execute(
            user_input=request.message,
            context=request.context or {},
            stream=False
        )
        
        # Convert to API response model
        return ChatResponse(
            response_id=response.response_id,
            content=response.content,
            agent_id=response.agent_id,
            agent_name=response.agent_name,
            status=response.status.value,
            tools_used=response.tools_used,
            metadata=response.metadata,
            timestamp=response.timestamp
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/history", response_model=ConversationHistory)
async def get_agent_history(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get conversation history for a specific agent.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Conversation history
    """
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    history = agent.get_conversation_history()
    
    return ConversationHistory(
        conversation_id=agent_id,
        messages=history,
        metadata=agent.metadata
    )


@router.post("/{agent_id}/reset")
async def reset_agent(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Reset agent state and conversation history.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Success message
    """
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    try:
        await agent.reset()
        return {"status": "success", "message": f"Agent {agent_id} reset successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{agent_id}/usage", response_model=UsageStats)
async def get_agent_usage(
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get token usage statistics for an agent.
    
    Args:
        agent_id: Agent identifier
        
    Returns:
        Usage statistics
    """
    agent = orchestrator.agents.get(agent_id)
    if not agent:
        raise HTTPException(status_code=404, detail=f"Agent not found: {agent_id}")
    
    # This would get actual usage from the agent's OpenAI client
    # For now, returning placeholder data
    return UsageStats(
        total_prompt_tokens=0,
        total_completion_tokens=0,
        total_tokens=0,
        estimated_cost_usd=0.0
    )
