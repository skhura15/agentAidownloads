# 🎨 Component Showcase

Visual reference for all landing page components and their states.

---

## 🎯 Color Palette

### Primary Colors
```
HCLTech Blue (Primary)
#0070AD
██████████

Light Blue (Secondary)  
#00A3E0
██████████

Vibrant Orange (Accent)
#FF6B35
██████████
```

### Semantic Colors
```
Success: #28A745  ██████████
Warning: #FFC107  ██████████
Error:   #DC3545  ██████████
Info:    #17A2B8  ██████████
```

### Neutrals
```
Dark:      #212529  ██████████
Dark Light:#495057  ██████████
Gray:      #ADB5BD  ██████████
Light:     #F8F9FA  ██████████
White:     #FFFFFF  ██████████
```

---

## 📐 Typography Scale

```
6xl:  3.75rem (60px) - Hero Headlines
5xl:  3rem    (48px) - Page Titles
4xl:  2.25rem (36px) - Section Headers
3xl:  1.875rem(30px) - Subsections
2xl:  1.5rem  (24px) - Card Titles
xl:   1.25rem (20px) - Large Body
lg:   1.125rem(18px) - Body Large
base: 1rem    (16px) - Body Text
sm:   0.875rem(14px) - Small Text
xs:   0.75rem (12px) - Captions
```

---

## 🏗️ Component States

### AgentCard Component

#### Default State
```
┌─────────────────────────────┐
│  🤖  [Icon]                │
│                             │
│  Customer Support Agent     │
│  ⭐⭐⭐⭐⭐ (5 stars)      │
│                             │
│  Intelligent AI agent...    │
│                             │
│  [RAG] [Tool Use] [Stream] │
│                             │
│        [Try Agent →]        │
└─────────────────────────────┘
Shadow: md (hover: xl)
```

#### Hover State
```
┌─────────────────────────────┐  ↑ -8px
│  🤖  [Icon]                │
│                             │
│  Customer Support Agent     │
│  ⭐⭐⭐⭐⭐              │
│                             │
│  Description text...        │
│                             │
│  [Capability badges]        │
│                             │
│    [Try Agent → (hover)]    │
└─────────────────────────────┘
Shadow: xl (enhanced)
Transform: translateY(-8px)
```

#### Status Indicators
```
LIVE:         ● Green  #28A745
BETA:         ● Yellow #FFC107  
COMING SOON:  ● Blue   #17A2B8
```

#### NEW Badge
```
┌─────────┐
│ ✨ NEW │  Orange background
└─────────┘  White text
```

---

### MetricBox Component

#### Default State
```
┌──────────────┐
│   🚀 Icon   │
│              │
│     15+      │  Large (3xl)
│              │
│ Production   │  Small (sm)
│   Agents     │
└──────────────┘
```

#### Animation Sequence
```
Frame 1:   0   (when not visible)
Frame 30:  7   (halfway through)
Frame 60:  15+ (animation complete)

Duration: 2 seconds
Trigger: IntersectionObserver (50% threshold)
```

#### Hover State
```
┌──────────────┐  ↑ -4px
│   🚀 Icon   │
│              │
│     15+      │
│              │
│ Production   │
│   Agents     │
└──────────────┘
Transform: translateY(-4px)
```

---

### Header Component

#### Desktop View (> 768px)
```
┌─────────────────────────────────────────────────────────────┐
│ [HCLTech Logo]  Home  AI Agents ▼  Docs  About  [Request Demo]│
└─────────────────────────────────────────────────────────────┘
Height: 80px
Position: Sticky
Shadow: appears on scroll
```

#### Mobile View (< 768px)
```
┌───────────────────────────────────┐
│ [HCLTech Logo]         [☰ Menu] │
└───────────────────────────────────┘

Mobile Menu (when open):
┌───────────────────────────────────┐
│ Home                              │
│ AI Agents                         │
│ Documentation                     │
│ About                             │
│ ─────────────────────────────────│
│ [Request Demo (full width)]      │
└───────────────────────────────────┘
```

#### Dropdown Submenu
```
AI Agents ▼
├─ All Agents
├─ By Category
└─ New Releases
```

---

## 📱 Responsive Grid Layouts

### Agent Cards Grid
```
Mobile (< 640px):      1 column
Tablet (640-1024px):   2 columns
Desktop (> 1024px):    3 columns

Grid: repeat(auto-fill, minmax(320px, 1fr))
Gap: 2rem
```

### Value Proposition Grid
```
Mobile (< 768px):      1 column (stacked)
Desktop (> 768px):     3 columns (side-by-side)

Grid: repeat(auto-fit, minmax(300px, 1fr))
Gap: 2rem
```

### Metrics Grid
```
Mobile (< 640px):      1 column
Tablet (640-1024px):   2 columns
Desktop (> 1024px):    4 columns

Grid: repeat(auto-fit, minmax(240px, 1fr))
Gap: 2rem
```

---

## 🎬 Animation Keyframes

### @keyframes fadeIn
```
0%:   opacity: 0
100%: opacity: 1

Duration: 0.5s
Easing: ease-in
```

### @keyframes slideInLeft
```
0%:   transform: translateX(-50px), opacity: 0
100%: transform: translateX(0), opacity: 1

Duration: 0.6s
Easing: ease-out
```

### @keyframes slideInRight
```
0%:   transform: translateX(50px), opacity: 0
100%: transform: translateX(0), opacity: 1

Duration: 0.6s
Easing: ease-out
```

### @keyframes scaleIn
```
0%:   transform: scale(0.9), opacity: 0
100%: transform: scale(1), opacity: 1

Duration: 0.5s
Easing: ease-out
```

### @keyframes pulse
```
0%, 100%: opacity: 1
50%:      opacity: 0.5

Duration: 2s
Iteration: infinite
```

---

## 🎨 Section Layouts

### Hero Section
```
┌────────────────────────────────────────────────┐
│              [Gradient Background]             │
│         [Animated Pattern Overlay]            │
│                                                │
│     [✨ Powered by Microsoft Badge]          │
│                                                │
│         HCLTech Agentic CoE                   │
│    Accelerating Enterprise AI Agent           │
│              Development                       │
│                                                │
│   Empowering organizations to build...        │
│                                                │
│   [Explore Agents]  [View Documentation]      │
│                                                │
└────────────────────────────────────────────────┘
Padding: 6rem vertical
Max-width: 900px (centered)
```

### Value Proposition Section
```
┌────────────────────────────────────────────────┐
│    Why HCLTech Agentic CoE?                   │
│    Accelerate your AI journey...              │
│                                                │
│  ┌───────┐    ┌───────┐    ┌───────┐        │
│  │ ⚡    │    │ 🛡️   │    │ 🔗    │        │
│  │Rapid  │    │Prod   │    │Multi- │        │
│  │Dev    │    │Ready  │    │Agent  │        │
│  └───────┘    └───────┘    └───────┘        │
└────────────────────────────────────────────────┘
Background: Light gray (#F8F9FA)
Padding: 6rem vertical
```

### Agents Gallery Section
```
┌────────────────────────────────────────────────┐
│         AI Agent Portfolio                     │
│    Explore our suite of specialized...        │
│                                                │
│  ┌─────┐  ┌─────┐  ┌─────┐  ┌─────┐        │
│  │Agent│  │Agent│  │Agent│  │Agent│        │
│  │ 1   │  │ 2   │  │ 3   │  │ 4   │        │
│  └─────┘  └─────┘  └─────┘  └─────┘        │
│  ┌─────┐  ┌─────┐                           │
│  │Agent│  │Agent│                           │
│  │ 5   │  │ 6   │                           │
│  └─────┘  └─────┘                           │
│                                                │
│         [View All Agents →]                   │
└────────────────────────────────────────────────┘
Background: White
Grid: 3 columns (desktop)
```

### CTA Section
```
┌────────────────────────────────────────────────┐
│         [Blue Gradient Background]            │
│                                                │
│    Ready to Transform Your Enterprise?        │
│                                                │
│  Join leading organizations who are           │
│  accelerating their AI journey...             │
│                                                │
│   [Request a Demo]    [Learn More]           │
│                                                │
└────────────────────────────────────────────────┘
Background: Linear gradient (primary to secondary)
Text: White
Padding: 6rem vertical
```

---

## 🔧 Interactive States

### Button States

#### Primary Button (Accent)
```
Default:    bg: #FF6B35, text: white
Hover:      bg: darker, translateY(-2px), shadow enhanced
Active:     bg: darkest, translateY(0)
Disabled:   bg: gray, cursor: not-allowed, opacity: 0.5
```

#### Secondary Button (Glass)
```
Default:    bg: rgba(255,255,255,0.15), border: white
Hover:      bg: rgba(255,255,255,0.25), translateY(-2px)
Active:     bg: rgba(255,255,255,0.35)
```

### Link States
```
Default:    color: primary (#0070AD)
Hover:      color: primaryDark, underline
Active:     color: primaryDark
Visited:    color: primaryDark (dimmed)
Focus:      outline: 2px primary
```

### Input States
```
Default:    border: 1px gray
Focus:      border: 2px primary, outline: none
Error:      border: 2px error (#DC3545)
Disabled:   bg: light gray, cursor: not-allowed
```

---

## 📏 Spacing System

```
xs:   0.25rem  (4px)   - Tight spacing
sm:   0.5rem   (8px)   - Small gaps
md:   1rem     (16px)  - Default spacing
lg:   1.5rem   (24px)  - Section spacing
xl:   2rem     (32px)  - Large sections
2xl:  3rem     (48px)  - Major sections
3xl:  4rem     (64px)  - Hero padding
4xl:  5rem     (80px)  - Page sections
5xl:  6rem     (96px)  - Major divisions
6xl:  8rem     (128px) - Largest spacing
```

---

## 🌗 Shadow System

```
sm:   0 1px 2px rgba(0,0,0,0.05)
md:   0 4px 6px rgba(0,0,0,0.1)
lg:   0 10px 15px rgba(0,0,0,0.1)
xl:   0 20px 25px rgba(0,0,0,0.15)
2xl:  0 25px 50px rgba(0,0,0,0.25)
inner:inset 0 2px 4px rgba(0,0,0,0.06)

Card:      0 4px 8px rgba(0,0,0,0.08)
CardHover: 0 12px 24px rgba(0,0,0,0.15)
```

---

## 🎯 Z-Index Layers

```
dropdown:  1000
sticky:    1020
overlay:   1030
modal:     1040
popover:   1050
tooltip:   1060
notification: 1070
```

---

## 📐 Border Radius

```
none: 0
sm:   0.125rem (2px)
md:   0.375rem (6px)
lg:   0.5rem   (8px)
xl:   0.75rem  (12px)
2xl:  1rem     (16px)
3xl:  1.5rem   (24px)
full: 9999px   (pill shape)
```

---

## 🚦 Component Usage Examples

### Creating a New Agent

```typescript
// 1. Add to agents.ts
{
  id: 'new-agent-id',
  name: 'New Agent Name',
  description: 'Agent description...',
  icon: 'Sparkles', // Lucide icon name
  status: 'live',
  capabilities: ['rag', 'toolUse'],
  category: 'Support',
  popularity: 4,
  features: ['Feature 1', 'Feature 2'],
  useCases: ['Use case 1', 'Use case 2'],
  metrics: {
    accuracy: '95%',
    responseTime: '1.2s',
    satisfaction: '4.8/5',
  },
  isNew: true,
}
```

### Using Theme Values

```typescript
// In any component
import { theme } from '../styles/theme';

<div style={{
  color: theme.colors.primary,
  fontSize: theme.typography.fontSize.lg,
  padding: theme.spacing.lg,
  borderRadius: theme.borderRadius.xl,
  boxShadow: theme.shadows.md,
}}>
  Content
</div>
```

### Adding a New Section

```typescript
<section
  id="new-section"
  style={{
    padding: '6rem 1.5rem',
    backgroundColor: theme.colors.white,
  }}
>
  <div style={{ maxWidth: '1280px', margin: '0 auto' }}>
    {/* Section content */}
  </div>
</section>
```

---

## 🎨 Visual Design Principles

### Hierarchy
1. **Large Bold Text**: Main headings (6xl, bold)
2. **Medium Text**: Section headers (4xl, semibold)
3. **Regular Text**: Body content (base, regular)
4. **Small Text**: Meta info (sm, medium)

### Contrast
- **High Contrast**: Headlines on backgrounds (white on gradient)
- **Medium Contrast**: Body text on white (dark on white)
- **Low Contrast**: Disabled states (gray on light gray)

### Spacing
- **Tight**: Within elements (badges, buttons)
- **Normal**: Between related items (card content)
- **Loose**: Between sections (major divisions)

### Colors
- **Primary Actions**: Accent orange (#FF6B35)
- **Secondary Actions**: Primary blue (#0070AD)
- **Tertiary Actions**: Glass effect with border
- **Status**: Semantic colors (success, warning, etc.)

---

## 📱 Mobile Optimization

### Breakpoint Strategy
```
Mobile First: Base styles for mobile
sm (640px):   Tablet adjustments
md (768px):   Desktop layout begins
lg (1024px):  Full desktop experience
xl+ (1280px): Enhanced spacing
```

### Mobile Specific
- Hamburger menu instead of nav bar
- Single column layouts
- Larger touch targets (min 44x44px)
- Simplified animations
- Reduced padding on small screens

---

## ✨ Brand Guidelines

### Logo Usage
- **Minimum Size**: 120px wide
- **Clear Space**: 20px on all sides
- **Background**: White or light backgrounds
- **Alt Version**: White logo for dark backgrounds

### Typography Rules
- **Headings**: Always Montserrat
- **Body**: Always Open Sans
- **Minimum Size**: 14px for body text
- **Line Height**: 1.6 for body, 1.2 for headings

### Color Rules
- **Primary CTA**: Always accent orange
- **Links**: Primary blue
- **Hover**: Always darken by 10%
- **Contrast**: Minimum 4.5:1 for text

---

**This showcase provides visual and technical reference for implementing and extending the HCLTech Agentic CoE landing page components.** 🎨
