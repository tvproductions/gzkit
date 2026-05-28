# Plan: OBPI-0.0.64-05-gz-task-fanout-readback

## OBPI Reference

OBPI-0.0.64-05-gz-task-fanout-readback
Parent ADR: ADR-0.0.64-task-envelope-and-planning-decomposition
Lane: Heavy

## Context

OBPIs 01-04 of ADR-0.0.64 are attested_completed. This is the final OBPI.

Decision item 5 of the parent ADR declares:
- `gz task fanout <REQ-ID>` command (table default; `--detail` ASCII tree with file:line spans; `--json` machine-readable)
- Columns: TASK, seq, status, files_touched, edits, attribution_check
- `gz status` TASK fan-out summary block (per-REQ fan-out shape during work)

`gz task envelope diagnose` was already implemented in OBPI-04 and is out of scope here.

## Files

- `src/gzkit/commands/task.py` — add `task_fanout_cmd` + helpers
- `src/gzkit/cli/parser_artifacts.py` — register `gz task fanout` subcommand
- `src/gzkit/commands/status.py` — enhance `_task_summary_for_adr` with per-REQ data
- `src/gzkit/commands/status_render.py` — update `_print_status_task_section` with per-REQ fan-out block
- `tests/test_tasks.py` — fixture-based tests for all three output formats + `gz status` integration
- `docs/user/manpages/task-fanout.md` — new manpage (Heavy lane CLI requirement)

## Steps

### Step 1: Write failing tests (TDD Red phase)

Add test class `TestTaskFanoutCmd` to `tests/test_tasks.py`:
- `test_fanout_table_default` — given REQ-ID with tasks in fixture ledger, assert table output contains required columns (TASK, seq, status, files_touched, edits, attribution_check)
- `test_fanout_detail_mode` — given REQ-ID with `@advances`-registered tasks, assert `--detail` output contains file:line spans
- `test_fanout_json_mode` — given REQ-ID, assert `--json` output is valid JSON with all required fields
- `test_fanout_empty_req` — given REQ-ID with no tasks, assert graceful empty output
- `test_fanout_attribution_check_drift` — given OBPI with sig_c drift, assert attribution_check shows "drift"

### Step 2: Implement `_build_fanout_rows` and `task_fanout_cmd` in `task.py`

Add to `src/gzkit/commands/task.py`:

1. `_build_fanout_rows(ledger, req_id)` — helper that:
   - Derives OBPI-ID from REQ-ID (parse `REQ-semver-obpi_item-req_index`)
   - Scans ledger for all task lifecycle events to get status per task_id
   - Scans `artifact_edited` events with matching `task_id` to count `files_touched` (unique paths) and `edits`
   - Derives `attribution_check` by running OBPI-level sig_c via `_collect_ledger_task_ids_for_obpi_prefix` and checking layer-drift against frontmatter tasks; "drift" if drift detected, "pass" otherwise
   - Returns `list[dict]` with keys: task_id, seq (parsed from task_id), status, files_touched, edits, attribution_check

2. `task_fanout_cmd(req_id, *, detail=False, as_json=False)`:
   - Calls `_build_fanout_rows`
   - `--json`: dumps JSON array of row dicts
   - `--detail`: renders ASCII tree per task (task_id, status, then file:line spans from `get_task_registry()` if any)
   - Default: renders table with columns TASK, seq, status, files_touched, edits, attribution_check

### Step 3: Register `gz task fanout` in `parser_artifacts.py`

Add `"task_fanout_cmd": "gzkit.commands.task"` to the lazy dispatch map.

Add `task_fanout` subparser under `task` with:
- `req_id` positional argument
- `--detail` flag (ASCII tree mode)
- `--json` flag (machine-readable mode)
- Help text + examples in epilog
- `func=lambda a: _lazy("task_fanout_cmd")(a.req_id, detail=a.detail, as_json=a.as_json)`

### Step 4: Enhance `gz status` per-REQ fan-out

In `src/gzkit/commands/status.py`, update `_task_summary_for_adr`:
- Add `per_req` dict: maps REQ prefix → {total, completed, in_progress, pending, blocked, escalated}
- Derive REQ prefix from task_id (TASK-semver-obpi-reqidx-seq → REQ-semver-obpi-reqidx)
- Include `per_req` in returned dict

In `src/gzkit/commands/status_render.py`, update `_print_status_task_section`:
- When `per_req` is present and has ≥1 entry, render a per-REQ table after the aggregate summary line
- Format: `  REQ-X.Y.Z-NN-MM:  N/T done (X active, Y pending)` per REQ
- Keep the existing aggregate `Tasks: N/T done (tracing: required)` line as the header

### Step 5: Create manpage `docs/user/manpages/task-fanout.md`

New file following the existing task-*.md manpage pattern:
- Title: `gz task fanout`
- Synopsis: `gz task fanout <REQ-ID> [--detail] [--json]`
- Description paragraph
- Options table
- Examples section with real output

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run gz validate --documents
test -f docs/user/manpages/task-fanout.md
uv run gz task fanout --help
```

## Notes

- `attribution_check` is derived from OBPI-level sig_c (layer-drift across channels). Per-task
  granularity is coarse in this implementation — if the parent OBPI has layer-drift, all tasks
  in that fanout show "drift". Fine-grained per-task drift tracking can be added later.
- `files_touched` counts unique `path` values from `artifact_edited` events where `task_id`
  matches. If no worklog events carry `task_id`, files_touched=0 (correct — unannotated work
  is exactly what attribution-drift means).
- `--detail` tree uses `get_task_registry()` for `@advances` records. If no decorators reference
  this task, the tree shows only lifecycle events without file:line spans.
- Module size discipline: `task.py` is currently 508 lines. Adding `_build_fanout_rows` (~40 lines)
  + `task_fanout_cmd` (~50 lines) brings it to ~600 lines — at the module size limit per
  `.claude/rules/pythonic.md`. If size becomes a concern, extract `_fanout_helpers.py`.
