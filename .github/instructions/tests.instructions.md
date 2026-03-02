---
applyTo: "tests/**"
---

# Test Policy (canonical)

> **Flag defects, never excuse them.** If a test reveals a defect in code, config, or test infrastructure — flag it as a defect. Never rationalize a failing or skipped test as "pre-existing" or "not in scope". Fix it or file a GHI.

-   Use **stdlib `unittest`**; no pytest.
-   Prefer **table-driven** tests with deterministic seeds; no network/external services.
-   **Smoke/BVT ≤60s**; cover current-scope surfaces only.
-   Fixtures: local, small, reproducible; avoid huge goldens.
-   **Database isolation**: Unit tests MUST use `TempDBMixin` or `tempfile` temp DBs; NEVER use live/production database (`load_settings().warehouse.db_path`).

## DB Isolation (Django-like philosophy)

-   Never touch the live/production DB from tests.
-   Prefer a shared in-memory SQLite DB for speed and isolation when feasible:
    -   Use a URI like `file:airlineops_test?mode=memory&cache=shared` and open connections with `sqlite3.connect(uri=True)`.
    -   Or pass a `sqlite3.Connection`/`db_uri` to code under test that supports it.
-   Otherwise, use `tests._tempdb.TempDBMixin` which provides a per-class temp file DB path via `self.db_path` / `cls.db_path`.
-   Always pass `sqlite_path`/`db_path` to functions under test; do not read `load_settings().warehouse.db_path` inside tests.

## Adapter Testing

Warehouse adapter tests (`tests/warehouse/adapters/`) use **mock-only** patterns. Adapter unit tests patch external dependencies — no live DB, no integration tests, no network calls.

### What to mock

-   **URLs and HTTP calls** — patch URL builders and download functions
-   **Config registries** — patch `get_cadence()`, `normalize_period()`, and calendar lookups
-   **Filesystem I/O** — use `tempfile` for any path-dependent logic
-   **External resolvers** — patch the resolver functions imported into the adapter module

### What NOT to do

-   **No live database access** — adapter tests validate delegation logic, not SQL
-   **No integration tests** — adapter correctness = correct delegation + correct period normalization
-   **No network calls** — all URL resolution is mocked

### Mock path rule

Mock paths MUST target the **import location** inside the adapter module, not the original definition site:

```python
# ✅ CORRECT — patches where the adapter imports it
@patch("airlineops.warehouse.adapters.bts_db10.db10.normalize")

# ❌ WRONG — patches the original module (adapter still sees the real function)
@patch("airlineops.warehouse.ingest.resolvers.bts.db10.normalize")
```

### Exemplars

-   `tests/warehouse/adapters/test_bts_db10_adapter.py` — quarterly adapter with `@patch` for normalize/load delegation
-   All adapter tests in `tests/warehouse/adapters/` follow this pattern (439+ tests)

### Enforcement

`tests/policy/test_adapter_mock_only_policy.py` statically scans adapter test files for forbidden patterns (live DB, network calls, config leakage). Runs via the `policy-tests` pre-commit hook — violations block commits.

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

### Pattern 2: TempDBMixin for Databases

Use `tests._tempdb.TempDBMixin` for SQLite databases. It provides Windows-safe cleanup with automatic garbage collection:

```python
from tests._tempdb import TempDBMixin

class TestDatabase(TempDBMixin, unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()  # Initializes cls.db_path (temp file)
        conn = sqlite3.connect(cls.db_path)
        # ... create schema ...
        conn.close()

    def test_query(self):
        result = query_db(self.db_path)
        self.assertEqual(result, expected)

    # tearDown automatic; TempDBMixin handles Windows file locking
```

### Pattern 3: Manual Cleanup (Only If Necessary)

If context managers or TempDBMixin don't fit, use `safe_rmtree()` from `tests._tempdb` with proper file handle cleanup:

```python
from tests._tempdb import safe_rmtree

class TestWithManualCleanup(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        # ✅ CORRECT: Use safe_rmtree with retry logic
        safe_rmtree(self.temp_dir)

    # ❌ WRONG (DO NOT USE):
    #   shutil.rmtree(self.temp_dir)  # Fails on Windows with file locking
    #   shutil.rmtree(self.temp_dir, ignore_errors=True)  # Silent failures
```

### Anti-Patterns (DO NOT USE)

| Pattern | Problem | Solution |
|---------|---------|----------|
| `shutil.rmtree(temp_dir)` in tearDown | Windows file locking (PermissionError: WinError 32) | Use context manager or safe_rmtree |
| `shutil.rmtree(..., ignore_errors=True)` | Silent failures; no retry logic | Use safe_rmtree with explicit error handling |
| Closing file handles after deletion attempt | File still locked during rmtree | Close handles BEFORE rmtree; use context manager |
| No `gc.collect()` before cleanup | Lingering file references on Windows | safe_rmtree calls gc.collect() automatically |
| Manual `os.remove()` in loop | Partial cleanup on error | Use context manager or safe_rmtree for atomic cleanup |

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
class TestReport(TempDBMixin, unittest.TestCase):
        @classmethod
        def setUpClass(cls):
                super().setUpClass()
                conn = sqlite3.connect(cls.db_path)
                conn.execute("CREATE TABLE bts_db10(period TEXT, carrier TEXT, operating_revenue INT)")
                conn.executemany("INSERT INTO bts_db10 VALUES(?,?,?)", [("2024-Q3","AA",220),("2024-Q3","DL",215)])
                conn.commit(); conn.close()

        def test_top2(self):
                out = summarize(period="2024-Q3", by="carrier", metric="operating_revenue", limit=2, sqlite_path=self.db_path)
                self.assertEqual([r["carrier"] for r in out], ["AA","DL"])
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
