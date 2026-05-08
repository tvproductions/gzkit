# gz task list

List tasks for an OBPI with their current lifecycle status.

## Usage

```bash
gz task list OBPI-0.20.0-01
gz task list OBPI-0.20.0-01 --json
```

## Description

Shows all tasks for the specified OBPI, derived from ledger events. Each task
displays its TASK ID, current status, and reason (if blocked or escalated).

## Flags

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | User/config error |

## Examples

```bash
# Table output
uv run gz task list OBPI-0.20.0-01

# JSON output for scripting
uv run gz task list OBPI-0.20.0-01 --json
```
