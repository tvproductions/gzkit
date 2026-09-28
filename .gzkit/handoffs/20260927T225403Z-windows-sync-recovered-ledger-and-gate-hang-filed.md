---
mode: CREATE
adr_id: null
branch: main
timestamp: '2026-09-27T22:54:03Z'
agent: claude-code
session_id: 0305567c-dbe3-48de-a84c-3bcff32d13dc
continues_from: .gzkit/handoffs/20260927T220401Z-trailer-repair-ghi-1142-fixed.md
---

## Current State Summary

Windows-clone session that ran alongside the Mac chain; its work is now on origin. A /git-sync found the clone 1 ahead and 180 behind. The pre-commit ledger guard refused a staged ledger diff that only re-sorted two committed session_exit_bookmark_skipped rows, 2feaa310 and 9cc907c1, which were written 40 microseconds apart before GHI #1074 and are identical as a set. On operator ruling the ledger was restored to HEAD bytes and the rebase went through the GHI #1075 merge driver cleanly. The pre-push gate then failed on two GHI #1092 tests on Windows. Cause: the test fixture passed the raw sys.executable backslash path to an sh hook and to a pre-commit entry, and both stripped the backslashes (sh exit 127). Fixed in one line with Path.as_posix; the commit landed as d46876f45 with Task: TASK-recorder-posix-path, added by amend after the commit_trailers gate refused its absence. Pushes were blocked in turn by a stale WSL credential helper in the clone's .git/config (removed), by orphaned push shells from a restarted session (killed), and by an intermittent deadlock in the pre-push unit tier: 40 workers at zero CPU for over 15 minutes (GHI #1143). A direct gz check under a hard timeout exited 0, and the next gz git-sync --apply pushed with exit 0. The final /git-sync fast-forwarded to 3960c214e. main equals origin/main, verified by fetch.

## Important Context

The ledger is Pydantic-typed and validated: all 17615 rows parse through gzkit.events.parse_typed_event, gz validate --ledger exits 0, and tests/governance/test_ledger_reader_parity.py keeps the schema reader and the typed reader in agreement. Ledger.append does NOT check the typed union at write time; it accepts the generic LedgerEvent. Repeated id values are expected, because id is the artifact id, not a row key. quality.run_command (src/gzkit/quality.py) calls subprocess.run with no timeout, so any gz check step whose child deadlocks blocks the pre-push hook and git push silently; pre-commit also buffers hook output, so a hung gate shows no progress. Diagnose a stall by sampling worker CPU, not by elapsed time. The Mac/PC attribution method: a handoff whose session_id has no transcript under this PC's Claude projects directory was written elsewhere. Every substantive handoff from 09-26 onward in this chain is the Mac's. The commit-locus recorder is now installed in this clone as .git/hooks/post-commit.legacy. Record of the 2026-09-27 restore: git restore of the ledger is the out-of-band shape the GHI #611 and GHI #973 ruling put out of bounds; it was used here only with explicit operator approval and removed no row.

## Decisions Made

- [operator-ruled] Restore the ledger to HEAD bytes and re-run the sync instead of diagnosing the re-sort first (verbatim: "A, go ahead").
- [operator-ruled] Remove the clone-local WSL credential helper and push (verbatim: "do it").
- [operator-ruled] File the gate-hang GHI and install the commit-locus hook (verbatim: "file the GHI for the hang and install the hook").
- [operator-ruled] Write this handoff, then present ADR-0.35.0 (verbatim: "write the handoff, then present ADR-0.35.0").
- [agent-chose] Fixed the GHI #1092 Windows test failure as an in-flight direct fix (one line, one surface, covered by the test itself), not through a GHI.
- [agent-chose] Recommended routing the ledger reconcile utility the operator requested to gz-design and an ADR, not a patch, so the merge driver, the append-only guard and a normalize verb share one typed reconcile core instead of three copies of the preserves-every-row judgment.

## Immediate Next Steps

1. Present ADR-0.35.0 so the operator can initiate its next OBPI through gz-obpi-pipeline (operator-requested for this session; campaign TOPMOST).
2. On the operator's go, route GHI #1140: open a gz-design session toward an ADR for a typed ledger reconcile core, or fix only the guard's multiset check under the GHI. It needs the operator's ruling on whether committed history may be re-sorted at all.
3. On the operator's go, repair GHI #1143: bound each gz check step in quality.run_command with a JSON-held timeout that kills the whole process tree and names the step; consider faulthandler output to name the hung test.
4. Carried from the predecessor: draw the ghi-triage 5.4.0 landing queue and hold the ruling-docket session, each on the operator's go.

## Pending Work / Open Loops

GHI #1140 is open: a committed out-of-order ledger pair cannot be brought into ts order through gz, and the lexical append-only guard in src/gzkit/hooks/guards.py blocks a reorder that removes no row. Which gz step re-sorted the committed rows in the working tree was never identified. Sibling family: GHI #973 and GHI #611. GHI #1143 is open: the unit-tier deadlock root cause is unknown and did not reproduce. Ledger size (16 MB, 17615 rows) and whole-file reads were raised as a design input for #1140 but not measured. The predecessor's open loops carry unchanged.

## Verification Checklist

git fetch origin then git status -sb shows main in sync with origin/main. uv run gz validate --ledger exits 0. uv run -m unittest tests.hooks.test_commit_locus_survives_precommit_stash reports OK (skipped=1) on Windows. git config --show-origin --get-all credential.helper lists only the system manager and the global store. .git/hooks/post-commit.legacy exists. gh issue view 1140 and gh issue view 1143 show OPEN.

## Evidence / Artifacts

Commit d46876f45 (Windows recorder test fix, Task: TASK-recorder-posix-path). GHI #1140 (ledger reorder blocked as a manual edit; deconflict utility request). GHI #1143 (gz check hang with no timeout). Cross-link comment on GHI #973. Files: `tests/hooks/test_commit_locus_survives_precommit_stash.py`, `src/gzkit/quality.py`, `src/gzkit/hooks/guards.py`, `src/gzkit/ledger_merge.py`, `src/gzkit/events.py`.

## Settled Rulings

1148 rulings booked and carried forward. The corpus lives in `.gzkit/handoffs/rulings.jsonl` — read it with `gz handoff rulings`.

Do NOT re-open these. A ruling booked once keeps arriving; it is carried by reference from the append-only store, not by copying the whole corpus into every successor document (GHI #838).
