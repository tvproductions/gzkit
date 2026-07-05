---
id: OBPI-0.32.0-06-work-domain-l2-schema-and-queue
parent: ADR-0.32.0-gzkit-ontology
item: 6
lane: Heavy
status: Draft
---

# OBPI-0.32.0-06-work-domain-l2-schema-and-queue: Work Domain L2 Schema And Queue

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- **Checklist Item:** #6 - "work domain: net-new L2 event schema (blocks/blocked_by/discovered_from/validates) + ready/blocked queue + advisory-first blocks with a declared fail-closed torque-up milestone; gated last on its own WWHTBT of the edge set (the one-way door)."

**Status:** Draft

## Objective

Lay the ontology's **work domain**: add the four net-new L2 edge event types
(`blocks`, `blocked_by`, `discovered_from`, `validates`) **additively** to the
ledger event schema, replay a `ready`/`blocked` TASK queue purely from those
edges, and **surface every unsatisfied block advisory-first — never
hard-refusing** — with the hard-refusal end-state declared as a promotable
future *torque-up* milestone and the exact edge vocabulary **frozen by a WWHTBT
pass before any event is emitted**, because L2 is append-only and this is the
ADR's one true one-way door (§ Consequences, Negative #4).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

Heavy because it adds four **permanent, append-only** L2 ledger event contracts
(the `TypedLedgerEvent` discriminated union) plus a committed JSON-schema
projection under `src/gzkit/schemas/` and a new importable runtime surface
(`gzkit.ontology.work`). The edge vocabulary is an irreversible external
contract once emitted — the highest-scrutiny surface in ADR-0.32.0.

> **Sensitivity: not declared (absent).** `gz validate --sensitivity` scopes the
> auto-detect floor to *Allowed-Paths overlap with a registered security
> surface* in `data/security_surfaces.json`. This brief's Allowed Paths
> (`src/gzkit/events.py`, `src/gzkit/schemas/work_edges.json`,
> `src/gzkit/ontology/work.py`, `tests/`) overlap **no** registered glob — the
> `ledger_integrity` category registers `src/gzkit/ledger.py`,
> `ledger_events.py`, `ledger_proof.py`, `ledger_semantics.py`, none of which is
> `events.py`, and this OBPI does **not** touch `src/gzkit/ledger.py`. The floor
> does not fire; escalation remains available if the operator wants the extended
> Gate-5 security walkthrough for the one-way-door schema.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/events.py` — **EDIT (additive only)**: add `BlocksEvent`, `BlockedByEvent`, `DiscoveredFromEvent`, `ValidatesEvent` (each a frozen `extra="forbid"` `_EventBase` subclass with a unique `event: Literal[...]` discriminator + typed endpoint fields) and join them into the `TypedLedgerEvent` union. Do NOT alter, rename, or re-semantic any existing event type.
- `src/gzkit/schemas/work_edges.json` — **CREATE**: committed JSON-schema projection of the four net-new edge event types (drop-in, loaded via `gzkit.schemas.load_schema("work_edges")`).
- `src/gzkit/ontology/work.py` — **CREATE**: TASK nodes + `ready`/`blocked` queue replayed from the four L2 edges + advisory-first surfacing (block provenance) + the additive edge structural validator + the schema projector `work_edge_json_schema()` + the declared `TORQUE_UP_MILESTONE` doctrine constant.
- `src/gzkit/ontology/__init__.py` — **CREATE**: package marker for the `ontology` package (docstring-only; no logic). Idempotent — a no-op if OBPI-0.32.0-01/02 already introduced the package.
- `tests/test_ontology_work.py` — **CREATE**: `@covers`-decorated REQ tests (flat convention, mirrors `tests/test_obpi_state_machine.py`).
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-06-work-domain-l2-schema-and-queue.md` — this brief (evidence).

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- **Existing event-type semantics in `src/gzkit/events.py`** — every pre-existing `_EventBase` subclass, discriminator literal, and field is UNTOUCHED. The four types are additive; parse-compatibility is pinned by REQ-06.
- `src/gzkit/ledger.py`, `src/gzkit/ledger_events.py`, `src/gzkit/ledger_proof.py`, `src/gzkit/ledger_semantics.py` — the append-only ledger writers/proof helpers; not edited here.
- **Corpus domain** (`ledger.get_artifact_graph` / corpus projection — OBPI-0.32.0-02) and **source domain** (tree-sitter anchors — OBPI-0.32.0-07).
- The **`ontology` CLI verb family** (`sense`/`trace`/`resense`/`seams`/`reach`) — that is OBPI-0.32.0-03; this OBPI adds NO new CLI verb and NO new `gz validate` scope.
- The parent ADR body — this OBPI anchors its STRUCTURAL-FENCE (REQ-05) to an **existing** Boundary Invariant (#2); no ADR edit.
- New third-party dependencies, CI files, lockfiles.
- Any path not listed in Allowed Paths.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI delivers the work-domain L2 edge schema (four net-new event types), the `ready`/`blocked` queue replayed from those edges, advisory-first block surfacing, and a declared fail-closed torque-up milestone — all within the Allowed Paths declared above.
2. NEVER: Emit any of the four L2 edge event types (`blocks`, `blocked_by`, `discovered_from`, `validates`) to the ledger until the **WWHTBT pass over the EXACT edge set is recorded**. L2 is append-only — the edge vocabulary is permanent and irreversible once emitted; a wrong or premature edge set cannot be retracted, only shadowed (parent ADR § Consequences, Negative #4 — "the one true one-way door"). The edge vocabulary is finalized via that WWHTBT pass BEFORE emission, not after.
3. NEVER: Alter, rename, or re-semantic any existing event type in `src/gzkit/events.py`. The four types are ADDED additively and joined into `TypedLedgerEvent`; existing discriminators and fields stay byte-identical (round-trip regression pinned by REQ-06).
4. ALWAYS: Keep the work-domain queue **derived-never-authority — advisory-only**. The queue SURFACES every unsatisfied block but NEVER hard-refuses, gates a `gz validate` scope, raises on a block, or blocks a closeout in this OBPI. The hard-refusal end-state is a DECLARED future *torque-up* milestone, not shipped here (parent ADR § Boundary Invariants #2).
5. ALWAYS: Keep the committed `src/gzkit/schemas/work_edges.json` byte-coherent with the model projection (`work_edge_json_schema()`), so the emitted edge vocabulary cannot silently drift from the WWHTBT-finalized set.
6. NEVER: Mark this OBPI accepted while scaffold defaults remain in the brief, or without explicit human attestation (Heavy lane; ADR-0.0.36 universal Gate 5).
7. ALWAYS: Reconcile this brief against the parent ADR § Decision (checklist item #6), § Consequences Negative #4, and § Boundary Invariants #2 before implementation; quote the Decision item into `### Implementation Summary`.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote checklist item #6 verbatim** into `### Implementation Summary`: "work domain (TASK nodes + ready/blocked queue over a net-new L2 event schema: blocks/blocked_by/discovered_from/validates; advisory-first with a declared fail-closed torque-up milestone)". The Decision item is the contract.
- [ ] **Parent ADR § Consequences, Negative #4** — the one-way-door consequence: "L2 is append-only, so blocks/blocked_by/discovered_from/validates events are permanent once emitted ... the work OBPI is gated last on its own WWHTBT of the exact edge set." This is the load-bearing frame for REQ-07 + Requirement #2.
- [ ] **Parent ADR § Boundary Invariants #2** (Derived-never-authority) — the STRUCTURAL-FENCE anchor for REQ-05.
- [ ] Parent ADR § Intent — the working-in-the-dark why-frame.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.claude/rules/tests.md` § REQ Scope Discipline — the BEHAVIOR / SUPPORT / STRUCTURAL-FENCE proof-channel matrix (ADR-0.0.59) each REQ below is tagged against.
- [ ] `.claude/rules/security-sensitivity.md` + `data/security_surfaces.json` — confirms `events.py` is not a registered surface (see Lane note).
- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract.

**Context:**

- [ ] Gold-standard exemplar: `docs/design/adr/pre-release/ADR-0.31.0-obpi-state-machine/obpis/OBPI-0.31.0-01-state-transition-models.md` — additive-model + committed-schema + schema-coherence shape this brief mirrors.
- [ ] Sibling OBPIs in ADR-0.32.0 (01 model/purity, 02 substrate/corpus, 03 interface).

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/events.py` exists with `_EventBase`, `TypedLedgerEvent`, and `parse_typed_event` — the additive extension point.
- [ ] `src/gzkit/schemas/` exists with `load_schema`/`get_schema_path` — the new schema lands here.
- [ ] Parent ADR present and registered in `gz state`.

**Existing Code (read; do NOT modify — establishes what is extended additively):**

- [ ] `src/gzkit/events.py` — the ~45 existing `_EventBase` subclasses, the `TypedLedgerEvent` `Annotated[... , Field(discriminator="event")]` union, and `parse_typed_event`; today only `parent` edges exist on `_EventBase`.
- [ ] `src/gzkit/schemas/obpi_state_machine.json` + `obpi_state_machine.py` — the committed-schema ↔ model-projection coherence pattern (REQ-05/REQ-01 of OBPI-0.31.0-01) this OBPI's schema drift-fence mirrors.
- [ ] `src/gzkit/schemas/__init__.py` — `load_schema(name)` drop-in loader.

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
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_ontology_work -v

# Specific verification for this OBPI
test -f src/gzkit/ontology/work.py
test -f src/gzkit/schemas/work_edges.json
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# The four net-new L2 edge event types are members of the typed ledger union
uv run python -c "from gzkit.events import BlocksEvent, BlockedByEvent, DiscoveredFromEvent, ValidatesEvent; print([e.__name__ for e in (BlocksEvent, BlockedByEvent, DiscoveredFromEvent, ValidatesEvent)])"

# Every existing event type still parses unchanged (additive-not-mutative)
uv run python -c "from gzkit.events import parse_typed_event; print(parse_typed_event({'schema': 'gzkit/ledger@1', 'event': 'project_init', 'id': 'x', 'ts': 't', 'mode': 'lite'}).event)"

# The ready/blocked queue replayed purely from L2 edges
uv run python -c "from gzkit.ontology.work import replay_work_queue; q = replay_work_queue(); print('ready:', len(q.ready), 'blocked:', len(q.blocked))"

# Advisory-first: every unsatisfied block is surfaced with provenance, and the
# call returns normally — the block is reported, never hard-refused
uv run python -c "from gzkit.ontology.work import replay_work_queue; q = replay_work_queue(); [print('BLOCKED', t.id, 'by', t.blockers) for t in q.blocked]"

# Committed edge schema equals the model projection (drift fail-close)
uv run python -c "from gzkit.schemas import load_schema; from gzkit.ontology.work import work_edge_json_schema; print('schema coherent:', load_schema('work_edges') == work_edge_json_schema())"

# The torque-up milestone is DECLARED (a future hard-refusal gate), not shipped
uv run python -c "from gzkit.ontology.work import TORQUE_UP_MILESTONE; print(TORQUE_UP_MILESTONE.enforced, '-', TORQUE_UP_MILESTONE.summary)"
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID + exactly one [kind] tag
(ADR-0.0.59): BEHAVIOR (@covers test), SUPPORT (ledger event + structural
validator), STRUCTURAL-FENCE (parent-ADR ## Boundary Invariants entry).
-->

- [ ] REQ-0.32.0-06-01 [SUPPORT]: The four net-new L2 edge event types — `BlocksEvent`/`blocks`, `BlockedByEvent`/`blocked_by`, `DiscoveredFromEvent`/`discovered_from`, `ValidatesEvent`/`validates` — are added ADDITIVELY to `src/gzkit/events.py` (each a frozen `extra="forbid"` `_EventBase` subclass with a unique `event: Literal[...]` discriminator + typed endpoint fields, joined into `TypedLedgerEvent`) with a committed `src/gzkit/schemas/work_edges.json` projection, and the additive edge structural validator in `gzkit.ontology.work` admits their shape. Proven by `uv run gz validate --documents` passing (structural validator admits the brief + schema shape) AND an `artifact_edited` ledger event citing this brief file emitted at OBPI completion.
- [ ] REQ-0.32.0-06-02 [BEHAVIOR]: `gzkit.ontology.work` replays a `ready`/`blocked` TASK queue **purely** from the four L2 edge events — a TASK partitions to `ready` when it has zero unsatisfied blocking edges (`blocked_by`/`blocks`) and to `blocked` otherwise; the partition is a deterministic rebuild over L2 (no L1/frontmatter read, no direct-edit state). Pinned by a `@covers(REQ-0.32.0-06-02)` table-driven test in `tests/test_ontology_work.py` over edge fixtures.
- [ ] REQ-0.32.0-06-03 [BEHAVIOR]: Advisory-first — given a TASK with an unsatisfied block, when the queue is replayed, then the TASK appears in the `blocked` partition **with its blocking edge(s) surfaced as provenance** AND the computation returns normally (no exception raised, no non-zero gate). Pinned by a `@covers(REQ-0.32.0-06-03)` test asserting the block is reported (present with its blocker) and that no gating error is raised — the block is surfaced, never a hard refusal.
- [ ] REQ-0.32.0-06-04 [SUPPORT]: The fail-closed **torque-up milestone** — the FUTURE hard-block-refusal end-state where an unsatisfied block gates work — is DECLARED (not implemented) as a promotable future gate via the `TORQUE_UP_MILESTONE` doctrine constant in `gzkit.ontology.work` (marked `enforced=False`) and in this brief; the shipped release is advisory-first only. Proven by `uv run gz validate --documents` passing (structural validator admits the declaration's shape in this brief) AND an `artifact_edited` ledger event citing this brief file emitted at OBPI completion.
- [ ] REQ-0.32.0-06-05 [STRUCTURAL-FENCE]: The work-domain `ready`/`blocked` queue is a Tier-B **derived-never-authority** projection — advisory-only; it NEVER gates, and no `gz validate` scope, gate, or closeout step consumes the queue as enforcement evidence; the work module adds no `gz` verb or `gz validate` scope. Anchored in the parent ADR `## Boundary Invariants` #2 (Derived-never-authority), audited at ADR closeout.
- [ ] REQ-0.32.0-06-06 [BEHAVIOR]: Additive-not-mutative — after the four types are added, every pre-existing event type STILL parses unchanged through `parse_typed_event` (no discriminator collision, no altered existing field/semantic), and each of the four new types round-trips (`parse_typed_event(model.model_dump()).event == model.event`). Pinned by a `@covers(REQ-0.32.0-06-06)` regression test asserting a representative pre-existing type parses identically AND the four new types round-trip.
- [ ] REQ-0.32.0-06-07 [SUPPORT]: The exact edge vocabulary `{blocks, blocked_by, discovered_from, validates}` is FINALIZED via a recorded WWHTBT pass BEFORE any of the four event types is emitted to the ledger — because L2 is append-only and the edge set is permanent/irreversible once emitted (the one true one-way door). The committed schema's discriminator set equals the WWHTBT-finalized vocabulary (drift fail-close, Requirement #5). Proven by `uv run gz validate --documents` passing (structural validator admits the WWHTBT record captured in `### Implementation Summary`) AND an `artifact_edited` ledger event citing this brief file emitted at OBPI completion.

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

Before: gzkit has no typed notion of *work coupling*. TASK lineage exists only
as `task_started`/`task_blocked`/`task_completed` worklog events (a per-TASK
status stream), with no edge vocabulary expressing that one unit *blocks*
another, was *discovered from* another, or *validates* another — so "what is
ready to work vs. blocked, and why" cannot be replayed from the ledger; it is
reasoned in the dark from stale docs. After: four net-new append-only L2 edge
types (`blocks`/`blocked_by`/`discovered_from`/`validates`) give work coupling a
typed, permanent home, and `gzkit.ontology.work` replays a `ready`/`blocked`
queue from those edges — **advisory-first**: every unsatisfied block is surfaced
with provenance, none hard-refuses, and the hard-refusal *torque-up* end-state
is declared as a promotable future gate. Because L2 is append-only, the edge set
is the ADR's one true one-way door — frozen by a WWHTBT pass before the first
event is ever emitted.

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

Intended proof (fill with observed output at completion):
`uv run python -c "from gzkit.ontology.work import replay_work_queue; q = replay_work_queue(); print('ready:', len(q.ready), 'blocked:', len(q.blocked))"`
— demonstrates the ready/blocked partition replayed purely from the four L2 edge
events, returning normally with blocks surfaced (never refused).

### Implementation Summary

<!-- Quote parent ADR § Decision checklist item #6 verbatim here, plus the
     recorded WWHTBT pass over the exact edge set (REQ-07). -->

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
