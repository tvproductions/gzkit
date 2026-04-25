---
id: OBPI-0.0.26-02-justify-binding-gate
parent: ADR-0.0.26-evaluation-feedback-loop-doctrine
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.26-02-justify-binding-gate: `gz validate --evaluation-justify-binding`

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/ADR-0.0.26-evaluation-feedback-loop-doctrine.md`
- **Checklist Item:** #2 — "Implement `gz validate --evaluation-justify-binding` — fail-closed when score < 3.0 or ≥3 red-team challenges fire and no `gz-justify` artifact exists for the parent artifact"

**Status:** Draft

## Objective

Mechanically enforce the existing advisory rule that `gz-justify` must be invoked when an `gz-adr-evaluate` dimension scores < 3.0 (or ≥3 red-team challenges fire). Today the rule lives in the skill description; the gate makes it fail-closed.

## Lane

**Heavy** — Adds a new validate scope and gates lifecycle advancement.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — new `validate_evaluation_justify_binding`
- `src/gzkit/cli/parser_artifacts.py` — register `--evaluation-justify-binding` flag
- `src/gzkit/commands/lifecycle.py` (or wherever artifact-state advance happens) — call the gate before advancing past Pending/Draft
- `data/eval_feedback_thresholds.json` — new config file with `low_score_threshold` (default 3.0) and `red_team_count_threshold` (default 3)
- `tests/governance/test_justify_binding_gate.py`
- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/**`

## Denied Paths

- `src/gzkit/skills/gz-justify/**` — skill description already prescribes the trigger; not edited here
- `src/gzkit/skills/gz-adr-evaluate/**` — skill description already prescribes the score range; not edited here
- `AGENTS.md`, `docs/governance/**` — doc updates land in OBPI-04
- `features/**` — BDD coverage in OBPI-05

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: New function `validate_evaluation_justify_binding(artifact_id) -> ValidationResult` reads ledger for `adr-evaluation` events for the artifact.
2. REQUIREMENT: For the most recent `adr-evaluation` event, if any `dimensions` score is < `low_score_threshold` OR `len(red_team_challenges_fired) >= red_team_count_threshold`, the gate requires a `gz-justify` artifact at the canonical path (`docs/design/adr/**/justify/<artifact-id>-<timestamp>.md` or wherever `gz-justify` writes).
3. REQUIREMENT: If the trigger fires and no qualifying `gz-justify` artifact exists, the validator exits 3 with a structured message naming the failing dimensions and the missing artifact path.
4. REQUIREMENT: The gate is invoked automatically before any artifact advances past `Pending` lifecycle state (or the first downstream gate, depending on integration point).
5. REQUIREMENT: Threshold values come from `data/eval_feedback_thresholds.json`, never hardcoded.
6. REQUIREMENT: Tests cover: trigger fires on low score → no artifact → exit 3; trigger fires on red-team count → no artifact → exit 3; trigger fires → qualifying artifact present → exit 0; trigger does not fire (all scores ≥ threshold, < N challenges) → exit 0 with no requirement.
7. REQUIREMENT: Tests use tempfile-backed ledger and tempfile-backed justify-artifact fixtures.
8. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.26-02-NN)`.
9. REQUIREMENT: NEVER include the operator's personal email.
10. REQUIREMENT: TDD discipline.

> STOP-on-BLOCKERS: if OBPI-01 has not landed, STOP — there are no `adr-evaluation` events to read.

## Discovery Checklist

- [ ] Parent ADR § Decision item 2
- [ ] OBPI-0.0.26-01 evidence — confirm event shape stable
- [ ] `gz-justify` skill SKILL.md — read existing trigger description and artifact path convention
- [ ] `gz-adr-evaluate` skill SKILL.md — confirm dimension scoring conventions

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
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_justify_binding_gate.py -v
# Smoke
uv run gz validate --evaluation-justify-binding ADR-<fixture-id>
```

## Acceptance Criteria

- [ ] REQ-0.0.26-02-01: Given an `adr-evaluation` event with a dimension score < 3.0 and no qualifying `gz-justify` artifact, when the gate runs, then exit 3 with the failing dimension named.
- [ ] REQ-0.0.26-02-02: Given an `adr-evaluation` event with ≥3 red-team challenges fired and no qualifying `gz-justify` artifact, when the gate runs, then exit 3.
- [ ] REQ-0.0.26-02-03: Given the same conditions but a qualifying `gz-justify` artifact present, when the gate runs, then exit 0.
- [ ] REQ-0.0.26-02-04: Given an `adr-evaluation` event with all scores ≥ 3.0 and < 3 challenges, when the gate runs, then exit 0 with no requirement.
- [ ] REQ-0.0.26-02-05: Given the threshold config in `data/eval_feedback_thresholds.json`, when the file is updated, then gate behavior reflects the new thresholds without code changes.

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
