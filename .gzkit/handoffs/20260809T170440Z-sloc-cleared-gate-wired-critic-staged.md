---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-09T17:04:40Z'
agent: g0
session_id: 970da8fc-e56e-4287-b30f-45b5974353d7
continues_from: .gzkit/handoffs/20260809T135757Z-chores-swept-three-failing-release-v0342.md
---

## Current State Summary

Discharged all five advised steps of the resumed anchor, then worked three operator-ruled follow-ons. Six commits landed and pushed; `origin/main` 0/0, tree clean.

MODULE-SLOC CORRECTION COMPLETE (`c3d9a99a0`). All four shrink-only breaches cleared by reduction, not re-baselining — `data/module_size_grandfather.json` untouched. Each extraction moved the cohesive family that GREW, attributed by `git log --numstat` over the overage window: the handoff parser family out of `parser_maintenance.py` (1667, ceiling 1582; GHI #757 alone was net +73 of the +85), the 720-line `gz obpi` group out of `parser_artifacts.py` (1760, ceiling 1743; every commit in the window added Step-4b flags), and the pure sensitivity record-walker out of `validate_cmd.py` (1354, ceiling 1309). The two CLI modules are named `parser_*.py` on purpose: `gzkit.doc_coverage.scanner` globs that pattern and reads `add_parser` string literals via AST, so any other name compiles, passes tests, and silently orphans manpages. `gz cli audit` held at 134/134 across both.

THE RATCHET NOW HAS A CALLER (`59931cb07`). `gz check` runs the module-size gate at step 4 of 53. It invokes the chore's own script rather than re-implementing the band check, with `--self-test` short-circuiting first. Enrolled in the ADR-0.0.73 QC registry as `bound` with a negative control.

GHI #782 CLOSED `fixed` (`eba0b0828`, then `96f5c0d77`) on a fourth option none of the issue's three arms had considered: criterion 6 was a strictly weaker duplicate of criterion 3's AST detector, so it was deleted rather than patched. The chore sweep then found two more greps of the same shape, and they were NOT clean deletions — the detector matched only `ast.Subscript`, so `for p in Path(__file__).parents:` slipped past it while the greps caught it. The detector was widened first, then the greps retired.

CAMPAIGN AMENDED TWICE (`99d98db45`, `e4c8eff44`). The cross-family critic was pulled ahead of `ADR-0.35.0`, then its delivery was staged after the adversary re-run its own § Promotion plan demanded returned `PERFORATED-BUT-NARROWABLE`.

FOUR GHIs FILED: #783 (71 runtime_state proof files ship in the wheel), #784 (a live brief omits `sensitivity` over a `ledger_integrity` overlap), #785 (no mechanism asks which gates have no automatic caller), #786 (the critic ADR's R4 transport premise is measurably wrong).

## Important Context

EVERY REAL FINDING THIS SESSION CAME FROM A GATE REFUSING THE AGENT, NOT FROM ITS OWN READING. The `verifier-pipe-gate` refused a piped `unittest` twice, before a false green could be read back. The QC registry refused to build for an unclassified `gz check` step and named the remedy in its own exception. `gz validate --transcribed-adr-counts` caught a transcribed OBPI count typed into the campaign plan. The chore's own criterion 5 caught a regression a targeted test run had passed. The agent's confident claims were the unreliable input; the mechanical witnesses were the correction.

ADDING A `gz check` STEP IS NOT ONE EDIT, AND THAT KNOWLEDGE HAD NO BINDING HOME. `_build_check_steps()` is the derived source for the ADR-0.0.73 QC registry, so a new entry obliges a `_STEP_CLASSIFICATION` entry, an `@enforces` negative control with no debt escape, an entrypoint, and a fixture. GHI #744's close comment enumerated all four "worth recording for the next person" — and this session re-derived the list by breaking 23 tests, because that record lived only in a closed issue's comment. Now written into `_build_check_steps()`'s own docstring. Point of use is the only placement that binds.

A REDUNDANCY ARGUMENT MUST BE PROBED, NOT ASSERTED. Criterion 6 was safely deletable because its needle was `parents[`, exactly the subscript form the AST detector covers. The two per-directory greps used `parents`, which is broader, and the probe proved the detector missed `for p in Path(__file__).parents:` entirely. Deleting them on the same argument would have been a real regression wearing a cleanup's clothes. The operator's ruling was an ordering, and the ordering was the whole content of it.

THE ADVERSARY'S DELIVERY VEHICLE IS NOT WHAT THE ADR BELIEVES. R4 ruled the shipped Anthropic plugin already supplies the transport. Measured on plugin `codex/1.0.6` with `codex-cli 0.147.0`: the plugin's `adversarial-review` command reviews BRANCH DIFFS — invoked here it returned "No branch diff against main was provided or present" — and the `codex:codex-rescue` forwarder is contracted to "return nothing" when Codex cannot be invoked. Two dispatches returned nothing, which is indistinguishable from an adversary that found no objections. Had the first empty return been accepted, this session would have reported "no objections" on a design that is in fact still perforated. What worked was `codex exec --sandbox read-only` driven from the main session.

THE FRESHNESS TREADMILL STILL BITES. `scripts/check_proof_freshness.py` compares commit epochs, so any commit touching `.gzkit/rules` re-stales all four control-surface chores. No rule files were edited this session, so the four stayed green; land rule edits BEFORE running those audits, never after.

THE HARNESS REPORTS THE WRONG EXIT CODE FOR BACKGROUNDED `cmd > log; echo "REAL EXIT: $?"` INVOCATIONS. The notification reports the trailing `echo`'s status, which is always 0. Read `REAL EXIT` out of the task output file. This masked a genuinely failing chore sweep once during this session.

## Decisions Made

- [operator-ruled] Work all four live advised steps of the resumed anchor (verbatim: "All four steps — 2, 3, 4, 5 in order"), selected from a four-option picker. Advised step 1 was recorded set-aside as already discharged: `origin/main` was 0/0 before the session began.
- [operator-ruled] GHI #782 takes a fourth option the issue body never listed — delete criterion 6 as redundant with criterion 3 (verbatim selection: "Delete criterion 6 — redundant with criterion 3"). The three arms in the issue all assumed the grep must survive; it did not, because `gz lint` already asserts the property via AST over the identical scope.
- [operator-ruled] Route the pre-existing `--sensitivity` red to a GHI rather than fixing the brief in-session (verbatim selection: "File a GHI alongside step 5"). The authoring call belongs to `ADR-0.35.0`, whose brief it is.
- [operator-ruled] Amend the campaign and pull the cross-family critic ahead of `ADR-0.35.0` (verbatim selection: "Amend the campaign — pull the critic now"), after the operator asked verbatim: "what happened to our 2nd opinion work? it is supposed to kick in anytime you invoke AskUserQuestion."
- [operator-ruled] File a GHI for the inverse-direction gate question rather than building the check immediately or only measuring (verbatim selection: "File a GHI for the inverse-direction check"). Produced GHI #785.
- [operator-ruled] Sweep all 39 chores for the #782 shape, reporting only, editing nothing (verbatim selection: "Sweep now, report, fix nothing yet").
- [operator-ruled] Re-run the adversary against the revised critic design before any promotion (verbatim selection: "Re-run the adversary first, then decide"), discharging the ADR's own § Promotion plan item 4.
- [operator-ruled] Widen the AST detector first, then delete the two remaining greps (verbatim: "widen the AST detector, then delete the two greps"). The ordering is the ruling: deleting first would have dropped the non-subscript coverage the greps uniquely carried.
- [operator-ruled] Stage the critic's delivery while keeping the pull-ahead (verbatim selection: "Amend to staged delivery, keep the pull-ahead"), on the adversary's `PERFORATED-BUT-NARROWABLE` verdict. The automatic `AskUserQuestion` door ships dark until a calibrated pilot measures false blocks, latency, operator reading time, and decisions changed.
- [operator-ruled] Record the R4 transport correction in both registers (verbatim selection: "Both — ADR correction and a GHI"). Produced the ADR's § R4 transport correction and GHI #786.
- [operator-ruled] Author this handoff and sync (verbatim: "yes handoff with git-sync").
- [agent-chose] Split the SLOC work into three commits rather than one, so each extraction is independently revertable and its attribution evidence sits with its own diff.
- [agent-chose] Classified the new `Module size` QC step `bound` rather than `advisory`. It exits 3 and gates the `gz check` exit code; calling a gating step advisory would have re-created the uncalled-gate hole under a different name.
- [agent-chose] Extracted only the PURE half of the sensitivity family from `validate_cmd.py`, leaving `_run_sensitivity_scope` behind. Relocating a renderer would have written to a console that `patch.object(validate_cmd, "console", ...)` never rebinds — the `0a2672562` lesson applied before it could bite rather than after.
- [agent-chose] Left `data/module_size_grandfather.json` untouched on shrink, following the `0a2672562` precedent, and flagged the resulting slack as an open loop rather than changing the ratchet's contract unasked.
- [agent-chose] Kept the six presence-greps in `agents-md-architectural-boundaries`. They are the SOLE witness for the six Architectural Boundaries sentences — those are not corpus-owned, so `--invariant-coherence` never sees them — and a presence assertion cannot mistake narration for an instance.
- [agent-chose] Stopped the flailing `codex:codex-rescue` subagent after two empty returns and drove `codex exec` directly, which the operator then correctly challenged; the challenge is what surfaced GHI #786.

## Immediate Next Steps

1. Author the critic pool ADR's `## Target Scope` and `## Proposed OBPI Decomposition` table, then promote. `uv run gz adr promote` is fail-closed today because the ADR has neither. Decompose against the THREE DOORS (operator, agent, gate), not the hook — the skill is the unit and the `PreToolUse` adapter is one OBPI that must land DARK. Carry the staged shape the campaign box now requires: skill, scope-first challenge, A3 envelope, R3 transition and provenance binding first; the automatic door lights only after a pilot measures false blocks, latency, operator reading time, and decisions changed. Target `--semver 0.36.0 --kind feature --lane heavy`; `0.36.0` is free (highest existing feature ADR is `0.35.0`, and `ADR-0.44.0` is absent from disk so its prior claim on the number is moot). Do NOT hand-wire a hook — that option was explicitly declined.

2. Work GHI #786 — scope the gzkit-owned transport. The shipped plugin's `adversarial-review` carries branch diffs, not decisions, so some gzkit surface must carry a decision to the adversary and a verdict back. This is an argument FOR the skill R2 ruled, and it weakens the adversary's own strongest no-build argument, which rested on the falsified premise that the plugin already supplies the transport.

3. Work GHI #785 — the inverse-direction gate question. Measured on `main`: 88 registry scopes, 13 default (all reachable via the bare invocation), 75 explicit, 41 explicit UNREACHED, plus 2 of 3 chore gate scripts with no caller. Do NOT read 41 as a remedy size: several scopes are deliberately explicit because they are expensive or single-artifact scoped. The tractable first move is inventory plus disclosure — make "this gate has no automatic caller" a counted, visible fact with an accepted-list that can only shrink, on the `data/module_size_grandfather.json` pattern. Which of the 41 deserve callers is a separate per-scope ruling and must not block making the count visible.

4. Work GHI #783 — 71 `runtime_state` proof files ship in the wheel. Deletion alone fixes the instance; the class fix is a converging sync that prunes `runtime_state` from the package side, or a distribution check that asserts absence rather than exempting presence. Without one, the next `gz chores run` writes a `CHORE-LOG.md` and the count climbs again.

5. Work GHI #784 — rule `sensitivity` on `OBPI-0.35.0-02-content-withdraw-verb.md`. One frontmatter line, or narrow the Allowed Paths. `src/gzkit/cli/**` is a broad glob and may be the real overlap cause rather than a genuine ledger-integrity surface. The scope is explicit-tier so `gz check` stays green while it is red, which is why it is also an instance under GHI #785.

## Pending Work / Open Loops

- THE RATCHET DOES NOT TIGHTEN ON SHRINK, AND THIS SESSION CREATED THE SLACK. `parser_maintenance.py` fell from 1667 to roughly 1388 SLOC while its grandfather entry still records 1582, so it may regrow about 194 SLOC without tripping. The gate's `_doc` says the LIST shrinks (entries are surrendered when a module drops under the band), not that recorded values tighten, and `0a2672562` set the precedent of not touching the file on shrink. Followed the precedent rather than change the contract unasked. UNFILED — needs an operator ruling on whether a shrink should re-record the lower ceiling.

- 29 OF 39 CHORES RUN THE FULL UNIT SUITE AS A CRITERION. At roughly 88 seconds each that is about 43 minutes of duplicated work in a full sweep, which is the mechanical reason the last two sessions both abandoned their sweeps partway. UNFILED.

- THE CRITIC'S PRIOR VERDICTS ARE ONLY PARTLY DISSOLVED. Pass 1 axis 2 and Pass 2's missing-policy attack are DISSOLVED by R4 and R3. Axes 1 (duplicates shipped machinery), 3 (inverted coverage) and 4 (campaign accretion) remain PARTIALLY ADDRESSED and are live against the promoted design. Strong subject binding — prompt hash, scope manifest, primary-output hash — is explicitly unbuilt, and R1 left the scope-time versus conclusion-time timing question the ADR calls "live" unresolved.

- A3 AND A4 ARE RULED ADOPT-NARROWED BUT NOT YET SPECIFIED. A3 narrows to one decision-scoped envelope rather than persistent state across every tool transition. A4 narrows to mandatory review for the enumerated consequential categories plus explicit operator requests, sampling the routine, with the constraint that the primary agent's own unvalidated confidence must NOT set the tier — the ADR itself asks whether that confidence is "placebo".

- GHI #785 SUBSUMES AN OLDER UNRULED LOOP carried across several handoffs: "54 of 89 registered validator scopes bind no scorecard row. Needs an operator ruling on whether the inverse direction gets an owner." Same inverse-direction question on the scorecard surface rather than the gate surface.

- `ADR-0.35.0-canon-entry-corpus-landing` IS NOW SECOND IN THE QUEUE, not first. It is `Draft` and unstarted, so the pull-ahead exchanged which feature is in flight rather than running two; the one-feature-at-a-time ruling is NOT relaxed. Run `uv run gz adr status ADR-0.35.0-canon-entry-corpus-landing` for its landed count.

- THE SESSION-EXIT BOOKMARK EVENT FIRED AS `session_exit_bookmark_skipped` at session start, which is the condition GHI #766 is open against.

## Verification Checklist

Run these before trusting any claim above. Read `REAL EXIT` from the log, never a harness exit-code notification on a backgrounded command whose last stage is an `echo`.

```
git rev-list --left-right --count origin/main...main    # expect 0 0
uv run gz check                                          # expect exit 0, 53 steps
uv run python .gzkit/chores/module-sloc-cap-radon/check_module_size.py   # expect exit 0
uv run gz cli audit                                      # expect exit 0, 134/134
uv run -m unittest tests.test_lint_parents               # expect exit 0, 6 tests
uv run gz chores advise hardcoded-root-eradication       # expect exit 0, 3 of 3 PASS
gh issue view 782 --json state                           # expect CLOSED
gh issue view 783 --json state                           # expect OPEN
gh issue view 784 --json state                           # expect OPEN
gh issue view 785 --json state                           # expect OPEN
gh issue view 786 --json state                           # expect OPEN
```

To confirm the module-size gate is genuinely wired rather than merely present:

```
uv run python -c "from gzkit.commands.quality import _build_check_steps; n=[x for x,_ in _build_check_steps()]; print('Module size' in n, n.index('Module size'), len(n))"
```

To reproduce the GHI #785 measurement (88 scopes, 13 default, 75 explicit, 41 explicit unreached), count `VALIDATOR_REGISTRY` entries by tier and match them against the `gz validate --<flag>` string literals in `src/gzkit/quality.py`. The coupling is a string literal, not a function call, so a name-match against the registry finds nothing.

To confirm the negative control has teeth rather than merely existing:

```
uv run python -c "from gzkit.governance.trust_audits._qc_negative_controls import _build_module_size; from gzkit.governance.trust_audits._qc_nc_entrypoints import _ep_module_size; print(bool(_ep_module_size(_build_module_size())))"
```

Expect `True` — the fixture plants a module over a deliberately small band and the production script must catch it.

A full 39-chore sweep costs roughly 43 minutes because 29 chores re-run the unit suite. Do not start one without budgeting for that.

## Evidence / Artifacts

Module extractions (`c3d9a99a0`):

- `src/gzkit/cli/parser_handoff.py` (new; the `gz handoff` group)
- `src/gzkit/cli/parser_obpi.py` (new; the `gz obpi` group)
- `src/gzkit/commands/validate_sensitivity.py` (new; the pure sensitivity walker)
- `src/gzkit/cli/parser_maintenance.py`
- `src/gzkit/cli/parser_artifacts.py`
- `src/gzkit/commands/validate_cmd.py`

Module-size gate wiring and QC enrolment (`59931cb07`):

- `src/gzkit/quality.py` (`run_module_size_audit`)
- `src/gzkit/commands/quality.py` (step tuple, plus the coupled-surface checklist in `_build_check_steps`'s docstring)
- `src/gzkit/qc_binding.py` (`_STEP_CLASSIFICATION` entry)
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` (`_build_module_size` fixture)
- `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py` (`_ep_module_size`)
- `tests/test_quality.py` (`TestModuleSizeInCheckPipeline`, 3 tests)

GHI #782 repair, both cuts (`eba0b0828`, `96f5c0d77`):

- `.gzkit/chores/hardcoded-root-eradication/acceptance.json` (6 criteria down to 3)
- `.gzkit/chores/hardcoded-root-eradication/CHORE.md` (the do-not-re-add note and its ordering rationale)
- `src/gzkit/quality.py` (`_find_parents_access_lines`, widened and renamed)
- `tests/test_lint_parents.py` (`test_non_subscript_parents_access_detected`)

Governance (`99d98db45`, `e4c8eff44`):

- `docs/governance/build-to-1.0-campaign-2026-07-18.md` (Movement A queue box, plus amendments 2026-08-09 and 2026-08-09 (2))
- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/ADR-pool.convergence-moment-cross-family-critic.md` (§ R4 transport correction)

ARB receipts:

- `artifacts/receipts/arb-step-unittest-cfb0141d2a7e46feadcd293d0c6310aa.json` (8270 tests, exit 0, after extraction 1)
- `artifacts/receipts/arb-step-unittest-4714752d4b2b40799193bffd010ef412.json` (8270 tests, exit 0, after all three extractions)
- `artifacts/receipts/arb-step-unittest-de42c1f55e284e97b31f56d135d34939.json` (8273 tests, exit 0, after QC enrolment)

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
- Work advised steps 1, 2, 3 and 4 from the resumed handoff; step 5 (scan for fail-closed refusals with no manpage coverage) recorded set-aside for the fourth time. Booked via `gz handoff decide`.
- GHI #768 takes accept-and-disclaim plus a fence, selected from a four-option picker over the four remedies filed in the issue body. The alternatives declined were marked-syntax validator, generated block, and commit-time coupling. Stop writing the number down; add a narrow check so the subtraction cannot decay back into a convention.
- GHI #581 closes `superseded` citing `ADR-pool.governance-document-structural-validation`, selected from a three-option picker. The alternatives declined were re-affirm TRACK-ONLY in the body, and direct-fix the third failure class only.
- The canonical typecheck scope widens to tree-minus-features, selected from a four-option picker. The alternatives declined were add-scripts-only, fix-the-diagnostics-without-a-scope-change, and leave-both-and-record-as-accepted.
- The Movement C doctrine-declared-without-mechanism box is kept open and re-scoped to its criterion, selected from a three-option picker. The alternatives declined were check-it-off and split-the-box.
- Correct the count, then work the arm (verbatim: "Correct the count, then work the arm"). Selected from a four-option picker after the agent reported that the campaign criterion figure did not reproduce. Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Work all 9 rows as drafted (verbatim: "Work all 9 as drafted"), from a four-option picker over the agent-drafted per-row disposition table.
- Rows 49 and 62 re-score to Judgment rather than being mechanized (verbatim: "Re-score both to Judgment (Recommended)"). This ratified the agent withdrawing its own mechanize recommendation after probes disproved the premise.
- Work the grandfathered rules one per commit, through all four (verbatim: "One rule per commit, work through all four"), accepting the full clause-scoring cost the Coverage Ledger forces.
- Enable BLE001 and defer PLC0415 (verbatim: "Enable BLE001, defer PLC0415 (Recommended)"). Six live bare-except violations are the observed drift the promotion freeze requires; the 138 lazy imports need per-site readings against the rule own carve-outs.
- Author this handoff (verbatim: "yes, author the handoff").
- Work all five advised steps (verbatim: "Step 1 — skill arm, Step 2 — ruff-code reachability check, Steps 3+4 — record deferred postures as accepted, Step 5 — rule on ADR-0.44.0,  we DO NOT go out of sequence (0.44.0)"). Selected as a multi-select over the agent-drafted step table; no step set aside.
- ADR-0.44.0 is PARKED, not finished (verbatim: "we DO NOT go out of sequence (0.44.0)"). This forecloses the checkbox's first arm; the agent had wrongly offered pull-it as live when campaign sequencing already ruled it out, and logged that as an improvement insight under scope handoff-resume-presentation.
- ADR-0.44.0 is an agent overreach with three acceptable dispositions (verbatim: "this was originally an agent overeach. this either becomes 0.36.0, revert to pool, or we just ignore/deleted the implemented code - I won't be paralyzed in purgatory."; spelling preserved). The closing clause is a standing instruction against stalling on this class of decision.
- File GHIs and fix them (verbatim: "ghis and fix - we are plagued by misalignments like this."). The second clause set the bar at class-level couplings rather than instance patches.
- Do not resequence out of order (verbatim: "we DO NOT go out of sequence (0.44.0)"), which foreclosed finishing the ADR in place.
- Review the handoff, then work advised step 1 (verbatim: "review the handoff", then "do step 1"). Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 were recorded set-aside at that point.
- Fix the H1/id mismatch as a class: rewrite all 38 pool files, fix `gz adr demote`, and narrow the byte-for-byte preservation test (selected from a four-option picker with rendered previews). This overrode the agent's recommendation to leave the mismatch alone, and the operator was right: the agent had verified there was no code consumer but had not checked whether the stale ids collide with live ones. Eight do.
- Sync the work (verbatim: "Sync now"), selected from a two-option picker.
- Scope GHI #777 as a class fix — teach `gz adr demote` to strip the kind-invalid ceremony section and backfill, rather than editing the id per line or fixing only the 8 observable collisions (selected from a four-option picker with rendered previews).
- Work advised step 2 (verbatim: "do step 2"). Booked via `gz handoff decide`, reversing its earlier set-aside.
- Repair `rename_chain_target` by subsumption — one shared fold with both readers delegating — rather than repairing it in place, deleting it, or recording the finding without a fix (selected from a four-option picker with rendered previews).
- Author this handoff carrying advised steps 3, 4 and 5 forward (verbatim: "write steps 3-5 to a fresh handoff").
- Review the handoff, then work advised step 1 (verbatim: "review handoff", then "Step 1 — widen the check"). Booked via `gz handoff decide`; advised steps 2, 3 and 4 were recorded set-aside at that point.
- Scope the widened check to executable witness paths plus ruff family citations, and NOT to `gz validate` scope flags (selected from a four-option picker with rendered previews). The flag arm was declined on the agent's own evidence that it finds nothing today — 36 cited flags, 36 resolve — and that the promotion-order freeze admits a check only on observed drift.
- Enable PTH package-scoped rather than re-scoring row 41 to Judgment (verbatim: "Enable PTH, package-scoped"), selected from a four-option picker after the agent surfaced that the grandfather pin on `cross-platform.md` makes the re-score path cost a full clause re-score while the enable path costs no rule edit.
- File a GHI through `/ghi-author` for the missing ARB rule-file citation rather than investigating it in-session or logging an insight (verbatim: "File a GHI via /ghi-author"), selected from a three-option picker. Produced GHI #778.
- Author this handoff and sync (verbatim: "write fresh handoff and git sync").
- Work advised steps 1 and 3 of the resumed handoff, instance-scope only on GHI #778 (verbatim: "Step 1 — fix GHI #778, Steps 1 + 3 — fix, then triage" and "Instance only (Recommended)"). Booked via `gz handoff decide`; advised steps 2 and 4 recorded set-aside.
- Rule the sequencing question after #778 and the triage (verbatim: "Fix #769, then pull ADR-0.35.0 (Recommended)"), selected from a four-option picker. This reversed the earlier set-aside of advised step 4.
- REVERSED that sequencing ruling in flight once #769 landed (verbatim selection: "Work more defect repair instead"). ADR-0.35.0 was NOT pulled. Recorded as an `improvement` insight under scope `campaign-sequencing` so the booked `gz handoff decide` text cannot be misread as evidence the feature was started.
- The "we will NOT alter the OBPI process, at all" freeze is NARROW (verbatim selection: "Freeze is narrow — work #765 in full"). It bars importing the cross-family critic design into `adversarial_validation`; it does not bar defect repair of the Step-4b gate. Recorded as an insight under scope `obpi-pipeline-freeze-scope`.
- Close GHI #765 `fixed` and file the residual rather than hardening in place (verbatim: "Close #765 fixed, file the residual (Recommended)"), on the ground that mandating a receipt raises the bar on every heavy-lane completion and deserves its own ruling. Produced GHI #780.
- Sync after the #778 repair (verbatim: "Sync now (Recommended)").
- Author this handoff and stop rather than continuing to GHI #719 or #747 (verbatim: "Write the handoff and sync (Recommended)").
- Work advised step 1 of the resumed handoff — GHI #719 (verbatim: "Step 1 — work GHI #719"), selected from a four-option picker. Booked via `gz handoff decide`; advised steps 2, 3, 4 and 5 recorded set-aside.
- Proceed on the resumed handoff, working advised steps 1-4 and setting step 5 aside (verbatim: "Rule steps 1–4, then work"). Booked via `gz handoff decide`.
- GHI #747 routes to a pool ADR parked behind ADR-0.35.0, not a direct fix (selected from a three-option picker). The issue self-labels `enhancement` and canon's direct-repair grant covers defects only; a headless OBPI is forbidden and no ADR promised the verb, so pool was the only available home.
- GHI #780 requires the ARB receipt, direct fix (selected from a three-option picker).
- The #780 requirement rides ANY resolved cross-vendor claim, not only a declared tier 1 (verbatim selection: "Any cross-vendor claim"). Ruled after the agent surfaced that the literal scope would have been a no-op fence.
- GHI #779 takes ratchet-plus-widen rather than line-level narration markers or widening alone (selected from a three-option picker).
- GHI #567 disposition: Move 2 as direct doc edits now, Move 1 to a pool ADR, Move 3 declined, then close `superseded` (selected from a four-option picker).
- Sync the five commits and author this handoff (selected from a four-option picker over the close-out).
- Cut patch release v0.34.2 (verbatim: "/gz-patch-release"), then approved the drafted narrative release notes (verbatim: "Approved — execute").
- Work the four-item routing in the order recommended (verbatim: "proceed as suggested"): fix the advise exit code first, then the control-surface chores, then module-SLOC, filing the hardcoded-root GHI alongside the first.
- Re-run the remaining three control-surface chores at full fidelity rather than a shallow pass, and apply the R18/R19 scope fix to governance-core.md (verbatim: "1. yes, 2. yes").
- Stop the SLOC correction after the first module, author a handoff, determine only the chores still failing, and git-sync (verbatim: "stop, write a new handoff, determine only the chores that still need to be passed. git-sync").
