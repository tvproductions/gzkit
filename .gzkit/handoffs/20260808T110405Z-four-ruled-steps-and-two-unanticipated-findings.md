---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T11:04:05Z'
agent: claude-code
session_id: 136551a7-7907-4d45-8e1e-bafdfc8dc961
continues_from: .gzkit/handoffs/20260808T094439Z-obpi-status-monitor-collapse.md
---

## Current State Summary

Resumed the anchor handoff, presented its five advised steps with every claim tagged against Layer-2, and the operator ruled four of them in one picker pass. All four landed; step 5 was recorded set-aside for the fourth time.

**Four commits, all pushed.** `641d4eab9` folded GHI #581's diagnosis into `ADR-pool.governance-document-structural-validation` and closed it `superseded`. `cd0fcf0f5` re-scoped the Movement C family-closure box to its own criterion rather than checking it off on closed exemplars. `3f40cae73` widened the canonical typecheck scope from `src` to the whole tree minus `features`, and made three of the command's four copies derive rather than agree. `5287c32ed` discharged GHI #768 with a subtractive remedy plus a fence.

`uv run gz check` exit 0. 8166 unit tests OK, up from 8141 at the anchor. `origin/main` 0/0 and tree clean at authoring.

**Two findings the ruled work did not anticipate.** Widening the typecheck scope retroactively invalidated 749 truthful ARB receipts, which is a write-forward-only violation of the same shape this session had just written INTO the pool ADR one commit earlier; provenance now resolves as of each receipt's own timestamp. And the new count fence caught a live transcribed count in the campaign's Housekeeping section that appears in neither GHI and in no triage pass.

## Important Context

**A change to a canonical scope can retroactively falsify sealed evidence, and the validator will not tell you kindly.** Widening `CANONICAL_STEP_COMMANDS["typecheck"]` made `gz arb validate` report 749 historical receipts as non-canonical provenance. Those receipts truthfully record what was run; judging them against today's canon is the validator asserting a falsehood about history. The fix is `RETIRED_STEP_COMMANDS`: provenance resolves as of the receipt's own `timestamp_utc`. Two edges close it in the other direction, and both are tested — the retired command run AFTER the boundary is still rejected, and a missing or unparseable timestamp cannot claim the exemption. The boundary is `10:00Z`, the real transition instant, not a rounded date; midnight would have re-invalidated this same session's earlier receipts.

**Append to `RETIRED_STEP_COMMANDS` on every future canonical-command change, and never edit an existing row.** Editing one re-invalidates exactly the history the table exists to protect.

**`src/gzkit/skills/` is a generated mirror and its path name does not say so.** An edit there was silently reverted by `gz agent sync control-surfaces`. AGENTS.md names `.gzkit/skills` as canonical with mirrors under `.claude/`, `.agents/` and `.github/`; the wheel-shipped copy under `src/gzkit/skills/` is equally generated. Edit `.gzkit/`, bump `metadata.skill-version` AND `last_reviewed` in the same edit, then sync.

**Grep over a rendered table is an existence check wearing a truth check's clothes.** Checking whether the destination pool ADR was registered by grepping `gz adr report` for the full slug returned a clean zero — because rich truncates the ADR column to 32 characters. Had that been trusted, GHI #581 would have stayed open for an eighth re-derivation on the grounds that its destination did not exist. This is the same defect class #581 itself names, one layer up.

**A citation chain is a reference graph, and an issue can accumulate diagnoses without converging.** GHI #581 was re-derived to the same TRACK-ONLY answer seven times between 2026-06-05 and 2026-08-07, and its stated destination changed twice underneath it. Both prior destinations were later retired on measured evidence. The re-derivation history is now written into the pool ADR so promotion sees it.

**Exemplars named inside a class-level criterion make a campaign box look dischargeable.** All six issues the Movement C family-closure box names by number are closed, and the box still is not done, because its own last sentence says it closes the family rather than the instance. The re-scope found the criterion was already countable and pointed at the wrong instrument: the advisory scorecard's four scores map one-to-one onto it, with `Promotable` and `Ambiguous` being precisely the forbidden third state.

**The false positives in the new count fence were found by running it, not by reasoning.** `OBPI-02/03` is a brief range, and a closeout record's `2/2` is a QC dimension score sharing its ADR's line. Both would have demanded that correct prose be edited. Design the regex, then run it over the live corpus before trusting the shape.

## Decisions Made

- [operator-ruled] Work advised steps 1, 2, 3 and 4 from the resumed handoff; step 5 (scan for fail-closed refusals with no manpage coverage) recorded set-aside for the fourth time. Booked via `gz handoff decide`.
- [operator-ruled] GHI #768 takes accept-and-disclaim plus a fence, selected from a four-option picker over the four remedies filed in the issue body. The alternatives declined were marked-syntax validator, generated block, and commit-time coupling. Stop writing the number down; add a narrow check so the subtraction cannot decay back into a convention.
- [operator-ruled] GHI #581 closes `superseded` citing `ADR-pool.governance-document-structural-validation`, selected from a three-option picker. The alternatives declined were re-affirm TRACK-ONLY in the body, and direct-fix the third failure class only.
- [operator-ruled] The canonical typecheck scope widens to tree-minus-features, selected from a four-option picker. The alternatives declined were add-scripts-only, fix-the-diagnostics-without-a-scope-change, and leave-both-and-record-as-accepted.
- [operator-ruled] The Movement C doctrine-declared-without-mechanism box is kept open and re-scoped to its criterion, selected from a three-option picker. The alternatives declined were check-it-off and split-the-box.
- [agent-chose] Judged the anchor's one `CITES SETTLED` advised step as provenance rather than precondition. Step 2 named four closed siblings, but its target `#581` was live and the closed members are the disposition precedent the step tells you to read. The step stood.
- [agent-chose] Made `RETIRED_STEP_COMMANDS` timestamp-resolved rather than reverting the scope widening or accepting 749 falsely-invalid receipts. Reverting would have discharged an operator ruling by undoing it; accepting would have left the validator asserting a falsehood about sealed evidence.
- [agent-chose] Made `run_typecheck` and `arb_typecheck_cmd` READ the canonical entry rather than adding a test that asserts three spellings agree. Derivation makes the divergence unrepresentable; an agreement test only detects it after it ships.
- [agent-chose] Wrote the lockstep tests to MUTATE the canonical value and assert consumers follow, rather than comparing current values. A value comparison cannot distinguish derivation from two copies that happen to agree today, which is the state that shipped GHI #199.
- [agent-chose] Made the count fence opt-in by registry rather than corpus-wide with exemptions. An opt-in registry cannot sweep the 135-file archive; a corpus-wide regex would have to be taught not to, and would be one missed exemption away from rewriting dated records.
- [agent-chose] Planted BOTH poles in the count fence's live negative control, and keyed the entrypoint filter on line CONTENT rather than a line number. A control that only plants a violation passes equally well against an audit that flags everything; an offset filter silently empties when the fixture gains a line.
- [agent-chose] Restated the `trust-doctrine.md` anti-pattern as a scope RELATION rather than naming two literal commands, so it does not go stale the next time the scope moves.
- [agent-chose] Left the corpus-entry counts in `ADR-0.35.0` (the 50 to 43 invariant-entry figures) untouched. GHI #768's declared class names ADR OBPI counts; a different subject with a different reconciliation source is scope the ruling did not cover.

## Immediate Next Steps

1. **Work the Movement C family-closure box now that it is measurable.** This session re-scoped it and did not start it. The rules arm is a bounded number: 12 `Promotable` plus 2 `Ambiguous` rows in `docs/governance/advisory-rules-audit.md` must reach zero, each either mechanized to `Mechanical` or its rule text amended to state it is advisory and re-scored `Judgment`. Re-scoring alone, without the text edit, is laundering. **Route:** direct fix per row, or operator ruling if a row turns out to need a design conversation.

2. **Decide the Movement C skill arm, which is unmeasured rather than clean.** `docs/governance/advisory-rules-audit.md` scores `CLAUDE.md` and `.gzkit/rules/**` and covers NO `.gzkit/skills/**/SKILL.md` mandate, which is exactly where all three agent-side exemplars lived (`#459 [settled]`, `#574 [settled]`, `#620 [settled]`). Either extend scorecard coverage to skill mandates or record in the audit why skills are structurally out of scope. **Route:** operator rules the scope, then direct fix.

3. **Scan for fail-closed refusals with no manpage coverage.** Set aside four times now, this session included. Five modules under `src/gzkit/commands/` emit blocker appends: `sync.py`, `status_render.py`, `chores_exec.py`, `common.py`, `chores.py`. Do not pre-commit to a validator scope before the scan says whether the gap is systemic. Note the relationship: if it IS systemic, it is an instance of advised step 2's family, not a separate item. **Route:** scan, then decide.

4. **Clear the 8 non-canonical `unittest` receipts, or record them as accepted.** `uv run gz arb validate --limit 800` reports 8 receipts whose `step.name` is `unittest` but whose command ran a test SUBSET. They are pre-existing, unrelated to this session, and correctly flagged. They are also the only thing standing between the receipt store and a clean provenance report, which is the surface `.claude/rules/adr-audit.md` prescribes at step 2. **Route:** operator decides delete-versus-accept, then direct fix.

5. **Rule whether `ADR-0.44.0-vendor-alignment` is finished or parked.** The campaign's Housekeeping section carries it as `IN_PROGRESS`, tracked by no campaign edition. It surfaced this session only because the new count fence flagged its transcribed count. **Route:** operator ruling, then either pull it or park it to pool per the box's own text.

## Pending Work / Open Loops

1. **The Movement C skill arm is stated as UNMEASURED, not clean, and that wording is load-bearing.** A successor reading the box must not convert "no findings" into "no problem" — there is no scanner over skill mandates at all. The box records this deliberately, because an uncovered surface reported green is the same defect the whole family names.

2. **The count fence's cue-window heuristic is not claimed exhaustive.** A count is flagged only when its line names an ADR and a progress cue sits within 24 characters. Governance prose will grow `N/M` shapes this does not anticipate. What bounds the blast radius is that the registry is opt-in, so a new false-positive class can only reach a surface someone deliberately enrolled. Stated in the manpage and the close comment rather than left implicit.

3. **`RETIRED_STEP_COMMANDS` is append-only by convention with no mechanical witness.** Nothing stops a future edit to an existing row, which would re-invalidate the history the table protects. The module docstring says so; that is a declared discipline without a mechanism, which is Movement C's own family. Worth a row in the advisory scorecard when advised step 1 is worked.

4. **GHI #719 is the pool ADR's only remaining open Related GHI** (pool-interview JSON, unschema'd). `#581 [settled]` and `#615 [settled]` have both now closed `superseded` into it, so its Related block is close to fully discharged and promotion pressure rises accordingly.

5. **GHI #769, #767, #766, #765 remain open.** `#766` is blocked by `#767`; both are parked behind `ADR-pool.primary-source-corroboration` promotion by a prior session ruling. That pool ADR is one of the five surfaces disclaimed this session. `#765` still carries a fix commit while remaining open, which is worth determining as deliberate tracker discipline or a forgot-to-close.

6. **GHI #533, #747, #719, #611, #594, #579, #567 remain open and were never named by the anchor.** Carried unchanged. Several are old; a triage sweep would say whether any are stale rather than deferred.

7. **`ADR-0.35.0` is `Pending` with no OBPIs landed, and Movement A stays deferred by explicit ruling, not drift.** Briefs 04 through 10 remain unreconciled against the tree. Carried unchanged from the anchor. Its pre-mortem number 1 (the ratchet becomes a ceiling) remains unmitigated by the ADR's own admission; cadence, owner and scheduled floor-raise must be resolved before OBPI-04.

8. **The dispatch residual is untouched, carried from five sessions back.** `gz-adr-audit` and `gz-adr-closeout-ceremony` carry the same Persona Dispatch mandate with no channel.

9. **AGENTS.md instructions-file budget work stays parked by standing operator ruling.** `gz check` reports it as an advisory naming a 385 B overage against the codex delivery cap; exit code is unaffected.

## Verification Checklist

- Never pipe a verifier. Capture to a file and read the bare status: `<cmd> > out.log 2>&1; echo "REAL EXIT: $?"`. The `verifier-pipe-gate` hook judges the pipeline, not the filter identity, and it refused a `gz handoff resume` piped into `head` on this session's first command. Use the Read and Grep tools for line ranges and file searches.
- The handoff-resume gate also refuses COMPOUND commands and command substitution in any quoting form until a `proceed` ruling is booked. Run the `gz handoff decide` recovery line bare.
- Confirm the count fence: `uv run gz validate --transcribed-adr-counts` expects exit 0 and `Validated: transcribed_adr_counts`.
- Confirm its gate enrollment, which is separate from registration (GHI #744): the step appears as `[36/51] Transcribed ADR counts` in `uv run gz check` output, and `transcribed_adr_counts` appears in the `in_check` list of `data/check_scope_membership.json`.
- Confirm the fence has teeth: `uv run -m unittest tests.governance.test_transcribed_counts` expects exit 0, 14 tests. The `DatedRecordsAreLeftAlone` class is the load-bearing half — it asserts what the audit must NOT flag.
- Confirm the typecheck lockstep: `uv run -m unittest tests.arb.test_typecheck_scope_lockstep` expects exit 0, 6 tests. The two `TypecheckGateDerivesFromCanon` mutation cases are the load-bearing ones.
- Confirm the receipt grandfather: `uv run -m unittest tests.arb.test_validator_provenance` expects exit 0, 13 tests. `RetiredCanonIsJudgedAtTheReceiptsOwnTimestamp` closes the clause in both directions.
- Confirm no receipt was retroactively falsified: `uv run gz arb validate --limit 800` expects exactly 8 findings, ALL of them `step.name=unittest` with a test-subset command. Any `typecheck` finding is a regression of the grandfather clause.
- Confirm the canonical scope is live: `uv run gz arb typecheck` expects exit 0 and a receipt whose `step.command` is `uv run ty check . --exclude features/**`.
- Confirm the quality gate: `uv run gz check` expects exit 0. Two advisories are expected and are not regressions — 692 unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning (parked by standing operator ruling).
- Confirm the full suite: `uv run gz arb step --name unittest -- uv run -m unittest -q` expects 8166 tests, exit 0.
- Confirm the sweep guard before any `--apply` on a dirty tree, never after: `uv run python -c "from pathlib import Path; from gzkit.commands.sync import _sweep_governed_paths; print(_sweep_governed_paths(Path(chr(46))))"`. A non-empty result means `gz git-sync --apply` will refuse and stage nothing.
- Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` expects `0` and `git rev-list --count HEAD..origin/main` expects `0`. Use these rather than the three-dot symmetric form, which the handoff authoring gate rejects as an unfilled-scaffold marker.
- Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `docs/design/adr/pool/ADR-pool.governance-document-structural-validation.md` — GHI #581's fold. Decision item 6 states the three reachability failure classes and the binding constraint that a two-valued liveness check is more confidently wrong than the existence check it replaces. Related GHIs records the seven re-derivations so promotion sees them.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — the Movement C family-closure box re-scoped to its criterion with the three arms and the measured 14-row third-state count, plus the operator-ratified amendment appended to the Amendments section. Also carries three of the five disclaimed counts.
- `src/gzkit/arb/validator.py` — the widened canonical typecheck scope, the per-entry statement of which gate mirrors which command, and `RETIRED_STEP_COMMANDS` with `_matches_retired_canon`.
- `src/gzkit/quality.py` — `run_typecheck` now READS the canonical entry; `run_transcribed_adr_counts_audit` is the new gate step.
- `src/gzkit/commands/arb.py` — `arb_typecheck_cmd` reads the same entry rather than spelling a third copy.
- `.pre-commit-config.yaml` — the `ty-check` hook entry, the one copy that cannot derive, pinned by equality instead.
- `scripts/session_orientation.py` — the five diagnostics fixed. `handoff_delta_rule` returned `tuple[str, object]` for a Callable, which is what made `commits_since_range(sha)` a call-non-callable.
- `tests/arb/test_typecheck_scope_lockstep.py` — 6 tests. Derivation is proven by moving the canonical value, not by comparing two literals.
- `tests/arb/test_validator_provenance.py` — the retired-canon clause and both its closing edges; the negative control rewritten so it is a genuine scope divergence rather than canon minus the launcher.
- `src/gzkit/governance/trust_audits/transcribed_counts.py` — the count fence. Opt-in registry, section and inline opt-outs, identifier-range exclusion, progress-cue window.
- `data/transcribed_count_surfaces.json` — the declared live surfaces. The comment states why opt-in is the design rather than an optimization.
- `tests/governance/test_transcribed_counts.py` — 14 tests, roughly half asserting what the audit must NOT flag.
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — the `transcribed-adr-counts` live control, planting both a live claim and a historical record.
- `docs/user/manpages/validate.md` — the `--transcribed-adr-counts` section: the opt-out table, the cue rule, and why the control plants both poles.
- `docs/user/manpages/arb.md` — the typecheck scope restated, with the reason it widened.
- `docs/governance/trust-doctrine.md` — the GHI #199 anti-pattern restated as a scope relation rather than two literal commands.
- `docs/governance/arb-middleware.md` — records that the defect was divergence, never the particular scope, and names the lockstep test.
- `data/check_scope_membership.json` — `transcribed_adr_counts` declared `in_check`; counts moved 86 to 87 registry scopes and 45 to 46 in-check.
- `tests/cli/test_validate_registry_parity.py` — the explicit-tier declaration with its rationale, including why the scope is explicit rather than default.
- `.gzkit/skills/gz-arb/SKILL.md` — canonical skill updated, the skill-version key nested under metadata moved 1.2.0 to 1.2.1, `last_reviewed` bumped, mirrors regenerated by sync.
- Commits: `641d4eab9` (#581 fold), `cd0fcf0f5` (Movement C re-scope), `3f40cae73` (typecheck scope), `5287c32ed` (#768 remedy).
- GHI #581 closed `superseded` and GHI #768 closed `fixed` this session. ARB receipts, each confirmed to resolve on disk before citation: arb-ruff-8884f2cda6f64e33b6063895972ba7e1, arb-step-typecheck-f7f371c840df4e91a480e5948c59c78e, arb-step-unittest-a392e4de9a7040d28365984f55f2d167.

## Settled Rulings

- Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (operator verbatim 2026-08-06: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). The residual the canon does not cover: a correction never traces back to the ADR it repaired.
- Work the session as 'commit, then traige' (verbatim), booked via gz handoff decide; advised steps 1, 3 and 4 were recorded set-aside, step 1 because origin/main was already 0/0 and the sync it advised had run before the predecessor handoff's ink dried.
- Do the top 5 of the triage list (verbatim: 'let's do the top 5 on the triage list').
- Direct fix beats riding the pool ADR where the fix removes or reuses rather than adding a parallel reader (operator: 'pool won't be promoted soon, is direct fix better?'). Applied per-item, which is what caught #581.
- Park all instructions-file budget work until the product stabilizes (verbatim: 'don't worry about any instructions file budgets right now, we want the product to stabilize').
- No ARB purge until insight retention is solid (verbatim: 'i don't want purges until guaranteed summaries for action-taking remedies are in place'), on the stated ground that 'there is no point in 1/2 measures now unless we are going to solve now'.
- Align the forcing-function surfaces as a direct fix (verbatim: 'ALIGN THESE!!!'), characterized by the operator as 'a direct fix for what is a clear defect of misalignment/incomplete implementation'.
- Build the efficacy channel (verbatim: 'efficacy channel is right — build it - these are all defects of design').
- Remedial action against a closed feature routes as a GHI direct fix referencing the original ADR (verbatim: 'GHIs that direct fix and reference the original adr seems prudent to me. this is a grey area, but the best I have at the moment'). This restates canon the operator had already booked; the genuine residual is that a correction never traces BACK to its ADR.
- The OBPI process must NOT be altered at all (verbatim: 'we will NOT alter the OBPI process, at all! This is a broader and per-session tool need'). This forecloses the critic alternative of extending adversarial_validation with a phase discriminator. Booked to insights 2026-08-07.
- Generalizing FROM the existing 4b skills and tooling is acceptable, but the OBPI pipeline itself stays untouched (verbatim: 'it is possible we generalize from the existing skills/tooling for obpi 4b, but I am hesitant to alter anything about the obpi pipeline as it is the most enduringly stable part of gzkit').
- The trigger is the convergence moment (verbatim: 'we are trying to jump in when you offer analyzed and considered design options in the same structed way - you've achieved convergence, within that session, when you do so, I need a 2nd opinion in that exact moment'). Explicitly not an Airlock Jr.
- Stated goal for the whole session, verbatim: 'retain cross-family review for consequential decisions'.
- Vendor posture is deliberately concrete, not generic (verbatim: 'I am trying to be specific: The US Air Force, the Chinese Air Force, etc. we can refactor to generics once we have platform stability'). Claude is the daily driver; Codex is the named adversary; the lock-in risk is accepted knowingly (verbatim: 'I need forward momentum, not design niceties - they can come with the refactor').
- Experimental refinement is expected (verbatim: 'we can experimentally refine this moving forward'), so a calibrated pilot is compatible with the ruling; a universal fail-closed gate on day one is not required.
- Park all instructions-file budget work until the product stabilizes (carried from the predecessor session).
- The critic accompanies the question rather than being absorbed by the agent (verbatim: "yes, it is a 2nd opinion, not a usurped opinion. this seems fitting: 'I re-pose the question carrying the critic's verdict unedited, the same way § Attestation makes me pass your words through unchanged.'"). `updatedInput` proved stronger than the ruling required: the harness enforces the passthrough, so the critique never enters the agent's context before the operator sees it.
- Maximum information flows to the hook (verbatim: "we should pass max information to the hook"). Already satisfied by the harness -- `transcript_path` gives the critic the entire session.
- The option cap and similar limits are accepted as design inputs (verbatim: "we can work with 4 options, and other limitations - contraints usually strengthen designs"; spelling preserved).
- Allowing the critic to actually run is the named next blocker (verbatim: "we need to allow the critic to operate, so that needs resolution").
- No OBPI-pipeline mechanism may be imported into this design yet (verbatim: "do not conflate any mechanism for the obpi pipeline with this work just yet"). The withdrawn latency figure is the concrete casualty.
- The agent equivocates after presenting converged options (verbatim: "the option you always provide is 'discuss this' (approximating): the critic needs to engage your premise. You almost always equivocate and hedge in the narrative that follows. easly a discernible majority of the time."; spelling preserved). Booked to insights as an `improvement` under scope `agent-narrative-discipline`.
- Authorized the probe and required the agent to clear its own gate (verbatim: "On probe, we can't proceed unless you do so"). Booked via `gz handoff decide` against the predecessor.
- Work all five advised steps (verbatim: "do the advised steps"). Booked via `gz handoff decide`; no step set aside.
- Injection shape is preamble-always plus an appended option when the base question carries 3 or fewer (selected from a 3-option picker with rendered previews). The critic's PREMISE-ATTACK/VERDICT map to the preamble, its UNASKED line to the option label.
- memory-hygiene is restructured, not retired: replace the witness and fix the wheel-shipped path defect, deferring the 41-file migration that would grow the parked instruction surface.
- Fix defects when found rather than parking them behind a fence ruling (verbatim: "do it right - fix defects when found"). This authorized the GHI #678 repair after the agent had parked it; standing canon already grants direct-repair authority to GHI-tracked defects, so the park was the error.
- Scope challenge on Step 4b (verbatim: "4b is opbi stuff, why surface it here? is it one of the 5 items?"). It IS advised step 3; it entered the design session because Step 4b is the existing precedent for cross-family adversarial review. The agent had flagged the campaign-sequencing tension but missed the OBPI-fence tension, which was the sharper of the two.
- Do advised steps 1 and 2 from the resumed handoff (verbatim: "do 1 and 2"); steps 3, 4 and 5 recorded set-aside via gz handoff decide.
- Rule and build, not merely rule (verbatim: "explain further, also, rule and build").
- The AskUserQuestion critic design belongs in a pool ADR, not a GHI comment (verbatim: "maybe the askuserquestion work should have been made into a pool adr - the handoff to handoff method seems to be diluting its design").
- Recover the design at full fidelity immediately (verbatim: "get it into a pool adr now, while the iron is hot" and "yes, do full capture, full recall, max context for highest quality adr authoring").
- Transcripts may be copied into an ADR package as appendices, trimmed to relevant passages but never condensed (verbatim: "allow transcripts to be copied as appenditures to an adr within its folder - these are vital original sources. so, this: "into the repo as ADR evidence" - they could be cleaned up to include only relevant passages - not condensed summaries, just trimmed").
- R1 -- the critic performs BOTH scope and conclusion challenge with full context; the either/or framing is rejected (verbatim: "why is this a choice? we want the adversary to get full context. measure twice, cut once").
- R2 -- the critic is a SKILL with three invocation doors: operator, agent, or gate (verbatim: "this is a skill but can be invoked by me, by agent, or at gate").
- R3 -- post-verdict resolution is operator plus main agent, modeled on Step 4b (verbatim: "operator and main agent work for resolution. obpi pipeline 4b already handles this well - observe it").
- R4 -- use the built-in Codex integration rather than a hand-rolled port (verbatim: "we just want to run the most up-to-date codex. Anthropic offers a built-in feature to call a codex adversary, why not use that and keep it simple?").
- GHI #766 takes option B -- retire the bookmark document, keep the signal as a ledger event -- with SessionStart as the forcing function (verbatim: "I liked your ledger suggestion, I just want sessionstart to see that legder entry and consult the transcripts").
- A handoff must carry its transcript so sensemaking is corroborated by the primary source; the ledger path is the floor, not the goal (verbatim: "I should get HIGHER QUALITY results when I call for a handoff that the ounter-checks the transcript, but I'll get some quality if I see that ledger entry and force the just-initiated agent to review prior transcript").
- The corroboration doctrine is ADR-shaped, not rule-shaped (verbatim challenge: "ok, but why not an adr?"). The agent's rule-file recommendation was withdrawn as a second instance of under-routing.
- Campaign placement for ADR-pool.convergence-moment-cross-family-critic is provisionally after ADR-0.35.0, explicitly not yet decided (verbatim: "after 0.35.0 I guess, not ready to decide").
- Proceed with sync first and the ADR second (verbatim: "Proceed — sync, then ADR"), booked via gz handoff decide against the predecessor handoff with no step set aside.
- The corroboration doctrine takes kind pool, not feature, after the agent offered a closed foundation kind and was challenged (verbatim: "why are you offering foundation ADRs?").
- Only one feature at a time (verbatim: "only one feature at a time, feature, finish, draw from pool"). Pool is the staging queue, not post-1.0 deferral; ADR-0.35.0 is the in-flight feature so a second feature ADR was never available.
- The archive half of the corroboration doctrine carries a redaction obligation stated at doctrine level, with the standing operator-PII prohibition binding on appendices. A mechanical pre-commit scrub gate was offered and declined.
- Fold three forcing-function findings into ADR scope: portable transcript references, a pointer liveness signal, and producer-stamped rather than authored.
- Fix both flagged items (verbatim: "fix both items") - the GHI #766 cross-reference and the orphan warnings.
- Work advised step 1 first (verbatim: "Step 1 first — rule on splitting GHI #766"), then return to the campaign; advised steps 3 and 4 recorded set-aside via `gz handoff decide`.
- Split GHI #766 and park both halves behind the doctrine ADR (verbatim: "Split; park both behind the doctrine ADR"). #767 filed for the transcript channel; #766 keeps bookmark retirement and is blocked by it.
- Correct the stale campaign counts and file the class-level defect (verbatim: "Fix it and file the class-level defect") — produced GHI #768.
- Sync, then survey ADR-0.35.0 before touching code (verbatim: "Sync, then survey ADR-0.35.0 first").
- Extend `gz content retire` in place rather than rename it to `withdraw` (verbatim: "Extend `retire` in place"); ADR-0.35.0 amended at five sites to match.
- Verify the family clustering before amending Magna Carta (verbatim: "Verify first, then ratify").
- Build the class-of-failure index as a real surface before writing campaign boxes against it (verbatim: "Build the class-of-failure index first").
- Ratify both Movement C amendments (verbatim: "ratify both, write handoff, git-sync").
- Determine C2's status before pulling the next work item (verbatim: "Determine C2 status first"). This overrode the agent's recommendation to set advised step 2 aside and go straight to GHI #770; the determination is what found the second-dispatch-path residual. Booked via `gz handoff decide`, with advised steps 2, 3, 4 and 5 recorded set-aside.
- Close the C2 residual immediately rather than filing it or amending around it (verbatim: "Close the residual now (Recommended)").
- Check C2 off, amend the campaign with the determination, and sync (verbatim: "Check C2 + sync").
- Work GHI #770 (verbatim: "do 770").
- Work advised step 4, the `gz git-sync` commit-shape question (verbatim: "Rule on the git-sync commit shape (step 4)"). Booked via `gz handoff decide`; advised steps 1, 2, 3 and 5 recorded set-aside, step 1 with the note that it is unexecutable as written because all five of its named members are closed.
- Refuse the bundle — `gz git-sync` fails closed when staged files carry source scope (verbatim: "Refuse the bundle (fence at sync)"). Selected from a four-option picker with rendered previews; the alternatives were split-the-commit, fix-the-query-not-the-commit, and warn-do-not-refuse.
- Write the recommendations into a handoff rather than executing them (verbatim: "write recommendations to handoff. git-sync"). D1 through D5 are carried as advised steps below, none of them started.
- Work D2 first, then D1 (verbatim: "D2 first, then D1"). Booked via `gz handoff decide` against the anchor; D3, D4 and D5 recorded set-aside.
- Take the converged `ghi-close` reading of D2 rather than the campaign-box or GHI #768 readings (selected from a four-option picker after the agent reported that D2's handoff arm had already landed in `ef3f9e0a2`). Both remaining arms land on one file, so "D2 first, then D1" was executed as a single pass.
- Author this handoff (verbatim: "write the handoff").
- Continue defect repair rather than pulling the campaign's Movement A sequence position (verbatim: "continue defect repair", given twice). This answered the predecessor handoff's advised step 1, which had put the sequencing question first precisely because it governs the other four.
- Author this handoff and sync (verbatim: "create new handoff - git sync").
- Pull the `#669` chain from the resumed handoff advised steps (verbatim: "Pull the #669 chain"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Collapse the three guard mechanisms to one monitor rather than mechanizing the current shape (selected from a four-option picker: collapse / validator-over-current-shape / route-to-pool / record-and-move-on). This ruling also selected the ROUTE: collapse frames the work as a correction against ADR-0.31.0 and routes to direct fix, where the validator-over-current-shape arm would have been an enhancement adding a CLI flag and routed to OBPI ceremony.
