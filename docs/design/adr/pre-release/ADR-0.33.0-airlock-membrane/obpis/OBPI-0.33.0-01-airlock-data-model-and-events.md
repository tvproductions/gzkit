---
id: OBPI-0.33.0-01-airlock-data-model-and-events
parent: ADR-0.33.0-airlock-membrane
item: 1
lane: Heavy
status: Completed
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

**Status:** Completed

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
- `src/gzkit/ontology/corpus.py` — additive ONLY: disposition `airlock_in` / `airlock_out` in `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES`. The registry-coupled fence derives its discriminator set from the union and fail-closes on any un-dispositioned name (test_ontology_corpus, test_all_live_discriminators_are_dispositioned)
- `src/gzkit/schemas/ledger.json` — additive ONLY: add `events` rules for `airlock_in` / `airlock_out`. The `events` map is a closed registry; an absent name is rejected as `Unknown event type` (ledger_check, line 303) at first emit
- `tests/test_schemas.py` — additive ONLY: add the two class imports + two `_EVENT_MODELS` entries, required by test_all_schema_events_have_models once the ledger schema carries the events
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

### Step 4b — Independent Adversarial Validation (GHI #643)

**Adversary:** Codex (different vendor — an independent context prompted to REFUTE,
not confirm; a Claude validating Claude shares failure modes).
**Job:** `task-mrcrhhaq-dambrd`, status `completed`, workspace `/Users/jeff/Documents/Code/gzkit`,
created `2026-07-09T00:21:32Z`. Transcript (82 KB, vendor-cache — see GHI on
repo-bound capture): `~/.claude/plugins/data/codex-openai-codex/state/gzkit-6c7dcdb70ca321f2/jobs/task-mrcrhhaq-dambrd.log`

**Verdict: `REFUTED`** → gap fixed → re-validated against the adversary's own mutation.

**The refutation (Attack 2 — mutation).** REQ-03 claims `Provenance` is closed "of
exactly `LAW` / `OBSERVED`"; REQ-04 pins four further closed vocabularies. The tests
asserted only that a *specific* out-of-enum value was rejected — which proves the set
lacks that value, never that it lacks every other. The adversary added
`Authority.MATE`, `Decision.DEFER`, `Verdict.REVIEW` and observed:

```text
Ran 5 tests in 0.002s
OK
['captain', 'delegated', 'mate']
['proceed', 'pause', 'hold', 'revert', 'defer']
['clean', 'block', 'surface', 'resolve', 'review']
```

Adversary's closing **Weakest Point**, verbatim: *"The weakest point is exact enum
closure. The implementation currently has the right values, but the REQ-04 test suite
lets additional `Authority`/`Decision`/`Verdict` members pass, so the 'closed
vocabulary' claim is not fail-closed."*

**Fix.** Membership assertions added to the two REQs that make the claim
(`tests/test_airlock_model.py`, REQ-03 and REQ-04): each vocabulary is pinned to its
exact member list. Re-running the adversary's identical mutation now yields:

```text
Ran 5 tests in 0.001s
FAILED (failures=1)
```

Two further mutants that previously survived are also killed: a third `Provenance`
vein (`FABRICATED`) and a third `SeamKind` (`SIDEWAYS`).

**Attacks that failed to break the work** (each with real pasted output in the
transcript): the `events.py` diff is additive with no existing variant altered; no
`networkx`/`graspologic`/`tree-sitter` import; no airlock operator verb (gz airlock) registered;
`seam_map_json_schema()` is a pure projector; `load_schema("seam_map") ==
seam_map_json_schema()` returned `True`; and an `airlock_in` entry appended to a
scratch ledger **passed** `uv run gz validate --ledger` — exercising the registry
entry rather than merely reading the validator. The adversary restored the working
tree exactly.

**Findings deliberately NOT fixed here (routed, not excused).** Attack 7 surfaced four
unconstrained states: a `PULL`-kind edge inside `push_edges`; `accounted=True` inside
`unaccounted`; empty `source`/`target`; negative `blast_radius`. The adversary itself
judged these *"not explicit OBPI-01 REQ failures."* This OBPI ships shapes, never
compute (REQ-01). They are enforceable at the point of construction and are routed to
OBPI-0.33.0-02 (airlock-IN), which owns seam-map construction. Recorded in
`.gzkit/insights/agent-insights.jsonl` as a `discovery` record.

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof


The shape is live in the runtime, not merely declared in a schema file:

```
$ uv run python -c "from gzkit.events import parse_typed_event; print(type(parse_typed_event({'event':'airlock_in','id':'x','ts':'2026-07-08T00:00:00+00:00'})).__name__)"
AirlockInEvent
```

Falsifiability is witnessed, not asserted. Independent adversarial validation (Codex, job `task-mrcrhhaq-dambrd`) returned **REFUTED**: the tests proved a specific out-of-enum value was rejected, but never that the vocabularies were closed to exactly their declared members. Its refuting mutation — `Authority.MATE` + `Decision.DEFER` + `Verdict.REVIEW` — left the suite green:

```
Ran 5 tests in 0.002s
OK
```

Membership assertions were added to REQ-03 and REQ-04. Re-running the adversary's identical mutation now yields:

```
Ran 5 tests in 0.001s
FAILED (failures=1)
```

Three further mutants are killed that previously survived: a third Provenance vein (FABRICATED), a third SeamKind (SIDEWAYS), a third Verdict (FUZZY). Removing `frozen=True` kills REQ-01 and REQ-03; renaming `unaccounted` kills REQ-02.

Green bar (receipts): 6817 tests `arb-step-unittest-47804087a4d54b989f041ff003c74c7b`; ruff `arb-ruff-8f09af87b3cc47e48ff2c000dfb5a69f`; typecheck `arb-step-typecheck-8e43d17394114bdd9de43b37d5551325`; mkdocs --strict `arb-step-mkdocs-7b8824dcecb144179086dbf556ed640f`. `gz validate --documents --req-kind-discipline --cli-alignment`: 3 scopes pass. `gz covers`: behavior_uncovered_reqs 0.

### Implementation Summary


- Files created: `src/gzkit/airlock/__init__.py`, `src/gzkit/airlock/model.py`, `src/gzkit/schemas/seam_map.json`, `tests/test_airlock_model.py`, `tests/test_airlock_events.py`
- Files modified (additive only): `src/gzkit/events.py` (AirlockInEvent/AirlockOutEvent + TypedLedgerEvent union append), `src/gzkit/ontology/corpus.py` (registry-coupled fence disposition), `src/gzkit/schemas/ledger.json` (closed events registry), `tests/test_schemas.py` (_EVENT_MODELS coherence)
- Delivered: the airlock's pure additive data layer — five closed `enum.StrEnum` vocabularies (SeamKind, Provenance, Authority, Decision, Verdict), four frozen `extra="forbid"` Pydantic models (SeamEdge, the two-layer SeamMap, Preflight, DriftDiff), a committed `seam_map.json` projection, and two additive L2 ledger event variants. Shapes only: no behavior, no compute, no CLI verb, no ontology-sonar call, no new runtime dependency.
- Parent ADR section Decision seated: the seam-map carries BOTH senses of "seam" — seam-as-BODY (`bodies`, the declared footprint) distinct from seam-as-BOUNDARY (`push_edges`/`pull_edges`, the join) — and Provenance is non-erasable by construction (the state-doctrine section-2 guard).
- Tests added: 4 `@covers` tests (REQ-01..04) plus 1 schema-drift guard; 4 advisory round-trip tests. REQ-05/06 are [SUPPORT]: proof channel is ledger event + structural validator, never `@covers`.
- Coupled-surface note: registering a TypedLedgerEvent variant is a FOUR-surface operation (union, ledger registry, corpus fence, test _EVENT_MODELS). The brief's allowlist under-declared three; operator approved a surgical amendment matching precedent commit eeda0988.
- Date completed: 2026-07-09
- Attestation status: operator-attested (g0); Gate 5 recorded
- Defects noted: GHI #676 filed; #666 and #652 evidenced; four production-discovery gaps routed to OBPI-0.33.0-02

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

- **GHI #676** (filed this OBPI) — `gz-obpi-pipeline`: Step-4b adversary verdict has no
  durable capture; it lives only in a vendor plugin cache, outside the repo, ledger, and
  brief. The `### Step 4b` evidence section above is the hand-copied stopgap this GHI
  exists to mechanize. Cross-linked to #643 (parent doctrine) and #642 (sibling: RED
  falsifiability witness).
- **GHI #666** (pre-existing; recurrence evidence added this OBPI) — `pipeline-gate`:
  plan-audit receipt id-form mismatch dead-blocks `src/` writes. Reproduced verbatim here:
  `gz plan audit OBPI-0.33.0-01` writes a short-form receipt id that can never match the
  full-slug marker written by `gz obpi pipeline`. Cost an entire `implementer` subagent
  dispatch, which correctly refused to bypass the hook and returned `BLOCKED`.
- **GHI #652** (pre-existing; second instance added this OBPI) — module exceeds the
  600-line limit: `src/gzkit/events.py` is 735 lines (721 before this OBPI's additive
  14-line append). Pre-existing and additively worsened; a split is out of scope for an
  additive-only OBPI under the surgical-changes rule.
- **Routed to OBPI-0.33.0-02** (no GHI; `discovery` insight record) — four unconstrained
  states the adversary surfaced: a `PULL`-kind edge inside `push_edges`; `accounted=True`
  inside `unaccounted`; empty `source`/`target`; negative `blast_radius`. Not OBPI-01 REQ
  failures (this OBPI ships shapes, never compute); enforceable at construction time,
  which OBPI-02 owns.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Gate 5 recorded by g0 for OBPI-0.33.0-01-airlock-data-model-and-events after independent adversarial validation (Codex, job task-mrcrhhaq-dambrd) returned REFUTED on exact enum closure, the refutation was closed with membership assertions on REQ-03/REQ-04, and the adversary's identical mutation (Authority.MATE + Decision.DEFER + Verdict.REVIEW) was re-run and now FAILS. Green bar: 6817 tests receipt arb-step-unittest-47804087a4d54b989f041ff003c74c7b; ruff receipt arb-ruff-8f09af87b3cc47e48ff2c000dfb5a69f; typecheck receipt arb-step-typecheck-8e43d17394114bdd9de43b37d5551325; mkdocs --strict receipt arb-step-mkdocs-7b8824dcecb144179086dbf556ed640f; gz validate --documents --req-kind-discipline --cli-alignment 3 scopes pass; gz covers behavior_uncovered_reqs 0. Four BEHAVIOR REQs mutation-witnessed; REQ-05/06 [SUPPORT] proven via ledger event + structural validator. Defects tracked: GHI #676 filed, #666 and #652 evidenced; four production-discovery gaps routed to OBPI-0.33.0-02.
- Date: 2026-07-09

---

**Date Completed:** 2026-07-09

**Evidence Hash:** -
</content>
</invoke>
