---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-25T23:59:23Z'
agent: claude-code
session_id: e4c56baa-badc-4b41-bf17-03773ca97f18
continues_from: .gzkit/handoffs/20260725T203657Z-patch-release-v0332-hooks-unenforced.md
---

## Current State Summary

Closed GHI #715 (adopter hook activation) and landed the operator's ruling on GHI #615's residual Discovery findings, then filed GHI #716 for a dropped cross-ADR deliverable found while diagnosing the scenario-reachability advisory. Two commits on main: `7f5705de` (init delivers the pre-push gate) and `a0a2e10e` (brief-reconcile scopes unstarted Discovery by predicate). Main at `a0a2e10e`, tree clean and level with origin, no active OBPI lock, no in-flight pipeline, 14 GHIs open (#715 closed, #716 filed). The campaign's Movement A capstone line was corrected from 1/5 to 2/5 with an operator-ratified amendment.

Both commits were routed as direct fixes under operator canon that GHIs are authorized for direct repair, always. 304 fix() commits in the 60-day window against a threshold of 3.

## Important Context

FIRST, GHI #715's premise was wrong and the gap was one step further upstream than the issue described. The body opens "gzkit scaffolds .pre-commit-config.yaml"; nothing in the wheel ever wrote one. That was true only of this repo, where the file is committed. Reproducing the adopter path in a scratch git repo showed `gz init` produces no config, no hooks, and a `gz check` that fail-closes on a file gzkit tells the adopter to hand-author while citing a gzkit-internal OBPI id meaningless in their repo. So the fix has three arms (declare, activate, verify), not the two the issue named.

SECOND, the CI carve-out for the delivery arm resolved on the `CI` environment variable, read at the CLI adapter boundary so the audit stays a parameterized pure function. This tripped a real gate: `tests/policy/test_env_usage.py` and `tests/policy/test_import_boundaries.py` maintain env-var allowlists, and `CI` had to be registered in both with rationale. That gate is working as designed and should not be read as friction.

THIRD, the newly-installed hooks caught a regression on their first run. The first attempt at `7f5705de` was blocked by the xenon pre-commit hook at rank D, because the inline setup loops tipped `init` over the complexity ceiling. Extracted to `_session_green_gate_statuses` / `_setup_session_green_gate`.

FOURTH, and most consequential for the next session: the prior handoff's recommendation on GHI #615 was route (iii), a marker convention letting a Discovery row declare itself a deliverable. It is WITHDRAWN. Checking its own three cited examples showed they resolve three different ways. `OBPI-0.0.43-02`'s `domain_models.py` row is a PREREQUISITE annotated `(OBPI-01 product)`; marking it a deliverable would falsify the brief. `OBPI-0.0.43-01`'s `src/gzkit/cli/prd.py` is a TRUE POSITIVE (no such module ever existed; the scaffolder is `commands/init_cmd.py::prd`); marking it would suppress exactly the defect GHI #581 exists to catch. Only `OBPI-0.0.39-03`'s audit artifact is the own-deliverable class route (iii) assumed.

FIFTH, the class split measured corpus-wide is 35 own-deliverable, 23 pending-upstream, 27 dead-citation across 54 briefs. Those totals are a SUPERSET of the thread's 36 and not a reproduction of it: the migration and escalation patches remain reverted, so the pass classifies every unstarted brief rather than only the 154 migrated ones. The proportions are the finding.

SIXTH, in `_pending_deliverable_paths` the non-terminal qualifier on sibling briefs is load-bearing. A completed sibling's Allowed Paths prove the file should already exist, so if it is missing that is real drift; laundering it as pending-upstream would suppress the rename-after-close case. Pinned by `test_terminal_sibling_does_not_launder_a_dead_path`.

SEVENTH, GHI #716's finding is a cross-ADR deliverable handoff with no carrier. `OBPI-0.0.33-04` states verbatim that the scenario registry is "owned by ADR-0.0.34"; ADR-0.0.33 states Invariant 4 is "advisory until ADR-0.0.34 lands". ADR-0.0.34 is Validated with 8/8 attested and its package contains zero references to the registry. The obligation was inherited and dropped, and Era-1 skip mode is exit 0 by design so nothing noticed.

## Decisions Made

- [operator-ruled] Work GHI #715 and correct campaign line 131 (operator verbatim 2026-07-25: "#715 + campaign line 131"; booked via `gz handoff authorize`, session e4c56baa). This authorized the resumed handoff's advised steps 1 and 2 only; steps 3, 4, and 5 were not authorized at that point.
- [operator-ruled] Route GHI #615's residual findings by mechanical re-triage into three classes, file a GHI for the scenario-reachability advisory, and confirm the brief_reconcile landing order (operator verbatim 2026-07-25: "Mechanical re-triage into 3 classes; File a GHI; #615 -> #581 -> #641"; booked via `gz handoff authorize`). Routes (i), (ii), and (iii) were declined; building the scenario registry now and accepting Era-1 as permanent were declined; landing #641 first was declined.
- [agent-chose] Expanded GHI #715's scope to three arms after reproducing the adopter path. The issue named two gaps; `gz init` writing no `.pre-commit-config.yaml` at all is upstream of both and was unnamed. Scope expansion is not scope creep.
- [agent-chose] Resolved the CI carve-out on the `CI` environment variable rather than a gzkit-specific flag or config knob. Every major runner sets it, so it is the smallest surface that separates a developer worktree from a CI checkout without asking adopters to configure anything.
- [agent-chose] Did NOT unset `core.hooksPath` on the operator's behalf when it blocks installation. Some organizations set it deliberately. `gz init` reports with recovery prose and the delivery arm keeps failing until it is resolved, so the condition cannot be silently ignored.
- [agent-chose] Did NOT make pre-commit a gzkit dependency. STDLIB-FIRST requires foundation attestation for a runtime dep; activation is best-effort across `uv run`, `uvx`, and bare `pre-commit`, and the fail-closed verification arm is what makes a failed activation impossible to miss.
- [agent-chose] Withdrew the prior session's route (iii) recommendation on GHI #615 after checking its three cited examples. Two of the three would have been actively harmed by a marker convention.
- [agent-chose] Landed the brief-reconcile predicate AHEAD of the 154-brief migration. Engine first means the migration cannot escalate classes A and C when it lands; migrating onto an engine that still mis-classifies and then suppressing the fallout is the staging-flag anti-pattern.
- [agent-chose] Left GHI #716 OPEN with a blocker comment rather than closing it. Authoring the scenario registry requires deciding what the scenarios are, which is design judgment; guessing would turn Invariant 4 green while proving nothing.
- [agent-chose] Verified the pre-push gate by driving git's own `.git/hooks/pre-push` over a real push range rather than inferring it from the shim's presence. A first synthetic run with identical local and remote SHAs produced an empty push range and pre-commit skipped the hook, which would have read as a pass.
- [agent-chose] Used gzkit's own extractors for the GHI #615 triage rather than writing a classification parser. A fourth parser would have been that issue's own defect.

## Immediate Next Steps

1. Rule GHI #716: is Invariant 4's Era-2 still wanted? If yes, the destination is a design conversation producing a scenario model and then an ADR that carries `data/agent-control-surface-scenarios.json`; close #716 as superseded against it. If no, retire Invariant 4 explicitly in ADR-0.0.33, remove the validator's Era-2 branch and its 8 covering tests rather than leaving dead enforcement, and close #716 as withdrawn. The current third state, neither enforced nor retired, is what let the advisory read as ambient noise for two months.
2. Pull GHI #615 cuts 2 and 3 (the 154-brief migration plus the strict-parse flip and its fail-closed `gz validate` scope). The doctrine blocker that held cut 2 is cleared as of `a0a2e10e`. The two cuts must land together; a strict flip over a partially-migrated tree is the staging-flag anti-pattern. The migration script is reproducible in seconds.
3. Then GHI #581, consuming the 27 class-B dead citations as its evidence base. Sample already identified: `src/gzkit/governance/trust_audits.py` (a package now), `src/gzkit/cli/validate.py` (it is `commands/validate_cmd.py`), `src/gzkit/ledger` and `src/gzkit/io` (no such directories), `src/gzkit/personas.py` (it is `personas/`).
4. Then GHI #641, the `gz brief reconcile` versus `gz obpi reconcile` rename, last of the trio so it re-points settled content once instead of three times. Heavy lane: CLI contract plus manpages plus two skills plus runbooks, and `gz validate --cli-alignment` gates every reference.
5. Decide whether the cross-ADR deferral class named in GHI #716 warrants its own sweep. Every "until ADR-X lands" or "owned by ADR-X" prose deferral is an untracked obligation today, with no gate at ADR-X's closeout asking what other ADRs handed it. The first step would be a sweep of ADR packages for deferral prose to size the class before anything is built.

## Pending Work / Open Loops

GHI #716 is OPEN and is the live tracker for the scenario-reachability registry. It carries a blocker comment naming the binary operator decision. Its secondary finding, the cross-ADR deferral class, was deliberately NOT filed separately because it would be a bundled second class of failure; this instance is evidence for the pattern but does not establish its frequency.

GHI #615 remains OPEN with cuts 2 and 3 unstarted, plus the parser-sprawl half entirely untouched: roughly 14 modules re-parse ADR frontmatter by hand, the dual ReqKind enum collision persists, and `validate_brief_reconcile` still escalates only structured briefs rather than keying on lifecycle. Post-migration the escalation keying stops mattering for the 154 migrated briefs, but the keying itself is still structural-shape rather than lifecycle.

GHI #715's own residual is nil for this repo, but adopters who initialized before `7f5705de` get the config and hooks only on their next `gz init` run. There is no migration for already-initialized adopter projects beyond re-running init, which is the documented repair path.

FILE CONTENTION, now sequenced but not resolved. GHI #615 cuts 2 and 3, GHI #581, and GHI #641 all modify `src/gzkit/governance/brief_reconcile.py`. The order is operator-confirmed as #615 then #581 then #641, and it is a data dependency rather than only a file conflict: #615's triage produces #581's corpus.

CARRIED AND STILL UNRESOLVED from the predecessor handoff: the spec-test drift advisory stands at 2026 findings (2015 unlinked specs, 10 orphan tests, 1 unjustified code change). GHI #551 carries a runtime label but landed no src commits, the inverse of the #532 and #682 labeling problem, harmless but worth watching.

STALE-BLOCKER FLAGS surfaced by the triage script in the prior session and adjudicated but not acted on: #533 cites settled #517 and #712; #581 cites settled #519; #594 cites settled #585; #641 cites settled #618 and #532. Each is a citation, not a verdict; the preconditions have moved but the issues' own merits were not re-argued.

## Verification Checklist

`git log --oneline -3` (expect `a0a2e10e`, `7f5705de`, `7fc073f1`);
`git status --short --branch` (expect a clean tree level with origin/main);
`ls .git/hooks/` (expect `pre-commit` and `pre-push` present, not only `.sample` files);
`git config --local --get core.hooksPath` (expect no output; a returned path means enforcement is off again);
`uv run gz validate --session-green-gate` (expect exit 0; the delivery arm now binds by default outside CI);
`uv run gz check` (expect exit 0, with the pre-existing scenario-reachability and spec-test-drift advisories);
`uv run -m unittest -q` (expect 7460 or more OK);
`uv run gz obpi lock list` (expect no active locks);
`gh issue list --state open` (expect 14 open, including #716 and #615);
`gh issue view 715 --json state` (expect CLOSED);
`uv run gz adr status ADR-0.34.0` (expect 2/5, matching the corrected campaign line 131).

To re-derive the GHI #615 class split, reconcile every brief and count `discovery_delta.unresolved_paths` for unstarted briefs, classifying each path against the brief's own Allowed Paths and its non-terminal siblings' Allowed Paths. Before `a0a2e10e` the corpus showed 36 briefs with drift and 313 unresolved discovery paths; after, 22 and 276.

To confirm the new tests discriminate rather than merely pass, run `git stash push -- src/gzkit/governance/brief_reconcile.py`, then `uv run -m unittest tests.governance.test_brief_reconcile_pending_upstream -q` (expect `Ran 6 tests` and `FAILED (failures=2)`), then `git stash pop`. The two failures are the narrowing assertions; the four that pass on both sides are the fence.

To confirm the pre-push gate fires through git's own entry point rather than only existing on disk, pipe a real push range into `.git/hooks/pre-push` using HEAD and HEAD~1 as the local and remote SHAs. Identical SHAs produce an empty range and pre-commit skips the hook, which is not a pass.

## Evidence / Artifacts

Session commits: `7f5705de` (GHI #715: init declares, activates, and verifies the pre-push gate; campaign line 131 correction), `a0a2e10e` (GHI #615: unstarted Discovery scoped by computed predicate).

Changed surfaces: `src/gzkit/commands/init_cmd.py` (the pre-commit config scaffolder, the hook installer, and the two setup helpers extracted to hold the complexity ceiling); `src/gzkit/commands/validate_cmd.py` (the delivery-arm CI predicate and the session_green_gate scope entry); `src/gzkit/governance/trust_audits/session_green_gate.py` (`configured_hooks_path` made public so init and the audit share one parser); `src/gzkit/governance/brief_reconcile.py` (the pending-deliverable predicate and the unstarted Discovery scoping); `tests/commands/test_init_hook_delivery.py`; `tests/governance/test_brief_reconcile_pending_upstream.py`; `tests/policy/test_env_usage.py`; `tests/policy/test_import_boundaries.py`; `docs/user/manpages/init.md`; `docs/user/runbook.md`; `docs/governance/build-to-1.0-campaign-2026-07-18.md`.

ARB receipts, GHI #715: `arb-ruff-50533dc66a454f97a0ee2104ff2b3cc8`, `arb-step-typecheck-c3ed5081cbb14efe942c75db173c1198`, `arb-step-unittest-0d0bc58f5f154c6995911b556d7b2b74` (7454 OK). GHI #615: `arb-ruff-eb8a471051a940388ab337defb6983c9`, `arb-step-typecheck-18e839e07afd4d96b73756678154b152`, `arb-step-unittest-9be8dd7329d847f5ac759fe15b15ebbe` (7460 OK). `uv run gz check` exit 0 on both.

GHIs: #715 closed as fixed citing `7f5705de`; #716 filed and left OPEN with a blocker comment; cross-link comment posted on #598 recording that the runtime half it deferred has landed; two comments posted on #615 (the three-class triage withdrawing route (iii), and the landing record).

Campaign amendment: `docs/governance/build-to-1.0-campaign-2026-07-18.md` section Amendments, entry dated 2026-07-25, recording the ADR-0.34.0 count correction from 1/5 to 2/5 verified via `uv run gz adr status ADR-0.34.0`.

Skills wielded: `.claude/skills/ghi-close/SKILL.md`, `.claude/skills/ghi-author/SKILL.md`, `.claude/skills/gz-session-handoff/SKILL.md`.

Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`.
Predecessor handoff: `.gzkit/handoffs/20260725T203657Z-patch-release-v0332-hooks-unenforced.md`.

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
