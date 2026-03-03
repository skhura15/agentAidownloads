"""
WebSocket Routes for Real-time Agent Communication
"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends
import json
from typing import Dict
import logging

from api.dependencies import get_orchestrator
from orchestration.agent_orchestrator import AgentOrchestrator
from core.logging_service import LoggingService

router = APIRouter(tags=["websocket"])

# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}

logger = LoggingService.get_logger("websocket")


@router.websocket("/ws/agent/{agent_id}")
async def agent_websocket(
    websocket: WebSocket,
    agent_id: str,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    WebSocket endpoint for streaming agent responses.
    
    Args:
        websocket: WebSocket connection
        agent_id: Agent identifier
    """
    await websocket.accept()
    connection_id = f"{agent_id}_{id(websocket)}"
    active_connections[connection_id] = websocket
    
    logger.info(f"WebSocket connection established for agent: {agent_id}")
    
    try:
        # Validate agent exists
        agent = orchestrator.agents.get(agent_id)
        if not agent:
            await websocket.send_json({
                "type": "error",
                "content": f"Agent not found: {agent_id}",
                "metadata": {}
            })
            await websocket.close()
            return
        
        # Send connection confirmation
        await websocket.send_json({
            "type": "status",
            "content": "Connected to agent",
            "metadata": {
                "agent_id": agent_id,
                "agent_name": agent.agent_name
            }
        })
        
        # Listen for messages
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            context = message_data.get("context", {})
            
            if not user_message:
                continue
            
            logger.info(f"Received message for agent {agent_id}: {user_message[:50]}...")
            
            # Send processing status
            await websocket.send_json({
                "type": "status",
                "content": "Processing...",
                "metadata": {"agent_id": agent_id}
            })
            
            try:
                # Stream response from agent
                async for chunk in agent._execute_streaming(user_message, context):
                    await websocket.send_json({
                        "type": "text",
                        "content": chunk,
                        "metadata": {"agent_id": agent_id}
                    })
                
                # Send completion status
                await websocket.send_json({
                    "type": "complete",
                    "content": "",
                    "metadata": {
                        "agent_id": agent_id,
                        "status": "success"
                    }
                })
                
            except Exception as e:
                logger.error(f"Error streaming response: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "content": str(e),
                    "metadata": {"agent_id": agent_id}
                })
    
    except WebSocketDisconnect:
        logger.info(f"WebSocket disconnected for agent: {agent_id}")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]


@router.websocket("/ws/orchestrate")
async def orchestration_websocket(
    websocket: WebSocket,
    orchestrator: AgentOrchestrator = Depends(get_orchestrator)
):
    """
    WebSocket endpoint for streaming multi-agent orchestration.
    
    Args:
        websocket: WebSocket connection
    """
    await websocket.accept()
    connection_id = f"orchestrate_{id(websocket)}"
    active_connections[connection_id] = websocket
    
    logger.info("WebSocket connection established for orchestration")
    
    try:
        await websocket.send_json({
            "type": "status",
            "content": "Connected to orchestrator",
            "metadata": {}
        })
        
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            user_message = message_data.get("message", "")
            initial_agent_id = message_data.get("initial_agent_id")
            context = message_data.get("context", {})
            
            if not user_message or not initial_agent_id:
                continue
            
            logger.info(f"Received orchestration request: {user_message[:50]}...")
            
            try:
                # Execute orchestration and stream results
                responses = await orchestrator.orchestrate(
                    initial_agent_id=initial_agent_id,
                    user_input=user_message,
                    context=context
                )
                
                # Send each response as it's generated
                for response in responses:
                    await websocket.send_json({
                        "type": "agent_response",
                        "content": response.content,
                        "metadata": {
                            "agent_id": response.agent_id,
                            "agent_name": response.agent_name,
                            "tools_used": response.tools_used,
                            "handoff_to": response.handoff_to
                        }
                    })
                
                # Send completion
                await websocket.send_json({
                    "type": "complete",
                    "content": "",
                    "metadata": {
                        "total_agents": len(set(r.agent_id for r in responses)),
                        "status": "success"
                    }
                })
                
            except Exception as e:
                logger.error(f"Error in orchestration: {str(e)}")
                await websocket.send_json({
                    "type": "error",
                    "content": str(e),
                    "metadata": {}
                })
    
    except WebSocketDisconnect:
        logger.info("Orchestration WebSocket disconnected")
    except Exception as e:
        logger.error(f"WebSocket error: {str(e)}", exc_info=True)
    finally:
        if connection_id in active_connections:
            del active_connections[connection_id]
