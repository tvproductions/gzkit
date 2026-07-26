---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T16:53:54Z'
agent: claude-code
session_id: 5eed8cd8-58a7-48c0-9d4b-0280c2ebecd4
continues_from: .gzkit/handoffs/20260726T161447Z-git-sync-720-721-fixed-ci-green.md
---

## Current State Summary

Supersedes `20260726T161447Z`, which recorded GHI #722 as filed-and-unfixed. That
stopped being true one commit later, and the stale record would have been the
resume surface for the next session — the exact decay the predecessor chain was
written to prevent.

GHI #722 is now fixed, closed, and gate-verified: `fa51920b` lands
`validate_decision_markers`, repairs the two malformed handoffs, and corrects the
skill contract that produced the shape. HEAD at `fa51920b`, tree clean and level
with origin.

Four commits this session: `02ed4e83` (git-sync governance sweep), `d9224500`
(GHI #721), `2a0652b6` (GHI #720), `3fa20990` (predecessor handoff), `fa51920b`
(GHI #722). Three GHIs filed, fixed, and closed in one session — #720, #721,
#722 — all three surfaced by the ritual rather than planned. No active OBPI lock,
no in-flight pipeline, 13 open GHIs.

CI green on #720 and #721; the #722 run is unverified at authoring time (pushed
minutes before this handoff) and is the one open verification.

## Important Context

FIRST, and correcting the record this handoff exists to supersede: the
predecessor states *"Filed as GHI #722; the parser is unfixed, so the next
unbulleted handoff drops its rulings again."* That is now FALSE. `fa51920b`
landed the fail-closed refusal. The predecessor's four numbered next steps remain
accurate — #722 was recorded in its Pending Work, never as an advised step — so
this supersession corrects one claim, not a plan.

SECOND, the shape of the #722 fix matters for anyone who touches it. The refusal
is ASYMMETRIC by design: `validate_decision_markers` fires only on a line that
CLAIMS attribution (`[operator-ruled]` / `[agent-chose]`) and would therefore be
discarded, never on ordinary prose. Widening it to "decisions must be bulleted"
would be a formatting opinion and would fail the whole legacy corpus — 225
handoffs, most of them prose-shaped. A negative control
(`test_unattributed_prose_is_not_refused`) pins that boundary; if a future change
makes it fire on prose, that test is the one that should stop it.

THIRD, the two malformed handoffs were REPAIRED, not grandfathered, and this was
a judgment call worth knowing about. `validate_handoff_document` is gate-wired
corpus-wide over post-cutover entries, so the offenders (both 2026-07-26) would
have turned `gz check` red. The GHI #692 precedent for exactly this situation was
a path-scoped waiver in the shrink-only ratchet. Repair was chosen instead: 18
changed lines per file, every one a `- ` prefix, ruling text byte-identical (0
content-altering lines, verified by diffing with the marker stripped). A
permanent waiver for a missing hyphen buys nothing, and repair makes those
rulings re-derivable from their own handoffs rather than only from the recovery
seated downstream.

FOURTH, the three defects of this session share one shape, and naming it is worth
more than the three fixes: a predicate evaluated against state that something
else had already changed or discarded. #721 read the filesystem, mutated by
whichever repos sit beside gzkit. #720 read ahead/behind, mutated by the
ceremony's own commit. #722 read a section the parser had already discarded. All
three produced a confident verdict from a stale premise, and all three were
invisible in the environment where they were authored.

FIFTH, unchanged and still the most likely repeat offender: negative-path tests
print fail-closed prose into CI logs that reads exactly like a real failure. This
session's CI diagnosis initially targeted `Fidelity validation failed
[surface-weight]` from a PASSING test. Second documented occurrence. Recorded as
a discovery insight; still has no GHI. Full detail is in the predecessor's
Important Context THIRD and is not repeated here.

SIXTH, unchanged: the `g0` authorship guard is PER-CLONE and PII-adjacent. Global
git config still holds the operator's personal email; only the local override
keeps it out of commits. Detail in the predecessor's Important Context FOURTH.

SEVENTH, the skill-staleness cohort remains RESOLVED upstream — `uv run gz skill
audit` passes, 68 skills, Blocking 0. Do not re-sweep it.

## Decisions Made

- [operator-ruled] Fix GHI #722 by failing closed at authoring rather than
  widening the parser (operator verbatim 2026-07-26: "fix #722 by failing closed
  at authoring"). Direction (a), widening `_section_items`, was declined.
- [operator-ruled] Write this successor handoff rather than leave the stale claim
  standing (operator verbatim 2026-07-26: "yes, write the successor handoff").
- [agent-chose] Repaired the two malformed handoffs instead of grandfathering
  them, departing from the GHI #692 waiver precedent. Reasoning in Important
  Context THIRD; the ruling text is byte-identical, so the repair adds a marker
  and changes no content.
- [agent-chose] Wired the refusal into `validate_handoff_document` (corpus-wide)
  rather than into the authoring path alone. "Failing closed at authoring" is
  satisfied either way, but every other handoff contract lives in that function,
  and a check that fires only on the write path would not catch a handoff altered
  after authoring.
- [agent-chose] Corrected the skill contract in the same patch as the validator.
  The wording is what produced the broken shape — an author following "lead each
  entry with `[operator-ruled]`" literally wrote a section the promoter could not
  read — so shipping the gate without the contract fix would fail authors for
  following the instructions.
- [agent-chose] Added a parse round-trip test asserting that what the validator
  ACCEPTS, `parse_decisions` can actually read. The two now carry duplicated
  pattern knowledge (`handoff_validation` cannot import from `handoff_api`, which
  imports it), and that duplication is exactly how the original defect would
  return.
- [agent-chose] Surfaced the predecessor handoff's stale claim rather than
  silently letting it stand, and asked before writing the successor. A handoff is
  the resume surface; a false sentence in it is worse than a missing one.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. Verify CI on `fa51920b` (the one open verification from
   this session), then every step below requires an explicit operator ruling.
2. Rule the negative-path log-legibility finding: file a GHI, or accept it as
   known noise. Two wrong diagnoses in two sessions; tracked only as an insight,
   which is not a tracker. Proposed remedy is a marker convention distinguishing
   exercised fail-closed prose from genuine failures in CI logs.
3. Rule the `g0` guard's durability: leave it per-clone, change the global config,
   or add a `gz init` step that writes the local guard. The PII rule treats a
   personal-email leak as needing a filter-repo rewrite to recover, so the
   per-clone gap is a standing risk on every fresh clone.
4. The predecessor chain's advice is UNWORKED and still live: GHI #719 (pool
   interview JSON unschema'd, direction (b)); campaign Movement A remains topmost
   absent a ruling (ADR-0.35.0-canon-entry-corpus-landing at 0/9 and the
   ADR-0.34.0-foundation-sunset capstone at 2/5, including wiring the permanent
   `--taxonomy` gate into `gz check`, currently red with 74 foundation grandfather
   errors); promotion of the two pool ADRs when wanted, with the
   ephemeral-worktree doctrine carve-out ratified FIRST for
   ADR-pool.worktree-parallel-agents.

## Pending Work / Open Loops

CI ON `fa51920b` IS UNVERIFIED at authoring time. Every other claim in this
handoff is gate-verified locally (`uv run gz check` exit 0, all 43 steps).

THE NEGATIVE-PATH LOG-LEGIBILITY FINDING is untracked by deliberate choice
pending an operator ruling, recorded in `.gzkit/insights/agent-insights.jsonl` as
a discovery insight. Second occurrence.

THE `g0` GUARD IS PER-CLONE. Fixed for this working copy only.

CARRIED FROM THE PREDECESSOR CHAIN, all unworked: GHI #719; campaign Movement A
(ADR-0.35.0 at 0/9, ADR-0.34.0 at 2/5); promotion of
ADR-pool.worktree-parallel-agents and ADR-pool.ledger-concurrency-substrate.

13 GHIs open. #581 remains OPEN against
`src/gzkit/governance/brief_reconcile.py`, which this session also modified under
#721 — re-read before assuming the earlier three-way contention shape still
holds.

SPEC-TEST DRIFT ADVISORY stands at 2031 findings. Advisory only.

NOT DONE UNDER #722, deliberately: `_section_items` itself is unchanged. The
parser stays narrow and the requirement is now explicit at authoring. If a future
session decides the parser SHOULD tolerate marker-less entries, the negative
control `test_unattributed_prose_is_not_refused` is the boundary to preserve.

## Verification Checklist

`git log --oneline -5` (expect `fa51920b`, `3fa20990`, `2a0652b6`, `d9224500`,
`02ed4e83`);
`git status --short --branch` (expect a clean tree level with origin/main);
`git log -1 --format=%an` (expect `g0`);
`gh issue view 720 --json state`, `gh issue view 721 --json state`,
`gh issue view 722 --json state` (expect CLOSED for all three);
`gh run list --workflow=CI --limit 3` (expect success on `2a0652b6` and
`d9224500`; CONFIRM `fa51920b` — unverified at authoring time);
`uv run gz check` (expect exit 0, all 43 steps, with the pre-existing
spec-test-drift and complexity advisories);
`uv run gz skill audit` (expect exit 0, Blocking 0, 68 skills);
`uv run gz obpi lock list` (expect no active locks).

To confirm GHI #722's gate is live rather than merely present, feed
`validate_decision_markers` a Decisions Made section whose entry reads
`[operator-ruled] X` with no leading `- `; it must return a violation naming
Settled Rulings. Feeding it plain prose must return nothing — that asymmetry is
the contract, not an accident.

To confirm the corpus is genuinely repaired, `parse_decisions` on
`20260726T103339Z` and `20260726T113150Z` must return 7/2 and 11/8
(decisions/settled). Zero settled from either means the repair was reverted.

## Evidence / Artifacts

Session commits: `02ed4e83` (git-sync governance sweep), `d9224500` (GHI #721
brief-reconcile out-of-tree guard), `2a0652b6` (GHI #720 git-sync pull ordering),
`3fa20990` (predecessor handoff), `fa51920b` (GHI #722 decision-marker gate).

GHI #722 surfaces: `src/gzkit/handoff_validation.py`,
`tests/governance/test_handoff_validation.py`,
`.gzkit/skills/gz-session-handoff/SKILL.md`.

Handoffs repaired under #722 (marker added, ruling text unchanged):
`.gzkit/handoffs/20260726T103339Z-ghi-581-ruled-717-fixed-slugs-renamed.md`,
`.gzkit/handoffs/20260726T113150Z-swarm-forge-pool-adrs-718-fixed-719-open.md`.

The parser this gate protects, deliberately unchanged: `src/gzkit/handoff_api.py`.

GHI #721 surfaces: `src/gzkit/governance/brief_reconcile.py`,
`tests/governance/test_brief_reconcile.py`.

GHI #720 surfaces: `src/gzkit/commands/sync.py`,
`tests/commands/test_sync_pull_ordering.py`, `docs/user/manpages/git-sync.md`.

Negative control that must NOT be "fixed": `tests/content/test_validation_hooks.py`.

Insights recorded this session: `.gzkit/insights/agent-insights.jsonl`.

Receipts:
`artifacts/receipts/arb-step-unittest-263e6779a4094c61ad83c152145012c9.json`
(7491 tests OK),
`artifacts/receipts/arb-step-typecheck-6b9a274e20ce44b881b43de3cb1c1cdb.json`.

Predecessor handoff (superseded on the #722 claim only):
`.gzkit/handoffs/20260726T161447Z-git-sync-720-721-fixed-ci-green.md`.

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
