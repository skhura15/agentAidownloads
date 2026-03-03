"""
Shadow Coach Agent

The "Observer" agent that silently monitors the simulation and provides coaching hints.
This agent has FULL knowledge of the coaching rubric but NEVER interacts with CustomerSim.

Key Principles:
1. Silent observation - only outputs to the sidebar "whisper channel"
2. Rubric-based evaluation - checks against SME-defined checkpoints
3. Helpful, not annoying - intervenes only when necessary
4. Positive reinforcement - acknowledges good behaviors too
"""

import logging
import re
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from agents.skilling.simple_llm_client import SimpleLLMClient
from agents.skilling.models import (
    SimulationConfig,
    CoachingRubric,
    CoachingCheckpoint,
    SimulationMessage,
    MessageRole,
    CheckpointStatus,
)


def build_coach_system_prompt(config: SimulationConfig) -> str:
    """Build the system prompt for ShadowCoach from SimulationConfig."""
    rubric = config.coaching_rubric
    
    # Format checkpoints
    checkpoint_list = "\n".join([
        f"  {cp.id}. [{cp.importance.upper()}] {cp.description}"
        f"\n     Trigger phrases: {', '.join(cp.trigger_phrases) if cp.trigger_phrases else 'Use judgment'}"
        f"\n     Hint if missed: {cp.hint_if_missed}"
        for cp in rubric.checkpoints
    ])
    
    mistakes_list = "\n".join([f"  - {m}" for m in rubric.common_mistakes_to_watch])
    positive_list = "\n".join([f"  - {p}" for p in rubric.positive_reinforcement_triggers])
    
    return f"""You are a Shadow Coach observing a training simulation. Your job is to monitor the trainee's performance and provide helpful guidance through a private sidebar channel.

## SCENARIO CONTEXT:
{config.scenario_context}

## PRIMARY SKILL BEING PRACTICED:
{config.primary_skill}

## SUCCESS CRITERIA:
{config.success_summary}

## COACHING RUBRIC - CHECKPOINTS TO EVALUATE:
{checkpoint_list}

## COMMON MISTAKES TO WATCH FOR:
{mistakes_list}

## POSITIVE BEHAVIORS TO REINFORCE:
{positive_list}

## YOUR ROLE:

You are a supportive coach watching through a one-way mirror. The trainee can see your hints in a sidebar, but the customer CANNOT see anything you say. You are invisible to the customer.

## HOW TO RESPOND:

After each exchange (trainee message + customer response), analyze:
1. Did the trainee complete any checkpoints? (Use SEMANTIC matching - see below)
2. Did the trainee make a common mistake?
3. Is there an opportunity to provide a helpful nudge?

Then respond with ONE of these formats:

### If no intervention needed:
NONE

### If trainee did something good (positive reinforcement):
PRAISE: [brief acknowledgment - max 1 sentence]

### If trainee missed something or could improve:
HINT: [helpful, specific suggestion - max 2 sentences]

### If trainee made a significant mistake:
WARNING: [gentle correction - max 2 sentences]

### If checkpoint(s) completed (MOST IMPORTANT):
CHECKPOINT: [id] - [brief acknowledgment]
Or for multiple: CHECKPOINT: [id1], [id2] - [brief acknowledgment]

## CHECKPOINT DETECTION - SEMANTIC MATCHING:

**CRITICAL: Use SEMANTIC matching, not exact phrase matching!**

The trigger phrases are EXAMPLES, not requirements. Mark a checkpoint complete if the trainee conveys the SAME INTENT, even with different words:

Examples of semantic equivalence:
- "Thanks for being a power user!" = "I see you're an IT Director" = acknowledging expertise ✓
- "I'll wait while you try this" = "I'll stay on the line" = offering to stay on chat ✓
- "We can escalate to L3 if needed" = "I'll connect you with engineering" = offering escalation ✓
- "Let's skip the basics since you've covered them" = "We'll dive into advanced steps" = skipping basic troubleshooting ✓

**If the trainee accomplishes the checkpoint's GOAL, mark it complete!**

## CRITICAL RULES:

1. **CHECKPOINT DETECTION IS PRIORITY #1** - Your primary job is accurately tracking which checkpoints are completed. Be generous in recognizing semantic equivalents.

2. **MULTIPLE CHECKPOINTS** - If the trainee completes multiple checkpoints in one message, list ALL of them: "CHECKPOINT: 1, 3, 5 - Great work!"

3. **BE SPECIFIC** - Generic advice like "be empathetic" is not helpful. Say exactly what to do.

4. **BE BRIEF** - Trainees are in the middle of a conversation. Keep hints to 1-2 sentences max.

5. **BE ENCOURAGING** - Frame feedback positively. "Try acknowledging their frustration first" not "You forgot to show empathy".

6. **TRACK PROGRESS** - Remember which checkpoints have been completed. Don't repeat praise for the same checkpoint.

7. **TIMING MATTERS** - Sometimes the trainee is building toward something. Give them a turn or two before hinting.

## EXAMPLES:

Good checkpoint (single): "CHECKPOINT: 2 - Nice work verifying the account details first."

Good checkpoint (multiple): "CHECKPOINT: 1, 3 - Excellent! You acknowledged their expertise and skipped the basics."

Good hint: "HINT: The customer mentioned they've been waiting 3 hours - acknowledging that specific frustration could help de-escalate."

Good praise: "PRAISE: Great job acknowledging their frustration before explaining the policy!"

Remember: You're a supportive mentor, not a critic. Help the trainee succeed."""


class ShadowCoachAgent:
    """
    The Observer - silently monitors simulations and provides coaching feedback.
    
    This agent:
    - Has full knowledge of the coaching rubric
    - Evaluates each exchange against checkpoints
    - Provides hints through a separate "whisper channel"
    - NEVER communicates with CustomerSim
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        simulation_config: SimulationConfig,
        logger: Optional[logging.Logger] = None
    ):
        self.config = config_manager
        self.sim_config = simulation_config
        self.logger = logger or LoggingService.get_logger("ShadowCoach")
        self.llm = SimpleLLMClient(config_manager)
        
        # Build system prompt from coaching rubric
        self.system_prompt = build_coach_system_prompt(simulation_config)
        
        # Track checkpoint completion
        self.checkpoint_status: Dict[int, CheckpointStatus] = {
            cp.id: CheckpointStatus(
                checkpoint_id=cp.id,
                description=cp.description,
                completed=False
            )
            for cp in simulation_config.coaching_rubric.checkpoints
        }
        
        # Track coaching history
        self.hints_given: List[Dict[str, Any]] = []
        self.turn_count = 0
        
        # Rate limiting - don't hint too frequently
        self.last_hint_turn = -2  # Allow hint on first turn
        self.min_turns_between_hints = 1  # At least 1 turn gap between hints
        
        self.logger.info("ShadowCoach initialized with rubric")
    
    async def analyze(
        self,
        trainee_message: str,
        customer_response: str,
        full_transcript: Optional[List[Dict[str, str]]] = None
    ) -> Tuple[Optional[str], Optional[str]]:
        """
        Analyze the latest exchange and decide whether to provide feedback.
        
        Args:
            trainee_message: What the trainee said
            customer_response: How the customer responded
            full_transcript: Optional full conversation history
            
        Returns:
            Tuple of (feedback_type, feedback_content) or (None, None) if no intervention
        """
        self.turn_count += 1
        self.logger.info(f"Turn {self.turn_count}: Coach analyzing exchange")
        
        # Build analysis prompt
        analysis_prompt = self._build_analysis_prompt(
            trainee_message, 
            customer_response,
            full_transcript
        )
        
        try:
            # Use SimpleLLMClient for analysis
            response_text = await self.llm.chat(
                system_prompt=self.system_prompt,
                user_message=analysis_prompt,
                temperature=0.3,  # Lower temperature for consistent evaluation
                max_tokens=300
            )
            
            # Parse the response
            feedback_type, feedback_content = self._parse_coach_response(
                response_text.strip()
            )
            
            # Track hints given
            if feedback_type and feedback_type != "NONE":
                self.hints_given.append({
                    "turn": self.turn_count,
                    "type": feedback_type,
                    "content": feedback_content,
                    "trainee_message": trainee_message[:100]
                })
                self.last_hint_turn = self.turn_count
            
            return feedback_type, feedback_content
                
        except Exception as e:
            self.logger.error(f"ShadowCoach analysis failed: {e}", exc_info=True)
            return None, None
    
    def _build_analysis_prompt(
        self,
        trainee_message: str,
        customer_response: str,
        full_transcript: Optional[List[Dict[str, str]]] = None
    ) -> str:
        """Build the prompt for analysis."""
        # Include checkpoint status
        completed = [
            f"  ✓ {cs.checkpoint_id}: {cs.description}" 
            for cs in self.checkpoint_status.values() 
            if cs.completed
        ]
        pending = [
            f"  ○ {cs.checkpoint_id}: {cs.description}"
            for cs in self.checkpoint_status.values()
            if not cs.completed
        ]
        
        checkpoint_summary = "CHECKPOINTS COMPLETED:\n" + (
            "\n".join(completed) if completed else "  None yet"
        ) + "\n\nCHECKPOINTS PENDING:\n" + "\n".join(pending)
        
        # Build context from transcript if provided
        context = ""
        if full_transcript and len(full_transcript) > 2:
            recent = full_transcript[-6:]  # Last 3 exchanges
            context = "RECENT CONTEXT:\n" + "\n".join([
                f"  {msg['role'].upper()}: {msg['content'][:200]}..."
                if len(msg['content']) > 200 else f"  {msg['role'].upper()}: {msg['content']}"
                for msg in recent[:-2]  # Exclude current exchange
            ]) + "\n\n"
        
        return f"""{context}{checkpoint_summary}

---

CURRENT EXCHANGE (Turn {self.turn_count}):

TRAINEE: {trainee_message}

CUSTOMER: {customer_response}

---

Analyze this exchange carefully:

1. CHECKPOINT EVALUATION (MOST IMPORTANT): Review EACH pending checkpoint above. Did the trainee's message demonstrate completion of ANY checkpoints? Use SEMANTIC matching - the trainee doesn't need to use exact trigger phrases, just convey the same intent. For example:
   - "Thanks for being a power user!" = acknowledging technical expertise
   - "I'll wait while you try this" = offering to stay on chat
   - "We can escalate to L3" = offering escalation path

2. Did the trainee make any common mistakes?

3. Is there a helpful hint you should provide?

Remember:
- You can mark MULTIPLE checkpoints complete if the trainee achieved several in one message
- It's been {self.turn_count - self.last_hint_turn} turns since your last hint
- Be specific and brief

Your response format:
- If checkpoints completed: CHECKPOINT: [id1], [id2], ... - [brief acknowledgment]
- If praise (no checkpoint): PRAISE: [brief acknowledgment]
- If hint needed: HINT: [specific suggestion]
- If warning needed: WARNING: [gentle correction]
- If no intervention: NONE"""

    def _parse_coach_response(self, response: str) -> Tuple[Optional[str], Optional[str]]:
        """Parse the coach's response into type and content."""
        response = response.strip()
        
        if response.upper() == "NONE":
            return None, None
        
        # Parse formatted responses
        for prefix in ["CHECKPOINT:", "PRAISE:", "HINT:", "WARNING:"]:
            if response.upper().startswith(prefix):
                content = response[len(prefix):].strip()
                feedback_type = prefix.rstrip(":")
                
                # Handle checkpoint completion
                if feedback_type == "CHECKPOINT":
                    self._mark_checkpoint_complete(content)
                
                return feedback_type, content
        
        # Fallback - treat as hint if format not recognized
        if response:
            self.logger.warning(f"Unexpected coach response format: {response[:50]}")
            return "HINT", response
        
        return None, None
    
    def _mark_checkpoint_complete(self, content: str) -> None:
        """Mark checkpoint(s) as completed based on coach response.
        
        Supports multiple formats:
        - "2 - Nice work..." (original format)
        - "2, 3, 5 - Great job..." (multiple checkpoints)
        - "Checkpoint 2 completed" (alternative format)
        - "checkpoints 1 and 3" (natural language)
        """
        # Extract all numbers from the content before any descriptive text
        # First, try to get the ID portion (before the dash or colon)
        id_portion = content.split(" - ")[0] if " - " in content else content.split(":")[0] if ":" in content else content
        
        # Find all numbers in the ID portion using regex
        checkpoint_ids = re.findall(r'\b(\d+)\b', id_portion)
        
        if not checkpoint_ids:
            # Fallback: try to find any numbers in the full content (first 50 chars)
            checkpoint_ids = re.findall(r'\b(\d+)\b', content[:50])
        
        marked_count = 0
        for id_str in checkpoint_ids:
            try:
                checkpoint_id = int(id_str)
                if checkpoint_id in self.checkpoint_status:
                    if not self.checkpoint_status[checkpoint_id].completed:
                        self.checkpoint_status[checkpoint_id].completed = True
                        self.checkpoint_status[checkpoint_id].completed_at = (
                            datetime.utcnow().isoformat()
                        )
                        self.checkpoint_status[checkpoint_id].turn_completed = self.turn_count
                        marked_count += 1
                        self.logger.info(f"Checkpoint {checkpoint_id} marked complete")
            except (ValueError, IndexError) as e:
                self.logger.debug(f"Could not parse checkpoint ID '{id_str}' from: {content}")
        
        if marked_count == 0:
            self.logger.warning(f"No valid checkpoint IDs found in: {content[:100]}")
    
    def get_checkpoint_status_list(self) -> List[CheckpointStatus]:
        """Get list of all checkpoint statuses."""
        return list(self.checkpoint_status.values())
    
    def get_completion_stats(self) -> Dict[str, Any]:
        """Get completion statistics."""
        total = len(self.checkpoint_status)
        completed = sum(1 for cs in self.checkpoint_status.values() if cs.completed)
        
        return {
            "total_checkpoints": total,
            "completed_checkpoints": completed,
            "completion_percentage": (completed / total * 100) if total > 0 else 0,
            "hints_given": len(self.hints_given),
            "turns_elapsed": self.turn_count
        }
    
    async def generate_summary_feedback(
        self,
        full_transcript: List[Dict[str, str]]
    ) -> Dict[str, Any]:
        """
        Generate comprehensive end-of-session summary feedback for manager review.
        
        Args:
            full_transcript: Complete conversation history
            
        Returns:
            Detailed feedback with strengths, opportunities, skill scores, and manager notes
        """
        stats = self.get_completion_stats()
        
        # Format the full transcript for analysis
        transcript_text = ""
        for i, msg in enumerate(full_transcript):
            role = msg.get("role", "unknown").upper()
            content = msg.get("content", "")
            transcript_text += f"[Turn {i//2 + 1}] {role}: {content}\n\n"
        
        # Build comprehensive summary prompt
        summary_prompt = f"""The training simulation has ended. Generate a COMPREHENSIVE performance report for manager review.

## SESSION STATS:
- Total conversation turns: {self.turn_count}
- Checkpoints completed: {stats['completed_checkpoints']}/{stats['total_checkpoints']}
- Completion rate: {stats['completion_percentage']:.1f}%
- Coaching hints provided: {stats['hints_given']}

## CHECKPOINTS STATUS:
""" + "\n".join([
            f"{'✓ COMPLETED' if cs.completed else '✗ NOT COMPLETED'} - Checkpoint {cs.checkpoint_id}: {cs.description}"
            + (f" (completed at turn {cs.turn_completed})" if cs.completed and cs.turn_completed else "")
            for cs in self.checkpoint_status.values()
        ]) + f"""

## COACHING INTERVENTIONS GIVEN:
""" + ("\n".join([
            f"Turn {h['turn']}: [{h['type']}] {h['content']}"
            for h in self.hints_given
        ]) if self.hints_given else "No interventions were needed.") + f"""

## FULL CONVERSATION TRANSCRIPT:
{transcript_text}

## YOUR TASK:
Analyze the trainee's performance in detail and generate a comprehensive report.

Respond with VALID JSON in this EXACT format:
{{
  "overall_score": <number 1-100>,
  "performance_rating": "<Excellent|Good|Developing|Needs Improvement>",
  "skill_scores": [
    {{
      "skill_name": "Empathy & Active Listening",
      "score": <1-5>,
      "evidence": ["specific quote or action from transcript"],
      "recommendation": "specific improvement suggestion or null"
    }},
    {{
      "skill_name": "Problem Resolution",
      "score": <1-5>,
      "evidence": ["specific quote or action from transcript"],
      "recommendation": "specific improvement suggestion or null"
    }},
    {{
      "skill_name": "Communication Clarity",
      "score": <1-5>,
      "evidence": ["specific quote or action from transcript"],
      "recommendation": "specific improvement suggestion or null"
    }},
    {{
      "skill_name": "Process & Policy Knowledge",
      "score": <1-5>,
      "evidence": ["specific quote or action from transcript"],
      "recommendation": "specific improvement suggestion or null"
    }}
  ],
  "strengths": ["specific strength with example from conversation", "another strength"],
  "opportunities": ["specific area for improvement with example", "another opportunity"],
  "key_moments": [
    {{
      "turn": <turn number>,
      "type": "positive|negative|missed_opportunity",
      "description": "what happened and why it matters"
    }}
  ],
  "watch_out_warnings": [
    {{
      "category": "<Communication|Empathy|Process|Escalation|Tone|Accuracy>",
      "behavior": "specific behavior pattern observed that manager should watch for",
      "frequency": "<once|multiple_times|pattern>",
      "severity": "<low|medium|high>",
      "example_turn": <turn number where observed or null>,
      "example_quote": "exact quote from trainee showing this behavior or null",
      "coaching_suggestion": "specific coaching point for manager to discuss with trainee"
    }}
  ],
  "summary_feedback": "2-3 sentence overall assessment",
  "manager_notes": "Professional summary for manager: what went well, what needs coaching, and recommended follow-up actions. Be specific and actionable.",
  "recommended_training": ["specific training module or topic", "another training"],
  "follow_up_actions": ["specific action item for manager/trainee", "another action"]
}}

IMPORTANT:
- Be SPECIFIC - reference actual quotes and turns from the transcript
- Be BALANCED - acknowledge both strengths and areas for growth
- Be ACTIONABLE - provide clear next steps for improvement
- Base overall_score on: checkpoint completion (40%), skill demonstration (40%), hint usage (20%)
- A trainee who needed many hints should score lower than one who was self-sufficient
- WATCH OUT WARNINGS: Identify specific behavioral patterns that could become problems if not addressed. Include warnings even for minor issues that managers should monitor. Be specific with quotes and turn numbers."""

        try:
            # Use SimpleLLMClient for comprehensive summary generation
            response_text = await self.llm.chat(
                system_prompt="You are an expert training coach generating a comprehensive performance report for manager review. Always respond with valid JSON only, no additional text.",
                user_message=summary_prompt,
                temperature=0.4,
                max_tokens=2000
            )
            
            # Parse JSON response
            import json
            try:
                # Clean up response
                text = response_text.strip()
                if text.startswith("```"):
                    lines = text.split("\n")
                    lines = [l for l in lines if not l.strip().startswith("```")]
                    text = "\n".join(lines)
                
                feedback = json.loads(text)
                feedback["stats"] = stats
                
                # Ensure all expected fields exist
                feedback.setdefault("overall_score", 50)
                feedback.setdefault("performance_rating", "Developing")
                feedback.setdefault("skill_scores", [])
                feedback.setdefault("strengths", ["Completed the simulation"])
                feedback.setdefault("opportunities", ["Review the coaching hints for areas to improve"])
                feedback.setdefault("key_moments", [])
                feedback.setdefault("watch_out_warnings", [])
                feedback.setdefault("summary", feedback.get("summary_feedback", "Session completed."))
                feedback.setdefault("manager_notes", "")
                feedback.setdefault("recommended_training", [])
                feedback.setdefault("follow_up_actions", [])
                
                return feedback
            except json.JSONDecodeError as e:
                self.logger.error(f"JSON parse error: {e}")
                return self._generate_fallback_feedback(stats)
                    
        except Exception as e:
            self.logger.error(f"Failed to generate summary: {e}", exc_info=True)
            return self._generate_fallback_feedback(stats)
    
    def _generate_fallback_feedback(self, stats: Dict[str, Any]) -> Dict[str, Any]:
        """Generate basic fallback feedback if LLM fails."""
        completion_pct = stats.get("completion_percentage", 0)
        
        if completion_pct >= 80:
            rating = "Excellent"
            score = 85
        elif completion_pct >= 60:
            rating = "Good"
            score = 70
        elif completion_pct >= 40:
            rating = "Developing"
            score = 55
        else:
            rating = "Needs Improvement"
            score = 40
            
        return {
            "overall_score": score,
            "performance_rating": rating,
            "skill_scores": [],
            "strengths": ["Completed the simulation session"],
            "opportunities": ["Review the coaching hints provided during the session"],
            "key_moments": [],
            "watch_out_warnings": [],
            "summary": "Session completed. Please review the transcript for detailed insights.",
            "manager_notes": "Automated report - detailed analysis unavailable. Please review transcript manually.",
            "recommended_training": [],
            "follow_up_actions": ["Review session transcript with trainee"],
            "stats": stats
        }
    
    def reset(self) -> None:
        """Reset the coach for a new simulation."""
        for cs in self.checkpoint_status.values():
            cs.completed = False
            cs.completed_at = None
            cs.turn_completed = None
        
        self.hints_given = []
        self.turn_count = 0
        self.last_hint_turn = -2
        self.logger.info("ShadowCoach reset for new simulation")
