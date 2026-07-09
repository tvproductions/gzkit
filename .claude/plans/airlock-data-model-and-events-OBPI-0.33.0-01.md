# Plan — OBPI-0.33.0-01-airlock-data-model-and-events

**OBPI:** `OBPI-0.33.0-01-airlock-data-model-and-events`
**Parent ADR:** `ADR-0.33.0-airlock-membrane` (feature / Heavy)
**Lane:** Heavy — ships a committed JSON-schema projection and two L2 ledger-event contract surfaces.

## Context

The parent ADR § Decision seats the two-sense seam-map this OBPI must shape:

> "The seam-map carries BOTH senses of 'seam' (operator refinement): seam-as-BODY (a contiguous region of similarity = the FOOTPRINT; for the pipeline door these are the OBPI brief's DECLARED Allowed Paths, not an inferred guess) and seam-as-BOUNDARY (the push/pull edges = the join). PUSH edges come from gz ontology reach (computed blast radius); PULL edges from the brief + parent-ADR invariants."

and the state-doctrine boundary that makes `Provenance` non-erasable:

> "the airlock ALWAYS logs what it encounters to the L2 ledger (L3 recomputes from L1+L2); it NEVER rewrites L1 canon — it reports findings and proposes governed, attested amendments only."

This OBPI ships **shapes, never compute**. No airlock-IN/OUT behavior, no CLI verb, no ontology sonar call, no new runtime dependency.

## Files

Amended allowlist (operator-approved 2026-07-08 — see § Notes, Gate Friction):

| File | Action |
|---|---|
| `src/gzkit/airlock/__init__.py` | CREATE — package marker, docstring only |
| `src/gzkit/airlock/model.py` | CREATE — 5 StrEnums, 4 frozen models, `seam_map_json_schema()` |
| `src/gzkit/schemas/seam_map.json` | CREATE — committed `SeamMap` projection |
| `src/gzkit/events.py` | ADDITIVE — `AirlockInEvent`/`AirlockOutEvent` + union append |
| `src/gzkit/ontology/corpus.py` | ADDITIVE — disposition both names in `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES` |
| `src/gzkit/schemas/ledger.json` | ADDITIVE — `events` rules for both |
| `tests/test_schemas.py` | ADDITIVE — 2 imports + 2 `_EVENT_MODELS` entries |
| `tests/test_airlock_model.py` | CREATE — `@covers` REQ-01..04 |
| `tests/test_airlock_events.py` | CREATE — `@covers` round-trip |

## Steps

### Step 1 — `gzkit.airlock` package + model module (REQ-01, REQ-02, REQ-03, REQ-04)

RGR per behavior. Create the importable skeleton first (stub symbols) so each test reds on its **own assertion**, never on `ImportError`.

Mirrors `src/gzkit/ontology/model.py:17-141` (closed `enum.StrEnum` + frozen `extra="forbid"` model + `*_json_schema()` projector).

Vocabularies (closed `enum.StrEnum`):

- `SeamKind`: `push` | `pull`
- `Provenance`: `LAW` | `OBSERVED`
- `Authority`: `captain` | `delegated`
- `Decision`: `proceed` | `pause` | `hold` | `revert`
- `Verdict`: `clean` | `block` | `surface` | `resolve`

Models, all `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`:

- `SeamEdge`: `kind: SeamKind`, `provenance: Provenance`, `source: str`, `target: str`, `accounted: bool`
- `SeamMap` (two-layer, exactly four fields): `bodies: tuple[str, ...]` (seam-as-BODY) · `push_edges: tuple[SeamEdge, ...]` · `pull_edges: tuple[SeamEdge, ...]` (seam-as-BOUNDARY) · `unaccounted: tuple[SeamEdge, ...]`
- `Preflight`: `seam_map: SeamMap`, `blast_radius: int` (delegation dial), `authority: Authority`, `decision: Decision | None`
- `DriftDiff`: `drift: tuple[SeamEdge, ...]`, `verdict: Verdict`, `resolutions: tuple[str, ...]`

`seam_map_json_schema() -> dict[str, Any]` returns `SeamMap.model_json_schema()`.

Core imports **stdlib + Pydantic only** (`.claude/rules/hexagonal-architecture.md` rule 1/2). No `networkx`, no `graspologic`, no `tree-sitter`.

### Step 2 — committed schema projection (REQ-05)

Write `src/gzkit/schemas/seam_map.json` as the exact output of `seam_map_json_schema()`. Verify `load_schema("seam_map")` resolves it name-generically (`src/gzkit/schemas/__init__.py:17`).

### Step 3 — additive event registration (REQ-06)

Mirror the `BlocksEvent` precedent at `src/gzkit/events.py:629-658`:

- `AirlockInEvent(_EventBase)` with `event: Literal["airlock_in"]`
- `AirlockOutEvent(_EventBase)` with `event: Literal["airlock_out"]`
- Append both to the `TypedLedgerEvent` union (`events.py:709-712`). No existing variant touched.

Base fields only — the brief's `## Demo` pins `parse_typed_event({'event':'airlock_in','id':'x','ts':...})`, so every payload field would have to be optional. See § Notes for why payload is deferred.

### Step 4 — coupled-surface coherence (AGENTS.md § DO IT RIGHT 1a)

Three consumers read the union or its registry. All three land in this same commit:

1. `src/gzkit/ontology/corpus.py` — add `"airlock_in"`, `"airlock_out"` to `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES`. Fail-closed today: `ledger_event_discriminators()` (`corpus.py:118`) derives from the live union, and `tests/test_ontology_corpus.py:193` asserts `registry - _ACCOUNTED_EVENT_TYPES == frozenset()`.
2. `src/gzkit/schemas/ledger.json` — add `events` rules `{"required": [], "properties": {}}` for both. The `events` map is a closed registry: `ledger_check.py:301-309` emits `Unknown event type: <name>` otherwise.
3. `tests/test_schemas.py` — add both class imports and both `_EVENT_MODELS` entries. Forced by step 4.2 via `test_all_schema_events_have_models` (`test_schemas.py:317`).

### Step 5 — tests

- `tests/test_airlock_model.py` — `@covers("REQ-0.33.0-01-01")` frozen + `extra="forbid"` on all four models (unknown field ⇒ `ValidationError`; post-construction mutation ⇒ `ValidationError`); `@covers("REQ-0.33.0-01-02")` four distinct `SeamMap` fields, `bodies` holds region strings, edge fields hold `SeamEdge`, an edge placed in `unaccounted` is preserved and not folded into push/pull; `@covers("REQ-0.33.0-01-03")` out-of-enum provenance rejected at construction AND `edge.provenance = <other>` raises; `@covers("REQ-0.33.0-01-04")` `Preflight`/`DriftDiff` shape, out-of-enum on `kind`/`authority`/`decision`/`verdict` raises, `decision` accepts `None`.
- `tests/test_airlock_events.py` — `@covers` round-trip: `parse_typed_event` resolves both discriminators; serialization round-trips.

Assertions derive from the brief's Acceptance Criteria, not from a run of the code (AGENTS.md § DO IT RIGHT 6).

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_airlock_model -v
uv run -m unittest tests.test_airlock_events -v
uv run -m unittest tests.test_ontology_corpus -v
uv run -m unittest tests.test_schemas -v
uv run gz covers OBPI-0.33.0-01-airlock-data-model-and-events --json
```

Heavy lane adds `uv run mkdocs build --strict`. Gate 4 (BDD) contributes no scenario — this is a library-only unit; the ADR's BDD is owned by OBPI-02/03.

## Notes

### Gate Friction — brief allowlist amendment (operator-approved)

`gz plan audit` reached FAIL, and the evaluator pass established that registering a `TypedLedgerEvent` variant is a four-surface operation. Precedent `eeda0988` (OBPI-0.32.0-06) touched `events.py` + `ledger.json` + `test_schemas.py` + `corpus.py` in one unit to register its four additive edge events. The brief named those events as its precedent but did not enumerate their files. Operator approved the surgical amendment; `improvement` insight appended to `.gzkit/insights/agent-insights.jsonl`.

### Step 6a — plan-before-exploration disclosure

**Destination-in-mind.** Before writing this plan I had already formed the approach: mirror `ontology/model.py` one-for-one — closed `StrEnum`s, frozen `extra="forbid"` models, a `*_json_schema()` projector, committed schema — and mirror `BlocksEvent` for the two additive events. The brief itself names both as the shapes to mirror, so the destination was supplied by the brief rather than discovered. What exploration *did* change: I did not know `corpus.py` fail-closes on union additions, and my original plan would have shipped a `gz check` red.

**Rejected alternatives.**

1. *Payload-bearing event models now* (`obpi_id`, `authority`, `decision`, seam counts on `AirlockInEvent`). Rejected: the brief's `## Demo` pins `parse_typed_event({'event':'airlock_in','id':'x','ts':...})`, forcing every payload field optional; and no emit site exists until OBPI-02, so any field set would be speculative (AGENTS.md § DO IT RIGHT 10, "nothing speculative"). OBPI-02 adds optional payload fields additively when it knows what the airlock actually encounters.
2. *Reuse `ontology.model.Provenance`* (values `intent`/`observed`) rather than a new airlock `Provenance` (`LAW`/`OBSERVED`). Rejected: the brief's `## Demo` pins `provenance='LAW'`, and the two vocabularies mean different things — the ontology's records which *vein* an edge came from, the airlock's records whether a seam is *declared law* or *observed fact*. Sharing a name across differing semantics is precisely the drift the ontology exists to kill (`.claude/rules/hexagonal-architecture.md` rule 8).
3. *Defer `ledger.json` + `_EVENT_MODELS` to OBPI-02* (minimal amendment, `corpus.py` only). Rejected by the operator: it leaves a latent `Unknown event type` defect across an OBPI boundary and departs from the `eeda0988` precedent.
4. *Compute the seam-map here.* Rejected — explicitly denied by the brief; this OBPI ships the shapes the computation later fills.

### Boundary Invariants honored

- BI-1 (airlock never writes L1 canon): this OBPI writes no canon; `Provenance` is a frozen, closed enum, so provenance is structurally non-rewritable.
- BI-6 (L3 informs, never gates): no `gz validate` scope consumes these models.
