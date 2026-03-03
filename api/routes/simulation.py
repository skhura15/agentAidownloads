"""
Simulation API Routes

REST endpoints for the Contact Center Knowledge-Based Coach.
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel, Field
from typing import Any, Dict, List, Optional
import logging
import asyncio

from core.config_manager import ConfigManager
from core.logging_service import LoggingService
from api.dependencies import get_config_manager
from agents.skilling import SimulationOrchestrator

logger = LoggingService.get_logger("simulation_api")

router = APIRouter(prefix="/in-flow-simulation", tags=["Simulation"])

# Session timeout in seconds (15 minutes)
SESSION_TIMEOUT_SECONDS = 900
# Warning is shown on the frontend before this many seconds of idle
SESSION_WARNING_SECONDS = 720  # 12 minutes

# Global orchestrator instance (initialized on startup)
_orchestrator: Optional[SimulationOrchestrator] = None
_cleanup_task: Optional[asyncio.Task] = None


def get_orchestrator() -> SimulationOrchestrator:
    """Dependency to get the simulation orchestrator."""
    global _orchestrator
    if _orchestrator is None:
        raise HTTPException(status_code=503, detail="Simulation service not initialized")
    return _orchestrator


def set_orchestrator(orchestrator: SimulationOrchestrator):
    """Set the global orchestrator instance."""
    global _orchestrator
    _orchestrator = orchestrator


def initialize_simulation_service(config_manager: ConfigManager):
    """Initialize the simulation orchestrator (called on startup)."""
    global _orchestrator, _cleanup_task
    _orchestrator = SimulationOrchestrator(config_manager)
    # Start background cleanup loop
    _cleanup_task = asyncio.get_event_loop().create_task(_session_cleanup_loop())
    logger.info("Simulation service initialized with session timeout=%ds", SESSION_TIMEOUT_SECONDS)


async def _session_cleanup_loop():
    """Periodically remove stale sessions."""
    while True:
        await asyncio.sleep(60)  # check every 60 seconds
        try:
            if _orchestrator:
                removed = _orchestrator.cleanup_stale_sessions(max_idle_seconds=SESSION_TIMEOUT_SECONDS)
                if removed:
                    logger.info("Auto-cleaned %d stale session(s): %s", len(removed), removed)
        except Exception as e:
            logger.error("Session cleanup error: %s", e)


# =============================================================================
# Request/Response Models
# =============================================================================

class CaseListItem(BaseModel):
    """Summary of a training case"""
    case_id: str
    title: str
    difficulty: str
    primary_skill: str
    estimated_time: int
    tags: List[str]
    context: Optional[str] = None


class StartSessionRequest(BaseModel):
    """Request to start a new simulation session"""
    case_id: str = Field(..., description="Which case to practice")
    trainee_id: Optional[str] = Field(default=None, description="Trainee identifier")


class StartSessionResponse(BaseModel):
    """Response when starting a session"""
    session_id: str
    case_id: str
    title: str
    difficulty: str
    primary_skill: str
    customer_name: str
    opening_message: str
    total_checkpoints: int


class ChatRequest(BaseModel):
    """Send a message in the simulation"""
    message: str = Field(..., description="Trainee's message to customer")


class ChatResponse(BaseModel):
    """Response from a chat turn"""
    customer_response: str
    coach_feedback: Optional[Dict[str, str]] = None
    checkpoint_status: List[Dict[str, Any]]
    session_stats: Dict[str, Any]


class AskCoachRequest(BaseModel):
    """Explicit request for coach help"""
    question: Optional[str] = Field(default=None, description="Specific question")


class AskCoachResponse(BaseModel):
    """Coach's advice"""
    advice: str


class SkillScoreResponse(BaseModel):
    """Score for a specific skill category"""
    skill_name: str
    score: int
    max_score: int = 5
    evidence: List[str] = []
    recommendation: Optional[str] = None


class CheckpointDetailResponse(BaseModel):
    """Detailed checkpoint information"""
    checkpoint_id: int
    description: str
    importance: str
    completed: bool
    completed_at_turn: Optional[int] = None
    trainee_action: Optional[str] = None


class CoachingInterventionResponse(BaseModel):
    """Summary of coaching interventions"""
    total_hints: int
    total_warnings: int
    total_praise: int
    interventions: List[Dict[str, Any]] = []


class ConversationTurnResponse(BaseModel):
    """Analysis of a single conversation turn"""
    turn_number: int
    trainee_message: str
    customer_response: str
    coach_intervention: Optional[str] = None
    intervention_type: Optional[str] = None
    timestamp: str


class WatchOutWarningResponse(BaseModel):
    """Specific behavior pattern for manager to watch out for"""
    category: str
    behavior: str
    frequency: str
    severity: str
    example_turn: Optional[int] = None
    example_quote: Optional[str] = None
    coaching_suggestion: str


class SessionReportResponse(BaseModel):
    """Comprehensive end of session report for manager review"""
    session_id: str
    case_title: str
    case_id: str
    trainee_id: Optional[str] = None
    difficulty: str = "intermediate"
    primary_skill: str = ""
    
    # Timeline
    started_at: str = ""
    ended_at: str = ""
    total_turns: int
    duration_minutes: float
    completion_status: str = "completed"
    
    # Overall Performance
    overall_score: int = 0
    performance_rating: str = ""
    
    # Checkpoints
    checkpoints_completed: int
    total_checkpoints: int
    completion_percentage: float
    checkpoint_details: List[CheckpointDetailResponse] = []
    
    # Skills
    skill_scores: List[SkillScoreResponse] = []
    
    # Coaching
    hints_received: int
    coaching_summary: Optional[CoachingInterventionResponse] = None
    
    # Qualitative Feedback
    strengths: List[str]
    opportunities: List[str]
    summary_feedback: str
    manager_notes: str = ""
    
    # Conversation Analysis
    conversation_analysis: List[ConversationTurnResponse] = []
    key_moments: List[Dict[str, Any]] = []
    
    # Full Transcript
    transcript: List[Dict[str, Any]] = []
    
    # Watch Out Warnings for Manager
    watch_out_warnings: List[WatchOutWarningResponse] = []
    
    # Recommendations
    recommended_training: List[str] = []
    follow_up_actions: List[str] = []
    
    generated_at: str = ""


# =============================================================================
# Endpoints
# =============================================================================

@router.get("/cases", response_model=List[CaseListItem])
async def list_cases() -> List[CaseListItem]:
    """
    List all available training cases.
    
    Returns a list of cases that can be used to start a simulation.
    """
    global _orchestrator
    
    # Try to use orchestrator if available
    if _orchestrator is not None:
        try:
            cases = _orchestrator.list_available_cases()
            return [CaseListItem(**case) for case in cases]
        except Exception as e:
            logger.warning(f"Failed to get cases from orchestrator: {e}. Using fallback.")
    
    # Fallback: load cases directly from files
    cases = _load_cases_directly()
    return [CaseListItem(**case) for case in cases]


@router.post("/start", response_model=StartSessionResponse)
async def start_simulation(
    request: StartSessionRequest,
    orchestrator: SimulationOrchestrator = Depends(get_orchestrator)
) -> StartSessionResponse:
    """
    Start a new simulation session.
    
    Loads the specified case, generates the simulation config,
    and returns the customer's opening message.
    """
    try:
        session = await orchestrator.start_session(
            case_id=request.case_id,
            trainee_id=request.trainee_id
        )
        
        return StartSessionResponse(
            session_id=session.session_id,
            case_id=session.case_id,
            title=session.config.title,
            difficulty=session.config.difficulty,
            primary_skill=session.config.primary_skill,
            customer_name=session.config.customer_profile.name,
            opening_message=session.config.customer_profile.opening_message,
            total_checkpoints=session.total_checkpoints
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to start simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to start simulation")


@router.post("/{session_id}/chat", response_model=ChatResponse)
async def send_message(
    session_id: str,
    request: ChatRequest,
    orchestrator: SimulationOrchestrator = Depends(get_orchestrator)
) -> ChatResponse:
    """
    Send a message in the simulation.
    
    The message goes to the CustomerSim agent, and the ShadowCoach
    analyzes the exchange to provide optional coaching feedback.
    """
    try:
        result = await orchestrator.process_message(
            session_id=session_id,
            trainee_message=request.message
        )
        
        return ChatResponse(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to process message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to process message")


@router.post("/{session_id}/ask-coach", response_model=AskCoachResponse)
async def ask_coach(
    session_id: str,
    request: AskCoachRequest,
    orchestrator: SimulationOrchestrator = Depends(get_orchestrator)
) -> AskCoachResponse:
    """
    Explicitly ask the coach for help.
    
    This is the "Ask Coach" button functionality - lets trainees
    request guidance at any point during the simulation.
    """
    try:
        advice = await orchestrator.ask_coach(
            session_id=session_id,
            question=request.question
        )
        
        return AskCoachResponse(advice=advice)
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to get coach advice: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Coach unavailable")


@router.post("/{session_id}/end", response_model=SessionReportResponse)
async def end_simulation(
    session_id: str,
    orchestrator: SimulationOrchestrator = Depends(get_orchestrator)
) -> SessionReportResponse:
    """
    End the simulation and get the comprehensive report card.
    
    Generates a detailed summary of the session including:
    - Overall performance score and rating
    - Skill-based scores with evidence
    - Checkpoint completion details
    - Coaching intervention summary
    - Turn-by-turn conversation analysis
    - Key moments (positive/negative)
    - Manager notes and recommendations
    """
    try:
        report = await orchestrator.end_session(session_id)
        
        # Map checkpoint details
        checkpoint_details = [
            CheckpointDetailResponse(
                checkpoint_id=cp.checkpoint_id,
                description=cp.description,
                importance=cp.importance,
                completed=cp.completed,
                completed_at_turn=cp.completed_at_turn,
                trainee_action=cp.trainee_action
            )
            for cp in report.checkpoint_details
        ]
        
        # Map skill scores
        skill_scores = [
            SkillScoreResponse(
                skill_name=ss.skill_name,
                score=ss.score,
                max_score=ss.max_score,
                evidence=ss.evidence,
                recommendation=ss.recommendation
            )
            for ss in report.skill_scores
        ]
        
        # Map coaching summary
        coaching_summary = None
        if report.coaching_summary:
            coaching_summary = CoachingInterventionResponse(
                total_hints=report.coaching_summary.total_hints,
                total_warnings=report.coaching_summary.total_warnings,
                total_praise=report.coaching_summary.total_praise,
                interventions=report.coaching_summary.interventions
            )
        
        # Map conversation analysis
        conversation_analysis = [
            ConversationTurnResponse(
                turn_number=ca.turn_number,
                trainee_message=ca.trainee_message,
                customer_response=ca.customer_response,
                coach_intervention=ca.coach_intervention,
                intervention_type=ca.intervention_type,
                timestamp=ca.timestamp
            )
            for ca in report.conversation_analysis
        ]
        
        # Map watch out warnings
        watch_out_warnings = [
            WatchOutWarningResponse(
                category=w.category,
                behavior=w.behavior,
                frequency=w.frequency,
                severity=w.severity,
                example_turn=w.example_turn,
                example_quote=w.example_quote,
                coaching_suggestion=w.coaching_suggestion
            )
            for w in report.watch_out_warnings
        ]
        
        return SessionReportResponse(
            session_id=report.session_id,
            case_title=report.case_title,
            case_id=report.case_id,
            trainee_id=report.trainee_id,
            difficulty=report.difficulty,
            primary_skill=report.primary_skill,
            
            # Timeline
            started_at=report.started_at,
            ended_at=report.ended_at,
            total_turns=report.total_turns,
            duration_minutes=report.duration_minutes,
            completion_status=report.completion_status,
            
            # Overall Performance
            overall_score=report.overall_score,
            performance_rating=report.performance_rating,
            
            # Checkpoints
            checkpoints_completed=report.checkpoints_completed,
            total_checkpoints=report.total_checkpoints,
            completion_percentage=report.completion_percentage,
            checkpoint_details=checkpoint_details,
            
            # Skills
            skill_scores=skill_scores,
            
            # Coaching
            hints_received=report.hints_received,
            coaching_summary=coaching_summary,
            
            # Qualitative Feedback
            strengths=report.strengths,
            opportunities=report.opportunities,
            summary_feedback=report.summary_feedback,
            manager_notes=report.manager_notes,
            
            # Conversation Analysis
            conversation_analysis=conversation_analysis,
            key_moments=report.key_moments,
            
            # Full Transcript
            transcript=report.transcript,
            
            # Watch Out Warnings
            watch_out_warnings=watch_out_warnings,
            
            # Recommendations
            recommended_training=report.recommended_training,
            follow_up_actions=report.follow_up_actions,
            
            generated_at=report.generated_at
        )
        
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Failed to end simulation: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to generate report")


@router.get("/{session_id}/status")
async def get_session_status(
    session_id: str,
    orchestrator: SimulationOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Get the current status of a simulation session.
    """
    session = orchestrator.get_session(session_id)
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {
        "session_id": session.session_id,
        "case_id": session.case_id,
        "is_active": session.is_active,
        "turn_count": session.turn_count,
        "checkpoints_completed": session.checkpoints_completed,
        "total_checkpoints": session.total_checkpoints,
        "hints_received": session.hints_received,
        "started_at": session.started_at,
        "ended_at": session.ended_at,
        "idle_seconds": orchestrator.get_idle_seconds(session_id) or 0,
        "session_timeout_seconds": SESSION_TIMEOUT_SECONDS,
        "session_warning_seconds": SESSION_WARNING_SECONDS,
    }


@router.post("/{session_id}/keepalive")
async def keep_session_alive(
    session_id: str,
    orchestrator: SimulationOrchestrator = Depends(get_orchestrator)
) -> Dict[str, Any]:
    """
    Keep a simulation session alive by resetting its idle timer.
    Call this when the user clicks "Continue Session" on the expiry warning.
    """
    success = orchestrator.touch_session(session_id)
    if not success:
        raise HTTPException(status_code=404, detail="Session not found or already ended")
    return {
        "status": "alive",
        "session_id": session_id,
        "session_timeout_seconds": SESSION_TIMEOUT_SECONDS,
    }


@router.delete("/{session_id}")
async def cleanup_session(
    session_id: str,
    orchestrator: SimulationOrchestrator = Depends(get_orchestrator)
) -> Dict[str, str]:
    """
    Clean up a simulation session from memory.
    """
    orchestrator.cleanup_session(session_id)
    return {"status": "cleaned up", "session_id": session_id}


def _load_cases_directly() -> List[Dict[str, Any]]:
    """Load cases directly from JSON files without requiring orchestrator."""
    import json
    from pathlib import Path
    cases = []
    cases_dir = Path(__file__).parent.parent.parent / "data" / "cases"
    
    if not cases_dir.exists():
        logger.warning(f"Cases directory not found: {cases_dir}")
        return cases
    
    for case_file in cases_dir.glob("*.json"):
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
                })
        except Exception as e:
            logger.warning(f"Failed to load case {case_file}: {e}")
    
    return cases
