---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-07T19:22:15Z'
agent: claude-code
session_id: adbba522-a3a4-4812-b872-0e3ae0e0f7f1
continues_from: .gzkit/handoffs/20260807T105937Z-step4b-receipt-and-crm-critic-design-recovery.md
---

## Current State Summary

Session opened on a git-sync request and ran to three completions. Sync landed the pending session-exit bookmark plus the booked handoff ruling, then later the ADR package and the defect repair. The corroboration-doctrine ADR advised by the predecessor handoff was authored as ADR-pool.primary-source-corroboration (pool kind, heavy lane, registered, adr_created booked, status index regenerated at 86 ADRs). A defect surfaced in flight during that registration and was direct-fixed: gz register-adrs was reporting 358 orphan OBPIs, every one of them parked rather than missing. GHI #766 now carries a cross-reference recording that the doctrine has a decision home and that the issue retains the bookmark-retirement half. Four commits on main, all pushed, origin/main even at authoring. This handoff supersedes the mechanical session-exit bookmark at .gzkit/handoffs/20260807T110928Z-session-exit-bookmark.md, which SessionStart had flagged for sensemaking.

## Important Context

The foundation kind is CLOSED, and reading past that cost the most time this session. ADR-0.34.0-foundation-sunset sealed authoring-time rejection at all three CLI doors, so no new foundation ADR can be created; pool and feature are the two live kinds (campaign line 73). The agent offered a foundation ADR anyway after reading the campaign movement NAME (close the Foundation Sunset) rather than its content, then reinforced the error by computing a next-free foundation integer from a directory listing. A single gz plan create --kind foundation probe refutes it in two seconds and prints the reason.

Rich console output wraps at terminal width, and the wrapped remainder can read as a data defect. Eleven orphan lines appeared to carry empty ids at default width; COLUMNS=300 showed zero, and a ledger scan found no OBPI events with empty ids. Re-render wide before characterizing any pattern in console output as a defect.

The orphan repair turns on a two-flag asymmetry. withdraw and park both mean the brief is intentionally absent, but park arrived later (GHI #584) as the reversible counterpart and nothing went back to teach the detector about it. The parked flag was already materialized onto the artifact graph by _apply_obpi_parked_metadata, so the data was present and only the reader was stale. Because park is two-way, obpi_unparked correctly returns an OBPI to orphan reporting.

PIPESTATUS is a bash-ism and this shell is zsh, so exit codes read back empty from a pipeline. Separately the verifier-pipe-gate PreToolUse hook refuses a verifier in any non-final pipeline stage outright. Capture to a file and read the real status.

Pool ADRs take a different authoring path than feature ADRs: gz interview adr fails closed on a pool id, the scaffold comes from gz plan create --kind pool, the post-authoring evaluate gate is exempt until promotion, and the Step-0 interview artifact is stored beside the ADR as slug-interview.json (an established convention, three prior examples).

## Decisions Made

- [operator-ruled] Proceed with sync first and the ADR second (verbatim: "Proceed — sync, then ADR"), booked via gz handoff decide against the predecessor handoff with no step set aside.
- [operator-ruled] The corroboration doctrine takes kind pool, not feature, after the agent offered a closed foundation kind and was challenged (verbatim: "why are you offering foundation ADRs?").
- [operator-ruled] Only one feature at a time (verbatim: "only one feature at a time, feature, finish, draw from pool"). Pool is the staging queue, not post-1.0 deferral; ADR-0.35.0 is the in-flight feature so a second feature ADR was never available.
- [operator-ruled] The archive half of the corroboration doctrine carries a redaction obligation stated at doctrine level, with the standing operator-PII prohibition binding on appendices. A mechanical pre-commit scrub gate was offered and declined.
- [operator-ruled] Fold three forcing-function findings into ADR scope: portable transcript references, a pointer liveness signal, and producer-stamped rather than authored.
- [operator-ruled] Fix both flagged items (verbatim: "fix both items") - the GHI #766 cross-reference and the orphan warnings.
- [agent-chose] Chained this handoff from 20260807T105937Z rather than from the session-exit bookmark. The bookmark is CHECKPOINT mode and carries no Settled Rulings, so chaining to it would have dropped fourteen booked rulings from the successor.
- [agent-chose] Routed the orphan detector repair as a direct fix rather than ceremony: 341 fix-commit precedents in 60 days, one module, two source lines, unit-testable without a new BDD scenario.
- [agent-chose] Filed no GHI for the orphan repair, per the standing moratorium against filing a GHI merely to satisfy a commit trailer. Used Task: TASK-orphan-detector-skips-parked.
- [agent-chose] Delegated the ADR body to an opus subagent per the gz-adr-create self-escalation clause, then verified the output and corrected one unmeasured count (13 of 26 rules citing a parent ADR) that the agent had itself relayed unmeasured from a prior GHI comment. Measured value is 15 of 26.

## Immediate Next Steps

1. Decide whether GHI #766 should split. It now carries the bookmark-retirement half while the doctrine lives in the ADR. The ordering constraint stands and is recorded in both: the handoff transcript channel lands BEFORE bookmark retirement, because retiring the mechanical bookmark removes the only reliable transcript citer in the system.
2. Return to the campaign. Movement A item 2 remains topmost: ADR-0.35.0-canon-entry-corpus-landing at 0 of 9 OBPIs landed. Nothing this session was on the Build-to-1.0 checklist.
3. Consider the ledger event asymmetry recorded across two sessions and still unfixed: src/gzkit/ledger_events.py defines session_exit_bookmark_skipped_event with no corresponding written-event counterpart, so bookmark files exist on disk with zero ledger events. The beat books its non-actions and not its actions.
4. When ADR-pool.primary-source-corroboration is drawn from pool, resolve the ownership question it deliberately left open: whether ADR-0.0.65 or the OBPI-0.0.72-02 superset design owns HandoffFrontmatter, and therefore which ADR the transcript field lands under.

## Pending Work / Open Loops

- ADR-pool.primary-source-corroboration is Pool and unpromoted, with no campaign placement decided. Its risk item 7 records the strongest argument against it: the real defect may be hop count rather than missing corroboration, since the critic design degraded across three handoffs and fewer hops would have preserved it with no corroboration machinery at all.
- The session-exit bookmark at 20260807T110928Z is superseded by this handoff but remains on disk. It was committed by this session because the exit beat structurally cannot commit its own output.
- GHI #766 remains open and now carries two coupled halves, with the transcript-channel half identified as the larger surface that should get its own issue if they split.
- ADR-pool.convergence-moment-cross-family-critic promotion still owes the four items the predecessor handoff named, including re-running the adversary against the revised design since both prior verdicts perforated a mechanism the R1-R4 rulings materially changed.
- The _CROSS_VENDOR_ADVERSARY_PREFIXES residual remains unfiled by choice: the receipt proves which binary ran, not which model family answered.
- AGENTS.md instructions-budget work stays parked by standing operator ruling until the product stabilizes.
- ARB harvest still reads a fraction of accumulated receipts, carried untouched across six sessions now.

## Verification Checklist

- Confirm the four commits are present and pushed: git log --oneline -4 shows 584f9ec47, 9131c191c, 1b6449957 and a68c406d6; git status --short --branch reads main...origin/main with no ahead or behind marker.
- Confirm the orphan repair holds, reading the verifier exit code bare rather than through a pipe: COLUMNS=300 uv run gz register-adrs > out.log 2>&1; echo $? expects 0, and grep -c "orphan:" out.log expects 0 (was 358 before 9131c191c).
- Re-run the register test module bare: uv run -m unittest tests.commands.test_register_adrs > out.log 2>&1; echo $? expects 0 across 14 tests, including the new parked case and the pre-existing withdrawn case.
- Confirm the ADR package validates: uv run gz validate --documents --taxonomy --adr-status-fresh > out.log 2>&1; echo $? expects 0 across 3 scopes; uv run mkdocs build --strict expects 0.
- Confirm no active locks: uv run gz obpi lock list reports No active locks.
- Confirm GHI state: gh issue view 766 --json state reads OPEN and carries the ADR cross-reference comment.
- Never pipe a verifier. The verifier-pipe-gate PreToolUse hook refuses it, and PIPESTATUS reads back empty under zsh.

## Evidence / Artifacts

- `docs/design/adr/pool/ADR-pool.primary-source-corroboration.md` - the doctrine ADR, four sections, with the reversibility split driving the liberal-with-pointers principle and eleven recorded risks.
- `docs/design/adr/pool/primary-source-corroboration-interview.json` - the Step-0 interview artifact, including the two forcing functions the sibling exemplar omits (constraint archaeology, assumption surfacing).
- `src/gzkit/commands/register.py` - _detect_orphan_obpis now skips parked alongside withdrawn; docstring records why and notes that park is two-way.
- `tests/commands/test_register_adrs.py` - the parked mirror of the withdrawn case; first coverage this detector has ever had.
- `.gzkit/insights/agent-insights.jsonl` - three improvement records this session under scopes adr-kind-selection (twice) and diagnostic-claims.
- `.gzkit/handoffs/20260807T110928Z-session-exit-bookmark.md` - the mechanical bookmark this handoff supersedes.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` - line 73 carries the closed-foundation taxonomy ruling that the kind error contradicted.

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
