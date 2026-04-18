---
id: OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity
parent: ADR-0.5.0-skill-lifecycle-governance
item: 5
lane: Heavy
status: attested_completed
---

# OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity

**Brief Status:** Completed

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #5 -- "Align OBPI completion runtime semantics with AirlineOps acceptance protocol."

## Objective

Enforce OBPI completion semantics at runtime so `completed` receipts are fail-closed on evidence and heavy/foundation inheritance requires human attestation evidence before acceptance can be recorded.

## Lane

**Heavy**

## Allowed Paths

- `AGENTS.md`
- `src/gzkit/cli.py`
- `src/gzkit/ledger.py`
- `src/gzkit/schemas/ledger.json`
- `docs/governance/**`
- `docs/user/**`
- `tests/**`

## Denied Paths

- New dependencies
- External network calls
- Destructive git operations

## Requirements (FAIL-CLOSED)

1. OBPI completion transitions MUST enforce heavy/foundation attestation inheritance.
2. Runtime checks MUST fail closed when required completion evidence is missing.
3. Ledger events MUST capture machine-readable completion evidence.
4. Completion semantics MUST preserve value narrative and key proof requirements.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [x] Runtime completion semantics tests added and passing.

### Gate 3: Docs

- [x] Runtime completion protocol documented for operators.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] Human attestation received for OBPI completion (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] REQ-0.5.0-05-01: Completion evidence enforcement matches heavy/foundation inheritance rules.
- [x] REQ-0.5.0-05-02: Ledger/schema surfaces represent completion evidence deterministically.
- [x] REQ-0.5.0-05-03: Runtime/command docs reflect fail-closed completion protocol.

## Evidence

### Implementation Summary

- Files created/modified:
  - `src/gzkit/cli.py`
  - `src/gzkit/ledger.py`
  - `src/gzkit/schemas/ledger.json`
  - `tests/test_cli.py`
  - `tests/test_ledger.py`
  - `docs/user/commands/obpi-emit-receipt.md`
  - `docs/user/concepts/lifecycle.md`
  - `docs/governance/governance_runbook.md`
  - `docs/governance/GovZero/validation-receipts.md`
- Runtime parity behavior implemented:
  - Added fail-closed completed-receipt validator requiring `value_narrative` and `key_proof`.
  - Enforced heavy/foundation inheritance checks:
    `human_attestation=true`, non-empty `attestation_text`,
    valid `attestation_date` (`YYYY-MM-DD`), and `--attestor human:<name>`.
  - Added machine-readable normalization in receipt evidence:
    `obpi_completion`, `attestation_requirement`, `parent_adr`, `parent_lane`.
  - Added top-level `obpi_completion` on `obpi_receipt_emitted` ledger events and schema enum support (`completed`, `attested_completed`, `not_completed`).
  - Kept non-`completed` receipts explicit by defaulting `obpi_completion` to `not_completed` when evidence is provided.
- AirlineOps parity intent:
  - Runtime now enforces the same ceremony-critical boundary: heavy/foundation completion requires human authority evidence before completion can be treated as attested.
- Date implemented: 2026-03-01

### Verification Commands Run (2026-03-01)

```text
uv run -m unittest tests.test_cli.TestSkillCommands tests.test_cli.TestAdrRuntimeCommands
Ran 35 tests in 0.684s
OK

uv run -m unittest tests.test_ledger
Ran 23 tests in 0.005s
OK

uv run gz lint
All checks passed

uv run gz test
Ran 271 tests in 2.347s
OK

uv run gz validate --documents
All validations passed
```

### Key Proof

```text
uv run gz obpi emit-receipt OBPI-0.5.0-05-obpi-acceptance-protocol-runtime-parity \
  --event completed \
  --attestor human:jeff \
  --evidence-json '{"value_narrative":"manual completion now auditable","key_proof":"uv run gz status --table","human_attestation":true,"attestation_text":"attest completed","attestation_date":"2026-03-01"}' \
  --dry-run

Dry-run event payload includes:
  "obpi_completion": "attested_completed"
  "attestation_requirement": "required"
```

### Human Attestation

- Attestor: Human operator (in-session)
- Attestation: "attest completed"
- Date: 2026-03-01
- Scope: OBPI-0.5.0-05 runtime parity evidence reviewed and accepted
