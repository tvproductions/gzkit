# gz-personas

Persona identity frame commands.

## Synopsis

```bash
gz personas <subcommand> [OPTIONS]
```

## Subcommands

### list

Enumerate persona files from `.gzkit/personas/` (read-only).

```bash
gz personas list [--json]
```

### drift

Report persona trait adherence from behavioral proxies.

```bash
gz personas drift [--persona NAME] [--json]
```

Scans local governance artifacts for evidence of trait-aligned behavior.
Exit code 0 when no drift detected, exit code 3 on policy breach.

## Options

| Flag | Applies To | Description |
|------|-----------|-------------|
| `--json` | list, drift | Output as JSON |
| `--persona NAME` | drift | Evaluate only the named persona |

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Success / no drift |
| 3 | Policy breach (drift detected) |

## See Also

- [personas-list](../commands/personas-list.md)
- [personas-drift](../commands/personas-drift.md)
