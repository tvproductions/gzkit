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

- Canonical skills: `.gzkit/skills`
- Claude skill mirror: `.claude/skills`
- Codex skill mirror: `.agents/skills`
- Copilot skill mirror: `.github/skills`

### Available Skills

- `airlineops-parity-scan`: Run a repeatable governance parity scan between `../airlineops` (canon) and gzkit (extraction). (`.gzkit/skills/airlineops-parity-scan/SKILL.md`)
- `format`: Auto-format code with Ruff. (`.gzkit/skills/format/SKILL.md`)
- `git-sync`: Run the guarded repository sync ritual with lint/test gates. (`.gzkit/skills/git-sync/SKILL.md`)
- `gz-adr-audit`: --- (`.gzkit/skills/gz-adr-audit/SKILL.md`)
- `gz-adr-autolink`: --- (`.gzkit/skills/gz-adr-autolink/SKILL.md`)
- `gz-adr-check`: --- (`.gzkit/skills/gz-adr-check/SKILL.md`)
- `gz-adr-closeout-ceremony`: --- (`.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`)
- `gz-adr-create`: --- (`.gzkit/skills/gz-adr-create/SKILL.md`)
- `gz-adr-emit-receipt`: --- (`.gzkit/skills/gz-adr-emit-receipt/SKILL.md`)
- `gz-adr-map`: --- (`.gzkit/skills/gz-adr-map/SKILL.md`)
- `gz-adr-recon`: --- (`.gzkit/skills/gz-adr-recon/SKILL.md`)
- `gz-adr-status`: --- (`.gzkit/skills/gz-adr-status/SKILL.md`)
- `gz-adr-sync`: --- (`.gzkit/skills/gz-adr-sync/SKILL.md`)
- `gz-adr-verification`: --- (`.gzkit/skills/gz-adr-verification/SKILL.md`)
- `gz-agent-sync`: --- (`.gzkit/skills/gz-agent-sync/SKILL.md`)
- `gz-arb`: --- (`.gzkit/skills/gz-arb/SKILL.md`)
- `gz-attest`: --- (`.gzkit/skills/gz-attest/SKILL.md`)
- `gz-audit`: --- (`.gzkit/skills/gz-audit/SKILL.md`)
- `gz-check`: --- (`.gzkit/skills/gz-check/SKILL.md`)
- `gz-check-config-paths`: --- (`.gzkit/skills/gz-check-config-paths/SKILL.md`)
- `gz-cli-audit`: --- (`.gzkit/skills/gz-cli-audit/SKILL.md`)
- `gz-closeout`: --- (`.gzkit/skills/gz-closeout/SKILL.md`)
- `gz-constitute`: --- (`.gzkit/skills/gz-constitute/SKILL.md`)
- `gz-gates`: --- (`.gzkit/skills/gz-gates/SKILL.md`)
- `gz-implement`: --- (`.gzkit/skills/gz-implement/SKILL.md`)
- `gz-init`: --- (`.gzkit/skills/gz-init/SKILL.md`)
- `gz-interview`: --- (`.gzkit/skills/gz-interview/SKILL.md`)
- `gz-migrate-semver`: --- (`.gzkit/skills/gz-migrate-semver/SKILL.md`)
- `gz-obpi-audit`: --- (`.gzkit/skills/gz-obpi-audit/SKILL.md`)
- `gz-obpi-brief`: --- (`.gzkit/skills/gz-obpi-brief/SKILL.md`)
- `gz-obpi-reconcile`: --- (`.gzkit/skills/gz-obpi-reconcile/SKILL.md`)
- `gz-obpi-sync`: --- (`.gzkit/skills/gz-obpi-sync/SKILL.md`)
- `gz-plan`: --- (`.gzkit/skills/gz-plan/SKILL.md`)
- `gz-prd`: --- (`.gzkit/skills/gz-prd/SKILL.md`)
- `gz-register-adrs`: --- (`.gzkit/skills/gz-register-adrs/SKILL.md`)
- `gz-session-handoff`: --- (`.gzkit/skills/gz-session-handoff/SKILL.md`)
- `gz-specify`: --- (`.gzkit/skills/gz-specify/SKILL.md`)
- `gz-state`: --- (`.gzkit/skills/gz-state/SKILL.md`)
- `gz-status`: --- (`.gzkit/skills/gz-status/SKILL.md`)
- `gz-tidy`: --- (`.gzkit/skills/gz-tidy/SKILL.md`)
- `gz-typecheck`: --- (`.gzkit/skills/gz-typecheck/SKILL.md`)
- `gz-validate`: --- (`.gzkit/skills/gz-validate/SKILL.md`)
- `lint`: Run code linting with Ruff and PyMarkdown. (`.gzkit/skills/lint/SKILL.md`)
- `test`: Run unit tests with unittest. (`.gzkit/skills/test/SKILL.md`)

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
