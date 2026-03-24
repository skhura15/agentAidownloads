import React, { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Zap,
  Shield,
  Network,
  Rocket,
  ArrowRight,
  Play,
  Code,
  Database,
  Cloud,
  Sparkles,
} from 'lucide-react';
import Header from '../components/Header';
import AgentCard from '../components/AgentCard';
import MetricBox from '../components/MetricBox';
import { SupportChat } from '../components/SupportChat';
// @ts-ignore - Module exists but TypeScript can't resolve it
import { getPopularAgents } from '../data/agents';
import { theme } from '../styles/theme';

const LandingPage: React.FC = () => {
  const navigate = useNavigate();
  const [isVisible, setIsVisible] = useState(false);

  useEffect(() => {
    setIsVisible(true);
    const hash = window.location.hash;
    if (hash) {
      setTimeout(() => {
        document.querySelector(hash)?.scrollIntoView({ behavior: 'smooth' });
      }, 100);
    }
  }, []);

  const popularAgents = getPopularAgents(6);

  return (
    <div style={{ backgroundColor: theme.colors.white, minHeight: '100vh' }}>
      <Header />

      {/* Hero Section */}
      <section
        id="hero"
        style={{
          position: 'relative',
          background: theme.colors.gradientHero,
          color: theme.colors.white,
          padding: '6rem 1.5rem',
          overflow: 'hidden',
        }}
      >
        <div
          style={{
            position: 'absolute',
            top: 0,
            left: 0,
            right: 0,
            bottom: 0,
            opacity: 0.1,
            backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%23ffffff' fill-opacity='1'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          }}
        />

        <div
          style={{
            maxWidth: '1280px',
            margin: '0 auto',
            position: 'relative',
            zIndex: 1,
          }}
        >
          <div
            style={{
              maxWidth: '900px',
              margin: '0 auto',
              textAlign: 'center',
              opacity: isVisible ? 1 : 0,
              transform: isVisible ? 'translateY(0)' : 'translateY(30px)',
              transition: `all ${theme.transitions.slow}`,
            }}
          >
            <div
              style={{
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                backgroundColor: 'rgba(255, 255, 255, 0.15)',
                backdropFilter: 'blur(10px)',
                padding: '0.5rem 1.5rem',
                borderRadius: theme.borderRadius.full,
                marginBottom: '2rem',
                fontFamily: theme.typography.fontBody,
                fontSize: theme.typography.fontSize.sm,
                fontWeight: theme.typography.fontWeight.semibold,
              }}
            >
              <Sparkles size={16} />
              <span>Powered by Microsoft Agent Framework</span>
            </div>

            <h1
              style={{
                fontFamily: theme.typography.fontHeading,
                fontSize: 'clamp(2.5rem, 5vw, 4rem)',
                fontWeight: theme.typography.fontWeight.extrabold,
                lineHeight: theme.typography.lineHeight.tight,
                marginBottom: '1.5rem',
                textShadow: '0 2px 4px rgba(0, 0, 0, 0.1)',
              }}
            >
              HCLTech Agentic CoE
            </h1>

            <h2
              style={{
                fontFamily: theme.typography.fontHeading,
                fontSize: theme.typography.fontSize['2xl'],
                fontWeight: theme.typography.fontWeight.semibold,
                marginBottom: '1.5rem',
                opacity: 0.95,
              }}
            >
              Accelerating Enterprise AI Agent Development
            </h2>

            <p
              style={{
                fontFamily: theme.typography.fontBody,
                fontSize: theme.typography.fontSize.lg,
                lineHeight: theme.typography.lineHeight.relaxed,
                marginBottom: '3rem',
                opacity: 0.9,
                maxWidth: '800px',
                margin: '0 auto 3rem',
              }}
            >
              Empowering organizations to build production-ready, multi-agent AI solutions at scale 
              using Microsoft Azure and cutting-edge Agentic Frameworks. From concept to deployment 
              in weeks, not months.
            </p>

            <div
              style={{
                display: 'flex',
                gap: '1rem',
                justifyContent: 'center',
                flexWrap: 'wrap',
              }}
            >
              <button
                style={{
                  padding: '1rem 2rem',
                  backgroundColor: theme.colors.accent,
                  color: theme.colors.white,
                  border: 'none',
                  borderRadius: theme.borderRadius.md,
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: `all ${theme.transitions.base}`,
                  boxShadow: '0 4px 6px rgba(0, 0, 0, 0.1)',
                }}
                onClick={() => document.getElementById('agents')?.scrollIntoView({ behavior: 'smooth' })}
                onMouseOver={(e) => {
                  e.currentTarget.style.transform = 'translateY(-2px)';
                  e.currentTarget.style.boxShadow = '0 6px 12px rgba(0, 0, 0, 0.15)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.transform = 'translateY(0)';
                  e.currentTarget.style.boxShadow = '0 4px 6px rgba(0, 0, 0, 0.1)';
                }}
              >
                <Rocket size={20} />
                Explore Agents
              </button>

              <button
                style={{
                  padding: '1rem 2rem',
                  backgroundColor: 'rgba(255, 255, 255, 0.15)',
                  backdropFilter: 'blur(10px)',
                  color: theme.colors.white,
                  border: `2px solid ${theme.colors.white}`,
                  borderRadius: theme.borderRadius.md,
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.semibold,
                  cursor: 'pointer',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '0.5rem',
                  transition: `all ${theme.transitions.base}`,
                }}
                onClick={() => navigate('/docs')}
                onMouseOver={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.25)';
                  e.currentTarget.style.transform = 'translateY(-2px)';
                }}
                onMouseOut={(e) => {
                  e.currentTarget.style.backgroundColor = 'rgba(255, 255, 255, 0.15)';
                  e.currentTarget.style.transform = 'translateY(0)';
                }}
              >
                <Play size={20} />
                View Documentation
              </button>
            </div>
          </div>
        </div>
      </section>

      {/* Value Proposition Section */}
      <section
        id="value-proposition"
        style={{
          padding: '6rem 1.5rem',
          backgroundColor: theme.colors.light,
        }}
      >
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2
              style={{
                fontFamily: theme.typography.fontHeading,
                fontSize: theme.typography.fontSize['4xl'],
                fontWeight: theme.typography.fontWeight.bold,
                color: theme.colors.dark,
                marginBottom: '1rem',
              }}
            >
              Why HCLTech Agentic CoE?
            </h2>
            <p
              style={{
                fontFamily: theme.typography.fontBody,
                fontSize: theme.typography.fontSize.lg,
                color: theme.colors.darkLight,
                maxWidth: '700px',
                margin: '0 auto',
              }}
            >
              Accelerate your AI journey with proven frameworks and enterprise-grade solutions
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))',
              gap: '2rem',
            }}
          >
            {[
              {
                icon: Zap,
                title: 'Rapid Development',
                description:
                  'Pre-built frameworks and reusable components reduce agent development time by 70%. Get from prototype to production faster with battle-tested patterns and comprehensive tooling.',
              },
              {
                icon: Shield,
                title: 'Production Ready',
                description:
                  'Enterprise-grade architecture with built-in security, monitoring, and compliance. Designed for Microsoft Azure cloud-native deployment with automatic scaling and high availability.',
              },
              {
                icon: Network,
                title: 'Multi-Agent Orchestration',
                description:
                  'Seamlessly coordinate multiple specialized agents working together. Built on Microsoft Agent Framework and AutoGen for intelligent collaboration and complex task decomposition.',
              },
            ].map((prop, index) => {
              const Icon = prop.icon;
              return (
                <div
                  key={index}
                  style={{
                    backgroundColor: theme.colors.white,
                    padding: '2.5rem',
                    borderRadius: theme.borderRadius.xl,
                    boxShadow: theme.shadows.md,
                    transition: `all ${theme.transitions.base}`,
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-8px)';
                    e.currentTarget.style.boxShadow = theme.shadows.xl;
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = theme.shadows.md;
                  }}
                >
                  <div
                    style={{
                      width: '72px',
                      height: '72px',
                      backgroundColor: theme.colors.overlayLight,
                      borderRadius: theme.borderRadius.xl,
                      display: 'flex',
                      alignItems: 'center',
                      justifyContent: 'center',
                      marginBottom: '1.5rem',
                    }}
                  >
                    <Icon size={36} color={theme.colors.primary} strokeWidth={2} />
                  </div>
                  <h3
                    style={{
                      fontFamily: theme.typography.fontHeading,
                      fontSize: theme.typography.fontSize['2xl'],
                      fontWeight: theme.typography.fontWeight.bold,
                      color: theme.colors.dark,
                      marginBottom: '1rem',
                    }}
                  >
                    {prop.title}
                  </h3>
                  <p
                    style={{
                      fontFamily: theme.typography.fontBody,
                      fontSize: theme.typography.fontSize.base,
                      color: theme.colors.darkLight,
                      lineHeight: theme.typography.lineHeight.relaxed,
                    }}
                  >
                    {prop.description}
                  </p>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* AI Agents Gallery Section */}
      <section
        id="agents"
        style={{
          padding: '6rem 1.5rem',
          backgroundColor: theme.colors.white,
        }}
      >
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2
              style={{
                fontFamily: theme.typography.fontHeading,
                fontSize: theme.typography.fontSize['4xl'],
                fontWeight: theme.typography.fontWeight.bold,
                color: theme.colors.dark,
                marginBottom: '1rem',
              }}
            >
              AI Agent Portfolio
            </h2>
            <p
              style={{
                fontFamily: theme.typography.fontBody,
                fontSize: theme.typography.fontSize.lg,
                color: theme.colors.darkLight,
                maxWidth: '700px',
                margin: '0 auto',
              }}
            >
              Explore our suite of specialized agents powered by cutting-edge AI capabilities
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
              gap: '2rem',
              marginBottom: '3rem',
            }}
          >
            {popularAgents.map((agent: any) => (
              <AgentCard key={agent.id} agent={agent} />
            ))}
          </div>

          <div style={{ textAlign: 'center' }}>
            <button
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
                display: 'inline-flex',
                alignItems: 'center',
                gap: '0.5rem',
                transition: `all ${theme.transitions.base}`,
              }}
              onClick={() => navigate('/agents')}
              onMouseOver={(e) => {
                e.currentTarget.style.backgroundColor = theme.colors.primaryDark;
                e.currentTarget.style.transform = 'translateY(-2px)';
              }}
              onMouseOut={(e) => {
                e.currentTarget.style.backgroundColor = theme.colors.primary;
                e.currentTarget.style.transform = 'translateY(0)';
              }}
            >
              View All Agents
              <ArrowRight size={18} />
            </button>
          </div>
        </div>
      </section>

      {/* Technology Stack Section */}
      <section
        id="tech-stack"
        style={{
          padding: '6rem 1.5rem',
          backgroundColor: theme.colors.light,
        }}
      >
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2
              style={{
                fontFamily: theme.typography.fontHeading,
                fontSize: theme.typography.fontSize['4xl'],
                fontWeight: theme.typography.fontWeight.bold,
                color: theme.colors.dark,
                marginBottom: '1rem',
              }}
            >
              Powered by Industry Leaders
            </h2>
            <p
              style={{
                fontFamily: theme.typography.fontBody,
                fontSize: theme.typography.fontSize.lg,
                color: theme.colors.darkLight,
                maxWidth: '700px',
                margin: '0 auto',
              }}
            >
              Built on Microsoft's world-class AI and cloud infrastructure
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '2rem',
              alignItems: 'center',
              justifyItems: 'center',
            }}
          >
            {[
              { name: 'Microsoft Azure', icon: Cloud, color: theme.colors.primary },
              { name: 'Agent Framework', icon: Network, color: theme.colors.secondary },
              { name: 'Azure OpenAI', icon: Sparkles, color: theme.colors.accent },
              { name: 'FastAPI', icon: Code, color: theme.colors.success },
              { name: 'PostgreSQL', icon: Database, color: theme.colors.info },
            ].map((tech, index) => {
              const Icon = tech.icon;
              return (
                <div
                  key={index}
                  style={{
                    display: 'flex',
                    flexDirection: 'column',
                    alignItems: 'center',
                    gap: '1rem',
                    padding: '2rem',
                    backgroundColor: theme.colors.white,
                    borderRadius: theme.borderRadius.lg,
                    transition: `all ${theme.transitions.base}`,
                    width: '100%',
                  }}
                  onMouseOver={(e) => {
                    e.currentTarget.style.transform = 'translateY(-4px)';
                    e.currentTarget.style.boxShadow = theme.shadows.lg;
                  }}
                  onMouseOut={(e) => {
                    e.currentTarget.style.transform = 'translateY(0)';
                    e.currentTarget.style.boxShadow = 'none';
                  }}
                >
                  <Icon size={48} color={tech.color} strokeWidth={1.5} />
                  <span
                    style={{
                      fontFamily: theme.typography.fontBody,
                      fontSize: theme.typography.fontSize.base,
                      fontWeight: theme.typography.fontWeight.semibold,
                      color: theme.colors.dark,
                    }}
                  >
                    {tech.name}
                  </span>
                </div>
              );
            })}
          </div>
        </div>
      </section>

      {/* Statistics Section */}
      <section
        id="metrics"
        style={{
          padding: '6rem 1.5rem',
          backgroundColor: theme.colors.white,
        }}
      >
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div style={{ textAlign: 'center', marginBottom: '4rem' }}>
            <h2
              style={{
                fontFamily: theme.typography.fontHeading,
                fontSize: theme.typography.fontSize['4xl'],
                fontWeight: theme.typography.fontWeight.bold,
                color: theme.colors.dark,
                marginBottom: '1rem',
              }}
            >
              Proven Impact
            </h2>
            <p
              style={{
                fontFamily: theme.typography.fontBody,
                fontSize: theme.typography.fontSize.lg,
                color: theme.colors.darkLight,
                maxWidth: '700px',
                margin: '0 auto',
              }}
            >
              Real results from organizations leveraging our Agentic CoE
            </p>
          </div>

          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))',
              gap: '2rem',
            }}
          >
            <MetricBox icon="Rocket" value="15+" label="Production Agents" />
            <MetricBox icon="Users" value="1000+" label="AI Agents in Development Pipeline for GTM & Industry Specific" />
            <MetricBox icon="TrendingUp" value="70%" label="Development Time Saved" />
            <MetricBox icon="Award" value="99.9%" label="Uptime SLA" />
          </div>
        </div>
      </section>

      {/* Footer */}
      <footer
        style={{
          backgroundColor: theme.colors.dark,
          color: theme.colors.white,
          padding: '3rem 1.5rem 2rem',
        }}
      >
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))',
              gap: '3rem',
              marginBottom: '3rem',
            }}
          >
            <div>
              <h3
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize.lg,
                  fontWeight: theme.typography.fontWeight.bold,
                  marginBottom: '1rem',
                }}
              >
                HCLTech Agentic CoE
              </h3>
              <p
                style={{
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.sm,
                  color: theme.colors.gray,
                  lineHeight: theme.typography.lineHeight.relaxed,
                }}
              >
                Accelerating enterprise AI agent development with Microsoft partnership excellence.
              </p>
            </div>
            <div>
              <h4
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize.base,
                  fontWeight: theme.typography.fontWeight.semibold,
                  marginBottom: '1rem',
                }}
              >
                Resources
              </h4>
              <ul style={{ listStyle: 'none', padding: 0, margin: 0 }}>
                {['Documentation', 'API Reference', 'Examples', 'Blog'].map((item) => (
                  <li key={item} style={{ marginBottom: '0.5rem' }}>
                    <a
                      href="#"
                      style={{
                        fontFamily: theme.typography.fontBody,
                        fontSize: theme.typography.fontSize.sm,
                        color: theme.colors.gray,
                        textDecoration: 'none',
                        transition: `color ${theme.transitions.fast}`,
                      }}
                      onMouseOver={(e) => (e.currentTarget.style.color = theme.colors.secondary)}
                      onMouseOut={(e) => (e.currentTarget.style.color = theme.colors.gray)}
                    >
                      {item}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          </div>
          <div
            style={{
              paddingTop: '2rem',
              borderTop: `1px solid ${theme.colors.darkLight}`,
              textAlign: 'center',
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.sm,
              color: theme.colors.gray,
            }}
          >
            <p>© 2024 HCLTech. All rights reserved. Microsoft Partner.</p>
          </div>
        </div>
      </footer>
      
      {/* Support Chat Widget */}
      <SupportChat />
    </div>
  );
};

export default LandingPage;
