<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.10 — Storage Tiers and Simplicity Profile

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Catalog all on-disk storage locations and classify each as Tier A, B, or C
  1. Identify undocumented Tier B items (pipeline markers, caches, derived indexes)
  1. Verify that `git clone` + `uv sync` recovers all Tier A + B state

No external behavior changes in this prep phase. Commits separated as:
prep (catalog/classify) -> change (tier enforcement) -> polish (docs/cleanup).

STOP/BLOCKERS: If any Tier C dependency exists without an authorizing ADR,
resolve or document before proceeding.

**Date Added:** 2026-03-29
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.0.10
**Area:** Foundation — Storage Architecture

## Agent Context Frame — MANDATORY

**Role:** Foundation architect formalizing the storage simplicity profile that
ensures gzkit remains dependency-minimal and git-recoverable.

**Purpose:** Every storage location in the repository is classified into one of
three tiers with explicit rules. Identity surfaces are portable across all tiers.
No external runtime dependency is required for core governance operations.

**Goals:**

- Three storage tiers (A, B, C) are defined with explicit authority boundaries
- Five identity surfaces (ADR-\*, OBPI-\*, REQ-\*, TASK-\*, EV-\*) are portable across all tiers
- Tier escalation (A/B to C) requires an explicit ADR authorization
- No external protocol (MCP, LSP, etc.) is prerequisite for core governance
- Full project state survives `git clone` from scratch

**Critical Constraint:** Implementations MUST NOT introduce external runtime
dependencies (databases, servers, protocols) for core governance operations
without an explicit Heavy-lane ADR authorizing the escalation.

**Anti-Pattern Warning:** A "helpful" SQLite cache that starts as Tier B
(rebuildable) but gradually accumulates state not derivable from L1 + L2 —
silently becoming Tier C without governance authorization. It looks like an
optimization but is an unaudited tier escalation.

**Integration Points:**

- `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md` — pool ADR being promoted
- `.gzkit/ledger.jsonl` — Tier A canonical ledger
- `.gzkit/markers/` — Tier B pipeline markers (documented debt)
- `src/gzkit/core/models.py` — identity surface Pydantic models

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract unchanged (Lite lane) — no CLI surface changes
  - Documentation-only for most OBPIs; model updates for identity surfaces
- Registry & resolvers
  - Identity surface models in `core/models.py` updated for EV-* and TASK-*
- Tests
  - stdlib `unittest` guards: tier classification tests, identity portability tests
  - Smoke path < 60s
- Docs
  - Governance runbook updated with storage tier reference
  - Pool ADR archived with forwarding note
- OBPI mapping
  - Each numbered checklist item maps to one brief

## Intent

Formalize the three-tier storage model that ensures gzkit remains
dependency-minimal, git-recoverable, and protocol-independent. Promotes pool
ADR `storage-simplicity-profile` to foundation status with additional locks
for identity surfaces, tier escalation governance, and post-1.0 SQLite path.

## Decision

- **Tier A (Canonical):** Authored markdown with YAML frontmatter + append-only
  JSONL ledger. No external dependencies. The default for all governance data.
- **Tier B (Derived/Rebuildable):** Deterministic derived indexes and caches
  rebuilt from Tier A sources. Permitted freely but must be rebuildable from
  scratch. Pipeline markers (`.gzkit/markers/`) are the known Tier B item.
- **Tier C (External/Stateful):** External runtime backends (databases, servers,
  protocols). Only by explicit Heavy-lane ADR authorization. Not present today.
- Five identity surfaces are preserved across all tiers: ADR-\*, OBPI-\*, REQ-\*,
  TASK-\*, EV-\*. IDs are portable — no tier-specific translation required.
- Tier escalation (moving data from Tier A/B to Tier C) is a Heavy-lane decision
  requiring its own ADR.
- No external protocol dependency for core governance. CLI + hooks + ledger is the
  universal baseline. MCP, LSP, or any future protocol enhances but never becomes
  a prerequisite.
- JSONL for 1.0.0. No SQLite cache for MVP. SQLite is a known future option
  post-1.0, governed by tier escalation. BEADS' JSONL-to-SQLite progression is
  acknowledged as a likely path.
- All Tier A + B state must survive a `git clone` from scratch. Ledger committed
  to git. Tier B rebuilds on demand.
- Tier B manifest deferred until 3+ Tier B items exist. Graph engine (when built)
  will be Tier B item #2, triggering manifest design.

## Interfaces

- **CLI (no new surfaces):** Existing `gz state` and `gz validate` enforce tier rules
- **Identity models:** `src/gzkit/core/models.py` — ADR, OBPI, REQ, TASK, Evidence ID schemes
- **Config keys consumed:** None — tier classification is structural, not configurable

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.10-01 | Document three-tier model with authority boundaries | Lite | Pending |
| 2 | OBPI-0.0.10-02 | Define five identity surfaces with ID schemes and portability rules | Lite | Pending |
| 3 | OBPI-0.0.10-03 | Catalog and classify all on-disk storage locations | Lite | Pending |
| 4 | OBPI-0.0.10-04 | Enforce tier escalation governance (ADR-required for Tier C) | Lite | Pending |
| 5 | OBPI-0.0.10-05 | Validate git-clone recovery (all Tier A + B state survives) | Lite | Pending |
| 6 | OBPI-0.0.10-06 | Archive pool ADR with forwarding note | Lite | Pending |

**Briefs location:** `obpis/OBPI-0.0.10-*.md`

**WBS Completeness Rule:** Every row in this table MUST have a corresponding brief file.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

---

## Rationale

Pool ADR `storage-simplicity-profile` is well-written and ready for promotion.
It defines three tiers and explicitly rejects mandatory Dolt/SQL runtime
dependency. This foundation ADR ratifies and extends it with:

- Evidence identity slot (EV-\*) from the Entity Hierarchy decision (Section 1)
- Protocol independence reframed from MCP-specific to universal
- Explicit post-1.0 SQLite path acknowledging BEADS precedent
- Tier B manifest concept (deferred until 3+ items)
- Pipeline markers documented as known Tier B item

This ADR has zero dependencies and can be authored in parallel with ADR-0.0.9
(State Doctrine). Together they form the foundation pair that unlocks the
Graph Engine and all subsequent runtime work.

Source: Architecture Planning Memo Section 3, Decision Record 2026-03-29.

## Consequences

- All storage locations have explicit tier classification
- Tier C (external dependencies) requires Heavy-lane ADR — no silent escalation
- Five identity surfaces are locked as portable across all tiers
- Pool ADR `storage-simplicity-profile` archived with forwarding note
- SQLite cache path is acknowledged but deferred to post-1.0

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/adr/test_storage_tiers.py`
- **BDD:** Not applicable (no external contract changes)
- **Docs:** `docs/governance/governance_runbook.md`

---

## OBPI Acceptance Note (Human Acknowledgment)

Each checklist item maps to one brief (OBPI). Record a one-line acceptance note
in the brief once gates are green. Include the exact command to reproduce:

`uv run gz validate --documents --surfaces`

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.0.10`
- **Related issues:** Architecture Planning Memo Section 3
- **Promotes:** `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

### Source & Contracts

- Core modules: `src/gzkit/core/models.py`
- Pool ADR: `docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md`

### Tests

- Unit: `tests/adr/test_storage_tiers.py`

### Docs

- Governance: `docs/governance/governance_runbook.md`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|---------------------|----------|-------|
| src/gzkit/core/models.py | M | Five identity surfaces defined | Test output | |
| docs/governance/governance_runbook.md | M | Storage tier doctrine documented | Rendered docs | |
| docs/design/adr/pool/ADR-pool.storage-simplicity-profile.md | M | Archived with forwarding note | File check | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
