---
id: OBPI-0.0.45-02-cli-mode-density-doctrine
parent: ADR-0.0.45-cli-mode-density-doctrine
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.45-02-cli-mode-density-doctrine: Cli Mode Density Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`
- **Checklist Item:** #2 - "OBPI-0.0.45-02: **cli-flag-density-validator** — AST walker over `src/gzkit/cli/parser_*.py`; counts per-verb flag accretion against bands (Green ≤7, Yellow 8–12, Red >12); Yellow requires waiver naming why not subcommand promotion; Red fail-closed."

**Status:** Draft

## Objective

**cli-flag-density-validator** — AST walker over `src/gzkit/cli/parser_*.py`; counts per-verb flag accretion against bands (Green ≤7, Yellow 8–12, Red >12); Yellow requires waiver naming why not subcommand promotion; Red fail-closed.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md` — parent ADR for intent and scope (read-only)
- `src/gzkit/cli/parser_*.py` — read-only AST walk surface
- `src/gzkit/governance/trust_audits/cli_flag_density.py` — net-new validator created by this OBPI
- `tests/governance/test_cli_flag_density.py` — net-new unit tests created by this OBPI

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## OBPI creates these files

- `src/gzkit/governance/trust_audits/cli_flag_density.py`
- `tests/governance/test_cli_flag_density.py`

## Requirements (FAIL-CLOSED)

1. REQ-0.0.45-02-01: An AST walker at `src/gzkit/governance/trust_audits/cli_flag_density.py` parses every `src/gzkit/cli/parser_*.py` file and yields per-verb flag counts (counting `add_argument` calls that contribute long-option flags, excluding positional arguments).
1. REQ-0.0.45-02-02: Per-verb counts compare against the Green (≤7) / Yellow (8–12) / Red (>12) bands from `data/cli_flag_density_thresholds.json` resolved via the `CliFlagDensityThresholds` model from OBPI-0.0.45-01.
1. REQ-0.0.45-02-03: Green produces no diagnostic; Yellow produces a diagnostic that demands a waiver entry naming why the verb is not promoted to a subcommand; Red fail-closes with exit 3 unless a foundation-attested waiver entry exists for the verb.
1. REQ-0.0.45-02-04: Waiver entries are resolved from `data/cli_flag_density_waivers.json`; missing waiver entry, blank `next_action`, or expired `valid_until` are all fail-closed.
1. REQ-0.0.45-02-05: The validator is registered as `cli-flag-density` in `data/validate_audits.json` and invokable via `gz validate audit cli-flag-density` (CLI wiring lands in OBPI-0.0.45-04; this OBPI only ships the validator function).
1. REQ-0.0.45-02-06: Unit tests at `tests/governance/test_cli_flag_density.py` cover Green / Yellow / Red cases against synthetic parser fixtures, missing-waiver fail-close, and expired-waiver fail-close.

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
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/cli/parser_*.py`
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
test -f src/gzkit/cli/parser_validate.py
test -f src/gzkit/governance/trust_audits/cli_density_models.py
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

- [ ] REQ-0.0.45-02-01: Given `src/gzkit/cli/parser_*.py`, when the AST walker runs, then it returns one count per registered verb covering all long-option flags.
- [ ] REQ-0.0.45-02-02: Given thresholds from `data/cli_flag_density_thresholds.json`, when the walker classifies a verb, then bands resolve to Green ≤7, Yellow 8–12, Red >12.
- [ ] REQ-0.0.45-02-03: Given a verb in Red band without a waiver, when the validator runs, then it exits 3 with an error naming the verb and the count.
- [ ] REQ-0.0.45-02-04: Given a waiver entry with blank `next_action` or expired `valid_until`, when validated, then it fail-closes with a typed error.
- [ ] REQ-0.0.45-02-05: Given the validator is registered in `data/validate_audits.json` as `cli-flag-density`, when listed, then `gz validate audit cli-flag-density` resolves to this validator function.
- [ ] REQ-0.0.45-02-06: Given synthetic parser fixtures, when the validator runs under unittest, then Green / Yellow / Red and missing/expired-waiver cases all assert the expected band classification and exit shape.

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
