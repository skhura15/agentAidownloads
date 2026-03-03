# Required Assets

This directory should contain the following brand assets for the HCLTech Agentic CoE landing page.

## Logo Files

### HCLTech Logos
- `hcltech-logo.png` - Primary HCLTech logo (color version, ~200x60px)
- `hcltech-logo-white.png` - White version for dark backgrounds
- Format: PNG with transparency
- Resolution: @2x for retina displays

### Partner Badges
- `microsoft-partner-badge.png` - Microsoft Partnership badge
- Size: ~150x150px
- Format: PNG with transparency

## Technology Icons

### Azure & Microsoft
- `azure-logo.svg` - Microsoft Azure cloud logo
- `microsoft-logo.svg` - Microsoft corporation logo
- `agent-framework-icon.svg` - Microsoft Agent Framework icon

### AI Providers
- `openai-logo.svg` - OpenAI logo
- `azure-openai-logo.svg` - Azure OpenAI Service logo

### Development Stack
- `fastapi-logo.svg` - FastAPI framework logo
- `postgresql-logo.svg` - PostgreSQL database logo
- `react-logo.svg` - React library logo
- `typescript-logo.svg` - TypeScript logo

## Background Images (Optional)

- `hero-background.jpg` - Optional hero section background image
- `tech-pattern.svg` - Repeating pattern for decorative sections

## Favicon

- `favicon.ico` - Browser tab icon (16x16, 32x32, 48x48)
- `apple-touch-icon.png` - iOS home screen icon (180x180)
- `android-chrome-192x192.png` - Android icon
- `android-chrome-512x512.png` - Android icon (larger)

## Agent Icons

Agent icons are currently using Lucide React icons dynamically. If you prefer custom icons:

- `agent-customer-support.svg`
- `agent-data-analytics.svg`
- `agent-document-processing.svg`
- `agent-code-review.svg`
- `agent-research-assistant.svg`
- `agent-sales-intelligence.svg`
- `agent-hr-recruiting.svg`
- `agent-compliance-monitoring.svg`

## Image Optimization Guidelines

1. **Format Selection**:
   - Use SVG for logos and icons (scalable, small file size)
   - Use PNG for photos with transparency
   - Use WebP for photos with fallback to JPG

2. **Size Optimization**:
   - Compress all images (TinyPNG, ImageOptim)
   - Provide @2x versions for retina displays
   - Use appropriate dimensions (don't use 4000px images for 200px display)

3. **Naming Convention**:
   - Use lowercase with hyphens: `hcltech-logo.png`
   - Include size in filename if multiple versions: `logo-200x60.png`
   - Be descriptive: `microsoft-azure-cloud-logo.svg`

4. **Loading Strategy**:
   - Critical images (logos, hero): Preload
   - Below-fold images: Lazy load
   - Decorative images: Low priority

## CDN Configuration

For production, host assets on a CDN:

```
https://cdn.hcltech.com/agentic-coe/assets/
```

Update image references in components to use CDN URLs.

## Placeholder Usage

Until actual assets are available, the landing page uses:
- Lucide React icons as fallbacks
- CSS gradients for backgrounds
- Text-based logos
- SVG data URIs for patterns

## Current Status

⚠️ **Assets Directory is Empty** - Please add the required brand assets before production deployment.

## How to Add Assets

1. Obtain assets from HCLTech brand team
2. Optimize images following guidelines above
3. Place files in this directory (`/ui/frontend/public/assets/`)
4. Update references in components:
   - `Header.tsx` - Update logo path
   - `LandingPage.tsx` - Update technology logos
   - `public/index.html` - Update favicon references

## License & Usage

All brand assets are proprietary to HCLTech and Microsoft. 
Usage is restricted to official HCLTech projects only.
Do not distribute or use outside authorized contexts.

## Contact

For brand asset requests, contact:
- HCLTech Brand Team: [brand@hcltech.com](mailto:brand@hcltech.com)
- Agentic CoE Lead: [Contact via internal channels]
