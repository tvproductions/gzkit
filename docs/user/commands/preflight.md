# gz preflight

Detect and clean stale markers, orphan receipts, and expired locks.

## Usage

```bash
gz preflight                    # Dry-run report only
gz preflight --apply            # Remove stale artifacts
gz preflight --json             # Machine-readable output
```

## Description

Scans the workspace for stale governance artifacts: orphan receipts,
expired OBPI locks, and leftover markers from interrupted pipelines.
By default runs in dry-run mode, reporting findings without changes.

## Flags

| Flag | Description |
|------|-------------|
| `--apply` | Remove stale artifacts (default: dry-run report only) |
| `--json` | Output as JSON |
| `--quiet` | Suppress non-error output |
| `--verbose` | Enable verbose output |
| `--debug` | Enable debug mode with full tracebacks |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success (no stale artifacts, or cleanup applied) |
| 1 | User/config error |

## Examples

```bash
# Check for stale artifacts (dry-run)
uv run gz preflight

# Clean up stale artifacts
uv run gz preflight --apply

# Machine-readable report
uv run gz preflight --json
```
