import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { simulationService, CaseListItem } from '../../services/simulationApi'

// Difficulty badge colors
const difficultyColors = {
  beginner: 'bg-green-100 text-green-800 dark:bg-green-900 dark:text-green-200',
  intermediate: 'bg-amber-100 text-amber-800 dark:bg-amber-900 dark:text-amber-200',
  advanced: 'bg-blue-100 text-blue-900 dark:bg-blue-900 dark:text-blue-100',
}

// Skill icons (simple emoji for MVP)
const skillIcons: Record<string, string> = {
  'De-escalation': '🎯',
  'Problem Resolution': '🔧',
  'Technical Troubleshooting': '💻',
  'Empathy': '💚',
  'Policy Enforcement': '📋',
  'default': '📞',
}

interface ScenarioCardProps {
  scenario: CaseListItem
  onSelect: (caseId: string) => void
  isLoading: boolean
  onTagClick?: (tag: string) => void
}

function ScenarioCard({ scenario, onSelect, isLoading, onTagClick }: ScenarioCardProps) {
  const icon = skillIcons[scenario.primary_skill] || skillIcons.default

  return (
    <div className="bg-white dark:bg-gray-800 rounded-lg shadow-md hover:shadow-lg transition-shadow duration-200 overflow-hidden flex flex-col h-full">
      {/* Card Header */}
      <div className="p-6 flex-grow">
        <div className="flex items-start justify-between mb-3">
          <span className="text-3xl">{icon}</span>
          <div className="flex flex-col items-end gap-2">
            <span className={`px-2 py-1 rounded-full text-xs font-medium ${difficultyColors[scenario.difficulty]}`}>
              {scenario.difficulty.charAt(0).toUpperCase() + scenario.difficulty.slice(1)}
            </span>
            <div className="flex items-center text-sm text-gray-500 dark:text-gray-400">
              <svg className="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
              ~{scenario.estimated_time} min
            </div>
          </div>
        </div>
        
        <div className="min-h-24 mb-4">
          <h3 className="text-lg font-semibold text-gray-900 dark:text-white mb-2 line-clamp-2">
            {scenario.title}
          </h3>
          
          <p className="text-sm text-gray-600 dark:text-gray-400">
            Practice: <span className="font-medium">{scenario.primary_skill}</span>
          </p>
        </div>
        
        <div className="h-32 mb-6 overflow-hidden">
          <div className="p-3 bg-yellow-50 dark:bg-yellow-900/20 rounded border border-yellow-200 dark:border-yellow-800 h-full">
            <p className="text-xs text-gray-700 dark:text-gray-300 line-clamp-6">
              <span className="font-semibold">Overview:</span> {scenario.context || 'No context available'}
            </p>
          </div>
        </div>
        
        {/* Tags */}
        <div className="flex flex-wrap gap-2 mb-4">
          {scenario.tags.slice(0, 3).map((tag) => (
            <button
              key={tag}
              onClick={() => onTagClick?.(tag)}
              className="px-2 py-1 bg-purple-100 dark:bg-purple-900/30 text-purple-700 dark:text-purple-300 rounded text-xs hover:bg-purple-200 dark:hover:bg-purple-900/50 transition-colors duration-200 cursor-pointer"
            >
              {tag}
            </button>
          ))}
        </div>
      </div>
      
      {/* Card Footer */}
      <div className="px-6 py-4 bg-gray-50 dark:bg-gray-700/50">
        <button
          onClick={() => onSelect(scenario.case_id)}
          disabled={isLoading}
          className="w-full py-2 px-4 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-400 text-white font-medium rounded-lg transition-colors duration-200 flex items-center justify-center"
        >
          {isLoading ? (
            <>
              <svg className="animate-spin -ml-1 mr-2 h-4 w-4 text-white" fill="none" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
              </svg>
              Loading...
            </>
          ) : (
            <>
              Start Session
              <svg className="w-4 h-4 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </>
          )}
        </button>
      </div>
    </div>
  )
}

export default function ScenarioSelector() {
  const navigate = useNavigate()
  const [cases, setCases] = useState<CaseListItem[]>([])
  const [isLoading, setIsLoading] = useState(true)
  const [startingCase, setStartingCase] = useState<string | null>(null)
  const [error, setError] = useState<string | null>(null)
  const [selectedDifficulties, setSelectedDifficulties] = useState<Set<string>>(new Set())
  const [selectedTags, setSelectedTags] = useState<string[]>([])

  const handleDifficultyToggle = (difficulty: string) => {
    const newSet = new Set(selectedDifficulties)
    if (difficulty === 'all') {
      if (newSet.size === 0) {
        setSelectedDifficulties(new Set(['beginner', 'intermediate', 'advanced']))
      } else {
        setSelectedDifficulties(new Set())
      }
    } else {
      if (newSet.has(difficulty)) {
        newSet.delete(difficulty)
      } else {
        newSet.add(difficulty)
      }
      setSelectedDifficulties(newSet)
    }
  }

  const handleTagToggle = (tag: string) => {
    setSelectedTags((prev) =>
      prev.includes(tag)
        ? prev.filter((t) => t !== tag)
        : [...prev, tag]
    )
  }

  // Load available cases
  useEffect(() => {
    async function loadCases() {
      try {
        setIsLoading(true)
        const data = await simulationService.listCases()
        setCases(data)
      } catch (err) {
        setError('Failed to load training scenarios. Please try again.')
        console.error('Failed to load cases:', err)
      } finally {
        setIsLoading(false)
      }
    }
    loadCases()
  }, [])

  // Handle starting a simulation
  const handleStartSimulation = async (caseId: string) => {
    try {
      setStartingCase(caseId)
      const session = await simulationService.startSession({ case_id: caseId })
      navigate(`/in-flow-simulation/${session.session_id}`, { state: { session } })
    } catch (err) {
      setError('Failed to start simulation. Please try again.')
      console.error('Failed to start simulation:', err)
    } finally {
      setStartingCase(null)
    }
  }

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gray-50 dark:bg-gray-900 flex items-center justify-center">
        <div className="text-center">
          <svg className="animate-spin h-12 w-12 text-blue-600 mx-auto mb-4" fill="none" viewBox="0 0 24 24">
            <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
            <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
          </svg>
          <p className="text-gray-600 dark:text-gray-400">Loading training scenarios...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 dark:bg-gray-900">
      {/* Header */}
      <div className="bg-white dark:bg-gray-800 shadow-sm">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 dark:text-white">
                🎯 Skilling Agent Scenarios
              </h1>
              <p className="mt-2 text-gray-600 dark:text-gray-400">
                Practice handling real customer scenarios with AI coaching
              </p>
            </div>
            <button
              onClick={() => navigate('/')}
              className="text-gray-500 hover:text-gray-700 dark:text-gray-400 dark:hover:text-gray-200"
            >
              ← Back to Home
            </button>
          </div>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {error && (
          <div className="mb-6 p-4 bg-red-50 dark:bg-red-900/50 border border-red-200 dark:border-red-800 rounded-lg">
            <p className="text-red-700 dark:text-red-200">{error}</p>
          </div>
        )}

        {/* Info Banner */}
        <div className="mb-8 p-4 bg-blue-50 dark:bg-blue-900/30 border border-blue-200 dark:border-blue-800 rounded-lg">
          <div className="flex items-start">
            <span className="text-2xl mr-3">💡</span>
            <div>
              <h3 className="font-semibold text-blue-900 dark:text-blue-200">How it works</h3>
              <p className="text-sm text-blue-700 dark:text-blue-300 mt-1">
                Select a scenario to practice. You'll chat with a simulated customer while a 
                coach provides real-time guidance in a sidebar. Focus on building the skills 
                highlighted in each scenario.
              </p>
            </div>
          </div>
        </div>

        {/* Active Filters Display */}
        {selectedTags.length > 0 && (
          <div className="mb-8 p-4 bg-purple-50 dark:bg-purple-900/20 border border-purple-200 dark:border-purple-800 rounded-lg">
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-purple-900 dark:text-purple-200 mb-2">Active tag filters:</p>
                <div className="flex flex-wrap gap-2">
                  {selectedTags.map((tag) => (
                    <button
                      key={tag}
                      onClick={() => handleTagToggle(tag)}
                      className="inline-flex items-center gap-1 px-3 py-1 bg-purple-200 dark:bg-purple-800 text-purple-800 dark:text-purple-200 rounded-full text-sm hover:bg-purple-300 dark:hover:bg-purple-700 transition-colors duration-200"
                    >
                      {tag}
                      <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                      </svg>
                    </button>
                  ))}
                </div>
              </div>
              <button
                onClick={() => setSelectedTags([])}
                className="text-sm text-purple-600 dark:text-purple-400 hover:text-purple-700 dark:hover:text-purple-300 font-medium"
              >
                Clear all
              </button>
            </div>
          </div>
        )}

        {/* Difficulty Filter */}
        <div className="mb-8 flex flex-wrap gap-3 items-center">
          <span className="text-sm font-medium text-gray-700 dark:text-gray-300">Filter by difficulty:</span>
          <div className="flex flex-wrap gap-2">
            {['all', 'beginner', 'intermediate', 'advanced'].map((difficulty) => (
              <button
                key={difficulty}
                onClick={() => handleDifficultyToggle(difficulty)}
                className={`px-4 py-2 rounded-lg font-medium text-sm transition-colors duration-200 ${
                  difficulty === 'all'
                    ? selectedDifficulties.size === 0 || selectedDifficulties.size === 3
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                    : selectedDifficulties.has(difficulty)
                    ? 'bg-blue-600 text-white'
                    : 'bg-gray-200 dark:bg-gray-700 text-gray-700 dark:text-gray-300 hover:bg-gray-300 dark:hover:bg-gray-600'
                }`}
              >
                {difficulty === 'all' ? 'All' : difficulty.charAt(0).toUpperCase() + difficulty.slice(1)}
              </button>
            ))}
          </div>
        </div>

        {/* Scenario Grid */}
        {cases.length === 0 ? (
          <div className="text-center py-12">
            <span className="text-6xl mb-4 block">📭</span>
            <h3 className="text-xl font-semibold text-gray-900 dark:text-white mb-2">
              No scenarios available
            </h3>
            <p className="text-gray-600 dark:text-gray-400">
              Training scenarios will appear here once they're configured.
            </p>
          </div>
        ) : (
          <div>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {cases
                .filter((scenario) => {
                  // Show all difficulties if none selected
                  const difficultyMatch = selectedDifficulties.size === 0 || selectedDifficulties.has(scenario.difficulty)
                  // Show all tags if none selected, otherwise match any selected tag
                  const tagMatch = selectedTags.length === 0 || scenario.tags.some((tag) =>
                    selectedTags.some((selectedTag) => tag.toLowerCase().includes(selectedTag.toLowerCase()))
                  )
                  return difficultyMatch && tagMatch
                })
                .map((scenario) => (
                  <ScenarioCard
                    key={scenario.case_id}
                    scenario={scenario}
                    onSelect={handleStartSimulation}
                    isLoading={startingCase === scenario.case_id}
                    onTagClick={handleTagToggle}
                  />
                ))}
            </div>
          </div>
        )}
      </div>
    </div>
  )
}
