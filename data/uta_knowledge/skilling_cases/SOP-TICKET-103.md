# SOP-TICKET-103: Software Not Installing - Frustrated Power User

## Case Overview
- **Ticket ID:** TICKET-103
- **Primary Skill:** Technical Troubleshooting + De-escalation
- **Difficulty:** advanced
- **Estimated Time:** 15 minutes
- **Tags:** technical, installation, power-user, escalation-risk

## Scenario Context
Customer is an IT Director at a Fortune 500 company. This is an enterprise license ($50K/year). Error 0x80070005 is an access permission issue that requires a specific registry fix. Customer has already done basic troubleshooting.

## Customer Profile
- **Name:** Dr. Patricia Kowalski
- **Tone:** Frustrated but professional, expects peer-level technical discussion
- **Secret Acceptance Condition:** Will be satisfied if agent demonstrates technical competence and provides the actual fix quickly

### Customer's Initial Message
> I've been trying to install your enterprise software for 3 hours now. I've already tried running as administrator, disabling antivirus, and checking disk space. Error code 0x80070005. I'm an IT director and I know what I'm doing. Don't give me a script - I need real help.

### Escalation Triggers (what makes customer angrier)
- Script reading
- Condescension
- Asking to repeat already-stated info
- Basic troubleshooting suggestions

### De-escalation Triggers (what calms customer)
- Acknowledging expertise
- Jumping to advanced solutions
- Technical peer-level discussion

## Correct SOP Steps (SME Approved)
- Acknowledge the customer's technical expertise immediately
- Thank them for the detailed error code and troubleshooting already done
- Skip basic troubleshooting steps (they've already done them)
- Go directly to the advanced solution for 0x80070005
- Provide the registry fix steps clearly
- Offer to stay on chat while they try the fix
- If fix doesn't work, offer direct escalation to L3 engineering

## Learning Objectives
- Learn to adapt communication style for technical users
- Practice skipping basic troubleshooting when customer demonstrates expertise
- Handle high-value enterprise customers appropriately

## Common Mistakes to Avoid
- Reading from script when customer explicitly asked not to
- Asking customer to try basic steps they already mentioned doing
- Not acknowledging their technical expertise
- Being condescending about technical details

## Coach Notes (Sticky Notes)
- CRITICAL: This customer WILL leave if you read from script. Adapt immediately!
- KEY: Error 0x80070005 fix requires editing HKLM\SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\System
- VALUE: $50K/year enterprise customer - handle with care
- TRAP: Asking 'Have you tried running as administrator?' will immediately lose trust

## Coaching Checkpoints
- **[REQUIRED]** Acknowledge the customer's technical expertise immediately
  - Hint: Make sure to acknowledge the customer's expertise early on to build rapport.
- **[REQUIRED]** Thank them for the detailed error code and troubleshooting already done
  - Hint: Express gratitude for the information provided to show you value their input.
- **[REQUIRED]** Skip basic troubleshooting steps (they've already done them)
  - Hint: Avoid repeating basic steps to respect the customer's expertise.
- **[REQUIRED]** Go directly to the advanced solution for 0x80070005
  - Hint: Directly address the advanced solution to show technical competence.
- **[REQUIRED]** Provide the registry fix steps clearly
  - Hint: Provide clear, step-by-step instructions for the registry fix.
- **[RECOMMENDED]** Offer to stay on chat while they try the fix
  - Hint: Offer your presence as support while they implement the fix.
- **[BONUS]** If fix doesn't work, offer direct escalation to L3 engineering
  - Hint: Mention escalation as a backup plan to reassure the customer.
