---
name: twitter-posting
description: Generates and posts tweets/threads to Twitter (X). Use when user asks to "tweet about", "post on Twitter", "X post", or "create thread about". Automatically drafts engaging content following Twitter best practices, saves for approval, and posts via Playwright automation.
---

# Twitter/X Posting Skill

Generate and post content to Twitter/X with human approval.

## When to Use

Trigger when user requests:
- "Tweet about [topic]"
- "Post on Twitter about [topic]"
- "Create X post about [topic]"
- "Thread about [topic]"

## Process

1. **Read Context**
   - `vault/Business_Goals.md` - Brand voice
   - `vault/Dashboard.md` - Recent activity

2. **Generate Content**
   - Single tweet: 280 chars max
   - Thread: 3-5 connected tweets
   - Hashtags: 2-3 relevant

3. **Save Draft**
   - Location: `vault/Social_Media/Twitter_Drafts/`
   - Filename: `YYYY-MM-DD_[topic].md`

4. **On Approval**
   - Execute via `scripts/twitter_poster.py`
   - Log result in Logs/

## Tweet Guidelines

### Single Tweet
- 200-270 characters ideal
- Hook in first line
- One clear message
- 2-3 hashtags max
- Optional emoji (1-2)

### Thread
- Tweet 1: Hook + premise
- Tweets 2-4: Main points
- Final tweet: CTA + hashtags

## Output Format

```markdown
---
type: twitter_draft
created: [timestamp]
format: single|thread
status: pending
---

# Twitter Draft: [Topic]

## Tweet
[Content here - 280 char max]

## Hashtags
#Tag1 #Tag2 #Tag3

---
Move to Approved/ to post.
```

## Safety

- Always draft first (no auto-post)
- Human reviews before posting
- Rate limit: 3 tweets/day max
- No controversial content

## Scripts

Use `scripts/twitter_poster.py` for Playwright automation.
