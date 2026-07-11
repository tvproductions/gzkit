# Plan — OBPI-0.33.0-02-airlock-in-pipeline-tracer

**Parent ADR:** `ADR-0.33.0-airlock-membrane` (feature / heavy)
**Brief:** `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/obpis/OBPI-0.33.0-02-airlock-in-pipeline-tracer.md`
**Lane:** Heavy · **Sensitivity:** security (auth_boundaries overlap on `obpi_cmd.py`)

## Context

Build the airlock-IN primitive and wire it into pipeline Stage 1. This is the
**landing keystone** of ADR-0.33.0 — all deferred breadth (OBPI-04 mx door,
OBPI-05 permitted-entry, OBPI-06 doctrine-lawful) is gated behind its §5 live
negative control biting un-forced in production config.

Consumes OBPI-01's already-landed layer: `SeamEdge` / `SeamMap` / `Preflight`
(`src/gzkit/airlock/model.py:61,73,89`) and `AirlockInEvent`
(`src/gzkit/events.py:732`). Defines none of them.

Stands on the attested HULL floor: `gz ontology reach` →
`compute_reach(graph, node_id)` (`src/gzkit/commands/ontology.py`), backed by
`OntologyGraph.reachable_from` returning `set[str]`. No new runtime dependency.

## Load-bearing design decisions

### D1 — What makes a seam edge `accounted`? (the choice that decides whether the airlock bites)

The brief pins `bodies` = the declared `## Allowed Paths` (REQ-02) and pins
`push_edges` = `gz ontology reach` output. It does **not** define how an edge
becomes `accounted`. `reach` returns *artifact ids* (`ADR-…`, `OBPI-…`);
Allowed Paths are *file paths*. They do not share a key, so `accounted` cannot
simply mean "the edge target is in `bodies`."

**Chosen (A): the brief IS the declaration.** An edge is `accounted` iff its
target id appears anywhere in the target brief's text. To account for a seam,
the declarer names it in the brief — the same act the brief's own Discovery
Checklist and Denied Paths already perform. Mechanical, L1-sourced, no schema
change, no inference.

Rejected:

- **(B) new `accounted_seams:` frontmatter list.** Cleanest long-term, but the
  brief schema and airlock models are OBPI-01's surface — Denied Paths fences
  them. A schema change here is scope creep into a sibling.
- **(C) accounted iff target is the parent ADR or a declared sibling.** Too
  narrow. Every real reach edge would resolve to "accounted" by construction,
  so the gate could never refuse — a membrane that cannot bite (parent ADR
  § Negative #1, the theater pre-mortem).

### D2 — Reconciling REQ-03 (GO structurally unreachable) with REQ-05 (captain override may pass)

`airlock_enter(..., override=None)` — the **default, un-overridden path** — can
never return `PROCEED` while `seam_map.unaccounted` is non-empty. The override
is a separate, explicit, logged, revocable input; it is not a default and not a
kwarg the NC can trip over. The §5 negative control invokes the un-overridden
production path, so "structurally unreachable" is literally true for the path
the NC exercises. `blast_radius` is consulted only on a fully-accounted map
(delegation dial, REQ-08), never as an override.

### D3 — Port shape (hexagonal rule 4: never name the technology; take a parameter)

`airlock_enter(*, reach_fn: Callable[[str], list[str] | None] = _default_reach, ...)`.
The core reaches the ontology only through the injected callable, so it is
exercisable with no projection built (Cockburn rule 6). One adapter →
no `Protocol` extracted yet (hexagonal rule 5: formalize on the second adapter).

### D4 — Gate function placement

`check_airlock_in_gate(obpi_id, brief_path, project_root) -> list[str]` lives in
`src/gzkit/pipeline_runtime.py`, mirroring `check_reconcile_receipt_gate`
(same signature shape, same contract: empty list = pass, non-empty = blockers,
caller raises `SystemExit(3)`). It is **invoked** from `obpi_pipeline_cmd` in
`src/gzkit/commands/obpi_cmd.py`, adjacent to the existing
`check_reconcile_receipt_gate` call at line 659 — because `pipeline_runtime.py`
holds Stage-1 *helpers*, never the executor. A gate authored but never invoked
is the ORPHAN that REQ-09 forbids.

## Files

**Create**

- `src/gzkit/airlock/enter.py` — the primitive, seam-map compute, refusal
  builder, override, `_ensure_airlock_claims_registered()`
- `src/gzkit/commands/airlock.py` — `airlock_in_cmd`, mirroring `commands/ontology.py`
- `tests/test_airlock_enter.py` — `@covers` REQ tests incl. the §5 live NC
- `features/airlock.feature` — Gate-4 BDD scenario
- `docs/user/manpages/airlock.md` — Gate-3 verb doc

**Modify**

- `src/gzkit/cli/parser_governance.py` — `airlock` group + `in` subparser (mirror `p_ontology`)
- `src/gzkit/cli/parser_handler_manifest.py` — `airlock_in_cmd` → `gzkit.commands.airlock`
- `src/gzkit/pipeline_runtime.py` — `check_airlock_in_gate` (additive)
- `src/gzkit/commands/obpi_cmd.py` — Stage-1 call site (import + invoke)
- `src/gzkit/enforcement.py` — wire `_ensure_airlock_claims_registered()` into
  `_ensure_production_claims_registered()` (add THIS claim source only)

**Untouched neighbor:** `src/gzkit/airlock/__init__.py` — already seated by OBPI-01.

## Steps (one Red-Green-Refactor increment per REQ; `req_atomic` declared)

Every step: write ONE minimal test → run it → confirm an **assertion-level**
failure with the expected message (an `ImportError` is a *false red*; seat an
importable stub first) → simplest code to green → refactor.

1. **REQ-01 — three-beat + closed decision set.**
   Test: `airlock_enter` runs DECLARE → PING → RECONCILE → gate; returns a
   `Preflight` whose `decision` ∈ `{proceed,pause,hold,revert}`; PING result is
   stored as advisory input, never consumed as the verdict; the decision is not
   recorded as a completion attestation (BI #3).
   Code: `airlock_enter(...)` skeleton + `_ping(reach_fn, target)`.

2. **REQ-02 — two-layer seam-map.**
   Test: real entry → `seam_map.bodies` == declared Allowed Paths set (read via
   `governance.brief_path_validity.extract_allowed_paths`, L1, never inferred);
   a known reach dependent appears as a `push_edge`; assert **no** statistical
   body inference is performed (laundered-blind-spot fence, § Negative #2).
   Code: `compute_seam_map(...)` — `bodies` from L1; `push_edges` from
   `reach_fn`; `pull_edges` from brief + parent-ADR invariants.

3. **REQ-03 — un-accounted seam ⇒ GO structurally unreachable (the §5 live NC).**
   Test: omit a real `reach` push edge from the declared seam-set of a REAL
   entry → `airlock_enter` cannot return `PROCEED` (`hold`/`pause`).
   Code: the un-accounted → block rule; then register the claim:
   `_AIRLOCK_CLAIM_IDS = frozenset({"airlock-in-unaccounted-seam"})`,
   `_build_unaccounted_seam_violation()` (fixture), `_ep_airlock_unaccounted_seam()`
   (production entrypoint — returns truthy when the airlock refuses GO; **no
   forcing kwarg pre-bound**), `_ensure_airlock_claims_registered()` mirroring
   `mx/proxy_reality.py:146` exactly (`set_known_claims(_KNOWN_QC_CLAIM_IDS | _AIRLOCK_CLAIM_IDS)`,
   idempotent re-registration guard).

4. **REQ-04 — diagnostic refusal.**
   Test: refusal for a known un-accounted seam names (a) the exact seam id,
   (b) provenance (push-from-reach vs pull-from-invariant; `LAW` vs `OBSERVED`),
   (c) the one-command re-sense `gz ontology resense <target>`.
   Code: `build_refusal(seam_map, target) -> str`. Never a bare NO-GO
   (§ Negative #5, the 2am finding).

5. **REQ-05 — logged, revocable captain override; blast_radius is the delegation dial.**
   Test: an override books an L2 event carrying the overridden seam + attestor;
   the override can be revoked; a non-accounted seam is **not** auto-proceeded by
   `blast_radius` alone.
   Code: `Override` input + L2 emission; `blast_radius` consulted only on a
   fully-accounted map.

6. **REQ-06 — Stage-1 wiring + `airlock_in` L2 event.**
   Test: the Stage-1 seam calls the primitive (the gate is wired, not an orphan);
   a transit books an `airlock_in` event to L2; **no** write to L1 canon (BI #1).
   Code: `check_airlock_in_gate` in `pipeline_runtime.py`; import + invoke in
   `obpi_pipeline_cmd` adjacent to `check_reconcile_receipt_gate`.

7. **REQ-07 [SUPPORT] — §5 claim registered and wired (no ORPHAN).**
   Proof channel is **not** a `@covers` test (ADR-0.0.59): an
   `enforcement_claim_verified` ledger event for the airlock claim at
   meta-validator run, AND `uv run gz validate --qc-binding` exit 0 with the
   airlock claim among the verified set.
   Code: add `_ensure_airlock_claims_registered()` to
   `_ensure_production_claims_registered()` in `enforcement.py:302`
   (this claim source only; the `mx` wiring stays untouched).

8. **CLI + docs + BDD.** `airlock in` verb (`commands/airlock.py`, parser group,
   handler manifest); `docs/user/manpages/airlock.md` with a real invocation and
   observed output; `features/airlock.feature` exercising the un-accounted-seam
   NO-GO through `airlock in`.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz validate --sensitivity
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_airlock_enter -v
uv run gz validate --qc-binding
uv run -m behave features/airlock.feature
uv run gz covers OBPI-0.33.0-02-airlock-in-pipeline-tracer --json
uv run gz arb red --req REQ-0.33.0-02-03 --obpi OBPI-0.33.0-02-airlock-in-pipeline-tracer
```

## Notes — Step 6a disclosures (plan-before-exploration ordering)

**Destination-in-mind.** Before writing this plan I had already formed the shape:
a pure `airlock_enter` in a new `enter.py`, an injected `reach_fn` port, a gate
function in `pipeline_runtime.py` mirroring `check_reconcile_receipt_gate`, and a
`@enforces` claim copied structurally from `mx/proxy_reality.py`. Exploration
confirmed that shape rather than generating it — the brief's Allowed Paths and
Discovery Checklist name those exact anchors, so the plan is substantially
transcribed from the brief. The one thing exploration genuinely *changed*: I
assumed the Stage-1 call site was in `pipeline_runtime.py` because the brief said
so; reading the code showed it is `obpi_cmd.py:659`, which forced the brief
amendment (D4) and the `sensitivity: security` declaration.

**Rejected alternatives.**

- Fold `airlock_enter` into `check_reconcile_receipt_gate` rather than adding a
  sibling gate — rejected: the brief forbids changing existing Stage-1 gate
  behavior, and it conflates two independent gates.
- Have the airlock derive `bodies` by statistical/community inference over the
  reach graph — rejected on doctrine: § Negative #2, the laundered blind spot;
  `graspologic` is ruled out (3.13-incompatible + a category error in a gating
  path), and `networkx.algorithms.community` is L3-advisory-only, never gating.
- Register a second negative-control framework for the airlock rather than
  reusing the single `@enforces` primitive — rejected: parent ADR § Boundary
  Invariants #6, one enforcement-claim surface, not two.
- Emit the acknowledge-and-decide gate as an attestation event — rejected as a
  doctrine violation: BI #3, the sacrosanct word stays reserved for completion.

**Open question carried to the operator:** D1 (`accounted` semantics) is a design
choice the brief does not pin. Confidence < 90%; surfacing before Stage 2 per
AGENTS.md § Behavior Rules — Always #7/#8 and the Stage 1→2 Confidence Gate.
