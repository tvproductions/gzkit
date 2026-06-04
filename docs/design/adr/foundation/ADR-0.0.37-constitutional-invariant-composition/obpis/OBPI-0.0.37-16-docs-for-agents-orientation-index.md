---
id: OBPI-0.0.37-16-docs-for-agents-orientation-index
parent: ADR-0.0.37-constitutional-invariant-composition
item: 16
lane: Lite
status: Abandoned
---

# OBPI-0.0.37-16-docs-for-agents-orientation-index: Docs-for-Agents Orientation Index

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #16 — "OBPI-0.0.37-16 — Docs-for-agents orientation index (routable surface→authoritative-model+doctrine map rendered from the same substrate; closes the re-derivation loop)"

**Status:** Draft

## Objective

Add an authoritative, routable **Agent Orientation Index** to the substrate doctrine: a
table mapping each agent-control surface (AGENTS.md, CLAUDE.md, rules, skills, personas) to
its canonical model, its governing doctrine, and the command to load it — with an explicit
"do not re-derive from source" instruction. This is the durable, discoverable answer to the
open-loop finding (an agent re-deriving the rendering architecture from source because
capture is write-only). Mechanical re-injection via the SessionStart orientation is a named
forward-reference.

## Lane

**Lite** — documentation surface; no command/API/schema/runtime-contract change. Brief-level
human attestation still applies (ADR-0.0.36 universal attestation).

## Allowed Paths

- `docs/governance/agent-control-surface-rendering-substrate.md` — add the "Agent Orientation Index" section
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-16-docs-for-agents-orientation-index.md` — this brief
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- `AGENTS.md`, `CLAUDE.md`, rendered surfaces — this OBPI documents, it does not render
- `scripts/session_orientation.py` — mechanical re-injection wiring is a forward-reference, not this OBPI
- Source code, schemas; new runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: the orientation index MUST map, per surface, the canonical model, the governing doctrine doc, and the load command, with a "do not re-derive from source" instruction.
2. REQUIREMENT: the index MUST live in the authoritative substrate doctrine (the place an agent reasoning about rendering already lands), not in a new orphan doc.
3. REQUIREMENT: every doc/model/command the index references MUST resolve to an on-disk artifact (no dangling pointers).
4. NEVER: duplicate the doctrine prose into the index — the index is pointers, not a second copy.

> STOP-on-BLOCKERS: requires `docs/governance/agent-control-surface-rendering-substrate.md` present. If absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (quote verbatim into Implementation Summary):** "OBPI-0.0.37-16 — Docs-for-agents orientation index (routable surface→authoritative-model+doctrine map rendered from the same substrate; closes the re-derivation loop)."
- [ ] Parent ADR § "Decision Extension (2026-05-30)" § Open loop named.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` — the host doc and its existing section structure.
- [ ] `.gzkit/insights/agent-insights.jsonl` — the 2026-05-30 open-loop insight this index addresses.

**Prerequisites (check existence, STOP if missing):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` exists
- [ ] The surfaces/models/commands to be indexed exist on disk (AGENTS.md, the content models, `gz content`, `gz governance render`)

**Existing Code (understand current state):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` — current sections, so the index is added coherently
- [ ] `src/gzkit/content/models/agent_contract.py` — the canonical model the index points to

## Quality Gates

### Gate 1: ADR
- [ ] Decision item quoted into Implementation Summary

### Gate 2: TDD / Validation
- [ ] `uv run gz validate --documents` passes (the index links resolve)

### Code Quality
- [ ] Markdown lint clean within the edited doc

### Gate 5: Human (universal)
- [ ] Human attestation recorded (ADR-0.0.36 universal)

## Verification

```bash
uv run gz validate --documents
uv run gz validate --req-kind-discipline
uv run mkdocs build --strict
```

## Demo

```bash
uv run python -c "print('open the substrate doctrine, find the Agent Orientation Index, route to the AgentContract model without reading source')"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-16-01 [SUPPORT]: `docs/governance/agent-control-surface-rendering-substrate.md` gains an "Agent Orientation Index" section mapping surface → model → doctrine → load command — `uv run gz validate --documents` passes and an `artifact_edited` ledger event is emitted for the doc.
- [ ] REQ-0.0.37-16-02 [SUPPORT]: every pointer in the index resolves to an on-disk artifact — `uv run gz validate --documents` passes with no dangling-link finding and the `artifact_edited` event records the change.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision item quoted
- [ ] **Gate 2 (Validation):** `gz validate --documents` green
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** the index routes an agent to the model without source reading
- [ ] **Gate 5:** human attestation recorded

> For ceremony steps and lane-inheritance attestation rules, see `AGENTS.md` section `OBPI Acceptance Protocol`.

## Evidence

### Gate 1 (ADR)
- [ ] Intent and scope recorded

### Gate 2 (Validation)
```text
# Paste gz validate --documents output here
```

### Gate 5 (Human)
```text
# Record attestation text here
```

### Value Narrative

Before: the rendering architecture is documented but nothing routes an agent to it, so each
session re-derives it from source (the open loop, observed and logged 2026-05-30). After: an
authoritative orientation index points each surface to its model, doctrine, and load command —
the durable answer that the handoff is the interim stand-in for.

### Key Proof

An agent reasoning about AGENTS.md rendering finds the index in the substrate doctrine and
loads the `AgentContract` model and doctrine directly, instead of reconstructing from
`sync_surfaces.py` and `compose.py`.

### Implementation Summary

- Decision item implemented (verbatim): "OBPI-0.0.37-16 — Docs-for-agents orientation index (routable surface→authoritative-model+doctrine map rendered from the same substrate; closes the re-derivation loop)."
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

**Date Completed:** -

**Evidence Hash:** -
