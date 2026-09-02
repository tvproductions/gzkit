---
mode: CHECKPOINT
adr_id: ADR-0.35.0
branch: main
timestamp: '2026-09-02T22:22:42Z'
agent: claude-code
obpi_id: OBPI-0.35.0-04-section-ownership-and-ratchet
session_id: 9b60410d-b9da-4ed2-86d0-e8b165e13b0b
continues_from: .gzkit/handoffs/20260902T201847Z-obpi-0-35-0-04-findings-1-and-4-closed.md
---

## Current State Summary

CHECKPOINT for OBPI-0.35.0-04-section-ownership-and-ratchet (parent ADR-0.35.0, Heavy lane) under
gz-obpi-pipeline. Lock HELD (agent=claude-code-9de7e7a3). Pipeline marker active. Bookmarking
mid-flight by operator ruling, NOT departing, so this CHECKPOINT does not discharge the lock release.

PIPELINE POSITION: Stages 2, 3 and 4a are COMPLETE and green. Stage 4b ran and returned REFUTED a
SECOND time. Stage 5 has never been entered and NO attestation has been solicited.

WHAT THIS SESSION CLOSED. The first adversary pass left three open findings; all three are now
fixed, reviewed and independently probe-verified by the orchestrator rather than accepted on report.
FINDING 3 (REQ-08's proof channel was vacuous) — `gz validate --documents` now schema-validates
every `.gzkit/ownership/*.json` against `section_ownership.json` and then constructs
`OwnershipDeclaration`, wired beside `_validate_exemplar_corpus`. Mutation probe on the live
artifact: dropping `floor_event_id` and injecting a bogus enum value made the scope exit 1 naming
the file, the schema and the property, with three-part recovery prose; the file was restored
byte-identical. FINDING 2 (`gz content unown` non-atomic, lost concurrent transitions) — the whole
read-modify-write now runs inside `exclusive_declaration_lock`, the declaration write is
temp-plus-`os.replace`, the event id is deterministic and chained on its predecessor, and a journal
makes an interrupted two-store transaction completable on retry. FINDING 5 (REQ-07's covering test
could not detect a stored snapshot) — two differential controls added; the orchestrator ran the
adversary's own substitution in-process and the ORIGINAL test passed while both new controls failed.

THREE FIX CYCLES RAN ON FINDING 2's SURFACE, the third by explicit operator ruling past the skill's
MAX_REVIEW_FIX_CYCLES bound of 2. Cycle 1 closed an fsync-on-a-read-only-handle bug that broke
`gz content unown` entirely on Windows. Cycle 2 closed a stale-read ratchet race the orchestrator
reproduced (floor 40 raised to 60 through the ordinary path). Cycle 3 closed a stale
`sections`/`measured_at` lost-update that both re-reviewers found independently.

MEASURED GREEN AT CHECKPOINT (Stage 3, all ARB-wrapped, exit_status read from the receipt JSON):
full suite 9235 pass (arb-step-unittest-ed4edb8ba7fe44269e3eae66bdd48215); ruff clean
(arb-ruff-a6b0ed21703e4a51bcc19f0eced5125c); typecheck clean
(arb-step-typecheck-a2428489c01043f3846ed6acd239eb6e); mkdocs strict built
(arb-step-mkdocs-e41c69d5e5334310bd7ac95baa2bb9a3); behave scoped to
@REQ-0.35.0-04-04,@REQ-0.35.0-04-05 gives 5 scenarios and 29 steps, 0 failed
(arb-step-behave-2ad195a1548f4fbdb395f92109f5e0af). `gz validate --documents`,
`--req-kind-discipline`, and `gz cli audit` (141/141) all exit 0. Scoped suites: 63 pass across
tests/content/test_ownership.py and tests/commands/test_content_unown.py, plus 7 in
tests/commands/test_validate_ownership_declarations.py. `gz covers` reports 7/8 with
behavior_uncovered_reqs 0.

`gz obpi precomplete` is at 10 of 11 preconditions met. The single remaining blocker is
`adversarial_validation`, which now correctly reads "Step 4b records refuted" — the gate is doing
its job.

## Important Context

THE STANDING VERDICT IS REFUTED AND THE OBPI IS NOT COMPLETABLE. Receipt
arb-step-codexadversary-d04634100678415daada4acd3a6f2881 (tier 1 Codex, cross-vendor, dispatched
through the openai-codex plugin runtime, exit_status 0). Tier-1 readiness was confirmed before
dispatch (ready true, runtime mode direct, no stale broker), so tiers 2 and 3 were FORBIDDEN. The
full verdict and all four findings are written into the brief's `### Step 4b` section; the two open
high findings are additionally recorded in the brief's Tracked Defects.

FINDING 1 IS THE ONE THAT MATTERS AND IT IS A DESIGN GAP, NOT A BUG. `load_declaration` treats ANY
section/floor-coherent declaration carrying a null `floor_event_id` as a legitimate genesis, and
nothing proves it is the original genesis state. THE ORCHESTRATOR REPRODUCED IT: copy the real
declaration into a scratch root, flip `attestation` from corpus-owned to unowned, recompute the
floor so it stays self-coherent, keep the id null, and it LOADS. Observed: baseline floor 8637,
hand-raised floor 10182, ledger file does not exist, RESULT ACCEPTED. The adversary separately
showed the non-null branch is only an id/floor equality check, so a `task_started` event for
`Other.md` was accepted as proof for `Doc.md`. Together these defeat REQ-0.35.0-04-02's central
claim that the ratchet rises only through the attested path.
THIS IS THE DOCTRINE THIS OBPI EXISTS TO CLOSE, SITTING INSIDE THE OBPI. AGENTS.md, verbatim: "A
PRESENCE CHECK ANSWERS 'is something armed', NEVER 'did the governed procedure run'." Genesis is
witnessed by self-coherence, and self-coherence is exactly what an attacker recomputes. Genesis has
no provenance anchor BY CONSTRUCTION, so the repair shape is an operator ruling, not a patch.
Candidate anchors named by the adversary and by this session: a `section_ownership_genesis` ledger
event; a commit-SHA anchor; or forbidding a null `floor_event_id` after day one. Do NOT pick one
without the operator.

FINDING 2 WAS INTRODUCED BY THIS SESSION'S OWN REPAIR, and that is the sharper lesson.
`_replay_pending_transition` validates only that the journal is an object carrying
`_JOURNAL_FIELDS`, then writes `declaration_json` VERBATIM and appends its claimed event. It never
validates attestor/reason, never recomputes the event id, never compares the intended transition
against the live section span, and never proves the journal starts from the declaration currently
on disk. The adversary forged a journal that was accepted with exit 0, raised a floor from 26 to
1025, and printed blank provenance. Separately `_JOURNAL_FIELDS` omits `ts` while
`_append_event_once` reads `record["ts"]` at unown.py:176, so a field-complete journal can still
die on a raw KeyError instead of the governed three-part refusal (verified by reading both sites).
The journal that made the two-store transaction recoverable became a new unattested write path.

FINDINGS 3 AND 4 WERE ALREADY DISCLOSED in the brief's Tracked Defects before the pass, and the
adversary confirmed both by probe rather than by argument. That is what disclosure is for. Finding 3
is `record_unowned_total`'s two-store transaction being unrecoverable; finding 4 is the missing
directory fsync after `os.replace`.

THE ALLOWLIST WAS WIDENED FOUR TIMES ACROSS THIS BRIEF'S LIFE, each by an operator ruling under the
Gate Friction escalation loop and each documented in place in the brief's Allowed Paths with its
reasoning. This session added two: `src/gzkit/commands/validate_cmd.py` plus its test module (for
finding 3) and `.gitignore` (for the sidecars the atomic write creates). Never widen it unilaterally.

SUBAGENT TURN CEILINGS REMAIN THE DOMINANT COST. Five of this session's dispatches hit the 25-turn
implementer or 15-turn reviewer limit. What got every resumed dispatch through was front-loading
VERIFIED state into the resume message: exact symbols, measured figures, what is already green, and
an explicit list of what NOT to re-check. Budget instructions in the initial prompt help less than
the resume message does.

THE ORCHESTRATOR VERIFIED EVERY SUBSTANTIVE CLAIM BY EXECUTABLE PROBE rather than by reading agent
reports, and this repeatedly paid. The implementer's report that a stale read was safe was wrong and
a probe disproved it; the claim that finding 5's controls were closed was unproven until the
substitution was actually run. Continue that discipline.

## Decisions Made

- [operator-ruled] Resume the prior handoff and work all of its advised steps (selection: "Proceed — all advised steps"). Booked via `gz handoff decide`.
- [operator-ruled] Adversary finding 3's repair lives in THIS brief and extends `gz validate --documents` rather than adding a new validator scope flag (selection: "Here, extending --documents"). Rejected alternatives were routing it to OBPI-0.35.0-06, adding a dedicated `--ownership` scope, and deferring it to a GHI. A new flag would have been a CLI surface change and REQ-08 names `--documents` by name.
- [operator-ruled] Widen the allowlist by `.gitignore` and add the three sidecar globs, rather than relocating the sidecars or deferring to a GHI (selection: "Widen allowlist, add the three globs"). Both reviewers graded the omission major.
- [operator-ruled] Run a THIRD fix cycle past the skill's MAX_REVIEW_FIX_CYCLES bound of 2, to close the stale sections/measured_at lost-update properly rather than ship it latent with a docstring that denied it (selection: "One more cycle — close it properly"). The re-review had SPLIT: spec-reviewer FAIL, quality-reviewer PASS on the same finding.
- [operator-ruled] The agent may mint the subdivided seq=02 TASKs inside the pipeline the operator had already initiated (selection: "You authorize me to mint them"). Rejected: declaring `req_atomic:`, which would have asserted something false given the labor visibly subdivided across three fix cycles.
- [operator-ruled] CHECKPOINT and resume in a fresh session rather than run a fourth fix cycle on a design decision (selection: "Handoff now, resume fresh"). Finding 1 wants a clear-headed design ruling, not a tired fourth cycle.
- [agent-chose] Mint five seq=02 TASKs, not eight. REQ-01, REQ-04 and REQ-06 stayed at seq=01 because their labor genuinely did not subdivide this session; minting all eight would have made the envelope pass while asserting something false about three of them.
- [agent-chose] Verify every substantive agent claim by executable probe rather than by reading the report. This overturned an implementer's judgment that a stale read was safe, and it is why finding 5's controls are known to bite rather than merely believed to.
- [agent-chose] Do NOT re-review a fourth time after fix cycle 3's closure check returned PASS; fold its three remaining honesty-layer minors into task 7's dispatch instead, since they touched the same two files.
- [agent-chose] Rename `test_baseline_against_real_agents_md_matches_independently_rederived_figures` to `test_baseline_arithmetic_is_self_consistent_against_the_real_surface_and_corpus`, because the old name claimed an independence the test does not have.
- [agent-chose] Add the missing `@covers("REQ-0.35.0-04-07")` to the corpus-perturbation control. It is not cosmetic backfill: coverage already passed without it, and the tag makes the strongest REQ-07 evidence visible in the coverage table.
- [agent-chose] Record the Step 4b REFUTED verdict and both open high findings in the brief BEFORE handing off, so the refutation is Layer-1 canon rather than only a session artifact.
- [agent-chose] Keep the lock HELD. This is a CHECKPOINT, which by the skill's own contract cannot discharge a lock release, and a fresh session resumes the same OBPI.

## Immediate Next Steps

1. OBTAIN AN OPERATOR RULING ON FINDING 1's REPAIR SHAPE before touching any code. Genesis has no provenance anchor by construction, so this is a design decision and not a patch. Present the three candidate anchors: a `section_ownership_genesis` ledger event; a commit-SHA anchor; or forbidding a null `floor_event_id` after day one. Note that the third is the simplest but changes the day-one bootstrap story, and that whichever is chosen must ALSO fix the non-null branch, which today accepts any event id whose floor matches regardless of event type or surface.
2. FIX FINDING 2 — journal replay validation. This one is mechanical and needs no ruling. Use a strict journal model that includes `ts` (the current `_JOURNAL_FIELDS` roster omits it while `_append_event_once` reads it), the predecessor event id, and a fingerprint of the declaration the journal started from. Before replaying, validate non-blank attestor and reason, surface and path identity, exactly one section transition, a span-derived floor delta, a recomputed event id, and that the declaration currently on disk is either the recorded predecessor or the already-completed successor. Refuse without writing otherwise, in three-part prose.
3. RE-RUN STAGE 3 IN FULL after both fixes land, then regenerate the Stage-4a packet with `uv run gz obpi present-evidence OBPI-0.35.0-04-section-ownership-and-ratchet`. NEVER hand-compose that packet and never dispatch a narrator to compose it.
4. RE-DISPATCH STEP 4b a THIRD time against the repaired tree. Dispatch through the plugin (`codex-companion.mjs adversarial-review`) and never `codex exec`; ARB-wrap it so the receipt can be cited. Clear prop first if a prior run may have wedged the broker. Only after a clean or caveat-resolved verdict may attestation be solicited.
5. WHEN COMPLETION IS FINALLY REACHED, `gz obpi complete` will require `--adversary-resolution` naming what was fixed and how the adversary's own checks were re-run, because the standing verdict is refuted. It also fail-closes without `--adversary-verdict`, `--adversary`, `--adversary-tier 1` and `--adversary-receipt`.

## Pending Work / Open Loops

- ADVERSARY FINDING 1 OPEN [high] — genesis has no provenance anchor; a self-coherent hand edit raises the ratchet with no ledger event. REPRODUCED at floor 8637 raised to 10182. BLOCKED ON AN OPERATOR DESIGN RULING. Recorded in the brief's Step 4b section and Tracked Defects.
- ADVERSARY FINDING 2 OPEN [high] — journal replay is an unvalidated arbitrary declaration write, and `_JOURNAL_FIELDS` omits `ts` while `_append_event_once` reads it. Mechanical; fix first on resume. Introduced by this session's own repair.
- ADVERSARY FINDING 3 OPEN [medium] — `record_unowned_total`'s two-store transaction is not recoverable; it has no journal and no rollback. Already in Tracked Defects; the adversary confirmed it by injecting an OSError into the ledger append.
- ADVERSARY FINDING 4 OPEN [medium] — no directory fsync after `os.replace`, so a power-loss window can leave an unresolvable floor pointer with no recovery record. Already in Tracked Defects.
- STEP 4b STANDING VERDICT IS REFUTED. `gz obpi precomplete` is at 10 of 11, blocked solely on `adversarial_validation`, which correctly reads that Step 4b records refuted.
- GHI NOT YET FILED — Rich markup swallows every validator error type. `src/gzkit/commands/validate_cmd.py:1140` prints the type inside square brackets through Rich, which parses it as a style tag and drops it. Verified by observation: a perturbed run printed only the artifact path. Affects EVERY validator scope, not just the new one. Recorded as an insight; wants a GHI.
- GHI NOT YET FILED — `_exclusive_store_lock` should be promoted from a private symbol in `corpus_store.py` to a public `exclusive_file_lock(path)` in a neutral module that both `corpus_store` and `ownership` call. Recorded in the brief's Tracked Defects; `corpus_store.py` is outside this brief's allowlist.
- GHI NOT YET FILED — `gz task envelope diagnose` reports the frontmatter `tasks:` channel as EMPTY although the brief carries all eight TASK ids. Looks like a reader defect in the diagnostic rather than real layer-drift. Recorded as an insight.
- GHI #940 OPEN — verifier-pipe-gate misses the backgrounded-sequence case. Operator ruled the remedy (build the background-aware predicate); not implemented.
- GHI #941 OPEN — reviewer personas cannot execute, so unrunnable asks degrade a verdict that gates advancement. Operator ruled read-only intent and channel separation. Touches `ReviewResult` in `src/gzkit/pipeline_dispatch.py`.
- GHI #942 OPEN — Stage-4a pasted output is unverified and Step 4b never checks the packet.
- GHI #919 OPEN (operator's) — fourth member of the same defect family.
- TRACKED DEBT in the brief beyond the four adversary findings: the content-layer ledger write deferred to OBPI-0.35.0-05, and the generic ledger-absence behave step living in `content_retire_steps.py` rather than `gz_steps.py`.
- PARENT-ADR COUPLING UNRESOLVED — ADR-0.35.0 Decision item 4 and Consequences Positive #4 still carry the retired entry-witness figures. Scoped to OBPI-0.35.0-05 and -06, outside this brief's allowlist.

## Verification Checklist

Run these before acting on anything above. Every claim in this document is Layer-1 narrative and is
unverified until checked.

    uv run gz obpi status OBPI-0.35.0-04-section-ownership-and-ratchet
    uv run gz obpi lock list
    uv run gz obpi precomplete OBPI-0.35.0-04-section-ownership-and-ratchet
    uv run gz obpi brief-drift OBPI-0.35.0-04
    uv run gz covers OBPI-0.35.0-04-section-ownership-and-ratchet --json
    uv run -m unittest tests.content.test_ownership tests.commands.test_content_unown
    uv run -m unittest tests.commands.test_validate_ownership_declarations
    uv run ruff check .
    uv run gz cli audit

Expected at checkpoint: lock HELD; precomplete BLOCKED at 10 of 11 with only
`adversarial_validation` failing; brief-drift clean; covers 7/8 with behavior_uncovered_reqs 0;
63 pass across the two scoped modules; 7 pass in the validator module; ruff clean; cli audit 141/141.

TO RECONFIRM FINDING 1 RATHER THAN TRUSTING THIS DOCUMENT, re-run the orchestrator's probe: copy
`AGENTS.md` and `.gzkit/ownership/AGENTS.md.json` into a scratch root, flip one corpus-owned section
to unowned, recompute `unowned_byte_floor` as the summed span of the unowned sections, leave
`floor_event_id` null, and call `load_declaration`. It should be ACCEPTED today, with no ledger file
in existence. When finding 1 is repaired, that same probe must be REFUSED, and the repair is not
complete until it is.

TO RECONFIRM FINDING 5 IS CLOSED, monkeypatch `compute_baseline` in
`tests.content.test_ownership` to return a frozen snapshot regardless of input and run the three
`TestComputeBaseline` methods. Expected:
`test_baseline_arithmetic_is_self_consistent_against_the_real_surface_and_corpus` PASSES (it is the
weak control, kept deliberately and named honestly), while
`test_baseline_is_recomputed_when_the_corpus_changes_not_read_from_a_constant` and
`test_baseline_deltas_a_known_perturbation_by_exactly_that_amount` both FAIL.

NEVER pipe a verifier through tail, head or grep, and never background a verifier that is not the
final statement of its command. The shell reports the last statement's exit status, which is the
defect GHI #940 names. Redirect to a file and read the ARB receipt's `exit_status`.

If a unittest failure contradicts source you have just read, clear stale bytecode before diagnosing:
`find src tests -name __pycache__ -type d -exec rm -rf {} +`

## Evidence / Artifacts

Brief, plan, markers and evidence packet:
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-04-section-ownership-and-ratchet.md`
- `.claude/plans/.plan-audit-receipt-OBPI-0.35.0-04-section-ownership-and-ratchet.json`
- `.claude/plans/.pipeline-active-OBPI-0.35.0-04-section-ownership-and-ratchet.json`
- `.gzkit/evidence/OBPI-0.35.0-04-section-ownership-and-ratchet.evidence.json`

Production surfaces changed this session:
- `src/gzkit/content/ownership.py`
- `src/gzkit/commands/content/unown.py`
- `src/gzkit/commands/validate_cmd.py`
- `src/gzkit/schemas/section_ownership.json`
- `.gzkit/ownership/AGENTS.md.json`
- `.gitignore`

Tests changed or added this session:
- `tests/content/test_ownership.py`
- `tests/commands/test_content_unown.py`
- `tests/commands/test_validate_ownership_declarations.py`

Step 4b adversary receipts (the second is the standing verdict):
- `artifacts/receipts/arb-step-codexadversary-f7a101da3ba3498e94249f2bdb39969f.json`
- `artifacts/receipts/arb-step-codexadversary-d04634100678415daada4acd3a6f2881.json`

Stage 3 receipts, all exit_status 0:
- `artifacts/receipts/arb-ruff-a6b0ed21703e4a51bcc19f0eced5125c.json`
- `artifacts/receipts/arb-step-typecheck-a2428489c01043f3846ed6acd239eb6e.json`
- `artifacts/receipts/arb-step-unittest-ed4edb8ba7fe44269e3eae66bdd48215.json`
- `artifacts/receipts/arb-step-mkdocs-e41c69d5e5334310bd7ac95baa2bb9a3.json`
- `artifacts/receipts/arb-step-behave-2ad195a1548f4fbdb395f92109f5e0af.json`

Precedents the repairs were built against:
- `src/gzkit/content/corpus_store.py`
- `src/gzkit/governance/invariants.py`
- `features/content_unown.feature`
- `features/steps/content_unown_steps.py`

Governance surfaces:
- `.gzkit/ledger.jsonl`
- `.gzkit/insights/agent-insights.jsonl`
- `.gzkit/handoffs/rulings.jsonl`

Prior handoff in this chain:
- `.gzkit/handoffs/20260902T201847Z-obpi-0-35-0-04-findings-1-and-4-closed.md`

## Settled Rulings

678 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
