---
id: OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration
parent: ADR-0.10.0-obpi-runtime-surface
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration: OBPI proof and lifecycle integration

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- **Checklist Item:** #3 -- "Integrate OBPI proof state with lifecycle guidance and parity-dependent operator flows."

**Status:** Completed

## Objective

Integrate OBPI runtime state with REQ proof, closeout guidance, and parity-driven
operator flows so future AirlineOps pipeline imports target a stable gzkit-native
lifecycle surface instead of bespoke manual routines.

## Lane

**Heavy** -- This unit changes lifecycle guidance, proof semantics, and operator-facing closeout behavior.

## Allowed Paths

- `src/gzkit/commands/` -- closeout/status/gate surfaces that consume OBPI proof state.
- `src/gzkit/hooks/` -- parity-dependent hook/runtime integration points if in scope.
- `src/gzkit/ledger.py` and related proof consumers.
- `tests/` and `features/` -- lifecycle verification and BDD coverage.
- `docs/user/commands/`, `docs/user/concepts/`, `docs/governance/GovZero/` -- operator and governance docs.
- `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- ADR/OBPI evidence and linkage.

## Denied Paths

- Importing deferred AirlineOps pipeline hooks without compatible gzkit runtime support.
- Weakening heavy-lane attestation or receipt evidence requirements.
- Introducing hidden LLM-only lifecycle inference where deterministic proof is available.
- New dependencies or CI changes unrelated to lifecycle integration.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: OBPI proof state MUST be visible in lifecycle/closeout surfaces through deterministic command output.
1. REQUIREMENT: REQ linkage and proof gaps MUST surface as explicit drift or pending state, not implicit success.
1. REQUIREMENT: Operator docs MUST describe the OBPI-native flow coherently from verification through attestation and receipts.
1. NEVER: Mark or imply heavy-lane completion before explicit human attestation.
1. ALWAYS: Preserve compatibility with current receipt semantics while preparing clear integration seams for deferred AirlineOps parity hooks.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md`
- [ ] Parent ADR: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- [ ] `docs/governance/GovZero/validation-receipts.md`

**Context:**

- [ ] `src/gzkit/hooks/core.py`
- [ ] `src/gzkit/commands/status.py`
- [ ] `src/gzkit/commands/attest.py`
- [ ] `docs/design/adr/pre-release/ADR-0.9.0-airlineops-surface-breadth-parity/claude-hooks-intake-matrix.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] OBPI runtime contract and command surfaces from OBPI-0.10.0-01 and OBPI-0.10.0-02 are defined
- [ ] REQ-proof linkage strategy is accepted or explicitly stubbed

Status after implementation:

- [x] `AGENTS.md` / `CLAUDE.md`
- [x] Parent ADR and OBPI-0.10.0-01/02 runtime surfaces were reviewed before editing closeout behavior
- [x] `docs/governance/GovZero/validation-receipts.md` and operator lifecycle docs were audited for contract drift
- [x] REQ-proof linkage stayed on the existing `req_proof_inputs` contract; no new proof schema was introduced

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Coverage maintained: `uv run coverage run -m unittest discover tests && uv run coverage report`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Format clean: `uv run gz format`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz test
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run -m behave features/
uv run gz status
uv run gz closeout <adr-id> --dry-run
```

## Acceptance Criteria

- [x] REQ-0.10.0-03-01: Lifecycle/closeout surfaces report OBPI proof state deterministically.
- [x] REQ-0.10.0-03-02: REQ-proof gaps surface as explicit pending or drift state.
- [x] REQ-0.10.0-03-03: [doc] Operator docs describe an OBPI-native verification -> attestation -> receipt flow.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded.
- [x] Parent checklist item remains quoted and unchanged.
- [x] Existing runtime contract seams were consumed instead of duplicated:
  `src/gzkit/cli.py`, `src/gzkit/commands/status.py`, `src/gzkit/ledger.py`,
  `docs/user/commands/closeout.md`, and `docs/user/concepts/lifecycle.md`.

### Gate 2 (TDD)

```text
$ uv run gz test
Running tests...
Ran 328 tests in 4.205s
OK

Tests passed.

$ uv run coverage run -m unittest discover tests
Ran 328 tests in 5.336s
OK

$ uv run coverage report
TOTAL                                    9334   1882    80%
```

### Code Quality

```text
$ uv run gz format
Formatting code...
68 files left unchanged

All checks passed!

Format complete.

$ uv run gz lint
Running linters...
All checks passed!

ADR path contract check passed.
Lint passed.

$ uv run gz typecheck
Running type checker...
All checks passed!

Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict
INFO    -  Cleaning site directory
INFO    -  Building documentation to directory: /Users/jeff/Documents/Code/gzkit/site
INFO    -  Documentation built in 0.68 seconds
```

### Gate 4 (BDD)

```text
$ uv run -m behave features/
1 feature passed, 0 failed, 0 skipped
3 scenarios passed, 0 failed, 0 skipped
16 steps passed, 0 failed, 0 skipped
```

### Value Narrative

Before this change, OBPI runtime proof existed in status/reconcile internals, but
ADR closeout still behaved like an ADR-only ceremony. Operators could start
closeout without a deterministic OBPI blocker list, and the docs still described
closeout as a presentation-only step.

Now the same OBPI runtime issues that drive `gz obpi status` and
`gz obpi reconcile` also drive `gz closeout` and focused ADR status. Closeout
stops before `closeout_initiated` is recorded, prints `BLOCKERS:`, and points
operators at the exact OBPI reconcile commands needed to clear the proof gap.

### Key Proof

- `uv run gz obpi status OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration --json`
  now reports `runtime_state: attested_completed`,
  `attestation_requirement: required`, and zero issues.
- `uv run gz adr status ADR-0.10.0` now reports `OBPI Completion: 3/3 complete`
  and `Closeout Readiness: READY`.
- `uv run gz closeout ADR-0.10.0 --dry-run` now succeeds and presents the
  full closeout command set instead of `BLOCKERS:`.

### Implementation Summary

- Files created/modified: `src/gzkit/cli.py`, `src/gzkit/commands/status.py`,
  `tests/commands/common.py`, `tests/commands/test_runtime.py`,
  `tests/commands/test_status.py`, `docs/user/commands/closeout.md`,
  `docs/user/commands/adr-status.md`, `docs/user/commands/status.md`,
  `docs/user/concepts/closeout.md`, `docs/user/concepts/lifecycle.md`,
  `docs/user/concepts/obpis.md`, `docs/user/concepts/workflow.md`,
  `docs/user/index.md`, and this brief
- Tests added: closeout blocker coverage, closeout JSON payload coverage, heavy
  attestation-proof blocker coverage, and focused ADR closeout-readiness coverage
- Ledger events recorded: `gate_checked` pass events for Gates 2, 3, and 4 on
  `ADR-0.10.0-obpi-runtime-surface`, plus `obpi_receipt_emitted` (`completed`)
  for `OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration`
- Date completed: 2026-03-10

### Gate 5 (Human)

- [x] Human attestation received from the user on 2026-03-10.
- [x] Completion receipt can be emitted with matching attestation metadata.

## Human Attestation

- Attestor: human:jeff
- Attestation: Completed
- Date: 2026-03-10
- Scope: OBPI-0.10.0-03 proof and lifecycle integration accepted after operator review.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-10

**Evidence Hash:** 173dfc0
