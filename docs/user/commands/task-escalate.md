# gz task escalate

Escalate a task with a reason (in_progress to escalated).

## Usage

```bash
gz task escalate TASK-0.20.0-01-01-01 --reason "Needs human decision"
gz task escalate TASK-0.20.0-01-01-01 --reason "Needs human decision" --json
```

## Description

Transitions an in_progress task to escalated with a required reason string.
Emits a `task_escalated` ledger event. Only in_progress tasks can be
escalated; other transitions fail with exit code 1.

## Flags

| Flag | Description |
|------|-------------|
| `--reason` | Required reason for escalation |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid transition or user error |

## Examples

```bash
uv run gz task escalate TASK-0.20.0-01-01-01 --reason "Needs human decision"
```
