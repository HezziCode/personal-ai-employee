# Personal AI Employee Constitution

## Core Principles

### I. Autonomous Yet Accountable
The AI Employee operates 24/7 to automate personal and business affairs, but humans remain accountable. Every action must be logged, reviewable, and subject to human oversight via HITL (Human-in-the-Loop) controls.

### II. Skills-First Architecture
All AI functionality is implemented as Agent Skills (SKILL.md format). Skills are self-contained, independently testable, and composable. No hardcoded logic in orchestrators.

### III. Local-First & Privacy-Centric
Data lives locally in Obsidian vault by default. External APIs are used only when necessary. Credentials never stored in vault; always via .env or secure managers.

### IV. Three-Layer Perception → Reasoning → Action
- **Perception**: Python Watchers detect changes in Gmail, WhatsApp, Bank, Files
- **Reasoning**: Claude Code reads vault state and creates Plans
- **Action**: MCP servers execute approved actions (email, payments, social posts)

### V. Human-in-the-Loop for Sensitive Actions
Approval thresholds:
- Payments > $50: Always require approval
- New email recipients: Require approval
- Social posts to new platforms: Require approval
- Auto-approve known patterns only

### VI. Obsidian Vault as Source of Truth
All state stored as markdown:
- `/Needs_Action/` - Triggered by Watchers
- `/Plans/` - Created by Claude (pending approval)
- `/Pending_Approval/` - Awaiting human decision
- `/Approved/` - Ready for action
- `/Done/` - Completed tasks logged
- `/Logs/` - All action audit trails (JSON)

### VII. Error Recovery & Graceful Degradation
Transient errors trigger exponential backoff retries. Authentication failures pause operations with human alert. Missing components degrade gracefully (e.g., Gmail API down → queue locally, process later).

### VIII. Audit Logging Non-Negotiable
Every action logged with timestamp, actor, approval status, and result. Retention minimum 90 days. Audit logs stored in `/Vault/Logs/YYYY-MM-DD.json`.

## Technology Stack

- **Brain**: Claude Code (Claude 4.5 Opus via Claude Code Router for free access)
- **Memory**: Obsidian (local markdown vault)
- **Perception**: Python 3.13+ Watcher scripts
- **Action**: MCP servers (Node.js/Python)
- **Orchestration**: Python Orchestrator + Watchdog
- **Accounting**: Odoo Community 19+ (Gold tier) via JSON-RPC MCP
- **Automation**: PM2 (process manager), cron/Task Scheduler

## Development Workflow

1. **Spec Creation** - Define feature requirements in `specs/<feature>/spec.md`
2. **Planning** - Design architecture in `specs/<feature>/plan.md`
3. **Skills First** - Implement all AI logic as Agent Skills before integration
4. **Task Generation** - Create actionable tasks in `specs/<feature>/tasks.md`
5. **Implementation** - Execute tasks, minimum viable diff
6. **Testing** - Integration tests for cross-service communication
7. **Documentation** - ADR for significant decisions, README for setup
8. **Demo** - 5-10 min video showing end-to-end flow

## Quality Gates

- All skills must have SKILL.md documentation
- Credentials validated in dry-run mode before production
- Approval workflows tested with mock data
- Audit logs verified for completeness
- Error paths tested (API failures, network timeouts, malformed data)

## Security Requirements

- **Credential Handling**: .env files only, never in vault, rotated monthly
- **DRY_RUN Mode**: All action scripts support `--dry-run` flag
- **Rate Limiting**: Max actions per hour enforced (10 emails, 3 payments, 50 social posts)
- **Sandboxing**: Development uses test/sandbox accounts
- **Permission Boundaries**: See hackathon doc Section 4 for action thresholds

## Governance

Constitution supersedes all other practices. Amendments require:
1. Documented justification
2. Impact analysis (what changes, what breaks)
3. Migration plan for existing state
4. Approval by project lead

All PRs must verify compliance. Complexity must be justified. Code reviews must check:
- Audit logging completeness
- HITL safeguards for sensitive actions
- Error paths properly handled
- Credentials not exposed

**Version**: 1.0.0 | **Ratified**: 2026-02-10 | **Last Amended**: 2026-02-10
