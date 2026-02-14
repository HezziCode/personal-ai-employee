# Inbox Categorization Rules

## Priority Decision Tree

```
Is it from unknown sender?
  YES → HIGH (needs verification)
  NO → Check content keywords

Contains urgent keywords? (payment, invoice, urgent, help, asap, client)
  YES → HIGH
  NO → Check amount/value

Transaction amount > $100?
  YES → HIGH
  NO → Check type

Is it promotional/newsletter?
  YES → LOW (archive)
  NO → MEDIUM (auto-plan)
```

## Priority Thresholds

| Factor | HIGH | MEDIUM | LOW |
|--------|------|--------|-----|
| Unknown sender | Always | - | - |
| Keywords | payment, urgent, help | question, info, fyi | newsletter, promo |
| Amount | > $100 | $10-100 | < $10 |
| Category | New client, new vendor | Existing contact | Subscription |

## Sender Reputation

Stored in `/Contacts.md`:
- **Trusted** (5+interactions): Auto-plan, low approval threshold
- **Known** (1-4 interactions): Medium approval threshold
- **New** (0 interactions): High priority, always approve

## Content Patterns

### High Priority Patterns
- `(?i)(payment|invoice|contract|signature|urgent|asap)`
- `(?i)(new (client|vendor|project))`
- `(?i)(error|failure|down|critical)`

### Low Priority Patterns
- `(?i)(newsletter|unsubscribe|confirm subscription)`
- `(?i)(receipt|confirmation|thank you)`
- `(?i)(read receipt|delivery|seen)`

## Action Routing

| Category | Action | Approval |
|----------|--------|----------|
| email | Reply/Forward | Human approval if HIGH |
| WhatsApp | Reply/Forward | Human approval if HIGH |
| file | Create task | Human approval if HIGH |
| transaction | Log + alert | Alert on > $100 |
| invoice | Create plan | Approval if > $500 |
