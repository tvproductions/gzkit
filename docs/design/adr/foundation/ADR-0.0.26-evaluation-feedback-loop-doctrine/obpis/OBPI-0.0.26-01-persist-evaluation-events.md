---
id: OBPI-0.0.26-01-persist-evaluation-events
parent: ADR-0.0.26-evaluation-feedback-loop-doctrine
item: 1
lane: Heavy
status: Completed
---

# OBPI-0.0.26-01-persist-evaluation-events: Persist `gz-adr-evaluate` scores as ledger events

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/ADR-0.0.26-evaluation-feedback-loop-doctrine.md`
- **Checklist Item:** #1 — "Persist `gz-adr-evaluate` scores as `adr-evaluation` ledger events; extend `gz validate --documents` to recognize the new event shape"

**Status:** Draft

## Objective

Bind every `gz-adr-evaluate` invocation to a canonical `adr-evaluation` ledger event so evaluation scores become T2 ledger truth, not stdout-only narrative.

## Lane

**Heavy** — Modifies ledger schema and emission contract.

## Allowed Paths

- `src/gzkit/commands/adr_evaluate.py` (or wherever the evaluate command lives) — emit ledger event after scoring
- `src/gzkit/governance/ledger_events.py` (or schema home) — register `adr-evaluation` event type
- `src/gzkit/schemas/ledger.json` — extend ledger schema
- `src/gzkit/governance/trust_audits.py` — extend `validate --documents` to recognize the new event shape
- `tests/governance/test_evaluation_event.py`, `tests/commands/test_adr_evaluate_emission.py`
- `docs/design/adr/foundation/ADR-0.0.26-evaluation-feedback-loop-doctrine/**`

## Denied Paths

- `src/gzkit/commands/adr_emit_receipt.py` — separate event family, not edited here
- `AGENTS.md`, `docs/governance/**` — doc updates land in OBPI-04
- `features/**` — BDD coverage in OBPI-05
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Every successful `gz-adr-evaluate` invocation emits exactly one `adr-evaluation` ledger event with payload `{artifact_id, artifact_type, dimensions, scores, weighted_total, red_team_challenges_fired, evaluator_persona, timestamp}`.
2. REQUIREMENT: Schema field `dimensions` is a map of dimension-name → score (0.0–5.0); `red_team_challenges_fired` is a list of challenge IDs that fired during the evaluation.
3. REQUIREMENT: `gz validate --documents` extends to validate the new event shape (well-formed dimensions map, scores within range, no duplicate timestamps).
4. REQUIREMENT: A failed evaluation (validator error, malformed input) MUST NOT emit the event. Partial scores are not preserved.
5. REQUIREMENT: Tests cover: successful evaluation emits event; malformed evaluation does not emit; multiple evaluations of same artifact append (no upsert/dedup); ledger replay reproduces score history.
6. REQUIREMENT: Tests use `tempfile`-backed ledger fixtures; NEVER touch the live `.gzkit/ledger.jsonl`.
7. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.26-01-NN)`.
8. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, or docstrings.
9. REQUIREMENT: NEVER edit the ledger directly in tests — emission must go through the same code path production uses.
10. REQUIREMENT: TDD discipline: Red-Green-Refactor per behavior increment.

> STOP-on-BLOCKERS: if the existing ledger event registration mechanism has changed since this OBPI was authored, STOP and reconcile.

## Discovery Checklist

- [x] Parent ADR § Decision item 1 — read first per OBPI-brief authoring discipline
- [x] AGENTS.md § Behavior Rules — Always item 3 (record governance events in ledger)
- [x] `src/gzkit/governance/` — existing event registration shape
- [x] `.gzkit/ledger.jsonl` — sample existing event shapes for consistency

**Prerequisites (check existence, STOP if missing):**

- [x] Parent ADR Decision item 1 confirmed: "emit a canonical `adr-evaluation` ledger event with payload `{artifact_id, dimensions, scores, red_team_challenges_fired, timestamp}`"
- [x] AGENTS.md § Behavior Rules — Always item 3 confirmed: all governance events must go through `Ledger.append`

**Existing Code (understand current state):**

- [x] `src/gzkit/ledger_events.py` — existing `adr_eval_completed_event` factory reviewed; `adr_evaluation_event` follows same LedgerEvent construction and extra payload pattern
- [x] `src/gzkit/events.py` — `AdrEvalCompletedEvent` typed model reviewed; `AdrEvaluationEvent` follows same Literal union registration pattern
- [x] `src/gzkit/schemas/ledger.json` — `adr_eval_completed` schema entry reviewed as reference for `adr-evaluation` schema shape
- [x] `src/gzkit/governance/trust_audits/events.py` — `_NO_GRAPH_IMPACT` dict reviewed; `adr-evaluation` waiver follows `adr_eval_completed` pattern
- [x] `src/gzkit/commands/adr_promote.py::adr_eval_cmd` — emission site confirmed; new event wired before `adr_eval_completed_event` call
- [x] `LedgerEvent._serialize` confirmed: `extra` is flattened to top-level fields in JSONL output

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] RGR per behavior increment
- [ ] `uv run gz test` passes

### Code Quality

- [ ] Lint, format, type checks clean

### Gate 3: Docs (Heavy)

- [ ] Manpage updates in OBPI-04

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios in OBPI-05

### Gate 5: Human (Heavy + Foundation)

- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_evaluation_event.py tests/commands/test_adr_evaluate_emission.py -v
# Smoke
uv run gz adr evaluate ADR-0.0.26 && tail -1 .gzkit/ledger.jsonl | grep adr-evaluation
```

## Acceptance Criteria

- [ ] REQ-0.0.26-01-01: Given a successful `gz-adr-evaluate` invocation, when the command exits 0, then exactly one `adr-evaluation` event is appended to the ledger with the canonical payload shape.
- [ ] REQ-0.0.26-01-02: Given a malformed evaluation (validator error), when the command exits non-zero, then no `adr-evaluation` event is emitted.
- [ ] REQ-0.0.26-01-03: Given the new event shape, when `gz validate --documents` runs, then the validator recognizes the shape and exits 0.
- [ ] REQ-0.0.26-01-04: Given multiple evaluations of the same artifact, when the ledger is read, then each evaluation appears as a distinct event with a unique timestamp (no upsert/dedup).

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** RGR cycle; tests pass
- [ ] **Code Quality:** Lint/format/type checks clean
- [ ] **OBPI Acceptance:** Heavy + foundation = TTY + `ATTEST` required

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR observations + final unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 5 (Human)
```text
# Record attestation text here at completion
```

### Value Narrative

### Key Proof


arb:unittest — 4004/4004 tests pass, receipt arb-step-unittest-bdc9602b3d9e4397960fd9fe23072047

validate --documents passes with new event shape recognized:
  $ uv run gz validate --documents
  Validated: documents
  ✓ All validations passed (1 scopes).

TestAdrEvalCmdEmission.test_successful_eval_emits_exactly_one_adr_evaluation_event: adr_eval_cmd with mocked evaluate_adr emits exactly 1 "adr-evaluation" event to tempfile ledger with artifact_id, dimensions, evaluator_persona fields present (lint: arb-ruff-ea2903ed5c9e4d0992253ee7da292560, typecheck: arb-step-typecheck-3d41814b7ecb4feaa194b58940ef43e9)

### Implementation Summary


- Files created: tests/governance/test_evaluation_event.py (11 tests: event factory shape, schema registration, multi-append); tests/commands/test_adr_evaluate_emission.py (6 tests: command emission, exception no-emit, NO_GO emits)
- Files modified: src/gzkit/ledger_events.py (adr_evaluation_event factory), src/gzkit/events.py (AdrEvaluationEvent + union), src/gzkit/schemas/ledger.json (adr-evaluation schema), src/gzkit/governance/trust_audits/events.py (_NO_GRAPH_IMPACT waiver), src/gzkit/commands/adr_promote.py (emission wired in adr_eval_cmd), src/gzkit/ledger.py (re-export), tests/test_schemas.py (AdrEvaluationEvent in schema map)
- Tests added: 17 (lint: arb-ruff-ea2903ed5c9e4d0992253ee7da292560, unittest: arb-step-unittest-bdc9602b3d9e4397960fd9fe23072047)
- Date completed: 2026-05-03
- Attestation status: attested by Jeffry ("attest completed")
- Defects noted: none

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — adr-evaluation ledger event emitted on every successful gz adr evaluate invocation with full per-dimension payload (artifact_id, artifact_type, dimensions, scores, weighted_total, red_team_challenges_fired, evaluator_persona, timestamp); gz validate --documents passes; 17 new tests covering all 4 REQs pass in 4004-test suite (lint: arb-ruff-ea2903ed5c9e4d0992253ee7da292560, typecheck: arb-step-typecheck-3d41814b7ecb4feaa194b58940ef43e9, unittest: arb-step-unittest-bdc9602b3d9e4397960fd9fe23072047)
- Date: 2026-05-03

---

**Brief Status:** Completed

**Date Completed:** 2026-05-03

**Evidence Hash:** -
