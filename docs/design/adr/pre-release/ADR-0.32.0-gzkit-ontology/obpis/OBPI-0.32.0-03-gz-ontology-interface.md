---
id: OBPI-0.32.0-03-gz-ontology-interface
parent: ADR-0.32.0-gzkit-ontology
item: 3
lane: Heavy
status: Draft
req_atomic:
  - REQ-0.32.0-03-01  # `sense` shape-sweep verb — one indivisible command + its @covers test.
  - REQ-0.32.0-03-02  # `trace <id>` lineage verb with edge provenance — one indivisible command + its @covers test.
  - REQ-0.32.0-03-03  # `resense` diff-vs-last-sweep verb — one indivisible command + its @covers test.
  - REQ-0.32.0-03-04  # `seams` fast contacts-only verb — one indivisible command + its @covers test.
  - REQ-0.32.0-03-05  # `reach <id>` blast-radius verb — one indivisible command + its @covers test.
  - REQ-0.32.0-03-06  # `--json` / `--dot` output + rebuild-fidelity self-report — one indivisible render surface + its @covers test.
  - REQ-0.32.0-03-07  # STRUCTURAL-FENCE (structural-only labeling) — a constraint audited via parent-ADR Boundary Invariant #3, not subdividable labor.
  - REQ-0.32.0-03-08  # STRUCTURAL-FENCE (read-only, never writes graph state) — a constraint audited via parent-ADR Boundary Invariant #2.
  - REQ-0.32.0-03-09  # SUPPORT (manpage + cli-audit + behave smoke) — one indivisible docs/coverage authoring unit.
---

# OBPI-0.32.0-03-gz-ontology-interface: Gz Ontology Interface

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`
- **Checklist Item:** #3 - "gz ontology interface -- sense (structural-shape sweep + labeled structural seams), trace <id> (vertical lineage + lateral proof + edge provenance), resense (diff vs last sweep), seams, reach; --json/--dot; extends commands/state.py L3 render + manpage + cli-audit + behave smoke. [MVP spine]"

**Status:** Draft

## Objective

Ship the operator-facing gz ontology verb group — a read-only sonar over the
corpus-domain projection (OBPI-02) — so an operator can image the current
governance shape (`sense`), walk one node's vertical + lateral lineage with edge
provenance (`trace <id>`), diff the shape against the last sweep for the airlock
re-sense gate (`resense`), run the fast contacts-only check (`seams`), and read a
node's downstream blast-radius (`reach <id>`), each with `--json` / `--dot`
output; "done" means the five verbs land under one noun namespace, reuse the L3
shape render extended from `commands/state.py`, are documented (manpage + index +
cli-audit) and smoke-covered by behave, and NEVER write graph state.

## Lane

**Heavy** - This OBPI adds a new gz ontology CLI subcommand group (five verbs
plus `--json` / `--dot` flags) — a runtime CLI-contract surface consumed by
humans and machines.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces. A new subcommand group with new exit-code/output
> contracts is squarely Heavy (CLI Doctrine — "New Subcommand (Heavy Lane)").

## Allowed Paths

- `src/gzkit/commands/ontology.py` — **CREATE**: the gz ontology command group implementation — `sense` / `trace` / `resense` / `seams` / `reach` plus the `--json` / `--dot` renderers. Consumes the corpus-domain projection (OBPI-02) read-only and renders via the L3 shape imaging reused from `state.py`. Never writes graph state (Boundary Invariant #2).
- `src/gzkit/cli/parser_governance.py` — **MODIFY**: register the gz ontology noun namespace and its verb subparsers (`sense`, `trace <id>`, `resense`, `seams`, `reach <id>`) with `--json` / `--dot` flags, seated beside the sibling `state` / `status` graph-navigation verbs.
- `src/gzkit/cli/parser_handler_manifest.py` — **MODIFY**: add the ontology handler key(s) to `_LAZY_HANDLERS` so `_lazy(...)` resolves the new group's handlers (fenced by `tests/cli/test_handler_manifest_resolves.py`).
- `src/gzkit/commands/state.py` — **MODIFY**: light extension only — expose/reuse the existing L3 render (`_render_artifact_state_table` and the ledger-graph derivation) for the ontology shape sweep. No change to the `state()` / `state_repair()` contracts.
- `docs/user/manpages/ontology.md` — **CREATE**: the gz ontology verb-group manpage (Gate 3 proof; `gz cli audit` manpage coverage).
- `docs/user/manpages/index.md` — **MODIFY**: add the gz ontology index entry (`gz cli audit` index coverage).
- `config/doc-coverage.json` — **MODIFY**: declare the documentation obligation for the new `ontology sense` / `trace` / `resense` / `seams` / `reach` commands (an undeclared command fails `gz cli audit` / doc-coverage).
- `docs/user/runbook.md` — **MODIFY**: reference the new gz ontology verbs in the operator workflow (Gate 3 runbook covenant).
- `docs/governance/governance_runbook.md` — **MODIFY**: reference the gz ontology re-sense workflow (the airlock gate) for governance maintainers.
- `tests/commands/test_ontology.py` — **CREATE**: the `@covers(REQ-0.32.0-03-NN)` behavior tests for the six BEHAVIOR REQs.
- `features/ontology.feature` — **CREATE**: the behave smoke for the gz ontology verb group (Gate 4).
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md` — parent ADR for intent and scope (read-only reference; Boundary Invariants anchor).
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/**` — parent ADR package scope (this brief; evidence).

## Denied Paths

- The Pydantic ontology model + JSON schema under `src/gzkit/schemas/` — item #1's surface (OntologyNode/OntologyEdge/LinkType + two-axis classification); consumed read-only here, never authored.
- The networkx MultiDiGraph substrate + corpus projection + rebuild-fidelity self-report internals — item #2's surface; this OBPI consumes the projection's output, it does NOT build or edit the graph.
- `src/gzkit/events.py` and the net-new L2 edge schema (`blocks` / `blocked_by` / `discovered_from` / `validates`) — item #6's surface (the one-way door); this OBPI emits NO new ledger event types.
- `src/gzkit/ledger.py` `get_artifact_graph` and `src/gzkit/triangle.py` — the absorbed representations; not re-expressed here.
- Any write path into graph state — this interface is strictly read-only over the derived projection (Boundary Invariant #2).
- Paths not listed in Allowed Paths.
- New runtime dependencies (networkx / tree-sitter are already ADR-attested; none added here), CI files, lockfiles.

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Deliver the gz ontology verb group — `sense`, `trace <id>`, `resense`, `seams`, `reach <id>` — with `--json` and `--dot` output, registered under one noun namespace and reachable through the gz parser tree.
2. REQUIREMENT: Every verb consumes the corpus-domain projection READ-ONLY. NEVER write graph state, emit a graph-mutation event, or edit the projection directly — writeback reaches the graph only by rebuild (Boundary Invariant #2).
3. REQUIREMENT: `sense` output MUST label STRUCTURAL vs semantic coverage and MUST NOT claim semantic completeness (Boundary Invariant #3).
4. REQUIREMENT: `--json` MUST include the graph's rebuild-fidelity self-report (replay completeness + freshness) so the shape can confess an incomplete or stale replay rather than image a lie.
5. REQUIREMENT: The new verb group MUST ship a manpage, `gz cli audit` coverage (manpage + index + doc-coverage entry), and a behave smoke before completion.
6. REQUIREMENT: Work MUST stay inside the Allowed Paths; the model (item #1), the substrate/projection internals (item #2), and the L2 edge schema (item #6) remain untouched.
7. ALWAYS: Reconcile this brief against the parent ADR § Decision (item #3) before implementation; quote the sentence this OBPI implements verbatim into `### Implementation Summary`.
8. NEVER: Mark this OBPI accepted while scaffold defaults remain, or while any REQ lacks its declared proof channel (BEHAVIOR `@covers`, SUPPORT ledger+validator, STRUCTURAL-FENCE parent-ADR anchor).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision — quote the interface sentence** verbatim into `### Implementation Summary`: "Operator surface is verb-first under a noun namespace: gz ontology sense (sweep the whole current shape + surface structural seams), trace <id> (vertical lineage + lateral anchors/proof for one node, with edge provenance), resense (diff vs last sweep -- the airlock's re-sense gate), plus seams and reach; --json/--dot output; extends commands/state.py's L3 render."
- [ ] Parent ADR § Intent — the "working in the dark" why-frame the sonar answers.
- [ ] Parent ADR § Boundary Invariants #2 (Derived-never-authority; writeback by rebuild only) and #3 (`sense` images structure only) — the two fences this interface must honor.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/ADR-0.32.0-gzkit-ontology.md`

> **STOP:** If you cannot quote the parent ADR § Decision interface sentence that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.claude/rules/cli.md` — CLI Doctrine (new-subcommand Heavy-lane checklist; exit-code map; `--json` output contract).
- [ ] `.claude/rules/tool-skill-runbook-alignment.md` — every new CLI verb needs a wielding skill + runbook-prescribed moment.
- [ ] `AGENTS.md` § REQ-kind discipline (ADR-0.0.59) — BEHAVIOR / SUPPORT / STRUCTURAL-FENCE proof channels.

**Context:**

- [ ] OBPI-0.32.0-02 (substrate + corpus projection) — the read-only source this interface renders; land order: 02 before 03.
- [ ] OBPI-0.32.0-04 (ownership/plane doctrine + Boundary Invariants) — the STRUCTURAL-FENCE home this OBPI's fence REQs anchor to.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/state.py` exists with `_render_artifact_state_table` and the ledger-graph derivation (the L3 render this OBPI extends).
- [ ] `src/gzkit/cli/parser_governance.py` and `src/gzkit/cli/parser_handler_manifest.py` exist (the CLI registration + lazy-handler manifest surfaces).
- [ ] The corpus-domain projection from OBPI-0.32.0-02 is importable (this OBPI consumes it read-only). If absent, STOP — the interface has nothing to image.
- [ ] Parent ADR present and registered in `gz state`.

**Existing Code (understand current state):**

- [ ] `src/gzkit/commands/state.py` — `state()`, `_render_artifact_state_table`, `_hide_withdrawn_obpis`; the L3 render + graph-derivation to reuse without altering `state()` / `state_repair()`.
- [ ] `src/gzkit/cli/parser_governance.py` — the `gz personas` / `gz mx` noun-namespace registration pattern (`add_parser` → `add_subparsers(dest=...)` → `required = True`) to mirror for the new `ontology` group.
- [ ] `src/gzkit/cli/parser_handler_manifest.py` — `_LAZY_HANDLERS` map + `_lazy` resolver (fenced by `tests/cli/test_handler_manifest_resolves.py`).
- [ ] `src/gzkit/commands/cli_audit.py` + `config/doc-coverage.json` — the manpage/index/doc-coverage surfaces `gz cli audit` checks.
- [ ] `features/state_repair.feature` — the behave smoke shape (Given workspace initialized / When I run the gz command / Then exit code) to mirror in `features/ontology.feature`.

## Quality Gates

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

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run -m behave features/ontology.feature
```

## Demo

Real invocations of the new verbs against live governance nodes (run after the
group lands). Every node id below exists in the current ledger.

<!-- gz-validate-skip: command-shape -->
```bash
uv run gz ontology sense
uv run gz ontology sense --json
uv run gz ontology sense --dot
uv run gz ontology trace ADR-0.31.0-obpi-state-machine
uv run gz ontology resense
uv run gz ontology seams
uv run gz ontology reach ADR-0.32.0-gzkit-ontology
```

## Acceptance Criteria

- [ ] REQ-0.32.0-03-01 [BEHAVIOR]: `ontology sense` images the current structural shape (sweeps the corpus subgraph and surfaces STRUCTURAL seams) and exits 0 on a healthy tree. Proven by a `@covers(REQ-0.32.0-03-01)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-02 [BEHAVIOR]: `ontology trace <id>` returns one node's vertical lineage plus lateral anchors/proof, WITH edge provenance (why each edge is present or absent). Proven by a `@covers(REQ-0.32.0-03-02)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-03 [BEHAVIOR]: `ontology resense` reports the diff versus the last sweep (added/removed nodes and edges) — the airlock re-sense gate. Proven by a `@covers(REQ-0.32.0-03-03)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-04 [BEHAVIOR]: `ontology seams` runs the fast contacts-only check (STRUCTURAL seams without full per-node lineage). Proven by a `@covers(REQ-0.32.0-03-04)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-05 [BEHAVIOR]: `ontology reach <id>` returns the downstream blast-radius (transitive dependents) for one node. Proven by a `@covers(REQ-0.32.0-03-05)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-06 [BEHAVIOR]: `--json` emits the machine-readable shape plus the rebuild-fidelity self-report (replay completeness + freshness), and `--dot` emits a graphviz rendering of the same shape. Proven by a `@covers(REQ-0.32.0-03-06)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-07 [STRUCTURAL-FENCE]: `ontology sense` labels STRUCTURAL versus semantic coverage and never claims semantic completeness — anchored in the parent ADR `## Boundary Invariants` #3.
- [ ] REQ-0.32.0-03-08 [STRUCTURAL-FENCE]: the ontology interface consumes the graph read-only and never writes graph state (no direct-edit writeback; writeback reaches the graph only by rebuild) — anchored in the parent ADR `## Boundary Invariants` #2.
- [ ] REQ-0.32.0-03-09 [SUPPORT]: the new gz ontology verb group ships `docs/user/manpages/ontology.md` (with an index entry + doc-coverage declaration for `gz cli audit`) and a behave smoke under `features/ontology.feature` — proven by `gz validate --documents` passing AND an `artifact_edited` ledger event citing `docs/user/manpages/ontology.md`.

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
