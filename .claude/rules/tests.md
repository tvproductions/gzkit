---
paths:
  - "tests/**"
---

# Test Policy (canonical)

> **Flag defects, never excuse them.** If a test reveals a defect in code, config, or test infrastructure — flag it as a defect. Never rationalize a failing or skipped test as "pre-existing" or "not in scope". Fix it or file a GHI.

-   Use **stdlib `unittest`**; no pytest.
-   Prefer **table-driven** tests with deterministic seeds; no network/external services.
-   **Smoke/BVT ≤60s**; cover current-scope surfaces only.
-   Fixtures: local, small, reproducible; avoid huge goldens.
-   **Database isolation**: Unit tests MUST use `tempfile` temp DBs; NEVER use live/production databases.

## DB Isolation (Django-like philosophy)

-   Never touch live/production DBs from tests.
-   Prefer a shared in-memory SQLite DB for speed and isolation when feasible:
    -   Use a URI like `file:gzkit_test?mode=memory&cache=shared` and open connections with `sqlite3.connect(uri=True)`.
    -   Or pass a `sqlite3.Connection`/`db_uri` to code under test that supports it.
-   Always pass `sqlite_path`/`db_path` to functions under test; do not read paths from settings inside tests.

## Cross-Platform Test Cleanup (Windows-Critical)

**BINDING RULE:** Never use raw `shutil.rmtree()` in test tearDown. Tests written on Mac may fail silently on Windows due to file locking.

### Pattern 1: Context Manager (Preferred)

Use `tempfile.TemporaryDirectory()` or equivalent context manager. This ensures cleanup happens with proper exception handling:

```python
class TestSomething(unittest.TestCase):
    def test_with_temp_dir(self):
        with tempfile.TemporaryDirectory() as temp_dir:
            # Create test artifacts
            test_file = Path(temp_dir) / "data.json"
            test_file.write_text("{}")

            # Run test
            result = process_dir(temp_dir)
            self.assertEqual(result, expected)

            # Cleanup automatic on exit (Windows-safe)
```

**Why preferred:** Context managers handle cleanup automatically, even if an exception occurs. They work reliably on Windows, macOS, and Linux.

### Pattern 2: Manual Cleanup (Only If Necessary)

If context managers don't fit, use `shutil.rmtree()` with proper file handle cleanup:

```python
class TestWithManualCleanup(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)
```

### Anti-Patterns (DO NOT USE)

| Pattern | Problem | Solution |
|---------|---------|----------|
| `shutil.rmtree(temp_dir)` in tearDown | Windows file locking (PermissionError: WinError 32) | Use context manager or context manager |
| `shutil.rmtree(..., ignore_errors=True)` | Silent failures; no retry logic | Use context manager with explicit error handling |
| Closing file handles after deletion attempt | File still locked during rmtree | Close handles BEFORE rmtree; use context manager |
| No `gc.collect()` before cleanup | Lingering file references on Windows | context manager calls gc.collect() automatically |
| Manual `os.remove()` in loop | Partial cleanup on error | Use context manager or context manager for atomic cleanup |

### Why Windows File Locking Happens

On Windows:
-   File handles may not release immediately after `.close()`
-   SQLite connections retain locks until garbage collection
-   `shutil.rmtree()` fails on first locked file (no retry)
-   `tempfile` module cleanup at interpreter exit races with manual cleanup

On Mac/Linux:
-   File handles release immediately after `.close()`
-   File deletion succeeds even with lingering references (Unix semantics)
-   Developers unaware of Windows behavior write Mac-only tests

**Prevention:** Always test with `uv run` (ensures subprocess isolation) and validate on Windows before pushing.

## NamedTemporaryFile Pitfall

When using `tempfile.NamedTemporaryFile()`, close the handle immediately after getting the path:

```python
# ✅ CORRECT
with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
    db_path = tmp.name  # Get path while handle is open
# Handle now closed; safe to use db_path

# ❌ WRONG (file may be locked by open handle)
tmp = tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False)
db_path = tmp.name
# ... later ...
tmp.close()  # Only now is handle released
```

Example (curated table fixture):

```python
class TestWithDB(unittest.TestCase):
    def test_with_temp_db(self):
        with tempfile.NamedTemporaryFile(suffix=".sqlite", delete=False) as tmp:
            db_path = tmp.name
        try:
            conn = sqlite3.connect(db_path)
            conn.execute("CREATE TABLE items(name TEXT, value INT)")
            conn.executemany("INSERT INTO items VALUES(?,?)", [("a", 1), ("b", 2)])
            conn.commit()
            conn.close()
            # ... test logic using db_path ...
        finally:
            Path(db_path).unlink(missing_ok=True)
```

## Coverage Floor

-   **Minimum line coverage: 40.00%** (frozen as of 2025-11-11, CHORE-coverage-40pct)
-   Before closing any brief (ADR/CHORE/FIX), verify coverage has not regressed:
    ```bash
    uv run -m coverage run -m unittest discover -q
    uv run -m coverage report --precision=2 | grep "^TOTAL"
    ```
-   If coverage drops below 40%, **add tests** to restore the floor before committing.
-   Deleting dead code is exempt (coverage may rise naturally).
-   Prefer adding tests for **new code** rather than backfilling old modules.

## Run

-   `uv run ruff check . --fix && uv run ruff format .`
-   `uv run -m unittest -v`

## Verify

-   All tests PASS; smoke suite ≤60s on a typical laptop.
-   Coverage ≥40.00% (run coverage report if files changed in `src/`).
