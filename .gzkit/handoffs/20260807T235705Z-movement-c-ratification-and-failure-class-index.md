---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-07T23:57:05Z'
agent: claude-code
session_id: e5e7eb67-51ec-4d66-83a8-d8a6154144de
continues_from: .gzkit/handoffs/20260807T192215Z-corroboration-adr-and-orphan-detector-repair.md
---

## Current State Summary

Session opened on a handoff review and ran to a ratified campaign amendment plus one new shipped surface. Sequence: resumed and verified the predecessor handoff (one STALE claim found — ADR-0.35.0 is 0/10, not 0/9); split GHI #766 into #766 (bookmark retirement) + #767 (handoff transcript channel), with #766 blocked by #767; filed #768 (transcribed OBPI counts couple to nothing), #769 (adr-evaluate scorecard writer fights its own skill), #770 (dispatch-attestation audit checks a marker, not dispatch); reconciled OBPI-0.35.0-01/02/03 against 16 days of unseen pre-landed drift; amended ADR-0.35.0 to extend `gz content retire` rather than ship a second `withdraw` verb; evaluated ADR-0.35.0 (GO, 3.60 substance, 2 red-team failures) and fixed a duplicate BI-04; measured the whole 333-GHI closed corpus for recurrence; built the `failure-class-index` chore; ratified two Movement C amendments. Seven commits, all pushed, origin/main even at authoring.

## Important Context

The reconciler cannot see the drift that matters. `gz obpi brief-drift` reported CLEAN on all five dimensions for OBPI-0.35.0-01/02/03 while every one of them was materially wrong: the verb they plan to CREATE already ships as `gz content retire`, the tombstone field already exists, `tier_policy` already reads it, and 1 of 8 retirements already landed. All five dimensions are existence checks. Recorded on GHI #581 as a third failure class (exists-but-should-not-yet, the mirror of its exists-but-dead). Do not read a green brief-drift as evidence a brief is current.

The `gz-validate-skip: command-shape` marker is load-bearing in both directions. It hid the retire/withdraw collision for 16 days; removing it made `--cli-alignment` catch three residual references instantly (exit 1). The marker asserts planned-but-unlanded — so it is correct for `gz content land` (OBPI-07, genuinely coming) and a lie for `withdraw` (no longer planned). Reword historical references; never re-mark them.

Analysis surfaces ship as a chore plus a module, never as a `gz` verb. Precedent: `session-correction-mining` -> `src/gzkit/insights/correction_mining.py`, invoked `uv run python -m ...`. No CLI contract means no Heavy lane and no OBPI ceremony, which is how the failure-class index landed without violating one-feature-at-a-time while ADR-0.35.0 is in flight.

The GHI corpus was already a recurrence dataset. 288 of 333 closed GHIs carry an authored `## Class of failure` section (87%) because `/ghi-author` makes it part of filing rather than a convention to remember. That is the highest-compliance authored channel in the repo, against `@advances` at 0 and `tasks:` at 7 of 534 pre-stamp. The producer-stamping lesson was already proven and simply never generalized.

Layer drift is the one family measurably closing (10 -> 7 -> 6 -> 1 across May-Aug). It closed because it got a doctrine (`state-doctrine.md`), a regenerator (`gz register-adrs`), and a fail-close (`--adr-status-fresh`). That triple is the template the new Movement C box is modeled on; the doctrine family has at best the first two.

Chore proofs must not carry adapter inputs. The GHI snapshot is 1.4 MB of third-party issue text that has never been scanned against the operator-PII prohibition. It is regenerable via `gh`; only the emitted report and run telemetry belong under `proofs/`.

## Decisions Made

- [operator-ruled] Work advised step 1 first (verbatim: "Step 1 first — rule on splitting GHI #766"), then return to the campaign; advised steps 3 and 4 recorded set-aside via `gz handoff decide`.
- [operator-ruled] Split GHI #766 and park both halves behind the doctrine ADR (verbatim: "Split; park both behind the doctrine ADR"). #767 filed for the transcript channel; #766 keeps bookmark retirement and is blocked by it.
- [operator-ruled] Correct the stale campaign counts and file the class-level defect (verbatim: "Fix it and file the class-level defect") — produced GHI #768.
- [operator-ruled] Sync, then survey ADR-0.35.0 before touching code (verbatim: "Sync, then survey ADR-0.35.0 first").
- [operator-ruled] Extend `gz content retire` in place rather than rename it to `withdraw` (verbatim: "Extend `retire` in place"); ADR-0.35.0 amended at five sites to match.
- [operator-ruled] Verify the family clustering before amending Magna Carta (verbatim: "Verify first, then ratify").
- [operator-ruled] Build the class-of-failure index as a real surface before writing campaign boxes against it (verbatim: "Build the class-of-failure index first").
- [operator-ruled] Ratify both Movement C amendments (verbatim: "ratify both, write handoff, git-sync").
- [agent-chose] Commented the third failure class onto GHI #581 rather than filing a sibling GHI — same root cause, same already-decided TRACK ONLY remedy; a second issue would have been the sibling-cut duplication /ghi-author Step 0 exists to prevent.
- [agent-chose] Left three historical `0/9` strings unchanged (campaign 2026-07-29 amendment record, OBPI-0.35.0-10 provenance note, OBPI-03 REQ table). They were true on their dates; correcting a dated record falsifies history rather than repairing it.
- [agent-chose] Did not rename OBPI-0.35.0-02's id off `content-withdraw-verb`. Renaming an OBPI id is a semver-identifier migration touching the ADR 1:1 checklist mapping and every ledger reference. The id is a label; § Objective is the contract.
- [agent-chose] Did not silently rewrite OBPI-03's "EXACTLY EIGHT" to seven. Requirement 2 mandates re-derivation at implementation time and Requirement 1 warns an off-by-one inside a Gate 5 batch is a fabricated receipt; editing the count would have discharged the obligation on paper without anyone performing it.
- [agent-chose] Built the index as a chore plus module rather than a `gz` verb, following the `session-correction-mining` precedent, so no CLI contract is created and no OBPI ceremony is owed.
- [agent-chose] Removed the 1.4 MB GHI snapshot from `proofs/` and documented writing it outside the repo.

## Immediate Next Steps

1. Work the ratified Movement C box: close the doctrine-declared-without-mechanism family. Start with GHI #770's minimum honest fix, which needs no new machinery — rename `run_dispatch_attestation_audit` to what it checks (it is a legitimate absorption-marker audit), and require any ceremony whose mandated dispatch did not run to say so in its output. That converts the family's cheapest instance into the template for the rest.
2. Land the C2 enrollment fail-close (GHI #744) — registering a `gz validate` scope must enroll it in `gz check`. Until it does, the registry collapse lowers the count without closing the family, which is exactly what the amendment retargeted away from.
3. Re-run the `failure-class-index` chore against a fresh snapshot including OPEN GHIs (`--state all`). This session only indexed closed issues; open ones are where a live chain would show before its next instance is authored.
4. Return to ADR-0.35.0 when the operator draws it. The 01 -> 03 slice is unblocked and reconciled: OBPI-01 adds `supersedes` to `POST_BASELINE_IDENTITY_FIELDS`, builds the nine-clause fold, and repoints `tier_policy` off the flat `retired_ids()`. Note un-retirement does not work today and fails silently.
5. Decide whether GHI #767 (handoff transcript channel) waits for `ADR-pool.primary-source-corroboration` promotion or routes as an ADR-0.0.65 direct-fix correction. Both #766 and #767 are parked behind that promotion by this session's ruling.

## Pending Work / Open Loops

- GHI #766 and #767 are both open and parked behind `ADR-pool.primary-source-corroboration` promotion. #766 is blocked by #767; the ordering is recorded in both and in the ADR at lines 210-211.
- GHI #768 (transcribed OBPI counts couple to nothing), #769 (adr-evaluate scorecard writer), and #770 (dispatch-attestation audit) are open with no remedy selected. #769 and #770 each carry candidate shapes; none is chosen.
- GHI #581 remains open at TRACK ONLY with a third failure class added this session. That ruling is now three instances older than the evidence that produced it.
- ADR-0.35.0 is Draft, 0/10 landed. Briefs 04-10 have NOT been reconciled against the tree; only 01-03 were. The reconciler cannot detect pre-landed work, so assume the same drift class until each is read by hand.
- The `failure-class-index` chore indexes closed GHIs only. Open GHIs are unindexed.
- ADR-0.35.0's pre-mortem #1 (the ratchet becomes a ceiling) remains unmitigated by the ADR's own admission; cadence, owner, and scheduled floor-raise are UNDECIDED and must be resolved before OBPI-04, not after.
- The evaluation of ADR-0.35.0 was single-driver: the skill's mandated persona dispatch did not run, under a standing session instruction not to spawn subagents. Recorded in `EVALUATION_SUBSTANCE.md`; nothing mechanical required or noticed that disclosure, which is GHI #770's subject.
- AGENTS.md sits 385 B over the codex delivery cap (advisory in `gz check`). Instructions-file budget work stays parked by standing operator ruling.

## Verification Checklist

- Never pipe a verifier. Capture to a file and read the bare status: `<cmd> > out.log 2>&1; echo "REAL EXIT: $?"`. The verifier-pipe-gate PreToolUse hook refuses a verifier in any non-final pipeline stage, and PIPESTATUS reads back empty under zsh.
- Confirm the quality gate: `uv run gz check` expects exit 0. Two advisories are expected and pre-existing (AGENTS.md 385 B over the codex cap; 692 unlinked specs).
- Confirm the new chore: `uv run gz chores doctor` expects `failure-class-index HEALTHY / HEALTHY`; `uv run gz validate --chores-layout` expects 0; `uv run -m unittest tests.chores.test_failure_class_index` expects 20 tests, exit 0.
- Reproduce the index: `gh issue list --state closed --limit 800 --search 'closed:>=2026-05-09' --json number,title,body > "${TMPDIR:-/tmp}/s.json"` then `uv run python -m gzkit.insights.failure_classes --snapshot "${TMPDIR:-/tmp}/s.json" --dry-run` expects "read 333, indexed 288, 71 declaring (25%), deepest chain 12". Counts move as new GHIs close; the shape is the assertion, not the exact number.
- Confirm governance artifacts: `uv run gz validate --documents --taxonomy --cli-alignment --adr-status-fresh` expects 0 across 4 scopes; `uv run mkdocs build --strict` expects 0.
- Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."
- Confirm the branch: `git rev-list --left-right --count origin/main...HEAD` expects `0	0`.

## Evidence / Artifacts

- `src/gzkit/insights/failure_classes.py` — the index and chain resolver; core takes records as a parameter and never invokes `gh` (hexagonal rules 1 and 4).
- `tests/chores/test_failure_class_index.py` — 20 tests, semantics-derived from real GHI shapes (#505, #554, #537).
- `.gzkit/chores/failure-class-index/CHORE.md` — workflow, guardrails, and acceptance criteria that gate the chore's own subject (GHI #743).
- `.gzkit/chores/failure-class-index/proofs/failure-class-index-2026-08-07.md` — the first real report: 15 chains of depth >= 3, deepest 12.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — Movement C amended: new family-closure box, C2 retargeted; both recorded in § Amendments.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/ADR-0.35.0-canon-entry-corpus-landing.md` — Decision item 2 amended to `retire`, Boundary Invariants renumbered BI-01..BI-08, Q&A transcript under a SUPERSEDED banner.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/EVALUATION_SUBSTANCE.md` — the substance scorecard, 3.60 GO, with the single-driver limitation recorded in the artifact.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-01-corpus-tombstone-schema-and-fold.md` — PARTIALLY PRE-LANDED reconciliation note.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-02-content-withdraw-verb.md` — retargeted to extend `retire`; id deliberately unrenamed.
- `docs/design/adr/pre-release/ADR-0.35.0-canon-entry-corpus-landing/obpis/OBPI-0.35.0-03-retire-duplicate-invariant-entries.md` — re-reconciled; 7 of 8 retirements remain, 50 -> 43 live invariant.

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
