---
name: odoo-accounting
description: Use when creating, reading, or updating accounting records in Odoo Community ERP via JSON-RPC API integration. Handles invoices, payments, expenses, and business transactions.
---

# Odoo Accounting Integration Skill

Manage business accounting through Odoo Community ERP with MCP server integration.

## Architecture

- **Odoo Instance**: Local or cloud-hosted (Community Edition v19+)
- **MCP Server**: Node.js/Python server wrapping Odoo JSON-RPC API
- **Auth**: Username + API key (stored in .env, never in vault)
- **Protocol**: JSON-RPC 2.0 over HTTPS

## Common Operations

### Create Invoice
```
POST /api/invoice/create
- customer: string
- amount: number
- description: string
- due_date: ISO date
```

### Record Payment
```
POST /api/payment/record
- invoice_id: number
- amount: number
- payment_method: enum (bank, cash, etc)
- reference: string
```

### Fetch Transactions
```
GET /api/transactions?start_date=YYYY-MM-DD&end_date=YYYY-MM-DD
Returns: [{ id, date, description, amount, category }]
```

## Workflow

1. **Connect** to Odoo via MCP (verify credentials in .env)
2. **Query** current data (invoices, payments, expenses)
3. **Create/Update** records as needed
4. **Log** all changes to `/Logs/odoo-YYYY-MM-DD.json`
5. **Sync** to vault: `/Accounting/Odoo_Snapshot.md`

## Security

- Credentials: `.env` file (ODOO_URL, ODOO_USERNAME, ODOO_API_KEY)
- DRY_RUN mode: Test all operations before commit
- Rate limiting: Max 50 API calls per minute
- Approval required: Invoices > $500, new payment methods

## Script Location

`~/.claude/skills/odoo-accounting/scripts/odoo_mcp.py`

## References

- `references/odoo_api.md` - Full JSON-RPC documentation
- `references/chart_of_accounts.md` - Your business chart of accounts
