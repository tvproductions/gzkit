---
id: OBPI-0.0.26-03-clustering-chore
parent: ADR-0.0.26-evaluation-feedback-loop-doctrine
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.26-03-clustering-chore: `eval-feedback-cluster` chore

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/ADR-0.0.26-evaluation-feedback-loop-doctrine.md`
- **Checklist Item:** #3 — "Author the `eval-feedback-cluster` chore — periodic clustering over `adr-evaluation` events and `gz-justify` artifacts; emits structured proposals report"

**Status:** Draft

## Objective

Author a chore that periodically scans recent `adr-evaluation` ledger events and `gz-justify` artifacts, groups by recurring weak-dimension or confusion-shape patterns, and emits a structured proposals report when a pattern recurs ≥3 times across distinct artifacts.

## Lane

**Heavy** — New chore + new ledger reader; runtime contract change to the chore-runner surface.

## Allowed Paths

- `src/gzkit/chores/eval-feedback-cluster/` — new chore package (CHORE.md, acceptance.json, README.md, code modules)
- `.gzkit/chores/eval-feedback-cluster/` — project-local overlay
- `src/gzkit/chores/registry.json` — register the new chore
- `src/gzkit/chores/eval_feedback_cluster_lib.py` — clustering implementation (separate module per pythonic.md size limits)
- `tests/chores/test_eval_feedback_cluster.py`
- `data/eval_feedback_thresholds.json` — `cluster_min_recurrence` threshold (default 3)
- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/**`

## Denied Paths

- `src/gzkit/governance/trust_audits.py` — validator additions for proposal output happen in OBPI-04
- `AGENTS.md`, `docs/governance/**` — doc updates in OBPI-04
- `features/**` — BDD coverage in OBPI-05

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Chore named `eval-feedback-cluster` registered in chores registry, follows the two-surface layout (canonical `src/gzkit/chores/eval-feedback-cluster/`, project-local overlay).
2. REQUIREMENT: `gz chores run eval-feedback-cluster` reads `adr-evaluation` events from `.gzkit/ledger.jsonl` (last N days, configurable) and walks `gz-justify` artifact paths recursively.
3. REQUIREMENT: Clustering buckets by `(dimension_name, score_band)` for low-score patterns and by `(red_team_challenge_id)` for red-team patterns; for justify artifacts, by recurring confusion-shape keywords extracted from the structured scaffold.
4. REQUIREMENT: When any bucket has `>= cluster_min_recurrence` distinct artifacts (default 3), emit a proposal record into the chore's proofs directory at `.gzkit/chores/eval-feedback-cluster/proofs/proposal-<timestamp>.json`.
5. REQUIREMENT: Proposal record schema: `{cluster_key, recurrence_count, source_artifact_ids, source_artifact_paths, summary, proposed_rule_target}`.
6. REQUIREMENT: Chore is idempotent: running twice without new evidence produces no duplicate proposals (dedup by content hash).
7. REQUIREMENT: Chore is read-only at the `.gzkit/ledger.jsonl` and `docs/design/adr/**` surfaces; only writes to its own proofs directory.
8. REQUIREMENT: Tests cover: zero-evidence run produces empty report; below-threshold cluster produces no proposal; at-threshold cluster produces a proposal; multiple thresholds produce multiple proposals; idempotent re-run.
9. REQUIREMENT: Tests use `tempfile`-backed ledger and tempfile justify-artifact fixtures.
10. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.26-03-NN)`.
11. REQUIREMENT: NEVER include the operator's personal email.
12. REQUIREMENT: NEVER write outside the chore's own proofs directory.
13. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (event shape unstable), STOP.

## Discovery Checklist

- [ ] Parent ADR § Decision item 3
- [ ] OBPI-0.0.26-01 evidence — confirm event shape
- [ ] `.claude/rules/chores.md` § Two-Surface Layout (ADR-0.0.21)
- [ ] `src/gzkit/chores/<existing-chore>/` — example of an existing chore's structure
- [ ] `.gzkit/skills/gz-justify/SKILL.md` — confirm artifact path convention

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] RGR; tests pass
### Code Quality
- [ ] Lint, type clean
### Gate 3: Docs (Heavy)
- [ ] In OBPI-04
### Gate 4: BDD (Heavy)
- [ ] In OBPI-05
### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/chores/test_eval_feedback_cluster.py -v
uv run gz validate --chores-layout
# Smoke run
uv run gz chores show eval-feedback-cluster
uv run gz chores run eval-feedback-cluster
```

## Acceptance Criteria

- [ ] REQ-0.0.26-03-01: Given the chore registered in the registry, when `gz chores list` runs, then `eval-feedback-cluster` appears.
- [ ] REQ-0.0.26-03-02: Given fewer than 3 weak-dimension occurrences across distinct artifacts, when the chore runs, then no proposal record is emitted.
- [ ] REQ-0.0.26-03-03: Given ≥3 occurrences of the same weak dimension across distinct artifacts, when the chore runs, then exactly one proposal record is emitted with the source artifact IDs.
- [ ] REQ-0.0.26-03-04: Given a chore re-run with no new evidence, when the chore runs, then no duplicate proposals are emitted (idempotent).
- [ ] REQ-0.0.26-03-05: Given `gz validate --chores-layout`, when the chore's two-surface layout is verified, then exit 0.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR; tests pass
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# RGR observations + unittest output
```

### Code Quality
```text
# lint/typecheck output
```

### Gate 5 (Human)
```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` (heavy + foundation requires human)
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
