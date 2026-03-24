"""
Skilling Agent Package

Contact Center Knowledge-Based Coach POC.
Provides training simulation with CustomerSim and ShadowCoach agents.
"""

from agents.skilling.models import (
    CaseData,
    SimulationConfig,
    SimulationSession,
    SimulationMessage,
    SessionReport,
    MessageRole,
)
from agents.skilling.scenario_architect import ScenarioArchitect
from agents.skilling.customer_sim import CustomerSimAgent
from agents.skilling.shadow_coach import ShadowCoachAgent
from agents.skilling.simulation_orchestrator import SimulationOrchestrator

__all__ = [
    # Models
    "CaseData",
    "SimulationConfig", 
    "SimulationSession",
    "SimulationMessage",
    "SessionReport",
    "MessageRole",
    # Agents
    "ScenarioArchitect",
    "CustomerSimAgent",
    "ShadowCoachAgent",
    # Orchestration
    "SimulationOrchestrator",
]
