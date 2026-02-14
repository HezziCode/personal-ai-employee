---
name: process-inbox
description: Use when processing /Needs_Action folder to triage messages, emails, files, and transactions into actionable plans with priority levels and approval routing.
---

# Process Inbox Skill

Autonomously triage and categorize incoming items from Watchers into actionable tasks.

## Workflow

1. **Scan** `/Needs_Action/` folder for new items
2. **Categorize** by type (email, WhatsApp, file, transaction)
3. **Prioritize** based on keywords, sender reputation, and rules
4. **Create Plans** in `/Plans/` with suggested actions
5. **Route Approvals** for sensitive items to `/Pending_Approval/`
6. **Archive** processed items to `/Done/`

## Input Sources

- `/Needs_Action/*.md` - Items created by Watchers
- `/Company_Handbook.md` - Rules for prioritization
- `/Contacts.md` - Known senders database

## Output Files

Creates:
- `/Plans/PLAN_<type>_<id>_<sender>.md` - Action plan
- `/Pending_Approval/APPROVAL_<type>_<id>.md` - Approval request (if needed)

Moves:
- `/Needs_Action/...` → `/Done/...` after processing

## Priority Rules

**High Priority** (require approval):
- From unknown senders
- Containing keywords: "payment", "invoice", "urgent", "help", "asap"
- Transactions > $100
- New WhatsApp group mentions

**Medium Priority** (auto-plan, no approval):
- From known contacts
- Informational messages
- Follow-up questions

**Low Priority** (auto-archive):
- Marketing/newsletters
- Subscriptions confirmations
- Read receipts

## Script Location

`~/.claude/skills/process-inbox/scripts/process_inbox.py`

## References

See `references/categorization_rules.md` for full decision tree.
