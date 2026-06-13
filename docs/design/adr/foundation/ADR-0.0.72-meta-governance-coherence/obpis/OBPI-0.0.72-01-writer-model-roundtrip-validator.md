---
id: OBPI-0.0.72-01-writer-model-roundtrip-validator
parent: ADR-0.0.72-meta-governance-coherence
item: 1
lane: Heavy
status: Draft
---

# OBPI-0.0.72-01-writer-model-roundtrip-validator: Writer Model Roundtrip Validator

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- **Checklist Item:** #1 - "PORT: `gz validate --writer-model-roundtrip` coherence validator — explicit registry of meta-governance artifact writers (handoff writers, insight append path, ledger-event factories, brief authoring); round-trips each writer's ACTUAL emitted output (real emission or writer-derived golden fixture, not a happy-path stub) through that artifact's own authoring model; fails closed (exit 3) on divergence; wired into `gz check`; exhaustiveness test asserts every meta-governance `*_handoff`/`*_event`/`*_record` writer is registered."

**Status:** Draft

## Objective

Ship a new `gz validate --writer-model-roundtrip` scope under `src/gzkit/governance/trust_audits/` that holds an explicit registry of meta-governance writers (handoff writers, the insight-append path, ledger-event factories, brief authoring) and re-validates each writer's REAL emitted output against that artifact's own authoring model. Done looks like: a coherent writer round-trips clean and the audit passes; a writer whose output diverges from its model fails closed with exit 3; an exhaustiveness test fails when any meta-governance `*_handoff`/`*_event`/`*_record` writer is left out of the registry; and the scope runs inside the `gz check` default bundle.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- **CREATE** `src/gzkit/governance/trust_audits/writer_model_roundtrip.py` — new audit module: writer registry + round-trip function returning a `ValidationError` list (sibling to `lock_handoff_coupling.py`, `insights.py`)
- `src/gzkit/quality.py` — add the `run_writer_model_roundtrip_audit` wrapper that the CLI and `gz check` call
- `src/gzkit/cli/parser_maintenance.py` — register the `--writer-model-roundtrip` flag on `gz validate` and dispatch it
- `src/gzkit/commands/quality.py` — wire the audit into the `_build_check_steps` default `gz check` bundle
- `docs/user/manpages/validate.md` — document the `--writer-model-roundtrip` scope (contract + example)
- **CREATE** `tests/governance/test_writer_model_roundtrip.py` — new tests: coherent-pass, divergent-fail-closed, exhaustiveness
- `src/gzkit/handoff_validation.py` — round-trip target: `write_degenerate_handoff` / `_write_reaping_handoff` writers vs `HandoffFrontmatter` (read-only, round-trip target)
- `src/gzkit/lock_manager.py` — round-trip target: handoff writer paths (read-only, round-trip target)
- `src/gzkit/insights/model.py` — round-trip target: `InsightRecord` authoring model (read-only, round-trip target)
- `src/gzkit/ledger_events.py` — round-trip target: ledger-event factories (read-only, round-trip target)
- `src/gzkit/events.py` — round-trip target: Pydantic event models behind the factories (read-only, round-trip target)
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/**` — parent ADR package scope

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. ALWAYS round-trip each writer's REAL emitted output — captured from a live emission or a golden fixture DERIVED from the writer. NEVER round-trip a hand-built happy-path stub; a stub that never exercises the divergent field is the named performative-validator failure mode (ADR Negative #1).
1. ALWAYS fail closed with exit 3 on ANY divergence between a writer's emitted output and that artifact's own authoring model. NEVER downgrade a divergence to a warning or skip it.
1. ALWAYS keep an exhaustiveness assertion: every meta-governance `*_handoff`/`*_event`/`*_record` writer MUST appear in the registry, and an unregistered writer MUST fail the audit. NEVER let a new writer silently escape round-trip coverage.
1. NEVER add a runtime dependency — the audit uses stdlib plus the already-present Pydantic authoring models only (STDLIB-FIRST doctrine).
1. ALWAYS wire the scope into the `gz check` default bundle so the round-trip runs on every check, NEVER only on an explicit opt-in flag.
1. NEVER write outside the Allowed Paths; the round-trip targets (`handoff_validation.py`, `lock_manager.py`, `insights/model.py`, `ledger_events.py`, `events.py`) are read-only inputs in this OBPI — model reconciliation is OBPI-02/-03/-04 scope.
1. ALWAYS follow TDD: a failing test precedes each behavior increment (coherent-pass, divergent-fail-closed, exhaustiveness).

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/ADR-0.0.72-meta-governance-coherence.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.72-meta-governance-coherence/**`
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
uv run gz validate --writer-model-roundtrip
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
# Round-trip every registered meta-governance writer's real output through its own model.
uv run gz validate --writer-model-roundtrip

# Same scope as it runs inside the default check bundle.
uv run gz check
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.0.72-01-01 [behavior]: Given a registered meta-governance writer whose real emitted output validates against its own authoring model, when `--writer-model-roundtrip` runs, then the round-trip passes and the audit returns no error for that writer. (@covers test)
- [ ] REQ-0.0.72-01-02 [behavior]: Given a registered writer whose emitted output diverges from its authoring model (a field the model rejects), when `--writer-model-roundtrip` runs, then the audit fails closed with exit 3 and reports the divergent writer and field. (@covers test)
- [ ] REQ-0.0.72-01-03 [behavior]: Given a meta-governance `*_handoff`/`*_event`/`*_record` writer that is absent from the registry, when the exhaustiveness check runs, then the audit fails (the unregistered writer cannot silently escape round-trip coverage). (@covers test)
- [ ] REQ-0.0.72-01-04 [support]: The `--writer-model-roundtrip` scope is wired into the `gz check` default bundle (appears in `_build_check_steps`). Proof: `gz validate --writer-model-roundtrip` exit 0 as a step inside `gz check` + the `artifact_edited` ledger event for `src/gzkit/commands/quality.py`.
- [ ] REQ-0.0.72-01-05 [support]: The `--writer-model-roundtrip` scope is documented in `docs/user/manpages/validate.md` with contract and example. Proof: `gz cli audit` exit 0 + `gz validate --documents` exit 0 + the `artifact_edited` ledger event for `docs/user/manpages/validate.md`.

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
