# gz task start

Start or resume a task (pending/blocked to in_progress).

## Usage

```bash
gz task start TASK-0.20.0-01-01-01
gz task start TASK-0.20.0-01-01-01 --json
```

## Description

Transitions a pending task to in_progress, or resumes a blocked task to
in_progress. Both transitions emit a `task_started` ledger event. Invalid
transitions (e.g., starting a completed task) fail with exit code 1.

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
# Start a pending task
uv run gz task start TASK-0.20.0-01-01-01

# Resume a blocked task
uv run gz task start TASK-0.20.0-01-01-01
```
