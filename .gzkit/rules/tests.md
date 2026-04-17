---
id: tests
paths:
  - "tests/**"
description: Test policy and coverage requirements
---

# Test Policy (canonical)

These are instructions to you — the executing agent — when writing, running,
or evaluating tests. TDD discipline is the most commonly rationalized-away
practice in this codebase. Every anti-pattern below has been observed in
production agent sessions. Read accordingly.

> **Flag defects, never excuse them.** If a test reveals a defect in code, config, or test infrastructure — flag it as a defect. Never rationalize a failing or skipped test as "pre-existing" or "not in scope". Fix it or file a GHI.

## Red-Green-Refactor (TDD Discipline)

Gate 2 is named TDD. This is what TDD means — follow it.

**Red-Green-Refactor is a repeating cycle per behavior increment:**

- **Red:** Write a test for a behavior required by the OBPI brief (`REQ-*` identifier). Run it. Watch it fail for the right reason — the function does not exist yet, or the behavior is not implemented yet. A test that passes on first run is not Red.
- **Green:** Write the **simplest code** that makes the test pass. Green does not mean perfect — it means the test passes. Do not overbuild.
- **Refactor:** Improve the code's structure without changing its behavior. The passing tests protect you. Renaming, deduplication, simplification — all valid. Adding new behavior is not refactoring — that starts a new Red.

**The rhythm:** first define the behavior, then make it work, then make it clean.

**Derivation rule:** Test cases derive from OBPI brief acceptance criteria, not from the implementation. Tests verify the spec was met, not that the code does what it does. When adding tests outside a pipeline run, locate the governing OBPI brief and derive from its requirements.

**Anti-patterns:**
- Writing tests after implementation that confirm what the code already does (implementation-derived tests)
- Writing tests "alongside" without seeing them fail first (skipping Red)
- Writing all tests at once before any implementation (test-dump, not TDD)
- Refactoring while tests are still failing (mixing Green and Refactor)

## TASK-Driven Workflow (GHI-160 Phase 6)

Every code-change GHI decomposes into TASKs via `gz task`, and every commit
touching `src/**` or `tests/**` must carry a `Task:` trailer. The
four-tier chain `task → req → obpi → adr` is the only way to trace a code
change back to governance intent.

**Binding steps for any GHI-originated code fix:**

1. Identify the REQ(s) the fix addresses. Use `gz covers <ADR-ID>` to locate.
2. For each REQ, start a TASK: `gz task start TASK-X.Y.Z-NN-MM-PP`.
3. Perform the TDD cycle (Red → Green → Refactor) for that TASK.
4. Commit with the trailer: `Task: TASK-X.Y.Z-NN-MM-PP` as the final line.
5. Complete the TASK: `gz task complete TASK-X.Y.Z-NN-MM-PP`.
6. Decorate the new tests with `@covers(REQ-X.Y.Z-NN-MM)`.

**Verification:**

```bash
uv run gz validate --commit-trailers   # flags HEAD commits missing Task: trailer
uv run gz validate --requirements      # flags OBPIs with bare REQUIREMENTS sections
```

**Anti-patterns:**
- Skipping `gz task start` and writing a Task: trailer from memory — the
  ledger state-machine enforcement is the proof, the trailer is the link.
- Using a single TASK for multiple unrelated REQ fixes — breaks the
  REQ-granularity of the coverage graph.
- Orphan test files (no `@covers`) — invisible to `gz covers`.

## General Rules

- Use **stdlib `unittest`**; no pytest.
- Prefer **table-driven** tests with deterministic seeds; no network/external services.
- **Smoke/BVT <=60s**; cover current-scope surfaces only.
- Fixtures: local, small, reproducible; avoid huge goldens.
- **Database isolation**: Unit tests MUST use `tempfile` temp DBs; NEVER use live/production databases.

## Two runners, one test surface (GHI #181, #182)

gzkit does not have a separate "integration tier" under `unittest`. There
are two runners and they play different roles:

| Runner | Location | Purpose | Contract |
|--------|----------|---------|----------|
| `unittest` | `tests/` | Pure Python behavior, command contracts | Mocked subprocess boundaries; deterministic; fast |
| `behave` | `features/` | End-to-end CLI and governance scenarios | Real operator flows, Gherkin-readable |

`gz test` runs `unittest` over `tests/` and then `behave` over `features/`.
Both gates must pass for `gz check`.

### Unit-tier contract

A test under `tests/` must:

- Mock every subprocess boundary it touches. The canonical helpers in
  `tests/commands/common.py` are:
  - `_uv_sync_patcher` — stubs `gzkit.commands.init_cmd._run_uv_sync`
  - `_git_subprocess_patcher` — stubs `gzkit.utils.git_cmd` at every
    import site used by `gz git-sync`
  - `_quick_init(mode)` — 5x faster replacement for
    `runner.invoke(main, ["init"])` when the test is not exercising
    `gz init` itself
- Complete in < 200ms on a typical workstation
- Be deterministic across repeated runs without filesystem cleanup races
- Use `tempfile` temp DBs; NEVER touch live/production databases

Tests that exercise `gz init` directly (e.g. `tests/commands/test_init.py`)
keep `_uv_sync_patcher` module-level — `gz init` itself is the subject, but
its `uv sync` subprocess child is always mocked. Tests that touch real git
state (e.g. closeout-ceremony fixtures) may use `_init_git_repo` from the
common helper; this is a deliberate exception for tests where the real git
history is load-bearing and the mocking overhead exceeds the subprocess
cost.

### End-to-end coverage lives in behave

If a scenario requires real `git` subprocess semantics, real `uv sync`, or
a real `gz init` template-rendering round trip for its assertion, it
belongs in `features/*.feature`. The behave runner's step definitions
(`features/steps/`) handle subprocess setup explicitly, and the Gherkin
surface keeps the operator intent visible. Adding a third tier under
`unittest` (the mistake GHI #182 closes) obscures the boundary and
duplicates behave's role.

### Canonical history

- **GHI #181** (landed in `e22ac553`): introduced `tests/integration/` as
  a second `unittest` tier to isolate 83 subprocess-wrapping tests from
  the unit tier. Fast fix for the symptom (`gz test` from 90s to 30s),
  but labeled the wrong class of failure.
- **GHI #182** (this rewrite): per the DO IT RIGHT maxim in
  `.gzkit/rules/behavioral-invariants.md` § 6a/6c, the thorough fix is
  per-test triage — every test under the old `tests/integration/` was
  either (a) already mockable at the Python level and relocated back to
  `tests/commands/` with `_git_subprocess_patcher` / `_uv_sync_patcher` /
  `_quick_init`, or (b) genuinely E2E and the operator flow it covers
  belongs in `features/`. The triage decisions are recorded in
  `artifacts/audits/ghi-182-triage.md`. `tests/integration/`, the
  `load_tests` gating protocol, and the `gz test --integration` flag are
  removed.

### Anti-patterns

- Adding a third tier (`--integration`, `--e2e`, `--slow`) to `gz test` —
  the runner boundary (`unittest` vs `behave`) is the gate
- Spawning real `git` or `uv sync` in a `tests/` module without a
  documented justification — mock it with `_git_subprocess_patcher` /
  `_uv_sync_patcher` first
- Using `runner.invoke(main, ["init"])` when `_quick_init` would produce
  equivalent fixture state 5x faster
- Porting a subprocess-spawning test to behave without checking whether
  `features/` already covers the scenario — behave duplication is the
  same defect one layer down
- Deleting a test without verifying its coverage is preserved elsewhere

## DB Isolation (Django-like philosophy)

- Never touch live/production DBs from tests.
- Prefer shared in-memory SQLite DB for speed and isolation.
- Always pass `sqlite_path`/`db_path` to functions under test.

## Cross-Platform Test Cleanup (Windows-Critical)

**BINDING RULE:** Never use raw `shutil.rmtree()` in test tearDown.

### Pattern 1: Context Manager (Preferred)

```python
class TestSomething(unittest.TestCase):
    def test_with_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            test_file = Path(temp_dir) / "data.json"
            test_file.write_text("{}")
            result = process_dir(temp_dir)
            self.assertEqual(result, expected)
```

## Coverage Floor

- **Minimum line coverage: 40.00%**
- Before closing any brief, verify coverage has not regressed.

## Run

- `uv run ruff check . --fix && uv run ruff format .`
- `uv run -m unittest -v`

## Verify

- All tests PASS; smoke suite <=60s.
- Coverage >=40.00%.
