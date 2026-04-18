---
id: OBPI-0.0.3-08-progress-indication
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 8
lane: Heavy
status: attested_completed
---

# OBPI-0.0.3-08-progress-indication: Progress Indication

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #8 - "OBPI-0.0.3-08: Progress Indication"

**Status:** Completed

## Objective

Create progress indication utilities in the CLI adapter layer (`src/gzkit/cli/progress.py`) supporting spinner/progress bar display via Rich, with automatic suppression in quiet and json output modes.

## Lane

**Heavy** — Introduces CLI-visible progress display contract integrated with OutputFormatter modes.

## Allowed Paths

- `src/gzkit/cli/progress.py` — Progress context managers and helpers
- `src/gzkit/cli/__init__.py` — Update to export progress utilities
- `tests/test_progress.py` — Unit tests for progress indication
- `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/obpis/OBPI-0.0.3-08-progress-indication.md` — This brief

## Denied Paths

- `src/gzkit/core/` — Core must not know about progress display (presentation concern)
- `src/gzkit/commands/**` — Wiring progress into commands is incremental
- `src/gzkit/cli.py` — CLI entry point wiring is incremental
- `src/gzkit/ports/` — Port definitions are OBPI-01
- `docs/design/**` — ADR changes out of scope
- New dependencies (Rich is already available)
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: Progress utilities live exclusively in `src/gzkit/cli/progress.py` — CLI adapter layer
2. REQUIREMENT: Progress display uses Rich spinners/progress bars for human-mode output
3. REQUIREMENT: Progress is automatically suppressed when OutputFormatter mode is `quiet` or `json`
4. REQUIREMENT: Progress context manager pattern: `with progress_phase("Linting...", formatter):`
5. REQUIREMENT: Phase-based progress supports step counting (e.g., "[1/3] Linting...")
6. REQUIREMENT: Progress integrates with OutputFormatter — reads mode from formatter instance
7. NEVER: Import progress utilities in `core/` or `ports/` — presentation concern only
8. NEVER: Display progress output on stdout in `json` mode — would corrupt JSON stream
9. ALWAYS: Progress output goes to stderr (keeps stdout clean for data)
10. ALWAYS: Context manager cleanup ensures spinner/bar is removed on exception

> STOP-on-BLOCKERS: if `src/gzkit/cli/formatters.py` does not exist (OBPI-06), halt.

## Discovery Checklist

**Prerequisites (STOP if missing):**

- [ ] `src/gzkit/cli/__init__.py` exists (OBPI-06 completed)
- [ ] `src/gzkit/cli/formatters.py` exists with OutputFormatter (OBPI-06 completed)

**Context:**

- [ ] Parent ADR — Progress indication specification
- [ ] Rich documentation — Progress, Spinner, Status APIs

**Existing Code:**

- [ ] `src/gzkit/cli/formatters.py` — OutputFormatter modes to integrate with

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests verify progress displays in human mode
- [x] Tests verify progress suppression in quiet/json modes
- [x] Tests pass: `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [x] N/A — Progress is internal infrastructure

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification
python -c "from gzkit.cli.progress import progress_phase; print('Progress utilities importable')"
uv run -m unittest tests.test_progress -v
```

## Acceptance Criteria

- [x] REQ-0.0.3-08-01: `src/gzkit/cli/progress.py` exists with progress context manager
- [x] REQ-0.0.3-08-02: Progress displays Rich spinner/bar in human mode
- [x] REQ-0.0.3-08-03: Progress suppressed in quiet mode
- [x] REQ-0.0.3-08-04: Progress suppressed in json mode
- [x] REQ-0.0.3-08-05: Phase-based step counting works (e.g., "[1/3]")
- [x] REQ-0.0.3-08-06: Progress output goes to stderr
- [x] REQ-0.0.3-08-07: Context manager cleans up on exception
- [x] REQ-0.0.3-08-08: Unit tests cover mode-dependent display/suppression

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

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 19 tests in 0.005s — OK
```

### Code Quality

```text
uv run gz lint — All checks passed!
uv run gz typecheck — All checks passed!
```

### Gate 3 (Docs)

```text
uv run mkdocs build --strict — Documentation built in 0.97 seconds
```

### Gate 4 (BDD)

```text
N/A — Progress infrastructure
```

### Gate 5 (Human)

```text
attest completed — 2026-03-24
```

### Value Narrative

Before this OBPI, gzkit CLI commands had no progress indication — long-running operations ran silently. Now, `progress_phase`, `progress_spinner`, and `progress_bar` context managers provide Rich-powered visual feedback on stderr, with automatic suppression in quiet/json modes.

### Key Proof

```bash
$ uv run -m unittest tests.test_progress -v
test_importable_from_cli_package ... ok
test_all_display_modes ... ok
test_all_suppressed_modes ... ok
test_bar_cleanup_on_exception ... ok
test_bar_runs_in_human_mode ... ok
test_bar_suppressed_in_json_mode ... ok
test_bar_suppressed_in_quiet_mode ... ok
test_phase_cleanup_on_exception ... ok
test_phase_debug_mode_shows_progress ... ok
test_phase_runs_in_human_mode ... ok
test_phase_suppressed_in_json_mode ... ok
test_phase_suppressed_in_quiet_mode ... ok
test_phase_verbose_mode_shows_progress ... ok
test_phase_with_step_counting ... ok
test_phase_without_step_counting ... ok
test_spinner_cleanup_on_exception ... ok
test_spinner_runs_in_human_mode ... ok
test_spinner_suppressed_in_json_mode ... ok
test_spinner_suppressed_in_quiet_mode ... ok
Ran 19 tests in 0.005s — OK
```

### Implementation Summary

- Files created: `src/gzkit/cli/progress.py`, `tests/test_progress.py`
- Files modified: `src/gzkit/cli/__init__.py`
- Tests added: 19 (test_progress.py)
- Date completed: 2026-03-24
- Attestation status: Human attested
- Defects noted: None

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `human:jeff` — required (parent ADR is Heavy, Foundation series)
- Attestation: attest completed
- Date: 2026-03-24

---

**Brief Status:** Completed

**Date Completed:** 2026-03-24

**Evidence Hash:** -
