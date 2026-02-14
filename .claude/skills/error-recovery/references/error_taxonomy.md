# Error Taxonomy

## Error Categories & Recovery

### Transient Errors (Retry)
Auto-retry with exponential backoff (max 3 attempts, max 60s delay).

| Code | Message | Cause | Recovery |
|------|---------|-------|----------|
| TIMEOUT | Request timed out | Network slow/unstable | Retry with backoff |
| RATE_LIMIT | Rate limit exceeded | API quota hit | Retry with longer delay |
| SERVICE_UNAVAILABLE | Service temporarily down | API maintenance | Retry (502/503) |
| CONNECTION_REFUSED | Cannot connect | Network issue | Retry |

### Authentication Errors (Alert & Pause)
Alert human, pause operations, move item to `/Manual_Review/`.

| Code | Message | Cause | Recovery |
|------|---------|-------|----------|
| AUTH_FAILED | Invalid credentials | Expired token | Rotate credentials |
| UNAUTHORIZED | Access denied | Insufficient permissions | Grant access |
| TOKEN_EXPIRED | Token expired | Time passed | Refresh token |
| INVALID_API_KEY | API key invalid | Revoked/changed | Update .env |

### Logic Errors (Manual Review)
Move to `/Manual_Review/`, alert human, wait for decision.

| Code | Message | Cause | Recovery |
|------|---------|-------|----------|
| VALIDATION_ERROR | Required field missing | Data incomplete | Fix data |
| INVALID_FORMAT | Data format incorrect | Malformed JSON/CSV | Reformat |
| BUSINESS_RULE_VIOLATION | Amount exceeds limit | Policy breached | Escalate |
| CONFLICT | Item already exists | Duplicate operation | Check state |

### Data Errors (Quarantine)
Move to `/Quarantine/`, log details, alert human.

| Code | Message | Cause | Recovery |
|------|---------|-------|----------|
| CORRUPTED_FILE | File unreadable | Partial write | Manual inspection |
| MISSING_FIELD | Required field empty | Data incomplete | Manual data entry |
| TYPE_MISMATCH | Expected type, got other | Schema violation | Manual fix |
| ENCODING_ERROR | Cannot decode | Bad encoding | Re-encode |

### System Errors (Watchdog Restart)
Watchdog process restarts component, alerts human if repeated.

| Code | Message | Cause | Recovery |
|------|---------|-------|----------|
| PROCESS_CRASH | Process exited | Unhandled exception | Restart via watchdog |
| DISK_FULL | No space left | Storage exhausted | Clear space |
| MEMORY_ERROR | Out of memory | Heap too large | Restart process |
| FILE_LOCK | Cannot write file | Vault locked | Retry write |

## Retry Logic

```python
MAX_ATTEMPTS = 3
BASE_DELAY = 1  # seconds
MAX_DELAY = 60

for attempt in range(MAX_ATTEMPTS):
    try:
        return execute_action()
    except TransientError as e:
        if attempt == MAX_ATTEMPTS - 1:
            raise
        delay = min(BASE_DELAY * (2 ** attempt), MAX_DELAY)
        time.sleep(delay)
    except AuthError as e:
        alert_human(f"Auth failed: {e}")
        move_to_manual_review(item)
        return None
```

## Graceful Degradation Table

| Service | Failure | Degradation | Recovery Time |
|---------|---------|-------------|----------------|
| Gmail API | Down | Queue locally, retry daily | 1-4 hours |
| Payments | Failed | Alert human, never auto-retry | Manual |
| Social APIs | Rate limit | Queue post, post later | 15 min - 24h |
| Odoo | Connection lost | Cache locally, sync when up | Immediate |
| Orchestrator | Crash | Watchdog restarts | < 1 min |

## Alert Severity

### CRITICAL (Immediate)
- Payment failures
- Auth errors
- Orchestrator crash
- Data corruption

### WARNING (30 min)
- Multiple retries failing
- Rate limiting
- Transient timeouts

### INFO (Logging only)
- Successful retries
- Graceful degradations
