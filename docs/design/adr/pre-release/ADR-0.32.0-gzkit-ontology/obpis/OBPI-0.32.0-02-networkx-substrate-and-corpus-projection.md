---
id: OBPI-0.32.0-02-networkx-substrate-and-corpus-projection
parent: ADR-0.32.0-gzkit-ontology
item: 2
lane: Heavy
sensitivity: security
status: Draft
---

# OBPI-0.32.0-02-networkx-substrate-and-corpus-projection: Networkx Substrate And Corpus Projection

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- **Checklist Item:** #2 - "networkx MultiDiGraph substrate + corpus-domain projection absorbing ledger.get_artifact_graph as a typed view over one replay path; rebuild-fidelity self-report (replay completeness + freshness); Tier-B rebuild-only guardrail. [MVP spine]"

**Status:** Draft

## Objective

Stand up the networkx `MultiDiGraph` substrate (`src/gzkit/ontology/graph.py`)
and the corpus-domain projection (`src/gzkit/ontology/corpus.py`) that lifts
`ledger.get_artifact_graph()` into typed `OntologyNode`/`OntologyEdge` over a
single replay path — surfacing supersedes/attests/validates as first-class edges,
emitting a rebuild-fidelity self-report (replay completeness + freshness) that
confesses a stale or incomplete replay, and holding a Tier-B rebuild-only
guardrail — as the MVP spine every later ontology domain and the gz ontology
CLI (OBPI-03) reads.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds a new importable runtime surface (`gzkit.ontology.graph`,
`gzkit.ontology.corpus`) that OBPI-03's gz ontology CLI binds against, and it
adds a new **runtime dependency** (`networkx`) to `pyproject.toml` — a
dependency/runtime-contract change that the STDLIB-FIRST doctrine requires be
foundation-attested (discharged by the parent ADR § Decision).

**Security sensitivity (`sensitivity: security`).** The Allowed Paths touch
`src/gzkit/ledger.py`, a registered `ledger_integrity` surface (gzkit's
append-only system-of-record). The touch here is **read-side only** — a compat
view over `get_artifact_graph`, no new write path — but the auto-detect floor is
path-mechanical (`.gzkit/rules/security-sensitivity.md` §§ 1-2, escalate-not-escape):
an omitted declaration over a registered overlap fails closed. This declaration
is the mandated escalation, not net-new ledger-write security work.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/ontology/graph.py` — **CREATE**: networkx `MultiDiGraph` wrapper holding OBPI-01's Pydantic `OntologyNode`/`OntologyEdge`; parallel-edge (multigraph) retention + `reachable_from` lateral/reachability traversal.
- `src/gzkit/ontology/corpus.py` — **CREATE**: the corpus-domain projection that lifts `ledger.get_artifact_graph()` into typed `OntologyNode`/`OntologyEdge` over ONE replay path, surfaces supersedes/attests/validates as first-class `OntologyEdge`, and emits the rebuild-fidelity self-report.
- `src/gzkit/ledger.py` — light **read-side** extension only: expose/adapt `get_artifact_graph` as the SINGLE replay source the projection consumes (compat view). NO second replay, NO new L2 event type, NO write-path change.
- `pyproject.toml` — add the `networkx` runtime dependency (the ADR's attested STDLIB-FIRST departure; § Decision, GO-attested Phase-0 airlock-in 2026-07-02). Overrides the scaffold's default "New dependencies" deny.
- `uv.lock` — lock the `networkx` resolution for reproducible delivery (`gz validate --distribution`).
- `tests/test_ontology_graph.py` — **CREATE**: `@covers`-decorated REQ tests for the MultiDiGraph substrate.
- `tests/test_ontology_corpus.py` — **CREATE**: `@covers`-decorated REQ tests for the corpus projection, absorption parity, single-replay, and the fidelity self-report.
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-02-networkx-substrate-and-corpus-projection.md` — this brief (evidence).

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/cli/**`, `src/gzkit/commands/state.py`, `docs/user/manpages/**` — the gz ontology CLI namespace (sense / trace / resense / seams / reach) and the `commands/state.py` L3-render extension are OBPI-03, not this brief.
- `src/gzkit/events.py`, `src/gzkit/ledger_events.py`, `src/gzkit/schemas/*.json` — the net-new L2 work-domain event schema (blocks/blocked_by/discovered_from/validates) is OBPI-06 (the one-way door); this brief emits NO new ledger event type.
- `src/gzkit/triangle.py`, `src/gzkit/ontology/source*.py` — tree-sitter code-coupling + `@covers`/`@surface` anchors + `detect_drift` subgraph are the source domain (OBPI-07).
- `src/gzkit/ontology/model.py` and the ontology JSON schema under `src/gzkit/schemas/` — OBPI-01 owns the model + schema; this brief consumes them read-only and never edits them.
- New runtime dependencies **other than** `networkx` — tree-sitter lands with the source domain (OBPI-07); no other dependency is added here.
- Any path not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Deliver the networkx `MultiDiGraph` substrate + corpus projection that lifts `ledger.get_artifact_graph()` into typed `OntologyNode`/`OntologyEdge` over ONE replay path, with supersedes/attests/validates surfaced as first-class edges and a rebuild-fidelity self-report.
2. ALWAYS: Keep `ledger.get_artifact_graph()` the SINGLE replay source — the projection reads it and opens no second ledger replay; every node and edge it yields is preserved through the absorption (compat view, not a fork).
3. ALWAYS: The graph self-reports rebuild fidelity (replay completeness + freshness) and confesses an incomplete or stale replay — the runtime realization of parent ADR Boundary Invariant #1. Completeness is computed by diffing replayed event types against the LIVE `TypedLedgerEvent` discriminator registry, NEVER a hardcoded handled-type set; this fence is the breadth-gate the deferred domains (OBPI-05/06/07) wait behind (§ Target Scope).
4. NEVER: Let the ontology graph gate, or be read as authoritative proof by any `gz validate` scope, gate, or closeout step — it is Tier-B derived-never-authority (parent ADR Boundary Invariant #2); writeback reaches it only by rebuild, never by direct edit.
5. NEVER: Add a new L2 ledger event type, the gz ontology CLI surface, or tree-sitter/source-domain code — those are OBPI-06, OBPI-03, and OBPI-07 respectively.
6. ALWAYS: Add `networkx` as the attested STDLIB-FIRST departure (ADR § Decision, GO-attested Phase-0 airlock-in 2026-07-02) — declared in `pyproject.toml` and locked in `uv.lock`; no other new runtime dependency.
7. ALWAYS: Reconcile this brief against the parent ADR § Decision and § Boundary Invariants before implementation; quote the Decision line into Implementation Summary.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote Checklist item #2 + the substrate paragraph** ("Pydantic models carry the typed Objects/Links … held in a networkx MultiDiGraph"; "corpus … absorbs get_artifact_graph as a typed view over one replay path") verbatim into Implementation Summary. The Decision line is the contract.
- [ ] Parent ADR § Boundary Invariants #1 (rebuild fidelity — the load-bearing fence) and #2 (derived-never-authority) — the fences REQ-05 realizes and REQ-06 anchors to.
- [ ] Parent ADR § Intent — the "working in the dark" / silent-reversal why-frame.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` / `CLAUDE.md` - agent operating contract + REQ-kind discipline (ADR-0.0.59)
- [ ] `.claude/rules/security-sensitivity.md` - the `src/gzkit/ledger.py` overlap that pins `sensitivity: security`
- [ ] `.claude/rules/models.md` - Pydantic `frozen=True, extra="forbid"` policy for the `OntologyNode`/`OntologyEdge` this substrate holds

**Context:**

- [ ] OBPI-0.32.0-01 (Pydantic ontology model: `OntologyNode`/`OntologyEdge`/`LinkType` + schema) — the typed carriers this substrate holds
- [ ] Sibling OBPIs 03 (CLI), 06 (work-domain L2 schema), 07 (source domain) — all denied here

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/ontology/model.py` (`OntologyNode`/`OntologyEdge`/`LinkType`) delivered by OBPI-0.32.0-01 — the typed carriers the graph holds
- [ ] `src/gzkit/ledger.py::Ledger.get_artifact_graph` present — the single replay source to absorb
- [ ] `networkx` resolvable on PyPI for the pinned Python (`>=3.13`) before it is added to `pyproject.toml`
- [ ] Parent ADR present and registered in `gz state`

**Existing Code (understand current state):**

- [ ] `src/gzkit/ledger.py::Ledger.get_artifact_graph` (~line 776) — returns `dict[str, dict[str, Any]]`; nodes carry `type`/`parent`/`children`/`attested` plus supersede/attest/validate metadata applied by `_apply_graph_event_metadata`
- [ ] `src/gzkit/commands/state.py::state` — the current L3 dict consumer whose behavior the projection must not break (compat)
- [ ] `src/gzkit/req_kind.py` — `enum.StrEnum` + frozen Pydantic precedent for the typed model shape
- [ ] `.claude/rules/pythonic.md` — module/function size limits and top-level-import policy for the two new modules

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

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

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
uv run gz validate --sensitivity
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_ontology_graph -v
uv run -m unittest tests.test_ontology_corpus -v
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. `--help` is not a demo. -->

```bash
# The corpus projection lifts ledger.get_artifact_graph() into a typed OntologyGraph over ONE replay path
uv run python -c "from gzkit.ontology.corpus import project_corpus; p = project_corpus(); print('nodes', p.graph.node_count(), 'edges', p.graph.edge_count())"

# Absorption parity: every node get_artifact_graph yields is present as a typed OntologyNode
uv run python -c "from gzkit.ontology.corpus import project_corpus; p = project_corpus(); print('node parity', set(p.graph.node_ids()) == set(p.source_graph))"

# supersedes / attests / validates surface as first-class typed edges (typed LinkType, not node-dict metadata)
uv run python -c "from gzkit.ontology.corpus import project_corpus; print(sorted({e.link_type.value for e in project_corpus().graph.edges()}))"

# The graph self-reports rebuild fidelity (replay completeness + freshness) — it can confess a stale/incomplete replay
uv run python -c "from gzkit.ontology.corpus import project_corpus; f = project_corpus().fidelity; print('complete', f.complete, 'fresh', f.fresh, 'unaccounted', f.unaccounted_event_types)"

# networkx multigraph is genuinely exercised: lateral reachability from an ADR across its lineage
uv run python -c "from gzkit.ontology.corpus import project_corpus; print(sorted(project_corpus().graph.reachable_from('ADR-0.31.0-obpi-state-machine'))[:5])"
```

## Acceptance Criteria

<!-- Each REQ carries exactly one [kind] tag (ADR-0.0.59): BEHAVIOR proves via a
     @covers test; SUPPORT via a ledger event + structural validator; and
     STRUCTURAL-FENCE via the parent ADR ## Boundary Invariants entry. -->

- [ ] REQ-0.32.0-02-01 [BEHAVIOR]: `gzkit.ontology.graph.OntologyGraph` wraps a `networkx.MultiDiGraph` holding OBPI-01's Pydantic `OntologyNode`/`OntologyEdge`, and genuinely exercises the multigraph engine — two edges of different `LinkType` between the same node pair are BOTH retained (parallel edges), and `reachable_from(node_id)` returns the transitive-descendant set via networkx traversal; pinned by a `@covers(REQ-0.32.0-02-01)` test in `tests/test_ontology_graph.py`.
- [ ] REQ-0.32.0-02-02 [BEHAVIOR]: the corpus projection reproduces, as typed `OntologyNode`/`OntologyEdge`, every node AND every parent→child lineage edge that `ledger.get_artifact_graph()` yields for the same ledger — the node-id set and the parent/child edge set are identical (behavior preserved through the absorption, not a re-derivation); pinned by a `@covers(REQ-0.32.0-02-02)` parity test in `tests/test_ontology_corpus.py`.
- [ ] REQ-0.32.0-02-03 [BEHAVIOR]: the supersedes, attests, and validates relationships already carried in `get_artifact_graph` node metadata are lifted into first-class typed `OntologyEdge` instances with distinct `LinkType` values (not left implicit inside node dicts); a `@covers(REQ-0.32.0-02-03)` test asserts each such relationship present in the ledger metadata appears as its typed edge in `tests/test_ontology_corpus.py`.
- [ ] REQ-0.32.0-02-04 [BEHAVIOR]: the corpus projection derives its shape from exactly ONE replay path — it consumes `ledger.get_artifact_graph()` as its sole source and performs no independent `read_all()` / event re-scan of its own; a `@covers(REQ-0.32.0-02-04)` test proves `get_artifact_graph` is the only replay entrypoint invoked (e.g. a spy on `Ledger.read_all` records the single call routed through `get_artifact_graph`) in `tests/test_ontology_corpus.py`.
- [ ] REQ-0.32.0-02-05 [BEHAVIOR]: the projection emits a rebuild-fidelity self-report whose replay completeness is computed by DIFFING the replayed event types against the LIVE `TypedLedgerEvent` discriminator registry (`gzkit.events`) — NEVER a hardcoded handled-type set — so a discriminator present in the registry but unhandled by the projection is named `unaccounted` and drives `complete=False`; plus freshness (latest ledger event timestamp vs projection build time) driving `fresh=False`. A `@covers(REQ-0.32.0-02-05)` test DERIVES an unhandled discriminator from the live `TypedLedgerEvent` union (not a fixture literal) and asserts `complete=False`, asserts a stale build reports `fresh=False`, and asserts that when every registry discriminator is handled the report reads `complete=True` — so the test FAILS the moment a newly-registered event type is left unhandled (the runtime realization of parent ADR Boundary Invariant #1, registry-coupled), in `tests/test_ontology_corpus.py`.
- [ ] REQ-0.32.0-02-06 [STRUCTURAL-FENCE]: the ontology graph is Tier-B derived-never-authority — it NEVER gates, no `gz validate` scope / gate / closeout step reads it as authoritative proof, and writeback reaches it only by rebuild, never by direct edit; anchored in the parent ADR `## Boundary Invariants` entry #2 (derived-never-authority), audited at ADR closeout.
- [ ] REQ-0.32.0-02-07 [SUPPORT]: the `networkx` runtime dependency is declared in `pyproject.toml` `[project].dependencies` and locked in `uv.lock` as the ADR's attested STDLIB-FIRST departure (§ Decision, GO-attested Phase-0 airlock-in 2026-07-02: multigraph + lateral/reachability traversal `graphlib` cannot supply) — proven by `uv run gz validate --documents` passing AND an `artifact_edited` ledger event citing `pyproject.toml` emitted at OBPI completion.

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
