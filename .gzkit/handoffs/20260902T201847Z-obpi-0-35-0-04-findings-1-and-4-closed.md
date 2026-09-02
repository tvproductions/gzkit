---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-02T20:18:47Z'
agent: claude-code
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: 66d15068-b58b-4c7b-86b4-d8e072092658
continues_from: .gzkit/handoffs/20260902T190607Z-obpi-0-35-0-04-stage4b-refuted.md
---

## Current State Summary

CHECKPOINT for OBPI-0.35.0-04-section-ownership-and-ratchet (parent
ADR-0.35.0-canon-entry-corpus-landing, Heavy lane) under gz-obpi-pipeline. Lock HELD
(agent=claude-code-9de7e7a3). Pipeline marker active. Bookmarking mid-flight, NOT
departing, so this CHECKPOINT does not discharge the lock release.

PIPELINE POSITION: Stage 2 fix cycle, working down a Step-4b REFUTED verdict. Stage 5
has never been entered and no attestation has been solicited.

STAGE 4b RETURNED REFUTED (receipt arb-step-codexadversary-f7a101da3ba3498e94249f2bdb39969f,
tier 1 Codex, exit_status 0). Five findings: four [high], one [medium]. Two are now
FIXED and verified; three remain.

FINDING 1 FIXED — `record_unowned_total` emitted a ledger event announcing a new
ratchet floor and never wrote it to disk. It now writes the declaration BEFORE the
ledger append. The adversary's own probe was re-run and now agrees:
{"returned_floor": 40, "persisted_after_record": 40, "ledger_new_floor": 40, "agree": true}
(it previously read persisted_after_record 100 against ledger_new_floor 40). A new test
patches the declaration write to fail and asserts NO ledger event is emitted — the
invariant is that a witness must never outlive the state it witnesses. `declaration_path`
was also lifted into `ownership.py` as the single path vocabulary; `unown.py` imports it.

FINDING 4 FIXED — a direct hand-edit of the declaration could raise the ratchet floor
with no attestation, so `gz content unown` was only the SUPPLIED raise path, not the ONLY
one. Operator ruled the mechanism: an attested TRANSITION CHAIN, not a floor-coherence
recompute. `section_ownership.json` and `OwnershipDeclaration` gained a REQUIRED
`floor_event_id`; `load_declaration(path, surface_text, root)` now resolves it against
`.gzkit/ledger.jsonl` and fail-closes unless the named event's `new_unowned_byte_floor`
equals the stored floor. A null id is permitted ONLY for a genesis declaration whose floor
provably equals its own summed unowned spans — without that half, an attacker would
hand-raise the floor AND null the id and walk through. Verified directly: legitimate
genesis LOADS (the control); hand-raise with a null id is REFUSED; hand-raise naming a
nonexistent event is REFUSED.

MEASURED GREEN AT CHECKPOINT: full suite 9205 pass
(arb-step-unittest-0971ef3ee70b4cc28afd471502ccda5c, exit_status 0); tests.content.
test_ownership 30 pass (24 at session start); tests.commands.test_content_unown 10 pass;
ruff clean; behave scoped to @REQ-0.35.0-04-04,@REQ-0.35.0-04-05 gives 5 scenarios and
29 steps, 0 failed. `.gzkit/ownership/AGENTS.md.json` carries 22 sections, 10
corpus-owned, floor 8637, floor_event_id null, is genesis-coherent (summed unowned spans
8637) and validates against its schema.

STEP 4b HAS NOT BEEN RE-RUN, deliberately. Finding 2 is still live and touches the same
two files, so the adversary must run ONCE against a tree that can actually clear it
rather than burn a seven-minute pass on a tree already known to be refuted.

## Important Context

THE THREE REMAINING ADVERSARY FINDINGS, verbatim anchors. Read these before touching the
code.

FINDING 2 [high] — `gz content unown` is non-atomic and loses concurrent transitions
(`src/gzkit/commands/content/unown.py`). Unlocked whole-file read-modify-write. A forced
concurrent run had both operations exit 0 and emit success events while final state
retained only one. IT IS NOW COUPLED TO FINDING 4's FIX: because the declaration carries
a `floor_event_id`, a ledger append that fails after the declaration write leaves a
declaration naming an event that does not exist, and the loader fail-closes on it. That is
CORRECT and was designed in deliberately — do NOT add a "tolerate a missing event" escape
to soften it. Recovery from that partial write IS finding 2's work: atomic file
replacement plus a recoverable transaction tying declaration version to ledger event.

FINDING 3 [high] — the claimed REQ-08 validator never reads the artifact
(`src/gzkit/commands/validate_cmd.py:923-949`). `gz validate --documents` validates
manifest-declared Markdown and the exemplar corpus, never `.gzkit/ownership/*.json`. A
probe containing malformed ownership JSON returned documents_error_count 0. This was
DEMONSTRATED, not merely argued, during finding 4's repair: for a window the schema listed
`floor_event_id` as required while the committed artifact lacked it, so the day-one
artifact did not validate against its own schema and nothing said a word. REQ-08's SUPPORT
proof channel therefore reports `pass` without validating anything.
NEEDS AN OPERATOR RULING BEFORE ANY REPAIR: `validate_cmd.py` is NOT in this brief's
Allowed Paths, and a ratchet-coherence validator may belong to OBPI-0.35.0-06 (the
`--rendition-lineage` gate) rather than here. Surface that overlap when asking; never
widen the allowlist unilaterally.

FINDING 5 [medium] — REQ-07's covering test cannot detect a stored day-one snapshot
(`tests/content/test_ownership.py`). It derives its expectation from the same primitives
as production, so substituting a stored snapshot for day-one computation still passed the
whole class. The adversary names this its own weakest point: an evidence-quality defect,
not proof the arithmetic is wrong.

FIXING FINDING 4 CAUGHT DRIFT IN OUR OWN TEST DATA, which is worth carrying forward as a
signal about the fixtures generally. `tests/commands/test_content_unown.py` had been
seeding a declaration claiming `unowned_byte_floor` 10 while its own sections summed to
26 — an incoherent state the old loader accepted silently, inherited by every REQ-04/05
test built on it. The behave fixture carried the same shape. Both were repaired to be
genuinely coherent (computed with `measure_section_spans`, never hardcoded) rather than
exempted from the check.

THE SESSION'S OTHER SUBJECT IS A DEFECT FAMILY: A SIGNAL THAT DOES NOT MEAN WHAT ITS
SURFACE SAYS IT MEANS. Four members, three filed this session and one the operator's own.
- GHI #940 — `verifier-pipe-gate` misses the backgrounded-SEQUENCE case. The gate
  (`src/gzkit/verifier_pipe_gate.py:96`) treats a statement separator as ending the
  masking risk; true in the foreground, false when backgrounded, where only the final
  statement's exit status is surfaced. Measured: a backgrounded arb unittest step reported
  "exit code 0" while its receipt recorded exit_status 1 over 9198 tests with one failure.
  THE OBVIOUS FIX DOES NOT WORK — requiring `$?` be read immediately after would have
  PERMITTED that exact command. Operator ruled: build the background-aware predicate,
  testing TRUTHINESS of `run_in_background`, never key presence. The payload carries the
  field (Claude Code hooks reference gives a named per-tool Bash example).
- GHI #941 — reviewer personas are `tools: Read, Glob, Grep` with no Bash, so asking one
  to verify by RUNNING yields findings about its own coverage which then contaminate a
  verdict that gates advancement. Operator ruled: READ-ONLY IS THE INTENT; separate the
  finding channels. Do NOT grant reviewers Bash.
- GHI #942 — Stage-4a pasted command output is unverified and Step 4b never checks the
  packet. The narrator dispatch fabricated `gz covers --json` output with an invented flat
  shape and two invented key names, and cited a proof command that returns nothing. Filed
  as the residual of the CLOSED GHI #643, whose remedy (Step 4b) re-derives the CLAIM from
  the repository and is never handed the PACKET.
- GHI #919 (operator's, open) — a control that could not run reported as theater.

THE CORRECTION THAT MUST NOT BE REPEATED: after catching the narrator fabricating, the
orchestrator proposed to rebuild the Stage-4a packet itself. The operator flagged it
immediately. Swapping which agent authors the evidence keeps the fabrication surface —
the orchestrator is the same surface, a point #942's own body makes. THE ANSWER IS NO
AUTHOR: `uv run gz obpi present-evidence <OBPI>` generates the packet "from observables
the agent cannot author". NEVER hand-compose a Stage-4a packet, and never dispatch a
narrator to compose one.

THE BRIEF'S DEMO IS ASSERT-SHAPED NOW. `gz obpi present-evidence` first exited 3
NOT-ATTESTABLE because the Demo carried a refusal probe that exits 1 when the system is
HEALTHY, inverting `stage4_evidence.py`'s contract ("assert-shaped -- exit non-zero on a
bad state"). Repaired at the BRIEF, not the tool, and strengthened to assert BOTH of
REQ-04's claims. NOTE: the packet will need REGENERATING after the remaining findings
land, and ATTESTABLE from that tool does NOT mean completable — Stage 4b's verdict lives
in the adversary receipt, not in the evidence packet.

RED WITNESS IS WEAK ON ALL SEVEN BEHAVIOR REQs and that is expected, not a finding. All
returned failure_class=error, never the blocking `none`. An `error` red proves only that a
symbol was absent; NEVER report it as an assertion RED. Do not weaken any passing
assertion to quiet it.

COVERAGE HONESTY IS BINDING (brief Requirement 8). 81.6% is span-based and INFLATES: four
of the ten owned sections carry exactly ONE corpus entry, and governance-doctrine-surfaces'
single entry is compressible tier, so it is not on the invariant floor at all. Read it as
six real sections plus four tokens. Never round or present it as stronger.

SUBAGENT TURN CEILINGS ARE THE DOMINANT COST: seven of fifteen dispatches hit the 25-turn
(implementer) or 15-turn (reviewer) limit, and one reviewer died on a 600s stream-watchdog
stall with no verdict. The observed pattern is that a dispatch gets the DESIGN right and
then exhausts its budget on mechanical propagation afterward — call-site updates, fixture
coherence, artifact regeneration. Front-loading VERIFIED state (exact symbols, measured
figures, enumerated failures, what is already green, what NOT to re-check) is what got
every resumed dispatch through.

## Decisions Made

- [operator-ruled] Fix adversary finding 1 first (verbatim: "fix finding 1 first"). Landed: `record_unowned_total` persists the declaration before emitting its ledger event.
- [operator-ruled] Fix adversary finding 4 next (verbatim: "fix finding 4 next").
- [operator-ruled] Finding 4's mechanism is the ATTESTED TRANSITION CHAIN, not a floor-coherence recompute (selected from a three-way choice; rejected alternatives were the coherence-only check, which fail-closes on every legitimate edit to an unowned AGENTS.md section, and the both-mechanisms option, which inherits that brittleness).
- [operator-ruled] Resume the prior handoff and work Task 4 through all five stages (verbatim: "continue with task 4 (#1) do all 5 stages in task 4."). Booked via `gz handoff decide`.
- [operator-ruled] Add `tests/content/test_tui_affordances.py` to this brief's Allowed Paths so the `gz content` subcommand fence could admit `unown` (verbatim: "3. add to allowed"). Booked via `gz obpi unblock`. Widened by exactly one id with provenance named; never relaxed.
- [operator-ruled] GHI #941: reviewers stay READ-ONLY and the remedy is to separate the finding channels (verbatim: "2. read-only is the intent, separate the fundung channels" -- spelling preserved). Granting reviewers Bash is REJECTED.
- [operator-ruled] GHI #940: build the background-aware predicate rather than the declare-only fallback.
- [operator-ruled] The orchestrator must NOT rebuild the Stage-4a evidence packet itself (verbatim: 'this is bad: "I''ll rebuild the 4a packet from verified output only, and present it with the Codex verdict."'). No agent authors that packet; `gz obpi present-evidence` does.
- [agent-chose] Permit a null `floor_event_id` ONLY when the floor equals the summed span of the declaration's own unowned sections. Without that condition, hand-raising the floor AND nulling the id would bypass the chain entirely; genesis proves itself by coherence, every later floor by chain.
- [agent-chose] Keep persistence and event emission inside `record_unowned_total` rather than moving emission to a caller. A prior reviewer ruling in this brief's Tracked Defects overturned that split because no allowlisted command-layer caller exists, and the adversary independently recommends one adapter-level operation.
- [agent-chose] Lift `declaration_path` into `ownership.py` so `unown.py` and the ratchet resolve declaration locations through one function, on the same reasoning the module already applies to `section_id`.
- [agent-chose] Repair incoherent test and behave fixtures to be genuinely coherent rather than relaxing the new chain check to accommodate them.
- [agent-chose] Repair the brief's `## Demo` rather than the Stage-4 evidence tool when `present-evidence` exited 3; the tool's assert-shaped contract is correct and the Demo's refusal probe inverted it.
- [agent-chose] Do NOT re-run Step 4b until finding 2 lands, since it touches the same files and the adversary should run once against a tree that can clear it.
- [agent-chose] Do NOT relocate the `no ledger event <event> was emitted` behave step into `gz_steps.py`; behave raises on ambiguous duplicates and the definition is Gate-4 evidence for the attested-completed OBPI-0.35.0-02. Recorded as tracked debt instead.
- [agent-chose] File three separate GHIs (#940, #941, #942) rather than one bundled issue, and cross-link #942 onto the closed #643 as its residual rather than reopening.
- [agent-chose] Finish this OBPI before landing the #940/#941/#942 fixes, because #941's remedy edits `ReviewResult` in the review machinery this pipeline run is using.

## Immediate Next Steps

1. OBTAIN AN OPERATOR RULING ON FINDING 3's HOME before any repair. `gz validate --documents` never reads `.gzkit/ownership/*.json`, so REQ-08's SUPPORT proof reports pass without validating the artifact. The fix needs a new validator scope in `src/gzkit/commands/validate_cmd.py`, which is NOT in this brief's Allowed Paths, and it may belong to OBPI-0.35.0-06 instead. Present the overlap; never widen the allowlist unilaterally.
2. FIX FINDING 2 — make `gz content unown` atomic and recoverable. Atomic file replacement plus a transaction tying the declaration's `floor_event_id` to its ledger event, so a ledger failure after the declaration write is recoverable rather than leaving a declaration that names a nonexistent event. Test concurrent updates, ledger failure, partial declaration writes, and retry recovery. Do NOT weaken finding 4's chain check to make this case softer.
3. FIX FINDING 5 — add an independent control for REQ-07 that perturbs the real day-one surface and corpus and proves each reported figure changes accordingly, WITHOUT deriving its expectation through production's own measurement primitives.
4. RE-RUN STAGE 3 IN FULL, then regenerate the Stage-4a packet with `uv run gz obpi present-evidence OBPI-0.35.0-04-section-ownership-and-ratchet`. Never hand-compose it and never dispatch a narrator to compose it.
5. RE-DISPATCH STEP 4b ONCE, against the repaired tree. Codex tier 1 was confirmed READY this session (ready true, runtime mode direct, prop clear), so tiers 2 and 3 remain FORBIDDEN. Dispatch through the plugin (`codex-companion.mjs adversarial-review`) and never `codex exec`; ARB-wrap it so the receipt can be cited. Only after a clean or caveat-resolved verdict may attestation be solicited; `gz obpi complete` additionally requires `--adversary-resolution` naming what was fixed and how the adversary's own checks were re-run.

## Pending Work / Open Loops

- ADVERSARY FINDING 2 OPEN [high] — `unown` non-atomic, loses concurrent transitions; now coupled to finding 4's chain, so a post-write ledger failure leaves a declaration naming a nonexistent event and the loader fail-closes. That is correct; recovery is this finding's work.
- ADVERSARY FINDING 3 OPEN [high] — REQ-08's claimed validator never reads the ownership artifact. BLOCKED ON AN OPERATOR ALLOWLIST RULING; may belong to OBPI-0.35.0-06.
- ADVERSARY FINDING 5 OPEN [medium] — REQ-07's covering test cannot detect a stored day-one snapshot.
- STEP 4b NOT RE-RUN. The standing verdict is REFUTED. `gz obpi complete` fail-closes on the Heavy lane without an adversary verdict, and a refuted one additionally requires `--adversary-resolution`.
- GHI #940 OPEN — verifier-pipe-gate backgrounded-sequence masking. Operator ruled the remedy; direct-fix routed; not implemented. `UNWITNESSABLE` should also gain the foreground-sequence limit, since the module's contract is that coverage limits are declared rather than hidden.
- GHI #941 OPEN — reviewers cannot execute; unrunnable asks degrade the verdict. Operator ruled read-only intent and channel separation. Touches `ReviewResult` in `src/gzkit/pipeline_dispatch.py`; deferred until this pipeline run ends.
- GHI #942 OPEN — Stage-4a pasted output unverified; Step 4b does not check the packet. Remedy not chosen; the one that removes the surface is to never let a composing agent render command output.
- GHI #919 (operator's) OPEN — fourth member of the same family, cross-linked from #941.
- TRACKED DEBT in the brief's Tracked Defects: content-layer ledger write deferred to OBPI-0.35.0-05; `emit_unowned_ratchet_updated` constructs `LedgerEvent` inline; the generic ledger-absence behave step lives in `content_retire_steps.py` rather than `gz_steps.py`.
- DEFERRED OPERATOR QUESTION, logged as an `improvement` insight and not acted on: whether Stage-2 dispatch grain should be finer given context rot. Seven of fifteen dispatches hit turn ceilings this session; the observed split is design-and-core versus propagate-and-verify, not RED/GREEN/REFACTOR.
- PARENT-ADR COUPLING UNRESOLVED from an earlier session: ADR-0.35.0 § Decision item 4 and § Consequences Positive #4 still carry the retired entry-witness figures. Scoped to OBPI-0.35.0-05 and -06, outside this brief's allowlist.

## Verification Checklist

Run these before acting on anything above; every claim here is Layer-1 narrative and is
unverified until checked.

    uv run gz obpi status OBPI-0.35.0-04-section-ownership-and-ratchet
    uv run gz obpi lock list
    uv run gz obpi brief-drift OBPI-0.35.0-04
    uv run gz covers OBPI-0.35.0-04-section-ownership-and-ratchet --json
    uv run -m unittest tests.content.test_ownership
    uv run -m unittest tests.commands.test_content_unown
    uv run -m unittest tests.content.test_tui_affordances
    uv run ruff check .
    uv run gz cli audit

Expected at checkpoint: lock HELD; brief-drift clean on all five dimensions; covers 7/8
with behavior_uncovered_reqs 0; ownership 30 pass; unown 10 pass; tui-affordances 10 pass;
ruff clean; cli audit 141/141.

To reconfirm findings 1 and 4 are actually closed, re-run the adversary's own probes
rather than trusting this document: for finding 1, seed a declaration on disk, call
`record_unowned_total` with a lower total, and confirm the returned floor, the persisted
floor and the ledger event's new floor all agree. For finding 4, seed a valid declaration,
hand-edit its floor upward, and confirm `load_declaration` REFUSES it both with a null
`floor_event_id` and with one naming a nonexistent event, while a coherent genesis
declaration still loads.

BEWARE: `gz obpi present-evidence` reporting ATTESTABLE does NOT mean the OBPI may
complete. Stage 4b REFUTED it and that verdict lives in the adversary receipt, not in the
evidence packet. Both statements are true at once.

NEVER pipe a verifier through tail/head/grep, and NEVER background a verifier that is not
the final statement of its command; the shell reports the last statement's exit status,
which is the defect GHI #940 names. Redirect to a file and read the ARB receipt's
`exit_status`.

If a unittest failure contradicts source you have just read, clear stale bytecode before
diagnosing: `find src tests -name __pycache__ -type d -exec rm -rf {} +`.

## Evidence / Artifacts

Brief, plan and evidence packet:
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md`
- `.claude/plans/section-ownership-and-ratchet-OBPI-0.35.0-04.md`
- `.claude/plans/.plan-audit-receipt-OBPI-0.35.0-04-section-ownership-and-ratchet.json`
- `.claude/plans/.pipeline-active-OBPI-0.35.0-04-section-ownership-and-ratchet.json`
- `.gzkit/evidence/OBPI-0.35.0-04-section-ownership-and-ratchet.evidence.json`

Production and artifacts:
- `src/gzkit/content/ownership.py`
- `src/gzkit/commands/content/unown.py`
- `src/gzkit/commands/content/__init__.py`
- `src/gzkit/schemas/section_ownership.json`
- `src/gzkit/governance/events.py`
- `.gzkit/ownership/AGENTS.md.json`
- `config/doc-coverage.json`
- `docs/user/manpages/content.md`

Tests and scenarios:
- `tests/content/test_ownership.py`
- `tests/commands/test_content_unown.py`
- `tests/content/test_tui_affordances.py`
- `features/content_unown.feature`
- `features/steps/content_unown_steps.py`

Surfaces the remaining adversary findings name:
- `src/gzkit/commands/validate_cmd.py`
- `src/gzkit/verifier_pipe_gate.py`
- `src/gzkit/pipeline_dispatch.py`
- `src/gzkit/governance/stage4_evidence.py`

Precedents:
- `features/content_retire.feature`
- `features/steps/content_retire_steps.py`
- `src/gzkit/commands/content/retire.py`

Prior handoff in this chain:
- `.gzkit/handoffs/20260902T190607Z-obpi-0-35-0-04-stage4b-refuted.md`

Governance surfaces:
- `.gzkit/ledger.jsonl`
- `.gzkit/insights/agent-insights.jsonl`
- `.gzkit/handoffs/rulings.jsonl`

## Settled Rulings

670 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
