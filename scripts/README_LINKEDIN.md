# LinkedIn Post Generator - Quick Guide

Simple command to generate LinkedIn post drafts.

---

## Usage

### Windows (PowerShell)
```powershell
cd "D:\Side Projects\gh-hackthone\Hackathon-0\scripts"
.\linkedin_post.ps1 "your topic here"
```

### WSL/Linux
```bash
cd /mnt/d/Side\ Projects/gh-hackthone/Hackathon-0/scripts
./linkedin_post.sh "your topic here"
```

---

## Examples

```powershell
# Generate post about hackathon
.\linkedin_post.ps1 "AI Employee Hackathon Progress"

# Generate post about new service
.\linkedin_post.ps1 "launching automation consulting"

# Generate weekly update
.\linkedin_post.ps1 "weekly business update"
```

---

## What It Does

1. Takes your topic
2. Reads Business_Goals.md and Dashboard.md for context
3. Calls Claude Code to generate professional post
4. Saves draft in `vault/Social_Media/LinkedIn_Drafts/`
5. Ready to copy-paste to LinkedIn!

---

## Setup Alias (Optional - Windows)

Add to your PowerShell profile for quick access:

```powershell
# Open profile
notepad $PROFILE

# Add this line:
function linkedin-post {
    & "D:\Side Projects\gh-hackthone\Hackathon-0\scripts\linkedin_post.ps1" $args
}

# Now you can run from anywhere:
linkedin-post "my topic"
```

---

## Setup Alias (WSL/Linux)

Add to your `.bashrc` or `.zshrc`:

```bash
# Open bashrc
nano ~/.bashrc

# Add this line:
alias linkedin-post='/mnt/d/Side\ Projects/gh-hackthone/Hackathon-0/scripts/linkedin_post.sh'

# Reload
source ~/.bashrc

# Now you can run from anywhere:
linkedin-post "my topic"
```

---

## Output Location

Drafts saved in:
```
vault/Social_Media/LinkedIn_Drafts/YYYY-MM-DD_topic.md
```

Open in Obsidian to review and post!

---

*Part of AI Employee Silver Tier*
