---
id: OBPI-0.33.0-01-airlock-data-model-and-events
parent: ADR-0.33.0-airlock-membrane
item: 1
lane: Heavy
status: Draft
req_atomic:
  # Each REQ is one indivisible unit of labor with no sub-step below it —
  # implemented as a single Red-Green-Refactor cycle each: 01 the four frozen
  # models, 02 the two-layer SeamMap, 03 the non-erasable provenance guard,
  # 04 the Preflight + DriftDiff enum shape, 05 the committed seam_map schema
  # projection, 06 the additive airlock_in / airlock_out event registration.
  # No labor subdivided below any REQ.
  - REQ-0.33.0-01-01
  - REQ-0.33.0-01-02
  - REQ-0.33.0-01-03
  - REQ-0.33.0-01-04
  - REQ-0.33.0-01-05
  - REQ-0.33.0-01-06
---

# OBPI-0.33.0-01-airlock-data-model-and-events: Airlock Data Model And Events

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`
- **Checklist Item:** #1 - "Data model + ledger events: Pydantic SeamEdge (kind push|pull; provenance LAW|OBSERVED, non-erasable per state-doctrine section-2 guard), SeamMap (two-layer: bodies = declared regions + push/pull edges + unaccounted), Preflight (seam_map, blast_radius=delegation dial, authority captain|delegated, decision), DriftDiff (drift, verdict, resolutions) + airlock_in / airlock_out L2 event schemas under src/gzkit/schemas/. [SUPPORT; MVP spine]"

**Status:** Draft

## Objective

Lay the airlock's pure additive data layer — four frozen `extra="forbid"` Pydantic models under a net-new `gzkit.airlock` package (`SeamEdge`, the two-layer `SeamMap`, `Preflight`, `DriftDiff`) built on closed `enum.StrEnum` vocabularies, projected as a committed `src/gzkit/schemas/seam_map.json`, plus additive `airlock_in` / `airlock_out` L2 event variants registered in the `TypedLedgerEvent` discriminated union — carrying no behavior, no CLI, and no new runtime dependency.

## Lane

**Heavy** - This OBPI adds schema + ledger-event contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it ships two contract surfaces that later OBPIs and external
consumers bind against: a committed JSON-schema projection
(`src/gzkit/schemas/seam_map.json`, loadable via `gzkit.schemas.load_schema`)
and two net-new L2 ledger-event types (`airlock_in` / `airlock_out`) registered
in the `TypedLedgerEvent` discriminator — a persisted, replay-consumed runtime
contract. A new importable runtime model surface (`gzkit.airlock.model`) is added
that OBPI-02 (airlock-IN) and OBPI-03 (airlock-OUT) construct against.

## Allowed Paths

<!-- First backtick token on each bullet is the path; **CREATE** marks net-new
     files (existence-gate exempt, GHI #419). -->

- `src/gzkit/airlock/__init__.py` — **CREATE**: net-new `gzkit.airlock` package marker (docstring only)
- `src/gzkit/airlock/model.py` — **CREATE**: `SeamEdge` / `SeamMap` / `Preflight` / `DriftDiff` frozen `extra="forbid"` Pydantic models; closed `enum.StrEnum` vocabularies (`SeamKind` push|pull, `Provenance` LAW|OBSERVED, `Authority` captain|delegated, `Decision` proceed|pause|hold|revert, `Verdict` clean|block|surface|resolve); and a `seam_map_json_schema()` projector
- `src/gzkit/schemas/seam_map.json` — **CREATE**: committed JSON-schema projection of the `SeamMap` model, loaded name-generically via `gzkit.schemas.load_schema`
- `src/gzkit/events.py` — additive ONLY: add `AirlockInEvent` / `AirlockOutEvent` (`event: Literal["airlock_in"|"airlock_out"]`) and append them to the `TypedLedgerEvent` union; no existing variant touched
- `tests/test_airlock_model.py` — **CREATE**: `@covers`-decorated REQ tests for the model layer (frozen/extra-forbid, two-layer SeamMap, non-erasable provenance, Preflight/DriftDiff enum shape)
- `tests/test_airlock_events.py` — **CREATE**: `@covers` round-trip tests for the two additive event models (`parse_typed_event` discriminator resolution) — advisory coverage supporting the SUPPORT REQ
- `docs/user/manpages/` — a schema/event-contract manpage MAY be added here if the closeout docs pass warrants one (Gate 3 docs coherence); no other docs surface in scope
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` — parent ADR (READ-ONLY reference for § Intent / § Decision / § Boundary Invariants; no edit)
- `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-01-airlock-data-model-and-events.md` — this brief (evidence)

## Denied Paths

<!-- Items #2 (airlock-IN), #3 (airlock-OUT), #4 (mx door), #5 (permitted-entry),
     and #6 (doctrine-lawful) are sibling OBPIs in this same ADR — out of scope. -->

- `src/gzkit/airlock/enter.py`, any airlock-IN behavior (declare → ping → reconcile → gate) — that is OBPI-0.33.0-02, not this OBPI
- `src/gzkit/airlock/exit.py`, any airlock-OUT behavior (drift-diff → decision menu → fresh-transit routing) — that is OBPI-0.33.0-03
- Any pipeline Stage-1 / Stage-5 wiring, `gz mx` enter/exit wiring, or permitted-entry surface — OBPI-02/03/04/05
- The airlock CLI verb (gz airlock), any argparse/parser change, any `src/gzkit/commands/**` module — no operator verb ships in this OBPI
- Any `gz ontology reach` / sonar call, any seam-map COMPUTATION — this OBPI ships the shapes the computation later fills, never the computation
- `docs/governance/work-phases-and-airlock.md`, `docs/governance/four-phases-of-work.md`, any doctrine promotion — OBPI-06 (the one-way door)
- New runtime dependencies (networkx, graspologic, tree-sitter), CI files, lockfiles — the models are pure Pydantic + stdlib `enum.StrEnum`
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. NEVER/ALWAYS language. -->

1. REQUIREMENT: Deliver ONLY the additive data layer — the four `gzkit.airlock.model` Pydantic models + their closed `StrEnum` vocabularies, the committed `src/gzkit/schemas/seam_map.json` projection, and the additive `airlock_in` / `airlock_out` `TypedLedgerEvent` variants. No behavior, no compute, no CLI.
2. NEVER: add a new runtime dependency. The models are pure Pydantic + stdlib `enum.StrEnum`; `graspologic` stays ruled out (3.13-incompatible; statistical inference has no place in a gating path) and no `networkx` / `tree-sitter` import lands here.
3. NEVER: implement airlock-IN or airlock-OUT behavior, wire the pipeline / mx / permitted-entry doors, add the airlock operator verb (gz airlock), or call the ontology sonar — those are sibling OBPIs (#2–#5). The only surfaces this OBPI adds are the model module, the committed schema, and the two additive event types.
4. ALWAYS: keep all four models frozen with `extra="forbid"` per `.claude/rules/models.md` (`ConfigDict(frozen=True, extra="forbid")`); an unknown field or a post-construction mutation MUST raise `pydantic.ValidationError`.
5. ALWAYS: keep `SeamEdge.provenance` NON-ERASABLE — a closed `StrEnum` of exactly `LAW` / `OBSERVED` on a frozen model, so provenance can never be reassigned or blanked after construction (state-doctrine section-2 guard: L2 records what was encountered; provenance is not rewritable).
6. ALWAYS: register `airlock_in` / `airlock_out` ADDITIVELY — appended to the `TypedLedgerEvent` union with no edit to any existing variant — and keep the committed `src/gzkit/schemas/seam_map.json` the true projection of the `SeamMap` model (loadable via `load_schema("seam_map")`).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the seam-map + non-erasable-provenance clause** verbatim into `### Implementation Summary`. The clause this OBPI seats: *"The seam-map carries BOTH senses of 'seam' (operator refinement): seam-as-BODY (a contiguous region of similarity = the FOOTPRINT; for the pipeline door these are the OBPI brief's DECLARED Allowed Paths, not an inferred guess) and seam-as-BOUNDARY (the push/pull edges = the join). PUSH edges come from gz ontology reach (computed blast radius); PULL edges from the brief + parent-ADR invariants."* is the two-layer contract; the state-doctrine boundary — *"the airlock ALWAYS logs what it encounters to the L2 ledger … it NEVER rewrites L1 canon"* — is the non-erasable-provenance frame.
- [ ] Parent ADR § Intent — the "seam-map IS the externalized working set the model cannot hold in its head" why-frame for the model layer.
- [ ] Parent ADR § Boundary Invariants #1 (never writes L1 canon) — the doctrine backdrop for `Provenance` being a fixed, non-erasable field.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md`

> **STOP:** If you cannot quote the parent ADR § Decision clause that this OBPI implements (the two-sense seam-map + the "never rewrites L1" boundary), STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.claude/rules/models.md` — Pydantic `ConfigDict(frozen=True, extra="forbid")` policy the four models conform to
- [ ] `AGENTS.md` § "Every REQ … [kind]" (ADR-0.0.59) — the REQ-kind discipline the Acceptance Criteria below obey (BEHAVIOR → `@covers`; SUPPORT → ledger event + structural validator)

**Context:**

- [ ] Sibling OBPI-0.32.0-01 (ontology-model-and-purity) — the gold-standard closed-`StrEnum` + frozen-model + committed-schema-projection shape this OBPI mirrors
- [ ] OBPI-0.33.0-02 (airlock-IN) and OBPI-0.33.0-03 (airlock-OUT) CONSUME these models but are out of scope here — this OBPI ships shapes, never compute

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/schemas/` exists with `load_schema` / `get_schema_path` (name-generic drop-in loader) — the new `seam_map.json` lands here
- [ ] `src/gzkit/events.py` present with the `TypedLedgerEvent = Annotated[… , Field(discriminator="event")]` union and `parse_typed_event` — the two additive variants register here
- [ ] Parent ADR `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` present, registered in `gz state`, carrying `## Boundary Invariants`

**Existing Code (read; do NOT modify — establishes the conventions this module mirrors):**

- [ ] `src/gzkit/ontology/model.py` — `enum.StrEnum` + frozen `extra="forbid"` model + `..._json_schema()` projector precedent (the pattern `SeamEdge` / `SeamMap` mirror)
- [ ] `src/gzkit/events.py` — the `_EventBase` shape, the `Literal["…"]` discriminant convention, and the four ADR-0.32.0 edge events (`BlocksEvent` etc.) as the additive-append precedent for `AirlockInEvent` / `AirlockOutEvent`
- [ ] `src/gzkit/schemas/__init__.py` `load_schema` — the name-generic loader the committed `seam_map.json` is read through

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
- [ ] Relevant docs updated (schema/event-contract manpage if warranted)

### Gate 4: BDD (Heavy only)

<!-- gz-validate-skip: command-shape -->
- [ ] No behavior surface in this library-only unit; it contributes no BDD scenario. The ADR's Gate-4 BDD is owned by the airlock-IN / airlock-OUT OBPIs (#2 / #3, the sole `gz airlock` verb surface) and discharged once by the ADR-level `uv run -m behave features/` at closeout.

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
uv run -m unittest tests.test_airlock_model -v
uv run -m unittest tests.test_airlock_events -v
```

## Demo

<!-- THE YIELDED PRODUCT: the importable four-model airlock layer + committed
     schema + additive event types. Concrete, runnable invocations (not --help).
     Harvested by the closeout walkthrough. -->

```bash
# The four airlock models are importable from the net-new gzkit.airlock package
uv run python -c "from gzkit.airlock.model import SeamEdge, SeamMap, Preflight, DriftDiff; print('models:', SeamEdge.__name__, SeamMap.__name__, Preflight.__name__, DriftDiff.__name__)"

# The closed vocabularies: SeamKind push|pull, Provenance LAW|OBSERVED, Verdict clean|block|surface|resolve
uv run python -c "from gzkit.airlock.model import SeamKind, Provenance, Verdict; print([k.value for k in SeamKind], [p.value for p in Provenance], [v.value for v in Verdict])"

# Frozen + extra-forbid: an unknown field is refused at construction (fail-closed model)
uv run python -c "from gzkit.airlock.model import SeamEdge; import pydantic
try:
    SeamEdge(kind='push', provenance='LAW', source='a', target='b', accounted=True, bogus=1)
    print('LEAK: unknown field accepted')
except pydantic.ValidationError:
    print('OK: unknown field refused')"

# Provenance is non-erasable: mutating it on the frozen model raises (state-doctrine section-2 guard)
uv run python -c "from gzkit.airlock.model import SeamEdge; import pydantic
e = SeamEdge(kind='push', provenance='LAW', source='a', target='b', accounted=True)
try:
    e.provenance = 'OBSERVED'
    print('LEAK: provenance overwritten')
except pydantic.ValidationError:
    print('OK: provenance non-erasable')"

# Two-layer SeamMap: bodies (seam-as-body) and push/pull edges (seam-as-boundary) are distinct fields
uv run python -c "from gzkit.airlock.model import SeamMap; print('SeamMap layers:', sorted(SeamMap.model_fields))"

# The committed schema is the SeamMap projection (loads name-generically)
uv run python -c "from gzkit.schemas import load_schema; print('seam_map schema loaded:', bool(load_schema('seam_map')))"

# The two additive event types resolve through the TypedLedgerEvent discriminator
uv run python -c "from gzkit.events import parse_typed_event; ev = parse_typed_event({'event':'airlock_in','id':'x','ts':'2026-07-08T00:00:00+00:00'}); print('airlock_in parsed as:', type(ev).__name__)"
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test; SUPPORT via ledger event + structural validator; STRUCTURAL-FENCE
     via a parent-ADR ## Boundary Invariants entry. -->

- [ ] REQ-0.33.0-01-01 [BEHAVIOR]: `gzkit.airlock.model` ships `SeamEdge`, `SeamMap`, `Preflight`, and `DriftDiff` as frozen `extra="forbid"` Pydantic models (`ConfigDict(frozen=True, extra="forbid")`, `.claude/rules/models.md`); constructing any of the four with an unknown field, or mutating any field after construction, raises `pydantic.ValidationError` — pinned by a `@covers(REQ-0.33.0-01-01)` test in `tests/test_airlock_model.py`.
- [ ] REQ-0.33.0-01-02 [BEHAVIOR]: `SeamMap` is TWO-LAYER — it carries `bodies: tuple[str, ...]` (the declared regions, seam-as-BODY) as a field DISTINCT from `push_edges: tuple[SeamEdge, ...]` and `pull_edges: tuple[SeamEdge, ...]` (the join, seam-as-BOUNDARY), plus `unaccounted: tuple[SeamEdge, ...]`; a `@covers(REQ-0.33.0-01-02)` test asserts all four fields exist as separate members, that `bodies` holds region strings while the edge fields hold `SeamEdge` instances, and that an edge placed in `unaccounted` is preserved (not silently folded into `push_edges`/`pull_edges`).
- [ ] REQ-0.33.0-01-03 [BEHAVIOR]: `SeamEdge.provenance` is a closed `Provenance` `enum.StrEnum` of exactly `LAW` / `OBSERVED` and is NON-ERASABLE — because the model is frozen, provenance cannot be reassigned or blanked after construction (state-doctrine section-2 guard); a `@covers(REQ-0.33.0-01-03)` test asserts (a) an out-of-enum provenance value raises `pydantic.ValidationError` at construction, and (b) assigning `edge.provenance = <other>` on a constructed edge raises `pydantic.ValidationError` — the non-erasability is enforced, not merely documented.
- [ ] REQ-0.33.0-01-04 [BEHAVIOR]: the `Preflight` and `DriftDiff` shapes are pinned — `SeamEdge.kind` is a closed `SeamKind` StrEnum (`push`/`pull`); `Preflight` carries `seam_map: SeamMap`, `blast_radius: int` (the delegation dial), `authority: Authority` StrEnum (`captain`/`delegated`), and `decision: Decision | None` StrEnum (`proceed`/`pause`/`hold`/`revert`); `DriftDiff` carries `drift: tuple[SeamEdge, ...]`, `verdict: Verdict` StrEnum (`clean`/`block`/`surface`/`resolve`), and `resolutions: tuple[str, ...]`; a `@covers(REQ-0.33.0-01-04)` test constructs valid instances and asserts an out-of-enum value on any of `kind` / `authority` / `decision` / `verdict` raises `pydantic.ValidationError`, and that `decision` accepts `None`.
- [ ] REQ-0.33.0-01-05 [SUPPORT]: the JSON-schema projection of the `SeamMap` model is committed at `src/gzkit/schemas/seam_map.json` and loads via `gzkit.schemas.load_schema("seam_map")` — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing `src/gzkit/schemas/seam_map.json` emitted at OBPI completion.
- [ ] REQ-0.33.0-01-06 [SUPPORT]: `airlock_in` and `airlock_out` are registered as ADDITIVE `TypedLedgerEvent` variants in `src/gzkit/events.py` (appended to the discriminated union so `parse_typed_event` resolves them via the `event` discriminator, no existing variant altered) — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing `src/gzkit/events.py` emitted at OBPI completion.

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
</content>
</invoke>
