# Hexagonal Architecture Tune-Up Implementation Plan

> **For agentic workers:** REQUIRED: Use superpowers:subagent-driven-development (if subagents available) or superpowers:executing-plans to implement this plan. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Adopt hexagonal architecture with ports, adapters, domain extraction, structured logging, unified output formatting, config precedence, exception hierarchy, test fakes, progress indicators, and architectural policy tests — decomposed into 9 ordered increments.

**Architecture:** Three-layer model (CLI adapter, core domain, ports+adapters). Port Protocols (structural subtyping) define I/O boundaries. Core has zero I/O knowledge. Services receive dependencies via constructor injection. OutputFormatter is the single output chokepoint. structlog wraps stdlib logging with correlation IDs. Policy tests enforce import boundaries via AST scanning.

**Tech Stack:** Python 3.13, stdlib `unittest`, `argparse`, `typing.Protocol`, `json`, `pathlib`, `subprocess`, `tomllib`, `ast`; `pydantic` for models/config; `rich` for output/progress; `structlog` for logging; `PyInstaller` for binary distribution.

**Spec:** `docs/superpowers/specs/2026-03-15-hexagonal-architecture-tuneup-design.md`

---

## Chunk 1: Hexagonal Skeleton

Create the directory structure and define port Protocols. No behavior change — existing code continues to work unchanged.

### Task 1: Create directory structure

**Files:**
- Create: `src/gzkit/core/__init__.py`
- Create: `src/gzkit/ports/__init__.py`
- Create: `src/gzkit/adapters/__init__.py`
- Create: `tests/fakes/__init__.py`
- Create: `tests/unit/__init__.py`
- Create: `tests/integration/__init__.py`
- Create: `tests/policy/__init__.py`

- [ ] **Step 1: Create directories and __init__.py files**

Create the seven new directories with empty `__init__.py` files. Each `__init__.py` contains only a module docstring.

- [ ] **Step 2: Verify import paths work**

Run: `uv run python -c "import gzkit.core; import gzkit.ports; import gzkit.adapters"` — should succeed with no errors. Verify `tests/policy/` is discoverable.

- [ ] **Step 3: Commit**

```bash
git add src/gzkit/core/ src/gzkit/ports/ src/gzkit/adapters/ tests/fakes/ tests/unit/ tests/integration/ tests/policy/
git commit -m "feat: create hexagonal skeleton directories (core, ports, adapters, test layers)"
```

### Task 2: Define port Protocols

**Files:**
- Create: `src/gzkit/ports/interfaces.py`

- [ ] **Step 1: Write port interface definitions**

Define four port Protocols in `src/gzkit/ports/interfaces.py` using `typing.Protocol` (structural subtyping). Adapters satisfy these implicitly by matching method signatures — no inheritance required. The type checker (`ty`) verifies conformance at dev time.

```python
from typing import Protocol
from pathlib import Path

class FileStore(Protocol):
    """Port for filesystem operations."""

    def read_text(self, path: Path) -> str: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def exists(self, path: Path) -> bool: ...

    def iterdir(self, path: Path) -> list[Path]: ...

class ProcessRunner(Protocol):
    """Port for subprocess execution."""

    def run(self, cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]: ...

class LedgerStore(Protocol):
    """Port for append-only event persistence."""

    def append(self, event: dict) -> None: ...

    def read_all(self) -> list[dict]: ...

class ConfigStore(Protocol):
    """Port for configuration persistence."""

    def load(self) -> dict: ...

    def save(self, data: dict) -> None: ...
```

- [ ] **Step 2: Verify Protocols are importable**

Run: `uv run python -c "from gzkit.ports.interfaces import FileStore, ProcessRunner, LedgerStore, ConfigStore"` — should succeed.

- [ ] **Step 3: Run full test suite to verify no regressions**

Run: `uv run gz test`

- [ ] **Step 4: Commit**

```bash
git add src/gzkit/ports/interfaces.py
git commit -m "feat(ports): define FileStore, ProcessRunner, LedgerStore, ConfigStore Protocols"
```

---

## Chunk 2: Domain Extraction

Move pure logic out of mixed modules into `core/`. Existing I/O code calls into core instead of containing logic inline.

### Task 3: Extract domain models to core/models.py

**Files:**
- Create: `src/gzkit/core/models.py`
- Modify: `src/gzkit/ledger.py` (import from core)
- Test: `tests/unit/test_models.py`

- [ ] **Step 1: Write failing test for domain models**

Create `tests/unit/test_models.py` with tests that import from `gzkit.core.models` — models for LedgerEvent, governance states, lane types, ID validation patterns.

- [ ] **Step 2: Extract LedgerEvent and governance constants from ledger.py**

Move `LedgerEvent` dataclass/model, lane types, state enums, and ID validation regexes to `core/models.py`. Convert to Pydantic BaseModel per project rules. Leave I/O operations in `ledger.py`.

- [ ] **Step 3: Update ledger.py imports to use core/models.py**

Replace inline definitions with `from gzkit.core.models import LedgerEvent, ...`.

- [ ] **Step 4: Run tests to verify pass**

Run: `uv run gz test`

- [ ] **Step 5: Commit**

### Task 4: Extract pure logic to core modules

**Files:**
- Create: `src/gzkit/core/scoring.py` (from decomposition.py)
- Create: `src/gzkit/core/lifecycle.py` (ADR/OBPI state machines from cli.py)
- Create: `src/gzkit/core/validation_rules.py` (pure rules from validate.py)
- Modify: source modules to import from core
- Test: `tests/unit/test_scoring.py`, `tests/unit/test_lifecycle.py`, `tests/unit/test_validation_rules.py`

- [ ] **Step 1: Write failing tests for scoring module**

Tests import `gzkit.core.scoring` and verify scorecard computation logic (currently in `decomposition.py`).

- [ ] **Step 2: Move decomposition.py pure logic to core/scoring.py**

`decomposition.py` is already pure logic — relocate to `core/scoring.py`. Create a compatibility re-export in `decomposition.py` during transition.

- [ ] **Step 3: Write failing tests for lifecycle module**

Tests import `gzkit.core.lifecycle` and verify ADR/OBPI state transitions, promotion planning, gate readiness computation.

- [ ] **Step 4: Extract lifecycle logic from cli.py to core/lifecycle.py**

Extract ADR promotion planning (~150 LOC), gate readiness computation, OBPI completion validation rules. These are pure functions that take data in and return results — no I/O.

- [ ] **Step 5: Write failing tests for validation_rules module**

Tests import `gzkit.core.validation_rules` and verify frontmatter parsing, schema constraint checking, manifest validation rules.

- [ ] **Step 6: Extract pure validation rules from validate.py to core/validation_rules.py**

Move frontmatter parsing, field validation, constraint checking. Leave file-reading operations in validate.py.

- [ ] **Step 7: Update source module imports**

Update `cli.py`, `validate.py`, `decomposition.py` to import from `core/` modules.

- [ ] **Step 8: Run full test suite**

Run: `uv run gz test`

- [ ] **Step 9: Commit**

---

## Chunk 3: Exception Hierarchy & Exit Codes

Replace single GzCliError with retryability-oriented domain exception tree. Exit codes live as module constants, not baked into exception classes. The key runtime question for agent/pipeline consumers is "should I retry?" — not "what exit code?"

### Task 5: Create exception hierarchy and exit codes

**Files:**
- Create: `src/gzkit/core/exceptions.py`
- Create: `src/gzkit/core/exit_codes.py`
- Modify: `src/gzkit/commands/common.py` (alias GzCliError)
- Modify: `src/gzkit/cli.py` (update boundary pattern)
- Modify: `src/gzkit/validate.py` (rename ValidationError dataclass)
- Test: `tests/unit/test_exceptions.py`

- [ ] **Step 1: Write failing tests for exception hierarchy**

Test that `GzKitError`, `TransientError`, `PermanentError`, `OperatorError` exist with correct inheritance. Test that exit code constants exist in `exit_codes.py`.

- [ ] **Step 2: Create core/exit_codes.py with constants**

```python
# core/exit_codes.py
SUCCESS = 0
GENERAL_ERROR = 1
VALIDATION_ERROR = 2
RESOURCE_NOT_FOUND = 3
GOVERNANCE_ERROR = 4
CONFIG_ERROR = 5
```

- [ ] **Step 3: Create core/exceptions.py with retryability hierarchy**

```python
class GzKitError(Exception):
    """Base exception for all domain errors."""

class TransientError(GzKitError):
    """Temporary failure. Retry with backoff."""

class PermanentError(GzKitError):
    """Unrecoverable. Do not retry."""

class OperatorError(GzKitError):
    """Configuration or input error. Operator must intervene."""
```

- [ ] **Step 4: Rename existing ValidationError dataclass to ValidationResult**

In `validate.py`, rename the `ValidationError` dataclass to `ValidationResult`. Update all references.

- [ ] **Step 5: Alias GzCliError to GzKitError for backward compatibility**

In `commands/common.py`: `GzCliError = GzKitError` — existing code continues to work.

- [ ] **Step 6: Update CLI boundary pattern in main()**

Update `cli.py` `main()` to catch retryability-based exceptions and map to exit codes at the CLI boundary:

```python
try:
    handler(args)
    return exit_codes.SUCCESS
except OperatorError as exc:
    log.warning("command_failed", error=str(exc), error_type=type(exc).__name__)
    formatter.emit_error(str(exc))
    return _exit_code_for(exc)
except TransientError as exc:
    log.warning("transient_failure", error=str(exc))
    formatter.emit_error(str(exc))
    return exit_codes.GENERAL_ERROR
except PermanentError as exc:
    log.error("permanent_failure", error=str(exc))
    formatter.emit_error(str(exc))
    return _exit_code_for(exc)
```

- [ ] **Step 7: Run full test suite**

Run: `uv run gz test`

- [ ] **Step 8: Commit**

---

## Chunk 4: Test Fakes & Separation

Create in-memory port implementations and reorganize test directories.

### Task 6: Create test fakes

**Files:**
- Create: `tests/fakes/fake_filestore.py`
- Create: `tests/fakes/fake_process.py`
- Create: `tests/fakes/fake_ledger.py`
- Create: `tests/fakes/fake_config.py`
- Test: `tests/unit/test_fakes.py`

- [ ] **Step 1: Write failing tests that import fakes**

Tests verify `FakeFileStore`, `FakeLedgerStore`, `FakeProcessRunner`, `FakeConfigStore` satisfy their port Protocols via structural subtyping and provide in-memory behavior. Fakes do NOT inherit from Protocols — they match method signatures implicitly.

- [ ] **Step 2: Implement FakeFileStore**

In-memory dict-backed filesystem. Satisfies `FileStore` Protocol (no inheritance).

- [ ] **Step 3: Implement FakeLedgerStore**

In-memory list-backed event store. Satisfies `LedgerStore` Protocol (no inheritance).

- [ ] **Step 4: Implement FakeProcessRunner**

Configurable return values for subprocess calls. Satisfies `ProcessRunner` Protocol (no inheritance).

- [ ] **Step 5: Implement FakeConfigStore**

In-memory dict-backed config. Satisfies `ConfigStore` Protocol (no inheritance).

- [ ] **Step 6: Run tests to verify fakes work**

Run: `uv run -m unittest tests.unit.test_fakes -v`

- [ ] **Step 7: Commit**

### Task 7: Reorganize test directories

**Files:**
- Move: existing core logic tests → `tests/unit/`
- Move: existing CLI command tests → `tests/integration/`

- [ ] **Step 1: Move pure logic tests to tests/unit/**

Move test files that test core logic without CLI invocation: `test_config.py`, `test_decomposition.py`, `test_ledger.py`, `test_interview.py`, `test_superbook.py`, `test_superbook_models.py`, `test_superbook_parser.py`, `test_validate.py`, `test_hooks.py`, `test_obpi_validator.py`, `test_quality.py`, `test_pipeline_runtime.py`.

- [ ] **Step 2: Move CLI command tests to tests/integration/**

Move `tests/commands/` contents to `tests/integration/`.

- [ ] **Step 3: Update test discovery configuration**

Verify `uv run -m unittest discover -s tests` still finds all tests in the new structure.

- [ ] **Step 4: Run full test suite**

Run: `uv run gz test`

- [ ] **Step 5: Commit**

---

## Chunk 5: Config Precedence & Injection (ENV-Optional)

Migrate config to Pydantic with ENV-optional precedence chain. No env var config layer — environment variables are invisible state that can't be schema-validated and create a shadow configuration surface. Local override file (`.gzkit.local.json`, gitignored) handles per-machine customization.

### Task 8: Migrate config to Pydantic with ENV-optional precedence chain

**Files:**
- Modify: `src/gzkit/config.py`
- Test: `tests/unit/test_config.py`

- [ ] **Step 1: Write failing tests for precedence chain**

Test that CLI flags > config file (`.gzkit.json`) > local override file (`.gzkit.local.json`) > hard-coded defaults. Verify NO env var layer exists.

- [ ] **Step 2: Convert GzkitConfig and PathConfig from dataclasses to Pydantic BaseModel**

Apply `ConfigDict(frozen=True, extra="forbid")` per project rules. Use `Field(...)` with descriptions.

- [ ] **Step 3: Implement local override file support**

Support `.gzkit.local.json` (gitignored) for per-machine customization. Merged after `.gzkit.json` but before CLI flags.

- [ ] **Step 4: Implement precedence merge in load()**

Merge order: hard-coded defaults → `.gzkit.json` → `.gzkit.local.json` → CLI flags. No env var layer.

- [ ] **Step 5: Add .gzkit.local.json to .gitignore**

Ensure the local override file is gitignored.

- [ ] **Step 6: Run tests to verify pass**

Run: `uv run gz test`

- [ ] **Step 7: Commit**

### Task 9: Inject config at CLI boundary

**Files:**
- Modify: `src/gzkit/cli.py` (load config once in main())
- Modify: `src/gzkit/hooks/obpi.py` (receive config via constructor)
- Modify: other modules that call `GzkitConfig.load()` internally

- [ ] **Step 1: Audit all GzkitConfig.load() call sites**

Find every module that calls `GzkitConfig.load()` and list them.

- [ ] **Step 2: Load config once in main() and pass through args**

Load config in `main()` after parsing args, attach to `args` namespace or pass as parameter to handlers.

- [ ] **Step 3: Update services to receive config via constructor**

Replace internal `GzkitConfig.load()` calls with constructor parameters. Start with `ObpiValidator`.

- [ ] **Step 4: Run full test suite**

Run: `uv run gz test`

- [ ] **Step 5: Commit**

---

## Chunk 6: Output Formatter

Single chokepoint for all user-facing output. Add global flags.

### Task 10: Create OutputFormatter

**Files:**
- Create: `src/gzkit/cli/formatters.py`
- Modify: `src/gzkit/cli.py` (add global flags, wire formatter)
- Test: `tests/integration/test_formatters.py`

- [ ] **Step 1: Write failing tests for OutputFormatter**

Test emit() in JSON mode produces clean JSON on stdout. Test emit() in quiet mode produces nothing. Test emit() with Pydantic model uses model_dump_json(). Test emit_error() always writes to stderr.

- [ ] **Step 2: Implement OutputFormatter**

Create `cli/formatters.py` with `OutputMode` enum and `OutputFormatter` class. Handles human (Rich), JSON (model_dump_json/json.dumps), quiet (suppress), and error output.

- [ ] **Step 3: Add global flags to argument parser**

Add `--json`, `-q`/`--quiet`, `-v`/`--verbose`, `--debug` to the top-level parser in `_build_parser()`.

- [ ] **Step 4: Wire formatter into main() and pass to handlers**

Create formatter from parsed args in `main()`, pass to command handlers.

- [ ] **Step 5: Replace direct console.print() calls in command handlers**

Migrate command handlers to use `formatter.emit()` and `formatter.emit_error()` instead of direct `console.print()`.

- [ ] **Step 6: Run full test suite**

Run: `uv run gz test`

- [ ] **Step 7: Commit**

---

## Chunk 7: Structured Logging (structlog)

Add structlog dependency. Configure at startup. Correlation IDs. Verbosity levels.

### Task 11: Add structlog dependency and configuration

**Files:**
- Modify: `pyproject.toml` (add structlog dependency)
- Create: `src/gzkit/cli/logging_config.py`
- Modify: `src/gzkit/cli.py` (call configure_logging at startup)
- Test: `tests/unit/test_logging.py`

- [ ] **Step 1: Add structlog to dependencies**

Add `"structlog>=24.0"` to `[project.dependencies]` in `pyproject.toml`. Run `uv sync`.

- [ ] **Step 2: Write failing tests for logging configuration**

Test that `configure_logging()` sets up structlog with correlation ID, correct log level, stderr handler.

- [ ] **Step 3: Implement configure_logging()**

Create `cli/logging_config.py` with the `configure_logging()` function from the spec. Configures structlog wrapping stdlib logging, correlation ID binding, stderr handler (console when interactive, JSON otherwise), optional file handler.

- [ ] **Step 4: Wire into main()**

Call `configure_logging(level, log_file)` in `main()` before dispatching to command handlers. Map `--verbose` → INFO, `--debug` → DEBUG, default → WARNING.

- [ ] **Step 5: Add --log-file flag to parser**

Add `--log-file <path>` to the top-level parser.

- [ ] **Step 6: Replace bare logging in sync.py**

Replace the single `logging.getLogger(__name__)` in `sync.py` with `structlog.get_logger()`. Update the 2 warning calls to use structured key-value pairs.

- [ ] **Step 7: Add structured logging to core services**

Add `log.info("event_name", key=value)` calls to core service entry/exit points. Use snake_case event names.

- [ ] **Step 8: Run full test suite**

Run: `uv run gz test`

- [ ] **Step 9: Commit**

---

## Chunk 8: Progress Indication

Add rich.progress for long-running operations.

### Task 12: Add progress indicators

**Files:**
- Modify: `src/gzkit/cli.py` or relevant command handlers
- Modify: `src/gzkit/quality.py` (quality gate runs)
- Modify: `src/gzkit/sync.py` (sync operations)
- Modify: `src/gzkit/validate.py` (validation sweeps)
- Test: `tests/integration/test_progress.py`

- [ ] **Step 1: Write failing tests for progress suppression**

Test that progress output is suppressed in quiet mode and JSON mode. Test that progress writes to stderr, not stdout.

- [ ] **Step 2: Create progress helper**

Create a context manager or utility that wraps `rich.progress.Progress` with mode-aware suppression. Write to stderr. Suppress in quiet/JSON modes. Degrade in non-interactive terminals.

- [ ] **Step 3: Add progress to quality gate runs**

Wrap `lint`, `typecheck`, `test`, `check` commands with progress indication when operations are expected to take >1 second.

- [ ] **Step 4: Add progress to sync operations**

Wrap `sync_all()` with progress for skill mirroring, rule mirroring, manifest generation.

- [ ] **Step 5: Add progress to validation sweeps**

Wrap `validate_all()` with progress for artifact scanning.

- [ ] **Step 6: Run full test suite**

Run: `uv run gz test`

- [ ] **Step 7: Run full quality gates**

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
```

- [ ] **Step 8: Commit**

---

## Chunk 9: Policy Tests (Architectural Enforcement)

AST-scanning tests in `tests/policy/` that enforce import boundaries, ENV usage, and naming conventions. These tests scan source files — they do not import or execute application code.

### Task 13: Create policy tests

**Files:**
- Create: `tests/policy/test_import_boundaries.py`
- Create: `tests/policy/test_env_usage.py`
- Create: `tests/policy/test_naming_conventions.py`

- [ ] **Step 1: Write import boundary enforcement test**

Create `tests/policy/test_import_boundaries.py` using `ast` module to scan source files:
- Verify `core/` does not import from `cli/`, `adapters/`, `rich`, `argparse`
- Verify `ports/` imports only `typing` and stdlib type annotations
- Verify `tests/fakes/` imports only from `ports/` and stdlib

```python
import ast
import pathlib
import unittest

FORBIDDEN_CORE_IMPORTS = {"rich", "argparse"}
FORBIDDEN_CORE_PACKAGES = {"cli", "adapters"}

class TestImportBoundaries(unittest.TestCase):
    def test_core_does_not_import_cli_or_adapters(self):
        # AST scan all .py files in src/gzkit/core/
        ...

    def test_ports_imports_only_typing_and_stdlib(self):
        # AST scan all .py files in src/gzkit/ports/
        ...
```

- [ ] **Step 2: Write ENV usage enforcement test**

Create `tests/policy/test_env_usage.py` to scan CLI handler code for `os.getenv()` / `os.environ.get()` calls. Allowlist: `NO_COLOR`, `FORCE_COLOR`, `TERM`. Fail if any other env var access is found.

```python
class TestEnvUsage(unittest.TestCase):
    ALLOWED_ENV_VARS = {"NO_COLOR", "FORCE_COLOR", "TERM"}

    def test_no_env_vars_outside_allowlist(self):
        # AST scan for os.getenv / os.environ calls
        ...
```

- [ ] **Step 3: Write naming conventions test**

Create `tests/policy/test_naming_conventions.py`:
- Test files mirror source structure (snake_case modules)
- Modules use snake_case naming

- [ ] **Step 4: Run policy tests**

Run: `uv run -m unittest discover -s tests/policy -v`

- [ ] **Step 5: Verify policy tests pass with current codebase**

Policy tests should initially pass (or warn) against the current state. If violations exist, document them and set tests to warning mode initially, promoting to failure after Chunks 1-8 clean up the imports.

- [ ] **Step 6: Wire into gz test and CI**

Ensure `uv run gz test` includes `tests/policy/` in discovery. Policy tests run on every CI run.

- [ ] **Step 7: Run full quality gates**

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
```

- [ ] **Step 8: Commit**
