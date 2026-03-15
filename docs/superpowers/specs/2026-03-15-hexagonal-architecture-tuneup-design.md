# Hexagonal Architecture Tune-Up

**Date**: 2026-03-15
**Status**: Design approved, pending implementation plan

## Problem

gzkit's codebase grew organically around governance concerns. A gap analysis against the Python CLI best practices spec identified 7 full gaps and 8 partials. The structural root cause is that domain logic, I/O, and CLI presentation are interleaved:

- `cli.py` is 5,162 lines mixing argument parsing, business logic, filesystem operations, and Rich rendering
- 20 of 32 modules perform direct I/O (file reads, subprocess calls, network)
- Only 4 modules are pure logic (decomposition, interview, superbook_models, schemas)
- No Protocol or ABC interfaces exist anywhere in the source tree
- Services self-construct their dependencies (`ObpiValidator` creates its own `Ledger`)
- Single `GzCliError` exception class with no hierarchy
- No structured logging (1 bare `logging.getLogger()` in sync.py)
- No output formatter abstraction — commands call `console.print()` directly
- No `--quiet`, `--verbose`, or `--debug` global flags
- No progress indicators for long-running operations
- Config has no precedence chain (file > defaults only)
- No architectural enforcement tests — import boundaries exist only in prose

This blocks proper test isolation, makes dependency injection impossible, and prevents adding infrastructure cleanly.

## Goals

1. **Hexagonal layering** — Separate core domain logic from I/O and CLI concerns via ports and adapters
2. **Testability** — Enable unit tests with in-memory fakes instead of `mock.patch` on implementation internals
3. **Structured logging** — structlog with correlation IDs, verbosity levels, JSON file output
4. **Unified output** — Single OutputFormatter chokepoint supporting 5 modes (human, JSON, quiet, verbose, debug)
5. **Config discipline** — Precedence chain (ENV-optional), single load point, constructor injection
6. **Error clarity** — Domain exception hierarchy organized by retryability for agent/pipeline consumers
7. **Architectural enforcement** — Policy tests that enforce import boundaries and conventions via AST scanning

## Architecture

### CLI Spectrum Position

gzkit is a **platform CLI** (60+ commands, multiple domains, agent automation consumers). This means we adopt the scaling options where they apply: Protocol-based ports, policy tests for boundary enforcement, and JSON-everywhere config with Pydantic validation.

### Three-Layer Model

```
CLI Adapter Layer (cli/, commands/)
  Knows: argparse, rich, structlog config, OutputFormatter
  Does: parse args, wire adapters, call services, format output
  Imports: core/, ports/, adapters/

Core Domain Layer (core/)
  Knows: ports/ (Protocols only), pydantic, structlog (binding only)
  Does: business logic, domain models, state machines, validation rules
  Imports: ports/, pydantic, stdlib, domain deps

Ports and Adapters (ports/, adapters/)
  ports/: typing.Protocol definitions for I/O boundaries (structural subtyping)
  adapters/: Concrete implementations that satisfy protocols via duck typing
```

### Port Interfaces

Four primary ports covering all I/O boundaries, defined as `typing.Protocol` (structural subtyping). Adapters satisfy these implicitly — they match method signatures without inheriting from the protocol class. The type checker (`ty`) verifies conformance at dev time.

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

### Layer Import Rules

```
cli/          → core/, ports/, adapters/, rich, structlog, argparse, pydantic
core/         → ports/, pydantic, structlog (binding only), stdlib, domain deps
ports/        → typing (Protocol), stdlib type annotations only
adapters/     → ports/, stdlib, approved external libs, domain deps
tests/fakes/  → ports/, stdlib only
tests/unit/   → core/, ports/, tests/fakes/, unittest, pydantic
tests/integration/ → cli/, core/, ports/, adapters/, tests/fakes/, unittest
tests/policy/ → ast, pathlib, unittest (scans source; imports nothing from src/)
```

No code in the core domain layer may import from cli/, adapters/, rich, argparse, or any I/O module directly. If an import violates this table, the design is wrong. Restructure, don't bypass.

### Target Project Structure

```
src/gzkit/
├── cli/
│   ├── __init__.py
│   ├── main.py              # Entry point, parser, logging config
│   ├── commands/             # Existing commands/ directory
│   └── formatters.py         # OutputFormatter
├── core/
│   ├── __init__.py
│   ├── models.py             # Domain models (Pydantic)
│   ├── exceptions.py         # Exception hierarchy (retryability-oriented)
│   ├── exit_codes.py         # Exit code constants
│   ├── lifecycle.py           # ADR/OBPI state machines
│   ├── scoring.py             # Scorecard computation (from decomposition.py)
│   └── validation_rules.py   # Pure validation logic (from validate.py)
├── ports/
│   ├── __init__.py
│   └── interfaces.py         # Protocol port definitions
├── adapters/
│   ├── __init__.py
│   ├── filesystem.py         # FileStore adapter
│   ├── process.py            # ProcessRunner adapter
│   └── ledger.py             # LedgerStore adapter
├── config.py                  # Pydantic config model, precedence chain
├── ...                        # Remaining modules (migrated incrementally)
tests/
├── unit/                      # Core logic, fakes, no I/O
├── integration/               # CLI invocation, real adapters
├── policy/                    # Architectural enforcement (AST scans)
└── fakes/                     # In-memory port implementations
```

## Design Decisions

### 1. Protocol over ABC

Ports use `typing.Protocol` (structural subtyping) rather than `abc.ABC`. This is more Pythonic — adapters satisfy contracts by matching method signatures without inheriting from the protocol class. The type checker (`ty`) verifies conformance at dev time. Fakes also don't inherit; they just match the signatures. Protocol plays well with `TYPE_CHECKING` guards and allows an adapter to satisfy multiple ports without multiple inheritance.

ABC is reserved for cases requiring runtime `isinstance()` checking — adapter validation at startup, or dispatch logic that branches on adapter type. This should be rare in gzkit.

### 2. Exception Hierarchy (Retryability-Oriented)

gzkit's primary consumers are AI agents running in automation pipelines. The key runtime question is "should I retry?" not "what exit code?". Organize exceptions by retryability:

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

Exit codes are well-defined but live as module constants in `core/exit_codes.py`, not baked into exception classes. The mapping from exception to exit code happens at the CLI boundary:

```python
# core/exit_codes.py
SUCCESS = 0
GENERAL_ERROR = 1
VALIDATION_ERROR = 2
RESOURCE_NOT_FOUND = 3
GOVERNANCE_ERROR = 4
CONFIG_ERROR = 5
```

```python
# CLI boundary
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

The existing `ValidationError` dataclass in `validate.py` is renamed to `ValidationResult` to avoid collision.

### 3. Config Precedence & Injection (ENV-Optional)

gzkit values reproducibility and governance. Environment variables are invisible state — they don't appear in git diff, can't be schema-validated, and create a shadow configuration surface. Adopt the ENV-optional precedence model:

1. CLI flags (highest)
2. Config file (`.gzkit.json` — machine-managed, JSON-everywhere with Pydantic)
3. Local override file (`.gzkit.local.json` — gitignored, per-machine customization)
4. Hard-coded defaults (lowest)

No env var config layer. Enforced with a policy test that scans CLI handler code for `os.getenv()` / `os.environ.get()` calls and fails if any are found outside a narrow allowlist (`NO_COLOR`, `FORCE_COLOR`, `TERM`).

Migrate `GzkitConfig` and `PathConfig` from dataclasses to Pydantic models. Config loaded once in `main()`, passed to services via constructor. Services never call `GzkitConfig.load()` internally.

### 4. Output Formatter

Single chokepoint in `cli/formatters.py`:

```python
class OutputFormatter:
    def __init__(self, mode: OutputMode, console: Console) -> None: ...

    def emit(self, data: dict | list | str | BaseModel) -> None:
        if self.mode == OutputMode.JSON:
            if isinstance(data, BaseModel):
                print(data.model_dump_json(), file=sys.stdout)
            else:
                print(json.dumps(data), file=sys.stdout)
        elif self.mode == OutputMode.QUIET:
            return
        else:
            self._render_human(data)
```

Global flags: `--json`, `-q`/`--quiet`, `-v`/`--verbose`, `--debug`.

### 5. Structured Logging (structlog)

Add `structlog` as approved scaffold dependency. Configure once at CLI startup:

- Correlation ID per invocation (short UUID)
- Verbosity: default=WARNING, `--verbose`=INFO, `--debug`=DEBUG
- Stderr: console-rendered when interactive, JSON otherwise
- Optional `--log-file`: always JSON
- Core code calls `structlog.get_logger()` for event logging, never configures handlers

### 6. Progress Indication

`rich.progress` on stderr for operations >1 second. Suppressed in quiet and JSON modes. Degrades in non-interactive terminals.

### 7. Policy Tests

Architectural enforcement via AST scanning in `tests/policy/`. These tests scan source files — they do not import or execute application code.

- **Import boundary enforcement**: Verify core/ does not import from cli/, adapters/, rich, argparse. Verify ports/ imports only typing and stdlib.
- **ENV usage enforcement**: Scan CLI handlers for `os.getenv()` / `os.environ.get()` outside the narrow allowlist.
- **Naming conventions**: Test files mirror source structure, modules use snake_case.

Policy tests run on every CI run and every `uv run gz test` invocation.

### 8. Incremental Migration Strategy

The hexagonal skeleton is created first, but existing modules are migrated incrementally. The goal is not to rewrite everything at once but to:

1. Create the target structure (directories, port Protocols)
2. Extract the purest logic first (~400-600 LOC already identifiable)
3. Wire new code through ports from day one
4. Migrate existing code module-by-module as it's touched

Modules that are already pure (`decomposition.py`, `interview.py`, `superbook_models.py`) relocate with minimal changes. Mixed modules (`ledger.py`, `validate.py`, `sync.py`) get their pure logic extracted while the I/O code becomes adapter implementations.

### 9. Dependency Classification

The spec distinguishes **scaffold dependencies** (stdlib-first) from **domain dependencies** (justified by weight). gzkit's classification:

| Dependency | Type | Justification |
|-----------|------|---------------|
| pydantic | Scaffold | Typed config, domain models, JSON serialization |
| rich | Scaffold | Terminal output, tables, progress |
| structlog | Scaffold | Structured logging (new in this ADR) |
| behave | Domain | BDD testing framework for governance scenarios |

## Blast Radius

| Risk | Severity | Mitigation |
|------|----------|------------|
| cli.py 5,162-line refactor | High | OBPI-1 creates skeleton only (no behavior change). OBPI-2 extracts incrementally. |
| Test breakage during restructuring | Medium | Migrate tests in same OBPI as the code they test. Run full suite after each extraction. |
| Import path changes | Medium | Create compatibility re-exports in `__init__.py` during transition. Remove after all consumers updated. |
| structlog dependency in binary | Low | structlog is lightweight (~50KB). Scaffold dependency per spec. |
| Existing `GzCliError` consumers | Low | `GzKitError` is a drop-in base. `GzCliError` becomes an alias during transition. |
| Policy tests blocking CI | Low | Start with warnings, promote to failures after initial import cleanup. |

## Scope Exclusions

- **Full cli.py decomposition**: Only pure logic is extracted. The argparse tree and command handler wiring remain in the CLI layer (they belong there). Autoloaded command registration is a future scaling option, not part of this ADR.
- **Pydantic migration of all models**: Only config models migrate in this ADR. The broader dataclass→Pydantic migration is tracked in ADR-0.15.0.
- **behave**: Reclassified as domain dependency per spec v3. Not a scaffold concern.
- **Custom ArgumentParser**: Machine-parseable error format (`StableArgumentParser`) is a useful addition but not architecturally load-bearing. Future work.
- **Multiple CLI entry points**: Separate operator/developer CLIs are a scaling option. Not needed yet.

## References

- Gap analysis: conversation context (Python CLI best practices spec v3 evaluation)
- ADR-0.15.0: Pydantic schema enforcement (parallel migration)
- ADR-0.16.0: CMS architecture formalization (complementary, not overlapping)
- Project rules: `.claude/rules/pythonic.md`, `.claude/rules/models.md`
