---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-25T15:24:05Z'
agent: claude-code
session_id: 46f0c689-58f0-472c-a74b-0478943f960a
continues_from: .gzkit/handoffs/20261025T065203Z-ro9-t4-closed-ci-green.md
---

## Current State Summary

Safe mode was redesigned with the operator and every open repair order of the drydock was specified; nothing was executed except the safe-mode switch and GHI #1269's fix. Commits 757ddea7e (the alarm switch gzkit.mx.alarms), 62e4041d6 (each RO owns restoration), fbd1c376c (the pytest ban pinned CRITICAL; ruff and ty back on), c2017c7d4 (GHI #1269 fixed and closed: the reach trace counts file reads), then the specifications: be1ed2785 RO-10 parked, 4ff4a453f RO-1, RO-5, RO-4, 8a879a8bd RO-6, RO-7, RO-8, 38636bbaa (the compliance register), fc84f1b7f (the contractor brief). All pushed; the tree is clean but for ledger rows. The mx-session lock was renewed this session (lease 24h).

## Important Context

Read docs/governance/harbor-contractor-brief.md first: it is the drydock contractor's goal, order of work (RO-5, RO-4, RO-11 stop, RO-6, RO-7, RO-9, RO-8) and stop rules. The contract's § Punch list is now the compliance register: every item an order unplugs, dismantles or modifies, with its disposition (restored, reconnected, retired, replaced) and authority; exit condition 9 reads from it. Safe mode: six pre-commit/pre-push alarm hooks and the verifier pipe gate are off while .gzkit/mx.json carries mode safe; the guards sweep (pytest ban, ledger, Gate-5), ruff, ty, gitleaks and authorship stay on. No per-act gz arb red --commit or gz check. The operator wants one question at a time, with a recommendation, and discussion rather than reaction. Two agent-drafted clauses rode in on wholesale ratification (the per-act witness and the kept-or-reverted list, both from 17d80ef7a); surface each obligation an agent draft adds.

## Decisions Made

- [operator-ruled] No long checks in safe mode; leave things partially broken until reconfiguration, then adjust tests and turn the alarms back on (verbatim: "i don't want any long check at all - this is a remodel, things are going to be broken, disarray, and messy. it is time to leave things partially broken until the reconfiguration is complete, then we adjust tests and turn the "security alarms" back on. this is all backwards.").
- [operator-ruled] Each repair order owns restoring what it disconnects, rerouted or changed, to a prior or new stable state (verbatim: "The RO (or a sequence of ROs) are obligated to return the system to a prior, or new, stable system state.").
- [operator-ruled] The pytest ban is never turned off (verbatim: "never, ever, ever turn this off: "the pytest ban""); ruff and ty stay on (verbatim: "ruff and ty are reasonable too").
- [operator-ruled] Three kinds of protection: irreversible damage and identity rules stay alarms; old-structure checks go off, cheap ones as tripwires (verbatim: "1. yes; 2. yes; 3. yes, off" and "tripwires for the cheap ones, long ones fully off").
- [operator-ruled] Freeze lean safe mode, park the full design as RO-10, two contractors (verbatim: "yes, freeze lean, park the spec, two contractors").
- [operator-ruled] Specify all six open ROs first, then launch one contractor; on a structural question it stops and waits (verbatim: "specify all six first and launch the contractor once on everything"; "A").
- [operator-ruled] The pool stays as intentions, not ADRs, parsed into requirements on demand; RO-11 designs only the pull process (verbatim: "process for pool drain and work for pool drain are not the same thing").
- [operator-ruled] Undated live documents, dated documents are archives (verbatim: "anything dated implies archival status"); the PRD is Approved (verbatim: "B, it should have never stayed in draft for that long").
- [operator-ruled] Semver: PRD drives major, Release Package drives minor, GHI pressure drives patch (verbatim: "prd drives major, release package drives minor, ghi pressure drives patch").
- [operator-ruled] ADR-0.35.0's unfinished work is absorbed into the catalog and forms the 0.35.0 Release Package, reviewed very carefully later (verbatim: "they need to be absorbed into the new system, but not jettisoned").
- [operator-ruled] The punch list is the compliance register (verbatim: "yes, that is fine, it works well; you've captured the scope well."); set up the contractors and write a fresh handoff (verbatim: "yes, A, and write it into a fresh handoff.").
- [agent-chose] Each RO specification records every ruling verbatim and its number; the per-RO question-by-question rulings live there and as insights, not restated here.

## Immediate Next Steps

1. The operator launches the drydock contractor in a fresh session with docs/governance/harbor-contractor-brief.md (its Goal paragraph and loop prompt); first act: RO-5 tranche 1, which will stop at once to ask the names of the new gz verbs and events.
2. When RO-4 lands, specify RO-11 (the pool pull process) with the operator.
3. Before RO-8 act 3, the operator's careful review of requirements and Release Packages, including RO-4 ruling 6 against the 0.35.0 Release Package.
4. After the drydock contractor finishes, launch the restoration contractor from the same brief.

## Pending Work / Open Loops

GHI #1268 is open and is now an RO-0 restoration line, not drydock work. GHI #1269 [settled]'s acceptance rerun on 7b7ea83cd is an RO-0 restoration line. GHI #1252's flight moved to restoration. GHI #1188 routes to a docs-consolidation chore not yet authored. Leads after the drydock: Claude/Codex instruction-parity prior art, a progressive-disclosure system, a sweep for scopes deferred to "Phase 2" with no destination, the A/B/C/D timed trigger (RO-10), the campaign plan updated (civil rule's work). The handoff step 3 of the predecessor (the T/O/S orientation thread) and step 2 (PLC0415 plan before RO-9 tranche 6) still stand.

## Verification Checklist

git status shows only ledger rows; git log origin/main..HEAD is empty. uv run gz obpi lock list shows mx-session ACTIVE. grep -c "^### RO-" docs/governance/harbor-pilotage-candidate-2026-10-15.md counts the register's sections. uv run python -m unittest tests.mx.test_alarms tests.test_hooks_guards passes.

## Evidence / Artifacts

`docs/governance/harbor-contractor-brief.md` `docs/governance/harbor-pilotage-candidate-2026-10-15.md` `docs/governance/harbor-ro1-cut-measurement.md` `docs/governance/harbor-ro4-release.md` `docs/governance/harbor-ro5-work-packages.md` `docs/governance/harbor-ro6-canon-retirement.md` `docs/governance/harbor-ro7-context-cut.md` `docs/governance/harbor-ro8-in-flight-work.md` `docs/governance/harbor-ro10-safe-mode-classification.md` `src/gzkit/mx/alarms.py` `tests/mx/test_alarms.py` `docs/governance/safe-mode-doctrine.md`

## Settled Rulings

1701 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
