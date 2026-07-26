---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T19:37:32Z'
agent: claude-code
session_id: 5eed8cd8-58a7-48c0-9d4b-0280c2ebecd4
continues_from: .gzkit/handoffs/20260726T165354Z-ghi-722-fixed-three-defects-closed.md
---

## Current State Summary

Supersedes `20260726T165354Z`, which listed the log-legibility ruling as an open
next step. That ruling was given and discharged: GHI #723 is fixed, closed, and
CI-green at `2d3f2dd5`. HEAD at `2d3f2dd5`, tree clean and level with origin.

Four defects filed, fixed, closed, and CI-verified in one session — #720, #721,
#722, #723 — none of them planned. Every one was surfaced by the ritual that
preceded it. A fifth, GHI #724, is filed and OPEN as a ruling for the operator.

Six consecutive green CI runs (`d9224500`, `2a0652b6`, `3fa20990`, `fa51920b`,
`5e11ac7a`, `2d3f2dd5`) where the session opened on a five-run red streak. No
active OBPI lock, no in-flight pipeline, 14 open GHIs.

## Important Context

FIRST, correcting the record this handoff supersedes: the predecessor's advised
step 2 was *"Rule the negative-path log-legibility finding: file a GHI, or accept
it as known noise."* The operator ruled, the GHI was filed as #723, and it is
fixed and closed. Steps 3 and 4 (the `g0` guard, the carried chain) remain
accurate and unworked.

SECOND, and the single most useful number produced this session: **the parallel
test runner no longer fits the 60s budget either.** Measured on this tree, 32
processes, `Ran 7499 tests in 71.431s`. This is what settles the recurring
"should we just run unittest-parallel everywhere" question — it is not a runner
problem. GHI #512's Option B (replacing `CANONICAL_STEP_COMMANDS`) would pay a
foundation-attested STDLIB-FIRST departure plus a dated receipt cutover, and land
STILL non-compliant. Anyone reopening that question should read #724 before
spending time on it.

THIRD, GHI #723's fix does NOT match the remedy #723 itself proposed, and the
issue says so. The GHI proposed changing `CANONICAL_STEP_COMMANDS`; reading the
runner showed `gz check` never invokes it — it runs `unittest-parallel`, a
different runner. Buffering the locked contract would have fixed nothing while
retroactively marking ~1875 receipts `non-canonical provenance`. The fix landed
on the two sites that execute: `run_tests` in `quality.py` and the `unittest`
pre-commit hook. The GHI's Scope hint was written from AGENTS.md rather than from
the code — the same read-the-doc-not-the-surface error this session punished
three times.

FOURTH, why the log noise appears when it does, which is not obvious: `gz check`
dumps the test tier's captured output only when the tier FAILS. So the 26
error-shaped lines arrive precisely when someone is reading the log to triage. A
passing `gz check` shows none of it, which is why the defect survived so long —
it is invisible except in the moment it does maximum damage.

FIFTH, unchanged and still unruled: the `g0` authorship guard is PER-CLONE and
PII-adjacent. Global git config still holds the operator's personal email; only
the local override keeps it out of commits. Detail in the predecessor chain.

SIXTH, the four defects fixed this session share one shape worth more than the
four fixes: a predicate evaluated against state that something else had already
changed or discarded. #721 read the filesystem, mutated by whichever repos sit
beside gzkit. #720 read ahead/behind, mutated by the ceremony's own commit. #722
read a section the parser had already discarded. #723 is the reason the other
three were hard to see — the verification surface could not distinguish an
exercised guardrail from a broken one.

## Decisions Made

- [operator-ruled] Fix GHI #723 with the buffer flag (operator verbatim
  2026-07-26: "fix #723 with the buffer flag").
- [operator-ruled] File the smoke-budget breach as a GHI (operator verbatim
  2026-07-26: "file the smoke budget GHI"), which became #724.
- [operator-ruled] Write this successor handoff (operator verbatim 2026-07-26:
  "write the successor handoff").
- [agent-chose] Did NOT change `CANONICAL_STEP_COMMANDS` under #723, contradicting
  that GHI's own Scope hint, and recorded the contradiction on the issue rather
  than quietly diverging. `gz check` never runs the canonical command; changing it
  fixes nothing and invalidates ~1875 receipts.
- [agent-chose] Recommended AGAINST unifying on `unittest-parallel` when the
  operator raised it, then measured the parallel run (71.4s) rather than leaving
  the recommendation as a preference. The operator did not explicitly rule on
  Option B; they directed the smoke-budget GHI instead, so Option B remains
  formally open and is documented in #724 rather than treated as decided.
- [agent-chose] Left `runtime` OFF #724's labels despite the predicate arguably
  firing. Its resolution may be rule-text only (direction b), and labeling a
  ruling-shaped issue `runtime` before the direction is chosen pollutes the
  patch-release narrative. Whoever takes direction (a) adds it via the
  patch-release Step 1a labeling-recovery. Noted because #723 was UNDER-labeled
  earlier the same day and had to be corrected — the asymmetry is deliberate.
- [agent-chose] Verified `--buffer` against a deliberately FAILING test before
  adopting it. The first probe appeared to show failures being suppressed, which
  would have killed the approach; the fault was the fixture (temp test package
  missing `__init__.py`, discovery crashed, both counts read 0 for the same bogus
  reason). A remedy that quiets real failures would be worse than the noise.
- [agent-chose] Treated GHI #512 and #444 as three independent sightings of one
  class rather than as closed history, and cross-linked both. Neither was wrong to
  defer; the compounding of honest deferrals is the finding.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. This session's work is closed and CI-verified; every
   step below requires an explicit operator ruling.
2. Rule GHI #724 (smoke budget): define the smoke tier the 60s ceiling was
   written for (Heavy lane — new CLI verb plus a membership convention), or amend
   `.gzkit/rules/tests.md` to say what the number governs. Do NOT route it as a
   runner change; the parallel runner measures 71.4s and is also non-compliant.
3. Rule the `g0` guard's durability: leave it per-clone, change the global config,
   or add a `gz init` step that writes the local guard. Global config still holds
   the operator's personal email, and the PII rule treats a leak as needing a
   filter-repo rewrite to recover.
4. The carried chain is UNWORKED and still live: GHI #719 (pool interview JSON
   unschema'd, direction (b)); campaign Movement A remains topmost absent a ruling
   (ADR-0.35.0-canon-entry-corpus-landing at 0/9 and the
   ADR-0.34.0-foundation-sunset capstone at 2/5, including wiring the permanent
   `--taxonomy` gate into `gz check`, currently red with 74 foundation grandfather
   errors); promotion of the two pool ADRs when wanted, with the
   ephemeral-worktree doctrine carve-out ratified FIRST for
   ADR-pool.worktree-parallel-agents.

## Pending Work / Open Loops

GHI #724 IS OPEN as a ruling, not as work. It carries both directions with
tradeoffs and the measurements that rule out the runner-change path.

GHI #512's OPTION B REMAINS FORMALLY OPEN. The operator raised it and did not
rule; the measurement makes it unattractive but nobody has closed it. If it is
ever taken, it needs a foundation-attested STDLIB-FIRST departure rationale AND a
dated cutover, because `_check_step_command` compares every receipt's recorded
command against the current constant.

THE BEHAVE TIER STILL HAS THE NOISE #723 FIXED FOR unittest. `--buffer` is a
unittest-family flag. The PRIOR session's misdiagnosis
(`OBPI-unwaivered-pre-cutoff-01`) lives on the behave side and is untouched.
Named in #723's closing comment; no tracker of its own.

THE `g0` GUARD IS PER-CLONE. Fixed for this working copy only.

CARRIED, all unworked: GHI #719; campaign Movement A (ADR-0.35.0 at 0/9,
ADR-0.34.0 at 2/5); promotion of ADR-pool.worktree-parallel-agents and
ADR-pool.ledger-concurrency-substrate.

14 GHIs open. #581 remains OPEN against
`src/gzkit/governance/brief_reconcile.py`, which this session modified under
#721 — re-read before assuming the earlier contention shape holds.

SPEC-TEST DRIFT ADVISORY stands at 2031 findings. Advisory only.

## Verification Checklist

`git log --oneline -6` (expect `2d3f2dd5`, `5e11ac7a`, `fa51920b`, `3fa20990`,
`2a0652b6`, `d9224500`);
`git status --short --branch` (expect a clean tree level with origin/main);
`git log -1 --format=%an` (expect `g0`);
`gh issue view 720 --json state`, `721`, `722`, `723` (expect CLOSED for all four);
`gh issue view 724 --json state` (expect OPEN — the ruling);
`gh run list --workflow=CI --limit 6` (expect six consecutive successes);
`uv run gz check` (expect exit 0, all 43 steps, with the pre-existing
spec-test-drift and complexity advisories);
`uv run gz obpi lock list` (expect no active locks).

To re-confirm #724's central measurement rather than trusting this document:
`uv run --with unittest-parallel unittest-parallel -t . -s tests --buffer`
should report roughly 71s and well over 7000 tests. If it comes in under 60s,
the budget question has changed shape and #724 should be re-read before acting.

To confirm #723's fix is live, run the unit tier and grep for
`Fidelity validation failed` — a PASSING run must emit none. The prose still
exists and still fires; it is replayed only for tests that fail.

## Evidence / Artifacts

Session commits: `02ed4e83` (git-sync governance sweep), `d9224500` (GHI #721),
`2a0652b6` (GHI #720), `3fa20990` (handoff), `fa51920b` (GHI #722), `5e11ac7a`
(successor handoff), `2d3f2dd5` (GHI #723).

GHI #723 surfaces: `src/gzkit/quality.py` (`run_tests`), `.pre-commit-config.yaml`
(the `unittest` hook), `tests/test_quality.py`.

The locked contract deliberately NOT changed: `src/gzkit/arb/validator.py`.

GHI #722 surfaces: `src/gzkit/handoff_validation.py`,
`tests/governance/test_handoff_validation.py`,
`.gzkit/skills/gz-session-handoff/SKILL.md`.

GHI #721 surfaces: `src/gzkit/governance/brief_reconcile.py`,
`tests/governance/test_brief_reconcile.py`.

GHI #720 surfaces: `src/gzkit/commands/sync.py`,
`tests/commands/test_sync_pull_ordering.py`, `docs/user/manpages/git-sync.md`.

The rule carrying the breached budget: `.gzkit/rules/tests.md`.

Negative control that must NOT be "fixed": `tests/content/test_validation_hooks.py`.

Insights recorded this session: `.gzkit/insights/agent-insights.jsonl`.

Receipts:
`artifacts/receipts/arb-step-unittest-263e6779a4094c61ad83c152145012c9.json`,
`artifacts/receipts/arb-step-typecheck-9a224d65743e40c9a24a6a2c228cf07f.json`.

Predecessor handoff:
`.gzkit/handoffs/20260726T165354Z-ghi-722-fixed-three-defects-closed.md`.

Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`.

Skills wielded: `.claude/skills/git-sync/SKILL.md`,
`.claude/skills/ghi-author/SKILL.md`,
`.claude/skills/gz-session-handoff/SKILL.md`.

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
