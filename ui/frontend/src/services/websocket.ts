import { io, Socket } from 'socket.io-client'

const WS_BASE_URL = import.meta.env.VITE_WS_BASE_URL || 'ws://localhost:8000'

export interface WebSocketMessage {
  type: 'text' | 'status' | 'error' | 'complete' | 'agent_response'
  content: string
  metadata?: Record<string, any>
}

export class WebSocketService {
  private socket: Socket | null = null

  connect(endpoint: string): Socket {
    this.socket = io(`${WS_BASE_URL}${endpoint}`, {
      transports: ['websocket'],
    })

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
    })

    this.socket.on('disconnect', () => {
      console.log('WebSocket disconnected')
    })

    this.socket.on('error', (error) => {
      console.error('WebSocket error:', error)
    })

    return this.socket
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
  }

  send(data: any) {
    if (this.socket && this.socket.connected) {
      this.socket.emit('message', data)
    }
  }

  on(event: string, callback: (data: any) => void) {
    if (this.socket) {
      this.socket.on(event, callback)
    }
  }

  off(event: string, callback?: (data: any) => void) {
    if (this.socket) {
      this.socket.off(event, callback)
    }
  }
}

export const createAgentWebSocket = (agentId: string) => {
  const ws = new WebSocketService()
  ws.connect(`/ws/agent/${agentId}`)
  return ws
}

export const createOrchestrationWebSocket = () => {
  const ws = new WebSocketService()
  ws.connect('/ws/orchestrate')
  return ws
}
