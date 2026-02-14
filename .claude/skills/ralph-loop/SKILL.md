---
name: ralph-loop
description: Use when launching autonomous multi-step task completion with continuous iteration until task completion or max iterations reached.
---

# Ralph Wiggum Loop Skill

Keep Claude iterating on a task until it completes successfully or reaches max attempts.

## How It Works

1. **Setup** - Create state file with task prompt
2. **Iterate** - Claude works on task
3. **Check** - Stop hook checks: Is task done?
   - YES (found `TASK_COMPLETE` promise or file moved to `/Done/`) → Exit
   - NO → Re-inject prompt, Claude continues
4. **Repeat** - Up to `--max-iterations` times

## Completion Strategies

### Promise-Based (Simple)
Claude outputs: `<promise>TASK_COMPLETE</promise>`

Example: Process 5 emails, output `TASK_COMPLETE` when all 5 moved to `/Done/`.

### File-Movement-Based (Advanced)
Stop hook detects when task file moves from `/In_Progress/<agent_id>/` to `/Done/`.

More reliable because completion is natural part of workflow.

## Usage

```bash
claude-code /ralph-loop \
  "Process all files in /Needs_Action, move to /Done when complete" \
  --completion-promise "TASK_COMPLETE" \
  --max-iterations 10 \
  --task-name "Process Inbox" \
  --vault-path ~/AI_Employee_Vault
```

## Loop Invariants

- Previous outputs visible to Claude (shows failures, progress)
- Vault state updates between iterations (Claude sees new files)
- Stop hook validates completion before exit
- Logs all iterations to `/Logs/ralph-loop-YYYY-MM-DD.json`

## When to Use

- Multi-step processes: "Process inbox, create plans, execute approvals"
- Error recovery: "Retry failed payments with backoff"
- Batch operations: "Generate 10 social media posts"
- Never: Single-step decisions, real-time interactions

## Script Location

`~/.claude/skills/ralph-loop/scripts/ralph_loop.py`

## References

See `references/stop_hook_pattern.md` for implementation details.
