# gz task

Manage TASK entity lifecycle: list, start, complete, block, escalate.

## Usage

```bash
gz task list OBPI-0.20.0-01                                  # List tasks for an OBPI
gz task list OBPI-0.20.0-01 --json                            # JSON output
gz task start TASK-0.20.0-01-01-01                            # Start a pending task
gz task start TASK-0.20.0-01-01-01 --json                     # Start with JSON output
gz task complete TASK-0.20.0-01-01-01                          # Complete an in-progress task
gz task block TASK-0.20.0-01-01-01 --reason "Missing API"     # Block with reason
gz task escalate TASK-0.20.0-01-01-01 --reason "Needs human"  # Escalate with reason
```

## Description

The `gz task` command group manages TASK entities -- the fourth tier of
gzkit's governance hierarchy (ADR > OBPI > REQ > TASK). Each subcommand
transitions a task through its lifecycle and emits the corresponding
ledger event.

### Subcommands

| Subcommand | Description |
|------------|-------------|
| `list` | Show all tasks for an OBPI with status |
| `start` | Transition pending or blocked task to in_progress |
| `complete` | Transition in_progress task to completed |
| `block` | Transition in_progress task to blocked (with reason) |
| `escalate` | Transition in_progress task to escalated (with reason) |

### Valid Transitions

| From | To | Subcommand |
|------|----|------------|
| pending | in_progress | `start` |
| blocked | in_progress | `start` (resume) |
| in_progress | completed | `complete` |
| in_progress | blocked | `block` |
| in_progress | escalated | `escalate` |

Invalid transitions exit with code 1 and a clear error message.

## Flags

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--json` | All subcommands | Machine-readable JSON output |
| `--reason` | `block`, `escalate` | Required reason string |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid transition or user error |

## Examples

```bash
# List tasks for an OBPI
uv run gz task list OBPI-0.20.0-01

# Start a task (pending -> in_progress)
uv run gz task start TASK-0.20.0-01-01-01

# Resume a blocked task (blocked -> in_progress)
uv run gz task start TASK-0.20.0-01-01-01

# Complete a task
uv run gz task complete TASK-0.20.0-01-01-01

# Block a task with reason
uv run gz task block TASK-0.20.0-01-01-01 --reason "Waiting on upstream API"

# Escalate a task
uv run gz task escalate TASK-0.20.0-01-01-01 --reason "Needs human decision"

# JSON output for scripting
uv run gz task list OBPI-0.20.0-01 --json
```
