"""
Pytest configuration and fixtures
"""

import pytest
import asyncio
from typing import AsyncGenerator

from core.config_manager import ConfigManager
from core.state_manager import StateManager
from core.logging_service import LoggingService
from orchestration.agent_orchestrator import AgentOrchestrator


@pytest.fixture(scope="session")
def event_loop():
    """Create event loop for async tests"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()


@pytest.fixture
def config_manager():
    """Create test configuration manager"""
    return ConfigManager(config_dir="configs", environment="dev")


@pytest.fixture
async def state_manager():
    """Create test state manager"""
    manager = StateManager(use_redis=False)
    yield manager
    await manager.close()


@pytest.fixture
def orchestrator(state_manager):
    """Create test orchestrator"""
    return AgentOrchestrator(state_manager=state_manager)


# Configure logging for tests
LoggingService.configure(log_level="INFO")
