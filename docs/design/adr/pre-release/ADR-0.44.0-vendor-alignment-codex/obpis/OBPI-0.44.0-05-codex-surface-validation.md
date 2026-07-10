---
id: OBPI-0.44.0-05-codex-surface-validation
parent: ADR-0.44.0-vendor-alignment-codex
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.44.0-05-codex-surface-validation: Codex Surface Validation

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- **Checklist Item:** #5 - "OBPI-0.44.0-05: **codex-surface-validation** — Extend `gz validate --surfaces` and tests so Codex config, hooks, skills, personas, and generated metadata drift fail like Claude drift"

**Status:** Draft

## Objective

`gz validate --surfaces` fails closed on independently corrupted Codex config,
hook registration, skill metadata, persona, and agent-role fixtures, while the
committed and wheel-delivered surface passes the same parity contract.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` — parent ADR and fidelity assertion
- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-05-codex-surface-validation.md` — this contract and evidence
- `data` — machine-readable 12-behavior Codex parity contract
- `src/gzkit/schemas` — parity-contract schema
- `src/gzkit/validate_pkg/surface.py` — aggregate Codex surface validation
- `src/gzkit/validate_pkg/sync_parity.py` — generated-output drift validation
- `src/gzkit/governance/trust_audits/orientation.py` — current hook-schema validation
- `src/gzkit/skills_mirror.py` — Codex skill package parity
- `src/gzkit/personas` — Codex persona and role parity
- `src/gzkit/governance/trust_audits/distribution.py` — wheel-delivery parity integration
- `tests/test_codex_config_surface.py` — config and hook negative controls
- `tests/test_validate_sync_parity.py` — generated-output negative controls
- `tests/test_skills_audit.py` — skill metadata and asset negative controls
- `tests/test_persona_drift.py` — persona and role negative controls
- `tests/governance/test_orientation_freshness.py` — inert flat-hook rejection
- `tests/governance/test_distribution_audit.py` — wheel-delivery proof
- `features/agent_sync.feature` — fail-closed operator behavior
- `docs/user/manpages/validate.md` — Codex surface validation contract

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.codex/**` and `.agents/**` — delivery fixtures are validated, never repaired here
- `.claude/**` and `.github/**` — other vendor behavior is unchanged
- `.gzkit/ledger.jsonl` direct edits
- Paths not listed in Allowed Paths
- New dependencies, CI files, and lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Define a schema-validated 12-behavior contract naming the ten direct
   Codex lifecycle homes and the two runtime substitutes.
2. REQUIREMENT: Validate `.codex/config.toml` semantics and configured path,
   `.codex/hooks.json` current schema and owned groups, `.codex/agents` role
   parity, `.agents/personas` adaptation, and complete `.agents/skills`
   packages including `agents/openai.yaml` and assets.
3. REQUIREMENT: Include an independent negative control for each surface class; the
   validator must fail because of the corrupted semantic field, not a string
   snapshot mismatch alone.
4. REQUIREMENT: Reject the obsolete flat Codex hook shape even when orientation command
   text appears correct.
5. NEVER: Repair drift during validation, treat a generated surface as truth,
   or omit the same checks from package/wheel-delivered canonical content.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first.
     Order matters: read the structured input (parent ADR § Decision)
     before the unstructured one (allowed paths, prerequisites). -->

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/**`
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
uv run -m unittest tests.test_codex_config_surface tests.test_validate_sync_parity tests.test_skills_audit tests.test_persona_drift tests.governance.test_orientation_freshness tests.governance.test_distribution_audit
uv run gz validate --surfaces
uv run gz validate --distribution
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
uv run gz validate --surfaces
uv run gz validate --distribution
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.44.0-05-01 [BEHAVIOR]: Given the parity data, schema validation accepts exactly ten direct hook behaviors and two named runtime substitutes, with no unclassified Claude behavior.
- [ ] REQ-0.44.0-05-02 [BEHAVIOR]: Given one semantic corruption in config, hooks, skills, personas, or roles, `gz validate --surfaces` exits nonzero and identifies that surface and field.
- [ ] REQ-0.44.0-05-03 [BEHAVIOR]: Given an obsolete flat Codex hook registration containing plausible orientation text, validation rejects it because Codex discovers zero command handlers.
- [ ] REQ-0.44.0-05-04 [BEHAVIOR]: Given the committed repository surface, `gz validate --surfaces` passes without rewriting any file.
- [ ] REQ-0.44.0-05-05 [BEHAVIOR]: Given the built distribution in a clean initialized fixture, the same Codex surface is reproduced and `gz validate --distribution` passes.

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

- Parent Decision quote: **codex-surface-validation** — Extend `gz validate --surfaces` and tests so Codex config, hooks, skills, personas, and generated metadata drift fail like Claude drift
- Planned files: parity data/schema, surface and distribution validators, semantic negative-control tests, BDD, and validate documentation
- Tests added: pending TDD execution
- Date completed: pending
- Attestation status: pending Gate 5
- Defects noted: current validators falsely accept an inert flat Codex hook file

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
