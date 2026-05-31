---
id: OBPI-0.0.37-14-wire-sync-retire-monolith
parent: ADR-0.0.37-constitutional-invariant-composition
item: 14
lane: Heavy
status: Draft
---

# OBPI-0.0.37-14-wire-sync-retire-monolith: Wire Sync Through the Renderer, Retire the Monolith

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`
- **Checklist Item:** #14 — "OBPI-0.0.37-14 — Wire sync_agents_md through the renderer; retire monolithic template; --invariant-coherence diffs the model render"

**Status:** Draft

## Objective

Make the live surface-generation path render from the master model: repoint
`sync_agents_md` off `render_template("agents")` onto the OBPI-12 temperature renderer at the
default temperature, dissolve the hardcoded `get_project_context` literals into model rows,
retire the monolithic `src/gzkit/templates/agents.md`, and re-point
`gz validate --invariant-coherence` so it diffs the model render against the committed
AGENTS.md (the gate now means "committed surface equals the model render"). This is the step
that delivers zero hand-authored prose at the rendered location.

## Lane

**Heavy** — changes the sync runtime path and a validator contract; highest blast radius
(AGENTS.md generation). Foundation + heavy → Gate 5 human attestation
(`assets/HEAVY_LANE_PLAN_TEMPLATE.md`).

## Allowed Paths

- `src/gzkit/sync_surfaces.py` — repoint `sync_agents_md`; dissolve `get_project_context` literals into model-sourced values
- `src/gzkit/governance/compose.py` — repoint/retire the registry-only renderer in favor of the model renderer
- `src/gzkit/governance/trust_audits/invariant_coherence.py` — diff the model render against committed AGENTS.md
- `src/gzkit/templates/agents.md` — retire the monolithic prose template (becomes a structural shell or is removed)
- `tests/commands/test_sync_cmds.py` — sync-from-model behavior tests
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/obpis/OBPI-0.0.37-14-wire-sync-retire-monolith.md` — this brief
- `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md` — parent ADR (read-only)

## Denied Paths

- Paths not listed in Allowed Paths
- `src/gzkit/content/models/`, `src/gzkit/content/render/`, `src/gzkit/content/parse/` — those are OBPI-11/12/13
- `src/gzkit/content/vendors.py`, `data/vendor-manifest.json` — per-vendor selection is OBPI-15
- New runtime dependencies; CI files; lockfiles

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `sync_agents_md` MUST render AGENTS.md from the master `AgentContract` via the OBPI-12 renderer at the project's default temperature — NEVER via `render_template("agents")`.
2. REQUIREMENT: the hardcoded prose literals in `get_project_context` (`purpose`, `invariants`, and peers) MUST be sourced from the model, not from in-code strings — zero hand-authored prose at the rendered location.
3. REQUIREMENT: `gz validate --invariant-coherence` MUST diff the model render against the committed AGENTS.md and fail closed on drift — it MUST stop being a monolith-re-renders-to-itself check.
4. REQUIREMENT: the monolithic `src/gzkit/templates/agents.md` MUST no longer be the AGENTS.md render source; a hand-edit to a rendered surface MUST fail closed in `gz check`.
5. REQUIREMENT: the rendered AGENTS.md MUST remain semantically equivalent to the pre-migration contract at the default temperature (no silent doctrine loss); any intended change is a separate ADR amendment.
6. NEVER: re-introduce a hand-authored render source for any per-turn surface.

> STOP-on-BLOCKERS: requires OBPI-11/12/13 landed (model, renderer, imported master model). If absent, print BLOCKERS and halt.

## Discovery Checklist

**Parent ADR (read first; order pinned — GHI #321):**

- [ ] **Parent ADR § Decision item (quote verbatim into Implementation Summary):** "OBPI-0.0.37-14 — Wire sync_agents_md through the renderer; retire monolithic template; --invariant-coherence diffs the model render."
- [ ] Parent ADR § "Decision Extension (2026-05-30)" — zero-hand-authored-prose consequence.
- [ ] Parent ADR file: `docs/design/adr/foundation/ADR-0.0.37-constitutional-invariant-composition/ADR-0.0.37-constitutional-invariant-composition.md`

> **STOP:** If you cannot quote the parent ADR § Decision item this OBPI implements, STOP and re-read.

**Governance (read once, cache):**

- [ ] `docs/governance/agent-control-surface-rendering-substrate.md` — Era-1 to Era-2 transition; the binding claim this OBPI makes load-bearing.

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/sync_surfaces.py` exists (`sync_agents_md`, `get_project_context`)
- [ ] `src/gzkit/governance/compose.py` and `src/gzkit/governance/trust_audits/invariant_coherence.py` exist
- [ ] `src/gzkit/templates/agents.md` exists
- [ ] `tests/commands/test_sync_cmds.py` exists
- [ ] OBPI-13 imported master model is available

**Existing Code (understand current state):**

- [ ] `src/gzkit/sync_surfaces.py` — `sync_agents_md` → `render_template("agents", **context)`; `get_project_context` literals
- [ ] `src/gzkit/governance/trust_audits/invariant_coherence.py` — current `render_agents_md` byte-compare

## Quality Gates

### Gate 1: ADR
- [ ] Decision item quoted into Implementation Summary

### Gate 2: TDD (Red-Green-Refactor)
- [ ] Sync-from-model and coherence-diff tests RED before, GREEN after
- [ ] `uv run gz test` passes

### Code Quality
- [ ] `uv run gz lint` and `uv run gz typecheck` clean

### Gate 3: Docs (Heavy)
- [ ] `uv run mkdocs build --strict` clean
- [ ] `docs/user/runbook.md` updated: "to edit AGENTS.md, edit the master model and re-render"

### Gate 4: BDD (Heavy)
- [ ] `features/constitutional_invariants.feature` scenario tagged `@REQ-0.0.37-14-*`

### Gate 5: Human (Heavy + Foundation)
- [ ] Human attestation recorded

## Verification

```bash
uv run gz validate --documents
uv run gz validate --invariant-coherence
uv run gz validate --req-kind-discipline
uv run gz lint
uv run gz typecheck
uv run gz test
uv run -m unittest tests.commands.test_sync_cmds -v
```

## Demo

```bash
uv run python -c "print('edit a bullet in the master model, run gz agent sync, observe AGENTS.md re-rendered from the model')"
```

## Acceptance Criteria

- [ ] REQ-0.0.37-14-01 [BEHAVIOR]: `sync_agents_md` renders AGENTS.md from the master model; `render_template("agents")` is no longer invoked. Proof: `@covers(REQ-0.0.37-14-01)` test in `tests/commands/test_sync_cmds.py`.
- [ ] REQ-0.0.37-14-02 [BEHAVIOR]: the `get_project_context` prose literals are sourced from the model — no hardcoded `purpose`/`invariants` strings remain in the render path. Proof: `@covers(REQ-0.0.37-14-02)` test.
- [ ] REQ-0.0.37-14-03 [BEHAVIOR]: `gz validate --invariant-coherence` fails closed when AGENTS.md diverges from the model render (a hand-edit to AGENTS.md is rejected). Proof: `@covers(REQ-0.0.37-14-03)` test.
- [ ] REQ-0.0.37-14-04 [BEHAVIOR]: rendering the imported master model at the default temperature is semantically equivalent to the pre-migration contract. Proof: `@covers(REQ-0.0.37-14-04)` test.
- [ ] REQ-0.0.37-14-05 [SUPPORT]: the runbook records the new edit path — `uv run gz validate --documents` passes and an `artifact_edited` event is emitted for `docs/user/runbook.md`.

## Completion Checklist

- [ ] **Gate 1 (ADR):** Decision item quoted
- [ ] **Gate 2 (TDD):** RGR followed; tests derive from REQs
- [ ] **Code Quality:** lint, format, typecheck clean
- [ ] **Value Narrative:** documented
- [ ] **Key Proof:** edit-model-then-sync re-renders AGENTS.md
- [ ] **Gate 5:** human attestation recorded

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
# Paste docs-build output here
```

### Gate 4 (BDD)
```text
# Paste behave output here
```

### Gate 5 (Human)
```text
# Record attestation text here
```

### Value Narrative

Before: the live path renders a hardcoded monolith plus in-code literals; `--invariant-coherence`
checks the monolith against itself. After: `sync_agents_md` renders from the master model, the
literals are gone, and the coherence gate means "the committed surface equals the model render."

### Key Proof

Editing a bullet in the master model and running `gz agent sync` re-renders AGENTS.md; a direct
hand-edit to AGENTS.md fails `gz validate --invariant-coherence`.

### Implementation Summary

- Decision item implemented (verbatim): "OBPI-0.0.37-14 — Wire sync_agents_md through the renderer; retire monolithic template; --invariant-coherence diffs the model render."
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
