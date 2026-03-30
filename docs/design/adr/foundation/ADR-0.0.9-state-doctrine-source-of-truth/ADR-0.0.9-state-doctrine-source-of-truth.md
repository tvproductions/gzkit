<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.9 — State Doctrine and Source-of-Truth Hierarchy

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit all `gz` commands that read OBPI/ADR status to catalog which layer each reads from
  1. Document existing reconciliation touchpoints (commands that auto-fix frontmatter)
  1. Identify any Layer 3 artifacts that currently block gate checks

No external behavior changes in this prep phase. Commits separated as:
prep (audit/catalog) -> change (doctrine enforcement) -> polish (docs/cleanup).

STOP/BLOCKERS: If any gate check currently depends on Layer 3 as sole authority,
resolve that dependency before proceeding.

**Date Added:** 2026-03-29
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.0.9
**Area:** Foundation — State Management

## Agent Context Frame — MANDATORY

**Role:** Foundation architect establishing the state management doctrine that all
runtime, reconciliation, and graph engine work depends on.

**Purpose:** Every `gz` command that reads or writes state agrees on which storage
layer is authoritative. Drift between layers is detected and correctable. No
derived artifact can silently become the source-of-truth.

**Goals:**

- Ledger events are the single authoritative source for runtime status
- Frontmatter status is a lazy mirror, auto-fixed at lifecycle moments
- All Layer 3 artifacts (markers, caches, indexes) are rebuildable from L1 + L2
- `gz state --repair` provides explicit force-reconciliation for recovery
- No Layer 3 artifact can fail-close a gate check

**Critical Constraint:** Implementations MUST NOT read frontmatter status as
authoritative for "is this done?" decisions. The ledger is always the tiebreaker.

**Anti-Pattern Warning:** A command that checks `status: Completed` in YAML
frontmatter and treats that as proof of completion — even when no corresponding
ledger event exists — looks correct in demos but silently allows unproven work
to pass gates.

**Integration Points:**

- `src/gzkit/ledger_semantics.py` — derives OBPI status from ledger events
- `src/gzkit/sync.py` — reads frontmatter for reconciliation
- `src/gzkit/pipeline_markers.py` — Layer 3 runtime state
- `src/gzkit/commands/` — all commands reading status

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract: Heavy lane — `gz state --repair` is a new CLI surface
  - CLI help reflects new `--repair` flag
- Registry & resolvers
  - Ledger event types for reconciliation documented
- Tests
  - stdlib `unittest` guards: layer authority tests, repair command smoke test
  - Smoke path < 60s
- Docs
  - Governance runbook updated with state doctrine reference
  - Operator runbook updated with `gz state --repair` usage
- OBPI mapping
  - Each numbered checklist item maps to one brief

## Intent

Establish the canonical state doctrine for gzkit: a three-layer storage model
with explicit authority rules that prevent drift between governance canon (L1),
event log (L2), and derived state (L3). This is the single most important
missing foundation — it prevents divergence across the entire runtime track.

## Non-Goals (Explicit Scope Boundaries)

- **No SQLite or alternative storage backend.** This ADR locks the three-layer
  model. Storage tier promotion (JSONL to SQLite) is governed by ADR-0.0.10
  and deferred to post-1.0.
- **No pipeline stage tracking in the ledger.** Pipeline markers remain Layer 3
  for now. Migration to Layer 2 is documented as intent (OBPI-06) but not
  implemented in this ADR.
- **No graph engine integration.** The graph engine will consume the state
  doctrine but is a separate ADR. This ADR does not define entity resolution
  or cross-entity queries.
- **No real-time sync or watch mode.** Frontmatter is auto-fixed at lifecycle
  moments, not continuously. No file watcher or daemon.

## Decision

- The ledger (`.gzkit/ledger.jsonl`) is authoritative for all runtime status.
  If frontmatter says `status: Completed` but no corresponding ledger event
  exists, the entity is not complete.
- Frontmatter status is a lazy mirror. It is auto-fixed at lifecycle moments
  (`gz closeout`, `gz attest`, `gz obpi reconcile`) but allowed to lag during
  active execution. Frontmatter is never read as source-of-truth for completion.
- Layer 3 artifacts (pipeline markers, caches, derived indexes) are always
  rebuildable. Delete them all, run `gz state`, and everything reconstructs
  from L1 + L2.
- Reconciliation is a core architectural operation, not a maintenance chore.
  It is tested, gated, and optionally run as part of the pipeline.
- Layer 3 artifacts cannot block gates. Only L1 (canon) and L2 (events) can
  be gate evidence. L3 can surface warnings but never fail-close a gate.
- `gz state --repair` provides explicit force-reconciliation for recovery,
  onboarding, and drift diagnosis outside lifecycle moments.
- Pipeline markers (`.gzkit/markers/`) are acceptable as Layer 3 for now.
  Migration to Layer 2 (ledger events for stage transitions) is deferred to
  the Pipeline Lifecycle ADR.

## Interfaces

- **CLI (external contract):** `uv run gz state --repair`
  - Flags in scope: `--repair` (force-reconcile all frontmatter from ledger)
- **Lifecycle auto-fix points:** `gz closeout`, `gz attest`, `gz obpi reconcile`
  auto-update frontmatter to match ledger-derived state
- **Config keys consumed:** None — doctrine is code, not config

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.9-01 | Document three-layer model and five authority rules | Lite | Pending |
| 2 | OBPI-0.0.9-02 | Audit and enforce ledger-first reads in all status commands | Lite | Pending |
| 3 | OBPI-0.0.9-03 | Implement `gz state --repair` force-reconciliation command | Heavy | Pending |
| 4 | OBPI-0.0.9-04 | Auto-fix frontmatter at lifecycle moments (closeout, attest, reconcile) | Lite | Pending |
| 5 | OBPI-0.0.9-05 | Ensure no Layer 3 artifact blocks gate checks | Lite | Pending |
| 6 | OBPI-0.0.9-06 | Document pipeline marker migration path to Layer 2 | Lite | Pending |

**Briefs location:** `obpis/OBPI-0.0.9-*.md`

**WBS Completeness Rule:** Every row in this table MUST have a corresponding brief file.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

---

## Rationale

The repo has three storage layers but no document locking which layer is
authoritative for what. `ledger_semantics.py` derives OBPI status from ledger
events. `sync_*.py` reads frontmatter. Reconciliation commands exist to fix
drift between them. Without a locked doctrine, every new command that reads
status must independently decide which layer to trust.

This ADR has zero dependencies and should have been written before the runtime
track started. It is prerequisite to the Graph Engine (which must know where
to source entity state) and the Pipeline Lifecycle (which must know where to
persist stage transitions).

Source: Architecture Planning Memo Section 2, Decision Record 2026-03-29.

## Consequences

- Single source of truth: ledger events for runtime status, everywhere
- Frontmatter becomes a convenience for git diffs, not a governance authority
- Reconciliation is promoted from ad-hoc maintenance to core operation
- Pipeline markers have a documented migration path (from L3 to L2)
- All `gz` commands that read status must be audited for layer compliance

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/adr/test_state_doctrine.py`
- **BDD (OBPI-03 only):** `features/state_repair.feature`
- **Docs:** `docs/governance/governance_runbook.md`, `docs/user/runbook.md`

---

## OBPI Acceptance Note (Human Acknowledgment)

Each checklist item maps to one brief (OBPI). Record a one-line acceptance note
in the brief once gates are green. Include the exact command to reproduce:

`uv run gz state --repair`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.0.9`
- **Related issues:** Architecture Planning Memo Section 2

### Source & Contracts

- CLI / contracts: `src/gzkit/commands/state.py`
- Core modules: `src/gzkit/ledger_semantics.py`, `src/gzkit/sync.py`

### Tests

- Unit: `tests/adr/test_state_doctrine.py`
- BDD (OBPI-03): `features/state_repair.feature`

### Docs

- Governance: `docs/governance/governance_runbook.md`
- Operator: `docs/user/runbook.md`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|---------------------|----------|-------|
| src/gzkit/ledger_semantics.py | M | All status reads are ledger-first | Test output | |
| src/gzkit/commands/state.py | M | `--repair` flag works | CLI output | |
| docs/governance/governance_runbook.md | M | State doctrine documented | Rendered docs | |
| docs/user/runbook.md | M | `gz state --repair` usage documented | Rendered docs | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
