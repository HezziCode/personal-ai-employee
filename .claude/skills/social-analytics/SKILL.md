---
name: social-analytics
description: Use when analyzing social media engagement, generating post summaries, or creating performance reports from Twitter, Facebook, and Instagram metrics.
---

# Social Analytics Skill

Generate engagement reports and summaries from multi-platform social media activity.

## Platforms Supported

- **Twitter/X**: API v2, fetch tweets, replies, engagement metrics
- **Facebook**: Graph API, post performance, reach, comments
- **Instagram**: Graph API, likes, comments, follower growth

## Workflow

1. **Fetch** metrics from each platform via MCP
2. **Aggregate** by date, post type, engagement rate
3. **Analyze**:
   - Best performing content (engagement, reach, conversion)
   - Audience growth trends
   - Engagement rate vs historical average
   - Content gaps or opportunities
4. **Report** to `/Social/Analytics_YYYY-MM-DD.md`

## Output Format

```markdown
# Social Media Summary - Week of YYYY-MM-DD

## Performance Overview
- Total impressions: X
- Total engagements: X
- Average engagement rate: X%

## By Platform
### Twitter/X
- Tweets posted: N
- Top tweet: [content] (X retweets, Y likes)
- Follower change: +Z

### Facebook
- Posts: N
- Best post: [content] (X reactions, Y comments)
- Reach: X

### Instagram
- Posts: N
- Average likes: X
- Top post: [content] (X likes, Y comments)

## Insights
- [Top performing content type]
- [Best time to post]
- [Engagement trends]

## Recommendations
- Post more about [topic]
- Test [format]
- Engage with [audience segment]
```

## Script Location

`~/.claude/skills/social-analytics/scripts/fetch_analytics.py`

## References

- `references/platform_apis.md` - API endpoints and auth
- `references/engagement_metrics.md` - Metric definitions
