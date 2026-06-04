---
id: OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief
parent: ADR-0.0.37-constitutional-invariant-composition
item: 26
lane: Heavy
status: Draft
---

# OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief: Codex Root Setpoint Application Interim Attested Relief

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #26 - "OBPI-0.0.37-26 — #519 Codex-root setpoint application + interim attested relief (declare lean `AgentContract.codex`/tighter-root setpoint; land an operator-attested interim hand-compressed rendition as the first committed-rendition artifact — sequenced FIRST so the emergency is not stranded; fix `data/instructions_files_budget.json` miscalibration; composer regenerates the rendition once 21/22 land)"

**Status:** Draft

## Objective

OBPI-0.0.37-26 — #519 Codex-root setpoint application + interim attested relief (declare lean `AgentContract.codex`/tighter-root setpoint; land an operator-attested interim hand-compressed rendition as the first committed-rendition artifact — sequenced FIRST so the emergency is not stranded; fix `data/instructions_files_budget.json` miscalibration; composer regenerates the rendition once 21/22 land).

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief.md` — active brief and evidence record
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR for intent and scope
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/**` — interim committed-rendition artifact intentionally created by this OBPI
- `.gzkit/agents.local.md` — current local-content source spliced into root `AGENTS.md`; the near-term compression source
- `AGENTS.md` — Codex-loaded rendered root control surface; the #519 relief target
- `data/vendor-manifest.json` — `AgentContract` setpoint declaration surface
- `data/instructions_files_budget.json` — Codex-cap budget guard explicitly referenced by the checklist item
- `data/behave_coverage_waivers.json` — Gate 4 waiver registry for SUPPORT-kind structural REQs with no Gherkin-observable behavior

## Denied Paths

- Paths not listed in Allowed Paths
- New dependencies
- CI files, lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: This OBPI MUST deliver interim #519 relief by shrinking the repo-root `AGENTS.md` surface that Codex actually loads below Codex's 32,768-byte `project_doc_max_bytes` cap with real headroom.
1. REQUIREMENT: The completed root `AGENTS.md` MUST be no larger than 30,000 bytes, and `data/instructions_files_budget.json` MUST set `files["AGENTS.md"]` to a value no larger than 30,000.
1. REQUIREMENT: `data/vendor-manifest.json` MUST declare the setpoint used for the `AgentContract` root/Codex relief path; no in-code or prose-only setpoint is acceptable.
1. REQUIREMENT: This OBPI MUST land an operator-attested interim hand-compressed rendition artifact under `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/` so OBPI-21/22 can regenerate or migrate it later instead of re-deriving the relief payload.
1. REQUIREMENT: Root relief MUST remain coherent with the current render path: `.gzkit/agents.local.md` and the interim rendition supply the compressed source, `AGENTS.md` carries the rendered result, and `uv run gz validate --invariant-coherence` passes after implementation.
1. REQUIREMENT: Work MUST stay inside the Allowed Paths declared in this brief.
1. REQUIREMENT: Verification commands MUST prove the root byte ceiling, budget calibration, vendor-manifest validity, rendition artifact presence, invariant coherence, and document validity before acceptance.
1. NEVER: Start Stage 2 while this brief's Allowed Paths omit any surface required by the relief payload.
1. ALWAYS: Reconcile the brief with the parent ADR before implementation begins.

> STOP-on-BLOCKERS: if prerequisites are missing, print a BLOCKERS list and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item — quote the line this OBPI implements** verbatim into the brief's Implementation Summary. The Decision item is the contract; everything else hangs off it.
- [ ] Parent ADR § Intent — the why-frame for the Decision read above.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item that this OBPI implements, STOP and re-read. Do not proceed to Allowed Paths, Prerequisites, or implementation until the Decision quote is in hand.

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` or `CLAUDE.md` - agent operating contract

**Context:**

- [ ] Related OBPIs in same ADR

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- [ ] Required path exists or is intentionally created in this OBPI: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/`
- [ ] Required path exists or is intentionally created in this OBPI: `.gzkit/agents.local.md`
- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
- [ ] Required path exists or is intentionally created in this OBPI: `data/vendor-manifest.json`
- [ ] Required path exists or is intentionally created in this OBPI: `data/instructions_files_budget.json`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Root `AGENTS.md` current byte count measured before implementation.
- [ ] `.gzkit/agents.local.md` current byte count and rendered insertion point reviewed before implementation.
- [ ] `data/vendor-manifest.json` `content_type_temperatures.AgentContract` reviewed before implementation.
- [ ] `data/instructions_files_budget.json` current `files["AGENTS.md"]` budget reviewed before implementation.
- [ ] Parent ADR item #26 and OBPI-22 committed-rendition store intent reviewed for the interim artifact convention.

## Quality Gates

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

### Gate 3: Docs (Heavy only)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Relevant docs updated

### Gate 4: BDD (Heavy only)

- [ ] Acceptance scenarios pass: `uv run -m behave features/`

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz validate --vendor-manifest
uv run gz validate --instructions-files-budget
uv run gz validate --invariant-coherence
uv run gz obpi validate docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief.md --authored
uv run gz obpi precomplete OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief

# Specific verification for this OBPI
uv run python -c "from pathlib import Path; size = Path('AGENTS.md').stat().st_size; assert size <= 30000, size; print(size)"
uv run python -c "import json; data = json.load(open('data/instructions_files_budget.json', encoding='utf-8')); budget = data['files']['AGENTS.md']; assert budget <= 30000, budget; print(budget)"
uv run python -c "from pathlib import Path; size = Path('.gzkit/agents.local.md').stat().st_size; assert size <= 6500, size; print(size)"
test -f docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/agentcontract-codex-root-interim.md
```

## Demo

```bash
wc -c AGENTS.md
uv run python -c "import json; print(json.load(open('data/vendor-manifest.json', encoding='utf-8'))['content_type_temperatures']['AgentContract'])"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-26-01 [SUPPORT]: Given Codex silently truncates root `AGENTS.md` after 32,768 bytes, when this OBPI is complete, then root `AGENTS.md` is no larger than 30,000 bytes. Proof: `uv run gz validate --instructions-files-budget` plus Stage-5 `artifact_edited` accounting for `AGENTS.md`.
- [ ] REQ-0.0.37-26-02 [SUPPORT]: Given the instructions-file budget guard protects the same surface, when this OBPI is complete, then `data/instructions_files_budget.json` sets the `AGENTS.md` budget to a value no larger than 30,000. Proof: `uv run gz validate --instructions-files-budget` plus Stage-5 `artifact_edited` accounting for `data/instructions_files_budget.json`.
- [ ] REQ-0.0.37-26-03 [SUPPORT]: Given setpoints are declared data, when this OBPI is complete, then `data/vendor-manifest.json` records the `AgentContract` setpoint used for the root/Codex relief path. Proof: `uv run gz validate --vendor-manifest` plus existing `artifact_edited` accounting for the manifest-declared `AgentContract.codex` setpoint.
- [ ] REQ-0.0.37-26-04 [SUPPORT]: Given OBPI-21/22 have not yet landed the composer/store, when this OBPI is complete, then `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/agentcontract-codex-root-interim.md` exists as the operator-attested interim committed-rendition artifact. Proof: `uv run gz validate --documents` plus Stage-5 `artifact_edited` accounting for the rendition artifact.
- [ ] REQ-0.0.37-26-05 [SUPPORT]: Given `AGENTS.md` is currently rendered from `.gzkit/templates/agents.md` plus `.gzkit/agents.local.md`, when this OBPI is complete, then `uv run gz validate --invariant-coherence` passes. Proof: `uv run gz validate --invariant-coherence` plus the `composition_rendered` ledger event emitted by that validator.
- [ ] REQ-0.0.37-26-06 [SUPPORT]: Given the Allowed Paths in this brief, when the OBPI is executed, then changes remain inside scope and denied paths remain untouched. Proof: `uv run gz validate --brief-reconcile`, `uv run gz obpi precomplete OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief`, plus Stage-5 `artifact_edited` accounting for the scoped files.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** RGR cycle followed, tests derived from brief, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

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

### Key Proof

### Implementation Summary

- Parent ADR decision item: "OBPI-0.0.37-26 — #519 Codex-root setpoint application + interim attested relief (declare lean `AgentContract.codex`/tighter-root setpoint; land an operator-attested interim hand-compressed rendition as the first committed-rendition artifact — sequenced FIRST so the emergency is not stranded; fix `data/instructions_files_budget.json` miscalibration; composer regenerates the rendition once 21/22 land)"
- Planned files created/modified: `.gzkit/agents.local.md`; `AGENTS.md`; `data/vendor-manifest.json`; `data/instructions_files_budget.json`; `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/renditions/agentcontract-codex-root-interim.md`
- Tests added: To be determined by Stage 2; at minimum, verification must prove root byte ceiling, budget calibration, vendor manifest validity, rendition artifact presence, and document validity.
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>` when required, otherwise `n/a`
- Attestation: substantive attestation text or `n/a`
- Date: YYYY-MM-DD or `n/a`

---

**Date Completed:** -

**Evidence Hash:** -
