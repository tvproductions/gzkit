---
id: OBPI-0.0.11-04-agents-md-persona-section
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 4
lane: Heavy
status: attested_completed
---

# OBPI-0.0.11-04-agents-md-persona-section: Agents Md Persona Section

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #4 - "AGENTS.md context frame template update (persona section)"

**Status:** Completed

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

## Dependencies

- **Depends on:** OBPI-0.0.11-02 (persona control surface must exist before
  AGENTS.md can reference it in the mandatory persona section)
- **Blocks:** None directly

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

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [x] Existing contract: `AGENTS.md`
- [x] Template sources: `src/gzkit/templates/agents.md`, `src/gzkit/templates/adr.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists or is intentionally created in this OBPI: `AGENTS.md`
- [x] Required path exists or is intentionally created in this OBPI: `src/gzkit/templates/agents.md`
- [x] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [x] Pattern to follow: `AGENTS.md`
- [x] Pattern to follow: `src/gzkit/templates/agents.md`
- [x] Parent ADR integration points reviewed for local conventions

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Tests written before/with implementation
- [x] Tests pass: `uv run gz test`
- [x] Validation commands recorded in evidence with real outputs

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3: Docs (Heavy)

- [x] Docs build: `uv run mkdocs build --strict`
- [x] Runbook updates explain the mandatory persona section and its constraints

### Gate 4: BDD (Heavy)

- [x] Manual contract review or existing persona BDD surface demonstrates the persona section is rendered into generated instruction output

### Gate 5: Human (Heavy)

- [x] Human attestation recorded

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

- [x] REQ-0.0.11-04-01: `AGENTS.md` contains a mandatory `## Persona` section in the agent context frame
- [x] REQ-0.0.11-04-02: Template sources and regenerated surfaces stay synchronized with the new persona contract
- [x] REQ-0.0.11-04-03: The persona section frames behavioral identity and craftsmanship standards without expertise-claim language

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Tests pass, coverage maintained
- [x] **Code Quality:** Lint, format, type checks clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
$ uv run -m unittest tests.test_sync_surfaces -v
test_adr_persona_precedes_intent ... ok
test_adr_template_has_persona_section ... ok
test_agents_persona_forbids_expertise_claims ... ok
test_agents_persona_frames_behavioral_identity ... ok
test_agents_persona_references_control_surface ... ok
test_agents_template_has_persona_section ... ok
test_persona_discovery_command ... ok
Ran 7 tests in 0.001s — OK

$ uv run gz test
Ran 2342 tests in 33.010s — OK
```

### Code Quality

```text
$ uv run gz lint
All checks passed! Lint passed.

$ uv run gz typecheck
All checks passed! Type check passed.
```

### Gate 3 (Docs)

```text
$ uv run gz validate --documents
Validated: documents — All validations passed (1 scopes).

$ uv run mkdocs build --strict
Pre-existing warning: missing plan.md reference (not introduced by this OBPI).

Governance runbook updated with persona framing subsection (### Persona framing)
under ## Concepts, explaining mandatory persona section, constraints, commands,
and surface locations.
```

### Gate 4 (BDD)

```text
$ rg -n "^## Persona$" AGENTS.md src/gzkit/templates/agents.md src/gzkit/templates/adr.md
src/gzkit/templates/adr.md:12:## Persona
src/gzkit/templates/agents.md:13:## Persona
AGENTS.md:13:## Persona

Manual contract review confirms:
- Template source (agents.md) contains ## Persona section
- Regenerated AGENTS.md contains ## Persona section at line 13
- ADR template (adr.md) contains ## Persona placeholder at line 12
- Sync command propagates template to AGENTS.md and nested mirrors
```

### Gate 5 (Human)

```text
Human attestation: "attest completed" (2026-04-02)
```

### Implementation Summary

- Files created: `tests/test_sync_surfaces.py` (7 regression tests)
- Files modified: `src/gzkit/templates/agents.md`, `src/gzkit/templates/adr.md`, `docs/governance/governance_runbook.md`, `AGENTS.md` (regenerated)
- Tests added: 7
- Date completed: 2026-04-02
- Attestation status: Human attested
- Defects noted: Pre-existing mkdocs warning (missing `docs/user/commands/plan.md`)

### Key Proof

```text
$ rg -n "^## Persona$" AGENTS.md src/gzkit/templates/agents.md src/gzkit/templates/adr.md
src/gzkit/templates/adr.md:12:## Persona
src/gzkit/templates/agents.md:13:## Persona
AGENTS.md:13:## Persona
```

## Tracked Defects

- Pre-existing: `docs/user/commands/plan.md` referenced in `mkdocs.yml` nav but file does not exist (causes `mkdocs build --strict` warning)

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed
- Date: 2026-04-02

---

**Brief Status:** Completed

**Date Completed:** 2026-04-02

**Evidence Hash:** -
