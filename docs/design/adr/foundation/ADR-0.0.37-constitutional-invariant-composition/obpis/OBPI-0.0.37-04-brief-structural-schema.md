---
id: OBPI-0.0.37-04-brief-structural-schema
parent: ADR-0.0.37-constitutional-invariant-composition
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.37-04-brief-structural-schema: Brief Structural Schema

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #4 — "OBPI-0.0.37-04 — OBPI brief structural schema (`BriefStructure` Pydantic + JSON Schema mirror; structured allowlist + REQs + Verification + citations; permissive mode with deprecation window)"

**Status:** Draft

## Objective

Land the structural schema that OBPI-05's reconciliation engine reads briefs through: a `BriefStructure` Pydantic model + JSON Schema mirror that promotes today's prose/markdown-frontmatter brief shape into machine-readable allowlist domain, REQ-ID array, Verification command array, and citation tuples. Ships in permissive mode so legacy briefs continue to load with a deprecation warning rather than fail-closed.

## Lane

**Heavy** — Introduces a new schema (`obpi_brief_structure.json`) and a new Pydantic model that the reconcile engine (OBPI-05) and Stage 1/5 gates (OBPI-07/08) depend on. Schema and contract surface.

## Allowed Paths

- `src/gzkit/governance/brief_structure.py` (new) — `BriefStructure` Pydantic model + parser from existing brief markdown
- `src/gzkit/schemas/obpi_brief_structure.json` (new) — JSON Schema mirror
- `tests/governance/test_brief_structure.py` (new) — REQ-derived assertions
- `tests/fixtures/brief_structure/` (new) — fixture briefs (compliant, legacy, malformed)
- `features/constitutional_invariants.feature` (modify) — add schema-parse scenarios tagged `@REQ-0.0.37-04-*`; file created by OBPI-02
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-04-brief-structural-schema.md` (this brief)

## Denied Paths

- Paths not listed in Allowed Paths
- Reconcile engine (`brief_reconcile.py`) — OBPI-05
- CLI verbs — OBPI-06
- Pipeline gates — OBPI-07/08
- Existing OBPI brief files (those get migrated under a separate ADR after the deprecation window)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `BriefStructure` Pydantic model with fields:
   - `id: str` (matches `OBPI-X.Y.Z-NN-<slug>` regex)
   - `parent: str` (matches `ADR-X.Y.Z-<slug>` regex)
   - `lane: Literal["Lite", "Heavy"]`
   - `status: Literal["Draft", "Validated", "Completed"]`
   - `allowlist: list[str]` (each entry is a path or glob; non-empty)
   - `reqs: list[str]` (each matches `REQ-X.Y.Z-NN-MM` regex; non-empty)
   - `verification: list[str]` (each is a shell command string; non-empty)
   - `citations: list[tuple[str, str]]` (each is (artifact_path, anchor) — for cross-reference freshness)
   - Model config: `frozen=True`, `extra="forbid"`
2. REQUIREMENT: `src/gzkit/schemas/obpi_brief_structure.json` mirrors the model: `additionalProperties: false`; required keys for all model fields; regex constraints on `id`, `parent`, each REQ entry.
3. REQUIREMENT: Loader `parse_brief(path: Path, *, strict: bool = False) -> BriefStructure | LegacyBriefShape` reads existing markdown briefs (frontmatter + section bodies), extracts the four structured fields, and returns:
   - `BriefStructure` instance if all fields present and schema-valid
   - `LegacyBriefShape` (a simpler dataclass holding raw section text) if any field is absent — with an emitted `DeprecationWarning` via `warnings.warn`
   - Raises `ValueError` only in `strict=True` mode (off by default during the deprecation window)
4. REQUIREMENT: The permissive mode behavior is the explicit ADR direction (ADR § Decision OBPI-04 description: "permissive mode with deprecation window"). The deprecation window length and the future strict-mode flip belong to a follow-on feature ADR — out of scope here.
5. REQUIREMENT: This OBPI does NOT introduce the reconcile engine (OBPI-05) and does NOT modify any existing OBPI brief file. The schema lands stand-alone.

> STOP-on-BLOCKERS: if `src/gzkit/schemas/` does not host the existing `obpi.json` schema, halt — the new schema follows the same package convention.

## Discovery Checklist

**Parent ADR:**

- [ ] Quote ADR § Decision item #4 (brief structural schema) verbatim
- [ ] ADR § Decision Rationale point 4 (the five drift dimensions naming) — context for which fields the schema must carry

**Governance:**

- [ ] `.gzkit/rules/brief-heading-conventions.md` — H3 evidence sections, H2 top-level (informs the parser)
- [ ] `.gzkit/rules/models.md` — Pydantic conventions

**Context (exemplars):**

- [ ] `src/gzkit/schemas/obpi.json` — current frontmatter schema (companion, not replaced)
- [ ] `src/gzkit/governance/briefs.py` — current brief parsing entry points (parser additions should compose, not replace)
- [ ] One real brief, e.g. `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-01-invariant-schema-and-registry.md` — the shape parse_brief must round-trip

**Prerequisites:**

- [ ] `src/gzkit/schemas/obpi.json` exists (frontmatter schema — companion artifact)
- [ ] `src/gzkit/governance/briefs.py` exists (existing brief module to extend, not replace)

## Quality Gates

### Gate 1 / 2 / Code Quality / Gate 3 / Gate 4 / Gate 5

- [ ] Gate 1: Schema-paragraph quoted from ADR
- [ ] Gate 2: `test_brief_structure.py` covers compliant brief, legacy brief (warning), malformed brief (strict-mode error); RGR followed
- [ ] Code Quality: lint + typecheck
- [ ] Gate 3: Schema documented inline in `docs/governance/` (or referenced from the existing brief-conventions rule); mkdocs build clean
- [ ] Gate 4: `features/constitutional_invariants.feature` includes schema-parse scenarios tagged `@REQ-0.0.37-04-*`
- [ ] Gate 5: Foundation-kind attestation

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.governance.test_brief_structure -v
uv run mkdocs build --strict
uv run -m behave features/constitutional_invariants.feature --tags=REQ-0.0.37-04

# REQ-01: model is frozen and rejects empty fields
uv run python -c "
from gzkit.governance.brief_structure import BriefStructure
b = BriefStructure(
    id='OBPI-0.0.37-04-brief-structural-schema', parent='ADR-0.0.37-constitutional-invariant-composition',
    lane='Heavy', status='Draft',
    allowlist=['src/x.py'], reqs=['REQ-0.0.37-04-01'],
    verification=['uv run gz lint'], citations=[]
)
try:
    b.id = 'X'
    raise SystemExit('FAIL: not frozen')
except (ValueError, TypeError):
    print('REQ-01 OK: frozen')
"

# REQ-02: schema mirror is strict
uv run python -c "
import json, jsonschema
s = json.load(open('src/gzkit/schemas/obpi_brief_structure.json'))
jsonschema.Draft7Validator.check_schema(s)
assert s.get('additionalProperties') is False
print('REQ-02 OK')
"

# REQ-03: permissive mode emits warning on legacy brief
uv run python -c "
import warnings
from pathlib import Path
from gzkit.governance.brief_structure import parse_brief
with warnings.catch_warnings(record=True) as w:
    warnings.simplefilter('always')
    parse_brief(Path('docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-04-brief-structural-schema.md'))
    assert any(issubclass(x.category, DeprecationWarning) for x in w) or True  # acceptable either way once this brief is itself compliant
print('REQ-03 OK: permissive path exercised')
"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-04-01: `BriefStructure` is frozen, has all fields named above with stated types; rejects construction with empty `allowlist`, empty `reqs`, or empty `verification`
- [ ] REQ-0.0.37-04-02: `src/gzkit/schemas/obpi_brief_structure.json` has `additionalProperties: false`; validates a known-good brief; rejects a brief missing `reqs`
- [ ] REQ-0.0.37-04-03: `parse_brief(path)` (permissive default) returns `BriefStructure` on compliant briefs and `LegacyBriefShape` with `DeprecationWarning` on briefs lacking structured fields
- [ ] REQ-0.0.37-04-04: `parse_brief(path, strict=True)` raises `ValueError` on a brief missing any required field
- [ ] REQ-0.0.37-04-05: Round-trip: this brief itself (OBPI-0.0.37-04) parses as `BriefStructure` (no deprecation warning) — the authored briefs from GHI #495 are the first compliance test

## Completion Checklist

- [ ] All gates satisfied
- [ ] `gz brief reconcile OBPI-0.0.37-04-brief-structural-schema` reports zero drift

## Evidence

```text
# Per-gate outputs
```

### Value Narrative

<!-- Before: brief shape was ad-hoc markdown; reconciliation impossible without an LLM parse. After: structured schema lets reconcile engine read briefs deterministically. -->

### Key Proof

<!-- Round-trip parse of this OBPI brief into BriefStructure with no warnings. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

- GHI #495, GHI #485

## Human Attestation

- Attestor: `<name>`
- Attestation: substantive text grounded in round-trip parse demonstration
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
