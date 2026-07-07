# Plan: OBPI-0.32.0-07 — Source Domain Tree-Sitter Anchors

**OBPI:** OBPI-0.32.0-07-source-domain-tree-sitter-anchors
**Parent ADR:** ADR-0.32.0-gzkit-ontology
**Lane:** Heavy

## Context

The ontology's corpus (02), work (06), and OKF (05) domains are landed and
attested. OBPI-02's registry-coupled rebuild-fidelity fence is proven live —
the breadth-gate (parent ADR § Target Scope; brief REQ-6) is cleared, so the
source domain may begin. This increment builds `gzkit.ontology.source`: the
sensor that images the SOURCE subgraph (product code → REQ anchors + polyglot
code-coupling) and absorbs `triangle.py`'s `detect_drift` as a behavior-preserving
subgraph view. It discharges the `tree-sitter` half of the parent ADR's
GO-attested STDLIB-FIRST departure (Phase-0 airlock-in, 2026-07-02).

### Destination-in-mind (Step 6a disclosure)

Before writing this plan I had already formed the approach: mirror `corpus.py`'s
shape (frozen Pydantic domain models + `OntologyEdge` emission + a `.gzkit/ontology/*.json`
Tier-B index), reuse `traceability.find_covers_in_source` for the `@covers` half,
write a net-new `@surface` sibling scanner, and confine tree-sitter to a single
adapter function returning domain types. The `detect_drift` absorption is a
thin wrapper delegating to the existing pure function with a golden-fixture
parity test pinning byte-equality.

### Rejected alternatives

1. **Building source→REQ edges into the networkx `OntologyGraph` substrate directly.**
   Rejected: the brief scope is edge *emission* + a derived index, not graph
   mutation; adding graph-substrate coupling would reach into OBPI-02's surface
   and inflate blast radius. `source.py` emits `list[OntologyEdge]`; graph
   assembly is a downstream consumer's job.
2. **Using stdlib `ast` for the code-coupling parse.** Rejected on the parent
   ADR's own rationale: `ast` is Python-only; tree-sitter is the polyglot sensor
   the source domain exists to justify. Using `ast` would silently un-discharge
   the attested departure.
3. **Rewriting `detect_drift`'s internals as a graph traversal.** Rejected:
   REQ-02 demands byte-identical `DriftReport` for identical inputs. The safe
   absorption is a VIEW that delegates to the untouched pure function, not a
   reimplementation. "Subgraph view" = the source-subgraph edges are the input
   projection; the drift computation stays the proven pure `detect_drift`.

## Files

All within the brief Allowed Paths:

- `src/gzkit/ontology/source.py` — **CREATE** (core domain + tree-sitter adapter)
- `src/gzkit/ontology/__init__.py` — **MODIFY (reconcile only)** — no behavioral edit needed; docstring already scopes the package
- `.gzkit/ontology/source_anchors.json` — **CREATE (generated)** — Tier-B index
- `src/gzkit/triangle.py` — **MODIFY (compat)** — add `detect_drift` subgraph-view wrapper; preserve all public names
- `tests/test_ontology_source.py` — **CREATE** — `@covers`-decorated REQ tests + golden-fixture parity
- `pyproject.toml` — **MODIFY** — add `tree-sitter` + `tree-sitter-python` grammar
- `uv.lock` — **MODIFY** — lock the added dependency graph

## Architecture (hexagonal — binding)

Per `.claude/rules/hexagonal-architecture.md`: tree-sitter is a third-party
dependency and MUST live behind an adapter, never in the core.

- **Core (stdlib + Pydantic only):** the frozen models (`SourceAnchor`,
  `SourceAnchorIndex`, `CodeCouplingEdge`, `OrphanGapReport`), `@covers`/`@surface`
  scanning (reuses `traceability.find_covers_in_source` + a net-new AST/regex
  `@surface` scanner), index build/load/round-trip, orphan-gap detection, and
  the `detect_drift` view. All exercisable WITHOUT importing tree-sitter (rule 6).
- **Adapter (the ONLY tree-sitter import site):** one function,
  `_parse_coupling_edges(source_paths) -> list[CodeCouplingEdge]`, that invokes
  the tree-sitter Python grammar, walks the parse tree for import/definition
  relationships, and returns domain `CodeCouplingEdge` models — NEVER a
  tree-sitter native node crossing the boundary (rule 3).
- **One adapter → no formal `Protocol` port yet** (rule 5: encapsulate first;
  formalize when a second grammar adapter is real). The method shape is designed
  now; the port extraction is deferred.

## Steps (Red-Green-Refactor, one behavior per cycle)

Skeleton-first to avoid the false-red (import-error) anti-pattern: create
`source.py` with no-op stubs for every public symbol so tests import cleanly and
each red is an assertion-level failure.

1. **Dependency + skeleton.** Add `tree-sitter` + `tree-sitter-python` to
   `pyproject.toml`; `uv lock`; `uv sync`. Create `source.py` with stub
   signatures (`build_source_anchor_index`, `load_source_anchor_index`,
   `detect_orphan_gaps`, models) so the test module imports without error.
   Quote the parent ADR § Decision source-domain clause + the GO-attested
   departure verbatim in the module docstring / brief `### Implementation Summary`.

2. **REQ-01 [BEHAVIOR] — `@covers` in product source → source→REQ edges.**
   RED: test asserting a `@covers(REQ-...)` anchor in a `src/**` fixture yields a
   source→REQ `OntologyEdge` with `(source_path, line, req_id)` and a CODE-origin
   vertex, distinct from test→spec COVERS. GREEN: scan `src/**` via
   `find_covers_in_source`, emit `LinkType.COVERS` edges with `Provenance.OBSERVED`.

3. **REQ-02 [BEHAVIOR] — `@surface` many-to-many cross-REQ layer.**
   RED: test asserting a single source unit declaring multiple `@surface(REQ-...)`
   yields multiple surface→REQ edges, read WITHOUT `@covers`'s decoration-time
   REQ-existence enforcement, typed `LinkType.SURFACE`. GREEN: net-new `@surface`
   scanner (regex sibling of the `@covers` pattern), emit surface edges.

4. **REQ-03 [BEHAVIOR] — tree-sitter polyglot code-coupling.**
   RED: test asserting a known import-coupling edge between two fixture source
   units (grammar actually invoked, parse tree walked — not merely imported).
   GREEN: the tree-sitter adapter function parses with the Python grammar, walks
   import/definition nodes, returns `CodeCouplingEdge` domain models.

5. **REQ-04 [BEHAVIOR] — deterministic `source_anchors.json` round-trip.**
   RED: test asserting `build_source_anchor_index()` writes a Pydantic-modeled
   `.gzkit/ontology/source_anchors.json` mapping each REQ → covering anchors with
   `file:line` provenance, and `load(dump(x)) == x`. GREEN: frozen
   `SourceAnchorIndex` model + deterministic sorted serialization; `anchors_for(req)`
   query method.

6. **REQ-05 [BEHAVIOR] — orphan-gap detection.**
   RED: test over a fixture with a known gap asserting every REQ with no covering
   source anchor (and every source anchor whose REQ id is unknown) surfaces in a
   sorted `OrphanGapReport`. GREEN: deterministic set-diff against known brief REQs
   (via `traceability` REQ discovery), sorted output.

7. **REQ-06 [BEHAVIOR] — `detect_drift` compat subgraph view.**
   RED: golden-fixture parity test asserting the re-expressed `detect_drift`
   returns a `DriftReport` EQUAL to the pre-absorption result for identical inputs
   (including `scan_timestamp`). GREEN: express `detect_drift` as a subgraph view —
   delegate to the untouched pure computation over the source-subgraph edge
   projection; preserve `detect_drift` signature + `EdgeType`/`LinkageRecord`/
   `VertexRef`/`DriftReport` unchanged (no deletions/renames). Coupled-surface
   coherence: the parity test lands in the same commit (AGENTS.md § DO IT RIGHT 1a).

8. **REQ-07 [SUPPORT] — dependency attestation.** Confirm `pyproject.toml` +
   `uv.lock` carry `tree-sitter`; `gz validate --documents` green; the
   `artifact_edited` ledger event citing this brief emits at completion. Quote the
   GO-attested departure verbatim in `### Implementation Summary`.

## Verification (from brief § Verification — shell-less, one per line)

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_ontology_source -v
uv run gz drift
uv run gz covers
test -f src/gzkit/ontology/source.py
test -f .gzkit/ontology/source_anchors.json
```

## Notes / Boundary honoring

- **Derived-never-authority (BI #2):** `source_anchors.json` is Tier-B —
  regenerable, never authoritative, never a gate/`gz validate` input.
- **Denied paths honored:** no edit to `ledger.py`, `commands/state.py`, the L2
  event schema, `schemas/`, any CLI verb, or `traceability.py` (reused via import).
  No `networkx` dependency added here (OBPI-02 owns it).
- **No public-name deletion in `triangle.py`** — absorption is a compat view.
- **Models:** frozen Pydantic (`ConfigDict(frozen=True, extra="forbid")`) per
  `.claude/rules/models.md`.
- **Cross-platform:** `pathlib.Path`, `encoding="utf-8"`, `.as_posix()` on stored
  path identifiers per `.claude/rules/cross-platform.md`.
```
