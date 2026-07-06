---
id: OBPI-0.32.0-03-gz-ontology-interface
parent: ADR-0.32.0-gzkit-ontology
item: 3
lane: Heavy
status: Completed
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

**Status:** Completed

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
- `.gzkit/ontology/last_sweep.json` — **CREATE** (generated): the Tier-B derived last-sweep snapshot `sense` persists and `resense` diffs against — regenerable, never authoritative, never graph state (mirrors OBPI-07's `source_anchors.json` derived-index pattern).
- `docs/user/manpages/ontology.md` — **CREATE**: the gz ontology verb-group overview manpage (`# gz ontology`; group entry point).
- `docs/user/manpages/ontology-sense.md` — **CREATE**: `# gz ontology sense` per-verb manpage (Gate 3 proof; `gz cli audit` manpage coverage — `manpage_path_for("ontology sense")` → this file).
- `docs/user/manpages/ontology-trace.md` — **CREATE**: `# gz ontology trace` per-verb manpage (`gz cli audit` manpage coverage).
- `docs/user/manpages/ontology-resense.md` — **CREATE**: `# gz ontology resense` per-verb manpage (`gz cli audit` manpage coverage).
- `docs/user/manpages/ontology-seams.md` — **CREATE**: `# gz ontology seams` per-verb manpage (`gz cli audit` manpage coverage).
- `docs/user/manpages/ontology-reach.md` — **CREATE**: `# gz ontology reach` per-verb manpage (`gz cli audit` manpage coverage).
- `docs/user/manpages/index.md` — **MODIFY**: add the gz ontology group + per-verb index entries (`gz cli audit` index coverage).
- `config/doc-coverage.json` — **MODIFY**: declare the documentation obligation for the new `ontology sense` / `trace` / `resense` / `seams` / `reach` commands (an undeclared command fails `gz cli audit` / doc-coverage).
- `docs/user/runbook.md` — **MODIFY**: reference the new gz ontology verbs in the operator workflow (Gate 3 runbook covenant).
- `docs/governance/governance_runbook.md` — **MODIFY**: reference the gz ontology re-sense workflow (the airlock gate) for governance maintainers.
- `tests/commands/test_ontology.py` — **CREATE**: the `@covers(REQ-0.32.0-03-NN)` behavior tests for the six BEHAVIOR REQs.
- `features/ontology.feature` — **CREATE**: the behave smoke for the gz ontology verb group (Gate 4).
- `.gzkit/skills/gz-ontology/SKILL.md` — **CREATE**: the wielding skill required by `.claude/rules/tool-skill-runbook-alignment.md` Invariant 1 (every new CLI verb needs a skill that wields it); the generated mirrors under `src/gzkit/skills/`, `.claude/skills/`, `.agents/skills/`, `.github/skills/` are `gz agent sync control-surfaces` outputs, not hand-edited.
- `.gzkit/skills/gz-governance/SKILL.md` — **MODIFY**: route `gz-ontology` under the governance namespace router (router-tables-coverage requires every concrete skill be reachable from a router); version bump + sync mirrors.
- `docs/user/skills/gz-ontology.md` — **CREATE**: the operator skill manpage (skill-manpage-coverage: every active skill needs a manpage).
- `docs/user/skills/index.md` — **MODIFY**: link the gz-ontology skill manpage from the skills index (skill-index-coverage).
- `.gitignore` — **MODIFY**: gitignore the regenerable `.gzkit/ontology/last_sweep.json` derived diff-baseline cache (Tier-B, never authority).
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

1. REQUIREMENT: `sense` images the current structural shape (sweeps the corpus subgraph and surfaces STRUCTURAL seams) and exits 0 on a healthy tree with zero spurious seams (REQ-0.32.0-03-01).
2. REQUIREMENT: `trace <id>` returns one node's vertical lineage plus lateral anchors/proof, with edge provenance for why each edge is present or absent (REQ-0.32.0-03-02).
3. REQUIREMENT: `resense` reports the diff versus the last sweep (added/removed nodes and edges); the baseline is persisted by `sense` as a Tier-B derived snapshot (REQ-0.32.0-03-03).
4. REQUIREMENT: `seams` runs the fast contacts-only STRUCTURAL seam check without full per-node lineage (REQ-0.32.0-03-04).
5. REQUIREMENT: `reach <id>` returns the downstream blast-radius (transitive dependents) for one node (REQ-0.32.0-03-05).
6. REQUIREMENT: all five verbs register under one noun namespace reachable through the gz parser tree; `--json` includes the graph's rebuild-fidelity self-report (replay completeness + freshness) and `--dot` emits a graphviz rendering (REQ-0.32.0-03-06).
7. REQUIREMENT: `sense` labels STRUCTURAL versus semantic coverage and never claims semantic completeness (Boundary Invariant #3; REQ-0.32.0-03-07).
8. REQUIREMENT: every verb consumes the corpus-domain projection READ-ONLY and never writes graph state — the `last_sweep.json` diff-baseline is an exempt derived cache, not graph state (Boundary Invariant #2; REQ-0.32.0-03-08).
9. REQUIREMENT: the verb group ships per-verb manpages, `gz cli audit` coverage (manpage + index + doc-coverage entry), and a behave smoke before completion (REQ-0.32.0-03-09).

> Process guards: reconcile this brief against the parent ADR § Decision (item #3) before implementation and quote the implemented sentence verbatim into `### Implementation Summary`; do not mark this OBPI accepted while scaffold defaults remain or while any REQ lacks its declared proof channel (BEHAVIOR `@covers`, SUPPORT ledger+validator, STRUCTURAL-FENCE parent-ADR anchor). Work stays inside the Allowed Paths; the model (item #1), the substrate/projection internals (item #2), and the L2 edge schema (item #6) remain untouched.

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

- [ ] REQ-0.32.0-03-01 [BEHAVIOR]: `ontology sense` images the current structural shape (sweeps the corpus subgraph and surfaces STRUCTURAL seams) and exits 0 on a healthy tree; on a known-healthy fixture tree it surfaces NO spurious structural seam (every surfaced seam corresponds to a real structural gap) — a false-positive floor that keeps the sonar trustworthy so operators are not trained to mute it (§ Consequences Negative #7, the `sense`-as-noise concern). Proven by a `@covers(REQ-0.32.0-03-01)` test that asserts both the healthy-tree exit AND the zero-spurious-seam floor over a clean fixture, in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-02 [BEHAVIOR]: `ontology trace <id>` returns one node's vertical lineage plus lateral anchors/proof, WITH edge provenance (why each edge is present or absent). Proven by a `@covers(REQ-0.32.0-03-02)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-03 [BEHAVIOR]: `ontology resense` reports the diff versus the last sweep (added/removed nodes and edges) — the airlock re-sense gate. The last-sweep baseline is persisted by `sense` as a Tier-B DERIVED snapshot at `.gzkit/ontology/last_sweep.json` (regenerable, never authoritative; writing this derived diff-baseline cache is NOT a graph-state write and does not breach the read-only fence (never writes graph state), exactly as `source_anchors.json` is a derived index); `resense` reads that snapshot and diffs it against a fresh live sweep, so drift-since-a-prior-point is detectable (a two-live-rebuild diff, which cannot detect drift against a prior point in time, is insufficient). Proven by a `@covers(REQ-0.32.0-03-03)` test that seeds a baseline snapshot, mutates the shape, and asserts the added/removed delta, in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-04 [BEHAVIOR]: `ontology seams` runs the fast contacts-only check (STRUCTURAL seams without full per-node lineage). Proven by a `@covers(REQ-0.32.0-03-04)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-05 [BEHAVIOR]: `ontology reach <id>` returns the downstream blast-radius (transitive dependents) for one node. Proven by a `@covers(REQ-0.32.0-03-05)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-06 [BEHAVIOR]: `--json` emits the machine-readable shape plus the rebuild-fidelity self-report (replay completeness + freshness), and `--dot` emits a graphviz rendering of the same shape. Proven by a `@covers(REQ-0.32.0-03-06)` test in `tests/commands/test_ontology.py`.
- [ ] REQ-0.32.0-03-07 [STRUCTURAL-FENCE]: `ontology sense` labels STRUCTURAL versus semantic coverage and never claims semantic completeness — anchored in the parent ADR `## Boundary Invariants` #3.
- [ ] REQ-0.32.0-03-08 [STRUCTURAL-FENCE]: the ontology interface consumes the graph read-only and never writes graph STATE (no direct-edit writeback; writeback reaches the graph only by rebuild) — the Tier-B derived `last_sweep.json` diff-baseline cache `resense` persists is NOT graph state (a regenerable snapshot, like `source_anchors.json`), so it does not breach this fence — anchored in the parent ADR `## Boundary Invariants` #2.
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


`uv run gz ontology sense` on the live governance tree images the shape and reports zero spurious structural seams (REQ-01 false-positive floor holding against reality, not just fixtures):

```
Nodes: 1165  Edges: 1746  Seams: 0
STRUCTURAL coverage only — semantic completeness is NOT claimed (semantic-seam recall is deferred to RECALL / Phase-4, L3-advisory).
```

`uv run gz ontology sense --json` carries the rebuild-fidelity self-report (complete=True, fresh=True, unaccounted_event_types=[]); `uv run gz ontology trace ADR-0.32.0-gzkit-ontology` walks up to PRD-GZKIT-1.0.0 and down to its 7 OBPIs. Full suite green: receipt arb-step-unittest-b09f321435e441028a5cdb152f01f619 (6834 tests OK).

### Implementation Summary


- Delivered: the gz ontology read-only sonar (ADR-0.32.0 Decision item #3) — "Operator surface is verb-first under a noun namespace: gz ontology sense ... trace <id> ... resense ... plus seams and reach; --json/--dot output; extends commands/state.py's L3 render." Five verbs consume the OBPI-02 corpus projection READ-ONLY.
- Files created: src/gzkit/commands/ontology.py; tests/commands/test_ontology.py; features/ontology.feature; 6 manpages (ontology.md + 5 per-verb); docs/user/skills/gz-ontology.md; .gzkit/skills/gz-ontology/SKILL.md (+ synced mirrors).
- Files modified: src/gzkit/cli/parser_governance.py (noun namespace + 5 verbs); src/gzkit/cli/parser_handler_manifest.py (5 lazy keys); src/gzkit/commands/state.py (additive render_l3_table; state()/state_repair() contracts unchanged); config/doc-coverage.json; docs/user/manpages/index.md; docs/user/skills/index.md; docs/user/runbook.md; docs/governance/governance_runbook.md; .gzkit/skills/gz-governance/SKILL.md (routed gz-ontology, v0.4.0); .gitignore.
- Tests added: 14 unit (13 @covers over the 6 BEHAVIOR REQs + 1 read-only-fence regression guard) and 7 behave scenarios; full suite 6834 tests OK.
- Read-only fence honored (Boundary Invariant #2): the sole filesystem write is the Tier-B derived .gzkit/ontology/last_sweep.json diff-baseline cache (gitignored, never authority).
- Date completed: 2026-07-06.
- Attestation status: operator-attested (g0, "attest completed"); independent adversary NOT-REFUTED.
- Defects noted: none.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Gate 5 human attestation by operator g0 (2026-07-06) for the gz ontology read-only sonar (OBPI-0.32.0-03). Evidence: full suite 6834 tests OK (arb-step-unittest-b09f321435e441028a5cdb152f01f619), ruff clean (arb-ruff-99092de9114641ada6c686f60361be95), typecheck clean (arb-step-typecheck-b367bfe2b83244c29c36795595ba7487), mkdocs strict (arb-step-mkdocs-7ca7bb9a7b904a7789fcf9edcfd4daac), behave 7/7 (arb-step-behave-efd43e3e17254dc790a0375e5fffeeb4); covers behavior_uncovered_reqs=0 across 9 REQs; live sense on 1165-node graph reports 0 seams; independent adversary verdict NOT-REFUTED with its weakest point closed by a read-only-fence regression guard.
- Date: 2026-07-06

---

**Date Completed:** 2026-07-06

**Evidence Hash:** -
