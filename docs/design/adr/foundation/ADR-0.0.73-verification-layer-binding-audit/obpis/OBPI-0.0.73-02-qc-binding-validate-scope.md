---
id: OBPI-0.0.73-02-qc-binding-validate-scope
parent: ADR-0.0.73-verification-layer-binding-audit
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.0.73-02-qc-binding-validate-scope: Qc Binding Validate Scope

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md`
- **Checklist Item:** #2 - "`gz validate --qc-binding` scope — behavioral negative-control (each step ships a fixture it must fail on; the scope runs it) + theater-signature detection (the six ADR-0.0.37 facade signatures); wired into `gz check`; fail-closed exit 3; manpage + `gz cli audit` green; unit tests"

**Status:** Draft

## Objective

`gz validate --qc-binding` lands as a fail-closed (exit 3) scope wired into the
`gz check` default pipeline that flags any QC step claiming enforcement its code
does not deliver. Detection is **behavioral** — each step ships a negative-control
fixture it MUST fail on and the scope runs it — layered with the six theater
signatures calibrated on the ADR-0.0.37 facade. "Done" = the scope catches a
hollow step behaviorally, passes a genuinely bound step, exits 3 on findings, and
runs as part of `gz check`.

`gz validate --qc-binding` scope — behavioral negative-control (each step ships a fixture it must fail on; the scope runs it) + theater-signature detection (the six ADR-0.0.37 facade signatures); wired into `gz check`; fail-closed exit 3; manpage + `gz cli audit` green; unit tests.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/ADR-0.0.73-verification-layer-binding-audit.md` — parent ADR for intent and scope
- `src/gzkit/governance/trust_audits/qc_binding.py` **CREATE** — the `--qc-binding` audit (behavioral negative-control runner + theater-signature detection)
- `src/gzkit/governance/trust_audits/__init__.py` — register `audit_qc_binding`
- `src/gzkit/commands/validate_cmd.py` — add the `--qc-binding` flag and dispatch
- `src/gzkit/quality.py` — wire `--qc-binding` into the `gz check` default pipeline
- `tests/governance/test_qc_binding_scope.py` **CREATE** — unit tests incl. per-signature calibration fixtures and a behavioral negative-control case
- `docs/user/manpages/validate.md` — document the `--qc-binding` scope (Heavy-lane docs gate)
- `docs/design/adr/foundation/ADR-0.0.73-verification-layer-binding-audit/obpis/OBPI-0.0.73-02-qc-binding-validate-scope.md` — this brief (evidence recording)

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: This OBPI MUST deliver: `gz validate --qc-binding` scope — behavioral negative-control (each step ships a fixture it must fail on; the scope runs it) + theater-signature detection (the six ADR-0.0.37 facade signatures); wired into `gz check`; fail-closed exit 3; manpage + `gz cli audit` green; unit tests.
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
test -f src/gzkit/governance/trust_audits/qc_binding.py
test -f tests/governance/test_qc_binding_scope.py
uv run gz validate --qc-binding
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers. -->

```bash
# Behavioral catch: a hollow step that passes its own negative control is flagged.
uv run gz validate --qc-binding
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.73-02-01 [BEHAVIOR]: Given a QC step that passes its own negative-control fixture (a hollow step), when `gz validate --qc-binding` runs, then the step is flagged as theater. (@covers test in `tests/governance/test_qc_binding_scope.py`)
- [ ] REQ-0.0.73-02-02 [BEHAVIOR]: Given a genuinely bound step that fails its negative control, when `gz validate --qc-binding` runs, then the step passes (no false positive). (@covers test in `tests/governance/test_qc_binding_scope.py`)
- [ ] REQ-0.0.73-02-03 [BEHAVIOR]: Given a calibration fixture for each of the six ADR-0.0.37 theater signatures (mtime-where-name-says-content, empty-input, copy-vs-self, fixture-only, skip-if-PASS, prose-graded-by-nothing), when the scope runs, then each signature is detected. (@covers test in `tests/governance/test_qc_binding_scope.py`)
- [ ] REQ-0.0.73-02-04 [BEHAVIOR]: Given a theater finding, when `gz validate --qc-binding` completes, then it exits 3; given a clean step set, then it exits 0. (@covers test in `tests/governance/test_qc_binding_scope.py`)
- [ ] REQ-0.0.73-02-05 [SUPPORT]: The scope is wired into the `gz check` default pipeline. Proof: `gz validate --qc-binding` exit 0 in `gz check` + `artifact_edited` ledger event for `src/gzkit/quality.py`.
- [ ] REQ-0.0.73-02-06 [STRUCTURAL-FENCE]: `gz validate --qc-binding` is fail-closed (exit 3) and runs inside `gz check` — never a green-by-default opt-in (parent ADR § Boundary Invariants #2).
- [ ] REQ-0.0.73-02-07 [STRUCTURAL-FENCE]: Detection is behavioral — every `bound` step must fail its own negative control; a step that passes its negative control is theater regardless of its docstring (parent ADR § Boundary Invariants #3).
- [ ] REQ-0.0.73-02-08 [SUPPORT]: The new flag is documented in the manpage and `gz cli audit` is green. Proof: `gz validate --cli-alignment` exit 0 + `artifact_edited` ledger event for `docs/user/manpages/validate.md`.

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
