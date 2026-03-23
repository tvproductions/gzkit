---
id: ADR-0.0.4-cli-standards-presentation-foundation
status: Draft
semver: 0.0.4
lane: heavy
parent:
date: 2026-03-22
---

# ADR-0.0.4: CLI Standards & Presentation Foundation

## Intent

gzkit's CLI presentation is inferior to airlineops and opsdev. Help text is incomplete
(~50% of arguments lack help text), no command has epilogs with examples or exit codes,
runtime output is inconsistent (ASCII tables in some commands, Rich in others, bare
print in others), error messages lack structured format, and the 6100-line monolithic
`cli.py` prevents professional command development.

This ADR establishes the CLI infrastructure that every subsequent command absorption
ADR (0.25.0 through 0.39.0) depends on. Without it, absorbed commands would enter an
amateur chassis. The canonical specification is `docs/design/cli-standards-v3.md`.

### Goals

1. **Restructure** the monolithic `cli.py` into `cli/main.py` + `cli/commands/` + `cli/helpers/`
2. **Parser infrastructure** with stable error format, no-hyphen-break formatting, exit code epilogs
3. **Common flags** (`--quiet`, `--verbose`, `--debug`, `--json`) and standard option factories
4. **Help text completeness** on all ~123 bare arguments and all commands
5. **Epilog templates** with examples and exit codes on every command/subcommand
6. **OutputFormatter** as single chokepoint for all user-facing output (5 modes)
7. **Exception hierarchy** with typed exit codes and CLI boundary pattern
8. **Runtime presentation** with Rich tables everywhere, status symbols, BLOCKERS: prefix
9. **Progress indication** for long-running operations
10. **CLI consistency tests** as policy enforcement

### Blocks

- ADR-0.25.0 through ADR-0.39.0 (all absorption ADRs)
- ADR-0.31.0 (new CLI command absorption)
- ADR-0.32.0 (overlapping CLI command comparison)
- ADR-0.33.0 (specialized command absorption)

## Decision

Adopt the CLI Standards v3 specification (`docs/design/cli-standards-v3.md`) as the
canonical reference for gzkit's CLI architecture. Implement full compliance across all
existing commands before any new command absorption work begins.

### Boundary with ADR-0.0.3

This ADR owns the **CLI presentation surface** — what the operator sees in `--help` and
runtime output, the output formatting abstraction, and CLI-layer exception handling.
ADR-0.0.3 owns **hexagonal domain architecture** — ports, adapters, domain extraction,
test fakes, and structlog diagnostic logging.

The OutputFormatter created here becomes part of ADR-0.0.3's CLI adapter layer when
that work lands. structlog (diagnostic logging to stderr) stays in ADR-0.0.3.

### Reference Implementation

The target patterns are drawn from:

- **airlineops** `src/airlineops/cli/helpers/` — standard_options.py, io_helpers.py, shared.py, exit_codes.py
- **opsdev** `src/opsdev/commands/_common_flags.py` — common flags, skill paths, check_skill_flag
- **airlineops** `tests/cli/test_cli_consistency.py` — recursive parser auditor, convention enforcement
- **v3 CLI Standards** `docs/design/cli-standards-v3.md` — canonical specification

## Consequences

### Positive

- Every command presents professional help text with examples and exit codes
- Runtime output is consistent across all commands (Rich tables, status symbols, color conventions)
- New commands absorbed from airlineops/opsdev integrate into a mature infrastructure
- CLI consistency tests catch regressions automatically
- OutputFormatter eliminates scattered print/console.print calls
- cli.py decomposition enables parallel development on different command groups

### Negative

- Large diff touching every command registration and handler
- Temporary divergence from ADR-0.0.3's hexagonal target structure (OutputFormatter lives in cli/ before ports/adapters exist)
- Common flags on all commands may surface edge cases in commands that currently ignore verbose/quiet semantics

## Decomposition Scorecard

- Data/State: 1
- Logic/Engine: 1
- Interface: 2
- Observability: 2
- Lineage: 1
- Dimension Total: 7
- Baseline Range: 4
- Baseline Selected: 4
- Split Single-Narrative: 1
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 1
- Split Total: 4
- Final Target OBPI Count: 10

Note: Expanded beyond the 7-count formula because the v3 specification mandates
distinct deliverables (OutputFormatter, exception hierarchy, progress indication)
that cannot merge without violating single-narrative.

## Checklist

- [ ] OBPI-0.0.4-01: CLI module restructure — decompose 6100-line cli.py into cli/ package
- [ ] OBPI-0.0.4-02: Parser infrastructure — StableArgumentParser, NoHyphenBreaksFormatter, exit codes epilog
- [ ] OBPI-0.0.4-03: Common flags & standard option factories
- [ ] OBPI-0.0.4-04: Help text completeness — all args and commands documented
- [ ] OBPI-0.0.4-05: Epilog templates — examples and exit codes on every command
- [ ] OBPI-0.0.4-06: OutputFormatter — single output chokepoint (5 modes)
- [ ] OBPI-0.0.4-07: Exception hierarchy & exit codes
- [ ] OBPI-0.0.4-08: Runtime presentation — Rich everywhere, symbols, BLOCKERS:, color conventions
- [ ] OBPI-0.0.4-09: Progress indication — rich.progress for long-running operations
- [ ] OBPI-0.0.4-10: CLI consistency tests — policy enforcement via recursive parser auditor

## Dependency Graph

```
OBPI-01 (restructure) ──> OBPI-02 (parser infra) ──> OBPI-03 (common flags)
                                                          |
                      OBPI-04 (help text) <───────────────|
                      OBPI-05 (epilogs)   <───────────────┘

OBPI-06 (formatter) ──> OBPI-08 (runtime presentation)
                    ──> OBPI-09 (progress)

OBPI-07 (exceptions) ──> OBPI-08 (runtime presentation)

OBPI-10 (consistency tests) ── last, validates everything
```

## Evidence

- [ ] Tests: `tests/policy/test_cli_consistency.py`
- [ ] Tests: `tests/unit/test_output_formatter.py`
- [ ] Tests: `tests/unit/test_parser.py`
- [ ] Tests: `tests/unit/test_exception_hierarchy.py`
- [ ] Docs: `docs/design/cli-standards-v3.md` (canonical spec)
- [ ] Docs: `docs/user/commands/` (updated per command)
- [ ] Proof: All commands pass `--help` with descriptions, epilogs, documented args
- [ ] Proof: `gz check` output uses Rich + status symbols
- [ ] Proof: `gz status --table` uses Rich tables (not ASCII pipes)
- [ ] Proof: Zero undocumented arguments in recursive parser audit

## Alternatives Considered

1. **Fix help text only, keep monolith** — Rejected. Adding epilogs to 60+ parsers in a
   6100-line file is impractical and would be thrown away when ADR-0.0.3 restructures.
2. **Merge into ADR-0.0.3** — Rejected. ADR-0.0.3 is about hexagonal domain architecture.
   CLI presentation is a different concern that can land independently and sooner.
3. **Incremental per-command fixes** — Rejected. Without shared infrastructure (formatters,
   common flags, option factories), each command would reinvent conventions differently.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.0.4 | Pending | | | |
