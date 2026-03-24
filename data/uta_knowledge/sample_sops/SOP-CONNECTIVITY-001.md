# SOP-CONNECTIVITY-001: Connectivity and Network Troubleshooting

## Document Information
| Field | Value |
|-------|-------|
| SOP ID | SOP-CONNECTIVITY-001 |
| Category | Connectivity |
| Version | 2.1 |
| Last Updated | 2025-10-30 |
| Owner | CCaaS Support Engineering |

---

## Overview

This SOP provides guidance for troubleshooting connectivity issues affecting Microsoft CCaaS. Use this when customers experience connection failures, timeouts, degraded performance, or cannot access CCaaS services.

---

## Symptoms

- "Unable to connect" errors
- Agent desktop not loading
- Frequent disconnections
- High latency or poor call quality
- WebSocket connection failures
- "Service unavailable" messages
- API timeout errors

---

## Prerequisites

Before starting troubleshooting:
1. Confirm customer tenant ID and region
2. Identify affected components (voice, chat, admin portal, etc.)
3. Determine scope (single user, site, or all users)
4. Check Azure Service Health for outages

---

## Troubleshooting Steps

### Step 1: Check Azure Service Health

**Action:** Verify there are no ongoing Azure/CCaaS outages.

**How to Check:**
1. Go to Azure Status: https://status.azure.com
2. Check Microsoft 365 Status: https://status.microsoft.com
3. CCaaS Admin Portal > Service Health
4. Look for:
   - Active incidents in customer's region
   - Degraded services affecting Contact Center

**Expected Result:** No active incidents affecting CCaaS.

**If Outage Found:**
- Inform customer of known outage
- Provide status page link
- Set expectation for resolution timeline
- Monitor and update customer

---

### Step 2: Validate Network Requirements

**Action:** Confirm customer network meets CCaaS requirements.

**Required Endpoints (Must be whitelisted):**

| Service | URLs | Ports |
|---------|------|-------|
| CCaaS Core | *.ccaas.microsoft.com | 443 |
| Real-time Media | *.media.ccaas.microsoft.com | 443, 3478-3481 UDP |
| Authentication | login.microsoftonline.com | 443 |
| Teams Integration | *.teams.microsoft.com | 443 |
| WebSocket | wss://*.ccaas.microsoft.com | 443 |

**How to Check:**
1. Ask customer IT to verify firewall rules
2. Use network testing tool (if available)
3. Check proxy configuration

**Expected Result:** All required endpoints accessible.

**If Failed:**
- Provide endpoint list to customer IT
- Request firewall rule updates
- Check for proxy interference

---

### Step 3: Browser Compatibility Check

**Action:** Verify user's browser meets requirements.

**Supported Browsers:**
| Browser | Minimum Version | Notes |
|---------|-----------------|-------|
| Microsoft Edge | 88+ | Recommended |
| Google Chrome | 88+ | Fully supported |
| Mozilla Firefox | 85+ | Supported |
| Safari | 14+ | Limited support |

**How to Check:**
1. Confirm browser and version with user
2. Check for browser extensions that may interfere
3. Test in incognito/private mode

**Expected Result:** User on supported browser version.

**If Failed:**
- User needs to update browser
- Test in incognito mode (disables extensions)
- Try alternative supported browser

---

### Step 4: Check WebRTC and Media

**Action:** Validate WebRTC connectivity for voice/video.

**How to Check:**
1. Have user access: https://networktest.ccaas.microsoft.com (example)
2. Run connectivity test
3. Check results for:
   - UDP connectivity
   - TURN server access
   - Media relay availability

**Expected Result:** All media tests pass.

**If Failed:**
- UDP blocked: Enable UDP on firewall
- TURN failed: Whitelist media endpoints
- Relay failed: Check regional connectivity

---

### Step 5: Validate Agent Desktop Connectivity

**Action:** Test agent desktop application connectivity.

**How to Check:**
1. Open browser developer tools (F12)
2. Go to Network tab
3. Load agent desktop
4. Look for:
   - Failed requests (red)
   - Long response times (>5s)
   - WebSocket connection status

**Key Connections to Verify:**
- Authentication: login.microsoftonline.com
- API calls: api.ccaas.microsoft.com
- WebSocket: wss://realtime.ccaas.microsoft.com
- Media: media.ccaas.microsoft.com

**Expected Result:** All connections successful, <2s response.

**If Failed:**
- Identify failing endpoint
- Check specific firewall rule
- Verify DNS resolution

---

### Step 6: Check DNS Resolution

**Action:** Verify DNS resolves CCaaS endpoints correctly.

**How to Check (Windows):**
```
nslookup ccaas.microsoft.com
nslookup api.ccaas.microsoft.com
nslookup media.ccaas.microsoft.com
```

**How to Check (Browser):**
1. Developer Tools > Console
2. Check for DNS-related errors

**Expected Result:** DNS resolves to valid IP addresses.

**If Failed:**
- Check customer DNS configuration
- Try alternative DNS (8.8.8.8, 1.1.1.1)
- Check for DNS filtering/blocking

---

### Step 7: Proxy and SSL Inspection

**Action:** Check for proxy or SSL inspection interference.

**Common Issues:**
- SSL inspection breaking WebSocket
- Proxy not supporting WebSocket upgrade
- Certificate errors from inspection

**How to Check:**
1. Check browser certificate (click lock icon)
2. Verify certificate issuer is Microsoft
3. Ask customer if SSL inspection is enabled

**Expected Result:** Valid Microsoft-issued certificate.

**If Failed:**
- Request CCaaS domains be excluded from SSL inspection
- Bypass proxy for CCaaS endpoints if possible

---

### Step 8: Check Client-Side Performance

**Action:** Verify client machine performance.

**How to Check:**
1. Task Manager: Check CPU/Memory usage
2. Check available disk space
3. Verify no conflicting applications

**Minimum Requirements:**
- CPU: 2+ cores
- RAM: 4GB minimum (8GB recommended)
- Network: 1 Mbps per concurrent call

**Expected Result:** Adequate system resources.

**If Failed:**
- Close unnecessary applications
- Upgrade hardware if consistently insufficient
- Check for resource-heavy background processes

---

## Common Connectivity Error Codes

| Error Code | Meaning | Resolution |
|------------|---------|------------|
| CONN-001 | Connection timeout | Check firewall, network path |
| CONN-002 | WebSocket failed | Verify proxy supports WS |
| CONN-003 | Authentication failed | Check Azure AD connectivity |
| CONN-004 | Media negotiation failed | Verify UDP/TURN access |
| CONN-005 | SSL certificate error | Check SSL inspection |
| CONN-006 | DNS resolution failed | Verify DNS configuration |

---

## Regional Endpoints

| Region | Core API | Media |
|--------|----------|-------|
| US East | use.api.ccaas.microsoft.com | use.media.ccaas.microsoft.com |
| US West | usw.api.ccaas.microsoft.com | usw.media.ccaas.microsoft.com |
| EU West | euw.api.ccaas.microsoft.com | euw.media.ccaas.microsoft.com |
| EU North | eun.api.ccaas.microsoft.com | eun.media.ccaas.microsoft.com |
| UK South | uks.api.ccaas.microsoft.com | uks.media.ccaas.microsoft.com |
| Asia East | ase.api.ccaas.microsoft.com | ase.media.ccaas.microsoft.com |

---

## Escalation Criteria

Escalate to Tier 2 if:
- Connectivity issue persists after all checks
- Suspected service-side issue
- Multiple customers in same region affected
- Intermittent issues without clear pattern

---

## Related Documents

- SOP-CONNECTIVITY-002: VoIP Quality Troubleshooting
- KB-2025-0678: Network Requirements Guide
- KB-2025-0701: Firewall Configuration Reference
- KB-2025-0745: Proxy Configuration Best Practices

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.1 | 2025-10-30 | R. Kim | Added regional endpoints |
| 2.0 | 2025-07-15 | J. Smith | Major revision |
| 1.5 | 2025-04-20 | R. Kim | Added WebRTC checks |
