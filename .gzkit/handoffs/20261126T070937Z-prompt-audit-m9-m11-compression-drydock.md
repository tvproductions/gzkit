---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-26T07:09:37Z'
agent: claude-code
session_id: 5a6dbb4a-92c0-416e-bd7e-0692c29c72e4
continues_from: .gzkit/handoffs/20261126T045119Z-prompt-audit-m8-dep-currency.md
---

## Current State Summary

Session 5a6dbb4a resumed from 20261126T045119Z-prompt-audit-m8-dep-currency.md and walked prompt-audit M9, M10 and M11. All work is on main and pushed, through 9e36e1c52.

Closed, each confirmed by an independent reviewer subagent:
- #1373 (M9): gz-tidy rows 123 and 132 follow the exit-3 verdict (a4bb545bf), and the manpage index row is fixed (d0795826c). The fence tests/policy/test_tidy_exit_status_is_the_verdict.py was narrowed by operator ruling to the shapes it judges (79b7a2067, 93ac9cccb, 02514119c, 0a92ac44b, bde5964e5). Six review rounds; final CONFIRMED.
- #1374 (M10): 35 consumers of two facts the 2026-09-17 AGENTS.md compression (8ecb176f0) moved or dropped. The canonical invocations moved to gz-arb (S23), and the fix() precedent criterion was dropped by ruling (S14). ghi-triage's route() no longer labels a GHI ambiguous by precedent. Pipeline controls S5-016 and S4-170 declare their rewording. Fence tests/policy/test_moved_and_dropped_facts_not_restated.py. Commits 2fc4faaec..e64f08259. Three review rounds.
- #1375 (M11): about 45 consumers cited AGENTS.md numbering the same pass dropped. They now cite by section and quote the current rule. M13 (S24) is absorbed. Pipeline controls S4-045 and T-006 reworded. Fence tests/policy/test_agents_md_numbering_not_cited.py. Commits 7a291cd02, aeec877c5, 89fb60ac0, d37be8e5b. Three review rounds.

Drydock: a new discrepancy under RP-7, the compression routine's consumer blindness, is graded blocks return to service (bee16db5e, 9e36e1c52; mx_contract_amended booked twice).

The mx-session lease was renewed at session start; ACTIVE at 107 of 1440 minutes.

## Important Context

Safe mode is still open (docs/governance/harbor-pilotage-candidate-2026-10-15.md). Every act is one commit with a Task: trailer. A finding raised after induction is graded onto § List of discrepancies under its owning order, never added as a new order.

Shift turnover, reviewed 2026-11-26:
- gz wp tag show --all: "No tag has been issued."
- gz wp runs: "No work package is in flight."
- gz obpi lock list: mx-session ACTIVE (renewed this session).
- The buy-back record is not built.

Mechanics learned:
- BSD grep fails silently on multibyte characters such as the em dash under 2>/dev/null, so two sweeps returned a false empty. Sweep with Python.
- grep -v test also drops every line containing "attestation".
- A pipeline stage reference is rendered from data/obpi_pipeline_control_inventory.json. To change one: edit the control's delivered_span, add reworded {text, reason}, re-render with render_served_set(load_inventory(root)), repin the sha256 in src/gzkit/pipeline_procedure.py, and bump gz-obpi-pipeline.
- A chore directory with no CHORE.md classifies package_only, and sync never copies it. Its src/gzkit copy is the authored file (owasp-top10-2025-scan).
- A commit message containing "close #N" is refused by the closing-keywords pre-push hook. Reword with a soft reset of the unpushed commits.
- gz arb red --commit reads undriven when the behavior change is a deletion or when the commit's hunks are docstrings and pins; say so rather than add string tests.
- Prose fences: per the M9 ruling, a fence states exactly the shapes it judges, and its residuals go to #1370. Each M10 and M11 review round still found misses the fence and the sweep did not; the reviewer's concept sweep is the real coverage.

## Decisions Made

- [operator-ruled] Renew the mx-session lease, then M9 (verbatim: "renew the lease, then M9").
- [operator-ruled] The M9 fence is narrowed and says so; residuals go to #1370; #1373 closes with the review on record (verbatim: "a").
- [operator-ruled] Close #1373 after its review, then M10 (verbatim: "ok, close it after the review, then M10").
- [operator-ruled] M10 reach: one GHI for every consumer, the triage routing change included (verbatim: "A").
- [operator-ruled] The compression routine's consumer blindness is a new drydock item (verbatim: "this is a major flaw in our compression skill/routine then, it is a new dry dock item").
- [operator-ruled] M11 started (verbatim: "M11 now").
- [operator-ruled] RP-7's compression-consumer line is graded blocks return to service (verbatim: "Blocks return to service").
- [agent-chose] ghi-triage keeps reporting the 60-day fix() count as information (header and precedent_60d); only routing on it was removed, so the JSON contract stands.
- [agent-chose] Dated records stay as written: docs/rnd, dated analyses and appraisals, campaign measurements, the rendered obpi-pipeline-control-rationale.md, and lift anchors. Dated lineage lines get the 2026-09-17 step appended instead.
- [agent-chose] The active campaign plan's line 297, which repeats the precedent claim inside a dated measurement, was put to the operator, not edited.
- [agent-chose] The M11 fence exempts src/gzkit/handoff_api.py by name: its parser comments name Always #13 as text the handoff corpus still holds.

## Immediate Next Steps

1. Confirm CI on 9e36e1c52 or its git-sync follow-up: check (ubuntu-latest) and check (windows-latest) should pass. full-strength-report stays red on the demoted hangar debt (#1262).
2. M12 in map order, per the Revised mechanism map in docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md: the campaign name left AGENTS.md on 2026-10-10 (64f35c53e), and gz-intent-trace still says the Magna Carta campaign is named in § Operator Doctrine (S25). M13 is absorbed into #1375 [settled]; skip it.
3. RP-7's new blocks-return-to-service line: the compression routine (gz-context-diet, the instructions-files-diet chore, gz content compose) must name and repair or record every consumer of a fact it moves or drops, with a witness, before RP-7 closes. Put its design to the operator before building.
4. Continue M14 onward in map order, stopping after each.

## Pending Work / Open Loops

- #1370: the form of the prose fences. M4, M7, M8, M9, M10 and M11 now each carry a witness of this form, with residuals posted for M9, M10 and M11.
- #1371: package copies are never byte-checked against canon; the owasp orphan chore directory is an instance.
- #1372: gz init's template stays on language: system.
- Insight: src/gzkit/sync_surfaces.py:155-160 writes the retired 50/600 size thresholds into the generated manifest, an M7 leftover, unrouted.
- Insight: the control-surface-skill-rule-reachability chore's below-the-bar findings are never routed.
- OBPI-0.35.0-20, pending, must name S5-016, S4-170, S4-045 and T-006, alongside the 18 named on 2026-11-25, in its completing attestation (insights recorded).
- The active campaign plan build-to-1.0-campaign-2026-09-20.md:297 repeats "the precedent query AGENTS.md § Defect-fix routing prescribes" inside a dated measurement; the operator's to amend or leave.
- Carried from the prior handoff: #1361, #1363 and #1365 filed, not worked; check whether #1346 absorbs M25, M28 and M40; M32 needs the operator's attestation words; the leftovers M11, M13, M14 and M24 (M11 and M13 now done); after the audit, the conceptual-model R&D frontier, the DDD-discipline R&D run, two stale worktrees under .claude/worktrees, and the frontier-model-card-currency chore.

## Verification Checklist

- gh issue view 1373 --json state, then 1374 and 1375: all CLOSED.
- uv run -m unittest tests.policy.test_tidy_exit_status_is_the_verdict tests.policy.test_moved_and_dropped_facts_not_restated tests.policy.test_agents_md_numbering_not_cited tests.skills.test_ghi_triage_routing: OK.
- uv run -m unittest tests.governance.test_pipeline_procedure_render tests.test_pipeline_procedure: OK; the stage pins match.
- uv run gz obpi lock list: mx-session ACTIVE.
- gh run list --limit 4: CI on the newest main commit.
- git rev-list --left-right --count origin/main...HEAD: 0 0.

## Evidence / Artifacts

- `tests/policy/test_tidy_exit_status_is_the_verdict.py`
- `tests/policy/test_moved_and_dropped_facts_not_restated.py`
- `tests/policy/test_agents_md_numbering_not_cited.py`
- `tests/skills/test_ghi_triage_routing.py`
- `.gzkit/skills/ghi-triage/scripts/triage.py`
- `.gzkit/skills/gz-tidy/SKILL.md`
- `data/obpi_pipeline_control_inventory.json`
- `src/gzkit/pipeline_procedure.py`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md`

## Settled Rulings

2578 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
