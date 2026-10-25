---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-25T01:14:25Z'
agent: claude-code
session_id: 46f0c689-58f0-472c-a74b-0478943f960a
continues_from: .gzkit/handoffs/20261024T110059Z-ro9-t4-subprocess-resolved-ty-tail-orientation-work.md
---

## Current State Summary

RO-9 tranche 4's ty work is complete: the tests/** override is deleted, and ty check passes on the host, linux and win32. Five acts took the lifted-block count from 498 to 0: forwarded kwargs bags Any (026cd840d), read-only Mapping parameters (504790e8f), Optional narrowing (a30b020a9), unresolved-attribute retired (a62515421), and the override retired (1dd9bb86a). A test-isolation defect found in flight was fixed in a0baed6da. The passage log has all six rows (9520e470a). The act 2c red verdict (7b7ea83cd, undriven) was recorded at 88577b3ae. Everything is pushed (012eb6ada). CI was queued at handoff time and has not been confirmed.

## Important Context

The witness verdicts on the type acts are honest rather than defects. A hunk that changes only an annotation or moves an import under TYPE_CHECKING can only survive, because ty is its witness and no test can see it. Act D's inconclusive verdict (a62515421) came from tests.test_smoke_gate leaking a nested runner's 'Ran N tests' line: read_test_observations reads a count only from a single summary, so every mutation baseline over that module read zero tests. a0baed6da fixed it, and the full unit run now prints exactly one summary. Ruff's TC003 fix is unsafe in modules that define Pydantic models: applying it to src/gzkit/enforcement.py broke EnforcementClaimRecord and cost 833 tests (707 errors, 126 failures) before it was reverted (GHI #1270). Apply only safe ruff fixes, and move only names you added under TYPE_CHECKING.

## Decisions Made

- [agent-chose] Each act fixed a root cause rather than the instance, and the four tests that pass a refused value on purpose carry a reasoned ty: ignore instead of a narrowed signature.
- [agent-chose] gz_check_cmd.steps, a function attribute set behind a blanket type: ignore, was deleted; its three tests read _build_check_steps(), and the @covers bindings of REQ-0.0.27-07-06 and REQ-0.0.69-03-03 stand because both REQs assert the step list, not the attribute.
- [agent-chose] The smoke-gate leak was committed as its own act (a0baed6da) rather than folded into a type act.

## Immediate Next Steps

1. Confirm CI on 012eb6ada with gh run list, then gh run view --log on any failure.
2. Write tranche 4's closing passage-log row, or present the tranche-exit reading against the contract's RO-9 entry before declaring it closed.
3. Route GHI #1269 (the reach trace drops source-reading fences) and GHI #1268 (mirror hunks) before any further wide production-code tranche, then GHI #1270 (ruff runtime-evaluated-base-classes for Pydantic).
4. Ask the operator to route the T/O/S orientation thread carried from the predecessor handoff: a GHI through ghi-author (recommended), or a direct patch.
5. Before tranche 6, present the plan for the held PLC0415 sites against the pythonic.md carve-outs; before gz mx exit, read the contract's § Exit and the repair-order register.

## Pending Work / Open Loops

GHIs #1268, #1269 and #1270 are open and unselected. The T/O/S orientation thread from the drive-time discussion has no route yet. The ADR-0.34.0 ordering conflict is open: OBPI-0.34.0-02 was repudiated on 2026-10-01 (verification-invalid, GHI #849 [settled]), so ADR-0.34.0 is the lowest feature ADR with unlanded work while the campaign names ADR-0.35.0 as in flight. That is the operator's to rule before campaign work resumes after gz mx exit. Two prunable worktrees from older sessions are listed by git worktree list.

## Verification Checklist

uv run ty check (and with --python-platform win32 and linux) must exit 0. uv run gz lint must exit 0. uv run python -m unittest discover -s tests -t . must pass with exactly one 'Ran N tests' line. grep -n 'tool.ty.overrides' pyproject.toml must show only the timeout.py block. gh run list must show CI green on 012eb6ada.

## Evidence / Artifacts

`docs/governance/harbor-pilotage-candidate-2026-10-15.md` `pyproject.toml` `tests/test_smoke_gate.py` `src/gzkit/commands/quality.py` `artifacts/receipts/arb-red-commit-1dd9bb86ac53-9a356af968f047f0b9ff9aac86bfaff4.json` `artifacts/receipts/arb-red-commit-a62515421587-77072f36523b49b883b02cd6a70d3bd7.json`

## Settled Rulings

1688 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
