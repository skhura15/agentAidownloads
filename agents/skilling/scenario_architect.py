"""
Scenario Architect Agent

Transforms SME-annotated CaseData (Golden Record) into SimulationConfig (Game State).
This is Phase 1 - Preparation/Offline processing.

The Architect ensures that:
1. Customer persona is fully fleshed out for immersive roleplay
2. Coaching rubric is structured for real-time evaluation
3. The "right way" to handle the scenario is codified
"""

import json
import logging
from typing import Optional
from datetime import datetime

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from agents.skilling.simple_llm_client import SimpleLLMClient
from agents.skilling.models import (
    CaseData,
    SimulationConfig,
    CustomerProfile,
    CoachingRubric,
    CoachingCheckpoint,
)


ARCHITECT_SYSTEM_PROMPT = """You are the Scenario Architect, responsible for transforming SME-annotated support cases into structured simulation configurations.

Your job is to analyze the provided case data and generate a complete SimulationConfig that will be used to run a training simulation.

## Your Responsibilities:

1. **Customer Profile**: Create a detailed, immersive customer persona that:
   - Has a clear emotional tone and personality
   - Has specific triggers that escalate or de-escalate their mood
   - Has a "secret" acceptance condition that the trainee must discover through good service
   - Will respond consistently and realistically throughout the roleplay

2. **Coaching Rubric**: Create structured checkpoints that:
   - Map to the SME's correct SOP steps
   - Include specific trigger phrases that indicate completion
   - Provide helpful hints when steps are missed
   - Distinguish between required, recommended, and bonus checkpoints

3. **Scenario Context**: Provide enough context for the coach to understand:
   - What the trainee is practicing
   - What success looks like
   - What common mistakes to watch for

## Output Format:
You MUST respond with valid JSON matching the SimulationConfig schema. No markdown, no explanation, just the JSON object.

## Schema Reference:
{
  "case_id": "string - original ticket ID",
  "title": "string - scenario title",
  "difficulty": "string - beginner/intermediate/advanced",
  "primary_skill": "string - main skill being practiced",
  "customer_profile": {
    "name": "string",
    "tone": "string - emotional description",
    "knowledge_level": "string - low/average/high/expert",
    "opening_message": "string - first message to trainee",
    "secret_condition": "string - what will satisfy customer",
    "escalation_triggers": ["array of trigger phrases"],
    "de_escalation_triggers": ["array of calming phrases"],
    "personality_notes": "string - additional character notes"
  },
  "coaching_rubric": {
    "checkpoints": [
      {
        "id": 1,
        "description": "string - what this evaluates",
        "trigger_phrases": ["array of phrases that satisfy this"],
        "importance": "required|recommended|bonus",
        "hint_if_missed": "string - hint for sidebar"
      }
    ],
    "common_mistakes_to_watch": ["array of mistake patterns"],
    "positive_reinforcement_triggers": ["array of good behaviors to praise"]
  },
  "scenario_context": "string - full context for coach",
  "success_summary": "string - what constitutes success",
  "max_turns": 20
}
"""


class ScenarioArchitect:
    """
    Transforms CaseData into SimulationConfig using GPT-4.
    
    This agent runs during the "Preparation" phase, before any simulation starts.
    It can be run offline to pre-generate configs, or on-demand when loading a case.
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        logger: Optional[logging.Logger] = None
    ):
        self.config = config_manager
        self.logger = logger or LoggingService.get_logger("ScenarioArchitect")
        self.llm = SimpleLLMClient(config_manager)
        
    async def generate_simulation_config(
        self,
        case_data: CaseData
    ) -> SimulationConfig:
        """
        Transform CaseData into SimulationConfig.
        
        Args:
            case_data: The SME-annotated case (Golden Record)
            
        Returns:
            SimulationConfig ready for runtime agents
        """
        self.logger.info(f"Generating simulation config for case: {case_data.ticket_id}")
        
        # Prepare the input for the LLM
        case_json = case_data.model_dump_json(indent=2)
        
        user_prompt = f"""Analyze the following SME-annotated case and generate a complete SimulationConfig.

## Case Data (Golden Record):
```json
{case_json}
```

Generate the SimulationConfig JSON now. Remember:
1. The customer_profile.opening_message should be the initial_message from raw_content
2. Map ALL correct_sop_steps to coaching checkpoints
3. Include the common_mistakes in coaching_rubric.common_mistakes_to_watch
4. The secret_condition comes from customer_persona_hints.secret_acceptance_condition
5. Create helpful, specific hints for each checkpoint

Respond with ONLY the JSON object, no markdown code blocks or explanation."""

        try:
            # Use SimpleLLMClient for generation
            response_text = await self.llm.chat(
                system_prompt=ARCHITECT_SYSTEM_PROMPT,
                user_message=user_prompt,
                temperature=0.3,  # Lower temperature for structured output
                max_tokens=2000
            )
            
            # Parse the response
            config_dict = self._parse_response(response_text)
            
            # Add generated timestamp
            config_dict["generated_at"] = datetime.utcnow().isoformat()
            
            # Validate with Pydantic
            config = SimulationConfig(**config_dict)
            
            self.logger.info(
                f"Generated config with {len(config.coaching_rubric.checkpoints)} checkpoints"
            )
            
            return config
                
        except Exception as e:
            self.logger.error(f"Failed to generate simulation config: {e}", exc_info=True)
            raise
    
    def _parse_response(self, response_text: str) -> dict:
        """Parse LLM response into a dictionary."""
        # Clean up the response (remove markdown if present)
        text = response_text.strip()
        
        # Remove markdown code blocks if present
        if text.startswith("```"):
            lines = text.split("\n")
            # Remove first line (```json) and last line (```)
            lines = [l for l in lines if not l.strip().startswith("```")]
            text = "\n".join(lines)
        
        try:
            return json.loads(text)
        except json.JSONDecodeError as e:
            self.logger.error(f"Failed to parse JSON response: {e}")
            self.logger.debug(f"Raw response: {response_text}")
            raise ValueError(f"LLM returned invalid JSON: {e}")
    
    async def generate_and_save(
        self,
        case_data: CaseData,
        output_path: str
    ) -> SimulationConfig:
        """
        Generate config and save to file.
        
        Args:
            case_data: The SME-annotated case
            output_path: Path to save the generated config
            
        Returns:
            Generated SimulationConfig
        """
        config = await self.generate_simulation_config(case_data)
        
        # Save to file
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(config.model_dump_json(indent=2))
        
        self.logger.info(f"Saved simulation config to: {output_path}")
        return config


def create_default_config_from_case(case_data: CaseData) -> SimulationConfig:
    """
    Create a default SimulationConfig without LLM (for testing/fallback).
    
    This is useful for:
    - Unit testing without API calls
    - Fallback when LLM is unavailable
    - Quick prototyping
    """
    # Extract data from case
    raw = case_data.raw_content
    annotations = case_data.annotations
    hints = case_data.customer_persona_hints
    
    # Build checkpoints from SOP steps
    checkpoints = []
    for i, step in enumerate(annotations.correct_sop_steps, start=1):
        checkpoints.append(CoachingCheckpoint(
            id=i,
            description=step,
            trigger_phrases=[],  # Would need LLM to generate these
            importance="required" if i <= 3 else "recommended",
            hint_if_missed=f"Consider: {step}"
        ))
    
    # Build customer profile
    customer_profile = CustomerProfile(
        name=raw.customer_name,
        tone=hints.tone,
        knowledge_level="average",
        opening_message=raw.initial_message,
        secret_condition=hints.secret_acceptance_condition,
        escalation_triggers=hints.escalation_triggers,
        de_escalation_triggers=getattr(hints, 'de_escalation_triggers', []),
        personality_notes=""
    )
    
    # Build coaching rubric
    rubric = CoachingRubric(
        checkpoints=checkpoints,
        common_mistakes_to_watch=annotations.common_mistakes,
        positive_reinforcement_triggers=[]
    )
    
    return SimulationConfig(
        case_id=case_data.ticket_id,
        title=case_data.title,
        difficulty=case_data.difficulty,
        primary_skill=case_data.primary_skill,
        customer_profile=customer_profile,
        coaching_rubric=rubric,
        scenario_context=raw.context,
        success_summary=f"Successfully demonstrate: {case_data.primary_skill}",
        max_turns=20
    )
