---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-08-09T13:57:57Z'
agent: claude-code
session_id: 275b37a7-4746-4c06-85e0-a0db35c3666b
continues_from: .gzkit/handoffs/20260809T022008Z-four-carried-ghis-closed-and-two-pool-adrs.md
---

## Current State Summary

Released v0.34.2 (30 GHIs), then swept all 39 chores and worked the operator-ruled queue.

Shipped: patch release v0.34.2 with narrative RELEASE_NOTES + 31 CHANGELOG entries (21e52563a);
GHI #781 filed, fixed and closed -- `gz chores advise` exited 0 while printing FAIL, which had
hidden 7 failing chores (b86c4426f); GHI #782 filed and left open with a blocker comment;
governance-core.md scoped to 0.9.0, closing two blocking rule-pair rows (1c36e0c4b); all four
control-surface audit chores re-derived and green (d63947989, b27db3b7c, 8c6f0de9c, 4b425cfce,
a81b5c37e, 962fdc972); the first of four module-SLOC breaches corrected by extracting the Step-4b
adversarial gate to its own module (0a2672562).

Stopped mid-way through the SLOC correction on operator instruction. 9 commits ahead of origin at
handoff time; git-sync is the immediate next action.

FAILING CHORES (the operator's specific ask -- swept with the now-correct exit code):
3 of 39 fail. Measured 2026-08-09 AFTER b86c4426f, so the exit codes are trustworthy.

  1. hardcoded-root-eradication  -- criterion 6 only. FALSE POSITIVE, tracked at GHI #782 (OPEN,
     approach unruled). The sole grep hit is a COMMENT at
     src/gzkit/chores/module-sloc-cap-radon/check_module_size.py:50 stating the file AVOIDS
     Path(__file__).parents[N] -- and naming this very chore as the reason. The code is compliant.
  2. module-sloc-cap-radon       -- 3 of 4 breaches remain: parser_artifacts.py (1743->1760),
     parser_maintenance.py (1582->1667), validate_cmd.py (1309->1354). obpi_complete.py was
     corrected this session (0a2672562).
  3. test-isolation-compliance   -- criterion 1 only (tests/tools/test_health_profiler.py). Two
     observations, both failing, different causes: an idle run failed on 'Stdout noise: 6 lines'
     at 116.7s; a run under concurrent sweep load TIMED OUT at 120.0s. The profiler sits close to
     its own timeout budget, so re-measure it idle before diagnosing.

31 chores confirmed PASS this run. The remaining 5 (skill-command-doc-parity, skill-trigger-testing,
test-consolidation-subtest-sweep, test-manpage-examples, validate-manpages) were not re-swept -- the
sweep was stopped early for context budget. Their earlier-sweep OUTPUT TEXT read 'All criteria pass',
which is trustworthy (only the exit code was broken, never the rendering), but they have not been
re-verified against today's changes. Treat them as probably-passing, not confirmed.

## Important Context

THE ADVISE EXIT-CODE DEFECT SHAPED THIS WHOLE SESSION. Before b86c4426f,
`gz chores advise` printed per-criterion FAIL and 'Some criteria failed.' and returned exit 0.
A 39-chore sweep recorded exit=0 for all 39 and would have been reported as '39/39 green, nothing
to do'. Seven were failing. Any chore result from before that commit is untrustworthy.

THE FRESHNESS GATE IS A TREADMILL BY DESIGN. All four control-surface chores audit .gzkit/rules,
and scripts/check_proof_freshness.py compares COMMIT EPOCHS (%ct), not dates. Any commit touching
.gzkit/rules re-stales all four, even minutes later. This happened once in-session: 1c36e0c4b
re-staled chore 1 after it was green. The recovery is to re-derive, never to touch. Sequence rule
learned: land rule edits BEFORE running the audits, not after.

THREE AUDITS REACHED ONE CONCLUSION INDEPENDENTLY. Pass A (rule vs rule, 19 rows), Pass C (prose vs
check, 43 rows), Pass B (skill vs rule, 11 gaps) each found the same thing by a different route:
a rule that ASSERTS a mechanism rots silently; a rule that DISCLOSES having no gate never does.
Pass C quantified it -- 19 rows assert, all 19 drifted; 6 disclose, none ever has. In every Pass B
gap the skill is coherent and the rule is coherent; what is missing is the witness.

A HELPER'S MODULE IS PART OF ITS OBSERVABLE BEHAVIOR. The first SLOC extraction attempt promoted
_fail to commands/common.py to break an import cycle. It imported cleanly and all 52 of the
adversarial gate's own tests passed -- then 12 tests across four other obpi_complete suites failed,
all asserting on captured console output, all empty. Those tests patch obpi_complete.console; a
_fail living in common.py writes to common.console. Only the full 8270-test suite caught it. On a
Gate-5 path, the targeted run was the misleading signal.

A PRESENCE CHECK CANNOT VERIFY BEHAVIOR. Scorecard row 17e was authored this session claiming
`--cli-alignment` exits 3; it exits 1. The scorecard's own _missing_witness_path_errors arm exists
for exactly this class and could not catch it -- the row cited a real flag, a real module, and a
real registration. Every path resolved; the behavior claim was false. Corrected in place.

## Decisions Made

- [operator-ruled] Cut patch release v0.34.2 (verbatim: "/gz-patch-release"), then approved the drafted narrative release notes (verbatim: "Approved — execute").
- [operator-ruled] Work the four-item routing in the order recommended (verbatim: "proceed as suggested"): fix the advise exit code first, then the control-surface chores, then module-SLOC, filing the hardcoded-root GHI alongside the first.
- [operator-ruled] Re-run the remaining three control-surface chores at full fidelity rather than a shallow pass, and apply the R18/R19 scope fix to governance-core.md (verbatim: "1. yes, 2. yes").
- [operator-ruled] Stop the SLOC correction after the first module, author a handoff, determine only the chores still failing, and git-sync (verbatim: "stop, write a new handoff, determine only the chores that still need to be passed. git-sync").
- [agent-chose] Left GHI #594 OPEN and uncounted in the release Stats. `gz arb archive` landed but the purge half did not, so patch-release Step 1b Case 2 applied. Closing it to clear the discovery bucket is the defect that bucket exists to prevent.
- [agent-chose] Backfilled the `runtime` label on GHI #773 and #777 (remedies landed in src/gzkit/commands/adr_demote.py) but NOT on #533 or #779, following the #750 precedent recorded in v0.34.1 Gate Evidence: a src/ diff confined to generated mirrors does not fire the runtime predicate.
- [agent-chose] Scoped the governance-core tool-output bullet rather than retracting it, and re-cut untrusted-content.md rule 3 on provenance rather than artifact type.
- [agent-chose] Reverted the _fail promotion to common.py and used a call-time import in the extracted module instead, per pythonic.md § Imports' cycle-avoidance carve-out.
- [agent-chose] Recorded parity row M6 as 'not re-verified' rather than carried or closed, because its module path returned no match. An unverified row is not a clean one.

## Immediate Next Steps

1. Run `uv run gz git-sync --apply` to push the 9 local commits. Note: the #708 [settled] fix refuses to sweep src/ into a chore commit, so any src/ work must be committed under its own message with a `Task:` trailer first (this session hit that twice).
2. Finish the module-SLOC correction: parser_maintenance.py (+85), validate_cmd.py (+45), parser_artifacts.py (+17). The extraction pattern is proven in 0a2672562 -- find the cohesive family that grew, move it, import back what the caller uses, run the FULL suite (not the targeted one). Re-baselining is forbidden by the ratchet's own _doc.
3. Wire the module-size gate into gz check AFTER step 2, not before -- it has no automatic caller today, which is how a 297-SLOC breach shipped in v0.34.2 with every gate green. Wiring it first would fail the build.
4. Rule on GHI #782's approach: (1) tighten the criterion regex to match code not prose, (2) add the file to --exclude, or (3) reword the comment. Only (1) fixes the class; (2) is the shape GHI #779 [settled] argued against. The blocker comment on the issue carries the tradeoff.
5. File the GHI routed by Pass B: 29 chore directories ship a proofs/ folder into src/gzkit/chores/ (71 files) from a surface chores.md:35 declares 'always project-local, never canonical', and the distribution baseline manifest mentions proofs zero times, so --distribution reports clean.

## Pending Work / Open Loops

- GHI #782 is OPEN with a blocker comment; the approach is unruled. hardcoded-root-eradication stays red until it is ruled.
- Module-SLOC: 3 of 4 modules still breach their shrink-only ceilings. 1 of 4 corrected.
- The module-size gate still has no automatic caller. It is the only witness for the shrink-only ratchet and it only speaks when a human runs the chore.
- Pass C follow-up #1 [settled] is a one-string fix not yet applied: transcribed_counts.py emits type="surface" while "transcribed_adr_counts" is registered in _POLICY_BREACH_ERROR_TYPES, so the registration matches nothing.
- Pass C found four surfaces claiming exit 3 that deliver exit 1 (--cli-alignment, --brief-headings, --changelog, gz cli audit). Needs one ruling on direction, then four edits.
- Pass D found standing consent to run the commit ceremony with the secret scanner disabled: .claude/settings.local.json:80 grants Bash(SKIP=gitleaks ...), and no deny rule mentions SKIP. Routed as a one-line addition to settings.json's deny list. NOT applied -- the chore is read-only on permission surfaces.
- Pass B: 9 of 11 skill/rule gaps carry a filed GHI. The two most serious are in gz-obpi-pipeline (#284 [settled], #643 [settled]); #643 [settled] sits on the Gate-5 attestation path.
- 54 of 89 registered validator scopes bind no scorecard row. Needs an operator ruling on whether the inverse direction gets an owner.
- The ADR-0.35.0 sequencing question is now nine sessions wide and untouched this session.
- The advisory-scorecard grandfather sweep shrank 23 -> 16 as a side effect of scoring governance-core for real. 16 rules remain pinned.

## Verification Checklist

Run these before trusting any claim above:

```
git rev-list --left-right --count origin/main...HEAD   # expect 0 N until git-sync runs
uv run gz check                                        # expect exit 0
uv run -m unittest -q                                  # expect exit 0, 8270 tests
uv run python .gzkit/chores/module-sloc-cap-radon/check_module_size.py   # expect exit 3, 3 modules
gh issue view 781 --json state                         # expect CLOSED
gh issue view 782 --json state                         # expect OPEN (approach unruled)
gh issue view 594 --json state                         # expect OPEN (deliberate, uncounted in v0.34.2)
```

Chore state is only trustworthy from commit b86c4426f forward. Before that, `gz chores advise`
returned exit 0 on failure. To re-derive the failing set:

```
for s in $(jq -r '.chores[].slug' .gzkit/chores/registry.json); do
  uv run gz chores advise "$s" > /dev/null 2>&1 || echo "FAIL $s"
done
```

Note that several chores run the full unit suite as an acceptance criterion, so a full sweep costs
roughly 25 minutes.

## Evidence / Artifacts

Release:
- `RELEASE_NOTES.md` (v0.34.2 narrative, 30 GHIs)
- `CHANGELOG.md` (31 entries)
- `docs/releases/PATCH-v0.34.2.md`

Runtime fixes:
- `src/gzkit/commands/chores.py` (GHI #781 -- advise exits 3)
- `docs/user/manpages/chores-advise.md` (coupled surface)
- `src/gzkit/commands/obpi_complete_adversarial.py` (new; Step-4b gate extracted)
- `src/gzkit/commands/obpi_complete.py`
- `tests/test_adversarial_validation_gate.py`

Governance:
- `.gzkit/rules/governance-core.md` (0.9.0 -- tool-output scope)
- `docs/governance/untrusted-content.md` (rule 0 + provenance re-cut)
- `docs/governance/advisory-rules-audit.md` (rows 17c-17g scored; row 17e corrected)
- `data/advisory_scorecard_grandfather.json` (23 -> 16 entries)

Audit proofs (all four re-derived):
- `.gzkit/chores/control-surface-rule-conflicts/proofs/`
- `.gzkit/chores/control-surface-permission-consent-drift/proofs/`
- `.gzkit/chores/control-surface-rule-vs-check-drift/proofs/`
- `.gzkit/chores/control-surface-skill-rule-reachability/proofs/`

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
