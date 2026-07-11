# Plan — OBPI-0.33.0-03-airlock-out-pipeline-tracer

**OBPI:** OBPI-0.33.0-03-airlock-out-pipeline-tracer
**Parent ADR:** ADR-0.33.0-airlock-membrane
**Lane:** Heavy
**Mode:** subagent-dispatch (default)

## Context

Airlock-OUT is the co-equal exit half of the ONE extracted airlock primitive
("same shape both ways"). airlock-IN (OBPI-02) shipped `airlock_enter` in
`src/gzkit/airlock/enter.py` + `check_airlock_in_gate` in `pipeline_runtime.py`
+ the `gz airlock in` verb; airlock-OUT mirrors that geometry at the pipeline
Stage-5 exit membrane. It consumes OBPI-01's models (`SeamEdge`, `SeamMap`,
`DriftDiff`, `Verdict`, the `airlock_out` event) and defines the NEW closed
`ExitDecision` menu + fresh-transit routing in `exit.py`.

Parent ADR § Decision (airlock-OUT clause, verbatim — the contract):
> AIRLOCK-OUT (co-equal): drift-diff push-minus-pull -> findings +
> recommendations -> a decision menu (leave-it-be | modify | repair |
> adjust-maps) -> route any discovered correction as a FRESH transit through
> the right door (never smuggled inline; 'better housekeeping/bookkeeping') ->
> log to L2.

Tracer discipline (mirrors IN): the primitive proves the MECHANISM (drift-diff
classification bites on fixtures); the wired Stage-5 call site is
DIAGNOSTIC-ONLY (logs findings as warnings, never `SystemExit`). Real-entry
calibration (WWHTBT-a) is the named successor, deferred past the tracer.

## Step 6a — Plan-Before-Exploration disclosures (required)

**Destination-in-mind:** Before exploring I intended to mirror airlock-IN 1:1 —
an `airlock_exit` entrypoint in `exit.py` paralleling `airlock_enter`, a
`check_airlock_out_gate` paralleling `check_airlock_in_gate`, and an `out`
subcommand paralleling `in`. Exploration confirmed the mirror and additionally
surfaced two brief-reality drifts (the Stage-5 executor lives in
`obpi_stages.py`, not `pipeline_runtime.py`; the manpage is per-subcommand
`airlock-out.md`, not a shared `airlock.md`) — both amended under operator
approval before this plan.

**Rejected alternatives:** (1) Define `ExitDecision` in `model.py` — REJECTED:
`model.py` is OBPI-01's, DENIED here; the brief explicitly scopes `ExitDecision`
to `exit.py`. (2) Reuse `model.py`'s `Verdict` enum AS the decision menu —
REJECTED: `Verdict` (clean|block|surface|resolve) is drift adjudication, a
different axis from the operator `ExitDecision` menu (leave_it_be|modify|repair|
adjust_maps); conflating them collapses two distinct concepts. (3) Wire the
Stage-5 call only into `pipeline_runtime.py` and drive the test there directly —
REJECTED: that produces an orphan gate the ADR's un-accounted-seam doctrine and
airlock-IN's own anti-orphan test reject (this drove the operator escalation).
(4) Fail-close the Stage-5 gate on drift — REJECTED: mirrors IN's deferred
calibration; a mis-calibrated exit gate would 2am-wall a real pipeline.

## Files

**CREATE:**
- `src/gzkit/airlock/exit.py` — the airlock-OUT primitive.
- `tests/test_airlock_exit.py` — `@covers` REQ tests (RGR).
- `docs/user/manpages/airlock-out.md` — per-subcommand manpage (H1 `# gz airlock out`).

**MODIFY (additive, surgical):**
- `src/gzkit/commands/airlock.py` — add `airlock_out_cmd` (verify OBPI-02's `airlock_in_cmd` in same edit — coupled).
- `src/gzkit/cli/parser_governance.py` — add `out` subparser under the `airlock` noun.
- `src/gzkit/cli/parser_handler_manifest.py` — map `airlock_out_cmd` → `gzkit.commands.airlock`.
- `src/gzkit/pipeline_runtime.py` — add `check_airlock_out_gate` helper adjacent to `check_airlock_in_gate`.
- `src/gzkit/commands/obpi_stages.py` — invoke `check_airlock_out_gate` in `_run_pipeline_sync_stage` at the exit membrane (diagnostic warning).
- `docs/user/manpages/index.md` — add `gz airlock out` row.
- `config/doc-coverage.json` — add `"airlock out"` coverage entry.
- `src/gzkit/governance/trust_audits/cli.py` — add `_NO_SKILL_VERBS["airlock out"]`.
- `features/airlock.feature` — add `gz airlock out` smoke scenarios.
- `docs/user/runbook.md`, `docs/governance/governance_runbook.md` — verb-resolution mentions iff cli-alignment requires.

## Steps (Red-Green-Refactor, one behavior per cycle)

Design of `exit.py` (shapes defined here, consuming OBPI-01 models):
- `ExitDecision(StrEnum)` = closed `{leave_it_be, modify, repair, adjust_maps}`.
- `Door(StrEnum)` = `{pipeline, mx, permitted-entry}` (fresh-transit targets).
- `FindingKind(StrEnum)` = `{wrecked_something, broken_contract}`.
- `Finding(BaseModel frozen)` = `edge: SeamEdge`, `kind: FindingKind`, `recommendation: str (min_length=1)`.
- `FreshTransit(BaseModel frozen)` = `door: Door`, `correction: str`, `smuggled: bool = False`.
- `LawProposal(BaseModel frozen)` = `surface: str`, `proposal: str` (L1 amendment PROPOSED, never written).
- `ExitReport(BaseModel frozen)` = `drift_diff: DriftDiff`, `findings`, `decision_menu: tuple[ExitDecision,...]`, `routing: tuple[FreshTransit,...]`, `proposals: tuple[LawProposal,...]`.
- `EXIT_DECISION_MENU: tuple[ExitDecision,...]` = the four, in order (the closed menu constant).

1. **REQ-01 [BEHAVIOR] — drift-diff push-minus-pull.** RED: fixture two-graph
   with exactly one un-matched FACT edge (OBSERVED, no intent) and one un-matched
   INTENT edge (LAW, no fact); assert `wrecked_something` + `broken_contract`
   findings emitted with correct classification; assert a fully-matched two-graph
   yields empty drift. GREEN: `compute_drift_diff(fact_edges, intent_edges)` →
   `DriftDiff`; fact-target − intent-target = wrecked, intent-target − fact-target
   = broken, intersection = clean; `Verdict.CLEAN` when empty else `Verdict.SURFACE`.

2. **REQ-02 [BEHAVIOR] — closed decision menu + recommendations.** RED: assert
   `EXIT_DECISION_MENU` member-set is EXACTLY `{leave_it_be, modify, repair,
   adjust_maps}` (a fifth/renamed member fails — bites on business-logic change);
   assert every emitted `Finding.recommendation` is non-empty. GREEN: define
   `ExitDecision` closed enum + `EXIT_DECISION_MENU`; `build_findings` attaches a
   non-empty recommendation to each drift edge.

3. **REQ-03 [BEHAVIOR] — fresh-transit routing, never smuggled.** RED: drive a
   drift-diff carrying a discovered correction; assert `airlock_exit` returns a
   `FreshTransit` naming the correct `Door`; assert ZERO in-sortie mutation of the
   discovered surface (no file writes beyond L2). GREEN: `route_fresh_transit`
   maps a finding → `FreshTransit(door=..., smuggled=False)`; `airlock_exit`
   performs no filesystem write except the L2 append.

4. **REQ-04 [BEHAVIOR] — always logs exactly one airlock_out; Stage-5 wired.**
   RED: drive `check_airlock_out_gate` (via `pipeline_runtime` re-export); assert
   EXACTLY one `airlock_out` event appended to the ledger per transit (computed
   drift-diff with no event fails); anti-orphan: assert `hasattr(obpi_stages,
   "check_airlock_out_gate")` (obpi_stages invokes it). GREEN: `_book_exit`
   emits one `airlock_out` LedgerEvent (mirror `_book_transit`);
   `check_airlock_out_gate` in `pipeline_runtime.py` runs `airlock_exit`;
   `_run_pipeline_sync_stage` invokes it at the exit membrane.

5. **REQ-05 [BEHAVIOR] — never writes L1 canon.** RED: run `airlock_exit`
   against a fixture surfacing a canon-amendment recommendation; assert zero
   mutations to any L1 surface (ADR/invariant/canon file) — returns a
   `LawProposal`, never a write. GREEN: proposals are frozen objects returned in
   `ExitReport.proposals`; `airlock_exit` opens no L1 file for writing.

6. **CLI + coupling surfaces (Gate 3 docs / skill-alignment / doc-coverage /
   Gate 4 BDD).** `airlock_out_cmd` mirrors `airlock_in_cmd` (diagnostic-only,
   `--json`/`--dry-run`, exit 0 except unresolvable brief → 1); `out` subparser +
   manifest entry; `airlock-out.md` manpage; `index.md` row; `doc-coverage.json`
   entry; `_NO_SKILL_VERBS["airlock out"]`; `features/airlock.feature` scenarios.
   Run `uv run gz cli audit` (exit 0) as the mechanical check.

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run gz cli audit
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.test_airlock_exit -v
uv run gz covers OBPI-0.33.0-03-airlock-out-pipeline-tracer --json
```

## Notes

- Allowlist amended twice under operator approval (2026-07-11, Gate Friction):
  (a) `obpi_stages.py` as the Stage-5 executor call site; (b) the full
  `gz airlock out` docs-coupling footprint (per prior insight's 9-point CLI
  checklist). Both improvement insights appended to agent-insights.jsonl.
- `sensitivity` stays absent: none of the allowed paths (incl. `obpi_stages.py`)
  match a registered security surface.
- Diagnostic-only at the Stage-5 seam; real-entry calibration is deferred
  (WWHTBT-a), not claimed done here.
