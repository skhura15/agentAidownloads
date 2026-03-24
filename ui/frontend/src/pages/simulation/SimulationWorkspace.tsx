import { useState, useEffect, useRef, useCallback } from 'react'
import { useParams, useNavigate, useLocation } from 'react-router-dom'
import { 
  simulationService, 
  StartSessionResponse, 
  ChatResponse,
  CheckpointStatus,
  CoachFeedback,
  SessionReport 
} from '../../services/simulationApi'
import ObjectivesSidebar from './ObjectivesSidebar'
import CoachSidebar from './CoachSidebar'
import SessionReportModal from './SessionReportModal'
import SessionExpiryWarning from './SessionExpiryWarning'

// Default timeout values (overridden by server response)
const DEFAULT_TIMEOUT_SECONDS = 900   // 15 minutes
const DEFAULT_WARNING_SECONDS = 720   // 12 minutes (warn 3 min before)

interface Message {
  id: string
  role: 'user' | 'customer'
  content: string
  timestamp: Date
  customerName?: string
}

export default function SimulationWorkspace() {
  const { sessionId } = useParams<{ sessionId: string }>()
  const navigate = useNavigate()
  const location = useLocation()
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLTextAreaElement>(null)

  // Session state
  const [session, _setSession] = useState<StartSessionResponse | null>(
    location.state?.session || null
  )
  const [messages, setMessages] = useState<Message[]>([])
  const [inputValue, setInputValue] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [error, setError] = useState<string | null>(null)

  // Coaching state
  const [coachHints, setCoachHints] = useState<CoachFeedback[]>([])
  const [checkpoints, setCheckpoints] = useState<CheckpointStatus[]>([])
  const [sessionStats, setSessionStats] = useState({
    turn_count: 0,
    checkpoints_completed: 0,
    total_checkpoints: 0,
    hints_received: 0,
    is_active: true,
  })

  // Report modal
  const [showReport, setShowReport] = useState(false)
  const [report, setReport] = useState<SessionReport | null>(null)
  const [isEndingSession, setIsEndingSession] = useState(false)

  // Session expiry warning state
  const [showExpiryWarning, setShowExpiryWarning] = useState(false)
  const [secondsRemaining, setSecondsRemaining] = useState(0)
  const lastActivityRef = useRef<number>(Date.now())
  const sessionTimeoutRef = useRef(DEFAULT_TIMEOUT_SECONDS)
  const sessionWarningRef = useRef(DEFAULT_WARNING_SECONDS)
  const expiryTimerRef = useRef<ReturnType<typeof setInterval> | null>(null)

  // Reset local idle timer whenever the user takes an action
  const resetIdleTimer = useCallback(() => {
    lastActivityRef.current = Date.now()
    setShowExpiryWarning(false)
  }, [])

  // Idle-check interval: runs every second, calculates local idle time
  useEffect(() => {
    if (!sessionStats.is_active) {
      // Session ended — stop checking
      if (expiryTimerRef.current) clearInterval(expiryTimerRef.current)
      setShowExpiryWarning(false)
      return
    }

    expiryTimerRef.current = setInterval(() => {
      const idleMs = Date.now() - lastActivityRef.current
      const idleSec = Math.floor(idleMs / 1000)
      const remaining = sessionTimeoutRef.current - idleSec

      if (remaining <= 0) {
        // Session has timed out
        setShowExpiryWarning(false)
        setError('Session expired due to inactivity. Redirecting...')
        setTimeout(() => navigate('/in-flow-simulation'), 2000)
      } else if (idleSec >= sessionWarningRef.current) {
        setShowExpiryWarning(true)
        setSecondsRemaining(remaining)
      } else {
        setShowExpiryWarning(false)
      }
    }, 1000)

    return () => {
      if (expiryTimerRef.current) clearInterval(expiryTimerRef.current)
    }
  }, [sessionStats.is_active, navigate])

  // Handle "Continue Session" click
  const handleKeepAlive = useCallback(async () => {
    if (!sessionId) return
    // Reset idle timer immediately so the interval doesn't expire during the API call
    resetIdleTimer()
    try {
      const res = await simulationService.keepAlive(sessionId)
      sessionTimeoutRef.current = res.session_timeout_seconds
    } catch (err: any) {
      if (err?.response?.status === 404) {
        // Session has genuinely expired on the server (e.g. after redeployment)
        setError('Session has expired on the server. Redirecting to scenarios...')
        setTimeout(() => navigate('/in-flow-simulation'), 2500)
      } else {
        // Network error or transient issue — don't navigate away
        setError('Could not reach the server to extend session. You can keep chatting.')
        setTimeout(() => setError(null), 5000)
      }
    }
  }, [sessionId, resetIdleTimer, navigate])

  // Initialize session
  useEffect(() => {
    if (!session && sessionId) {
      // Fetch session status if not passed via state
      simulationService.getSessionStatus(sessionId)
        .then((status) => {
          // Redirect if session not found
          if (!status.is_active) {
            navigate('/in-flow-simulation')
          }
        })
        .catch(() => {
          navigate('/in-flow-simulation')
        })
    } else if (session) {
      // Add opening message
      setMessages([{
        id: 'opening',
        role: 'customer',
        content: session.opening_message,
        timestamp: new Date(),
        customerName: session.customer_name,
      }])
      setSessionStats(prev => ({
        ...prev,
        total_checkpoints: session.total_checkpoints,
      }))
    }
  }, [session, sessionId, navigate])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Handle sending a message
  const handleSendMessage = async () => {
    if (!inputValue.trim() || isLoading || !sessionId) return

    // Reset idle timer on user activity
    resetIdleTimer()

    const userMessage: Message = {
      id: `user-${Date.now()}`,
      role: 'user',
      content: inputValue.trim(),
      timestamp: new Date(),
    }

    setMessages(prev => [...prev, userMessage])
    setInputValue('')
    setIsLoading(true)
    setError(null)

    try {
      const response: ChatResponse = await simulationService.sendMessage(
        sessionId,
        userMessage.content
      )

      // Add customer response
      const customerMessage: Message = {
        id: `customer-${Date.now()}`,
        role: 'customer',
        content: response.customer_response,
        timestamp: new Date(),
        customerName: session?.customer_name,
      }
      setMessages(prev => [...prev, customerMessage])

      // Update coaching state
      if (response.coach_feedback) {
        setCoachHints(prev => [...prev, response.coach_feedback!])
      }
      setCheckpoints(response.checkpoint_status)
      setSessionStats(response.session_stats)

      // Check if session ended
      if (!response.session_stats.is_active) {
        handleEndSession()
      }
    } catch (err: any) {
      if (err?.response?.status === 404) {
        setError('Session not found or expired. Please start a new simulation.')
        // Auto-redirect after a short delay
        setTimeout(() => navigate('/in-flow-simulation'), 3000)
      } else if (err?.response?.status === 503) {
        setError('Simulation service is not available. Please try again later.')
      } else {
        setError('Failed to send message. Please try again.')
      }
      console.error('Send message error:', err)
    } finally {
      setIsLoading(false)
      inputRef.current?.focus()
    }
  }

  // Handle asking coach for help
  const handleAskCoach = async (question?: string) => {
    if (!sessionId) return
    resetIdleTimer()

    try {
      const response = await simulationService.askCoach(sessionId, question)
      setCoachHints(prev => [...prev, { type: 'HINT', content: response.advice }])
    } catch (err) {
      console.error('Ask coach error:', err)
    }
  }

  // Handle ending the session
  const handleEndSession = async () => {
    if (!sessionId || isEndingSession) return

    setIsEndingSession(true)
    try {
      const sessionReport = await simulationService.endSession(sessionId)
      setReport(sessionReport)
      setShowReport(true)
    } catch (err) {
      console.error('End session error:', err)
      navigate('/in-flow-simulation')
    } finally {
      setIsEndingSession(false)
    }
  }

  // Handle keyboard shortcuts
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSendMessage()
    }
  }

  if (!session) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
          </svg>
          <p className="text-gray-600 dark:text-gray-400">Loading simulation...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="h-screen flex flex-col bg-gray-100 dark:bg-gray-900">
      {/* Header */}
      <header className="bg-white dark:bg-gray-800 shadow-sm px-4 py-3 flex items-center justify-between">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => navigate('/in-flow-simulation')}
            className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
          >
            ← Exit
          </button>
          <div className="border-l border-gray-300 dark:border-gray-600 h-6"></div>
          <div>
            <h1 className="font-semibold text-gray-900 dark:text-white">
              {session.title}
            </h1>
            <p className="text-sm text-gray-500 dark:text-gray-400">
              Skill: {session.primary_skill} • Customer: {session.customer_name}
            </p>
          </div>
        </div>
        <button
          onClick={handleEndSession}
          disabled={isEndingSession}
          className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors flex items-center space-x-2 ${
            isEndingSession
              ? 'bg-gray-200 dark:bg-gray-700 text-gray-400 dark:text-gray-500 cursor-not-allowed'
              : 'bg-red-100 hover:bg-red-200 dark:bg-red-900/50 dark:hover:bg-red-900 text-red-700 dark:text-red-300'
          }`}
        >
          {isEndingSession && (
            <svg className="animate-spin h-4 w-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
          )}
          <span>{isEndingSession ? 'Generating Report...' : 'End Session'}</span>
        </button>
      </header>

      {/* Session Expiry Warning Banner */}
      {showExpiryWarning && (
        <SessionExpiryWarning
          secondsRemaining={secondsRemaining}
          onContinue={handleKeepAlive}
          onDismiss={() => setShowExpiryWarning(false)}
        />
      )}

      {/* Main Content - Split View */}
      <div className="flex-1 flex overflow-hidden">
        {/* Left Panel - Objectives Sidebar */}
        <ObjectivesSidebar
          checkpoints={checkpoints}
          stats={sessionStats}
        />

        {/* Center Panel - Chat */}
        <div className="flex-1 flex flex-col bg-white dark:bg-gray-800">
          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.map((message) => (
              <div
                key={message.id}
                className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-2 ${
                    message.role === 'user'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-100 dark:bg-gray-700 text-gray-900 dark:text-white'
                  }`}
                >
                  {message.role === 'customer' && (
                    <p className="text-xs font-medium text-gray-500 dark:text-gray-400 mb-1">
                      {message.customerName}
                    </p>
                  )}
                  <p className="whitespace-pre-wrap">{message.content}</p>
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-gray-100 dark:bg-gray-700 rounded-lg px-4 py-2">
                  <div className="flex space-x-2">
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce"></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></div>
                    <div className="w-2 h-2 bg-gray-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></div>
                  </div>
                </div>
              </div>
            )}
            
            <div ref={messagesEndRef} />
          </div>

          {/* Error */}
          {error && (
            <div className="px-4 py-2 bg-red-50 dark:bg-red-900/50 text-red-700 dark:text-red-300 text-sm">
              {error}
            </div>
          )}

          {/* Input */}
          <div className="border-t border-gray-200 dark:border-gray-700 p-4">
            <div className="flex space-x-2">
              <textarea
                ref={inputRef}
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="Type your response to the customer..."
                rows={2}
                disabled={!sessionStats.is_active}
                className="flex-1 resize-none rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-4 py-2 text-gray-900 dark:text-white placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 disabled:opacity-50"
              />
              <button
                onClick={handleSendMessage}
                disabled={!inputValue.trim() || isLoading || !sessionStats.is_active}
                className="px-6 py-2 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white rounded-lg font-medium transition-colors"
              >
                Send
              </button>
            </div>
            <p className="text-xs text-gray-500 dark:text-gray-400 mt-2">
              Press Enter to send, Shift+Enter for new line
            </p>
          </div>
        </div>

        {/* Right Panel - Coach Sidebar */}
        <CoachSidebar
          hints={coachHints}
          stats={sessionStats}
          onAskCoach={handleAskCoach}
        />
      </div>

      {/* Report Modal */}
      {isEndingSession && (
        <div className="fixed inset-0 bg-black/50 z-50 flex items-center justify-center">
          <div className="bg-white dark:bg-gray-800 rounded-2xl p-8 text-center shadow-2xl max-w-sm mx-4">
            <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z"></path>
            </svg>
            <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2">Generating Report</h3>
            <p className="text-sm text-gray-500 dark:text-gray-400">Analyzing your session performance...</p>
          </div>
        </div>
      )}
      {showReport && report && (
        <SessionReportModal
          report={report}
          onClose={() => {
            setShowReport(false)
            navigate('/in-flow-simulation')
          }}
          onTryAgain={() => {
            setShowReport(false)
            if (session) {
              navigate('/in-flow-simulation')
            }
          }}
        />
      )}
    </div>
  )
}
