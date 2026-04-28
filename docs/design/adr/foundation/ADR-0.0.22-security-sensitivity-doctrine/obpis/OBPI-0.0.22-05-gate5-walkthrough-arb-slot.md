---
id: OBPI-0.0.22-05-gate5-walkthrough-arb-slot
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 5
lane: Heavy
status: Draft
depends_on:
  - OBPI-0.0.22-04-requires-security-review-attestation
---

# OBPI-0.0.22-05-gate5-walkthrough-arb-slot: Gate 5 walkthrough extension and ARB canonical command slot

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- **Checklist Item:** #5 - "Gate 5 walkthrough extension + ARB canonical command slot — Walkthrough prompt at obpi.py; checklist in rule file; `CANONICAL_STEP_COMMANDS` extends with reserved security-scan slot; fail-closed when receipt unavailable; behavioral tests for walkthrough-fires, receipt-missing, receipt-stale"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Gate 5 walkthrough extension + ARB canonical command slot — Walkthrough prompt at obpi.py; checklist in rule file; `CANONICAL_STEP_COMMANDS` extends with reserved security-scan slot; fail-closed when receipt unavailable; behavioral tests for walkthrough-fires, receipt-missing, receipt-stale.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/obpis/OBPI-0.0.22-05-gate5-walkthrough-arb-slot.md` — this brief
- `src/gzkit/commands/obpi.py` — walkthrough prompt extension when brief carries `sensitivity: security`
- `src/gzkit/arb/validator.py` — `CANONICAL_STEP_COMMANDS` extension with the reserved security-scan slot
- `tests/commands/**` — walkthrough-fires, receipt-missing, receipt-stale tests
- `tests/arb/**` — canonical-step-commands tests
- `data/behave_coverage_waivers.json` — waiver if BDD is deferred per existing pattern

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold for THIS brief's scope. Cross-brief invariants
     live in the parent ADR Decision; per-brief requirements assert this brief's
     contract only. -->

1. REQUIREMENT: When `gz obpi complete` runs against a brief carrying `sensitivity: security` (declared or auto-detected), `src/gzkit/commands/obpi.py` extends the attestation walkthrough with a security-specific checklist enumerated in `.gzkit/rules/security-sensitivity.md` (authored by OBPI-06).
1. REQUIREMENT: The security checklist enumerates at minimum: credential handling reviewed, subprocess input validated, crypto choices justified, boundary validation confirmed. The walkthrough reads the canonical list from the rule file at runtime; the list is NOT hardcoded into `obpi.py`.
1. REQUIREMENT: `CANONICAL_STEP_COMMANDS` at `src/gzkit/arb/validator.py` is extended with one new entry — a reserved slot for the security-scan step. The slot reserves the receipt-name prefix `arb-step-security-` and a command-string placeholder; the actual canonical command is left unfilled in this OBPI (filled by the toolchain feature ADR that promotes `pool.agentic-security-review`).
1. REQUIREMENT: When the canonical security-scan command is unset (placeholder state) and a brief carrying `sensitivity: security` reaches Gate 5, `gz obpi complete` fails closed (exit 3) with a finding that names the unfilled slot and the parent ADR.
1. REQUIREMENT: When the canonical security-scan command is set but no fresh receipt exists in `.gzkit/arb/` (or wherever ARB receipts live), `gz obpi complete` fails closed with a "receipt-missing" finding.
1. REQUIREMENT: When a security-scan receipt exists but is older than the canonical staleness threshold (24 hours per parent ADR Decision), `gz obpi complete` fails closed with a "receipt-stale" finding citing the receipt timestamp.
1. REQUIREMENT: Behavioral tests confirm: walkthrough fires for `sensitivity: security` briefs and not for others; receipt-missing produces exit 3 with the documented finding shape; receipt-stale produces exit 3 with the documented finding shape; placeholder-slot produces exit 3 with the documented finding shape.
1. REQUIREMENT: NEVER author the schema/frontmatter field, the registry, the validate scope, the audit OR predicate, the rule file, or the AGENTS.md matrix in this OBPI — those belong to OBPIs 01-04 and 06.
1. REQUIREMENT: NEVER author the actual security-scan command string in this OBPI — that is the toolchain feature ADR's scope. Reserving the slot is in scope; filling it is not.

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
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.22-05-01: Given a brief with `sensitivity: security`, when `gz obpi complete` runs in a TTY, then the prompt enumerates the security checklist (credential handling, subprocess input, crypto choices, boundary validation) sourced from `.gzkit/rules/security-sensitivity.md`.
- [ ] REQ-0.0.22-05-02: Given a brief without `sensitivity: security`, when `gz obpi complete` runs, then the security checklist is NOT presented (no false-positive walkthrough).
- [ ] REQ-0.0.22-05-03: Given `CANONICAL_STEP_COMMANDS` after this OBPI lands, when inspected, then it contains a reserved entry whose receipt prefix is `arb-step-security-` and whose canonical command string is in a documented placeholder state awaiting the toolchain feature ADR.
- [ ] REQ-0.0.22-05-04: Given a `sensitivity: security` brief and an unfilled canonical security-scan slot, when `gz obpi complete` is invoked, then it exits 3 with a finding identifying the unfilled slot and the parent ADR (placeholder-slot fail-closed).
- [ ] REQ-0.0.22-05-05: Given a `sensitivity: security` brief, a filled canonical security-scan slot, and no matching ARB receipt under `.gzkit/arb/`, when `gz obpi complete` is invoked, then it exits 3 with a "receipt-missing" finding (receipt-missing fail-closed).
- [ ] REQ-0.0.22-05-06: Given a `sensitivity: security` brief and an `arb-step-security-*` receipt older than the documented staleness threshold (24 hours), when `gz obpi complete` is invoked, then it exits 3 with a "receipt-stale" finding citing the receipt's timestamp.

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
