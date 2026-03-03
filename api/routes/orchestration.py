"""
Orchestration Routes for Multi-Agent Workflows
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import List
import uuid

from api.models import (
    OrchestrationRequest,
    OrchestrationResponse,
    ChatResponse,
    ConversationHistory
)
from api.dependencies import get_orchestrator
from orchestration.agent_orchestrator import AgentOrchestrator, OrchestrationStrategy

router = APIRouter(prefix="/orchestrate", tags=["orchestration"])


@router.post("/", response_model=OrchestrationResponse)
async def orchestrate_agents(
    request: OrchestrationRequest,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Orchestrate multiple agents to handle a request.
    
    Args:
        request: Orchestration request with initial agent and strategy
        
    Returns:
        List of agent responses from the orchestration
    """
    try:
        # Validate initial agent
        if request.initial_agent_id not in orchestrator.agents:
            raise HTTPException(
                status_code=404,
                detail=f"Initial agent not found: {request.initial_agent_id}"
            )
        
        # Map strategy string to enum
        strategy_map = {
            "sequential": OrchestrationStrategy.SEQUENTIAL,
            "parallel": OrchestrationStrategy.PARALLEL,
            "conditional": OrchestrationStrategy.CONDITIONAL,
            "hierarchical": OrchestrationStrategy.HIERARCHICAL
        }
        
        strategy = strategy_map.get(
            request.strategy.lower(),
            OrchestrationStrategy.SEQUENTIAL
        )
        
        # Execute orchestration
        responses = await orchestrator.orchestrate(
            initial_agent_id=request.initial_agent_id,
            user_input=request.message,
            context=request.context or {},
            strategy=strategy,
            max_iterations=request.max_iterations
        )
        
        # Convert responses to API models
        chat_responses = [
            ChatResponse(
                response_id=resp.response_id,
                content=resp.content,
                agent_id=resp.agent_id,
                agent_name=resp.agent_name,
                status=resp.status.value,
                tools_used=resp.tools_used,
                metadata=resp.metadata,
                timestamp=resp.timestamp
            )
            for resp in responses
        ]
        
        conversation_id = str(uuid.uuid4())
        
        return OrchestrationResponse(
            responses=chat_responses,
            conversation_id=conversation_id,
            total_agents=len(set(r.agent_id for r in responses)),
            completed=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/parallel", response_model=OrchestrationResponse)
async def orchestrate_parallel(
    agent_ids: List[str],
    message: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Execute multiple agents in parallel.
    
    Args:
        agent_ids: List of agent IDs to execute
        message: User message
        
    Returns:
        List of agent responses
    """
    try:
        # Validate agents
        invalid_agents = [aid for aid in agent_ids if aid not in orchestrator.agents]
        if invalid_agents:
            raise HTTPException(
                status_code=404,
                detail=f"Agents not found: {', '.join(invalid_agents)}"
            )
        
        # Execute in parallel
        responses = await orchestrator.orchestrate_parallel(
            agent_ids=agent_ids,
            user_input=message,
            context={}
        )
        
        # Convert responses
        chat_responses = [
            ChatResponse(
                response_id=resp.response_id,
                content=resp.content,
                agent_id=resp.agent_id,
                agent_name=resp.agent_name,
                status=resp.status.value,
                tools_used=resp.tools_used,
                metadata=resp.metadata,
                timestamp=resp.timestamp
            )
            for resp in responses
        ]
        
        conversation_id = str(uuid.uuid4())
        
        return OrchestrationResponse(
            responses=chat_responses,
            conversation_id=conversation_id,
            total_agents=len(agent_ids),
            completed=True
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/history", response_model=ConversationHistory)
async def get_orchestration_history(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Get orchestration conversation history.
    
    Returns:
        Complete conversation history from orchestrator
    """
    history = orchestrator.get_conversation_history()
    
    return ConversationHistory(
        conversation_id="orchestration",
        messages=history,
        metadata={"total_messages": len(history)}
    )


@router.post("/history/clear")
async def clear_orchestration_history(
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    Clear orchestration conversation history.
    
    Returns:
        Success message
    """
    orchestrator.clear_conversation_history()
    return {"status": "success", "message": "Orchestration history cleared"}
