# Plan — OBPI-0.0.72-04-security-floor-overridden-event

**Parent ADR:** ADR-0.0.72-meta-governance-coherence (foundation, heavy)
**OBPI:** OBPI-0.0.72-04-security-floor-overridden-event (Heavy)

## Decision item (parent ADR §Decision #4, verbatim)

> ADAPTER — `security_floor_overridden` ledger event. New Pydantic event model +
> factory + `ledger.json` schema entry, emitted whenever `gz obpi complete
> --accept-security-floor` fires, recording `obpi_id`, overridden surface(s),
> `reason`, `attestor`, and `ts`. Makes overrides of a completion-state-editing
> gate auditable via ledger census.

## Destination-in-mind (Step 6a disclosure)

Before writing this plan I had already concluded the shape: mirror the existing
`obpi_completion_repudiated` event triple (model in `events.py`, factory in
`ledger_events.py`, schema entry in `ledger.json`) plus the `_EVENT_MODELS`
registration in `tests/test_schemas.py`, and emit from the `if
accept_security_floor and effective_sensitivity == "security":` branch at
`obpi_complete.py:1103`. The `ObpiCompletionUncoveredAcceptEvent` is the closer
template (it declares an explicit `obpi_id` field alongside base `id`).

**Rejected alternatives:** (a) reuse base `_EventBase.id` as the obpi_id instead
of an explicit field — rejected because the brief REQ-01 lists `obpi_id` as a
first-class recorded field and `ObpiCompletionUncoveredAcceptEvent` sets the
precedent for an explicit `obpi_id`. (b) A new global writer-model round-trip
validator — rejected/withdrawn already (OBPI-0.0.72-01), coherence re-homed to
the existing `_EVENT_MODELS` alignment (REQ-05).

## Design (mirror the repudiated triple)

1. **Model** — `src/gzkit/events.py`: `SecurityFloorOverriddenEvent(_EventBase)`
   with `event: Literal["security_floor_overridden"]` and explicit
   `obpi_id`/`surfaces`/`reason`/`attestor`, each `Field(..., min_length=1)`.
   `ts` is inherited from `_EventBase`. Add the class to the `TypedLedgerEvent`
   discriminated union.
2. **Factory** — `src/gzkit/ledger_events.py`: `security_floor_overridden_event(*,
   obpi_id, surfaces, reason, attestor) -> LedgerEvent` mirroring
   `obpi_completion_uncovered_accept_event` (base `id=obpi_id`, `parent=obpi_id`,
   `extra={obpi_id, surfaces, reason, attestor}`).
3. **Schema** — `src/gzkit/schemas/ledger.json`: new `security_floor_overridden`
   entry under `events`, `required: [obpi_id, surfaces, reason, attestor]`,
   properties each `type:string, min_length:1` (mirror the repudiated entry;
   base fields id/ts/event/schema/parent are not per-event schema properties).
4. **Registration** — `tests/test_schemas.py`: import the model and add
   `"security_floor_overridden": SecurityFloorOverriddenEvent` to `_EVENT_MODELS`
   so the set-equality + property-parity alignment tests pass (REQ-05).
5. **Emission** — `src/gzkit/commands/obpi_complete.py` at the line-1103 branch:
   `ledger.append(security_floor_overridden_event(obpi_id=obpi_id,
   surfaces=<matched categories>, reason=accept_security_floor,
   attestor=attestor))`. `accept_security_floor` IS the operator reason string.
   Emit exactly once, only in this branch (REQ-02/03); additive/best-effort,
   never a new gate (REQ-04).

## Scope decision — sourcing `surfaces` — RESOLVED: Option A (operator-approved 2026-07-13)

`surfaces` = the matched security-surface category labels (e.g. `auth_boundaries`)
from `match_globs(brief_allowed_paths, registry)`. Both `load_registry` and
`match_globs` are public in `gzkit.models.security_surfaces`, BUT extracting the
brief's allowed-path globs uses `_extract_sensitivity_allowed_paths` (+3 module
regexes) which is **private to `sensitivity.py` — a file NOT in this brief's
Allowed Paths.**

- **Option A (recommended):** add a public `detect_brief_security_surfaces(
  brief_text, project_root) -> tuple[str, ...]` to `sensitivity.py` (mirrors
  `detect_brief_security_floor`, reuses the canonical extraction + registry
  load, returns `match_globs(...)`); **amend OBPI-04 Allowed Paths to include
  `sensitivity.py`.** No duplication; one canonical extraction serves both the
  floor decision and the surface record (DO IT RIGHT §1 fix-the-class).
- **Option B:** keep Allowed Paths as-is; inline-duplicate the ~18-line
  extractor + 3 regexes in `obpi_complete.py`. Stays in declared scope but
  duplicates canonical logic (drift risk).

## Self-dogfood consequence (Stage 5)

OBPI-04 edits `obpi_complete.py`, a registered `auth_boundaries` surface, so its
OWN completion computes `effective_sensitivity == "security"` and the completion
must pass `--accept-security-floor '<reason>'` — which fires the new emission
branch and writes the first real `security_floor_overridden` event. The feature
proves itself at its own Gate 5. (Brief is grandfathered, so `gz validate
--sensitivity` does not fail-close.) This is the Key Proof.

## TDD sequence (Red-Green-Refactor, one behavior per cycle)

`tests/test_security_floor_overridden.py` (CREATE):
1. RED: construct model with all fields → assert fields present; construct with
   an empty required field → assert `ValidationError` (REQ-01). Watch it fail on
   the assertion (create importable stub first to avoid an import-only red).
2. RED: factory produces a `LedgerEvent` with `event="security_floor_overridden"`
   and the four extra fields (REQ-02).
3. RED: schema round-trip via `_EVENT_MODELS` alignment (REQ-05).
4. RED: emission — a `--accept-security-floor` completion appends exactly one
   event; a normal completion appends none (REQ-02/03); census counts 0→1
   (REQ-03).
5. GREEN each in turn (model → factory → schema → registration → emission).

## Verification

- `uv run gz arb ruff` / `arb typecheck` / `arb step --name unittest`
- `uv run -m unittest tests.test_security_floor_overridden -v`
- `uv run gz validate --documents`
- `uv run gz covers OBPI-0.0.72-04-security-floor-overridden-event --json`
  (BEHAVIOR REQ @covers parity) + `gz arb red` per BEHAVIOR REQ
- Heavy: `uv run mkdocs build --strict`, scoped behave for @REQ tags if any

## Allowed-Paths note

If Option A is chosen, `src/gzkit/governance/trust_audits/sensitivity.py` is
added to the brief Allowed Paths via operator-approved amendment before Stage 2
edits it (Gate Friction: evaluator → operator approval → surgical amendment).
