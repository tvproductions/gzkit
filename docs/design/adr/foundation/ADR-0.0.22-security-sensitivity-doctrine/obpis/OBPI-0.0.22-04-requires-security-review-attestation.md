---
id: OBPI-0.0.22-04-requires-security-review-attestation
parent: ADR-0.0.22-security-sensitivity-doctrine
item: 4
lane: Heavy
status: Draft
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
- `AGENTS.md` — primary context-frame contract
- `src/gzkit/templates/agents.md` — generated AGENTS template source
- `src/gzkit/templates/adr.md` — ADR template surface for future context frames
- `src/gzkit/sync_surfaces.py` — AGENTS regeneration surface

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: `gz validate --sensitivity` intersects each brief's `## ALLOWED PATHS` glob list with a registered security-surface registry (`data/security_surfaces.json`).
1. REQUIREMENT: Any intersection forces `sensitivity: security` regardless of frontmatter (the auto-detect floor).
1. REQUIREMENT: Frontmatter MAY declare `sensitivity: security` when paths don't trigger detection (escalation channel for cases the registry misses, e.g. test fixtures for new auth flows under `tests/**`).
1. REQUIREMENT: Frontmatter MAY NOT declare a value lower than detected. Validator exits 3 on attempted escape.
1. REQUIREMENT: Same enforcement shape as `kind` (declared in frontmatter, validated by `gz validate --taxonomy`), with the auto-detect floor added on top.
1. REQUIREMENT: A new function `_requires_security_review_attestation` at `src/gzkit/commands/adr_audit.py` returns True when the brief carries `sensitivity: security` (whether declared or auto-detected).
1. REQUIREMENT: This function ORs into the existing `_requires_human_obpi_attestation` predicate alongside the foundation-kind branch and the heavy-lane branch.
1. REQUIREMENT: A `lite + feature + sensitivity:security` brief is no longer self-closeable. Gate 5 human attestation is required at the brief level.
1. REQUIREMENT: The TTY + `ATTEST` confirmation gate at `_enforce_human_attestation_authenticity` (the GHI #290 closure) automatically applies because attestation is now required.
1. REQUIREMENT: Heightened attestation walkthrough: TTY + `ATTEST` prompt enumerates a security-specific checklist (credential handling reviewed, subprocess input validated, crypto choices justified, boundary validation confirmed). The walkthrough is enumerated in the rule file, not authored ad-hoc per brief.
1. REQUIREMENT: Scan receipt cited inline: attestation text MUST cite a fresh `arb-step-security-*` receipt produced by whatever scanner the feature ADR settles on. `CANONICAL_STEP_COMMANDS` at `src/gzkit/arb/validator.py` extends with the security-scan invocation slot; the slot is reserved by this ADR but the canonical command string is filled by the feature ADR that promotes the toolchain.
1. REQUIREMENT: Same shape as today's heavy-lane attestation pattern (canonical receipts cited + attestation text), with the security-specific walkthrough added.
1. REQUIREMENT: `src/gzkit/schemas/adr.json` and `src/gzkit/schemas/obpi.json`: add optional `sensitivity` enum field with values [`security`].
1. REQUIREMENT: `data/security_surfaces.json` (new): registry of glob patterns + category labels. Edits governed by the doctrine itself.
1. REQUIREMENT: `src/gzkit/governance/trust_audits.py`: add `validate_sensitivity_binding` for `gz validate --sensitivity` scope. Emits structured findings (file, declared_sensitivity, detected_sensitivity, intersecting_paths, registry_categories). Fail-closed (exit 3) on escape attempts and unwaived violations.
1. REQUIREMENT: `src/gzkit/commands/adr_audit.py`: add `_requires_security_review_attestation`; OR into `_requires_human_obpi_attestation` alongside the existing foundation-kind and heavy-lane branches.
1. REQUIREMENT: `src/gzkit/arb/validator.py`: extend `CANONICAL_STEP_COMMANDS` with the security-scan invocation slot (reserved name, command string filled by the toolchain feature ADR).
1. REQUIREMENT: `src/gzkit/commands/obpi.py`: walkthrough prompt extension when the brief being completed carries `sensitivity: security`.
1. REQUIREMENT: `data/behave_coverage_waivers.json` extension: foundation OBPIs deferring BDD per existing pattern.
1. REQUIREMENT: `docs/governance/advisory-rules-audit.md`: scorecard entry classifying the new rule as Mechanical.
1. REQUIREMENT: `.gzkit/rules/security-sensitivity.md` (new): canonical rule file declaring the invariant, the registry contract, the validate scope, the walkthrough enumeration, and the scanner-unavailable failure mode.
1. REQUIREMENT: `AGENTS.md` § Lane & Kind & Sensitivity Attestation Matrix: add the third axis to the existing lane/kind matrix.
1. REQUIREMENT: Does NOT author the security scanner toolchain (bandit/semgrep) — that's the feature ADR promoting `pool.agentic-security-review`.
1. REQUIREMENT: Does NOT author content-layer injection scanning — that's `pool.content-injection-scanning`, complementary attack surface.
1. REQUIREMENT: Does NOT add additional sensitivity values beyond `security` — privacy, compliance, safety-critical are separate foundation ADRs (YAGNI).
1. REQUIREMENT: Does NOT enforce separation-of-duties (attestor != implementer) — appealing but adds multi-agent coordination requirement; follow-up ADR if drift observed.
1. REQUIREMENT: Does NOT enforce allow-list expiry on the registry — registry edits are governed by the doctrine; no expiry mechanism in v1.
1. REQUIREMENT: Does NOT change the existing `kind` or `lane` axes — sensitivity is purely additive.

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

- [ ] REQ-0.0.22-04-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.22-04-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.22-04-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

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
