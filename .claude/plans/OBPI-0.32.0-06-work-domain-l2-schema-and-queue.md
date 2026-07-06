# Plan — OBPI-0.32.0-06: Work Domain L2 Schema And Queue

**OBPI:** OBPI-0.32.0-06-work-domain-l2-schema-and-queue
**Parent ADR:** ADR-0.32.0-gzkit-ontology (checklist item #6)
**Lane:** Heavy
**Mode:** Subagent-dispatch default (inline fallback acceptable given tight single-surface coupling)

## Context

Deliver the ontology **work domain**: four net-new append-only L2 edge event types
(`blocks`/`blocked_by`/`discovered_from`/`validates`), a `ready`/`blocked` TASK queue
replayed purely from those edges, advisory-first block surfacing (never a hard refusal),
a declared fail-closed `TORQUE_UP_MILESTONE`, and a code-enforced WWHTBT emission gate —
the four edge events are permanent once emitted (the ADR's one true one-way door,
§ Consequences Negative #4).

**Parent ADR § Decision item #6 (verbatim, for Implementation Summary):**
> "work domain: net-new L2 event schema (blocks/blocked_by/discovered_from/validates) +
> ready/blocked queue + advisory-first blocks with a declared fail-closed torque-up
> milestone; gated last on its own WWHTBT of the edge set (the one-way door)."

## Step 6a — Plan-Before-Exploration Disclosure (required narrative)

**Destination-in-mind:** Before writing this plan I had already formed the shape from the
brief REQs + the OBPI-0.31.0-01 / OBPI-0.32.0-02 exemplars: four frozen `_EventBase`
subclasses joined into `TypedLedgerEvent`; a `work_edge_json_schema()` projector coherence-
checked against a committed `work_edges.json` (mirroring `obpi_state_machine_json_schema()`);
a `replay_work_queue()` deriving ready/blocked purely from edges; a `TORQUE_UP_MILESTONE`
doctrine constant (`enforced=False`); and a sole `emit_work_edge()` path gated on a
`WwhtbtRecord` whose vocabulary must equal the committed discriminator set. That was the
destination.

**Rejected alternatives considered during exploration:**
1. *Emit the four events via new `ledger_events.py` factory helpers* (like `attested_event`).
   REJECTED — that would ripple into `audit_event_handlers` (graph-handler coverage in
   `ledger.py` / `_NO_GRAPH_IMPACT` waivers) and widen the surface beyond the brief. The
   sole-emit path in `work.py` constructs the typed model, dumps it, and appends a
   `LedgerEvent` directly — no factory, smaller blast radius.
2. *Model "block satisfaction" via a completion/unblock signal read from L1 frontmatter or
   `task_completed` events.* REJECTED — REQ-02 pins "purely from the four L2 edges, no
   L1/frontmatter read." In the advisory MVP a present block edge IS an unsatisfied block;
   satisfaction/removal semantics are the deferred `TORQUE_UP_MILESTONE`'s job, not shipped.
3. *Store the WWHTBT attestation as brief prose only (Requirement #2 minimum).* REJECTED —
   REQ-07 demands the freeze be **code-enforced** (emit raises on vocabulary divergence), so
   a `WwhtbtRecord` value object + a frozen `WORK_EDGE_DISCRIMINATORS` set is required, not
   just prose.
4. *Widen `triangle.py`'s EdgeType / reuse `LinkType.VALIDATES` as the event discriminator.*
   REJECTED — the graph `LinkType` layer and the L2 event-discriminator layer are distinct;
   conflating them is the differing-semantics-under-a-shared-name drift the ontology exists
   to kill (ADR § Alternatives).

## Files (all within amended Allowed Paths)

**Create:**
- `src/gzkit/ontology/work.py` — TASK/edge queue replay, advisory-first surfacing,
  `WORK_EDGE_DISCRIMINATORS`, `work_edge_json_schema()`, `TORQUE_UP_MILESTONE`,
  `WwhtbtRecord`, `emit_work_edge()` (sole gated emit path), `EmissionRefused` error.
- `src/gzkit/schemas/work_edges.json` — committed projection of the four edge event schemas.
- `tests/test_ontology_work.py` — `@covers`-decorated REQ tests.

**Edit (additive):**
- `src/gzkit/events.py` — four frozen `_EventBase` subclasses + union join.
- `src/gzkit/ontology/__init__.py` — idempotent package docstring marker (already present → no-op verify).
- `src/gzkit/ontology/corpus.py` — disposition 4 discriminators in `_ACKNOWLEDGED_NON_CORPUS_EVENT_TYPES` (coupled-surface; operator-ratified).
- `src/gzkit/schemas/ledger.json` — 4 `events` schema entries (coupled-surface; operator-ratified).
- `tests/test_schemas.py` — 4 `_EVENT_MODELS` rows (coupled-surface; operator-ratified).
- The brief — evidence.

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **REQ-01 + REQ-06 — four typed events + union join + round-trip.** RED: test that
   `parse_typed_event({...blocks...})` yields `BlocksEvent` (×4) and each round-trips
   `parse_typed_event(m.model_dump()).event == m.event`; a representative pre-existing type
   (`project_init`) still parses unchanged. Build the importable skeleton first (define the
   4 classes as stubs) so the red is assertion-level, not `ImportError`. GREEN: add classes
   with typed endpoint fields + join to union.
2. **REQ-01 + REQ-05 — schema projection + coherence.** RED: `load_schema("work_edges") ==
   work_edge_json_schema()` and projection non-trivial. GREEN: implement projector; write
   committed `work_edges.json` = `json.dumps(work_edge_json_schema(), indent=2, sort_keys=True)`.
3. **Coupled-surface coherence (Maxim 1a).** Disposition the 4 discriminators in `corpus.py`;
   add 4 `ledger.json` entries; add 4 `test_schemas.py` `_EVENT_MODELS` rows. Verify the
   pre-existing fences GREEN: `test_ontology_corpus.py::test_all_live_discriminators_are_dispositioned`,
   `::test_projection_reports_fidelity_on_live_lineage`, `test_ledger_event_schema_coverage`,
   `test_schemas` symmetry tests. (These fences are the RED that the union addition created;
   this step turns them GREEN.)
4. **REQ-02 — ready/blocked queue replay.** RED: table-driven test over edge fixtures — a
   TASK with an incoming block edge → `blocked`; one with none → `ready`; derived purely
   from edges (fixture ledger, no frontmatter). GREEN: `replay_work_queue(ledger)`.
5. **REQ-03 — advisory-first surfacing.** RED: a blocked TASK carries its blocker(s) as
   provenance AND `replay_work_queue` returns normally (no raise, no non-zero gate). GREEN.
6. **REQ-04 — torque-up milestone declared.** RED: `TORQUE_UP_MILESTONE.enforced is False`
   and `.summary` is substantive. GREEN: doctrine constant.
7. **REQ-07 — WWHTBT-gated sole emit path.** RED: `emit_work_edge` RAISES `EmissionRefused`
   when the `WwhtbtRecord` is absent OR its vocabulary diverges from `work_edges.json` set;
   succeeds only when present-and-matching — success branch on a **fixture** ledger (never the
   real append-only ledger). GREEN.
8. **REQ-05 fence (STRUCTURAL-FENCE).** No code — anchored to parent ADR Boundary Invariant #2.
   Verify no `gz validate` scope / gate / closeout consumes the queue; the work module adds no
   `gz` verb or `gz validate` scope. Audited at ADR closeout.

## Verification (from brief)

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_ontology_work -v
test -f src/gzkit/ontology/work.py
test -f src/gzkit/schemas/work_edges.json
```

Plus (coupled-surface regression guard): `uv run -m unittest tests.test_ontology_corpus
tests.test_schemas tests.governance.test_ledger_event_schema_coverage -v`.

## WWHTBT — the exact edge set (recorded before emission, REQ-07 / Requirement #2)

The frozen vocabulary is exactly the four ADR-Decision-named discriminators:
`{blocks, blocked_by, discovered_from, validates}`. What would have to be true for THIS set
to be the right permanent set: (a) work coupling decomposes into precedence (`blocks`/its
inverse `blocked_by`), provenance (`discovered_from`), and verification (`validates`) — the
three relations the ready/blocked queue + lineage need, and no fourth relation is required by
the queue's ready/blocked partition; (b) `blocks` and `blocked_by` are retained as distinct
(not collapsed) because emitters may naturally author from either endpoint and L2 is append-
only — collapsing later is impossible, keeping both is cheap and symmetric; (c) no existing
discriminator collides (verified against the union); (d) satisfaction/removal is deliberately
NOT an edge in this set (it is the torque-up milestone), so the set stays minimal. The gate
`emit_work_edge` refuses any emission whose declared vocabulary ≠ this committed set.

## Notes

- Core stays stdlib + Pydantic (hexagonal): `work.py` imports no third-party lib; networkx
  is not needed for the edge-replay queue (it operates on the L2 event stream, not the graph
  substrate).
- Size discipline: keep `work.py` ≤600 lines, functions ≤50.
