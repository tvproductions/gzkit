---
id: OBPI-0.0.11-04-agents-md-persona-section
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 4
lane: Heavy
status: Draft
---

# OBPI-0.0.11-04-agents-md-persona-section: Agents Md Persona Section

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #4 - "AGENTS.md context frame template update (persona section)"

**Status:** Draft

## Objective

`AGENTS.md` and the template surfaces that generate future agent context frames
include a mandatory `## Persona` section that references the persona control
surface and forbids expertise-claim identity framing.

## Lane

**Heavy** - `AGENTS.md` is an external operator-facing governance contract, and
template changes affect future generated instruction surfaces.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md` — parent ADR for contract intent
- `AGENTS.md` — primary operator-facing contract
- `src/gzkit/templates/agents.md` — generated AGENTS template source
- `src/gzkit/templates/adr.md` — ADR template source for future context frames
- `src/gzkit/sync_surfaces.py` — regeneration surface for agent files
- `docs/governance/governance_runbook.md` — operator documentation for the persona section
- `tests/test_sync_surfaces.py` — regression surface for generated output if needed

## Denied Paths

- `.gzkit/personas/` — control-surface implementation belongs to OBPI-0.0.11-02
- `docs/design/adr/pool/ADR-pool.per-command-persona-context.md` — supersession belongs to OBPI-0.0.11-05
- `tests/test_persona_schema.py` — schema validation belongs to OBPI-0.0.11-06
- Persona profile content for specific roles belongs to ADR-0.0.12
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `AGENTS.md` MUST gain a mandatory `## Persona` section in the
   Agent Context Frame
1. REQUIREMENT: Template sources that generate future context frames MUST stay
   in sync with the `AGENTS.md` contract
1. REQUIREMENT: The persona section MUST describe behavioral identity and
   craftsmanship standards, not expertise claims
1. NEVER: Make the persona section optional or frame it as motivational copy
1. ALWAYS: Re-run the agent/control-surface sync after editing generated
   templates or mirrors

> STOP-on-BLOCKERS: if the generated-vs-source template relationship is unclear,
> print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] `.github/discovery-index.json` - repo structure
- [ ] `AGENTS.md` - agent operating contract
- [ ] Parent ADR - understand full context

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [ ] Existing contract: `AGENTS.md`
- [ ] Template sources: `src/gzkit/templates/agents.md`, `src/gzkit/templates/adr.md`

**Prerequisites (check existence, STOP if missing):**

- [ ] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
- [ ] Required path exists or is intentionally created in this OBPI: `src/gzkit/templates/agents.md`
- [ ] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [ ] Pattern to follow: `AGENTS.md`
- [ ] Pattern to follow: `src/gzkit/templates/agents.md`
- [ ] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted

### Gate 2: TDD

- [ ] Tests written before/with implementation
- [ ] Tests pass: `uv run gz test`
- [ ] Validation commands recorded in evidence with real outputs

### Code Quality

- [ ] Lint clean: `uv run gz lint`
- [ ] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [ ] Docs build: `uv run mkdocs build --strict`
- [ ] Runbook updates explain the mandatory persona section and its constraints

### Gate 4: BDD (Heavy)

- [ ] Manual contract review or existing persona BDD surface demonstrates the persona section is rendered into generated instruction output

### Gate 5: Human (Heavy)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict

# Specific verification for this OBPI
test -f AGENTS.md
rg -n "^## Persona$" AGENTS.md src/gzkit/templates/agents.md src/gzkit/templates/adr.md
uv run gz agent sync control-surfaces
```

## Acceptance Criteria

- [ ] REQ-0.0.11-04-01: `AGENTS.md` contains a mandatory `## Persona` section in the agent context frame
- [ ] REQ-0.0.11-04-02: Template sources and regenerated surfaces stay synchronized with the new persona contract
- [ ] REQ-0.0.11-04-03: The persona section frames behavioral identity and craftsmanship standards without expertise-claim language

## Completion Checklist

- [ ] **Gate 1 (ADR):** Intent recorded in brief
- [ ] **Gate 2 (TDD):** Tests pass, coverage maintained
- [ ] **Code Quality:** Lint, format, type checks clean
- [ ] **Value Narrative:** Problem-before vs capability-now is documented
- [ ] **Key Proof:** One concrete usage example is included
- [ ] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [ ] Intent and scope recorded

### Gate 2 (TDD)

```text
# Record test output here during execution.
```

### Code Quality

```text
# Record lint/typecheck output here during execution.
```

### Gate 3 (Docs)

```text
# Record mkdocs output and runbook evidence here during execution.
```

### Gate 4 (BDD)

```text
# Record manual contract-review notes or generated-surface evidence here during execution.
```

### Gate 5 (Human)

```text
# Record human attestation here before closure.
```

### Value Narrative

Before this OBPI, the new persona surface could exist without becoming part of
the agent contract itself. After this OBPI, the core instruction surface
explicitly requires persona framing in every context frame.

### Key Proof

`rg -n "^## Persona$" AGENTS.md src/gzkit/templates/agents.md src/gzkit/templates/adr.md`

### Implementation Summary

- Files created/modified:
- Tests added:
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

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
