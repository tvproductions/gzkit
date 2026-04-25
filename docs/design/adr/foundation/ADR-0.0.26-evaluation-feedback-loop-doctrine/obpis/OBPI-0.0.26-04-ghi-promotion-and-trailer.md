---
id: OBPI-0.0.26-04-ghi-promotion-and-trailer
parent: ADR-0.0.26-evaluation-feedback-loop-doctrine
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.26-04-ghi-promotion-and-trailer: Cluster → GHI proposals + provenance trailer

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/ADR-0.0.26-evaluation-feedback-loop-doctrine.md`
- **Checklist Item:** #4 — "Wire cluster output into automatic `enhancement` GHI authoring with `Eval-feedback-source` provenance trailer; extend `gz validate --commit-trailers` to validate the new trailer"

**Status:** Draft

## Objective

Convert clustering-chore proposal records into GitHub issues automatically (with operator approval), and validate that any rule edit landing under such a GHI carries an `Eval-feedback-source:` commit trailer naming the source artifacts.

## Lane

**Heavy** — Adds CLI surface (`gz chores propose-ghi <chore>`), extends commit-trailer validator, and updates AGENTS.md.

## Allowed Paths

- `src/gzkit/commands/chores.py` — add `propose-ghi` subcommand
- `src/gzkit/governance/trust_audits.py` — extend `validate --commit-trailers` to recognize `Eval-feedback-source:`
- `AGENTS.md` — § Behavior Rules updated with the trailer convention; § Defect-fix routing references the loop
- `.claude/rules/tests.md` — § Governance-intent trailers extends with `Eval-feedback-source:`
- `docs/governance/arb-middleware.md` — cross-reference the loop
- `tests/governance/test_eval_feedback_trailer.py`
- `tests/commands/test_chores_propose_ghi.py`
- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/**`

## Denied Paths

- `src/gzkit/chores/eval-feedback-cluster/` — owned by OBPI-03
- `features/**` — BDD coverage in OBPI-05

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: New CLI verb `gz chores propose-ghi eval-feedback-cluster` reads the most recent proposal records from the chore's proofs directory and authors a GHI per record via `gh issue create --label enhancement --label eval-feedback`.
2. REQUIREMENT: GHI body includes the cluster key, recurrence count, source artifact IDs, summary, and proposed rule target. Title uses pattern `eval-feedback: <cluster-summary> (recurrence ≥ N)`.
3. REQUIREMENT: The verb is operator-gated — TTY + `PROPOSE` confirmation per record (mirrors the attestation-authenticity discipline). Headless runs are advisory-only (write proposal record but do not file GHI).
4. REQUIREMENT: After successful filing, the proposal record is marked `filed` with the GHI URL appended; subsequent runs do not refile.
5. REQUIREMENT: `Eval-feedback-source:` is a recognized commit-trailer key. Format: `Eval-feedback-source: <event-id-or-artifact-path>` (repeatable).
6. REQUIREMENT: `gz validate --commit-trailers` recognizes the new trailer key alongside `Task:` and `Ceremony:`. A commit body that touches `.gzkit/rules/**` or `AGENTS.md` AND closes a GHI labeled `eval-feedback` MUST carry at least one `Eval-feedback-source:` trailer.
7. REQUIREMENT: AGENTS.md § Behavior Rules — Always gains a brief item describing the trailer; `.claude/rules/tests.md` § Governance-intent trailers expands the trailer table.
8. REQUIREMENT: Tests cover: propose-ghi with TTY confirm files GHI; without TTY produces advisory-only output; refile is idempotent; trailer validator recognizes the key; trailer validator fails on rule edit closing eval-feedback GHI without trailer.
9. REQUIREMENT: Tests mock the `gh` subprocess boundary; NEVER hit the real GitHub API.
10. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.26-04-NN)`.
11. REQUIREMENT: NEVER include the operator's personal email.
12. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if OBPI-03 has not landed (no proposal records to read), STOP.

## Discovery Checklist

- [ ] Parent ADR § Decision items 4 and 5
- [ ] OBPI-0.0.26-03 evidence — confirm proposal record schema stable
- [ ] `.claude/rules/tests.md` § Governance-intent trailers — existing trailer convention
- [ ] AGENTS.md § Behavior Rules — Always — for insertion point
- [ ] `src/gzkit/commands/adr_audit.py` `_enforce_human_attestation_authenticity` — TTY-confirmation pattern to mirror

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded
### Gate 2: TDD
- [ ] RGR; tests pass
### Code Quality
- [ ] Lint, type clean
### Gate 3: Docs (Heavy)
- [ ] AGENTS.md and rule updates landed in this OBPI; `mkdocs build --strict` exits 0
### Gate 4: BDD (Heavy)
- [ ] In OBPI-05
### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_eval_feedback_trailer.py tests/commands/test_chores_propose_ghi.py -v
uv run gz validate --commit-trailers
```

## Acceptance Criteria

- [ ] REQ-0.0.26-04-01: Given a proposal record from OBPI-03, when `gz chores propose-ghi eval-feedback-cluster` runs in a TTY with `PROPOSE` confirmation, then a GHI is filed with the canonical title pattern and body shape.
- [ ] REQ-0.0.26-04-02: Given the same in a headless environment, when the verb runs, then no GHI is filed and the proposal record is annotated `advisory-only`.
- [ ] REQ-0.0.26-04-03: Given a re-run with already-filed proposals, when the verb runs, then no duplicate GHIs are filed (idempotent).
- [ ] REQ-0.0.26-04-04: Given a commit touching `.gzkit/rules/**` and closing a GHI labeled `eval-feedback`, when `gz validate --commit-trailers` runs, then exit 3 if no `Eval-feedback-source:` trailer is present.
- [ ] REQ-0.0.26-04-05: Given the same commit with a valid trailer, when the validator runs, then exit 0.

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR; tests pass
- [ ] **Gate 3:** mkdocs strict clean
- [ ] **Code Quality:** clean
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD)
```text
# RGR + unittest output
```

### Code Quality
```text
# lint/typecheck output
```

### Gate 3 (Docs)
```text
# mkdocs build --strict output
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
