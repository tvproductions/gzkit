---
id: OBPI-0.44.0-03-codex-skills-personas-subagents
parent: ADR-0.44.0-vendor-alignment-codex
item: 3
lane: Heavy
status: Draft
allowlist:
- docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md
- docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-03-codex-skills-personas-subagents.md
- src/gzkit/personas
- src/gzkit/sync_surfaces.py
- src/gzkit/sync_skills.py
- .codex/agents
- .agents/verifier.md
- tests/test_agent_sync.py
- tests/test_persona_portability.py
- tests/test_persona_drift.py
- tests/test_sync.py
- features/persona_sync.feature
- docs/user/manpages/personas.md
reqs:
- REQ-0.44.0-03-01
- REQ-0.44.0-03-02
- REQ-0.44.0-03-03
- REQ-0.44.0-03-04
- REQ-0.44.0-03-05
verification:
- gz validate --brief-command-shape and rejected at the verify stage.
- Write multi-step verification as separate uv run ... lines. -->
- uv run -m unittest tests.test_agent_sync tests.test_persona_portability tests.test_persona_drift tests.test_sync
- uv run gz personas drift
- uv run gz agent sync control-surfaces --dry-run
---

# OBPI-0.44.0-03-codex-skills-personas-subagents: Codex Skills Personas Subagents

## ADR Item

- **Source ADR:** `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md`
- **Checklist Item:** #3 - "OBPI-0.44.0-03: **codex-skills-personas-subagents** — Generate Codex subagent roles from canonical inputs and validate skill, persona, and role parity without treating vendor mirrors as source"

**Status:** Draft

## Objective

Control-surface sync deterministically derives Codex pipeline roles from
canonical persona and role contracts, preserves user-owned roles, and proves
that Codex skill metadata and persona mirrors remain faithful delivery outputs.

## Lane

**Heavy** - This OBPI changes a command/API/schema/runtime contract surface.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

<!-- What files/directories are IN SCOPE? Be explicit with paths. -->

- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/ADR-0.44.0-vendor-alignment-codex.md` — parent ADR and generated-surface invariant
- `docs/design/adr/pre-release/ADR-0.44.0-vendor-alignment-codex/obpis/OBPI-0.44.0-03-codex-skills-personas-subagents.md` — this contract and evidence
- `src/gzkit/personas` — canonical persona composition and role rendering
- `src/gzkit/sync_surfaces.py` — role and persona sync wiring
- `src/gzkit/sync_skills.py` — Codex skill-package metadata preservation
- `.codex/agents` — generated and user-owned Codex role files
- `.agents/verifier.md` — remove the orphaned legacy role file
- `tests/test_agent_sync.py` — role generation and preservation coverage
- `tests/test_persona_portability.py` — Codex persona adapter coverage
- `tests/test_persona_drift.py` — generated persona parity coverage
- `tests/test_sync.py` — Codex skill metadata mirroring coverage
- `features/persona_sync.feature` — operator-visible persona and role sync behavior
- `docs/user/manpages/personas.md` — generated-role documentation

## Denied Paths

<!-- What files/directories are OUT OF SCOPE? Agents will not touch these. -->

- `.gzkit/personas/**` — canonical project persona content is consumed, not rewritten
- `.gzkit/skills/**` — canonical skill packages are consumed, not rewritten
- `.agents/skills/**` and `.agents/personas/**` — generated mirrors are never authored directly
- `.codex/config.toml` and `.codex/hooks.json` — owned by OBPI-01 and OBPI-02
- `.gzkit/ledger.jsonl` direct edits
- Paths not listed in Allowed Paths
- New dependencies, CI files, and lockfiles

## Requirements (FAIL-CLOSED)

<!-- Constraints that MUST hold. Numbered list. NEVER/ALWAYS language.
     These are the rules agents ground against. If not met, OBPI fails. -->

1. REQUIREMENT: Generate implementer, narrator, quality-reviewer, spec-reviewer, and
   pipeline-orchestrator Codex roles from canonical persona plus role contracts.
2. REQUIREMENT: Compose each role's `developer_instructions` from the canonical persona
   frame and explicit produces/consumes/boundaries contract; generic expertise
   claims are forbidden.
3. REQUIREMENT: Preserve Codex agent files outside the generated role set and remove the
   orphaned `.agents/verifier.md` legacy surface.
4. REQUIREMENT: Retain each canonical skill package's `agents/openai.yaml` and assets
   byte-for-byte in the Codex skill mirror.
5. NEVER: Read a vendor mirror as input; derive `.agents/personas` through the
   registered Codex adapter and prove idempotent role, skill, and persona parity.

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
- [ ] Required path exists or is intentionally created in this OBPI: `.agents/skills`
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
uv run -m unittest tests.test_agent_sync tests.test_persona_portability tests.test_persona_drift tests.test_sync
uv run gz personas drift
uv run gz agent sync control-surfaces --dry-run
```

## Demo

<!-- THE YIELDED PRODUCT, not housekeeping. Concrete, runnable invocations
     that demonstrate the capability this OBPI delivers — e.g. an actual
     diagnosis run against a real file, the `--json` form, an auto-chain
     trigger. The closeout ceremony walkthrough harvests this section
     (parser-validated; unregistered verbs are dropped). Prefer real paths
     and arguments over `<placeholder>` syntax. `--help` is not a demo. -->

```bash
uv run gz personas drift
```

## Acceptance Criteria

<!--
Specific, testable criteria for completion.
Each checkbox MUST carry a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [ ] REQ-0.44.0-03-01 [BEHAVIOR]: Given the five canonical pipeline personas and role contracts, sync emits parseable Codex agent TOML whose instructions contain both the persona grounding and the role boundaries.
- [ ] REQ-0.44.0-03-02 [BEHAVIOR]: Given a user-owned Codex role, repeated sync preserves it while refreshing each generated role exactly once and produces no second-run diff.
- [ ] REQ-0.44.0-03-03 [BEHAVIOR]: Given canonical skill packages containing `agents/openai.yaml` or assets, the Codex mirror is byte-equivalent and no package metadata is omitted.
- [ ] REQ-0.44.0-03-04 [BEHAVIOR]: Given canonical personas, the registered Codex adapter regenerates equivalent `.agents/personas` content and drift is reported when a delivery file changes.
- [ ] REQ-0.44.0-03-05 [BEHAVIOR]: Given the legacy `.agents/verifier.md`, sync removes the orphan without deleting any canonical persona, skill, or user-owned Codex role.

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

- Parent Decision quote: **codex-skills-personas-subagents** — Generate Codex subagent role definitions from canonical persona and role contracts, and validate skill, persona, and agent-role parity without editing vendor mirrors as source
- Planned files: canonical persona/role renderer, sync wiring, generated Codex roles, focused parity tests, BDD, and persona documentation
- Tests added: pending TDD execution
- Date completed: pending
- Attestation status: pending Gate 5
- Defects noted: `.agents/verifier.md` is an orphan and existing `.codex/agents/*.toml` files are hand-maintained

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
