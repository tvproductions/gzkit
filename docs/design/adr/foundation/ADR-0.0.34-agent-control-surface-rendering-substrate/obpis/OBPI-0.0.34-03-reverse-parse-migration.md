---
id: OBPI-0.0.34-03-reverse-parse-migration
parent: ADR-0.0.34-agent-control-surface-rendering-substrate
item: 3
lane: Heavy
status: Draft
---

# OBPI-0.0.34-03-reverse-parse-migration: Reverse Parse Migration

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- **Checklist Item:** #3 - "OBPI-0.0.34-03: Reverse-parse migration tooling — `gz content import <file> --as <type>` reads existing hand-authored markdown back into canonical Pydantic models; round-trip fidelity contract enforced"

**Status:** Draft

## Objective

<!-- One-sentence concrete outcome. What does "done" look like? -->

Reverse-parse migration tooling — `gz content import <file> --as <type>` reads existing hand-authored markdown back into canonical Pydantic models; round-trip fidelity contract enforced.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: **Content model registry generalization.** Extend ADR-0.16.0 OBPI-01
1. REQUIREMENT: **Rendering pipeline.** Replace file-copy logic in `gz agent sync` with
1. REQUIREMENT: **Reverse-parse migration tooling.** `gz content import <file> --as <type>`
1. REQUIREMENT: **Authoring CLI.** `gz content edit / render / list / show` —
1. REQUIREMENT: **Light TUI affordances.** Claude-Code-style status lines, chore-runner
1. REQUIREMENT: **Validation hooks.** Every render and every save fires the ADR-0.0.33
1. REQUIREMENT: **Migration layer.** Pydantic schema versioning so model refactors do
1. REQUIREMENT: **Vendor manifest expansion.** ADR-0.16.0 OBPI-03 seeded the vendor

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/**`
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
test -f docs/design/adr/foundation/ADR-0.0.34-agent-control-surface-rendering-substrate/ADR-0.0.34-agent-control-surface-rendering-substrate.md
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.34-03-01: Given the parent ADR intent, when the OBPI implementation is complete, then the primary scoped artifacts exist and match the documented contract
- [ ] REQ-0.0.34-03-02: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched
- [ ] REQ-0.0.34-03-03: Given the Verification commands in this brief, when they run, then evidence is recorded before the OBPI is accepted

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
