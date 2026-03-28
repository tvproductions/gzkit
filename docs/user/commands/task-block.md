# gz task block

Block a task with a reason (in_progress to blocked).

## Usage

```bash
gz task block TASK-0.20.0-01-01-01 --reason "Missing API"
gz task block TASK-0.20.0-01-01-01 --reason "Missing API" --json
```

## Description

Transitions an in_progress task to blocked with a required reason string.
Emits a `task_blocked` ledger event. Only in_progress tasks can be blocked;
other transitions fail with exit code 1.

## Flags

| Flag | Description |
|------|-------------|
| `--reason` | Required reason for blocking |
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid transition or user error |

## Examples

```bash
uv run gz task block TASK-0.20.0-01-01-01 --reason "Waiting on upstream API"
```
