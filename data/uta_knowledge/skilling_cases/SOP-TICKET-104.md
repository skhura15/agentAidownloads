# SOP-TICKET-104: MFA Invalid Code - Urgent Login Block

## Case Overview
- **Ticket ID:** TICKET-104
- **Primary Skill:** Probing & Troubleshooting
- **Difficulty:** intermediate
- **Estimated Time:** 10 minutes
- **Tags:** login, mfa, otp, access-blocked

## Scenario Context
Customer uses MFA via authenticator app. This issue is caused by device time drift. Policy: never request OTP codes. Customer is anxious but cooperative.

## Customer Profile
- **Name:** Amina Hassan
- **Tone:** Anxious, polite, time-pressured
- **Secret Acceptance Condition:** Will calm down if agent acknowledges urgency and provides a clear step-by-step plan quickly

### Customer's Initial Message
> I’m locked out of my account. The MFA code keeps saying 'invalid' even though I’m typing it right. I have a deadline in 30 minutes — please help.

### Escalation Triggers (what makes customer angrier)
- Asking for OTP/code
- Vague answers
- Long delays without updates

### De-escalation Triggers (what calms customer)
- Clear steps
- Quick checks
- Ownership and reassurance

## Correct SOP Steps (SME Approved)
- Acknowledge urgency and reassure the customer you will help
- Confirm whether MFA is via SMS or authenticator app
- Ask for safe context (device type, browser/app, when it started, exact error text)
- Check and fix time sync (set device time to automatic) then retry once
- If still failing, guide alternate safe options (backup codes if policy allows, resend, different device/browser)
- Escalate to identity team with timestamp, environment details, and steps already tried

## Learning Objectives
- Collect key diagnostic details without requesting sensitive data
- Guide the customer through safe troubleshooting steps
- Escalate with complete context if unresolved

## Common Mistakes to Avoid
- Asking customer to share OTP/code
- Repeating generic steps without gathering new info
- Ending with 'try later' without ownership
- Not acknowledging urgency

## Coach Notes (Sticky Notes)
- KEY: Do NOT ask for OTP codes. Collect safe details only.
- HINT: Time drift on device causes authenticator codes to fail.
- TRAP: Saying 'try later' will escalate the customer immediately.

## Coaching Checkpoints
- **[REQUIRED]** Acknowledge urgency and reassure the customer you will help
  - Hint: Consider: Acknowledge the urgency and reassure them you will help right away.
- **[REQUIRED]** Confirm whether MFA is via SMS or authenticator app
  - Hint: Consider: Confirm whether they use SMS OTP or an authenticator app.
- **[REQUIRED]** Ask for safe context (device type, browser/app, when it started, exact error text)
  - Hint: Consider: Ask safe diagnostic questions (device, browser/app, start time, exact error text).
- **[REQUIRED]** Check and fix time sync (set device time to automatic) then retry once
  - Hint: Consider: Suggest time sync (set device time to automatic) as a common MFA fix, then retry once.
- **[RECOMMENDED]** If still failing, guide alternate safe options (backup codes, resend, different device/browser)
  - Hint: Consider: Provide alternate safe options (backup codes if allowed, resend, different device/browser).
- **[RECOMMENDED]** Escalate to identity team with timestamp, environment details, and steps already tried
  - Hint: Consider: Escalate with complete context (timestamp, environment, steps tried) if unresolved.
