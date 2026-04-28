---
id: OBPI-0.0.22-04-requires-security-review-attestation
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 4
lane: Heavy
status: Draft
depends_on:
  - OBPI-0.0.22-01-schema-frontmatter-field
---

# OBPI-0.0.22-04-requires-security-review-attestation: _requires_security_review_attestation audit OR

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md`
- **Checklist Item:** #4 - "`_requires_security_review_attestation` audit OR — Function at adr_audit.py; OR into `_requires_human_obpi_attestation`; behavioral tests confirm lite+feature+security brief not self-closeable; TTY+ATTEST gate activates correctly; matrix update at AGENTS.md"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

`_requires_security_review_attestation` audit OR — Function at adr_audit.py; OR into `_requires_human_obpi_attestation`; behavioral tests confirm lite+feature+security brief not self-closeable; TTY+ATTEST gate activates correctly; matrix update at AGENTS.md.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/ADR-0.0.22-security-sensitivity-doctrine.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.22-security-sensitivity-doctrine/obpis/OBPI-0.0.22-04-requires-security-review-attestation.md` — this brief
- `src/gzkit/commands/adr_audit.py` — `_requires_security_review_attestation` is added here and ORed into `_requires_human_obpi_attestation`
- `tests/commands/**` — behavioral tests for the audit predicate
- `AGENTS.md` — Lane & Kind & Sensitivity Attestation Matrix update (third-axis row additions)
- `src/gzkit/templates/agents.md` — template source mirrored to AGENTS.md by sync
- `src/gzkit/sync_surfaces.py` — sync surface regenerator if matrix wiring requires it

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold for THIS brief's scope. Cross-brief invariants
     live in the parent ADR Decision; per-brief requirements assert this brief's
     contract only. -->

1. REQUIREMENT: A new function `_requires_security_review_attestation` is defined at `src/gzkit/commands/adr_audit.py` and returns `True` for any brief carrying `sensitivity: security` — whether declared in frontmatter or auto-detected by OBPI-03's validator output.
1. REQUIREMENT: `_requires_security_review_attestation` ORs into the existing `_requires_human_obpi_attestation` predicate at `src/gzkit/commands/adr_audit.py` alongside the foundation-kind branch and the heavy-lane branch — same shape as the existing OR composition.
1. REQUIREMENT: A `lite + feature + sensitivity:security` brief is no longer self-closeable: `gz obpi complete` on such a brief refuses to emit a `human_attestation: true` receipt without TTY-bound human attestation.
1. REQUIREMENT: The existing TTY + `ATTEST` confirmation gate at `_enforce_human_attestation_authenticity` (the GHI #290 closure) activates for security-sensitive briefs by virtue of the OR — no new TTY-gating code is added in this OBPI; the ORing alone reuses the existing gate.
1. REQUIREMENT: AGENTS.md § "Lane & Kind & Sensitivity Attestation Matrix" exists and is the third-axis successor to the current "Lane & Kind Attestation Matrix" — every (kind × lane × sensitivity) cell is enumerated, with `sensitivity: security` rows marking attestation as Required regardless of lane or kind.
1. REQUIREMENT: The matrix in AGENTS.md cites the canonical source-of-truth function (`_requires_human_obpi_attestation`) and notes that the matrix is a readable projection of the code, not authoritative — same disclaimer pattern as the existing kind/lane matrix.
1. REQUIREMENT: The matrix update flows through `src/gzkit/templates/agents.md` and is propagated to `AGENTS.md` via `gz agent sync control-surfaces` if the project regenerates AGENTS.md from the template; if AGENTS.md is hand-maintained, edit the file directly per `.claude/rules/skill-surface-sync.md`.
1. REQUIREMENT: Behavioral tests confirm: `lite + feature + sensitivity:security` brief returns True from `_requires_human_obpi_attestation`; `lite + feature + sensitivity:null` returns False; `heavy + feature + sensitivity:null` continues to return True (no regression of the heavy branch); `lite + foundation + sensitivity:null` continues to return True (no regression of the foundation branch).
1. REQUIREMENT: NEVER author the schema/frontmatter field, the validate scope, the walkthrough extension, the ARB canonical command slot, or the standalone rule file in this OBPI — those belong to OBPIs 01, 03, 05, and 06 respectively.

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
- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
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
rg -n "^## Persona$" AGENTS.md
test -f src/gzkit/templates/agents.md
test -f src/gzkit/templates/adr.md
test -f src/gzkit/sync_surfaces.py
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.22-04-01: Given a brief with `sensitivity: security`, when `_requires_security_review_attestation(brief)` is called, then it returns `True`; given any other sensitivity value or absent field, it returns `False`.
- [ ] REQ-0.0.22-04-02: Given a `lite + feature + sensitivity:security` brief, when `_requires_human_obpi_attestation(brief)` is called, then it returns `True` via the OR composition that includes `_requires_security_review_attestation`.
- [ ] REQ-0.0.22-04-03: Given a `lite + feature + sensitivity:null` brief, when `_requires_human_obpi_attestation(brief)` is called, then it returns `False` (self-closeable baseline preserved).
- [ ] REQ-0.0.22-04-04: Given a `heavy + feature + sensitivity:null` brief and a `lite + foundation + sensitivity:null` brief, when `_requires_human_obpi_attestation` is called, then both still return `True` (no regression of heavy-lane and foundation-kind branches).
- [ ] REQ-0.0.22-04-05: Given a `lite + feature + sensitivity:security` brief authored under a headless process, when `gz obpi complete` is invoked, then attestation is refused at `_enforce_human_attestation_authenticity` (the existing TTY + `ATTEST` gate) — the audit OR alone is sufficient to reuse the gate; no new TTY-gating code is added.
- [ ] REQ-0.0.22-04-06: Given AGENTS.md after this OBPI lands, when read, then a section titled "Lane & Kind & Sensitivity Attestation Matrix" exists, enumerates every (kind × lane × sensitivity) combination, marks `sensitivity: security` rows as Required, and cites `_requires_human_obpi_attestation` as the source-of-truth function.

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
