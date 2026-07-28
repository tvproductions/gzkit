---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-28T11:10:26Z'
agent: claude-code
session_id: fb99d72b-3ab8-4335-8598-80a6e2fd35b7
continues_from: .gzkit/handoffs/20260728T091801Z-budget-doc-reconciled-relaxation-ruled-triage-census.md
---

## Current State Summary

Session resumed the 2026-07-28T09:18Z budget handoff, verified its claims against Layer-2, and worked its advised step 1 under operator authorization. Two commits are on main; the tree is clean and level with origin at `9db71b6ff`.

The `gz drift` advisory of 2020 unlinked specs was investigated and found to be MOSTLY NOT DRIFT, though not for the reason the predecessor handoff proposed. Its hypothesis (SUPPORT and STRUCTURAL-FENCE correctly show unlinked under ADR-0.0.59) is true but accounts for only 244 of 2020, about 12 percent. The dominant term is 1645 REQs carrying no taxonomy tag at all, because only ~21 percent of the 3739-REQ corpus has been tagged since ADR-0.0.59 landed.

The question underneath the advisory resolved cleanly: NO GATE WAS BYPASSED. Eight uncovered BEHAVIOR REQs sit in Completed briefs, a class AGENTS.md says is impossible because the REQ-coverage gate cannot be waived. All eight are correctly-superseded REQs whose retirement is recorded in bold prose that no scanner reads.

`gz drift` now reports 1418 unlinked and 0 orphan, down from 2020 and 10. `gz check` passes all gates; 7548 unit tests OK; 23 new tests landed.

GHI #729 was filed, fixed, and closed citing `9db71b6ff`. GHI #730 was filed for a defect the sweep unmasked and remains OPEN with only its narrow half addressed. The REQ-retirement finding was folded onto GHI #611 per operator ruling.

## Important Context

THE TWO DRIFT ARMS NEED DIFFERENT REQ SETS. This is the single most important fact for anyone touching `detect_drift`. The unlinked arm reads the covers-channel subset; the orphan arm computes `test_target_req_ids - known_req_ids` and MUST see every declared REQ. An intermediate revision filtered at the caller, which shrank the orphan baseline and turned every legitimate SUPPORT citation into a phantom orphan: 10 orphans became 63. The filter therefore lives inside the engine where both facts are available, and no caller can get it wrong. Pinned by `TestScopingDoesNotManufactureOrphans`.

RETIRED IS NARROWER THAN SEALED. `is_terminal_brief_status` is deliberately NOT the predicate for drift scoping. `BRIEF_TERMINAL_STATUSES` includes `Completed`, `attested_completed`, and `Validated`; those briefs still owe their attested coverage, so a covering test deleted afterwards is exactly the regression drift exists to catch. Only `Abandoned`, `Withdrawn`, `Superseded`, and `archived` are exempt. The local `_RETIRED_BRIEF_STATUSES` restates four members rather than composing, so that a NEW terminal status defaults to in-scope instead of silently exempting itself; a subset assertion pins it against the upstream authority.

UNTAGGED REQs STAY IN SCOPE. 1645 of the corpus carry no ADR-0.0.59 tag. A missing tag is unknown kind, never an exemption. Inferring one would let the largest segment exempt itself and would make the metric meaningless in the opposite direction.

THE @covers DECORATOR SILENCES THE TAUTOLOGICAL AUDIT. `_calls_production_code` walks the function node, which includes `decorator_list`, so any `@covers` (a call to a gzkit-imported name) satisfies the "exercises project computation" exemption. Measured: the audit sees 73 of 290 filesystem-op plus assertion co-occurrences; 217 are masked. The masked population is precisely the one the rule targets, since a test authored to fill a REQ evidence cell carries a `@covers` by construction. This is GHI #730 and it is NOT fixed.

THE DISTRIBUTION GATE IS FILENAME-LEVEL, NOT BYTE-LEVEL. AGENTS.md describes byte-equivalence, but the static T0 audit in `src/gzkit/governance/trust_audits/distribution.py` derives surface roots as `src/gzkit/<surface>` from `data/distribution_baseline_manifest.json` and checks filename membership plus wheel include globs. The only sha256 in that module hashes the manifest file itself for a regeneration ledger event. It does not track file content or file mode. An in-session recommendation was built on the wrong reading and had to be retracted.

`.gzkit/hooks/` HAS NO STRUCTURAL GATE. Registering it under `.gzkit/manifest.json` `control_surfaces` was attempted and reverted: the distribution audit never reads that file, and `gz check-config-paths` rejects the key with "`.gzkit/hooks`: manifest.control_surfaces.gzkit_hooks should be a file". The shipped hook script currently has no gate over its content; the three unit tests are the only guard.

HARNESS NOTE, INHERITED AND CONFIRMED: the handoff-resume gate refuses compound Bash commands. `&&`, a `| head` pipe, and even `git rev-list --left-right --count origin/main...HEAD` (the triple-dot) were all refused during the claim-verification pass. Use bare commands and native flags. Note also that `uv run gz drift` is NOT in the permitted-read set, so the one claim the predecessor handoff flagged twice was the one claim the gate structurally forbade verifying before authorization.

## Decisions Made

- [operator-ruled] Investigate the `gz drift` advisory rather than defer it again (verbatim 2026-07-28: "investigate: 1. Decide whether to chase the gz drift advisory (2020 unlinked specs, 10 orphan tests). Under the ADR-0.0.59 three-kind taxonomy, SUPPORT and STRUCTURAL-FENCE REQs correctly show as unlinked, so the figure may be entirely benign — unverified either way. Precondition currently UNVERIFIABLE (finding 2)."; booked via `gz handoff authorize`, session fb99d72b).
- [operator-ruled] File one GHI for drift kind-blindness and direct-fix it, fold the REQ-retirement finding into GHI #611 rather than filing a sibling, and do the sweep of stale `@covers` citations (verbatim: "1. do it, 2. fold, 3. do sweep").
- [operator-ruled] Resolve the three unmasked tautological tests by registering the surface and widening the fence exemption, chosen from three bounded options after the first recommendation was retracted. The pure-SUPPORT route (build `gz validate --hook-integrity`) and reverting the citation removals were both declined.
- [agent-chose] Landed the drift scoping and the tautological fence in ONE commit rather than two. Splitting would have left a red intermediate commit, because removing the false citations is what exposes the three tests. Coupled-surface coherence, DO IT RIGHT rule 1a.
- [agent-chose] Scoped the sweep to one uniform rule: remove `@covers` citations naming REQs that were never declared. No brief was edited, no REQ was invented, and no attested acceptance criteria were changed.
- [agent-chose] Repointed exactly one citation (`REQ-0.22.0-04-08` to `04-03`) because the brief text matched the test verbatim. Left `TestTaskBlock` citing `04-05` where block is `04-04`, and recorded that rather than fixing it, because a full re-citation audit of ADR-0.22.0 is a different job.
- [agent-chose] Did NOT mark the eight superseded REQs as `- [x]`. That would assert the criterion was met, which is false. The honest states are met, not-yet-met, and retired; the vocabulary carries two. Folded onto #611 instead.
- [agent-chose] Reverted the `.gzkit/manifest.json` registration after verifying it was inert for the distribution gate and broke config-path coherence, rather than forcing it through to satisfy the shape of the ruling.
- [agent-chose] Restructured a test I had just written after the tautological audit flagged it. It asserted a filesystem fact directly; it now asserts on a derived list, which `.claude/rules/tests.md` § Prefer structured assertion targets independently prefers.
- [agent-chose] Closed GHI #729 despite a documented residue (in-range semantic mis-citations), per the ghi-author routing doctrine: the observation is homed in a commit, and the residue is distinct work rather than the issue unfinished.

## Immediate Next Steps

1. Rule the disposition strategy for GHI #730. This is the one blocking question left. The predicate fix is under 10 lines, but turning it on reveals 217 previously-masked tautological ops, and both `data/tautological_test_baseline.json` and `data/tautological_test_waivers.json` are registered shrink-only in `data/waiver_ratchet_registry.json`. They cannot absorb the 217, so each must be converted or deleted, and that pass has to land WITH the predicate fix rather than after it.
2. Decide whether the in-range semantic mis-citation class deserves a tracker. Drift is structurally blind to it: the REQ id resolves, so the link looks healthy. Confirmed instances exist in `tests/test_tasks.py`, which carries 219 `@covers`. No mechanical detector exists today.
3. Decide whether `.gzkit/hooks/` should get a real structural gate. It ships an executable gzkit installs and runs, and nothing currently validates its content. The three unit tests are the only guard, and they survive only because the fence exemption now names that root.
4. Review the triage census carried in the predecessor handoff and authorize which item to pull next. It was verified intact this session: 13 open GHIs, ranked, with #615 first as the only blocking-tier item. The count is now 14 open with #730 added.
5. Re-derive the four damaged Settled Rulings entries. They were flagged in the predecessor handoff and remain uncorrected; see Pending Work for the corrected line numbers.

## Pending Work / Open Loops

- GHI #730 is OPEN with only its narrow half addressed. The root defect is untouched: `_calls_production_code` still walks `decorator_list`, so 217 of 290 tautological ops remain masked. Blocked on an operator ruling for the disposition strategy.
- The in-range semantic mis-citation class has no tracker and no detector. `TestTaskBlock` in `tests/test_tasks.py` cites `REQ-0.22.0-04-05` (which is "gz task list --json") where the block criterion is `04-04`. Removing the mis-cited decorator from `TestTaskComplete` this session is why unlinked went 1417 to 1418: it exposed that `04-04` has no truthful coverage. That single-count rise is the honest number, not a regression.
- `.gzkit/hooks/` has no structural gate over its content. Documented on GHI #730.
- 1418 unlinked specs remain, dominated by 1645 untagged REQs corpus-wide. Backfilling ADR-0.0.59 tags is unowned work. The figure is now meaningful where it previously was not, so it can be triaged rather than dismissed.
- THE SETTLED-RULINGS DAMAGE IS NOW IN THIS FILE. Composition unions carried entries, so four corrupted entries propagated verbatim into this handoff. IDENTIFIED BY TEXT, NOT LINE NUMBER, deliberately: the four consecutive entries beginning "Work the triage list in its ranked order (operator verbatim 2026-07-25:" (truncated mid-quote, no closing quote, no authorization scope), then "Proceed with GHI #615 cuts 2 and 3", then "Escalation should key on lifecycle rather than on frontmatter shape", then "Dimension-aware Draft scoping: a Draft brief does NOT gate on its own" (three orphaned fragments with no attribution and no verbatim text). An intact version of the first ruling exists later in the same section. Do not read any of the four as a complete ruling. There is also a near-duplicate pair of the "Fix the gz check advisory-visibility defect" ruling that the dedup pass did not collapse.
- LINE NUMBERS ARE THE WRONG COORDINATE for a self-referential handoff, which is why the entry above uses text. The predecessor reported this same damage but cited lines 105, 106, 110, 111, 112, 113 for its own file when the damage sat at 156 through 159 and 151 through 152; a reader following its line 110 lands on a `## Verification Checklist` heading and concludes the report was wrong. This session reproduced the error before catching it: a first draft of this handoff cited lines 133 through 136, and adding two bullets to THIS section pushed the target to 135. Any edit above a citation invalidates it, so cite the entry text.
- Re-deriving the four damaged entries from their source handoffs is still unowned. The forward fix (the settled-ruling dedup defect) landed; the backfill never did, so every successor inherits them. Composition cannot repair them because it has no source to re-derive from; this needs a deliberate pass over the predecessor chain.
- Complexity-thresholds bootstrap-mode advisory persists (GHIs #404 and #405). Pre-existing, untouched.
- The surface-delivery witness reports AGENTS.md at 32208 B against the 32768 B codex delivery cap, 560 B of headroom. Advisory by design; the margin is thin and unchanged this session.
- No ADR or OBPI in flight. No locks held. No blockers.

## Verification Checklist

Commands run this session and their observed results:

- `uv run gz check` — exit 0, all gates green, run after the fix. Advisories are pre-existing: vendor-cap distance and complexity bootstrap mode.
- `uv run -m unittest -q` — Ran 7548 tests, OK. A "Smoke tier FAILED" line appears in captured output; it is a negative-control fixture, not a real failure. `uv run gz smoke` independently reports "Smoke tier PASSED within budget" (2 tests, 0.01s against a 60s budget).
- `uv run gz drift` — 1418 unlinked, 0 orphan, 3 unjustified before commit (the unjustified entries were the in-flight `src/` edits and clear once committed). Before the fix: 2020 unlinked, 10 orphan.
- Fence delta measured before landing, by monkeypatching `_asserts_shipped_executable` to return False and re-scanning: exactly 3 newly exempt, 0 newly flagged. The three are `test_hook_is_posix_shell`, `test_hook_is_executable`, and `test_no_operator_email_in_artifacts`.
- Blind-spot blast radius measured by stripping `decorator_list` before the exemption check and re-scanning: 73 ops detected with decorators walked, 290 with them excluded, 217 masked.
- `uv run gz validate --distribution` — passed, but verified NOT to cover `.gzkit/hooks/`; it reads `data/distribution_baseline_manifest.json` and walks `src/gzkit/<surface>`.
- `uv run gz check-config-paths` — failed with "`.gzkit/hooks`: manifest.control_surfaces.gzkit_hooks should be a file" when the manifest registration was attempted; passes after the revert.
- `uv run gz git-sync --apply` — pushed; ahead=0 behind=0 against origin/main afterwards.

To re-verify current state: run `uv run gz check` and confirm exit 0, then `git status --short` and confirm a clean tree.

## Evidence / Artifacts

Source changed this session:

- `src/gzkit/triangle.py` — `covers_channel_reqs`, `_RETIRED_BRIEF_STATUSES`, `_is_reserved_fixture_req`, `brief_status` on `ReqEntity`, `covers_channel_req_ids` on `SourceSubgraphView`, and the generalized `_parse_frontmatter_field`
- `src/gzkit/commands/drift.py` — `tests/fixtures/` exclusion in `scan_covers_references`
- `src/gzkit/tautological_tests.py` — `_asserts_shipped_executable` and `_SHIPPED_EXECUTABLE_ROOTS`

Tests added:

- `tests/governance/test_drift_proof_channel_scope.py` — 16 tests pinning the scoping rule, the retired-vs-sealed distinction, the reserved namespace, and the orphan-regression guard
- `tests/governance/test_shipped_executable_fence.py` — 7 tests, including three negative controls that pin the exemption narrow

Tests swept:

- `tests/test_tasks.py`
- `tests/governance/test_security_surfaces_registry.py`
- `tests/hooks/test_complexity_advisor_auto_chain.py`
- `tests/governance/test_closeout_proof_view.py`
- `tests/test_ontology_source.py`

Governance records:

- `.gzkit/ledger.jsonl` — handoff authorization for session fb99d72b
- Commit `9db71b6ff` on origin/main
- GHI #729 filed and closed `completed`, comment 5103204654
- GHI #730 filed, OPEN, comment 5103207730
- GHI #611 comment 5102934978 (the REQ-retirement fold)

## Settled Rulings

- Work the degrading tier starting with #696 (verbatim authorization booked via gz handoff authorize, session 81765765).
- Finish what is on the plate rather than deferring items for later sequencing rulings.
- Do not assert campaign-movement intent without reading it; the claim that Movement C is shrinking the pre-1.0 board was fabricated and is withdrawn. Movement C is Reduce the accretion.
- #696 defect 2 was the buildable cut; defects 3/4 were NOT to be left to an unbuilt ADR.
- Reframe #580 from periphery criticality to truncation survival (operator verbatim 2026-07-25: 'reframe #580 to truncation survival'). The mechanism is unchanged; the warrant and ranking source are replaced. Arrived AFTER the prior handoff was written and was carried by neither its Decisions nor its Settled section.
- #580's survival declaration is ratified with must-survive = ranks 1-11 (operator-doctrine-verbatim-canon first, architectural-boundaries last), cumulative 21582 B, leaving 11186 B of growth headroom. Ranks 12-20 are declared expendable-under-pressure because they are recoverable, not because they are unimportant. Ratified as data only: applying the order to committed AGENTS.md remains a Layer-1 canon change requiring Gate-5 attestation.
- #580's destination is SPLIT, not a single home. The witness half (declaration plus the assertion that every must-survive section begins before the vendor cap, plus fail-closed declaration completeness) lands with GHI #712. The reorder half (permuting the surface) parks to pool post-1.0, because only it is expensive and it pays off only once the cap binds. This supersedes the withdrawn whole-issue pool recommendation, which rested on a false claim about Movement C.
- GHI #607 is UNPARKED. Attested REQ-0.14.0-04-04 asserts a detection capability and is silent on scope, so an adopter-scope predicate that preserves gzkit's own self-enforcement does not falsify it. No repudiation and no amendment are required to work the issue.
- Work advised steps 1 through 4 (verbatim authorization "do 1 to 4", booked via gz handoff authorize, session 8b138d99).
- Mechanize GHI-blocker freshness by extending the bundled triage script rather than adding a gz verb, so the signal lands in the report the operator already reads before pulling work.
- Work GHI #712 (operator verbatim 2026-07-25: 'authorized, proceed with GHI #712'; booked via gz handoff authorize, session bb837938). This authorized the resumed handoff's advised step 1 only; steps 2 through 5 were not authorized and were not worked.
- Fix the gz check advisory-visibility defect, and file it as a GHI first (operator verbatim 2026-07-25: 'yes, fix this defect'). The defect was surfaced for routing rather than fixed unilaterally because it changes a shared renderer's output contract for every step; the operator's ruling converted it into authorized work.
- Fix the gz check advisory-visibility defect, and file it as a GHI first (operator verbatim 2026-07-25: 'yes, fix this defect'). It had been surfaced for routing rather than fixed unilaterally because it changes a shared renderer's output contract for every step.
- Fix the settled-ruling dedup defect, then author a fresh handoff (operator verbatim 2026-07-25: 'fix, then write me a fresh handoff'). It had been surfaced with routing facts rather than fixed, because 'write handoff' is a narrow skill scope and Always #17 forbids launching unrequested implementation work off the back of one.
- Fix the CI failure (operator verbatim 2026-07-25: "fix this:"; booked via gz handoff authorize, session bd43ecd7). This authorized the CI repair only; the resumed handoff's five advised steps were not authorized and were not worked.
- Write the entire triage into a new handoff for context cleanup (operator verbatim 2026-07-25: "write entire triage to new handoff, i want to clean up").
- Work the triage list in its ranked order (operator verbatim 2026-07-25:
- Proceed with GHI #615 cuts 2 and 3 (migration plus strict enforcement)
- Escalation should key on lifecycle rather than on frontmatter shape
- Dimension-aware Draft scoping: a Draft brief does NOT gate on its own
- Book the patch release as the session's work and leave the resumed handoff's five advised steps unauthorized (operator verbatim 2026-07-25: "/gz-patch-release"; booked via gz handoff authorize, session e6b3da00). GHI #615's held migration was NOT authorized and was not worked.
- Backfill the runtime label on #532 and #682 only, not on #533 or #710 (Step 1a labeling-recovery). Both landed genuine validator changes under gz validate; #533 is an open tracker with markdown-only commits and #710 was a skill-doc change, so the excluded bucket is correct for them per Step 1a's own guidance.
- Describe only what actually landed for the open GHIs in the narrative, omit #533 entirely, and file a GHI against the closure-marker heuristic after the release completed rather than pausing the ceremony.
- Approve the drafted release notes as written (operator verbatim: "yes"), triggering the Iron Law run of Steps 4a-4e without pauses.
- Fix GHI #714 via Direction 2 -- keep the commit marker authoritative for discovery, consult upstream state one layer down, and downgrade a still-OPEN GHI to a warned bucket the operator adjudicates (operator verbatim: "direction 2"). Directions 1 and 3 were declined.
- Deferring a proven defect with a governance-flavored rationale is not acceptable (operator verbatim 2026-07-25: "slop, bullshit, facade, and wank"). The turn-closing "one thing worth your judgment" note on the git-sync gate gap was rejected as rationalized incompleteness; the correction produced the hook-enforcement investigation, its two commits, and GHI #715. Recorded as an improvement insight per Behavior Rule 11.
- Work GHI #715 and correct campaign line 131 (operator verbatim 2026-07-25: "#715 + campaign line 131"; booked via `gz handoff authorize`, session e4c56baa). This authorized the resumed handoff's advised steps 1 and 2 only; steps 3, 4, and 5 were not authorized at that point.
- Route GHI #615's residual findings by mechanical re-triage into three classes, file a GHI for the scenario-reachability advisory, and confirm the brief_reconcile landing order (operator verbatim 2026-07-25: "Mechanical re-triage into 3 classes; File a GHI; #615 -> #581 -> #641"; booked via `gz handoff authorize`). Routes (i), (ii), and (iii) were declined; building the scenario registry now and accepting Era-1 as permanent were declined; landing #641 first was declined.
- Book the patch release as this session's work and leave the resumed handoff's five advised steps unauthorized (operator verbatim 2026-07-25: "/gz-patch-release"; booked via `gz handoff authorize`, session bfc3ccad). GHI #716, #615 cuts 2 and 3, #581, and #641 were NOT authorized and were not worked.
- Fix the CI failure, diagnosed by the operator from the job log as blocking skill-audit staleness rather than a code runtime defect (operator verbatim 2026-07-25: "fix:"). This authorized the skill-audit repair only.
- Approve the v0.33.3 release narrative as drafted and execute it (operator verbatim 2026-07-25: "yes, appprove the patch release narrative - do the work"), triggering the Iron Law run of Steps 4a through 4e without pauses.
- Decline the near-edge staleness sweep and record it in a handoff instead (operator verbatim 2026-07-25: "no, but place it into a handoff and then git-sync the handoff").
- Authorize the git-sync only, before any handoff steps were worked (operator verbatim 2026-07-25: "authorized, git-sync only"; booked via `gz handoff authorize`, session a76662eb). The stale-pinned handoff's five advised steps were NOT authorized at that point and were not worked.
- Work advised steps 1 through 5 of the current handoff (operator verbatim 2026-07-25: "do these:" followed by the five steps; booked via `gz handoff authorize`). Steps 1 through 3 were completed; 4 and 5 were not started.
- Resolve the skill-version pin collision by asserting the increment rather than the literal, chosen over updating the four frozen constants and over reverting the stamps. The equality pins contradicted REQ-0.0.35-02-04's own wording.
- Add a fixed 75-day non-blocking warn band, chosen over deriving the band from the ceiling and over leaving the gate binary.
- Retire ADR-0.0.33 Invariant 4 rather than build the scenario registry; GHI #716 closed withdrawn against the retirement commit.
- Fix the handoff evidence check's category error when the pre-push gate blocked the retirement, chosen over annotating the two sealed handoffs and over reverting the retirement.
- Work all four authorized buckets (operator verbatim 2026-07-26, booked via `gz handoff authorize`, session 7dd80db9): "GHI #615 cuts 2 and 3, Then #581, then #641, Steps 3 and 4 (the two cheap judgments), Fix the two handoff-surface defects".
- Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written, and over landing the extractor fixes as a separate prior commit.
- Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — an honest claim that they are no longer a live authoring surface, without asserting a ledger completion they do not carry.
- Scope GHI #581 first and do NOT build — chosen over executing the 6-registry collapse, over building the 6th validator dimension, and over closing the issue unexamined.
- Take GHI #641's own strawman naming: `gz brief reconcile` becomes `gz obpi brief-drift`, `gz obpi reconcile` becomes `gz obpi sync`, and the single-verb `brief` namespace goes away.
- Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written.
- Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — no ledger completion is asserted.
- Scope GHI #581 first and do NOT build — chosen over executing the collapse, over building the 6th validator dimension, and over closing it unexamined.
- Take GHI #641's own strawman naming, then execute it (operator verbatim 2026-07-26: "refresh it" followed the landing; the rename itself was authorized by the strawman ruling and the follow-up "okay, so what about 641?").
- Work GHI buckets 1, 3, 4, and 5; decline bucket 2 (the Movement A campaign work).
- Retire .gzkit/schemas/ledger_events.json by forward supersession and keep the file.
- Write two pool ADRs (substrate + capability) crediting swarm-forge + superpowers (verbatim: "authorized -- write the two pool ADRs"; booked via gz handoff authorize, session 786a9e8f).
- Primary use case = parallel read-only review personas; parallelism itself "isn't too important"; record the alternatives (parallel OBPI impl / GHI fixes / ADR pipelines) as future scope.
- Allow ephemeral worktrees (scratch checkouts, land on main, no branch dance) -- a carve-out from "never create feature branches"; ratifying it is a hard promotion gate for ADR-pool.worktree-parallel-agents.
- Ledger concurrency = single-writer-by-construction (only merge-to-main writes Layer-2), NOT a daemon.
- Two pool ADRs (substrate + capability), not one combined nor three.
- Use the governed skill, not hand-scaffolding ("there is an adr authoring skill don't vibe"; "use skills - skills have rules + tools"). Recorded as an improvement insight.
- Fix GHI #718 via direction (a), the skill-doc fix (chosen via AskUserQuestion).
- File the #718 follow-on via /ghi-author (became GHI #719).
- A git-sync is ALWAYS authorized and never gated on a handoff (operator verbatim 2026-07-26: "yes, just do my git-sync - a git-sync will ALWAYS be authorized - think about it, if we need to sync with remote, your local handoff is almost always likely to have been superseded by something on remote. Challenging me on a handoff for a git-sync is silly."). Booked via `gz handoff authorize` against both the gating handoff and, after the pull replaced it, its successor. Borne out mechanically in-session: the 24 pulled commits had already landed all five advised steps of the handoff being gated on.
- Add the local `user.name = g0` guard (operator verbatim 2026-07-26: "yes, do the user.name = g0 guard.").
- Fix GHI #720 with the recompute approach rather than reordering the ceremony to pull before committing (operator verbatim 2026-07-26: "fix #720 with the recompute").
- Fix GHI #722 by failing closed at authoring rather than widening the parser (operator verbatim 2026-07-26: "fix #722 by failing closed at authoring"). Direction (a), widening `_section_items`, was declined.
- Write this successor handoff rather than leave the stale claim standing (operator verbatim 2026-07-26: "yes, write the successor handoff").
- Fix GHI #723 with the buffer flag (operator verbatim 2026-07-26: "fix #723 with the buffer flag").
- File the smoke-budget breach as a GHI (operator verbatim 2026-07-26: "file the smoke budget GHI"), which became #724.
- Write this successor handoff (operator verbatim 2026-07-26: "write the successor handoff").
- Sync first, then re-present, before working any advised step (verbatim 2026-07-27: "Sync first, then re-present"; booked via `gz handoff authorize`).
- Comment the measured blast radius on #717 and file the two genuinely untracked findings, after Step-0 prior art voided the originally-recommended GHI (verbatim: "Comment on #717 + file the two trackers").
- Fix GHI #724, #725 and #726 (verbatim: "fix 724, 725, and 726").
- Directions, chosen from bounded options: #724 direction (a) build the smoke tier; #725 direction (4) fail-closed assertion; #726 direction (b) silence at the fixtures.
- Discharge the three items left undone rather than narrating them (verbatim: "fix:" quoting the turn-closing deferral paragraph). Recorded as an improvement insight per Behavior Rule 11.
- Work the triage list in its ranked order (operator verbatim 2026-07-25: "continue on the triage list"; booked via `gz handoff authorize`, session 6aa88bcf). This resolved the predecessor handoff's advised step 1 by ruling the pull order to be the ranking already recorded in `.gzkit/cache/triage/rank.json`, which puts GHI #615 first.
- Proceed with GHI #615 cuts 2 and 3 (migration plus strict enforcement) rather than sampling first or switching to GHI #607.
- Escalation should key on lifecycle rather than on frontmatter shape (operator selected the recommended option after the three dispositions were presented). Implementation is preserved but not landed, because measurement afterwards showed it does not by itself reach a green gate.
- Dimension-aware Draft scoping: a Draft brief does NOT gate on its own deliverables (allowlist existence, `gz` verb resolution) but DOES still gate on prerequisites (Discovery Checklist, citations). Landed as 5111b7dd.
- Seat the four recovered rulings via `--settled` on the next handoff, chosen from four presented routes (verbatim: selection of "Seat via --settled next handoff"). Filing a GHI first, direct repair of the committed artifact, and review-only were all declined.
- Run the git-sync (verbatim: "/git-sync"; booked via `gz handoff authorize`, session f2ee5b4e). A git-sync is always authorized per standing canon; no other advised step of the resumed handoff was authorized, and none was worked.
- Test-suite at-scale scope routes as parallelize `gz test` plus the subTest sweep (operator ruling 2026-07-27, chosen from three bounded options). The parallelism half was ALREADY SHIPPED in `baeb1f72e` and needed no work. GHI #512's Option B stays declined on measurement and was not re-litigated. GHI #644 closed `superseded` against `baeb1f72e` plus the project-local chore `test-consolidation-subtest-sweep` registered in `cac0917d8`.
- ARB receipt retention takes the mirror-`gz handoff archive` shape: `gz arb archive --older-than <N>d`, move-not-delete, with a dry-run and a harvest-before-archive guard so `advise`/`patterns` intelligence is never dropped unharvested (operator ruling 2026-07-27). A unified ARB-plus-handoff retention doctrine, purge-only-with-a-window, and won't-fix were all declined. GHI #594 stays OPEN with the direction booked: a new CLI verb is a contract change and this is not defect repair, so the GHI-direct-fix override does not apply and it needs an ADR home.
- Rules get a staleness clock, built with the honest backfill: `last_reviewed` added to `RuleFrontmatter`, each rule stamped with its last substantive commit date rather than today's, advisory first and fail-closed once the stale set clears (operator ruling 2026-07-27). Today's-date-plus-immediate-gating, attest-re-read-on-edit, and won't-fix were declined. GHI #691 stays OPEN with the direction booked: `RuleFrontmatter` is a schema/runtime contract and this is not defect repair, so it needs an ADR home.
- A registered chore counts as a valid `ghi-close` landing site (operator ruling 2026-07-27), widening that skill's enumerated list of commit SHA / registered ADR id / registered OBPI brief id / higher-numbered GHI. A chore satisfies the doctrine's principle -- a real artifact, discoverable via `gz chores list`, with its own acceptance criteria and run/audit lifecycle -- but was not named in the list. The widening is recorded in the GHI #644 close comment rather than applied silently.
- Clear the deck via the rulings lane rather than by implementing (verbatim: selection of "Rule the 3 decision-only trackers"). The two bounded-build options and the combined lane were declined.
- Author the consolidation chore in-session and then close, rather than naming it in the close comment or leaving the tracker open (verbatim: selection of "Author the chore, then close"). This corrected an earlier selection of mine that would have dead-lettered the scope.
- Write the entire triage into a handoff for context cleanup (verbatim 2026-07-28: "write the triage to handoff"). This mirrors the standing ruling of 2026-07-25, "write entire triage to new handoff, i want to clean up".
- Discuss the adopter Pydantic leak as this segment's subject (verbatim: "discuss this issue:" quoting the claim that it is unparked, bounded, defect repair, and the cheapest real close left).
- `models.md` text is fine and must not be rewritten; fix the mechanization and the export only (verbatim 2026-07-28: "the text is fine, fix the mechanization and the export"). A prior plan to re-scope the doctrine wording was withdrawn.
- STDLIB-FIRST is gzkit's constraint and a principle, not a bright line (verbatim: "STDLIB first != STDLIB only, I am getting tired of tripping up on this" and "STDLIB FIRST is gzkit's constraint and it is a principle").
- Take the #607 fix now and file the architecture work as its own GHI (verbatim: "take the #607 deletion now and file the architecture work as its own GHI"). The deletion half was substituted for scoping after the attested-REQ binding was found; the operator confirmed the substitution (verbatim: "yes, confirm").
- Keep campaign sequencing as is (verbatim: "keep sequencing as is"). Movement A remains topmost; Movement B (airlock on the real doors) is NOT pulled forward despite the airlock findings. This is a live ruling against acting on the investigation.
- Direct-fix the airlock mis-citation (verbatim: "yes, direct fix mis-citation"). No GHI filed -- filing one to construct a trailer anchor is the moratorium violation named in `.gzkit/rules/task-discovery.md`.
- Correct the chore's false text and file the gap behind it (verbatim: selection of "Correct the text, file the gap"). Building the affordance now, deleting the chore, and letting it ship uncorrected were all declined.
- Reconcile the budget `_doc` against the enforced value and restore the gate rather than doing a documentation-only fix (verbatim: "reconcile the budget _doc against the enforced 50000").
- Relax limits until gzkit is stable; the retune is reverted and budgets stay at 50000, 15000, 30000 (verbatim: "until we get gzkit stable, I want to relax limits. the cms system is meant to control this, but we don't have gzkit feature stable enough to be strict").
- Add the capture-channel evidence as a comment on GHI #727 extending its scope, rather than filing a fifth sibling in the 607, 669, 691, 727 family.
- File through the ghi-author skill and push both commits via `gz git-sync`.
