# ADR-0.33.0 bounded intent trace — 2026-09-12

Persona: spec-reviewer; independent, evidence-based. Read-only sample requested by the parent after the three earlier audit axes. Reference HEAD: `464dd4ff8fa2ee12d98afe99a867280e1b82b431` (observed `git rev-parse HEAD`). No other ADR's implementation intent was sampled. No source edits, ledger writes, locks, TASKs, pipeline launch, or attestation actions performed by this reviewer.

## Evidence order and lifecycle

Read the complete 206-line `docs/design/adr/pre-release/ADR-0.33.0-airlock-membrane/ADR-0.33.0-airlock-membrane.md` before examining implementation for this sample. Its Decision is line 23, six-item Feature Checklist lines 118–123, and explicit calibration qualification line 36. Skills read before commands: `gz-intent-trace`, `gz-context`, `gz-adr-status`, `gz-airlock` (canonical `.gzkit/skills/*/SKILL.md`). The context bundle was generated, but is not represented as a fully read bundle.

Executed successfully (exit 0):

- `UV_CACHE_DIR=/tmp/gz-health-uv-cache uv run gz context ADR-0.33.0` → `/tmp/gz-health-context-033.md`.
- `UV_CACHE_DIR=/tmp/gz-health-uv-cache uv run gz adr status ADR-0.33.0` → `/tmp/gz-health-status-033.txt`.

Status observed: `heavy | Validated | validated | 6/6 | READY | READY`; all six OBPIs `attested_completed`, brief `completed`, done `yes`. These are Layer-3 summaries, corroborated by Layer-2: `.gzkit/ledger.jsonl:12932` is ADR `attested`, status `completed`, by `g0`; line 12939 records Proposed→Completed; line 12948 is the `validated` audit receipt, attestor `g0`, 2026-07-12, anchor commit `89c5ee9`. The chosen terminal brief has its completed, human-attested receipt at line 12501: `OBPI-0.33.0-01-airlock-data-model-and-events`, `obpi_completion=attested_completed`, anchor `b786fb8`. The historically reused numeric ADR prefix has older unrelated ledger records; conclusions use the exact `airlock-membrane` identity, not prefix matches.

## Three representative claims

### 1. IN computes meaningful declared/observed seams and a decision — PARTIAL, explicitly staged

Extracted claim, ADR line 23: “AIRLOCK-IN is a three-beat, not a single compute: (1) DECLARE intent + expectation; (2) PING the shape via the HULL sonar”; “PUSH edges come from gz ontology reach (computed blast radius); PULL edges from the brief + parent-ADR invariants.” Feature Checklist item 2 (line 119) names the IN pipeline tracer, live negative control, parent invariants, and override handling.

Governing qualification, line 36: “A real entry therefore computes an empty seam-map and always PROCEEDs.” It expressly makes Stage 1 “diagnostic-only” until meaningful reach/pull calibration lands, and calls calibration a named successor increment. This qualification must travel with the broader Decision; the final calibrated operational claim is not fulfilled merely because the tracer shipped.

Implementation read: `src/gzkit/airlock/enter.py:48` derives default reach from the projected ontology; `:70–94` reads the brief/Allowed Paths and reconciles reach, with `parent_invariants=()` by default. `:120–155` gives observed push and LAW pull provenance and considers an edge accounted when its target string occurs in brief text. `:158–170` returns HOLD for unaccounted edges unless a live override is supplied. The wired pipeline helper `src/gzkit/pipeline_runtime.py:589–625` never supplies parent invariants; `src/gzkit/commands/obpi_cmd.py:740–752` renders any refusal as a warning. CLI `src/gzkit/commands/airlock.py:94–99` calls the same primitive and deliberately supplies no ledger in dry-run.

Exact observed command and stdout, exit 0:

```text
UV_CACHE_DIR=/tmp/gz-health-uv-cache uv run gz airlock in --target OBPI-0.33.0-01 --phase build --dry-run --json
{
  "target": "OBPI-0.33.0-01",
  "phase": "build",
  "decision": "proceed",
  "authority": "captain",
  "blast_radius": 0,
  "seam_map": {
    "bodies": 12,
    "push": 0,
    "pull": 0,
    "unaccounted": 0
  },
  "unaccounted": []
}
```

Verdict: the real CLI executes the shipped three-beat mechanism and declares 12 footprint bodies; this sampled production input gives no meaningful join accounting. Neither zero unaccounted seams nor exit 0 proves safety, calibration, or orientation completeness. The live NC implementation at `enter.py:244–264` compares controlled accounted/unaccounted briefs with an injected reach; it exercises production decision code, but does not prove meaningful production ontology reach. No NC was rerun here and no claim about current NC results is made.

Owning route: remaining real-entry calibration is corrective fulfillment under ADR-0.33.0 and its explicitly staged frontier; do not invent a fresh pool ADR or start an OBPI. This trace does not verify the implementation or completion of a successor outside the sample.

### 2. OUT accounts for disturbance, presents choices, and recommends fresh work — PARTIAL diagnostic delivery

Extracted claim, ADR line 23: “AIRLOCK-OUT (co-equal): drift-diff push-minus-pull -> findings + recommendations -> a decision menu (leave-it-be | modify | repair | adjust-maps) -> route any discovered correction as a FRESH transit through the right door (never smuggled inline; 'better housekeeping/bookkeeping') -> log to L2.” Checklist item 3 (line 120) names the OUT tracer, drift-diff/menu, fresh routing and Stage 5.

Implementation read: `src/gzkit/airlock/exit.py:140–179` computes a symmetric difference between fact and intent target sets; `:182–231` turns push edges into fresh-transit recommendations and pull edges into map-amendment proposals. `:234–273` extracts bodies, compares current reach with supplied parent invariants, and returns findings/menu/routing/proposals. Bodies are counted for the event; they do not make the comparison an observed before/after filesystem diff. No prior entry snapshot is consumed by this function. `src/gzkit/pipeline_runtime.py:628–662` omits parent invariants and reports this as the same deferred calibration frontier. `src/gzkit/commands/obpi_stages.py:506–529` prints findings as warnings.

Exact observed command and stdout, exit 0:

```text
UV_CACHE_DIR=/tmp/gz-health-uv-cache uv run gz airlock out --target OBPI-0.33.0-01 --dry-run --json
{
  "target": "OBPI-0.33.0-01",
  "verdict": "clean",
  "decision_menu": [
    "leave_it_be",
    "modify",
    "repair",
    "adjust_maps"
  ],
  "drift": [],
  "findings": [],
  "routing": [],
  "proposals": []
}
```

Verdict: menu and reporting are live, without inline mutation. The observed CLEAN is the empty comparison result, not proof that no disturbance occurred. Nonempty production finding/routing behavior was not exercised by this preview. Source also limits routing: `exit.py:212–223` always recommends the pipeline door for a push finding; it does not classify corrective versus intentional work. Therefore the broad “right door” promise is not certified by this sample. The permitted-entry door separately presents pipeline and MX criteria (`commands/permitted_entry.py:255–268`); that is not evidence that OUT's fixed recommendation selects the right door.

Owning route: account-for-disturbance calibration and any OUT routing correction remain under ADR-0.33.0. Preserve the distinction between a returned recommendation and actual transit execution; no automatic repair or OBPI dispatch is authorized by this finding. No new GHI was filed by this read-only reviewer; parent owns any tracking action.

### 3. One reusable primitive records encounters without spending Gate-5 attestation — QUALIFIED PASS for inspected wiring

Extracted claim, ADR line 23: “mx and permitted-entry adapt to the airlock; the airlock is never forked per-door”; “the airlock ALWAYS logs what it encounters to the L2 ledger ... it NEVER rewrites L1 canon.” Boundary Invariant 3 at lines 61–64 explicitly separates acknowledge-and-decide from completion attestation. Checklist items 1, 4 and 5 name the data/event layer, MX door and permitted-entry door.

Inspected common producers: `enter.py:173–192` appends `airlock_in` with target, decision and unaccounted targets; `exit.py:285–329` appends `airlock_out` with target, verdict, drift/routing, or ABORTED on a failed exit. The successful exit path returns proposals, not L1 writes. `airlock/model.py:16–119` has separate closed decision/verdict/provenance model vocabulary.

Consumers actually call those shared functions: pipeline `pipeline_runtime.py:618–622,653–657`; MX `commands/mx_cmd.py:152–192` called at enter `:280` and successful guarded exit `:383`; permitted entry `commands/permitted_entry.py:237–280` calls IN then OUT in `finally`. The latter displays the declared footprint and proposes fresh routing; it never performs an inline repair. No inspected airlock producer emits a completion-attestation event.

Existing live Layer-2 evidence, read without appending: 63 `airlock_in` and 21 `airlock_out` events at this observation. Recent exact examples are `.gzkit/ledger.jsonl:16373–16374`, target `permitted-entry:.gzkit/skills/gz-health-audit/SKILL.md`, IN `decision=proceed, unaccounted=[]`, OUT `verdict=clean, drift=[], routing=[], bodies=1`. Counts are vocabulary/producer evidence, not a claim that all historical transits are paired. The preceding pair at lines 16367–16368 concerns `permitted-entry:docs/governance/capability-control-review-2026-09-12.md`.

Limits: MX returns before calling the primitive when no brief-bearing scope resolves (`mx_cmd.py:152–158,182–188`); its source explicitly names brief-less DECLARE as deferred, and its production reach is deliberately empty (`:160,:190`). The sampled brief text explicitly narrows per-door ceremony calibration as residual (`OBPI-0.33.0-04-airlock-mx-door.md:95–98`). Thus shared wiring and distinct event types pass, while total every-entry coverage is not certified. Each event's `id` is the target, not a unique transit identity (`enter.py:192`, `exit.py:305,:322`); arbitrary concurrent/repeated-target pairing cannot be proven from identity alone. The ADR does not explicitly prescribe a UUID, so absence of one alone is not classified as an independent intent violation. Earlier audit-axis pairing findings retain their own evidence and disposition.

Owning route: substantive every-entry/accountability gaps belong to ADR-0.33.0's membrane intent. The qualified pass does not reopen completed briefs or authorize OBPI machinery.

## Broader canon and verdict boundary

`AGENTS.md:365` gives the operator's four airlock purposes: awareness/synthetic memory, movement control, focus/orientation/contamination, and monitoring disturbance. It expressly calls the missing purposes in ADR-0.33.0 a CAPTURE GAP, not a change in purpose, and rejects treating the airlock as a verification gate. `AGENTS.md:366` says transit and session handoff cooperate to provide synthetic memory. These binding statements prevent using the ADR's narrower wording or successful diagnostic exits as proof of the complete purpose.

This sample confirms the staged diagnostic primitive and its limited live output. It does not certify resident project orientation, contamination detection, calibrated blast-radius accounting, or cross-session memory cooperation. The canon itself tracks the capture gap under the airlock's existing intent; this reviewer neither inferred those purposes were abandoned nor read a later ADR to claim they shipped. The correction route remains the owning ADR and existing operator-authorized work, not new feature design or unrequested OBPI execution. No external issue state was inferred.
