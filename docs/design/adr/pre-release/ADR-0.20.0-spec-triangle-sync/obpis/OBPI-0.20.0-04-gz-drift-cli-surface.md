---
id: OBPI-0.20.0-04-gz-drift-cli-surface
parent: ADR-0.20.0-spec-triangle-sync
item: 4
lane: Heavy
status: Accepted
---

# OBPI-0.20.0-04: gz drift CLI Surface

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.20.0-spec-triangle-sync/ADR-0.20.0-spec-triangle-sync.md`
- **Checklist Item:** #4 — "`gz drift` CLI surface with human/JSON/plain output modes and repository signal scanning"

**Status:** Accepted

## Objective

Expose the drift detection engine via a `gz drift` CLI command that scans the
repository's OBPI briefs, existing `@covers` references in test files, and the
active repository change set, computes drift, and presents results in
human-readable (default), `--json`, and `--plain` output modes.

## Lane

**Heavy** — New CLI command (external contract change). Requires docs, BDD, and human attestation.

## Allowed Paths

- `src/gzkit/commands/drift.py` — drift CLI command implementation
- `src/gzkit/cli.py` — register drift subcommand
- `tests/test_triangle.py` — CLI smoke tests (extend existing)
- `docs/user/commands/drift.md` — command documentation
- `features/triangle_drift.feature` — BDD acceptance scenarios
- `features/steps/triangle_drift_steps.py` — BDD step implementations

## Denied Paths

- `src/gzkit/triangle.py` — data model belongs to OBPIs 01-03 (read-only consumer)
- `src/gzkit/commands/check.py` — gate integration belongs to OBPI-05
- CI files, lockfiles, new dependencies

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz drift` MUST scan all OBPI briefs under `docs/design/adr/` and extract REQ entities.
1. REQUIREMENT: `gz drift` MUST scan test files for existing `@covers` decorator references to build test linkage. This ADR consumes existing references only; enforcement remains ADR-0.21.0 scope.
1. REQUIREMENT: `gz drift` MUST inspect the active repository change set (or an explicitly supplied diff window) to build changed code vertices for unjustified-code-change detection.
1. REQUIREMENT: Default output MUST be human-readable tables showing unlinked specs, orphan tests, and unjustified code changes.
1. REQUIREMENT: `--json` MUST output valid JSON DriftReport to stdout; logs to stderr.
1. REQUIREMENT: `--plain` MUST output one record per line (grep-friendly).
1. REQUIREMENT: Exit code 0 when no drift detected; exit code 1 when any drift category exists.
1. REQUIREMENT: `-h`/`--help` MUST include description, usage, options, and at least one example.
1. NEVER: Use LLM inference in the CLI path.
1. ALWAYS: Lines in help text <= 80 chars.

> STOP-on-BLOCKERS: OBPIs 01-03 must be complete (data model, extraction, and detection engine).

## Quality Gates (Heavy)

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief

### Gate 2: TDD

- [ ] Unit tests for CLI invocation and output modes
- [ ] Tests pass: `uv run gz test`

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs

- [ ] `docs/user/commands/drift.md` created with examples
- [ ] `uv run mkdocs build --strict` passes

### Gate 4: BDD

- [ ] `features/triangle_drift.feature` with acceptance scenarios
- [ ] `uv run -m behave features/triangle_drift.feature` passes

### Gate 5: Human

- [ ] Human attestation recorded

## Acceptance Criteria

- [ ] REQ-0.20.0-04-01: Given a repository with drift, when `gz drift` is run, then human-readable output shows unlinked specs, orphan tests, and unjustified code changes in tables.
- [ ] REQ-0.20.0-04-02: Given a repository with drift, when `gz drift --json` is run, then valid JSON DriftReport is written to stdout.
- [ ] REQ-0.20.0-04-03: Given a repository with no drift, when `gz drift` is run, then exit code is 0 and output confirms no drift.
- [ ] REQ-0.20.0-04-04: Given a repository with drift in any category, when `gz drift` is run, then exit code is 1.
- [ ] REQ-0.20.0-04-05: Given changed source files without any matching governance justification in the inspected window, when `gz drift` is run, then unjustified code changes are reported.
- [ ] REQ-0.20.0-04-06: Given `gz drift --help`, then output includes description, usage, options, and example.

## Completion Checklist (Heavy)

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Gate 3 (Docs):** Docs build, command docs created
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Gate 5 (Human):** Human attestation recorded
- [ ] **Code Quality:** Lint, format, type checks clean

## Evidence

### Gate 2 (TDD)

```text
# Paste test output here
```

### Gate 3 (Docs)

```text
# Paste mkdocs build output here
```

### Gate 4 (BDD)

```text
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation here
```

## Human Attestation

- Attestor: `human:<name>`
- Attestation:
- Date:

---

**Brief Status:** Accepted

**Date Completed:** -

**Evidence Hash:** -
