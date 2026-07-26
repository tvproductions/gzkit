---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T11:31:50Z'
agent: claude-code
session_id: 786a9e8f-b5d7-47a4-ab93-224c0e4fd9ae
continues_from: .gzkit/handoffs/20260726T094159Z-ghi-615-641-landed-authorized-queue-clear.md
---

## Current State Summary

Off-cycle session: no parent ADR, no OBPI lock. Began as a competitive analysis of unclebob/swarm-forge vs gzkit (SWOT + deep dive; superpowers/obra folded in), which the operator turned into authoring work. Delivered TWO pool ADRs crediting swarm-forge (Robert C. Martin) and superpowers (Jesse Vincent): ADR-pool.ledger-concurrency-substrate (single-writer-by-construction, no daemon) and ADR-pool.worktree-parallel-agents (ephemeral worktrees; primary use = parallel read-only review personas). Committed 5ef2a1d57 and pushed. Then surfaced and fixed GHI #718 (gz interview adr rejects the pool ADRs its own gz-adr-create skill mandates the interview for) via a direction-(a) skill-doc fix, commit 47c996134, closed with evidence. Filed follow-on GHI #719 (pool interview JSON is unschema'd -- the deferred direction-(b) scope), cross-linked to class GHI #615, left open. Tree clean, main level with origin/main at 47c996134. The original ask is fully delivered.

## Important Context

1. CONCURRENT-SESSION HAZARD (resolved). A second Claude session the operator was running shared THIS working tree earlier and committed+pushed on main, advancing HEAD past this session's start snapshot (1cb3477d6 -> 6051cdadb) and sweeping one interview JSON into commit 26f3473b7. I STOPPED and surfaced it rather than committing into a tree another session was pushing; operator confirmed clear ("I was running one, but it is clear now - proceed"). This is the LIVE instance of the ledger race ADR-pool.ledger-concurrency-substrate theorizes.
2. gz interview adr --from scaffolds NON-POOL ADRs only (interview_cmd.py:145-156); pool ADRs are authored via gz plan create <slug> --kind pool with the interview kept as a hand-authored JSON. That asymmetry is GHI #718 (doc fixed) and #719 (schema gap, open).
3. gz validate --taxonomy is RED (74 foundation grandfather-manifest errors) -- pre-existing Foundation-Sunset state, NOT wired into gz check. The two new pool ADRs are absent from those errors (pool carries no kind/semver).
4. Pool ADRs do NOT appear in docs/governance/GovZero/adr-status.md (that index is foundation/pre-release only -- which is why --adr-status-fresh passes); they DO appear in gz adr report pool. The Pool table truncates long slugs with an ellipsis, so grep a short prefix (ledger-concurrency / worktree-parallel), not the full slug.
5. Skill edits: edit canonical .gzkit/skills first, bump metadata.skill-version AND last_reviewed in the same edit, then gz agent sync control-surfaces. Never hand-edit the .claude/.agents/.github mirrors or the src/gzkit pkg copy.

## Decisions Made

- [operator-ruled] Write two pool ADRs (substrate + capability) crediting swarm-forge + superpowers (verbatim: "authorized -- write the two pool ADRs"; booked via gz handoff authorize, session 786a9e8f).
- [operator-ruled] Primary use case = parallel read-only review personas; parallelism itself "isn't too important"; record the alternatives (parallel OBPI impl / GHI fixes / ADR pipelines) as future scope.
- [operator-ruled] Allow ephemeral worktrees (scratch checkouts, land on main, no branch dance) -- a carve-out from "never create feature branches"; ratifying it is a hard promotion gate for ADR-pool.worktree-parallel-agents.
- [operator-ruled] Ledger concurrency = single-writer-by-construction (only merge-to-main writes Layer-2), NOT a daemon.
- [operator-ruled] Two pool ADRs (substrate + capability), not one combined nor three.
- [operator-ruled] Use the governed skill, not hand-scaffolding ("there is an adr authoring skill don't vibe"; "use skills - skills have rules + tools"). Recorded as an improvement insight.
- [operator-ruled] Fix GHI #718 via direction (a), the skill-doc fix (chosen via AskUserQuestion).
- [operator-ruled] File the #718 follow-on via /ghi-author (became GHI #719).
- [agent-chose] Classified #719 defect+runtime+tech-debt as a sibling-cut of #615 (different artifact, same not-schema-enforced class); posted a cross-link comment on #615.
- [agent-chose] skill-version bump 6.6.2 -> 6.6.3 as PATCH (procedure/wording fix, no governance-rule change) per the skill-surface-sync version table.
- [agent-chose] STOPPED and surfaced the concurrent-writer state before any commit rather than interleaving writes into another session's push.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. The original ask (two credited pool ADRs) is delivered and pushed; every step below needs an explicit operator ruling before execution.
2. GHI #719 (pool interview JSON unschema'd) -- direction (b): add a gz plan create --from <interview.json> --kind pool path that deserializes+validates the interview JSON, and/or a pool-interview schema under src/gzkit/schemas/ with a gz validate scope. Adding a flag is CLI-contract-bearing -> likely Heavy/OBPI; a validate-only scope may be direct-fixable.
3. Campaign Movement A remains topmost absent a ruling: ADR-0.35.0-canon-entry-corpus-landing (0/9) and the ADR-0.34.0-foundation-sunset capstone (2/5), including "wire the permanent --taxonomy gate into gz check" -- currently red with 74 foundation grandfather errors.
4. Promotion of the two pool ADRs when wanted: assign SemVer IDs; for ADR-pool.worktree-parallel-agents, ratify the ephemeral-worktree doctrine carve-out FIRST (hard promotion gate). ADR-pool.ledger-concurrency-substrate enables the write-heavy modes of the worktree ADR; the read-only review-persona mode needs neither promotion first.

## Pending Work / Open Loops

- GHI #719 OPEN: the deferred direction-(b) capability (schema-validate the pool interview JSON). Not blocked; awaiting fix-time routing per AGENTS.md Defect-fix routing.
- gz validate --taxonomy RED: 74 foundation ADRs missing from data/foundation_grandfather.json -- Foundation-Sunset campaign work, not this session's scope, and not in gz check.
- The two pool ADRs are Pool/Pending/LITE, UNSCOPED (no OBPIs until promotion); ADR-pool.worktree-parallel-agents is additionally blocked-for-promotion on the ephemeral-worktree carve-out.
- No OBPI lock held; no in-flight pipeline; nothing carried-and-unstarted from the authorized queue.

## Verification Checklist

git log --oneline -3 (expect 47c996134, 5ef2a1d57, then the concurrent session's 6051cdadb);
git status --short --branch (clean, level with origin/main);
gh issue view 718 --json state (CLOSED); gh issue view 719 --json state (OPEN);
uv run gz adr report pool | grep -E 'ledger-concurrency|worktree-parallel' (both Pending/LITE/UNSCOPED);
uv run gz validate --cli-alignment (exit 0); uv run gz validate --adr-status-fresh (exit 0);
uv run gz skill audit (passed, 0 blocking; gz-adr-create at skill-version 6.6.3).

## Evidence / Artifacts

Commits (main, pushed): `5ef2a1d57` (docs(pool): two parallel-agent pool ADRs), `47c996134` (fix(gz-adr-create): name real pool-ADR interview path, GHI #718).
Pool ADRs: `docs/design/adr/pool/ADR-pool.ledger-concurrency-substrate.md`, `docs/design/adr/pool/ADR-pool.worktree-parallel-agents.md`.
Interview artifacts: `docs/design/adr/pool/ledger-concurrency-substrate-interview.json`, `docs/design/adr/pool/worktree-parallel-agents-interview.json`.
Skill fix: `.gzkit/skills/gz-adr-create/SKILL.md` (Step-0, skill-version 6.6.3).
Course-correction insight: `.gzkit/insights/agent-insights.jsonl` (improvement, scope adr-authoring).
GHIs: #718 (closed, fixed), #719 (open), #615 (cross-link comment).

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
