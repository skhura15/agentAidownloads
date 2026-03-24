import { useState } from 'react'
import { CheckpointStatus } from '../../services/simulationApi'

interface ObjectivesSidebarProps {
  checkpoints: CheckpointStatus[]
  stats: {
    turn_count: number
    checkpoints_completed: number
    total_checkpoints: number
    hints_received: number
    is_active: boolean
  }
}

export default function ObjectivesSidebar({
  checkpoints,
  stats,
}: ObjectivesSidebarProps) {
  const [showOnlyAchieved, setShowOnlyAchieved] = useState(false)
  const completionPercentage = stats.total_checkpoints > 0
    ? Math.round((stats.checkpoints_completed / stats.total_checkpoints) * 100)
    : 0

  return (
    <div className="w-80 bg-gray-50 dark:bg-gray-850 border-r border-gray-200 dark:border-gray-700 flex flex-col">
      {/* Header */}
      <div className="p-4 border-b border-gray-200 dark:border-gray-700 bg-white dark:bg-gray-800">
        <div className="mb-3">
          <h2 className="font-semibold text-gray-900 dark:text-white mb-2">
            Progress
          </h2>
          <div className="flex justify-between text-xs text-gray-600 dark:text-gray-400 mb-2">
            <span>Checkpoints</span>
            <span>{stats.checkpoints_completed}/{stats.total_checkpoints}</span>
          </div>
          <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
            <div
              className="h-full bg-green-500 rounded-full transition-all duration-500"
              style={{ width: `${completionPercentage}%` }}
            />
          </div>
        </div>
        
        <div className="text-sm text-gray-600 dark:text-gray-400 mt-3 pt-3 border-t border-gray-200 dark:border-gray-700">
          <span className="font-medium">Turn:</span> {stats.turn_count}
        </div>
      </div>

      {/* Content - Scrollable */}
      <div className="flex-1 overflow-y-auto p-4">
        {/* Objectives Checklist */}
        <div>
          <div className="flex items-center justify-between mb-3">
            <h3 className="text-sm font-medium text-gray-700 dark:text-gray-300 flex items-center">
              <span className="mr-2">📋</span>
              Objectives
            </h3>
            <div className="flex items-center bg-gray-200 dark:bg-gray-700 rounded-full p-0.5 relative" style={{ width: '100px' }}>
              <button
                onClick={() => setShowOnlyAchieved(false)}
                className={`flex-1 py-1 px-2 text-xs font-medium rounded-full transition-all duration-200 text-center ${
                  !showOnlyAchieved
                    ? 'bg-blue-500 text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                }`}
              >
                All
              </button>
              <button
                onClick={() => setShowOnlyAchieved(true)}
                className={`flex-1 py-1 px-2 text-xs font-medium rounded-full transition-all duration-200 text-center ${
                  showOnlyAchieved
                    ? 'bg-green-500 text-white shadow-sm'
                    : 'text-gray-600 dark:text-gray-400 hover:text-gray-800 dark:hover:text-gray-200'
                }`}
              >
                Achieved
              </button>
            </div>
          </div>
          <div className="space-y-2">
            {checkpoints.length === 0 ? (
              <p className="text-xs text-gray-500 dark:text-gray-400 italic">
                Objectives will appear as you progress...
              </p>
            ) : (
              (showOnlyAchieved
                ? checkpoints.filter((cp) => cp.completed)
                : checkpoints
              ).map((cp) => (
                <div
                  key={cp.checkpoint_id}
                  className={`flex items-start space-x-2 text-sm ${
                    cp.completed
                      ? 'text-green-600 dark:text-green-400'
                      : 'text-gray-600 dark:text-gray-400'
                  }`}
                >
                  <span className="mt-0.5 flex-shrink-0">
                    {cp.completed ? (
                      <svg className="w-4 h-4" fill="currentColor" viewBox="0 0 20 20">
                        <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                      </svg>
                    ) : (
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <circle cx="12" cy="12" r="10" strokeWidth="2" />
                      </svg>
                    )}
                  </span>
                  <span className={cp.completed ? 'line-through' : ''}>
                    {cp.description}
                  </span>
                </div>
              ))
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
