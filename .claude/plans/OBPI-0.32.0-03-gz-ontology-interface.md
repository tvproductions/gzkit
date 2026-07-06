# Plan: OBPI-0.32.0-03 — gz ontology interface

**OBPI:** OBPI-0.32.0-03-gz-ontology-interface
**Parent ADR:** ADR-0.32.0-gzkit-ontology (checklist item #3, MVP spine)
**Lane:** Heavy (new CLI subcommand group + --json/--dot output contracts)

## Context

Ship the operator-facing `gz ontology` read-only sonar over the corpus-domain
projection built by OBPI-0.32.0-02. Five verbs under one noun namespace:

- `sense` — sweep the current structural shape + surface STRUCTURAL seams
- `trace <id>` — one node's vertical lineage + lateral anchors/proof + edge provenance
- `resense` — diff vs last sweep (the airlock's re-sense gate)
- `seams` — fast contacts-only STRUCTURAL seam check
- `reach <id>` — downstream blast-radius (transitive dependents)

Each with `--json` and `--dot`. The interface is strictly READ-ONLY over the
derived projection (Boundary Invariant #2) — the sole write is the Tier-B derived
`.gzkit/ontology/last_sweep.json` diff-baseline cache, explicitly NOT graph state
(mirrors `source_anchors.json`; brief REQ-08).

### Substrate API consumed read-only (mapped from OBPI-02)

- `project_corpus(ledger=None) -> CorpusProjection` — `gzkit.ontology.corpus:236`
- `CorpusProjection.graph: OntologyGraph`, `.source_graph: dict`, `.fidelity: RebuildFidelity`
- `OntologyGraph`: `node_ids()`, `nodes()->list[OntologyNode]`, `edges()->list[OntologyEdge]`,
  `node_count()`, `edge_count()`, `reachable_from(node_id)->set[str]` (`gzkit.ontology.graph`)
- `RebuildFidelity`: `complete: bool`, `fresh: bool`, `unaccounted_event_types`,
  `unregistered_replayed_event_types`, `latest_event_ts`, `build_ts` (`corpus:125`)
- `OntologyNode(node_id, object_type, ownership, plane)`, `OntologyEdge(source_id, target_id, link_type)`,
  `LinkType`, `ObjectType` (`gzkit.ontology.model`)

### Registration surfaces (mapped)

- Parser: `register_governance_parsers` in `cli/parser_governance.py` — add an `ontology` noun
  block after the `mx` group (ends line 843). Pattern: `commands.add_parser("ontology")` ->
  `add_subparsers(dest="ontology_command")` -> `.required = True`; per verb `add_json_flag(p)` +
  raw `p.add_argument("--dot", action="store_true")` + `set_defaults(func=lambda a: _lazy("ontology_<verb>_cmd")(...))`.
  No `add_dot_flag` helper exists — register `--dot` raw (dest `dot`).
- Handler manifest: `cli/parser_handler_manifest.py` `_LAZY_HANDLERS` — 5 keys
  (`ontology_sense_cmd` … `ontology_reach_cmd`) -> `gzkit.commands.ontology`. Fenced by
  `tests/cli/test_handler_manifest_resolves.py` (key must byte-match the module `def` name).
- Handler house style: `def ontology_sense_cmd(*, as_json=False, as_dot=False) -> None:`;
  `raise SystemExit(code)` for nonzero exit (never `return int`).

## Design decisions

**Structural-seam definition (STRUCTURAL, zero-false-positive floor for REQ-01):** a seam is a
**dangling edge endpoint** — an edge whose `source_id` or `target_id` is not a materialized node
in the graph. On a healthy tree every CHILD/SUPERSEDES edge resolves to a real node -> zero seams.
Purely structural, no semantic judgment. Orphan-node detection is deliberately NOT used (roots like
PRD/Constitution are legitimately parentless -> would false-positive, breaching REQ-01's floor and
the § Consequences Negative #7 sense-as-noise concern).

**Derived-never-authority (BI #2):** `sense`/`seams` report seams but ALWAYS exit 0 — the sonar
never gates (matches Fidelity Assertions expecting exit 0). `trace`/`reach` exit 1 only on an
unknown node id (user error, exit-code map code 1).

**Pure-core / thin-shell:** seam/trace/reach/snapshot/diff are PURE functions over `OntologyGraph`
so `@covers` tests build fixtures via `add_node`/`add_edge` directly (fast, no ledger fixture).
Command handlers wrap: `project_corpus()` -> pure helper -> render (`--json`/`--dot`/table).

**state.py L3 render reuse (ADR "extends commands/state.py's L3 render"):** add ONE additive public
helper `render_l3_table(title, columns, rows, *, full=False) -> None` to `state.py` (thin rich.Table
wrapper); ontology imports it. Do NOT alter `state()` / `state_repair()` / `_render_artifact_state_table`
contracts (brief constraint).

**Manpage shape (operator-confirmed brief amendment):** per-verb manpages + group overview (6 files),
5 doc-coverage entries manpage:true. Amend brief Allowed Paths (+5 per-verb manpages) with an
`improvement` insight per Behavior Rule Always #11.

## Files

**CREATE:**
- `src/gzkit/commands/ontology.py` — the 5 handlers + pure helpers + renderers
- `.gzkit/ontology/last_sweep.json` — generated Tier-B baseline (created at runtime by `sense`)
- `tests/commands/test_ontology.py` — 6 BEHAVIOR `@covers` tests
- `features/ontology.feature` — behave smoke (Gate 4)
- `docs/user/manpages/ontology.md` — group overview (`# gz ontology`)
- `docs/user/manpages/ontology-sense.md` — `# gz ontology sense`
- `docs/user/manpages/ontology-trace.md` — `# gz ontology trace`
- `docs/user/manpages/ontology-resense.md` — `# gz ontology resense`
- `docs/user/manpages/ontology-seams.md` — `# gz ontology seams`
- `docs/user/manpages/ontology-reach.md` — `# gz ontology reach`

**MODIFY:**
- `src/gzkit/cli/parser_governance.py` — register the `ontology` noun namespace + 5 verb subparsers
- `src/gzkit/cli/parser_handler_manifest.py` — add 5 `_LAZY_HANDLERS` keys
- `src/gzkit/commands/state.py` — add additive `render_l3_table` helper (no contract change)
- `docs/user/manpages/index.md` — 6 index links (group + 5 verbs)
- `config/doc-coverage.json` — 5 verb entries (manpage/index true)
- `docs/user/runbook.md` — reference the ontology verbs in operator workflow
- `docs/governance/governance_runbook.md` — reference the re-sense workflow (airlock gate)
- `docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology/obpis/OBPI-0.32.0-03-gz-ontology-interface.md`
  — amend Allowed Paths (+5 per-verb manpages)

## Steps (Red-Green-Refactor, one behavior per cycle)

1. **Brief amendment first** — add the 5 per-verb manpage paths to the OBPI Allowed Paths; append an
   `improvement` insight to `.gzkit/insights/agent-insights.jsonl` (scope/summary/evidence/next_action).
2. **RED/GREEN sense seam floor (REQ-01):** test — build a clean fixture graph (all edges resolve) ->
   `compute_seams(graph) == []`; and `ontology_sense_cmd()` exits 0 on that fixture. Watch assertion-level
   red (stub `compute_seams` returning a sentinel), then implement dangling-edge detection.
3. **RED/GREEN trace (REQ-02):** test — fixture with parent/child + a self VALIDATES edge; `compute_trace`
   returns vertical lineage (ancestors+descendants) + lateral edges + per-edge provenance. Implement.
4. **RED/GREEN resense (REQ-03):** test — `snapshot_of(graph_a)` seeded, mutate to graph_b,
   `diff_snapshots(a,b)` reports added/removed nodes+edges. Implement snapshot/diff + `.gzkit/ontology/`
   mkdir + JSON read/write.
5. **RED/GREEN seams (REQ-04):** test — `seams` lists dangling edges only (no lineage), exit 0. Implement
   thin wrapper reusing `compute_seams`.
6. **RED/GREEN reach (REQ-05):** test — fixture chain A->B->C; `compute_reach(graph,"A") == {"B","C"}`;
   unknown id -> exit 1. Implement via `graph.reachable_from`.
7. **RED/GREEN --json/--dot fidelity (REQ-06):** test — `render_sense_json(projection)` includes a
   `fidelity` block with `complete`/`fresh`/`unaccounted_event_types`; `render_dot(graph)` emits a
   `digraph` with node+edge lines. Implement both renderers; wire `--json`/`--dot` in every verb.
8. **Register parser + handlers:** add ontology noun block to `parser_governance.py`; 5 keys to
   `parser_handler_manifest.py`. Confirm `tests/cli/test_handler_manifest_resolves.py` green.
9. **state.py L3 helper:** add `render_l3_table`; route ontology table render through it.
10. **Docs + doc-coverage:** author 6 manpages (each documents `--json`/`--dot`; trace/reach document the
    `<id>` arg), 6 index links, 5 doc-coverage entries, runbook + governance_runbook refs.
11. **behave smoke:** `features/ontology.feature` mirrors `state_repair.feature` — Given workspace init /
    When I run `gz ontology sense` / Then exit 0; tag scenarios `@REQ-0.32.0-03-01` … for scoped behave.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_ontology -v
uv run gz covers OBPI-0.32.0-03-gz-ontology-interface --json    # REQ->@covers parity gate
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run gz validate --documents
uv run mkdocs build --strict
uv run -m behave features/ontology.feature
```

## Step 6a disclosures (Plan-Before-Exploration)

**Destination-in-mind:** Before authoring this plan I had formed the approach of a pure-core /
thin-shell command module reusing `project_corpus` read-only, with dangling-edge as the structural-seam
definition and `reachable_from` for blast-radius — chosen because it maximizes testability (fixtures
built directly on `OntologyGraph`) and keeps the read-only fence provable.

**Rejected alternatives considered during exploration:** (a) orphan-node seam definition — rejected: roots
(PRD/Constitution) are legitimately parentless and would false-positive, breaching REQ-01's zero-spurious
floor. (b) Single group manpage with `manpage:false` verb entries — rejected: misuses the deprecated-alias
escape for live verbs (dishonest gate-pass); operator confirmed per-verb manpages. (c) Refactoring
`_render_artifact_state_table` to share internals with ontology — rejected: risks the state()/state_repair()
contract the brief fences; chose an additive `render_l3_table` helper instead. (d) Building the graph inside
the CLI — rejected: violates BI #2 (read-only consumer); ontology consumes `project_corpus` output only.

## Notes

- Read-only fence (REQ-02/08): no graph-mutation, no new ledger event type, no direct projection edit.
  The `last_sweep.json` write is the ONLY filesystem write and is an exempt derived cache (brief REQ-08).
- Land order honored: OBPI-02 (substrate+projection) is complete; this OBPI consumes it.
- STRUCTURAL-FENCE REQs 07/08 prove via parent ADR § Boundary Invariants #3/#2 (already authored) — no
  per-OBPI behavior test; `sense` still emits the "STRUCTURAL coverage only" label for operator honesty.
