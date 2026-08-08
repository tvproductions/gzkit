---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T08:44:51Z'
agent: claude-code
session_id: 838b144d-34be-4d4f-8728-7126249ae97b
continues_from: .gzkit/handoffs/20260808T024518Z-ghi-close-claim-derivation.md
---

## Current State Summary

Second work stretch of the same session. The operator ruled defect repair over campaign sequence, which answered the predecessor's advised step 1; D3 was pulled as the top item needing no further ruling, and it did not go the way it was scoped.

**D3's premise was wrong about its own tool.** The advised step held that the Movement C family had no identified open membership because the index had only been run over a closed-only snapshot. `resolve_chains` unions each entry's number with its citations, so a cited GHI is already a chain member whether or not the snapshot contains it — `#669`, `#581` and `#533` were in the 2026-08-07 closed-only report all along as bare numbers. Widening to `--state all` (766 records, up from 333) added no membership.

**What widening did surface was an artifact, and chasing it found a real defect.** Chain depth counted every member including citation targets that carry no `## Class of failure` section, so a two-member pair citing six April-2026 GHIs ranked second in the corpus above two chains holding five authored diagnoses each. Filed as GHI #772 and fixed in `1f4ee53da`: authored depth is now the ranking and cut currency, span keeps its old meaning, and the report's false "outside the indexed window" label — which had already propagated a wrong cause into this session's own guidance commit — now states only what the renderer can know.

**The corrected tool agrees with the campaign, which is the load-bearing outcome.** Before the fix the tool contradicted the Movement C box's claim about the deepest chains. After it, the top three are the `#537` chain at 9 authored and the box's own two named arms at 5 each. The campaign was not edited.

Three commits plus ceremony syncs, all pushed. `uv run gz check` exit 0; 8121 unit tests OK (was 8116). `origin/main` 0/0 and tree clean at authoring.

## Important Context

**The actionable answer to D3's real question is three chains the campaign never named.** The Movement C box is genuinely unexecutable as scoped — its family is fully closed, now confirmed by a tool measuring the right thing rather than by inspection. Open membership lives in three different families: `#669` (5 authored of 6, with `#607`, `#691`, `#727`, `#728`, `#740`), `#581` (4 of 4, with `#612`, `#619`, `#633`), and `#533` (3 of 3, with `#752`, `#753`). The `#669` chain is the strongest pull: its subject — no mechanical audit that every OBPI-status writer consults the terminal rule — is the same doctrine-declared-without-mechanism shape the box wants closed, just a different chain than the one it named.

**Fixing the tool rather than the campaign was a real fork, and the wrong branch was the easy one.** When a measurement contradicts prose, "the measurement changed, update the prose" is the available move. Here it would have written a counting artifact into doctrine. The discriminator was cheap and should be reused: check whether the new measurement is *substantively* better before treating it as authority. It was not — six of the artifact chain's eight members contributed no diagnosis at all.

**Chain depth was deliberately NOT redefined in place.** Making it mean authored count would have silently changed every figure already transcribed from a prior run, including the campaign's "~19 members", with no diff to show for it. That is GHI #768's exact failure mode, and committing it inside the fix for an adjacent defect would have been poor form. The authored count is additive, and a cited-only accessor exposes the difference.

**A fallback label that collapses two distinct states will propagate the wrong cause fast.** The report rendered any member missing from its title map as "outside the indexed window", but that map is built from entries carrying a class statement, not from snapshot membership. The stated cause applied to zero members. It was transcribed into the chore guidance in `84df74d2c` within one commit, before the check that disproved it, and corrected in `1f4ee53da`. Recorded as a `defect-resolution` insight: when a report renders a fallback, ask what distinct states collapse into it and state the observation rather than the cause.

**The amended `ghi-close` steps from the first stretch got their second and third exercise.** GHI #772's close comment was written through them — step 7f resolved eleven references before writing, step 7d confirmed the ARB receipt resolves on disk, and step 7b's enumeration was derived by grepping the module for every read of the two count-bearing attributes and checking each against the currency it should use. Five sites, all covered. That method is reusable for any single-module metric fix.

**One pre-existing test changed fixture, not contract.** The report-rendering test used a single GHI citing three statement-less ancestors, which rendered only because the cut read total span. It now forms a real three-member family and asserts the same four things. A test whose fixture depends on the defect under repair is a signal to re-derive the fixture, never to weaken the assertion.

## Decisions Made

- [operator-ruled] Continue defect repair rather than pulling the campaign's Movement A sequence position (verbatim: "continue defect repair", given twice). This answered the predecessor handoff's advised step 1, which had put the sequencing question first precisely because it governs the other four.
- [operator-ruled] Author this handoff and sync (verbatim: "create new handoff - git sync").
- [agent-chose] Pulled D3 as the top item needing no operator ruling. Advised step 2 (GHI #768) required a remedy ruled from four candidates and would have blocked; D3 required none.
- [agent-chose] Filed GHI #772 rather than fixing the measurement defect silently. It is a class-level runtime defect with a live consequence in a campaign-consumed report, and the trailer needed an anchor.
- [agent-chose] Added an authored-depth metric rather than redefining chain depth. Redefinition would have changed transcribed figures with no visible diff — GHI #768's shape, which this fix should not commit while closing an adjacent one.
- [agent-chose] Fixed the tool rather than amending the campaign box the tool contradicted. Verified first that the campaign's substantive claim was correct and the tool's new ranking was an artifact; had that gone the other way the campaign would have needed operator-ratified amendment, not a unilateral edit.
- [agent-chose] Corrected this session's own `84df74d2c` guidance commit in `1f4ee53da` rather than leaving the wrong cause in the chore doc. The `--state all` versus date-window distinction in that commit stands; only the explanation of why members render unindexed was wrong.
- [agent-chose] Re-derived a pre-existing test's fixture rather than relaxing its assertions when the corrected cut filtered its chain out.
- [agent-chose] Left the deepest-chain figure reporting span and added a deepest-authored figure alongside, rather than switching the field. Same reasoning as chain depth: a field consumers already read should not change meaning silently.

## Immediate Next Steps

1. **Pull the `#669` chain — the strongest open-membership family the corrected index surfaced.** Five authored diagnoses, one open member, and its subject (*no mechanical audit that every OBPI-status writer consults the terminal rule; convention-only*) is the doctrine-declared-without-mechanism shape Movement C wants closed. Its closed siblings `#607 [settled]`, `#691 [settled]`, `#727 [settled]`, `#728 [settled]`, `#740 [settled]` are the family evidence a fix should close against, not just the instance. **Route:** read the chain, then `/ghi-close 669` if the family is closable in one pass, else `/ghi-author` for the class and direct-fix each arm.

2. **Give GHI #768 a remedy at its real scope.** Transcribed `N/M` OBPI counts across 135 files under `docs/`. Four candidates in the filed body, none selected: marked-syntax validator, generated block, commit-time coupling, or accept-and-disclaim. The body argues option 4 deserves a real hearing. Its warning binds any remedy — a blanket sweep would falsify dated amendment records correct as history. This session twice avoided committing #768's shape by hand; a mechanism would make that not depend on vigilance. **Route:** operator rules a remedy, then direct fix.

3. **Consider whether the Movement C box should be re-scoped or checked off.** Its named family is fully closed and its completion criterion (*a declared discipline either carries a mechanical witness or is demoted to advisory in its own text*) is arguably met for those members. The corrected index says the live work is in three other chains. Amending a campaign box is operator-ratified, so this is a ruling, not a task. **Route:** operator decision, informed by the 2026-08-08 chore report under the chore's proofs directory.

4. **Scan for fail-closed refusals with no manpage coverage.** Set aside twice now. Five modules under `src/gzkit/commands/` emit blocker appends: `sync.py`, `status_render.py`, `chores_exec.py`, `common.py`, `chores.py`. Cross-check each blocker site against its manpage, then decide whether `gz cli audit` should carry the check. Do not pre-commit to a validator scope before the scan says whether the gap is systemic. **Route:** scan, then decide.

5. **Decide whether campaign-box GHI citations need their own mechanism.** Handoff authoring is covered by `ef3f9e0a2` and close comments by `4344ad69b`; campaign documents under `docs/governance/` have no resolver. Plausibly cheap since the reference-checker port exists, and plausibly a duplicate of item 2 rather than separate work. **Route:** decide scope first.

## Pending Work / Open Loops

1. **`ADR-0.35.0` is `Pending` at 0/10 and Movement A has now been deferred by explicit ruling, not by drift.** That is a better state than the predecessor's, but the deferral is not a decision to abandon the sequence. Briefs 04 through 10 remain unreconciled against the tree; only 01 through 03 were, and `gz obpi brief-drift` cannot see pre-landed work.

2. **`ADR-0.35.0` pre-mortem number 1 (the ratchet becomes a ceiling) remains unmitigated by the ADR's own admission.** Cadence, owner, and scheduled floor-raise are undecided and must be resolved before OBPI-04.

3. **The GHI #771 [settled] remedy still has no mechanical witness.** A closing agent that skips `ghi-close` step 7b produces a close comment nothing rejects. Recorded again here so a doctrine-declared-without-mechanism sweep does not read #771 [settled] as a member it already closed — it is a floor raise, not a mechanism.

4. **GHI #769, #767, #766, #765 remain open.** #766 is blocked by #767; both are parked behind `ADR-pool.primary-source-corroboration` promotion by a prior session ruling. #765 carries a fix commit while remaining open, which is the shape GHI #714 [settled] named — worth determining whether that is deliberate tracker discipline or a forgot-to-close.

5. **GHI #581 remains open at TRACK ONLY** and is now also a member of one of the three open-membership chains, which is new information its standing ruling predates.

6. **The dispatch residual is untouched, carried from three sessions back.** `gz-adr-audit` and `gz-adr-closeout-ceremony` carry the same Persona Dispatch mandate with no channel; they emit no artifact in the shape the scorecard does, so hanging one on them is a design question rather than a mechanical extension.

7. **AGENTS.md instructions-file budget work stays parked by standing operator ruling.** `gz check` reports it as an advisory; exit code is unaffected.

8. **The 2026-08-07 chore proof was overwritten in place by the 2026-08-08 run before the metric fix, then again after it.** Only the corrected report survives on disk under the 2026-08-08 stamp. The pre-fix figures are recoverable from `84df74d2c` and from GHI #772 [settled]'s body, but not from the proofs directory. A future run wanting a before/after pair should pass distinct stamp values.

## Verification Checklist

- Never pipe a verifier. Capture to a file and read the bare status: `<cmd> > out.log 2>&1; echo "REAL EXIT: $?"`. The `verifier-pipe-gate` PreToolUse hook refuses a verifier in any non-final pipeline stage, and PIPESTATUS reads back empty under zsh.
- Confirm the metric fix: `uv run -m unittest tests.chores.test_failure_class_index` expects exit 0, 25 tests. The ordering test is the assertion that closed GHI #772; the total-span test is the negative control proving chain depth was not silently redefined.
- Confirm the report no longer asserts an unknowable cause: `grep -c "outside the indexed window" .gzkit/chores/failure-class-index/proofs/failure-class-index-2026-08-08.md` expects 0.
- Re-run the chore end-to-end by taking a fresh snapshot outside the repo, then `uv run python -m gzkit.insights.failure_classes --snapshot "$SNAPSHOT" --dry-run`. Expect roughly 12 chains with at least 3 authored diagnoses and a headline naming both authored depth and span.
- Confirm the quality gate: `uv run gz check` expects exit 0. Two advisories are expected and are not regressions — 692 unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning (parked by standing operator ruling).
- Confirm the full suite: `uv run gz arb step --name unittest -- uv run -m unittest -q` expects 8121 tests, exit 0.
- Confirm the sweep guard before any `--apply` on a dirty tree, never after: `uv run python -c "from pathlib import Path; from gzkit.commands.sync import _sweep_governed_paths; print(_sweep_governed_paths(Path('.')))"`. A non-empty result means `gz git-sync --apply` will refuse and stage nothing.
- Confirm the branch: `git rev-list --left-right --count origin/main...HEAD` expects `0	0`.
- Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `src/gzkit/insights/failure_classes.py` — the authored-members field with its authored-depth and cited-only accessors; chain resolution populates and sorts on it; the summary gains deepest-authored and cited-only totals and counts attention-worthy chains on authored depth; the report filters and headlines on authored depth and states no cause it cannot know; the CLI prints the same metric so run log and report cannot disagree.
- `tests/chores/test_failure_class_index.py` — 25 tests, up from 20. New class covering authored depth (4 tests) plus a report-label test. The report-rendering test changed fixture, not contract.
- `.gzkit/chores/failure-class-index/CHORE.md` — snapshot-step guidance corrected twice: the widening explanation in `84df74d2c` and its wrong causal claim in `1f4ee53da`. Now carries a snippet for determining whether an unindexed member is absent from the snapshot or merely carries no class section.
- `.gzkit/chores/failure-class-index/proofs/failure-class-index-2026-08-08.md` — the corrected archival run: 12 chains with at least 3 authored diagnoses, 26 cited-only members, top three being the `#537` chain and the campaign's two named arms.
- `.gzkit/chores/failure-class-index/proofs/run-2026-08-08.json` — run telemetry for the same.
- `.gzkit/skills/ghi-close/SKILL.md` — steps 7b, 7d and 7f from the first stretch of this session; used to write GHI #772's close comment, their second exercise.
- `.gzkit/insights/agent-insights.jsonl` — a `defect-resolution` under scope `failure-class-index-metric` on fallback labels that collapse distinct states, alongside the first stretch's `discovery` under `ghi-close-claim-derivation`.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — read, not modified. Its Movement C claim was verified correct against the corrected index and deliberately left alone.
- Commits: `84df74d2c` (chore run and widening guidance, partly self-corrected), `1f4ee53da` (the metric fix), and the ceremony syncs that carried only `.gzkit` state.
- GHI #772 filed and closed this session. ARB receipt for the suite: arb-step-unittest-9bb2a00eba68460094368f5f2c84764e, confirmed to resolve on disk before citation.

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
