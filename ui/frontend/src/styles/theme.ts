/**
 * HCLTech Brand Theme Configuration
 * 
 * This file contains the official HCLTech brand colors, typography, and design tokens
 * for consistent styling across the Agentic CoE platform.
 * 
 * Usage:
 * import { theme } from '@/styles/theme';
 * <div style={{ color: theme.colors.primary }}>
 */

export const theme = {
  colors: {
    // HCLTech Brand Colors
    primary: '#0070AD',        // HCLTech Blue - Primary brand color
    primaryDark: '#005A8C',    // Darker blue for hover states
    secondary: '#00A3E0',      // Light Blue - Supporting brand color
    accent: '#FF6B35',         // Orange - CTAs and highlights
    
    // Neutrals
    dark: '#2C3E50',          // Dark Gray - Primary text
    darkLight: '#495057',     // Medium Gray - Secondary text
    gray: '#ADB5BD',          // Gray - Borders and dividers
    light: '#F8F9FA',         // Light Gray - Backgrounds
    white: '#FFFFFF',         // White - Cards and text
    
    // Semantic Colors
    success: '#28A745',       // Green - Success states
    warning: '#FFC107',       // Yellow - Warning states
    error: '#DC3545',         // Red - Error states
    info: '#17A2B8',          // Teal - Info states
    
    // Status Indicators
    statusLive: '#28A745',    // Green - Live agents
    statusBeta: '#17A2B8',    // Blue - Beta agents
    statusComingSoon: '#FFC107', // Orange - Coming soon
    
    // Gradients
    gradientPrimary: 'linear-gradient(135deg, #0070AD 0%, #00A3E0 100%)',
    gradientHero: 'linear-gradient(135deg, #0070AD 0%, #00A3E0 50%, #0070AD 100%)',
    gradientOverlay: 'linear-gradient(135deg, #0070AD 0%, #00A3E0 100%)',
    gradientCard: 'linear-gradient(145deg, #FFFFFF 0%, #F8F9FA 100%)',
    
    // Overlays
    overlay: 'rgba(0, 112, 173, 0.9)',
    overlayLight: 'rgba(0, 112, 173, 0.05)',
  },
  
  typography: {
    // Font Families
    fontHeading: "'Montserrat', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontBody: "'Open Sans', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif",
    fontMono: "'Fira Code', 'Courier New', monospace",
    
    // Font Sizes
    fontSize: {
      xs: '0.75rem',      // 12px
      sm: '0.875rem',     // 14px
      base: '1rem',       // 16px
      lg: '1.125rem',     // 18px
      xl: '1.25rem',      // 20px
      '2xl': '1.5rem',    // 24px
      '3xl': '1.875rem',  // 30px
      '4xl': '2.25rem',   // 36px
      '5xl': '3rem',      // 48px
      '6xl': '3.75rem',   // 60px
      '7xl': '4.5rem',    // 72px
    },
    
    // Font Weights
    fontWeight: {
      light: 300,
      regular: 400,
      medium: 500,
      semibold: 600,
      bold: 700,
      extrabold: 800,
    },
    
    // Line Heights
    lineHeight: {
      tight: 1.2,
      normal: 1.5,
      relaxed: 1.75,
      loose: 2,
    },
  },
  
  spacing: {
    xs: '0.25rem',    // 4px
    sm: '0.5rem',     // 8px
    md: '1rem',       // 16px
    lg: '1.5rem',     // 24px
    xl: '2rem',       // 32px
    '2xl': '3rem',    // 48px
    '3xl': '4rem',    // 64px
    '4xl': '6rem',    // 96px
    '5xl': '8rem',    // 128px
  },
  
  borderRadius: {
    sm: '0.25rem',    // 4px
    md: '0.5rem',     // 8px
    lg: '0.75rem',    // 12px
    xl: '1rem',       // 16px
    '2xl': '1.5rem',  // 24px
    full: '9999px',   // Fully rounded
  },
  
  shadows: {
    sm: '0 1px 2px 0 rgba(0, 0, 0, 0.05)',
    md: '0 4px 6px -1px rgba(0, 0, 0, 0.1), 0 2px 4px -1px rgba(0, 0, 0, 0.06)',
    lg: '0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05)',
    xl: '0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04)',
    '2xl': '0 25px 50px -12px rgba(0, 0, 0, 0.25)',
    card: '0 4px 20px rgba(0, 112, 173, 0.08)',
    cardHover: '0 8px 30px rgba(0, 112, 173, 0.15)',
  },
  
  transitions: {
    fast: '150ms cubic-bezier(0.4, 0, 0.2, 1)',
    base: '300ms cubic-bezier(0.4, 0, 0.2, 1)',
    slow: '500ms cubic-bezier(0.4, 0, 0.2, 1)',
  },
  
  breakpoints: {
    sm: '640px',
    md: '768px',
    lg: '1024px',
    xl: '1280px',
    '2xl': '1536px',
  },
  
  zIndex: {
    base: 0,
    dropdown: 1000,
    sticky: 1020,
    fixed: 1030,
    modalBackdrop: 1040,
    modal: 1050,
    popover: 1060,
    tooltip: 1070,
  },
} as const;

// Type exports for TypeScript
export type Theme = typeof theme;
export type ThemeColors = typeof theme.colors;
export type ThemeTypography = typeof theme.typography;

// Helper function to get responsive value
export const getResponsiveValue = (
  mobile: string | number,
  tablet: string | number,
  desktop: string | number
) => ({
  base: mobile,
  md: tablet,
  lg: desktop,
});

// CSS-in-JS media query helpers
export const mediaQuery = {
  sm: `@media (min-width: ${theme.breakpoints.sm})`,
  md: `@media (min-width: ${theme.breakpoints.md})`,
  lg: `@media (min-width: ${theme.breakpoints.lg})`,
  xl: `@media (min-width: ${theme.breakpoints.xl})`,
  '2xl': `@media (min-width: ${theme.breakpoints['2xl']})`,
};

// Animation keyframes
export const animations = {
  fadeIn: `
    @keyframes fadeIn {
      from {
        opacity: 0;
        transform: translateY(20px);
      }
      to {
        opacity: 1;
        transform: translateY(0);
      }
    }
  `,
  slideInLeft: `
    @keyframes slideInLeft {
      from {
        opacity: 0;
        transform: translateX(-50px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }
  `,
  slideInRight: `
    @keyframes slideInRight {
      from {
        opacity: 0;
        transform: translateX(50px);
      }
      to {
        opacity: 1;
        transform: translateX(0);
      }
    }
  `,
  scaleIn: `
    @keyframes scaleIn {
      from {
        opacity: 0;
        transform: scale(0.9);
      }
      to {
        opacity: 1;
        transform: scale(1);
      }
    }
  `,
  pulse: `
    @keyframes pulse {
      0%, 100% {
        transform: scale(1);
      }
      50% {
        transform: scale(1.05);
      }
    }
  `,
};
