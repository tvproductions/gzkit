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

An expired work lock is reported as an `Expired lease` and is not an issue to clean:
it stays held, its expiry is booked as `obpi_lock_lease_expired`, and it is freed by
its holder's completion or by a release on the operator's word (operator ruling
2026-10-18). In `--json` each `expired_locks` entry carries `held`. Only the orphan
`mx-session` lock, whose hangar is no longer open, is cleaned by `--apply`.

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
