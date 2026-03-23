---
id: OBPI-0.0.3-08-progress-indication
parent: ADR-0.0.3-hexagonal-architecture-tune-up
item: 8
lane: Heavy
status: Draft
---

# OBPI-0.0.3-08-progress-indication: Progress Indication

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.3-hexagonal-architecture-tune-up/ADR-0.0.3-hexagonal-architecture-tune-up.md`
- **Checklist Item:** #8 - "OBPI-0.0.3-08: Progress Indication"

**Status:** Draft

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

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests verify progress displays in human mode
- [ ] Tests verify progress suppression in quiet/json modes
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`

### Gate 4: BDD (Heavy only)

- [ ] N/A — Progress is internal infrastructure

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.0.3-08-01: `src/gzkit/cli/progress.py` exists with progress context manager
- [ ] REQ-0.0.3-08-02: Progress displays Rich spinner/bar in human mode
- [ ] REQ-0.0.3-08-03: Progress suppressed in quiet mode
- [ ] REQ-0.0.3-08-04: Progress suppressed in json mode
- [ ] REQ-0.0.3-08-05: Phase-based step counting works (e.g., "[1/3]")
- [ ] REQ-0.0.3-08-06: Progress output goes to stderr
- [ ] REQ-0.0.3-08-07: Context manager cleans up on exception
- [ ] REQ-0.0.3-08-08: Unit tests cover mode-dependent display/suppression

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
N/A — Progress infrastructure
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
