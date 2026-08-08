---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T00:50:49Z'
agent: claude-code
continues_from: 20260807T235705Z-movement-c-ratification-and-failure-class-index.md
---

## Current State Summary

Session opened on a handoff review and closed two Movement C items. Sequence: reviewed the resumed handoff and found its advised step 2 STALE on the day it was authored (GHI #744 had closed `COMPLETED` 2026-08-02 at `0f671b31c`, six days earlier — the handoff read the campaign's `(GHI #744)` parenthetical citation as unlanded scope); the operator overrode the agent's recommendation to skip ahead and ruled "Determine C2 status first"; that determination found a live residual and closed it (`57bd15f91`); then GHI #770 was worked end-to-end through `/ghi-close` and closed `fixed` (`ae7ffffc6`).

Two commits, both pushed, `origin/main` even at authoring. `uv run gz check` exit 0; 8104 unit tests OK.

**C2 (`Collapse the validate() surface to the registry`) is checked off.** Its criterion had three sub-claims; two already held, and the third had not held since the #618 collapse: `VALIDATOR_REGISTRY`'s header called itself *"Single source of validate dispatch"* while `--qc-binding`, `--fidelity-presence` and `--waiver-ratchet` reached `gz check` without appearing in it. Registering them retired a third hand-maintained scope->audit map (`_early_return_scope_audit`, added under GHI #630 to patch that same gap) — **net -18 source lines**.

**GHI #770 closed both arms of its stated minimum honest fix.** `run_dispatch_attestation_audit` -> `run_dispatch_absorption_marker_audit` (QC step `dispatch-attestation` -> `dispatch-absorption-marker`), and a new `gzkit.adr_eval_dispatch` channel makes an undispatched evaluation say so in the scorecard instead of being byte-identical to a dispatched one.

## Important Context

**A campaign citation is not a work item, and nothing couples the two.** The resumed handoff turned `(GHI #744)` — a parenthetical citing the criterion the 2026-08-07 amendment adopted — into advised step 2, "land the enrollment fail-close". It had landed six days before. This is GHI #768's exact shape (*transcribed counts couple to nothing*) applied to a citation rather than a count, and #768 is still open with no remedy selected. Verify a campaign box's criterion against source before pulling its next item.

**The GHI #624 substance channel is the template for any "declared but unattested" gap.** `src/gzkit/adr_eval_substance.py` grades ONLY from a recorded judge verdict and reports `UNGRADED` absent one. It ships reading `adr_substance_verdict` — an event with **zero occurrences in the ledger and no typed entry in `src/gzkit/events.py`** — so it truthfully reports UNGRADED on every scorecard and will populate without a renderer change once a producer exists. `src/gzkit/adr_eval_dispatch.py` was built by mirroring it exactly. When the next member of the doctrine-declared-without-mechanism family needs closing, read that module first rather than designing something new.

**`gz git-sync` authors `chore: update ...` subjects, which hides source fixes from the routing protocol's own precedent query.** The C2 fix landed that way at `57bd15f91`; `git log --grep='^fix('` cannot see it. That query is what AGENTS.md § Defect-fix routing prescribes for its precedent check AND the source of Movement B's "470 fix commits in 90 days" figure, so the figure undercounts by an unknown amount. Recorded as a `discovery` insight under scope `git-sync-commit-shape`; no remedy chosen.

**The golden-set fences in `tests/cli/test_validate_registry_parity.py` have an honest-hatch doctrine — use it, do not edit the goldens.** `_POST_SNAPSHOT_EXPLICIT_ADDITIONS` exists (GHI #741) so the pre-collapse snapshot stays measured evidence. The `_other_scopes_active` exclusion set had no such hatch; one was added this session on the same pattern rather than appending to the golden.

**Registering a solo-lifecycle scope does NOT re-route its flag.** `_dispatch_early_return_scopes` runs first and returns True, short-circuiting the aggregate path — which is why `sensitivity`, `unscoped_rules` and `evaluation_justify_binding` were already both registered and solo. `in_other_scopes=False` is what preserves solo-ness under the GHI #704 combined-scope refusal.

## Decisions Made

- [operator-ruled] Determine C2's status before pulling the next work item (verbatim: "Determine C2 status first"). This overrode the agent's recommendation to set advised step 2 aside and go straight to GHI #770; the determination is what found the second-dispatch-path residual. Booked via `gz handoff decide`, with advised steps 2, 3, 4 and 5 recorded set-aside.
- [operator-ruled] Close the C2 residual immediately rather than filing it or amending around it (verbatim: "Close the residual now (Recommended)").
- [operator-ruled] Check C2 off, amend the campaign with the determination, and sync (verbatim: "Check C2 + sync").
- [operator-ruled] Work GHI #770 (verbatim: "do 770").
- [agent-chose] Registered the three scopes in `VALIDATOR_REGISTRY` rather than moving their dispatch. Their solo 0/2/3 lifecycle, exit codes and custom prose are unchanged; only the registry's self-description became true. Moving dispatch would have been a CLI-contract change (exit 3 -> 1, different rendering) and therefore not a direct fix.
- [agent-chose] Retired `_early_return_scope_audit` in the same commit rather than leaving it dead. Coupled-surface coherence (Invariant 1a) — it existed only because the registry could not resolve those scopes, and it was a third copy of knowledge the registry now holds.
- [agent-chose] Strengthened `test_second_dispatch_path_scopes_are_accounted` into `test_the_registry_is_the_single_source_of_validate_dispatch` instead of deleting it. Left as-is it would have passed trivially on an empty set — the GHI #730 tautology shape.
- [agent-chose] Mirrored the substance channel for the dispatch channel rather than designing a new mechanism, and deliberately shipped it reading an event nothing emits. The substance channel is the attested precedent for exactly those terms.
- [agent-chose] Treated partial dispatch as SINGLE-DRIVER. The three personas score different dimension families, so crediting one would launder the two that never ran.
- [agent-chose] Extracted `_render_dispatch_section` when the pre-commit xenon gate flagged `render_scorecard_markdown` at rank D, rather than waiving the gate (AGENTS.md § Never #6).
- [agent-chose] Did NOT extend the dispatch channel to `gz-adr-audit` or `gz-adr-closeout-ceremony`. Named as residual in the #770 close comment instead — see § Pending Work item 1.
- [agent-chose] Committed the #770 fix with a `fix(...)` subject and `Task:` trailer BEFORE invoking git-sync, applying the discovery recorded earlier in the same session rather than filing it and repeating the pattern.

## Immediate Next Steps

1. Draw the next cut of the Movement C family box — *close the doctrine-declared-without-mechanism family*. Named members still open: **#692** (checks section presence, not population) and **#693** (verifies a flag is mentioned, never that its description is true) on the validator side; **#459**, **#574**, **#620** on the agent side. GHI #770 is now the box's worked template: rename the overclaiming surface, then give the concern a channel that reports its own absence.
2. Decide the `gz-adr-audit` / `gz-adr-closeout-ceremony` dispatch residual (see § Pending Work item 1). It needs an emitted artifact per ceremony to hang a channel on; that is a design question, not a mechanical extension of `ae7ffffc6`.
3. Rule on GHI #768 (transcribed counts couple to nothing). It has now produced two observed instances in two sessions — the stale campaign count corrected this session, and the stale advised step that opened it. It is open with no remedy selected.
4. Decide whether `gz git-sync` should refuse to bundle `src/**` changes under a `chore:` subject, or whether source fixes must carry a `fix()` subject before sync is invoked. Recorded as a `discovery` insight this session; the Movement B "470 fix commits" figure depends on the answer.
5. Return to ADR-0.35.0 when the operator draws it — `Pending`, 0/10, all ten briefs `draft`. Briefs 04-10 have still NOT been reconciled against the tree; only 01-03 were, and `gz obpi brief-drift` cannot see pre-landed work.

## Pending Work / Open Loops

1. **Named residual, recorded in the close comment.** `gz-adr-audit` and `gz-adr-closeout-ceremony` carry the same `## Persona Dispatch` mandate and got no channel — their dispatches are still unattested and undisclosed. They don't emit an artifact in the shape the scorecard does, so hanging a channel on them is a different piece of work. I did not quietly extend to them and I did not quietly ignore them.

2. **The commit-shape discovery from earlier held up.** This one landed as `fix(quality): … (GHI #770)` with a `Task: TASK-dispatch-audit-naming-#770` trailer, committed before invoking git-sync — so `git log --grep='^fix('` can see it. That's the practice the earlier insight prescribed, applied immediately rather than filed and forgotten.

3. The receipt machinery that would CAUSE a persona dispatch to be recorded is unbuilt: `ADR-pool.obpi-pipeline-dispatch-attestation` Target Scopes #5/#6, unpromoted. Nothing emits `persona_dispatched`, so the new channel truthfully reports SINGLE-DRIVER on every scorecard until it lands.

4. GHI #768, #769, #765, #767, #766 are open with no remedy selected. #766 is blocked by #767; both are parked behind `ADR-pool.primary-source-corroboration` promotion by the prior session's ruling.

5. GHI #581 remains open at TRACK ONLY. It gained a third failure class last session and its ruling is now three instances older than the evidence that produced it.

6. The `failure-class-index` chore still indexes closed GHIs only. Open GHIs are unindexed; re-running with a `--state all` snapshot was set aside this session.

7. ADR-0.35.0's pre-mortem #1 (the ratchet becomes a ceiling) remains unmitigated by the ADR's own admission; cadence, owner, and scheduled floor-raise are UNDECIDED and must be resolved before OBPI-04.

8. AGENTS.md instructions-file budget work stays parked by standing operator ruling.

## Verification Checklist

- Never pipe a verifier. Capture to a file and read the bare status: `<cmd> > out.log 2>&1; echo "REAL EXIT: $?"`. The `verifier-pipe-gate` PreToolUse hook refuses a verifier in any non-final pipeline stage, and PIPESTATUS reads back empty under zsh.
- Confirm the quality gate: `uv run gz check` expects exit 0, with `Dispatch absorption marker` at step 47/49. Two advisories are expected: 692 unlinked specs (pre-existing) and unjustified code changes (this session's diff).
- Confirm the C2 fence: `uv run -m unittest tests.governance.test_check_scope_parity tests.cli.test_validate_registry_parity tests.cli.test_validate_dispatch_consistency` expects exit 0. `test_the_registry_is_the_single_source_of_validate_dispatch` is the assertion that closed C2.
- Confirm the #770 fix: `uv run -m unittest tests.test_adr_eval_dispatch tests.governance.test_dispatch_attestation_absorption` expects exit 0, 21 tests. `test_dispatched_and_undispatched_scorecards_differ` is the assertion that the byte-identity #770 reproduced cannot recur.
- Confirm the solo scopes are behaviorally unchanged: `uv run gz validate --qc-binding` / `--fidelity-presence` / `--waiver-ratchet` each expect exit 0 with their own prose; `uv run gz validate --qc-binding --documents` expects exit 1 with the GHI #704 combined-scope refusal; bare `uv run gz validate` expects 13 default scopes.
- Confirm the full suite: `uv run gz arb step --name unittest -- uv run -m unittest -q` expects 8104 tests, exit 0.
- Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."
- Confirm the branch: `git rev-list --left-right --count origin/main...HEAD` expects `0	0`.

## Evidence / Artifacts

- `src/gzkit/adr_eval_dispatch.py` — the dispatch channel; mirrors the substance channel, credits only from a receipt, reports NOT DISPATCHED absent one.
- `tests/test_adr_eval_dispatch.py` — 14 tests, including `test_dispatched_and_undispatched_scorecards_differ` and `test_an_empty_channel_still_reports_not_dispatched`.
- `src/gzkit/adr_eval.py` — `_render_dispatch_section` (extracted under the xenon gate) and the `dispatch` field on `AdrEvalResult`.
- `src/gzkit/adr_eval_substance.py` — the GHI #624 precedent the dispatch channel mirrors.
- `src/gzkit/quality.py` — `run_dispatch_absorption_marker_audit`, docstring now disclaiming what it does NOT check.
- `src/gzkit/commands/validate_cmd.py` — the three `_ScopeEntry` rows that made the "single source" header true.
- `src/gzkit/req_kind_support.py` — `_early_return_scope_audit` retired; dispatch resolves through the registry.
- `tests/governance/test_check_scope_parity.py` — the fence strengthened from accommodation to assertion.
- `tests/cli/test_validate_registry_parity.py` — `_POST_SNAPSHOT_OTHER_SCOPES_EXCLUDED` hatch, mirroring GHI #741.
- `tests/governance/test_dispatch_attestation_absorption.py` — `TestTheStepIsNamedForItsSubject`, the naming-honesty contract.
- `data/check_scope_membership.json` — `reached_outside_registry` now empty; `registry_scopes` 82 -> 85.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — C2 checked off; § Amendments 2026-08-08 records the determination, the operator's verbatim rulings, and the count correction.
- `docs/design/adr/pool/ADR-pool.obpi-pipeline-dispatch-attestation.md` — § Absorption Note carries the naming correction and states the Target Scopes are unchanged and still unbuilt.
- `.gzkit/skills/gz-adr-evaluate/SKILL.md` — `### Degraded mode` section, skill-version 6.4.1 -> 6.5.0.
- `.gzkit/insights/agent-insights.jsonl` — an `improvement` under `campaign-item-verification` and a `discovery` under `git-sync-commit-shape`.

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
