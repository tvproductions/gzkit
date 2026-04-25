---
id: OBPI-0.0.30-03-authoring-hint-engine
parent: ADR-0.0.30
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.30-03-authoring-hint-engine: Authoring-time Hint Engine + AuthoringHint Projection

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/ADR-0.0.30-complexity-authoring-guidance.md`
- **Checklist Item:** #3 — "Authoring-time hint engine + AuthoringHint projection from AdvisorDiagnosis (consumes ADR-0.0.29-02 engine; src/gzkit/complexity/authoring/{hint.py, engine.py})"

**Status:** Draft

## Objective

Implement the frozen `AuthoringHint` Pydantic model + projection from `AdvisorDiagnosis` at `src/gzkit/complexity/authoring/hint.py`, plus the authoring-time hint engine at `src/gzkit/complexity/authoring/engine.py` that consumes ADR-0.0.29-02's diagnosis engine and emits `AuthoringHint` for `advise`-band crossings only. Projection direction is fixed (`AdvisorDiagnosis` → `AuthoringHint`); the reverse direction is not allowed.

## Lane

**Heavy** — New runtime data contract + projection function consumed by OBPI-01 CLI, OBPI-04 protocol, OBPI-05 justify integration. Foundation-kind brief-level Gate 5 attestation.

## Allowed Paths

- `src/gzkit/complexity/authoring/__init__.py`
- `src/gzkit/complexity/authoring/hint.py` — `AuthoringHint` model + `project_diagnosis_to_hint` function
- `src/gzkit/complexity/authoring/engine.py` — authoring-time hint engine wrapping ADR-0.0.29-02
- `src/gzkit/schemas/authoring_hint.json` — JSON Schema mirror
- `tests/complexity/authoring/test_hint.py`, `tests/complexity/authoring/test_engine.py`
- `docs/design/adr/foundation/ADR-0.0.30-complexity-authoring-guidance/obpis/OBPI-0.0.30-03-authoring-hint-engine.md` — this brief's evidence section only

## Denied Paths

- `src/gzkit/complexity/advisor/diagnosis.py` — schema is ADR-0.0.29-01 (consumed, not edited)
- `src/gzkit/complexity/advisor/engine.py` — engine is ADR-0.0.29-02 (consumed, not edited)
- `src/gzkit/complexity/thresholds.py` — ThresholdTable is ADR-0.0.28-02 (consumed via the advisor engine)
- `src/gzkit/commands/complexity_guide.py` — CLI is OBPI-01
- `src/gzkit/complexity/authoring/protocol.py` — protocol is OBPI-04
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `AuthoringHint` is a frozen Pydantic `BaseModel` with `ConfigDict(frozen=True, extra="forbid")`. Fields: `metric: str`, `precedence_band: Literal["approaching", "approaching_warn"]`, `crossing_value: float`, `archetype: RefactorArchetype` (imported from ADR-0.0.29-01), `doctrinal_frame_headline: str` (truncated 1-line excerpt of the full doctrinal frame), `recommended_move: str`, `file_path: str`, `start_line: int`, `end_line: int`.
2. REQUIREMENT: `project_diagnosis_to_hint(diagnosis: AdvisorDiagnosis) -> AuthoringHint | None` is the projection function. It returns a hint ONLY when `diagnosis.crossing_band == "advise"`; for `warn` or `block` it returns `None` (those crossings are the trigger-time advisor's responsibility, not the authoring-guidance surface). The projection is one-direction; there is NO reverse projection function.
3. REQUIREMENT: The projection drops `proof: tuple[ProofRange, ...]` (the developer has the file open; proof is implicit), drops `intrinsic_attestation` (authoring-time hints precede attestation), and truncates `doctrinal_frame.excerpt` to a one-line headline. The first `ProofRange`'s `file_path`, `start_line`, `end_line` are promoted to top-level fields on the `AuthoringHint` (the engine guarantees the developer's editor can place the hint at the correct location).
4. REQUIREMENT: The authoring engine `analyze(path: Path) -> tuple[AuthoringHint, ...]` invokes the ADR-0.0.29-02 advisor engine for each metric crossing in the threshold table, applies the projection, filters to non-`None` results, and returns the hint tuple. Empty input (no advise crossings) returns `()`.
5. REQUIREMENT: A `precedence_band` of `approaching_warn` indicates the metric is in the upper portion of the advise band (close to crossing into warn); `approaching` is the lower portion. The boundary is the median between advise's lower and upper edges per the threshold table; the engine computes the boundary from the table, not from a hardcoded value.
6. REQUIREMENT: The JSON Schema at `src/gzkit/schemas/authoring_hint.json` is `extra="forbid"`-equivalent and validates: `precedence_band` is one of two enum values; `archetype` is in the ten-value enum; `start_line ≤ end_line`; line numbers are positive integers.
7. REQUIREMENT: Tests cover: model instantiation with valid input; rejection of `precedence_band` outside enum; rejection of `archetype` outside enum; projection returns `None` for warn/block crossings; projection returns `AuthoringHint` for advise crossings; projection drops `proof` and `intrinsic_attestation`; projection promotes first ProofRange location to top-level fields; engine `analyze` returns empty tuple on clean file; engine `analyze` returns hints for advise-band crossings; `precedence_band` correctly classifies upper-vs-lower portion; mutation attempts on `AuthoringHint` raise. Each test decorated with `@covers(REQ-0.0.30-03-NN)`.
8. REQUIREMENT: Function-size discipline per `.claude/rules/pythonic.md` — projection ≤ 50 lines; engine decomposes into named helpers (advisor invocation, projection filtering, precedence classification).
9. REQUIREMENT: TDD discipline; `tempfile`-backed fixtures.
10. REQUIREMENT: NEVER include the operator's personal email in code, fixtures, or docstrings.

> STOP-on-BLOCKERS: if ADR-0.0.29-01 schema and ADR-0.0.29-02 engine are not landed, STOP — both are consumed.

## Discovery Checklist

- [ ] ADR-0.0.29-01 schema (`AdvisorDiagnosis`, `RefactorArchetype`, `DoctrinalFrame`, `ProofRange`)
- [ ] ADR-0.0.29-02 engine (`engine.diagnose` interface)
- [ ] ADR-0.0.28-02 `ThresholdTable` model (consumed transitively via the advisor engine)
- [ ] `.claude/rules/models.md`, `.claude/rules/pythonic.md`
- [ ] Parent ADR § Decision rationale #1 — projection direction is fixed (full → light)

## Quality Gates

### Gate 1: ADR
- [ ] Intent recorded; parent checklist item quoted

### Gate 2: TDD
- [ ] RGR cycle; tests pass with `@covers`

### Code Quality
- [ ] Lint/type clean; size limits

### Gate 3: Docs (Heavy)
- [ ] mkdocs --strict clean

### Gate 4: BDD (Heavy)
- [ ] BDD waiver registered: engine-internal OBPI; user-facing scenarios at OBPI-01 CLI

### Gate 5: Human (Heavy + Foundation)
- [ ] TTY + `ATTEST`

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --documents
uv run gz arb step --name unittest -- uv run -m unittest tests/complexity/authoring/test_hint.py tests/complexity/authoring/test_engine.py -v
```

## Acceptance Criteria

- [ ] REQ-0.0.30-03-01: Given a valid input dict, when `AuthoringHint(**data)` runs, then a frozen instance is returned.
- [ ] REQ-0.0.30-03-02: Given an `AdvisorDiagnosis` with `crossing_band="advise"`, when projected, then a non-None `AuthoringHint` is returned.
- [ ] REQ-0.0.30-03-03: Given an `AdvisorDiagnosis` with `crossing_band="warn"` or `"block"`, when projected, then `None` is returned.
- [ ] REQ-0.0.30-03-04: Given a projection, when inspected, then it has no `proof` or `intrinsic_attestation` field; the first `ProofRange`'s `file_path`/`start_line`/`end_line` are top-level fields.
- [ ] REQ-0.0.30-03-05: Given a clean file, when `engine.analyze(path)` runs, then `()` is returned.
- [ ] REQ-0.0.30-03-06: Given a file with advise-band crossings, when `engine.analyze` runs, then the returned tuple contains one hint per advise-band crossing.
- [ ] REQ-0.0.30-03-07: Given a metric value at the upper portion of the advise band, when classified, then `precedence_band="approaching_warn"`; lower portion → `"approaching"`.
- [ ] REQ-0.0.30-03-08: Given a frozen `AuthoringHint` instance, when mutation is attempted, then `ValidationError` is raised.

## Completion Checklist

- [ ] Gate 1: Intent recorded
- [ ] Gate 2: RGR cycle; tests pass with `@covers`
- [ ] Code Quality: lint/type clean; size limits
- [ ] Gate 3: docs clean
- [ ] Gate 4: BDD waiver registered
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
# Paste mkdocs --strict output
```

### Gate 4 (BDD)
```text
# Waiver: data/behave_coverage_waivers.json — OBPI-0.0.30-03
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
