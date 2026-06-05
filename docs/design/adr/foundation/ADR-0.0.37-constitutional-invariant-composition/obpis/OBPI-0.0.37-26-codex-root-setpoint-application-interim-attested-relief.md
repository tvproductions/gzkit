---
id: OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief
parent: ADR-0.0.37-constitutional-invariant-composition
item: 26
lane: Heavy
status: Completed
# req_atomic rationale (ADR-0.0.64 escape valve): this OBPI delivered ONE coherent
# #519 emergency-relief payload — a single root-surface compression with its budget
# calibration, vendor-manifest setpoint declaration, and interim rendition artifact.
# Each REQ is one indivisible acceptance check against that single payload; none
# decomposes into independent labor units, so seq=01-per-REQ is correct granularity,
# not under-subdivision.
req_atomic:
  - REQ-0.0.37-26-01
  - REQ-0.0.37-26-02
  - REQ-0.0.37-26-03
  - REQ-0.0.37-26-04
  - REQ-0.0.37-26-05
  - REQ-0.0.37-26-06
---

# OBPI-0.0.37-26-codex-root-setpoint-application-interim-attested-relief: Codex Root Setpoint Application Interim Attested Relief

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #26 - "OBPI-0.0.37-26 — #519 Codex-root setpoint application + interim attested relief (declare lean `AgentContract.codex`/tighter-root setpoint; land an operator-attested interim hand-compressed rendition as the first committed-rendition artifact — sequenced FIRST so the emergency is not stranded; fix `data/instructions_files_budget.json` miscalibration; composer regenerates the rendition once 21/22 land)"

**Status:** Completed

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

Problem before: root `AGENTS.md` sat at 32,651 B = 99.6% of Codex's 32,768 B
`project_doc_max_bytes` cap (~117 B from silent truncation) — the #519 emergency.
Codex loads the shared root surface by name and silently truncates past the cap
with no warning, so the agent contract was one edit from losing its tail unseen.

Capability now: the shared root surface is 28,489 B with ~4.3 KB headroom under
the cap, achieved by re-homing terse Mechanical skeletons into the local splice
(`.gzkit/agents.local.md`) rather than deleting prose the ADR-0.0.33 retention gate
requires verbatim — so surface-fidelity stays green. The interim compressed
rendition is committed so the composer (OBPI-21/22) regenerates it rather than
re-deriving the relief payload.

### Key Proof


`wc -c AGENTS.md` → `28489` (under the 32,768 B Codex cap, ~4.3 KB headroom).
`uv run gz check` → "✓ All checks passed" (26/26), including `--invariant-coherence`,
`--instructions-files-budget`, and surface-fidelity.

### Implementation Summary


- Parent ADR decision item: "OBPI-0.0.37-26 — #519 Codex-root setpoint application + interim attested relief (declare lean `AgentContract.codex`/tighter-root setpoint; land an operator-attested interim hand-compressed rendition as the first committed-rendition artifact — sequenced FIRST so the emergency is not stranded; fix `data/instructions_files_budget.json` miscalibration; composer regenerates the rendition once 21/22 land)"
- #519 interim relief landed via direct commit `705a2354` (sanctioned recovery direct-fix path; loosening pass `8dc04a9a` routes recovery/emergency fixes to direct-fix, not the pipeline): root `AGENTS.md` compressed 32,651 → 28,489 B via the local-splice diet (`.gzkit/agents.local.md` → 4,997 B), under Codex's 32,768 B `project_doc_max_bytes` cap with ~4.3 KB headroom (REQ-01).
- `data/instructions_files_budget.json` `files["AGENTS.md"]` recalibrated to 30,000 — the prior 33,000 exceeded the Codex cap and would have green-lit a silently-truncated file (REQ-02).
- `data/vendor-manifest.json` `content_type_temperatures.AgentContract` declares the relief-path setpoint as `{codex: lite, claude: heavy}` (REQ-03).
- Interim committed-rendition artifact present at `renditions/agentcontract-codex-root-interim.md` for OBPI-21/22 to regenerate or migrate (REQ-04).
- Render-path coherence holds: `.gzkit/agents.local.md` + the rendition supply the compressed source, `AGENTS.md` carries the rendered result, `uv run gz validate --invariant-coherence` passes (REQ-05). Scope stayed inside Allowed Paths (REQ-06).
- Tests/validation: `uv run gz check` 26/26 green incl. `--invariant-coherence`, `--instructions-files-budget`, surface-fidelity; behave REQ coverage waived per the interim-relief rationale (all six REQs are SUPPORT-kind, no Gherkin-observable behavior).
- Defects noted: none.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — operator Gate-5 attestation for OBPI-0.0.37-26 (Heavy/foundation). Verified at Stage 4: root AGENTS.md 28,489 B (≤30,000 cap, ~4.3 KB Codex headroom); budget recalibrated to 30,000; vendor-manifest AgentContract setpoint declared; rendition artifact present; invariant-coherence green (10 scopes). Receipts: arb-ruff-0f99170233774f7b99912b6f711fe4d8, arb-step-typecheck-659e3deb06124647a8cb74d6d2088967, arb-step-unittest-1967d22de9ef4e63bdf94a17537cc2dd (5879 tests), arb-step-mkdocs-454b1a5b8d724a5391a40bc5188b75f5. All 6 REQs SUPPORT-kind, LEDGER_PLUS_VALIDATOR channel.
- Date: 2026-06-05

---

**Date Completed:** 2026-06-05

**Evidence Hash:** -
