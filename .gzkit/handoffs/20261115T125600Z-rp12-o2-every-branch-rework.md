---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-15T12:56:00Z'
agent: claude-code
session_id: 7bc921ee-d80c-40da-9e49-75bfe581c2c9
continues_from: .gzkit/handoffs/20261115T073007Z-rp12-o2-dock-trial-rework.md
---

## Current State Summary

Resumed the O2 dock-trial rework and ran four rounds of it under RP-12 ruling 27. Each round widened the sweep and was inspected by a fresh reviewer; each inspection failed it, finding O2 refusals the sweep never mutated, several of them real test gaps. The operator ruled the method in turn: ruling 92 (scope is every function, verb and module O2's Mode Contract rows cite, each whole, against twelve test modules), its is_run_id reading for acceptance_store, ruling 93 (three package controls in commands/wp.py stay out), ruling 94 (mutate every branch, not only what is recognised as a refusal) and ruling 95 (a survivor of the twelve is re-run against its own outside test, disclosed apart). Rulings 92 to 95 and eleven new or strengthened tests are committed in this handoff's commit. The trial script, its JSON record and the record prose section of the contractor kit are uncommitted and do not stand: the script still predates ruling 94.

## Important Context

Safe mode is open under docs/governance/harbor-pilotage-candidate-2026-10-15.md; the ruled order is RP-5, RP-12, RP-11, RP-4 and RP-12 is the critical path. The instrument is gzkit.mutation_witness.run_mutation_sweep. It compiles each mutated file with py_compile, so a JSON file (src/gzkit/schemas/ledger.json) runs through it too. Probes that spawn the test runner must pass the full environment: with PATH stripped, the acceptance tests error at baseline and read as kills. The current script, o2_mutation_sweep.py, and its record o2-sweep-2026-11-15.json under docs/governance/harbor-ro12-dock-trial-evidence/ are untracked, so not cited as evidence; the script finds refusals by call name (REFUSERS) plus hand mutants (MANUAL), and ruling 94 retires that method. Its last record was 155 mutants: 118 killed, 15 survived, 22 inconclusive against the twelve; the 15 died against tests outside the twelve and 12 inconclusive rows died narrowed, 10 disclosed. A full sweep takes 15 to 20 minutes; run it in the background. The four inspection reports are in this session's subagent transcripts; the fourth's probe evidence sits in the session scratchpad, which a reboot clears. Shift turnover: no tag-out hung, no work package commenced; gz obpi lock list shows only the mx-session lock, its lease expired and booked as mx_session_lease_expired, held by claude-code-cf5aca02.

## Decisions Made

- [operator-ruled] Proceed on the O2 dock-trial rework handoff of 2026-11-15T07:30Z (verbatim: "Proceed").
- [operator-ruled] RP-12 ruling 92, O2's trial sweeps every code site its Mode Contract rows cite (verbatim: "A: Mode Contract rows"), confirmed as put, each function whole against twelve modules (verbatim: "A as put: whole, 12").
- [operator-ruled] Ruling 92's reading of gzkit.acceptance_store as the functions that branch on is_run_id (verbatim: "Keep the is_run_id reading").
- [operator-ruled] RP-12 ruling 93, the three package controls in commands/wp.py stay outside O2's trial (verbatim: "Leave the package controls out").
- [operator-ruled] RP-12 ruling 94, the sweep mutates every branch (verbatim: "A: Every branch").
- [operator-ruled] RP-12 ruling 95, a survivor of the twelve is re-run against its own test outside them, disclosed apart (verbatim: "Yes, disclosed apart").
- [operator-ruled] Hand the every-branch rework to a fresh session (verbatim: "Yes, hand off, this sounds like needed work").
- [agent-chose] Committed rulings 92 to 95, the eleven tests and the amended lifecycle clause, and kept the trial's script, record and prose out of main until the rework passes inspection.

## Immediate Next Steps

1. Put this handoff to the operator, book the ruling with uv run gz handoff decide under the new session's own id, and ask whether to push this handoff's commit.
2. Rebuild o2_mutation_sweep.py on ruling 94: for each function ruling 92 takes and each same-module helper those functions call, mutate every if test, raise, conditional expression and early return by a mechanical AST rule, keeping the schema conditionals' required and property mutants; take acceptance_store as the six functions that branch on is_run_id (resolve_brief, _without_departed, initialize, record_human_review, owed_ids, acceptance_verb), not round_bound_refusal; list the helper set the rule yields so the inspector can check it, and put to the operator whether helpers are taken transitively if the rule leaves it open.
3. Write tests for the two mutants the fourth inspection found no test kills anywhere: resolve_brief's translation of a RegistryError into a ValueError, and work_package_run._package returning nothing for an unknown package; drop the dead table entries (NARROWED wp_order_new_cmd:197 and wp_order_close_cmd:404, OUTSIDE fenced_packages); rewrite the script docstring to rulings 92 to 95.
4. Run the sweep in the background; route each non-kill: a survivor killed by its own test outside the twelve to OUTSIDE (ruling 95), an inconclusive row to NARROWED (ruling 91), a mutant no test kills to a new test, and a wording-only or equivalent mutant to a disclosure with its reading; rewrite the record prose from the JSON with the headline counting only kills within the twelve and ruling 91 quoted verbatim; stage it together, run gz check under an ARB receipt, and send it to a fresh independent inspector.
5. On a standing trial, put O2's close to the operator with the open @covers ruling, then O3, the tag-out log.

## Pending Work / Open Loops

- The @covers finding: tests/commands/test_wp_order.py is hexagon-held and test_a_store_broken_before_the_call_names_the_store_to_repair names no REQ, since no admitted REQ covers O2; gz validate --hexagon-tests reports it, demoted by the hangar, and it fails at gz mx exit until the operator rules (defect insight recorded).
- Two defect insights record this session's scope drifts (ruling 92 first booked narrower than option A as put; the acceptance_store list typed with round_bound_refusal for acceptance_verb); derive the scope from the code by the ruled rule, never from a hand list.
- The hexagon guard canaries: tests.governance.test_guard_canaries still fails on the four hexagon claims, carried from the predecessor; it belongs on the contract's list of discrepancies on the operator's word.
- The mx-session lease is expired; renew or exit through gz-mx.
- Open siblings #1314 and #1316 stand, on the operator's word.
- The uncommitted trial: the record section in the contractor kit and the two untracked evidence files are working-tree only and do not stand as written.

## Verification Checklist

- git status shows docs/governance/harbor-ro12-contractor-kit.md modified (the trial section only) and the sweep script and its JSON untracked.
- uv run -m unittest tests.commands.test_wp_order tests.commands.test_wp_req tests.governance.test_catalog_orders tests.governance.test_catalog_repair_reqs tests.test_acceptance_store tests.test_order_ledger_schema tests.test_order_run passes.
- docs/governance/harbor-ro12-contractor-kit.md holds rulings 92 to 95 at HEAD.
- uv run gz validate --hexagon-tests reports only the @covers finding on test_a_store_broken_before_the_call_names_the_store_to_repair.
- uv run gz handoff rulings --search "ruling 94" returns this session's ruling.

## Evidence / Artifacts

- `docs/governance/harbor-ro12-contractor-kit.md` — rulings 92 to 95 and the amended lifecycle clause (committed); the trial record section (uncommitted).
- `tests/commands/test_wp_order.py`, `tests/commands/test_wp_req.py`, `tests/governance/test_catalog_orders.py`, `tests/governance/test_catalog_repair_reqs.py`, `tests/test_acceptance_store.py`, `tests/test_order_ledger_schema.py`, `tests/test_order_run.py` — the tests (committed).

## Settled Rulings

2251 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
