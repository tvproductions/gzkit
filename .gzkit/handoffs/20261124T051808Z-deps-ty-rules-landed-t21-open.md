---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-24T05:18:08Z'
agent: claude-code
session_id: 2ad7357b-ad76-41f7-bc78-dab16572ea9f
continues_from:
- .gzkit/handoffs/20261123T215050Z-drydock-taxonomy-t15-t20-ruled-t21-open.md
- .gzkit/handoffs/20261123T224728Z-session-exit-bookmark.md
- .gzkit/handoffs/20261124T001657Z-session-exit-bookmark.md
---

## Current State Summary

The drydock taxonomy walk has not moved since the predecessor: T21 is still unruled (docs/governance/drydock-taxonomy.md section 8, row T21, "the census's reading, unruled") and is where the walk resumes. Between the predecessor and this handoff, sessions 91adc806 and e48a7b2f (each left only a mechanical exit bookmark, 20261123T224728Z and 20261124T001657Z, both folded here) and this session 2ad7357b did dependency and type-checker work, 17 commits from ff650c5ca to 2b2bd9408, all on main and pushed: the lock and floors upgraded (49e0f48fd), toolchain defects repaired (f011b9342), the MX lease renewed (be013d0c3), tautological-test debt drained and its four waivers withdrawn (70903c37e, 80926468e), and ty rules adopted one per commit (a10cf8720, b3d2444c3, 1c7da48a8, 78dbf676f, 8212725a4, 68cfb7848, da8360f8a, fa49a3d71). This session found unresolved conflict markers at pyproject.toml line 335 left by a prior Claude session (Codex repaired them before this session began), then verified and landed the truthiness-test-of-none-union adoption (fa49a3d71): two stale guard canaries rebound and reviewed on the operator's word, the cognitive-complexity baseline lowered to exact scores, and canonical history synced. On the operator's "fix this" it then checked every one of the 560 sites that rule flags on the parent commit and found that plain "x is not None" rewrites changed behaviour for empty values; 2b2bd9408 restores exact truthiness at 116 sites and keeps the rest only on a stated closed fact, with 0 sites unproven. uv run gz check passed on the staged tree and uv run gz test ran 14248 tests OK (4 skipped). The tree is clean and in sync with origin/main apart from this handoff and one uncommitted insight record.

## Important Context

Safe mode is still open under docs/governance/harbor-pilotage-candidate-2026-10-15.md: most guards are advisory, the slow alarms are off, and lint, the fast static checks, gate5_invariants, the ledger through gz verbs and operator PII still bind. The operator ruled the taxonomy walk one decision per question ("one-at-a-time please"); do not batch rows. T21 is a mechanism row: RP-13 rulings 5 and 8 key MEL defaults on a control role label, and alarm and tripwire mean opposite things in the census (census-code-controls.md lines 66 to 71, never ruled) and in RP-10 (in force, followed by the doctrine alarm test and gzkit.mx.alarms); the census classifies by purpose in normal operation, RP-10 by behaviour while out of service. The MX lease was renewed at 2026-11-23T23:24Z for 1440 minutes, so it lapses near 2026-11-24T23:24Z, not the 18:21Z the predecessor gives. Shift turnover, read this session: uv run gz wp tag show --all reports no tag issued; uv run gz wp runs reports no work package in flight; uv run gz obpi lock list shows only mx-session, held by MX session 57346836-b4d2-414f-b5b1-04898f13456f; the buy-back record is unbuilt, so the contract's list of discrepancies stands in for findings awaiting buy-back. Lesson booked as insights: adopting a ty rule that rewrites conditions needs the rule's own diagnostic list on the parent commit and a site-by-site equivalence proof, because truthiness-test-of-none-union fires only where the non-None part of the type can itself be falsy. The ghi-triage, hook and chore scripts have mirrors: edit .gzkit/skills and the src/gzkit/hooks/scripts templates, then run uv run gz agent sync control-surfaces.

## Decisions Made

- [operator-ruled] Reviewed the two guard canaries the truthiness adoption staled, astral-discipline-deferred-annotations and requirements-catalog-work-packages, after the guard diffs were shown and each mutant was killed on an isolated copy; booked through gz canary review (verbatim: "ok").
- [operator-ruled] Every truthiness rewrite fa49a3d71 left unchecked is to be checked and repaired (verbatim: "fix this").
- [operator-ruled] The PLC0415 suppression-route question (declare deferred modules under banned-module-level-imports, name each carve-out, or wait for 3.15) is set aside (verbatim: "ok, disregard").
- [operator-ruled] Author a fresh handoff superseding the predecessor and git sync (verbatim: "fresh handoff + git sync").
- [agent-chose] Restored exact truthiness by default at every non-equivalent site rather than arguing reachability site by site, keeping "is None" only on a closed fact: an ast identifier field, an all-non-empty StrEnum, a ty-narrowed non-empty str, a regex group or Field pattern that cannot match empty, or "x is not None and P(x)" with P falsy on the empty value. This kept both reviewed canaries' bindings unchanged.
- [agent-chose] Recorded three defect insights rather than repairing them in flight: the TestGhIssueCreatedAt hexagon-test findings, the OBPI-0.39.0-01 and -02 briefs omitting sensitivity (brief edits are operator-initiated), and 1049 bare '# noqa: PLC0415' suppressions that name no carve-out.

## Immediate Next Steps

1. Put T21 to the operator again: alarm and tripwire keep RP-10 senses; the census role set stays the MEL role field with its colliding names renamed (proposed interlock for the census tripwire, annunciator for the census alarm), so a MEL entry carries a role and an out-of-service behaviour (option A, recommended); B the census senses win; C drop the census role set. Record the ruling as W44 in docs/governance/drydock-taxonomy.md section 9 and mark the row in section 8.
2. Continue in table order, one decision per question: T22, T23, T24, T25, T26, T27, T28, T29, T30, T31, T32, T33, T34, T35, T36, T37, T39, committing after each ruling.
3. Renew the MX lease through the gz-mx skill on the operator's word before it lapses near 2026-11-24T23:24Z.
4. When the rulings are done, draft the execution plan: the contract amendment and the per-package revisions T10 (W35) routes, in an order the operator rules; then open the documentation R&D run through gz-rnd (W15).
5. Ask the operator whether the false settled marks in the committed handoff 20261122T051329Z are corrected or kept as the record of that defect.

## Pending Work / Open Loops

Unruled naming rows carried from the predecessor as draft recommendations, to be put singly: T22 RP-12 maps persona files to positions in the crosswalk data and the reviewer position is inspector with spec and quality sub-roles (the SingleDriver unreachable arm is GHI #1353); T23 the side is construction and its package the work package, store kind delivery renamed work, the maintenance visit not a third kind; T28 the passage log closed as a dated record, the maintenance record its successor, no backfill; T30 page file names kept, every sub-id cited with its package prefix, RP-0 specification is the contract; T31 one qualification rule, record-level senses win; T32 supersession recorded forward through --settled, never by editing rulings.jsonl; T33 pool entries take a record id such as POOL-nnnn-slug with ADR-pool.slug as alias (the POOL prefix is the agent proposal, not canon); T35 the no-separate-document rulings and the feature package declared compatible; T37 page-scoped ruling numbers stay citations, not records. GHI #1356 stays open as the record of the survey findings; its unswept parts are the widened chore first sweep after the drydock. GHI #1304 owns the two-level marker and banners (T17). Defects that gz mx exit will meet at full strength, each recorded in .gzkit/insights/agent-insights.jsonl: the TestGhIssueCreatedAt tests in tests/commands/test_insights_recurrence.py fail the hexagon-test rules; the OBPI-0.39.0-01 and -02 briefs omit sensitivity while their allowed paths overlap registered security surfaces. Also recorded, route set aside by the operator: 1049 of 1140 '# noqa: PLC0415' suppressions name no carve-out, against .gzkit/rules/pythonic.md, and 2557 PLC0415 findings are held in data/ruff_baseline.json. Ten default-ignored ty rules remain unadopted after the deps pass; missing-type-argument is repaired at 684 sites but not yet adopted (da8360f8a).

## Verification Checklist

- uv run gz handoff resume, then read the drydock-taxonomy.md section 8 row for T21 to confirm it is still unruled.
- git rev-list --left-right --count origin/main...HEAD reads 0 0 after the sync.
- uv run gz obpi lock list shows mx-session as the only lock, and its elapsed time is inside the 1440-minute lease.
- uv run gz wp tag show --all and uv run gz wp runs for the shift-turnover review.
- uv run gz handoff rulings --search "one-at-a-time" returns the walk's one-decision ruling.

## Evidence / Artifacts

- `docs/governance/drydock-taxonomy.md` (section 8 table, section 9 rulings W1 to W43)
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md` (the safe-mode contract)
- `.gzkit/handoffs/20261123T224728Z-session-exit-bookmark.md` and `.gzkit/handoffs/20261124T001657Z-session-exit-bookmark.md` (folded exit bookmarks)
- `.gzkit/insights/agent-insights.jsonl` (this session's improvement and defect records)
- `data/guard_canaries.json` (the two rebound canaries)
- `data/cognitive_complexity_baseline.json` and `data/waiver_ratchet_registry.json` (the exact-score adjustment)
- `pyproject.toml` (ty truthiness-test-of-none-union at error)
- Commits fa49a3d71 and 2b2bd9408 on main, pushed to origin.

## Settled Rulings

2521 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
