# CCaaS Known Issues Repository

## Document Information
| Field | Value |
|-------|-------|
| Last Updated | 2026-01-15 |
| Total Active Issues | 23 |
| Owner | CCaaS Engineering |

---

## Active Known Issues

### Routing Issues

#### KI-2025-1145: Skills-Based Routing Delay in v2.5.x
| Field | Value |
|-------|-------|
| ID | KI-2025-1145 |
| Severity | Medium |
| Affected Versions | 2.5.0 - 2.5.2 |
| Status | Fix available in 2.5.3 |
| Discovered | 2025-09-15 |

**Symptoms:**
- Skills-based routing takes 10-15 seconds longer than expected
- Agents with matching skills not receiving calls immediately
- Queue wait times increased for skill-routed calls

**Root Cause:**
Skill matching algorithm optimization in 2.5.0 introduced a caching bug that causes delay in skill evaluation.

**Workaround:**
1. Apply hotfix HF-2025-1145 (available via support request)
2. Or upgrade to v2.5.3+

**Permanent Fix:**
Fixed in version 2.5.3. Upgrade recommended.

---

#### KI-2025-1203: Overflow Not Triggering After Queue Edit
| Field | Value |
|-------|-------|
| ID | KI-2025-1203 |
| Severity | Medium |
| Affected Versions | 2.5.0 - 2.5.1 |
| Status | Fixed in 2.5.2 |
| Discovered | 2025-10-02 |

**Symptoms:**
- Overflow rules stop working after editing queue settings
- Calls remain in queue past overflow threshold
- No overflow events logged

**Root Cause:**
Queue configuration save operation was clearing overflow settings cache without rebuilding.

**Workaround:**
1. After editing queue, toggle overflow off and back on
2. Save twice to ensure cache rebuild

**Permanent Fix:**
Fixed in version 2.5.2.

---

#### KI-2025-1298: Agent Presence Sync Delay
| Field | Value |
|-------|-------|
| ID | KI-2025-1298 |
| Severity | Low |
| Affected Versions | 2.4.5+ |
| Status | Under investigation |
| Discovered | 2025-11-10 |

**Symptoms:**
- Agent presence status takes 30-60 seconds to update
- Calls routed to agents who just went unavailable
- Supervisor dashboard shows stale presence

**Root Cause:**
Under investigation. Suspected: presence service scaling issue during peak load.

**Workaround:**
1. Agents should wait 60 seconds after status change before expecting change
2. Supervisors can manually refresh dashboard

**Permanent Fix:**
Targeted for v2.6.0.

---

### Licensing Issues

#### KI-2025-1056: License Sync Failure on Tenant Move
| Field | Value |
|-------|-------|
| ID | KI-2025-1056 |
| Severity | High |
| Affected Versions | All |
| Status | Workaround available |
| Discovered | 2025-06-20 |

**Symptoms:**
- After tenant geo-move, CCaaS licenses show as "not assigned"
- Users cannot access CCaaS features
- Admin Portal shows license errors

**Root Cause:**
License sync does not automatically trigger after tenant geo-move operation.

**Workaround:**
1. Contact support to trigger manual license resync
2. Provide tenant ID and new region
3. Allow 4 hours for sync to complete

**Permanent Fix:**
Planned for Q2 2026.

---

#### KI-2025-1178: Feature Flag Reset During Upgrade
| Field | Value |
|-------|-------|
| ID | KI-2025-1178 |
| Severity | Medium |
| Affected Versions | 2.4.x to 2.5.x upgrade |
| Status | By design (documented) |
| Discovered | 2025-08-30 |

**Symptoms:**
- Some feature flags reset to default (off) after upgrade
- Preview features disabled
- Beta features need re-enabling

**Root Cause:**
By design - preview/beta features require explicit re-opt-in after major version upgrade for compliance.

**Workaround:**
1. After upgrade, review Feature Management settings
2. Re-enable desired preview/beta features
3. Document enabled features before upgrade

**Permanent Fix:**
N/A - This is expected behavior.

---

### Connectivity Issues

#### KI-2025-1234: WebSocket Reconnection Loop
| Field | Value |
|-------|-------|
| ID | KI-2025-1234 |
| Severity | Medium |
| Affected Versions | 2.5.0+ |
| Status | Fixed in 2.5.4 |
| Discovered | 2025-10-20 |

**Symptoms:**
- Agent desktop shows repeated "Reconnecting..." messages
- High CPU usage on client
- Eventually disconnects completely

**Root Cause:**
WebSocket reconnection logic had exponential backoff bug causing rapid retry attempts.

**Workaround:**
1. Refresh browser page
2. If persists, clear browser cache
3. Switch to incognito mode temporarily

**Permanent Fix:**
Fixed in version 2.5.4.

---

#### KI-2025-1289: Media Connection Failure in Restricted Networks
| Field | Value |
|-------|-------|
| ID | KI-2025-1289 |
| Severity | High |
| Affected Versions | All |
| Status | Configuration guidance available |
| Discovered | 2025-11-05 |

**Symptoms:**
- Voice calls fail to connect
- "Media negotiation failed" error
- Works on some networks, fails on others

**Root Cause:**
Corporate firewalls blocking UDP traffic required for WebRTC media.

**Workaround:**
1. Ensure UDP ports 3478-3481 are open
2. Whitelist TURN server IPs
3. See KB-2025-0701 for full network requirements

**Permanent Fix:**
N/A - Network configuration required.

---

### UI/Feature Issues

#### KI-2025-1312: Dashboard Widgets Not Loading
| Field | Value |
|-------|-------|
| ID | KI-2025-1312 |
| Severity | Low |
| Affected Versions | 2.5.2+ |
| Status | Fixed in 2.5.5 |
| Discovered | 2025-11-25 |

**Symptoms:**
- Real-time dashboard widgets show "Loading..."
- Some widgets never load
- Refreshing helps temporarily

**Root Cause:**
Dashboard widget initialization race condition.

**Workaround:**
1. Refresh page
2. Reduce number of widgets on dashboard
3. Use Chrome/Edge instead of Firefox

**Permanent Fix:**
Fixed in version 2.5.5.

---

#### KI-2025-1267: Custom Report Export Timeout
| Field | Value |
|-------|-------|
| ID | KI-2025-1267 |
| Severity | Low |
| Affected Versions | 2.5.0+ |
| Status | Under investigation |
| Discovered | 2025-10-28 |

**Symptoms:**
- Large report exports time out
- Export fails for reports >100K rows
- No partial download available

**Root Cause:**
Export timeout threshold too aggressive for large datasets.

**Workaround:**
1. Apply date filters to reduce data size
2. Export in smaller chunks
3. Schedule export during off-peak hours

**Permanent Fix:**
Targeted for v2.6.0.

---

### Integration Issues

#### KI-2025-1189: CRM Connector Authentication Expiry
| Field | Value |
|-------|-------|
| ID | KI-2025-1189 |
| Severity | Medium |
| Affected Versions | All with CRM integration |
| Status | Documentation updated |
| Discovered | 2025-09-10 |

**Symptoms:**
- CRM popup stops working
- "Authentication expired" errors
- CRM data not syncing

**Root Cause:**
OAuth tokens expire after 90 days and don't auto-refresh in certain configurations.

**Workaround:**
1. Admin Portal > Integrations > CRM > Re-authorize
2. Set calendar reminder for 80 days

**Permanent Fix:**
Token auto-refresh being implemented for v2.6.0.

---

## Recently Resolved Issues

| ID | Issue | Resolved In | Resolution Date |
|----|-------|-------------|-----------------|
| KI-2025-1234 | WebSocket reconnection loop | 2.5.4 | 2025-12-01 |
| KI-2025-1203 | Overflow not triggering | 2.5.2 | 2025-10-15 |
| KI-2025-1145 | Skills routing delay | 2.5.3 | 2025-11-01 |
| KI-2025-1098 | Queue capacity display | 2.5.2 | 2025-10-15 |
| KI-2025-1067 | Agent status stuck | 2.5.1 | 2025-09-20 |

---

## How to Report New Issues

1. Verify issue is not already documented above
2. Check release notes for known limitations
3. Submit via internal Support Engineering portal
4. Include:
   - Tenant ID
   - Version
   - Steps to reproduce
   - Impact assessment
   - Any workarounds discovered

---

*This document is updated weekly. Last sync: 2026-01-15*
