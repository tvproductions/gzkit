---
id: OBPI-0.32.0-07-source-domain-tree-sitter-anchors
parent: ADR-0.32.0-gzkit-ontology
item: 7
lane: Heavy
status: Completed
# req_atomic — each REQ is one indivisible unit of labor with no sub-REQ
# subdivision. The source domain was authored as one continuous TDD flow, one
# Red-Green-Refactor increment per REQ: 01 (@covers source anchors via structural
# decorator-walk), 02 (@surface many-to-many layer), 03 (tree-sitter import +
# definition coupling resolved between source units), 04 (deterministic
# round-tripping source_anchors.json), 05 (orphan-gap detection), 06 (detect_drift
# re-expressed as a subgraph view — one behavior-preserving absorption), 07
# [SUPPORT] (the tree-sitter dependency add — no test labor), 08 (the SourceParser
# port + two adapters — one cohesive "an interchangeable port exists" deliverable;
# its internal parts — port, ast adapter, tree-sitter adapter, contract test — are
# the single act of building the port, not separately-attributable labor units).
# None subdivided into seq=02+; the pipeline-minted seq=01-per-REQ buckets ARE the
# true labor shape (GHI #590).
req_atomic:
  - REQ-0.32.0-07-01
  - REQ-0.32.0-07-02
  - REQ-0.32.0-07-03
  - REQ-0.32.0-07-04
  - REQ-0.32.0-07-05
  - REQ-0.32.0-07-06
  - REQ-0.32.0-07-07
  - REQ-0.32.0-07-08
---

# OBPI-0.32.0-07-source-domain-tree-sitter-anchors: Source Domain Tree Sitter Anchors

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- **Checklist Item:** #7 - "source domain: tree-sitter code-coupling + @covers/@surface anchors + source->REQ first-class + source_anchors.json query index + orphan-gap detection; absorbs triangle.py's edge model, re-expressing detect_drift as a subgraph view (compat-view, behavior preserved)."

**Status:** Completed

## Objective

Build the ontology's **source domain**: a `src/gzkit/ontology/source.py` sensor
that (1) extracts `@covers(REQ-...)` anchors found in product source (`src/**`)
as first-class source→REQ edges, (2) reads the lighter `@surface(REQ-...)` anchor
as a many-to-many cross-REQ layer, (3) uses tree-sitter to build polyglot
code-coupling edges between source units, (4) emits a regenerable
`source_anchors.json` query-before-grep index, and (5) runs orphan-gap detection
over every REQ. It absorbs `triangle.py`'s edge model by re-expressing
`detect_drift` as a behavior-preserving subgraph VIEW over the source-subgraph —
triangle's public surface stays intact. This is the increment that discharges the
`tree-sitter` half of the parent ADR's GO-attested STDLIB-FIRST departure.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds a new importable runtime module surface
(`gzkit.ontology.source`), a generated `source_anchors.json` index contract that
the downstream ontology CLI (item #3) consumes, and a new runtime dependency
(`tree-sitter`) — a dependency-manifest change is itself a heavy-lane
external-contract change. It also re-expresses `triangle.py`'s `detect_drift`
(a runtime contract other code and tests bind to), so coupled-surface behavior
preservation is a heavy-lane concern.

**Why tree-sitter, re-justified (STDLIB-FIRST).** The departure rationale is NOT
that tree-sitter parses Python better than stdlib `ast` (it does not) — it is
that gzkit is a HARNESS that runs on adopter codebases, and `ast` is
structurally Python-only; tree-sitter is the polyglot sensor `ast` cannot be.
That is a named-capability gap, not popularity or recency (the STDLIB-FIRST
anti-rationales). The source-domain parse REQ exercises the Python grammar at
minimum, but the dependency earns its place on the multi-language surface — the source domain's
reason to exist. Per § Target Scope this is deferred-breadth: the source domain
does NOT begin until OBPI-02's registry-coupled rebuild-fidelity fence is proven
live.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/ontology/source.py` — **CREATE**: tree-sitter polyglot code-coupling extraction + `@covers`/`@surface` source-anchor scanning → source→REQ edges; `source_anchors.json` index builder; orphan-gap detector
- `src/gzkit/ontology/__init__.py` — **CREATE** (package marker; created by OBPI-0.32.0-01/02 if not already present — reconcile only, no behavioral edit)
- `src/gzkit/ontology/model.py` — **CONSUMED (import-only, never edited)**: `source.py` and the tests import `OntologyNode`/`OntologyEdge`/`LinkType`/`Provenance` from it. Declared here for coupled-surface honesty (AGENTS.md § DO IT RIGHT 1a — the source domain's real import dependency); owned by OBPI-0.32.0-01, NEVER modified by this OBPI
- `.gzkit/ontology/source_anchors.json` — **CREATE** (generated): the Tier-B derived query-before-grep index of every source→REQ anchor (regenerable from source, never authoritative)
- `src/gzkit/triangle.py` — **MODIFY (compat)**: re-express `detect_drift` as a subgraph VIEW over the source-subgraph; preserve the public surface (`EdgeType`, `LinkageRecord`, `VertexRef`, `DriftReport`, `detect_drift` signature) with behavior unchanged — no deletions
- `tests/test_ontology_source.py` — **CREATE**: `@covers`-decorated REQ tests including the `detect_drift` golden-fixture parity test (flat convention, mirrors `tests/test_lifecycle.py`)
- `pyproject.toml` — **MODIFY**: add the `tree-sitter` runtime dependency (core + Python grammar) — an **attested STDLIB-FIRST departure** per the parent ADR § Decision (GO-attested Phase-0 airlock-in, 2026-07-02); this deliberately overrides the scaffold's default "New dependencies" deny
- `uv.lock` — **MODIFY**: lock the newly-added `tree-sitter` dependency graph
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md` — parent ADR for intent and scope (reference)
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-07-source-domain-tree-sitter-anchors.md` — this brief (evidence)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/ledger.py`, `src/gzkit/commands/state.py` — the corpus-domain projection + `get_artifact_graph` absorption (OBPI-0.32.0-02); consumed, never edited here
- The net-new L2 event schema and `blocks`/`blocked_by`/`discovered_from`/`validates` events + ready/blocked queue (OBPI-0.32.0-06, the work domain) — this OBPI emits none of them
- `src/gzkit/commands/**`, `src/gzkit/cli/**` — the ontology CLI verb surface (item #3); this OBPI builds no CLI verb and adds no manpage
- The ontology Pydantic model + `src/gzkit/schemas/` ontology schema (OBPI-0.32.0-01) — `OntologyNode`/`OntologyEdge`/`LinkType` are imported, never modified
- `networkx` as a new dependency — item #2 owns the graph-substrate dependency; this OBPI adds only `tree-sitter`
- `src/gzkit/traceability.py` — NOT edited (denied). NOTE (operator-ratified port refactor, 2026-07-06): source anchors are extracted by **structural decorator-walk** inside the `SourceParser` adapters (`ast` walks `decorator_list`; tree-sitter walks `decorator` nodes) — superseding the earlier `find_covers_in_source` reuse. Decorator-walk is strictly more correct for product source (a real decorator is never inside a string, so the GHI #390 masking class does not arise) and lets both adapters agree by construction. `traceability.py` is untouched.
- Deleting or renaming any public name in `src/gzkit/triangle.py` — absorption is a compat view, not a removal
- Any path not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Deliver `src/gzkit/ontology/source.py` — `@covers`/`@surface` source-anchor extraction into source→REQ edges, tree-sitter polyglot code-coupling edges, the `source_anchors.json` query-before-grep index builder, and orphan-gap detection — plus the `triangle.py` `detect_drift` compat view.
2. NEVER: Delete, rename, or change the observable behavior of `triangle.py`'s public surface (`detect_drift`, `EdgeType`, `LinkageRecord`, `VertexRef`, `DriftReport`). `detect_drift` is re-expressed as a subgraph VIEW; for identical inputs it MUST return an equal `DriftReport` (coupled-surface coherence — AGENTS.md § DO IT RIGHT 1a).
3. NEVER: Touch another domain — the corpus projection / `get_artifact_graph` (item #2), the work L2 event schema (item #6), the ontology model/schema (item #1), or any ontology CLI surface (item #3). This OBPI consumes those; it never edits them.
4. ALWAYS: The `source_anchors.json` index is Tier-B derived — regenerable from source, never authoritative, and never consumed as a gate or `gz validate` enforcement input (parent ADR Boundary Invariant #2, derived-never-authority).
5. ALWAYS: The `tree-sitter` dependency is added under the parent ADR's GO-attested STDLIB-FIRST departure (Phase-0 airlock-in, 2026-07-02) — quote that attestation verbatim into `### Implementation Summary`. NEVER add `networkx` here (item #2 owns it).
6. ALWAYS: Reconcile this brief against the parent ADR § Decision (source-domain clause) before implementation; on missing prerequisites, print a BLOCKERS list and halt.
7. ALWAYS: `build_source_anchor_index()` is deterministic — identical source trees yield byte-identical `source_anchors.json` (sorted keys, stable ordering) and the index round-trips through its Pydantic model (`load(dump(x)) == x`). NEVER emit nondeterministic ordering.
8. ALWAYS: source parsing is a `SourceParser` port (`typing.Protocol` returning domain types) with TWO real adapters — `AstSourceParser` (stdlib) and `TreeSitterSourceParser` (polyglot). tree-sitter is confined to `TreeSitterSourceParser` (function-local import) and NEVER crosses the port — adapters return only `SourceAnchor`/`CodeCouplingEdge`, never a parser-native node (hexagonal-architecture.md rules 3/5/6). The core MUST be exercisable via `AstSourceParser` without importing tree-sitter.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the source-domain clause** verbatim into `### Implementation Summary`: "source (tree-sitter code-coupling + @covers/@surface anchors; source->REQ first-class; absorbs triangle.py's edge model and re-expresses detect_drift as a subgraph view)". That clause is the contract.
- [ ] Parent ADR § Intent — the working-in-the-dark failure the source-subgraph images; the substrate-reversal incident that motivates a computed shape.
- [ ] Parent ADR § Decision — the STDLIB-FIRST departure sentence discharging `networkx` + `tree-sitter` (GO-attested Phase-0 airlock-in, 2026-07-02); this OBPI discharges the `tree-sitter` half.
- [ ] Parent ADR § Boundary Invariants #2 (derived-never-authority) and #3 (sense images structure only) — the fences the index and orphan-gap report must honor.

> **STOP:** If you cannot quote the parent ADR § Decision source-domain clause that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `AGENTS.md` § STDLIB-FIRST DOCTRINE — departures are foundation-attested; "popularity" / "hot topic" are named anti-rationales
- [ ] `AGENTS.md` § DO IT RIGHT 1a — coupled-surface coherence (the `detect_drift` consumer check lands in the same commit as the absorption)
- [ ] `.claude/rules/models.md` — Pydantic `frozen=True, extra="forbid"` for the index + edge models

**Context:**

- [ ] Related OBPIs in same ADR — 01 (ontology model), 02 (networkx substrate + corpus projection), 03 (ontology CLI), 06 (work L2 schema)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/ontology/` package exists (created by OBPI-0.32.0-01/02); `source.py` lands beside the model + substrate modules
- [ ] `src/gzkit/triangle.py` exists with `detect_drift`, `EdgeType`, `LinkageRecord`, `DriftReport`
- [ ] `src/gzkit/traceability.py` exists with `find_covers_in_source` / `scan_test_tree` (the `@covers` scanner reused here)
- [ ] `pyproject.toml` and `uv.lock` present and writable (the `tree-sitter` dependency add)

**Existing Code (understand current state):**

- [ ] `src/gzkit/triangle.py` — read `EdgeType` (COVERS/PROVES/JUSTIFIES), `LinkageRecord`, `VertexRef`, and `detect_drift` (pure, `scan_timestamp`-parameterized) before re-expressing it as a view
- [ ] `src/gzkit/traceability.py` — the canonical `@covers` regex + AST scanner (`find_covers_in_source`, `scan_test_tree`); `@surface` scanning is the net-new sibling
- [ ] `tests/test_lifecycle.py` — flat test-file convention and state/drift test shape to mirror
- [ ] Parent ADR § Decision + Boundary Invariants — the derived-never-authority posture the generated index must satisfy

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

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_ontology_source -v

# Behavior-preserved absorption: the legacy drift + coverage surfaces still resolve
uv run gz drift
uv run gz covers

# Specific verification for this OBPI
test -f src/gzkit/ontology/source.py
test -f .gzkit/ontology/source_anchors.json
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Extract @covers/@surface source anchors from product source as first-class edges
uv run python -c "from gzkit.ontology.source import build_source_anchor_index; idx = build_source_anchor_index(); print('source->REQ edges:', len(idx.edges))"

# The generated query-before-grep index — query it instead of grepping the tree
uv run python -c "from gzkit.ontology.source import load_source_anchor_index; idx = load_source_anchor_index(); print('anchors for REQ-0.32.0-07-01:', idx.anchors_for('REQ-0.32.0-07-01'))"
test -f .gzkit/ontology/source_anchors.json

# Orphan-gap detection: every REQ with no covering source anchor
uv run python -c "from gzkit.ontology.source import detect_orphan_gaps; print('REQs with no source anchor:', detect_orphan_gaps().orphan_reqs)"

# Absorption is behavior-preserving: triangle's detect_drift still yields its DriftReport
uv run gz drift
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
@covers test; SUPPORT proves via ledger event + structural validator;
STRUCTURAL-FENCE proves via a parent-ADR ## Boundary Invariants entry.
-->

- [ ] REQ-0.32.0-07-01 [BEHAVIOR]: `@covers(REQ-...)` anchors located in product source under `src/**` (not only `tests/**`) are extracted as first-class source→REQ edges — each edge carries `(source_path, line, req_id)` with a CODE-origin vertex, distinct from the test→spec COVERS edges `triangle.py` already scans; pinned by a `@covers(REQ-0.32.0-07-01)` test in `tests/test_ontology_source.py`.
- [ ] REQ-0.32.0-07-02 [BEHAVIOR]: A `@surface(REQ-...)` anchor is scanned as a lighter, many-to-many cross-REQ layer — a single source unit MAY declare multiple `@surface` REQs, and `@surface` is read without the decoration-time REQ-existence enforcement `@covers` applies — producing surface→REQ edges typed distinctly from the strict binding; pinned by a `@covers(REQ-0.32.0-07-02)` test.
- [ ] REQ-0.32.0-07-03 [BEHAVIOR]: `tree-sitter` parses the source tree (polyglot-capable; the Python grammar exercised at minimum) and builds code-coupling edges (import/definition relationships) between source units — the grammar is actually invoked and the parse tree walked, not merely imported (parent ADR WWHTBT clause (d)); pinned by a `@covers(REQ-0.32.0-07-03)` test asserting a known coupling edge from a fixture.
- [ ] REQ-0.32.0-07-04 [BEHAVIOR]: `build_source_anchor_index()` produces a deterministic, Pydantic-modeled `source_anchors.json` written to `.gzkit/ontology/source_anchors.json` mapping each REQ to its covering source anchors with `file:line` provenance — a query-before-grep index that round-trips through its model (`load(dump(x)) == x`); pinned by a `@covers(REQ-0.32.0-07-04)` test.
- [ ] REQ-0.32.0-07-05 [BEHAVIOR]: Orphan-gap detection deterministically surfaces every REQ with no covering source anchor (and, symmetrically, every source anchor whose REQ id is not a known brief REQ), returned as a sorted report; pinned by a `@covers(REQ-0.32.0-07-05)` test over a fixture with a known gap.
- [ ] REQ-0.32.0-07-06 [BEHAVIOR]: `triangle.py`'s `detect_drift` is re-expressed as a subgraph VIEW over the source-subgraph while its public surface (`detect_drift` signature, `EdgeType`, `LinkageRecord`, `VertexRef`, `DriftReport`) is preserved unchanged — for identical inputs (including `scan_timestamp`) the view returns a `DriftReport` equal to the pre-absorption result; pinned by a golden-fixture parity `@covers(REQ-0.32.0-07-06)` test.
- [ ] REQ-0.32.0-07-07 [SUPPORT]: The `tree-sitter` runtime dependency (core + Python grammar) is added to `pyproject.toml` and locked in `uv.lock` as a STDLIB-FIRST departure attested in the parent ADR § Decision (GO-attested Phase-0 airlock-in, 2026-07-02) quoted verbatim into `### Implementation Summary`; proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing this brief emitted at OBPI completion.
- [ ] REQ-0.32.0-07-08 [BEHAVIOR]: Source parsing is expressed as a `SourceParser` port (`typing.Protocol` returning domain `SourceAnchor`/`CodeCouplingEdge` models) fulfilled by TWO real adapters — `AstSourceParser` (stdlib `ast`, Python-only, the STDLIB-FIRST default) and `TreeSitterSourceParser` (the polyglot departure). The core (`build_source_anchor_index`, `detect_orphan_gaps`) depends on the port by injection and runs on the `ast` adapter without importing tree-sitter (rule 6); a port-contract test asserts both adapters produce identical anchors and coupling on a Python fixture (operator-ratified port refactor, 2026-07-06); pinned by a `@covers(REQ-0.32.0-07-08)` test.

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


Port interchangeability across the full src tree (REQ-08):

$ uv run python -c "from gzkit.ontology.source import build_source_anchor_index as b, AstSourceParser, TreeSitterSourceParser; a=b(parser=AstSourceParser(),write=False); t=b(parser=TreeSitterSourceParser(),write=False); print('anchors',a.anchors==t.anchors,'coupling',a.coupling_edges==t.coupling_edges,'n',len(t.coupling_edges))"
anchors True coupling True n 3947

The stdlib and tree-sitter adapters produce byte-identical domain output over the entire src/** tree — the port is a real seam, not a facade. REQ-03 definition coupling: `from b import helper` (helper defined in b.py) yields a uses_definition edge c.py->b.py symbol=helper. rule 6: build_source_anchor_index(parser=AstSourceParser()) runs with `import tree_sitter` blocked. Full suite: Ran 6788 tests in ~92s, OK — receipt arb-step-unittest-a35bb141b207490d96f61a14a7bb0cde (exit_status=0). Both adversaries NOT-REFUTED; negative controls (break _walk_definitions / AstSourceParser.coupling) turned the port-contract test RED then restored green.

### Implementation Summary


- Files created: `src/gzkit/ontology/source.py` (SourceParser Protocol port + AstSourceParser/TreeSitterSourceParser adapters; @covers/@surface structural decorator-walk; import+definition coupling resolved between source units; deterministic source_anchors.json build/load; orphan-gap detection; triangle edge-model absorption). `tests/test_ontology_source.py` (11 @covers tests incl. REQ-08 port-contract equivalence). `.gzkit/ontology/source_anchors.json` (Tier-B derived index, 3947 coupling edges).
- Files modified: `src/gzkit/triangle.py` (detect_drift re-expressed as a SourceSubgraphView subgraph view; public surface — detect_drift signature, EdgeType, LinkageRecord, VertexRef, DriftReport — preserved unchanged). `pyproject.toml` + `uv.lock` (tree-sitter + tree-sitter-python added). Brief (REQ-08, FAIL-CLOSED requirement 8, req_atomic, model.py declared consumed).
- Parent ADR Decision (verbatim): "source (tree-sitter code-coupling + @covers/@surface anchors; source->REQ first-class; absorbs triangle.py's edge model and re-expresses detect_drift as a subgraph view)". STDLIB-FIRST departure GO-attested Phase-0 airlock-in, 2026-07-02: tree-sitter supplies deterministic multi-surface (polyglot) parsing stdlib ast (Python-only) cannot.
- Hexagonal: source parsing is a SourceParser port fulfilled by two real adapters; tree-sitter confined function-local to TreeSitterSourceParser; core exercisable via AstSourceParser without importing tree-sitter (rule 6); adapters byte-identical across the full src tree.
- Tests added: 11 scoped (REQ-01..06 + REQ-08 BEHAVIOR; REQ-07 SUPPORT proves via ledger+validator).
- Date completed: 2026-07-06.
- Attestation status: operator-attested (g0, "attest completed").
- Defects noted: pre-existing Windows-backslash paths in historical artifact_edited ledger entries (out-of-scope; Stage-5 GHI candidate).

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy-lane OBPI-0.32.0-07 source domain built as a SourceParser hexagonal port with two interchangeable adapters (AstSourceParser stdlib + TreeSitterSourceParser polyglot), proven byte-identical across the full src tree (3947 coupling edges; anchors+coupling equal). 8 REQs covered (11 scoped tests), full suite 6788/6788 green (receipt arb-step-unittest-a35bb141b207490d96f61a14a7bb0cde), lint clean (arb-ruff-6cdc178aad0f49f99695c7073f48e78e), typecheck clean (arb-step-typecheck-05c4cdd55d5d48a18e85bb9daccbe3ab), mkdocs --strict clean (arb-step-mkdocs-2ae5dc67a7fc46bc9560e32ff1b54c5e). REQ-03 import+definition coupling between source units and REQ-08 port contract independently validated by two adversaries (Codex + independent Claude, both NOT-REFUTED with fired negative controls); the Codex-caught REQ-03 semantic gap and the operator-directed port refactor were both corrected in flight. tree-sitter confirmed GO-attested against canon (not paraphrase). Precomplete 8/8 READY.
- Date: 2026-07-07

---

**Date Completed:** 2026-07-07

**Evidence Hash:** -
