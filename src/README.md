# src/ - AI Employee Implementation

Professional source code organization for Personal AI Employee system.

## 📁 Directory Structure

```
src/
├── __init__.py              # Main package exports
├── README.md                # This file
│
├── accounting/              # Odoo ERP Integration
│   ├── __init__.py
│   └── odoo_client.py       # Odoo XML-RPC API client
│
├── social/                  # Social Media Automation
│   ├── __init__.py
│   ├── twitter.py           # Twitter/X posting
│   ├── instagram.py         # Instagram posting
│   └── facebook.py          # Facebook posting (todo)
│
├── briefing/                # CEO Briefing Generation
│   ├── __init__.py
│   └── briefing.py          # Weekly business audit report
│
├── inbox/                   # Inbox Processing (todo)
│   ├── __init__.py
│   └── process.py
│
├── orchestration/           # Task Orchestration (todo)
│   ├── __init__.py
│   ├── orchestrator.py
│   └── ralph_loop.py        # Ralph Wiggum loop pattern
│
└── utils/                   # Utilities & Common Functions
    ├── __init__.py
    ├── logging.py           # Audit logging
    └── errors.py            # Error handling & retry logic
```

## 🚀 Usage

### Importing Modules

```python
# Direct imports
from src.accounting import OdooClient
from src.social import TwitterPoster, InstagramPoster
from src.briefing import generate_briefing

# Or use package imports
from src import OdooClient, TwitterPoster, InstagramPoster
```

### Examples

#### Odoo Accounting
```python
from src.accounting import OdooClient

client = OdooClient()
invoices = client.get_invoices()
revenue = client.get_revenue_summary()
```

#### Twitter Posting
```python
from src.social import TwitterPoster

poster = TwitterPoster()
result = poster.post("Hello World!", dry_run=True)
```

#### CEO Briefing
```python
from src.briefing import generate_briefing

briefing = generate_briefing("/path/to/vault")
print(briefing)
```

#### Error Handling
```python
from src.utils.errors import ErrorHandler, retry_with_backoff

@retry_with_backoff(max_attempts=3)
def risky_operation():
    # Will retry on TransientError
    pass
```

## 📝 Module Details

### accounting/odoo_client.py
- Connects to Odoo Community 19+ via XML-RPC
- Create invoices, track payments
- Query revenue and transaction data

### social/twitter.py
- Post tweets with Playwright automation
- Generate tweet drafts
- Save to vault for manual review

### social/instagram.py
- Post to Instagram with image
- Playwright automation
- Draft generation

### briefing/briefing.py
- Read from Odoo (revenue, invoices)
- Read from vault (tasks, approvals)
- Generate CEO briefing markdown

### utils/logging.py
- JSON audit logging
- Query logs by type/date/result
- Compliance-ready format

### utils/errors.py
- Custom error classes (Transient, Auth, Validation, Data, System)
- Retry decorator with exponential backoff
- Centralized error handling

## 🔒 Environment Variables (.env)

```env
# Odoo
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=user@example.com
ODOO_API_KEY=password

# Social Media
TWITTER_EMAIL=test@example.com
TWITTER_PASSWORD=password
INSTAGRAM_EMAIL=test@example.com
INSTAGRAM_PASSWORD=password

# Vault
VAULT_PATH=./vault
```

## 🧪 Testing

Run individual modules:

```bash
# Test Odoo
python -m src.accounting.odoo_client

# Test Twitter
python -m src.social.twitter --post "Hello" --dry-run

# Test Briefing
python -m src.briefing.briefing --save

# Test Logging
python -m src.utils.logging
```

## 📦 Dependencies

```
playwright>=1.40.0
python-dotenv>=1.0.0
requests>=2.31.0
```

Install:
```bash
pip install -r requirements.txt
```

## 🎯 Next Steps

- [ ] Implement `src/inbox/process.py` - Inbox triage
- [ ] Implement `src/orchestration/orchestrator.py` - Main orchestrator
- [ ] Implement `src/orchestration/ralph_loop.py` - Task loops
- [ ] Add `src/social/facebook.py` - Facebook posting
- [ ] Add comprehensive unit tests

## 📄 License

Part of Personal AI Employee Hackathon Project

---

*Last Updated: 2026-02-11*
