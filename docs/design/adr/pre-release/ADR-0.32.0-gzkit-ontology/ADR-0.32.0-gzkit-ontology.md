---
id: ADR-0.32.0-gzkit-ontology
status: Draft
kind: feature
semver: 0.32.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-07-05
---

# ADR-0.32.0-gzkit-ontology: gzkit ontology (object/link plane)

## Persona

**Active persona:** `main-session` — craftsperson, governance-aware, whole-file-reasoning, direct. This ADR builds the instrument that makes drift visible, so author it in that spirit: every object, link, and verb earns its place by imaging the *actual* shape, never by asserting a convenient one. The graph must be honest about what it does and does not know — it images structure, confesses its own rebuild fidelity, and never launders a blind spot into false confidence. Derived-never-authority is not a limitation to work around but the discipline that keeps the sonar trustworthy.

## Intent

gzkit governance work repeatedly proceeds 'in the dark': agents and operators reason from stale or partial design docs instead of the actual shape of the codebase, docs, and governance artifacts. This session demonstrated the failure live -- a GO-attested substrate decision (tree-sitter + networkx) was silently reversed to stdlib because the reversal was authored from a handoff paraphrase rather than the attested source; the drift passed as a 'correction' because nothing imaged the real decided shape. gzkit's own graph knowledge is fragmented across parallel, un-unifiable representations: ledger.get_artifact_graph (an untyped dict of parent/child + metadata), triangle.py (a spec-test-code drift model), and a dormant ontology.schema.json -- none traversable as one whole. Movement III's airlock depends on re-sensing the shape before acting, and that cannot be certified by judgment ('I looked everywhere') -- only against a computed graph that enumerates the seams. This ADR builds that graph: the object/link plane of the gzkit ontology, a typed, queryable substrate that images the actual shape (vertical and lateral traversal) so ratified facts become queryable nodes and silent reversals light up instead of slipping through as corrections.

## Decision

Build the gzkit ontology as ONE unified, heavy feature ADR (not a multi-ADR constellation; OBPI decomposition manages blast radius within one ADR, as KEEL/ADR-0.31.0 proved). It is Palantir-Ontology-shaped: Objects + Links + Actions. Substrate: Pydantic models carry the typed Objects/Links (OntologyNode/OntologyEdge + a typed LinkType), held in a networkx MultiDiGraph (the graph engine -- lateral/reachability traversal + multigraph that stdlib graphlib cannot supply); tree-sitter is the polyglot source sensor; gz verbs are the Actions that write authoritative L1/L2, with the graph a Tier-B derived projection that rebuilds from them and never gates (writeback reaches the graph only by rebuild, never by direct edit). A two-axis type model classifies every object: ownership (harness|product; a Harness-Purity Invariant admits only GovZero-universal types into ownership:harness, enforced by a validator landing in the same increment) x plane (product|process; the semantics are seated in ontology.schema.json's dormant plane field for continuity-of-naming and validated to genuinely partition our objects, not merely asserted). Three domains are subgraphs of the one graph: corpus (ADR/OBPI/REQ/GHI/Receipt/Doc lineage -- absorbs get_artifact_graph as a typed view over one replay path; reads canon), work (TASK nodes + ready/blocked queue over a net-new L2 event schema: blocks/blocked_by/discovered_from/validates; advisory-first with a declared fail-closed torque-up milestone), source (tree-sitter code-coupling + @covers/@surface anchors; source->REQ first-class; absorbs triangle.py's edge model and re-expresses detect_drift as a subgraph view). Operator surface is verb-first under a noun namespace: gz ontology sense (sweep the whole current shape + surface structural seams), trace <id> (vertical lineage + lateral anchors/proof for one node, with edge provenance), resense (diff vs last sweep -- the airlock's re-sense gate), plus seams and reach; --json/--dot output; extends commands/state.py's L3 render. Docs are absorbed via OKF open-absorption: Doc subtype = OKF type verbatim, NO subset-validator (a closed-set check would breach OKF BI-1/BI-3), links_to edges kept. sense is honest about coverage: it images the STRUCTURAL shape only and never claims semantic completeness (the pre-registered falsifier is 'no un-accounted STRUCTURAL seam'; semantic-seam recall is RECALL/Phase-4's deferred, L3-advisory job). The graph self-reports its own rebuild fidelity (replay completeness + freshness) so it can confess when it might be lying. Supersedes pool ADRs artifact-graph-navigation, execution-memory-graph, covers-source-anchors; read-folds ADR-0.0.47 (its write-side returns to pool as a thin consumer that queries this ontology). MVP is corpus-first (model + corpus projection + gz ontology sense/trace + doctrine/Boundary-Invariants); work, source, and OKF are follow-on OBPIs in the same ADR, with the net-new L2 schema (the one irreversible surface) gated last on its own What-Would-Have-To-Be-True pass. This ADR discharges the STDLIB-FIRST departure attestation owed for networkx + tree-sitter (GO-attested Phase-0 airlock-in, 2026-07-02: 'deterministic multi-surface extraction + topo-sort/cycle-detection stdlib cannot supply').

## Consequences

### Positive

1. Vertical and lateral traversal replaces working in the dark: the actual shape of governance lineage, work, and source is queryable, not inferred from stale docs.
2. Ratified facts become queryable nodes -- a decision that contradicts a GO-attested node lights up instead of slipping through as a 'correction' (the exact failure this session demonstrated and would have caught).
3. The airlock (HATCH) gains a real seam-enumerator: re-sense can be certified against a graph, not asserted by judgment.
4. Three fragmented graph representations (get_artifact_graph, triangle, dormant ontology) unify into one typed substrate; drift detection and artifact-graph become views over one replay path -- less code, one source of shape.
5. The Tier-B derived-never-authority posture makes almost the entire feature a two-way door: rip out the graph and L1/L2 are untouched, so the design can be iterated freely.
What would have to be true for this to be right (WWHTBT), in order of shakiness: (a) rebuild fidelity is provable -- the graph reconstructs from L1/L2 with no missed event type (the load-bearing condition; nearly all risk concentrates here); (b) the absorptions preserve behavior exactly (tests pin every consumer through subsumption); (c) sense's structural-seam false-positive rate is low enough to be trusted; (d) networkx/tree-sitter are actually exercised (lateral/reachability + polyglot parse used, not just imported); (e) the two axes partition real objects.

### Negative

1. Trust-drift (the named pre-mortem failure, load-bearing): a rebuild bug or missed event type lets the Tier-B graph diverge from L1/L2 -- sense images a stale shape and the airlock certifies 'all seams seen' against a lie. A wrong graph is more dangerous than none because it is trusted (the GHI #348 class, one layer up). Mitigation is hardened into a rebuild-fidelity Boundary Invariant + falsifier and the graph's fidelity self-report; this is where the heavy-lane evidence concentrates.
2. False-confidence / laundered blind spots (assumption-surfacing): if the projection misses an edge type, sense is confidently wrong in exactly the way nobody noticed. Mitigation: sense must be honest about coverage -- it labels STRUCTURAL vs semantic and never claims semantic completeness.
3. Structural seams != semantic seams: the graph enumerates structural seams and can give false comfort about semantic ones ('the code does X, the REQ meant Y'). Semantic-seam recall is explicitly out of scope (deferred to RECALL/Phase-4 as L3-advisory).
4. The net-new L2 edge schema is the one true one-way door: L2 is append-only, so blocks/blocked_by/discovered_from/validates events are permanent once emitted. Irreversibility scrutiny concentrates here -- the work OBPI is gated last on its own WWHTBT of the exact edge set; the graph, CLI, and absorptions stay two-way (absorptions ship as compat views, not deletions).
5. Operational (2am): the operator needs edge provenance (why sense believes an edge is present/absent -- anchor missed? tree-sitter didn't parse? malformed @covers?), fidelity self-report (the graph confessing incomplete replay), and -- if a seam gates GO -- a traceable + witnessed override (ADR-0.29.0 precedent), never a 2am hard wall.
6. New runtime dependencies (networkx, tree-sitter) are a STDLIB-FIRST departure; attested here per the GO record, but a real maintenance surface (esp. tree-sitter grammars) if gzkit stays Python-only and reachability/polyglot are under-exercised.
7. sense-as-noise: too many spurious structural seams and operators mute the warning; the false-positive rate is a first-class acceptance concern.

## Boundary Invariants

These are the structural fences this ADR establishes. They are audited at ADR closeout
(STRUCTURAL-FENCE proof channel), not by per-OBPI behavior tests.

1. **Rebuild fidelity — the graph never lies about the shape.** The Tier-B projection
   reconstructs from L1 canon + L2 ledger with no missed event type or silent drop, and
   `sense` self-reports its replay completeness and freshness. A graph that cannot confess
   an incomplete or stale replay is a defect. This is the load-bearing fence — the entire
   trust premise (the airlock certifying "every seam seen") rests here.
2. **Derived-never-authority.** The ontology graph is a Tier-B projection: it NEVER gates,
   and no `gz validate` scope, gate, or closeout step consumes it as enforcement evidence.
   Truth lives in L1 canon and L2 ledger; the graph is an imaging/navigation aid
   (state-doctrine Rule 5). Writeback reaches the graph only by rebuild, never by direct edit.
3. **`sense` images structure only.** The sweep enumerates STRUCTURAL seams and never claims
   semantic completeness; the pre-registered falsifier is *"no un-accounted STRUCTURAL seam."*
   Semantic-seam recall is out of scope (RECALL / Phase-4, strictly L3-advisory).
4. **Harness purity.** `ownership:harness` admits only GovZero-universal object types; gzkit's
   own product objects (CliVerb/Validator/Skill/Chore) are `ownership:product` and never appear
   in the harness subgraph.
5. **OKF absorption stays open.** Doc `subtype` = OKF `type` verbatim; no consumer rejects a
   Doc for an unknown `type`, and no OKF frontmatter or link is consumed as enforcement evidence
   — preserving OKF (ADR-0.30.0) Boundary Invariants BI-1 and BI-3.

## Fidelity Assertions

<!-- Every non-pool ADR Decision ships runnable commands that exercise its thesis
     against the real system. `gz adr fidelity <ADR-ID>` RUNS these and compares
     observed-vs-expected exit. Replace the example row with assertions for THIS
     ADR; each becomes green as its owning OBPI lands. A non-pool ADR Decision
     with no parseable block fails `gz validate --fidelity-presence` (exit 3,
     ADR-0.0.73 Boundary Invariant #4). Keep at least one claim/command/exit row. -->

| Claim | Command | Expected exit |
|-------|---------|---------------|
| `gz ontology sense` images the current shape and exits clean on a healthy tree | `uv run gz ontology sense` | 0 |
| `gz ontology trace` walks a real node's vertical + lateral lineage | `uv run gz ontology trace ADR-0.31.0-obpi-state-machine` | 0 |
| The Harness-Purity fence refuses a product object placed in `ownership:harness` | `uv run gz validate --ontology-purity` | 0 |
| `sense --json` emits the machine-readable shape plus the rebuild-fidelity self-report | `uv run gz ontology sense --json` | 0 |

## Decomposition Scorecard

<!-- Deterministic OBPI sizing: score each dimension 0/1/2. -->
<!-- Cutoffs are notional defaults and should be calibrated over time from project evidence. -->

- Data/State: 2
- Logic/Engine: 2
- Interface: 2
- Observability: 2
- Lineage: 2
- Dimension Total: 10
- Baseline Range: 5+
- Baseline Selected: 5
- Split Single-Narrative: 0
- Split Surface Boundary: 1
- Split State Anchor: 1
- Split Testability Ceiling: 0
- Split Total: 2
- Final Target OBPI Count: 7

## Checklist

<!-- Each item becomes an OBPI (One Brief Per Item). Sequential numbering, no gaps. -->

- [ ] Pydantic ontology model (OntologyNode/OntologyEdge + typed LinkType) + two-axis ownership/plane classification + Harness-Purity validator (with a refusal test: a product object pushed into ownership:harness is rejected); plane semantics validated to partition our objects; JSON schema under src/gzkit/schemas/.
- [ ] networkx MultiDiGraph substrate + corpus-domain projection absorbing ledger.get_artifact_graph as a typed view over one replay path; rebuild-fidelity self-report (replay completeness + freshness); Tier-B rebuild-only guardrail. [MVP spine]
- [ ] gz ontology interface -- sense (structural-shape sweep + labeled structural seams), trace <id> (vertical lineage + lateral proof + edge provenance), resense (diff vs last sweep), seams, reach; --json/--dot; extends commands/state.py L3 render + manpage + cli-audit + behave smoke. [MVP spine]
- [ ] ownership/plane doctrine surface + this ADR's ## Boundary Invariants (rebuild-fidelity fence; Tier-B derived-never-authority; sense images structural-only) as STRUCTURAL-FENCE, audited at closeout. [MVP spine]
- [ ] OKF open-absorption: Doc subtype = OKF type verbatim, no subset-validator (honors OKF BI-1/BI-3), links_to edges kept.
- [ ] work domain: net-new L2 event schema (blocks/blocked_by/discovered_from/validates) + ready/blocked queue + advisory-first blocks with a declared fail-closed torque-up milestone; gated last on its own WWHTBT of the edge set (the one-way door).
- [ ] source domain: tree-sitter code-coupling + @covers/@surface anchors + source->REQ first-class + source_anchors.json query index + orphan-gap detection; absorbs triangle.py's edge model, re-expressing detect_drift as a subgraph view (compat-view, behavior preserved).

## Q&A Transcript

<!-- Interview transcript preserved for context -->

*Interview conducted: 2026-07-05T16:27:25.853812*

### Q: What is the ADR identifier? (canonical slug-form: ADR-<semver>-<slug>)

**A:** ADR-0.32.0-gzkit-ontology

### Q: What is the title of this ADR?

**A:** gzkit ontology (object/link plane)

### Q: What is the semantic version?

**A:** 0.32.0

### Q: Which lane? (lite = internal changes, heavy = external contracts)

**A:** heavy

### Q: What is the parent brief ID?

**A:** PRD-GZKIT-1.0.0

### Q: What problem are we solving? What is the specific goal of this ADR?

**A:** gzkit governance work repeatedly proceeds 'in the dark': agents and operators reason from stale or partial design docs instead of the actual shape of the codebase, docs, and governance artifacts. This session demonstrated the failure live -- a GO-attested substrate decision (tree-sitter + networkx) was silently reversed to stdlib because the reversal was authored from a handoff paraphrase rather than the attested source; the drift passed as a 'correction' because nothing imaged the real decided shape. gzkit's own graph knowledge is fragmented across parallel, un-unifiable representations: ledger.get_artifact_graph (an untyped dict of parent/child + metadata), triangle.py (a spec-test-code drift model), and a dormant ontology.schema.json -- none traversable as one whole. Movement III's airlock depends on re-sensing the shape before acting, and that cannot be certified by judgment ('I looked everywhere') -- only against a computed graph that enumerates the seams. This ADR builds that graph: the object/link plane of the gzkit ontology, a typed, queryable substrate that images the actual shape (vertical and lateral traversal) so ratified facts become queryable nodes and silent reversals light up instead of slipping through as corrections.

### Q: What did we decide? Be specific about the approach, libraries, patterns.

**A:** Build the gzkit ontology as ONE unified, heavy feature ADR (not a multi-ADR constellation; OBPI decomposition manages blast radius within one ADR, as KEEL/ADR-0.31.0 proved). It is Palantir-Ontology-shaped: Objects + Links + Actions. Substrate: Pydantic models carry the typed Objects/Links (OntologyNode/OntologyEdge + a typed LinkType), held in a networkx MultiDiGraph (the graph engine -- lateral/reachability traversal + multigraph that stdlib graphlib cannot supply); tree-sitter is the polyglot source sensor; gz verbs are the Actions that write authoritative L1/L2, with the graph a Tier-B derived projection that rebuilds from them and never gates (writeback reaches the graph only by rebuild, never by direct edit). A two-axis type model classifies every object: ownership (harness|product; a Harness-Purity Invariant admits only GovZero-universal types into ownership:harness, enforced by a validator landing in the same increment) x plane (product|process; the semantics are seated in ontology.schema.json's dormant plane field for continuity-of-naming and validated to genuinely partition our objects, not merely asserted). Three domains are subgraphs of the one graph: corpus (ADR/OBPI/REQ/GHI/Receipt/Doc lineage -- absorbs get_artifact_graph as a typed view over one replay path; reads canon), work (TASK nodes + ready/blocked queue over a net-new L2 event schema: blocks/blocked_by/discovered_from/validates; advisory-first with a declared fail-closed torque-up milestone), source (tree-sitter code-coupling + @covers/@surface anchors; source->REQ first-class; absorbs triangle.py's edge model and re-expresses detect_drift as a subgraph view). Operator surface is verb-first under a noun namespace: gz ontology sense (sweep the whole current shape + surface structural seams), trace <id> (vertical lineage + lateral anchors/proof for one node, with edge provenance), resense (diff vs last sweep -- the airlock's re-sense gate), plus seams and reach; --json/--dot output; extends commands/state.py's L3 render. Docs are absorbed via OKF open-absorption: Doc subtype = OKF type verbatim, NO subset-validator (a closed-set check would breach OKF BI-1/BI-3), links_to edges kept. sense is honest about coverage: it images the STRUCTURAL shape only and never claims semantic completeness (the pre-registered falsifier is 'no un-accounted STRUCTURAL seam'; semantic-seam recall is RECALL/Phase-4's deferred, L3-advisory job). The graph self-reports its own rebuild fidelity (replay completeness + freshness) so it can confess when it might be lying. Supersedes pool ADRs artifact-graph-navigation, execution-memory-graph, covers-source-anchors; read-folds ADR-0.0.47 (its write-side returns to pool as a thin consumer that queries this ontology). MVP is corpus-first (model + corpus projection + gz ontology sense/trace + doctrine/Boundary-Invariants); work, source, and OKF are follow-on OBPIs in the same ADR, with the net-new L2 schema (the one irreversible surface) gated last on its own What-Would-Have-To-Be-True pass. This ADR discharges the STDLIB-FIRST departure attestation owed for networkx + tree-sitter (GO-attested Phase-0 airlock-in, 2026-07-02: 'deterministic multi-surface extraction + topo-sort/cycle-detection stdlib cannot supply').

### Q: What good things result from this decision? List benefits.

**A:** 1. Vertical and lateral traversal replaces working in the dark: the actual shape of governance lineage, work, and source is queryable, not inferred from stale docs.
2. Ratified facts become queryable nodes -- a decision that contradicts a GO-attested node lights up instead of slipping through as a 'correction' (the exact failure this session demonstrated and would have caught).
3. The airlock (HATCH) gains a real seam-enumerator: re-sense can be certified against a graph, not asserted by judgment.
4. Three fragmented graph representations (get_artifact_graph, triangle, dormant ontology) unify into one typed substrate; drift detection and artifact-graph become views over one replay path -- less code, one source of shape.
5. The Tier-B derived-never-authority posture makes almost the entire feature a two-way door: rip out the graph and L1/L2 are untouched, so the design can be iterated freely.
What would have to be true for this to be right (WWHTBT), in order of shakiness: (a) rebuild fidelity is provable -- the graph reconstructs from L1/L2 with no missed event type (the load-bearing condition; nearly all risk concentrates here); (b) the absorptions preserve behavior exactly (tests pin every consumer through subsumption); (c) sense's structural-seam false-positive rate is low enough to be trusted; (d) networkx/tree-sitter are actually exercised (lateral/reachability + polyglot parse used, not just imported); (e) the two axes partition real objects.

### Q: What tradeoffs or downsides come with this decision?

**A:** 1. Trust-drift (the named pre-mortem failure, load-bearing): a rebuild bug or missed event type lets the Tier-B graph diverge from L1/L2 -- sense images a stale shape and the airlock certifies 'all seams seen' against a lie. A wrong graph is more dangerous than none because it is trusted (the GHI #348 class, one layer up). Mitigation is hardened into a rebuild-fidelity Boundary Invariant + falsifier and the graph's fidelity self-report; this is where the heavy-lane evidence concentrates.
2. False-confidence / laundered blind spots (assumption-surfacing): if the projection misses an edge type, sense is confidently wrong in exactly the way nobody noticed. Mitigation: sense must be honest about coverage -- it labels STRUCTURAL vs semantic and never claims semantic completeness.
3. Structural seams != semantic seams: the graph enumerates structural seams and can give false comfort about semantic ones ('the code does X, the REQ meant Y'). Semantic-seam recall is explicitly out of scope (deferred to RECALL/Phase-4 as L3-advisory).
4. The net-new L2 edge schema is the one true one-way door: L2 is append-only, so blocks/blocked_by/discovered_from/validates events are permanent once emitted. Irreversibility scrutiny concentrates here -- the work OBPI is gated last on its own WWHTBT of the exact edge set; the graph, CLI, and absorptions stay two-way (absorptions ship as compat views, not deletions).
5. Operational (2am): the operator needs edge provenance (why sense believes an edge is present/absent -- anchor missed? tree-sitter didn't parse? malformed @covers?), fidelity self-report (the graph confessing incomplete replay), and -- if a seam gates GO -- a traceable + witnessed override (ADR-0.29.0 precedent), never a 2am hard wall.
6. New runtime dependencies (networkx, tree-sitter) are a STDLIB-FIRST departure; attested here per the GO record, but a real maintenance surface (esp. tree-sitter grammars) if gzkit stays Python-only and reachability/polyglot are under-exercised.
7. sense-as-noise: too many spurious structural seams and operators mute the warning; the false-positive rate is a first-class acceptance concern.

### Q: What are the implementation checklist items? Each becomes an OBPI.

**A:** 1. Pydantic ontology model (OntologyNode/OntologyEdge + typed LinkType) + two-axis ownership/plane classification + Harness-Purity validator (with a refusal test: a product object pushed into ownership:harness is rejected); plane semantics validated to partition our objects; JSON schema under src/gzkit/schemas/.
2. networkx MultiDiGraph substrate + corpus-domain projection absorbing ledger.get_artifact_graph as a typed view over one replay path; rebuild-fidelity self-report (replay completeness + freshness); Tier-B rebuild-only guardrail. [MVP spine]
3. gz ontology interface -- sense (structural-shape sweep + labeled structural seams), trace <id> (vertical lineage + lateral proof + edge provenance), resense (diff vs last sweep), seams, reach; --json/--dot; extends commands/state.py L3 render + manpage + cli-audit + behave smoke. [MVP spine]
4. ownership/plane doctrine surface + this ADR's ## Boundary Invariants (rebuild-fidelity fence; Tier-B derived-never-authority; sense images structural-only) as STRUCTURAL-FENCE, audited at closeout. [MVP spine]
5. OKF open-absorption: Doc subtype = OKF type verbatim, no subset-validator (honors OKF BI-1/BI-3), links_to edges kept.
6. work domain: net-new L2 event schema (blocks/blocked_by/discovered_from/validates) + ready/blocked queue + advisory-first blocks with a declared fail-closed torque-up milestone; gated last on its own WWHTBT of the edge set (the one-way door).
7. source domain: tree-sitter code-coupling + @covers/@surface anchors + source->REQ first-class + source_anchors.json query index + orphan-gap detection; absorbs triangle.py's edge model, re-expressing detect_drift as a subgraph view (compat-view, behavior preserved).

### Q: What alternatives were considered and why were they rejected?

**A:** stdlib graphlib + adjacency + ast substrate (REJECTED, and reverted in-session): graphlib is only a topological sorter -- it cannot image lateral/reachability traversal, which is the entire point of the sonar; stdlib ast is Python-only, wrong for a harness that runs on adopter codebases. This was briefly adopted as a same-day campaign amendment and reverted -- the tree-sitter+networkx floor is GO-attested (Phase-0 airlock-in 2026-07-02) with the STDLIB-FIRST departure rationale already named; the reversal contradicted a ratified decision without new evidence. 3-ADR constellation (REJECTED): splitting corpus/work/source into three cohered ADRs invents cross-ADR coherence machinery (shared namespace, frame-gates-siblings, 1:1 supersession across a set) that a single ADR does not need; blast radius is handled by OBPI decomposition, which KEEL proved lands cleanly; the domains share one substrate and one replay, with no independent release cadence. Parallel typed model / widen triangle.py's EdgeType (REJECTED): keeping a separate model beside triangle, or bolting corpus edges onto a drift-scoped enum, both invite the drift the ontology exists to kill -- differing-semantics-under-a-shared-name is precisely the case one type system resolves (by endpoint object-types) and two type systems let rot; the unifying move is subsumption -- triangle and get_artifact_graph become views over the one graph. OKF subset-validator requiring Doc subtype to be a member of a closed OKF type set (REJECTED): OKF type is deliberately free-form (BI-3: unknown types are not errors) and nothing may consume OKF frontmatter as enforcement (BI-1) -- a subset check would breach both and break shipped OKF v0.30.0; open-absorption (subtype = type verbatim) is the only OKF-legal path. plane: harness|product axis naming (REJECTED): the dormant ontology.schema.json plane field already means product|process (constrains-code|constrains-governance); naming the ownership axis 'plane' would invert a canonical field. MCP-served ontology (DEFERRED, not rejected): the first cut is tool-native (gz verbs); gz mcp serve is a conscious later increment.


## Evidence

<!-- Links to tests, documentation, and other artifacts that prove completion -->

- [ ] Tests: `tests/`
- [ ] Docs: `docs/`

## Alternatives Considered

stdlib graphlib + adjacency + ast substrate (REJECTED, and reverted in-session): graphlib is only a topological sorter -- it cannot image lateral/reachability traversal, which is the entire point of the sonar; stdlib ast is Python-only, wrong for a harness that runs on adopter codebases. This was briefly adopted as a same-day campaign amendment and reverted -- the tree-sitter+networkx floor is GO-attested (Phase-0 airlock-in 2026-07-02) with the STDLIB-FIRST departure rationale already named; the reversal contradicted a ratified decision without new evidence. 3-ADR constellation (REJECTED): splitting corpus/work/source into three cohered ADRs invents cross-ADR coherence machinery (shared namespace, frame-gates-siblings, 1:1 supersession across a set) that a single ADR does not need; blast radius is handled by OBPI decomposition, which KEEL proved lands cleanly; the domains share one substrate and one replay, with no independent release cadence. Parallel typed model / widen triangle.py's EdgeType (REJECTED): keeping a separate model beside triangle, or bolting corpus edges onto a drift-scoped enum, both invite the drift the ontology exists to kill -- differing-semantics-under-a-shared-name is precisely the case one type system resolves (by endpoint object-types) and two type systems let rot; the unifying move is subsumption -- triangle and get_artifact_graph become views over the one graph. OKF subset-validator requiring Doc subtype to be a member of a closed OKF type set (REJECTED): OKF type is deliberately free-form (BI-3: unknown types are not errors) and nothing may consume OKF frontmatter as enforcement (BI-1) -- a subset check would breach both and break shipped OKF v0.30.0; open-absorption (subtype = type verbatim) is the only OKF-legal path. plane: harness|product axis naming (REJECTED): the dormant ontology.schema.json plane field already means product|process (constrains-code|constrains-governance); naming the ownership axis 'plane' would invert a canonical field. MCP-served ontology (DEFERRED, not rejected): the first cut is tool-native (gz verbs); gz mcp serve is a conscious later increment.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.32.0 | Pending | | | |
