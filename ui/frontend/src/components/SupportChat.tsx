/**
 * Support Chat Component for Landing Page
 * Real-time chat interface for Self-Service Support Agent
 */

import React, { useState, useRef, useEffect } from 'react';
import { Send, Bot, User, X, MessageCircle, Loader } from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import { theme } from '../styles/theme';

interface Message {
  id: string;
  type: 'user' | 'agent';
  content: string;
  timestamp: Date;
  sentiment?: { sentiment: string; score: number };
  metadata?: any;
}

export const SupportChat: React.FC = () => {
  const [isOpen, setIsOpen] = useState(false);
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'agent',
      content: '👋 Hi! I\'m your AI support agent. How can I help you today?',
      timestamp: new Date()
    }
  ]);
  const [input, setInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [apiStatus, setApiStatus] = useState<'online' | 'offline' | 'checking'>('checking');
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Check API health on mount
  useEffect(() => {
    checkApiHealth();
  }, []);

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io';

  const checkApiHealth = async () => {
    try {
      const response = await fetch(`${API_BASE_URL}/health`);
      if (response.ok) {
        setApiStatus('online');
      } else {
        setApiStatus('offline');
      }
    } catch (error) {
      setApiStatus('offline');
    }
  };

  const handleSend = async () => {
    if (!input.trim() || isLoading) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setInput('');
    setIsLoading(true);

    try {
      const response = await fetch(`${API_BASE_URL}/api/support/query`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ query: input })
      });

      if (!response.ok) throw new Error('API request failed');

      const data = await response.json();

      const agentMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: data.response,
        timestamp: new Date(),
        sentiment: data.sentiment,
        metadata: {
          kb_articles_found: data.kb_articles_found,
          needs_escalation: data.needs_escalation,
          resolution_time: data.resolution_time_seconds
        }
      };

      setMessages(prev => [...prev, agentMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'agent',
        content: `❌ Sorry, I couldn't process your request. Please make sure the API server is running on ${API_BASE_URL}`,
        timestamp: new Date()
      };
      setMessages(prev => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  if (!isOpen) {
    return (
      <button
        onClick={() => setIsOpen(true)}
        style={{
          position: 'fixed',
          bottom: '2rem',
          right: '2rem',
          width: '60px',
          height: '60px',
          borderRadius: '50%',
          backgroundColor: theme.colors.primary,
          color: theme.colors.white,
          border: 'none',
          boxShadow: '0 4px 12px rgba(0, 0, 0, 0.15)',
          cursor: 'pointer',
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          transition: 'all 0.3s',
          zIndex: 1000
        }}
        onMouseOver={(e) => {
          e.currentTarget.style.transform = 'scale(1.1)';
          e.currentTarget.style.boxShadow = '0 6px 16px rgba(0, 0, 0, 0.2)';
        }}
        onMouseOut={(e) => {
          e.currentTarget.style.transform = 'scale(1)';
          e.currentTarget.style.boxShadow = '0 4px 12px rgba(0, 0, 0, 0.15)';
        }}
      >
        <MessageCircle size={28} />
      </button>
    );
  }

  return (
    <div
      style={{
        position: 'fixed',
        bottom: '2rem',
        right: '2rem',
        width: '400px',
        height: '600px',
        backgroundColor: theme.colors.white,
        borderRadius: '12px',
        boxShadow: '0 8px 32px rgba(0, 0, 0, 0.15)',
        display: 'flex',
        flexDirection: 'column',
        zIndex: 1000,
        overflow: 'hidden'
      }}
    >
      {/* Header */}
      <div
        style={{
          padding: '1.5rem',
          background: theme.colors.gradientPrimary,
          color: theme.colors.white,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between'
        }}
      >
        <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <Bot size={24} />
          <div>
            <h3 style={{ margin: 0, fontSize: '1.1rem', fontWeight: 600 }}>
              AI Support Agent
            </h3>
            <p style={{ margin: 0, fontSize: '0.85rem', opacity: 0.9 }}>
              {apiStatus === 'online' ? '🟢 Online' : '🔴 Offline'}
            </p>
          </div>
        </div>
        <button
          onClick={() => setIsOpen(false)}
          style={{
            background: 'none',
            border: 'none',
            color: theme.colors.white,
            cursor: 'pointer',
            padding: '0.5rem'
          }}
        >
          <X size={24} />
        </button>
      </div>

      {/* Messages */}
      <div
        style={{
          flex: 1,
          padding: '1.5rem',
          overflowY: 'auto',
          backgroundColor: '#f8f9fa'
        }}
      >
        {messages.map((message) => (
          <div
            key={message.id}
            style={{
              marginBottom: '1rem',
              display: 'flex',
              flexDirection: message.type === 'user' ? 'row-reverse' : 'row',
              gap: '0.75rem'
            }}
          >
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: '50%',
                backgroundColor: message.type === 'user' ? theme.colors.secondary : theme.colors.primary,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0
              }}
            >
              {message.type === 'user' ? <User size={18} color={theme.colors.white} /> : <Bot size={18} color={theme.colors.white} />}
            </div>
            <div
              style={{
                maxWidth: '75%',
                padding: '0.75rem 1rem',
                borderRadius: '12px',
                backgroundColor: message.type === 'user' ? theme.colors.secondary : theme.colors.white,
                color: message.type === 'user' ? theme.colors.white : theme.colors.dark,
                boxShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
                wordBreak: 'break-word'
              }}
            >
              <div style={{ margin: 0, fontSize: '0.95rem', lineHeight: 1.5 }}>
                {message.type === 'user' ? (
                  message.content
                ) : (
                  <ReactMarkdown
                    components={{
                      p: ({ children }) => <p style={{ margin: '0 0 0.5rem 0' }}>{children}</p>,
                      ul: ({ children }) => <ul style={{ margin: '0.5rem 0', paddingLeft: '1.25rem' }}>{children}</ul>,
                      ol: ({ children }) => <ol style={{ margin: '0.5rem 0', paddingLeft: '1.25rem' }}>{children}</ol>,
                      li: ({ children }) => <li style={{ marginBottom: '0.25rem' }}>{children}</li>,
                      strong: ({ children }) => <strong style={{ fontWeight: 600 }}>{children}</strong>,
                      h1: ({ children }) => <h1 style={{ fontSize: '1.25rem', fontWeight: 600, margin: '0.75rem 0 0.5rem' }}>{children}</h1>,
                      h2: ({ children }) => <h2 style={{ fontSize: '1.1rem', fontWeight: 600, margin: '0.75rem 0 0.5rem' }}>{children}</h2>,
                      h3: ({ children }) => <h3 style={{ fontSize: '1rem', fontWeight: 600, margin: '0.5rem 0 0.25rem' }}>{children}</h3>,
                      code: ({ children }) => <code style={{ backgroundColor: 'rgba(0,0,0,0.1)', padding: '0.125rem 0.25rem', borderRadius: '4px', fontSize: '0.9em' }}>{children}</code>,
                    }}
                  >
                    {message.content}
                  </ReactMarkdown>
                )}
              </div>
              {message.metadata && (
                <div style={{ marginTop: '0.5rem', fontSize: '0.75rem', opacity: 0.7 }}>
                  {message.metadata.needs_escalation && '⚠️ Escalated | '}
                  {message.metadata.resolution_time && `${message.metadata.resolution_time.toFixed(1)}s`}
                </div>
              )}
            </div>
          </div>
        ))}
        {isLoading && (
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.75rem', color: theme.colors.gray }}>
            <Loader size={18} className="animate-spin" />
            <span>Agent is thinking...</span>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>

      {/* Input */}
      <div
        style={{
          padding: '1rem',
          borderTop: `1px solid ${theme.colors.light}`,
          display: 'flex',
          gap: '0.75rem',
          backgroundColor: theme.colors.white
        }}
      >
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={handleKeyPress}
          placeholder="Type your question..."
          disabled={isLoading || apiStatus === 'offline'}
          style={{
            flex: 1,
            padding: '0.75rem',
            border: `1px solid ${theme.colors.light}`,
            borderRadius: '8px',
            fontSize: '0.95rem',
            outline: 'none',
            fontFamily: theme.typography.fontBody
          }}
        />
        <button
          onClick={handleSend}
          disabled={!input.trim() || isLoading || apiStatus === 'offline'}
          style={{
            padding: '0.75rem 1.25rem',
            backgroundColor: theme.colors.primary,
            color: theme.colors.white,
            border: 'none',
            borderRadius: '8px',
            cursor: isLoading || apiStatus === 'offline' ? 'not-allowed' : 'pointer',
            opacity: isLoading || apiStatus === 'offline' ? 0.5 : 1,
            transition: 'all 0.2s'
          }}
        >
          <Send size={20} />
        </button>
      </div>
    </div>
  );
};
