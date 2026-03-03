# Expert Insights & Tribal Knowledge

## Document Information
| Field | Value |
|-------|-------|
| Last Updated | 2026-01-15 |
| Contributors | Senior Support Engineers, SMEs |
| Purpose | Curated expert knowledge to accelerate troubleshooting |

---

## How to Use This Document

This document contains insights from experienced CCaaS support engineers - the "tribal knowledge" that often isn't documented elsewhere. These insights help you:
- Avoid common pitfalls
- Recognize patterns faster
- Apply proven solutions
- Reduce trial-and-error

---

## Routing Insights

### Insight: The "Ghost Agent" Problem
**Contributed by:** J. Smith, Senior Engineer

When calls aren't routing despite agents showing as "Available":
1. Check if agents recently crashed or force-closed browser
2. Their presence may show Available but session is stale
3. **Quick fix:** Have agent click their status icon twice (Off -> Available)
4. **Root cause:** WebSocket disconnect doesn't always trigger presence update

---

### Insight: Skills Routing "All-or-Nothing" Trap
**Contributed by:** M. Chen, Principal Engineer

Common misconfiguration with skills-based routing:
- If queue requires Skill A (Level 3) AND Skill B (Level 2)
- But agent has Skill A (Level 3) only
- Agent gets ZERO calls from this queue, not even Skill A calls

**Solution:** 
- Use separate queues for different skill combinations
- Or set skills as "preferred" not "required" if flexibility is acceptable

---

### Insight: Overflow Timing Gotcha
**Contributed by:** R. Kim, Senior Engineer

Overflow threshold of "60 seconds" doesn't mean what you think:
- Timer starts when call enters queue
- BUT timer resets if call is offered to agent (even if agent doesn't answer)
- A call could theoretically wait much longer than 60 seconds

**Best Practice:** 
- Set threshold lower than you think you need
- Monitor actual wait times, not just configured threshold

---

### Insight: The Midnight Queue Reset
**Contributed by:** S. Patel, Senior Engineer

Every midnight (tenant timezone), the system runs a queue optimization job:
- If you're seeing routing issues that "fix themselves" next day
- Or issues that "appear every morning"
- Check if changes were made close to midnight
- Changes made during the job may not apply until next cycle

**Workaround:** Make queue changes at least 2 hours before midnight

---

## Licensing Insights

### Insight: The 48-Hour License Lag
**Contributed by:** A. Kumar, Principal Engineer

When customers say "I assigned the license but user still can't access":
1. Initial sync can take up to 48 hours (not the 15-30 min docs say)
2. This is especially true for new tenants or first CCaaS license
3. Subsequent license assignments are faster

**What to tell customer:**
- Wait 48 hours before escalating
- User should sign out completely and back in (not just refresh)
- Clear browser cache if still not working after 48h

---

### Insight: Feature Flag vs. License Feature
**Contributed by:** M. Chen, Principal Engineer

These are different things:
- **License Feature:** What the license tier allows
- **Feature Flag:** On/off toggle for the feature

Both must be true for feature to work:
1. License must include feature (can't toggle on Premium feature with Standard license)
2. Feature flag must be enabled (even if licensed, may be off by default)

**Common confusion:** Customer has Premium license but feature is off → Enable flag

---

### Insight: The Role Propagation Mystery
**Contributed by:** S. Patel, Senior Engineer

When you assign a role to a user:
- Role shows as assigned immediately in Admin Portal
- But actual permissions may take 15-60 minutes
- Some permissions require user to log out and back in

**Pattern to recognize:**
- "I can see the option but get 'Access Denied' when I click it"
- = Role assigned but not propagated yet

---

## Connectivity Insights

### Insight: The Proxy Double-Check
**Contributed by:** R. Kim, Senior Engineer

When customer says "We whitelisted all the URLs":
90% of the time, they did NOT whitelist:
1. WebSocket URLs (wss://)
2. Media/TURN URLs (different domain)
3. New URLs added in recent releases

**Always ask:** "Can you share your current whitelist?" and compare against latest requirements doc.

---

### Insight: VPN Split-Tunnel Impact
**Contributed by:** J. Smith, Senior Engineer

Many call quality issues trace back to VPN:
- Customer uses VPN for security
- All CCaaS traffic goes through VPN (full tunnel)
- Media traffic adds latency, causes jitter

**Recommendation:**
- Split-tunnel: Route CCaaS media direct, not through VPN
- If not possible: At minimum, exclude UDP media traffic

---

### Insight: The "Works in Incognito" Test
**Contributed by:** A. Kumar, Principal Engineer

First thing to try for any client-side issue:
1. Open incognito/private browser window
2. Log in to CCaaS
3. Try to reproduce issue

If it works in incognito:
- Browser extension is likely the cause
- Or cached data is corrupt
- Solution: Clear cache, disable extensions one by one

---

## Upgrade/Migration Insights

### Insight: The Config Backup Nobody Makes
**Contributed by:** M. Chen, Principal Engineer

Before ANY upgrade:
1. Export all call flows (JSON)
2. Screenshot all queue configurations
3. Export routing rules
4. Document custom integrations

Customers almost never do this. When upgrade breaks something, recovery is painful.

**Post-upgrade:** First 24 hours, run through core functionality checklist before declaring success.

---

### Insight: API Version Deprecation Timing
**Contributed by:** S. Patel, Senior Engineer

When API v1 is deprecated:
- It doesn't immediately stop working
- Grace period is usually 90 days
- But during grace period, you'll see intermittent failures
- Failures increase over time until full deprecation

**Pattern:** "Our integration worked fine, then started failing randomly, now fails always"
→ Check API version being used

---

### Insight: The Post-Upgrade 24-Hour Rule
**Contributed by:** J. Smith, Senior Engineer

After any major upgrade:
1. Background jobs run for up to 24 hours (indexing, migration)
2. Performance may be degraded during this time
3. Some features may show inconsistent behavior
4. Real-time dashboards especially affected

**Guidance:** Wait 24 hours before reporting performance issues post-upgrade (unless critical)

---

## General Troubleshooting Insights

### Insight: The "What Changed?" Question
**Contributed by:** R. Kim, Senior Engineer

First question for any new issue:
"What changed in the last 24-48 hours?"

Changes include:
- CCaaS version upgrade
- Configuration changes
- Azure AD changes
- Network/firewall changes
- New employees/role changes
- M365 license changes

80% of issues correlate with a recent change.

---

### Insight: Screenshot > Description
**Contributed by:** A. Kumar, Principal Engineer

When collecting issue details:
- Ask for screenshot of the error
- Ask for screenshot of the configuration
- Ask for browser console screenshot (F12 > Console)

Descriptions are often inaccurate. Screenshots don't lie.

---

### Insight: The Multi-Tenant Confusion
**Contributed by:** M. Chen, Principal Engineer

Large customers often have multiple tenants:
- Production
- UAT/Staging
- Dev
- Sometimes regional tenants

**Always confirm:** "Which tenant ID is this issue in?" before troubleshooting.

Common trap: Customer describes issue in prod, provides config screenshots from dev.

---

### Insight: Time Zone Troubles
**Contributed by:** S. Patel, Senior Engineer

Half of all schedule-related issues are timezone problems:
1. Queue hours set in wrong timezone
2. User browser in different timezone than tenant
3. Daylight saving time transitions
4. UTC vs. local time confusion in logs

**Always ask:** What timezone is the tenant configured for? What timezone is the user in?

---

## Quick Diagnostic Patterns

| Customer Says | Likely Cause | First Check |
|---------------|--------------|-------------|
| "Nothing's working" | Service outage or auth issue | status.azure.com |
| "It was working yesterday" | Recent change | What changed in 48h? |
| "Only for some users" | Licensing or role issue | Compare working vs non-working user |
| "Only on our network" | Firewall/proxy | Test from different network |
| "After the upgrade" | Known issue or config reset | Check KI list for version |
| "Randomly fails" | Intermittent connectivity | Check WebSocket stability |
| "Slow but works" | Performance/load issue | Check background jobs, metrics |

---

*This document is a living collection. Add your insights via the Support Engineering wiki.*
