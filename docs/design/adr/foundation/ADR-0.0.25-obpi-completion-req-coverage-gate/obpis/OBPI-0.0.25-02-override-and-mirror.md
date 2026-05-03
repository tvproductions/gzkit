---
id: OBPI-0.0.25-02-override-and-mirror
parent: ADR-0.0.25-obpi-completion-req-coverage-gate
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.25-02-override-and-mirror: --accept-uncovered override + ADR-emit-receipt mirror

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/ADR-0.0.25-obpi-completion-req-coverage-gate.md`
- **Checklist Item:** #2 — "Implement the `--accept-uncovered=<REQ>` override path with ledger event recording and TTY+`ACCEPT` confirmation discipline; mirror the gate in `gz adr emit-receipt --event closed`"

**Status:** Draft

## Objective

Add `--accept-uncovered=REQ-X.Y.Z-NN-MM` (repeatable) override flag to `gz obpi complete`, record each acceptance as a ledger event with operator name and rationale, gate the override path on TTY + `ACCEPT` confirmation for heavy/foundation, and mirror the entire coverage gate into `gz adr emit-receipt --event closed`.

## Lane

**Heavy** — Modifies completion runtime contract and ADR closeout contract.

## Allowed Paths

- `src/gzkit/commands/obpi_complete.py` — add `--accept-uncovered` flag handling and TTY confirmation
- `src/gzkit/commands/adr_audit.py` — mirror the coverage gate in `adr_emit_receipt_cmd`; model `_enforce_human_attestation_authenticity` for the TTY+confirmation pattern
- `src/gzkit/governance/req_coverage.py` — extend with override-record helper (no behavior change to OBPI-01 functions)
- `src/gzkit/ledger_events.py` — add `obpi_completion_uncovered_accept_event` factory (follows existing factory pattern; recording ledger events is core to REQ-3)
- `src/gzkit/ledger.py` — add re-export of the new factory in the late-import block (single-line addition)
- `src/gzkit/cli/parser_artifacts.py` — register `--accept-uncovered`, `--accept-uncovered-reason` flags; add `"closed"` to `gz adr emit-receipt` event choices
- `tests/commands/test_obpi_complete_coverage_gate.py` — extend with override scenarios
- `tests/commands/test_adr_emit_receipt_coverage_gate.py` — new wiring tests
- `docs/design/adr/foundation/ADR-0.0.25-obpi-completion-req-coverage-gate/**` — parent ADR package scope

## Denied Paths

- `src/gzkit/governance/req_coverage.py` core parsing/discovery functions — owned by OBPI-01
- `src/gzkit/commands/obpi_complete.py` lines implementing the OBPI-01 gate logic — extend only, do not modify
- `AGENTS.md`, `docs/user/runbook.md` — doc updates in OBPI-03
- `features/**` — BDD coverage in OBPI-03
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz obpi complete --accept-uncovered=REQ-X.Y.Z-NN-MM` (repeatable) accepts a list of REQs that the operator explicitly waives.
2. REQUIREMENT: Each `--accept-uncovered` argument MUST also carry an inline rationale via `--accept-uncovered-reason="<text>"` (or one rationale per REQ via repeatable pairing).
3. REQUIREMENT: Every accepted-uncovered REQ produces a ledger event of type `obpi-completion-uncovered-accept` with payload `{brief_id, req_id, operator, rationale, timestamp}`.
4. REQUIREMENT: For heavy or foundation parents, the override path requires interactive TTY + `ACCEPT` confirmation, modeled on `_enforce_human_attestation_authenticity`. Headless runs cannot use `--accept-uncovered`.
5. REQUIREMENT: For lite-non-foundation parents, `--accept-uncovered` records the ledger event without TTY (matching the existing lite-lane attestation discipline).
6. REQUIREMENT: The override prevents fail-closed exit 3 only for the explicitly named REQ-IDs; any unwaived gap still fails the gate.
7. REQUIREMENT: `gz adr emit-receipt --event closed` mirrors the coverage gate: it iterates the closing ADR's OBPIs, runs the same coverage check per brief, and refuses ADR closeout if any OBPI has unwaived gaps.
8. REQUIREMENT: Tests cover: single-REQ override succeeds; multi-REQ override succeeds; override with empty rationale fails-closed; headless heavy-lane override is refused; ADR closeout fails when any OBPI has an unwaived gap; ADR closeout succeeds when all gaps are waived.
9. REQUIREMENT: Tests use `tempfile`-backed ledger and TTY-mocking helpers; NEVER prompt the real terminal in unit tests.
10. REQUIREMENT: Each test decorated with `@covers(REQ-0.0.25-02-NN)`.
11. REQUIREMENT: NEVER include the operator's personal email in code or test fixtures.
12. REQUIREMENT: NEVER allow the override to suppress the receipt-binding gate from ADR-0.0.24 — these are independent gates.
13. REQUIREMENT: TDD discipline: Red-Green-Refactor per behavior increment.

> STOP-on-BLOCKERS: if OBPI-01 has not landed (gate logic does not exist), STOP.

## Discovery Checklist

**Prerequisites**

- [x] OBPI-0.0.25-01 completed and gate logic wired in `obpi_complete.py` — verified via `gz adr audit-check ADR-0.0.25`
- [x] AGENTS.md § OBPI Acceptance Protocol — TTY+`ATTEST` gate and `_enforce_human_attestation_authenticity` three-branch model studied
- [x] `.gzkit/rules/cli.md` § Exit Codes — exit 3 is Policy Breach; used for coverage gate failures

**Existing Code**

- [x] `src/gzkit/commands/adr_audit.py` — `_enforce_human_attestation_authenticity` (line ~444): three-branch TTY/agent-relayed/fail-closed model; `_is_human_attestation_tty_available`, `_active_pipeline_marker_exists` reused directly
- [x] `src/gzkit/ledger_events.py` — factory function pattern: `LedgerEvent(event=..., id=..., parent=..., extra={...})`; all event factories live here, not in `events.py`
- [x] `src/gzkit/governance/req_coverage.py` — `parse_brief_reqs` and `discover_covers` from OBPI-01; both AST-based, no test imports

## Quality Gates

### Gate 1: ADR

- [ ] Intent recorded
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] RGR per behavior increment
- [ ] `uv run gz test` passes

### Code Quality

- [ ] Lint clean
- [ ] Type check clean

### Gate 3: Docs (Heavy)

- [ ] Manpage updates land in OBPI-03

### Gate 4: BDD (Heavy)

- [ ] BDD scenarios in OBPI-03

### Gate 5: Human (Heavy + Foundation)

- [ ] TTY + `ATTEST` required

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz arb step --name unittest -- uv run -m unittest tests/commands/test_obpi_complete_coverage_gate.py tests/commands/test_adr_emit_receipt_coverage_gate.py -v
# Smoke: try a fixture brief with --accept-uncovered=REQ-X.Y.Z-NN-MM in a TTY and headless context
```

## Acceptance Criteria

- [ ] REQ-0.0.25-02-01: Given a heavy-lane brief with one uncovered REQ AND a TTY + `ACCEPT` confirmed `--accept-uncovered=<REQ>` flag, when `gz obpi complete` runs, then completion proceeds and a `obpi-completion-uncovered-accept` event is recorded.
- [ ] REQ-0.0.25-02-02: Given the same brief in a headless run, when `gz obpi complete --accept-uncovered=<REQ>` runs, then the override is refused and exit 3.
- [ ] REQ-0.0.25-02-03: Given two uncovered REQs and a single `--accept-uncovered` for one of them, when `gz obpi complete` runs, then exit 3 (the unwaived REQ still fails the gate).
- [ ] REQ-0.0.25-02-04: Given a closing ADR whose any OBPI has an unwaived REQ gap, when `gz adr emit-receipt --event closed` runs, then exit 3.
- [ ] REQ-0.0.25-02-05: Given the override path, when run without `--accept-uncovered-reason`, then exit 1 with a usage error (rationale is mandatory).

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded
- [ ] **Gate 2 (TDD):** RGR cycle; tests pass
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Documented
- [ ] **Key Proof:** Override accept + override refuse transcripts
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


uv run -m unittest tests.commands.test_obpi_complete_coverage_gate tests.commands.test_adr_emit_receipt_coverage_gate: 15 tests, 0 failures; heavy TTY-present waiver → proceeds + ledger event; headless → exit 3; partial waiver → exit 3; no rationale → exit 1; ADR unwaived gap → exit 3; waived gap → proceeds

### Implementation Summary


- obpi_completion_uncovered_accept_event factory (ledger_events.py); ObpiCompletionUncoveredAcceptEvent typed model (events.py); _enforce_uncovered_acceptance_confirmation three-branch TTY helper (adr_audit.py); _check_adr_obpi_coverage_gaps + --event closed branch (adr_audit.py); --accept-uncovered / --accept-uncovered-reason flags (parser_artifacts.py, obpi_complete.py); schema + event-handler waiver + per-flag docs (ledger.json, trust_audits/events.py, obpi-complete.md); 15 new unit tests

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed. — 15 new tests green (6 OBPI-02 override scenarios + 3 ADR closeout mirror scenarios); ruff arb-ruff-ed89979944e749d68dfa93739dbfd67f, typecheck arb-step-typecheck-509b68613534482689623f9168ef7bcc, unittest arb-step-unittest-b6d8369d4dec4f0682c64f3ac59417b9; all 3984 tests pass; --accept-uncovered escape-hatch wired with TTY+ACCEPT gate, ledger event per waiver, ADR closeout coverage mirror
- Date: 2026-05-03

---

**Brief Status:** Completed

**Date Completed:** 2026-05-03

**Evidence Hash:** -
