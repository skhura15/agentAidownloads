"""
Unit tests for BaseAgent
"""

import pytest
from unittest.mock import Mock, AsyncMock

from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from core.config_manager import ConfigManager
from core.state_manager import StateManager


class TestAgent(BaseAgent):
    """Test agent implementation"""
    
    async def _load_configuration(self) -> None:
        pass
    
    async def _setup_tools(self) -> None:
        pass
    
    async def _execute_logic(self, user_input: str, context: dict) -> AgentResponse:
        return AgentResponse(
            content=f"Echo: {user_input}",
            agent_id=self.agent_id,
            agent_name=self.agent_name,
            status=AgentStatus.COMPLETED
        )


@pytest.mark.asyncio
async def test_agent_initialization(config_manager, state_manager):
    """Test agent initialization"""
    agent = TestAgent(
        agent_id="test_agent",
        agent_name="Test Agent",
        description="A test agent",
        capabilities=["testing"],
        config_manager=config_manager,
        state_manager=state_manager
    )
    
    await agent.initialize()
    
    assert agent.agent_id == "test_agent"
    assert agent.agent_name == "Test Agent"
    assert agent.status == AgentStatus.IDLE


@pytest.mark.asyncio
async def test_agent_execution(config_manager, state_manager):
    """Test agent execution"""
    agent = TestAgent(
        agent_id="test_agent",
        agent_name="Test Agent",
        description="A test agent",
        capabilities=["testing"],
        config_manager=config_manager,
        state_manager=state_manager
    )
    
    await agent.initialize()
    
    response = await agent.execute("Hello, agent!")
    
    assert response.content == "Echo: Hello, agent!"
    assert response.status == AgentStatus.COMPLETED
    assert response.agent_id == "test_agent"


@pytest.mark.asyncio
async def test_agent_conversation_history(config_manager, state_manager):
    """Test conversation history tracking"""
    agent = TestAgent(
        agent_id="test_agent",
        agent_name="Test Agent",
        description="A test agent",
        capabilities=["testing"],
        config_manager=config_manager,
        state_manager=state_manager
    )
    
    await agent.initialize()
    
    await agent.execute("Message 1")
    await agent.execute("Message 2")
    
    history = agent.get_conversation_history()
    
    assert len(history) == 4  # 2 user messages + 2 assistant responses
    assert history[0]["content"] == "Message 1"
    assert history[2]["content"] == "Message 2"


@pytest.mark.asyncio
async def test_agent_reset(config_manager, state_manager):
    """Test agent reset"""
    agent = TestAgent(
        agent_id="test_agent",
        agent_name="Test Agent",
        description="A test agent",
        capabilities=["testing"],
        config_manager=config_manager,
        state_manager=state_manager
    )
    
    await agent.initialize()
    
    await agent.execute("Test message")
    assert len(agent.conversation_history) > 0
    
    await agent.reset()
    assert len(agent.conversation_history) == 0
    assert agent.status == AgentStatus.IDLE
