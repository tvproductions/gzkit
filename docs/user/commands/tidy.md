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
| `--fix` | Apply automatic fixes for the issues the check would flag |
| `--dry-run` | Show planned actions without executing |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Maintenance completed successfully |
| 1 | Maintenance errors encountered |
