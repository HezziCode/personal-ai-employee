# Dashboard Schema

## Dashboard.md Structure

```markdown
---
last_updated: ISO timestamp
status: active | paused | error
---

# AI Employee Dashboard

## Current Status
- System: [Running / Paused / Error]
- Last Activity: [time ago]
- Pending Actions: N
- Approvals Needed: N

## Quick Metrics
| Metric | Value | Target |
|--------|-------|--------|
| Revenue MTD | $X | $Y |
| Tasks Completed | N | - |
| Response Time | X min | < 1 hour |

## Pending Approvals (Count: N)
- [List of approval items]

## In Progress (Count: N)
- [Current tasks]

## Recent Completions
- [Last 5 items moved to /Done/]

## System Health
| Component | Status | Last Check |
|-----------|--------|-----------|
| Gmail Watcher | ✓ Online | 2m ago |
| Orchestrator | ✓ Running | now |
| Database | ✓ Connected | 1m ago |

## Alerts
- [Any warnings or errors]
```

## Folder Counts

### /Needs_Action/
Count items by type:
- `EMAIL_*` count
- `WHATSAPP_*` count
- `FILE_*` count
- `TRANSACTION_*` count

### /Pending_Approval/
List all items:
- Type (email, payment, post, invoice)
- Age (created timestamp)
- Status (pending, expired)

### /In_Progress/
List active items:
- Task name
- Owner (agent)
- Started (timestamp)

### /Done/
Count by day (last 7 days)
