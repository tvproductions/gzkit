---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-07-26T09:41:59Z'
agent: claude-code
session_id: 7dd80db9-500f-426b-9d05-989e6c2775d5
continues_from: .gzkit/handoffs/20260726T091905Z-ghi-615-schema-enforced-641-scoped.md
---

## Current State Summary

Supersedes `20260726T091905Z`, which said GHI #641 was scoped-but-not-started — that stopped being true one commit later. Resumed `20260726T023530Z` under operator authorization booked verbatim as "GHI #615 cuts 2 and 3, Then #581, then #641, Steps 3 and 4 (the two cheap judgments), Fix the two handoff-surface defects" (session 7dd80db9). THE AUTHORIZED QUEUE IS NOW EMPTY — every item is landed, ruled, or reported. Seven commits on main and pushed, ending at `4307d10c7`. Tree clean and level with origin/main, no active OBPI lock, no in-flight pipeline, 12 GHIs open after #641 closed. GHI #615 cuts 2 and 3 landed; #641 landed and closed; #581 scoped with a recommendation AGAINST the work it was tracking; the two judgment calls ruled; the handoff truncation defect fixed and its corpus damage repaired.

## Important Context

FIRST, the recurring shape across four of this session's five fixes: a checker reading one surface while ignoring the adjacent surface that already answers its question. The Discovery extractor collected backtick paths without reading what the row said about them. `missing_in_brief` read Allowed Paths and ignored Denied Paths. Coverage attribution substring-matched REQ ids instead of reading `@covers`. The orientation script fetched remote state and rendered it beside a working-tree selection without relating them. Every fix was to make the checker read what was already there. Expect more of this family.

SECOND, migrating a corpus ARMS a gate. `validate_brief_reconcile` skips legacy briefs, so the 146-brief migration flipped them from skipped to escalated and armed 34 dormant findings at once. The arming is the risk, not the edit. Any future corpus migration here has the same shape.

THIRD, the doc-coverage scanner cannot see through a helper, and this cost a rework cycle on #641. `discover_commands` binds EVERY `_register_*` function parameter to an empty prefix and never follows the call graph, so a helper receiving a NESTED subparsers action is discovered as a top-level command. Registering inline — as every other `obpi` subcommand already does — is the fix. Read `src/gzkit/doc_coverage/scanner.py` around the `_register_` parameter binding before adding any nested-parser helper.

FOURTH, a string sweep cannot see argument lists. `runner.invoke(main, ["brief", "reconcile", ...])` matches no search for the verb string. Any future verb rename needs a second pass over `tests/` and `features/` for the list form.

FIFTH, `gz obpi brief-drift --apply` writes the verb name INTO briefs as amendment-annotation prose. A stale verb there would propagate into governance artifacts as attested text, and NO gate covers it. Found by reading the command, not by a check firing.

SIXTH, sealed-surface scoping is the constraint that shaped both large changes. 514 terminal briefs stayed legacy; 60 handoffs and 28 terminal briefs kept the old verb strings. A repo-wide sed on either would have rewritten attested artifacts.

SEVENTH, GHI #581's premise was measurably false and the scoping pass recommends AGAINST the work the issue was tracking. The six event registries do not disagree — live-ledger minus schema, and typed-models minus schema, are both empty. `audit_event_schemas` already holds the coupling, but its only caller is a unittest rather than a `gz validate` scope, which is why the protection was invisible enough to be re-litigated.

## Decisions Made

- [operator-ruled] Work all four authorized buckets (operator verbatim 2026-07-26, booked via `gz handoff authorize`, session 7dd80db9): "GHI #615 cuts 2 and 3, Then #581, then #641, Steps 3 and 4 (the two cheap judgments), Fix the two handoff-surface defects".
- [operator-ruled] Fix the engine first, then repair genuine drift — chosen over rewriting 22 briefs to satisfy the scrapers as written.
- [operator-ruled] Seal the 8 pre-frontmatter ADR-0.0.1 briefs as `archived` rather than `Completed` — no ledger completion is asserted.
- [operator-ruled] Scope GHI #581 first and do NOT build — chosen over executing the collapse, over building the 6th validator dimension, and over closing it unexamined.
- [operator-ruled] Take GHI #641's own strawman naming, then execute it (operator verbatim 2026-07-26: "refresh it" followed the landing; the rename itself was authorized by the strawman ruling and the follow-up "okay, so what about 641?").
- [agent-chose] REJECTED directory-prefix containment for the pending-upstream predicate after MEASURING it: it clears the 5 real cases but launders three genuine renames, which is the defect GHI #581 names.
- [agent-chose] Registered `brief-drift` INLINE after the helper form was discovered as a top-level command — matching the existing convention rather than teaching the scanner to follow call graphs.
- [agent-chose] Left the two skill directory slugs (`gz-brief-reconcile`, `gz-obpi-reconcile`) unrenamed. Content and `gz_command` point at the new verbs and `gz skill audit` passes, but renaming triggers delete-on-retire across four mirror roots — wider than the ruled scope. Flagged on the issue.
- [agent-chose] Left `gz frontmatter reconcile` alone: a third `reconcile`, but on a different artifact, so outside the same-artifact collision #641 named.
- [agent-chose] Reverted two chore `proofs/**` logs the rename sweep had touched — `runtime_state` per the surface classifier, not content to rewrite.
- [agent-chose] Did NOT widen `_ruling_key` normalization. My earlier near-duplicate finding was wrong: the narrowness is deliberate — a visible duplicate is harmless, collapsing two distinct rulings drops a booked ruling silently.
- [agent-chose] Repaired the predecessor handoff's Settled Rulings by RE-DERIVING through the fixed parser rather than hand-editing, verifying losslessness first.

## Immediate Next Steps

1. NOTHING IS AUTHORIZED. The queue this session worked is empty; every advised step below needs an operator ruling before execution.
2. GHI #581's three actionable items, which replace the collapse the issue was tracking — retire `.gzkit/schemas/ledger_events.json` (6 events, all already canonical in `src/gzkit/schemas/ledger.json`, zero runtime consumers, residue of ADR-0.0.37's permanently-withdrawn registry-spine OBPIs, and the issue's own reproduction case); promote `audit_event_schemas` from a unittest-only caller to a `gz validate` scope; reconcile the three hyphenated event names that carry schema entries but no typed model. None is architectural. Full measurement is in the issue comment.
3. The campaign is topmost absent a ruling. Movement A: `ADR-0.35.0-canon-entry-corpus-landing` at 0/9 and the `ADR-0.34.0-foundation-sunset` capstone at 2/5 (demote the unstarted foundations to pool, backfill `foundation_grandfathered`, `gz ontology resense`, wire the permanent `--taxonomy` gate into `gz check`).
4. Two skill slugs name retired verbs — `gz-brief-reconcile` and `gz-obpi-reconcile`. Content is correct and `gz skill audit` passes, but `tool-skill-runbook-alignment.md` Invariant 2 is the rule that eventually bites. Renaming means delete-on-retire across four mirror roots plus every slug reference.
5. An unfiled defect worth a GHI: `gz handoff create` without `--continues-from` silently writes a chain-less handoff that carries ZERO settled rulings, and nothing gates it. Hit live this session — the first attempt at the predecessor handoff dropped all 32 booked rulings and validated clean. Same decay class as the truncation fixed in `e84e6a85b`: one drops part of a ruling, the other drops all of them.
6. GHI #615's untouched half — parser sprawl (roughly 14 hand-rolled ADR frontmatter parsers, the dual ReqKind enum collision, the REQ-ID grammar divergence) and the escalation-keying gap, where `validate_brief_reconcile` still escalates on structural shape rather than lifecycle.

## Pending Work / Open Loops

THE AUTHORIZED QUEUE IS EMPTY. Unlike every recent predecessor, nothing is carried-and-unstarted.

GHI #581 IS NO LONGER AN IMPLEMENTATION TRACKER for the registry collapse. The scoping pass recommends against it on measured evidence and substitutes three small items. The issue's ORIGINAL observation — brief-reconcile cannot see cross-directory couplings or exists-but-dead surfaces — stands and is untouched.

THE RESIDUAL 3 allowlist gaps on `OBPI-0.34.0-04` (`src/gzkit/triangle.py`, `src/gzkit/commands/drift.py`, `src/gzkit/commands/common.py`) are neither allowed nor denied by that brief, so they are genuine signal. They belong to the ADR-0.34.0 capstone. `src/gzkit/commands/common.py` may belong in the test-infra exclusion set alongside `src/gzkit/config.py` and `src/gzkit/tasks.py`; not investigated.

TWO RESIDUAL TRUNCATED SETTLED RULINGS survive the repair — truncated in their own predecessor and not recoverable at that depth. Recoverable from the 20260725T110348Z handoff if wanted.

AMENDMENT-ANNOTATION PROSE IS UNGATED. `gz obpi brief-drift --apply` writes verb names into briefs as attested text; no check verifies those names resolve.

THE SPEC-TEST DRIFT ADVISORY stands at 2030 findings, unchanged by this session.

## Verification Checklist

`git log --oneline -8` (expect `4307d10c7` at HEAD, then `e1719bcb0`, `8dba6a218`, `32489b83a`, `e84e6a85b`, `e5494fd32`, `72f65a7aa`);
`git status --short --branch` (expect a clean tree level with origin/main);
`uv run gz check` (expect exit 0 — capture to a file rather than piping, since a pipe reports the filter's exit and not the verifier's);
`uv run gz obpi sync --help` and `uv run gz obpi brief-drift --help` (expect both to resolve);
`uv run gz obpi reconcile --help` (expect an invalid-choice error — the verb is retired);
`uv run gz cli audit` (expect 131/131 commands fully covered);
`uv run gz validate --cli-alignment` and `--router-tables` (expect exit 0);
`uv run gz validate --brief-structure` (expect exit 0 — the gate landed this session);
`uv run -m unittest -q` (expect 7474 or more OK);
`uv run gz obpi lock list` (expect no active locks);
`gh issue list --state open` (expect 12 open, #641 now closed).

To confirm the #615 migration is real rather than merely green, count structured briefs: expect 149 of 668 parsing as BriefStructure and every one of the remaining 519 carrying a terminal status.

To confirm the #641 rename left sealed surfaces alone, grep the old verb strings and expect hits ONLY in `.gzkit/handoffs/`, `.claude/plans/`, terminal OBPI briefs, CHANGELOG.md, and RELEASE_NOTES.md.

## Evidence / Artifacts

Session commits, all on main and pushed: `72f65a7aa` (fix(brief-reconcile): read row semantics before calling a citation dead), `e5494fd32` (feat(brief-structure): enforce the schema that shipped and was never used), `e84e6a85b` (fix(handoff): stop truncating a wrapped ruling to its first line), `32489b83a` (fix(gz-obpi-specify): rule the workflow contradiction against the runtime), `8dba6a218` (fix(orientation): caveat the handoff selection when the clone is behind), `e1719bcb0` (superseded handoff), `4307d10c7` (refactor(cli): end the reconcile verb collision).

CLI surfaces renamed: `src/gzkit/cli/parser_artifacts.py`, `config/doc-coverage.json`, `docs/user/manpages/obpi-brief-drift.md`, `docs/user/manpages/obpi-sync.md`, `docs/user/manpages/index.md`.

Runtime surfaces changed this session: `src/gzkit/governance/brief_reconcile.py`, `src/gzkit/governance/trust_audits/brief_structure.py`, `src/gzkit/governance/trust_audits/_qc_negative_controls.py`, `src/gzkit/governance/trust_audits/_qc_nc_entrypoints.py`, `src/gzkit/commands/validate_cmd.py`, `src/gzkit/commands/quality.py`, `src/gzkit/commands/brief_reconcile.py`, `src/gzkit/commands/obpi_stages.py`, `src/gzkit/cli/parser_maintenance.py`, `src/gzkit/quality.py`, `src/gzkit/qc_binding.py`, `src/gzkit/handoff_api.py`, `scripts/session_orientation.py`, `scripts/migrate_brief_frontmatter.py`.

Tests changed: `tests/governance/test_brief_reconcile.py`, `tests/governance/test_brief_structure_scope.py`, `tests/governance/test_handoff_api.py`, `tests/scripts/test_session_orientation.py`, `tests/cli/test_validate_registry_parity.py`, `tests/commands/test_brief_reconcile.py`, `tests/commands/test_obpi_pipeline.py`, `tests/commands/test_pipeline_baseline_verification.py`, `tests/test_doc_coverage.py`, `tests/commands/test_skills.py`.

Skills edited and version-bumped: `.gzkit/skills/gz-obpi-specify/SKILL.md`, `.gzkit/skills/gz-brief-reconcile/SKILL.md`, `.gzkit/skills/gz-obpi-pipeline/SKILL.md`, `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md`, `.gzkit/skills/gz-governance/SKILL.md`.

ARB receipts, #641 landing run: `arb-step-unittest-4e322b109c564fc3ac8ee2df2df484a4`, `arb-ruff-3fa11524c4d64af79550765e2ca71932`, `arb-step-typecheck-27fc5f2e13bf4251b9532d2ebf570338`. GHI #615 landing run: `arb-step-unittest-140f6f740fdd42318e89496841fa38e6`, `arb-ruff-fe44c9bab90e42da8ded1354ee07332c`, `arb-step-typecheck-938e54cd8fcd40d8a3a883f2f5715ff6`.

Issue activity: GHI #615 comment (cuts 2+3 outcome), GHI #581 comment (scoping pass, recommendation against the collapse), GHI #641 CLOSED with evidence.

Campaign: `docs/governance/build-to-1.0-campaign-2026-07-18.md`. Predecessor: `.gzkit/handoffs/20260726T091905Z-ghi-615-schema-enforced-641-scoped.md`.

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
