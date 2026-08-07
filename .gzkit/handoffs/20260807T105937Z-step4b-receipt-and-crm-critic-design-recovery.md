---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-07T10:59:37Z'
agent: claude-code
continues_from: 20260807T030745Z-advised-steps-discharged-step4b-tier-binding.md
---

## Current State Summary

Resumed the 2026-08-07 exit bookmark, discharged its two advised steps, then worked two operator-directed builds to completion and recovered a diluted design from primary sources. Seven commits on main, all pushed (origin/main 0/0 at authoring).

Build 1 landed GHI #765: Step-4b tier-1 is now proven from an ARB step receipt's recorded argv rather than asserted by the caller. Build 2 was redirected mid-flight by the operator from "implement the critic hook" to "capture the design properly" after they observed that carrying it handoff-to-handoff had degraded it -- verbatim, "multiple audio tape recordings of audio tape recordings where the quality is dissipating rapidly". The design now lives in ADR-pool.convergence-moment-cross-family-critic as a package with four primary-source appendices.

The session's through-line is one defect class, named by the operator: a summary without its primary source is an assertion. It appeared on three surfaces -- a Step-4b verdict without a receipt, a handoff without its transcript, an ADR built from handoffs. The operator calls it the Memento problem.

## Important Context

The recovery method is the reusable lesson. Session transcripts are Layer-1 primary sources; handoffs are Layer-3 summaries. The critic design had been carried across three handoffs and lost most of its substance. Going back to the transcripts (882dfc48, d01f355f, 8e5c43b1) recovered: the CRM/flight-deck framing the whole design is built on (the prior ADR draft did not contain the string "CRM"); the fact that BOTH independent Codex passes returned PERFORATED, not merely "challenged"; and the hardest number in the corpus -- 239 AskUserQuestion calls against 41,624 assistant turns over 160 transcripts, so the convergence-moment trigger covers 0.57% of turns.

Transcripts expire on a ~30-day rolling window. No cleanupPeriodDays is configured and the oldest surviving transcript measured exactly 30 days on 2026-08-07, so the three design sessions expire around 2026-09-05. That is why the ADR became a package with appendices rather than a document citing session IDs -- a pointer alone would have dangled. Pre-commit formatters were excluded from docs/design/adr/.*/appendices/ after end-of-file-fixer and trailing-whitespace rewrote the archived evidence on first commit attempt; a formatter that rewrites a primary source destroys the one property it must have.

Two verification traps fired against this session's own work. First, a background-task completion notification reports the exit code of the LAST command in a compound invocation -- it reported "exit code 0" while gz check had exited 1. Run verifiers BARE in background tasks. Second, the pre-commit xenon hook caught _enforce_adversarial_validation at rank D after the receipt logic was added inline; the extraction into _enforce_adversary_receipt is that fix, not a speculative seam.

The agent under-routed design to the cheaper artifact twice and was corrected both times -- a GHI comment instead of a pool ADR, then a rule file instead of an ADR. Rules are the enforcement surface for a decision an ADR made (13 of 26 cite parent ADRs). Both corrections are logged to insights under scopes ghi-destination-routing and artifact-routing.

## Decisions Made

- [operator-ruled] Do advised steps 1 and 2 from the resumed handoff (verbatim: "do 1 and 2"); steps 3, 4 and 5 recorded set-aside via gz handoff decide.
- [operator-ruled] Rule and build, not merely rule (verbatim: "explain further, also, rule and build").
- [operator-ruled] The AskUserQuestion critic design belongs in a pool ADR, not a GHI comment (verbatim: "maybe the askuserquestion work should have been made into a pool adr - the handoff to handoff method seems to be diluting its design").
- [operator-ruled] Recover the design at full fidelity immediately (verbatim: "get it into a pool adr now, while the iron is hot" and "yes, do full capture, full recall, max context for highest quality adr authoring").
- [operator-ruled] Transcripts may be copied into an ADR package as appendices, trimmed to relevant passages but never condensed (verbatim: "allow transcripts to be copied as appenditures to an adr within its folder - these are vital original sources. so, this: "into the repo as ADR evidence" - they could be cleaned up to include only relevant passages - not condensed summaries, just trimmed").
- [operator-ruled] R1 -- the critic performs BOTH scope and conclusion challenge with full context; the either/or framing is rejected (verbatim: "why is this a choice? we want the adversary to get full context. measure twice, cut once").
- [operator-ruled] R2 -- the critic is a SKILL with three invocation doors: operator, agent, or gate (verbatim: "this is a skill but can be invoked by me, by agent, or at gate").
- [operator-ruled] R3 -- post-verdict resolution is operator plus main agent, modeled on Step 4b (verbatim: "operator and main agent work for resolution. obpi pipeline 4b already handles this well - observe it").
- [operator-ruled] R4 -- use the built-in Codex integration rather than a hand-rolled port (verbatim: "we just want to run the most up-to-date codex. Anthropic offers a built-in feature to call a codex adversary, why not use that and keep it simple?").
- [operator-ruled] GHI #766 takes option B -- retire the bookmark document, keep the signal as a ledger event -- with SessionStart as the forcing function (verbatim: "I liked your ledger suggestion, I just want sessionstart to see that legder entry and consult the transcripts").
- [operator-ruled] A handoff must carry its transcript so sensemaking is corroborated by the primary source; the ledger path is the floor, not the goal (verbatim: "I should get HIGHER QUALITY results when I call for a handoff that the ounter-checks the transcript, but I'll get some quality if I see that ledger entry and force the just-initiated agent to review prior transcript").
- [operator-ruled] The corroboration doctrine is ADR-shaped, not rule-shaped (verbatim challenge: "ok, but why not an adr?"). The agent's rule-file recommendation was withdrawn as a second instance of under-routing.
- [operator-ruled] Campaign placement for ADR-pool.convergence-moment-cross-family-critic is provisionally after ADR-0.35.0, explicitly not yet decided (verbatim: "after 0.35.0 I guess, not ready to decide").
- [agent-chose] Did NOT repair _is_cross_vendor_adversary to token membership. Testing the proposed fix against real ledger data disproved it: two recorded adversaries read "codex-unavailable", so a scan admitting a mentioned vendor would classify degraded Claude-family runs as tier 1 -- failing OPEN. The prefix scan's conservatism is a safe wrong answer and was left intact with a test fence pinning why.
- [agent-chose] Filed GHI #765 as a sibling cut of #678 rather than reopening it. #678 bound the declared tier; #765 asks whether the bound value is provable, which #678's fix cannot answer by construction.
- [agent-chose] Left the _CROSS_VENDOR_ADVERSARY_PREFIXES residual unfiled. The gap is prospective, it is recorded as Risks item 8 in the ADR, and the proper fix is the vendor-neutral port that R4 deferred.

## Immediate Next Steps

1. Author the corroboration-doctrine ADR. Operator ruled it is ADR-shaped, not a rule. It decides that a summary artifact must cite the primary source corroborating it, and that the corroboration window must match the artifact lifetime -- pointers for short-lived artifacts, archived passages for permanent ones. Rejected alternatives to record: pointer-only, archive-everything, extend cleanupPeriodDays. It requires building: a structured transcript field on HandoffFrontmatter (which is extra=forbid, so this is a model change under ADR-0.0.65), the session_exit_uncovered ledger event, and generalizing the ADR-appendix pattern. The design is captured in GHI #766 comments meanwhile.
2. Execute GHI #766 as ruled: replace the seven-constant-section bookmark with a session_exit_uncovered event carrying session_id and transcript_path; teach SessionStart orientation to read it and direct the incoming agent to the transcript. Note the coupling -- retiring the bookmark removes the only reliable transcript citer in the system (20 of 277 authored handoffs mention one), so landing this without the handoff transcript channel is a net loss of corroboration.
3. Fix the ledger event asymmetry surfaced under #766: ledger_events.py defines session_exit_bookmark_skipped_event and no corresponding written event, so six bookmark files exist with zero ledger counterparts. The beat books its non-actions and not its actions.
4. Return to the campaign. Nothing this session was on the Build-to-1.0 checklist; the topmost unchecked item remains Movement A item 2, ADR-0.35.0-canon-entry-corpus-landing at 0/10 OBPIs landed.
5. Consider whether transcript retention should be extended. Everything recovered this session came from files that expire around 2026-09-05. The ADR is safe because its sources are in-package; no other artifact carries that protection.

## Pending Work / Open Loops

- The corroboration-doctrine ADR is unwritten. Design captured in GHI #766 comments; the decision home does not exist yet.
- GHI #766 is open and now carries two coupled halves: bookmark retirement and the handoff transcript channel. If they split, the transcript channel is the larger surface and should get its own GHI.
- ADR-pool.convergence-moment-cross-family-critic is Pool, unpromoted, campaign placement undecided. Promotion owes four things: decompose against the three doors rather than the hook; generalize Step 4b resolution without altering 4b; adjudicate the still-unruled critic alternatives (persistent decision envelope, risk tiering, strong subject binding); and RE-RUN the adversary against the revised design, since both prior verdicts perforated a mechanism R1-R4 materially changed.
- The _CROSS_VENDOR_ADVERSARY_PREFIXES residual is unfiled by choice. The receipt proves which binary ran, not which model family answered.
- A cheap tightening was proposed and not applied: require the Step-4b adversary invocation to name the model in argv so the receipt captures it. Skill text only, no code.
- The hook-surface currency chore is unbuilt -- gzkit wires 6 hook events against a materially larger exposed set. Recorded in the ADR as separable, chore-shaped.
- AGENTS.md remains 385 B over the Codex delivery cap; instructions-budget work stays parked by standing ruling.
- ARB harvest still reads a fraction of accumulated receipts; carried untouched across five sessions now.
- Movement C remains a 1.0 gate that every new mechanism runs against.

## Verification Checklist

- Confirm the seven commits are present and pushed: git log --oneline -8 shows bdd858fee through cd4e14687; git rev-list --left-right --count using the three-dot range against origin/main reads 0 0.
- Re-run the Step-4b gate suite reading the verifier own exit code, never a pipe: uv run -m unittest tests.test_adversarial_validation_gate > out.log 2>&1; echo $? expects 0 across 44 tests.
- Confirm the new flag is registered and documented: uv run gz obpi complete --help shows --adversary-receipt RUN_ID, and uv run gz cli audit exits 0 at 134/134.
- Confirm the ADR package validates: uv run gz register-adrs reports 86 ADRs; uv run gz validate --documents --adr-status-fresh --taxonomy exits 0 across 3 scopes.
- Confirm the appendices are byte-identical to their extraction and were not rewritten by hooks: the A2 and A3 files must not have gained a trailing newline, and .pre-commit-config.yaml must exclude docs/design/adr/.*/appendices/ on both end-of-file-fixer and trailing-whitespace.
- Confirm GHI state: gh issue view 670 --json state reads CLOSED, 765 OPEN, 766 OPEN.
- Full gate: uv run gz check exited 0 across 50 checks at authoring time, with two standing advisories (instructions-files budget, spec-test-code drift) that do not affect exit code.

## Evidence / Artifacts

- `src/gzkit/commands/obpi_complete.py` -- `_receipt_proves_cross_vendor`, `_load_adversary_receipt`, and `_enforce_adversary_receipt`; precedence is proven over declared over inferred.
- `src/gzkit/cli/parser_artifacts.py` -- the `--adversary-receipt` flag.
- `src/gzkit/events.py` -- `adversary_receipt` on the typed read path.
- `src/gzkit/schemas/ledger.json` -- the structural-validator arm of the same field.
- `tests/test_adversarial_validation_gate.py` -- 44 tests, 16 new; includes the fence pinning why the name scan is deliberately not repaired to token membership.
- `docs/user/manpages/obpi-complete.md` -- flag row plus a worked example carrying real observed ARB output.
- `.gzkit/skills/gz-obpi-pipeline/SKILL.md` -- Step 4b now teaches the receipt channel; skill-version 6.34.0.
- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/ADR-pool.convergence-moment-cross-family-critic.md` -- the recovered design, rulings R1-R4, both PERFORATED verdicts, twelve unadjudicated alternatives.
- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/appendices/A1-operator-turns-verbatim.txt` -- 29 operator turns, verbatim.
- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/appendices/A2-codex-verdict-pass1-perforated.txt` -- Pass 1 verdict, complete.
- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/appendices/A3-codex-verdict-pass2-perforated.txt` -- Pass 2 verdict, complete.
- `docs/design/adr/pool/ADR-pool.convergence-moment-cross-family-critic/appendices/A4-operator-exhibit-askuserquestion-picker.png` -- the operator exhibit, decoded from a transcript base64 block after the image cache had been cleared.
- `.pre-commit-config.yaml` -- formatters excluded from ADR appendices so archived evidence is not rewritten.
- `.gzkit/insights/agent-insights.jsonl` -- three records this session: verification-exit-integrity, ghi-destination-routing, artifact-routing.

Transcript corroboration for this handoff (primary source, outside the repo and expiring ~2026-09-05):
- This session: /Users/jeff/.claude/projects/-Users-jeff-Documents-Code-gzkit/31073cf8-6f3f-45a7-b2c0-ad4a3ba58f76.jsonl
- Design sessions recovered from: 882dfc48-123b-4b9e-aaff-e2909cd4fe06, d01f355f-362e-45ed-9ed8-4d30ad06d452, 8e5c43b1-7bf5-423b-b4f4-599b1eee0840

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
