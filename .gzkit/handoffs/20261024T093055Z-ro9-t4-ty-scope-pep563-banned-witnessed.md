---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-24T09:30:55Z'
agent: claude-code
session_id: 950708bf-c0ab-4d6d-b449-d5ba1ca4c0fd
continues_from:
- .gzkit/handoffs/20261024T072528Z-ro9-t4-ruff-all-sweep-windows-green.md
- .gzkit/handoffs/20261024T072939Z-session-exit-bookmark.md
---

## Current State Summary

RO-9 tranche 4 (drydock, safe mode) advanced three acts and one in-flight fix, all pushed; local main matches origin. Acts: `8fa1d06da` features/ in ty scope (14 diagnostics fixed) and ty.toml moved into pyproject [tool.ty] with terminal error-on-warning; `0fb920d89` the chores.md scorecard ledger row that act missed; `17f722d63` the RO-9 import-boundary row amended (GHI #1267 filed for hexagonal direction, cross-linked on #956); `fb5b1c43e` the PEP 563 import removed from 1,051 modules, the extensionless prepare-commit-msg hook and five hook templates, with Ruff TID251 banning it and no baseline row; `6c17779b7` gz lint judges no named file outside Ruff's whole-tree walk; `7ee0cd896` the ban witnessed by the astral rule deferred-annotations-unbanned and NC:astral-discipline-deferred-annotations, canary reviewed, scorecard row 23b Mechanical. Passage-log rows landed for every act. CI passed on `4da1aa097` (through the lint fix); the run for `7c66f77f6` (act B) was queued at handoff. The MX lease was renewed at session start.

## Important Context

Safe mode is open; the lease was renewed this session (24h). Ruff refuses the PEP 563 import and gzkit owns only the banned-api entry in pyproject.toml, so the guard a canary can mutate is the astral-discipline rule _deferred_annotations_rules, which fires only at a requires-python floor of 3.14 or above (the 3.13 gz init scaffold is exempt). The seven dated evidence scripts under docs/governance/*-evidence and .gzkit/evidence keep their PEP 563 import under the banned-api per-file exception, the same precedent as their C901 and EXE001 records. A new Mechanical scorecard row must cite a registered NC claim, and every claim needs a canary the operator reviews through gz canary review; the guard_canary grandfather lists are shrink-only. gz arb red --commit runs only the commit's own test modules, so a registration row or exemption declaration needs a test in that module or it survives. ruff analyze graph reports first-party files only and cannot carry the stdlib-plus-Pydantic allowlist; tests/policy/test_import_boundaries.py stays. The hexagonal canon's 2026-07-06 ruling blesses I/O through an injected project_root Path, so id_resolver's file reads are conformant; its reach into commands/ is the defect GHI #1267 tracks. The pre-commit ruff-check hook runs gz lint on staged files, which now holds them to ruff check --show-files .

## Decisions Made

- [operator-ruled] Renew the MX lease, bring features/ into ty's scope, and proceed on the handoff (verbatim: "renew the mx lease, features in ty scope, proceed").
- [operator-ruled] Remove the PEP 563 imports before banning them, so TID251 enters with no baseline row (selection: "Remove first, then ban (Rec.)").
- [operator-ruled] Let ruff analyze graph feed the import-boundary test (selection: "Graph feeds the AST test (Rec.)"), later superseded when the graph was found to see first-party files only.
- [operator-ruled] File the hexagonal-direction GHI, amend the RO-9 row, and run the PEP 563 removal (verbatim: "okay - do 1-3"); GHI #1267.
- [operator-ruled] Sync, then register the TID251 control (verbatim: "git sync, then act B"); canary reviewed (verbatim: "book em").
- [operator-ruled] Sync and write a fresh handoff (verbatim: "sync and fresh handoff").
- [agent-chose] Moved ty.toml into pyproject [tool.ty], since ty.toml took precedence and RO-9 names a [tool.ty] table.
- [agent-chose] Raised warn-level ty rules through terminal error-on-warning rather than listing rule names, proved by a planted @deprecated call exiting 1 with it and 0 without.
- [agent-chose] Split the PEP 563 work into act A (removal and ban) and act B (registered control), because a Mechanical row needs an operator-reviewed canary.
- [agent-chose] Hosted the ban's witness in the astral-discipline gate rather than a new validator scope.
- [agent-chose] Fixed gz lint's named-file scope as a direct fix, found when act A's own commit hook refused it.

## Immediate Next Steps

1. Confirm CI passed for `7c66f77f6` (act B) with gh run list; read the failing step from gh run view --log if not.
2. Ask the operator to rule whether RO-9 tranche 4's done condition ("No lint or type row remains") holds: data/astral_discipline_baseline.json holds 8 rows, none of them lint or type. If ruled, add the tranche's closing passage-log row.
3. Before tranche 6, present the plan for the 2,590 held PLC0415 sites across 363 files, read against the pythonic.md carve-outs.
4. When the drydock's work allows, read the contract's § Exit and the repair-order register before any gz mx exit.

## Pending Work / Open Loops

- GHI #1267 (hexagonal direction: domain reaches the command layer) is open for work after the RO-9 lint tranche: inject the scope runner into resolve_support_proof, add a transitive gz validate scope over ruff analyze graph, widen the fenced set to the canon's domain modules measured clean, and restate rule 1's rationale.
- GHI #956 carries the same req_kind_support.py:320 edge as a private-symbol reach.
- docs/examples/tutorial-rhea-bootstrap.md still shows the PEP 563 import in an adopter example; left as an adopter project's code, not gzkit's.
- 30 chores were overdue at session start (orientation, advisory).

## Verification Checklist

- `git rev-list --left-right --count origin/main...HEAD` reads 0 0.
- `uv run gz check` passes on a clean tree.
- `uv run ty check .` passes with no exclusion.
- A file under src/gzkit with `from __future__ import annotations` fails `uv run gz lint` with TID251.
- `uv run gz validate --astral-discipline` passes; data/astral_discipline_baseline.json holds 8 rows.
- `gh issue view 1267` is open.

## Evidence / Artifacts

- `pyproject.toml`
- `src/gzkit/canonical_steps.py`
- `src/gzkit/ruff_baseline.py`
- `src/gzkit/governance/trust_audits/astral_discipline.py`
- `src/gzkit/governance/trust_audits/_qc_negative_controls.py`
- `data/guard_canaries.json`
- `docs/governance/advisory-rules-audit.md`
- `docs/governance/harbor-ro9-astral-toolchain.md`
- `docs/governance/harbor-pilotage-candidate-2026-10-15.md`
- `.gzkit/rules/pythonic.md`
- `tests/governance/test_astral_discipline.py`
- `tests/test_ruff_baseline.py`

## Settled Rulings

1682 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
