# 🚀 HCLTech Agentic CoE Landing Page - Deployment Guide

## 📋 Table of Contents

1. [Quick Start](#quick-start)
2. [Prerequisites](#prerequisites)
3. [Installation](#installation)
4. [Development](#development)
5. [Production Build](#production-build)
6. [Deployment](#deployment)
7. [Configuration](#configuration)
8. [Troubleshooting](#troubleshooting)

---

## 🎯 Quick Start

```bash
# Navigate to frontend directory
cd ui/frontend

# Install dependencies
npm install

# Start development server
npm run dev

# Open browser to http://localhost:5173
```

---

## ✅ Prerequisites

### Required Software
- **Node.js**: v18.0.0 or higher
- **npm**: v9.0.0 or higher (or yarn/pnpm)
- **Git**: v2.0.0 or higher

### Recommended IDE Setup
- **VS Code** with extensions:
  - ESLint
  - Prettier
  - Volar (Vue Language Features)
  - TypeScript Vue Plugin (Volar)

---

## 📦 Installation

### 1. Install Dependencies

```bash
cd ui/frontend
npm install
```

### 2. Verify Installation

```bash
# Check if all packages installed correctly
npm list --depth=0

# Expected packages:
# ├── react@18.2.0
# ├── react-dom@18.2.0
# ├── react-router-dom@6.20.0
# ├── lucide-react@latest
# ├── typescript@5.0.0
# └── vite@5.0.0
```

### 3. Add Brand Assets

Place required assets in `/ui/frontend/public/assets/`:
- `hcltech-logo.png` - HCLTech logo
- `microsoft-partner-badge.png` - Partnership badge
- Technology logos (Azure, OpenAI, etc.)

See [assets/README.md](./public/assets/README.md) for complete list.

---

## 💻 Development

### Start Development Server

```bash
npm run dev
```

- Opens at `http://localhost:5173`
- Hot Module Replacement (HMR) enabled
- Auto-opens browser
- Displays network URL for testing on mobile devices

### Available Scripts

| Command | Description |
|---------|-------------|
| `npm run dev` | Start development server with HMR |
| `npm run build` | Build production bundle |
| `npm run preview` | Preview production build locally |
| `npm run lint` | Run ESLint for code quality |
| `npm run type-check` | Run TypeScript compiler check |

### Development Workflow

1. **Make Changes**: Edit files in `/src`
2. **Hot Reload**: Changes reflect instantly in browser
3. **Test**: Test on different screen sizes (use browser DevTools)
4. **Commit**: Commit working changes to Git

### Environment Variables

Create `.env.local` file for development overrides:

```bash
# API Endpoints
VITE_API_BASE_URL=http://localhost:8000
VITE_AGENT_API_URL=http://localhost:8001

# Feature Flags
VITE_ENABLE_ANALYTICS=false
VITE_ENABLE_ERROR_TRACKING=false

# Branding
VITE_APP_NAME="HCLTech Agentic CoE"
```

---

## 🏗️ Production Build

### 1. Create Production Build

```bash
npm run build
```

Output directory: `/ui/frontend/dist/`

### 2. Verify Build

```bash
# Preview production build locally
npm run preview

# Opens at http://localhost:4173
```

### 3. Build Optimizations

The production build includes:
- ✅ Minification (HTML, CSS, JS)
- ✅ Tree shaking (removes unused code)
- ✅ Code splitting (route-based)
- ✅ Asset optimization (images, fonts)
- ✅ Gzip compression
- ✅ Source maps generation

### Build Output

```
dist/
├── assets/
│   ├── index-[hash].js       # Main bundle
│   ├── vendor-[hash].js      # Third-party libraries
│   ├── LandingPage-[hash].js # Landing page chunk
│   └── [component]-[hash].js # Other route chunks
├── index.html                # Entry point
└── assets/                   # Static assets
```

---

## 🌐 Deployment

### Option 1: Azure Static Web Apps (Recommended)

```bash
# Install Azure CLI
brew install azure-cli  # macOS
# or download from https://aka.ms/installazurecliwindows

# Login to Azure
az login

# Create Static Web App
az staticwebapp create \
  --name hcltech-agentic-coe \
  --resource-group agentic-coe-rg \
  --source . \
  --location "West US 2" \
  --branch main \
  --app-location "/ui/frontend" \
  --output-location "dist"
```

#### Azure Static Web Apps Configuration

Create `staticwebapp.config.json`:

```json
{
  "routes": [
    {
      "route": "/assets/*",
      "headers": {
        "cache-control": "public, max-age=31536000, immutable"
      }
    },
    {
      "route": "/*",
      "serve": "/index.html",
      "statusCode": 200
    }
  ],
  "navigationFallback": {
    "rewrite": "/index.html",
    "exclude": ["/assets/*"]
  },
  "globalHeaders": {
    "content-security-policy": "default-src 'self' 'unsafe-inline' https:; img-src 'self' data: https:;"
  }
}
```

### Option 2: Vercel

```bash
# Install Vercel CLI
npm install -g vercel

# Deploy
cd ui/frontend
vercel

# Production deployment
vercel --prod
```

### Option 3: Netlify

```bash
# Install Netlify CLI
npm install -g netlify-cli

# Deploy
cd ui/frontend
netlify deploy

# Production deployment
netlify deploy --prod
```

Create `netlify.toml`:

```toml
[build]
  command = "npm run build"
  publish = "dist"

[[redirects]]
  from = "/*"
  to = "/index.html"
  status = 200

[[headers]]
  for = "/assets/*"
  [headers.values]
    Cache-Control = "public, max-age=31536000, immutable"
```

### Option 4: Docker Container

```dockerfile
# Dockerfile
FROM node:18-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

```nginx
# nginx.conf
server {
  listen 80;
  server_name _;
  root /usr/share/nginx/html;
  index index.html;

  # Gzip compression
  gzip on;
  gzip_types text/plain text/css application/json application/javascript text/xml application/xml application/xml+rss text/javascript;

  # Cache static assets
  location /assets/ {
    expires 1y;
    add_header Cache-Control "public, immutable";
  }

  # SPA routing
  location / {
    try_files $uri $uri/ /index.html;
  }
}
```

Build and run:

```bash
docker build -t hcltech-agentic-coe:latest .
docker run -p 8080:80 hcltech-agentic-coe:latest
```

---

## ⚙️ Configuration

### Update API Endpoints

Edit [App.tsx](./src/App.tsx) or create API configuration file:

```typescript
// src/config/api.ts
export const API_CONFIG = {
  baseUrl: import.meta.env.VITE_API_BASE_URL || 'https://api.hcltech.com',
  endpoints: {
    agents: '/api/agents',
    chat: '/api/chat',
    analytics: '/api/analytics',
  },
};
```

### Customize Branding

Edit [theme.ts](./src/styles/theme.ts):

```typescript
export const theme = {
  colors: {
    primary: '#0070AD',      // Your primary brand color
    secondary: '#00A3E0',    // Your secondary brand color
    accent: '#FF6B35',       // Your accent color
  },
  typography: {
    fontHeading: 'Montserrat, sans-serif',
    fontBody: 'Open Sans, sans-serif',
  },
};
```

### Add Analytics

```typescript
// src/utils/analytics.ts
export const initAnalytics = () => {
  if (import.meta.env.PROD) {
    // Google Analytics
    window.gtag('config', 'GA_MEASUREMENT_ID');
    
    // Microsoft Clarity
    window.clarity('init', 'CLARITY_PROJECT_ID');
  }
};
```

Call in [main.tsx](./src/main.tsx):

```typescript
import { initAnalytics } from './utils/analytics';

initAnalytics();
```

### Configure SEO

Update [index.html](./index.html):

```html
<head>
  <title>HCLTech Agentic CoE | Enterprise AI Agent Development</title>
  <meta name="description" content="Accelerate your AI journey with HCLTech's Agentic Center of Excellence. Build production-ready multi-agent AI solutions at scale.">
  <meta name="keywords" content="AI, Agentic, HCLTech, Microsoft, Azure, OpenAI, Agent Framework">
  
  <!-- Open Graph -->
  <meta property="og:title" content="HCLTech Agentic CoE">
  <meta property="og:description" content="Enterprise AI Agent Development Platform">
  <meta property="og:image" content="/assets/og-image.jpg">
  <meta property="og:url" content="https://agentic-coe.hcltech.com">
  
  <!-- Twitter Card -->
  <meta name="twitter:card" content="summary_large_image">
  <meta name="twitter:title" content="HCLTech Agentic CoE">
  <meta name="twitter:description" content="Enterprise AI Agent Development Platform">
  <meta name="twitter:image" content="/assets/twitter-card.jpg">
</head>
```

---

## 🐛 Troubleshooting

### Issue: Dependencies Not Installing

**Solution:**
```bash
# Clear npm cache
npm cache clean --force

# Delete node_modules and package-lock.json
rm -rf node_modules package-lock.json

# Reinstall
npm install
```

### Issue: Port Already in Use

**Solution:**
```bash
# Kill process on port 5173
lsof -ti:5173 | xargs kill -9

# Or use different port
npm run dev -- --port 3000
```

### Issue: TypeScript Errors

**Solution:**
```bash
# Run type check
npm run type-check

# Install missing types
npm install --save-dev @types/react @types/react-dom @types/node
```

### Issue: Build Fails

**Solution:**
```bash
# Check for syntax errors
npm run lint

# Clean build directory
rm -rf dist

# Rebuild
npm run build
```

### Issue: Assets Not Loading

**Solution:**
1. Check asset paths (must start with `/assets/`)
2. Verify files exist in `/public/assets/`
3. Check browser console for 404 errors
4. Clear browser cache (Cmd+Shift+R / Ctrl+Shift+R)

### Issue: Routes Not Working After Deployment

**Solution:**
Configure server for SPA routing (see deployment sections above). Ensure all routes redirect to `/index.html`.

---

## 📊 Performance Optimization

### 1. Analyze Bundle Size

```bash
npm run build -- --mode=analyze
```

### 2. Optimize Images

```bash
# Install image optimization tool
npm install -g imagemin-cli

# Optimize all images
imagemin public/assets/*.{png,jpg} --out-dir=public/assets
```

### 3. Enable CDN

Update Vite config for CDN:

```typescript
// vite.config.ts
export default defineConfig({
  build: {
    assetsInlineLimit: 0, // Don't inline assets
    rollupOptions: {
      output: {
        assetFileNames: 'assets/[name]-[hash][extname]',
      },
    },
  },
});
```

Then upload `/dist/assets/` to CDN and update paths.

---

## 🔒 Security Checklist

- [ ] Remove all console.log statements
- [ ] Enable Content Security Policy (CSP)
- [ ] Use HTTPS only
- [ ] Implement rate limiting on APIs
- [ ] Sanitize user inputs
- [ ] Enable CORS correctly
- [ ] Keep dependencies updated
- [ ] Use environment variables for secrets
- [ ] Enable security headers
- [ ] Implement authentication/authorization

---

## 📈 Monitoring

### Application Insights (Azure)

```typescript
import { ApplicationInsights } from '@microsoft/applicationinsights-web';

const appInsights = new ApplicationInsights({
  config: {
    instrumentationKey: import.meta.env.VITE_APPINSIGHTS_KEY,
  },
});
appInsights.loadAppInsights();
appInsights.trackPageView();
```

### Error Tracking (Sentry)

```typescript
import * as Sentry from '@sentry/react';

Sentry.init({
  dsn: import.meta.env.VITE_SENTRY_DSN,
  environment: import.meta.env.MODE,
  tracesSampleRate: 1.0,
});
```

---

## 🎯 Success Criteria

Before going live, ensure:

✅ **Functionality**
- All routes work correctly
- All agent cards navigate properly
- Chat interface is functional
- Mobile navigation works
- All links are valid

✅ **Performance**
- Lighthouse score > 90 (all categories)
- First Contentful Paint < 1.5s
- Time to Interactive < 3.5s
- Bundle size < 500KB (gzipped)

✅ **Accessibility**
- WCAG 2.1 AA compliant
- Keyboard navigation works
- Screen reader compatible
- Color contrast ratios met

✅ **Branding**
- All logos replaced with actual assets
- Colors match brand guidelines
- Typography matches specifications
- Microsoft partnership visible

✅ **Content**
- All placeholder text replaced
- Agent descriptions accurate
- Contact information current
- Legal/privacy pages linked

---

## 📞 Support

For deployment issues or questions:

- **Technical Support**: [Agentic CoE Team]
- **Azure Support**: [Azure Portal → Support]
- **Documentation**: [Landing Page README](./LANDING_PAGE_README.md)

---

## 📝 License

Proprietary - HCLTech © 2024. All rights reserved.
