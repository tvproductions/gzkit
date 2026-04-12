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

## General Rules

- Use **stdlib `unittest`**; no pytest.
- Prefer **table-driven** tests with deterministic seeds; no network/external services.
- **Smoke/BVT <=60s**; cover current-scope surfaces only.
- Fixtures: local, small, reproducible; avoid huge goldens.
- **Database isolation**: Unit tests MUST use `tempfile` temp DBs; NEVER use live/production databases.

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
