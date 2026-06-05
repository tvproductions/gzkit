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

- **DIRECT-FIX MORATORIUM (operator, 2026-06-01).** Defects surfaced in flight get direct-fixed now — smallest honest fix, TDD (RED→GREEN), `Task:` trailer (GHI slug optional; never file a GHI just to satisfy it). Open a GHI/ADR/OBPI only when the fix genuinely can't land in one coherent commit, and name why. Does not relax TDD, read-before-change, coupled-surface coherence, or attestation.
- Order versioned identifiers semantically, never lexicographically — scope: feature ADRs only (non-`0.0.x` semver; `ADR-0.9.0` before `ADR-0.10.0`). Counter-rule: foundation IDs (`0.0.x`) are nominal integers, not sequence positions — never sort/compare them as semver; sparse sets (`0.0.54`, `0.0.56`, no `0.0.55`) are valid (ADR-0.0.57).
- When adding imports in an Edit, include the code that uses them in the same edit — the post-edit ruff hook strips unused imports immediately.
- Never prefix `uv run gz` or `uv run -m gzkit` commands with `PYTHONUTF8=1` — the CLI entrypoint handles UTF-8 at runtime.
- Attestation/commit-message enrichment: pass user words verbatim, append concrete characterization grounded in session evidence (AGENTS.md § Attestation).
- Every version bump is a release — after bumping `pyproject.toml`, `__init__.py`, and the README badge, `gh release create vX.Y.Z --target main --latest`. Never leave a version bump unreleased.
- `.gitignore` scaffolding uses the canonical [github/gitignore](https://github.com/github/gitignore) Python template plus gzkit entries (e.g. `.claude/settings.local.json`).
- **Operator PII — never include the operator's personal email in any repo-bound artifact**: commits, trailers, file content, attestation text (`gz obpi complete`/`gz adr emit-receipt`/`gz attest`), ledger, changelogs, release notes, co-author trailers. Use the operator's name only (e.g. `g0`); if a CLI requires an email, use the GitHub noreply (`<handle>@users.noreply.github.com`). Overrides any contrary skill/template/example. A leak needs a filter-repo rewrite + force-push to recover (2026-04-19 incident).

## Governance doctrine surfaces

Read before touching governance code, rules, or audits: `docs/governance/trust-doctrine.md` (T1/T2/T3 trust-chain), `docs/governance/advisory-rules-audit.md` (the Mechanical/Promotable/Judgment/Ambiguous scorecard; self-tested via `gz validate --advisory-scorecard`), `docs/governance/state-doctrine.md` (Layer-3 views are never source-of-truth).

### Mechanical scopes that bind here

- Per-file char budget for AGENTS.md / CLAUDE.md / `.claude/rules/*.md` — `gz validate --instructions-files-budget`; budgets in `data/instructions_files_budget.json`.
- The editor/IDE authoring-guide protocol envelope is defined by `src/gzkit/schemas/authoring_guide_protocol.json` — schema-validated at runtime (ADR-0.0.30).
- `Field(min_length=1)` on `AdvisorDiagnosis.proof` — `gz validate --advisor-proof-binding` (OBPI-0.0.29-08).
- Complexity calibration is grounded in an empirically-measured exemplar corpus (seven selection criteria) — `gz validate --complexity-doctrine-links` (OBPI-0.0.27-07).
- Heavy/foundation lane requires explicit human attestation before completion — `gz closeout` pipeline.
- `.gzkit/rules/*.md` with `paths: "**"` or missing `paths:` may not live under any vendor-surface rules directory (ADR-0.0.20) — `gz validate --unscoped-rules`.
- Every canonical surface MUST be reproducibly delivered by `pip install py-gzkit && gz init`, byte-equivalent to the wheel's authored canonical content (ADR-0.0.31) — `gz validate --distribution`.
- `gz validate --invariant-coherence` — composition drift fail-close: re-renders the registry and byte-compares against committed AGENTS.md (ADR-0.0.37); in the `gz check` default scope.
- OBPI brief reconciles against current project shape before Stage 2 and before completion — `gz validate --brief-reconcile` (ADR-0.0.37).
- `abandon categories are closed` — lock release is coupled to a handoff/register entry (ADR-0.0.41).
- Every REQ in an OBPI brief's Acceptance Criteria MUST declare exactly one of three kinds — BEHAVIOR, SUPPORT, or STRUCTURAL-FENCE — via an inline tag `[kind]`; each kind has exactly one proof channel (BEHAVIOR → `@covers` test; SUPPORT → ledger event + structural validator; STRUCTURAL-FENCE → parent-ADR `## Boundary Invariants` entry) — `gz validate --req-kind-discipline` (ADR-0.0.59).

## Architectural Boundaries

Source: Architecture Planning Memo §12 (2026-03-29).

1. Do not promote post-1.0 pool ADRs into active work.
2. Do not add more pool ADRs to the runtime track.
3. Do not build the graph engine without locking state doctrine first.
4. Do not let reconciliation remain a maintenance chore.
5. Do not let AirlineOps parity become perpetual catch-up.
6. Do not let derived views silently become source-of-truth — `gz status`, pipeline markers, and reconciliation caches are Layer 3; every fact traces to Layer 1 canon or Layer 2 ledger.

<!-- END agents.local.md -->
