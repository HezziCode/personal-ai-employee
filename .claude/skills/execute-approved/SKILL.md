---
name: execute-approved
description: Use when executing approved actions from /Approved folder via MCP servers. Processes email sends, payments, social posts, and other external actions.
---

# Execute Approved Actions Skill

Execute human-approved actions through MCP servers.

## Workflow

1. **Scan** `/Approved/` folder for approval files
2. **Parse** action type and parameters from YAML frontmatter
3. **Validate** all required fields present
4. **Execute** via appropriate MCP server:
   - Email MCP: send_email
   - Browser MCP: perform_payment, fill_form
   - Social MCP: post_tweet, post_facebook, post_instagram
   - Odoo MCP: create_invoice, record_payment
5. **Log** result to `/Logs/executed-YYYY-MM-DD.json`
6. **Move** file: `/Approved/...` → `/Done/...`

## Approval File Format

```yaml
---
type: email | payment | social_post | invoice
action_id: UNIQUE_ID
created: ISO timestamp
expires: ISO timestamp (24h from creation)
status: approved
---

## Action Details
[Specific parameters for action type]
```

## Error Handling

- **Transient errors** (timeout, rate limit): Retry with exponential backoff
- **Auth errors** (expired token): Alert human, pause execution
- **Validation errors** (missing field): Quarantine file, alert human
- **Success**: Move to `/Done/`, update Dashboard.md

## MCP Servers Invoked

- `email-mcp` - Gmail, send emails
- `browser-mcp` - Payment forms, web interactions
- `social-mcp` - Twitter, Facebook, Instagram posts
- `odoo-mcp` - Accounting operations

## Script Location

`~/.claude/skills/execute-approved/scripts/executor.py`

## References

See `references/mcp_methods.md` for full MCP API reference.
