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
- `gz-adr-audit`: Audit ADR evidence and verify gate completion. (`.github/skills/gz-adr-audit/SKILL.md`)
- `gz-adr-autolink`: --- (`.github/skills/gz-adr-autolink/SKILL.md`)
- `gz-adr-check`: --- (`.github/skills/gz-adr-check/SKILL.md`)
- `gz-adr-closeout-ceremony`: --- (`.github/skills/gz-adr-closeout-ceremony/SKILL.md`)
- `gz-adr-manager`: Create and manage ADRs with OBPI briefs. (`.github/skills/gz-adr-manager/SKILL.md`)
- `gz-adr-map`: --- (`.github/skills/gz-adr-map/SKILL.md`)
- `gz-adr-recon`: --- (`.github/skills/gz-adr-recon/SKILL.md`)
- `gz-adr-status`: --- (`.github/skills/gz-adr-status/SKILL.md`)
- `gz-adr-sync`: --- (`.github/skills/gz-adr-sync/SKILL.md`)
- `gz-adr-verification`: --- (`.github/skills/gz-adr-verification/SKILL.md`)
- `gz-arb`: --- (`.github/skills/gz-arb/SKILL.md`)
- `gz-obpi-audit`: --- (`.github/skills/gz-obpi-audit/SKILL.md`)
- `gz-obpi-brief`: --- (`.github/skills/gz-obpi-brief/SKILL.md`)
- `gz-obpi-reconcile`: --- (`.github/skills/gz-obpi-reconcile/SKILL.md`)
- `gz-obpi-sync`: --- (`.github/skills/gz-obpi-sync/SKILL.md`)
- `gz-session-handoff`: --- (`.github/skills/gz-session-handoff/SKILL.md`)
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
