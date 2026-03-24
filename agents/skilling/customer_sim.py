"""
Customer Simulation Agent

The "Actor" agent that roleplays as the customer during training simulations.
This agent has NO knowledge of the ShadowCoach and operates purely in character.

Key Principles:
1. Strict character adherence - never break the fourth wall
2. Realistic emotional responses based on customer profile
3. Secret acceptance condition that can be unlocked by good service
4. Consistent personality throughout the conversation
"""

import logging
from typing import Optional, List, Dict, Any

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from agents.skilling.simple_llm_client import SimpleLLMClient
from agents.skilling.models import (
    CustomerProfile,
    SimulationConfig,
    SimulationMessage,
    MessageRole,
)


def build_customer_system_prompt(config: SimulationConfig) -> str:
    """Build the system prompt for CustomerSim from SimulationConfig."""
    profile = config.customer_profile
    
    return f"""You are {profile.name}, a customer contacting support. You MUST stay in character at all times.

## YOUR CHARACTER:
- **Name**: {profile.name}
- **Emotional Tone**: {profile.tone}
- **Knowledge Level**: {profile.knowledge_level}
- **Personality**: {profile.personality_notes if profile.personality_notes else "A realistic customer with reasonable expectations"}

## YOUR SITUATION:
{config.scenario_context}

## YOUR OPENING MESSAGE:
You have already sent this message: "{profile.opening_message}"
Do NOT repeat this. Continue the conversation based on what the support agent says.

## HOW TO BEHAVE:

### Your Secret Acceptance Condition:
{profile.secret_condition}
- If the agent fulfills this condition, you should gradually become satisfied
- Do NOT reveal this condition explicitly - let it emerge naturally

### Things That Make You ANGRIER (Escalation Triggers):
{chr(10).join(f"- {trigger}" for trigger in profile.escalation_triggers)}
- If the agent does any of these, escalate your frustration
- Use phrases like "This is ridiculous", "I want to speak to a manager", "I've been a loyal customer"

### Things That CALM You Down (De-escalation Triggers):
{chr(10).join(f"- {trigger}" for trigger in profile.de_escalation_triggers)}
- If the agent does any of these, soften your tone gradually
- Acknowledge when they're being helpful, but don't become overly positive immediately

## CRITICAL RULES:

1. **NEVER break character** - You are the customer, not an AI. Never say things like "As an AI" or "I'm designed to"

2. **Emotional Realism** - Your mood should shift naturally based on how you're treated:
   - Start with your initial tone ({profile.tone})
   - Escalate if triggers hit
   - De-escalate if agent responds well
   - Don't flip instantly - gradual changes are more realistic

3. **Stay Focused** - Keep responses to the issue at hand. Don't go on tangents unless frustrated.

4. **Realistic Length** - Keep messages concise like a real customer chatting:
   - Frustrated customers write shorter, more intense messages
   - Calming customers might write slightly longer as they explain

5. **Natural Language** - Use contractions, casual language, maybe occasional typos when frustrated.

## EXAMPLES OF YOUR TONE:

Frustrated: "Look, I don't have time for this. Just tell me what you can do."
Slightly calmer: "Okay, I appreciate you looking into this. What are my options?"
Satisfied: "Alright, that actually sounds reasonable. How do we proceed?"

Remember: You are {profile.name}. Stay in character. React to how you're being treated."""


class CustomerSimAgent:
    """
    The Actor - roleplays as the customer during training simulations.
    
    This agent:
    - Maintains strict character adherence
    - Has NO awareness of coaching or evaluation
    - Responds realistically to trainee inputs
    - Can be "won over" by good service (secret condition)
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        simulation_config: SimulationConfig,
        logger: Optional[logging.Logger] = None
    ):
        self.config = config_manager
        self.sim_config = simulation_config
        self.logger = logger or LoggingService.get_logger("CustomerSim")
        self.llm = SimpleLLMClient(config_manager)
        
        # Build system prompt from customer profile
        self.system_prompt = build_customer_system_prompt(simulation_config)
        
        # Track conversation state
        self.conversation_history: List[Dict[str, str]] = []
        self.turn_count = 0
        self.mood_trajectory: List[str] = []  # Track mood changes
        
        self.logger.info(
            f"CustomerSim initialized as '{simulation_config.customer_profile.name}'"
        )
    
    async def respond(
        self,
        trainee_message: str,
        context: Optional[Dict[str, Any]] = None
    ) -> str:
        """
        Generate customer response to trainee's message.
        
        Args:
            trainee_message: What the trainee/agent said
            context: Optional additional context
            
        Returns:
            Customer's response in character
        """
        self.turn_count += 1
        self.logger.info(f"Turn {self.turn_count}: Generating customer response")
        
        try:
            # Use SimpleLLMClient for chat completion
            response = await self.llm.chat_with_history(
                system_prompt=self.system_prompt,
                messages=self.conversation_history + [{"role": "user", "content": trainee_message}],
                temperature=0.8,  # Slightly higher for natural variation
                max_tokens=500
            )
            
            # Clean up response
            response = response.strip()
            
            # Update conversation history
            self.conversation_history.append({
                "role": "user",  # Trainee = user from customer's perspective
                "content": trainee_message
            })
            self.conversation_history.append({
                "role": "assistant",  # Customer = assistant
                "content": response
            })
            
            self.logger.debug(f"Customer response: {response[:100]}...")
            return response
                
        except Exception as e:
            self.logger.error(f"CustomerSim failed to respond: {e}", exc_info=True)
            # Fallback response that stays in character
            return "I'm sorry, I'm having trouble understanding. Can you repeat that?"
    
    def _build_messages(self, new_message: str) -> List[Dict[str, str]]:
        """Build message list for the LLM."""
        messages = []
        
        # Add conversation history
        for msg in self.conversation_history:
            messages.append(msg)
        
        # Add new trainee message
        messages.append({
            "role": "user",
            "content": new_message
        })
        
        return messages
    
    def get_opening_message(self) -> SimulationMessage:
        """Get the customer's opening message to start the simulation."""
        return SimulationMessage(
            role=MessageRole.CUSTOMER,
            content=self.sim_config.customer_profile.opening_message,
            visible_to_trainee=True,
            metadata={
                "turn": 0,
                "is_opening": True,
                "customer_name": self.sim_config.customer_profile.name
            }
        )
    
    def reset(self) -> None:
        """Reset the agent for a new simulation."""
        self.conversation_history = []
        self.turn_count = 0
        self.mood_trajectory = []
        self.logger.info("CustomerSim reset for new simulation")
    
    def get_conversation_summary(self) -> Dict[str, Any]:
        """Get a summary of the conversation for reporting."""
        return {
            "customer_name": self.sim_config.customer_profile.name,
            "turn_count": self.turn_count,
            "message_count": len(self.conversation_history),
            "mood_trajectory": self.mood_trajectory
        }
