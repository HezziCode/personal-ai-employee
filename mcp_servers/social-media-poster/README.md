# Social Media Poster MCP Server

Unified automation system for posting to Twitter, Facebook, Instagram, and LinkedIn with human-in-the-loop approval workflow.

## Architecture

```
Social_Media/
├── Twitter_Drafts/       ← New Twitter drafts saved here
├── Facebook_Drafts/      ← New Facebook drafts saved here
├── Instagram_Drafts/     ← New Instagram drafts saved here
├── LinkedIn_Drafts/      ← New LinkedIn drafts saved here
├── Approved/             ← Awaiting human review (HITL)
└── Posted/               ← Successfully posted content

Workflow:
1. Skill generates draft → Social_Media/*_Drafts/
2. social_media_watcher.py detects new draft → creates approval request in Approved/
3. Human reviews in Obsidian → approves by keeping file in Approved/
4. Cron job (every 10 min) runs social_media_poster.py --process-approved
5. Automation executes post → moves to Posted/ on success
6. Logs recorded in vault/Logs/social_media_YYYYMMDD.jsonl
```

## Components

### 1. Social Media Poster (MCP Server)
**File**: `social_media_poster.py`

Main executor that:
- Reads approved posts from `Approved/` folder
- Authenticates with each platform (Twitter, Facebook, LinkedIn)
- Posts content using Playwright automation
- Logs results to `vault/Logs/`
- Moves successful posts to `Posted/`

**Usage**:
```bash
# Process approved posts (runs via cron every 10 minutes)
python social_media_poster.py --vault /path/to/vault --process-approved

# Dry run (test without posting)
python social_media_poster.py --vault /path/to/vault --process-approved --dry-run
```

### 2. Social Media Watcher
**File**: `watchers/social_media_watcher.py`

Monitors draft folders for new content:
- Watches all `*_Drafts/` folders
- Auto-creates approval requests when new draft is detected
- Moves draft to `Posted/` folder after approval request
- Enables real-time workflow

**Usage**:
```bash
python watchers/social_media_watcher.py --vault /path/to/vault
```

### 3. Scheduling
**Cron Job**: Every 10 minutes
```
*/10 * * * * cd "/path/to/project" && uv run python mcp_servers/social-media-poster/social_media_poster.py --vault "/path/to/vault" --process-approved
```

## Credentials Required

Add to `.env`:
```
TWITTER_EMAIL=your_email@gmail.com
TWITTER_PASSWORD=your_password
FACEBOOK_EMAIL=your_email@gmail.com
FACEBOOK_PASSWORD=your_password
ODOO_URL=http://localhost:8069
ODOO_DB=ai_employee
ODOO_USERNAME=username
ODOO_API_KEY=api_key
```

## How It Works

### Creating a Post

1. **Via Skill** (Recommended):
   ```
   User: "Tweet about launching new AI features"
   → twitter-posting skill generates draft
   → Draft saved to vault/Social_Media/Twitter_Drafts/
   → social_media_watcher detects it
   → Approval request created in Approved/
   ```

2. **Manual Draft**:
   - Create markdown file in `Social_Media/Twitter_Drafts/`
   - Watcher will auto-create approval request

### Approving a Post

1. Open Obsidian vault
2. Go to `Social_Media/Approved/`
3. Review the post content
4. **To post**: Leave file in Approved/ (cron will execute)
5. **To reject**: Delete the file

### Automation Flow

```
Cron runs every 10 minutes:
  1. Check vault/Social_Media/Approved/ for posts
  2. For each post:
     a. Parse platform and content
     b. Authenticate with platform
     c. Execute post using Playwright
     d. On success: Move to Posted/, log result
     e. On failure: Keep in Approved/, log error
```

## Platforms

### Twitter
- **Automation**: Full Playwright automation with session persistence
- **Limits**: 280 characters, threads supported
- **Session**: Stored in `playwright/.auth/twitter_session`
- **Status**: ✅ Working

### Facebook
- **Automation**: Full Playwright automation
- **Limits**: Up to 63,000 characters, images supported
- **Session**: Stored in `playwright/.auth/facebook_session`
- **Status**: ✅ Working

### Instagram
- **Method**: Meta Business Suite recommended (web automation limited)
- **Note**: Instagram web blocks direct posting; use Meta Business Suite API or mobile app
- **Fallback**: Draft created, manual posting required
- **Status**: ⚠️ Draft-only (API integration recommended)

### LinkedIn
- **Automation**: Via existing linkedin-poster MCP server
- **Limits**: 3,000 characters, documents/images supported
- **Status**: ✅ Working

## Logs

All posting activity logged to `vault/Logs/social_media_YYYYMMDD.jsonl`:

```json
{
  "timestamp": "2026-02-11T12:30:45.123456",
  "platform": "twitter",
  "status": "posted",
  "draft": "launch_announcement"
}
```

## Rate Limiting (Recommended)

Add to approval workflow:
- Max 2 posts per platform per day
- Space posts 1 hour apart
- Monitor logs for posting frequency

## Testing

### Dry Run (No Actual Posts)
```bash
python social_media_poster.py --vault vault --process-approved --dry-run
```

### Manual Test
```bash
# Create test draft
echo "Testing Twitter automation! 🚀" > vault/Social_Media/Twitter_Drafts/test_tweet.md

# Watcher will create approval request automatically
# Then approve and cron will post
```

## Troubleshooting

### Posts not executing
- Check: `tail -f /tmp/social_media_poster.log`
- Verify credentials in `.env`
- Check for files in `Approved/` folder

### Playwright timeout errors
- Increase timeout values in script
- Check internet connection
- Verify platform credentials are correct

### Instagram posting not working
- This is expected (web limitation)
- Use Meta Business Suite API instead
- Or post manually via Instagram app

## Integration with Skills

Each posting skill works with this system:

1. **twitter-posting**: Generates draft → triggers watcher → creates approval
2. **facebook-instagram**: Generates drafts → triggers watcher → creates approvals
3. **linkedin-drafting**: (Already exists, still works via skill)

## Next Steps

1. ✅ Set up credentials in `.env`
2. ✅ Cron job configured to run every 10 min
3. Test by creating a draft post:
   ```bash
   python -c "
   from pathlib import Path
   draft = Path('vault/Social_Media/Twitter_Drafts/test.md')
   draft.write_text('Test tweet from AI Employee! 🤖')
   "
   ```
4. Monitor approval folder and cron logs

## Files

- `social_media_poster.py` - Main MCP server (execution)
- `watchers/social_media_watcher.py` - Draft monitoring and approval requests
- `README.md` - This file
