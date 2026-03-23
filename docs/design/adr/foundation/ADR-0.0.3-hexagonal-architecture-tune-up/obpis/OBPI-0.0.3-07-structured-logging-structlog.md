---
id: OBPI-0.0.3-07-structured-logging-structlog
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 7
lane: Heavy
status: Draft
---

# OBPI-0.0.3-07-structured-logging-structlog: Structured Logging

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #7 - "OBPI-0.0.3-07: Structured Logging (structlog)"

**Status:** Draft

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

- [ ] `src/gzkit/cli/__init__.py` exists (OBPI-06 completed)

**Context:**

- [ ] Parent ADR — Structured logging specification
- [ ] structlog documentation — Processor pipeline and configuration patterns

**Existing Code:**

- [ ] Grep for `print(`, `logging.` across `src/gzkit/` to understand current logging patterns

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests verify logging configuration produces correct output format
- [ ] Tests verify correlation ID propagation
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — Logging infrastructure, no CLI command surface change

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.0.3-07-01: `src/gzkit/cli/logging.py` exists with `configure_logging()` entry point
- [ ] REQ-0.0.3-07-02: structlog added to `pyproject.toml` dependencies
- [ ] REQ-0.0.3-07-03: 4 verbosity levels configurable (quiet, normal, verbose, debug)
- [ ] REQ-0.0.3-07-04: JSON file output produces valid structured log events
- [ ] REQ-0.0.3-07-05: Console output is human-readable
- [ ] REQ-0.0.3-07-06: Correlation IDs bind at command entry
- [ ] REQ-0.0.3-07-07: Core layer code can bind context without importing CLI logging config
- [ ] REQ-0.0.3-07-08: Unit tests cover all verbosity levels and output formats

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here
```

### Gate 4 (BDD)

```text
N/A — Logging infrastructure
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

### Key Proof

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:<name>` — required (parent ADR is Heavy, Foundation series)
- Attestation: substantive attestation text required
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
