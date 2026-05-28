# Plan: OBPI-0.0.64-03-subdivision-driven-seq-advancement

## Context

- **OBPI:** OBPI-0.0.64-03-subdivision-driven-seq-advancement
- **Parent ADR:** ADR-0.0.64-task-envelope-and-planning-decomposition
- **Lane:** Heavy
- **Brief:** `docs/design/adr/foundation/ADR-0.0.64-task-envelope-and-planning-decomposition/obpis/OBPI-0.0.64-03-subdivision-driven-seq-advancement.md`

## ADR Decision Item (verbatim)

> OBPI-0.0.64-03: **subdivision-driven-seq-advancement** — Add `next_seq_for_req(req_id: str) -> int` helper to `src/gzkit/tasks.py` (queries ledger for max `seq` under `(req_id, current_obpi_id)`, returns +1). Add `gz task start --req REQ-X --seq next|N` CLI surface (subcommand additive to existing `gz task ...` shape). Preserve `d70793c4`'s `seq=01` auto-coordination as default-bucket fallback. Add subdivision sub-invariant to `.gzkit/rules/task-discovery.md` (bump rule version). Tests: `next_seq_for_req` returns 1 on empty ledger, N+1 on populated; `gz task start --seq next` mints next-available; explicit `--seq N` is honored when N doesn't collide. (heavy lane: new CLI surface).

## Files

### In scope (expanded from brief — Allowed Paths gap noted in audit)

- `src/gzkit/tasks.py` — add `next_seq_for_req` helper
- `src/gzkit/commands/task.py` — add `task_start_by_req_cmd`, update imports
- `src/gzkit/cli/parser_artifacts.py` — wire `--req`/`--seq` flags into `gz task start`
- `tests/test_tasks.py` — unit tests for `next_seq_for_req`
- `tests/governance/test_task_start_by_req.py` — CLI integration tests (new file)
- `.gzkit/rules/task-discovery.md` — bump rule version 0.1.0 → 0.2.0
- `docs/user/manpages/task-start.md` — document new `--req`/`--seq` flags

### Out of scope

- New dependencies
- CI files, lockfiles
- Any path not listed above

## Steps

### Step 1: Add `next_seq_for_req` to `src/gzkit/tasks.py`

Add a pure function that takes a req_id and a list of existing TASK ID strings
and returns the next available seq number:

```python
def next_seq_for_req(req_id: str, *, existing_task_ids: list[str]) -> int:
    """Return next available seq for req_id given already-started TASK IDs.

    Scans existing_task_ids for TASK IDs derived from req_id (same semver,
    obpi_item, req_index prefix) and returns max(seq) + 1. Returns 1 if no
    matches exist (empty ledger case).
    """
    m = _REQ_TO_TASK_RE.match(req_id)
    if not m:
        msg = f"Invalid REQ ID format: {req_id!r} (expected REQ-X.Y.Z-NN-MM)"
        raise ValueError(msg)
    semver, obpi_item, req_index = m.groups()
    prefix = f"TASK-{semver}-{obpi_item}-{req_index}-"
    max_seq = 0
    for task_id_str in existing_task_ids:
        if task_id_str.startswith(prefix):
            try:
                tid = TaskId.parse(task_id_str)
                max_seq = max(max_seq, int(tid.seq))
            except ValueError:
                pass
    return max_seq + 1
```

### Step 2: Add `task_start_by_req_cmd` to `src/gzkit/commands/task.py`

Add `re` import and a REQ-to-OBPI pattern. Add new function that:
- Loads ledger
- Derives obpi_id and adr_id from req_id
- Gets existing task IDs for the OBPI
- If seq_arg == "next": calls `next_seq_for_req` to get N
- If seq_arg is an integer string: validates no collision with existing tasks
- Mints TASK ID via `derive_req_task_id(req_id, seq=seq_num)`
- Emits `task_started` event
- Reports result (JSON or human-readable)

Also update the import from gzkit.tasks to include `next_seq_for_req`.

### Step 3: Wire `--req`/`--seq` flags into parser in `src/gzkit/cli/parser_artifacts.py`

Modify the `p_task_start` block in `_register_task_parsers`:
- Add `"task_start_by_req_cmd": "gzkit.commands.task"` to the `_LAZY_IMPORTS` table
- Make `task_id` positional optional (`nargs="?"`)
- Add `--req` flag (REQ identifier)
- Add `--seq` flag (`"next"` or integer string)
- Update the `set_defaults` lambda to route:
  - If `a.req`: call `task_start_by_req_cmd(req_id=a.req, seq_arg=a.seq, as_json=a.as_json)`
  - Else: call `task_start_cmd(task_id_str=a.task_id, as_json=a.as_json)`

### Step 4: Write tests

#### Unit tests in `tests/test_tasks.py`

Add to existing test file:
- `TestNextSeqForReq` class with:
  - `test_returns_1_on_empty` — empty list → 1
  - `test_returns_n_plus_1_on_populated` — list with seq=01 → 2; list with max seq=03 → 4
  - `test_ignores_different_req_prefix` — different req_index → not counted
  - `test_invalid_req_id_raises` — non-matching req_id → ValueError

#### Integration tests in `tests/governance/test_task_start_by_req.py` (new file)

- `TestTaskStartByReqCmd` with:
  - `test_seq_next_mints_first_task` — empty ledger → mints seq=01
  - `test_seq_next_mints_next_available` — ledger with seq=01 → mints seq=02
  - `test_explicit_seq_honored_no_collision` — seq=3 on clean ledger → mints seq=03
  - `test_explicit_seq_collision_raises` — seq=01 on ledger with seq=01 → GzCliError

Decorate tests with `@covers("REQ-0.0.64-03-01")` (or appropriate REQ IDs).

### Step 5: Bump `.gzkit/rules/task-discovery.md` rule version

Change `> **Rule version:** 0.1.0` → `0.2.0` in the header.
Add a sentence under "Subdivision sub-invariant" linking the `--seq next|N`
CLI surface as the enforcement mechanism.

### Step 6: Update `docs/user/manpages/task-start.md`

Add `--req` and `--seq` flags to the Flags table.
Add examples showing the new `--req REQ-X --seq next|N` usage form.
Update description to mention the REQ-based start mode.

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.64-03-subdivision-driven-seq-advancement --json
```

## Notes

- `next_seq_for_req` is a pure function (no I/O) — ledger loading stays in
  `commands/task.py`
- Existing `gz task start TASK-X.Y.Z-NN-MM-PP` positional form is preserved
- `--seq next` and `--seq N` are mutually exclusive with the positional form
- `task-discovery.md` already exists (OBPI-02 landed); only bump version
