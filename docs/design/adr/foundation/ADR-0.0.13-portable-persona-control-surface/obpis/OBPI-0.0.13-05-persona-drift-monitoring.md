---
id: OBPI-0.0.13-05-persona-drift-monitoring
parent: ADR-0.0.13-portable-persona-control-surface
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.13-05-persona-drift-monitoring: Persona Drift Monitoring

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- **Checklist Item:** #5 - "Persona drift monitoring surface (observability)"

**Status:** Draft

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

- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand drift monitoring scope and non-goals
- [ ] CLI doctrine: `.claude/rules/cli.md` - new subcommand requirements

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.13-portable-persona-control-surface/ADR-0.0.13-portable-persona-control-surface.md`
- [ ] ADR Rationale > Drift Monitoring section - PSM/Assistant Axis theoretical basis
- [ ] OBPI-0.0.13-04 - persona loading must be complete

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/personas.py` exists with `list` command
- [ ] `src/gzkit/personas.py` exists with `compose_persona_frame()` and vendor adapters
- [ ] `.gzkit/personas/` has persona files with traits defined

**Existing Code (understand current state):**

- [ ] Pattern to follow: `src/gzkit/commands/personas.py` - existing personas CLI structure
- [ ] Pattern to follow: `gz validate` command pattern - similar "check and report" output style
- [ ] Test patterns: `tests/commands/test_personas_cmd.py` - existing persona CLI tests
- [ ] BDD: `features/persona.feature` - existing persona scenarios

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Command docs written: `docs/user/commands/personas.md`
- [ ] Manpage written: `docs/user/manpages/gz-personas.md`

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/persona.feature`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

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

- [ ] REQ-0.0.13-05-01: Given `gz personas drift` is invoked with no flags, when personas exist in `.gzkit/personas/`, then a human-readable table of all personas with trait adherence is printed to stdout.
- [ ] REQ-0.0.13-05-02: Given `gz personas drift --json` is invoked, when personas exist, then valid JSON is printed to stdout with persona names, trait checks, and pass/fail per trait.
- [ ] REQ-0.0.13-05-03: Given `gz personas drift --persona implementer` is invoked, when the implementer persona exists, then only that persona's drift report is shown.
- [ ] REQ-0.0.13-05-04: Given no drift is detected, when the command completes, then exit code is 0.
- [ ] REQ-0.0.13-05-05: Given drift is detected for at least one trait, when the command completes, then exit code is 3 (policy breach).
- [ ] REQ-0.0.13-05-06: Given `gz personas drift --help` is invoked, then help text includes description, usage, all options, and at least one example.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build, command docs and manpage written
- [ ] **Gate 4 (BDD):** Persona drift scenarios pass
- [ ] **Gate 5 (Human):** Human attestation recorded
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
# Paste behave output here
```

### Gate 5 (Human)

```text
# Record attestation text here
```

### Value Narrative

<!-- What problem existed before this OBPI, and what capability exists now? -->

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

### Implementation Summary

- Files created/modified:
- Tests added:
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
