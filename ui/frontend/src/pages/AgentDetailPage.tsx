/**
 * Agent Detail Page
 * 
 * Displays detailed information about a specific AI agent and provides
 * an interactive chat interface for testing the agent's capabilities.
 */

import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import {
  ArrowLeft,
  Send,
  Sparkles,
  CheckCircle,
  Clock,
  Star,
  Users,
  Code,
  ChevronRight,
  Play,
} from 'lucide-react';
import ReactMarkdown from 'react-markdown';
import Header from '../components/Header';
// @ts-ignore - Module exists but TypeScript can't resolve it
import { getAgentById, Agent } from '../data/agents';
import { theme } from '../styles/theme';

interface Message {
  id: string;
  role: 'user' | 'agent';
  content: string;
  timestamp: Date;
}

const AgentDetailPage: React.FC = () => {
  const { agentId } = useParams<{ agentId: string }>();
  const navigate = useNavigate();
  const [agent, setAgent] = useState<Agent | null>(null);
  const [messages, setMessages] = useState<Message[]>([]);
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    if (agentId) {
      const foundAgent = getAgentById(agentId);
      setAgent(foundAgent || null);
      
      // Initial greeting message
      if (foundAgent) {
        setMessages([
          {
            id: '1',
            role: 'agent',
            content: `Hello! I'm the ${foundAgent.name}. ${foundAgent.description} How can I assist you today?`,
            timestamp: new Date(),
          },
        ]);
      }
    }
  }, [agentId]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const handleSendMessage = async () => {
    if (!inputValue.trim() || !agent) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: inputValue,
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    const query = inputValue;
    setInputValue('');
    setIsLoading(true);

    const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'https://azca2a6z7bdznymc2.blackbeach-53f09f44.eastus.azurecontainerapps.io';

    // For agents with real backend, call the API
    if (agent.id === 'self-service-support' || agent.id === 'uta-troubleshooting') {
      try {
        const response = await fetch(`${API_BASE_URL}/agents/${agent.id}/chat`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ message: query, context: {} })
        });

        if (!response.ok) throw new Error('API request failed');

        const data = await response.json();

        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'agent',
          content: data.content || data.response,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, agentMessage]);
      } catch (error) {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'agent',
          content: `❌ Sorry, I couldn't process your request. Please make sure the API server is running on ${API_BASE_URL}`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, errorMessage]);
      } finally {
        setIsLoading(false);
      }
    } else {
      // Simulate agent response for other agents
      setTimeout(() => {
        const agentMessage: Message = {
          id: (Date.now() + 1).toString(),
          role: 'agent',
          content: `I understand you'd like to know about "${query}". As the ${agent.name}, I can help you with that. This is a demo interface - in production, I would connect to the actual agent backend.`,
          timestamp: new Date(),
        };
        setMessages((prev) => [...prev, agentMessage]);
        setIsLoading(false);
      }, 1500);
    }
  };

  const handleKeyPress = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSendMessage();
    }
  };

  if (!agent) {
    return (
      <div style={{ minHeight: '100vh', backgroundColor: theme.colors.light }}>
        <Header />
        <div
          style={{
            display: 'flex',
            flexDirection: 'column',
            alignItems: 'center',
            justifyContent: 'center',
            minHeight: 'calc(100vh - 80px)',
            padding: '2rem',
          }}
        >
          <h2
            style={{
              fontFamily: theme.typography.fontHeading,
              fontSize: theme.typography.fontSize['3xl'],
              color: theme.colors.dark,
              marginBottom: '1rem',
            }}
          >
            Agent Not Found
          </h2>
          <p
            style={{
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.lg,
              color: theme.colors.darkLight,
              marginBottom: '2rem',
            }}
          >
            The agent you're looking for doesn't exist.
          </p>
          <button
            onClick={() => navigate('/')}
            style={{
              padding: '0.875rem 2rem',
              backgroundColor: theme.colors.primary,
              color: theme.colors.white,
              border: 'none',
              borderRadius: theme.borderRadius.md,
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.base,
              fontWeight: theme.typography.fontWeight.semibold,
              cursor: 'pointer',
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              transition: `all ${theme.transitions.base}`,
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.primaryDark;
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.primary;
            }}
          >
            <ArrowLeft size={18} />
            Back to Home
          </button>
        </div>
      </div>
    );
  }

  const statusColors = {
    live: theme.colors.success,
    beta: theme.colors.warning,
    'coming-soon': theme.colors.info,
  };

  return (
    <div style={{ minHeight: '100vh', backgroundColor: theme.colors.light }}>
      <Header />

      {/* Agent Header */}
      <section
        style={{
          backgroundColor: theme.colors.white,
          borderBottom: `1px solid ${theme.colors.gray}`,
          padding: '2rem 1.5rem',
        }}
      >
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <button
            onClick={() => navigate('/')}
            style={{
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
              backgroundColor: 'transparent',
              border: 'none',
              color: theme.colors.primary,
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.sm,
              fontWeight: theme.typography.fontWeight.medium,
              cursor: 'pointer',
              marginBottom: '1.5rem',
              padding: 0,
              transition: `color ${theme.transitions.fast}`,
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.color = theme.colors.primaryDark;
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.color = theme.colors.primary;
            }}
          >
            <ArrowLeft size={16} />
            Back to Agents
          </button>

          <div style={{ display: 'flex', alignItems: 'flex-start', gap: '1.5rem' }}>
            <div
              style={{
                width: '80px',
                height: '80px',
                backgroundColor: theme.colors.overlayLight,
                borderRadius: theme.borderRadius.xl,
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
                flexShrink: 0,
              }}
            >
              <Sparkles size={40} color={theme.colors.primary} strokeWidth={2} />
            </div>

            <div style={{ flex: 1 }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: '1rem', marginBottom: '0.5rem' }}>
                <h1
                  style={{
                    fontFamily: theme.typography.fontHeading,
                    fontSize: theme.typography.fontSize['3xl'],
                    fontWeight: theme.typography.fontWeight.bold,
                    color: theme.colors.dark,
                    margin: 0,
                  }}
                >
                  {agent.name}
                </h1>
                <span
                  style={{
                    display: 'inline-flex',
                    alignItems: 'center',
                    gap: '0.25rem',
                    padding: '0.25rem 0.75rem',
                    backgroundColor: statusColors[agent.status as keyof typeof statusColors],
                    color: theme.colors.white,
                    borderRadius: theme.borderRadius.full,
                    fontFamily: theme.typography.fontBody,
                    fontSize: theme.typography.fontSize.xs,
                    fontWeight: theme.typography.fontWeight.bold,
                    textTransform: 'uppercase',
                  }}
                >
                  {agent.status === 'live' && <CheckCircle size={12} />}
                  {agent.status === 'beta' && <Clock size={12} />}
                  {agent.status}
                </span>
              </div>

              <p
                style={{
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.lg,
                  color: theme.colors.darkLight,
                  marginBottom: '1rem',
                  lineHeight: theme.typography.lineHeight.relaxed,
                }}
              >
                {agent.description}
              </p>

              <div style={{ display: 'flex', gap: '2rem', flexWrap: 'wrap' }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Star size={16} color={theme.colors.warning} fill={theme.colors.warning} />
                  <span
                    style={{
                      fontFamily: theme.typography.fontBody,
                      fontSize: theme.typography.fontSize.sm,
                      color: theme.colors.dark,
                      fontWeight: theme.typography.fontWeight.semibold,
                    }}
                  >
                    {agent.popularity}/5
                  </span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
                  <Users size={16} color={theme.colors.darkLight} />
                  <span
                    style={{
                      fontFamily: theme.typography.fontBody,
                      fontSize: theme.typography.fontSize.sm,
                      color: theme.colors.darkLight,
                    }}
                  >
                    {agent.category}
                  </span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Main Content */}
      <div style={{ maxWidth: '1280px', margin: '0 auto', padding: '2rem 1.5rem' }}>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 400px', gap: '2rem' }}>

          {/* Training agents get a "Launch Simulator" CTA instead of chat */}
          {agent.category === 'training' ? (
            <div
              style={{
                backgroundColor: theme.colors.white,
                borderRadius: theme.borderRadius.xl,
                boxShadow: theme.shadows.lg,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                height: '600px',
                padding: '3rem',
                textAlign: 'center',
                gap: '1.5rem',
              }}
            >
              <div
                style={{
                  width: '96px',
                  height: '96px',
                  background: `linear-gradient(135deg, ${theme.colors.primary}, ${theme.colors.secondary || '#6366f1'})`,
                  borderRadius: '50%',
                  display: 'flex',
                  alignItems: 'center',
                  justifyContent: 'center',
                }}
              >
                <Play size={44} color={theme.colors.white} />
              </div>
              <h3
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize['2xl'],
                  fontWeight: theme.typography.fontWeight.bold,
                  color: theme.colors.dark,
                  margin: 0,
                }}
              >
                Launch Training Simulator
              </h3>
              <p
                style={{
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.base,
                  color: theme.colors.darkLight,
                  lineHeight: theme.typography.lineHeight.relaxed,
                  maxWidth: '400px',
                }}
              >
                Practice real customer scenarios with an AI-powered customer and real-time coaching. 
                Choose from 30+ training cases across de-escalation, billing, technical support, and more.
              </p>
              <button
                onClick={() => navigate('/in-flow-simulation')}
                style={{
                  display: 'inline-flex',
                  alignItems: 'center',
                  gap: '0.75rem',
                  padding: '1rem 2.5rem',
                  backgroundColor: theme.colors.primary,
                  color: theme.colors.white,
                  border: 'none',
                  borderRadius: theme.borderRadius.lg,
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.bold,
                  cursor: 'pointer',
                  transition: `all ${theme.transitions.base}`,
                  boxShadow: theme.shadows.md,
                }}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = theme.colors.primaryDark;
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = theme.shadows.lg;
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = theme.colors.primary;
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = theme.shadows.md;
                }}
              >
                <Play size={20} />
                Start Simulation
              </button>
              <p
                style={{
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.xs,
                  color: theme.colors.darkLight,
                  opacity: 0.7,
                }}
              >
                Avg. session: ~10 minutes • Detailed report after each session
              </p>
            </div>
          ) : (
          /* Chat Interface */
          <div
            style={{
              backgroundColor: theme.colors.white,
              borderRadius: theme.borderRadius.xl,
              boxShadow: theme.shadows.lg,
              display: 'flex',
              flexDirection: 'column',
              height: '600px',
              overflow: 'hidden',
            }}
          >
            {/* Chat Header */}
            <div
              style={{
                padding: '1.5rem',
                borderBottom: `1px solid ${theme.colors.gray}`,
                backgroundColor: theme.colors.light,
              }}
            >
              <h3
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                  color: theme.colors.dark,
                  margin: 0,
                }}
              >
                Try {agent.name}
              </h3>
            </div>

            {/* Messages */}
            <div
              style={{
                flex: 1,
                overflowY: 'auto',
                padding: '1.5rem',
                display: 'flex',
                flexDirection: 'column',
                gap: '1rem',
              }}
            >
              {messages.map((message) => (
                <div
                  key={message.id}
                  style={{
                    display: 'flex',
                    justifyContent: message.role === 'user' ? 'flex-end' : 'flex-start',
                  }}
                >
                  <div
                    style={{
                      maxWidth: '70%',
                      padding: '0.875rem 1.25rem',
                      borderRadius: theme.borderRadius.lg,
                      backgroundColor:
                        message.role === 'user' ? theme.colors.primary : theme.colors.light,
                      color: message.role === 'user' ? theme.colors.white : theme.colors.dark,
                      fontFamily: theme.typography.fontBody,
                      fontSize: theme.typography.fontSize.base,
                      lineHeight: theme.typography.lineHeight.relaxed,
                    }}
                    className="markdown-content"
                  >
                    {message.role === 'user' ? (
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
                </div>
              ))}
              {isLoading && (
                <div style={{ display: 'flex', justifyContent: 'flex-start' }}>
                  <div
                    style={{
                      padding: '0.875rem 1.25rem',
                      borderRadius: theme.borderRadius.lg,
                      backgroundColor: theme.colors.light,
                      fontFamily: theme.typography.fontBody,
                      fontSize: theme.typography.fontSize.base,
                      color: theme.colors.darkLight,
                    }}
                  >
                    Thinking...
                  </div>
                </div>
              )}
              <div ref={messagesEndRef} />
            </div>

            {/* Input */}
            <div
              style={{
                padding: '1.5rem',
                borderTop: `1px solid ${theme.colors.gray}`,
                backgroundColor: theme.colors.light,
              }}
            >
              <div style={{ display: 'flex', gap: '1rem' }}>
                <input
                  type="text"
                  value={inputValue}
                  onChange={(e) => setInputValue(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder={
                    agent.status === 'coming-soon'
                      ? 'Coming soon...'
                      : 'Type your message...'
                  }
                  disabled={agent.status === 'coming-soon'}
                  style={{
                    flex: 1,
                    padding: '0.875rem 1.25rem',
                    border: `1px solid ${theme.colors.gray}`,
                    borderRadius: theme.borderRadius.md,
                    fontFamily: theme.typography.fontBody,
                    fontSize: theme.typography.fontSize.base,
                    outline: 'none',
                    transition: `border-color ${theme.transitions.fast}`,
                  }}
                  onFocus={(e) => {
                    e.currentTarget.style.borderColor = theme.colors.primary;
                  }}
                  onBlur={(e) => {
                    e.currentTarget.style.borderColor = theme.colors.gray;
                  }}
                />
                <button
                  onClick={handleSendMessage}
                  disabled={!inputValue.trim() || agent.status === 'coming-soon'}
                  style={{
                    padding: '0.875rem 1.5rem',
                    backgroundColor:
                      !inputValue.trim() || agent.status === 'coming-soon'
                        ? theme.colors.gray
                        : theme.colors.primary,
                    color: theme.colors.white,
                    border: 'none',
                    borderRadius: theme.borderRadius.md,
                    cursor:
                      !inputValue.trim() || agent.status === 'coming-soon'
                        ? 'not-allowed'
                        : 'pointer',
                    display: 'flex',
                    alignItems: 'center',
                    gap: '0.5rem',
                    fontFamily: theme.typography.fontBody,
                    fontSize: theme.typography.fontSize.base,
                    fontWeight: theme.typography.fontWeight.semibold,
                    transition: `all ${theme.transitions.base}`,
                  }}
                  onMouseOver={(e) => {
                    if (inputValue.trim() && agent.status !== 'coming-soon') {
                      e.currentTarget.style.backgroundColor = theme.colors.primaryDark;
                    }
                  }}
                  onMouseOut={(e) => {
                    if (inputValue.trim() && agent.status !== 'coming-soon') {
                      e.currentTarget.style.backgroundColor = theme.colors.primary;
                    }
                  }}
                >
                  <Send size={18} />
                  Send
                </button>
              </div>
            </div>
          </div>
          )}

          {/* Sidebar - Agent Details */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            {/* Capabilities */}
            <div
              style={{
                backgroundColor: theme.colors.white,
                padding: '1.5rem',
                borderRadius: theme.borderRadius.xl,
                boxShadow: theme.shadows.md,
              }}
            >
              <h4
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                  color: theme.colors.dark,
                  marginBottom: '1rem',
                }}
              >
                Capabilities
              </h4>
              <div style={{ display: 'flex', flexWrap: 'wrap', gap: '0.5rem' }}>
                {agent.capabilities.map((cap: any, index: number) => (
                  <span
                    key={cap?.id || cap?.label || index}
                    style={{
                      padding: '0.5rem 1rem',
                      backgroundColor: cap?.color ? `${cap.color}15` : theme.colors.overlayLight,
                      color: cap?.color || theme.colors.primary,
                      borderRadius: theme.borderRadius.md,
                      fontFamily: theme.typography.fontBody,
                      fontSize: theme.typography.fontSize.sm,
                      fontWeight: theme.typography.fontWeight.medium,
                    }}
                  >
                    {cap?.label || String(cap)}
                  </span>
                ))}
              </div>
            </div>

            {/* Key Features */}
            <div
              style={{
                backgroundColor: theme.colors.white,
                padding: '1.5rem',
                borderRadius: theme.borderRadius.xl,
                boxShadow: theme.shadows.md,
              }}
            >
              <h4
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                  color: theme.colors.dark,
                  marginBottom: '1rem',
                }}
              >
                Key Features
              </h4>
              <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                {agent.features.map((feature: string, index: number) => (
                  <li
                    key={index}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      marginBottom: '0.75rem',
                    }}
                  >
                    <ChevronRight
                      size={16}
                      color={theme.colors.primary}
                      style={{ marginTop: '0.25rem', flexShrink: 0 }}
                    />
                    <span
                      style={{
                        fontFamily: theme.typography.fontBody,
                        fontSize: theme.typography.fontSize.sm,
                        color: theme.colors.darkLight,
                        lineHeight: theme.typography.lineHeight.relaxed,
                      }}
                    >
                      {feature}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Use Cases */}
            <div
              style={{
                backgroundColor: theme.colors.white,
                padding: '1.5rem',
                borderRadius: theme.borderRadius.xl,
                boxShadow: theme.shadows.md,
              }}
            >
              <h4
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                  color: theme.colors.dark,
                  marginBottom: '1rem',
                }}
              >
                Use Cases
              </h4>
              <ul style={{ margin: 0, padding: 0, listStyle: 'none' }}>
                {agent.useCases.map((useCase: string, index: number) => (
                  <li
                    key={index}
                    style={{
                      display: 'flex',
                      alignItems: 'flex-start',
                      gap: '0.75rem',
                      marginBottom: '0.75rem',
                    }}
                  >
                    <Code
                      size={16}
                      color={theme.colors.secondary}
                      style={{ marginTop: '0.25rem', flexShrink: 0 }}
                    />
                    <span
                      style={{
                        fontFamily: theme.typography.fontBody,
                        fontSize: theme.typography.fontSize.sm,
                        color: theme.colors.darkLight,
                        lineHeight: theme.typography.lineHeight.relaxed,
                      }}
                    >
                      {useCase}
                    </span>
                  </li>
                ))}
              </ul>
            </div>

            {/* Performance Metrics */}
            <div
              style={{
                backgroundColor: theme.colors.white,
                padding: '1.5rem',
                borderRadius: theme.borderRadius.xl,
                boxShadow: theme.shadows.md,
              }}
            >
              <h4
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                  color: theme.colors.dark,
                  marginBottom: '1rem',
                }}
              >
                Performance
              </h4>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '0.75rem' }}>
                {agent.metrics && typeof agent.metrics === 'object' && 'accuracy' in agent.metrics && (
                  <>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span
                        style={{
                          fontFamily: theme.typography.fontBody,
                          fontSize: theme.typography.fontSize.sm,
                          color: theme.colors.darkLight,
                        }}
                      >
                        Accuracy
                      </span>
                      <span
                        style={{
                          fontFamily: theme.typography.fontBody,
                          fontSize: theme.typography.fontSize.sm,
                          fontWeight: theme.typography.fontWeight.semibold,
                          color: theme.colors.success,
                        }}
                      >
                        {(agent.metrics as any).accuracy}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span
                        style={{
                          fontFamily: theme.typography.fontBody,
                          fontSize: theme.typography.fontSize.sm,
                          color: theme.colors.darkLight,
                        }}
                      >
                        Response Time
                      </span>
                      <span
                        style={{
                          fontFamily: theme.typography.fontBody,
                          fontSize: theme.typography.fontSize.sm,
                          fontWeight: theme.typography.fontWeight.semibold,
                          color: theme.colors.info,
                        }}
                      >
                        {(agent.metrics as any).responseTime}
                      </span>
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span
                        style={{
                          fontFamily: theme.typography.fontBody,
                          fontSize: theme.typography.fontSize.sm,
                          color: theme.colors.darkLight,
                        }}
                      >
                        Satisfaction
                      </span>
                      <span
                        style={{
                          fontFamily: theme.typography.fontBody,
                          fontSize: theme.typography.fontSize.sm,
                          fontWeight: theme.typography.fontWeight.semibold,
                          color: theme.colors.primary,
                        }}
                      >
                        {(agent.metrics as any).satisfaction}
                      </span>
                    </div>
                  </>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default AgentDetailPage;
