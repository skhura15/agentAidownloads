# SOP-LICENSING-001: Licensing and Feature Access Troubleshooting

## Document Information
| Field | Value |
|-------|-------|
| SOP ID | SOP-LICENSING-001 |
| Category | Licensing |
| Version | 1.8 |
| Last Updated | 2025-11-20 |
| Owner | CCaaS Support Engineering |

---

## Overview

This SOP provides guidance for troubleshooting licensing-related issues in Microsoft CCaaS. Use this when customers cannot access features, receive license errors, or experience feature gating issues.

---

## Symptoms

- "Feature not available" errors
- Missing features in Admin Portal
- License assignment failures
- SKU mismatch warnings
- Feature flags not enabling
- Premium features inaccessible

---

## Prerequisites

Before starting troubleshooting:
1. Confirm customer tenant ID
2. Obtain the M365 Admin Center access (or ask customer to check)
3. Identify specific feature(s) that are inaccessible
4. Note product version

---

## CCaaS License Tiers

| Tier | SKU Name | Key Features |
|------|----------|--------------|
| Standard | CCaaS_STD | Basic queues, voice, chat |
| Premium | CCaaS_PRM | Skills routing, analytics, WFM |
| Enterprise | CCaaS_ENT | All features, custom integrations |

---

## Troubleshooting Steps

### Step 1: Verify Tenant License

**Action:** Confirm the tenant has appropriate CCaaS licenses.

**How to Check:**
1. Access M365 Admin Center (admin.microsoft.com)
2. Navigate to Billing > Licenses
3. Search for "Contact Center" or "CCaaS"
4. Verify:
   - License is present
   - License tier matches expected (Standard/Premium/Enterprise)
   - Available licenses > 0

**Expected Result:** CCaaS license present with available seats.

**If Failed:**
- Customer needs to purchase CCaaS license
- Contact account team for license procurement

---

### Step 2: Verify User License Assignment

**Action:** Confirm the affected user has a CCaaS license assigned.

**How to Check:**
1. M365 Admin Center > Users > Active Users
2. Select the affected user
3. Click "Licenses and apps"
4. Verify:
   - CCaaS license is checked/assigned
   - Required dependent licenses are assigned (e.g., Teams)

**Expected Result:** User has CCaaS license assigned.

**If Failed:**
- Assign CCaaS license to user
- Wait 15-30 minutes for propagation
- Have user sign out and back in

---

### Step 3: Check Feature Flags

**Action:** Verify feature flags are enabled for the tenant.

**How to Check:**
1. CCaaS Admin Portal > Settings > Feature Management
2. Review list of feature flags
3. Verify:
   - Required feature is listed
   - Feature toggle is "Enabled"
   - Feature is not in "Preview" if expecting GA

**Expected Result:** Required feature flag is enabled.

**If Failed:**
- Enable the feature flag if available
- Some features require support ticket to enable
- Preview features may require opt-in

---

### Step 4: Validate License-Feature Mapping

**Action:** Confirm the feature is included in the customer's license tier.

**How to Check (Reference Table):**

| Feature | Standard | Premium | Enterprise |
|---------|----------|---------|------------|
| Voice Queues | ✓ | ✓ | ✓ |
| Chat Queues | ✓ | ✓ | ✓ |
| Basic Reporting | ✓ | ✓ | ✓ |
| Skills-Based Routing | ✗ | ✓ | ✓ |
| Advanced Analytics | ✗ | ✓ | ✓ |
| Workforce Management | ✗ | ✓ | ✓ |
| Sentiment Analysis | ✗ | ✗ | ✓ |
| Custom Integrations | ✗ | ✗ | ✓ |
| AI Agent Assist | ✗ | ✗ | ✓ |

**Expected Result:** Feature is included in customer's license tier.

**If Failed:**
- Customer needs to upgrade license tier
- Advise on upgrade path to Premium/Enterprise

---

### Step 5: Check Regional Availability

**Action:** Verify the feature is available in the customer's region.

**How to Check:**
1. Identify customer's tenant region (Admin Portal > About)
2. Reference Feature Availability Matrix (internal doc)
3. Verify feature is GA in that region

**Regional Restrictions (Common):**
- Sentiment Analysis: NA, EU, UK only
- AI Agent Assist: NA, EU only (expanding)
- Real-time Translation: Limited regions

**Expected Result:** Feature is available in customer's region.

**If Failed:**
- Feature not yet available in region
- Provide estimated rollout timeline if known
- Consider tenant migration if critical

---

### Step 6: Verify Role-Based Access

**Action:** Confirm user has the role required to access the feature.

**How to Check:**
1. CCaaS Admin Portal > Users > [User] > Roles
2. Verify assigned roles
3. Reference role-permission matrix

**Role Requirements (Common):**
| Feature | Required Role |
|---------|---------------|
| Queue Management | Admin, Supervisor |
| Agent Desktop | Agent, Supervisor, Admin |
| Analytics Dashboard | Supervisor, Admin, Analyst |
| System Configuration | Admin only |
| WFM Scheduling | WFM Admin, Admin |

**Expected Result:** User has appropriate role assigned.

**If Failed:**
- Assign required role to user
- User may need supervisor to grant access

---

### Step 7: Check License Sync Status

**Action:** Verify license sync between M365 and CCaaS.

**How to Check:**
1. CCaaS Admin Portal > Settings > License Sync
2. Check last sync timestamp
3. Look for sync errors

**Expected Result:** Last sync within 24 hours, no errors.

**If Failed:**
- Trigger manual sync if available
- Wait up to 24 hours for auto-sync
- Escalate if sync consistently fails

---

## Common License Error Codes

| Error Code | Meaning | Resolution |
|------------|---------|------------|
| LIC-001 | No valid license | Assign license to user |
| LIC-002 | License expired | Renew subscription |
| LIC-003 | Feature not in SKU | Upgrade license tier |
| LIC-004 | License sync pending | Wait for sync or trigger manual |
| LIC-005 | Regional restriction | Feature not available in region |
| LIC-006 | Role insufficient | Assign required role |

---

## Escalation Criteria

Escalate to Tier 2 if:
- License appears correctly assigned but feature still blocked
- License sync repeatedly fails
- Suspected backend license service issue
- Customer disputes license tier/features

---

## Related Documents

- SOP-LICENSING-002: Enterprise License Configuration
- KB-2025-0456: License Propagation Timelines
- KB-2025-0523: Feature Flag Management Guide
- Policy: CCaaS Feature Availability Matrix

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.8 | 2025-11-20 | S. Patel | Added AI Agent Assist |
| 1.7 | 2025-08-15 | M. Chen | Updated role matrix |
| 1.6 | 2025-05-10 | S. Patel | Added regional availability |
