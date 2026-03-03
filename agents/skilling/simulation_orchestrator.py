"""
Simulation Orchestrator

Custom control loop for managing the training simulation.
This is NOT a standard GroupChat - it maintains strict separation between
CustomerSim and ShadowCoach (the "Fourth Wall" architecture).

Key Responsibilities:
1. Route trainee messages to CustomerSim
2. Send transcript to ShadowCoach for analysis (in parallel)
3. Merge responses into separate channels (main chat vs sidebar)
4. Track session state and progress
"""

import asyncio
import logging
import json
import uuid
from pathlib import Path
from typing import Optional, Dict, Any, List, Tuple
from datetime import datetime

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from agents.skilling.models import (
    CaseData,
    SimulationConfig,
    SimulationSession,
    SimulationMessage,
    SessionReport,
    MessageRole,
    CheckpointStatus,
    ConversationTurnAnalysis,
    CheckpointDetail,
    SkillScore,
    CoachingInterventionSummary,
    WatchOutWarning,
)
from agents.skilling.scenario_architect import ScenarioArchitect, create_default_config_from_case
from agents.skilling.customer_sim import CustomerSimAgent
from agents.skilling.shadow_coach import ShadowCoachAgent


class SimulationOrchestrator:
    """
    Orchestrates training simulations with the Fourth Wall architecture.
    
    This orchestrator differs from standard multi-agent patterns:
    - CustomerSim and ShadowCoach NEVER see each other's messages
    - The orchestrator is the only entity with full visibility
    - Responses are routed to separate UI channels
    """
    
    def __init__(
        self,
        config_manager: ConfigManager,
        cases_dir: str = "data/cases",
        configs_dir: str = "data/sim_configs",
        logger: Optional[logging.Logger] = None
    ):
        self.config = config_manager
        self.cases_dir = Path(cases_dir)
        self.configs_dir = Path(configs_dir)
        self.logger = logger or LoggingService.get_logger("SimulationOrchestrator")
        
        # Session storage (in-memory for MVP)
        self.sessions: Dict[str, SimulationSession] = {}
        
        # Architect for generating configs
        self.architect = ScenarioArchitect(config_manager)
        
        # Ensure directories exist
        self.cases_dir.mkdir(parents=True, exist_ok=True)
        self.configs_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger.info("SimulationOrchestrator initialized")
    
    # =========================================================================
    # Case Management
    # =========================================================================
    
    def list_available_cases(self) -> List[Dict[str, Any]]:
        """List all available training cases."""
        cases = []
        
        for case_file in self.cases_dir.glob("*.json"):
            try:
                with open(case_file, 'r', encoding='utf-8') as f:
                    case_data = json.load(f)
                    cases.append({
                        "case_id": case_data.get("ticket_id", case_file.stem),
                        "title": case_data.get("title", "Untitled"),
                        "difficulty": case_data.get("difficulty", "intermediate"),
                        "primary_skill": case_data.get("primary_skill", "Unknown"),
                        "estimated_time": case_data.get("estimated_time_minutes", 10),
                        "tags": case_data.get("tags", []),
                        "context": case_data.get("context") or case_data.get("raw_content", {}).get("context"),
                        "file_path": str(case_file)
                    })
            except Exception as e:
                self.logger.warning(f"Failed to load case {case_file}: {e}")
        
        return cases
    
    def load_case(self, case_id: str) -> CaseData:
        """Load a case by ID."""
        # Try to find the case file
        case_file = None
        for file in self.cases_dir.glob("*.json"):
            with open(file, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get("ticket_id") == case_id:
                    case_file = file
                    break
        
        if not case_file:
            # Try direct filename match
            case_file = self.cases_dir / f"{case_id}.json"
            if not case_file.exists():
                raise ValueError(f"Case not found: {case_id}")
        
        with open(case_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return CaseData(**data)
    
    async def get_or_generate_config(
        self,
        case_id: str,
        force_regenerate: bool = False
    ) -> SimulationConfig:
        """
        Get cached config or generate new one from case data.
        
        Args:
            case_id: The case to load/generate config for
            force_regenerate: If True, regenerate even if cached
            
        Returns:
            SimulationConfig ready for runtime
        """
        config_file = self.configs_dir / f"config_{case_id}.json"
        
        # Check for cached config
        if config_file.exists() and not force_regenerate:
            self.logger.info(f"Loading cached config for {case_id}")
            with open(config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return SimulationConfig(**data)
        
        # Load case and generate config
        self.logger.info(f"Generating new config for {case_id}")
        case_data = self.load_case(case_id)
        
        try:
            config = await self.architect.generate_simulation_config(case_data)
        except Exception as e:
            self.logger.warning(f"LLM generation failed, using default: {e}")
            config = create_default_config_from_case(case_data)
        
        # Cache the config
        with open(config_file, 'w', encoding='utf-8') as f:
            f.write(config.model_dump_json(indent=2))
        
        return config
    
    # =========================================================================
    # Session Management
    # =========================================================================
    
    async def start_session(
        self,
        case_id: str,
        trainee_id: Optional[str] = None
    ) -> SimulationSession:
        """
        Start a new simulation session.
        
        Args:
            case_id: Which case to practice
            trainee_id: Optional trainee identifier
            
        Returns:
            New SimulationSession with initial state
        """
        session_id = str(uuid.uuid4())
        self.logger.info(f"Starting new session {session_id} for case {case_id}")
        
        # Get or generate the config
        config = await self.get_or_generate_config(case_id)
        
        # Initialize agents
        customer_sim = CustomerSimAgent(self.config, config)
        shadow_coach = ShadowCoachAgent(self.config, config)
        
        # Create session
        session = SimulationSession(
            session_id=session_id,
            case_id=case_id,
            trainee_id=trainee_id,
            config=config,
            checkpoint_status=[
                CheckpointStatus(
                    checkpoint_id=cp.id,
                    description=cp.description,
                    completed=False
                )
                for cp in config.coaching_rubric.checkpoints
            ],
            total_checkpoints=len(config.coaching_rubric.checkpoints)
        )
        
        # Get opening message
        opening = customer_sim.get_opening_message()
        session.messages.append(opening)
        session.main_chat_messages.append(opening)
        
        # Store session with agents
        self.sessions[session_id] = {
            "session": session,
            "customer_sim": customer_sim,
            "shadow_coach": shadow_coach
        }
        
        return session
    
    def get_session(self, session_id: str) -> Optional[SimulationSession]:
        """Get a session by ID."""
        session_data = self.sessions.get(session_id)
        if session_data:
            return session_data["session"]
        return None
    
    async def process_message(
        self,
        session_id: str,
        trainee_message: str
    ) -> Dict[str, Any]:
        """
        Process a trainee message through the Fourth Wall control loop.
        
        This is the core orchestration logic:
        1. Send trainee message to CustomerSim
        2. In parallel, send transcript to ShadowCoach
        3. Return both responses through separate channels
        
        Args:
            session_id: Active session ID
            trainee_message: What the trainee said
            
        Returns:
            {
                "customer_response": str,
                "coach_feedback": {"type": str, "content": str} | None,
                "checkpoint_update": CheckpointStatus | None,
                "session_stats": {...}
            }
        """
        session_data = self.sessions.get(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        session: SimulationSession = session_data["session"]
        customer_sim: CustomerSimAgent = session_data["customer_sim"]
        shadow_coach: ShadowCoachAgent = session_data["shadow_coach"]
        
        if not session.is_active:
            raise ValueError("Session has ended")
        
        # Update last activity timestamp
        session.last_activity = datetime.utcnow().isoformat()
        
        # Increment turn
        session.turn_count += 1
        
        # Record trainee message
        trainee_msg = SimulationMessage(
            role=MessageRole.USER,
            content=trainee_message,
            metadata={"turn": session.turn_count}
        )
        session.messages.append(trainee_msg)
        session.main_chat_messages.append(trainee_msg)
        
        # === FOURTH WALL CONTROL LOOP ===
        
        # Step 1: Get customer response
        customer_response = await customer_sim.respond(trainee_message)
        
        customer_msg = SimulationMessage(
            role=MessageRole.CUSTOMER,
            content=customer_response,
            metadata={
                "turn": session.turn_count,
                "customer_name": session.config.customer_profile.name
            }
        )
        session.messages.append(customer_msg)
        session.main_chat_messages.append(customer_msg)
        
        # Step 2: Get coach analysis (CustomerSim doesn't see this)
        transcript = [
            {"role": msg.role.value, "content": msg.content}
            for msg in session.main_chat_messages
        ]
        
        feedback_type, feedback_content = await shadow_coach.analyze(
            trainee_message,
            customer_response,
            transcript
        )
        
        coach_feedback = None
        if feedback_type and feedback_content:
            coach_msg = SimulationMessage(
                role=MessageRole.COACH,
                content=f"[{feedback_type}] {feedback_content}",
                visible_to_trainee=True,  # Visible in sidebar
                metadata={
                    "turn": session.turn_count,
                    "feedback_type": feedback_type
                }
            )
            session.messages.append(coach_msg)
            session.coach_hints.append(coach_msg)
            session.hints_received += 1
            
            coach_feedback = {
                "type": feedback_type,
                "content": feedback_content
            }
        
        # Step 3: Update checkpoint status from coach
        session.checkpoint_status = shadow_coach.get_checkpoint_status_list()
        session.checkpoints_completed = sum(
            1 for cs in session.checkpoint_status if cs.completed
        )
        
        # Check for max turns
        if session.turn_count >= session.config.max_turns:
            session.is_active = False
            session.ended_at = datetime.utcnow().isoformat()
        
        return {
            "customer_response": customer_response,
            "coach_feedback": coach_feedback,
            "checkpoint_status": [cs.model_dump() for cs in session.checkpoint_status],
            "session_stats": {
                "turn_count": session.turn_count,
                "checkpoints_completed": session.checkpoints_completed,
                "total_checkpoints": session.total_checkpoints,
                "hints_received": session.hints_received,
                "is_active": session.is_active
            }
        }
    
    async def ask_coach(
        self,
        session_id: str,
        question: Optional[str] = None
    ) -> str:
        """
        Explicitly ask the coach for help.
        
        Args:
            session_id: Active session ID
            question: Optional specific question
            
        Returns:
            Coach's advice
        """
        session_data = self.sessions.get(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        session: SimulationSession = session_data["session"]
        shadow_coach: ShadowCoachAgent = session_data["shadow_coach"]
        
        # Get coach's current assessment
        stats = shadow_coach.get_completion_stats()
        
        # Build context for explicit help request
        pending_checkpoints = [
            cs.description for cs in session.checkpoint_status if not cs.completed
        ]
        
        prompt = f"""The trainee is explicitly asking for help.

Current turn: {session.turn_count}
Checkpoints completed: {stats['completed_checkpoints']}/{stats['total_checkpoints']}
Pending checkpoints: {', '.join(pending_checkpoints[:3])}

{"The trainee asks: " + question if question else "Provide helpful guidance for their next message."}

Give a helpful, specific tip (2-3 sentences max). Be encouraging."""

        try:
            # Use SimpleLLMClient for help request
            from agents.skilling.simple_llm_client import SimpleLLMClient
            llm = SimpleLLMClient(self.config)
            
            response = await llm.chat(
                system_prompt="You are a supportive training coach helping a trainee practice customer service.",
                user_message=prompt,
                temperature=0.5,
                max_tokens=200
            )
            
            # Record the help request
            coach_msg = SimulationMessage(
                role=MessageRole.COACH,
                content=f"[HELP] {response.strip()}",
                metadata={"turn": session.turn_count, "explicit_request": True}
            )
            session.coach_hints.append(coach_msg)
            session.hints_received += 1
            
            return response.strip()
                
        except Exception as e:
            self.logger.error(f"Failed to get coach help: {e}")
            return "Focus on acknowledging the customer's concerns first."
    
    async def end_session(
        self,
        session_id: str
    ) -> SessionReport:
        """
        End a simulation session and generate a comprehensive report for manager review.
        
        Args:
            session_id: Session to end
            
        Returns:
            SessionReport with detailed performance analysis
        """
        session_data = self.sessions.get(session_id)
        if not session_data:
            raise ValueError(f"Session not found: {session_id}")
        
        session: SimulationSession = session_data["session"]
        shadow_coach: ShadowCoachAgent = session_data["shadow_coach"]
        
        # Mark session as ended
        session.is_active = False
        session.ended_at = datetime.utcnow().isoformat()
        
        # Generate comprehensive feedback from coach
        transcript = [
            {"role": msg.role.value, "content": msg.content}
            for msg in session.main_chat_messages
        ]
        feedback = await shadow_coach.generate_summary_feedback(transcript)
        
        # Calculate duration
        start = datetime.fromisoformat(session.started_at)
        end = datetime.fromisoformat(session.ended_at)
        duration = (end - start).total_seconds() / 60
        
        # Build conversation analysis from transcript
        conversation_analysis = self._build_conversation_analysis(session, shadow_coach)
        
        # Build checkpoint details
        checkpoint_details = self._build_checkpoint_details(shadow_coach, session)
        
        # Build coaching intervention summary
        coaching_summary = self._build_coaching_summary(shadow_coach)
        
        # Build skill scores from feedback with error handling
        skill_scores = []
        for score in feedback.get("skill_scores", []):
            try:
                skill_scores.append(SkillScore(
                    skill_name=score.get("skill_name", "Unknown Skill"),
                    score=score.get("score", 3),
                    max_score=score.get("max_score", 5),
                    evidence=score.get("evidence", []),
                    recommendation=score.get("recommendation")
                ))
            except Exception as e:
                self.logger.warning(f"Failed to parse skill score: {e}")
        
        # Build watch out warnings from feedback with error handling
        watch_out_warnings = []
        for warning in feedback.get("watch_out_warnings", []):
            try:
                watch_out_warnings.append(WatchOutWarning(
                    category=warning.get("category", "General"),
                    behavior=warning.get("behavior", ""),
                    frequency=warning.get("frequency", "once"),
                    severity=warning.get("severity", "medium"),
                    example_turn=warning.get("example_turn"),
                    example_quote=warning.get("example_quote"),
                    coaching_suggestion=warning.get("coaching_suggestion", "Review with trainee")
                ))
            except Exception as e:
                self.logger.warning(f"Failed to parse watch out warning: {e}")
        
        # Calculate completion percentage
        completion_pct = round(
            session.checkpoints_completed / session.total_checkpoints * 100
            if session.total_checkpoints > 0 else 0,
            1
        )
        
        # Build comprehensive report
        report = SessionReport(
            session_id=session_id,
            case_id=session.case_id,
            case_title=session.config.title,
            trainee_id=session.trainee_id,
            difficulty=session.config.difficulty,
            primary_skill=session.config.primary_skill,
            
            # Session Timeline
            started_at=session.started_at,
            ended_at=session.ended_at,
            total_turns=session.turn_count,
            duration_minutes=round(duration, 2),
            completion_status="completed",
            
            # Overall Performance
            overall_score=feedback.get("overall_score", 50),
            performance_rating=feedback.get("performance_rating", "Developing"),
            
            # Checkpoint Performance
            checkpoints_completed=session.checkpoints_completed,
            total_checkpoints=session.total_checkpoints,
            completion_percentage=completion_pct,
            checkpoint_details=checkpoint_details,
            
            # Skill Scores
            skill_scores=skill_scores,
            
            # Coaching Summary
            hints_received=session.hints_received,
            coaching_summary=coaching_summary,
            
            # Qualitative Feedback
            strengths=feedback.get("strengths", []),
            opportunities=feedback.get("opportunities", []),
            summary_feedback=feedback.get("summary", feedback.get("summary_feedback", "")),
            manager_notes=feedback.get("manager_notes", ""),
            
            # Conversation Analysis
            conversation_analysis=conversation_analysis,
            key_moments=feedback.get("key_moments", []),
            
            # Full Transcript
            transcript=[
                {
                    "role": msg.role.value,
                    "content": msg.content,
                    "timestamp": msg.timestamp
                }
                for msg in session.main_chat_messages
            ],
            
            # Watch Out Warnings for Manager (already built with error handling)
            watch_out_warnings=watch_out_warnings,
            
            # Recommendations
            recommended_training=feedback.get("recommended_training", []),
            follow_up_actions=feedback.get("follow_up_actions", [])
        )
        
        return report
    
    def _build_conversation_analysis(
        self, 
        session: SimulationSession, 
        shadow_coach: ShadowCoachAgent
    ) -> List[ConversationTurnAnalysis]:
        """Build turn-by-turn conversation analysis."""
        analysis = []
        messages = session.main_chat_messages
        hints = {h["turn"]: h for h in shadow_coach.hints_given}
        
        self.logger.info(f"Building conversation analysis from {len(messages)} messages")
        
        turn_num = 0
        i = 0
        while i < len(messages):
            msg = messages[i]
            
            # USER role is the trainee (not TRAINEE)
            if msg.role == MessageRole.USER:
                turn_num += 1
                trainee_msg = msg.content
                customer_resp = ""
                
                # Get customer response (next message)
                if i + 1 < len(messages) and messages[i + 1].role == MessageRole.CUSTOMER:
                    customer_resp = messages[i + 1].content
                    i += 1
                
                # Check for coach intervention at this turn
                hint = hints.get(turn_num)
                
                turn_analysis = ConversationTurnAnalysis(
                    turn_number=turn_num,
                    trainee_message=trainee_msg,
                    customer_response=customer_resp,
                    coach_intervention=hint["content"] if hint else None,
                    intervention_type=hint["type"] if hint else None,
                    checkpoint_completed=None,
                    skill_demonstrated=None,
                    timestamp=msg.timestamp
                )
                analysis.append(turn_analysis)
            
            i += 1
        
        self.logger.info(f"Built {len(analysis)} conversation turn analyses")
        return analysis
    
    def _build_checkpoint_details(
        self, 
        shadow_coach: ShadowCoachAgent,
        session: SimulationSession
    ) -> List[CheckpointDetail]:
        """Build detailed checkpoint information."""
        details = []
        
        for cp_status in shadow_coach.get_checkpoint_status_list():
            # Find the original checkpoint from config to get importance
            importance = "medium"
            for cp in session.config.coaching_rubric.checkpoints:
                if cp.id == cp_status.checkpoint_id:
                    importance = cp.importance
                    break
            
            detail = CheckpointDetail(
                checkpoint_id=cp_status.checkpoint_id,
                description=cp_status.description,
                importance=importance,
                completed=cp_status.completed,
                completed_at_turn=cp_status.turn_completed,
                trainee_action=None  # Could be enhanced to capture the specific action
            )
            details.append(detail)
        
        return details
    
    def _build_coaching_summary(
        self, 
        shadow_coach: ShadowCoachAgent
    ) -> CoachingInterventionSummary:
        """Build summary of all coaching interventions."""
        hints = shadow_coach.hints_given
        
        hint_count = sum(1 for h in hints if h["type"] == "HINT")
        warning_count = sum(1 for h in hints if h["type"] == "WARNING")
        praise_count = sum(1 for h in hints if h["type"] == "PRAISE")
        
        return CoachingInterventionSummary(
            total_hints=hint_count,
            total_warnings=warning_count,
            total_praise=praise_count,
            interventions=[
                {
                    "turn": h["turn"],
                    "type": h["type"],
                    "content": h["content"]
                }
                for h in hints
            ]
        )
    
    def touch_session(self, session_id: str) -> bool:
        """Update last_activity timestamp to keep a session alive."""
        session_data = self.sessions.get(session_id)
        if not session_data:
            return False
        session: SimulationSession = session_data["session"]
        if not session.is_active:
            return False
        session.last_activity = datetime.utcnow().isoformat()
        self.logger.info(f"Session {session_id} kept alive")
        return True

    def get_idle_seconds(self, session_id: str) -> Optional[float]:
        """Return how many seconds a session has been idle, or None if not found."""
        session_data = self.sessions.get(session_id)
        if not session_data:
            return None
        session: SimulationSession = session_data["session"]
        last = datetime.fromisoformat(session.last_activity)
        return (datetime.utcnow() - last).total_seconds()

    def cleanup_stale_sessions(self, max_idle_seconds: int = 900) -> List[str]:
        """Remove sessions that have been idle longer than max_idle_seconds. Returns removed IDs."""
        removed = []
        now = datetime.utcnow()
        for sid in list(self.sessions.keys()):
            session: SimulationSession = self.sessions[sid]["session"]
            last = datetime.fromisoformat(session.last_activity)
            idle = (now - last).total_seconds()
            if idle > max_idle_seconds:
                del self.sessions[sid]
                removed.append(sid)
                self.logger.info(f"Auto-cleaned stale session {sid} (idle {idle:.0f}s)")
        return removed

    def cleanup_session(self, session_id: str) -> None:
        """Remove a session from memory."""
        if session_id in self.sessions:
            del self.sessions[session_id]
            self.logger.info(f"Cleaned up session {session_id}")
