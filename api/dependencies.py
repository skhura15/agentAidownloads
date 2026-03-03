"""
API Dependency Injection

Provides shared dependencies for API routes.
"""

from typing import Optional
from functools import lru_cache

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from core.state_manager import StateManager
from orchestration.agent_orchestrator import AgentOrchestrator

# Global instances (initialized on startup)
_config_manager: Optional[ConfigManager] = None
_state_manager: Optional[StateManager] = None
_orchestrator: Optional[AgentOrchestrator] = None


def initialize_dependencies(
    config_manager: ConfigManager,
    state_manager: StateManager,
    orchestrator: AgentOrchestrator
):
    """
    Initialize global dependencies.
    
    Args:
        config_manager: Configuration manager instance
        state_manager: State manager instance
        orchestrator: Agent orchestrator instance
    """
    global _config_manager, _state_manager, _orchestrator
    _config_manager = config_manager
    _state_manager = state_manager
    _orchestrator = orchestrator


def get_config_manager() -> ConfigManager:
    """Get configuration manager instance"""
    if _config_manager is None:
        raise RuntimeError("ConfigManager not initialized")
    return _config_manager


def get_state_manager() -> StateManager:
    """Get state manager instance"""
    if _state_manager is None:
        raise RuntimeError("StateManager not initialized")
    return _state_manager


def get_orchestrator() -> AgentOrchestrator:
    """Get orchestrator instance"""
    if _orchestrator is None:
        raise RuntimeError("AgentOrchestrator not initialized")
    return _orchestrator
