---
name: error-recovery
description: Use when handling transient failures, retrying failed actions with exponential backoff, or implementing graceful degradation for missing services.
---

# Error Recovery Skill

Handle failures gracefully and retry operations with exponential backoff.

## Error Categories

**Transient** (auto-retry):
- Network timeouts
- API rate limits
- Temporary service outages
- Retry: exponential backoff, max 3 attempts

**Authentication** (alert human):
- Expired tokens
- Invalid credentials
- Permission denied
- Action: Pause operations, alert human, quarantine files

**Logic** (manual review):
- Claude misinterpreted request
- Invalid data format
- Unexpected state
- Action: Move to `/Manual_Review/`, wait for human

**Data** (quarantine):
- Corrupted file
- Missing required field
- Invalid schema
- Action: Move to `/Quarantine/`, log error

**System** (fallback):
- Orchestrator crash
- Disk full
- Service unavailable
- Action: Watchdog restarts, queue grows

## Retry Strategy

```python
def retry_with_backoff(func, max_attempts=3, base_delay=1):
    for attempt in range(max_attempts):
        try:
            return func()
        except TransientError as e:
            if attempt == max_attempts - 1:
                raise
            delay = min(base_delay * (2 ** attempt), 60)
            time.sleep(delay)
```

## Graceful Degradation

| Component | Failure | Degradation |
|-----------|---------|-------------|
| Gmail API | Down | Queue outgoing locally |
| Payments | Failed | Never auto-retry, alert |
| Social API | Rate limit | Queue post for later |
| Odoo | Down | Cache locally, sync later |

## Script Location

`~/.claude/skills/error-recovery/scripts/retry_handler.py`

## References

See `references/error_taxonomy.md` for full error codes.
