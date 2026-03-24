# HCLTech Agentic CoE Landing Page

## Overview

Professional, enterprise-grade landing page for HCLTech's Agentic Center of Excellence (CoE). Built with React, TypeScript, and modern UI/UX best practices.

## Features

### 🎨 Design System
- **HCLTech Brand Colors**:
  - Primary: #0070AD (HCLTech Blue)
  - Secondary: #00A3E0 (Light Blue)
  - Accent: #FF6B35 (Vibrant Orange)
- **Typography**: Montserrat (headings) + Open Sans (body text)
- **Responsive Design**: Mobile-first approach with 5 breakpoints
- **Smooth Animations**: Fade-in, slide, scale, and hover effects
- **Accessibility**: WCAG 2.1 AA compliant

### 📄 Page Sections

1. **Hero Section**
   - Gradient background with animated pattern
   - Clear value proposition
   - Dual CTA buttons (Explore Agents, View Documentation)
   - "Powered by Microsoft Agent Framework" badge

2. **Value Proposition**
   - 3-column grid highlighting key benefits:
     - Rapid Development (70% time savings)
     - Production Ready (enterprise-grade security)
     - Multi-Agent Orchestration

3. **AI Agents Gallery**
   - 6 popular agents displayed
   - Interactive cards with hover effects
   - "View All Agents" navigation

4. **Technology Stack**
   - Microsoft Azure
   - Agent Framework
   - Azure OpenAI
   - FastAPI
   - PostgreSQL

5. **Statistics/Metrics**
   - Animated counters (IntersectionObserver)
   - Key achievements:
     - 15+ Production Agents
     - 5000+ Monthly Active Users
     - 70% Development Time Saved
     - 99.9% Uptime SLA

6. **Call-to-Action**
   - Gradient overlay background
   - "Request a Demo" primary CTA
   - "Learn More" secondary CTA

7. **Footer**
   - Resources links
   - Company links
   - Microsoft Partner badge

## Components

### Header.tsx
- Sticky navigation bar
- HCLTech logo
- Navigation menu with dropdowns
- Mobile hamburger menu
- "Request Demo" CTA button
- Scroll shadow effect

### AgentCard.tsx
- Agent icon and metadata
- NEW badge for recent agents
- Status indicator (Live/Beta/Coming Soon)
- Capabilities badges
- Popularity stars (1-5)
- Hover lift animation
- "Try Agent" navigation button

### MetricBox.tsx
- Animated counter component
- IntersectionObserver triggers animation when visible
- Optional icon support
- Hover effects
- Responsive design

## Routes

| Route | Component | Description |
|-------|-----------|-------------|
| `/` | LandingPage | Main landing page |
| `/agents` | AllAgentsPage | Full agent gallery with filters |
| `/agents/:agentId` | AgentDetailPage | Individual agent detail & chat |
| `/dashboard` | Dashboard | Admin dashboard (with Layout) |
| `/admin/agents` | AgentList | Agent management (with Layout) |

## Data Structure

### Agent Interface
```typescript
interface Agent {
  id: string;
  name: string;
  description: string;
  icon: string; // Lucide icon name
  status: 'live' | 'beta' | 'coming-soon';
  capabilities: string[];
  category: string;
  popularity: number; // 1-5 stars
  features: string[];
  useCases: string[];
  metrics: {
    accuracy: string;
    responseTime: string;
    satisfaction: string;
  };
  isNew?: boolean;
}
```

## Styling Approach

- **Inline Styles**: Used for maximum control and theme integration
- **No CSS Classes**: Direct theme variable usage
- **Hover States**: Interactive feedback on all clickable elements
- **Responsive Grid**: CSS Grid with `auto-fit` and `minmax`
- **Performance**: Hardware-accelerated transforms (`translateY`, `scale`)

## Assets Required

Place the following assets in `/ui/frontend/public/assets/`:

1. **hcltech-logo.png** - HCLTech corporate logo
2. **hcltech-logo-white.png** - White version for dark backgrounds
3. **microsoft-partner-badge.png** - Microsoft partnership badge
4. **azure-logo.svg** - Microsoft Azure logo
5. **openai-logo.svg** - OpenAI logo
6. **agent-framework-icon.svg** - Microsoft Agent Framework icon

## Browser Support

- Chrome/Edge 90+
- Firefox 88+
- Safari 14+
- Mobile browsers (iOS 14+, Android 10+)

## Performance

- **Lighthouse Score Target**: 90+ on all metrics
- **Core Web Vitals**:
  - LCP < 2.5s
  - FID < 100ms
  - CLS < 0.1
- **Optimization Techniques**:
  - Lazy loading for images
  - IntersectionObserver for animations
  - Code splitting by route
  - Debounced search input

## Accessibility Features

- Semantic HTML5 elements
- ARIA labels on interactive elements
- Keyboard navigation support
- Focus indicators
- Alt text for images
- Color contrast ratios > 4.5:1

## Development

```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

## Deployment Checklist

- [ ] Replace placeholder images with actual assets
- [ ] Update HCLTech logo paths in Header.tsx
- [ ] Configure actual API endpoints for agent chat
- [ ] Set up analytics tracking
- [ ] Add meta tags for SEO
- [ ] Configure CDN for assets
- [ ] Enable compression (gzip/brotli)
- [ ] Set up error tracking (Sentry, etc.)
- [ ] Test on all target browsers
- [ ] Run Lighthouse audit
- [ ] Validate accessibility with screen reader

## Customization

### Changing Brand Colors

Edit [theme.ts](./src/styles/theme.ts):

```typescript
export const theme = {
  colors: {
    primary: '#0070AD', // Your primary brand color
    secondary: '#00A3E0', // Your secondary brand color
    accent: '#FF6B35', // Your accent color
    // ...
  },
};
```

### Adding New Agents

Edit [agents.ts](./src/data/agents.ts):

```typescript
export const agents: Agent[] = [
  {
    id: 'new-agent',
    name: 'New Agent',
    description: 'Agent description',
    // ... full configuration
  },
];
```

### Modifying Section Order

Edit [LandingPage.tsx](./src/pages/LandingPage.tsx) and reorder the `<section>` elements.

## Tech Stack

- **React 18.2** - UI framework
- **TypeScript 5.0** - Type safety
- **Vite 5.0** - Build tool
- **React Router 6.20** - Client-side routing
- **Lucide React** - Icon library

## License

Proprietary - HCLTech © 2024

## Contact

For questions or support, contact the HCLTech Agentic CoE team.
