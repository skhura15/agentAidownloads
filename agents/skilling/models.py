"""
Skilling Agent Data Models

Pydantic models for the Contact Center Knowledge-Based Coach POC.
Defines the data structures for cases, simulation configs, and session state.
"""

from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


# =============================================================================
# INPUT: Case Data (The SME Bundle / Golden Record)
# =============================================================================

class CaseAnnotations(BaseModel):
    """SME annotations for a training case"""
    sme_author: str = Field(..., description="Name of the SME who created annotations")
    sme_date: str = Field(..., description="Date annotations were created")
    learning_objectives: List[str] = Field(default_factory=list, description="What trainee should learn")
    correct_sop_steps: List[str] = Field(..., description="The correct steps to follow")
    common_mistakes: List[str] = Field(default_factory=list, description="Mistakes to watch for")
    success_criteria: Dict[str, List[str]] = Field(default_factory=dict, description="What constitutes success")
    sticky_notes: List[str] = Field(default_factory=list, description="Quick tips for the coach")


class CaseRawContent(BaseModel):
    """Original ticket content"""
    channel: str = Field(default="chat", description="Communication channel")
    customer_name: str = Field(..., description="Customer's name")
    initial_message: str = Field(..., description="Customer's opening message")
    context: str = Field(..., description="Background context for the scenario")


class CustomerPersonaHints(BaseModel):
    """Hints for building the customer persona"""
    tone: str = Field(..., description="Customer's emotional tone")
    secret_acceptance_condition: str = Field(..., description="What will satisfy the customer")
    escalation_triggers: List[str] = Field(default_factory=list, description="What makes customer angrier")
    de_escalation_triggers: List[str] = Field(default_factory=list, description="What calms customer down")


class CaseData(BaseModel):
    """
    The Golden Record - SME-annotated case for training.
    This is the INPUT to the ScenarioArchitect agent.
    """
    ticket_id: str = Field(..., description="Unique ticket identifier")
    title: str = Field(..., description="Case title for display")
    difficulty: str = Field(default="intermediate", description="beginner, intermediate, advanced")
    estimated_time_minutes: int = Field(default=10, description="Expected completion time")
    primary_skill: str = Field(..., description="Main skill being practiced")
    tags: List[str] = Field(default_factory=list, description="Searchable tags")
    
    raw_content: CaseRawContent = Field(..., description="Original ticket content")
    annotations: CaseAnnotations = Field(..., description="SME annotations")
    customer_persona_hints: CustomerPersonaHints = Field(..., description="Persona construction hints")


# =============================================================================
# OUTPUT: Simulation Config (The Game State)
# =============================================================================

class CustomerProfile(BaseModel):
    """Generated customer persona for simulation"""
    name: str = Field(..., description="Customer's name")
    tone: str = Field(..., description="Emotional tone description")
    knowledge_level: str = Field(default="average", description="Customer's technical knowledge")
    opening_message: str = Field(..., description="First message to send")
    secret_condition: str = Field(..., description="Hidden acceptance condition")
    escalation_triggers: List[str] = Field(default_factory=list, description="Phrases that anger customer")
    de_escalation_triggers: List[str] = Field(default_factory=list, description="Phrases that calm customer")
    personality_notes: str = Field(default="", description="Additional personality details")


class CoachingCheckpoint(BaseModel):
    """A single checkpoint in the coaching rubric"""
    id: int = Field(..., description="Checkpoint ID")
    description: str = Field(..., description="What this checkpoint evaluates")
    trigger_phrases: List[str] = Field(default_factory=list, description="Phrases that satisfy this checkpoint")
    importance: str = Field(default="required", description="required, recommended, bonus")
    hint_if_missed: str = Field(default="", description="Hint to show if trainee misses this")


class CoachingRubric(BaseModel):
    """The evaluation rubric for the shadow coach"""
    checkpoints: List[CoachingCheckpoint] = Field(default_factory=list, description="Evaluation checkpoints")
    common_mistakes_to_watch: List[str] = Field(default_factory=list, description="Mistakes that trigger hints")
    positive_reinforcement_triggers: List[str] = Field(default_factory=list, description="Good actions to praise")


class SimulationConfig(BaseModel):
    """
    The Game State - Generated by ScenarioArchitect from CaseData.
    This is the OUTPUT used to configure runtime agents.
    """
    case_id: str = Field(..., description="Reference to original case")
    title: str = Field(..., description="Scenario title")
    difficulty: str = Field(..., description="Difficulty level")
    primary_skill: str = Field(..., description="Main skill being practiced")
    
    customer_profile: CustomerProfile = Field(..., description="Customer persona configuration")
    coaching_rubric: CoachingRubric = Field(..., description="Evaluation rubric")
    
    scenario_context: str = Field(..., description="Context for the coach to understand the scenario")
    success_summary: str = Field(..., description="What constitutes successful completion")
    max_turns: int = Field(default=20, description="Maximum conversation turns")
    
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())


# =============================================================================
# SESSION STATE: Runtime tracking
# =============================================================================

class MessageRole(str, Enum):
    """Who sent the message"""
    USER = "user"           # The trainee
    CUSTOMER = "customer"   # CustomerSim agent
    COACH = "coach"         # ShadowCoach hints (sidebar only)
    SYSTEM = "system"       # System messages


class SimulationMessage(BaseModel):
    """A single message in the simulation"""
    role: MessageRole = Field(..., description="Who sent the message")
    content: str = Field(..., description="Message content")
    timestamp: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional metadata")
    visible_to_trainee: bool = Field(default=True, description="Whether trainee sees this")


class CheckpointStatus(BaseModel):
    """Status of a coaching checkpoint"""
    checkpoint_id: int
    description: str
    completed: bool = False
    completed_at: Optional[str] = None
    turn_completed: Optional[int] = None


class SimulationSession(BaseModel):
    """Active simulation session state"""
    session_id: str = Field(..., description="Unique session identifier")
    case_id: str = Field(..., description="Which case is being practiced")
    trainee_id: Optional[str] = Field(default=None, description="Trainee identifier")
    
    config: SimulationConfig = Field(..., description="Simulation configuration")
    
    messages: List[SimulationMessage] = Field(default_factory=list, description="Conversation history")
    main_chat_messages: List[SimulationMessage] = Field(default_factory=list, description="Main chat only")
    coach_hints: List[SimulationMessage] = Field(default_factory=list, description="Sidebar hints only")
    
    checkpoint_status: List[CheckpointStatus] = Field(default_factory=list, description="Progress tracking")
    
    turn_count: int = Field(default=0, description="Current turn number")
    started_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
    ended_at: Optional[str] = Field(default=None, description="When session ended")
    is_active: bool = Field(default=True, description="Whether session is still active")
    last_activity: str = Field(default_factory=lambda: datetime.utcnow().isoformat(), description="Last activity timestamp")
    
    # Performance metrics
    hints_received: int = Field(default=0, description="Number of coach hints received")
    checkpoints_completed: int = Field(default=0, description="Checkpoints achieved")
    total_checkpoints: int = Field(default=0, description="Total checkpoints in rubric")


# =============================================================================
# POST-SESSION: Report Card
# =============================================================================

class ConversationTurnAnalysis(BaseModel):
    """Analysis of a single conversation turn"""
    turn_number: int
    trainee_message: str
    customer_response: str
    coach_intervention: Optional[str] = None
    intervention_type: Optional[str] = None  # HINT, PRAISE, WARNING, CHECKPOINT
    checkpoint_completed: Optional[int] = None
    skill_demonstrated: Optional[str] = None
    timestamp: str


class CheckpointDetail(BaseModel):
    """Detailed checkpoint information for report"""
    checkpoint_id: int
    description: str
    importance: str  # critical, high, medium
    completed: bool
    completed_at_turn: Optional[int] = None
    trainee_action: Optional[str] = None  # What the trainee said/did to complete it


class SkillScore(BaseModel):
    """Score for a specific skill category"""
    skill_name: str
    score: int  # 1-5 scale
    max_score: int = 5
    evidence: List[str] = Field(default_factory=list)  # Specific examples from conversation
    recommendation: Optional[str] = None


class CoachingInterventionSummary(BaseModel):
    """Summary of coaching interventions"""
    total_hints: int
    total_warnings: int
    total_praise: int
    interventions: List[Dict[str, Any]] = Field(default_factory=list)


class WatchOutWarning(BaseModel):
    """Specific behavior pattern for manager to watch out for"""
    category: str  # e.g., "Communication", "Empathy", "Process", "Escalation"
    behavior: str  # The specific behavior observed
    frequency: str  # "once", "multiple times", "pattern"
    severity: str  # "low", "medium", "high"
    example_turn: Optional[int] = None  # Turn number where this was observed
    example_quote: Optional[str] = None  # Specific quote showing the behavior
    coaching_suggestion: str  # What the manager should discuss/coach


class SessionReport(BaseModel):
    """Comprehensive post-session performance report for manager review"""
    session_id: str
    case_id: str
    case_title: str
    trainee_id: Optional[str] = None
    difficulty: str = "intermediate"
    primary_skill: str = ""
    
    # Session Timeline
    started_at: str = ""
    ended_at: str = ""
    total_turns: int
    duration_minutes: float
    completion_status: str  # "completed", "abandoned", "timeout"
    
    # Overall Performance Score
    overall_score: int = 0  # 1-100 scale
    performance_rating: str = ""  # Excellent, Good, Developing, Needs Improvement
    
    # Checkpoint Performance
    checkpoints_completed: int
    total_checkpoints: int
    completion_percentage: float
    checkpoint_details: List[CheckpointDetail] = Field(default_factory=list)
    
    # Skill-based Scoring (detailed rubric)
    skill_scores: List[SkillScore] = Field(default_factory=list)
    
    # Coaching Interventions Analysis
    hints_received: int
    coaching_summary: Optional[CoachingInterventionSummary] = None
    
    # Qualitative Feedback
    strengths: List[str] = Field(default_factory=list)
    opportunities: List[str] = Field(default_factory=list)
    summary_feedback: str = ""
    manager_notes: str = ""  # AI-generated notes specifically for manager
    
    # Detailed Conversation Analysis
    conversation_analysis: List[ConversationTurnAnalysis] = Field(default_factory=list)
    key_moments: List[Dict[str, Any]] = Field(default_factory=list)  # Critical good/bad moments
    
    # Full Transcript (for reference)
    transcript: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Watch Out Warnings for Manager
    watch_out_warnings: List[WatchOutWarning] = Field(default_factory=list)
    
    # Recommendations
    recommended_training: List[str] = Field(default_factory=list)
    follow_up_actions: List[str] = Field(default_factory=list)
    
    generated_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())
