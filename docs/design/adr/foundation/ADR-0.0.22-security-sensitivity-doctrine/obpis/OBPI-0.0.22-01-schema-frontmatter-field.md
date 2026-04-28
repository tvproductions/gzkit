---
id: OBPI-0.0.22-01-schema-frontmatter-field
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 1
lane: Heavy
status: Draft
depends_on: []
---

# OBPI-0.0.22-01-schema-frontmatter-field: Schema + frontmatter field for sensitivity axis

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- **Checklist Item:** #1 - "Schema + frontmatter field — Add `sensitivity` enum to adr.json and obpi.json schemas; Pydantic model updates; table-driven TDD tests (declared:absent, declared:security, malformed); backwards-compatibility audit on ~150 existing briefs"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Schema + frontmatter field — Add `sensitivity` enum to adr.json and obpi.json schemas; Pydantic model updates; table-driven TDD tests (declared:absent, declared:security, malformed); backwards-compatibility audit on ~150 existing briefs.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/obpis/OBPI-0.0.22-01-schema-frontmatter-field.md` — this brief
- `src/gzkit/schemas/adr.json` — ADR JSON schema gains optional `sensitivity` enum
- `src/gzkit/schemas/obpi.json` — OBPI JSON schema gains optional `sensitivity` enum
- `src/gzkit/models/**` — Pydantic model surfaces gain `sensitivity` field
- `tests/governance/**` — schema and model tests
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

1. REQUIREMENT: `src/gzkit/schemas/adr.json` accepts `sensitivity` as an optional enum field with values [`security`] and rejects all other values with a schema-validation failure.
1. REQUIREMENT: `src/gzkit/schemas/obpi.json` accepts `sensitivity` as an optional enum field with values [`security`] and rejects all other values with a schema-validation failure.
1. REQUIREMENT: The Pydantic model(s) for ADR and OBPI frontmatter expose `sensitivity` as a typed optional field (e.g. `sensitivity: str | None` constrained to {None, "security"}); `extra="forbid"` continues to reject unrecognized keys.
1. REQUIREMENT: Existing ADR and OBPI artifacts under `docs/design/adr/**` validate cleanly without a `sensitivity` field present — backwards compatibility is preserved (the field is optional, defaulting to absent).
1. REQUIREMENT: NEVER promote `sensitivity` to a required field in this OBPI; auto-detect enforcement is OBPI-03's scope.
1. REQUIREMENT: NEVER author the security-surface registry, the validate scope, the audit OR, the walkthrough extension, the rule file, or the AGENTS.md matrix in this OBPI — those belong to OBPIs 02-06 respectively.

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
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/**`
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
uv run -m unittest tests/test_persona_schema.py -v
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.22-01-01: Given a brief frontmatter with `sensitivity: security`, when validated against `src/gzkit/schemas/obpi.json` (and the ADR equivalent against `adr.json`), then the schema accepts the document.
- [ ] REQ-0.0.22-01-02: Given a brief frontmatter omitting `sensitivity` entirely, when validated against the schemas, then the schema accepts the document (field is optional; floor for ~existing briefs).
- [ ] REQ-0.0.22-01-03: Given a brief frontmatter with `sensitivity: confidential` (or any value not in the enum), when validated, then the schema rejects the document with a clear error citing the offending field.
- [ ] REQ-0.0.22-01-04: Given the canonical Pydantic ADR/OBPI frontmatter model(s), when constructed with `sensitivity="security"`, then the value is preserved on the immutable model; when constructed without the key, then `sensitivity` is `None`.
- [ ] REQ-0.0.22-01-05: Given every existing ADR and OBPI artifact under `docs/design/adr/**`, when validated by `gz validate --documents` after this OBPI lands, then validation passes — backwards-compatibility floor.

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
