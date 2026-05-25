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

Follow the OBPI Acceptance Protocol defined in `AGENTS.md`. Key rule: use
`uv run gz obpi pipeline <OBPI-ID>` after plan approval; never implement
freeform. Human attestation is required at the brief level whenever the
parent ADR is `heavy`-lane OR `foundation`-kind (either axis alone triggers
it — a `lite`-lane foundation OBPI is NOT self-closeable). `kind` and
`lane` are orthogonal axes (see AGENTS.md § Kinds and § Lane & Kind
Attestation Matrix). A TTY + `ATTEST` confirmation gate prevents agent
subprocesses from synthesizing attestation payloads (GHI #290).

## Skills

Use the canonical skill catalog and keep mirrors synced via `gz agent sync control-surfaces`:

- Canonical skills: `.gzkit/skills`
- Claude skill mirror: `.claude/skills`
- Codex skill mirror: `.agents/skills`
- Copilot skill mirror: `.github/skills`

### Available Skills

See `AGENTS.md` § Available Skills for the complete skill catalog.

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

- **Feature ADRs ordered semantically** (non-`0.0.x`: `ADR-0.9.0` before `ADR-0.10.0`).
- **Foundation ADR IDs (`0.0.x`) are nominal integers** (ADR-0.0.57).
- **Edit imports with usage in the same call** (ruff removes unused).
- **Never prefix `uv run gz` with `PYTHONUTF8=1`** (entrypoint handles UTF-8).
- **Attestation enrichment:** user words verbatim + concrete characterization (§ Attestation).
- **Every version bump is a release** — `gh release create vX.Y.Z --target main --latest`.
- **`.gitignore` scaffolding** uses [github/gitignore](https://github.com/github/gitignore) Python template.
- **Operator PII — never include the operator's personal email in any repo-bound artifact.** Use operator name only (`g0`); if email-shape required, use `<handle>@users.noreply.github.com`.

See [`docs/governance/behavior-rules.md` § Local Agent Rules](docs/governance/behavior-rules.md#local-agent-rules--verbatim-prose-expansions) for verbatim prose expansions and the 2026-04-19 PII-incident recovery procedure.

## Governance doctrine surfaces

Read before touching governance code, rules, or audits:

- [`docs/governance/trust-doctrine.md`](docs/governance/trust-doctrine.md) — T1/T2/T3 layer-boundary invariants.
- [`docs/governance/advisory-rules-audit.md`](docs/governance/advisory-rules-audit.md) — rule scorecard; self-testing via `gz validate --advisory-scorecard`.
- [`docs/governance/state-doctrine.md`](docs/governance/state-doctrine.md) — Layer 3 derived views never source-of-truth.

See [`docs/governance/agent-contract-rationale.md` § Governance doctrine surfaces — mechanical scopes that bind](docs/governance/agent-contract-rationale.md#governance-doctrine-surfaces--mechanical-scopes-that-bind) for the full per-scope mechanical enforcement narrative (budget, authoring-guide schema, eval-feedback trailer, advisor proof binding, complexity calibration, lane attestation, unscoped rules, distribution parity, invariant coherence, brief reconcile).

## Architectural Boundaries

Source: Architecture Planning Memo § 12 (2026-03-29).

1. **Do not promote post-1.0 pool ADRs into active work.**
2. **Do not add more pool ADRs to the runtime track.**
3. **Do not build the graph engine without locking state doctrine first.**
4. **Do not let reconciliation remain a maintenance chore.**
5. **Do not let AirlineOps parity become perpetual catch-up.**
6. **Do not let derived views silently become source-of-truth.**

See [`docs/governance/agent-contract-rationale.md` § Architectural Boundaries](docs/governance/agent-contract-rationale.md#architectural-boundaries--planning-memo-rationale) for each boundary's planning-memo source narrative.

<!-- END agents.local.md -->
