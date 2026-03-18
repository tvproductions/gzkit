---
id: cli
paths:
  - "src/gzkit/commands/**"
description: CLI contract doctrine and design principles
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

## Flag Conventions

| Flag | Behavior |
|------|----------|
| `--quiet` | Errors only |
| `--verbose` | Debug output |
| `--dry-run` | Show plan, don't execute |
| `--json` | Machine-readable to stdout |
| `--help` / `-h` | Always works |

---

## Output Contracts

| Mode | Output |
|------|--------|
| Default | Human-readable (tables, colors, progress) |
| `--json` | Valid JSON to stdout; logs to stderr |
| `--plain` | One record per line (grep-friendly) |

---

## Help Text Requirements

Every command must:

1. Respond to `-h`/`--help` (exit 0)
2. Include description (1-2 sentences)
3. Include usage line
4. List all options
5. Include at least one example
6. Keep lines <=80 chars

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
