import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// =============================================================================
// Types
// =============================================================================

export interface CaseListItem {
  case_id: string
  title: string
  difficulty: 'beginner' | 'intermediate' | 'advanced'
  primary_skill: string
  estimated_time: number
  tags: string[]
  context?: string
}

export interface StartSessionRequest {
  case_id: string
  trainee_id?: string
}

export interface StartSessionResponse {
  session_id: string
  case_id: string
  title: string
  difficulty: string
  primary_skill: string
  customer_name: string
  opening_message: string
  total_checkpoints: number
}

export interface ChatRequest {
  message: string
}

export interface CoachFeedback {
  type: 'HINT' | 'PRAISE' | 'WARNING' | 'CHECKPOINT'
  content: string
}

export interface CheckpointStatus {
  checkpoint_id: number
  description: string
  completed: boolean
  completed_at?: string
  turn_completed?: number
}

export interface SessionStats {
  turn_count: number
  checkpoints_completed: number
  total_checkpoints: number
  hints_received: number
  is_active: boolean
}

export interface ChatResponse {
  customer_response: string
  coach_feedback: CoachFeedback | null
  checkpoint_status: CheckpointStatus[]
  session_stats: SessionStats
}

export interface AskCoachRequest {
  question?: string
}

export interface AskCoachResponse {
  advice: string
}

// Detailed report types
export interface SkillScore {
  skill_name: string
  score: number
  max_score: number
  evidence: string[]
  recommendation: string | null
}

export interface CheckpointDetail {
  checkpoint_id: number
  description: string
  importance: string
  completed: boolean
  completed_at_turn: number | null
  trainee_action: string | null
}

export interface CoachingInterventionSummary {
  total_hints: number
  total_warnings: number
  total_praise: number
  interventions: Array<{
    turn: number
    type: string
    content: string
  }>
}

export interface ConversationTurnAnalysis {
  turn_number: number
  trainee_message: string
  customer_response: string
  coach_intervention: string | null
  intervention_type: string | null
  timestamp: string
}

export interface KeyMoment {
  turn: number
  type: 'positive' | 'negative' | 'missed_opportunity'
  description: string
}

export interface WatchOutWarning {
  category: string
  behavior: string
  frequency: 'once' | 'multiple_times' | 'pattern'
  severity: 'low' | 'medium' | 'high'
  example_turn: number | null
  example_quote: string | null
  coaching_suggestion: string
}

export interface SessionReport {
  session_id: string
  case_title: string
  case_id: string
  trainee_id: string | null
  difficulty: string
  primary_skill: string
  
  // Timeline
  started_at: string
  ended_at: string
  total_turns: number
  duration_minutes: number
  completion_status: string
  
  // Overall Performance
  overall_score: number
  performance_rating: string
  
  // Checkpoints
  checkpoints_completed: number
  total_checkpoints: number
  completion_percentage: number
  checkpoint_details: CheckpointDetail[]
  
  // Skills
  skill_scores: SkillScore[]
  
  // Coaching
  hints_received: number
  coaching_summary: CoachingInterventionSummary | null
  
  // Qualitative Feedback
  strengths: string[]
  opportunities: string[]
  summary_feedback: string
  manager_notes: string
  
  // Conversation Analysis
  conversation_analysis: ConversationTurnAnalysis[]
  key_moments: KeyMoment[]
  
  // Full Transcript
  transcript: Array<{
    role: string
    content: string
    timestamp: string
  }>
  
  // Watch Out Warnings for Manager
  watch_out_warnings: WatchOutWarning[]
  
  // Recommendations
  recommended_training: string[]
  follow_up_actions: string[]
  
  generated_at: string
}

export interface SessionStatus {
  session_id: string
  case_id: string
  is_active: boolean
  turn_count: number
  checkpoints_completed: number
  total_checkpoints: number
  hints_received: number
  started_at: string
  ended_at: string | null
  idle_seconds: number
  session_timeout_seconds: number
  session_warning_seconds: number
}

export interface KeepAliveResponse {
  status: string
  session_id: string
  session_timeout_seconds: number
}

// =============================================================================
// Simulation API Service
// =============================================================================

export const simulationService = {
  /**
   * Get list of available training cases
   */
  async listCases(): Promise<CaseListItem[]> {
    const response = await apiClient.get<CaseListItem[]>('/in-flow-simulation/cases')
    return response.data
  },

  /**
   * Start a new simulation session
   */
  async startSession(request: StartSessionRequest): Promise<StartSessionResponse> {
    const response = await apiClient.post<StartSessionResponse>('/in-flow-simulation/start', request)
    return response.data
  },

  /**
   * Send a message in the simulation
   */
  async sendMessage(sessionId: string, message: string): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(
      `/in-flow-simulation/${sessionId}/chat`,
      { message }
    )
    return response.data
  },

  /**
   * Explicitly ask the coach for help
   */
  async askCoach(sessionId: string, question?: string): Promise<AskCoachResponse> {
    const response = await apiClient.post<AskCoachResponse>(
      `/in-flow-simulation/${sessionId}/ask-coach`,
      { question }
    )
    return response.data
  },

  /**
   * End the simulation and get the report
   */
  async endSession(sessionId: string): Promise<SessionReport> {
    const response = await apiClient.post<SessionReport>(`/in-flow-simulation/${sessionId}/end`)
    return response.data
  },

  /**
   * Get current session status
   */
  async getSessionStatus(sessionId: string): Promise<SessionStatus> {
    const response = await apiClient.get<SessionStatus>(`/in-flow-simulation/${sessionId}/status`)
    return response.data
  },

  /**
   * Clean up a session
   */
  async cleanupSession(sessionId: string): Promise<void> {
    await apiClient.delete(`/in-flow-simulation/${sessionId}`)
  },

  /**
   * Keep a session alive (reset idle timer)
   */
  async keepAlive(sessionId: string): Promise<KeepAliveResponse> {
    const response = await apiClient.post<KeepAliveResponse>(
      `/in-flow-simulation/${sessionId}/keepalive`
    )
    return response.data
  },
}

export default simulationService
