import { useQuery } from '@tanstack/react-query'
import { Link } from 'react-router-dom'
import { Bot, ArrowRight } from 'lucide-react'
import { agentService } from '../services/api'

export default function AgentList() {
  const { data: agents, isLoading } = useQuery({
    queryKey: ['agents'],
    queryFn: agentService.listAgents,
  })

  if (isLoading) {
    return <div className="text-center py-12">Loading agents...</div>
  }

  return (
    <div className="animate-fade-in">
      <h2 className="text-3xl font-bold mb-6">Available Agents</h2>
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {agents?.map((agent) => (
          <div key={agent.agent_id} className="card group">
            <div className="flex items-start justify-between mb-4">
              <div className="flex items-center space-x-3">
                <div className="p-2 bg-primary-100 dark:bg-primary-900 rounded-lg">
                  <Bot className="w-6 h-6 text-primary-500" />
                </div>
                <div>
                  <h3 className="text-lg font-semibold">{agent.agent_name}</h3>
                  <span className={`text-sm ${
                    agent.status === 'idle' ? 'text-green-500' : 'text-yellow-500'
                  }`}>
                    {agent.status}
                  </span>
                </div>
              </div>
            </div>
            
            <p className="text-gray-600 dark:text-gray-400 mb-4 text-sm">
              {agent.description}
            </p>
            
            <div className="mb-4">
              <p className="text-sm font-semibold mb-2">Capabilities:</p>
              <div className="flex flex-wrap gap-2">
                {agent.capabilities.slice(0, 3).map((cap, idx) => (
                  <span
                    key={idx}
                    className="px-2 py-1 bg-gray-100 dark:bg-gray-700 rounded text-xs"
                  >
                    {cap}
                  </span>
                ))}
              </div>
            </div>
            
            <Link
              to={`/chat/${agent.agent_id}`}
              className="flex items-center justify-between w-full btn-primary group-hover:shadow-lg transition-all"
            >
              <span>Chat with Agent</span>
              <ArrowRight className="w-4 h-4" />
            </Link>
          </div>
        ))}
      </div>
    </div>
  )
}
