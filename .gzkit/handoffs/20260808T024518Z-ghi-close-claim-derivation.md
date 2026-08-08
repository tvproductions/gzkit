---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T02:45:18Z'
agent: claude-code
session_id: 838b144d-34be-4d4f-8728-7126249ae97b
continues_from: .gzkit/handoffs/20260808T013508Z-sweep-guard-widened-and-defect-ledger.md
---

## Current State Summary

Session opened on a handoff review, found the anchor's top-ranked item already fixed, and closed the residual plus the item beneath it as one GHI.

**This handoff supersedes two documents.** The authored anchor `20260808T013508Z-sweep-guard-widened-and-defect-ledger.md` carried five ranked recommendations (D1-D5) written to be carried rather than executed; the operator ruled "D2 first, then D1" and D3/D4/D5 were booked set-aside. The mechanical CHECKPOINT bookmark `20260808T020817Z-session-exit-bookmark.md` was a floor record with no authored content; it was committed in `4344ad69b` so its Layer-2 `handoff_path` has a referent in a fresh clone, and its sensemaking is this document.

**D2 was already fixed when the ruling was given.** `ef3f9e0a2` — the anchor's own successor commit, authored after it — closed the handoff-authoring arm exactly as D2 prescribed: `create_handoff` takes a `reference_checker`, reuses the existing `ReferenceChecker` port rather than standing up a second resolver, scopes to prospective sections, and annotates settled citations. It names the same GHI #573 instance this session re-found. The anchor was one commit stale on its own top recommendation.

**What remained was one surface, not two.** D2's residual (GHI close comments cite issues without resolving them) and D1 (the class-of-failure claim is prose nothing checks) both land on `.gzkit/skills/ghi-close/SKILL.md`. Filed as GHI #771, fixed across `4344ad69b` and `deb6d7f6b`, closed with the new template as its own first use. `uv run gz check` exit 0 on both commits; synced at `e26467c0f`; `origin/main` 0/0 and tree clean at authoring.

## Important Context

**D1's prescribed remedy would not have caught its own motivating instance, and this is the session's most portable finding.** The anchor prescribed extending `ghi-close` so the class claim must "name its covering tests". GHI #708's 2026-07-21 close comment **already named three tests**, one section above the claim they backed. The actual gap was that the claimed family had four causes and the comment enumerated three, omitting the one that was the entire premise of the flag the guard sat inside. A remedy stated at the level of an artifact's *shape* ("name X") misses a defect whose mechanism is the *moment of derivation* ("re-derive X at this close"). Recorded as a `discovery` insight under scope `ghi-close-claim-derivation`. When grading any advised remedy, test it against the instance that motivated it before implementing.

**The anchor attached its D2 finding to GHI #768, which does not contain that scope.** #768's filed Class of failure names transcribed `N/M` **OBPI counts** in governance prose across 135 files under `docs/`. The anchor's D2 was about GHI-reference liveness. The two rhyme — a fact typed into prose that no mechanism reconciles — but they are different surfaces with different remedies. `ef3f9e0a2` was right to decline closing #768, and its commit body says so explicitly. #768 remains open at its real scope with four candidate remedies and none selected. Do not read a prior handoff's citation of a GHI as evidence of that GHI's scope; read the GHI.

**The new step found a defect on its first use, which is the only available evidence it does anything.** Enumerating the family for GHI #771's own close comment — the thing step 7b now demands — surfaced that step 7d instructed agents to cite ARB receipt IDs and never to resolve them. Same shape as arms A and B, same file, previously unnoticed. Fixed in `deb6d7f6b` rather than deferred.

**The `ghi-close` fix has NO mechanical witness, and this was stated in the close comment rather than implied.** GHI #765 could resolve a tier-1 claim against an ARB receipt because a receipt existed to resolve. A close comment has no such artifact; a validator would need a machine-readable close-comment schema that does not exist and is not proposed. The honest status is that this raises the floor on what a diligent agent writes and lowers nothing for a careless one. It is a weaker result than the doctrine-declared-without-mechanism family generally wants, and it should not be counted as a mechanized closure.

**Campaign sequence was not worked and that is now three consecutive sessions.** Movement A item 2 is `ADR-0.35.0-canon-entry-corpus-landing`, `Pending` at 0/10. This session and the two before it worked Movement B/C defect repair. The Magna Carta ruling is that the campaign governs pull order while handoffs and triage advise — so a fourth session of defect repair should be an explicit operator ruling, not a default.

**The two-commit sync shape held and is visible in the log.** `4344ad69b` and `deb6d7f6b` carry source under `fix(` subjects; `e26467c0f` carries only `.gzkit` state under the ceremony subject. The sweep-guard predicate was checked before `--apply` and returned empty. A single `chore:` commit carrying both is the GHI #708 defect returning.

## Decisions Made

- [operator-ruled] Work D2 first, then D1 (verbatim: "D2 first, then D1"). Booked via `gz handoff decide` against the anchor; D3, D4 and D5 recorded set-aside.
- [operator-ruled] Take the converged `ghi-close` reading of D2 rather than the campaign-box or GHI #768 readings (selected from a four-option picker after the agent reported that D2's handoff arm had already landed in `ef3f9e0a2`). Both remaining arms land on one file, so "D2 first, then D1" was executed as a single pass.
- [operator-ruled] Author this handoff (verbatim: "write the handoff").
- [agent-chose] Corrected the session's own earlier framing rather than building on it. The agent presented the GHI #573 stale citation as a fresh finding and ranked D2 above D1 partly on that basis; `ef3f9e0a2` had already found and fixed it. The correction was stated plainly because it changed what work remained.
- [agent-chose] Filed one GHI with two arms rather than two GHIs. `ghi-author` forbids bundling because it "couples two routing decisions into one" — here both arms resolve to the same routing decision on the same file, so the anti-bundling rationale does not fire. The class statement covers both: any claim restated without re-derivation at this close.
- [agent-chose] Rewrote D1's remedy rather than implementing it as stated. Naming covering tests would have passed the very comment that motivated D1. Step 7b now requires the family enumerated and each cause bound to the test exercising that cause, and step 8 collects it as a table because prose cannot show a missing row.
- [agent-chose] Fixed step 7d (ARB receipt IDs cited without resolution) in the same session rather than filing it. It is the third member of the family GHI #771 named, in the file already being edited — `AGENTS.md` § DO IT RIGHT #1.
- [agent-chose] Corrected the `steps 7a-7e` Red Flag to `7a-7f` in the commit that added step 7f. The range is a coupled surface (DO IT RIGHT 1a); leaving it would have orphaned the new step from the tripwire that enforces step ordering.
- [agent-chose] Posted the sibling-cut cross-link on GHI #765 at authoring time rather than as follow-up, per `ghi-author` Step 0. The cross-link names where the two diverge as well as where they agree: #765 had an ARB receipt to resolve against, #771 has no artifact, so it can borrow the principle but not the mechanism.
- [agent-chose] Left the anchor's stale `#573` citation in place rather than editing the historical document. A handoff is a record of what was believed when written; correcting it retroactively would falsify the archive, which is the trap GHI #768's own body warns about.

## Immediate Next Steps

1. **Rule on campaign sequence before pulling more defect repair.** Movement A item 2 — `ADR-0.35.0-canon-entry-corpus-landing`, `Pending` 0/10, all ten briefs `draft` — is the campaign's topmost open item, and three consecutive sessions have worked Movement B/C instead. Magna Carta gives the campaign the pull order and makes handoffs advisory. A fourth defect-repair session is a legitimate choice but should be an operator ruling, not a default. **Route:** operator decision, then either `gz context ADR-0.35.0` or the chosen defect.

2. **Give GHI #768 a remedy at its real scope.** Transcribed `N/M` OBPI counts across 135 files under `docs/`. Four candidate remedies are in the filed body and none is selected: marked-syntax validator, generated block, commit-time coupling, or accept-and-disclaim. The body argues option 4 deserves a real hearing — the cheapest fix may be to stop writing the number down. Its own warning binds any remedy: a blanket sweep would falsify dated amendment records that are correct as history. **Route:** operator rules a remedy, then direct fix under #768.

3. **Re-run `failure-class-index` against a `--state all` snapshot.** Set aside this session. `src/gzkit/insights/failure_classes.py` is snapshot-driven with no internal state filter, so this is an input change and not a code change — feed it `gh issue list --state all`. It unblocks the campaign's Movement C box, whose five named members are all closed exemplars, which is why an earlier advised step naming them was unexecutable. **Route:** chore run.

4. **Scan for fail-closed refusals with no manpage coverage.** Set aside this session. Five modules under `src/gzkit/commands/` emit `blockers.append`: `sync.py`, `status_render.py`, `chores_exec.py`, `common.py`, `chores.py`. Cross-check each blocker site against its manpage, then decide whether `gz cli audit` should carry the check. Do not pre-commit to a validator scope before the scan says whether the gap is systemic or a single miss. **Route:** scan, then decide.

5. **Decide whether campaign-box GHI citations need a mechanism.** The third reading of the anchor's D2, still unaddressed. Handoff authoring is covered by `ef3f9e0a2` and close comments by `4344ad69b`; campaign documents under `docs/governance/` have no resolver and no owner. This may be genuinely cheap — the `ReferenceChecker` port already exists — or it may belong with GHI #768 as one "transcribed facts in governance prose" remedy rather than two. **Route:** decide scope first; it is plausibly a duplicate of item 2.

## Pending Work / Open Loops

1. **The GHI #771 [settled] remedy has no mechanical witness and must not be counted as a mechanized closure.** A closing agent that skips step 7b produces a close comment nothing rejects. This is stated in the close comment as a residual; it is recorded here so a future doctrine-declared-without-mechanism sweep does not read #771 [settled] as a member it has already closed.

2. **GHI #768 is open at a scope no prior handoff described correctly.** Its class is transcribed OBPI counts, not GHI-reference liveness. Two handoffs have now attached reference-liveness scope to it.

3. **GHI #769, #767, #766, #765 remain open.** #766 is blocked by #767; both are parked behind `ADR-pool.primary-source-corroboration` promotion by a prior session ruling. #765 carries a fix commit (`cd4e14687`) while remaining open — worth checking whether that is deliberate tracker discipline or a forgot-to-close, since it is exactly the shape GHI #714 [settled] named.

4. **GHI #581 remains open at TRACK ONLY**, with a ruling now several instances older than the evidence that produced it.

5. **`ADR-0.35.0` is `Pending` at 0/10, all ten briefs `draft`.** Briefs 04 through 10 have still not been reconciled against the tree; only 01 through 03 were, and `gz obpi brief-drift` cannot see pre-landed work.

6. **`ADR-0.35.0` pre-mortem number 1 (the ratchet becomes a ceiling) remains unmitigated by the ADR's own admission.** Cadence, owner, and scheduled floor-raise are undecided and must be resolved before OBPI-04.

7. **The dispatch residual is untouched, carried from two sessions back.** `gz-adr-audit` and `gz-adr-closeout-ceremony` carry the same Persona Dispatch mandate with no channel; they emit no artifact in the shape the scorecard does, so hanging one on them is a design question rather than a mechanical extension.

8. **AGENTS.md instructions-file budget work stays parked by standing operator ruling.** `gz check` reports it 33153 chars as an advisory; exit code is unaffected.

9. **The session-exit bookmark rode into `4344ad69b` rather than the ceremony commit.** It was already staged when the session opened and needed committing regardless, but it is not part of the `ghi-close` fix. History was left alone rather than rewritten. Noted so the commit's file count is not read as scope creep.

## Verification Checklist

- Never pipe a verifier. Capture to a file and read the bare status: `<cmd> > out.log 2>&1; echo "REAL EXIT: $?"`. The `verifier-pipe-gate` PreToolUse hook refuses a verifier in any non-final pipeline stage, and PIPESTATUS reads back empty under zsh.
- Confirm the new steps shipped to the wheel-bound mirror, not merely to the canonical file: `grep -n "enumerate the family, then bind each member" src/gzkit/skills/ghi-close/SKILL.md` expects a hit at step 7b. Repeat for `"resolve, don't transcribe"` (7d), `"Reference-liveness check"` (7f), and `"Cause in the family"` (the step 8 table).
- Confirm the step-range Red Flag was corrected with the step that created it: `grep -n "steps 7a" src/gzkit/skills/ghi-close/SKILL.md` expects `7a-7f`, never `7a-7e`.
- Confirm the quality gate: `uv run gz check` expects exit 0. Two advisories are expected and are not regressions — 692 unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning (parked by standing operator ruling).
- Confirm the sweep guard before any `--apply` on a dirty tree, never after: `uv run python -c "from pathlib import Path; from gzkit.commands.sync import _sweep_governed_paths; print(_sweep_governed_paths(Path('.')))"`. A non-empty result means `gz git-sync --apply` will refuse and stage nothing.
- Confirm the two-commit shape held: `git log --oneline -4` expects two `fix(ghi-close):` commits carrying source and a separate `chore:` ceremony commit carrying only `.gzkit` state.
- Confirm the branch: `git rev-list --left-right --count origin/main...HEAD` expects `0	0`.
- Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."
- Measure commit types by subject, never by `--grep`: `git log --since='90 days ago' --format='%s'` then filter. `--grep='^chore'` matches commit bodies and inflates the count.

## Evidence / Artifacts

- `.gzkit/skills/ghi-close/SKILL.md` — canonical surface; step 7b (family enumeration plus per-cause binding), step 7d (receipt IDs resolved on disk), step 7f (reference liveness, new), step 8 template (cause-to-test table plus Related resolution note), two Common Rationalizations rows, two Red Flags, `7a-7e` corrected to `7a-7f`. `skill-version` 2.6.0 to 2.7.0; `last_reviewed` 2026-08-07.
- `src/gzkit/skills/ghi-close/SKILL.md` — the wheel-bound mirror, regenerated by `gz agent sync control-surfaces`. Verification greps target this file rather than the canonical one, because it is what ships.
- `src/gzkit/handoff_api.py` — read, not modified. `ReferenceChecker` at line 168 and `_annotate_settled_citations` are the handoff-side precedent `ef3f9e0a2` landed; named here because GHI #771 arm A is the same defect on the surface that port does not reach.
- `.gzkit/insights/agent-insights.jsonl` — a `discovery` under scope `ghi-close-claim-derivation` recording that an advised remedy can be wrong while sounding right, with the next action to test any remedy against its motivating instance before implementing.
- `.gzkit/handoffs/20260808T013508Z-sweep-guard-widened-and-defect-ledger.md` — the superseded anchor. Its D1 through D5 are dispositioned in this document; its stale `#573` citation was deliberately left in place.
- `.gzkit/handoffs/20260808T020817Z-session-exit-bookmark.md` — the superseded mechanical bookmark, committed in `4344ad69b`.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — read, not modified. Movement A item 2 is the sequence position advised step 1 names.
- Commits: `4344ad69b` (arms A and B), `deb6d7f6b` (the third family member found by the new step), `e26467c0f` (ceremony sync carrying only `.gzkit` state).
- GHI #771 filed and closed this session; sibling-cut cross-link posted on GHI #765 at authoring time.

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
