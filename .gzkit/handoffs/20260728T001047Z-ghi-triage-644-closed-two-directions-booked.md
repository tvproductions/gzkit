---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-28T00:10:47Z'
agent: claude-code
session_id: f2ee5b4e-8f77-4953-859a-f86517090abf
continues_from: .gzkit/handoffs/20260727T234748Z-handoff-review-shattered-rulings-reseated.md
---

## Current State Summary

Triage session following the handoff review. Operator asked to clear the GHI
deck; `ghi-triage` ran end-to-end and 12 of 13 open issues were ranked.

Net: the deck went 13 -> 12. GHI #644 closed `superseded`. GHI #594 and #691 have booked
directions recorded as issue comments and stay open. One chore was authored and registered.

The load-bearing finding is a correction, not a closure. GHI #644's blocker asked how far
to extend test parallelism; re-deriving it against the tree showed `run_tests` has invoked
`unittest-parallel` since `baeb1f72e`, and CI runs `uv run gz check` which calls it. Two of
the five rows in that issue's "Verified current state (2026-06-25)" table were stale. The
operator ruled on a premise I had relayed from the issue body without checking the code.

## Important Context

FIRST, the reusable lesson, and it is the same one twice in one session: a
GHI body carries MEASURED STATE WITH A TIMESTAMP, and that measurement rots exactly like a
handoff claim does. The Claim Verification Gate I applied rigorously to the handoff earlier
in this session, I skipped on the GHI body. `ghi-triage` mandates reading bodies but has no
gate requiring re-verification of their measurements -- a real asymmetry between it and
`gz-session-handoff`, whose Claim Verification Gate exists precisely for this.

SECOND, a skill correctly refused an operator instruction, and that is the system working.
The option I drafted and the operator selected was "close the tracker, name the chore in the
close comment" -- which is the dead-letter signature `ghi-close` forbids by name. That skill
also anticipates the operator's voice: "Even if the operator says close this and we'll
handle it later, the skill's response is to surface that later needs a destination." The
resolution was to author the chore in-session so the close cited a real artifact. My option
framing was the defect; the doctrine caught it.

THIRD, the chore is PROJECT-LOCAL ON PURPOSE. It is not authored into `src/gzkit/chores/`
and so never ships in the wheel, because it encodes gzkit's own test hygiene rather than
portable adopter governance. Shipping it would repeat the adopter-boundary leak GHI #607
names. `uv run gz validate --distribution` exits 0 with the chore project-local, so wheel
parity is unaffected -- verified, not assumed.

FOURTH, two near-misses on surgical discipline while editing `registry.json`, both caught by
reading the diff rather than trusting the write. The registry is NOT alphabetically ordered;
sorting it produced a 138-insertion/130-deletion reorder of 36 untouched entries. Reverted
to append-only. Then `ensure_ascii=False` un-escaped `\u2014` in four other entries; the
file's convention is escaped, so the default was correct. Final diff is 8 insertions, 0
deletions. Read the diff after any programmatic edit of a shared registry.

FIFTH, the triage script routes EVERYTHING to `direct-fix` because the 60-day `fix(`
precedent is 313 commits, far past the threshold of 3. That is the mechanical answer, not
the final one -- it cannot see that some issues are pool-ADR-shaped. Read `route` as "the
thresholds do not block you", never as "this is a small change".

SIXTH, the blocker-freshness instrument earned its keep but needs adjudication, exactly as
its own skill warns. Several blockers cite issues that have since closed. GHI #594's cited
precondition genuinely cleared; the excluded GHI #533 carries the same stale flag but is
still truly gated on ADR-0.35.0 corpus work sitting at 0/9. Same signal, opposite verdicts.

## Decisions Made

- [operator-ruled] Clear the deck via the rulings lane rather than by
  implementing (verbatim: selection of "Rule the 3 decision-only trackers"). The two
  bounded-build options and the combined lane were declined.
- [operator-ruled] Author the consolidation chore in-session and then close, rather than
  naming it in the close comment or leaving the tracker open (verbatim: selection of
  "Author the chore, then close"). This corrected an earlier selection of mine that would
  have dead-lettered the scope.
- [agent-chose] Surfaced the stale-premise correction BEFORE closing anything, rather than
  proceeding on the ruling as given. The operator had ruled on a table that was two rows
  wrong, and acting on it would have produced a close comment asserting work that was
  already shipped.
- [agent-chose] Pushed back on my own option framing once `ghi-close` was loaded, instead
  of executing the selected option. The distinction between the two options I had offered
  was precisely the line the dead-letter doctrine draws, and I had put the unlawful one
  first and marked it recommended.
- [agent-chose] Excluded GHI #533 from the ranking entirely. Its stale-blocker flag fires,
  but its real gate is ADR-0.0.37 completion plus registry-projection migration, which is
  `ADR-0.35.0` at 0/9. Ranking it would have recommended work that cannot start.
- [agent-chose] Re-measured the chore's baseline at authoring rather than inheriting the
  tracker's figures: 78 of 497 test files use `subTest` (15.7%) against the recorded 59/449
  (13.1%). Both numerator and denominator had moved. Given the session's central finding,
  copying the stale numbers into the chore would have propagated the same defect one layer
  down.
- [agent-chose] Recorded the booked directions as comments on the two issues that stay
  open, not only in this handoff. A direction living solely in a handoff is discoverable
  only by someone already reading the chain; the work will be picked up from the issue.

## Immediate Next Steps

1. NOTHING BEYOND THIS SESSION'S WORK IS AUTHORIZED. The close, the chore,
   the two issue comments and this handoff are done; every step below needs an explicit
   operator ruling first.
2. The two booked-but-unhomed directions need an ADR home before they can be built:
   ARB retention (mirror `gz handoff archive`) and the rules staleness clock. Neither is
   defect repair, so the GHI-direct-fix override does not reach them and canon forbids a
   headless OBPI. One ADR could plausibly carry both, since both are governance-surface
   lifecycle capabilities.
3. The top-ranked open issue is the adopter-boundary Pydantic leak, unparked by settled
   ruling and still unworked. It is a real shipped defect breaking adopters' `gz validate`,
   it is bounded, and it is defect repair -- so it routes to direct fix with no ADR needed.
4. The consolidation chore is registered but has never been run. First run should re-measure
   the baseline before editing anything.
5. Consider whether `ghi-triage` should carry a measurement-freshness gate mirroring
   `gz-session-handoff`'s Claim Verification Gate. This session's central finding was a
   stale measurement inside a GHI body that the triage protocol had no reason to re-check.

## Pending Work / Open Loops

12 GHIs open, down from 13. GHI #644 closed `superseded`.

TWO ISSUES CARRY BOOKED DIRECTIONS AND NO HOME. GHI #594 and #691 both have settled
directions recorded as issue comments and both need an ADR before an OBPI can carry them.
Neither direction should be re-adjudicated; only the home is missing.

THE NEW CHORE HAS NEVER BEEN RUN. `test-consolidation-subtest-sweep` is registered and
resolves as `project`, with two acceptance criteria, but `proofs/` is empty.

GHI #719 OPEN and unworked -- the carried direction-(b) capability from #718.

A DESTINATION-LIST WIDENING IS NOW IN EFFECT: a registered chore counts as a `ghi-close`
landing site. It is recorded in the #644 close comment and seated in this handoff's Settled
Rulings, but `ghi-close` SKILL.md itself still enumerates the narrower list. Reconciling the
skill text to the ruling is unwritten work.

NO OBPI LOCK HELD, no in-flight pipeline. No source or test file was modified this session.

## Verification Checklist

git status --short --branch (clean, level with origin/main);
gh issue view 644 --json state (expect CLOSED);
gh issue list --state open --json number (expect 12);
gh issue view 594 --json comments and 691 (expect the booked-direction comment on each);
uv run gz chores list --explain (expect test-consolidation-subtest-sweep, lite, 2 criteria,
source `project`);
uv run gz validate --chores-layout (expect exit 0);
uv run gz validate --distribution (expect exit 0 -- the project-local chore must not break
wheel parity);
uv run gz chores show test-consolidation-subtest-sweep (expect exit 0).

To confirm the session's central correction rather than trusting this document, read
`src/gzkit/quality.py` at `run_tests` and observe it invokes `unittest-parallel`. GHI #644's
body asserts that path is serial. The body is the stale one.

Do NOT pipe these verifiers through tail or grep: the shell reports the filter's exit, not
the verifier's (`.gzkit/rules/tests.md` § Verification exit-code integrity). Capture to a
file and read the file.

## Evidence / Artifacts

Session commit: `cac0917d8` (chore authored and registered).

The already-shipped commit the correction turns on: `baeb1f72e`.

Chore authored this session:
`.gzkit/chores/test-consolidation-subtest-sweep/CHORE.md`,
`.gzkit/chores/test-consolidation-subtest-sweep/acceptance.json`,
`.gzkit/chores/test-consolidation-subtest-sweep/README.md`,
and an empty proofs directory alongside them.

Registry entry appended (8 insertions, 0 deletions):
`.gzkit/chores/registry.json`.

The surface whose docstring disproved the tracker's premise: `src/gzkit/quality.py`.

Triage rank input for this run: `.gzkit/cache/triage/rank.json`.

Predecessor handoff:
`.gzkit/handoffs/20260727T234748Z-handoff-review-shattered-rulings-reseated.md`.

Issue comments recording the two booked directions: GHI #594 and GHI #691.

No source or test files were modified this session.

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
