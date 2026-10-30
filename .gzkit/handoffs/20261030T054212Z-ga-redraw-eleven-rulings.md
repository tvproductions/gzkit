---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-30T05:42:12Z'
agent: claude-code
session_id: 1250b9d4-92de-4a19-9f62-75c19adc6c5c
continues_from: .gzkit/handoffs/20261029T095729Z-step-back-rulings-ga-redraw-begun.md
---

## Current State Summary

The general-arrangement redraw (exit item 11, under RO-0) advanced through intake, the catalog's organization, catalog to work package, release and the Release Package, the ADR's and the PRD's roles, legacy migration and work selection. Eleven operator rulings were recorded in docs/governance/harbor-pilotage-candidate-2026-10-15.md § Rulings of 2026-10-29, each with an insight and its own commit (77ad1f6ff through 13eccb880, all pushed, gz check passing on each). Coupled texts were amended in the same commits: requirements-model.md (records table, decisions 2 and 9, § 5, § 7, outcome lifecycle, maxim-17 row), harbor-ro4-release.md (rulings 2, 6, 7, tranche 1), harbor-ro8-in-flight-work.md (ruling 1, act 3) and RO-11's row. No code changed. No tag is hung, no work package is commenced and no finding awaits buy-back; the mx-session lock is held by claude-code-fe40d249 at about 1410 of 1440 minutes, so the lease needs the operator's gz mx renew or a release decision.

## Important Context

The operator works one question at a time and wants A/B/C with a recommendation for bounded choices; each ruling is booked verbatim into § Rulings of 2026-10-29, recorded with gz insights remember --source operator, and committed alone with the Task: TASK-ro0-contract-amendment-scope-freeze trailer. Research the operator asked for (intake approaches: Scrum backlog, upstream Kanban, Shape Up, dual-track/SAFe funnel, ISO/IEC/IEEE 29148, aviation deferred defects) was from the agent's knowledge, not fetched. The intake door set is now five: pool pull, R&D sign-off, deferred finding (at handback, to its owning outcome), the operator's word, and an accepted ADR. The gz-obpi-pipeline § Work selection canon is verbatim AGENTS.md corpus doctrine and still states ascending ADR order; it changes through gz-content-remember when RO-4 lands data/catalog/releases.json. The rendition-lineage and two-need catalog-coverage advisories in gz check come from the QC binding's negative-control fixtures (_qc_negative_controls.py, NCSurface.md), not from defects. The remaining ledger.jsonl change in the tree is the commit hook's mx_contract_amended rows, swept by git-sync.

## Decisions Made

- [operator-ruled] Intake: a pool entry stays an intention until pulled; an R&D disposition and the operator's word enter the catalog as queued outcomes (verbatim: "yes, but let's do some homework too: what common and successful approaches?").
- [operator-ruled] A deferred finding stays on the list of discrepancies while the hangar is open and is handed to its owning outcome at the handback (verbatim: "yes, hand it to the owning outcome").
- [operator-ruled] Every catalog outcome requires its source, the 29148 source attribute and upward trace leg (verbatim: "yes, require the source").
- [operator-ruled] The catalog has exactly three levels: family H, capability H1 (never carries work), outcome H1.4 (verbatim: "A").
- [operator-ruled] Gate 5 is attested once at the work package's close, and that close moves the outcome (verbatim: "A").
- [operator-ruled] A Release Package plans in outcomes and repair packages; release_recorded names the closed work packages and issues (verbatim: "a").
- [operator-ruled] The 0.35.0 Release Package is the outcomes of all twenty items, the eleven attested carrying legacy evidence; RO-4 no-backfill stands with 0.35.0 its one exception (verbatim: "A").
- [operator-ruled] An ADR leads to work through an outcome, a fifth intake door, its source and governed_by the ADR (verbatim: "A").
- [operator-ruled] Unstarted feature ADRs 0.36.0, 0.37.0 and 0.39.0 stay decision records; briefs withdraw as superseded; REQs enter as queued outcomes once each ADR is accepted (verbatim: "A").
- [operator-ruled] Completed ADRs 0.0.2, 0.0.71 and 0.0.74 stand as legacy evidence with no closeout, status mapping to accepted (verbatim: "A").
- [operator-ruled] Work selection: the lowest-version open Release Package first, readiness from depends_on, the operator's recorded pull order; ascending ADR order retired explicitly (verbatim: "a").
- [agent-chose] The gz-obpi-pipeline canon change waits for RO-4's Release Package store, since the new rule has nothing to select by before then; the operator may move it.

## Immediate Next Steps

1. Ask the operator to renew the mx-session lease (gz mx renew) or rule on releasing the lock.
2. Continue the redraw with its remaining components, one question at a time: the contract field the rails and requirements-model § 6 rely on but no schema holds; repair order held as a GitHub issue versus RO-5 ruling 1's repair work package naming issues; the terms drift (feature area, family, outcome; REQ state versus proof); mandate 3 and exit item 3's feature-area registry wording.
3. Name the major state changes at each process's edges, the handoff's bookends, and redraw the general arrangement as one clear description with the drawing beside it.
4. Ask the operator to grade the three-level-brief finding under the induction freeze.
5. Specify RO-11 to its widened scope (five intake doors, the Release Package selection rule) and RO-13 with the operator; then land the major-states Mermaid source and regenerate the artifact.

## Pending Work / Open Loops

The gz-obpi-pipeline § Work selection canon change through gz-content-remember, due when RO-4 lands releases.json. The capability record's store and the tightened outcome code pattern in src/gzkit/schemas/catalog_outcomes.json. gz wp close emitting outcome_transitioned. A required source field and gz validate --catalog refusal. gz-rnd disposition row 1 rerouted from ADR/OBPI to the catalog. Withdrawal of the 22 briefs of ADR-0.36.0, 0.37.0 and 0.39.0 and the legacy-evidence mapping of 0.0.2, 0.0.71, 0.0.74 and 0.35.0's attested eleven, worked under RO-8 and RO-11. Campaign plan update after drydock exit (standing ruling).

## Verification Checklist

uv run gz handoff resume; git log --oneline 7572b452c^..13eccb880 plus 77ad1f6ff through 6459f99f9; git rev-list --left-right --count origin/main...HEAD; uv run gz obpi lock list; grep -n 'Rulings of 2026-10-29' docs/governance/harbor-pilotage-candidate-2026-10-15.md; uv run gz handoff rulings --search 'Release Package'; uv run gz check.

## Evidence / Artifacts

`docs/governance/harbor-pilotage-candidate-2026-10-15.md`, `docs/governance/ieee/requirements-model.md`, `docs/governance/harbor-ro4-release.md`, `docs/governance/harbor-ro8-in-flight-work.md`, `.gzkit/insights/agent-insights.jsonl`

## Settled Rulings

1839 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
