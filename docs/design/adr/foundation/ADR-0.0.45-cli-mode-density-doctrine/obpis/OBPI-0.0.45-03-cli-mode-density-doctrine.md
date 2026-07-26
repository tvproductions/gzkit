---
id: OBPI-0.0.45-03-cli-mode-density-doctrine
parent: ADR-0.0.45-cli-mode-density-doctrine
item: 3
lane: Heavy
status: Draft
allowlist:
- docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md
- data/validate_suites.json
- src/gzkit/governance/trust_audits/suite_density.py
- tests/governance/test_suite_density.py
reqs:
- REQ-0.0.45-03-01
- REQ-0.0.45-03-02
- REQ-0.0.45-03-03
- REQ-0.0.45-03-04
- REQ-0.0.45-03-05
- REQ-0.0.45-03-06
- REQ-0.0.45-03-07
verification:
- uv run gz validate --documents
- uv run gz lint
- uv run gz typecheck
- uv run gz test
---

# OBPI-0.0.45-03-cli-mode-density-doctrine: Cli Mode Density Doctrine

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md`
- **Checklist Item:** #3 - "OBPI-0.0.45-03: **suite-density-validator** — Walker over `data/validate_suites.json`; counts per-suite audit membership against bands (Green ≤6, Yellow 7–10, Red >10); includes orphan-member detection."

**Status:** Draft

## Objective

**suite-density-validator** — Walker over `data/validate_suites.json`; counts per-suite audit membership against bands (Green ≤6, Yellow 7–10, Red >10); includes orphan-member detection.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.45-cli-mode-density-doctrine/ADR-0.0.45-cli-mode-density-doctrine.md` — parent ADR for intent and scope (read-only)
- `data/validate_suites.json` — read-only registry input (created by OBPI-0.0.45-01)
- `src/gzkit/governance/trust_audits/suite_density.py` — net-new validator created by this OBPI
- `tests/governance/test_suite_density.py` — net-new unit tests created by this OBPI

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## OBPI creates these files

- `src/gzkit/governance/trust_audits/suite_density.py`
- `tests/governance/test_suite_density.py`
- `data/validate_suites.json`

## Requirements (FAIL-CLOSED)

1. REQ-0.0.45-03-01: A walker at `src/gzkit/governance/trust_audits/suite_density.py` reads `data/validate_suites.json` and yields per-suite audit membership counts.
1. REQ-0.0.45-03-02: Per-suite counts compare against the Green (≤6) / Yellow (7–10) / Red (>10) bands from `data/suite_density_thresholds.json` resolved via the `SuiteDensityThresholds` model from OBPI-0.0.45-01.
1. REQ-0.0.45-03-03: Green produces no diagnostic; Yellow requires a waiver entry naming why the suite is not split; Red fail-closes with exit 3 unless a foundation-attested waiver entry exists for the suite.
1. REQ-0.0.45-03-04: Orphan-member detection: any audit name listed in `data/validate_suites.json` that does not resolve to a registered validator in `data/validate_audits.json` fail-closes with exit 3 and an error naming the orphan name and host suite.
1. REQ-0.0.45-03-05: Waiver entries are resolved from `data/suite_density_waivers.json`; missing waiver entry, blank `next_action`, or expired `valid_until` are all fail-closed.
1. REQ-0.0.45-03-06: The validator is registered as `suite-density` in `data/validate_audits.json` and invokable via `gz validate audit suite-density` (CLI wiring lands in OBPI-0.0.45-04).
1. REQ-0.0.45-03-07: Unit tests at `tests/governance/test_suite_density.py` cover Green / Yellow / Red, orphan-member, missing-waiver, and expired-waiver cases against synthetic suite-registry fixtures.

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
- [ ] Required path exists or is intentionally created in this OBPI: `data/validate_suites.json`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
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
```

## Demo

```bash
# Replace with concrete product demonstrations for this OBPI.
```

## Acceptance Criteria

- [ ] REQ-0.0.45-03-01: Given `data/validate_suites.json`, when the walker runs, then it returns one count per suite covering all listed audit members.
- [ ] REQ-0.0.45-03-02: Given thresholds from `data/suite_density_thresholds.json`, when the walker classifies a suite, then bands resolve to Green ≤6, Yellow 7–10, Red >10.
- [ ] REQ-0.0.45-03-03: Given a suite in Red band without a waiver, when the validator runs, then it exits 3 with an error naming the suite and the count.
- [ ] REQ-0.0.45-03-04: Given a suite entry referencing an audit name unknown to `data/validate_audits.json`, when the validator runs, then it exits 3 with an orphan-member error naming both the orphan and host suite.
- [ ] REQ-0.0.45-03-05: Given a waiver entry with blank `next_action` or expired `valid_until`, when validated, then it fail-closes with a typed error.
- [ ] REQ-0.0.45-03-06: Given the validator is registered as `suite-density` in `data/validate_audits.json`, when listed, then `gz validate audit suite-density` resolves to this validator function.
- [ ] REQ-0.0.45-03-07: Given synthetic suite-registry fixtures, when the validator runs under unittest, then Green / Yellow / Red, orphan-member, and missing/expired-waiver cases all assert the expected band classification and exit shape.

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
