import { useState } from 'react'
import { SessionReport, SkillScore, CheckpointDetail, ConversationTurnAnalysis, KeyMoment, WatchOutWarning } from '../../services/simulationApi'

interface SessionReportModalProps {
  report: SessionReport
  onClose: () => void
  onTryAgain: () => void
}

type TabType = 'overview' | 'skills' | 'conversation' | 'manager'

export default function SessionReportModal({
  report,
  onClose,
  onTryAgain,
}: SessionReportModalProps) {
  const [activeTab, setActiveTab] = useState<TabType>('overview')

  // Use the performance rating from the report, or calculate fallback
  const getPerformanceLevel = () => {
    if (report.performance_rating) {
      const rating = report.performance_rating.toLowerCase()
      if (rating.includes('excellent')) return { label: 'Excellent', color: 'text-green-600', bgColor: 'bg-green-500', emoji: '🌟' }
      if (rating.includes('good')) return { label: 'Good', color: 'text-blue-600', bgColor: 'bg-blue-500', emoji: '👍' }
      if (rating.includes('developing')) return { label: 'Developing', color: 'text-yellow-600', bgColor: 'bg-yellow-500', emoji: '📈' }
      return { label: 'Needs Improvement', color: 'text-orange-600', bgColor: 'bg-orange-500', emoji: '💪' }
    }
    // Fallback to completion percentage
    if (report.completion_percentage >= 80) return { label: 'Excellent', color: 'text-green-600', bgColor: 'bg-green-500', emoji: '🌟' }
    if (report.completion_percentage >= 60) return { label: 'Good', color: 'text-blue-600', bgColor: 'bg-blue-500', emoji: '👍' }
    if (report.completion_percentage >= 40) return { label: 'Developing', color: 'text-yellow-600', bgColor: 'bg-yellow-500', emoji: '📈' }
    return { label: 'Needs Improvement', color: 'text-orange-600', bgColor: 'bg-orange-500', emoji: '💪' }
  }

  const performance = getPerformanceLevel()

  const renderSkillBar = (score: number, maxScore: number = 5) => {
    const percentage = (score / maxScore) * 100
    let barColor = 'bg-red-500'
    if (percentage >= 80) barColor = 'bg-green-500'
    else if (percentage >= 60) barColor = 'bg-blue-500'
    else if (percentage >= 40) barColor = 'bg-yellow-500'
    
    return (
      <div className="h-2 bg-gray-200 dark:bg-gray-700 rounded-full overflow-hidden">
        <div className={`h-full ${barColor} rounded-full transition-all duration-500`} style={{ width: `${percentage}%` }} />
      </div>
    )
  }

  const renderTab = (tab: TabType, label: string, icon: string) => (
    <button
      onClick={() => setActiveTab(tab)}
      className={`flex-1 py-2 px-3 text-xs font-medium rounded-lg transition-colors ${
        activeTab === tab
          ? 'bg-blue-600 text-white'
          : 'bg-gray-100 dark:bg-gray-700 text-gray-600 dark:text-gray-300 hover:bg-gray-200 dark:hover:bg-gray-600'
      }`}
    >
      {icon} {label}
    </button>
  )

  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-white dark:bg-gray-800 rounded-2xl shadow-2xl max-w-3xl w-full max-h-[90vh] overflow-hidden flex flex-col">
        {/* Header with Overall Score */}
        <div className="bg-gradient-to-r from-blue-500 to-purple-500 p-6 text-white">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-xl font-bold">{report.case_title}</h2>
              <p className="text-blue-100 text-sm mt-1">
                {report.difficulty} • {report.primary_skill}
              </p>
            </div>
            <div className="text-center">
              <div className="text-4xl font-bold">{report.overall_score || Math.round(report.completion_percentage)}</div>
              <div className="text-blue-100 text-xs">Overall Score</div>
            </div>
          </div>
          <div className="flex items-center mt-4 gap-4">
            <span className="text-3xl">{performance.emoji}</span>
            <div>
              <span className="font-semibold">{performance.label}</span>
              <p className="text-blue-100 text-sm">{report.total_turns} turns • {report.duration_minutes.toFixed(1)} min</p>
            </div>
          </div>
        </div>

        {/* Tab Navigation */}
        <div className="flex gap-2 p-3 border-b border-gray-200 dark:border-gray-700">
          {renderTab('overview', 'Overview', '📊')}
          {renderTab('skills', 'Skills', '🎯')}
          {renderTab('conversation', 'Conversation', '💬')}
          {renderTab('manager', 'Manager View', '📋')}
        </div>

        {/* Tab Content */}
        <div className="flex-1 overflow-y-auto p-4">
          {activeTab === 'overview' && (
            <div className="space-y-4">
              {/* Quick Stats */}
              <div className="grid grid-cols-4 gap-3">
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{report.total_turns}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Turns</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{Math.round(report.completion_percentage)}%</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Complete</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{report.hints_received}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Hints</p>
                </div>
                <div className="bg-gray-50 dark:bg-gray-700 rounded-lg p-3 text-center">
                  <p className="text-2xl font-bold text-gray-900 dark:text-white">{report.checkpoints_completed}/{report.total_checkpoints}</p>
                  <p className="text-xs text-gray-500 dark:text-gray-400">Checkpoints</p>
                </div>
              </div>

              {/* Summary Feedback */}
              {report.summary_feedback && (
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <p className="text-gray-700 dark:text-gray-300 text-sm italic">"{report.summary_feedback}"</p>
                </div>
              )}

              {/* Checkpoint Details */}
              {report.checkpoint_details && report.checkpoint_details.length > 0 && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-3">Checkpoint Progress</h3>
                  <div className="space-y-2">
                    {report.checkpoint_details.map((cp: CheckpointDetail) => (
                      <div key={cp.checkpoint_id} className="flex items-center gap-2">
                        <span className={cp.completed ? 'text-green-500' : 'text-gray-400'}>{cp.completed ? '✓' : '○'}</span>
                        <span className={`text-sm ${cp.completed ? 'text-gray-700 dark:text-gray-300' : 'text-gray-500'}`}>{cp.description}</span>
                        {cp.importance === 'critical' && <span className="text-xs bg-red-100 dark:bg-red-900/30 text-red-600 px-1.5 py-0.5 rounded">Critical</span>}
                        {cp.completed_at_turn && <span className="text-xs text-gray-400 ml-auto">Turn {cp.completed_at_turn}</span>}
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Strengths & Opportunities */}
              <div className="grid grid-cols-2 gap-4">
                {report.strengths.length > 0 && (
                  <div className="bg-green-50 dark:bg-green-900/20 rounded-lg p-4">
                    <h3 className="font-medium text-green-700 dark:text-green-400 mb-2 flex items-center gap-2">
                      <span>✓</span> Strengths
                    </h3>
                    <ul className="space-y-1">
                      {report.strengths.map((s: string, i: number) => (
                        <li key={i} className="text-sm text-gray-600 dark:text-gray-400">• {s}</li>
                      ))}
                    </ul>
                  </div>
                )}
                {report.opportunities.length > 0 && (
                  <div className="bg-yellow-50 dark:bg-yellow-900/20 rounded-lg p-4">
                    <h3 className="font-medium text-yellow-700 dark:text-yellow-400 mb-2 flex items-center gap-2">
                      <span>📈</span> Opportunities
                    </h3>
                    <ul className="space-y-1">
                      {report.opportunities.map((o: string, i: number) => (
                        <li key={i} className="text-sm text-gray-600 dark:text-gray-400">• {o}</li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>

              {/* Key Moments */}
              {report.key_moments && report.key_moments.length > 0 && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-3">Key Moments</h3>
                  <div className="space-y-2">
                    {report.key_moments.map((moment: KeyMoment, i: number) => (
                      <div key={i} className={`flex items-start gap-2 p-2 rounded ${
                        moment.type === 'positive' ? 'bg-green-100 dark:bg-green-900/30' :
                        moment.type === 'negative' ? 'bg-red-100 dark:bg-red-900/30' :
                        'bg-yellow-100 dark:bg-yellow-900/30'
                      }`}>
                        <span>{moment.type === 'positive' ? '👍' : moment.type === 'negative' ? '⚠️' : '💡'}</span>
                        <div>
                          <span className="text-xs text-gray-500">Turn {moment.turn}</span>
                          <p className="text-sm text-gray-700 dark:text-gray-300">{moment.description}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          )}

          {activeTab === 'skills' && (
            <div className="space-y-4">
              {report.skill_scores && report.skill_scores.length > 0 ? (
                report.skill_scores.map((skill: SkillScore, i: number) => (
                  <div key={i} className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <h4 className="font-medium text-gray-900 dark:text-white">{skill.skill_name}</h4>
                      <span className="text-sm font-bold">{skill.score}/{skill.max_score}</span>
                    </div>
                    {renderSkillBar(skill.score, skill.max_score)}
                    {skill.evidence && skill.evidence.length > 0 && (
                      <div className="mt-3">
                        <p className="text-xs text-gray-500 dark:text-gray-400 mb-1">Evidence:</p>
                        <ul className="text-sm text-gray-600 dark:text-gray-400 space-y-1">
                          {skill.evidence.map((e: string, j: number) => (
                            <li key={j} className="italic">"{e}"</li>
                          ))}
                        </ul>
                      </div>
                    )}
                    {skill.recommendation && (
                      <div className="mt-2 p-2 bg-blue-50 dark:bg-blue-900/20 rounded">
                        <p className="text-xs text-blue-700 dark:text-blue-300">💡 {skill.recommendation}</p>
                      </div>
                    )}
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  Skill analysis not available for this session.
                </div>
              )}
            </div>
          )}

          {activeTab === 'conversation' && (
            <div className="space-y-3">
              {report.conversation_analysis && report.conversation_analysis.length > 0 ? (
                report.conversation_analysis.map((turn: ConversationTurnAnalysis) => (
                  <div key={turn.turn_number} className="border border-gray-200 dark:border-gray-700 rounded-lg overflow-hidden">
                    <div className="bg-gray-50 dark:bg-gray-700 px-3 py-1.5 flex items-center justify-between">
                      <span className="text-xs font-medium text-gray-600 dark:text-gray-400">Turn {turn.turn_number}</span>
                      {turn.intervention_type && (
                        <span className={`text-xs px-2 py-0.5 rounded ${
                          turn.intervention_type === 'PRAISE' ? 'bg-green-100 text-green-700' :
                          turn.intervention_type === 'HINT' ? 'bg-blue-100 text-blue-700' :
                          turn.intervention_type === 'WARNING' ? 'bg-red-100 text-red-700' :
                          'bg-purple-100 text-purple-700'
                        }`}>
                          {turn.intervention_type}
                        </span>
                      )}
                    </div>
                    <div className="p-3 space-y-2">
                      <div>
                        <p className="text-xs text-blue-600 dark:text-blue-400 font-medium">Trainee:</p>
                        <p className="text-sm text-gray-700 dark:text-gray-300">{turn.trainee_message}</p>
                      </div>
                      {turn.customer_response && (
                        <div>
                          <p className="text-xs text-gray-500 font-medium">Customer:</p>
                          <p className="text-sm text-gray-600 dark:text-gray-400">{turn.customer_response}</p>
                        </div>
                      )}
                      {turn.coach_intervention && (
                        <div className="bg-yellow-50 dark:bg-yellow-900/20 p-2 rounded">
                          <p className="text-xs text-yellow-700 dark:text-yellow-400">🎯 Coach: {turn.coach_intervention}</p>
                        </div>
                      )}
                    </div>
                  </div>
                ))
              ) : report.transcript && report.transcript.length > 0 ? (
                // Fallback to raw transcript
                report.transcript.map((msg: { role: string; content: string; timestamp: string }, i: number) => (
                  <div key={i} className={`p-3 rounded-lg ${
                    msg.role === 'user' ? 'bg-blue-50 dark:bg-blue-900/20 ml-8' :
                    msg.role === 'customer' ? 'bg-gray-50 dark:bg-gray-700/50 mr-8' :
                    msg.role === 'coach' ? 'bg-yellow-50 dark:bg-yellow-900/20' :
                    'bg-gray-100 dark:bg-gray-600'
                  }`}>
                    <p className="text-xs text-gray-500 mb-1 capitalize">{msg.role === 'user' ? 'Trainee' : msg.role}</p>
                    <p className="text-sm text-gray-700 dark:text-gray-300">{msg.content}</p>
                  </div>
                ))
              ) : (
                <div className="text-center text-gray-500 dark:text-gray-400 py-8">
                  Conversation analysis not available.
                </div>
              )}
            </div>
          )}

          {activeTab === 'manager' && (
            <div className="space-y-4">
              {/* Manager Summary */}
              {report.manager_notes && (
                <div className="bg-purple-50 dark:bg-purple-900/20 rounded-lg p-4">
                  <h3 className="font-medium text-purple-700 dark:text-purple-400 mb-2">📋 Manager Notes</h3>
                  <p className="text-sm text-gray-700 dark:text-gray-300">{report.manager_notes}</p>
                </div>
              )}

              {/* Watch Out Warnings */}
              {report.watch_out_warnings && report.watch_out_warnings.length > 0 && (
                <div className="bg-red-50 dark:bg-red-900/20 rounded-lg p-4 border-l-4 border-red-500">
                  <h3 className="font-medium text-red-700 dark:text-red-400 mb-3 flex items-center gap-2">
                    <span>⚠️</span> Watch Out Warnings
                  </h3>
                  <div className="space-y-3">
                    {report.watch_out_warnings.map((warning: WatchOutWarning, i: number) => (
                      <div key={i} className="bg-white dark:bg-gray-800 rounded-lg p-3 border border-red-200 dark:border-red-800">
                        <div className="flex items-center justify-between mb-2">
                          <span className="font-medium text-gray-900 dark:text-white text-sm">{warning.category}</span>
                          <div className="flex gap-2">
                            <span className={`text-xs px-2 py-0.5 rounded ${
                              warning.severity === 'high' ? 'bg-red-100 text-red-700 dark:bg-red-900/50 dark:text-red-400' :
                              warning.severity === 'medium' ? 'bg-yellow-100 text-yellow-700 dark:bg-yellow-900/50 dark:text-yellow-400' :
                              'bg-gray-100 text-gray-700 dark:bg-gray-700 dark:text-gray-400'
                            }`}>
                              {warning.severity}
                            </span>
                            <span className="text-xs px-2 py-0.5 rounded bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-400">
                              {warning.frequency === 'pattern' ? '🔄 Pattern' : 
                               warning.frequency === 'multiple_times' ? '📊 Multiple' : '1x'}
                            </span>
                          </div>
                        </div>
                        <p className="text-sm text-gray-700 dark:text-gray-300 mb-2">{warning.behavior}</p>
                        {warning.example_quote && (
                          <div className="bg-gray-50 dark:bg-gray-700/50 rounded p-2 mb-2">
                            <p className="text-xs text-gray-500 dark:text-gray-400">
                              {warning.example_turn && <span className="font-medium">Turn {warning.example_turn}: </span>}
                              <span className="italic">"{warning.example_quote}"</span>
                            </p>
                          </div>
                        )}
                        <div className="flex items-start gap-2 text-sm">
                          <span className="text-blue-500">💡</span>
                          <p className="text-blue-700 dark:text-blue-400">{warning.coaching_suggestion}</p>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Coaching Intervention Summary */}
              {report.coaching_summary && (
                <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                  <h3 className="font-medium text-gray-900 dark:text-white mb-3">Coaching Interventions</h3>
                  <div className="grid grid-cols-3 gap-3 mb-3">
                    <div className="text-center p-2 bg-blue-100 dark:bg-blue-900/30 rounded">
                      <p className="text-xl font-bold text-blue-700 dark:text-blue-400">{report.coaching_summary.total_hints}</p>
                      <p className="text-xs text-blue-600">Hints</p>
                    </div>
                    <div className="text-center p-2 bg-red-100 dark:bg-red-900/30 rounded">
                      <p className="text-xl font-bold text-red-700 dark:text-red-400">{report.coaching_summary.total_warnings}</p>
                      <p className="text-xs text-red-600">Warnings</p>
                    </div>
                    <div className="text-center p-2 bg-green-100 dark:bg-green-900/30 rounded">
                      <p className="text-xl font-bold text-green-700 dark:text-green-400">{report.coaching_summary.total_praise}</p>
                      <p className="text-xs text-green-600">Praise</p>
                    </div>
                  </div>
                  {report.coaching_summary.interventions && report.coaching_summary.interventions.length > 0 && (
                    <div className="space-y-1 max-h-40 overflow-y-auto">
                      {report.coaching_summary.interventions.map((int: { turn: number; type: string; content: string }, i: number) => (
                        <div key={i} className="text-xs flex items-start gap-2">
                          <span className="text-gray-400">T{int.turn}</span>
                          <span className={`font-medium ${
                            int.type === 'PRAISE' ? 'text-green-600' :
                            int.type === 'HINT' ? 'text-blue-600' :
                            'text-red-600'
                          }`}>[{int.type}]</span>
                          <span className="text-gray-600 dark:text-gray-400">{int.content}</span>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              )}

              {/* Recommended Training */}
              {report.recommended_training && report.recommended_training.length > 0 && (
                <div className="bg-blue-50 dark:bg-blue-900/20 rounded-lg p-4">
                  <h3 className="font-medium text-blue-700 dark:text-blue-400 mb-2">📚 Recommended Training</h3>
                  <ul className="space-y-1">
                    {report.recommended_training.map((t: string, i: number) => (
                      <li key={i} className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
                        <span className="text-blue-500">→</span> {t}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Follow-up Actions */}
              {report.follow_up_actions && report.follow_up_actions.length > 0 && (
                <div className="bg-orange-50 dark:bg-orange-900/20 rounded-lg p-4">
                  <h3 className="font-medium text-orange-700 dark:text-orange-400 mb-2">✅ Follow-up Actions</h3>
                  <ul className="space-y-1">
                    {report.follow_up_actions.map((a: string, i: number) => (
                      <li key={i} className="text-sm text-gray-700 dark:text-gray-300 flex items-center gap-2">
                        <input type="checkbox" className="rounded" /> {a}
                      </li>
                    ))}
                  </ul>
                </div>
              )}

              {/* Session Metadata */}
              <div className="bg-gray-50 dark:bg-gray-700/50 rounded-lg p-4">
                <h3 className="font-medium text-gray-900 dark:text-white mb-2">Session Details</h3>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div><span className="text-gray-500">Session ID:</span> <span className="text-gray-700 dark:text-gray-300 font-mono text-xs">{report.session_id}</span></div>
                  <div><span className="text-gray-500">Case ID:</span> <span className="text-gray-700 dark:text-gray-300">{report.case_id || 'N/A'}</span></div>
                  <div><span className="text-gray-500">Trainee:</span> <span className="text-gray-700 dark:text-gray-300">{report.trainee_id || 'Anonymous'}</span></div>
                  <div><span className="text-gray-500">Duration:</span> <span className="text-gray-700 dark:text-gray-300">{report.duration_minutes?.toFixed(1) || '0'} minutes</span></div>
                  <div><span className="text-gray-500">Started:</span> <span className="text-gray-700 dark:text-gray-300">{report.started_at ? new Date(report.started_at).toLocaleString() : 'N/A'}</span></div>
                  <div><span className="text-gray-500">Ended:</span> <span className="text-gray-700 dark:text-gray-300">{report.ended_at ? new Date(report.ended_at).toLocaleString() : 'N/A'}</span></div>
                </div>
              </div>
            </div>
          )}
        </div>

        {/* Actions */}
        <div className="p-4 border-t border-gray-200 dark:border-gray-700 flex space-x-3">
          <button
            onClick={onTryAgain}
            className="flex-1 py-3 px-4 bg-blue-600 hover:bg-blue-700 text-white font-medium rounded-lg transition-colors"
          >
            Practice Again
          </button>
          <button
            onClick={onClose}
            className="flex-1 py-3 px-4 bg-gray-100 hover:bg-gray-200 dark:bg-gray-700 dark:hover:bg-gray-600 text-gray-700 dark:text-gray-300 font-medium rounded-lg transition-colors"
          >
            Back to Menu
          </button>
        </div>
      </div>
    </div>
  )
}
