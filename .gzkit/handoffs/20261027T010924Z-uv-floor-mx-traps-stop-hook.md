---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-10-27T01:09:24Z'
agent: claude-code
session_id: 49b1b2dd-2757-4abb-b076-5db81832e61a
continues_from: .gzkit/handoffs/20261026T172406Z-radar-october-refresh-chore-routed.md
---

## Current State Summary

Safe mode open under docs/governance/harbor-pilotage-candidate-2026-10-15.md; session 57346836 lease renewed 2026-10-27T01:07Z (mx_session_lease_renewed). Main at 2d9ed1901, 0/0 with origin. Work this session:
- GHI #1283 (closed, fixed): hooks run through uv run, and uv exits 2 on a version required-version refuses, so an exact pin locked the session out. d564f3334 loosened pyproject [tool.uv] required-version to ">=0.13.1" (the uv_build floor), switched .readthedocs.yaml to the latest uv, and amended the gz-deps-upgrade skill (1.5.0) and the RO-9 record.
- The interrupted rebase onto 05f6e3db2 was finished. The ledger merge driver (uv run gz ledger merge-driver) had failed for the same reason, leaving UU with only one side's rows. I re-ran it by hand, confirmed the union, and gz validate --ledger passed.
- A uv-version-capped validator rule (5c5d27b95) and its canary rebind (f78a9f795) were added, then reverted in 996ac4094 at the operator's direction. The guard source is back byte for byte, and both astral-discipline canaries match their original reviewed bindings.
- a29b2f3af: stop-turn-feedback.py now routes both block points through gzkit.mx.checkpoint.hangar_demotes. An open hangar or safe-mode marker reports with exit 0; an exiting, missing or unreadable marker still blocks.
- GHI #1263: the parked stash was posted as a patch to the issue (comment 6429260504, with a correction in 6429268910) and then dropped.
- GHI #1273: received a measured table of the six traps this session hit in safe mode.

## Important Context

- Safe mode means freeing things up, not adding guard surface. The operator corrected twice on this point (insights recorded). Do not grow validators, canaries or reviews inside a fix during the drydock.
- CI on main is red and was red before this session: Lint on src/gzkit/mx/alarms.py and .claude/hooks/verifier-pipe-gate.py (RO-0 punch list, left broken by operator ruling 2026-10-25), plus 11 older unit-test failures (cli-alignment, the advisory-scorecard self-test, mx.alarms argv). Not chased: they belong to the alarms-off period and matter when RO-0 reconnects the alarms.
- Guard canaries hash the guard function's source, so any edit to a canaried guard (data/guard_canaries.json) makes its canary stale and turns tests.governance.test_guard_canaries red. Check that registry before touching a guard.
- The post-commit recorder writes artifact_edited rows while a rebase replays commits, which blocks git rebase --continue. Stash the ledger, continue, then union the stash back through gz ledger merge-driver. This is item 3 on #1273.
- A uv older than 0.13.1 still exits 2 in every hook; that residual is stated on #1283.

## Decisions Made

- [operator-ruled] Loosen the uv pin rather than bypass uv in the hook commands (verbatim: "no, loosen uv, it will likely run python at any version").
- [operator-ruled] Move GHI #1263's parked stash into the issue and drop the stash; #1263 stays parked (verbatim: "Preserve, drop stash (Rec.)").
- [operator-ruled] While a mode is open, CI's full-strength run of demoted guards reports and does not fail, and the shape is decided inside the MX-system review (verbatim: "report only, decide within #1273").
- [operator-ruled] Safe mode should remove friction, so revert the validator rule added in safe mode and make the Stop hook report rather than block under an open mode (verbatim: "we are supposed to be freeing things up in mx, not hashing canaries", then "both").
- [operator-ruled] Renew the safe-mode lease rather than exit (verbatim: "1").
- [agent-chose] Floor at 0.13.1 to match the uv_build floor already in pyproject.toml, rather than at the current 0.13.5, so a uv behind the current release keeps working.
- [agent-chose] The Stop hook reads the marker through checkpoint.hangar_demotes, the one demotion authority, rather than its own marker read. An unreadable marker keeps the block, as the pre-commit guards do.

## Immediate Next Steps

1. Ask the operator whether to resume the contractor-kit R&D through gz-rnd (docs/rnd/contractor-kit.md): append a decision entry with the operator's words, check the record against git, and recompute the frontier. This is the predecessor handoff's step 2. Its step 1 (grill adrkit moves 112-116) landed as dfc234632 and d23fbf045.
2. Then the mode contract's syntax: the candidate Python affordances for code controls (decorators, typing.Protocol ports, context managers, class registration, entry points), after reading the census and the seven chore --self-test arms.
3. When the operator takes up GHI #1273, carry the 2026-10-26 trap table (comments 6431031401 and 6431150899) and the report-only ruling: if the marker stays committed, a continue-on-error CI job with GZKIT_MX_FULL_STRENGTH=1; if it leaves git, a separate report-only mechanism.

## Pending Work / Open Loops

- GHI #1273: MX-system review. It owns traps 3 (the post-commit recorder during rebase) and 6 (full Ruff lint and the cognitive baseline applying in safe mode), the marker's place in git, and the report-only CI shape.
- GHI #1263: parked. The reference patch is on the issue; it no longer applies cleanly to main (10 of 13 files fail).
- RO-0 punch list: Lint debt in src/gzkit/mx/alarms.py and .claude/hooks/verifier-pipe-gate.py, left broken until reconfiguration.
- 11 older CI unit-test failures, not yet checked against the punch list or any GHI.
- The safe-mode lease runs to about 2026-10-28T01:07Z, and advisory debt keeps aging.

## Verification Checklist

- git rev-list --left-right --count origin/main...HEAD: expect 0 0.
- grep -n required-version pyproject.toml: expect >=0.13.1.
- uv run -m unittest tests.hooks.test_stop_turn_feedback tests.governance.test_guard_canaries: expect OK.
- uv run gz validate --ledger: expect all validations passed.
- gh issue view 1283 --json state: expect CLOSED; gh issue view 1263 and 1273: expect OPEN.

## Evidence / Artifacts

- `pyproject.toml` (required-version floor, d564f3334)
- `.readthedocs.yaml`
- `.gzkit/skills/gz-deps-upgrade/SKILL.md`
- `docs/governance/harbor-ro9-astral-toolchain.md` (amendment 2026-10-26)
- `src/gzkit/hooks/scripts/quality.py` and `.claude/hooks/stop-turn-feedback.py` (a29b2f3af)
- `tests/hooks/test_stop_turn_feedback.py` (TestOpenModeReports)
- `data/guard_canaries.json` (restored to original bindings, 996ac4094)
- Commits: d564f3334, 5c5d27b95 (reverted), f78a9f795 (data reverted), 996ac4094, a29b2f3af
- GHIs: #1283 closed; #1263 comments 6429260504, 6429268910, 6429308404; #1273 comments 6429308859, 6431031401, 6431150899

## Settled Rulings

1758 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
