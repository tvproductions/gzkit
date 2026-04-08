# gz patch release(1) -- GHI-driven patch release ceremony

## SYNOPSIS

```
gz patch release [--dry-run] [--json]
```

## DESCRIPTION

Execute the GHI-driven patch release ceremony. Discovers qualifying
GHIs closed since the last tag, cross-validates them (runtime label
AND source diff), bumps the patch version, and writes a dual-format
release manifest.

Currently a scaffold. Full logic is tracked by ADR-0.0.15 OBPIs 02-06.

## OPTIONS

`--dry-run`
:   Show planned actions without executing.

`--json`
:   Emit machine-readable JSON to stdout.

## EXIT CODES

| Code | Meaning |
|------|---------|
| 0 | Success (or dry-run preview) |
| 1 | User/config error |
| 2 | System/IO error |
| 3 | Policy breach |

## EXAMPLES

Preview what the patch release would do:

```bash
uv run gz patch release --dry-run
```

Machine-readable output:

```bash
uv run gz patch release --json
```

## SEE ALSO

`gz closeout`(1)
