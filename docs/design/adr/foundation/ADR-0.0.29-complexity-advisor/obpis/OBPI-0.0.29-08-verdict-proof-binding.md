---
id: OBPI-0.0.29-08-verdict-proof-binding
parent: ADR-0.0.29
item: 8
lane: Heavy
status: Draft
---

# OBPI-0.0.29-08-verdict-proof-binding: Verdict ↔ Proof Binding

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #8 — "Verdict ↔ proof binding (every diagnosis carries non-empty proof: tuple[ProofRange, ...]; engine fails closed if proof unavailable)"

**Status:** Draft

## Objective

Codify the verdict ↔ proof binding as a defense-in-depth invariant: model-layer enforcement (OBPI-01: empty proof raises `ValidationError`), engine-layer enforcement (OBPI-02: engine fails closed with `EngineError` before model instantiation if proof is unavailable), and validator-layer enforcement (this OBPI: `gz validate --advisor-proof-binding` scans diagnosis fixtures and ledger events for any diagnosis lacking proof and fail-closes). The validator is the gate-time defense against future regressions in either lower layer.

## Lane

**Heavy** — New CLI flag is a contract change per `.gzkit/rules/cli.md`; new validator is a Mechanical-class rule audit. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/governance/trust_audits.py` — add `validate_advisor_proof_binding`
- `src/gzkit/cli/parser_artifacts.py` — register `--advisor-proof-binding` flag on `gz validate`
- `src/gzkit/commands/validate.py` (or wherever the dispatcher lives) — wire the flag and `--all` aggregation
- `tests/governance/test_advisor_proof_binding_validator.py`
- `features/advisor_proof_binding.feature` — behave scenarios tagged with REQ IDs
- `docs/user/manpages/gz-validate.md` — manpage section for the new flag
- `docs/user/runbook.md` — entry under "Complexity doctrine surfaces"
- `docs/governance/advisory-rules-audit.md` — scorecard entry classifying the new validator scope as Mechanical
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-08-verdict-proof-binding.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is OBPI-01 (the model-layer enforcement is OBPI-01's contract)
- `src/gzkit/complexity/advisor/engine.py` — engine is OBPI-02 (the engine-layer enforcement is OBPI-02's contract)
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `validate_advisor_proof_binding` scans (a) any persisted diagnosis fixtures under `tests/fixtures/advisor/` (used by OBPI-02/03/06 tests); (b) any `intrinsic-complexity-attestation` ledger events whose payload references a diagnosis (cross-check: the cited diagnosis must have non-empty proof); (c) the JSON Schema at `src/gzkit/schemas/advisor_diagnosis.json` (assert it requires non-empty `proof`).
2. REQUIREMENT: The validator fail-closes (exit 3) on: any fixture diagnosis with empty proof; any ledger-event-cited diagnosis with empty proof; the JSON Schema not requiring non-empty proof.
3. REQUIREMENT: The CLI flag `--advisor-proof-binding` is registered on `gz validate` and integrates into both `gz validate --all` and `gz check`.
4. REQUIREMENT: The exit-code map per `.claude/rules/cli.md`: 0 success, 3 policy breach. System errors exit 2.
5. REQUIREMENT: The validator's failure messages name the file path + line number (for fixtures) or ledger event ID (for ledger entries) where the empty-proof diagnosis was found, so the operator can navigate directly to the defect.
6. REQUIREMENT: A speculative-marker escape (per the precedent in `.claude/rules/governance-core.md`) is supported for fixtures explicitly named as "negative case" tests of the empty-proof rejection (the model-layer test that asserts `ValidationError` on empty proof is not itself a defect — it is the test of the defense).
7. REQUIREMENT: Tests cover: well-formed diagnosis fixtures pass (exit 0); a fixture with empty proof fails (exit 3) with named error; a ledger event citing an empty-proof diagnosis fails; JSON Schema lacking the non-empty-proof constraint fails; the speculative-marker escape correctly skips negative-case fixtures; integration into `gz validate --all` and `gz check` fires the validator. Each test decorated with `@covers(REQ-0.0.29-08-NN)`.
8. REQUIREMENT: A behave scenario at `features/advisor_proof_binding.feature` tagged `@REQ-0.0.29-08-{02,03}` covers the two canonical failure paths.
9. REQUIREMENT: Manpage section + runbook entry land in the same patch per `.gzkit/rules/gate5-runbook-code-covenant.md`.
10. REQUIREMENT: The advisory-rules-audit scorecard entry classifies the validator scope as Mechanical.
11. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures.
12. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, manpage, runbook, or commit messages.

> STOP-on-BLOCKERS: if OBPI-01's model + JSON Schema and OBPI-02's engine are not landed, STOP — the validator scans those surfaces.

## Discovery Checklist

- [ ] OBPI-01 model + JSON Schema (`src/gzkit/complexity/advisor/diagnosis.py`, `src/gzkit/schemas/advisor_diagnosis.json`)
- [ ] OBPI-02 engine (engine-layer enforcement contract)
- [ ] OBPI-07 ledger event family (`intrinsic-complexity-attestation`)
- [ ] `src/gzkit/governance/trust_audits.py` — existing validator patterns (e.g. `validate_complexity_doctrine_links` from OBPI-0.0.27-07)
- [ ] `.claude/rules/governance-core.md` — speculative-marker precedent

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean
- [ ] Manpage section + runbook entry

### Gate 4: BDD (Heavy)
- [ ] Behave scenarios pass for two canonical failure paths

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --advisor-proof-binding
uv run gz validate --all
uv run gz check
uv run mkdocs build --strict
uv run gz arb step --name unittest -- uv run -m unittest tests/governance/test_advisor_proof_binding_validator.py -v
uv run -m behave features/advisor_proof_binding.feature
```

## Acceptance Criteria

- [ ] REQ-0.0.29-08-01: Given well-formed advisor fixtures and ledger events, when `gz validate --advisor-proof-binding` runs, then exit 0.
- [ ] REQ-0.0.29-08-02: Given a fixture diagnosis with empty proof, when the validator runs, then exit 3 with a named error citing the file + line.
- [ ] REQ-0.0.29-08-03: Given an `intrinsic-complexity-attestation` ledger event citing a diagnosis with empty proof, when the validator runs, then exit 3 with a named error citing the event ID.
- [ ] REQ-0.0.29-08-04: Given the JSON Schema fails to require non-empty proof, when the validator runs, then exit 3 with a named error.
- [ ] REQ-0.0.29-08-05: Given `gz validate --all` and `gz check`, when invoked, then the new validator fires.
- [ ] REQ-0.0.29-08-06: Given the manpage and runbook, when read, then the new flag is documented with at least one example.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: mkdocs --strict + manpage + runbook
- [ ] Gate 4: behave scenarios pass
- [ ] Gate 5: TTY + `ATTEST`

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)
```text
# Paste RGR + unittest output
```

### Code Quality
```text
# Paste lint/typecheck output
```

### Gate 3 (Docs)
```text
# Paste mkdocs --strict + manpage + runbook diffs
```

### Gate 4 (BDD)
```text
# Paste behave output
```

### Gate 5 (Human)
```text
# Record attestation + receipt IDs
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

### Closing Argument

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive attestation text
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
