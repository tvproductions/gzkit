---
applyTo: src/gzkit/commands/**
---

# CLI Contract Doctrine

**Baseline:** [clig.dev](https://clig.dev/) — Human-first CLI design principles.
**Machine-readable:** `config/cli_doctrine.json`
**Heavy Lane Trigger:** Any CLI contract change (subcommands, flags, exit codes, output schemas).

---

## Core Principles

| Principle | Rule |
|-----------|------|
| Human-first | Optimize for humans; add `--json`/`--plain` for machines |
| Consistency | Follow UNIX/POSIX patterns; match existing flags |
| Discovery | Comprehensive help with examples; no web docs needed |
| Robustness | Validate early; fail fast; provide progress indicators |

---

## Exit Codes (Standard 4-Code Map)

| Code | Meaning | Recovery |
|------|---------|----------|
| **0** | Success | N/A |
| **1** | User/Config Error | Fix invocation or config |
| **2** | System/IO Error | Check network/disk; retry |
| **3** | Policy Breach | Review logs; partial success needs review |

Use `sys.exit(code)`. Document codes 2/3 in help text.

---

## Config-First Doctrine (ADR-0.1.0)

All paths, toggles, and periods from typed JSON settings or CLI flags — never ENV for behavior.

```python
# ❌ WRONG
offline = os.getenv("GZKIT_OFFLINE") == "1"

# ✅ RIGHT
settings = load_settings()
offline = ns.offline or settings.network.offline
```

**Allowed ENV:** `HTTP_PROXY`, `HTTPS_PROXY`, `NO_PROXY`, `REQUESTS_CA_BUNDLE` (connectivity only), `NO_COLOR`, `TERM` (formatting only).

---

## Flag Conventions

| Flag | Behavior |
|------|----------|
| `--quiet` | Errors only |
| `--verbose` | Debug output |
| `--dry-run` | Show plan, don't execute |
| `--json` | Machine-readable to stdout |
| `--help` / `-h` | Always works |

- Prefer flags over positional args (`--dataset db28` not `db28`)
- Use `-` separator (`--dry-run` not `--dry_run`)
- The gz CLI uses these conventions

---

## Output Contracts

| Mode | Output |
|------|--------|
| Default | Human-readable (tables, colors, progress) |
| `--json` | Valid JSON to stdout; logs to stderr |
| `--plain` | One record per line (grep-friendly) |

**Color rules:** Disable if not TTY, `NO_COLOR` set, or `--json` used.

---

## Help Text Requirements

Every command must:

1. Respond to `-h`/`--help` (exit 0)
2. Include description (1-2 sentences)
3. Include usage line
4. List all options
5. Include at least one example
6. Keep lines ≤80 chars

```text
Usage: gz gates --adr ADR-X.Y.Z [options]

Run lane-required gate checks for an ADR.

Options:
  --adr ADR_ID       Target ADR identifier
  --dry-run          Show plan, don't execute
  --quiet            Suppress non-error output
  -h, --help         Show this help

Examples:
  gz gates --adr ADR-0.15.0
  gz closeout ADR-0.15.0 --dry-run

Exit codes:
  0   Success
  1   Gate check failed
  2   Configuration error
```

---

## Configuration

All paths, toggles, and settings from typed JSON config or CLI flags — never ENV for behavior.

---

## Logging

- Use project logger, not `print()`
- Respect `--quiet`/`--verbose`
- Progress to stderr; disable in `--json` mode

---

## Adding CLI Features

### New Flag (Additive = Lite Lane)

1. Follow naming conventions
2. Check for equivalent in other CLI
3. Update help text with example

### New Subcommand (Heavy Lane)

1. ADR or brief documenting purpose
2. Help text with examples
3. Behave smoke test
4. Manpage in `docs/user/manpages/`
5. Release notes

### Changing Exit Codes (Heavy Lane)

1. ADR documenting old vs new
2. Deprecation warning one release prior
3. Update Behave tests
4. Release notes with migration guide

---

## Enforcement

```bash
uv run gz check-config-paths  # Must report 0 violations
```

Policy tests validate help structure, flag naming, exit code documentation.
