# gz task fanout

Show the TASK fan-out for a given REQ-ID with detailed file and edit attribution.

## Usage

```bash
gz task fanout <REQ-ID>
gz task fanout <REQ-ID> --detail
gz task fanout <REQ-ID> --json
```

## Description

Displays all tasks spawned from a single requirement, organized with sequential numbering.
When `--detail` is provided, renders an ASCII tree with file:line spans sourced from
`@advances` decorators in task implementation code. The output traces requirement
decomposition through the TASK envelope and shows file-level attribution for each edit.

## Arguments

| Argument | Description |
|----------|-------------|
| `<REQ-ID>` | Requirement ID (e.g., `REQ-0.0.64-05-01`) |

## Flags

| Flag | Description |
|------|-------------|
| `--detail` | Render ASCII tree with file:line spans from `@advances` decorators |
| `--json` | Machine-readable JSON output |

## Output

Table output (default) includes columns:

| Column | Description |
|--------|-------------|
| `TASK` | Task ID |
| `seq` | Sequential number in fan-out |
| `status` | Current task status (pending, in_progress, completed, blocked) |
| `files_touched` | Count of distinct files modified by this task |
| `edits` | Total number of edit operations recorded in ledger |
| `attribution_check` | Attribution coherence status (clean, drift, unattributed) |

With `--detail`, the output includes an indented tree structure showing:

```
REQ-0.0.64-05-01
├─ TASK-0.0.64-05-01-01
│  └─ src/gzkit/example.py:42 (@advances)
├─ TASK-0.0.64-05-01-02
│  ├─ src/gzkit/other.py:18 (@advances)
│  └─ tests/test_other.py:105 (@advances)
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success |
| 1 | REQ-ID not found or invalid |

## Examples

```bash
# Show task fan-out in table format
uv run gz task fanout REQ-0.0.64-05-01

# Show detailed tree with file:line attribution
uv run gz task fanout REQ-0.0.64-05-01 --detail

# Machine-readable JSON output for scripting
uv run gz task fanout REQ-0.0.64-05-01 --json
```
