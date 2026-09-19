---
id: cli
paths:
  - "src/gzkit/commands/**"
description: CLI contract doctrine and design principles
---

# CLI Contract Doctrine

<!-- rule-version: 0.9.0 -->

> **Rule version:** `0.9.0` — diet pass under GHI #921: the 2026-08-22 shape measurements, the lane-vs-route quotations and the `8d9e09a4` worked example lifted to [Rule Version History](../../docs/governance/rule-version-history.md#climd) and [`docs/design/cli-architecture-analysis.md`](../../docs/design/cli-architecture-analysis.md). Binding rules unchanged.

**Baseline:** [clig.dev](https://clig.dev/). **Canonical specification:** [`docs/design/cli-standards-v3.md`](../../docs/design/cli-standards-v3.md) (ADR-0.0.4) — read its § Document status before citing a section; parts are live-and-met, live-but-unmet, or retired. **Mechanical check:** `uv run gz cli audit`. **Heavy lane trigger:** any CLI contract change — subcommands, flags, exit codes, output schemas.

## Command shape (binding)

Mirrored from the specification's § Command Structure and § Output Rules; scored at `docs/governance/advisory-rules-audit.md` § CLI Contract Doctrine, measured in `docs/design/cli-architecture-analysis.md`.

- The count of depth-1 leaf commands may not increase — the specification prescribes `<group> <command>`; the existing bare root verbs are waived shrink-only, and new commands take a noun.
- No subcommand may share its verb with a bare root command (`gz adr status` vs `gz status`); repetition under different nouns (`list`) collides with nothing.
- A noun may not be registered in both singular and plural form.
- New root commands may not hyphenate a noun-verb pair; a subcommand is what the hyphen stands in for.
- Every leaf command declares --json or carries a waiver with rationale.
- A parser node is a leaf or a group, never both.
- Building the gz parser tree may not import handler-only dependencies — every `gz --help` pays what the tree imports (GHI #180); guarded by `tests/cli/test_help_path_imports.py`.
- A new subcommand satisfies all seven coupled obligations in the authoring patch (§ New Subcommand); the validators named there win any disagreement with the list.
- User-facing output passes through the formatter, never console.print directly — the precondition for the `--json` rule: a `--json` flag on a command whose body prints human text is green while blind.

## Core Principles

| Principle | Rule |
|-----------|------|
| Human-first | Optimize for humans; add `--json`/`--plain` for machines |
| Consistency | Before landing a flag or subcommand, `uv run gz cli audit` exits 0 and a new flag's usage line agrees with its parser (required-ness and value-taking; GHI #693). Missing coverage is authored in the same patch. |
| Discovery | Comprehensive help with examples; no web docs needed |
| Robustness | Validate early; fail fast; show progress |

## Exit Codes

| Code | Meaning | Recovery |
|------|---------|----------|
| **0** | Success | — |
| **1** | User/Config Error | Fix invocation or config |
| **2** | Usage or System/IO Error | Usage: fix the invocation. System/IO: check network/disk; retry |
| **3** | Policy Breach | Review logs; partial success needs review |

Use `sys.exit(code)`; document codes 2/3 in help text.

- Code 2 means Usage or System/IO error; every parse error exits 2 — `StableArgumentParser.error`, attested REQ-0.0.4-02-03.
- Never key a retry on exit 2 without the `BLOCKERS:` usage prefix on stderr — a caller cannot read 2 as an I/O fault alone.

## Flag Conventions

| Flag | Behavior |
|------|----------|
| `--quiet` | Errors only |
| `--verbose` | INFO-level logging to stderr (the default logs warnings and errors) |
| `--debug` | DEBUG-level logging to stderr; full tracebacks on error |
| `--dry-run` | Show plan, don't execute |
| `--json` | Machine-readable to stdout; logs to stderr |
| `--plain` | One record per line (grep-friendly) |
| `--help` / `-h` | Always works, exit 0 |

- Verbosity flags: the default logs warnings and errors, `--quiet` errors only, `--verbose` INFO, `--debug` DEBUG, all to stderr — `docs/design/cli-standards-v3.md` § Verbosity Levels, witnessed by `NC:cli-log-levels-follow-spec`.

## Help Text Requirements

Every command responds to `-h`/`--help` (exit 0) with a one-or-two-sentence description, a usage line, every option, at least one example, and lines ≤ 80 chars.

## Adding CLI Features

Lane authority is `AGENTS.md` § Gate Covenant: a new flag or subcommand is a contract change used by humans, so it is **Heavy**, and planned contract work is OBPI work the operator initiates. **Lane is not route — a GHI-tracked defect repair routes direct even when it adds a CLI surface** (`AGENTS.md` § Defect-fix routing; operator reaffirmed 2026-09-06). Heavy lane still binds the gates the repair must clear; it never converts the repair into OBPI ceremony. `gz cli audit` audits a flag's documentation (manpage row, GHI #350; usage-line agreement, GHI #693) and says nothing about lane.

### New Flag (Heavy Lane)

1. Follow naming conventions and check for an equivalent in other CLIs.
2. Update help text with an example.
3. Add the flag row to the manpage in `docs/user/manpages/`.

### New Subcommand (Heavy Lane)

Seven obligations fire for a new verb, each mechanically checked; satisfy them in the authoring patch. The authority is the code — `_SURFACE_NAMES` and `check_surfaces` (`src/gzkit/doc_coverage/scanner.py`), `find_undeclared_commands` (`src/gzkit/doc_coverage/manifest.py`), `audit_skill_alignment` (`src/gzkit/governance/trust_audits/cli.py`) — never this list.

1. **Manifest entry** — `config/doc-coverage.json`.
2. **Manpage** — `docs/user/manpages/<slug>.md`, spaces hyphenated (`gz adr audit-check` → `adr-audit-check.md`), never a `gz-` prefix (GHI #532).
3. **Index entry** — the filename in `docs/user/manpages/index.md`.
4. **Operator runbook** — a reference in `docs/user/runbook.md`.
5. **Governance runbook** — a reference in `docs/governance/governance_runbook.md`.
6. **Handler docstring** — non-empty; the one obligation that is code rather than a doc file, and the one most often missed.
7. **Wielding skill** — a `.gzkit/skills/**/SKILL.md` naming the full verb path, or an `_NO_SKILL_VERBS` waiver with rationale.

Alongside these: an ADR or brief documenting purpose, help text with examples, a behave smoke test, and the GHI cited in the commit. Release notes are never hand-written — `RELEASE_NOTES.md` and `CHANGELOG.md` are authored by the `gz-patch-release` ceremony (`.gzkit/rules/changelog-release-notes.md`). A deprecated verb inverts obligations 4, 5 and 7: absence is the passing state, because a runbook or skill that prescribes a retired verb routes agents back onto it (GHI #705). The seven cover verb registration only; a change that also alters a *format* has consumers this list cannot enumerate.
