---
id: OBPI-0.0.3-07-structured-logging-structlog
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 7
lane: Heavy
status: in_progress
---

# OBPI-0.0.3-07-structured-logging-structlog: Structured Logging

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #7 - "OBPI-0.0.3-07: Structured Logging (structlog)"

**Status:** Completed

## Objective

Integrate structlog for structured logging with correlation IDs, verbosity levels tied to CLI flags, JSON file output for machine consumption, and human-readable console output — with configuration in the CLI layer and binding-only usage in core.

## Lane

**Heavy** — Adds a new dependency (structlog) and establishes cross-layer logging contract.

## Allowed Paths

- `src/gzkit/cli/logging.py` — structlog configuration (processors, formatters, levels)
- `src/gzkit/cli/__init__.py` — Update to export logging setup
- `pyproject.toml` — Add structlog dependency
- `tests/test_logging.py` — Unit tests for logging configuration
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-07-structured-logging-structlog.md` — This brief

## Denied Paths

- `src/gzkit/core/**` — Core uses structlog binding only; config is CLI layer
- `src/gzkit/commands/**` — Retrofitting commands with structlog is incremental
- `src/gzkit/cli.py` — CLI entry point wiring is incremental
- `src/gzkit/ports/` — Port definitions are OBPI-01
- `docs/design/**` — ADR changes out of scope
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: structlog is configured in the CLI layer (`src/gzkit/cli/logging.py`) — never in core
2. REQUIREMENT: Core layer uses structlog binding only: `structlog.get_logger()`, `.bind()`, `.msg()`
3. REQUIREMENT: Logging configuration supports 4 verbosity levels tied to CLI flags: quiet, normal, verbose, debug
4. REQUIREMENT: JSON file output writes structured log events for machine parsing
5. REQUIREMENT: Console output uses human-readable rendering for interactive use
6. REQUIREMENT: Correlation IDs are bound at request/command entry and propagated through the call stack
7. REQUIREMENT: `configure_logging(verbosity, log_file)` is the single configuration entry point
8. NEVER: Configure structlog processors or formatters in `core/` — core binds context only
9. NEVER: Use stdlib `logging` directly — all logging goes through structlog
10. ALWAYS: Log output respects `--quiet` flag (errors only) and `--json` flag (JSON format)

> STOP-on-BLOCKERS: if `src/gzkit/cli/__init__.py` does not exist (OBPI-06), halt.

## Discovery Checklist

**Prerequisites (STOP if missing):**

- [x] `src/gzkit/cli/__init__.py` exists (OBPI-06 completed)

**Context:**

- [x] Parent ADR — Structured logging specification
- [x] structlog documentation — Processor pipeline and configuration patterns

**Existing Code:**

- [x] Grep for `print(`, `logging.` across `src/gzkit/` to understand current logging patterns

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests verify logging configuration produces correct output format
- [x] Tests verify correlation ID propagation
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [x] N/A — Logging infrastructure, no CLI command surface change

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "from gzkit.cli.logging import configure_logging; configure_logging('normal'); import structlog; log = structlog.get_logger(); print('Logging configured')"
uv run -m unittest tests.test_logging -v
```

## Acceptance Criteria

- [x] REQ-0.0.3-07-01: `src/gzkit/cli/logging.py` exists with `configure_logging()` entry point
- [x] REQ-0.0.3-07-02: [doc] structlog added to `pyproject.toml` dependencies
- [x] REQ-0.0.3-07-03: 4 verbosity levels configurable (quiet, normal, verbose, debug)
- [x] REQ-0.0.3-07-04: JSON file output produces valid structured log events
- [x] REQ-0.0.3-07-05: Console output is human-readable
- [x] REQ-0.0.3-07-06: Correlation IDs bind at command entry
- [x] REQ-0.0.3-07-07: Core layer code can bind context without importing CLI logging config
- [x] REQ-0.0.3-07-08: Unit tests cover all verbosity levels and output formats

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded in this brief

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.test_logging -v
Ran 23 tests in 0.007s — OK
23 tests across 8 classes: ConfigureLogging(3), VerbosityLevels(7), JsonFileOutput(3), ConsoleOutput(2), CorrelationId(4), CoreLayerBinding(2), ExportFromCliPackage(2)
Coverage: 98% on src/gzkit/cli/logging.py
```

### Code Quality

```text
$ uv run gz lint — All checks passed
$ uv run gz typecheck — All checks passed
```

### Gate 3 (Docs)

```text
$ uv run mkdocs build --strict — Documentation built in 0.96 seconds
```

### Gate 4 (BDD)

```text
N/A — Logging infrastructure
```

### Gate 5 (Human)

```text
Attestor: human:jeff
Attestation: "attest completed"
Date: 2026-03-24
```

### Value Narrative

Before this OBPI, gzkit had no structured logging — diagnostic output used ad-hoc print() and console.print() with no correlation tracking, no machine-parseable file output, and no verbosity control. Now, structlog provides structured logging with correlation IDs, 4 verbosity levels tied to CLI flags, JSON file output for machine consumption, and human-readable console rendering — all configured in the CLI adapter layer while core code uses binding-only.

### Key Proof

```bash
$ uv run python -c "
from gzkit.cli.logging import configure_logging, bind_correlation_id
import structlog, tempfile, json
from pathlib import Path
cid = bind_correlation_id('demo-req-42')
with tempfile.TemporaryDirectory() as tmp:
    log_file = Path(tmp) / 'app.log'
    configure_logging('normal', log_file=log_file)
    log = structlog.get_logger()
    log.info('processing request', user='jeff', action='deploy')
    import logging
    for h in logging.getLogger().handlers: h.flush()
    entry = json.loads(log_file.read_text().strip())
    print(f'correlation_id: {entry[\"correlation_id\"]}')
    print(f'event: {entry[\"event\"]}')
"
correlation_id: demo-req-42
event: processing request
```

### Implementation Summary

- Files created: src/gzkit/cli/logging.py, tests/test_logging.py
- Files modified: src/gzkit/cli/__init__.py (added exports), pyproject.toml (added structlog>=24.0)
- Tests added: tests/test_logging.py (23 tests across 8 classes)
- Date completed: 2026-03-24
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: human:jeff
- Attestation: attest completed
- Date: 2026-03-24

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
