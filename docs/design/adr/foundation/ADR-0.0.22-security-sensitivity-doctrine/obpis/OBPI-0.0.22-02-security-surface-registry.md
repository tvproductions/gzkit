---
id: OBPI-0.0.22-02-security-surface-registry
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 2
lane: Heavy
status: Completed
depends_on: []
---

# OBPI-0.0.22-02-security-surface-registry: Security-surface registry data file

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- **Checklist Item:** #2 - "Security-surface registry — Author `data/security_surfaces.json` with 9 initial categories; JSON schema fragment; Pydantic SecuritySurfaceEntry model with frozen+forbid; governance contract documented (self-bootstrapping); glob-matching tests"

**Status:** Draft

## Objective

Author the canonical security-surface registry (`data/security_surfaces.json`) with the nine categories canonized in ADR-0.0.22, the JSON Schema fragment that validates it (`src/gzkit/schemas/security_surfaces.json`), the frozen+`extra="forbid"` Pydantic `SecuritySurfaceEntry` model with a stdlib-glob-aware `match_globs` helper for OBPI-03's `validate_sensitivity_binding` to consume, and a sibling README documenting the self-bootstrapping governance contract plus the one-time bootstrap exception — leaving the validate scope, audit OR, walkthrough extension, rule file, and AGENTS.md matrix to OBPIs 03–06.

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


```python
>>> from pathlib import Path
>>> from gzkit.models import load_registry, match_globs
>>> registry = load_registry(Path("data/security_surfaces.json"))
>>> len(registry), {e.category for e in registry} == set([
...     "credential_handling", "subprocess_user_input", "crypto_primitives",
...     "auth_boundaries", "external_api_surfaces", "ledger_integrity",
...     "arb_receipt_chain", "secret_handling", "deserialization_user_input"])
(9, True)
>>> match_globs(("src/gzkit/arb/validator.py", "src/gzkit/ledger.py"), registry)
('ledger_integrity', 'arb_receipt_chain')
>>> match_globs(("docs/**/*.md",), registry)
()
```

The auto-detect floor (ADR-0.0.22 §Decision) is mechanically grounded: a brief whose `## ALLOWED PATHS` lists `src/gzkit/arb/**` or `src/gzkit/ledger.py` will be classified `sensitivity: security` once OBPI-03 wires `validate_sensitivity_binding`; a brief touching only `docs/**` returns no categories and remains unaffected.

Quality receipts (Stage 3 ARB-wrapped):
- Lint clean: `arb-ruff-ae458924858b4a6999e90836854a841f`
- Typecheck clean: `arb-step-typecheck-4c27e795ae154c9798196e1c559a5b48`
- Scoped unittest 32/32: `arb-step-unittest-5f4311e9375b465a94f0c21518bbd3bb`
- Full unittest suite GREEN: `arb-step-unittest-6f556666bc704d26b83c11aa85f8e2a8`
- mkdocs --strict GREEN: `arb-step-mkdocs-f90786ebd7344d14ab8765e2ab0e8adb`
- Documents validated: `uv run gz validate --documents` → "All validations passed (1 scopes)"
- REQ → @covers parity gate: `uv run gz covers OBPI-0.0.22-02 --json` → 6/6 REQs covered (100%)

### Implementation Summary


- Files created: `src/gzkit/models/security_surfaces.py` (Pydantic `SecuritySurfaceEntry` + `load_registry` + `match_globs` + `CANONICAL_CATEGORIES` + `SecurityCategory` re-exports); `src/gzkit/schemas/security_surfaces.json` (JSON Schema 2020-12 fragment, `additionalProperties: false`, 9-category enum); `data/security_surfaces.json` (9 entries: `credential_handling`, `subprocess_user_input`, `crypto_primitives`, `auth_boundaries`, `external_api_surfaces`, `ledger_integrity`, `arb_receipt_chain`, `secret_handling`, `deserialization_user_input` — globs cross-checked against the live `src/gzkit` tree); `data/README-security-surfaces.md` (governance contract citing ADR-0.0.22 + bootstrap-exception narrative); `tests/models/test_security_surface_entry.py` (11 tests covering REQ-03 + REQ-04); `tests/governance/test_security_surfaces_registry.py` (21 tests covering REQ-01, REQ-02, REQ-05, REQ-06 + TestScopeDiscipline asserting OBPI-03/04/06 surfaces remain unauthored).
- Files modified: `src/gzkit/models/__init__.py` (re-exports `SecuritySurfaceEntry`, `load_registry`, `match_globs`, `CANONICAL_CATEGORIES`, `SecurityCategory` so OBPI-03 can `from gzkit.models import match_globs`); `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/obpis/OBPI-0.0.22-02-security-surface-registry.md` (Objective made substantive per `gz obpi precomplete` brief-readiness check).
- Tests added: 32 unit tests (11 model-tier in `tests/models/`, 21 governance-tier in `tests/governance/`); full unittest suite GREEN; OBPI-scoped tests run in 5 ms.
- Date completed: 2026-04-29.
- Attestation status: human, operator-attested via `attest completed` at Stage 4; relayed through `gz obpi complete --attestor-present` per AGENTS.md GHI #292 (active pipeline marker at `.claude/plans/.pipeline-active-OBPI-0.0.22-02.json` satisfies the co-presence proxy).
- Defects noted: none. One in-flight ruff catch (`B905` zip-without-strict) fixed before ARB receipt emission; ARB-ruff went `exit_status=1` → `exit_status=0` on re-run. No GHIs filed.

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — Confirmed at Stage 4 ceremony following 32/32 unittest GREEN, full suite GREEN, mkdocs --strict GREEN, gz validate --documents GREEN, and 6/6 REQ→@covers parity (100%). Registry data file authored with the nine canonical categories from ADR-0.0.22 §Decision; governance contract documented in sibling README per REQ-06; bootstrap exception narrated; cross-OBPI scope discipline mechanically asserted by TestScopeDiscipline (3 tests confirming OBPI-03/04/06 surfaces NOT authored). Receipts: lint arb-ruff-ae458924858b4a6999e90836854a841f; types arb-step-typecheck-4c27e795ae154c9798196e1c559a5b48; scoped tests arb-step-unittest-5f4311e9375b465a94f0c21518bbd3bb; full suite arb-step-unittest-6f556666bc704d26b83c11aa85f8e2a8; docs arb-step-mkdocs-f90786ebd7344d14ab8765e2ab0e8adb.
- Date: 2026-04-29

---

**Brief Status:** Completed

**Date Completed:** 2026-04-29

**Evidence Hash:** -
