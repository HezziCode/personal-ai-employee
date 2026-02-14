# Quick Reference: Platinum Workflow

## Do I Need to Do This Manually?

**Short Version:**
- ✅ Cloud detects emails and creates drafts **24/7 automatically**
- ⚠️ **You review and approve** (manual decision)
- ✅ Ralph Loop executes approved items (manual trigger, can be scheduled)

---

## What You Do vs What's Automatic

### Automatic (Cloud Running on Render 24/7)
```
Email arrives → Detected → Drafted → Synced to GitHub
```
**Result:** Files in `vault/Pending_Approval/` on GitHub

---

### Manual (Your Laptop - When You Want)
```
git pull → Review files → Approve (move to Approved/) → git push
```
**Result:** Approved files in GitHub under `vault/Approved/`

---

### Automatic OR Manual (Your Laptop - You Choose)
```
Ralph Loop executes: Reads Approved/ → Sends emails/posts/etc. → Moves to Done/
```

**Two Options:**
1. **Manual:** Run whenever you want
   ```bash
   python scripts/ralph_loop.py --vault ./vault --agent-mode local
   ```

2. **Scheduled:** Runs automatically (e.g., every hour)
   ```bash
   # Linux/Mac: crontab -e
   0 * * * * cd /path/to/Hackathon-0 && python scripts/ralph_loop.py --vault ./vault --agent-mode local

   # Windows: Task Scheduler GUI
   ```

---

## Today's Example: 349 Emails

**What's happening right now:**
- ✅ Cloud detected 349 emails (24/7, no action needed)
- ✅ Ralph Loop drafted 349 items (automatic)
- ✅ Pushed to GitHub (automatic via git sync)

**What YOU need to do:**
1. `git pull origin main` → Get the 349 drafts
2. Review them: `ls vault/Pending_Approval/`
3. Approve some: `mv vault/Pending_Approval/EMAIL_*.md vault/Approved/`
4. `git push origin main` → Tell cloud you approved them
5. Execute: `python scripts/ralph_loop.py --vault ./vault --agent-mode local`

**That's it.** Cloud handles the rest.

---

## The Three Phases Explained

| Phase | What | Automatic? | You Do |
|-------|------|------------|--------|
| **Detection** | Cloud sees emails 24/7 | ✅ Yes | Nothing |
| **Drafting** | Ralph Loop creates plans | ✅ Yes | Nothing |
| **Approval** | You review & decide | ⚠️ No | Review & move files |
| **Execution** | Send/post/execute | ⚠️ No (optional) | Run script or schedule |

---

## One-Command Workflow

After your cloud has been running:

```bash
# 1. Get cloud drafts
git pull origin main

# 2. See what's waiting
ls vault/Pending_Approval/ | head -5

# 3. Approve everything (danger: check first!)
mv vault/Pending_Approval/* vault/Approved/

# 4. Tell cloud
git add . && git commit -m "Approved all" && git push

# 5. Execute (send emails, post, etc.)
python scripts/ralph_loop.py --vault ./vault --agent-mode local
```

Done. Everything moves to `vault/Done/`.

---

## Real World Timeline

```
Day 1, 11 PM: You sleep
  → Email arrives
  → Cloud detects (24/7)
  → Ralph drafts it
  → GitHub updated

Day 2, 9 AM: You wake up
  → git pull
  → Review drafts
  → Approve 5, reject 2
  → git push

Day 2, 10 AM: You run execute (or it runs on schedule)
  → 5 approved items processed
  → Moved to Done/
  → Complete
```

**You only worked 5 minutes. Cloud did the rest.**

---

## What Gets Created/Updated

### Cloud Creates (automatic):
- `vault/Pending_Approval/EMAIL_*.md`
- `vault/In_Progress/cloud-agent/` (items being worked on)
- Pushes to GitHub every 5 min

### You Manage (manual):
- Move files: `Pending_Approval/` → `Approved/` or `Done/`
- `git push` to tell cloud

### Ralph Loop Updates (when executed):
- Moves files: `Approved/` → `Done/`
- Email sent, payment made, post published
- `git push` to sync

---

## Key Points

🎯 **You only decide YES or NO** (approve/reject). Everything else is automatic.

🎯 **Cloud never sends anything** (cloud mode = draft-only). Your laptop executes.

🎯 **Git is the messenger** between cloud and laptop. Every 5 min they sync.

🎯 **You control timing** - approve when ready, execute when you want.

🎯 **Can be fully automated** - schedule Ralph Loop and you don't touch anything.

---

## Next Steps

**Right Now:**
```bash
git pull origin main
ls vault/Pending_Approval/ | wc -l  # How many emails?
cat vault/Pending_Approval/EMAIL_*.md | head -100  # Read first one
```

**Today:**
```bash
# Approve 1-5 emails
mv vault/Pending_Approval/EMAIL_PICK_ONE.md vault/Approved/
git add . && git push
python scripts/ralph_loop.py --vault ./vault --agent-mode local
```

**This Week:**
```bash
# Set up scheduled execution (optional but recommended)
# Linux: crontab -e
# Windows: Task Scheduler GUI
```

Done. Welcome to the Platinum Tier! 🚀
