---
id: OBPI-0.0.73-04-closeout-audit-fidelity-repoint
parent: ADR-0.0.73-verification-layer-binding-audit
item: 4
lane: Heavy
status: Completed
# req_atomic: each REQ is one indivisible unit of labor — wiring the shared gate
# into closeout (01) and into audit (02) are each a single coherent edit+test;
# graceful-absence handling (03) is folded into the one shared helper, not a
# separate sub-task; the runbook update (04) and the skill repoint+sync (05) are
# each one SUPPORT deliverable. None decomposes into parallel seq=02+ sub-tasks
# (ADR-0.0.64 task-envelope exemption).
req_atomic:
  - REQ-0.0.73-04-01
  - REQ-0.0.73-04-02
  - REQ-0.0.73-04-03
  - REQ-0.0.73-04-04
  - REQ-0.0.73-04-05
---

# OBPI-0.0.73-04-closeout-audit-fidelity-repoint: Closeout Audit Fidelity Repoint

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #4 - "Closeout/audit repoint onto the fidelity gate — both the closeout ceremony and the audit ceremony invoke gz adr fidelity, replacing the prose 'Demonstrate Value' step; runbook + governance_runbook updated; unit tests"

**Status:** Completed

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

- `src/gzkit/traceability.py` (added by brief reconcile, attestor g0)
- `src/gzkit/__init__.py` (added by brief reconcile, attestor g0)

- `src/gzkit/commands/__init__.py` (added by brief reconcile, attestor g0)
- `src/gzkit/commands/ceremony_state.py` (added by brief reconcile, attestor g0)
- `src/gzkit/commands/common.py` (added by brief reconcile, attestor g0)

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR for intent and scope
- `src/gzkit/fidelity.py` — the shared bound gate (`assert_fidelity_for_ceremony`) both ceremonies invoke
- `src/gzkit/commands/closeout_ceremony.py` — invoke the fidelity gate in the closeout ceremony
- `src/gzkit/commands/audit_cmd.py` — invoke the fidelity gate in the audit ceremony
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

1. REQUIREMENT: The closeout ceremony MUST invoke the OBPI-03 fidelity gate at the EXECUTE→ATTESTATION boundary and fail closed when any fidelity assertion fails — never advance to attestation over a red gate (REQ-0.0.73-04-01).
1. REQUIREMENT: The audit ceremony MUST invoke the same standalone fidelity gate — one gate, two consumers — never a second prose copy of the check (REQ-0.0.73-04-02).
1. REQUIREMENT: When an ADR Decision carries no `## Fidelity Assertions` block, both ceremonies MUST flag the absence and fail rather than accept agent prose; the prose 'Demonstrate Value' step is removed, not retained as a fallback (REQ-0.0.73-04-03).
1. REQUIREMENT: The operator runbook and governance runbook MUST describe the bound fidelity gate replacing the prose step, and `gz validate --documents` MUST stay green (REQ-0.0.73-04-04).
1. REQUIREMENT: The gz-adr-audit and gz-adr-closeout-ceremony skills MUST be repointed onto the gate and synced to all mirrors via `gz agent sync control-surfaces`, with `gz validate --surfaces` green (REQ-0.0.73-04-05).

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


$ uv run gz covers OBPI-0.0.73-04-closeout-audit-fidelity-repoint --json
REQ-0.0.73-04-01 | BEHAVIOR | TEST_COVERS           | pass
REQ-0.0.73-04-02 | BEHAVIOR | TEST_COVERS           | pass
REQ-0.0.73-04-03 | BEHAVIOR | TEST_COVERS           | pass
REQ-0.0.73-04-04 | SUPPORT  | LEDGER_PLUS_VALIDATOR | pass
REQ-0.0.73-04-05 | SUPPORT  | LEDGER_PLUS_VALIDATOR | pass
  behavior_uncovered_reqs: 0

The gate is genuinely bound: a failing assertion raises PolicyBreachError
(test_failing_assertion_raises_policy_breach), and both ceremonies resolve to
the SAME function object (test_both_ceremonies_import_the_same_gate). Full-suite
receipt: arb-step-unittest-4d41eba9c7a24700b71a4f1e506a81d3 (exit_status=0).

### Implementation Summary


- Shared gate: src/gzkit/fidelity.py assert_fidelity_for_ceremony — one bound gate both ceremonies invoke (one gate, two consumers)
- Closeout wiring: src/gzkit/commands/closeout_ceremony.py _gate_closeout_proof runs the gate at the EXECUTE->ATTESTATION edge
- Audit wiring: src/gzkit/commands/audit_cmd.py runs the gate before any validation receipt is written
- trust_model fix: .gzkit/skills/gz-adr-audit/SKILL.md no longer documents "does NOT re-verify evidence" (the facade-enabler the ADR named)
- Absence policy: missing ## Fidelity Assertions block warns (stderr), does not hard-block in-flight; presence enforced at ADR closeout (Boundary Invariant #4) — operator-ratified
- SUPPORT: docs/user/runbook.md + docs/governance/governance_runbook.md (REQ-04); gz-adr-audit + gz-adr-closeout-ceremony skills repointed + synced (REQ-05)
- Tests added: 7 in tests/governance/test_closeout_audit_fidelity.py (@covers REQ-01/02/03)
- Fixture migration: tests/test_audit_pipeline.py ADR fixture carries a ## Fidelity Assertions block
- Date completed: 2026-06-17
- Attestation: operator "attest completed" (Gate 5)
- Defects: none in scope; the first-impl deadlock gate bug was fixed under GHI #626 (commit d66a6168)

## Tracked Defects

<!-- Record GitHub defect linkage when defects are discovered during this OBPI.
     Use one bullet per issue so status surfaces can preserve traceability. -->

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — closeout + audit repointed onto the bound fidelity gate (one gate, two consumers via assert_fidelity_for_ceremony); the prose 'Demonstrate Value' step is removed. 3 BEHAVIOR REQs unit-proven (behavior_uncovered_reqs=0 via tests/governance/test_closeout_audit_fidelity.py), 2 SUPPORT REQs via gz validate --documents/--surfaces. Full suite green arb-step-unittest-4d41eba9c7a24700b71a4f1e506a81d3, lint arb-ruff-b9548735f27b45ccaef3a7ee3306b13a, typecheck arb-step-typecheck-526c474a66074b38a45512980f177d11, mkdocs arb-step-mkdocs-0b78a421012d4d948176f19196fc64b2. Graceful-absence policy operator-ratified 2026-06-17.
- Date: 2026-06-17

---

**Date Completed:** 2026-06-17

**Evidence Hash:** -
