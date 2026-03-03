# SOP-ROUTING-001: Queue Routing Troubleshooting

## Document Information
| Field | Value |
|-------|-------|
| SOP ID | SOP-ROUTING-001 |
| Category | Routing |
| Version | 2.3 |
| Last Updated | 2025-12-15 |
| Owner | CCaaS Support Engineering |

---

## Overview

This SOP provides step-by-step guidance for troubleshooting call routing issues in Microsoft CCaaS environments. Use this procedure when customers report calls not being routed to agents, stuck in queues, or routing to incorrect destinations.

---

## Symptoms

- Calls remain in queue despite available agents
- Calls route to wrong queue or agent group
- Overflow rules not triggering
- Skills-based routing not matching correctly
- After-hours routing not activating

---

## Prerequisites

Before starting troubleshooting:
1. Confirm customer tenant ID and environment (Production/Sandbox)
2. Verify product version (Admin Portal > About)
3. Obtain timeframe of issue occurrence
4. Get sample call IDs if available

---

## Troubleshooting Steps

### Step 1: Verify Queue Status

**Action:** Check if the queue is active and properly configured.

**How to Check:**
1. Navigate to Admin Portal > Contact Center > Queues
2. Locate the affected queue
3. Verify:
   - Queue status is "Active"
   - Operating hours are correctly set
   - Queue capacity is not exceeded

**Expected Result:** Queue shows as Active with correct hours.

**If Failed:** 
- If queue is Inactive, enable it and test
- If hours are wrong, correct the schedule
- If capacity exceeded, increase limit or add agents

---

### Step 2: Validate Agent Assignment

**Action:** Confirm agents are assigned to the queue and are available.

**How to Check:**
1. Navigate to Admin Portal > Contact Center > Queues > [Queue Name]
2. Click "Members" tab
3. Verify:
   - At least one agent is assigned
   - Agents have correct skills (if skills-based routing)
   - Agent presence status is "Available"

**Expected Result:** One or more agents assigned and showing Available.

**If Failed:**
- Add agents to queue if none assigned
- Check agent skill assignments match queue requirements
- Verify agents are logged in and set to Available

---

### Step 3: Check Routing Rules

**Action:** Validate routing rule configuration and priority.

**How to Check:**
1. Navigate to Admin Portal > Contact Center > Routing Rules
2. Find rules associated with the affected queue
3. Verify:
   - Rule is enabled
   - Priority order is correct
   - Conditions match expected criteria
   - Target queue/agent is correct

**Expected Result:** Routing rules are enabled with correct targets.

**If Failed:**
- Enable disabled rules
- Correct rule conditions
- Adjust priority if rules conflict

---

### Step 4: Validate Skills Configuration (If Skills-Based Routing)

**Action:** Ensure skills are properly configured for routing.

**How to Check:**
1. Navigate to Admin Portal > Contact Center > Skills
2. Verify skill definitions exist
3. Check agent skill assignments:
   - Admin Portal > Users > [Agent] > Skills
4. Verify queue skill requirements:
   - Admin Portal > Queues > [Queue] > Skill Requirements

**Expected Result:** Skills defined, assigned to agents, and required by queue.

**If Failed:**
- Create missing skills
- Assign skills to agents
- Configure queue skill requirements

---

### Step 5: Check Overflow Settings

**Action:** Verify overflow configuration for high-volume scenarios.

**How to Check:**
1. Navigate to Admin Portal > Contact Center > Queues > [Queue Name]
2. Click "Overflow" tab
3. Verify:
   - Overflow is enabled (if needed)
   - Wait time threshold is appropriate
   - Overflow target queue is valid
   - Fallback action is configured

**Expected Result:** Overflow configured with valid targets.

**If Failed:**
- Enable overflow if calls are timing out
- Set appropriate wait thresholds
- Configure valid overflow destination

---

### Step 6: Review Call Flow Configuration

**Action:** Check the call flow/IVR for routing logic issues.

**How to Check:**
1. Navigate to Admin Portal > Contact Center > Call Flows
2. Open the affected call flow
3. Trace the path from entry to queue routing
4. Verify:
   - Correct conditions and branches
   - Queue transfer action points to correct queue
   - No infinite loops or dead ends

**Expected Result:** Call flow correctly routes to intended queue.

**If Failed:**
- Fix call flow logic errors
- Update queue references
- Remove dead-end paths

---

### Step 7: Check for Known Issues

**Action:** Verify if this is a known product issue.

**How to Check:**
1. Search internal KB for similar symptoms
2. Check release notes for current version
3. Review known issues list for routing bugs

**Common Known Issues:**
- KI-2025-1145: Skills routing delay in v2.5.x
- KI-2025-1203: Overflow not triggering after queue edit
- KI-2025-1298: Agent presence sync delay

**If Match Found:** Apply documented workaround or hotfix.

---

## Escalation Criteria

Escalate to Tier 2 if:
- Issue persists after all steps completed
- Suspected product bug not in known issues
- Customer impact is P1/Critical
- Configuration appears correct but routing fails

---

## Related Documents

- SOP-ROUTING-002: Skills-Based Routing Deep Dive
- SOP-ROUTING-003: Call Flow Troubleshooting
- KB-2025-0892: Queue Capacity Best Practices
- KB-2025-0915: Agent Presence States Explained

---

## Revision History

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 2.3 | 2025-12-15 | J. Smith | Added v2.5.x known issues |
| 2.2 | 2025-09-20 | M. Chen | Updated overflow steps |
| 2.1 | 2025-06-10 | J. Smith | Added skills validation |
| 2.0 | 2025-03-01 | A. Kumar | Major revision |
