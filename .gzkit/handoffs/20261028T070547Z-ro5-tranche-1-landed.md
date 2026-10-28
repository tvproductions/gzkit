---
mode: CHECKPOINT
adr_id: null
branch: main
timestamp: '2026-10-28T07:05:47Z'
agent: claude-code
session_id: 09d0691e-76a7-4edd-a07b-7d2ad57a6422
continues_from: .gzkit/handoffs/20261028T063805Z-contractor-kit-funded-rows-2-4-landed.md
---

## Current State Summary

Resumed the contractor-kit handoff on the operator's 'proceed with all four' (booked with gz handoff decide). Step 1: mode-contract compression reviewed; the dropped fail-safe clause restored as rule 0.1.2 (7a6ce8d4d). Step 4: GHI #1278 retroactively reviewed by an independent subagent, NOT CONFIRMED on 8 stale data/waiver_identity_baseline.json rows; fixed with a test in da636fa4d, confirmed by a second reviewer, comment posted on the issue. Step 2: MX lease renewed; RO-5 tranche 1 landed (20c584676): data/catalog/work_packages.json with model and schema, the gz validate --catalog work-package checks, work_package_transitioned and work_package_changed with writers in gzkit.work_package_ledger, producer probes, the requirements-catalog-work-packages negative control and guard canary. Pushed; origin in sync. Tranche 2 (the gz wp verbs) not started.

## Important Context

Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md; lease renewed 2026-10-28. RO-5's contractor stops on every structural question. Tranche 2 surface per the canary precedent (121f99576): parser module, parser_handler_manifest, a commands module, one manpage per subverb plus docs/user/manpages/index.md and config/doc-coverage.json, both runbooks, a features/ BDD file. Ledger writers already exist and take TransitionRequest and ChangeRequest models; the store file must be edited only through the verbs (ruling 3), so gz wp new and gz wp attach write data/catalog/work_packages.json. _EventBase has its own serializer, so model_dump(exclude=...) does not drop ts. Shift turnover: the only hung lock is mx-session (lease renewed); the contract's list of discrepancies has no RO-5 tranche-1 line because nothing was disconnected.

## Decisions Made

- [operator-ruled] Restore the fail-safe clause the mode-contract compression dropped (verbatim choice: "Restore that clause (Recommended)").
- [operator-ruled] RO-5 tranche 1 store and event shape accepted as drafted (verbatim choice: "Accept as drafted (Recommended)").
- [operator-ruled] RO-5 tranche 2 verbs are gz wp <verb>: new, initiate, freeze, commence, accept, close, change, attach, show (verbatim choice: "gz wp <verb> (Recommended)").
- [operator-ruled] Keep the hand-prune of the retired-hook rows from the identity baseline (verbatim choice: "Keep the prune (Recommended)").
- [agent-chose] Added item to work_package_changed to name the alteration or departure a change records; disclosed in the commit, the spec and the passage log.
- [agent-chose] Both writers take one request model each instead of keyword lists, after Ruff PLR0913.

## Immediate Next Steps

1. Build RO-5 tranche 2, the gz wp verbs over gzkit.work_package_ledger, with manpages, index, runbooks and a BDD feature.
2. Ask the operator whether the forward rule turns fail-closed in tranche 2 (RO-3 ruling 4), since legacy task events still carry no outcome id.
3. Repair the RO-12 pre-kit GHIs (#1200, #1206, #1208, #1028, #1273, #1198, #1203, #1205, #1194, #1209, #1185 and the cwd-escape guard), each with a reviewer subagent confirming before close.
4. Have the operator review the requirements-catalog-work-packages guard canary through gz canary review.

## Pending Work / Open Loops

RO-5 tranches 3 to 5 (the repair label and ghi-close, the realignment, the RO-9 witness flight). RO-12 specification waits on RO-5 landing. The list-of-discrepancies lines for RO-5 (brief-lane validators, specify_cmd checklist count) open until tranche 4.

## Verification Checklist

uv run gz validate --catalog; uv run python -m unittest tests.governance.test_catalog tests.test_work_package_ledger tests.test_ledger_producer_probe; git rev-list --left-right --count origin/main...HEAD; uv run gz obpi lock list

## Evidence / Artifacts

src/gzkit/work_package_ledger.py, src/gzkit/models/catalog.py, src/gzkit/governance/trust_audits/catalog.py, data/catalog/work_packages.json, src/gzkit/schemas/catalog_work_packages.json, tests/test_work_package_ledger.py, docs/governance/harbor-ro5-work-packages.md, .gzkit/rules/mode-contract.md, tests/test_hooks.py

## Settled Rulings

1786 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
