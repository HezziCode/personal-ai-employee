---
name: facebook-instagram
description: Generates and posts content to Facebook and Instagram. Use when user asks to "post on Facebook", "Instagram post", "FB post", or "social media post". Creates drafts for both platforms with appropriate formatting, saves for approval, and posts via Meta Graph API.
---

# Facebook & Instagram Posting Skill

Generate and post content to Facebook and Instagram using the official Meta Graph API.

## When to Use

Trigger when user requests:
- "Post on Facebook about [topic]"
- "Instagram post about [topic]"
- "FB post about [topic]"
- "Create social media post"

## Process

1. **Read Context**
   - `vault/Business_Goals.md` - Brand voice
   - `vault/Dashboard.md` - Recent activity

2. **Generate Content**
   - Facebook: Long-form allowed (up to 63k chars)
   - Instagram: Caption + hashtags (2200 chars) + requires image URL

3. **Save Draft**
   - Facebook: `vault/Social_Media/Facebook_Drafts/`
   - Instagram: `vault/Social_Media/Instagram_Drafts/`

4. **On Approval**
   - Execute via `scripts/fb_ig_poster.py --platform facebook --content "..."`
   - Or: `scripts/fb_ig_poster.py --platform instagram --content "..." --image-url "..."`
   - Uses Meta Graph API (100% reliable, no browser automation)
   - Log result in Logs/

## API Details

### Facebook Graph API
- Endpoint: `POST https://graph.facebook.com/v19.0/{page_id}/feed`
- Auth: Page Access Token with `pages_manage_posts` permission
- Free tier, no rate limit issues for normal use

### Instagram Graph API
- Step 1: Create container: `POST https://graph.facebook.com/v19.0/{ig_account_id}/media`
- Step 2: Publish: `POST https://graph.facebook.com/v19.0/{ig_account_id}/media_publish`
- Requires: Business/Professional Instagram account linked to Facebook Page
- Requires: Publicly accessible image URL

## Environment Variables Required

```
FACEBOOK_PAGE_ID=your_page_id
FACEBOOK_PAGE_ACCESS_TOKEN=your_page_token
FACEBOOK_USER_ACCESS_TOKEN=your_user_token
INSTAGRAM_BUSINESS_ACCOUNT_ID=your_ig_id  # For Instagram
```

## Platform Guidelines

### Facebook
- Length: 100-500 words ideal
- Engaging question or story
- 2-3 hashtags max
- Call-to-action at end
- Emojis: moderate use

### Instagram
- Caption: 150-300 words
- 20-30 hashtags (in first comment or end)
- Strong first line (hook)
- Line breaks for readability
- Emojis: more acceptable
- Image required (publicly accessible URL)

## Output Format

```markdown
---
type: facebook_draft | instagram_draft
created: [timestamp]
platform: facebook | instagram
status: pending
---

# [Platform] Draft: [Topic]

## Caption/Post
[Content here]

## Hashtags
#Tag1 #Tag2 ...

---
Move to Approved/ to post.
```

## Safety

- Always draft first
- Human reviews before posting
- Rate limit: 2 posts/day/platform
- No controversial content
- Follow platform guidelines
- Audit logging for all actions
