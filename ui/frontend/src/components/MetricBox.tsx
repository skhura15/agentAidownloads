/**
 * MetricBox Component
 * 
 * Displays a single metric with animated counter and icon.
 * Features:
 * - Count-up animation when in viewport
 * - Icon support
 * - Responsive design
 */

import React, { useState, useEffect, useRef } from 'react';
import * as LucideIcons from 'lucide-react';
import { theme } from '../styles/theme';

interface MetricBoxProps {
  value: string;
  label: string;
  icon?: keyof typeof LucideIcons;
  animated?: boolean;
}

const MetricBox: React.FC<MetricBoxProps> = ({
  value,
  label,
  icon,
  animated = true,
}) => {
  const [count, setCount] = useState(0);
  const [hasAnimated, setHasAnimated] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  const Icon = icon ? (LucideIcons as any)[icon] : null;

  // Extract number from value string (e.g., "15+" -> 15)
  const numericValue = parseInt(value.replace(/[^0-9]/g, ''), 10);
  const suffix = value.replace(/[0-9]/g, '');

  useEffect(() => {
    if (!animated || hasAnimated || isNaN(numericValue)) return;

    const observer = new IntersectionObserver(
      (entries) => {
        if (entries[0].isIntersecting) {
          setHasAnimated(true);
          
          // Animate counter
          const duration = 2000; // 2 seconds
          const steps = 60;
          const increment = numericValue / steps;
          let current = 0;

          const timer = setInterval(() => {
            current += increment;
            if (current >= numericValue) {
              setCount(numericValue);
              clearInterval(timer);
            } else {
              setCount(Math.floor(current));
            }
          }, duration / steps);

          return () => clearInterval(timer);
        }
      },
      { threshold: 0.5 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => {
      if (ref.current) {
        observer.unobserve(ref.current);
      }
    };
  }, [animated, hasAnimated, numericValue]);

  return (
    <div
      ref={ref}
      style={{
        backgroundColor: theme.colors.white,
        borderRadius: theme.borderRadius.xl,
        padding: '2rem',
        boxShadow: theme.shadows.md,
        textAlign: 'center',
        transition: `all ${theme.transitions.base}`,
        border: `1px solid ${theme.colors.light}`,
      }}
      onMouseOver={(e) => {
        e.currentTarget.style.transform = 'translateY(-4px)';
        e.currentTarget.style.boxShadow = theme.shadows.lg;
      }}
      onMouseOut={(e) => {
        e.currentTarget.style.transform = 'translateY(0)';
        e.currentTarget.style.boxShadow = theme.shadows.md;
      }}
    >
      {Icon && (
        <div
          style={{
            width: '64px',
            height: '64px',
            margin: '0 auto 1rem',
            backgroundColor: theme.colors.overlayLight,
            borderRadius: theme.borderRadius.full,
            display: 'flex',
            alignItems: 'center',
            justifyContent: 'center',
          }}
        >
          <Icon size={32} color={theme.colors.primary} strokeWidth={2} />
        </div>
      )}

      <div
        style={{
          fontFamily: theme.typography.fontHeading,
          fontSize: theme.typography.fontSize['4xl'],
          fontWeight: theme.typography.fontWeight.bold,
          color: theme.colors.primary,
          marginBottom: '0.5rem',
          lineHeight: theme.typography.lineHeight.tight,
        }}
      >
        {animated && !isNaN(numericValue) ? `${count}${suffix}` : value}
      </div>

      <div
        style={{
          fontFamily: theme.typography.fontBody,
          fontSize: theme.typography.fontSize.base,
          color: theme.colors.darkLight,
          fontWeight: theme.typography.fontWeight.medium,
        }}
      >
        {label}
      </div>
    </div>
  );
};

export default MetricBox;
