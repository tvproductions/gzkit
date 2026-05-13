# Plan: OBPI-0.0.32-05 — gz init --update flag

## Context

Implements ADR-0.0.32 Feature Checklist item #5: add `gz init --update` as a third mode of `gz init` that performs version-aware refresh of the adopter's `.gzkit/<surface>/` from the wheel's package data, with three-state detection (IDENTICAL/STALE/EDITED), preserving operator edits and surfacing conflicts. Closes failure class D from GHI #318.

Foundation-kind + Heavy-lane → brief-level Gate 5 attestation required.

## Files

**Modify:**
- `src/gzkit/commands/init_cmd.py` — add `--update` dispatch, refresh dispatch logic, three-state detection function
- `src/gzkit/cli/parser_governance.py` — add `--update` flag at the existing `p_init` subparser (lines 107-151)
- `src/gzkit/skills/__init__.py` — add `refresh_core_skills` (if needed for refresh-mode semantics)
- `src/gzkit/rules/__init__.py` — add `refresh_core_rules` (if needed)
- `src/gzkit/chores/__init__.py` — add `refresh_core_chores` (if needed)
- `docs/user/manpages/init.md` — document three modes, marker contract, exit codes, dry-run
- `docs/user/runbook.md` — upgrade workflow section
- `features/init.feature` — three @REQ-tagged scenarios (create file)

**Create:**
- `tests/commands/test_init_update.py` — unit tests for three-state detection and `--update` dispatch
- `features/init.feature` — behave scenarios

## Steps

### Step 1: Author three-state detection function + unit tests (RED-GREEN)

Files: `src/gzkit/commands/init_cmd.py`, `tests/commands/test_init_update.py`

1. RED: Author `tests/commands/test_init_update.py` with 5 unit tests:
   - `test_detect_state_identical` — bytes match → IDENTICAL
   - `test_detect_state_stale_no_marker` — bytes differ, no operator-edit marker → STALE
   - `test_detect_state_edited_marker_present` — bytes differ, marker present → EDITED
   - `test_detect_state_edited_hash_mismatch` — bytes differ, no prior-version match → EDITED
   - `test_detect_state_missing_canonical` — package source unavailable → raise typed error
2. GREEN: Implement `_detect_refresh_state(project_path, canonical_bytes, *, marker_pattern) -> Literal["IDENTICAL", "STALE", "EDITED"]` in `init_cmd.py`. Use byte-comparison for IDENTICAL; regex marker check (`<!-- gzkit-canonical-version: X.Y.Z -->`) for EDITED.
3. Verify: `uv run -m unittest tests.commands.test_init_update -v`

### Step 2: Wire `--update` flag into parser + dispatch

Files: `src/gzkit/cli/parser_governance.py`, `src/gzkit/commands/init_cmd.py`

1. In `parser_governance.py` `p_init` block (lines 107-151), add:
   - `--update` flag (action="store_true", mutually exclusive with `--force` — use add_mutually_exclusive_group)
   - Update help/epilog to document the third mode
   - Update `set_defaults(func=...)` to pass `update=a.update` through to the init handler
2. In `init_cmd.py`, refactor `init()` entry function to route on flags:
   - `update=True, force=True` → exit 1 (usage error)
   - `update=True` → call new `_refresh_canonical_surfaces(project_root, dry_run)`
   - `force=True` → existing wipe-and-recreate path
   - default → existing repair path
3. Implement `_refresh_canonical_surfaces(project_root, dry_run) -> RefreshResult`:
   - Iterate surfaces (skills, rules, chores, personas, templates)
   - For each canonical artifact: read project copy, read wheel canonical via `importlib.resources.files`, detect state, dispatch (refresh STALE, skip IDENTICAL, conflict EDITED)
   - Collect per-artifact results and any conflicts
   - Return `RefreshResult` (Pydantic BaseModel) with `identical: list[str]`, `stale_refreshed: list[str]`, `edited_conflicts: list[str]`
4. Print structured summary at end-of-run; exit 3 if `edited_conflicts` non-empty; exit 0 otherwise
5. Verify: `uv run gz init --help | grep -- --update`; `uv run gz init --update --force` exits 1

### Step 3: Author behave scenarios

Files: `features/init.feature`, possibly `features/steps/init_steps.py`

1. Create `features/init.feature` with:
   - `@REQ-0.0.32-05-01` — Scenario: stale canonical refreshes cleanly (set up temp project, modify wheel-side canonical, run `gz init --update`, assert STALE→refreshed, exit 0)
   - `@REQ-0.0.32-05-02` — Scenario: project-edit preservation (add operator-edit marker to a canonical, run update, assert EDITED→not overwritten, exit 3)
   - `@REQ-0.0.32-05-03` — Scenario: conflict reporting (multiple EDITED states, assert structured summary lists each, exit 3)
2. Verify: `uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-01`, `-02`, `-03`

### Step 4: Manpage + runbook updates

Files: `docs/user/manpages/init.md`, `docs/user/runbook.md`

1. Update `docs/user/manpages/init.md`:
   - Add `--update` to the options table
   - New section: "Update Mode (Version-Aware Refresh)" — describes three modes, three-state detection, marker contract, dry-run, exit codes
   - Add example: `gz init --update --dry-run`
2. Update `docs/user/runbook.md` with a new "Upgrade Workflow" subsection under operator tasks, showing the canonical refresh ceremony
3. Verify: `uv run mkdocs build --strict`

### Step 5: Run full quality gates

1. `uv run gz arb ruff` (lint)
2. `uv run gz arb typecheck` (ty)
3. `uv run gz arb step --name unittest -- uv run -m unittest -q` (full test sweep)
4. `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict`
5. `uv run gz arb step --name behave -- uv run -m behave --tags=@REQ-0.0.32-05-01,@REQ-0.0.32-05-02,@REQ-0.0.32-05-03 features/init.feature`
6. `uv run gz validate --documents`

## Verification

```bash
uv run gz init --help | grep -- --update
uv run gz init --update --dry-run /tmp/gz-update-smoke
uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-01
uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-02
uv run -m behave features/init.feature --tags=@REQ-0.0.32-05-03
uv run gz check
uv run mkdocs build --strict
```

## Notes

### Destination-in-mind

Before writing this plan, the destination I had in mind: implement `--update` as a new flag on the existing `p_init` subparser (NOT extract to a separate `parser_init.py`), wire dispatch in `init_cmd.py`, use a `<!-- gzkit-canonical-version: X.Y.Z -->` body marker for the operator-edit detection mechanism, and structure the refresh as a pure function returning a typed result that the CLI handler renders.

### Rejected alternatives

- **Three-way merge against prior wheel version** — rejected because it requires shipping prior-version snapshots, increases wheel size, and is less robust than marker-based detection.
- **Content-hash manifest shipped with the wheel** — rejected because the manifest must be updated on every release and creates a second source of truth alongside the canonical bytes.
- **Extract init parser to `parser_init.py`** — rejected per Option A: simpler to add `--update` directly to `parser_governance.py` where `p_init` is already defined; extraction is yak-shaving for a one-flag addition.
- **`--update` as a separate `gz upgrade` subcommand** — rejected here because OBPI-14 already plans a distinct `gz upgrade` for surface-only refresh; `gz init --update` is the project-refresh ceremony per ADR § Decision.

### Operator-edit marker choice (REQ-04)

Use marker (a): `<!-- gzkit-canonical-version: X.Y.Z -->` body marker.
- The scaffolder writes the marker on initial copy (`gz init`).
- `--update` updates the marker after a refresh.
- Manual operator edits remove or invalidate the marker (or change content without bumping it), which is detected as EDITED.
- Composes with existing `skill-version:` frontmatter (skills) and `<!-- rule-version: X.Y.Z -->` (rules) per `.claude/rules/skill-surface-sync.md` — the canonical-version marker tracks "version of canonical content delivered by the wheel" and is distinct from the surface-author's version semantics.
