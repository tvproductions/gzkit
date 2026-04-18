---
id: OBPI-0.0.11-05-supersede-pool-persona-context
parent: ADR-0.0.11-persona-driven-agent-identity-frames
item: 5
lane: Lite
status: attested_completed
---

# OBPI-0.0.11-05-supersede-pool-persona-context: Supersede Pool Persona Context

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- **Checklist Item:** #5 - "Supersede `ADR-pool.per-command-persona-context`"

**Status:** Completed

## Objective

`ADR-pool.per-command-persona-context` is explicitly superseded, and any useful
cognitive-stance ideas are carried forward into ADR-0.0.11 lineage documents so
the repository no longer has competing active guidance.

## Lane

**Lite** - This OBPI is lineage cleanup and documentation reconciliation. It
does not introduce a new runtime contract by itself.

> Heavy is reserved for command/API/schema/runtime-contract changes. Process,
> documentation, and template-only work stays Lite unless it changes one of
> those external surfaces.

## Dependencies

- **Depends on:** OBPI-0.0.11-01 (research synthesis reviews the pool ADR for
  reusable ideas; supersession is the formal conclusion of that review)
- **Blocks:** None

## Allowed Paths

- `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md` — superseding ADR
- `docs/design/adr/pool/ADR-pool.per-command-persona-context.md` — pool ADR being superseded
- `docs/design/research-persona-selection-agent-identity.md` — design-principle continuity surface
- `docs/governance/governance_runbook.md` — durable operator-facing guidance after supersession

## Denied Paths

- `src/gzkit/**` — implementation work belongs to other OBPIs
- `AGENTS.md` — template integration belongs to OBPI-0.0.11-04
- `.gzkit/personas/` — control-surface implementation belongs to OBPI-0.0.11-02
- Paths not listed in Allowed Paths

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The pool ADR MUST be marked superseded by ADR-0.0.11 with an
   unambiguous lineage statement
1. REQUIREMENT: Reusable ideas from the pool ADR MUST be preserved in ADR-0.0.11
   or linked governance docs rather than lost during supersession
1. REQUIREMENT: Operator-facing docs MUST stop presenting the pool ADR as an
   active design authority
1. NEVER: Leave both the pool ADR and ADR-0.0.11 appearing authoritative for
   persona-context guidance
1. ALWAYS: Preserve a traceable path from the superseded pool idea to the new
   canonical ADR

> STOP-on-BLOCKERS: if the pool ADR contains unresolved design material with no
> destination in ADR-0.0.11, print a BLOCKERS list and halt.

## Discovery Checklist

**Governance (read once, cache):**

- [x] `.github/discovery-index.json` - repo structure
- [x] `AGENTS.md` - agent operating contract
- [x] Parent ADR - understand full context

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md`
- [x] Pool ADR: `docs/design/adr/pool/ADR-pool.per-command-persona-context.md`
- [x] Research handoff doc: `docs/design/research-persona-selection-agent-identity.md`

**Prerequisites (check existence, STOP if missing):**

- [x] Required path exists or is intentionally created in this OBPI: `docs/design/adr/pool/ADR-pool.per-command-persona-context.md`
- [x] Required path exists or is intentionally created in this OBPI: `docs/governance/governance_runbook.md`
- [x] Parent ADR evidence artifacts referenced by this brief are present

**Existing Code (understand current state):**

- [x] Pattern to follow: `docs/design/adr/pool/ADR-pool.per-command-persona-context.md`
- [x] Parent ADR integration points reviewed for local conventions
- [x] Existing references to the pool ADR are searched before closure

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted

### Gate 2: TDD

- [x] Verification commands recorded in evidence with real outputs
- [x] Repository checks stay green: `uv run gz lint`, `uv run gz typecheck`, `uv run gz test`

### Code Quality

- [x] Lint clean: `uv run gz lint`
- [x] Type check clean: `uv run gz typecheck`

### Gate 3 (Docs)

```text
# Not required for Lite lane.
```

### Gate 4 (BDD)

```text
# Not required for Lite lane.
```

### Gate 5 (Human)

```text
# Not required for Lite lane.
```

## Verification

```bash
uv run gz validate --documents
uv run gz lint
uv run gz typecheck
uv run gz test

# Specific verification for this OBPI
test -f docs/design/adr/pool/ADR-pool.per-command-persona-context.md
rg -n "Superseded|supersede" docs/design/adr/pool/ADR-pool.per-command-persona-context.md docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md
rg -n "per-command persona context|cognitive stance" docs/design/adr/foundation/ADR-0.0.11-persona-driven-agent-identity-frames/ADR-0.0.11-persona-driven-agent-identity-frames.md docs/governance/governance_runbook.md
```

## Acceptance Criteria

- [x] REQ-0.0.11-05-01: The pool ADR is explicitly marked superseded by ADR-0.0.11
- [x] REQ-0.0.11-05-02: Any preserved cognitive-stance guidance is rehomed into ADR-0.0.11 lineage docs
- [x] REQ-0.0.11-05-03: Repository-facing guidance no longer presents the pool ADR as an active authority for persona framing

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief
- [x] **Gate 2 (TDD):** Verification commands executed and recorded
- [x] **Code Quality:** Lint and type checks remain clean
- [x] **Value Narrative:** Problem-before vs capability-now is documented
- [x] **Key Proof:** One concrete usage example is included
- [x] **OBPI Acceptance:** Evidence recorded below

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)

- [x] Intent and scope recorded

### Gate 2 (TDD)

```text
uv run gz lint → All checks passed
uv run gz typecheck → All checks passed
uv run gz test → 2342 tests pass
```

### Code Quality

```text
uv run gz lint → All checks passed
uv run gz typecheck → All checks passed
```

### Gate 3 (Docs)

```text
# Not required for Lite lane.
```

### Gate 4 (BDD)

```text
# Not required for Lite lane.
```

### Gate 5 (Human)

```text
# Not required for Lite lane.
```

### Implementation Summary

- Files modified: pool ADR (lineage table, duplicate status fix), research doc (provenance pointer), ADR-0.0.11 (carried-forward concepts in Provenance)
- Tests added: none (Lite docs-only OBPI)
- Date completed: 2026-04-02
- Attestation status: Accepted with note
- Defects noted: OBPI objective was already substantially satisfied before implementation; lineage documentation adds minor traceability value

### Key Proof

```bash
$ rg -n "Superseded|supersede" docs/design/adr/pool/ADR-pool.per-command-persona-context.md
3:status: Superseded
4:superseded_by: ADR-0.0.11-persona-driven-agent-identity-frames
15:Superseded — subsumed into [ADR-0.0.11-persona-driven-agent-identity-frames]...
```

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `jeff`
- Attestation: `Accepted with note: OBPI objective was already substantially satisfied before implementation; lineage documentation adds minor traceability value`
- Date: `2026-04-02`

---

**Brief Status:** Completed

**Date Completed:** 2026-04-02

**Evidence Hash:** -
