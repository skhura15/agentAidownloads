"""
Agent Orchestrator

Manages multi-agent conversations, handoffs, and workflow coordination.
"""

from typing import Any, Dict, List, Optional, Callable
import asyncio
import logging
from datetime import datetime
from enum import Enum

from agents.base_agent import BaseAgent, AgentResponse, AgentStatus
from core.logging_service import LoggingService
from core.state_manager import StateManager


class OrchestrationStrategy(Enum):
    """Orchestration strategies"""
    SEQUENTIAL = "sequential"  # Agents execute in sequence
    PARALLEL = "parallel"  # Agents execute in parallel
    CONDITIONAL = "conditional"  # Agent selection based on conditions
    HIERARCHICAL = "hierarchical"  # Manager agent delegates to worker agents


class HandoffRule:
    """Defines when and how to hand off from one agent to another"""
    
    def __init__(
        self,
        from_agent_id: str,
        to_agent_id: str,
        condition: Callable[[AgentResponse], bool],
        priority: int = 0
    ):
        self.from_agent_id = from_agent_id
        self.to_agent_id = to_agent_id
        self.condition = condition
        self.priority = priority


class AgentOrchestrator:
    """
    Orchestrates multi-agent conversations and workflows.
    
    Features:
    - Multiple orchestration strategies
    - Dynamic agent handoffs
    - Context sharing between agents
    - Conversation history tracking
    - Error recovery
    """
    
    def __init__(
        self,
        state_manager: StateManager,
        logger: Optional[logging.Logger] = None
    ):
        """
        Initialize orchestrator.
        
        Args:
            state_manager: State manager instance
            logger: Optional custom logger
        """
        self.state_manager = state_manager
        self.logger = logger or LoggingService.get_logger("orchestrator")
        
        self.agents: Dict[str, BaseAgent] = {}
        self.handoff_rules: List[HandoffRule] = []
        self.conversation_history: List[Dict[str, Any]] = []
        
        self.logger.info("Initialized AgentOrchestrator")
    
    def register_agent(self, agent: BaseAgent) -> None:
        """
        Register an agent with the orchestrator.
        
        Args:
            agent: Agent instance to register
        """
        self.agents[agent.agent_id] = agent
        self.logger.info(f"Registered agent: {agent.agent_name} ({agent.agent_id})")
    
    def register_handoff_rule(self, rule: HandoffRule) -> None:
        """
        Register a handoff rule.
        
        Args:
            rule: Handoff rule to register
        """
        self.handoff_rules.append(rule)
        self.handoff_rules.sort(key=lambda r: r.priority, reverse=True)
        self.logger.info(
            f"Registered handoff rule: {rule.from_agent_id} -> {rule.to_agent_id}"
        )
    
    async def orchestrate(
        self,
        initial_agent_id: str,
        user_input: str,
        context: Optional[Dict[str, Any]] = None,
        strategy: OrchestrationStrategy = OrchestrationStrategy.SEQUENTIAL,
        max_iterations: int = 10
    ) -> List[AgentResponse]:
        """
        Orchestrate multi-agent conversation.
        
        Args:
            initial_agent_id: ID of the first agent to handle the request
            user_input: User's input
            context: Additional context
            strategy: Orchestration strategy
            max_iterations: Maximum number of agent handoffs
            
        Returns:
            List of agent responses
        """
        context = context or {}
        responses = []
        current_agent_id = initial_agent_id
        iterations = 0
        
        self.logger.info(
            f"Starting orchestration with agent {initial_agent_id}, "
            f"strategy: {strategy.value}"
        )
        
        # Add to conversation history
        self.conversation_history.append({
            "role": "user",
            "content": user_input,
            "timestamp": datetime.utcnow().isoformat()
        })
        
        while iterations < max_iterations:
            iterations += 1
            
            # Get current agent
            agent = self.agents.get(current_agent_id)
            if not agent:
                self.logger.error(f"Agent not found: {current_agent_id}")
                break
            
            try:
                # Execute agent
                self.logger.info(f"Executing agent: {agent.agent_name}")
                
                # Share context from previous responses
                agent_context = context.copy()
                agent_context["previous_responses"] = responses
                agent_context["conversation_history"] = self.conversation_history
                
                response = await agent.execute(user_input, agent_context)
                responses.append(response)
                
                # Add to conversation history
                self.conversation_history.append({
                    "role": "assistant",
                    "agent_id": agent.agent_id,
                    "agent_name": agent.agent_name,
                    "content": response.content,
                    "timestamp": datetime.utcnow().isoformat()
                })
                
                # Check for explicit handoff
                if response.handoff_to:
                    self.logger.info(
                        f"Explicit handoff from {agent.agent_name} to {response.handoff_to}"
                    )
                    current_agent_id = response.handoff_to
                    continue
                
                # Check handoff rules
                next_agent_id = self._check_handoff_rules(response)
                if next_agent_id:
                    self.logger.info(
                        f"Rule-based handoff from {agent.agent_name} to {next_agent_id}"
                    )
                    current_agent_id = next_agent_id
                    continue
                
                # No handoff, conversation complete
                break
                
            except Exception as e:
                self.logger.error(
                    f"Error executing agent {agent.agent_name}: {str(e)}",
                    exc_info=True
                )
                responses.append(AgentResponse(
                    content=f"An error occurred during agent execution.",
                    agent_id=agent.agent_id,
                    agent_name=agent.agent_name,
                    status=AgentStatus.ERROR,
                    error=str(e)
                ))
                break
        
        if iterations >= max_iterations:
            self.logger.warning(f"Reached max iterations ({max_iterations})")
        
        self.logger.info(f"Orchestration complete with {len(responses)} responses")
        return responses
    
    def _check_handoff_rules(self, response: AgentResponse) -> Optional[str]:
        """
        Check if any handoff rules apply to the response.
        
        Args:
            response: Agent response to check
            
        Returns:
            Next agent ID if handoff rule matches, None otherwise
        """
        for rule in self.handoff_rules:
            if rule.from_agent_id == response.agent_id:
                try:
                    if rule.condition(response):
                        return rule.to_agent_id
                except Exception as e:
                    self.logger.error(f"Error evaluating handoff rule: {str(e)}")
        
        return None
    
    async def orchestrate_parallel(
        self,
        agent_ids: List[str],
        user_input: str,
        context: Optional[Dict[str, Any]] = None
    ) -> List[AgentResponse]:
        """
        Execute multiple agents in parallel.
        
        Args:
            agent_ids: List of agent IDs to execute
            user_input: User's input
            context: Additional context
            
        Returns:
            List of agent responses
        """
        context = context or {}
        self.logger.info(f"Executing {len(agent_ids)} agents in parallel")
        
        # Create tasks for all agents
        tasks = []
        for agent_id in agent_ids:
            agent = self.agents.get(agent_id)
            if agent:
                tasks.append(agent.execute(user_input, context))
            else:
                self.logger.warning(f"Agent not found: {agent_id}")
        
        # Execute all agents concurrently
        responses = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Handle exceptions
        valid_responses = []
        for i, response in enumerate(responses):
            if isinstance(response, Exception):
                self.logger.error(f"Error in parallel execution: {str(response)}")
                agent_id = agent_ids[i]
                valid_responses.append(AgentResponse(
                    content="An error occurred during agent execution.",
                    agent_id=agent_id,
                    agent_name=self.agents[agent_id].agent_name if agent_id in self.agents else "Unknown",
                    status=AgentStatus.ERROR,
                    error=str(response)
                ))
            else:
                valid_responses.append(response)
        
        return valid_responses
    
    async def orchestrate_conditional(
        self,
        user_input: str,
        agent_selector: Callable[[str, Dict[str, Any]], str],
        context: Optional[Dict[str, Any]] = None,
        max_iterations: int = 10
    ) -> List[AgentResponse]:
        """
        Orchestrate with conditional agent selection.
        
        Args:
            user_input: User's input
            agent_selector: Function to select next agent
            context: Additional context
            max_iterations: Maximum iterations
            
        Returns:
            List of agent responses
        """
        context = context or {}
        responses = []
        iterations = 0
        
        self.logger.info("Starting conditional orchestration")
        
        while iterations < max_iterations:
            iterations += 1
            
            # Select agent using custom logic
            try:
                agent_id = agent_selector(user_input, context)
                if not agent_id:
                    break
                
                agent = self.agents.get(agent_id)
                if not agent:
                    self.logger.error(f"Agent not found: {agent_id}")
                    break
                
                # Execute agent
                response = await agent.execute(user_input, context)
                responses.append(response)
                
                # Update context with response
                context["last_response"] = response
                context["all_responses"] = responses
                
            except Exception as e:
                self.logger.error(f"Error in conditional orchestration: {str(e)}")
                break
        
        return responses
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """Get complete conversation history"""
        return self.conversation_history.copy()
    
    def clear_conversation_history(self) -> None:
        """Clear conversation history"""
        self.conversation_history = []
        self.logger.info("Conversation history cleared")
    
    def get_registered_agents(self) -> List[Dict[str, Any]]:
        """Get information about all registered agents"""
        return [agent.get_info() for agent in self.agents.values()]
