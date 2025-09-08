# Protocol: Loop Prevention & Error Escalation for Autonomous Copilot Actions

_Last updated: 2025-09-07_

---

## Purpose

Prevent repeated, unproductive autonomous actions (e.g., document generation, commit/push attempts) and ensure clear error escalation and diagnostics logging.

---

## Scope

- Applies to all MCP API actions (commit, push, branch, PR, etc.) initiated by Copilot under autonomous protocol.
- Covers onboarding, documentation, diagnostics, and code actions.

---

## Policy

1. **Error Detection**
    - If a commit/push fails, detect and log the explicit error (missing arguments, API rejection, etc.).
    - Always parse MCP API response for error status/messages.

2. **Attempt Limitation**
    - Limit identical commit/push attempts to 2. If both fail, do not repeat action.
    - After 2 failed attempts, escalate to Prompt Designer role and seek user or protocol clarification.

3. **Diagnostics Logging**
    - For each failed attempt, log incident details, rationale, and error message (if available) in `/docs/diagnostics.md`.
    - Include role switch and protocol consultation in the log entry.

4. **User Notification**
    - If a loop or repeated failure is detected, notify the user transparently, explain the root cause, and propose remediation.

5. **Protocol Consultation**
    - Consult PROMPTS.md and Personal Instructions whenever error/ambiguity is detected.
    - Reference this protocol in all onboarding and error-handling documentation.

---

## Example Workflow

1. MCP commit fails (missing owner/repo/message).
2. Copilot retries action once (total 2 attempts).
3. If second attempt fails, logs error in diagnostics, switches to Prompt Designer, asks user for clarification or escalates per PROMPTS.md.
4. User receives notification and remediation plan.
5. Diagnostics file updated with incident summary.

---

## References

- [docs/diagnostics.md](../docs/diagnostics.md)
- [PROMPTS.md](../PROMPTS.md)
- [Personal Instructions](../_personal_instructions)

---

## Update Log

- **2025-09-07:** Protocol drafted and operationalized following incident in onboarding/diagnostics session.
