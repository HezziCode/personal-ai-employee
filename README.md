# AI Employee - Hackathon 0

> Your Personal AI Employee that runs your business on autopilot. It reads your emails, watches your WhatsApp, posts on socials, manages invoices, and keeps you updated - all while you sleep.

Built for **Panaversity Hackathon 0** | All 4 Tiers Complete: Bronze + Silver + Gold + **Platinum**

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

### Platinum - 24/7 Cloud Deployment
- [x] Cloud worker on Render.com (free tier, always alive)
- [x] FastAPI `/health` endpoint + UptimeRobot to prevent spindown
- [x] Cloud-local split: cloud does email triage + drafting, local does approvals & sends
- [x] Git-based vault sync (claim-by-move rule to prevent conflicts)
- [x] Agent modes: `cloud-agent` (draft-only) vs `local-agent` (execute)
- [x] Deployment via render.yaml or Dockerfile

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

## Platinum Tier: 24/7 Cloud Deployment

The AI Employee can now run on a cloud server (Render.com) 24/7 while your laptop handles approvals and final actions.

### Architecture: Cloud vs Local Split

```
CLOUD (Render.com - 24/7):          LOCAL (Your Laptop):
├── Gmail Watcher                    ├── WhatsApp Handler
├── Email Drafter                    ├── Approval Reviewer
├── Social Drafter                   ├── Final Sender
├── Ralph Loop (draft-only)          ├── Payment Handler
├── /health endpoint                 └── Dashboard Owner
└── Git Sync (push/pull vault)               |
         |                                   |
         └──── Git Vault Sync ───────────────┘
              (via GitHub)
```

### How It Works

1. **Cloud runs constantly**: Monitors emails, creates drafts, syncs vault
2. **Local approves**: You review drafts when ready, approve via git (move files)
3. **Git is the messenger**: Changes sync between cloud and local every 5 minutes
4. **Claim-by-move rule**: Files in `In_Progress/cloud-agent/` belong to cloud; files in `In_Progress/local-agent/` belong to you

### Quick Start: Deploy to Render

#### 1. Connect GitHub Repository
- Push this code to GitHub
- Go to https://dashboard.render.com
- Click "New +" → "Web Service"
- Connect your GitHub repo

#### 2. Deploy with render.yaml
```bash
# Option A: Use render.yaml (automatic)
# Render reads render.yaml and deploys automatically

# Option B: Manual Configuration
# Runtime: Python
# Build Command: pip install -r requirements.txt
# Start Command: uvicorn cloud.cloud_worker:app --host 0.0.0.0 --port $PORT
```

#### 3. Set Environment Variables in Render Dashboard
```
VAULT_PATH=./vault
AGENT_MODE=cloud
DRY_RUN=true
RALPH_CHECK_INTERVAL=300
GIT_SYNC_INTERVAL=300
GMAIL_CHECK_INTERVAL=120
```

#### 4. Add Secrets in Render Dashboard
- `GMAIL_CREDENTIALS`: Download from Google Cloud Console, save as base64
- `GIT_TOKEN`: GitHub personal access token (for vault syncing)

#### 5. Keep Alive with UptimeRobot
Render's free tier spins down after 15 min of inactivity. Solution: UptimeRobot pings `/health` every 5 minutes.

```bash
# Sign up (free): https://uptimerobot.com
# Add Monitor:
#   URL: https://your-app.onrender.com/health
#   Interval: 5 minutes
#   Alert: Email
```

#### 6. Set Up Git Sync
```bash
# On your local laptop:
cd Hackathon-0
git remote add cloud https://github.com/YOUR_ORG/Hackathon-0.git
git pull cloud main  # Get cloud drafts
```

#### 7. Understand the Workflow
See **[PLATINUM_WORKFLOW.md](./PLATINUM_WORKFLOW.md)** for detailed explanation of:
- What's automatic (cloud 24/7)
- What's manual (your approval decision)
- What you can schedule (Ralph Loop execution)
- Full timeline examples

**Quick Version:** Cloud detects emails → You approve → Ralph executes. [See Quick Reference →](./WORKFLOW_QUICK_REFERENCE.md)

### Troubleshooting

**Cloud not picking up emails?**
- Check Render logs: Dashboard → Your App → Logs
- Verify Gmail credentials are set in environment
- Check `/health` endpoint responds

**Git sync not working?**
- Verify `GIT_TOKEN` is set in Render
- Check vault has `.git/config` with origin remote
- Run manual test: `python cloud/git_sync.py ./vault cloud-agent`

**WhatsApp not working on cloud?**
- WhatsApp watchers don't run in cloud (only local)
- Cloud is email + social drafting only

### Files for Platinum Tier

```
Hackathon-0/
├── cloud/                         # New: Cloud worker package
│   ├── __init__.py
│   ├── cloud_worker.py            # FastAPI app + background threads
│   ├── git_sync.py                # Vault sync via Git
│   └── Dockerfile                 # Docker image (optional)
│
├── render.yaml                    # Render deployment blueprint
│
├── vault/
│   ├── In_Progress/
│   │   ├── cloud-agent/           # Files claimed by cloud
│   │   └── local-agent/           # Files claimed by local
│   └── Updates/                   # Cloud writes status updates here
│
└── scripts/ralph_loop.py          # Modified for agent_mode
    (Now supports cloud/local modes)
```

---

## Built By

**Huzaifa** - [@HezziCode](https://github.com/HezziCode)

Built for Panaversity Hackathon 0 | MIT License
