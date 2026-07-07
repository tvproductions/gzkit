# AUDIT (Gate-5) — ADR-0.32.0-gzkit-ontology

| Field | Value |
|-------|-------|
| ADR ID | ADR-0.32.0-gzkit-ontology |
| ADR Title | gzkit ontology (object/link plane) |
| ADR Dir | docs/design/adr/pre-release/ADR-0.32.0-gzkit-ontology |
| Audit Date | 2026-07-07 |
| Auditor(s) | pipeline-orchestrator (driver) · spec-reviewer + quality-reviewer (independent) · g0 (operator, attesting) |
| Prior state | Completed (all 7 OBPIs `attested_completed`, gates 1–5 pass) |
| Target state | Validated |

## Feature Demonstration (Step 3 — Fidelity Gate, bound)

The ADR delivers the **object/link plane of the gzkit ontology**: ONE typed
`networkx.MultiDiGraph`, three domain subgraphs (corpus / work / source) plus
OKF Docs, imaged by read-only `gz ontology` verbs and held Tier-B
(derived-never-authority). The bound Fidelity Gate ran each thesis assertion
against the running system:

```text
$ uv run gz adr fidelity ADR-0.32.0
  Assertions: 4
  PASS  gz ontology sense images the current shape          (expected 0, observed 0)
  PASS  gz ontology trace walks vertical + lateral lineage  (expected 0, observed 0)
  PASS  Harness-Purity fence refuses product in harness     (expected 0, observed 0)
  PASS  sense --json emits the rebuild-fidelity self-report (expected 0, observed 0)
  Summary: 4 pass, 0 fail
```

### Capability 1: Image the actual shape (`sense`)

```text
$ uv run gz ontology sense --json  (excerpt)
node_count: 1171   edge_count: 1757
node_types: {PRD: 1, ADR: 261, OBPI: 903, Doc: 6}
seams: 0 structural seam(s)
fidelity: {complete: true, fresh: true, unaccounted_event_types: [], ...}
```

**Why it matters:** The operator can now query the *actual* 1171-node
governance shape instead of reasoning from stale design docs — the exact
"working in the dark" failure this ADR answers. 0 structural seams = the tree
is clean and honestly reports it.

### Capability 2: Walk vertical + lateral lineage with provenance (`trace`)

```text
$ uv run gz ontology trace ADR-0.32.0-gzkit-ontology
  ancestors:   PRD-GZKIT-1.0.0
  descendants: OBPI-0.32.0-01 … 07 (all seven)
  child: declared parent of OBPI-0.32.0-0N (get_artifact_graph children)
  attests: node carries a completion attestation (self-loop)
```

**Why it matters:** A decision that contradicts a GO-attested node now *lights
up* against a computed graph rather than slipping through as a "correction" —
the drift incident that motivated the ADR would have been caught. Edge
provenance ("*why* the graph believes this edge exists") answers the 2am
operator question.

### Capability 3: Confess its own rebuild fidelity (the honesty fence)

`sense --json` emits `fidelity.complete=true, fresh=true,
unaccounted_event_types=[]` across all four domains (corpus/work/source/okf).
The `unaccounted_event_types` list is computed by diffing replayed event types
against the **live `TypedLedgerEvent` discriminator registry** — so a future
ADR that adds a ledger event type surfaces here as `complete=false` instead of
being silently dropped.

**Why it matters:** "A wrong graph is more dangerous than none because it is
trusted." This fence is what lets the airlock certify "every seam seen" without
certifying against a lie.

### Value Summary

The operator can now sweep the real governance shape, trace any node's lineage
with edge provenance, and — crucially — trust that the graph will *confess*
when its replay is incomplete rather than image a stale shape confidently. This
is the keel-up substrate Movement III's HATCH airlock re-sense gate consumes.

## Execution Log

| Check | Command | Result | Notes |
|-------|---------|--------|-------|
| Ledger completeness (L2) | `gz adr audit-check ADR-0.32.0` | ✓ | PASS; 7/7 OBPIs completed w/ evidence; 16 REQ advisories non-blocking → `proofs/` (stdout) |
| Fidelity Gate (bound) | `gz adr fidelity ADR-0.32.0` | ✓ | 4 pass / 0 fail → `proofs/fidelity.txt` |
| Sonar images shape | `gz ontology sense` | ✓ | exit 0; 1171 nodes / 1757 edges → `proofs/live-sonar.txt` |
| Vertical + lateral trace | `gz ontology trace ADR-0.32.0-gzkit-ontology` | ✓ | exit 0; ancestors + 7 descendants + provenance → `proofs/live-sonar.txt` |
| Harness-Purity fence (clean) | `gz validate --ontology-purity` | ✓ | exit 0; seated registry pure |
| Harness-Purity fence (fail-closed) | `tests/test_ontology_purity.py` | ✓ | `test_product_type_in_harness_is_refused` pins breach refusal |
| Rebuild-fidelity self-report | `gz ontology sense --json` | ✓ | `complete=true`, 0 unaccounted → `proofs/sense-json.json` |
| CLI doc coverage | `gz cli audit` | ✓ | 120/120 commands → `proofs/cli-audit.txt` |

## Boundary-Invariant Witness (discharges the "audited at closeout" claim)

The ADR asserts (lines 48–49) that its 5 Boundary Invariants are "audited at
ADR closeout (STRUCTURAL-FENCE proof channel)." Under ADR-0.0.59 the proof
channel is the *presence* of the parent-ADR entry (satisfied). This table
supplies the enumerated per-fence **witness** — the reviewer assessment the
closeout form left implicit — grounded in independent source/test review.

| BI | Fence | Witness | Verdict |
|----|-------|---------|---------|
| #1 | Rebuild fidelity — graph never lies; completeness diffed against the **live** `TypedLedgerEvent` registry, not a hardcoded set | `corpus.py:118-129` introspects the union via `get_args` dynamically; fence `corpus.py:169-173` sets `complete=False` on registry growth; test `test_ontology_corpus.py:206-219` derives its discriminator from the live union (non-vacuous) | ✓ CONFIRMED (load-bearing) |
| #2 | Derived-never-authority — no `gz validate`/gate/closeout consumes the graph | Only read-only `gz ontology` verbs call `project_all`; `--ontology-purity` audits the *static type registry*, never the derived graph; work-domain block enforcement is `enforced=False` advisory | ✓ CONFIRMED, no leak |
| #3 | `sense` images structure only | Falsifier "no un-accounted STRUCTURAL seam"; `test_ontology.py:116-125` pairs the zero-seam floor with a non-vacuity guard (dangling graph → exactly 1 seam) | ✓ CONFIRMED |
| #4 | Harness purity — `ownership:harness` admits only GovZero-universal types | `test_ontology_purity.py` pins breach-refusal (CliVerb-in-harness rejected), clean-pass, and seated-registry purity | ✓ CONFIRMED |
| #5 | OKF absorption stays open — Doc subtype = OKF type verbatim, no subset-validator | `test_ontology_okf.py:39-48` asserts byte-for-byte verbatim incl. mixed-case/spaced `type`; no consumer rejects unknown `type` (honors OKF BI-1/BI-3) | ✓ CONFIRMED |

## Independent Review Verdicts

### spec-reviewer — REQ-tracing (VERDICT: CONCERNS, non-blocking)

- **Load-bearing question CLEAN:** No BEHAVIOR REQ masquerades as
  advisory-uncovered. All 16 advisory REQs are legitimately SUPPORT or
  STRUCTURAL-FENCE per their brief `[kind]` tags.
- Sampled covered BEHAVIOR tests (REQ-02-05, 01-02, 01-04, 03-01, 06-07,
  05-01, 07-06) genuinely assert REQ semantics with non-vacuity guards — no
  string-pins, no tautologies.
- Concern (procedural): the closeout form lacked an enumerated per-fence
  witness. **Discharged** by the Boundary-Invariant Witness table above.

### quality-reviewer — structural coherence (VERDICT: COHERENT)

- **ONE-graph substrate CONFIRMED** (`unified.py:262-268`): domains compose
  in-place onto one `MultiDiGraph`, not parallel structures.
- **BI#1 registry-derived CONFIRMED** (the critical claim) — `corpus.py:118-129`.
- **BI#2 no-leak CONFIRMED** — derived graph never consumed as authority.
- Provenance note (recorded below).
- Honest limitation (disclosed in-code): source/OKF `fidelity.complete` is a
  directory-present boolean (`unified.py:224,244`), not a replay-completeness
  diff — so BI#1's rigorous registry-diff fence protects the **corpus and work**
  vocabularies; source/OKF confess *presence*, not replay fidelity. Consistent
  with the ADR's "structural shape only" posture and disclosed by the
  `honest domain disclosure` commit (GHI #672).

## Provenance Note (governance lesson, tracked + resolved)

The independent structural review established that the ADR's central claim —
*ONE unified graph, three typed domains as subgraphs* — was **not** true at the
moment the 7 OBPIs individually passed their gates. The work/source/OKF
subgraphs were built but uncomposed; `sense` imaged corpus-only. Unification
landed as **corrective work**:

- **GHI #672** [CLOSED] → `0f9aa6be` "compose breadth domains into one graph +
  honest domain disclosure"
- **GHI #674** [CLOSED] → `44d69295` "resolve intra-bundle OKF Doc→Doc links_to
  edges into the graph"

The lesson (recorded, not re-filed — the corrective GHIs are closed):
**per-OBPI gates do not self-certify ADR-level integration.** This is precisely
why the audit ceremony is a distinct COMPLETED→VALIDATED step. The current
runtime is coherent and the fix is structurally sound; VALIDATED is not
premature.

## Summary Table

| Aspect | Status |
|--------|--------|
| Implementation Completeness | ✓ 7/7 OBPIs completed with evidence |
| Fidelity (thesis runs live) | ✓ 4/4 bound assertions pass |
| Structural Coherence | ✓ COHERENT (one graph, three subgraphs, in-place composition) |
| Boundary Invariants (5) | ✓ all 5 witnessed |
| Data Integrity (rebuild fidelity) | ✓ `complete=true`, 0 unaccounted event types; registry-coupled |
| Documentation Alignment | ✓ CLI audit 120/120; mkdocs clean at closeout |
| Risk Items Resolved | ✓ trust-drift fence proven; corrective composition tracked (GHI #672/#674 closed) |

## Evidence Index

- `audit/AUDIT_PLAN.md`
- `audit/proofs/fidelity.txt` — bound Fidelity Gate, 4/4
- `audit/proofs/live-sonar.txt` — live `sense` + `trace` output
- `audit/proofs/sense-json.json` — machine-readable shape + fidelity self-report
- `audit/proofs/cli-audit.txt` — CLI doc coverage 120/120
- Source witnesses: `src/gzkit/ontology/{unified,corpus,graph,purity,work}.py`
- Test witnesses: `tests/test_ontology_{purity,corpus,model,okf,source,work}.py`, `tests/commands/test_ontology.py`

## Recommendations

- **Issue 1 (procedural, non-blocking):** Closeout form lacked per-fence
  witness. **Remedy applied:** Boundary-Invariant Witness table above supplies
  the enumerated reviewer assessment.
- **Issue 2 (disclosed limitation, non-blocking):** source/OKF fidelity is
  presence-only, not replay-diff. **Status:** disclosed in-code and consistent
  with the ADR's structural-only posture (GHI #672 `honest domain disclosure`).
  A future torque-up of source/OKF to a replay-completeness diff would be a new
  increment, not a correction of this ADR's declared intent.
- **No blocking issues found.**

## Attestation

Agent (pipeline-orchestrator driver, with independent spec-reviewer +
quality-reviewer) attests: ADR-0.32.0 is implemented as intended, evidence is
reproducible (proofs co-located under `audit/proofs/`), the bound Fidelity Gate
passes 4/4, all 5 Boundary Invariants are witnessed, and no blocking
discrepancies remain. Human attestation was recorded at each OBPI completion;
the ADR-level audit-validation acceptance is relayed via the operator's verbal
`accept audit` / `verify audit` into the `validated` receipt.

Signed (agent): pipeline-orchestrator — 2026-07-07
Signed (operator): g0 — "accept audit" (2026-07-07), relayed into the `validated`
ledger receipt (`audit_receipt_emitted`, event=validated, attestor=g0).

**Validation-time Layer-1 evidence (fresh ARB receipts, HEAD 44d69295):**

| Category | Receipt | exit_status |
|----------|---------|-------------|
| lint | `arb-ruff-102bc582bb0b4b95850ca76e74dc5c75` | 0 |
| typecheck | `arb-step-typecheck-dd931f0f9a90426aaff3a833e94191f3` | 0 |
| unittest (6804 tests) | `arb-step-unittest-64c803a7decb433d8cea05b8c26c1842` | 0 |
| mkdocs --strict | `arb-step-mkdocs-3d1d903294af4d4f82df638836fbdedf` | 0 |

**Lifecycle verified:** `gz adr report ADR-0.32.0` → Lifecycle **Validated**,
Closeout READY, QC READY, 7/7 OBPIs `attested_completed`. Frontmatter,
derived `adr-status.md` index, and ledger all coherent (`gz validate
--documents --adr-status-fresh` pass).
