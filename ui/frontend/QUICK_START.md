# ⚡ Quick Start Guide - HCLTech Agentic CoE Landing Page

Get up and running in 5 minutes! 🚀

---

## 🎯 Prerequisites Checklist

Before you begin, ensure you have:

- [ ] **Node.js 18+** installed ([Download](https://nodejs.org/))
- [ ] **npm 9+** or **yarn** package manager
- [ ] **Git** for version control
- [ ] **VS Code** (recommended IDE)
- [ ] Terminal/Command Line access

**Check your versions:**
```bash
node --version   # Should show v18.0.0 or higher
npm --version    # Should show 9.0.0 or higher
git --version    # Should show 2.0.0 or higher
```

---

## 🚀 5-Minute Setup

### Step 1: Navigate to Frontend Directory
```bash
cd /Users/sachidanand/Agentic-CoE/Source-Code/ui/frontend
```

### Step 2: Install Dependencies
```bash
npm install
```

This will install:
- React 18.2
- React Router Dom 6.20
- TypeScript 5.0
- Vite 5.0
- Lucide React (icons)

**Expected time**: 1-2 minutes

### Step 3: Start Development Server
```bash
npm run dev
```

You should see:
```
  VITE v5.0.0  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: http://192.168.1.x:5173/
  ➜  press h to show help
```

### Step 4: Open in Browser
```
http://localhost:5173
```

**🎉 You should now see the HCLTech Agentic CoE landing page!**

---

## 📂 Project Structure (Quick Reference)

```
ui/frontend/
├── src/
│   ├── styles/
│   │   └── theme.ts              # 🎨 Brand colors & design system
│   ├── data/
│   │   └── agents.ts             # 🤖 8 AI agents portfolio
│   ├── components/
│   │   ├── Header.tsx            # 🧭 Navigation bar
│   │   ├── AgentCard.tsx         # 🎴 Agent display cards
│   │   └── MetricBox.tsx         # 📊 Animated statistics
│   ├── pages/
│   │   ├── LandingPage.tsx       # 🏠 Main landing page ⭐
│   │   ├── AgentDetailPage.tsx   # 💬 Agent chat interface
│   │   └── AllAgentsPage.tsx     # 📋 Agent gallery
│   └── App.tsx                   # 🗺️ Routing configuration
└── public/
    └── assets/                   # 🖼️ Images & logos (add here)
```

---

## 🎨 Quick Customization Guide

### Change Brand Colors

**File**: `src/styles/theme.ts`

```typescript
export const theme = {
  colors: {
    primary: '#0070AD',    // ← Change HCLTech blue
    secondary: '#00A3E0',  // ← Change light blue
    accent: '#FF6B35',     // ← Change orange
  },
};
```

### Add a New Agent

**File**: `src/data/agents.ts`

```typescript
export const agents: Agent[] = [
  // ... existing agents
  {
    id: 'my-new-agent',
    name: 'My New Agent',
    description: 'What this agent does...',
    icon: 'Sparkles',      // Lucide icon name
    status: 'live',        // 'live' | 'beta' | 'coming-soon'
    capabilities: ['rag', 'toolUse'],
    category: 'Support',
    popularity: 5,         // 1-5 stars
    features: ['Feature 1', 'Feature 2'],
    useCases: ['Use case 1'],
    metrics: {
      accuracy: '95%',
      responseTime: '1.2s',
      satisfaction: '4.8/5',
    },
    isNew: true,           // Shows NEW badge
  },
];
```

### Change Landing Page Text

**File**: `src/pages/LandingPage.tsx`

Look for these key sections:
- **Line ~90**: Hero headline
- **Line ~110**: Vision statement
- **Line ~220**: Value proposition text
- **Line ~520**: CTA button text

### Add Your Logo

1. Place logo in: `public/assets/hcltech-logo.png`
2. Logo appears automatically in Header component
3. Recommended size: 200x60px (or similar aspect ratio)

---

## 📱 Testing on Mobile

### Option 1: Browser DevTools
1. Open Chrome DevTools (F12)
2. Click device icon (Ctrl+Shift+M)
3. Select iPhone/Android device
4. Test responsive breakpoints

### Option 2: Network URL
```bash
# When dev server is running, look for:
➜  Network: http://192.168.1.x:5173/

# Open this URL on your phone (same WiFi)
```

---

## 🐛 Common Issues & Fixes

### Issue 1: Port Already in Use

**Error**: `Port 5173 is already in use`

**Fix**:
```bash
# Kill process on port
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

### Issue 2: Dependencies Won't Install

**Error**: `npm install` fails

**Fix**:
```bash
# Clear cache and reinstall
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Issue 3: TypeScript Errors

**Error**: "Cannot find module 'react'"

**Fix**:
```bash
# Install missing types
npm install --save-dev @types/react @types/react-dom @types/node
```

### Issue 4: Blank Page

**Check**:
1. Console for errors (F12)
2. Verify all files created correctly
3. Check if dev server is running
4. Try hard refresh (Ctrl+Shift+R)

### Issue 5: Images Not Loading

**Fix**:
1. Ensure images are in `/public/assets/`
2. Use paths starting with `/assets/`
3. Check filename matches exactly
4. Clear browser cache

---

## 🔍 Quick Navigation

### Key Routes

| URL | Page | Description |
|-----|------|-------------|
| `/` | Landing Page | Main entry point |
| `/agents` | All Agents | Gallery with filters |
| `/agents/customer-support` | Agent Detail | Chat interface |

### Navigation Flow
```
Landing Page (/)
  ↓ Click "Explore Agents"
  ↓
Agent Gallery (/agents)
  ↓ Click Agent Card
  ↓
Agent Detail (/agents/:id)
  ↓ Chat with agent
```

---

## 🎯 Key Features to Test

### Landing Page Checklist
- [ ] Hero section loads with gradient
- [ ] "Explore Agents" button scrolls to agents section
- [ ] All 6 agent cards display correctly
- [ ] Hover effects work on cards
- [ ] Click agent card → navigates to detail page
- [ ] Metrics animate when scrolled into view
- [ ] "View All Agents" button works
- [ ] Footer links are present
- [ ] Mobile hamburger menu works

### Agent Detail Page Checklist
- [ ] Agent info loads correctly
- [ ] Chat interface displays
- [ ] Can type message
- [ ] Send button works
- [ ] Agent responds (demo mode)
- [ ] Sidebar shows capabilities
- [ ] Back button returns to home
- [ ] "Coming Soon" agents show disabled state

### All Agents Page Checklist
- [ ] All 8 agents display
- [ ] Search filters agents by name
- [ ] Category filter works
- [ ] Status filter works
- [ ] Results count updates
- [ ] Empty state shows when no results
- [ ] Click card → navigates to detail

---

## 📊 Development Commands

```bash
# Start development server (with HMR)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview

# Run linter
npm run lint

# Type check
npm run type-check

# Install new package
npm install <package-name>

# Update dependencies
npm update
```

---

## 🎨 Customization Examples

### Example 1: Change Hero Gradient

**File**: `src/styles/theme.ts`

```typescript
colors: {
  gradientHero: 'linear-gradient(135deg, #YOUR_COLOR_1 0%, #YOUR_COLOR_2 100%)',
}
```

### Example 2: Add New Metric

**File**: `src/pages/LandingPage.tsx` (Statistics Section)

```typescript
<MetricBox 
  icon={<YourIcon size={32} />} 
  value="100+" 
  label="Your New Metric" 
/>
```

### Example 3: Change Button Style

**File**: Any component with button

```typescript
<button
  style={{
    backgroundColor: theme.colors.YOUR_COLOR,
    // ... other styles
  }}
>
  Your Text
</button>
```

---

## 🚀 Next Steps

### After Initial Setup

1. **Replace Placeholder Assets**
   - Add HCLTech logo to `/public/assets/`
   - Add Microsoft partnership badge
   - Add technology logos (Azure, OpenAI, etc.)

2. **Customize Content**
   - Update agent descriptions
   - Change statistics/metrics
   - Update footer links
   - Modify hero text

3. **Configure API**
   - Replace demo chat with real backend
   - Connect to agent orchestration service
   - Add authentication if needed

4. **Add Analytics**
   - Google Analytics
   - Microsoft Clarity
   - Track button clicks

### Pre-Production Checklist

- [ ] All placeholder images replaced
- [ ] API endpoints configured
- [ ] Analytics tracking added
- [ ] SEO meta tags updated
- [ ] Tested on all browsers
- [ ] Mobile responsiveness verified
- [ ] Accessibility audit passed
- [ ] Performance optimized (Lighthouse > 90)

---

## 📚 Documentation Reference

For more details, see:

- **[LANDING_PAGE_README.md](./LANDING_PAGE_README.md)** - Component documentation
- **[DEPLOYMENT_GUIDE.md](./DEPLOYMENT_GUIDE.md)** - Deployment instructions
- **[IMPLEMENTATION_SUMMARY.md](./IMPLEMENTATION_SUMMARY.md)** - Complete overview
- **[COMPONENT_SHOWCASE.md](./COMPONENT_SHOWCASE.md)** - Visual reference

---

## 💡 Pro Tips

### Tip 1: Use VS Code Extensions
```
- ESLint (code quality)
- Prettier (formatting)
- Error Lens (inline errors)
- Auto Rename Tag
- Path Intellisense
```

### Tip 2: Keyboard Shortcuts
```
Ctrl+Shift+R - Hard refresh (clear cache)
Ctrl+Shift+C - Inspect element
F12          - Open DevTools
Ctrl+K, Ctrl+F - Format document (VS Code)
```

### Tip 3: Hot Module Replacement (HMR)
- Changes reflect instantly (no page reload)
- CSS updates immediately
- React components preserve state
- Fast development iteration

### Tip 4: Component Testing
- Test each component in isolation
- Use React DevTools to inspect props
- Check console for errors
- Test on different screen sizes

---

## 🆘 Getting Help

### Error Messages

If you see an error:
1. **Read the error message** - Usually tells you what's wrong
2. **Check the file and line number** - Navigate to exact location
3. **Look for typos** - Common cause of errors
4. **Check imports** - Ensure all imports are correct
5. **Restart dev server** - Sometimes fixes issues

### Resources

- **React Docs**: https://react.dev
- **TypeScript Docs**: https://www.typescriptlang.org/docs
- **Vite Docs**: https://vitejs.dev
- **Lucide Icons**: https://lucide.dev

### Support Channels

- **Technical Issues**: Check documentation files
- **HCLTech Brand**: Contact brand team
- **Azure Deployment**: Azure support portal

---

## ✅ Success Checklist

Before considering setup complete:

- [ ] Dev server starts without errors
- [ ] Landing page loads in browser
- [ ] Can navigate between pages
- [ ] Hover effects work
- [ ] Mobile menu functions
- [ ] Agent cards display correctly
- [ ] Chat interface loads
- [ ] No console errors
- [ ] Responsive on mobile
- [ ] All routes accessible

---

## 🎉 You're Ready!

If all checks pass, you're ready to start customizing and building!

**Happy coding! 🚀**

---

**Quick Reference Card**

```bash
# Development
cd ui/frontend
npm install
npm run dev          → http://localhost:5173

# Files to Customize
theme.ts             → Colors & design
agents.ts            → Agent data
LandingPage.tsx      → Main page content
/public/assets/      → Add logos here

# Key Components
Header               → Navigation
AgentCard            → Agent display
LandingPage          → Main page (7 sections)

# Testing
Browser DevTools     → F12
Mobile Testing       → Ctrl+Shift+M
Network URL          → Test on phone
```

**🎯 Need to make changes? Start with these files:**
1. `theme.ts` - Change colors
2. `agents.ts` - Add/edit agents
3. `LandingPage.tsx` - Modify content
4. `/public/assets/` - Add images

---

**Documentation Status: ✅ Complete**
**Code Status: ✅ Ready for Development**
**Next Step: Run `npm install && npm run dev` 🚀**
