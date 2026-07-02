# Plan — OBPI-0.31.0-01-state-transition-models

**OBPI:** OBPI-0.31.0-01-state-transition-models
**Parent ADR:** ADR-0.31.0-obpi-state-machine (feature, heavy)
**Lane:** Heavy

## Context

Lay the canonical OBPI state-machine **model layer** (ADR § Decision items 1–2)
as pure additive domain code — the state anchor OBPI-02 (CLI verbs) and OBPI-03
(runtime monitor) consume. No runtime monitor, no CLI verb, no edit to the
legacy `core/lifecycle.py` choreography (retiring it is deferred-in-keel).
Witness taxonomy is transport-agnostic per GovZero canon (`human_attested` /
`self_close`) — no TTY/PTY value.

## Files

- **CREATE** `src/gzkit/core/obpi_state_machine.py` — `OBPIState`/`WitnessRequirement` StrEnums, frozen `State`/`Transition` Pydantic models, `OBPI_STATES` + `CANONICAL_TRANSITIONS` declarations, `obpi_state_machine_json_schema()` projector
- **CREATE** `src/gzkit/schemas/obpi_state_machine.json` — committed JSON-schema projection
- **CREATE** `tests/test_obpi_state_machine.py` — `@covers` REQ tests
- (already done) `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/ADR-0.31.0-obpi-state-machine.md` — `## Boundary Invariants` anchor
- (evidence) `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/obpis/OBPI-0.31.0-01-state-transition-models.md`

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **Skeleton** — create `obpi_state_machine.py` with importable stubs
   (`OBPIState`, `WitnessRequirement`, `State`, `Transition`, `OBPI_STATES`,
   `CANONICAL_TRANSITIONS`, `obpi_state_machine_json_schema`) so tests import
   cleanly and each red is an assertion-level red (not an import error).
2. **REQ-01** — RED: assert `OBPIState` members are exactly the 8 canonical
   states with lowercase-name values → GREEN: define the closed `StrEnum`.
3. **REQ-02** — RED: assert `Transition` rejects a non-member state and an
   unknown field (`pydantic.ValidationError`); accepts a valid transition with
   `required_evidence` + `witness` → GREEN: define `WitnessRequirement`
   (`human_attested`, `self_close`) + frozen `Transition`.
4. **REQ-03** — RED: assert `State` carries `terminal`, and `OBPI_STATES` has
   exactly one entry per `OBPIState` with `withdrawn`/`superseded` terminal →
   GREEN: define frozen `State` + `OBPI_STATES`.
5. **Declare** `CANONICAL_TRANSITIONS` — the forward lifecycle
   (drafted→planned→implementing→verified→attested→synced) plus withdraw/
   supersede edges, each with `witness` + `required_evidence`
   (`verified→attested` requires `human_attested`; withdraw/supersede require
   `human_attested`; others `self_close`).
6. **REQ-04** — RED: assert `load_schema("obpi_state_machine")` equals
   `obpi_state_machine_json_schema()` → GREEN: implement the projector, write
   the committed `schemas/obpi_state_machine.json`, confirm coherence.
7. **REQ-05 (STRUCTURAL-FENCE)** — no code; assert (via test + grep) the module
   imports no monitor/command surface. Parent ADR `## Boundary Invariants`
   anchors it.
8. Decorate every test with `@covers("REQ-0.31.0-01-NN")`; run
   `gz covers OBPI-0.31.0-01-state-transition-models --json` → `uncovered_reqs == 0`.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_obpi_state_machine -v
```

## Notes

- **Scope-collision (advisory):** `schemas/obpi_state_machine.json` glob-matches
  6 sibling OBPIs' broad `schemas/**` allowlists — all completed/inactive; no
  real contention. New-file-under-existing-glob, expected.
- **STRUCTURAL-FENCE:** models + schema only; no monitor (OBPI-03), no CLI verb
  (OBPI-02), no legacy-choreography edit.

## Step 6a — Plan-before-exploration disclosures

- **Destination-in-mind:** Before writing this plan I had already formed the
  approach during brief authoring — a new pure-domain module at
  `src/gzkit/core/obpi_state_machine.py` (sibling to `lifecycle.py`), a
  committed JSON schema, and RGR tests. This plan reflects that formed
  destination; it is not a fresh derivation.
- **Rejected alternatives:**
  1. **`governance/state_machine.py` placement** — rejected: `core/` is the
     pure-domain / no-I/O home (matches `core/lifecycle.py`); the hexagonal
     split (ADR-0.0.3) keeps the future monitor's I/O in `governance/`
     consuming these pure models.
  2. **Model-only "schema binding" (no committed JSON file)** — rejected: the
     ADR says "schema-bound," gzkit has a drop-in `load_schema` convention, and
     OBPI-02/03 need a stable, loadable schema contract. A coherence test binds
     model↔schema against drift.
  3. **Extend `core/lifecycle.py` in place** — rejected: it is the legacy
     string-keyed content-type choreography; mixing the new closed-enum machine
     into it risks confusion during the transition. Retiring it is
     deferred-in-keel, not this OBPI.
