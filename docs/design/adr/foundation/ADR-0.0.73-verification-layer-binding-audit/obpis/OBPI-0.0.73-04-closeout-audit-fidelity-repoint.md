---
id: OBPI-0.0.73-04-closeout-audit-fidelity-repoint
parent: ADR-0.0.73-verification-layer-binding-audit
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.73-04-closeout-audit-fidelity-repoint: Closeout Audit Fidelity Repoint

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #4 - "Closeout/audit repoint onto the fidelity gate — both the closeout ceremony and the audit ceremony invoke gz adr fidelity, replacing the prose 'Demonstrate Value' step; runbook + governance_runbook updated; unit tests"

**Status:** Draft

## Objective

Both the closeout ceremony and the audit ceremony invoke the OBPI-03 fidelity gate
(one gate, two consumers), replacing the prose 'Demonstrate Value' step with a
bound, runnable check. "Done" = closeout and audit each run the fidelity gate
against the ADR under ceremony and fail when an assertion fails; the runbook and
governance_runbook describe the bound gate; the gz-adr-audit / closeout skills are
repointed and synced.

Closeout/audit repoint onto the fidelity gate — both the closeout ceremony and the audit ceremony invoke the fidelity gate, replacing the prose 'Demonstrate Value' step; runbook + governance_runbook updated; unit tests.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR for intent and scope
- `src/gzkit/commands/closeout_ceremony.py` — invoke the fidelity gate in the closeout ceremony
- `src/gzkit/commands/audit_cmd.py` — invoke the fidelity gate in the audit ceremony
- `src/gzkit/commands/adr_audit.py` — audit logic that drops the prose 'Demonstrate Value' step
- `.gzkit/skills/gz-adr-audit/SKILL.md` — replace the prose Value-Demonstration step with the bound gate (canonical; sync after)
- `.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md` — repoint the ceremony onto the gate (canonical; sync after)
- `docs/user/runbook.md` — operator runbook reflects the bound fidelity gate
- `docs/governance/governance_runbook.md` — governance runbook reflects the bound fidelity gate
- `tests/governance/test_closeout_audit_fidelity.py` **CREATE** — unit tests for both ceremonies invoking the gate
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-04-closeout-audit-fidelity-repoint.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: Closeout/audit repoint onto the fidelity gate — both the closeout ceremony and the audit ceremony invoke gz adr fidelity, replacing the prose 'Demonstrate Value' step; runbook + governance_runbook updated; unit tests.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief
1. REQUIREMENT: Verification commands MUST be concrete and runnable before acceptance
1. NEVER: Mark the OBPI accepted while scaffold defaults remain in the brief
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/**`
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
     outputs into Evidence. These are CONSTRUCTION HOUSEKEEPING (lint, type,
     test, mkdocs) — they prove the codebase is healthy, not what the OBPI
     yielded. The yielded product belongs in the `## Demo` section below.

     AUTHORING CONTRACT: Every command in this section must be a single-program,
     shell-less invocation — no &&, ||, |, ;, $(...), or redirects. The
     OBPI-pipeline verify stage executes commands via shlex.split + shell=False
     (GHI #415); compound commands are blocked at authoring time by
     gz validate --brief-command-shape and rejected at the verify stage.
     Write multi-step verification as separate uv run ... lines. -->

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f src/gzkit/commands/closeout_ceremony.py
test -f tests/governance/test_closeout_audit_fidelity.py
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. -->

```bash
# Closeout now runs the bound fidelity gate (was: prose 'Demonstrate Value').
uv run gz closeout ADR-0.0.73-verification-layer-binding-audit --dry-run
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.73-04-01 [BEHAVIOR]: Given an ADR under closeout, when the closeout ceremony runs, then it invokes the fidelity gate and fails the closeout when any fidelity assertion fails. (@covers test in `tests/governance/test_closeout_audit_fidelity.py`)
- [ ] REQ-0.0.73-04-02 [BEHAVIOR]: Given an ADR under audit, when the audit ceremony runs, then it invokes the same standalone fidelity gate (one gate, two consumers). (@covers test in `tests/governance/test_closeout_audit_fidelity.py`)
- [ ] REQ-0.0.73-04-03 [BEHAVIOR]: Given an ADR whose Decision has no `## Fidelity Assertions` block, when closeout or audit runs, then the ceremony flags the absence rather than accepting agent prose (the prose 'Demonstrate Value' step is gone). (@covers test in `tests/governance/test_closeout_audit_fidelity.py`)
- [ ] REQ-0.0.73-04-04 [SUPPORT]: The operator and governance runbooks describe the bound fidelity gate replacing the prose step. Proof: `gz validate --documents` exit 0 + `artifact_edited` ledger event for `docs/user/runbook.md`.
- [ ] REQ-0.0.73-04-05 [SUPPORT]: The gz-adr-audit and closeout-ceremony skills are repointed onto the gate and synced to mirrors. Proof: `gz validate --surfaces` exit 0 + `artifact_edited` ledger event for `.gzkit/skills/gz-adr-audit/SKILL.md`.

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

**Date Completed:** -

**Evidence Hash:** -
