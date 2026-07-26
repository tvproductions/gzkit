---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T09:19:05Z'
agent: claude-code
session_id: 7dd80db9-500f-426b-9d05-989e6c2775d5
continues_from: .gzkit/handoffs/20260726T023530Z-steps-1-3-landed-615-migration-unstarted.md
---

## Current State Summary

Resumed `20260726T023530Z` under operator authorization booked verbatim as "GHI #615 cuts 2 and 3, Then #581, then #641, Steps 3 and 4 (the two cheap judgments), Fix the two handoff-surface defects" (session 7dd80db9). Five commits landed on main and are pushed: `72f65a7aa` (brief-reconcile row semantics), `e5494fd32` (GHI #615 cuts 2+3 — 146-brief migration plus the fail-closed `--brief-structure` gate), `e84e6a85b` (handoff wrapped-ruling truncation), `32489b83a` (gz-obpi-specify workflow ruling), `8dba6a218` (orientation behind-clone caveat). HEAD at `8dba6a218`, tree clean and level with origin/main, no active OBPI lock, no in-flight pipeline, 13 GHIs open. GHI #615 cuts 2 and 3 are DONE; #581 is scoped-and-reported with a recommendation against the collapse; #641 is scoped but NOT started.

## Important Context

FIRST, the migration's real effect was never the frontmatter. `validate_brief_reconcile` SKIPS legacy briefs, so migrating flips them from skipped to escalated and arms every dormant finding at once — 34 across 22 briefs, measured before touching anything. Any future corpus migration in this repo has the same shape: the arming is the risk, not the edit.

SECOND, the 34 were four classes, not one, and three were ENGINE defects — the same failure GHI #615 names, one layer down. The Discovery extractor collected backtick paths without reading what the row said about them, so a row asserting a directory does NOT exist failed the brief for being correct about its own starting state. `_LINE_RANGE_SUFFIX_RE` anchored one trailing range so a multi-range line citation was existence-checked as a filename. `missing_in_brief` read `## Allowed Paths` alone and reported modules the brief explicitly DENIES as forgotten declarations. Repairing briefs to satisfy those scrapers would have encoded the misreading into 22 governance artifacts.

THIRD, coverage attribution was a substring match. Any test file MENTIONING a REQ id donated all its imports as leaked scope; `tests/test_triangle.py` is the worst case by construction because it exercises the REQ parser and carries `REQ-0.34.0-04-*` as fixture data. Attribution now goes through `@covers`. The scan is cached per tests-root — without the cache a full AST walk per brief turned a sub-second scope into a multi-minute one.

FOURTH, that fix exposed a test green for the wrong reason. `test_missing_on_disk_reported` asserted `has_drift` on a Draft fixture, which Draft scoping says must NOT gate; it only passed because the fixture's synthetic `REQ-0.0.99-01-01` also appears in six unrelated test modules. Expect more of these: any assertion that depended on substring attribution was resting on an accident.

FIFTH, sealed-record scoping is the recurring constraint. 514 terminal briefs stayed legacy on purpose; a repo-wide sed on the dead-citation paths would have rewritten attested artifacts. The same constraint now blocks GHI #641: 60 handoff files and terminal ADR-0.0.37 briefs carry the verb strings and must not be rewritten.

SIXTH, GHI #581's premise is measurably false and this is the session's most reusable finding. The six event registries do not disagree: live-ledger minus schema, and typed-models minus schema, are both empty. `audit_event_schemas` already holds the coupling — but its only caller is a unittest, not a `gz validate` scope, which is why the protection was invisible enough to be re-litigated.

## Decisions Made

- [operator-ruled] Work all four authorized buckets (operator verbatim 2026-07-26, booked via `gz handoff authorize`, session 7dd80db9): "GHI #615 cuts 2 and 3, Then #581, then #641, Steps 3 and 4 (the two cheap judgments), Fix the two handoff-surface defects".
- [operator-ruled] Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written, and over landing the extractor fixes as a separate prior commit.
- [operator-ruled] Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — an honest claim that they are no longer a live authoring surface, without asserting a ledger completion they do not carry.
- [operator-ruled] Scope GHI #581 first and do NOT build — chosen over executing the 6-registry collapse, over building the 6th validator dimension, and over closing the issue unexamined.
- [operator-ruled] Take GHI #641's own strawman naming: `gz brief reconcile` becomes `gz obpi brief-drift`, `gz obpi reconcile` becomes `gz obpi sync`, and the single-verb `brief` namespace goes away.
- [agent-chose] REJECTED directory-prefix containment for the pending-upstream predicate after MEASURING it. It clears the 5 real pending-upstream cases but launders three genuine renames — precisely the defect GHI #581 names. Naming the file in the owner's Allowed Paths clears them through the existing predicate with no engine change.
- [agent-chose] Scoped the strict flip to non-terminal briefs rather than flipping `parse_brief`'s default, which would have broken every one of the 519 legacy terminal reads.
- [agent-chose] Wrote `verification:` as command lines only, after PROVING it behaviour-preserving: verb extraction over the filtered lines equals extraction over the whole section for all 146 briefs, and is non-empty for all 146.
- [agent-chose] Repaired the current handoff's Settled Rulings by RE-DERIVING from its predecessor through the fixed parser rather than hand-editing, and verified losslessness first — all 32 rulings preserved, zero entries without an equal-or-fuller counterpart.
- [agent-chose] Did NOT widen `_ruling_key` normalization. My earlier near-duplicate finding was wrong: the narrowness is deliberate and documented — a visible duplicate is harmless, collapsing two distinct rulings drops a booked ruling silently.
- [agent-chose] Ruled the gz-obpi-specify contradiction from the RUNTIME, not taste: `SystemExit(1)` fires before the write, so a failed `--author` leaves no artifact, and the non-author success path prints steps 2-4 verbatim.
- [agent-chose] Rejected making the orientation handoff selection resolve against remote state; it would mean mutating the working tree from a SessionStart hook or reconstructing files from git objects. Caveat the selection instead — no new fetch, no mutation.
- [agent-chose] Did NOT start GHI #641. A 386-reference CLI rename that must land atomically, on a heavily-consumed context, is the risk profile that produces a half-landed rename — the same judgment the predecessor session made about the migration.

## Immediate Next Steps

1. GHI #641 — authorized this session with the naming already ruled, scoped, and NOT started. Rename `gz brief reconcile` to `gz obpi brief-drift` and `gz obpi reconcile` to `gz obpi sync`, dropping the single-verb `brief` namespace. 386 references across roughly 130 files; 172 files excluding handoffs and plans. Must land atomically. Three complications are already mapped: the 60 handoff files and terminal ADR-0.0.37 briefs are sealed and must not be rewritten (`--cli-alignment` exempts terminal briefs and does not scope handoffs); `CHANGELOG.md` and `RELEASE_NOTES.md` carry the strings but are ceremony-authored and must never be hand-edited; and `gz validate --cli-alignment` fail-closes on every unresolvable verb reference, so the doc sweep is the gate, not an afterthought.
2. GHI #581's three actionable items, in place of the rejected collapse — retire `.gzkit/schemas/ledger_events.json` (6 events, all already canonical in `src/gzkit/schemas/ledger.json`, zero runtime consumers, residue of ADR-0.0.37's permanently-withdrawn registry-spine OBPIs, and this issue's own reproduction case); promote `audit_event_schemas` from a unittest-only caller to a `gz validate` scope; reconcile the three hyphenated event names that carry schema entries but no typed model. None is architectural. Full measurement is in the issue comment.
3. The residual 3 allowlist gaps on `OBPI-0.34.0-04` — `src/gzkit/triangle.py`, `src/gzkit/commands/drift.py`, `src/gzkit/commands/common.py` are neither allowed nor denied by that brief, so they are genuine signal rather than a false positive. They belong to the ADR-0.34.0 capstone, not to GHI #615. Note `src/gzkit/commands/common.py` may belong in the test-infra exclusion set alongside `src/gzkit/config.py` and `src/gzkit/tasks.py`; that was not investigated.
4. GHI #615's untouched half — parser sprawl (roughly 14 hand-rolled ADR frontmatter parsers, the dual ReqKind enum collision between `src/gzkit/triangle.py` and `src/gzkit/req_kind.py`, the REQ-ID grammar divergence) and the escalation-keying gap, where `validate_brief_reconcile` still escalates on structural shape rather than lifecycle. Post-migration the keying stops mattering for the 146 but is unchanged in itself.
5. The campaign RULES sequencing. Movement A remains topmost with ADR-0.35.0 at 0/9 and ADR-0.34.0 at 2/5. Steps 1 through 4 are authorized carry-over and defect repair that the campaign refines rather than substitutes for; none is a campaign amendment.

## Pending Work / Open Loops

CARRIED AND UNSTARTED: GHI #641, fully scoped and its naming ruled, deliberately not begun on a spent context.

GHI #581 IS NO LONGER AN IMPLEMENTATION TRACKER FOR THE COLLAPSE. The scoping pass recommends against the 6-to-1 registry collapse on measured evidence and substitutes three small items. The issue's original observation — brief-reconcile cannot see cross-directory couplings or exists-but-dead surfaces — stands and is untouched.

CAMPAIGN LINE 131 IS NO LONGER STALE. The predecessor handoff carried a claim that it records ADR-0.34.0 at 1/5; verified this session at 2/5, with an operator-ratified correction already recorded at line 270. That open loop is discharged and should stop being carried.

TWO RESIDUAL TRUNCATED SETTLED RULINGS survive the repair — they are truncated in the predecessor itself and not recoverable at that depth. They read 'Escalation should key on lifecycle rather than on frontmatter shape' and 'Dimension-aware Draft scoping: a Draft brief does NOT gate on its own'. Both are recoverable from the 20260725T110348Z handoff if wanted.

THE SPEC-TEST DRIFT ADVISORY stands at 2030 findings, unchanged in substance by this session.

## Verification Checklist

`git log --oneline -6` (expect `8dba6a218`, `32489b83a`, `e84e6a85b`, `e5494fd32`, `72f65a7aa`);
`git status --short --branch` (expect a clean tree level with origin/main);
`uv run gz check` (expect exit 0 — capture to a file rather than piping, since a pipe reports the filter's exit and not the verifier's);
`uv run gz validate --brief-structure` (expect exit 0 — the new fail-closed gate);
`uv run gz validate --brief-reconcile` (expect exit 0);
`uv run gz cli audit` (expect 131/131 commands fully covered);
`uv run -m unittest -q` (expect 7474 or more OK);
`uv run gz obpi lock list` (expect no active locks);
`gh issue list --state open` (expect 13 open).

To confirm the migration is real rather than merely green, count structured briefs: expect 149 of 668 parsing as BriefStructure, 519 legacy, and every one of the 519 carrying a terminal status. To confirm the new gate discriminates, give a Draft brief frontmatter without allowlist/reqs/verification and expect `--brief-structure` exit 3; the brief-structure negative control in the QC registry asserts exactly this.

To confirm the handoff truncation fix, parse a predecessor with a wrapped ruling and check the operator's verbatim words survive: parse_decisions on the 20260726T004802Z handoff must return the patch-release ruling with its session id intact.

## Evidence / Artifacts

Session commits, all on main and pushed: `72f65a7aa` (fix(brief-reconcile): read row semantics before calling a citation dead), `e5494fd32` (feat(brief-structure): enforce the schema that shipped and was never used), `e84e6a85b` (fix(handoff): stop truncating a wrapped ruling to its first line), `32489b83a` (fix(gz-obpi-specify): rule the workflow contradiction against the runtime), `8dba6a218` (fix(orientation): caveat the handoff selection when the clone is behind).

Runtime surfaces changed: `src/gzkit/governance/brief_reconcile.py`, `src/gzkit/governance/trust_audits/brief_structure.py`, `src/gzkit/governance/trust_audits/__init__.py`, `src/gzkit/governance/trust_audits/_qc_negative_controls.py`, `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/commands/quality.py`, `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/quality.py`, `src/gzkit/qc_binding.py`, `src/gzkit/handoff_api.py`, `scripts/session_orientation.py`, `scripts/migrate_brief_frontmatter.py`.

Tests changed: `tests/governance/test_brief_reconcile.py`, `tests/governance/test_brief_structure_scope.py`, `tests/governance/test_handoff_api.py`, `tests/scripts/test_session_orientation.py`, `tests/cli/test_validate_registry_parity.py`, `tests/commands/test_brief_reconcile.py`, `tests/commands/test_skills.py`.

Docs and skills: `docs/user/manpages/validate.md`, `.gzkit/skills/gz-obpi-specify/SKILL.md`.

Representative repaired briefs (non-terminal only): `docs/design/adr/foundation/ADR-0.0.42-storybook-doctrine/obpis/OBPI-0.0.42-03-storybook-validator.md`, `docs/design/adr/foundation/ADR-0.0.43-ddd-domain-cascade/obpis/OBPI-0.0.43-06-domain-cascade-validators-check-pipeline.md`, `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/obpis/OBPI-0.0.45-01-cli-mode-density-doctrine.md`, `docs/design/adr/foundation/ADR-0.0.52-artifact-staleness-propagation/obpis/OBPI-0.0.52-04-trigger-wiring-and-atomic-transactions.md`, `docs/design/adr/foundation/ADR-0.0.55-package-import-direction-invariant/obpis/OBPI-0.0.55-01-author-layer-order-manifest.md`.

ARB receipts, final run: `arb-step-unittest-c51052fd53cf45a7b665d4cf9bd89c67`, `arb-ruff-fc089d9cef044a32903173300351c1cb`, `arb-step-typecheck-cc8b9dfb9cc8487bab5d34223bead2f8`. GHI #615 landing run: `arb-step-unittest-140f6f740fdd42318e89496841fa38e6`, `arb-ruff-fe44c9bab90e42da8ded1354ee07332c`, `arb-step-typecheck-938e54cd8fcd40d8a3a883f2f5715ff6`.

Issue comments posted: GHI #615 (cuts 2+3 outcome), GHI #581 (scoping pass and recommendation against the collapse).

Skills wielded: `.claude/skills/gz-session-handoff/SKILL.md`. Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`. Predecessor: `.gzkit/handoffs/20260726T023530Z-steps-1-3-landed-615-migration-unstarted.md`.

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
