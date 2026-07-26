---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T02:35:30Z'
agent: claude-code
session_id: a76662eb-2e52-4b51-a9c8-5e1b5ced7d2d
continues_from: .gzkit/handoffs/20260726T004802Z-v0333-release-and-skill-staleness-cohort.md
---

## Current State Summary

Worked the resumed handoff's advised steps 1 through 3 under operator authorization booked verbatim as "do these:" (session a76662eb). Four commits landed on main and are synced: `cc659dc23` (staleness cohort sweep plus 17 skill defects), `c5c878aa3` (75-day warn band), `0ec38794a` (ADR-0.0.33 Invariant 4 retirement), `35ff76f0b` (handoff evidence-check fix). HEAD at `35ff76f0b`, tree clean and level with origin/main, no active OBPI lock, no in-flight pipeline, 13 GHIs open after #716 closed withdrawn.

Advised steps 4 and 5 are NOT started. They were authorized but deliberately left for a fresh context budget: step 4 is the 154-brief migration plus the strict-parse flip, which must land atomically, and starting an all-or-nothing migration on a heavily-consumed context is the risk profile that produces a half-landed one. That was an agent judgment surfaced to the operator, who chose to write this handoff rather than push on.

The session opened on a plain git-sync request that turned out to be neither plain nor a no-op, and the resume gate had pinned the session to a handoff three generations stale.

## Important Context

FIRST, the sync was not a no-op and the ritual created its own blocker. The clone was 20 commits behind with a clean tree; `gz git-sync --apply` ran `git add -A` and committed the ledger authorization line, which flipped the repo to ahead=1 behind=20 and made `git pull --ff-only` abort. The divergence was resolved by rebasing the single one-line ledger commit onto origin/main and resolving the append-only conflict as a union with the later timestamp last. Any agent running git-sync from a behind-and-dirty state will reproduce this; the ritual's own commit step is what creates the divergence.

SECOND, the session-start resume gate resolved "most-recent handoff" against the pre-pull working tree. It pinned the session to `20260725T110348Z-ghi-615-three-cuts-migration-held.md` while two newer handoffs already existed upstream. The gate itself worked correctly; its freshness input was stale because the clone was behind. This is unfiled.

THIRD, review-not-stamp earned its keep. Twelve of the 22 reviewed skills were clean; ten carried 17 defects that a date-stamp pass would have preserved. The most serious was a fabricated quote: `gz-plan` attributed a warning string to `gz adr report` that exists nowhere in `src/`. Others were live traps rather than cosmetics -- an unrecognized `--replace` flag, an `--attest-intrinsic` example missing all four of its required inputs, and two wrong Pydantic field lists.

FOURTH, one skill defect was doctrine drift rather than staleness. `gz-issue-file` restated AGENTS.md's direct-fix threshold as a conjunction "(<=10 source lines, <=2 source files, >=3 recent precedents)" where AGENTS.md:286 reads "<=10 source lines OR <=2 source files". A narrowed threshold over-routes to ceremony, which is the exact over-application GHI #195 authored the routing rule to prevent.

FIFTH, the version-pin collision is structural, not incidental. Four tests pinned exact `skill-version` literals while `.gzkit/rules/skill-surface-sync.md` #6 mandates a version bump on every review stamp, so every mandated sweep breaks them. REQ-0.0.35-02-04 reads "incremented from its pre-edit baseline" -- an increment relation -- so the equality pins contradicted their own REQ. They were converted to a monotonic floor and negative-controlled in both directions.

SIXTH, deleting code was blocked by the handoff corpus, which is worth knowing before the next removal. `validate_referenced_files` required every path cited in a handoff's Evidence section to exist at HEAD, but those citations sit in past-tense "Changed surfaces:" lists. Retiring any module therefore retroactively invalidated every handoff that recorded touching it. Git history is now the discriminator between "deleted since" and "never existed".

## Decisions Made

- [operator-ruled] Authorize the git-sync only, before any handoff steps were worked (operator verbatim 2026-07-25: "authorized, git-sync only"; booked via `gz handoff authorize`, session a76662eb). The stale-pinned handoff's five advised steps were NOT authorized at that point and were not worked.
- [operator-ruled] Work advised steps 1 through 5 of the current handoff (operator verbatim 2026-07-25: "do these:" followed by the five steps; booked via `gz handoff authorize`). Steps 1 through 3 were completed; 4 and 5 were not started.
- [operator-ruled] Resolve the skill-version pin collision by asserting the increment rather than the literal, chosen over updating the four frozen constants and over reverting the stamps. The equality pins contradicted REQ-0.0.35-02-04's own wording.
- [operator-ruled] Add a fixed 75-day non-blocking warn band, chosen over deriving the band from the ceiling and over leaving the gate binary.
- [operator-ruled] Retire ADR-0.0.33 Invariant 4 rather than build the scenario registry; GHI #716 closed withdrawn against the retirement commit.
- [operator-ruled] Fix the handoff evidence check's category error when the pre-push gate blocked the retirement, chosen over annotating the two sealed handoffs and over reverting the retirement.
- [agent-chose] Resolved the git divergence by rebasing the single ledger commit rather than merging or forcing. The commit was one file and one insertion, was never pushed, and rebasing unpushed work is not rewriting published history.
- [agent-chose] Resolved the append-only ledger conflict as a union with the local line last, because its timestamp was the later of the two and ledger replay walks the file in order. Verified 14058/14058 lines parse as JSON with no markers and monotonic timestamps.
- [agent-chose] Delegated the 22 skill reviews to four parallel read-only agents but verified every consequential finding personally before acting on it -- the fabricated quote, the unrecognized flag, the threshold drift, and the uninstalled hook were each re-run or re-grepped rather than taken on report.
- [agent-chose] Stamped the real local date 2026-07-25 rather than the UTC date 2026-07-26, matching the precedent set by `0af34caf`. Stamping a day that has not happened locally would assert a review on a future date.
- [agent-chose] Fixed the stale `--auto-chain` CLI help text rather than only the skill that contradicted it. The implementation selects `AutoChainPresenter`, so the help calling it a no-op was the lying surface.
- [agent-chose] Struck Invariant 4 through in situ in ADR-0.0.33 rather than deleting it. "Four invariants, mechanically validated" is attested text; rewriting it to read three would falsify what was attested.
- [agent-chose] Negative-controlled every gate that was loosened. The version floor still fails on regression, the handoff exemption still fails on a path git has never seen, and the warn band still reports stale past the ceiling without double-reporting. An exemption that cannot fail is not a gate.
- [agent-chose] Did not fix the `gz-obpi-specify` workflow contradiction, because resolving it requires deciding which of two documented procedures is the real one -- a judgment, not a repair.
- [agent-chose] Surfaced the context-budget risk on step 4 rather than starting a migration that must land atomically. Half-landing it is worse than not starting it.

## Immediate Next Steps

1. Pull GHI #615 cuts 2 and 3 -- authorized this session but not started. The 154-brief corpus migration plus the strict-parse flip and its fail-closed `gz validate` scope. The two MUST land together: a strict flip over a partially-migrated tree is the staging-flag anti-pattern. Both are described in the GHI #615 comment thread. Note that `a0a2e10e` (landed 2026-07-25 by another session) already resolved the residual-36 Draft-discovery question by predicate, and `gz validate --brief-reconcile` is currently exit 0, so the tree is not red while this waits.
2. Then GHI #581, then GHI #641 -- also authorized, also not started. The order is a data dependency rather than only file contention: #615's triage produces #581's corpus. All three contend on `src/gzkit/governance/brief_reconcile.py`.
3. Rule the `gz-obpi-specify` workflow contradiction, surfaced by this session's review and deliberately not fixed. `SKILL.md:268` runs `gz specify --author`, whose help reads "fail unless `--authored` validation succeeds", while `:277` and the following steps describe a manual hand-authoring loop ending "keep authoring until it passes". When step 1 succeeds the later steps are unreachable; when it fails it leaves no artifact. Both cannot be the workflow. Deciding which is real is a judgment about intended procedure.
4. Decide whether the session-start resume gate should resolve the most-recent handoff against fetched remote state. It pinned this session to a handoff three generations stale because the clone was 20 commits behind. The gate behaved correctly; its input did not. Unfiled -- file a GHI via `/ghi-author` if it is wanted as tracked work.
5. The campaign RULES sequencing. Movement A remains topmost with ADR-0.35.0 at 0/9 and the ADR-0.34.0 capstone at 2/5. Steps 1 through 4 above are defect repair and authorized carry-over that the campaign refines rather than substitutes for; none is a campaign amendment.

## Pending Work / Open Loops

CARRIED AND STILL UNSTARTED: GHI #615 cuts 2 and 3, then #581, then #641. All were authorized this session and none was begun. The parser-sprawl half of #615 also remains entirely untouched -- roughly 14 modules re-parse ADR frontmatter by hand, and the dual `ReqKind` enum collision persists between `triangle.py` and `req_kind.py`.

CAMPAIGN LINE 131 remains stale by one OBPI and is re-injected at every session boot. `docs/governance/build-to-1.0-campaign-2026-07-18.md` records ADR-0.34.0 at 1/5 while Layer-2 carries an attested OBPI-0.34.0-02, so the true count is 2/5. Carried unedited across six handoffs now because campaign amendments are operator-ratified.

THE SKILL-STALENESS COHORT is swept, but the systemic question is only half closed. The 75-day warn band now gives runway, yet the next cohort still arrives as a batch: `gz-content-remember` tips 2026-09-04 and the remaining 45 skills carry dates that will cluster again, because batch review produces batch expiry. The band surfaces it earlier; it does not de-cluster it.

TWO REVIEW FINDINGS WERE NOT FIXED and are not defects of implementation. The `gz-obpi-specify` workflow contradiction is advised step 3 above. The resume-gate freshness input is advised step 4.

THE SECONDARY FINDING ON GHI #716 IS NOT DISCHARGED by its close. Every "until ADR-X lands" or "owned by ADR-X" prose deferral is an untracked obligation, with no gate at ADR-X's closeout asking what other ADRs handed it. Invariant 4 was one instance and is now repaired; the class is unsized. Sizing it needs a sweep of ADR packages for deferral prose.

CARRIED ADVISORY: the spec-test drift advisory stands at 2030 findings (2020 unlinked specs, 10 orphan tests). Unchanged in substance by this session.

## Verification Checklist

`git log --oneline -4` (expect `35ff76f0b`, `0ec38794a`, `c5c878aa3`, `cc659dc23`);
`git status --short --branch` (expect a clean tree level with origin/main);
`uv run gz check` (expect exit 0 -- capture to a file rather than piping, since a pipe reports the filter's exit and not the verifier's);
`uv run gz skill audit` (expect exit 0, Blocking 0, Non-blocking 0, 68 skills across 4 roots);
`uv run gz skill audit --max-review-age-days 89` (expect exit 0 -- simulates CI running one day ahead of local, which is the condition that broke on 2026-07-26);
`uv run gz validate --surface-fidelity` (expect exit 0 across three constituents, Invariant 4 having been retired);
`uv run gz validate --scenario-reachability` (expect an unrecognized-argument error -- the flag is retired);
`uv run gz validate --brief-reconcile` (expect exit 0);
`uv run gz cli audit` (expect 131/131 commands fully covered);
`uv run -m unittest -q` (expect 7455 or more OK);
`uv run gz obpi lock list` (expect no active locks);
`gh issue list --state open` (expect 13 open, #716 now closed).

To confirm the staleness cohort is genuinely cleared rather than merely green today, read `last_reviewed` from every `.gzkit/skills/*/SKILL.md` and add 91 days -- that is the first date the audit reports blocking in CI, since the predicate passes at exactly 90. Expect the earliest to be 2026-09-04 (`gz-content-remember`) and zero skills inside 40 days.

To confirm the loosened gates still discriminate, check that the version floor rejects a regression below its landed value, that a handoff citing a path git has never seen is still reported broken, and that a review past 90 days reports stale and NOT aging.

## Evidence / Artifacts

Session commits, all on main and synced: `cc659dc23` (review-and-stamp the near-edge staleness cohort, fixing 17 defects), `c5c878aa3` (staleness warn band), `0ec38794a` (retire ADR-0.0.33 Invariant 4, GHI #716), `35ff76f0b` (handoff evidence-check fix). Preceded by `52002d094`, the rebased ledger commit that resolved the 20-commit divergence.

Skill surfaces reviewed and stamped, canonical plus three vendor mirrors and the package copy each (22 slugs): `.gzkit/skills/gz-issue-file/SKILL.md`, `.gzkit/skills/gz-complexity-distill/SKILL.md`, `.gzkit/skills/gz-competitor-radar/SKILL.md`, `.gzkit/skills/ghi-author/SKILL.md`, `.gzkit/skills/gz-adr-map/SKILL.md`, `.gzkit/skills/gz-check-config-paths/SKILL.md`, `.gzkit/skills/gz-cli-audit/SKILL.md`, `.gzkit/skills/gz-constitute/SKILL.md`, `.gzkit/skills/gz-implement/SKILL.md`, `.gzkit/skills/gz-migrate-semver/SKILL.md`, `.gzkit/skills/gz-prd/SKILL.md`, `.gzkit/skills/gz-state/SKILL.md`, `.gzkit/skills/gz-validate/SKILL.md`, `.gzkit/skills/gz-plan/SKILL.md`, `.gzkit/skills/gz-complexity-advisor/SKILL.md`, `.gzkit/skills/gz-complexity-guide/SKILL.md`, `.gzkit/skills/gz-chores/SKILL.md`, `.gzkit/skills/gz-project/SKILL.md`, `.gzkit/skills/gz-quality/SKILL.md`, `.gzkit/skills/gz-workflow/SKILL.md`, `.gzkit/skills/gz-obpi-specify/SKILL.md`, `.gzkit/skills/gz-context-diet/SKILL.md`.

Runtime surfaces changed: `src/gzkit/skills_audit.py` (warn band), `src/gzkit/cli/parser_artifacts.py` (auto-chain help), `src/gzkit/cli/parser_maintenance.py` (retired flag), `src/gzkit/commands/validate_cmd.py` (retired scope), `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/governance/trust_audits/_qc_negative_controls.py`, `src/gzkit/governance/trust_audits/_qc_nc_composite.py`, `src/gzkit/quality.py`, `src/gzkit/handoff_validation.py` (historical-path discriminator).

Deleted by the retirement: `src/gzkit/governance/trust_audits/scenario_reachability.py` and `tests/governance/test_scenario_reachability.py`.

Tests changed: `tests/test_skills_audit.py`, `tests/governance/test_handoff_validation.py`, `tests/governance/test_foundation_invariance_skill_enrichment.py`, `tests/skills/test_complexity_advisor.py`, `tests/skills/test_complexity_guide.py`, `tests/skills/test_gz_complexity_distill.py`, `tests/governance/test_surface_fidelity_composite.py`, `tests/governance/test_enforcement_nc_discrimination.py`, `tests/cli/test_validate_registry_parity.py`.

Canon and docs: `docs/design/adr/foundation/ADR-0.0.33-agent-control-surface-fidelity/ADR-0.0.33-agent-control-surface-fidelity.md` (Amendment 2026-07-25), `docs/user/manpages/skill-audit.md`, `docs/user/manpages/validate.md`.

ARB receipts, in commit order: `arb-step-unittest-3cfce834cd654af4bfe0c7a19332cb57`, `arb-ruff-636d26446a964ed787c82a5a0d9aeb1c`, `arb-step-typecheck-aee427ee36374bfda4083a6848aee350` (sweep); `arb-step-unittest-5d7d63755a094486af4955e9a77fd3d8`, `arb-ruff-72ff9e1ae1fe4af5a94d8df04957b04a`, `arb-step-typecheck-af1ac1df42fc41a5886b64bdb0677985` (warn band); `arb-step-unittest-49c2d547b9dd4d6689f919cdb9add478`, `arb-ruff-9c4a885355bb41bdb6d8d0b70b8ba132`, `arb-step-typecheck-16f38154fdff49b9b1663d269cf7a815` (retirement); `arb-step-unittest-052caa8c6b4e4654906373b879cfdd20`, `arb-ruff-0d9145ffc2184994b167b888f735f669`, `arb-step-typecheck-f4c5b20a485a4c7a88d4334eb395be39` (handoff fix).

Skills wielded: `.claude/skills/git-sync/SKILL.md`, `.claude/skills/gz-session-handoff/SKILL.md`. Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`. Predecessor: `.gzkit/handoffs/20260726T004802Z-v0333-release-and-skill-staleness-cohort.md`.

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
