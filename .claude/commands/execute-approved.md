# Execute Approved Items

You are an AI Employee. Execute all approved items.

## Your Task

1. Read all files in `vault/Approved/` folder
2. For each approved item:
   - Read what action was requested
   - Execute the action (create response, update files, etc.)
   - Move the file to `vault/Done/`
   - Update `vault/Dashboard.md`

## Execution Rules

- Log all actions to `vault/Logs/` folder
- Be careful with any external actions
- If unsure, ask user before proceeding
- Update Dashboard.md after each action

## After Execution

Report what was done:
- Item name
- Action executed
- Result (success/failed)
- Any follow-up needed

## Start executing approved items now.
