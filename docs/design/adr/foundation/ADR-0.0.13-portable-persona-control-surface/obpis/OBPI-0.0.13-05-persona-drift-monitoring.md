---
id: OBPI-0.0.13-05-persona-drift-monitoring
parent: ADR-0.0.13-portable-persona-control-surface
item: 5
lane: Heavy
status: Completed
---

# OBPI-0.0.13-05-persona-drift-monitoring: Persona Drift Monitoring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #5 - "Persona drift monitoring surface (observability)"

**Status:** Completed

## Objective

Create the `gz personas drift` CLI command that reports persona adherence
metrics using behavioral proxies (output pattern matching against trait
specifications), closing the feedback loop between persona design and observed
agent behavior.

## Lane

**Heavy** - Adds a new CLI subcommand (`gz personas drift`) with defined output
format, exit codes, and operator-facing behavior. New subcommands are Heavy per
CLI doctrine.

## Allowed Paths

- `src/gzkit/commands/personas.py` - Add `drift` subcommand alongside existing `list`
- `src/gzkit/personas.py` - Add drift detection logic (behavioral proxy matching)
- `src/gzkit/models/persona.py` - Add drift result model if needed
- `src/gzkit/cli/parser_governance.py` - Wire `personas drift` into CLI parser
- `tests/test_persona_drift.py` - Drift detection unit tests
- `tests/commands/test_personas_cmd.py` - CLI integration tests
- `features/persona.feature` - BDD scenarios for drift command
- `docs/user/commands/personas.md` - Command documentation
- `docs/user/manpages/gz-personas.md` - Manpage for personas commands

## Denied Paths

- `src/gzkit/sync_surfaces.py` - Sync is OBPI-03
- `src/gzkit/schemas/` - Schema is OBPI-01
- `.gzkit/personas/` - Canon files are read-only
- `src/gzkit/commands/init_cmd.py` - Init is OBPI-02

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz personas drift` MUST accept an optional `--persona <name>` flag to check a single persona, defaulting to all personas.
2. REQUIREMENT: Command MUST support `--json` for machine-readable output and default human-readable table output.
3. REQUIREMENT: Drift detection MUST use behavioral proxies only — output pattern matching against trait specifications, not model-internal measurements.
4. ALWAYS: Exit code 0 when all checked personas show no drift; exit code 3 (policy breach) when drift is detected.
5. ALWAYS: Human-readable output MUST include persona name, each trait checked, and pass/fail per trait.
6. NEVER: Drift detection MUST NOT require network access or external API calls — it operates on local log/output artifacts.
7. NEVER: Do not claim activation-space measurement — the ADR explicitly excludes this as a non-goal.
8. ALWAYS: Help text MUST include at least one usage example and document exit codes per CLI doctrine.

> STOP-on-BLOCKERS: if OBPI-0.0.13-04 (vendor loading) is not complete, print a BLOCKERS list and halt. Drift detection needs loaded persona definitions to compare against.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [x] Parent ADR - understand drift monitoring scope and non-goals
- [x] CLI doctrine: `.claude/rules/cli.md` - new subcommand requirements

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [x] ADR Rationale > Drift Monitoring section - PSM/Assistant Axis theoretical basis
- [x] OBPI-0.0.13-04 - persona loading must be complete

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/commands/personas.py` exists with `list` command
- [x] `src/gzkit/personas.py` exists with `compose_persona_frame()` and vendor adapters
- [x] `.gzkit/personas/` has persona files with traits defined

**Existing Code (understand current state):**

- [x] Pattern to follow: `src/gzkit/commands/personas.py` - existing personas CLI structure
- [x] Pattern to follow: `gz validate` command pattern - similar "check and report" output style
- [x] Test patterns: `tests/commands/test_personas_cmd.py` - existing persona CLI tests
- [x] BDD: `features/persona.feature` - existing persona scenarios

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Command docs written: `docs/user/commands/personas-drift.md`
- [x] Manpage written: `docs/user/manpages/gz-personas.md`

### Gate 4: BDD (Heavy only)

- [x] Acceptance scenarios pass: `uv run -m behave features/persona.feature`

### Gate 5: Human (Heavy only)

- [x] Human attestation recorded

## Verification

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
uv run gz personas drift --help
uv run gz personas drift
uv run gz personas drift --persona implementer
uv run gz personas drift --json
echo $?
```

## Acceptance Criteria

- [x] REQ-0.0.13-05-01: Given `gz personas drift` is invoked with no flags, when personas exist in `.gzkit/personas/`, then a human-readable table of all personas with trait adherence is printed to stdout.
- [x] REQ-0.0.13-05-02: Given `gz personas drift --json` is invoked, when personas exist, then valid JSON is printed to stdout with persona names, trait checks, and pass/fail per trait.
- [x] REQ-0.0.13-05-03: Given `gz personas drift --persona implementer` is invoked, when the implementer persona exists, then only that persona's drift report is shown.
- [x] REQ-0.0.13-05-04: Given no drift is detected, when the command completes, then exit code is 0.
- [x] REQ-0.0.13-05-05: Given drift is detected for at least one trait, when the command completes, then exit code is 3 (policy breach).
- [x] REQ-0.0.13-05-06: Given `gz personas drift --help` is invoked, then help text includes description, usage, all options, and at least one example.

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Gate 3 (Docs):** Docs build, command docs and manpage written
- [x] **Gate 4 (BDD):** Persona drift scenarios pass
- [x] **Gate 5 (Human):** Human attestation recorded
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
Ran 2513 tests in 36.425s
OK
```

### Code Quality

```text
Lint passed.
Type check passed.
```

### Gate 3 (Docs)

```text
INFO - Documentation built in 1.18 seconds
```

### Gate 4 (BDD)

```text
1 feature passed, 0 failed, 0 skipped
9 scenarios passed, 0 failed, 0 skipped
44 steps passed, 0 failed, 0 skipped
```

### Gate 5 (Human)

```text
Attestor: Jeffry
Attestation: attest completed
Date: 2026-04-05
```

### Value Narrative

Before this OBPI, persona identity frames existed as static definitions with no way
to verify whether agents actually behaved according to their trait specifications.
The `gz personas drift` command closes this feedback loop by scanning local governance
artifacts (ledger events, OBPI audit logs) for behavioral evidence and reporting
per-trait adherence, detecting when observed behavior drifts from persona specifications.

### Key Proof

```bash
$ uv run gz personas drift --persona implementer --json
{
  "personas": [{"persona": "implementer", "checks": [...], "has_drift": false}],
  "total_personas": 1, "total_checks": 12, "drift_count": 0,
  "scan_timestamp": "2026-04-05T15:53:11.946647+00:00"
}
# Exit code: 0 (no drift)

$ uv run gz personas drift
# 6 personas, 55 checks, 3 drift findings
# Exit code: 3 (policy breach)
```

### Implementation Summary

- Files created: tests/test_persona_drift.py, docs/user/commands/personas-drift.md, docs/user/manpages/gz-personas.md
- Files modified: src/gzkit/models/persona.py, src/gzkit/personas.py, src/gzkit/commands/personas.py, src/gzkit/cli/parser_governance.py, tests/commands/test_personas_cmd.py, features/persona.feature, features/steps/persona_steps.py, config/doc-coverage.json, docs/user/commands/index.md
- Tests added: 24 unit tests (test_persona_drift.py), 6 CLI tests (test_personas_cmd.py), 3 BDD scenarios
- Date completed: 2026-04-05
- Attestation status: Human attested completed
- Defects noted: Pipeline improvement tracked in agent-insights.jsonl (Stage 4 should auto-detect new CLI surfaces for evidence)

## Tracked Defects

- Pipeline improvement: Stage 4 ceremony should detect new CLI surfaces and include live execution in evidence table (tracked in `.gzkit/insights/agent-insights.jsonl`)

## Human Attestation

- Attestor: Jeffry
- Attestation: attest completed
- Date: 2026-04-05

---

**Brief Status:** Completed

**Date Completed:** 2026-04-05

**Evidence Hash:** -
