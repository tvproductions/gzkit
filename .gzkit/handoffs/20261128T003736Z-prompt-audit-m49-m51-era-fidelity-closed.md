---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-11-28T00:37:36Z'
agent: claude-code
session_id: bf48fbf4-569b-438d-a1a2-acce7b46a27f
continues_from: .gzkit/handoffs/20261127T234859Z-prompt-audit-m33-m48-walked.md
---

## Current State Summary

Resumed on 'resume from h/o'. This session finished the prompt-audit walk (M49 to M51), settled the era question, and fixed one in-flight finding. Rows were walked one at a time.

GHIs closed, each with a reviewer subagent's CONFIRMED verdict recorded on the issue:
- #1414 (M50/R20): brief-heading-conventions.md called the top-level brief sections Gate 2. Rule 0.2.1 -> 0.2.2.
- #1415 (M51/A4): the manifest's thresholds.coverage_floor is now the floor's one authority. gz obpi audit and the coverage-40pct chore (new check_coverage_floor.py) read it, and sync keeps an authored value. Prose sites cite the key; tests.md 0.29.2 -> 0.29.3. Review pass 1 was NOT CONFIRMED (three gaps); pass 2 CONFIRMED.
- #1416: both era tables now say Era 2 in part, and specify_cmd suggests canon paths. Review pass 1 was NOT CONFIRMED (Era 2 was credited to the Jinja2 pipeline instead of composer.py); pass 2 CONFIRMED.
- #1417, found in flight: the fidelity doctrine stated four invariants, but Invariant 4 was retired under #716. It is now struck through in place, Invariant 1 is restated as tier-scoped, and the help text and manpages say three. Review pass 1 was NOT CONFIRMED (help text and manpages); pass 2 CONFIRMED.

M49 was recorded as no defect, with no GHI. Eight fix commits, c61933d24 through ab6e254e7. Last action: this handoff, then git-sync.

## Important Context

Safe mode is still open (docs/governance/harbor-pilotage-candidate-2026-10-15.md). Every act is one commit with a Task: trailer, and the ledger is written only through gz verbs.

Shift turnover, reviewed at resume:
- gz wp tag show --all: 'No tag has been issued.'
- gz wp runs: 'No work package is in flight.'
- gz obpi lock list: only mx-session, ACTIVE, past 50% of its TTL.
The buy-back record is not built, so the contract's list of discrepancies stands in for it.

Method learned this session:
- Every first review of the larger fixes (#1415, #1416, #1417) was NOT CONFIRMED, and each time for missed consumers, not for the edit itself. Sweep the consumers too: help text, manpages, the sync that regenerates the file, and the ledger evidence a command writes.
- Under safe mode, gz validate --distribution demotes violations to an '[MX advisory]' line and still prints 'passed'. Read the output for demotion lines before claiming a pass.
- New chore scripts cannot be held in data/ruff_baseline.json (it is shrink-only). Write sys.stdout.write rather than print. A line-1 '# noqa: INP001' with its reason is the precedent for scripts run by path.
- The coverage data on disk (.coverage, 2026-09-19) names deleted files, so coverage report fails on it. A chore run regenerates it first.

## Decisions Made

- [operator-ruled] M49: no defect, no GHI; the 'Carried verbatim from root AGENTS.md' lines are true dated provenance (verbatim: "B").
- [operator-ruled] M50: one GHI, direct fix of the brief-heading-conventions Gate 2 wording (verbatim: "A").
- [operator-ruled] M51: the manifest's thresholds.coverage_floor is the coverage floor's authority; obpi audit and the chore read it, and the 40% prose sites cite the key (verbatim: "A").
- [operator-ruled] The current era is Era 2 in part; rewrite both era tables and the specify suggestion under one GHI (verbatim: "A").
- [operator-ruled] #1417: strike retired Invariant 4 through in place with a dated amendment note, and restate Invariant 1 as tier-scoped (verbatim: "A").
- [operator-ruled] Keep the coverage-40pct chore id as a stable identifier, with no GHI (verbatim: "A").
- [operator-ruled] Write a fresh handoff and git-sync (verbatim: "write fresh handoff and git sync").
- [agent-chose] Read the coverage floor once at the gz obpi audit entry and pass it down as a value. hexagonal-architecture.md rule 10 asks new code to add no loader call; the configurator it names does not exist yet.
- [agent-chose] Left illustrative examples of the floor as they stand: gz-obpi-sync's JSON at 305, ledger-schema.md:105 and the arb --fail-under flag examples. The #1415 reviewer concurred.
- [agent-chose] Era tables state CLAUDE.md as Era 1 (rendered from the claude template), not corpus playback. This corrects my own framing of option A, and the ruling's substance (Era 2 in part) is unchanged.

## Immediate Next Steps

1. Give the operator the strategic, operational and tactical brief, short, vital facts first.
2. Offer the R&D's T37 and its sub-ids, W44 to W50, the open frontier, the disposition map, review.md and sign-off, as the predecessor advised.
3. Offer a coverage-40pct chore run (about 5 minutes) to witness check_coverage_floor.py against fresh coverage data.
4. Route the unrouted insights, one at a time: the dead anchor in arb-middleware.md (#attestation--worked-example) and gz task start ignoring --seq beside a task_id.

## Pending Work / Open Loops

- #1409 is open and blocked until the safe-mode exit: retire airlineops-parity-scan, gz parity check and its gz check step.
- #1412 is open: the per-site reading of the bare noqa and held PLC0415 sites.
- #1357 (M1) is still open.
- The live arm of check_coverage_floor.py has not run against fresh coverage data.
- #716 [settled]'s close comment cites 0ec38794a as the Invariant 4 retirement, which does not resolve; the commit is ab7bbd6b3. Recorded in #1417 [settled]'s body; the comment itself is not editable under the gh-cli allowed list.
- Carried from the predecessor:
  - scorecard row 33c and skill-surface-sync.md rule 6 wait for diamond 2;
  - the batch-run import error 'tests.arb.test_step_reporter tests' is undiagnosed;
  - the orientation's injected text is over its 4000 B budget.

## Verification Checklist

- gh issue view 1414 1415 1416 1417 --json state: all CLOSED, each with a CONFIRMED review comment.
- uv run gz validate --help | grep -A1 surface-fidelity: 'run the three live surface-fidelity invariants'.
- uv run python -m unittest tests.commands.test_obpi_audit_cmd tests.chores.test_coverage_floor_gate tests.test_manifest_v2 tests.commands.test_specify tests.governance.test_advisory_scorecard_coverage: OK.
- uv run python .gzkit/chores/coverage-40pct/check_coverage_floor.py --self-test: PASSED.
- uv run gz validate --distribution --surfaces --advisory-scorecard --invariant-coherence --surface-fidelity: passes with no '[MX advisory]' demotion line.
- git log 0c7edc24f..HEAD: the eight session commits, all with Task: trailers.

## Evidence / Artifacts

- `docs/rnd/conceptual-model/sources/prompt-audit-2026-11-25.md` (the walk's map, rows M49 to M51)
- `.gzkit/rules/brief-heading-conventions.md` (0.2.2)
- `.gzkit/rules/tests.md` (0.29.3, § Coverage Floor)
- `.gzkit/chores/coverage-40pct/check_coverage_floor.py`
- `tests/chores/test_coverage_floor_gate.py`
- `src/gzkit/commands/obpi_audit_cmd.py`
- `src/gzkit/sync_surfaces.py`
- `src/gzkit/commands/specify_cmd.py`
- `docs/governance/agent-control-surface-rendering-substrate.md`
- `docs/governance/agent-control-surface-fidelity-doctrine.md`
- `docs/user/manpages/validate.md`
- `docs/governance/advisory-rules-audit.md` (rows 38 and 53b, and the Coverage Ledger)
- `docs/governance/rule-version-history.md`

## Settled Rulings

2659 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
