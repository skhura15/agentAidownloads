import { useState } from 'react'
import { useParams } from 'react-router-dom'
import { Send } from 'lucide-react'

export default function AgentChat() {
  const { agentId } = useParams()
  const [message, setMessage] = useState('')
  const [messages, setMessages] = useState<any[]>([])
  
  // Use agentId in console log to avoid unused warning
  console.log('Agent ID:', agentId)

  const handleSend = () => {
    if (!message.trim()) return
    // Implementation would call the API
    setMessages([...messages, { text: message, sender: 'user' }])
    setMessage('')
  }

  return (
    <div className="animate-fade-in max-w-4xl mx-auto">
      <h2 className="text-3xl font-bold mb-6">Chat with Agent</h2>
      
      <div className="card h-[600px] flex flex-col">
        <div className="flex-1 overflow-y-auto mb-4 space-y-4">
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`p-4 rounded-lg ${
                msg.role === 'user'
                  ? 'bg-primary-100 dark:bg-primary-900 ml-auto max-w-[80%]'
                  : 'bg-gray-100 dark:bg-gray-700 mr-auto max-w-[80%]'
              }`}
            >
              {msg.content}
            </div>
          ))}
        </div>
        
        <div className="flex space-x-2">
          <input
            type="text"
            value={message}
            onChange={(e) => setMessage(e.target.value)}
            onKeyPress={(e) => e.key === 'Enter' && handleSend()}
            placeholder="Type your message..."
            className="flex-1 input"
          />
          <button onClick={handleSend} className="btn-primary">
            <Send className="w-5 h-5" />
          </button>
        </div>
      </div>
    </div>
  )
}
