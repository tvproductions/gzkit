---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-08T01:35:08Z'
agent: claude-code
session_id: 5b61831c-a7bb-4f61-b6db-7b458b664fbe
continues_from: .gzkit/handoffs/20260808T005049Z-c2-closure-and-dispatch-naming.md
---

## Current State Summary

Session opened on a handoff review, found its top advised step stale, and was redirected by the operator onto advised step 4 (the `gz git-sync` commit-shape question). That ruling produced a reopen-and-fix of GHI #708 plus a ranked defect ledger the operator asked be carried forward rather than executed.

**GHI #708 reopened and closed `fixed`.** Its sweep guard landed `6c26d67b` on 2026-07-21 and read `git diff --cached --name-only` **one line before** `git add -A` populated the index, so it defended only the aborted-commit cause. An ordinary dirty worktree — the entire premise of the `--auto-add` flag the guard sits inside — walked past it, and `57bd15f91` swept six governed files (165 lines) into a `chore:` ceremony commit **eighteen days after the guard shipped**. All nine of its tests stubbed `diff --cached`; none exercised the unstaged path. The predicate now unions the three reads whose result is exactly what `add -A` would stage: the index, tracked-but-unstaged changes, and untracked files.

Two commits, both pushed, `origin/main` 0/0 at authoring. `uv run gz check` exit 0; 8109 unit tests OK (was 8104 — the five new guard tests).

**The handoff that opened this session named five closed GHIs as open.** Advised step 1 listed #692, #693, #459, #574 and #620 as "still open"; all five are `CLOSED / COMPLETED`, #459 since 2026-05-12. The campaign box at line 156 never claimed otherwise — it cites them as exemplars measured over "the 333 GHIs closed since 2026-05-09". The handoff turned closed-corpus exemplars into an open-work list, which is GHI #768 exactly, one section after diagnosing the `(GHI #744)` instance of it.

## Important Context

**The `/ghi-author` Step-0 prior-art lookup is what prevented a duplicate, and it is the only reason this session found a live defect.** The intent was to file a fresh GHI for the chore-subject finding. Step 0 surfaced #708 — same root cause, closed `COMPLETED` seven minutes after filing, proposing verbatim the remedy the operator had just ruled. Skipping Step 0 would have produced a duplicate-scoped GHI **and** left the real hole open, because the fresh GHI would have been written against the symptom rather than against the guard that was supposed to stop it. Run Step 0 even when the finding feels novel; confidence in novelty is the failure state the skill names.

**A ≤30-day close on the same root cause is a reopen, never a fresh file.** `ghi-author` § Step 0 states it (*"never file a fresh GHI for the same root cause"*) and operator correction doctrine agrees — *discovering that more is needed to fulfil the intent of a feature is not an enhancement, it is a correction*. #708 closed 18 days before the reproduction. The routing was determined by rule, not judgment, so no operator round-trip was spent on it.

**`git log --grep` matches the whole commit message, not the subject — and this bites asymmetrically.** `--grep='^chore'` returned 236 commits touching `src/`, of which the true subject-anchored count was 193: `fix(chores):` commits whose **body** carries a line starting with "chore" matched. But `--grep='^fix('` has **zero** false positives across 90 days (verified: 481 by both methods), because almost no commit body starts a line with `fix(`. **The precedent query AGENTS.md § Defect-fix routing prescribes is therefore sound and needs no change** — an earlier claim in this session that it was contaminated was wrong and was corrected before any rule edit. Measure commit *types* with `git log --format='%s'` and filter the subjects; reserve `--grep` for body content.

**A figure with a date anchor is evidence; the same figure without one is a claim.** The campaign carries "470 `fix` commits" twice. Line 52 sits in a table headed *"(90d to 2026-07-18)"* and is correct as-of — it was left untouched. Line 144 carried the same number as a live, undated assertion and was the one that needed anchoring. Overwriting line 52 would have been GHI #768 inverted: destroying a correct measurement because a fresher one exists.

**`failure-class-index` is snapshot-driven, so widening it to open GHIs is an input change, not a code change.** `src/gzkit/insights/failure_classes.py` indexes whatever records it is handed and carries no internal state filter — its docstring cites "288 of 333 closed GHIs" because that is the snapshot it was run against. Feeding it `gh issue list --state all` needs no edit to the module. This reclassifies the long-deferred "re-run with open GHIs" item from engineering work to a chore run, which is why D3 below is cheap.

**The guard now dogfoods itself, and the commit log shows it.** The fix was landed by obeying the guard`s own refusal message, then synced: `4c77192d8` carries the source under a `fix(` subject and `0dbe5502a` carries **only** `.gzkit` state under the ceremony subject. That two-commit shape is the intended steady state; a single `chore:` commit carrying both is the defect returning.

## Decisions Made

- [operator-ruled] Work advised step 4, the `gz git-sync` commit-shape question (verbatim: "Rule on the git-sync commit shape (step 4)"). Booked via `gz handoff decide`; advised steps 1, 2, 3 and 5 recorded set-aside, step 1 with the note that it is unexecutable as written because all five of its named members are closed.
- [operator-ruled] Refuse the bundle — `gz git-sync` fails closed when staged files carry source scope (verbatim: "Refuse the bundle (fence at sync)"). Selected from a four-option picker with rendered previews; the alternatives were split-the-commit, fix-the-query-not-the-commit, and warn-do-not-refuse.
- [operator-ruled] Write the recommendations into a handoff rather than executing them (verbatim: "write recommendations to handoff. git-sync"). D1 through D5 are carried as advised steps below, none of them started.
- [agent-chose] Reopened GHI #708 rather than filing a fresh GHI. Same root cause, closed 18 days earlier, and `ghi-author` § Step 0 forbids a fresh file for a ≤30-day close on the same cause. No operator round-trip was spent because the rule is mechanical.
- [agent-chose] Widened the predicate to three `--name-only` probes rather than one `git status --porcelain`. Porcelain packs a two-char status prefix, ` -> ` rename arrows, and `core.quotePath` escaping into one stream — three parsing hazards bought for one subprocess call saved.
- [agent-chose] Renamed `_staged_governed_paths` to `_sweep_governed_paths` and `_filter_governed_staged` to `_filter_governed_paths`. Both names overclaimed once the subject stopped being the index; this is GHI #770 template applied — rename the overclaiming surface, then widen it.
- [agent-chose] Gave the filter set semantics rather than deduplicating at the call site. The probes overlap by design (a file both staged and further modified is reported by two of them) and the guard subject is *which* paths are governed, never how many reads mentioned each.
- [agent-chose] Preserved both of GHI #708 ratified scoping decisions unchanged — scope stays `src/**` plus `tests/**`, and the guard still fails **open** on a git error, now from any probe rather than only the first.
- [agent-chose] Documented the guard in `docs/user/manpages/git-sync.md` with the real refusal transcript. `6c26d67b` shipped a fail-closed refusal with zero manpage coverage; fixing the instance while leaving the doc gap would have repeated the shape being fixed.
- [agent-chose] Left the dated campaign figure at line 52 untouched and anchored only the undated claim at line 144. A dated snapshot is evidence, not drift.
- [agent-chose] Withdrew an earlier claim that the prescribed precedent query `git log --grep='^fix('` was contaminated, after measuring zero false positives across 90 days. No rule edit was made on the strength of the withdrawn claim.

## Immediate Next Steps

These are the session recommended actions, ranked. **None is started.** The operator asked that they be written down rather than executed, so each carries its routing and its cost, and the pull order remains an operator decision.

1. **D1 — Grade the class claim in a GHI close comment. RECOMMENDED FIRST. New finding, unfiled.** GHI #708 closed `COMPLETED` asserting *"Closed at the staging decision itself, so every path into `git add -A` inherits it — not per-cause"* while its predicate read only the pre-staging index. That sentence is why a live defect sat marked-closed for 18 days and why the next session had no reason to look. GHI #770 carried the same shape on the audit side. **Recommended action:** extend `ghi-close` so the *Class-of-failure coverage* section must **name its covering tests**, and verify those tests exist and touch the claimed surface. **Why this one first:** it is the mechanism by which defects hide while marked closed — every other item on this list is findable, this one suppresses finding. It is also an unusually tractable member of the doctrine-declared-without-mechanism family: most members have no obvious witness, this one does. **Route:** `/ghi-author`, then direct fix.

2. **D2 — Give GHI #768 a remedy. Open, no remedy selected, now five observed instances.** Two more landed today: the resumed handoff named five closed GHIs as "still open", and the prior session read a `(GHI #744)` parenthetical as unlanded scope. **Recommended action:** resolve every `#\d+` in campaign boxes and in handoff *Immediate Next Steps* against live issue state at write time, annotating closed citations. `gz handoff resume` already does exactly this for advised steps (GHI #696) and renders `live` / `settled` / `unknown` per reference — the missing arm is the **authoring** side, so a handoff cannot be written naming a closed GHI as open work in the first place. Reuse the existing resolver rather than building a second one. **Route:** direct fix under #768.

3. **D3 — Re-run `failure-class-index` against a `--state all` snapshot. Cheapest item here; pairs well with anything above.** The Movement C box *Close the doctrine-declared-without-mechanism family* has **no identified open membership** — its five named members are closed exemplars drawn from a closed-GHI snapshot, which is why advised step 1 was unexecutable this session. `src/gzkit/insights/failure_classes.py` is snapshot-driven and needs no code change; feed it `gh issue list --state all`. **Why it matters beyond the cheapness:** it unblocks the campaign own topmost open Movement C item and discharges a pending-work entry that has been set aside twice. **Route:** chore run.

4. **D4 — Scan for fail-closed refusals with no manpage coverage.** `6c26d67b` shipped a hard refusal an operator could hit with nothing in the command documentation explaining it; that instance is now fixed, the class is unscanned. Five modules under `src/gzkit/commands/` emit `blockers.append`: `sync.py`, `status_render.py`, `chores_exec.py`, `common.py`, `chores.py`. **Recommended action:** cross-check each blocker site against its manpage, then decide whether `gz cli audit` should carry the check. Adjacent to closed GHI #693, which found the same narrower-than-its-name shape in the flag-description audit. **Route:** scan first, then decide — do not pre-commit to a validator scope before the scan says whether the gap is systemic or a single miss.

5. **D5 — No action available; recorded so it stops being rediscovered.** 193 `chore`-subject commits touched `src/**/*.py` in the 90 days to 2026-08-08 and no query can retroactively distinguish defect fixes among them. The fence makes the count honest going forward only. Already captured as a `defect-resolution` insight under scope `git-sync-commit-shape` and in the Movement B campaign box, so the next session finding an odd `fix` count has the explanation in hand.

## Pending Work / Open Loops

1. **The Movement C family box remains unexecutable until D3 runs.** It is the campaign topmost open Movement C item and its five named members are closed. Do not pull it before the open-GHI snapshot exists, and do not re-read those five numbers as work.

2. **GHI #573 is still open and unaffected by the #708 repair.** It is the instance-level cut — a DRY classifier collapse that was swept into `996a481` and reverted — and still needs its governed TDD redo. The #708 fix closed the mechanism that allowed the sweep; it did not do #573 work.

3. **GHI #768, #769, #767, #766, #765 remain open with no remedy selected.** #766 is blocked by #767; both are parked behind `ADR-pool.primary-source-corroboration` promotion by a prior session ruling. #768 now has five instances and a concrete recommendation in advised step 2.

4. **GHI #581 remains open at TRACK ONLY**, with a ruling now several instances older than the evidence that produced it.

5. **ADR-0.35.0 is `Pending` at 0/10, all ten briefs `draft`.** Briefs 04 through 10 have still not been reconciled against the tree; only 01 through 03 were, and `gz obpi brief-drift` cannot see pre-landed work. It is Movement A item 2 and therefore ahead of Movement C in campaign sequence — worth naming, because two consecutive sessions have worked Movement C while Movement A stayed open.

6. **ADR-0.35.0 pre-mortem #1 (the ratchet becomes a ceiling) remains unmitigated by the ADR own admission**; cadence, owner, and scheduled floor-raise are undecided and must be resolved before OBPI-04.

7. **The dispatch residual from the prior session is untouched.** `gz-adr-audit` and `gz-adr-closeout-ceremony` carry the same `## Persona Dispatch` mandate and have no channel; they emit no artifact in the shape the scorecard does, so hanging one on them is a design question rather than a mechanical extension of `ae7ffffc6`.

8. **AGENTS.md instructions-file budget work stays parked by standing operator ruling.** `gz check` currently reports it 385 B over the codex delivery cap as an advisory; exit code is unaffected.

## Verification Checklist

- Never pipe a verifier. Capture to a file and read the bare status: `<cmd> > out.log 2>&1; echo "REAL EXIT: $?"`. The `verifier-pipe-gate` PreToolUse hook refuses a verifier in any non-final pipeline stage, and PIPESTATUS reads back empty under zsh.
- Confirm the guard fence: `uv run -m unittest tests.commands.test_sync_sweep_guard` expects exit 0, 17 tests. `test_unstaged_src_modification_blocks_the_sweep` is the assertion that closed the reopening; `test_ceremony_only_dirty_tree_still_sweeps` is the negative control proving the widened guard did not disarm the ceremony.
- Confirm the guard on the real CLI **without risking a commit**: run the predicate directly first — `uv run python -c "from pathlib import Path; from gzkit.commands.sync import _sweep_governed_paths; print(_sweep_governed_paths(Path('.')))"`. A non-empty result means `uv run gz git-sync --apply` will refuse and stage nothing; an empty result means the sweep is permitted. Check the predicate before running `--apply` on a dirty tree, never after.
- Confirm the quality gate: `uv run gz check` expects exit 0. Two advisories are expected and are not regressions — 692 unlinked specs (pre-existing) and the AGENTS.md instructions-files budget warning (parked by standing operator ruling).
- Confirm the full suite: `uv run gz arb step --name unittest -- uv run -m unittest -q` expects 8109 tests, exit 0.
- Confirm trailer discipline held: `uv run gz validate --commit-trailers` expects exit 0.
- Confirm the fix is visible to the query it hid from: `git log --since='90 days ago' --format='%s' --grep='^fix(' | grep 'add -A'` returns the `4c77192d8` subject.
- Measure commit **types** by subject, never by `--grep`: `git log --since='90 days ago' --format='%s' > subjects.txt` then `grep -c '^chore' subjects.txt`. Using `--grep='^chore'` inflates the count by matching commit bodies.
- Confirm no active locks: `uv run gz obpi lock list` expects "No active locks."
- Confirm the branch: `git rev-list --left-right --count origin/main...HEAD` expects `0	0`.

## Evidence / Artifacts

- `src/gzkit/commands/sync.py` — `_SWEEP_SCOPE_PROBES`, `_sweep_governed_paths` (widened predicate, fails open on any probe), `_filter_governed_paths` (set semantics), `_sweep_guard_message` (three-part recovery prose naming both the trailer-scope rule and the blinded precedent query).
- `tests/commands/test_sync_sweep_guard.py` — 17 tests, up from 12. New positives `test_unstaged_src_modification_blocks_the_sweep`, `test_untracked_test_file_blocks_the_sweep`, `test_unions_staged_unstaged_and_untracked`; new negative controls `test_ceremony_only_dirty_tree_still_sweeps`, `test_a_later_probe_failing_still_fails_open`.
- `docs/user/manpages/git-sync.md` — new **Governed-scope sweep guard** section carrying the real refusal transcript and the recovery example. The guard shipped in `6c26d67b` with no manpage coverage at all.
- `docs/governance/build-to-1.0-campaign-2026-07-18.md` — Movement B box now carries the dated figure, the current figure, the 193/187 blind-spot measurement, and the `--grep` versus `--format='%s'` measurement note. The dated table at line 52 was deliberately left unchanged.
- `.gzkit/insights/agent-insights.jsonl` — a `defect-resolution` under scope `git-sync-commit-shape`, closing the loop on the prior session `discovery` under the same scope, and naming the unrecoverable historical undercount as its next action.
- `src/gzkit/insights/failure_classes.py` — read, not modified. Named here because it is the surface D3 depends on: it is snapshot-driven with no internal state filter, which is what makes the open-GHI re-run an input change.
- Commits: `4c77192d8` (`fix(sync): guard what add -A would stage, not what is already staged (GHI #708)`, `Task: TASK-git-sync-sweep-guard-#708`) and `0dbe5502a` (ceremony sync carrying only `.gzkit` state — the two-commit shape the guard exists to produce).
- Receipts: `arb-step-unittest-840784a40b874d019b08f8cfe8b20cde` (8109 tests OK), `arb-ruff-62293efb89c648cdaa30e4ca69e0f397`, `arb-step-typecheck-c9d7fa00e012463ca2baf3676fecf803`.
- RED witness, observed before the production edit: an ImportError reporting that the name _sweep_governed_paths could not be imported from the sync command module. Captured in the session RED log before any production edit.

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
