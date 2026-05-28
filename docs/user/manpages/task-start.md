# gz task start

Start or resume a task (pending/blocked to in_progress), or mint and start a new
subdivision task for a REQ using `--req`/`--seq`.

## Usage

```bash
# Start by TASK ID (existing task)
gz task start TASK-0.20.0-01-01-01
gz task start TASK-0.20.0-01-01-01 --json

# Start by REQ ID (subdivision — mint a new TASK)
gz task start --req REQ-0.20.0-01-01 --seq next
gz task start --req REQ-0.20.0-01-01 --seq 2
```

## Description

**TASK-ID form:** Transitions a pending task to in_progress, or resumes a blocked
task to in_progress. Both transitions emit a `task_started` ledger event. Invalid
transitions (e.g., starting a completed task) fail with exit code 1.

**REQ + seq form:** Mints a new TASK ID from the given REQ identifier and starts it.
Use `--seq next` to auto-increment (returns max existing seq + 1, or 1 on an empty
ledger). Use `--seq N` to specify an explicit sequence number; fails if a task with
that seq already exists for the REQ. This form implements the subdivision sub-invariant
from ADR-0.0.64: deliberate labor-subdivision by the operator, not an inferred side-effect.

## Flags

| Flag | Description |
|------|-------------|
| `--req REQ_ID` | REQ identifier for subdivision-based start (e.g. `REQ-0.0.64-03-01`) |
| `--seq NEXT_OR_N` | Sequence value: `next` for auto-increment, or explicit positive integer |
| `--json` | Machine-readable JSON output |

`--req` and `--seq` must be used together. They are mutually exclusive with the
positional `task_id` argument.

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Invalid transition, collision on explicit `--seq N`, or missing argument |

## Examples

```bash
# Start a pending task by ID
uv run gz task start TASK-0.20.0-01-01-01

# Resume a blocked task by ID
uv run gz task start TASK-0.20.0-01-01-01

# Mint and start the next subdivision task for a REQ (seq auto-increment)
uv run gz task start --req REQ-0.0.64-03-01 --seq next

# Mint and start a specific subdivision seq (fails if seq=2 already exists)
uv run gz task start --req REQ-0.0.64-03-01 --seq 2
```
