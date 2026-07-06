# Plan — OBPI-0.32.0-02 networkx substrate + corpus projection

**OBPI:** OBPI-0.32.0-02-networkx-substrate-and-corpus-projection
**Parent ADR:** ADR-0.32.0-gzkit-ontology (Checklist item #2, MVP spine)
**Lane:** Heavy · **Sensitivity:** security (read-side `ledger.py` overlap)

## Parent ADR § Decision quote (the contract)

> "Pydantic models carry the typed Objects/Links (OntologyNode/OntologyEdge + a
> typed LinkType), held in a networkx MultiDiGraph (the graph engine —
> lateral/reachability traversal + multigraph that stdlib graphlib cannot
> supply)"; corpus "absorbs get_artifact_graph as a typed view over one replay
> path; reads canon". The graph "self-reports its own rebuild fidelity (replay
> completeness + freshness) so it can confess when it might be lying."

Boundary Invariant #1 (rebuild fidelity, registry-coupled — the load-bearing
fence, realized by REQ-05) and #2 (derived-never-authority — anchors REQ-06).

## Context

- OBPI-01 delivered `gzkit.ontology.model` (`OntologyNode`/`OntologyEdge`/
  `LinkType`/`ObjectType` + `OBJECT_TYPE_REGISTRY`), all frozen `extra="forbid"`.
- `Ledger.get_artifact_graph()` (`src/gzkit/ledger.py:776`) returns
  `dict[id -> {type, parent, children, attested, superseded_by, validated, ...}]`
  from ONE `read_all()` pass; it is the single replay source to absorb.
- `TypedLedgerEvent` (`src/gzkit/events.py:619`) is the live discriminated union;
  each member declares `event: Literal["<type>"]`. Enumerated read-only via
  `typing.get_args` — events.py is a DENIED path and stays untouched.

## Plan-Before-Exploration disclosures (Step 6a)

- **Destination-in-mind:** Before authoring, the approach I intended was: a thin
  `OntologyGraph` wrapper over `networkx.MultiDiGraph` keyed by `LinkType` for
  parallel edges, and a `project_corpus()` that maps `get_artifact_graph()` node
  dicts to typed nodes/edges, with fidelity computed against a live-introspected
  `TypedLedgerEvent` registry. Exploration confirmed this is feasible unchanged.
- **Rejected alternatives:** (a) Having the projection call `read_all()` itself
  to compute freshness — rejected, violates REQ-04 single-replay; resolved by
  caching a replay manifest inside `get_artifact_graph`'s existing pass.
  (b) A hardcoded `HANDLED = {...}` completeness set — rejected, violates REQ-05
  (goes stale); resolved by live union introspection. (c) Editing `events.py` to
  expose a discriminator helper — rejected, denied path + unnecessary; `get_args`
  introspection needs no source edit there.

## Files (all within brief Allowed Paths)

- `pyproject.toml` — add `networkx` to `[project].dependencies` (REQ-07 SUPPORT).
- `uv.lock` — lock the `networkx` resolution (`gz validate --distribution`).
- `src/gzkit/ontology/graph.py` — CREATE: `OntologyGraph` (MultiDiGraph wrapper).
- `src/gzkit/ledger.py` — light read-side: cache a replay manifest
  (`event_types`, `latest_ts`, `count`) during the existing `get_artifact_graph`
  `read_all()` pass; add getter. No signature change, no new write path.
- `src/gzkit/ontology/corpus.py` — CREATE: `project_corpus()` + `CorpusProjection`
  + `RebuildFidelity`.
- `tests/test_ontology_graph.py` — CREATE: `@covers(REQ-0.32.0-02-01)`.
- `tests/test_ontology_corpus.py` — CREATE: `@covers` for REQ-02/03/04/05.
- brief file — evidence sections.

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **networkx dependency (REQ-07 SUPPORT).** Add `networkx` to `pyproject.toml`
   `[project].dependencies`; `uv lock`; confirm import resolves. (Done first so
   graph.py imports are clean rather than import-erroring the later reds.)
2. **`OntologyGraph` substrate (REQ-01 BEHAVIOR).** RED: test that two edges of
   different `LinkType` between the same node pair are BOTH retained, and
   `reachable_from(id)` returns the transitive-descendant set. GREEN: MultiDiGraph
   wrapper keyed by `link_type`; `nx.descendants` for reachability; `add_node`/
   `add_edge`/`node_count`/`edge_count`/`node_ids`/`nodes`/`edges`.
3. **Ledger replay manifest (read-side; supports REQ-04/05).** RED: test that
   `get_artifact_graph` populates a cached manifest (event types seen + latest ts
   + count) and that reading it triggers no second `read_all`. GREEN: capture the
   manifest from the events list already fetched; add getter.
4. **Corpus node + parent/child edge parity (REQ-02 BEHAVIOR).** RED: node-id set
   and parent/child edge set identical to `get_artifact_graph`. GREEN: map each
   node `type` → `ObjectType`, seat ownership/plane via `OBJECT_TYPE_REGISTRY`,
   emit `parent`/`child` `OntologyEdge`s.
5. **Single-replay proof (REQ-04 BEHAVIOR).** RED: spy on `Ledger.read_all`
   records exactly one call, routed through `get_artifact_graph`; projection makes
   no independent `read_all`. GREEN: projection consumes `get_artifact_graph()` +
   cached manifest only.
6. **Typed supersedes/attests/validates edges (REQ-03 BEHAVIOR).** RED: each
   such relationship in ledger node metadata appears as a first-class
   `OntologyEdge` with distinct `LinkType` (SUPERSEDES/VALIDATES/…), not left in
   node dicts. GREEN: lift metadata (`superseded_by`, `validated`, attestation)
   into typed edges.
7. **Rebuild-fidelity self-report (REQ-05 BEHAVIOR).** RED: derive an unhandled
   discriminator from the LIVE `TypedLedgerEvent` union (not a fixture literal),
   assert it is `unaccounted` and `complete=False`; assert stale build →
   `fresh=False`; assert full-coverage → `complete=True`. GREEN: `RebuildFidelity`
   frozen model; `unaccounted = live_registry − projection_accounted`;
   `fresh = latest_ts <= build_ts`.
8. **REQ-06 STRUCTURAL-FENCE / REQ-07 SUPPORT verification.** Confirm ADR
   `## Boundary Invariants` #2 (derived-never-authority) anchors REQ-06 (already
   present — no code). REQ-07 proven by `gz validate --documents` + the
   `artifact_edited` ledger event citing `pyproject.toml` at completion.
9. **Verify + docs.** Run the brief Verification block; ensure `mkdocs --strict`
   and `gz validate --sensitivity`/`--req-kind-discipline` pass.

## Verification (from brief)

```
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --sensitivity
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_ontology_graph -v
uv run -m unittest tests.test_ontology_corpus -v
```

## REQ → proof channel

| REQ | Kind | Proof |
|-----|------|-------|
| REQ-0.32.0-02-01 | BEHAVIOR | `@covers` test in `tests/test_ontology_graph.py` |
| REQ-0.32.0-02-02 | BEHAVIOR | `@covers` parity test in `tests/test_ontology_corpus.py` |
| REQ-0.32.0-02-03 | BEHAVIOR | `@covers` typed-edge test |
| REQ-0.32.0-02-04 | BEHAVIOR | `@covers` single-replay spy test |
| REQ-0.32.0-02-05 | BEHAVIOR | `@covers` registry-coupled fidelity test |
| REQ-0.32.0-02-06 | STRUCTURAL-FENCE | ADR `## Boundary Invariants` #2 (closeout) |
| REQ-0.32.0-02-07 | SUPPORT | `gz validate --documents` + `artifact_edited` event citing `pyproject.toml` |

## Notes

- Tier-B derived-never-authority: no `gz validate` scope reads this graph as
  proof; writeback only by rebuild (REQ-04 NEVER, REQ-06).
- No new L2 event type, no `gz ontology` CLI, no tree-sitter (REQ-05 NEVER —
  those are OBPI-06/03/07).
