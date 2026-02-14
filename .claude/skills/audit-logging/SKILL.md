---
name: audit-logging
description: Use when logging all AI Employee actions, tracking approvals, and maintaining compliance audit trails in JSON format.
---

# Audit Logging Skill

Record every action with complete traceability for compliance and debugging.

## Log Format

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "email_send | payment | social_post | file_create",
  "action_id": "unique-identifier",
  "actor": "claude-code",
  "source": "process-inbox | execute-approved | orchestrator",
  "target": "recipient@email.com | social_platform | payment_account",
  "parameters": {
    "subject": "Invoice #123",
    "amount": 500.00,
    "platform": "twitter"
  },
  "approval_status": "auto | human_approved | human_rejected",
  "approved_by": "human_user | null",
  "approval_timestamp": "2026-01-07T10:25:00Z",
  "result": "success | failure",
  "error_code": "null | AUTH_FAILED | TIMEOUT",
  "error_message": "null | Detailed error",
  "duration_ms": 1250,
  "retry_count": 0
}
```

## Log Storage

- **Location**: `/Vault/Logs/YYYY-MM-DD.json`
- **Format**: One JSON object per line (newline-delimited)
- **Retention**: Minimum 90 days, queryable by date
- **Access**: Read-only after 24 hours (audit integrity)

## Logging Requirements

Every action MUST log:
1. Timestamp (ISO 8601 UTC)
2. Action type
3. Actor (always "claude-code" for now)
4. Approval status (who approved, when)
5. Result (success/failure + error code)
6. Duration in milliseconds

Never log:
- Passwords or API keys
- Personally identifiable information (beyond first/last name)
- Full email addresses (anonymize as xxx@domain.com)
- Complete payment card numbers (last 4 digits only)

## Query Examples

```bash
# Find all payments
grep '"action_type": "payment"' /Vault/Logs/2026-01-07.json

# Find failures
grep '"result": "failure"' /Vault/Logs/2026-01-07.json

# Find human approvals
grep '"approval_status": "human_approved"' /Vault/Logs/2026-01-*.json
```

## Script Location

`~/.claude/skills/audit-logging/scripts/audit_logger.py`

## References

See `references/compliance_requirements.md` for regulatory standards.
