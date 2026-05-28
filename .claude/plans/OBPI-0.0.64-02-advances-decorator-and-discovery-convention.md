# Plan: OBPI-0.0.64-02 advances-decorator-and-discovery-convention

## Context

**OBPI:** OBPI-0.0.64-02-advances-decorator-and-discovery-convention
**Parent ADR:** ADR-0.0.64-task-envelope-and-planning-decomposition
**Lane:** Heavy
**Decision item (verbatim):** "OBPI-0.0.64-02: **advances-decorator-and-discovery-convention** — Add `@advances(TASK-...)` decorator in `src/gzkit/tasks.py` as substantive peer of `@covers`. Decoration-time validation; captures `fn.__code__.co_filename` (rendered `.as_posix()`) + `fn.__code__.co_firstlineno`; registers `TaskAttributionRecord` (Pydantic `BaseModel` + `ConfigDict(frozen=True, extra='forbid')`) into module-level registry following `@covers`'s lazy `_load_known_reqs` pattern. Frontmatter `tasks: list[str]` channel added to structured-artifact schemas (brief frontmatter + ADR-package frontmatter where applicable). Author new rule `.gzkit/rules/task-discovery.md` codifying the four-channel taxonomy (Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`) with body-level `<!-- rule-version: 0.1.0 -->` marker + visible block quote per `.claude/rules/skill-surface-sync.md`. Tests: `@advances` decoration fail-closes on unknown TASK ID at import; registry surface exposes `TaskAttributionRecord` query API; frontmatter channel parses + validates via existing brief/ADR schema machinery. (heavy lane: new authoring contract; new rule)."

## Files (Allowed Paths)

- `src/gzkit/tasks.py` — add `@advances` decorator, `TaskAttributionRecord`, registry, helpers
- `.gzkit/rules/task-discovery.md` — CREATE new rule; four-channel taxonomy
- `tests/governance/test_advances_decorator.py` — CREATE new tests (TDD always allowed)

**Scope note:** `brief_structure.py` and `obpi_brief_structure.json` are NOT in the Allowed Paths. The frontmatter `tasks: list[str]` channel is documented as a convention in the new rule; schema enforcement is deferred per brief scope constraint.

## Steps

### Step 1: Write failing tests first (TDD Red)

Create `tests/governance/test_advances_decorator.py` with tests derived from the brief's acceptance criteria:

- REQ-0.0.64-02-01 coverage: Test `@advances` decorator registers `TaskAttributionRecord` with correct `task_id`, `source_fn`, `source_file` (.as_posix()), `source_line` fields. Test that decorated function's behavior is unchanged.
- REQ-0.0.64-02-01 coverage: Test registry query API — `get_task_registry()` returns a list of `TaskAttributionRecord`.
- REQ-0.0.64-02-01 coverage: Test decoration-time fail-close on invalid TASK ID format (ValueError).
- REQ-0.0.64-02-01 coverage: Test decoration-time fail-close on unknown parent REQ (ValueError with helpful message).
- REQ-0.0.64-02-02 coverage: Scope check — changes stay in `src/gzkit/tasks.py` (structural, verified by file diff).
- REQ-0.0.64-02-03 coverage: Test verification commands run cleanly after implementation.

Use `set_known_task_reqs()` and `reset_task_registry()` to isolate tests from on-disk state.

### Step 2: Implement `@advances` decorator in `src/gzkit/tasks.py` (TDD Green)

Add to `tasks.py` (after the existing git commit linkage section):

1. Import `pathlib`, `types`, `Callable` (from `collections.abc`), `TypeVar` (from `typing`)
2. Add `TaskAttributionRecord(BaseModel)` with `ConfigDict(frozen=True, extra="forbid")`:
   - `task_id: str` — TASK identifier
   - `source_fn: str` — qualified function name
   - `source_file: str | None` — `co_filename` rendered as `.as_posix()`
   - `source_line: int | None` — `co_firstlineno`
3. Add module globals: `_ADVANCES_REGISTRY: list[TaskAttributionRecord] = []` and `_KNOWN_TASK_REQS: frozenset[str] | None = None`
4. Add `_find_project_root_for_advances() -> Path | None` (mirrors `traceability._find_project_root()`)
5. Add `_load_known_task_reqs() -> frozenset[str]` — lazy scan briefs, cache known REQ IDs (same pattern as `_load_known_reqs()`)
6. Add `_qualified_fn_name(fn) -> str` helper
7. Add `advances(task_id_str: str) -> Callable[[_AF], _AF]`:
   - Call `TaskId.parse(task_id_str)` for format validation (raises `ValueError` on invalid)
   - Derive parent REQ: `f"REQ-{task_id.semver}-{task_id.obpi_item}-{task_id.req_index}"`
   - Load known task reqs, raise `ValueError` if parent not in known
   - In decorator: capture `code.co_filename` (`.as_posix()`), `code.co_firstlineno`, build `TaskAttributionRecord`, append to `_ADVANCES_REGISTRY`, return fn unchanged
8. Add `get_task_registry() -> list[TaskAttributionRecord]`
9. Add `set_known_task_reqs(reqs: frozenset[str]) -> None` (for testing)
10. Add `reset_task_registry() -> None` (for testing)

### Step 3: Create `.gzkit/rules/task-discovery.md`

Author the new rule with:
- YAML frontmatter: `id: task-discovery`, `paths: ["src/gzkit/**", "docs/design/adr/**", ".gzkit/**"]`, `description: ...`
- Body `<!-- rule-version: 0.1.0 -->` HTML comment (immediately after frontmatter)
- Visible `> **Rule version:** \`0.1.0\`` block quote with one-sentence rationale
- Four-channel taxonomy section: Python `@advances`, frontmatter `tasks:`, commit trailer, ledger `task_id`
- Convention for frontmatter `tasks: list[str]` in brief/ADR frontmatter (documents the channel; schema enforcement deferred to OBPI-04)
- Subdivision sub-invariant

### Step 4: Run quality checks

```bash
uv run ruff check . --fix && uv run ruff format .
uv run -m unittest tests/governance/test_advances_decorator.py -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

### Step 5: Run `uv run gz agent sync control-surfaces`

Propagates the new `.gzkit/rules/task-discovery.md` canonical rule to vendor mirrors (`.claude/rules/`, `.github/instructions/`).

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
test -f src/gzkit/tasks.py
test -f .gzkit/rules/task-discovery.md
```

## Notes

- Follow `@covers` pattern in `traceability.py` exactly for the lazy-load registry
- `source_file` MUST be rendered via `.as_posix()` per `.gzkit/rules/cross-platform.md`
- The `_load_known_task_reqs()` validates TASK IDs by checking their parent REQ in known briefs — this is the correct architectural coupling (TASK IDs are structurally tied to REQs)
- Brief Allowed Paths gap: `brief_structure.py` not listed; frontmatter `tasks:` schema enforcement deferred

## Plan-Before-Exploration Disclosure (gz-plan-audit Step 6a)

**Destination-in-mind:** Mirror `@covers` from `traceability.py` but in `tasks.py`, validate TASK IDs against their parent REQ rather than directly against TASK IDs (since the seq component can vary and TASK IDs aren't stored separately — the brief-scanned REQs ARE the anchor).

**Rejected alternatives:**
1. Validate TASK IDs against ledger `task_started` events — too heavy; requires ledger reads at decoration time; also unavailable in test contexts
2. Validate only format (no existence check) — violates the fail-close requirement; typo'd TASK IDs would silently pass
3. Put `@advances` in `traceability.py` alongside `@covers` — violates single-responsibility; `tasks.py` is the TASK module and all TASK machinery belongs there
4. Require exact TASK IDs including `seq` (full 5-part form) to exist in a pre-registered set — creates a chicken-and-egg problem (TASKs are minted by the pipeline, so they don't exist yet when `@advances` is written)
