---
id: OBPI-0.0.45-01-cli-mode-density-doctrine
parent: ADR-0.0.45-cli-mode-density-doctrine
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.45-01-cli-mode-density-doctrine: Cli Mode Density Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`
- **Checklist Item:** #1 - "OBPI-0.0.45-01: **registry-and-models** — Define `data/cli_flag_density_*.json`, `data/suite_density_*.json`, `data/validate_suites.json`, `data/validate_audits.json`, and Pydantic models at `src/gzkit/governance/trust_audits/cli_density_models.py` per `.claude/rules/models.md`."

**Status:** Draft

## Objective

**registry-and-models** — Define `data/cli_flag_density_*.json`, `data/suite_density_*.json`, `data/validate_suites.json`, `data/validate_audits.json`, and Pydantic models at `src/gzkit/governance/trust_audits/cli_density_models.py` per `.claude/rules/models.md`.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md` — parent ADR for intent and scope (read-only)
- `.gzkit/rules/models.md` — canonical models rule (read-only; binding constraint for Pydantic shape)
- `src/gzkit/governance/trust_audits/cli_density_models.py` — net-new Pydantic models created by this OBPI
- `data/cli_flag_density_thresholds.json` — net-new threshold registry created by this OBPI
- `data/cli_flag_density_floor.json` — net-new floor registry created by this OBPI
- `data/cli_flag_density_waivers.json` — net-new waiver registry created by this OBPI
- `data/suite_density_thresholds.json` — net-new threshold registry created by this OBPI
- `data/suite_density_floor.json` — net-new floor registry created by this OBPI
- `data/suite_density_waivers.json` — net-new waiver registry created by this OBPI
- `data/validate_suites.json` — net-new suite registry created by this OBPI
- `data/validate_audits.json` — net-new audit registry created by this OBPI
- `tests/governance/test_cli_density_models.py` — net-new unit tests created by this OBPI

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## OBPI creates these files

- `src/gzkit/governance/trust_audits/cli_density_models.py`
- `data/cli_flag_density_thresholds.json`
- `data/cli_flag_density_floor.json`
- `data/cli_flag_density_waivers.json`
- `data/suite_density_thresholds.json`
- `data/suite_density_floor.json`
- `data/suite_density_waivers.json`
- `data/validate_suites.json`
- `data/validate_audits.json`
- `tests/governance/test_cli_density_models.py`

## Requirements (FAIL-CLOSED)

1. REQ-0.0.45-01-01: Pydantic models for the two density surfaces live at `src/gzkit/governance/trust_audits/cli_density_models.py`, each model uses `BaseModel` with `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`, and the module exports `CliFlagDensityThresholds`, `CliFlagDensityWaiver`, `SuiteDensityThresholds`, `SuiteDensityWaiver`, `ValidateSuite`, `ValidateAudit`.
1. REQ-0.0.45-01-02: `data/cli_flag_density_thresholds.json`, `data/cli_flag_density_floor.json`, and `data/cli_flag_density_waivers.json` exist with documented band values (Green ≤7, Yellow 8–12, Red >12) and parse cleanly against `CliFlagDensityThresholds` / `CliFlagDensityWaiver` models.
1. REQ-0.0.45-01-03: `data/suite_density_thresholds.json`, `data/suite_density_floor.json`, and `data/suite_density_waivers.json` exist with documented band values (Green ≤6, Yellow 7–10, Red >10) and parse cleanly against `SuiteDensityThresholds` / `SuiteDensityWaiver` models.
1. REQ-0.0.45-01-04: `data/validate_suites.json` enumerates the canonical suites (`default`, `surface-fidelity`, `cheap-fidelity`) as suite-name → list-of-audit-names entries and parses cleanly against `ValidateSuite`.
1. REQ-0.0.45-01-05: `data/validate_audits.json` enumerates every registered audit name with scope metadata (description, registered validator function path) and parses cleanly against `ValidateAudit`.
1. REQ-0.0.45-01-06: Every waiver entry requires a non-empty `next_action` field; single-token reasons (`'TODO'`, `'TBD'`, `'pending'`) fail-closed at model validation time.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `data/cli_flag_density_*.json`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Test patterns: `tests/governance/test_cli_density_validators.py`
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md
test -f data/validate_suites.json
test -f data/validate_audits.json
test -f src/gzkit/governance/trust_audits/cli_density_models.py
test -f .claude/rules/models.md
test -f src/gzkit/cli/parser_validate.py
test -f src/gzkit/governance/trust_audits/cli_flag_density.py
test -f src/gzkit/governance/trust_audits/suite_density.py
uv run -m unittest tests/governance/test_cli_density_validators.py -v
uv run -m unittest tests/governance/test_cli_density_models.py -v
uv run -m unittest tests/cli/test_validate_suite_audit.py -v
uv run -m behave features/cli_mode_density.feature
test -f features/steps/cli_mode_density_steps.py
```

## Demo

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

- [ ] REQ-0.0.45-01-01: Given the cli_density_models module, when imported, then it exports six frozen `extra="forbid"` Pydantic models (`CliFlagDensityThresholds`, `CliFlagDensityWaiver`, `SuiteDensityThresholds`, `SuiteDensityWaiver`, `ValidateSuite`, `ValidateAudit`).
- [ ] REQ-0.0.45-01-02: Given `data/cli_flag_density_*.json`, when parsed, then they validate against `CliFlagDensityThresholds` / `CliFlagDensityWaiver` and the bands resolve to Green ≤7, Yellow 8–12, Red >12.
- [ ] REQ-0.0.45-01-03: Given `data/suite_density_*.json`, when parsed, then they validate against `SuiteDensityThresholds` / `SuiteDensityWaiver` and the bands resolve to Green ≤6, Yellow 7–10, Red >10.
- [ ] REQ-0.0.45-01-04: Given `data/validate_suites.json`, when parsed, then it enumerates `default`, `surface-fidelity`, `cheap-fidelity` as suite-name → audit-name lists and validates against `ValidateSuite`.
- [ ] REQ-0.0.45-01-05: Given `data/validate_audits.json`, when parsed, then every registered audit name carries scope metadata (description + validator function path) and validates against `ValidateAudit`.
- [ ] REQ-0.0.45-01-06: Given a waiver entry with a blank, missing, or single-token `next_action`, when model validation runs, then the entry is fail-closed with a typed error naming the field.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD — Red-Green-Refactor)

```text
# Paste test output here
```

### Code Quality

```text
# Paste lint/format/type check output here
```

### Gate 3 (Docs)

```text
# Paste docs-build output here when Gate 3 applies
```

### Gate 4 (BDD)

```text
# Paste behave output here when Gate 4 applies
```

### Gate 5 (Human)

```text
# Record attestation text here when required by parent lane
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

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
