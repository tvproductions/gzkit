---
id: OBPI-0.34.0-02-authoring-time-kind-rejection
parent: ADR-0.34.0-foundation-sunset
item: 2
lane: Heavy
status: Draft
---

# OBPI-0.34.0-02-authoring-time-kind-rejection: Authoring Time Kind Rejection

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`
- **Checklist Item:** #2 - "authoring-time-kind-rejection: Reject 'gz plan create --kind foundation' and 'gz adr promote --kind foundation' at the command layer with three-part guardrail-feedback prose (what failed / why forbidden: foundation kind closed ADR-0.34.0 / next step: --kind feature or pool). Close the authoring doors while leaving the schema enum intact for grandfathered validation. (heavy lane: CLI authoring-behavior change)."

**Status:** Draft

## Objective

Close the two foundation-authoring doors — `gz plan create --kind foundation` and `gz adr promote --kind foundation` — by rejecting each at the command handler with three-part guardrail-feedback prose (what failed / why forbidden: the foundation kind is closed by ADR-0.34.0 / governed next step: `--kind feature` or `--kind pool`), while leaving the `foundation` value in the schema `kind` enum and in argparse `choices` intact so the ~51 grandfathered `kind: foundation` ADRs still validate.

## Lane

**Heavy** - This OBPI changes CLI authoring behavior: two operator-facing command verbs (`gz plan create`, `gz adr promote`) that previously accepted `--kind foundation` now reject it. That is a runtime-contract change to a human-used surface, so Gate 3 (docs) and Gate 4 (BDD) fire alongside the universal Gate 5 brief-level attestation (ADR-0.0.36).

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `src/gzkit/commands/plan.py` — command handler for `gz plan create`; the `_validate_kind_and_semver` guard (~line 151, before the existing `kind == "foundation"` semver check at ~line 166) is where the closed-kind rejection is seated.
- `src/gzkit/commands/adr_promote.py` — command handler for `gz adr promote`; the `_validate_promotion_kind_semver` guard (~line 54, alongside the existing pool/foundation/feature kind checks) is where the closed-kind rejection is seated.
- `tests/` — new/updated tests covering the three REQs (rejection prose for both verbs; grandfathered-foundation still-validates).
- `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md` — parent ADR (read-only, for intent and scope).

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `src/gzkit/schemas/adr.json` — the `kind` enum MUST retain `foundation` (REQ-0.34.0-02-03 depends on it validating the grandfathered set). Do not remove the value.
- `src/gzkit/cli/parser_governance.py`, `src/gzkit/cli/parser_artifacts.py`, `src/gzkit/cli/parser_maintenance.py` — the argparse `choices=[..., "foundation", ...]` MUST stay so the handler receives `foundation` and emits the guardrail prose (argparse's bare "invalid choice" cannot carry three-part prose). Parser help-text / choices coherence for the closed kind is OBPI-0.34.0-03's coupled-surface sweep, not this OBPI.
- `data/foundation_grandfather.json`, `gz validate --taxonomy` scope — OBPI-0.34.0-01 and -03/-04 own the manifest, closed-kind assertion, and terminal-partition gate.
- All other paths not listed in Allowed Paths; new dependencies; CI files; lockfiles.

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS: Reject at the COMMAND HANDLER (`plan.py` / `adr_promote.py`), never by deleting `foundation` from the schema enum or argparse `choices` — the enum must still validate the ~51 grandfathered `kind: foundation` ADRs.
2. ALWAYS: Each rejection MUST emit three-part guardrail-feedback prose per `.claude/rules/guardrail-feedback-prose.md`: (a) what failed — `--kind foundation` was requested; (b) why forbidden — the foundation kind is closed to new authoring by ADR-0.34.0; (c) governed next step — re-run with `--kind feature` (release-carrying work) or `--kind pool` (backlog).
3. ALWAYS: Both rejected verbs exit non-zero and write no ADR file / perform no promotion I/O (fail before mutation, matching the existing pre-I/O validation ordering in both handlers).
4. NEVER: Widen the rejection to `--kind feature` or `--kind pool` — only `foundation` authoring is closed.
5. NEVER: Break validation of an existing on-disk `kind: foundation` ADR — `gz validate --documents` / `--taxonomy` on the grandfathered set MUST stay green.
6. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
7. REQUIREMENT: Verification commands MUST be concrete, single-program, and runnable before acceptance.
8. NEVER: Mark the OBPI accepted without explicit human attestation (universal Gate 5, ADR-0.0.36).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary: "reject 'gz plan create --kind foundation' and 'gz adr promote --kind foundation' at the command layer with three-part guardrail-feedback prose (what failed / why forbidden: kind closed ADR-0.34.0 / next step: --kind feature or pool)". The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the sunset closes the foundation kind to new authoring while keeping it a valid schema value for the grandfathered historical set (the kind is SEALED, not deleted).
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.34.0-foundation-sunset/ADR-0.34.0-foundation-sunset.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.claude/rules/guardrail-feedback-prose.md` — the three-part recovery-prose bar every fail-closed surface must meet (what failed / why forbidden / governed next step).
- [ ] `AGENTS.md` § Gate Covenant / Lane Rules — heavy-lane gate set and universal Gate 5.

**Context:**

- [ ] `src/gzkit/commands/plan.py` `_validate_kind_and_semver` (~line 151) and its existing `console.print(...)` rejection prose for the foundation-semver mismatch — match its console/exit style.
- [ ] `src/gzkit/commands/adr_promote.py` `_validate_promotion_kind_semver` (~line 54) and its existing `--kind pool` rejection prose — match its console/exit style.
- [ ] Sibling OBPIs: OBPI-0.34.0-01 (manifest + closed-kind assertion), OBPI-0.34.0-03 (parser/help coherence sweep) — this OBPI must not overlap their surfaces.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/commands/plan.py` exists and exposes `_validate_kind_and_semver`.
- [ ] `src/gzkit/commands/adr_promote.py` exists and exposes `_validate_promotion_kind_semver`.
- [ ] At least one on-disk `kind: foundation` ADR exists under `docs/design/adr/foundation/` to exercise REQ-0.34.0-02-03.

**Existing Code (understand current state):**

- [ ] Existing tests for `plan create` and `adr promote` kind/semver validation reviewed before implementation (search `tests/` for `_validate_kind_and_semver` / `_validate_promotion_kind_semver` coverage).
- [ ] Both handlers' pre-I/O validation ordering confirmed so the new rejection fires before any file write / promotion move.

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
- [ ] `gz plan create` / `gz adr promote` command docs reflect the closed foundation kind (coordinate with OBPI-0.34.0-03's coupled-surface sweep so the two do not conflict)

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
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# 1. gz plan create --kind foundation is rejected with three-part guardrail prose
#    (exits non-zero; names ADR-0.34.0 and the --kind feature / --kind pool alternatives; writes no ADR file).
uv run gz plan create sunset-demo --semver 0.0.99 --lane lite --kind foundation

# 2. gz adr promote --kind foundation is rejected with the same three-part guardrail prose.
uv run gz adr promote ADR-pool.some-backlog-item --semver 0.0.99 --kind foundation

# 3. The escape hatch the prose points at still works — feature authoring is unaffected.
uv run gz plan create sunset-demo --semver 0.35.0 --lane lite --kind feature --dry-run

# 4. An existing grandfathered kind: foundation ADR still validates (closure did not delete the enum value).
uv run gz validate --documents
uv run gz validate --taxonomy
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.34.0-02-01 [BEHAVIOR]: Given `gz plan create --kind foundation`, when the command runs, then it exits non-zero, writes no ADR file, and prints three-part guardrail-feedback prose that (a) states `--kind foundation` was requested, (b) cites the foundation kind as closed to new authoring by ADR-0.34.0, and (c) directs the operator to re-run with `--kind feature` or `--kind pool`.
- [ ] REQ-0.34.0-02-02 [BEHAVIOR]: Given `gz adr promote --kind foundation`, when the command runs, then it exits non-zero, performs no promotion I/O, and prints the same three-part guardrail-feedback prose naming ADR-0.34.0 and the `--kind feature` / `--kind pool` alternatives.
- [ ] REQ-0.34.0-02-03 [BEHAVIOR]: Given an existing grandfathered on-disk `kind: foundation` ADR, when `gz validate --documents` (and `gz validate --taxonomy`) runs over it, then validation exits zero — closing the authoring doors does not invalidate the frozen grandfathered set (the schema enum and argparse choices retain `foundation`).

## Completion Checklist

<!-- Verify all gates before marking OBPI accepted. -->

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Gate 3 (Docs):** Docs build clean; command docs reflect closed kind
- [ ] **Gate 4 (BDD):** Acceptance scenarios pass
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below; human attestation recorded (Gate 5)

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

Before: `gz plan create --kind foundation` and `gz adr promote --kind foundation` accepted the foundation kind and scaffolded/promoted a new foundation ADR, so the operator's "no more foundation ADRs" directive was policy-only and could drift. Now: both authoring doors are closed at the command handler with actionable three-part guardrail prose that names ADR-0.34.0 and points at the `--kind feature` / `--kind pool` alternatives — while the schema enum and argparse choices still carry `foundation` so the ~51 grandfathered ADRs keep validating.

### Key Proof

<!-- One concrete usage example, command, or before/after behavior. -->

`uv run gz plan create sunset-demo --semver 0.0.99 --lane lite --kind foundation` exits non-zero and prints the closed-kind guardrail prose (what failed / why forbidden: ADR-0.34.0 sealed the kind / next step: --kind feature or pool), while `uv run gz validate --documents` over the grandfathered `docs/design/adr/foundation/` set stays green.

### Implementation Summary

- Parent ADR § Decision item (verbatim): "reject 'gz plan create --kind foundation' and 'gz adr promote --kind foundation' at the command layer with three-part guardrail-feedback prose (what failed / why forbidden: kind closed ADR-0.34.0 / next step: --kind feature or pool)".
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
</content>
</invoke>
