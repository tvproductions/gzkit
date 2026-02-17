# GitHub Copilot Instructions

Instructions for GitHub Copilot when working with gzkit.

## Project Context

A gzkit-governed project

## Canonical Contract

`AGENTS.md` is the source of truth for governance behavior.

If these instructions drift from `AGENTS.md`, follow `AGENTS.md` and run `gz agent sync control-surfaces`.

## Tech Stack

Python 3.13+ with uv, ruff, ty

## Conventions

Ruff defaults: 4-space indent, 100-char lines, double quotes

## Quality Requirements

Before suggesting code:

1. Follow existing patterns in the codebase
2. Include type annotations for all public functions
3. Write tests for new functionality
4. Follow the invariants defined in governance docs

## Governance

This project uses gzkit for governance. Key commands:

- `gz status` - Check what gates are pending
- `gz validate --documents` - Validate governance artifacts
- `gz check` - Run all quality checks

## Skills

Use the canonical skill catalog and keep mirrors synced via `gz agent sync control-surfaces`:

- Canonical skills: `.github/skills`
- Claude skill mirror: `.claude/skills`

### Available Skills

- `airlineops-parity-scan`: Run a repeatable governance parity scan between `../airlineops` (canon) and gzkit (extraction). (`.github/skills/airlineops-parity-scan/SKILL.md`)
- `format`: Auto-format code with Ruff. (`.github/skills/format/SKILL.md`)
- `git-sync`: Run the guarded repository sync ritual with lint/test gates. (`.github/skills/git-sync/SKILL.md`)
- `gz-adr-audit`: --- (`.github/skills/gz-adr-audit/SKILL.md`)
- `gz-adr-autolink`: --- (`.github/skills/gz-adr-autolink/SKILL.md`)
- `gz-adr-check`: --- (`.github/skills/gz-adr-check/SKILL.md`)
- `gz-adr-closeout-ceremony`: --- (`.github/skills/gz-adr-closeout-ceremony/SKILL.md`)
- `gz-adr-create`: --- (`.github/skills/gz-adr-create/SKILL.md`)
- `gz-adr-emit-receipt`: Emit ADR receipt events with optional scoped evidence. (`.github/skills/gz-adr-emit-receipt/SKILL.md`)
- `gz-adr-map`: --- (`.github/skills/gz-adr-map/SKILL.md`)
- `gz-adr-recon`: --- (`.github/skills/gz-adr-recon/SKILL.md`)
- `gz-adr-status`: --- (`.github/skills/gz-adr-status/SKILL.md`)
- `gz-adr-sync`: --- (`.github/skills/gz-adr-sync/SKILL.md`)
- `gz-adr-verification`: --- (`.github/skills/gz-adr-verification/SKILL.md`)
- `gz-agent-sync`: Sync AGENTS and CLAUDE control surfaces from governance canon. (`.github/skills/gz-agent-sync/SKILL.md`)
- `gz-arb`: --- (`.github/skills/gz-arb/SKILL.md`)
- `gz-attest`: Record human attestation with gate prerequisite enforcement. (`.github/skills/gz-attest/SKILL.md`)
- `gz-audit`: Run strict post-attestation audit reconciliation. (`.github/skills/gz-audit/SKILL.md`)
- `gz-check`: Run all quality checks in one command. (`.github/skills/gz-check/SKILL.md`)
- `gz-check-config-paths`: Validate config and manifest path coherence. (`.github/skills/gz-check-config-paths/SKILL.md`)
- `gz-cli-audit`: Audit CLI docs and manpage coverage for command surfaces. (`.github/skills/gz-cli-audit/SKILL.md`)
- `gz-closeout`: Initiate ADR closeout with evidence context. (`.github/skills/gz-closeout/SKILL.md`)
- `gz-constitute`: Create constitutional governance documents. (`.github/skills/gz-constitute/SKILL.md`)
- `gz-gates`: Run lane-required gates or a specific gate and record events. (`.github/skills/gz-gates/SKILL.md`)
- `gz-implement`: Run Gate 2 tests and record gate results. (`.github/skills/gz-implement/SKILL.md`)
- `gz-init`: Initialize gzkit in a repository with governance scaffolding. (`.github/skills/gz-init/SKILL.md`)
- `gz-interview`: Drive interactive governance document interviews. (`.github/skills/gz-interview/SKILL.md`)
- `gz-migrate-semver`: Record semver ID rename migrations in governance state. (`.github/skills/gz-migrate-semver/SKILL.md`)
- `gz-obpi-audit`: --- (`.github/skills/gz-obpi-audit/SKILL.md`)
- `gz-obpi-brief`: --- (`.github/skills/gz-obpi-brief/SKILL.md`)
- `gz-obpi-reconcile`: --- (`.github/skills/gz-obpi-reconcile/SKILL.md`)
- `gz-obpi-sync`: --- (`.github/skills/gz-obpi-sync/SKILL.md`)
- `gz-plan`: Create ADR artifacts for planned changes. (`.github/skills/gz-plan/SKILL.md`)
- `gz-prd`: Create and record Product Requirements Documents. (`.github/skills/gz-prd/SKILL.md`)
- `gz-register-adrs`: Register existing ADR files missing from ledger state. (`.github/skills/gz-register-adrs/SKILL.md`)
- `gz-session-handoff`: --- (`.github/skills/gz-session-handoff/SKILL.md`)
- `gz-specify`: Create OBPI briefs for scoped implementation items. (`.github/skills/gz-specify/SKILL.md`)
- `gz-state`: Query artifact graph state and lineage relationships. (`.github/skills/gz-state/SKILL.md`)
- `gz-status`: Report gate and lifecycle status across ADRs. (`.github/skills/gz-status/SKILL.md`)
- `gz-tidy`: Run maintenance checks and cleanup routines. (`.github/skills/gz-tidy/SKILL.md`)
- `gz-typecheck`: Run static type checks with configured toolchain. (`.github/skills/gz-typecheck/SKILL.md`)
- `gz-validate`: Validate governance artifacts and schemas. (`.github/skills/gz-validate/SKILL.md`)
- `lint`: Run code linting with Ruff and PyMarkdown. (`.github/skills/lint/SKILL.md`)
- `test`: Run unit tests with unittest. (`.github/skills/test/SKILL.md`)

## Build Commands

```bash
uv sync                              # Hydrate environment
uv run -m gzkit --help            # CLI entry point
uvx ruff check src tests             # Lint
uvx ruff format --check .            # Format check
uvx ty check src                     # Type check
uv run -m unittest discover tests    # Run tests
```

## Key Files

- `AGENTS.md` - Universal agent contract
- `.gzkit/manifest.json` - Governance manifest
- `.gzkit/ledger.jsonl` - Event ledger

---

<!-- BEGIN agents.local.md -->

<!-- END agents.local.md -->
