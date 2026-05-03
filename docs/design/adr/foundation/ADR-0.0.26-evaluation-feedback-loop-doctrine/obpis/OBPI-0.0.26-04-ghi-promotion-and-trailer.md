---
id: OBPI-0.0.26-04-ghi-promotion-and-trailer
parent: ADR-0.0.26-evaluation-feedback-loop-doctrine
item: 4
lane: Heavy
status: Completed
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
- `src/gzkit/commands/validate_cmd.py` — extend `validate --commit-trailers` to recognize `Eval-feedback-source:`
- `src/gzkit/tasks.py` — add `parse_eval_feedback_source_trailers` alongside `parse_task_trailers` / `parse_ceremony_trailers`
- `AGENTS.md` — § Behavior Rules updated with the trailer convention; § Defect-fix routing references the loop
- `.gzkit/rules/tests.md` — § Governance-intent trailers extends with `Eval-feedback-source:` (canonical; sync mirrors to `.claude/`)
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

**Prerequisites**

- [x] Parent ADR § Decision items 4 and 5 read; scope is GHI authoring from cluster proposals + `Eval-feedback-source:` trailer validation.
- [x] OBPI-0.0.26-03 landed: `src/gzkit/chores/eval_feedback_cluster_lib.py` present, `ProposalRecord` schema stable (`cluster_key`, `recurrence_count`, `source_artifact_ids`, `source_artifact_paths`, `summary`, `proposed_rule_target`, `content_hash`).
- [x] `AGENTS.md` § foundation+heavy lane → brief-level Gate 5 attestation required.
- [x] Allowed paths corrected: brief originally listed `src/gzkit/governance/trust_audits.py` (non-existent) and `.claude/rules/tests.md` (vendor mirror); fixed to `src/gzkit/commands/validate_cmd.py`, `src/gzkit/tasks.py`, `.gzkit/rules/tests.md` (GHI #393).

**Existing Code**

- [x] `src/gzkit/commands/chores.py` — chore subcommand structure reviewed; `chores_audit` is the insertion point for `chores_propose_ghi`.
- [x] `src/gzkit/commands/validate_cmd.py:126` — `_validate_commit_trailers` reads HEAD commit via `_head_commit_message_and_files`; extended with `_validate_eval_feedback_trailer`.
- [x] `src/gzkit/tasks.py:201` — `parse_ceremony_trailers` pattern mirrored for `parse_eval_feedback_source_trailers`.
- [x] `.gzkit/rules/tests.md` § Governance-intent trailers — `Task:` and `Ceremony:` rows confirmed; `Eval-feedback-source:` row added, version bumped.

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
- [ ] REQ-0.0.26-04-10: Each test function that covers this OBPI's requirements is decorated with `@covers(REQ-0.0.26-04-NN)`; `ProposalRecord` accepts optional `filed`, `ghi_url`, and `advisory` fields with safe defaults for backward compatibility.
- [ ] REQ-0.0.26-04-12: TDD Red-Green-Refactor discipline is followed for each behavior increment in this OBPI.

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


`uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_eval_feedback_trailer.py tests/commands/test_chores_propose_ghi.py -v` → 10/10 pass, receipt arb-step-unittest-21a133398809485eabc8c3ef18384ad5. Full suite: 4044/4044 pass (receipt arb-step-unittest-154922a0876345b0aa353247b3ed7d33). mkdocs strict clean (receipt arb-step-mkdocs-977013e2b7e3427998d10f5e9944f9e1). REQ parity uncovered: 0.

### Implementation Summary


- Files created: tests/commands/test_chores_propose_ghi.py, tests/governance/test_eval_feedback_trailer.py
- Files modified: src/gzkit/chores/eval_feedback_cluster_lib.py (ProposalRecord +filed/ghi_url/advisory fields), src/gzkit/tasks.py (parse_eval_feedback_source_trailers), src/gzkit/commands/chores.py (chores_propose_ghi), src/gzkit/cli/parser_maintenance.py (propose-ghi registration), src/gzkit/commands/validate_cmd.py (_validate_eval_feedback_trailer), config/doc-coverage.json, docs/user/manpages/gz-chores.md, docs/user/runbook.md, AGENTS.md, .gzkit/rules/tests.md, docs/governance/arb-middleware.md
- Tests added: 10 new (6 propose-ghi, 4 trailer validator)
- Date completed: 2026-05-03
- Attestation status: Human attested (heavy + foundation lane)
- Defects noted: GHI #393 (stale brief allowed-paths — fixed in session)

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — `gz chores propose-ghi eval-feedback-cluster` and `Eval-feedback-source:` trailer validation implemented and verified: 4044/4044 tests pass, mkdocs strict clean, REQ parity uncovered:0 (lint: receipt arb-ruff-6dcc205c146b45128c3ff3f1095c75cd, typecheck: receipt arb-step-typecheck-e449c576aaa74faa9cfbc2988d973974, unittest: receipt arb-step-unittest-21a133398809485eabc8c3ef18384ad5, mkdocs: receipt arb-step-mkdocs-977013e2b7e3427998d10f5e9944f9e1)
- Date: 2026-05-03

---

**Brief Status:** Completed

**Date Completed:** 2026-05-03

**Evidence Hash:** -
