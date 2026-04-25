---
id: OBPI-0.0.29-01-advisor-diagnosis-schema
parent: ADR-0.0.29
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.29-01-advisor-diagnosis-schema: Advisor Diagnosis Schema

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/ADR-0.0.29-complexity-advisor.md`
- **Checklist Item:** #1 — "Advisor diagnosis schema (frozen Pydantic AdvisorDiagnosis, RefactorArchetype enum, DoctrinalFrame, ProofRange; JSON Schema mirror)"

**Status:** Draft

## Objective

Implement frozen Pydantic models `AdvisorDiagnosis`, `DoctrinalFrame`, `ProofRange`, and a `RefactorArchetype` enum at `src/gzkit/complexity/advisor/diagnosis.py`, with a JSON Schema mirror at `src/gzkit/schemas/advisor_diagnosis.json`. This is the data contract every downstream OBPI in ADR-0.0.29 binds against.

## Lane

**Heavy** — New runtime data contract consumed by OBPI-02 engine, OBPI-03 CLI, OBPI-08 proof binding, and downstream ADR-0.0.30 authoring-guidance. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/advisor/__init__.py`
- `src/gzkit/complexity/advisor/diagnosis.py`
- `src/gzkit/schemas/advisor_diagnosis.json`
- `tests/complexity/advisor/test_diagnosis.py`
- `docs/design/adr/foundation/ADR-0.0.29-complexity-advisor/obpis/OBPI-0.0.29-01-advisor-diagnosis-schema.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/engine.py` — engine is OBPI-02
- `src/gzkit/complexity/advisor/intrinsic.py` — attestation is OBPI-07
- `src/gzkit/complexity/advisor/timeout.py` — timeout is OBPI-09
- `src/gzkit/commands/complexity_advise.py` — CLI is OBPI-03
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `RefactorArchetype` is a `StrEnum` with exactly ten initial values: `long_parameter_list`, `arrowhead`, `switch_on_type`, `feature_envy`, `large_class`, `divergent_change`, `shotgun_surgery`, `primitive_obsession`, `data_clumps`, `message_chain`. Amendments require ADR-0.0.29 ceremony per § Decision rationale #2.
2. REQUIREMENT: `DoctrinalFrame` is a frozen Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`. Fields: `authority: Literal["fowler", "martin", "page_jones", "constantine"]`, `citation: str`, `excerpt: str`.
3. REQUIREMENT: `ProofRange` is a frozen Pydantic `BaseModel`. Fields: `file_path: str` (relative to repo root), `start_line: int` (≥ 1), `end_line: int` (≥ `start_line`), `ast_node_kind: str`.
4. REQUIREMENT: `AdvisorDiagnosis` is a frozen Pydantic `BaseModel`. Fields: `metric: str`, `crossing_band: Literal["block", "warn", "advise"]`, `crossing_value: float`, `archetype: RefactorArchetype`, `doctrinal_frame: DoctrinalFrame`, `proof: tuple[ProofRange, ...]` (non-empty), `recommended_move: str`, `intrinsic_attestation: IntrinsicAttestationRef | None` (optional). `IntrinsicAttestationRef` is defined here as a forward stub model with `attestation_id: str`; full implementation lands at OBPI-07.
5. REQUIREMENT: The JSON Schema at `src/gzkit/schemas/advisor_diagnosis.json` enforces: `proof` is a non-empty array; `archetype` is in the enum; `crossing_band` is one of the three trigger-semantic values; `authority` is one of the four canonical authorities.
6. REQUIREMENT: The `proof` field MUST be non-empty; `AdvisorDiagnosis` instantiation with `proof=()` raises `ValidationError`. This codifies ADR § Decision rationale #5 at the model layer.
7. REQUIREMENT: All four model classes use `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`; mutation attempts raise.
8. REQUIREMENT: Tests cover: valid instantiation; rejection of empty `proof`; rejection of `authority` outside enum; rejection of `archetype` outside enum; rejection of `crossing_band` outside enum; rejection of `end_line < start_line`; mutation raises; JSON Schema validates a serialized model dict; JSON Schema rejects empty proof / unknown enum. Each test decorated with `@covers(REQ-0.0.29-01-NN)`.
9. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures.
10. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, or docstrings.

> STOP-on-BLOCKERS: pydantic ≥ 2 is required (already runtime dep); if the constraint changes, reconcile before drafting.

## Discovery Checklist

- [ ] Parent ADR § Decision — schema field shapes, four-authority canon, ten-archetype canon
- [ ] `.claude/rules/models.md` — Pydantic immutable patterns
- [ ] `.claude/rules/pythonic.md` — size limits
- [ ] AGENTS.md § STDLIB-FIRST DOCTRINE — pydantic named departure

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean (no doc surface here; docs at OBPI-03/04)

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: schema-only; behavior coverage in OBPI-02/03

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/advisor/test_diagnosis.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.29-01-01: Given a valid input dict, when `AdvisorDiagnosis(**data)` runs, then a frozen instance is returned.
- [ ] REQ-0.0.29-01-02: Given `proof=()`, when `AdvisorDiagnosis` is instantiated, then `ValidationError` is raised.
- [ ] REQ-0.0.29-01-03: Given `archetype` outside the ten-value enum, when instantiated, then `ValidationError`.
- [ ] REQ-0.0.29-01-04: Given `authority` outside the four-value enum, when `DoctrinalFrame` is instantiated, then `ValidationError`.
- [ ] REQ-0.0.29-01-05: Given a frozen instance, when mutation is attempted, then `ValidationError`.
- [ ] REQ-0.0.29-01-06: Given a serialized `AdvisorDiagnosis` dict, when validated against the JSON Schema, then validation passes; given a dict with empty proof or unknown enum, validation fails.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean
- [ ] Gate 3: docs clean
- [ ] Gate 4: BDD waiver registered
- [ ] Gate 5: TTY + `ATTEST`

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

### Gate 3 (Docs)
```text
# n/a — schema-only OBPI
```

### Gate 4 (BDD)
```text
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.29-01
```

### Gate 5 (Human)
```text
# Record attestation text + receipt IDs
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
