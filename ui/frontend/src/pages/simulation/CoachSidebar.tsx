import { useState } from 'react'
import { CoachFeedback } from '../../services/simulationApi'

interface CoachSidebarProps {
  hints: CoachFeedback[]
  stats: {
    turn_count: number
    checkpoints_completed: number
    total_checkpoints: number
    hints_received: number
    is_active: boolean
  }
  onAskCoach: (question?: string) => void
  hasRudeTone?: boolean
}

// Feedback type styling
const feedbackStyles = {
  HINT: {
    bg: 'bg-blue-50 dark:bg-blue-900/30',
    border: 'border-blue-200 dark:border-blue-800',
    icon: '💡',
    title: 'Tip',
    textColor: 'text-blue-800 dark:text-blue-200',
  },
  PRAISE: {
    bg: 'bg-green-50 dark:bg-green-900/30',
    border: 'border-green-200 dark:border-green-800',
    icon: '⭐',
    title: 'Nice!',
    textColor: 'text-green-800 dark:text-green-200',
  },
  WARNING: {
    bg: 'bg-amber-50 dark:bg-amber-900/30',
    border: 'border-amber-200 dark:border-amber-800',
    icon: '⚠️',
    title: 'Watch out',
    textColor: 'text-amber-800 dark:text-amber-200',
  },
  CHECKPOINT: {
    bg: 'bg-purple-50 dark:bg-purple-900/30',
    border: 'border-purple-200 dark:border-purple-800',
    icon: '✅',
    title: 'Checkpoint!',
    textColor: 'text-purple-800 dark:text-purple-200',
  },
}

export default function CoachSidebar({
  hints,
  stats,
  onAskCoach,
  hasRudeTone = false,
}: CoachSidebarProps) {
  const [isAskingCoach, setIsAskingCoach] = useState(false)
  const [askQuestion, setAskQuestion] = useState('')

  const handleAskCoach = () => {
    onAskCoach(askQuestion || undefined)
    setAskQuestion('')
    setIsAskingCoach(false)
  }

  return (
    <div className="w-80 bg-gray-50 dark:bg-gray-850 border-l border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <h2 className="font-semibold text-gray-900 dark:text-white flex items-center">
          <span className="w-2 h-2 bg-green-500 rounded-full mr-2 animate-pulse"></span>
          Coach
        </h2>
      </div>

      {/* Content - Scrollable */}
      <div className="flex-1 overflow-y-auto">
        {/* DEBUG: Show prop value */}
        {import.meta.env.DEV && (
          <div className="text-xs text-gray-500 p-2 border-b border-gray-200">
            Debug: hasRudeTone = {String(hasRudeTone)}
          </div>
        )}
        
        {/* Rude Tone Warning */}
        {hasRudeTone && (
          <div className="p-3 m-3 bg-red-50 dark:bg-red-900/30 border border-red-200 dark:border-red-800 rounded-lg animate-pulse">
            <div className="flex items-start space-x-2">
              <span className="text-lg">⚠️</span>
              <div>
                <p className="text-xs font-medium text-red-800 dark:text-red-200 mb-1">
                  Watch out - Tone Alert
                </p>
                <p className="text-sm text-red-700 dark:text-red-300 font-semibold">
                  Your tone seems rude or aggressive. Remember to stay professional and respectful.
                </p>
              </div>
            </div>
          </div>
        )}

        {/* Live Feedback Cards */}
        <div className="p-4 space-y-3">
          {hints.length === 0 ? (
            <div className="text-center py-8">
              <span className="text-4xl mb-2 block">👀</span>
              <p className="text-sm text-gray-500 dark:text-gray-400">
                I'm watching and ready to help!
              </p>
            </div>
          ) : (
            hints.slice(-5).map((hint, index) => {
              const style = feedbackStyles[hint.type] || feedbackStyles.HINT
              return (
                <div
                  key={index}
                  className={`${style.bg} ${style.border} border rounded-lg p-3 animate-fadeIn`}
                >
                  <div className="flex items-start space-x-2">
                    <span className="text-lg">{style.icon}</span>
                    <div>
                      <p className={`text-xs font-medium ${style.textColor} mb-1`}>
                        {style.title}
                      </p>
                      <p className="text-sm text-gray-700 dark:text-gray-300">
                        {hint.content}
                      </p>
                    </div>
                  </div>
                </div>
              )
            })
          )}
        </div>
      </div>

      {/* Ask Coach Button */}
      <div className="p-4 border-t border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        {isAskingCoach ? (
          <div className="space-y-2">
            <textarea
              value={askQuestion}
              onChange={(e) => setAskQuestion(e.target.value)}
              placeholder="What do you need help with? (optional)"
              rows={2}
              className="w-full text-sm rounded-lg border border-gray-300 dark:border-gray-600 bg-white dark:bg-gray-700 px-3 py-2 text-gray-900 dark:text-white placeholder-gray-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500"
            />
            <div className="flex space-x-2">
              <button
                onClick={handleAskCoach}
                className="flex-1 py-2 bg-blue-600 hover:bg-blue-700 text-white text-sm font-medium rounded-lg transition-colors"
              >
                Get Help
              </button>
              <button
                onClick={() => setIsAskingCoach(false)}
                className="px-3 py-2 text-gray-600 dark:text-gray-400 hover:text-gray-900 dark:hover:text-white text-sm transition-colors"
              >
                Cancel
              </button>
            </div>
          </div>
        ) : (
          <button
            onClick={() => setIsAskingCoach(true)}
            disabled={!stats.is_active}
            className="w-full py-2 px-4 bg-gradient-to-r from-blue-500 to-purple-500 hover:from-blue-600 hover:to-purple-600 disabled:opacity-50 text-white font-medium rounded-lg transition-all flex items-center justify-center space-x-2"
          >
            <span>🙋</span>
            <span>Ask Coach for Help</span>
          </button>
        )}
      </div>
    </div>
  )
}
