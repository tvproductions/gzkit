---
id: OBPI-0.5.0-02-parity-verification-policy
parent: ADR-0.5.0-skill-lifecycle-governance
item: 2
lane: Heavy
status: in_progress
---

# OBPI-0.5.0-02-parity-verification-policy

**Brief Status:** Completed

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.5.0-skill-lifecycle-governance/ADR-0.5.0-skill-lifecycle-governance.md`
- **Checklist Item:** #2 -- "Define parity verification policy and runtime checks."

## Objective

Define and implement policy-backed parity checks so mirror drift and metadata violations are surfaced as explicit governance findings with clear blocking vs non-blocking semantics.

## Lane

**Heavy**

## Allowed Paths

- `src/gzkit/skills.py`
- `src/gzkit/cli.py`
- `src/gzkit/quality.py`
- `docs/user/commands/**`
- `tests/**`

## Denied Paths

- `src/gzkit/ledger.py`
- `features/**`

## Requirements (FAIL-CLOSED)

1. Parity policy MUST define blocking vs non-blocking findings.
2. Runtime command surface MUST expose parity checks for operators.
3. Aggregate quality checks MUST include parity audit execution.

## Quality Gates

### Gate 1: ADR

- [x] Scope is linked to parent ADR item.

### Gate 2: TDD

- [x] CLI and parity-policy tests added and passing.

### Gate 3: Docs

- [x] Command docs updated for parity policy behavior.

### Gate 4: BDD

- [x] N/A when `features/` is absent.

### Gate 5: Human

- [x] OBPI human attestation recorded (ADR-level Gate 5 closeout remains separate).

## Acceptance Criteria

- [x] REQ-0.5.0-02-01: `gz skill audit` reports parity findings deterministically.
- [x] REQ-0.5.0-02-02: `gz check` includes skill parity audit.
- [x] REQ-0.5.0-02-03: Policy behavior is documented and validated by tests.

## Evidence

### Implementation Summary

- Files created/modified: `src/gzkit/skills.py`, `src/gzkit/cli.py`, `docs/user/commands/skill-audit.md`, `docs/user/commands/agent-sync-control-surfaces.md`, `tests/test_skills_audit.py`, `tests/test_cli.py`, `tests/test_quality.py`
- Policy/runtime behavior implemented:
  - Added stable audit issue codes (`SKA-*`) and per-finding `blocking` semantics.
  - Reclassified stale mirror-only directories as non-blocking warnings by default (`SKA-MIRROR-DIR-UNEXPECTED`).
  - Added additive JSON counters: `blocking_error_count`, `non_blocking_warning_count`.
  - Preserved non-strict aggregate `gz check` behavior while supporting strict warning escalation via `gz skill audit --strict`.
- Tests added/updated:
  - `tests/test_skills_audit.py`: warning classification, issue codes, blocking semantics, deterministic ordering.
  - `tests/test_cli.py`: skill-audit warning/strict/json behavior and non-blocking aggregate-check scenario.
  - `tests/test_quality.py`: non-strict default wiring for `run_skill_audit`.
- Validation commands run:
  - `uv run -m unittest tests.test_skills_audit tests.test_quality tests.test_cli.TestSkillCommands`
  - `uv run gz skill audit`
  - `uv run gz skill audit --json`
  - `uv run gz parity check --json`
  - `uv run gz check`
  - `uv run gz lint`
  - `uv run gz test`
  - `uv run gz validate --documents`
- Validation outcome: PASS (all listed commands completed successfully on 2026-03-01)
- Human attestation: Operator explicitly requested implementation completion in-session on 2026-03-01.
- Date completed: 2026-03-01
