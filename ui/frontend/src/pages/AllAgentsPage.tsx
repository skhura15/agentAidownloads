/**
 * All Agents Page
 * 
 * Displays a comprehensive gallery of all available AI agents with filtering
 * and search capabilities.
 */

import React, { useState, useMemo } from 'react';
import { Search, Filter } from 'lucide-react';
import Header from '../components/Header';
import AgentCard from '../components/AgentCard';
// @ts-ignore - Module exists but TypeScript can't resolve it
import { agents, categories } from '../data/agents';
import { theme } from '../styles/theme';

const AllAgentsPage: React.FC = () => {
  const [searchQuery, setSearchQuery] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string>('All');
  const [selectedStatus, setSelectedStatus] = useState<string>('All');

  // Filter agents based on search and filters
  const filteredAgents = useMemo(() => {
    return agents.filter((agent: any) => {
      const matchesSearch =
        searchQuery === '' ||
        agent.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        agent.description.toLowerCase().includes(searchQuery.toLowerCase());

      const matchesCategory =
        selectedCategory === 'All' || agent.category === selectedCategory;

      const matchesStatus =
        selectedStatus === 'All' || agent.status === selectedStatus;

      return matchesSearch && matchesCategory && matchesStatus;
    });
  }, [searchQuery, selectedCategory, selectedStatus]);

  return (
    <div style={{ minHeight: '100vh', backgroundColor: theme.colors.light }}>
      <Header />

      {/* Hero Section */}
      <section
        style={{
          background: theme.colors.gradientHero,
          color: theme.colors.white,
          padding: '4rem 1.5rem',
          textAlign: 'center',
        }}
      >
        <div style={{ maxWidth: '800px', margin: '0 auto' }}>
          <h1
            style={{
              fontFamily: theme.typography.fontHeading,
              fontSize: theme.typography.fontSize['4xl'],
              fontWeight: theme.typography.fontWeight.bold,
              marginBottom: '1rem',
            }}
          >
            AI Agent Portfolio
          </h1>
          <p
            style={{
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.lg,
              lineHeight: theme.typography.lineHeight.relaxed,
              opacity: 0.95,
            }}
          >
            Discover and deploy specialized AI agents for every business need
          </p>
        </div>
      </section>

      {/* Filters and Search */}
      <section
        style={{
          backgroundColor: theme.colors.white,
          borderBottom: `1px solid ${theme.colors.gray}`,
          padding: '2rem 1.5rem',
        }}
      >
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          <div
            style={{
              display: 'grid',
              gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))',
              gap: '1rem',
              marginBottom: '1.5rem',
            }}
          >
            {/* Search */}
            <div style={{ position: 'relative' }}>
              <Search
                size={20}
                color={theme.colors.darkLight}
                style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                }}
              />
              <input
                type="text"
                placeholder="Search agents..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.875rem 1rem 0.875rem 3rem',
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
            </div>

            {/* Category Filter */}
            <div style={{ position: 'relative' }}>
              <Filter
                size={20}
                color={theme.colors.darkLight}
                style={{
                  position: 'absolute',
                  left: '1rem',
                  top: '50%',
                  transform: 'translateY(-50%)',
                  pointerEvents: 'none',
                }}
              />
              <select
                value={selectedCategory}
                onChange={(e) => setSelectedCategory(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.875rem 1rem 0.875rem 3rem',
                  border: `1px solid ${theme.colors.gray}`,
                  borderRadius: theme.borderRadius.md,
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.base,
                  outline: 'none',
                  cursor: 'pointer',
                  backgroundColor: theme.colors.white,
                  transition: `border-color ${theme.transitions.fast}`,
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = theme.colors.primary;
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = theme.colors.gray;
                }}
              >
                <option value="All">All Categories</option>
                {categories.map((category: any) => (
                  <option key={category.id} value={category.id}>
                    {category.label}
                  </option>
                ))}
              </select>
            </div>

            {/* Status Filter */}
            <div style={{ position: 'relative' }}>
              <select
                value={selectedStatus}
                onChange={(e) => setSelectedStatus(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.875rem 1rem',
                  border: `1px solid ${theme.colors.gray}`,
                  borderRadius: theme.borderRadius.md,
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.base,
                  outline: 'none',
                  cursor: 'pointer',
                  backgroundColor: theme.colors.white,
                  transition: `border-color ${theme.transitions.fast}`,
                }}
                onFocus={(e) => {
                  e.currentTarget.style.borderColor = theme.colors.primary;
                }}
                onBlur={(e) => {
                  e.currentTarget.style.borderColor = theme.colors.gray;
                }}
              >
                <option value="All">All Status</option>
                <option value="live">Live</option>
                <option value="beta">Beta</option>
                <option value="coming-soon">Coming Soon</option>
              </select>
            </div>
          </div>

          {/* Results Count */}
          <p
            style={{
              fontFamily: theme.typography.fontBody,
              fontSize: theme.typography.fontSize.sm,
              color: theme.colors.darkLight,
            }}
          >
            Showing {filteredAgents.length} of {agents.length} agents
          </p>
        </div>
      </section>

      {/* Agents Grid */}
      <section style={{ padding: '3rem 1.5rem' }}>
        <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
          {filteredAgents.length === 0 ? (
            <div
              style={{
                textAlign: 'center',
                padding: '4rem 2rem',
              }}
            >
              <h3
                style={{
                  fontFamily: theme.typography.fontHeading,
                  fontSize: theme.typography.fontSize['2xl'],
                  fontWeight: theme.typography.fontWeight.semibold,
                  color: theme.colors.dark,
                  marginBottom: '0.5rem',
                }}
              >
                No agents found
              </h3>
              <p
                style={{
                  fontFamily: theme.typography.fontBody,
                  fontSize: theme.typography.fontSize.base,
                  color: theme.colors.darkLight,
                }}
              >
                Try adjusting your search or filters
              </p>
            </div>
          ) : (
            <div
              style={{
                display: 'grid',
                gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))',
                gap: '2rem',
              }}
            >
              {filteredAgents.map((agent: any) => (
                <AgentCard key={agent.id} agent={agent} />
              ))}
            </div>
          )}
        </div>
      </section>
    </div>
  );
};

export default AllAgentsPage;
