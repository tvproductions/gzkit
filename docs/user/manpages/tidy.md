# gz tidy

Run maintenance checks and cleanup routines for repository hygiene.

## Usage

```bash
gz tidy [OPTIONS]
```

## Description

Executes repository maintenance tasks including artifact cleanup, stale file detection, and housekeeping routines. Helps keep the workspace organized and removes temporary or obsolete artifacts.

## Options

| Option | Description |
|--------|-------------|
| `--check` | Report issues without applying fixes (read-only audit mode) |
| `--fix` | Apply automatic fixes for the issues the check would flag. It syncs control surfaces on the same guarded path as `gz agent sync control-surfaces`: it refuses, leaving every mirror unchanged, when canonical skills fail the sync preflight (GHI #1100) |
| `--dry-run` | Show planned actions without executing |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Maintenance completed successfully |
| 1 | Maintenance errors encountered, including a `--fix` sync refused by the canonical preflight or failed by the post-sync skill audit |
