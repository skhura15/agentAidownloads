/**
 * AgentCard Component
 * 
 * Reusable card component for displaying agent information in the gallery.
 * Features:
 * - Hover effects with lift animation
 * - Status indicators
 * - Capability badges
 * - Popularity rating
 * - Responsive design
 */

import React from 'react';
import { useNavigate } from 'react-router-dom';
import * as LucideIcons from 'lucide-react';
// @ts-ignore - Module exists but TypeScript can't resolve it
import { Agent } from '../data/agents';
import { theme } from '../styles/theme';

interface AgentCardProps {
  agent: Agent;
  featured?: boolean;
}

const AgentCard: React.FC<AgentCardProps> = ({ agent, featured = false }) => {
  const navigate = useNavigate();
  const Icon = (LucideIcons as any)[agent.icon] || LucideIcons.Bot;

  // Status config
  const statusConfig = {
    live: {
      label: 'Live',
      color: theme.colors.statusLive,
      bgColor: 'rgba(40, 167, 69, 0.1)',
    },
    beta: {
      label: 'Beta',
      color: theme.colors.statusBeta,
      bgColor: 'rgba(23, 162, 184, 0.1)',
    },
    'coming-soon': {
      label: 'Coming Soon',
      color: theme.colors.statusComingSoon,
      bgColor: 'rgba(255, 193, 7, 0.1)',
    },
  };

  const currentStatus = statusConfig[agent.status as keyof typeof statusConfig];

  return (
    <div
      style={{
        backgroundColor: theme.colors.white,
        borderRadius: theme.borderRadius.xl,
        padding: featured ? '2rem' : '1.5rem',
        boxShadow: theme.shadows.card,
        transition: `all ${theme.transitions.base}`,
        cursor: 'pointer',
        position: 'relative',
        overflow: 'hidden',
        border: `1px solid ${theme.colors.light}`,
        height: '100%',
        display: 'flex',
        flexDirection: 'column',
      }}
      className="agent-card"
      onClick={() => {
        if (!agent.demoAvailable) return;
        if (agent.category === 'training') {
          navigate('/in-flow-simulation');
        } else {
          navigate(`/agents/${agent.id}`);
        }
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.transform = 'translateY(-8px)';
        e.currentTarget.style.boxShadow = theme.shadows.cardHover;
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = theme.shadows.card;
      }}
    >
      {/* New Badge */}
      {agent.isNew && (
        <div
          style={{
            position: 'absolute',
            top: '1rem',
            right: '1rem',
            backgroundColor: theme.colors.accent,
            color: theme.colors.white,
            padding: '0.25rem 0.75rem',
            borderRadius: theme.borderRadius.full,
            fontSize: theme.typography.fontSize.xs,
            fontWeight: theme.typography.fontWeight.bold,
            fontFamily: theme.typography.fontBody,
          }}
        >
          NEW
        </div>
      )}

      {/* Icon */}
      <div
        style={{
          width: featured ? '80px' : '64px',
          height: featured ? '80px' : '64px',
          backgroundColor: theme.colors.overlayLight,
          borderRadius: theme.borderRadius.xl,
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'center',
          marginBottom: '1.5rem',
        }}
      >
        <Icon
          size={featured ? 40 : 32}
          color={theme.colors.primary}
          strokeWidth={2}
        />
      </div>

      {/* Agent Info */}
      <div style={{ flex: 1 }}>
        <h3
          style={{
            fontFamily: theme.typography.fontHeading,
            fontSize: featured ? theme.typography.fontSize['2xl'] : theme.typography.fontSize.xl,
            fontWeight: theme.typography.fontWeight.bold,
            color: theme.colors.dark,
            marginBottom: '0.5rem',
            lineHeight: theme.typography.lineHeight.tight,
          }}
        >
          {agent.name}
        </h3>

        <p
          style={{
            fontFamily: theme.typography.fontBody,
            fontSize: theme.typography.fontSize.sm,
            color: theme.colors.primary,
            fontWeight: theme.typography.fontWeight.semibold,
            marginBottom: '0.75rem',
          }}
        >
          {agent.tagline}
        </p>

        <p
          style={{
            fontFamily: theme.typography.fontBody,
            fontSize: theme.typography.fontSize.sm,
            color: theme.colors.darkLight,
            lineHeight: theme.typography.lineHeight.relaxed,
            marginBottom: '1.5rem',
          }}
        >
          {agent.description}
        </p>

        {/* Capabilities */}
        <div
          style={{
            display: 'flex',
            flexWrap: 'wrap',
            gap: '0.5rem',
            marginBottom: '1.5rem',
          }}
        >
          {agent.capabilities.slice(0, 3).map((capability: any) => (
            <span
              key={capability.id}
              style={{
                padding: '0.25rem 0.75rem',
                backgroundColor: `${capability.color}15`,
                color: capability.color,
                borderRadius: theme.borderRadius.full,
                fontSize: theme.typography.fontSize.xs,
                fontWeight: theme.typography.fontWeight.medium,
                fontFamily: theme.typography.fontBody,
              }}
            >
              {capability.label}
            </span>
          ))}
        </div>

        {/* Popularity Stars */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.25rem',
            marginBottom: '1rem',
          }}
        >
          {[...Array(5)].map((_, index) => (
            <LucideIcons.Star
              key={index}
              size={16}
              fill={index < agent.popularity ? theme.colors.accent : 'none'}
              color={index < agent.popularity ? theme.colors.accent : theme.colors.light}
              strokeWidth={1.5}
            />
          ))}
        </div>
      </div>

      {/* Footer */}
      <div
        style={{
          display: 'flex',
          justifyContent: 'space-between',
          alignItems: 'center',
          paddingTop: '1rem',
          borderTop: `1px solid ${theme.colors.light}`,
        }}
      >
        {/* Status */}
        <div
          style={{
            display: 'flex',
            alignItems: 'center',
            gap: '0.5rem',
            padding: '0.375rem 0.75rem',
            backgroundColor: currentStatus.bgColor,
            borderRadius: theme.borderRadius.full,
          }}
        >
          <div
            style={{
              width: '8px',
              height: '8px',
              borderRadius: '50%',
              backgroundColor: currentStatus.color,
            }}
          />
          <span
            style={{
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.xs,
              fontWeight: theme.typography.fontWeight.semibold,
              color: currentStatus.color,
            }}
          >
            {currentStatus.label}
          </span>
        </div>

        {/* Try Button */}
        {agent.demoAvailable ? (
          <button
            style={{
              padding: '0.5rem 1rem',
              backgroundColor: theme.colors.primary,
              color: theme.colors.white,
              border: 'none',
              borderRadius: theme.borderRadius.md,
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.sm,
              fontWeight: theme.typography.fontWeight.semibold,
              cursor: 'pointer',
              transition: `all ${theme.transitions.fast}`,
              display: 'flex',
              alignItems: 'center',
              gap: '0.5rem',
            }}
            onClick={(e) => {
              e.stopPropagation();
              navigate(`/agents/${agent.id}`);
            }}
            onMouseOver={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.secondary;
            }}
            onMouseOut={(e) => {
              e.currentTarget.style.backgroundColor = theme.colors.primary;
            }}
          >
            Try Agent
            <LucideIcons.ArrowRight size={16} />
          </button>
        ) : (
          <span
            style={{
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.sm,
              color: theme.colors.darkLight,
              fontStyle: 'italic',
            }}
          >
            Coming Soon
          </span>
        )}
      </div>
    </div>
  );
};

export default AgentCard;
