# Platinum Tier Workflow Guide

## Question: Do I need to do this manually? What will happen?

**Short Answer:**
- ✅ **Automatic (Cloud handles 24/7):** Email detection, draft creation, git sync
- ✅ **Automatic (Laptop handles):** Reading drafts from GitHub, executing approved items
- ⚠️ **Manual (You decide):** Approving items - moving files from Pending_Approval to Approved

---

## Complete Workflow Breakdown

### Phase 1: Email Arrives (AUTOMATIC - Cloud)
```
Email arrives at your Gmail
           ↓
Cloud app detects it (runs 24/7 on Render)
           ↓
Gmail Watcher extracts content
           ↓
Ralph Loop classifies it ("Invoice request", "Meeting", etc.)
           ↓
Creates draft file: vault/Pending_Approval/EMAIL_*.md
           ↓
Git sync pushes to GitHub (automatic every 5 min)
```

**What you do:** Nothing. Cloud handles this entirely.

---

### Phase 2: Approval Decision (MANUAL - Your Laptop)

When you open your laptop:

```bash
# Step 1: Get the cloud drafts
cd Hackathon-0
git pull origin main

# Step 2: Review what's waiting
ls vault/Pending_Approval/
```

You'll see files like:
- `EMAIL_2024-02-14_invoice_request.md`
- `EMAIL_2024-02-14_meeting_invite.md`

**Now you decide for each one:**

```bash
# If you APPROVE it:
mv vault/Pending_Approval/EMAIL_*.md vault/Approved/

# If you REJECT it:
mv vault/Pending_Approval/EMAIL_*.md vault/Done/  # or delete it
```

Then push your decision back to the cloud:
```bash
git add . && git commit -m "Approved 5 emails" && git push origin main
```

**What you do:** You read the drafts and decide Yes/No by moving files.

---

### Phase 3: Execution (MANUAL or AUTOMATIC - Your Laptop)

After you approve and push, you can execute manually OR the Ralph Loop can handle it.

#### Option A: Manual Execution (You run it now)
```bash
# Execute all approved items
python scripts/ralph_loop.py --vault ./vault --agent-mode local
```

The Ralph Loop will:
- Read each file from `vault/Approved/`
- Execute it (send the email, post to social, etc.)
- Move it to `vault/Done/`

#### Option B: Automatic Execution (Schedule it)
Use a task scheduler to run Ralph Loop automatically:

**Windows:**
```bash
# Open Task Scheduler
# Create task: Run python scripts/ralph_loop.py every 1 hour
```

**Mac/Linux:**
```bash
# Add to crontab (run every 1 hour)
0 * * * * cd /path/to/Hackathon-0 && python scripts/ralph_loop.py --vault ./vault --agent-mode local
```

---

## Timeline Example

### Day 1: Cloud Works, You Sleep
```
11:00 PM - You go to sleep
11:05 PM - Email arrives: "Send me invoice for Q1"
11:06 PM - Cloud detects it → creates draft → pushes to GitHub
          (You don't know yet, you're asleep)
11:07 PM - UptimeRobot pings /health to keep cloud alive
```

### Day 2: You Review and Approve
```
9:00 AM  - You wake up, open laptop
9:01 AM  - git pull origin main
9:02 AM  - Review: vault/Pending_Approval/EMAIL_invoice_q1.md
9:03 AM  - Decision: "Yes, send the invoice"
9:04 AM  - mv vault/Pending_Approval/EMAIL_invoice_q1.md vault/Approved/
9:05 AM  - git add . && git commit -m "Approved invoice" && git push origin main
9:06 AM  - Cloud pulls changes, sees Approved/ folder
```

### Day 2: Execution (Your Choice)
```
Option A: RIGHT NOW
9:06 AM  - python scripts/ralph_loop.py --vault ./vault --agent-mode local
9:07 AM  - Invoice sent ✅

Option B: SCHEDULED (runs automatically at 10:00 AM)
10:00 AM - Scheduled task runs Ralph Loop
10:01 AM - Invoice sent ✅
```

---

## What Happens at Each Step

### Cloud → Local: Git Pull
```
Cloud pushes:
├── vault/Pending_Approval/EMAIL_1.md
├── vault/Pending_Approval/EMAIL_2.md
└── vault/Pending_Approval/EMAIL_3.md

You run: git pull origin main

Your laptop now has:
├── vault/Pending_Approval/EMAIL_1.md
├── vault/Pending_Approval/EMAIL_2.md
└── vault/Pending_Approval/EMAIL_3.md
```

### You Approve: Manual Move
```
Before:
vault/Pending_Approval/EMAIL_invoice.md

You run: mv vault/Pending_Approval/EMAIL_invoice.md vault/Approved/

After:
vault/Approved/EMAIL_invoice.md
```

### Local → Cloud: Git Push
```
You run: git push origin main

Cloud now sees Approved/ folder has:
├── vault/Approved/EMAIL_invoice.md
└── Cloud can either execute or wait for next sync
```

### Execution: Ralph Loop
```
Ralph Loop reads: vault/Approved/EMAIL_invoice.md

It contains:
- Customer name, amount, due date
- Template for PDF invoice
- Gmail address to send to

Ralph Loop:
1. Generates PDF
2. Sends via Gmail API
3. Moves file: vault/Approved/EMAIL_invoice.md → vault/Done/EMAIL_invoice.md
4. Git syncs (Done/ folder updated)
```

---

## Summary: What's Automatic vs Manual

| Step | What Happens | Where | Who | Auto/Manual |
|------|--------------|-------|-----|------------|
| Email arrives | Detected | Cloud (Render) | Cloud App | ✅ Auto |
| Draft created | Classified & drafted | Cloud | Ralph Loop | ✅ Auto |
| Draft synced | Pushed to GitHub | Cloud | Git Sync | ✅ Auto |
| You review | See Pending_Approval/ | Your Laptop | You | ⚠️ Manual |
| You approve | Move to Approved/ | Your Laptop | You | ⚠️ Manual |
| Approval synced | Pushed to GitHub | Your Laptop | Git | ✅ Auto |
| Execution | Send email, post social | Your Laptop | Ralph Loop | ⚠️ Manual (can schedule) |
| Done | Move to Done/ | Your Laptop | Ralph Loop | ✅ Auto |

---

## The Bottom Line

**You only need to:**
1. **Review** - Read Pending_Approval folder (when you have time)
2. **Decide** - Move files to Approved or Done
3. **Push** - git push (1 command)

**Everything else is automatic:**
- Cloud detects emails 24/7
- Cloud creates drafts 24/7
- Cloud syncs via Git every 5 minutes
- Cloud stays alive via UptimeRobot
- Ralph Loop can execute on a schedule (cron/Task Scheduler)

**The Design:** Cloud handles heavy lifting (watching, drafting). You handle judgment (approval). Ralph Loop on laptop handles execution (when scheduled or triggered).

---

## Next Steps

### Immediate Test (Today)
```bash
# See what's in Pending_Approval
git pull origin main
ls -la vault/Pending_Approval/

# Count emails
ls vault/Pending_Approval/ | wc -l
```

### Full Workflow Test (Next Hour)
```bash
# 1. Review a draft
cat vault/Pending_Approval/EMAIL_*.md | head -50

# 2. Approve 1 email
mv vault/Pending_Approval/EMAIL_YOUR_CHOICE.md vault/Approved/

# 3. Push approval back
git add vault/Approved/ vault/Pending_Approval/
git commit -m "Approved 1 email for testing"
git push origin main

# 4. Execute (test)
python scripts/ralph_loop.py --vault ./vault --agent-mode local --dry-run

# 5. Actually execute
python scripts/ralph_loop.py --vault ./vault --agent-mode local
```

### Production Setup (This Week)
```bash
# Schedule Ralph Loop to run every hour (optional but recommended)

# On Windows: Use Task Scheduler GUI
# On Mac/Linux: Add to crontab
crontab -e
# Add: 0 * * * * cd /path/to/Hackathon-0 && python scripts/ralph_loop.py --vault ./vault --agent-mode local > /tmp/ralph.log 2>&1
```

---

## Troubleshooting

**Q: I pulled git but Pending_Approval is empty?**
A: Cloud hasn't found emails yet. Check:
- Render logs: https://dashboard.render.com
- `/health` endpoint: curl https://your-app.onrender.com/health
- Gmail credentials set in Render env vars
- UptimeRobot is pinging (keep cloud alive)

**Q: I approved a file but nothing happened?**
A: Ralph Loop hasn't run yet. Options:
- Run manually: `python scripts/ralph_loop.py --vault ./vault --agent-mode local`
- Set up scheduled execution (cron/Task Scheduler)
- Wait for you to manually trigger it

**Q: Cloud is processing 349 emails but I only see 10 in Pending_Approval?**
A: Some emails are in other folders:
- `vault/Done/` - Already processed
- `vault/In_Progress/cloud-agent/` - Being worked on
- `vault/Approved/` - You approved them
- `vault/Plans/` - Drafts for future tasks

Use: `find vault -name "*.md" -type f | wc -l` to see total files.

---

## Key Insight

The **Platinum Tier is designed so:**
- **Cloud works 24/7 without you** (always on, always watching)
- **You work when you want** (approve emails on your schedule)
- **Ralph Loop executes when needed** (on demand or scheduled)

You're in control. The cloud handles the boring stuff.
