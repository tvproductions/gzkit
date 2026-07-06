# Plan — OBPI-0.32.0-01-ontology-model-and-purity

**OBPI:** OBPI-0.32.0-01-ontology-model-and-purity
**Parent ADR:** ADR-0.32.0-gzkit-ontology (Movement III Phase 2, HULL — "the gzkit ontology")
**Lane:** Heavy · **Kind:** feature · **Sensitivity:** absent (no allowlist ↔ `data/security_surfaces.json` overlap — verified)

## Context

This is the keel-up model layer for the gzkit ontology. It ships ONLY the pure
additive object/link Pydantic model + the Harness-Purity validator — no networkx
substrate, no domain projection, no operator verbs (those are OBPI-02..07). The
parent ADR § Decision clause this OBPI implements verbatim:

> "A two-axis type model classifies every object: ownership (harness|product; a
> Harness-Purity Invariant admits only GovZero-universal types into
> ownership:harness, enforced by a validator landing in the same increment) x
> plane (product|process; the semantics are seated in ontology.schema.json's
> dormant plane field for continuity-of-naming and validated to genuinely
> partition our objects, not merely asserted)."

STRUCTURAL-FENCE anchor: parent ADR `## Boundary Invariants` #4 (Harness purity).

## Files (from brief allowlist — no path outside this set)

**CREATE (net-new, existence-gate exempt):**
- `src/gzkit/ontology/__init__.py` — package marker, docstring only
- `src/gzkit/ontology/model.py` — `Ownership`/`Plane`/`LinkType`/`ObjectType` closed `StrEnum`s; frozen `extra="forbid"` `OntologyNode`/`OntologyEdge`; total `OBJECT_TYPE_REGISTRY`; `ontology_node_json_schema()` projector
- `src/gzkit/ontology/purity.py` — `audit_ontology_purity(project_root) -> list[ValidationError]` + pure `harness_purity_violations(...)` helper
- `src/gzkit/schemas/ontology_node.json` — committed projection of `OntologyNode` (loads via `load_schema("ontology_node")`)
- `tests/test_ontology_model.py` — `@covers` REQ-01/02/04 tests
- `tests/test_ontology_purity.py` — `@covers` REQ-03 refusal test

**MODIFY (surgical, additive only):**
- `src/gzkit/commands/validate_cmd.py` — register `ontology_purity` scope: `_ScopeEntry` in `VALIDATOR_REGISTRY`, `checks` map key, `check_ontology_purity` param, `_POLICY_BREACH_ERROR_TYPES` membership, `_ontology_purity_runner` lazy-import runner
- `src/gzkit/cli/parser_maintenance.py` — additive `--ontology-purity` flag (`dest="check_ontology_purity"`) + thread `check_ontology_purity=a.check_ontology_purity` into the `validate()` call (mirrors `--req-kind-discipline`)
- `docs/user/manpages/validate.md` — document the new `--ontology-purity` flag (Gate 3)

## Design decisions (grounded)

- **Enums (closed `enum.StrEnum`, req_kind.py precedent):**
  - `Ownership = {HARNESS="harness", PRODUCT="product"}`
  - `Plane = {PRODUCT="product", PROCESS="process"}` — members VERBATIM from `.gzkit/governance/ontology.schema.json $defs.plane` (REQ-02 continuity-of-naming)
  - `LinkType` — closed taxonomy the corpus/work/source subgraphs will consume: `PARENT, CHILD, LINKS_TO, COVERS, SURFACE, BLOCKS, BLOCKED_BY, DISCOVERED_FROM, VALIDATES, SUPERSEDES` (model layer seats the enum; later OBPIs consume it)
  - `ObjectType` — closed set of seated types: corpus/GovZero-universal `{ADR, OBPI, REQ, GHI, RECEIPT, DOC, TASK}` + gzkit product `{CLI_VERB, VALIDATOR, SKILL, CHORE}`
- **Models (`.claude/rules/models.md`):** `OntologyNode(node_id, object_type, ownership, plane)` and `OntologyEdge(source_id, target_id, link_type)`, both `ConfigDict(frozen=True, extra="forbid")`, required `Field(...)`.
- **`OBJECT_TYPE_REGISTRY: dict[ObjectType, tuple[Ownership, Plane]]`** — TOTAL over `ObjectType`. Plane rule = "constrains code"→product, "constrains governance"→process: corpus types → `(HARNESS, PROCESS)`; `CLI_VERB`/`VALIDATOR` → `(PRODUCT, PRODUCT)`; `SKILL`/`CHORE` → `(PRODUCT, PROCESS)`. Both planes non-empty; no product type is `ownership:harness`.
- **Purity fence:** `_PRODUCT_OBJECT_TYPES = {CLI_VERB, VALIDATOR, SKILL, CHORE}`. Pure `harness_purity_violations(classification)` flags any `(object_type ∈ _PRODUCT_OBJECT_TYPES) and (ownership == HARNESS)`. `audit_ontology_purity(project_root)` applies it to `OBJECT_TYPE_REGISTRY` → returns `ValidationError(type="ontology_purity", ...)` list (empty in production; non-empty on a bad node the refusal test constructs). Exit 3 via `_POLICY_BREACH_ERROR_TYPES`.
- **Schema projection:** `ontology_node_json_schema()` returns `OntologyNode.model_json_schema()`; committed `ontology_node.json` == that projection (coherence test asserts `load_schema("ontology_node") == ontology_node_json_schema()`), mirroring `obpi_state_machine`.

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **Skeleton first (avoid the false import-red):** create `ontology/__init__.py` + `ontology/model.py` with stub enums/models/registry (no-op bodies) and `purity.py` stub so tests import cleanly and fail at their OWN assertion.
2. **REQ-01-01** (RGR): frozen + `extra="forbid"` on both models (unknown field → `ValidationError`; post-construct mutation → `ValidationError`); `LinkType` closed `StrEnum`. Watch assertion-red → implement.
3. **REQ-01-02** (RGR): `OntologyNode` requires `ownership`+`plane`; out-of-enum → `ValidationError`; `Plane` member-set == live `.gzkit/governance/ontology.schema.json $defs.plane` enum (load file, assert set-equality).
4. **REQ-01-04** (RGR): `OBJECT_TYPE_REGISTRY` TOTAL over `ObjectType` (adding a member without an entry FAILS); each type exactly one plane; both planes non-empty; Harness-Purity obeyed.
5. **REQ-01-03** (RGR): `tests/test_ontology_purity.py` — a `CLI_VERB` node tagged `ownership:harness` → `audit`/helper returns non-empty (refusal); a harness-legal universal object (e.g. `ADR` at `ownership:harness`) passes clean.
6. **REQ-01-05** (SUPPORT): write `ontology_node.json` = `ontology_node_json_schema()`; coherence test; `gz validate --documents` green.
7. **Validator wiring:** `_ontology_purity_runner` + `_ScopeEntry("ontology_purity", "explicit", True, ...)` + `checks["ontology_purity"]` + `check_ontology_purity: bool = False` param + `"ontology_purity"` in `_POLICY_BREACH_ERROR_TYPES`; parser `--ontology-purity` flag + call-site thread.
8. **Docs:** `docs/user/manpages/validate.md` — add `--ontology-purity` row/example. Run `gz cli audit`.
9. **Refactor green:** dedupe, names, size limits (<=50 line fns).

> REQ-01-06 [STRUCTURAL-FENCE] needs no code — anchored at parent ADR `## Boundary Invariants` #4, audited at ADR closeout.

## Verification (from brief)

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run gz validate --ontology-purity
uv run -m unittest tests.test_ontology_model -v
uv run -m unittest tests.test_ontology_purity -v
```

## Step 6a disclosure (plan-before-exploration)

- **Destination-in-mind:** Before authoring I had formed the approach above — mirror the `req_kind.py` StrEnum + frozen-model + committed-schema pattern and the `req_kind_discipline` validator-wiring shape, because the brief's Discovery Checklist explicitly pins those as the precedents. This is convergent with the brief, not a reconstruction imposed on it.
- **Rejected alternatives considered during exploration:**
  1. *Validator reads the live registry only (no pure helper).* Rejected: it can never be `ownership:harness` in production, so the refusal test would have nothing to bite — a tautological green. The pure-helper split is what makes REQ-03 a real behavior test.
  2. *Fold `plane`/`ownership` into a single combined enum.* Rejected: the ADR § Decision and the partition test (REQ-04) require two independent axes with an explicit TOTAL cross-product registry; a combined enum cannot express "both planes non-empty" as a partition assertion.
  3. *Seat `LinkType` with only the corpus lineage members needed "now".* Rejected as under-building the closed taxonomy the ADR Decision names for all three subgraphs; the enum IS this layer's deliverable and later OBPIs consume it — a minimal-now enum would force a churn edit in OBPI-02.

## Notes

- Denied paths respected: no `graph.py`/networkx, no `ledger.py` edit, no `state.py`/operator verbs, no `triangle.py`/tree-sitter, no new runtime dependency. Only CLI change is the additive `--ontology-purity` scope flag.
- `src/gzkit/schemas/__init__.py` is an UNTOUCHED NEIGHBOR — `load_schema` is name-generic.
