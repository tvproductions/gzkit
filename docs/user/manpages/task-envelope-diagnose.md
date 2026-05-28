# gz task envelope diagnose

Render TASK ID declarations from all four discovery channels side-by-side for an OBPI.

## Usage

```bash
gz task envelope diagnose OBPI-0.0.64-04
gz task envelope diagnose OBPI-0.0.64-04 --json
```

## Description

Shows per-channel TASK declarations for the named OBPI. When `gz validate
--task-envelope-coherence` fails with a layer-drift (signature c) error, this
command names which channel needs updating.

The four discovery channels are:

| Channel | Source |
|---------|--------|
| `@advances (ch1)` | Python `@advances` decorator registrations |
| `frontmatter tasks: (ch2)` | `tasks: list[str]` in OBPI brief frontmatter |
| `commit trailers (ch3)` | `Task:` commit trailer in git history |
| `ledger task_id (ch4)` | `task_started` events in `.gzkit/ledger.jsonl` |

Layer-drift is reported when two or more non-empty channels declare different TASK IDs.

## Flags

| Flag | Description |
|------|-------------|
| `--json` | Machine-readable JSON output |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | Brief not found or legacy shape |

## Examples

```bash
# Table output showing per-channel TASK IDs
uv run gz task envelope diagnose OBPI-0.0.64-04

# JSON output for tooling
uv run gz task envelope diagnose OBPI-0.0.64-04 --json
```

**Related:** `gz validate --task-envelope-coherence` (ADR-0.0.64 / OBPI-04).
