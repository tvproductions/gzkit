# Plan: OBPI-0.30.0-01 — OKF concept-frontmatter Pydantic model + JSON schema

**OBPI:** OBPI-0.30.0-01-okf-concept-frontmatter-model
**Parent ADR:** ADR-0.30.0-okf-documentation-knowledge-structure
**Lane:** Heavy

## Context

This is the foundation OBPI of ADR-0.30.0. It delivers the typed contract every
downstream OBPI consumes: a Pydantic model for OKF concept-document frontmatter
plus a JSON schema mirror. The load-bearing constraint is the **OKF posture**
(parent ADR Boundary Invariant 3): unknown frontmatter fields and unknown `type`
values are NOT errors. Only `type` is required.

### Destination-in-mind (Step 6a disclosure)

Before writing this plan I had already concluded the approach: a new
`src/gzkit/knowledge/` package housing a `ConceptFrontmatter(BaseModel)` with
`extra="allow"` and `type: str` (free string, no enum), mirrored by a
hand-authored JSON schema with `additionalProperties: true` and
`required: ["type"]`. This conclusion came from reading the brief REQs + the
existing `AuthoringHint` model/schema pair as the established shape.

### Rejected alternatives

1. **`extra="forbid"` (the repo default in `models.md`).** Rejected — it
   directly contradicts Boundary Invariant 3. The default policy yields to an
   explicit ADR decision; the departure is documented inline so it is not
   "fixed" back.
2. **`type` as a `Literal[...]`/enum of known doc types.** Rejected — a closed
   enum revives the 0.0.74 doc-type taxonomy Movement I cut and violates posture
   tolerance. `type` must be a free non-empty string.
3. **Auto-generating the JSON schema from `model_json_schema()` at import.**
   Rejected — every existing schema under `src/gzkit/schemas/` is a hand-authored
   committed file; matching that convention keeps the parity-test pattern intact.
4. **Registering the schema in `tests/test_schemas.py::_ALL_SCHEMAS`.** Rejected
   as out-of-scope coupling — REQ-04 is SUPPORT (proven by `validate --documents`
   + ledger), so a self-contained load test in the new module suffices.

## Files

- `src/gzkit/knowledge/__init__.py` — **CREATE** package; export `ConceptFrontmatter`.
- `src/gzkit/knowledge/concept_frontmatter.py` — **CREATE** the Pydantic model.
- `src/gzkit/schemas/okf_concept_frontmatter.json` — **CREATE** JSON schema mirror.
- `tests/knowledge/__init__.py` — **CREATE** test package marker.
- `tests/knowledge/test_concept_frontmatter_model.py` — **CREATE** REQ-derived tests.

All within the brief's Allowed Paths (`src/gzkit/knowledge/`, `src/gzkit/schemas/`,
`tests/`, the ADR + this brief). No denied paths touched (no validator, no CLI,
no new runtime deps).

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **REQ-01 (BEHAVIOR)** — `type`-only document validates and exposes `type`.
   Red: test `ConceptFrontmatter(type="doctrine").type == "doctrine"` against an
   empty stub. Green: define model with required `type: str = Field(..., min_length=1)`.
2. **REQ-02 (BEHAVIOR, part a)** — missing/empty `type` fails validation.
   Red: assert `ValidationError` on `ConceptFrontmatter()` and on `type=""`.
   Green: `min_length=1` + required already enforces; confirm.
3. **REQ-02 (BEHAVIOR, part b)** — all optional fields accepted; type-only valid.
   Red: construct with `title/description/resource/tags/timestamp`. Green: add
   optional fields (`str | None = Field(None, ...)`, `tags: list[str] | None`).
4. **REQ-03 (BEHAVIOR)** — posture tolerance: unknown field + unknown `type`
   value both accepted. Red: `ConceptFrontmatter(type="totally-novel", novel_key="x")`.
   Green: `model_config = ConfigDict(extra="allow")`; `type` stays free `str`.
5. **REQ-04 (SUPPORT)** — schema mirror exists + loads clean. Author
   `okf_concept_frontmatter.json` (required `type` minLength 1; optional fields;
   `additionalProperties: true`). Test: `load_schema("okf_concept_frontmatter")`
   returns a dict with `required == ["type"]` and `additionalProperties is True`.
6. **Refactor** — docstrings cite the OKF posture + the `extra="allow"` departure
   from `models.md`; align model field set with schema property set.

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run -m unittest tests.knowledge.test_concept_frontmatter_model -v
```

Plus the brief Demo: type-only construct succeeds; missing-type raises.

## Notes

- `extra="allow"` is a **named departure** from `.gzkit/rules/models.md`
  (`extra="forbid"` default), mandated by ADR-0.30.0 Boundary Invariant 3. Inline
  comment records this so it is not reverted.
- Model is frozen (`frozen=True`) for snapshot immutability, consistent with the
  immutable-domain-model convention; frozen + `extra="allow"` is supported in
  Pydantic v2.
- STRUCTURAL-FENCE (Boundary Invariant 1): this model is a data contract only; it
  is NOT imported by any `gz validate`/gates/closeout surface. Enforced by staying
  within Allowed Paths (no validator/closeout edits).
