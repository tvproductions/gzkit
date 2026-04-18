---
id: OBPI-0.10.0-01-obpi-runtime-contract-and-state-model
parent: ADR-0.10.0-obpi-runtime-surface
item: 1
lane: Heavy
status: in_progress
---

# OBPI-0.10.0-01-obpi-runtime-contract-and-state-model: OBPI runtime contract and state model

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- **Checklist Item:** #1 -- "Define the OBPI runtime contract and derived state model."

**Status:** Completed

## Objective

Define the machine-readable OBPI runtime contract so status, proof, reconciliation,
and future pipeline hooks derive from one deterministic state model instead of
brief text heuristics alone.

## Lane

**Heavy** -- This unit defines lifecycle semantics consumed by operator-facing
commands and future parity hooks.

## Allowed Paths

- `src/gzkit/ledger.py` -- OBPI state derivation and graph semantics.
- `src/gzkit/commands/status.py` -- runtime status interpretation boundaries.
- `src/gzkit/schemas/ledger.json` -- ledger event/schema contract if new OBPI runtime evidence fields are required.
- `tests/` -- unit tests for OBPI state derivation and compatibility semantics.
- `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/**` -- ADR/OBPI evidence and linkage.
- `docs/user/concepts/` and `docs/governance/GovZero/` -- runtime contract documentation if introduced.

## Denied Paths

- New external databases or network services.
- `../airlineops/**` -- canonical source remains read-only.
- Deleting or weakening existing ADR lifecycle semantics.
- CI files, lockfiles, or new dependencies unless a separate approved brief requires them.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: OBPI runtime state MUST derive from ledger and document evidence through deterministic rules.
1. REQUIREMENT: The OBPI model MUST define compatibility with existing ADR-first status, receipt, and audit flows.
1. REQUIREMENT: REQ-proof state inputs MUST be named and scoped, even if later OBPIs implement the consuming surfaces.
1. NEVER: Introduce an alternate planner/store that bypasses `.gzkit/ledger.jsonl`.
1. ALWAYS: Preserve human attestation as the authority boundary for heavy/foundation completion.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md`
- [x] Parent ADR: `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/ADR-0.10.0-obpi-runtime-surface.md`
- [x] `docs/design/adr/pre-release/ADR-0.7.0-obpi-first-operations/ADR-0.7.0-obpi-first-operations.md`

**Context:**

- [x] `src/gzkit/ledger.py`
- [x] `src/gzkit/commands/status.py`
- [x] `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/obpis/OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity.md`

**Prerequisites (check existence, STOP if missing):**

- [x] `.gzkit/ledger.jsonl`
- [x] `src/gzkit/schemas/ledger.json`

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
uv run gz register-adrs ADR-0.10.0-obpi-runtime-surface --all
uv run gz test
uv run gz lint
uv run gz typecheck
uv run mkdocs build --strict
uv run -m behave features/
uv run gz status
```

## Acceptance Criteria

- [x] REQ-0.10.0-01-01: OBPI runtime lifecycle states and evidence inputs are defined deterministically.
- [x] REQ-0.10.0-01-02: [doc] Compatibility boundaries with existing ADR-first receipt/audit behavior are explicit.
- [x] REQ-0.10.0-01-03: [doc] Required REQ-proof inputs for later OBPI runtime surfaces are documented.

## Runtime Contract

The canonical machine-readable contract is documented in
`docs/governance/GovZero/obpi-runtime-contract.md` and implemented by
`derive_obpi_semantics()` in `src/gzkit/ledger.py`.

The current implementation defines these machine-readable OBPI runtime states:

- `pending` -- no completion proof has been recorded yet
- `in_progress` -- some proof exists, but completion requirements are not fully satisfied
- `completed` -- lite-compatible completion proof is present
- `attested_completed` -- heavy/foundation-compatible completion proof is present with attestation evidence
- `validated` -- a validated receipt exists on top of completed proof
- `drift` -- ledger and brief evidence disagree or required proof is missing from one side

Required REQ-proof inputs are normalized under receipt evidence as `req_proof_inputs`.
Each item carries `name`, `kind`, `source`, `status`, and optional `scope` / `gap_reason`.
When explicit inputs are omitted, runtime normalization backfills them from
substantive `Key Proof` text and completed human-attestation evidence so legacy
receipts remain consumable.

Derived runtime payloads also carry `attestation_requirement` and `attestation_state`
so later status/reconcile/lifecycle surfaces do not re-derive authority semantics ad hoc.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

### Value Narrative

Before this OBPI closeout pass, the runtime contract itself was already present
in code and docs, but `ADR-0.10.0` still had a governance defect: its OBPI files
were not linked in ledger state, so operator runtime surfaces could only resolve
them as briefs and `gz obpi emit-receipt` could not consume them as first-class
ledger artifacts.

After this pass, the runtime contract remains canonical in
`docs/governance/GovZero/obpi-runtime-contract.md`, the contract is exercised by
ledger/status/schema tests, and `gz register-adrs ADR-0.10.0-obpi-runtime-surface --all`
can deterministically backfill missing `obpi_created` lineage for the promoted
ADR package without touching unrelated ADR work.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded.
- [x] Parent checklist item remains quoted and unchanged.
- [x] Canonical contract doc is linked from this brief and implemented by
  `derive_obpi_semantics()` in `src/gzkit/ledger.py`.

### Gate 2 (TDD)

```text
$ uv run gz test
Running tests...
Ran 323 tests in 3.944s
OK

Tests passed.

$ uv run coverage run -m unittest discover tests && uv run coverage report
Ran 323 tests in 5.202s
OK
TOTAL                                    9161   1193    87%
```

### Code Quality

```text
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

### Key Proof

```text
$ uv run gz register-adrs ADR-0.10.0-obpi-runtime-surface --all
Registered OBPI: OBPI-0.10.0-01-obpi-runtime-contract-and-state-model (parent: ADR-0.10.0-obpi-runtime-surface)
Registered OBPI: OBPI-0.10.0-02-obpi-query-and-reconcile-command-surfaces (parent: ADR-0.10.0-obpi-runtime-surface)
Registered OBPI: OBPI-0.10.0-03-obpi-proof-and-lifecycle-integration (parent: ADR-0.10.0-obpi-runtime-surface)

ADR registration complete: 0 adr_created event(s), 3 obpi_created event(s) recorded.

$ uv run gz obpi status OBPI-0.10.0-01-obpi-runtime-contract-and-state-model --json
{
  "linked_in_ledger": true,
  "runtime_state": "attested_completed",
  "proof_state": "recorded",
  "attestation_state": "recorded",
  "req_proof_state": "recorded"
}
```

### Implementation Summary

- Files created/modified:
  - `src/gzkit/ledger.py`, `src/gzkit/commands/status.py`, `src/gzkit/schemas/ledger.json`
  - `src/gzkit/cli.py`, `src/gzkit/hooks/core.py`, `src/gzkit/validate.py`
  - `docs/governance/GovZero/obpi-runtime-contract.md`
  - `docs/user/commands/obpi-status.md`, `docs/user/commands/obpi-reconcile.md`, `docs/user/commands/register-adrs.md`
  - `docs/design/adr/pre-release/ADR-0.10.0-obpi-runtime-surface/obpis/OBPI-0.10.0-01-obpi-runtime-contract-and-state-model.md`
- Tests added:
  - runtime contract normalization and state-derivation coverage in `tests/test_ledger.py`
  - focused OBPI status/reconcile payload coverage in `tests/commands/test_status.py`
  - receipt normalization coverage in `tests/commands/test_runtime.py`, `tests/test_obpi_validator.py`, and `tests/test_validate.py`
- targeted OBPI backfill coverage for `gz register-adrs --all` in `tests/commands/test_register_adrs.py`
- Date completed: 2026-03-10

## Human Attestation

- Attestor: human:jeff
- Attestation: Completed
- Date: 2026-03-10
- Scope: OBPI-0.10.0-01 runtime contract, state model, ledger linkage repair, and operator/runtime evidence reviewed and accepted.

---

**Brief Status:** Completed

**Date Completed:** 2026-03-10

**Evidence Hash:** d466491
