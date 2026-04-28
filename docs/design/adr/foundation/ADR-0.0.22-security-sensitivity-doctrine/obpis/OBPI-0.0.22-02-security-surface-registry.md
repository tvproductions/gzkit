---
id: OBPI-0.0.22-02-security-surface-registry
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 2
lane: Heavy
status: Draft
depends_on: []
---

# OBPI-0.0.22-02-security-surface-registry: Security-surface registry data file

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- **Checklist Item:** #2 - "Security-surface registry — Author `data/security_surfaces.json` with 9 initial categories; JSON schema fragment; Pydantic SecuritySurfaceEntry model with frozen+forbid; governance contract documented (self-bootstrapping); glob-matching tests"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Security-surface registry — Author `data/security_surfaces.json` with 9 initial categories; JSON schema fragment; Pydantic SecuritySurfaceEntry model with frozen+forbid; governance contract documented (self-bootstrapping); glob-matching tests.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/obpis/OBPI-0.0.22-02-security-surface-registry.md` — this brief
- `data/security_surfaces.json` — the registry data file authored by this OBPI
- `src/gzkit/schemas/security_surfaces.json` — JSON schema fragment for the registry
- `src/gzkit/models/**` — `SecuritySurfaceEntry` Pydantic model home
- `tests/governance/**` — registry validation and glob-matching tests
- `tests/models/**` — model-level tests if that directory pattern applies

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold for THIS brief's scope. Cross-brief invariants
     live in the parent ADR Decision; per-brief requirements assert this brief's
     contract only. -->

1. REQUIREMENT: `data/security_surfaces.json` exists and validates against `src/gzkit/schemas/security_surfaces.json` after this OBPI lands.
1. REQUIREMENT: The registry contains the nine initial categories named in the parent ADR Decision: `credential_handling`, `subprocess_user_input`, `crypto_primitives`, `auth_boundaries`, `external_api_surfaces`, `ledger_integrity`, `arb_receipt_chain`, `secret_handling`, `deserialization_user_input`. Each category has at least one glob pattern.
1. REQUIREMENT: The JSON schema fragment at `src/gzkit/schemas/security_surfaces.json` declares `category` (enum), `globs` (non-empty array of strings), and `rationale` (non-empty string) as required fields and is `additionalProperties: false`.
1. REQUIREMENT: The Pydantic model `SecuritySurfaceEntry` is defined with `ConfigDict(frozen=True, extra="forbid")` per `.claude/rules/models.md`; fields match the JSON schema.
1. REQUIREMENT: A registry entry with a malformed glob, an unknown category, or an extra key fails Pydantic construction with a typed error.
1. REQUIREMENT: The registry's governance contract — "edits to `data/security_surfaces.json` require a brief carrying `sensitivity: security`" — is documented inline (top-of-file comment or sibling README) and cites the parent ADR.
1. REQUIREMENT: This OBPI's own brief is the bootstrap exception (registry doesn't exist before this OBPI commits); the rule file authored in OBPI-06 records the bootstrap waiver.
1. REQUIREMENT: NEVER author the schema/frontmatter field, the validate scope, the audit OR, the walkthrough extension, the rule file, or the AGENTS.md matrix in this OBPI — those belong to OBPIs 01 and 03-06 respectively.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- [ ] Required path exists or is intentionally created in this OBPI: `data/security_surfaces.json`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Existing tests adjacent to the Allowed Paths reviewed before implementation
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

<!-- Which gates apply and how to verify them. -->

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

<!-- Heavy lane only: -->
### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

<!-- What commands verify this work? Use real repo commands, then paste the
     outputs into Evidence. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md
test -f data/security_surfaces.json
uv run -m unittest tests/test_persona_schema.py -v
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.22-02-01: Given `data/security_surfaces.json` after this OBPI lands, when validated against `src/gzkit/schemas/security_surfaces.json`, then validation passes and the document parses as a list of `SecuritySurfaceEntry` records.
- [ ] REQ-0.0.22-02-02: Given the registry, when iterated, then all nine canonical categories are present (`credential_handling`, `subprocess_user_input`, `crypto_primitives`, `auth_boundaries`, `external_api_surfaces`, `ledger_integrity`, `arb_receipt_chain`, `secret_handling`, `deserialization_user_input`), each with at least one glob pattern.
- [ ] REQ-0.0.22-02-03: Given a registry entry with an unknown category, malformed glob, or extra key, when constructed via `SecuritySurfaceEntry(...)`, then Pydantic raises a typed validation error and the registry as a whole is rejected.
- [ ] REQ-0.0.22-02-04: Given the `SecuritySurfaceEntry` model, when inspected at runtime, then `model_config` declares `frozen=True` and `extra="forbid"` per `.claude/rules/models.md`.
- [ ] REQ-0.0.22-02-05: Given a brief whose `## ALLOWED PATHS` glob list intersects any registry glob, when matched against the registry by the helper function this OBPI exposes, then the matching category labels are returned (consumed by OBPI-03's `validate_sensitivity_binding`).
- [ ] REQ-0.0.22-02-06: Given the registry file, when read, then a top-of-file comment (or sibling README) records the self-bootstrapping governance contract and the one-time bootstrap exception for this OBPI.

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

<!-- Record observations during/after implementation.
     Command outputs, file:line references, dates. -->

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
