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

## OBPI Acceptance

When completing an OBPI brief:

1. Use `uv run gz obpi pipeline <OBPI-ID>` after plan approval instead of freeform implementation
2. Treat `gz-obpi-pipeline` as a thin alias over the canonical runtime
3. Provide value narrative + one key proof example
4. Provide verification evidence (tests/commands/output)
5. Wait for explicit human acceptance before setting `Completed` for Heavy/Foundation parent ADR work
6. Run `uv run gz git-sync --apply --lint --test` before final OBPI completion receipt/accounting

Reference: `AGENTS.md` section `OBPI Acceptance Protocol`.

## Skills

Use the canonical skill catalog and keep mirrors synced via `gz agent sync control-surfaces`:

- Canonical skills: `.gzkit/skills`
- Claude skill mirror: `.claude/skills`
- Codex skill mirror: `.agents/skills`
- Copilot skill mirror: `.github/skills`

### Available Skills

#### ADR Lifecycle
`gz-adr-create`, `gz-adr-eval`, `gz-adr-promote`, `gz-adr-status`, `gz-attest`, `gz-closeout`, `gz-plan`

#### ADR Operations
`gz-adr-autolink`, `gz-adr-check`, `gz-adr-emit-receipt`, `gz-adr-manager`, `gz-adr-map`, `gz-adr-recon`, `gz-adr-sync`, `gz-adr-verification`

#### ADR Audit & Closeout
`gz-adr-audit`, `gz-adr-closeout-ceremony`, `gz-audit`

#### OBPI Pipeline
`gz-obpi-audit`, `gz-obpi-brief`, `gz-obpi-pipeline`, `gz-obpi-reconcile`, `gz-obpi-sync`, `gz-plan-audit`, `gz-specify`

#### Governance Infrastructure
`gz-constitute`, `gz-gates`, `gz-implement`, `gz-init`, `gz-interview`, `gz-prd`, `gz-state`, `gz-status`, `gz-validate`

#### Agent & Repository Operations
`git-sync`, `gz-agent-sync`, `gz-check-config-paths`, `gz-migrate-semver`, `gz-register-adrs`, `gz-session-handoff`, `gz-tidy`

#### Code Quality
`format`, `gz-arb`, `gz-check`, `gz-cli-audit`, `gz-typecheck`, `lint`, `test`

#### Cross-Repository
`airlineops-parity-scan`

For details on any skill, read its `SKILL.md` in `.gzkit/skills/<skill-name>/`.

## Build Commands

```bash
uv sync                              # Hydrate environment
uv run -m gzkit --help            # CLI entry point
uv run gz lint                       # Lint
uv run gz format                     # Format
uv run gz typecheck                  # Type check
uv run gz test                       # Run tests
```

## Key Files

- `AGENTS.md` - Universal agent contract
- `.gzkit/manifest.json` - Governance manifest
- `.gzkit/ledger.jsonl` - Event ledger

---

<!-- BEGIN agents.local.md -->
# Local Agent Rules

- Order versioned identifiers semantically, never lexicographically. Example: `ADR-0.9.0` comes before `ADR-0.10.0`.
- Apply semantic-version ordering in ADR summaries, comparisons, and any operator-facing status narration.

<!-- END agents.local.md -->
