# Compliance & Audit Requirements

## Audit Log Standards

### What Must Be Logged

Every action MUST include:

1. **Timestamp** (ISO 8601 UTC)
   ```json
   "timestamp": "2026-01-07T10:30:00Z"
   ```

2. **Action Type** (email_send, payment, social_post, invoice, etc.)
   ```json
   "action_type": "payment"
   ```

3. **Actor** (who initiated)
   ```json
   "actor": "claude-code",
   "source": "execute-approved"
   ```

4. **Target** (what/who was affected)
   ```json
   "target": "client@example.com",
   "target_type": "email"
   ```

5. **Approval Status** (who approved, when)
   ```json
   "approval_status": "human_approved",
   "approved_by": "user",
   "approval_timestamp": "2026-01-07T10:25:00Z"
   ```

6. **Result** (success/failure + error code)
   ```json
   "result": "success",
   "error_code": null
   ```

7. **Duration** (how long it took)
   ```json
   "duration_ms": 1250
   ```

### What MUST NOT Be Logged

❌ Passwords or API keys
❌ Full email addresses (use xxx@domain.com)
❌ Full credit card numbers (use last 4 digits only: ****1234)
❌ Social security numbers
❌ Bank account numbers (use last 4 digits only)
❌ Medical records
❌ Any PII beyond name/email domain

### Data Minimization

```json
// BAD - Too much PII
"recipient": "john.doe@company.com"

// GOOD - Anonymized
"recipient": "j***@company.com"
```

## Log Storage Requirements

- **Location**: `/Vault/Logs/YYYY-MM-DD.json`
- **Format**: One JSON object per line (newline-delimited JSON)
- **Rotation**: Daily (new file per date)
- **Retention**: Minimum 90 days
- **Backup**: Weekly backup to secondary storage
- **Access Control**: Read-only after 24 hours
- **Encryption**: At-rest encryption recommended

## Query Examples

```bash
# Find all payments for audit
grep '"action_type": "payment"' /Vault/Logs/2026-01-*.json

# Find all failures
grep '"result": "failure"' /Vault/Logs/2026-01-*.json | jq '.error_code'

# Find actions by specific user
grep '"approved_by": "john"' /Vault/Logs/2026-01-*.json

# Find actions on specific date
jq 'select(.timestamp >= "2026-01-07T00:00:00Z" and .timestamp < "2026-01-08T00:00:00Z")' /Vault/Logs/2026-01-07.json
```

## Regulatory Compliance

### GDPR (EU)
- ✓ Right to be forgotten: Delete logs after 90 days
- ✓ Data minimization: No PII in logs
- ✓ Access control: Restrict log access
- ✓ Breach notification: Alert if breach detected

### CCPA (California)
- ✓ Consumer rights: Provide log dumps on request
- ✓ Data transparency: Clear what's being logged
- ✓ Deletion: Remove on consumer request
- ✓ Opt-out: Support non-logging mode (if needed)

### PCI-DSS (Payment Cards)
- ✓ No full PAN in logs
- ✓ Encrypt logs at rest
- ✓ Access control for log servers
- ✓ Audit trails for card operations

## Audit Log Example

```json
{
  "timestamp": "2026-01-07T10:30:00Z",
  "action_type": "payment",
  "action_id": "PAY-20260107-001",
  "actor": "claude-code",
  "source": "execute-approved",
  "target": "c***@acme.com",
  "target_type": "customer",
  "parameters": {
    "amount": 500.00,
    "method": "bank_transfer",
    "reference": "INV-2026-001",
    "card_last4": "****1234"
  },
  "approval_status": "human_approved",
  "approved_by": "user",
  "approval_timestamp": "2026-01-07T10:25:00Z",
  "result": "success",
  "error_code": null,
  "error_message": null,
  "duration_ms": 1250,
  "retry_count": 0
}
```

## Audit Trail Integrity

- Use monotonic timestamps
- Include retry information
- Track approval chain
- Never modify past logs
- Sign logs if using cloud storage
