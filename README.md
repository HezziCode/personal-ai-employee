# AI Employee - Hackathon 0

> Your Personal AI Employee that runs your business on autopilot. It reads your emails, watches your WhatsApp, posts on socials, manages invoices, and keeps you updated - all while you sleep.

Built for **Panaversity Hackathon 0** | All 3 Tiers Complete: Bronze + Silver + Gold

---

## What It Does

Drop a file, receive an email, get a WhatsApp message - your AI Employee picks it up, figures out what to do, and either handles it automatically or asks you first.

```
You get a WhatsApp: "Send me the invoice for January"
     |
     v
AI Employee detects it --> Creates action item --> Routes to approval
     |
     v
You approve --> AI sends the invoice via Odoo --> Done. You didn't lift a finger.
```

---

## The Stack

| Layer | What | Tech |
|-------|------|------|
| **Perception** | Watches Gmail, WhatsApp, Files | Python Watchers + Green API |
| **Brain** | Classifies, prioritizes, routes | Claude Code + Ralph Loop |
| **Action** | Sends emails, posts on social, creates invoices | MCP Servers + APIs |
| **Memory** | Stores everything in markdown | Obsidian Vault |
| **Accounting** | Invoices, payments, revenue tracking | Odoo Community 19+ |

---

## Tier Progress

### Bronze - Foundation
- [x] Obsidian vault with folder-based workflow
- [x] Dashboard + Company Handbook
- [x] File watcher (drop file -> auto-process)
- [x] Claude Code integration

### Silver - Communication Layer
- [x] Gmail watcher (auto-detect & categorize emails)
- [x] WhatsApp watcher (Green API - real-time message detection)
- [x] Email sending via Gmail API
- [x] Human-in-the-loop approval flow

### Gold - Full Automation
- [x] Ralph Wiggum Loop (autonomous task execution engine)
- [x] Odoo ERP integration (invoices, payments, customers)
- [x] Weekly CEO Briefing generator
- [x] Social media posting (Twitter, Facebook, Instagram, LinkedIn)
- [x] Cross-domain integration (everything talks to everything)

---

## How It Works

```
                    +-----------------+
                    |   WATCHERS      |
                    | Gmail | WhatsApp|
                    | Files | Social  |
                    +--------+--------+
                             |
                             v
                    +--------+--------+
                    |  OBSIDIAN VAULT |
                    |   Needs_Action/ |
                    +--------+--------+
                             |
                    +--------+--------+
                    |  RALPH LOOP     |
                    |  Classify -->   |
                    |  Route -->      |
                    |  Execute        |
                    +---+--------+----+
                        |        |
               Safe     |        |  Sensitive
               Auto     |        |  Needs OK
                  v     |        v
            +-----+--+  |  +----+----------+
            | Done/  |  |  | Pending_      |
            +--------+  |  | Approval/     |
                        |  +-------+-------+
                        |          |
                        |    Human Approves
                        |          |
                        v          v
                    +---+----------+---+
                    |   MCP SERVERS    |
                    | Email | WhatsApp |
                    | Odoo  | Social   |
                    +------------------+
```

---

## Quick Start

```bash
# 1. Clone & install
git clone <repo-url>
cd Hackathon-0
uv sync

# 2. Setup .env (copy from .env and fill in your keys)

# 3. Run watchers
uv run python watchers/file_watcher.py --vault ./vault
uv run python watchers/gmail_watcher.py --vault ./vault
uv run python watchers/whatsapp_watcher.py --vault ./vault

# 4. Run the Ralph Loop (autonomous processor)
uv run python scripts/ralph_loop.py --vault ./vault --dry-run    # safe test
uv run python scripts/ralph_loop.py --vault ./vault               # live mode
```

---

## Project Structure

```
Hackathon-0/
├── vault/                     # Obsidian Vault (the brain)
│   ├── Inbox/                 # Drop files here
│   ├── Needs_Action/          # Auto-detected items
│   ├── Pending_Approval/      # Waiting for human OK
│   ├── Approved/              # Ready to execute
│   ├── Done/                  # Completed items
│   ├── Accounting/            # Odoo invoices
│   ├── Briefings/             # CEO weekly reports
│   ├── Dashboard.md           # Live status
│   └── Company_Handbook.md    # AI behavior rules
│
├── watchers/                  # Perception layer
│   ├── base_watcher.py        # Abstract base class
│   ├── file_watcher.py        # File system monitor
│   ├── gmail_watcher.py       # Gmail API integration
│   └── whatsapp_watcher.py    # WhatsApp via Green API
│
├── scripts/                   # Orchestration
│   ├── ralph_loop.py          # Autonomous task processor
│   └── orchestrator.py        # Master coordinator
│
├── mcp_servers/               # Action layer
│   ├── email-sender/          # Gmail send API
│   ├── odoo-mcp/              # Odoo ERP client
│   ├── social-media-poster/   # Twitter/FB/Insta
│   └── linkedin-poster/       # LinkedIn automation
│
└── src/                       # Core modules
    ├── accounting/             # Odoo client
    ├── briefing/               # CEO briefing generator
    ├── social/                 # Social media posting
    └── utils/                  # Error handling & logging
```

---

## Key Features

**Human-in-the-Loop** - Sensitive actions (payments, emails to new contacts, social posts) always need your approval. Safe actions (file categorization, spam deletion) run automatically.

**Ralph Wiggum Loop** - Autonomous processor that keeps looping until all tasks are done. Classify -> Route -> Execute -> Repeat.

**Multi-Channel** - Gmail, WhatsApp, Twitter, Facebook, Instagram, LinkedIn - all connected through one system.

**Odoo ERP** - Real accounting integration. Create invoices, track payments, generate revenue reports.

**CEO Briefing** - Weekly automated report showing completed tasks, revenue, bottlenecks, and action items.

---

## Built By

**Huzaifa** - [@HezziCode](https://github.com/HezziCode)

Built for Panaversity Hackathon 0 | MIT License
