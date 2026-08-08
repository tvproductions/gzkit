---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T20:41:23Z'
agent: claude-code
continues_from: 20260808T190443Z-movement-c-skill-arm-closed-and-postures-accepted.md
---

## Current State Summary

Worked advised step 1 (the ADR-0.44.0 disposition) to completion. It took three defect fixes to get there, because the ceremony was blocked twice before executing and broke once during. Three commits, `gz check` 51/51 exit 0, three GHIs filed and closed.

**ADR-0.44.0 returned to pool** as `ADR-pool.vendor-alignment-codex`. Operator ruled it *an agent overreach* and gave three arms — become 0.36.0, revert to pool, or delete the implemented code. Pool, because the overreach was the NUMBERING not the work: the implemented Codex surface is real, in use, and stays; only the unsanctioned REQ/OBPI structure retires. Renumbering would have re-asserted it as sanctioned in-sequence feature work, and no governed renumber path exists anyway.

**Three misalignments, one root.** Each was something true at write-time that nothing ever re-verified.

- **#774** — park is a two-sided protocol and one side had NEVER fired: 371 `obpi_parked`, **0** `obpi_unparked`. It survived because park is one of the dispositions the orphan census excludes, so parking an orphan *silences* it.
- **#775** — no collision policy could return an ADR that had been *worked*; this one had diverged from its retained intake by 139 insertions / 140 deletions.
- **#773's own third arm** — 36 `@covers` decorators named REQs in briefs the demotion deletes, and `@covers` validates at IMPORT, so the suite stopped loading.

Branch 0/0 and tree clean at authoring.

## Important Context

**The same root under all three: a fact recorded once and never re-verified.** Park state, collision policy, and `@covers` targets were each correct when written and silently wrong later. This is the family the operator named — *'we are plagued by misalignments like this'* — and the durable fixes are all couplings, not cleanups.

**A disposition that silences a census must be re-checked, or it becomes permanent.** Park suppresses the orphan census; the GHI #584 backfill used that to quiet 233 orphans without checking whether each parent was still in pool. Nothing then noticed, because the census that would have noticed is the one park turns off.

**I got the #774 predicate wrong twice, and only RUNNING it caught both.** Testing parked OBPIs against every ADR id on disk flagged all 371 — every ordinary park points at a pool ADR that of course exists. Resolving the parent through `rename_chain_target` flagged **zero of the ones that mattered**: a demote/promote round trip is a rename CYCLE, and that function seeds `seen={current}` and halts when the next hop is already seen, so it resolves such an ADR to its pool id while the file sits in `pre-release/`. Round-tripped ADRs are precisely the population the check exists to find. Layer-1 brief placement needs no inference and is exactly the set `demote` deletes.

**`rename_chain_target` has a live weakness worth knowing.** It resolves `A -> B -> A` to B. Correct-ish for a graph with no terminal node, wrong for the question *"where is this ADR now"*. Any future consumer asking that question must not use it.

**A dry-run that reports files and events can still hide the blast radius.** The demote dry-run named every file it would delete and every park event it would write, and said nothing about the 36 `@covers` decorators pointing into those files. The suite failing to import was the first signal.

**I implemented an H1 retitle and BACKED IT OUT.** `test_sunset_migrate.py::test_pool_file_retains_adr_body_verbatim` asserts the ADR body survives demotion byte-for-byte, and the H1 sits inside that body. A tested preservation guarantee outranks a cosmetic id match. The pool file's H1 therefore still names the old feature id — deliberate, recorded in the test docstring and on #775 so it is not re-tried blind.

**`gz adr demote` deletes briefs and pool ADRs carry no OBPIs by doctrine**, so a completed OBPI's brief has nowhere to go. That is not a bug in demote — completion is a disposition the orphan census accepts — but it means demoting any ADR with attested work costs its REQ traceability. Know the price before ruling.

**Watch the count fence when writing campaign prose.** Transcribing '1/6 OBPIs' into the campaign line tripped `--transcribed-adr-counts` immediately. Cite `uv run gz adr status <ID>` instead of the number.

## Decisions Made

- [operator-ruled] ADR-0.44.0 is an agent overreach with three acceptable dispositions (verbatim: "this was originally an agent overeach. this either becomes 0.36.0, revert to pool, or we just ignore/deleted the implemented code - I won't be paralyzed in purgatory."; spelling preserved). The closing clause is a standing instruction against stalling on this class of decision.
- [operator-ruled] File GHIs and fix them (verbatim: "ghis and fix - we are plagued by misalignments like this."). The second clause set the bar at class-level couplings rather than instance patches.
- [operator-ruled] Do not resequence out of order (verbatim: "we DO NOT go out of sequence (0.44.0)"), which foreclosed finishing the ADR in place.
- [agent-chose] Pool over 0.36.0 over deletion. The overreach was the numbering, not the work; renumbering would re-assert it as sanctioned in-sequence feature work, deletion would destroy a working Codex surface, and no governed renumber path exists — `gz migrate-semver` is a bare-id to slugged-id backfill recorder and `gz adr promote --semver` needs a pool source, with demote-then-promote destroying briefs either way.
- [agent-chose] Grounded the #774 witness in Layer-1 brief placement after two wrong predicates, each disproved by running it against the live corpus rather than by reasoning.
- [agent-chose] Folded park coherence into the existing `--obpi-lifecycle-coherence` scope instead of adding `--park-coherence`. One subject, one gate; a second scope would have been the accretion Movement C is reducing.
- [agent-chose] Backed out the H1 retitle rather than override a tested byte-for-byte guarantee, and recorded the conflict in the test docstring instead of resolving it unilaterally.
- [agent-chose] Stripped the 36 `@covers` decorators BEFORE demoting, so the new guard would not need `--force` on its first real use.
- [agent-chose] Added the `@covers` guard with a `--force` escape rather than an absolute refusal — discarding REQ traceability stays possible, but only deliberately.
- [agent-chose] Corrected GHI #773's Remedy section by comment rather than by editing the body, so the wrong-then-corrected sequence stays auditable.
- [agent-chose] Reverted the first demotion entirely (all 14 paths were uncommitted) rather than recording a demote/promote round trip that never should have happened.
- [agent-chose] Retargeted OBPI-0.35.0-09's 14 references to the pool id and to checklist items, since pool ADRs carry no OBPIs so the OBPI-level ids no longer exist.

## Immediate Next Steps

1. **Rule whether the demoted pool file's H1 should match its id.** It still reads `# ADR-0.44.0-vendor-alignment-codex:` while `id:` says `ADR-pool.vendor-alignment-codex`. Retitling was built and backed out because `test_pool_file_retains_adr_body_verbatim` asserts the body survives byte-for-byte. Two defensible invariants disagree and only an operator can pick. **Route:** operator ruling; if the H1 wins, the byte-for-byte test needs narrowing to exclude the title line.

2. **Decide whether `rename_chain_target` should answer "where is this artifact now".** It resolves an `A -> B -> A` round trip to B, which is wrong for that question and right for nothing else obvious. Its consumers include the orphan census. Nothing is known to be broken by it today — this session routed around it — but the next consumer to ask the location question will get a wrong answer silently. **Route:** operator rules whether to audit its consumers, then direct fix.

3. **Widen the ruff-reachability check beyond ruff.** Carried unchanged from the predecessor and still the highest-yield known lead: the class is *any* Mechanical scorecard row citing an enforcement surface — validator scope flags, pre-commit hook ids, test module paths. Each is mechanically resolvable; the ruff arm found a fifth false row on its first run. **Route:** operator rules the scope, then direct fix.

4. **Sweep the 17 grandfathered rules for false Mechanical rows.** Also carried. Five false rows have now been found by hand across two sessions, and the new check covers only ruff citations. **Route:** operator rules scope; editing any grandfathered rule forces a full clause re-score.

5. **Triage the 11 open GHIs.** Untouched for several sessions and several are old. A sweep would say which are stale rather than deferred. **Route:** `/ghi-triage`, then operator rules the pull order.

## Pending Work / Open Loops

1. **The pool file's H1 names the old feature id.** Deliberate, not drift — see advised step 1. Recorded in the test docstring and on GHI #775 [settled] so a future author does not re-try the retitle blind.

2. **REQ-to-test traceability was discarded for OBPI-0.44.0-01**, an OBPI that was attested complete at Gate 5. The 36 tests still run and still assert the Codex behaviour; only the `@covers` decorators went. This was the deliberate price of retiring an overreached structure, not an oversight.

3. **`rename_chain_target` resolves a round trip to the wrong end.** No known live breakage; see advised step 2.

4. **`gz adr demote` on any ADR with attested-complete OBPIs costs their REQ traceability**, because pool ADRs carry no OBPIs by doctrine and the briefs are deleted. The new `@covers` guard surfaces it rather than preventing it. Know the price before ruling a demotion.

5. **The 8 non-canonical unittest ARB receipts remain, permanently and correctly flagged**, accepted last session. Reclassify only if the count GROWS.

6. **PLC0415 stands at 138 measured violations, accepted.** S603 stands at 35 and is deliberately unselected.

7. **17 rules remain grandfathered against a baseline of 23.**

8. **The AGENTS.md instructions-file budget advisory stands at 385 B over the codex delivery cap**, parked by standing operator ruling.

9. **ADR-0.35.0 is the sole in-flight feature, `Pending` with nothing landed.** Movement A stays deferred by explicit ruling, not drift. Its OBPI-09 now points at the pooled Codex ADR.

10. **GHI #719, #769, #767, #766, #765, #533, #747, #611, #594, #579, #567 remain open.** Verified live; none touched this session.

## Verification Checklist

Never pipe a verifier — the `verifier-pipe-gate` hook judges the pipeline, not the filter identity. Capture to a file and read the bare status.

Confirm the whole gate: `uv run gz check` expects exit 0, 51/51. Two advisories are expected and are NOT regressions — 692 unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning at 385 B (parked by standing operator ruling).

Confirm park coherence, the load-bearing new witness: `uv run gz validate --obpi-lifecycle-coherence` expects exit 0, and `uv run python -m gzkit.governance.obpi_park_backfill --release` expects "No OBPIs parked under a live ADR — park state is coherent." The repository now carries 6 `obpi_unparked` events; before this session it carried zero, so `grep -c '"event":"obpi_unparked"' .gzkit/ledger.jsonl` returning 0 would mean the repair was lost.

Confirm the witness discriminates rather than merely passing: `uv run -m unittest tests.governance.test_park_coherence` expects exit 0, 6 tests. `test_a_round_tripped_parent_is_still_found` is the load-bearing one — it pins the case a rename-chain implementation silently reported as clean.

Confirm the demote guards: `uv run -m unittest tests.commands.test_adr_demote` expects exit 0, 19 tests. `test_keep_pool_still_preserves_the_intake` matters as much as the new policy's own test — it is what stops `take-demoted` being smuggled in by redefining `keep-pool`.

Confirm the ADR actually moved: `uv run gz adr status ADR-pool.vendor-alignment-codex` resolves, `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/` does not exist, and `uv run gz validate --adr-status-fresh` expects exit 0.

Confirm no dangling references: `uv run gz validate --documents` expects exit 0. OBPI-0.35.0-09 carried 14 references to the demoted ADR and its OBPIs; pool ids resolve, OBPI-level ids do not.

Confirm the branch with two-dot ranges: `git rev-list --count origin/main..HEAD` expects 0 and `git rev-list --count HEAD..origin/main` expects 0. The three-dot symmetric form is rejected by the handoff authoring gate as an unfilled-scaffold marker.

Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."

## Evidence / Artifacts

- `src/gzkit/obpi_lifecycle.py` — `park_coherence_violations`, grounded in Layer-1 brief placement with both rejected predicates recorded in the docstring.
- `src/gzkit/governance/trust_audits/taxonomy.py` — `non_pool_brief_owners`, and the park arm folded into `audit_obpi_lifecycle_coherence`.
- `src/gzkit/governance/obpi_park_backfill.py` — the reversed-demotion guard on `plan_backfill`, plus `plan_release` / `apply_release` / `--release` / `--apply-release`.
- `tests/governance/test_park_coherence.py` — 6 tests; the round-trip case pins what a rename-chain implementation would have hidden.
- `src/gzkit/commands/adr_demote.py` — `take-demoted` collision policy, `_live_covers_into_deleted_briefs` guard, `promoted_from` stripped, and the widened `fail` message naming both alternatives.
- `tests/commands/test_adr_demote.py` — 19 tests; `CollisionWithRetainedIntake` carries the three collision poles, the covers guard, its `--force` escape, and the backed-out-retitle record.
- `src/gzkit/cli/parser_artifacts.py` and `docs/user/manpages/adr-demote.md` — the third policy, documented with the round-trip guidance.
- `docs/design/adr/pool/ADR-pool.vendor-alignment-codex.md` — the demoted ADR carrying its evolved content, not its 2026-03 intake.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-09-codex-playback-wiring.md` — 14 references retargeted.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — Housekeeping records the ruling verbatim, all three defects, and the stated residual.
- `tests/test_codex_config_surface.py`, `tests/test_validate_sync_parity.py`, `tests/test_sync.py`, `tests/commands/test_init.py` — 36 `@covers` decorators removed.
- Commits: a98c482f7 (park release side, take-demoted), f066126a2 (the disposition, covers guard, promoted_from), plus sync.
- ARB receipts, each confirmed to resolve on disk before citation: arb-ruff-8e8250f02f7648ff8841a81c2f1d6b0f, arb-step-typecheck-ee7be883fe404732adb13d3a2db68656, arb-step-unittest-3fb23b63d02949b798e90895e90f1a54 (8206 tests).

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
