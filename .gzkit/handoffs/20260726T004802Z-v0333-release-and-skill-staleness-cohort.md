---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T00:48:02Z'
agent: claude-code
session_id: bfc3ccad-e24c-4ec8-94da-c50652369757
continues_from: .gzkit/handoffs/20260725T235923Z-ghi-715-hook-delivery-and-615-discovery-scoping.md
---

## Current State Summary

Shipped patch release v0.33.3 and repaired the CI skill-audit staleness
failure that was blocking the pipeline. Three commits on main: `bdf63436`
(ledger sync booking the operator ruling), `0af34caf` (skill review-date
refresh), and `2f36f212` (the release). HEAD at `2f36f212`, tree clean and
level with origin. Version synced to 0.33.3 across `pyproject.toml`,
`src/gzkit/__init__.py`, and the README badge; manifest at
`docs/releases/PATCH-v0.33.3.md`; GitHub release created on the
non-Foundation path (draft=false, prerelease=false, target=main). GHI #714
and #715 CLOSED, #615 deliberately left OPEN by Step 1b adjudication. No
active OBPI lock, no in-flight pipeline.

The reason this handoff exists is the near-edge skill-staleness cohort: the
operator declined an immediate sweep and directed that it be recorded here
instead. The exact dates are in Important Context.

## Important Context

FIRST, the CI failure was a date boundary, not a code defect. The audit
predicate is `date.today() - last_reviewed <= timedelta(days=90)` at
`src/gzkit/skills_audit.py:280`, so exactly 90 days passes and 91 fails. The
three named skills carried `2026-04-26`; +90 = 2026-07-25 and +91 =
2026-07-26. The audit therefore passed locally (local date 2026-07-25) and
failed in CI (UTC 2026-07-26). Any agent reproducing this on the same local
day will see green and may wrongly conclude the job log was noise.

SECOND, and the point of this document: the near-edge cohort. These are
computed CI-fail dates (`last_reviewed` + 91 days), not estimates.

  2026-08-01  gz-issue-file
  2026-08-04  gz-complexity-distill
  2026-08-06  gz-competitor-radar
  2026-08-11  ghi-author
  2026-08-19  NINE AT ONCE: gz-adr-map, gz-check-config-paths, gz-cli-audit,
              gz-constitute, gz-implement, gz-migrate-semver, gz-prd,
              gz-state, gz-validate
  2026-08-20  gz-plan
  2026-08-21  gz-complexity-advisor, gz-complexity-guide
  2026-08-23  gz-chores, gz-project, gz-quality, gz-workflow
  2026-08-25  gz-obpi-specify
  2026-08-28  gz-context-diet

The 2026-08-19 cliff is nine skills tipping on one day and will present as a
mass CI failure rather than a single stale file.

Correction to a claim made in-session: the agent told the operator
gz-issue-file tips on 2026-07-31. That is the last day it PASSES; the first
CI failure is 2026-08-01. The corrected figure is the one above.

THIRD, `OBPI-unwaivered-pre-cutoff-01` is NOT a defect and must not be
"fixed". It appears exactly once in the repo, at
`features/steps/validate_receipt_shape_steps.py:270`, as a BDD
negative-control fixture. Its scenario is titled "Pre-cutoff receipt without
waiver entry is warn-only" and asserts exit 0; the line appearing in CI logs
is a LOG_WARNING, not an error, and its own text says the doctrine binds
going forward only. The feature passes 10 of 10 scenarios. Adding the
fixture to `data/historical_self_close_waivers.json` or migrating it to a
non-deprecated shape would make the negative control unable to fail, which
is the tautological-test failure AGENTS.md Never #5 forbids.

FOURTH, `last_reviewed` asserts that a review happened, so the three skills
were actually re-read rather than date-stamped. git-sync was exercised
directly in-session (dry-run then apply, with `git fetch --prune` preceding
the ahead/behind read); both pythonic-pattern skills had their chore targets,
`CHORE.md`, `acceptance.json`, and `scan.py` confirmed present.
skill-surface-sync rule #2 makes any skill edit a version bump and rule #6
couples `last_reviewed` to it, so each took a patch bump, canonical-first
then `gz agent sync control-surfaces` to the three vendor mirrors and the
package copy.

FIFTH, the changelog citation gate forced an attribution decision mid-release.
`gz validate --changelog` requires a `GHI #N` on every entry, and two shipped
fixes had no anchor: `79b775e8` (the `uvx` to `uv run` hook repoint) and
`3ca549e1` (the cli-alignment exemption for generated release manifests).
Both were attributed to #715 on the evidence of its own body, which names
the red tree `3ca549e1` resolved and the first-time hook installation that
surfaced `79b775e8`. The reasoning is recorded in the release-notes Gate
Evidence section so the attribution is auditable rather than silent.

SIXTH, #714 proved itself on its first live run: the release that shipped the
fix is the release where it fired. #615 surfaced in the `open_upstream`
bucket and was adjudicated as work-under-an-open-tracker, so Stats reads 2
rather than 3.

## Decisions Made

- [operator-ruled] Book the patch release as this session's work and leave the
  resumed handoff's five advised steps unauthorized (operator verbatim
  2026-07-25: "/gz-patch-release"; booked via `gz handoff authorize`, session
  bfc3ccad). GHI #716, #615 cuts 2 and 3, #581, and #641 were NOT authorized
  and were not worked.
- [operator-ruled] Fix the CI failure, diagnosed by the operator from the job
  log as blocking skill-audit staleness rather than a code runtime defect
  (operator verbatim 2026-07-25: "fix:"). This authorized the skill-audit
  repair only.
- [operator-ruled] Approve the v0.33.3 release narrative as drafted and
  execute it (operator verbatim 2026-07-25: "yes, appprove the patch release
  narrative - do the work"), triggering the Iron Law run of Steps 4a through
  4e without pauses.
- [operator-ruled] Decline the near-edge staleness sweep and record it in a
  handoff instead (operator verbatim 2026-07-25: "no, but place it into a
  handoff and then git-sync the handoff").
- [agent-chose] Reviewed the three skills rather than date-stamping them.
  `last_reviewed` asserts a review occurred; stamping without reading would
  rubber-stamp exactly what the staleness gate exists to prevent.
- [agent-chose] Stamped 2026-07-25, the real local date, not the
  operator-suggested 2026-07-26. The audit has no future-date guard so
  2026-07-26 would have passed, but it would have asserted a review on a day
  that had not yet happened. Day-1 in CI clears the gate identically.
- [agent-chose] Pushed back on the optional half of the operator's CI
  diagnosis rather than applying it. Waiving the negative-control fixture
  would have made the test unable to fail; migrating its shape would delete
  the thing it exists to prove. Evidence: the feature passes 10 of 10.
- [agent-chose] Attributed the two unanchored fixes to #715 rather than
  filing GHIs to satisfy the changelog citation gate. Filing a tracker purely
  to construct a required string is the moratorium pattern named in
  `.claude/rules/task-discovery.md`.
- [agent-chose] Left #615 OPEN and excluded it from the Stats count, per the
  patch-release Step 1b case for work under a still-open tracker. #714's own
  body names #615 as the canonical instance of the
  tracker-counted-as-closed failure, so closing it to clear the bucket would
  have reintroduced the exact defect the release was shipping the fix for.
- [agent-chose] Did not run the staleness sweep even though the cohort was
  already computed and the edit is mechanical. The operator declined it, and
  Always #17 forbids launching unrequested implementation work off the back
  of a narrow ask.
- [agent-chose] Committed the release explicitly before `gz git-sync --apply`
  rather than letting the sync auto-commit. A dirty tree makes git-sync
  generate a generic "chore: update .gzkit" subject, which would have buried
  the release under a chore message.

## Immediate Next Steps

1. Sweep the near-edge skill-staleness cohort before 2026-08-01, when
   gz-issue-file tips. Review-then-stamp per skill; never a bulk date
   rewrite, because `last_reviewed` asserts a review happened. Each edit
   needs a `skill-version` patch bump (skill-surface-sync rules #2 and #6)
   followed by `gz agent sync control-surfaces`. Prioritize the 2026-08-19
   nine-skill cliff, which will otherwise present as a mass CI failure.
2. Decide whether the 90-day staleness gate should warn before it blocks.
   Today it is binary and fails CI with no runway; a non-blocking warn band
   at roughly 75 days would surface the cohort while remediation is still
   cheap. This is an operator design decision, not an agent call, and it is
   the systemic fix for a failure that has now recurred once.
3. Rule GHI #716 (carried, still unauthorized): is Invariant 4's Era-2 still
   wanted? If yes, the destination is a design conversation producing a
   scenario model and then an ADR carrying
   `data/agent-control-surface-scenarios.json`, closing #716 as superseded.
   If no, retire Invariant 4 explicitly in ADR-0.0.33, remove the validator's
   Era-2 branch and its 8 covering tests rather than leaving dead
   enforcement, and close #716 as withdrawn. The current third state, neither
   enforced nor retired, is what let the advisory read as ambient noise.
4. Pull GHI #615 cuts 2 and 3 (carried, still unauthorized): the 154-brief
   migration plus the strict-parse flip and its fail-closed `gz validate`
   scope. The two must land together; a strict flip over a partially-migrated
   tree is the staging-flag anti-pattern.
5. Then GHI #581, then GHI #641 (both carried, still unauthorized). All three
   contend on `src/gzkit/governance/brief_reconcile.py`, and the order is a
   data dependency rather than only a file conflict: #615's triage produces
   #581's corpus.

## Pending Work / Open Loops

THE SKILL-STALENESS COHORT is unswept by operator decision. Exact dates are
in Important Context. It recurs on a schedule and will fail CI again on
2026-08-01 absent action. This is the open loop this handoff was written to
carry.

GHI #716 remains OPEN as the live tracker for the scenario-reachability
registry, carrying a blocker comment naming the binary operator decision.
Its secondary finding, the cross-ADR deferral class, was deliberately not
filed separately because it would bundle a second class of failure.

GHI #615 remains OPEN with cuts 2 and 3 unstarted plus the parser-sprawl half
entirely untouched: roughly 14 modules re-parse ADR frontmatter by hand, the
dual ReqKind enum collision persists, and `validate_brief_reconcile` still
escalates on structural shape rather than keying on lifecycle.

FILE CONTENTION, carried and still unresolved: #615 cuts 2 and 3, #581, and
#641 all modify `src/gzkit/governance/brief_reconcile.py`. The order is
operator-confirmed as #615 then #581 then #641.

CARRIED from the predecessor handoff: the spec-test drift advisory stands at
2026 findings (2015 unlinked specs, 10 orphan tests, 1 unjustified code
change). GHI #551 carries a runtime label but landed no src commits.

STALE-BLOCKER FLAGS, carried and adjudicated but not acted on: #533 cites
settled #517 and #712; #581 cites settled #519; #594 cites settled #585;
#641 cites settled #618 and #532. Each is a citation, not a verdict.

TWO CEREMONY OBSERVATIONS worth watching rather than fixing now. The
changelog citation gate has no escape hatch for a genuinely unanchored fix,
which is what forced the #715 attribution decision; if unanchored runtime
fixes become a pattern, the gate needs either an explicit
attribution-of-record convention or a warn band. And `gz git-sync --apply`
auto-commits a dirty tree under a generic "chore: update .gzkit" subject, so
any substantive change must be committed explicitly first or it is buried.

## Verification Checklist

`git log --oneline -3` (expect `2f36f212`, `0af34caf`, `bdf63436`);
`git status --short --branch` (expect a clean tree level with origin/main);
`grep -m1 '^version' pyproject.toml` (expect `0.33.3`);
`grep -m1 '__version__' src/gzkit/__init__.py` (expect `0.33.3`);
`uv run gz skill audit` (expect exit 0, Blocking: 0, 68 skills across 4 roots);
`uv run gz skill audit --max-review-age-days 89` (expect exit 0 — simulates
CI's date being one day ahead of local, which is the condition that broke);
`uv run gz validate --changelog` (expect exit 0);
`uv run -m behave features/validate_receipt_shape.feature` (expect 10
scenarios passed; the LOG_WARNING lines naming `OBPI-unwaivered-pre-cutoff-01`
and `OBPI-bad-added-under-01` are intended fixture output, not failures);
`uv run gz check` (expect exit 0, with the pre-existing scenario-reachability
and spec-test-drift advisories);
`gh release view v0.33.3` (expect draft=false, prerelease=false, target=main);
`gh issue view 714 --json state` and `gh issue view 715 --json state` (expect
CLOSED); `gh issue view 615 --json state` (expect OPEN);
`uv run gz obpi lock list` (expect no active locks).

To recompute the staleness cohort, read `last_reviewed` from every
`.gzkit/skills/*/SKILL.md` and add 91 days — that is the first date on which
the audit reports blocking in CI, since the predicate passes at exactly 90.

To confirm the negative control still discriminates, note that the two
LOG_WARNING lines in the receipt-shape feature are asserted alongside exit 0.
A change that silences them without a scenario change has broken the fixture.

## Evidence / Artifacts

Session commits: `bdf63436` (ledger sync booking the operator's ruling that
cleared the handoff-resume gate), `0af34caf` (skill review-date refresh
resolving the CI failure), `2f36f212` (release v0.33.3).

Skill surfaces refreshed, canonical plus three vendor mirrors and the package
copy each: `.gzkit/skills/git-sync/SKILL.md`,
`.gzkit/skills/gz-pythonic-pattern-apply/SKILL.md`,
`.gzkit/skills/gz-pythonic-pattern-detect/SKILL.md`.

Release surfaces: `RELEASE_NOTES.md`, `CHANGELOG.md`, `pyproject.toml`,
`src/gzkit/__init__.py`, `README.md`, `docs/releases/PATCH-v0.33.3.md`.

The audit predicate whose boundary caused the failure:
`src/gzkit/skills_audit.py`.

Negative-control fixture that must NOT be waived or migrated:
`features/steps/validate_receipt_shape_steps.py`,
`features/validate_receipt_shape.feature`.

Contended surface for the three carried GHIs:
`src/gzkit/governance/brief_reconcile.py`.

GitHub release: https://github.com/tvproductions/gzkit/releases/tag/v0.33.3

Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`.
Predecessor handoff:
`.gzkit/handoffs/20260725T235923Z-ghi-715-hook-delivery-and-615-discovery-scoping.md`.

Skills wielded: `.claude/skills/git-sync/SKILL.md`,
`.claude/skills/gz-patch-release/SKILL.md`,
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
