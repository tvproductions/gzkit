---
id: OBPI-0.41.0-05-ghi-160-retroactive-governance-housing
parent: ADR-0.41.0
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.41.0-05: GHI-160 Retroactive Governance Housing

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-0.41.0-tdd-emission-and-graph-rot-remediation.md`
- **Checklist Item:** #5 — "Retroactive governance housing for GHI-160 Phases 1-7 + Phase 6 validate-check evidence linkage"

**Status:** Draft

## Objective

Formally house GHI-160 Phases 1 through 7 under this ADR as retroactive governance evidence. The audit artifact at `artifacts/audits/ghi-160-phase-7-task-backfill.md` becomes this OBPI's primary evidence document; its "grandfather list" is promoted from ad-hoc exception to the ADR's formal scope statement. The `gz validate --commit-trailers` and `gz validate --requirements` checks from Phase 6 are traced to this OBPI's REQs so the four-tier chain is complete.

## Lane

**Heavy** — closes the retroactive governance gap that GHI-160 itself created. Affects the ledger through OBPI evidence linkage and affects the audit artifact as the primary evidence document.

## Allowed Paths

- `artifacts/audits/ghi-160-phase-7-task-backfill.md` — promote to formal evidence, add REQ IDs and OBPI linkage
- `artifacts/audits/ghi-160-phase-6-validate-checks.md` — new evidence file linking Phase 6 commits to this OBPI's REQs
- `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/obpis/OBPI-0.41.0-05-ghi-160-retroactive-governance-housing.md` — this brief
- `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-CLOSEOUT-FORM.md` — update GHI-160 summary table with commit-to-OBPI linkage
- `.gzkit/ledger.jsonl` — only via `gz task` commands (no direct edits)

## Denied Paths

- Historical Phase 1-7 commits — immutable; no amendment attempts
- `src/gzkit/**` — this OBPI is evidence linkage, not code
- `tests/**` — same

## Requirements (FAIL-CLOSED)

1. `artifacts/audits/ghi-160-phase-7-task-backfill.md` is updated to cite this OBPI's REQ IDs instead of "grandfathered" language. The commits listed in the grandfather table become "evidence for REQ-0.41.0-05-NN".
2. A new `artifacts/audits/ghi-160-phase-6-validate-checks.md` documents the Phase 6 work (the `gz validate --requirements` and `--commit-trailers` commits) and links each to a REQ on this OBPI.
3. `gz task start` + `gz task complete` events are emitted for REQs 05-01 through 05-05 as the linkage work completes.
4. The ADR-CLOSEOUT-FORM.md GHI-160 summary table is updated to show the commit-to-OBPI mapping explicitly.
5. Running `gz covers ADR-0.41.0 --json` shows non-zero total_reqs for OBPI-0.41.0-05 after REQ authoring.
6. Running `gz adr audit-check ADR-0.41.0` reports no audit gaps attributable to GHI-160 Phases 1-7.

## Discovery Checklist

**Governance:**

- [ ] `artifacts/audits/governance-graph-rot-audit-2026-04-15.md` — Phase 1 audit
- [ ] `artifacts/audits/ghi-160-phase-7-task-backfill.md` — Phase 7 audit with grandfather list

**Context:**

- [ ] GHI-160 issue body — the remedy program spec
- [ ] Commits 70cdcdb8, d3bdb60b, c481673a, 00bfea05, 9ba8e802 — Phase 1-4
- [ ] Phase 6/7 commit series (authored alongside this ADR)

**Prerequisites:**

- [ ] OBPIs 01, 02, 03, 04 Completed (so the `gz tdd` chain infrastructure exists to emit retroactive RED/GREEN events for Phase 5 if desired)

**Existing code:**

- [ ] `gz adr audit-check` is the verification tool; `gz covers` is the coverage tool.

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded

### Gate 2: TDD

- [ ] REQs for this OBPI have tests that verify the audit artifact contains the expected linkage structure (the evidence file itself is the product; test asserts it loads and contains the expected sections)

### Gate 3: Docs (Heavy)

- [ ] Docs build passes; audit artifacts render

### Gate 4: BDD (Heavy)

- [ ] No new BDD scope

### Gate 5: Human (Heavy)

- [ ] Attestation at ADR closeout references this OBPI as the retroactive governance anchor

## Verification

```bash
uv run gz adr audit-check ADR-0.41.0
uv run gz covers ADR-0.41.0 --json
uv run gz task list OBPI-0.41.0-05
uv run mkdocs build --strict
```

## Acceptance Criteria

- [ ] REQ-0.41.0-05-01: Given `artifacts/audits/ghi-160-phase-7-task-backfill.md`, when read after this OBPI completes, then the grandfather list is replaced by a table mapping each Phase 1-7 commit to a specific REQ on OBPI-0.41.0-05.
- [ ] REQ-0.41.0-05-02: Given `artifacts/audits/ghi-160-phase-6-validate-checks.md`, when read, then it documents the Phase 6 `gz validate --requirements` and `--commit-trailers` commits with linkage to REQ-0.41.0-05-NN.
- [ ] REQ-0.41.0-05-03: Given the ledger, when `gz task list OBPI-0.41.0-05` runs, then at least five TASK events (one per REQ 05-01 through 05-05) are present and in the `completed` state.
- [ ] REQ-0.41.0-05-04: Given `docs/design/adr/pre-release/ADR-0.41.0-tdd-emission-and-graph-rot-remediation/ADR-CLOSEOUT-FORM.md`, when read, then the GHI-160 summary table shows explicit commit-to-OBPI mapping (not "grandfathered").
- [ ] REQ-0.41.0-05-05: Given `uv run gz adr audit-check ADR-0.41.0`, when invoked after this OBPI completes, then no audit gaps attributable to GHI-160 Phases 1-7 are reported.

## Completion Checklist

- [ ] Gate 1/2/3/5 recorded
- [ ] Audit artifacts updated
- [ ] Ledger TASK events emitted
- [ ] Evidence filled

## Evidence

### Value Narrative

Before this OBPI: GHI-160 Phases 1-7 landed as a meta-remedy without a governing ADR. The Phase 7 audit used "grandfathered" language to explain why its commits lacked `Task:` trailers. That's an indefinite exception, not a fix. After this OBPI: the program has a formal governance home; every Phase 1-7 commit traces to a REQ on a specific OBPI; the audit artifact becomes primary evidence rather than a standing exception.

### Key Proof

```bash
$ uv run gz adr audit-check ADR-0.41.0
ADR-0.41.0: all OBPIs have matching evidence artifacts.
OBPI-0.41.0-05: 5/5 REQs covered by audit artifacts.
Phase 1-7 historical linkage: complete.
```

### Implementation Summary

- Files updated:
- TASK events emitted:
- Date completed:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: at ADR closeout
- Date: n/a

---

**Brief Status:** Draft

**Date Completed:** -
