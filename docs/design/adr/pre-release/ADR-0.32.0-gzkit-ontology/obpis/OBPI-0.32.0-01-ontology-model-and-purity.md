---
id: OBPI-0.32.0-01-ontology-model-and-purity
parent: ADR-0.32.0-gzkit-ontology
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.32.0-01-ontology-model-and-purity: Ontology Model And Purity

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- **Checklist Item:** #1 - "Pydantic ontology model (OntologyNode/OntologyEdge + typed LinkType) + two-axis ownership/plane classification + Harness-Purity validator (with a refusal test: a product object pushed into ownership:harness is rejected); plane semantics validated to partition our objects; JSON schema under src/gzkit/schemas/."

**Status:** Draft

## Objective

Lay the gzkit-ontology object/link model layer as pure additive domain code — frozen `OntologyNode`/`OntologyEdge` Pydantic models, a closed `LinkType` StrEnum, and the two-axis `ownership` (harness|product) × `plane` (product|process) classification — committed as a JSON-schema projection under `src/gzkit/schemas/` and fenced by a `gz validate --ontology-purity` Harness-Purity validator that refuses a product object placed in `ownership:harness`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds a new schema contract (`src/gzkit/schemas/ontology_node.json`),
a new importable runtime model surface (`gzkit.ontology.model`), and a new
additive `gz validate --ontology-purity` CLI scope that later OBPIs in this ADR
and the parent ADR's Fidelity Assertions bind against.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new
     files (existence-gate exempt, GHI #419). -->

- `src/gzkit/ontology/__init__.py` — **CREATE**: new `gzkit.ontology` package marker (docstring only)
- `src/gzkit/ontology/model.py` — **CREATE**: `OntologyNode`/`OntologyEdge` frozen `extra="forbid"` Pydantic models, `LinkType`/`Ownership`/`Plane`/`ObjectType` closed `StrEnum`s, a total `OBJECT_TYPE_REGISTRY: dict[ObjectType, tuple[Ownership, Plane]]` classifying every seated object type, and `ontology_node_json_schema()` projector
- `src/gzkit/ontology/purity.py` — **CREATE**: `audit_ontology_purity(project_root) -> list[ValidationError]` Harness-Purity validator (refuses a product-typed object placed in `ownership:harness`)
- `src/gzkit/schemas/ontology_node.json` — **CREATE**: committed JSON-schema projection of the `OntologyNode` model, loaded name-generically via `gzkit.schemas.load_schema`
- `tests/test_ontology_model.py` — **CREATE**: `@covers`-decorated REQ tests for the model layer (frozen/extra-forbid, two-axis, plane-verbatim, partition)
- `tests/test_ontology_purity.py` — **CREATE**: `@covers` refusal test for the Harness-Purity validator
- `src/gzkit/commands/validate_cmd.py` — register the `ontology_purity` scope ONLY: one `VALIDATOR_REGISTRY` entry (explicit tier), the `checks` map key, the `check_ontology_purity` param, and the `_POLICY_BREACH_ERROR_TYPES` membership so it exits 3 on refusal
- `src/gzkit/cli/parser_maintenance.py` — add the additive `--ontology-purity` argparse flag on `gz validate` and wire `check_ontology_purity=a.check_ontology_purity` (mirrors `--req-kind-discipline`)
- `docs/user/manpages/validate.md` — document the new `--ontology-purity` flag (Gate 3 docs coherence)
- `src/gzkit/schemas/__init__.py` — **UNTOUCHED NEIGHBOR** (`load_schema()` is name-generic; no per-schema registration needed)
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md` — parent ADR `## Boundary Invariants` #4 is the STRUCTURAL-FENCE anchor (read-only reference, no edit)
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-01-ontology-model-and-purity.md` — this brief (evidence)

## Denied Paths

<!-- Item 2 (graph substrate), item 3 (operator verbs), and item 5/6/7
     (domain projections) are sibling OBPIs in this same ADR — out of scope here. -->

- `src/gzkit/ontology/graph.py`, any networkx `MultiDiGraph` substrate module — the graph engine + corpus projection is OBPI-02, not this OBPI
- `src/gzkit/ledger.py` — `get_artifact_graph` absorption into a typed corpus view is OBPI-02; not touched here
- `src/gzkit/commands/state.py`, any new `ontology`-verb command module — the gz ontology operator surface (sense/trace/resense/seams/reach) is item #3; this OBPI ships no operator noun namespace
- `src/gzkit/triangle.py`, any source-domain / tree-sitter code — the source subgraph absorbing `detect_drift` is item #7
- New runtime dependencies (networkx, tree-sitter), CI files, lockfiles — the STDLIB-FIRST departure for the graph substrate is discharged by OBPI-02/07, not here
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. NEVER/ALWAYS language. -->

1. REQUIREMENT: Deliver ONLY the object/link model layer + Harness-Purity validator: `OntologyNode`/`OntologyEdge` (frozen, `extra="forbid"`), a closed `LinkType` StrEnum, the `ownership` (harness|product) and `plane` (product|process) axes, the committed `src/gzkit/schemas/ontology_node.json`, and the additive `gz validate --ontology-purity` scope.
2. NEVER: introduce the networkx `MultiDiGraph` substrate, absorb `ledger.get_artifact_graph`, or build any domain projection (corpus/work/source) — those are OBPI-02 and later in this ADR.
3. NEVER: add or edit the gz ontology operator verbs (sense/trace/resense/seams/reach) or the `src/gzkit/commands/state.py` render — the operator noun namespace is item #3; the only CLI change here is the additive `gz validate --ontology-purity` scope flag.
4. NEVER: add a new runtime dependency (networkx, tree-sitter); the models are pure Pydantic + stdlib `enum.StrEnum`.
5. ALWAYS: reproduce the `plane` members (`product`/`process`) verbatim from the dormant `.gzkit/governance/ontology.schema.json` `plane` `$defs` enum; naming or member drift from that canonical field is a fail-closed defect (parent ADR § Decision — continuity-of-naming).
6. ALWAYS: keep `OntologyNode`/`OntologyEdge` frozen with `extra="forbid"` per `.claude/rules/models.md`, and keep the committed `src/gzkit/schemas/ontology_node.json` the projection of the model (loadable via `load_schema`).
7. ALWAYS: reconcile this brief against parent ADR § Decision and § Boundary Invariants #4 before implementation; quote the Decision line into `### Implementation Summary`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the two-axis + Harness-Purity clause** verbatim into `### Implementation Summary`. The clause ("ownership (harness|product; a Harness-Purity Invariant admits only GovZero-universal types into ownership:harness … ) x plane (product|process; … seated in ontology.schema.json's dormant plane field … validated to genuinely partition our objects, not merely asserted)") IS this OBPI's contract.
- [ ] Parent ADR § Intent — the "working in the dark" / silent-reversal why-frame for the typed object plane.
- [ ] Parent ADR § Boundary Invariants #4 (Harness purity) — the STRUCTURAL-FENCE anchor for REQ-06.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`

> **STOP:** If you cannot quote the parent ADR § Decision clause that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.claude/rules/models.md` — Pydantic `ConfigDict(frozen=True, extra="forbid")` policy this module conforms to
- [ ] `AGENTS.md` § "Every REQ … [kind]" (ADR-0.0.59) — REQ-kind discipline the Acceptance Criteria below obey

**Context:**

- [ ] Sibling OBPI-0.31.0-01 (state-transition-models) — the gold-standard closed-StrEnum + frozen-model + committed-schema + fence-test shape this OBPI mirrors
- [ ] Later OBPIs in ADR-0.32.0 (graph substrate, operator verbs, domain projections) consume this model layer but are out of scope here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/schemas/` exists with `load_schema`/`get_schema_path` (name-generic drop-in loader) — the new `ontology_node.json` lands here
- [ ] `.gzkit/governance/ontology.schema.json` present — the source of the verbatim `plane` (`product`/`process`) `$defs` enum this OBPI reuses
- [ ] `.gzkit/governance/ontology.json` present — NOTE: this is a doctrine/rule/actions governance document, NOT a typed-object catalog. REQ-04's partition test validates against this brief's own `OBJECT_TYPE_REGISTRY` (a total map over the closed `ObjectType` enum), never against `ontology.json`; the file is read only for continuity-of-naming reference
- [ ] `src/gzkit/commands/validate_cmd.py` present with `VALIDATOR_REGISTRY` — the `ontology_purity` scope registers here
- [ ] Parent ADR `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md` present, registered in `gz state`, and carrying a `## Boundary Invariants` section (STRUCTURAL-FENCE anchor for REQ-06)

**Existing Code (read; do NOT modify — establishes the conventions this module mirrors):**

- [ ] `src/gzkit/req_kind.py` — `enum.StrEnum` + frozen `extra="forbid"` Pydantic model precedent for a closed governance taxonomy (the pattern `LinkType`/`Ownership`/`Plane` + `OntologyNode` mirror)
- [ ] `src/gzkit/core/obpi_state_machine.py` + `src/gzkit/schemas/obpi_state_machine.json` — committed-schema-as-model-projection precedent (`load_schema(...) == ..._json_schema()` coherence)
- [ ] `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/obpis/OBPI-0.31.0-01-state-transition-models.md` — gold-standard model+schema+fence OBPI brief shape
- [ ] `src/gzkit/commands/validate_cmd.py` (`VALIDATOR_REGISTRY`, `_taxonomy_runner` lazy-import runner) + `src/gzkit/cli/parser_maintenance.py` (`--req-kind-discipline` flag) — how a new `gz validate --<scope>` registers end-to-end
- [ ] `.gzkit/governance/ontology.schema.json` `$defs.plane` — the canonical `product`/`process` enum (with its "constrains code / constrains governance" gloss) reproduced verbatim by the `Plane` StrEnum

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] No behavior surface in this library-only unit; it contributes no BDD scenario. The ADR's Gate-4 BDD is owned by OBPI-0.32.0-03 (`features/ontology.feature`, the sole `gz ontology` verb surface) and discharged once by the ADR-level `uv run -m behave features/` at closeout.

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- CONSTRUCTION HOUSEKEEPING (lint, type, test) proving the codebase is healthy.
     AUTHORING CONTRACT: single-program, shell-less invocations only — no &&, ||,
     |, ;, $(...), or redirects (GHI #415). One command per line. -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
uv run gz validate --ontology-purity
uv run -m unittest tests.test_ontology_model -v
uv run -m unittest tests.test_ontology_purity -v
```

## Demo

<!-- THE YIELDED PRODUCT: the importable two-axis model layer + the Harness-Purity
     fence. Concrete, runnable invocations (not --help). Harvested by the closeout
     walkthrough. -->

```bash
# The two-axis classification: every OntologyNode carries a required ownership + plane
uv run python -c "from gzkit.ontology.model import OntologyNode; print(sorted(OntologyNode.model_fields))"

# The closed axes: ownership is harness|product, plane is product|process
uv run python -c "from gzkit.ontology.model import Ownership, Plane; print([o.value for o in Ownership], [p.value for p in Plane])"

# Frozen + extra-forbid: an unknown field is refused at construction (fail-closed model)
uv run python -c "from gzkit.ontology.model import OntologyNode; import pydantic
try:
    OntologyNode(node_id='n', object_type='ADR', ownership='harness', plane='process', bogus=1)
    print('LEAK: unknown field accepted')
except pydantic.ValidationError:
    print('OK: unknown field refused')"

# plane reuses the dormant governance schema enum verbatim (verbatim equality
# is asserted by the REQ-0.32.0-01-02 @covers test; here we just show the members)
uv run python -c "from gzkit.ontology.model import Plane; print('plane members:', [p.value for p in Plane])"

# Harness-Purity fence: a gzkit product object placed in ownership:harness is refused
uv run gz validate --ontology-purity

# The committed schema is the model projection (loads name-generically)
uv run python -c "from gzkit.schemas import load_schema; print('ontology_node schema loaded:', bool(load_schema('ontology_node')))"
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test; SUPPORT via ledger event + structural validator; STRUCTURAL-FENCE
     via a parent-ADR ## Boundary Invariants entry. -->

- [ ] REQ-0.32.0-01-01 [BEHAVIOR]: `gzkit.ontology.model` ships `OntologyNode` and `OntologyEdge` as frozen `extra="forbid"` Pydantic models (`ConfigDict(frozen=True, extra="forbid")`, `.claude/rules/models.md`) plus a closed `LinkType` `enum.StrEnum`; constructing either model with an unknown field, or mutating a field after construction, raises `pydantic.ValidationError` — pinned by a `@covers(REQ-0.32.0-01-01)` test in `tests/test_ontology_model.py`.
- [ ] REQ-0.32.0-01-02 [BEHAVIOR]: every `OntologyNode` carries BOTH a required `ownership` axis (closed `StrEnum` of exactly `harness`/`product`) and a required `plane` axis whose members are exactly `product`/`process` reproduced verbatim from `.gzkit/governance/ontology.schema.json` `$defs.plane`; a node missing either axis or given an out-of-enum value raises `pydantic.ValidationError`, and a `@covers(REQ-0.32.0-01-02)` test asserts the `Plane` member-set equals the governance-schema enum so drift between them fails the test.
- [ ] REQ-0.32.0-01-03 [BEHAVIOR]: the Harness-Purity validator (`gzkit.ontology.purity.audit_ontology_purity`, dispatched by `gz validate --ontology-purity`) refuses a `product`-typed object placed in `ownership:harness` — given a node whose object type is a gzkit product type (CliVerb/Validator/Skill/Chore) tagged `ownership:harness`, the validator returns a non-empty error list (exit 3); a `@covers(REQ-0.32.0-01-03)` refusal test in `tests/test_ontology_purity.py` constructs exactly that node and asserts the refusal, and asserts a harness-legal GovZero-universal object passes clean.
- [ ] REQ-0.32.0-01-04 [BEHAVIOR]: every seated object type is classified by a TOTAL `OBJECT_TYPE_REGISTRY: dict[ObjectType, tuple[Ownership, Plane]]` over the closed `ObjectType` `StrEnum` — a `@covers(REQ-0.32.0-01-04)` test asserts (a) the registry is TOTAL: every `ObjectType` member has exactly one entry, so adding an `ObjectType` member without classifying it FAILS the test (the partition can fail on a business-logic change, not merely author error); (b) each type maps to exactly one plane (`product` XOR `process`) with both planes non-empty; and (c) the split obeys Harness-Purity (no gzkit product type — CliVerb/Validator/Skill/Chore — is classified `ownership:harness`). This registry is the single seating list that the Harness-Purity refusal fixture and this partition both read — there is no hand-assigned list elsewhere.
- [ ] REQ-0.32.0-01-05 [SUPPORT]: the JSON-schema projection of the `OntologyNode` model is committed at `src/gzkit/schemas/ontology_node.json` and loads via `gzkit.schemas.load_schema("ontology_node")` — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing `src/gzkit/schemas/ontology_node.json` emitted at OBPI completion.
- [ ] REQ-0.32.0-01-06 [STRUCTURAL-FENCE]: the Harness-Purity boundary this OBPI seats — `ownership:harness` admits only GovZero-universal object types, while gzkit's own product objects (CliVerb/Validator/Skill/Chore) are `ownership:product` and never appear in the harness subgraph — maps to parent ADR-0.32.0 `## Boundary Invariants` #4 (Harness purity); anchored there and audited at ADR closeout, not by a per-OBPI behavior test.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
