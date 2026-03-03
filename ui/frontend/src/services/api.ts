import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io'

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

export interface Agent {
  agent_id: string
  agent_name: string
  description: string
  capabilities: string[]
  status: string
  tools: string[]
  metadata: Record<string, any>
}

export interface ChatMessage {
  role: string
  content: string
  timestamp?: string
}

export interface ChatRequest {
  message: string
  context?: Record<string, any>
  stream?: boolean
  temperature?: number
}

export interface ChatResponse {
  response_id: string
  content: string
  agent_id: string
  agent_name: string
  status: string
  tools_used: string[]
  metadata: Record<string, any>
  timestamp: string
}

export interface OrchestrationRequest {
  message: string
  initial_agent_id: string
  context?: Record<string, any>
  strategy?: string
  max_iterations?: number
}

export interface OrchestrationResponse {
  responses: ChatResponse[]
  conversation_id: string
  total_agents: number
  completed: boolean
}

// Agent API
export const agentService = {
  async listAgents(): Promise<Agent[]> {
    const response = await apiClient.get<Agent[]>('/agents/')
    return response.data
  },

  async getAgent(agentId: string): Promise<Agent> {
    const response = await apiClient.get<Agent>(`/agents/${agentId}`)
    return response.data
  },

  async chatWithAgent(agentId: string, request: ChatRequest): Promise<ChatResponse> {
    const response = await apiClient.post<ChatResponse>(`/agents/${agentId}/chat`, request)
    return response.data
  },

  async getAgentHistory(agentId: string): Promise<ChatMessage[]> {
    const response = await apiClient.get(`/agents/${agentId}/history`)
    return response.data.messages
  },

  async resetAgent(agentId: string): Promise<void> {
    await apiClient.post(`/agents/${agentId}/reset`)
  },
}

// Orchestration API
export const orchestrationService = {
  async orchestrate(request: OrchestrationRequest): Promise<OrchestrationResponse> {
    const response = await apiClient.post<OrchestrationResponse>('/orchestrate/', request)
    return response.data
  },

  async orchestrateParallel(agentIds: string[], message: string): Promise<OrchestrationResponse> {
    const response = await apiClient.post<OrchestrationResponse>('/orchestrate/parallel', {
      agent_ids: agentIds,
      message,
    })
    return response.data
  },

  async getOrchestrationHistory(): Promise<ChatMessage[]> {
    const response = await apiClient.get('/orchestrate/history')
    return response.data.messages
  },

  async clearOrchestrationHistory(): Promise<void> {
    await apiClient.post('/orchestrate/history/clear')
  },
}

// Health check
export const healthService = {
  async checkHealth(): Promise<any> {
    const response = await apiClient.get('/health')
    return response.data
  },
}

export default apiClient
