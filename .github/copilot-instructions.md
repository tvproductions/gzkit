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

- `airlineops-parity-scan`: Run a repeatable governance parity scan between ../airlineops (canon) and gzkit (extraction). (`.gzkit/skills/airlineops-parity-scan/SKILL.md`)
- `format`: Auto-format code with Ruff. (`.gzkit/skills/format/SKILL.md`)
- `git-sync`: Run the guarded repository sync ritual with lint/test gates. (`.gzkit/skills/git-sync/SKILL.md`)
- `gz-adr-audit`: Gate-5 audit templates and procedure for ADR verification. GovZero v6 skill. (`.gzkit/skills/gz-adr-audit/SKILL.md`)
- `gz-adr-autolink`: Maintain ADR verification links by scanning @covers decorators and updating docs. (`.gzkit/skills/gz-adr-autolink/SKILL.md`)
- `gz-adr-check`: Run blocking ADR evidence checks for a target ADR. (`.gzkit/skills/gz-adr-check/SKILL.md`)
- `gz-adr-closeout-ceremony`: Execute the ADR closeout ceremony protocol for human attestation. GovZero v6 skill. (`.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`)
- `gz-adr-create`: Create and book a GovZero ADR with its OBPI briefs. Enforces minor-version odometer and five-gate compliance. Portable skill for GovZero-compliant repositories. (`.gzkit/skills/gz-adr-create/SKILL.md`)
- `gz-adr-emit-receipt`: Emit ADR receipt events with scoped evidence payloads. Use when recording completed or validated accounting events. (`.gzkit/skills/gz-adr-emit-receipt/SKILL.md`)
- `gz-adr-eval`: Post-authoring quality evaluation for ADRs and OBPIs. Scores ADRs on 8 weighted dimensions, OBPIs on 5 dimensions, and can run 10 structured red-team challenges before proposal/defense. (`.gzkit/skills/gz-adr-eval/SKILL.md`)
- `gz-adr-manager`: Compatibility alias for gz-adr-create to preserve cross-repository governance ritual continuity. (`.gzkit/skills/gz-adr-manager/SKILL.md`)
- `gz-adr-map`: Build ADR-to-artifact traceability using gz state and repository search. (`.gzkit/skills/gz-adr-map/SKILL.md`)
- `gz-adr-promote`: Promote a pool ADR into canonical ADR package structure. Use when moving a backlog item (ADR-pool.*) into an active, versioned ADR. (`.gzkit/skills/gz-adr-promote/SKILL.md`)
- `gz-adr-recon`: Reconcile ADR/OBPI evidence state from ledger-driven gz outputs. (`.gzkit/skills/gz-adr-recon/SKILL.md`)
- `gz-adr-status`: Show the ADR table for summary requests, or show focused lifecycle and OBPI detail for one ADR. (`.gzkit/skills/gz-adr-status/SKILL.md`)
- `gz-adr-sync`: Reconcile ADR files with ledger registration and status views. (`.gzkit/skills/gz-adr-sync/SKILL.md`)
- `gz-adr-verification`: Verify ADR evidence and linkage using gz ADR/status checks. (`.gzkit/skills/gz-adr-verification/SKILL.md`)
- `gz-agent-sync`: Synchronize generated control surfaces and skill mirrors. Use after skill or governance-surface updates. (`.gzkit/skills/gz-agent-sync/SKILL.md`)
- `gz-arb`: Quality evidence workflow using native gz lint/typecheck/test/check commands. (`.gzkit/skills/gz-arb/SKILL.md`)
- `gz-attest`: Record human attestation with prerequisite enforcement. Use when formally attesting ADR completion state. (`.gzkit/skills/gz-attest/SKILL.md`)
- `gz-audit`: Run strict post-attestation reconciliation audits. Use after attestation to produce and verify audit artifacts. (`.gzkit/skills/gz-audit/SKILL.md`)
- `gz-check`: Run full quality checks in one pass. Use for pre-merge or pre-attestation quality verification. (`.gzkit/skills/gz-check/SKILL.md`)
- `gz-check-config-paths`: Validate configured and manifest path coherence. Use when diagnosing control-surface or path drift. (`.gzkit/skills/gz-check-config-paths/SKILL.md`)
- `gz-cli-audit`: Audit CLI documentation coverage and headings. Use when verifying command manpage and index parity. (`.gzkit/skills/gz-cli-audit/SKILL.md`)
- `gz-closeout`: Initiate ADR closeout with evidence context. Use when preparing an ADR for attestation and audit steps. (`.gzkit/skills/gz-closeout/SKILL.md`)
- `gz-constitute`: Create constitution artifacts. Use when governance constitutions must be created or refreshed. (`.gzkit/skills/gz-constitute/SKILL.md`)
- `gz-gates`: Run lane-required gates or specific gate checks. Use when verifying governance gate compliance for an ADR. (`.gzkit/skills/gz-gates/SKILL.md`)
- `gz-implement`: Run Gate 2 verification and record result events. Use when validating implementation progress for an ADR. (`.gzkit/skills/gz-implement/SKILL.md`)
- `gz-init`: Initialize gzkit governance scaffolding for a repository. Use when bootstrapping or reinitializing project governance surfaces. (`.gzkit/skills/gz-init/SKILL.md`)
- `gz-interview`: Run interactive governance interviews. Use when gathering structured inputs for governance artifacts. (`.gzkit/skills/gz-interview/SKILL.md`)
- `gz-migrate-semver`: Record semver identifier migration events. Use when applying canonical ADR or OBPI renaming migrations. (`.gzkit/skills/gz-migrate-semver/SKILL.md`)
- `gz-obpi-audit`: Audit OBPI brief status against actual code/test evidence. Records proof in JSONL ledger. (`.gzkit/skills/gz-obpi-audit/SKILL.md`)
- `gz-obpi-brief`: Generate a new OBPI brief file with correct headers, constraints, and evidence stubs. GovZero v6 skill. (`.gzkit/skills/gz-obpi-brief/SKILL.md`)
- `gz-obpi-pipeline`: Thin wrapper over the canonical `uv run gz obpi pipeline` runtime for post-plan OBPI execution. (`.gzkit/skills/gz-obpi-pipeline/SKILL.md`)
- `gz-obpi-reconcile`: OBPI brief reconciliation — Audit briefs against evidence, fix stale metadata, write ledger proof. (`.gzkit/skills/gz-obpi-reconcile/SKILL.md`)
- `gz-obpi-sync`: Sync OBPI status in ADR table from brief source files. Detects drift and reconciles. (Layer 3) (`.gzkit/skills/gz-obpi-sync/SKILL.md`)
- `gz-plan`: Create ADR artifacts for planned change. Use when recording architecture intent and lane-specific scope. (`.gzkit/skills/gz-plan/SKILL.md`)
- `gz-plan-audit`: Pre-flight alignment audit — verify ADR intent, OBPI brief scope, and plan are aligned before implementation begins. Use when exiting plan mode, before starting implementation, or to catch scope drift between ADR intent and the active OBPI brief. (`.gzkit/skills/gz-plan-audit/SKILL.md`)
- `gz-prd`: Create product requirement artifacts. Use when defining or revising project-level intent before ADR planning. (`.gzkit/skills/gz-prd/SKILL.md`)
- `gz-register-adrs`: Register existing ADR files missing from ledger state. Use when reconciling on-disk ADRs with governance state. (`.gzkit/skills/gz-register-adrs/SKILL.md`)
- `gz-session-handoff`: Create and resume session handoff documents for agent context preservation across engineering sessions. (`.gzkit/skills/gz-session-handoff/SKILL.md`)
- `gz-specify`: Create OBPI briefs linked to parent ADR items. Use when decomposing implementation into OBPI increments. (`.gzkit/skills/gz-specify/SKILL.md`)
- `gz-state`: Query artifact relationships and readiness state. Use when reporting lineage or artifact graph status. (`.gzkit/skills/gz-state/SKILL.md`)
- `gz-status`: Report gate and lifecycle status across ADRs. Use when checking blockers and next governance actions. (`.gzkit/skills/gz-status/SKILL.md`)
- `gz-tidy`: Run maintenance checks and cleanup routines. Use for repository hygiene and governance maintenance operations. (`.gzkit/skills/gz-tidy/SKILL.md`)
- `gz-typecheck`: Run static type checks. Use when verifying type safety before merge or attestation. (`.gzkit/skills/gz-typecheck/SKILL.md`)
- `gz-validate`: Validate governance artifacts against schema rules. Use when checking manifest, ledger, document, or surface validity. (`.gzkit/skills/gz-validate/SKILL.md`)
- `lint`: Run code linting with Ruff and PyMarkdown. (`.gzkit/skills/lint/SKILL.md`)
- `test`: Run unit tests with unittest. (`.gzkit/skills/test/SKILL.md`)

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
