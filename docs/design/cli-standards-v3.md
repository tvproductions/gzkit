# Python CLI Tool: Principles, Practices, and Guidelines (v3)

This document defines the design philosophy, architectural decisions, engineering
standards, and working directives for building a Python CLI tool. It serves as a
reference for both human developers and AI agents working on the project.

CLIs exist on a spectrum from focused utilities (one domain, a handful of commands)
to multi-domain platforms (multiple audiences, dozens of commands, pipeline
integration). This document presents the utility CLI pattern as the default and
offers scaling options for projects that outgrow the defaults.


## Design Philosophy

### stdlib-first Scaffold

The CLI scaffold — argument parsing, output formatting, and the wiring that connects
commands to core logic — follows a stdlib-first approach. This keeps the tool's
structural skeleton lightweight and portable.

The approved scaffold dependencies are:

- **pydantic** — typed configuration, domain model validation, JSON serialization
- **rich** — human-readable terminal output (tables, progress indicators, styled text)
- **structlog** — structured logging with key-value pairs, JSON output, correlation IDs

Every scaffold capability not covered above must come from the Python 3.13+ standard
library. Adding a new scaffold dependency requires explicit human approval before
proceeding.

### Domain Dependencies

Domain logic has different needs than the scaffold. A data platform needs pandas and
pyarrow the same way a web server needs an HTTP library. The stdlib-first principle
governs the scaffold, not the domain.

Domain dependencies are governed by justification, not count. Each must be load-bearing
and documented. The anti-pattern is not "many dependencies" but "unjustified
dependencies." When evaluating whether to add a domain dependency, the question is
"does this carry real weight in the domain?" not "can we reimplement it with stdlib?"

Document the rationale for each domain dependency in `pyproject.toml` comments or a
dedicated `DEPENDENCIES.md`.

### Binary vs. Wheel Distribution

Choose the distribution model based on the audience.

**PyInstaller binary** when the tool targets end users who may not have Python installed.
The tool ships as a self-contained single-file executable. This constrains design: no
dynamic plugin loading, path resolution requires `sys.frozen` detection, and every
dependency ships inside the binary.

**Wheel distribution** (`uv sync`, `pip install`) when the tool is installed into a
managed Python environment. This is simpler, avoids PyInstaller's path resolution
complexities, and supports plugin architectures. Console script entry points in
`pyproject.toml` handle the `PATH` registration.

When distributing as a PyInstaller binary:

- Use `sys.frozen` to detect binary mode.
- Resolve paths relative to `sys.executable` parent when frozen, not `__file__`.
- Do not assume the working directory is the binary's directory.
- Do not assume Python is available on the target machine.
- Config files ship next to the binary, not bundled inside it.
- Test binary builds periodically in a clean environment with no Python installed.

When distributing as a wheel:

- Define entry points in `pyproject.toml` under `[project.scripts]`.
- Resolve paths relative to `Path(__file__).parent` as normal.
- The `sys.frozen` machinery is unnecessary and should not be present.


## Architecture

### Hexagonal Architecture

The project uses hexagonal (ports and adapters) architecture with three distinct layers:

1. **CLI Adapter Layer** — The inbound adapter. Parses arguments via `argparse`, invokes
   core services, formats output. This layer knows about `argparse`, `rich`, and
   `structlog` configuration. It knows nothing about how core logic does its work.

2. **Core Domain Layer** — Business logic and domain models. This layer has zero
   knowledge of the CLI framework, output formatting, or any specific I/O
   implementation. It communicates with the outside world exclusively through ports.
   Core code may use `pydantic.BaseModel` for domain models and may bind a structlog
   logger for structured diagnostic output, but never configures logging or writes
   directly to stderr/stdout.

3. **Ports and Adapters** — Ports are `typing.Protocol` classes defining structural
   contracts for all I/O boundaries (filesystem access, network calls, external process
   invocation, etc.). Adapters satisfy these protocols implicitly through duck typing;
   they do not inherit from the protocol class. The core domain depends only on the
   port protocols, never on adapter implementations.

### Port Interfaces

All I/O boundaries are defined as `typing.Protocol` classes (structural subtyping).
This is the default and the expected pattern. Every interaction between the core domain
and the outside world passes through a port.

```python
from typing import Protocol

class FileStore(Protocol):
    """Port for filesystem operations."""

    def read(self, path: str) -> bytes:
        ...

    def write(self, path: str, content: bytes) -> None:
        ...
```

Adapters satisfy these protocols through structural conformance — they match the method
signatures without inheriting from the protocol class. The type checker (ty) verifies
conformance at dev time. This is more Pythonic than nominal inheritance and eliminates
coupling between the port definition and its implementations. Adapters do not need to
import from ports at runtime. Protocol also plays well with `TYPE_CHECKING` guards,
which matters for import cycle management in larger codebases, and allows an adapter to
satisfy multiple ports without multiple inheritance.

**When to use `abc.ABC` instead:** Use ABC only when runtime `isinstance()` checking is
required — for example, adapter validation at application startup, or dispatch logic
that branches on adapter type. This should be rare. If you find yourself reaching for
ABC, verify that the runtime check is genuinely necessary and that the same goal cannot
be achieved through the type system alone.

Adapters are injected into core services. This makes the core testable without touching
the filesystem, network, or any other external resource.

### Dependency Injection

Core services receive their port implementations via constructor injection. No service
instantiates its own adapters. The CLI adapter layer is responsible for wiring adapters
to services at application startup.

```python
class ProcessingService:
    def __init__(self, store: FileStore, config: ProcessingConfig) -> None:
        self._store = store
        self._config = config
```

### Layer Dependencies (Allowed Imports)

```
cli/          → core/, ports/, adapters/, rich, structlog, argparse, logging, json, pydantic
core/         → ports/, pydantic, structlog (binding only), stdlib, domain deps
ports/        → typing (Protocol), abc (only when runtime isinstance is needed), stdlib only
adapters/     → ports/, stdlib, approved external libs, domain deps
tests/fakes/  → ports/, stdlib only
tests/unit/   → core/, ports/, tests/fakes/, unittest, pydantic
tests/integration/ → cli/, core/, ports/, adapters/, tests/fakes/, unittest, pydantic
tests/policy/ → ast, pathlib, unittest (scans source; imports nothing from src/)
```

No code in the core domain layer may import from `cli/`, `adapters/`, `rich`,
`argparse`, or any I/O module directly. If an import violates this table, the
design is wrong. Restructure, don't bypass.


## Project Structure

```
project-root/
├── src/
│   └── projectname/
│       ├── __init__.py
│       ├── cli/
│       │   ├── __init__.py
│       │   ├── main.py           # Top-level parser, subcommand registration, logging config
│       │   ├── parser.py         # Custom ArgumentParser (if needed)
│       │   ├── commands/
│       │   │   ├── __init__.py
│       │   │   ├── group_a.py    # Subcommand group A
│       │   │   └── group_b.py    # Subcommand group B
│       │   └── formatters.py     # Output formatting (human, JSON, quiet)
│       ├── core/
│       │   ├── __init__.py
│       │   ├── services.py       # Business logic / use cases
│       │   ├── models.py         # Domain models (Pydantic BaseModel)
│       │   └── exceptions.py     # Domain exception hierarchy
│       ├── ports/
│       │   ├── __init__.py
│       │   └── interfaces.py     # Protocol port definitions
│       ├── adapters/
│       │   ├── __init__.py
│       │   ├── filesystem.py     # FileStore adapter
│       │   └── ...               # Other adapter implementations
│       └── config.py             # Configuration loading, typing, and precedence
├── tests/
│   ├── __init__.py
│   ├── unit/                     # Core logic tests (no I/O, no CLI)
│   │   ├── __init__.py
│   │   └── test_services.py
│   ├── integration/              # CLI invocation tests
│   │   ├── __init__.py
│   │   └── test_commands.py
│   ├── policy/                   # Architectural enforcement tests
│   │   ├── __init__.py
│   │   └── test_import_boundaries.py
│   └── fakes/                    # In-memory port implementations for testing
│       ├── __init__.py
│       └── fake_store.py
├── pyproject.toml
├── CLAUDE.md
└── README.md
```

### Layout Rules

- **src layout** (`src/projectname/`). The `src` directory prevents the local package
  from shadowing the installed package during test execution.
- One module per subcommand group under `cli/commands/`.
- Ports live in `ports/`, adapters in `adapters/`. They do not share modules.
- Test fakes (in-memory adapter implementations) live in `tests/fakes/` and satisfy
  the same Protocol contracts as production adapters.
- Policy tests live in `tests/policy/`. They scan source code; they do not import it.

### Scaling: Multiple CLI Entry Points

For projects with distinct operator and developer audiences, consider separate CLI entry
points rather than one CLI that serves both.

```toml
[project.scripts]
projectname = "projectname.cli.main:main"
projectname-dev = "projectname.dev.cli.main:main"
```

The operator CLI provides a stable, documented contract with explicit command
registration. The developer CLI can evolve more freely with autoloading and lighter
governance. Help text stays focused: each audience sees only their commands. The two
CLIs can have different dependency profiles if the developer CLI is a `[project.optional-dependencies]` extra.


## Command Structure

Commands use **grouped subcommands** (git-style):

```
projectname <group> <command> [options] [arguments]
```

### Explicit Registration (Default)

For stable, documented command sets, register subparsers manually:

```python
parser = argparse.ArgumentParser(prog="projectname")
subparsers = parser.add_subparsers(dest="group", required=True)

# Group
group_parser = subparsers.add_parser("group-a", help="Group A operations")
group_sub = group_parser.add_subparsers(dest="command", required=True)

# Command within group
cmd_parser = group_sub.add_parser("do-thing", help="Does the thing")
cmd_parser.set_defaults(func=handle_do_thing)
```

Every command handler function lives in the CLI adapter layer and follows the same
pattern: parse arguments, call a core service, format and emit output, handle
exceptions.

### Autoloaded Registration (Scaling Option)

For CLIs with many commands or plugin architectures, autoload command modules via
`pkgutil.iter_modules()`. Each module exposes a `register(subparsers, shared)` function.
Drop a module into `commands/` and it is live.

```python
import importlib
import pkgutil

def autoload_commands(package, subparsers, shared) -> None:
    """Discover and register command modules from a package."""
    for finder, name, ispkg in pkgutil.iter_modules(package.__path__):
        module = importlib.import_module(f"{package.__name__}.{name}")
        if hasattr(module, "register"):
            module.register(subparsers, shared)
```

This preserves the argparse contract while eliminating manual registration boilerplate.
Each autoloaded module's `register()` function follows the same pattern as explicit
registration. The discovery is automated; the registration contract is identical.

Use explicit registration for stable operator-facing commands. Use autoloading for
developer tooling that grows organically.

### Custom ArgumentParser

Override `ArgumentParser.error()` to emit a stable, machine-parseable error format.
Default argparse error formatting is implementation-defined and can change between
Python versions.

```python
class StableArgumentParser(argparse.ArgumentParser):
    def error(self, message: str) -> None:
        self.print_usage(sys.stderr)
        print(f"BLOCKERS: {self.prog}: error: {message}", file=sys.stderr)
        raise SystemExit(2)
```

A prefixed error format (`BLOCKERS:` or similar) can be consumed by CI, governance
tooling, and pipeline automation without fragile stderr parsing. The pattern is trivial
and adds no complexity.

### Adding a New Subcommand Group

1. Create `cli/commands/new_group.py`.
2. Register the group's subparser in `cli/main.py` (or via `register()` if autoloading).
3. Each command in the group gets its own handler function in the group module.
4. Each handler follows the boundary pattern documented under Error Handling.

### Adding a New Feature

Follow this order:

1. Define or extend the port Protocol in `ports/interfaces.py` if new I/O is involved.
2. Write the core service logic in `core/services.py` (or a new core module).
3. Write unit tests in `tests/unit/` using fakes from `tests/fakes/`.
4. Implement the adapter in `adapters/`.
5. Wire the command handler in `cli/commands/` — parse args, inject adapter, call
   service, format output.
6. Write integration tests in `tests/integration/`.
7. Add or update policy tests in `tests/policy/` if the feature introduces new
   architectural boundaries.
8. Run the pre-commit checklist before declaring the work done.


## Configuration

### Format Selection

Choose the config file format based on authorship, not preference.

**TOML** when the file is human-authored and tool-read. `tomllib` (stdlib 3.11+)
handles reading with zero dependencies. Comments survive because the tool never
rewrites the file. This is the right default for user preferences, feature flags,
and config files that ship next to a distributed binary.

**JSON** when the tool both creates and maintains the file. The stdlib `json` module
round-trips (read and write) with no third-party dependency — `tomllib` is read-only,
and TOML writing requires `tomli-w`. JSON is the correct choice when:

- The tool generates the file (e.g., `init` scaffolding) and updates it programmatically
- The file lives alongside other JSON artifacts (schemas, lockfiles, event logs)
- The serialization layer is Pydantic (`model_dump_json()` / `model_validate_json()`)
- Comments would be destroyed on the next machine write

**JSON-everywhere** when Pydantic is the universal model layer and all configuration is
schema-validated. This eliminates format-selection overhead entirely: one format, one
loading path, one validation pipeline. JSON round-trips natively through Pydantic
(`model_validate_json()` / `model_dump_json()`), is schema-validatable with
`jsonschema`, and is diffable in git (which matters when config changes are part of pull
requests and governance reviews). The "no comments" limitation is addressed by putting
human documentation in dedicated doc files (manpages, runbooks, README sections) rather
than in config file comments. Config and documentation are separate concerns. In a
multi-agent codebase where multiple AI agents and human developers all touch config,
one format with one validation pipeline reduces cognitive overhead.

The anti-pattern is mandating one format without considering authorship. TOML everywhere
forces a third-party write dependency for machine-managed files. JSON everywhere forces
users to hand-edit a comment-free format when comments would genuinely help. The
JSON-everywhere approach resolves this by moving documentation out of the config file
entirely.

### Precedence Chain

Configuration follows a precedence chain from highest to lowest priority. The default:

1. Command-line flags
2. Environment variables
3. Config file
4. Hard-coded defaults

**ENV-optional alternative:** For deterministic systems where reproducibility is a
governance requirement, environment variable overrides can be replaced with a local
override file (`config.local.json` or `config.local.toml`, gitignored). ENV variables
are invisible state: they do not appear in `git diff`, cannot be schema-validated, and
create a shadow configuration surface. A local override file serves the same per-machine
customization role in a typed, schema-validated, diffable format. The precedence chain
becomes:

1. Command-line flags
2. Config file (main)
3. Config file (local override, gitignored)
4. Hard-coded defaults

If you adopt the ENV-optional approach, enforce it with a policy test that scans CLI
handler code for `os.getenv()` / `os.environ.get()` calls and fails if any are found
outside a narrow allowlist (e.g., `HTTP_PROXY`, `NO_COLOR`, `TERM`, `PAGER`).

Document the chosen precedence chain explicitly, whichever model you adopt.

### Config File Location

For PyInstaller binaries, resolve the config path relative to the executable's
directory, not the temporary extraction directory:

```python
import sys
from pathlib import Path

def _binary_dir() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).parent
    else:
        return Path(__file__).resolve().parent
```

For wheel-distributed tools, `Path(__file__).resolve().parent` is sufficient. The
`sys.frozen` guard is unnecessary.

### Loading Rules

Format is a serialization detail. These rules apply regardless of format:

1. **Single load point.** Config is loaded once at the CLI boundary and injected into
   core services. Core code never opens config files, reads env vars, or parses CLI
   args.

2. **Typed immediately.** The raw file is deserialized into a typed structure (Pydantic
   model or dataclass) at load time. No raw dicts past the loading function.

3. **Config as constructor arg.** Core services receive config via constructor injection
   or a config parameter. No service resolves its own configuration.

```python
import tomllib
from pydantic import BaseModel

class AppConfig(BaseModel):
    max_retries: int = 3
    output_dir: str = "./output"
    log_level: str = "WARNING"

def load_config(cli_overrides: dict | None = None) -> AppConfig:
    config_path = _binary_dir() / "config.toml"
    file_data = {}
    if config_path.exists():
        with open(config_path, "rb") as f:
            file_data = tomllib.load(f)
    env_data = _load_from_env()  # reads relevant env vars
    merged = {**file_data, **env_data, **(cli_overrides or {})}
    return AppConfig(**merged)
```

For JSON-everywhere configs, Pydantic handles both directions:

```python
# Writing
config_path.write_text(config.model_dump_json(indent=2))

# Reading
config = AppConfig.model_validate_json(config_path.read_text())
```


## Output Modes

The tool supports five output modes, selectable via global flags:

| Flag | Mode | Behavior |
|------|------|----------|
| *(default)* | Human-readable | Styled output via `rich`. Color, tables, progress bars. |
| `--json` | Machine-parseable | Clean JSON to stdout. No decoration. No color codes. |
| `-q` / `--quiet` | Quiet | Suppresses all non-error output. Exit code only. |
| `-v` / `--verbose` | Verbose | Enables INFO-level logging to stderr. |
| `--debug` | Debug | Enables DEBUG-level logging to stderr. Full tracebacks on error. |

### Output Rules

- **Structured output goes to stdout.** This includes human-readable results and JSON.
- **Errors and diagnostics go to stderr.** Always. No exceptions.
- Human-readable mode uses `rich.console.Console` for rendering.
- JSON mode writes via Pydantic's `model_dump_json()` or `json.dumps()` to `sys.stdout`.
  No `rich` involvement.
- Quiet mode suppresses stdout entirely. Errors still go to stderr.
- Respect `NO_COLOR` environment variable. When set, disable all ANSI styling.
- Detect non-interactive terminals via `sys.stdout.isatty()` and degrade gracefully
  (no progress bars, no color in piped output).

### Output Architecture

A formatter abstraction (not a port — this lives in the CLI layer) selects rendering
strategy based on the active output mode:

```python
class OutputFormatter:
    def __init__(self, mode: OutputMode, console: Console) -> None:
        ...

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

**Never call `print()` directly for user-facing output.** Always go through the
formatter. **Never call `rich.print()` or `console.print()` outside of the formatter.**
The formatter is the single chokepoint for all user-facing output.

### Progress Indication

Any operation expected to take more than one second must show a progress indicator in
human-readable mode. Use `rich.progress` for this. Progress indicators must:

- Write to stderr (not stdout, so they don't corrupt piped output).
- Be suppressed in quiet mode and JSON mode.
- Degrade gracefully in non-interactive terminals (no progress bar, just periodic
  status lines or silence).


## Logging

Logging and user-facing output are **two separate systems** and must never be conflated.
User output flows through the `OutputFormatter` to stdout. Logging flows through
`structlog` to stderr and optionally to a log file. They never share a code path.

### Stack

The logging stack is `structlog` configured to wrap the stdlib `logging` module. This
gives structured key-value log records with JSON rendering while preserving
compatibility with any stdlib logging integrations.

### Verbosity Levels

| Flag | Effective Level | What It Enables |
|------|----------------|-----------------|
| *(default)* | WARNING | Warnings and errors only |
| `--verbose` / `-v` | INFO | Operational progress, high-level decisions |
| `--debug` | DEBUG | Full diagnostic detail, internal state |

### Log Destinations

Logs always write to **stderr**. When a `--log-file <path>` flag is provided, logs
additionally write to the specified file. The file receives JSON-formatted structured
records regardless of the stderr rendering style. This dual-output is configured once
at startup in the CLI adapter layer.

### Correlation IDs

Every top-level command invocation generates a correlation ID (a short UUID token)
that is bound to the structlog context at startup. All log records emitted during
that invocation carry the correlation ID. This allows tracing a single CLI run through
file logs, especially when the tool is invoked repeatedly by automation.

```python
import uuid
import structlog

def configure_logging(level: int, log_file: str | None = None) -> None:
    """Configure structlog + stdlib logging. Called once at CLI startup."""
    shared_processors = [
        structlog.contextvars.merge_contextvars,
        structlog.processors.add_log_level,
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_logger_name,
    ]

    structlog.configure(
        processors=[
            *shared_processors,
            structlog.stdlib.ProcessorFormatter.wrap_for_formatter,
        ],
        logger_factory=structlog.stdlib.LoggerFactory(),
        wrapper_class=structlog.stdlib.BoundLogger,
        cache_logger_on_first_use=True,
    )

    # Stderr handler: human-readable when interactive, JSON otherwise
    stderr_formatter = structlog.stdlib.ProcessorFormatter(
        processors=[
            structlog.stdlib.ProcessorFormatter.remove_processors_meta,
            structlog.dev.ConsoleRenderer()
            if sys.stderr.isatty()
            else structlog.processors.JSONRenderer(),
        ],
        foreign_pre_chain=shared_processors,
    )

    import logging

    root = logging.getLogger()
    root.setLevel(level)

    stderr_handler = logging.StreamHandler(sys.stderr)
    stderr_handler.setFormatter(stderr_formatter)
    root.addHandler(stderr_handler)

    if log_file:
        # File handler: always JSON
        file_formatter = structlog.stdlib.ProcessorFormatter(
            processors=[
                structlog.stdlib.ProcessorFormatter.remove_processors_meta,
                structlog.processors.JSONRenderer(),
            ],
            foreign_pre_chain=shared_processors,
        )
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(file_formatter)
        root.addHandler(file_handler)

    # Bind correlation ID for this invocation
    structlog.contextvars.clear_contextvars()
    structlog.contextvars.bind_contextvars(
        correlation_id=str(uuid.uuid4())[:8],
    )
```

### Using Loggers

In any module, obtain a logger via structlog and bind context as needed:

```python
import structlog

log = structlog.get_logger()

class ProcessingService:
    def process(self, path: str) -> Result:
        log.info("processing_started", path=path)
        # ...work...
        log.debug("validation_passed", record_count=len(records))
        return result
```

Key-value pairs are the primary mechanism. Use them for every log call. Bare string
messages without structured context are discouraged. Prefer
`log.info("file_loaded", path=p, size=s)` over `log.info(f"Loaded {p} ({s} bytes)")`.

### Logging Rules

1. Core domain code may call `structlog.get_logger()` and emit log records. It must
   never configure logging, add handlers, or import `logging` directly.
2. Logging configuration happens exactly once, in `cli/main.py`, before any command
   handler runs.
3. All log output goes to stderr (and optionally to a file). Never to stdout.
4. Log messages use `snake_case` event names: `file_loaded`, `validation_failed`,
   `request_sent`. Not sentences, not title case.
5. Sensitive data (credentials, tokens, PII) must never appear in log records.


## Error Handling

### Exception Hierarchy: Two Patterns

Choose the exception hierarchy based on what consumes errors.

**Exit-code-oriented (default).** When the primary consumer is a human at a terminal,
organize exceptions by what exit code they produce. Each exception carries its exit code
as a class attribute:

```python
class ProjectError(Exception):
    """Base exception for all domain errors."""
    exit_code: int = 1

class ValidationError(ProjectError):
    """Input failed validation."""
    exit_code: int = 2

class ResourceNotFoundError(ProjectError):
    """A required resource was not found."""
    exit_code: int = 3
```

**Retryability-oriented (scaling option).** When the primary consumer is pipeline
automation and the key runtime question is "should I retry?", organize exceptions by
retryability:

```python
class ProjectError(Exception):
    """Base exception for all domain errors."""

class TransientError(ProjectError):
    """Temporary failure. Retry with backoff."""

class PermanentError(ProjectError):
    """Unrecoverable. Do not retry."""

class OperatorError(ProjectError):
    """Configuration or input error. Operator must intervene."""
```

In the retryability pattern, exit codes are still well-defined but live as module
constants in a dedicated `exit_codes.py`, not baked into the exception class. The
mapping from exception to exit code happens at the CLI boundary where it belongs.
Retry logic (`retry_with_backoff()`) catches `TransientError` and retries; it
short-circuits on `PermanentError` and `OperatorError`. This separates error semantics
(should I retry?) from presentation (what number does the terminal show?).

### CLI Boundary Pattern

Every command handler wraps its core service call. The pattern is the same regardless
of which exception hierarchy you use:

```python
def handle_command(args: argparse.Namespace, formatter: OutputFormatter) -> int:
    try:
        result = service.do_work(args.input)
        formatter.emit(result)
        return 0
    except ProjectError as e:
        log.warning("command_failed", error=str(e), error_type=type(e).__name__)
        formatter.emit_error(str(e))
        return _exit_code_for(e)  # class attr or lookup, depending on pattern
    except Exception:
        log.exception("unexpected_error")
        if args.debug:
            import traceback
            traceback.print_exc(file=sys.stderr)
        formatter.emit_error("An unexpected error occurred.")
        return 1
```

### Exit Codes

- **0** — Success
- **1** — General / unexpected error
- **2** — Validation / usage error (argparse default)
- **3+** — Domain-specific (documented per exception class or in `exit_codes.py`)

Raw tracebacks never reach the user unless `--debug` is active.

### Adding a New Domain Exception

1. Define it in `core/exceptions.py`, inheriting from the appropriate base.
2. Assign an exit code (class attribute or constant in `exit_codes.py`).
3. The CLI boundary catches it automatically via the `ProjectError` base.


## Domain Models

Domain models use Pydantic `BaseModel`. This gives validated construction, type
coercion, JSON serialization (`model_dump_json()`), and JSON deserialization
(`model_validate_json()`) from a single class definition.

```python
from pydantic import BaseModel

class ProcessingResult(BaseModel):
    status: str
    records_processed: int
    errors: list[str] = []
```

### Model Rules

1. Domain models live in `core/models.py` (or a `core/models/` package if they grow).
2. Models are data containers with validation logic. Business logic belongs in services,
   not in model methods.
3. Models that cross the output boundary (returned to the formatter) must be
   JSON-serializable via `model_dump()` or `model_dump_json()`.
4. Models should use strict types where possible. Prefer `int` over `float` for counts,
   `Path` over `str` for file paths when the value is always a path.


## Policy Tests

Architectural rules written in prose documents drift. Rules written as tests are
enforced on every CI run. Policy tests are cheap to write (most are AST scans or regex
matches) and catch violations early, before code review, not during. In a multi-agent
codebase (multiple AI agents and human developers), policy tests are the most reliable
mechanism for preventing architectural drift. Prose instructions are re-read per
session; tests run every time.

Place policy tests in `tests/policy/`. They scan source code via `ast` parsing or
regex. They import nothing from `src/` — they read files, not execute code.

### What to Enforce

**Import boundary enforcement.** Verify that the layer dependency table is respected.
Parse import statements from source files with `ast` and assert that no module imports
from a forbidden layer. Allowlists are explicit and reviewed.

```python
class TestImportBoundaries(unittest.TestCase):
    def test_core_does_not_import_cli(self) -> None:
        violations = scan_imports("src/projectname/core/", forbidden=["projectname.cli"])
        self.assertEqual(violations, [], f"Core imported from CLI: {violations}")
```

**CLI contract enforcement.** Scan CLI handler code for forbidden patterns: underscore
flags, direct `os.getenv()` calls (if ENV-optional), missing help text, undocumented
exit codes.

**Config hygiene.** Validate config directory structure, schema conformance, and (for
JSON-everywhere configs) that all config files pass Pydantic validation with
`extra="forbid"`.

**Naming conventions.** Verify that test files mirror source structure, that modules use
snake_case, that no forbidden naming patterns appear.

### Policy Test Rules

1. Policy tests scan source code. They do not import or execute application code.
2. Policy tests use `ast` for structural analysis and `re` / string matching for
   pattern detection.
3. Policy tests must have clear error messages that explain what boundary was violated
   and where.
4. Allowlists for expected exceptions must be explicit and minimal.


## Testing

### Three-Layer Strategy

1. **Unit tests** (`tests/unit/`) — Test core services and domain logic directly. No
   CLI framework, no I/O. Inject fake adapters (from `tests/fakes/`) that satisfy
   the same Protocol contracts as production adapters. These tests are fast,
   deterministic, and isolated.

2. **Integration tests** (`tests/integration/`) — Test CLI commands end-to-end by
   invoking `argparse` parsing and command handlers. Verify argument parsing, output
   formatting, exit codes, and error message rendering.

3. **Policy tests** (`tests/policy/`) — Enforce architectural boundaries, import rules,
   naming conventions, and forbidden patterns as executable tests. See Policy Tests
   section above.

### Framework

- **unittest** (stdlib). No pytest, no third-party test runners.
- Use `unittest.mock` for mocking where fakes are insufficient.
- Use `tempfile.TemporaryDirectory` for filesystem-dependent tests.
- Use `unittest.TestCase.subTest()` for parameterized cases.
- Use `unittest.mock.patch.dict(os.environ, ...)` for env var tests.

### Test Fakes

Fake adapters live in `tests/fakes/` and satisfy the port Protocols with in-memory
backing stores. Because ports use structural subtyping, fakes do not need to inherit
from anything — they just need to match the method signatures:

```python
class FakeFileStore:
    """Satisfies FileStore protocol with in-memory storage."""

    def __init__(self) -> None:
        self._files: dict[str, bytes] = {}

    def read(self, path: str) -> bytes:
        if path not in self._files:
            raise FileNotFoundError(path)
        return self._files[path]

    def write(self, path: str, content: bytes) -> None:
        self._files[path] = content
```

Every production adapter should have a corresponding fake. Fakes are simple. They do
not simulate error conditions unless a test explicitly configures them to.

### Unit Test Pattern

```python
class TestProcessingService(unittest.TestCase):
    def setUp(self) -> None:
        self.store = FakeFileStore()
        self.service = ProcessingService(store=self.store)

    def test_processes_valid_input(self) -> None:
        self.store.write("input.txt", b"valid data")
        result = self.service.process("input.txt")
        self.assertEqual(result.status, "ok")
```

### Integration Test Pattern

Test CLI invocations by calling the argument parser and handler directly. Capture
stdout/stderr using `io.StringIO` and `contextlib.redirect_stdout`. Assert on exit
codes, stdout content, and stderr content.

### Logging in Tests

Use `structlog.testing.capture_logs()` to assert on log output in unit tests without
configuring real handlers:

```python
import structlog.testing

class TestProcessingService(unittest.TestCase):
    def test_logs_processing_start(self) -> None:
        with structlog.testing.capture_logs() as cap_logs:
            self.service.process("input.txt")
        self.assertTrue(
            any(l["event"] == "processing_started" for l in cap_logs)
        )
```


## Type Annotations

- **All code is fully type-annotated.** No `Any` unless genuinely unavoidable
  (document why in a comment if used).
- Type checking enforced by **ty** (Astral). ty is early-stage and its rule set is
  still evolving. When ty produces false positives on valid code, suppress with an
  inline comment explaining why, and revisit as ty matures. Do not disable ty or
  remove it from the checklist.
- Use Python 3.13+ built-in generics (`list[str]`, `dict[str, int]`) instead of
  `typing.List`, `typing.Dict`.
- Use `X | Y` union syntax instead of `typing.Union[X, Y]`.
- Use `X | None` instead of `typing.Optional[X]`.


## Linting and Formatting

- **ruff** handles both linting and formatting.
- Configuration lives in `pyproject.toml` under `[tool.ruff]`.
- Ruff is the single tool for style enforcement. No flake8, black, isort, or pylint.


## Build and Packaging

### pyproject.toml

`pyproject.toml` is the single source of truth for project metadata, dependencies,
build configuration, ruff settings, and entry points.

```toml
[project]
name = "projectname"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "pydantic",
    "rich",
    "structlog",
]

[project.scripts]
projectname = "projectname.cli.main:main"

[build-system]
requires = ["hatchling"]
build-backend = "hatchling.build"

[tool.hatch.build.targets.wheel]
packages = ["src/projectname"]

[tool.ruff]
target-version = "py313"

[tool.ruff.lint]
select = ["E", "F", "I", "N", "W", "UP", "ANN", "B", "A", "SIM"]
```

### Dependency Management

- **uv** for dependency resolution, lockfile generation, and virtual environment
  management.
- `uv lock` produces a lockfile for reproducible builds.
- `uv sync` installs from the lockfile.
- `uv run` executes commands in the managed environment.


## File Naming Conventions

- Modules: `snake_case.py`
- Classes: `PascalCase`
- Constants: `UPPER_SNAKE_CASE`
- Private functions/methods: leading `_`
- Log event names: `snake_case` (e.g., `file_loaded`, `validation_failed`)
- Test files mirror source: `src/.../services.py` → `tests/unit/test_services.py`


## Pre-Commit Checklist

Before declaring any task complete, run:

```bash
uv run ruff check src/ tests/
uv run ruff format --check src/ tests/
uv run ty check src/
uv run python -m unittest discover -s tests
```

All four must pass with zero errors and zero warnings. The test discovery includes
policy tests, which enforce architectural boundaries automatically.


## Toolchain Summary

| Concern | Tool |
|---------|------|
| Python version | 3.13+ |
| Argument parsing | `argparse` (stdlib) |
| Configuration (read) | `tomllib` (stdlib) for TOML, `json` (stdlib) for JSON |
| Configuration (typed) | `pydantic` |
| Domain models | `pydantic` |
| Logging | `structlog` wrapping stdlib `logging` |
| Testing | `unittest` (stdlib) |
| Type checking | `ty` (Astral) |
| Linting / formatting | `ruff` (Astral) |
| Package management | `uv` (Astral) |
| Human output | `rich` |
| Binary packaging | PyInstaller (if distributing binary) |


## Spectrum Summary

| Dimension | Utility CLI (default) | Platform CLI (scaling option) |
|---|---|---|
| Scope | One domain, 5-10 commands | Multiple domains, 60+ commands |
| Dependencies | stdlib-first everywhere | stdlib-first scaffold, domain deps justified |
| Config format | TOML (human) + JSON (machine) | JSON-everywhere with schema validation |
| Config precedence | CLI > ENV > file > defaults | CLI > file > local override > defaults |
| Distribution | PyInstaller binary | Wheel with console scripts |
| Registration | Manual subparser wiring | Manual for stable, autoloading for dev tooling |
| Error hierarchy | Exit-code-oriented | Retryability-oriented for pipelines |
| Architecture enforcement | Prose + code review | Policy tests (AST + regex scans) |
| Audience | Single CLI | Separate operator + developer CLIs |
| Port definitions | `typing.Protocol` | `typing.Protocol` |
| Error format | Default argparse | Custom parser for machine-parseable errors |
