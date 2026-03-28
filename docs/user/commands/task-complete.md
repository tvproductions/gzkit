# gz task complete

Complete a task (in_progress to completed).

## Usage

```bash
gz task complete TASK-0.20.0-01-01-01
gz task complete TASK-0.20.0-01-01-01 --json
```

## Description

Transitions an in_progress task to completed and emits a `task_completed`
ledger event. Only in_progress tasks can be completed; other transitions
fail with exit code 1.

## Flags

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid transition or user error |

## Examples

```bash
uv run gz task complete TASK-0.20.0-01-01-01
```
