---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T19:04:43Z'
agent: claude-code
continues_from: 20260808T173156Z-movement-c-rules-arm-closed.md
---

## Current State Summary

Resumed the anchor handoff, verified its claims against Layer-2, and worked all five advised steps under one operator ruling. Four commits, `gz check` 51/51 exit 0 at the last two.

**The skill arm is CLOSED, and its premise was wrong.** The anchor carried it as UNMEASURED on the belief that the advisory audit covers no skill mandate. It covers several — rows 28-33, 52 and 62b all score skill surfaces. The actual gap was ONE clause hiding in prose outside the table: Invariant 10a (skill-tool-invoke-same-turn) sat as free prose between two Scorecard subsections reading *is promotable — could be detected via hook analysis, but the signal-to-noise ratio is probably poor*. A discipline declared with neither witness nor admission is the forbidden third state, and this one was invisible to the family-closure criterion because it was never a row to count.

**The rules arm drove the Promotable COLUMN to zero while three prose sites still asserted a live Promotable band.** The other two named rows 29/30 and 23 — the very rows that read Judgment. That is Architectural Boundary 6 one surface over from the Summary table.

**A fifth false Mechanical row was found by the new check on its first live run.** Row 44 (no shell=True in subprocess) cited two S-family codes with the S family absent from select, and the single shell=True site already carried a justified S602 suppression that suppressed nothing because the rule never ran.

Summary re-fenced to 100 rows, 64/0/38/0. Branch 0/0 and tree clean but for governed paths at authoring.

## Important Context

**The premise of an advised step can be wrong while the step is still right.** The skill arm's stated finding (no skill coverage) did not survive a single grep, but the arm was genuinely open — just one clause over from where it was pointed. Verify the premise, not only the precondition.

**A suppression naming a rule that never runs is undetectable by inspection.** Row 44's S602 noqa and row 18's BLE0001 noqa are the same defect a rule apart: an author wrote a justified suppression believing the rule was on. Nothing reads a noqa against the select list, so the comment looks like diligence and is inert. Enabling the rule is what makes the existing comment start meaning something.

**A row can cite the wrong code and still look right.** Row 44 named S603 for no-shell-True — that rule is subprocess-without-shell-equals-true, the near-inverse, with 35 live hits. Naming the ruff RULE rather than its bare code would have made the miscitation visible on sight.

**The new check imposes a real constraint: a Mechanical row may not narrate a disabled code by its bare token.** It cannot tell a witness citation from a disclaimer. Accepted rather than worked around — a Mechanical row's job is to name its witness — but it bit twice while writing row 44's own correction.

**Exempt ROWS, not the section.** The prose fence first exempted the whole Scorecard section and therefore missed Invariant 10a, which lives inside it as free prose. Exempting the container excuses exactly the shape that gets a clause scored without becoming a row anyone counts.

**CLAUDE.md is a GENERATED surface.** Editing it directly passes every targeted check and fails gz check at Validate default scopes. The canonical is the claude template under .gzkit/templates; edit there and sync. On a case-insensitive filesystem the upper- and lower-case template names are one file.

**The resume gate's mutating-flag guard was the find over-grant mirrored.** There the flag set was trusted to cover a verb whose writes it could not see; here the in-place flag fired for verbs (sed, perl) the predicate already excludes, while blocking case-insensitive grep and rg. The membership test is now stated: a flag belongs only when some ADMITTED verb could carry it to write.

**gz arb validate gates nothing.** It is an on-demand provenance report, not a gz check step. That fact is what settled the 8 receipts after five sessions of delete-versus-accept — they were never blocking anything.

## Decisions Made

- [operator-ruled] Work all five advised steps (verbatim: "Step 1 — skill arm, Step 2 — ruff-code reachability check, Steps 3+4 — record deferred postures as accepted, Step 5 — rule on ADR-0.44.0,  we DO NOT go out of sequence (0.44.0)"). Selected as a multi-select over the agent-drafted step table; no step set aside.
- [operator-ruled] ADR-0.44.0 is PARKED, not finished (verbatim: "we DO NOT go out of sequence (0.44.0)"). This forecloses the checkbox's first arm; the agent had wrongly offered pull-it as live when campaign sequencing already ruled it out, and logged that as an improvement insight under scope handoff-resume-presentation.
- [agent-chose] Reframed step 1 after verification disproved its premise. The audit does cover skill mandates; the open item was Invariant 10a scored in prose rather than in a row.
- [agent-chose] Scored Invariant 10a **Judgment**, not Promotable. Mechanizing needs a turn's tool calls attributed to a skill step's semantics; gzkit models neither — the unmodelled-caller ground of row 62b. The original note already recorded the poor signal-to-noise objection with no observed instance, and the promotion freeze admits a check only on observed drift.
- [agent-chose] Stated the posture in CLAUDE.md's own text rather than re-scoring silently, per the anti-laundering rule the rules arm established — authored at the canonical template and synced.
- [agent-chose] Enabled S602 individually rather than the S family. Wholesale S adds 80 findings from rules no gzkit rule declares; S602 cost zero fixes because the one site was already justified.
- [agent-chose] Dropped row 44's second citation as miscited rather than enabling it. It is the near-inverse rule with 35 live hits.
- [agent-chose] Gated the ruff check on the SCORE and on a ruff anchor. Without the score gate it would punish the honest PLC0415 disclosure; without the anchor it would read markdownlint MD013 as a ruff claim.
- [agent-chose] Scoped the prose fence to **Promotable** alone. It is the third state the criterion counts; a Mechanical or Judgment narration is history, not a live classification.
- [agent-chose] Required a clause citation in the prose fence, so the Summary's conditional about what a return to Promotable would mean survives. It explains the score and assigns it to nothing.
- [agent-chose] Did NOT execute the demotion-to-pool arm of ADR-0.44.0. The ruling rules out pulling it, which is not the same as ordering it demoted; flagged as the residual instead.
- [agent-chose] Removed the in-place flag from the resume gate's guard rather than special-casing grep. The guard's own docstring states the premise that a flag an admitted verb can legally carry falsifies.
- [agent-chose] Left the cross-platform rule untouched. Promoting an already-claimed Mechanical makes nothing in it false, and editing a grandfathered rule forces a full clause re-score for no correctness gain.

## Immediate Next Steps

1. **Rule whether ADR-0.44.0 is demoted to pool, or stays a parked feature.** The only arm of this session's work left open, and it is open by design — the ruling foreclosed pulling it, which does not decide where it sits. The settled canon *only one feature at a time, feature, finish, draw from pool* points at demotion while ADR-0.35.0 is in flight, but demoting a partly-landed feature ADR is an artifact mutation with its own ceremony. **Route:** operator ruling, then the matching gz adr path.

2. **Decide whether the ruff-reachability check should widen beyond ruff.** It closes the narrow arm the anchor named and found a fifth false row immediately, but the class is *any* Mechanical row citing an enforcement surface — gz validate scope flags, pre-commit hook ids, test module paths. Each is mechanically resolvable and each would likely find something. **Route:** operator rules the scope, then direct fix.

3. **Consider making reachability an existence check.** Recorded as a stated limit: a mistyped code like BLE0001 is reachable under a BLE prefix select, so a typo still passes. Proving a code EXISTS means asking ruff, a subprocess this validator does not own. **Route:** operator decides whether a validator may shell out, then direct fix.

4. **Work the 138 PLC0415 sites, or leave the acceptance standing.** No longer an open loop — the posture is accepted and its reclassifying evidence is named — but the per-site pass remains genuinely available work if the operator wants the clause mechanized. **Route:** operator decides; not a defect until then.

5. **Sweep the remaining 17 grandfathered rules for false Mechanical rows.** The new check covers ruff citations only, and five false rows have now been found by hand across two sessions. Each grandfathered rule carries rows written against an unrecorded version. **Route:** operator rules scope; editing any of them forces a full clause re-score.

## Pending Work / Open Loops

1. **The demotion-to-pool question is the one deliberate open loop.** Recorded in the campaign line itself, not only here, so it cannot be lost with this handoff.

2. **A Mechanical scorecard row can no longer narrate a disabled ruff code by its bare token.** A real constraint of the new check, stated in its docstring and in row 44. Name the ruff rule instead. A future author who does not know this will read the refusal as a false positive.

3. **17 rules remain grandfathered against a baseline of 23** — unchanged this session. The pythonic rule was already ledger-scored, so its version bump cost only a ledger row, not a re-score.

4. **PLC0415 stands at 138 measured live violations, accepted.** Re-measured this session at the acceptance. S603 stands at 35 and is deliberately unselected.

5. **The 8 non-canonical unittest ARB receipts remain, permanently and correctly flagged.** Reclassify only if the count GROWS — that would mean a live producer defect rather than a fact about history.

6. **GHI #719, #769, #767, #766, #765, #533, #747, #611, #594, #579, #567 remain open.** Verified live this session; none were touched. Several are old and a triage sweep would say whether any are stale rather than deferred.

7. **RETIRED_STEP_COMMANDS is still append-only by convention with no mechanical witness.** Carried unchanged across three handoffs now. It is a candidate scorecard row.

8. **The AGENTS.md instructions-file budget advisory stands at 385 B over the codex delivery cap**, unchanged by this session's CLAUDE.md edit, and parked by standing operator ruling.

9. **ADR-0.35.0 is Pending with no OBPIs landed and Movement A stays deferred by explicit ruling, not drift.** Carried unchanged.

## Verification Checklist

Never pipe a verifier — the verifier-pipe-gate hook judges the pipeline, not the filter identity. Capture to a file and read the bare status. It fired twice this session.

Confirm the whole gate: `uv run gz check` expects exit 0, 51/51. Two advisories are expected and are NOT regressions — 692 unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning at 385 B (parked by standing operator ruling).

Confirm the scorecard arms: `uv run gz validate --advisory-scorecard` expects exit 0. The Summary table must read 64 Mechanical, **0 Promotable**, 38 Judgment, 0 Ambiguous across 100 rows. Three arms now ride this scope — coverage-ledger versions, summary drift, and (new) ruff reachability plus the prose fence.

Confirm the ruff arm actually discriminates rather than merely passing: add a Mechanical probe row citing PLC0415 to the Scorecard section and confirm the validator exits 3 naming it, then remove the row. A check that cannot be shown to fire is not evidence.

Confirm the prose fence exempts rows and not the section: the phrase Scored-Promotable-until appears inside Scorecard rows and must NOT be flagged, while a Promotable claim beside an Invariant or row citation outside a row must be. `uv run -m unittest tests.governance.test_advisory_scorecard_summary` expects exit 0, 21 tests.

Confirm S602 runs rather than merely being listed: `uv run ruff check .` expects exit 0, then plant a shell=True subprocess call in a scratch file at repo root and confirm ruff with S602 selected exits 1. Row 44 was configured-but-blind in exactly that way.

Confirm the resume gate permits case-insensitive reads: `uv run -m unittest tests.governance.test_handoff_resume_gate` expects exit 0, 51 tests. The in-place-edit test is the load-bearing half — it passed BEFORE the change too, which is the proof that the head predicate, not the flag guard, is what stops an in-place editor.

Confirm the negative controls discriminate: `uv run -m unittest tests.governance.test_enforcement_nc_discrimination tests.governance.test_enforcement_floor_wiring` expects exit 0.

Confirm CLAUDE.md is in sync after any edit to it: `uv run gz validate --surfaces` expects exit 0. A direct edit passes every targeted check and fails gz check at Validate default scopes.

Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` expects 0 and `git rev-list --count HEAD..origin/main` expects 0.

Confirm no active locks: `uv run gz obpi lock list` expects No active locks.

## Evidence / Artifacts

- `docs/governance/advisory-rules-audit.md` — new row 53a (Invariant 10a, Judgment); corrected row 44; row 23 posture accepted; Coverage Ledger bumped for the pythonic rule; Summary re-fenced to 100 rows 64/0/38/0; the three stale prose sites rewritten to point at the fenced table.
- `src/gzkit/governance/trust_audits/release.py` — the ruff-selection reader, the reachability predicate, the unreachable-claim arm, the prose-Promotable arm and its clause-citation regex, both wired into the audit entrypoint.
- `tests/governance/test_advisory_scorecard_summary.py` — 21 tests; two new classes pin the boundaries (score gate, ruff anchor, clause citation, row-not-section exemption).
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py` — the ruff-reachability live control, planting all three poles plus a pyproject without which the arm is hollow.
- `src/gzkit/handoff_resume_gate.py` — the in-place flag removed from the guard; the set's membership test stated.
- `tests/governance/test_handoff_resume_gate.py` — the case-insensitive-read test and its companion proving nothing was weakened.
- `pyproject.toml` — S602 selected individually, with the reason the whole family was refused.
- `.gzkit/rules/pythonic.md` — PLC0415 posture accepted, re-measured at 138.
- `docs/governance/arb-middleware.md` — the 8 non-canonical unittest receipts recorded as accepted, with the grows-not-exists reclassification trigger.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — ADR-0.44.0 parked with the operator's verbatim ruling and the demotion arm flagged as residual.
- `.gzkit/templates/claude.md` and `CLAUDE.md` — Invariant 10a's advisory posture stated in its own text, authored canonically and synced.
- `.gzkit/handoffs/20260808T181726Z-session-exit-bookmark.md` — the floor bookmark, now tracked (GHI #759).
- Commits: 5b921277f (resume-gate flag guard), 79774e620 (ruff reachability, row 44, bookmark), f8389e6da (prose fence, row 53a, skill arm), 21fc2f7a6 (three postures accepted), 8ce3568c9 (sync). The third and fourth SHAs were transposed at authoring — `21fc2f7a6` was read from HEAD *after* the postures commit and captioned as the prose fence, so a reader tracing "prose fence" would have landed on the wrong commit. Corrected in place.
- ARB receipts, each confirmed to resolve on disk before citation: arb-ruff-59d2f9c2130d40a298134434b33f6b6b, arb-step-typecheck-943d4ff615f84b3bbcdf34d30fee5ecc, arb-step-unittest-e7312188b7e14eaf910a7fd7e7a7a814 (8194 tests).

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
