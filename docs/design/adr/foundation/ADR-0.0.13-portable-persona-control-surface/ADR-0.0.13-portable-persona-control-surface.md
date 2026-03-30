<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.0.13 — Portable Persona Control Surface

## Tidy First Plan

Behavior-preserving tidyings required before any behavior change:

1. Inventory all GovZero portable primitives (`gz init`, `gz agent sync`,
   manifest schema, control surface matrix) to understand how new surfaces
   are added to the portable set
1. Review how `.gzkit/rules/` and `.gzkit/skills/` are currently synced
   to vendor mirrors (`.claude/`, `.github/`, `.agents/`) to establish the
   pattern persona syncing should follow
1. Catalog persona-like language in airlineops AGENTS.md to understand the
   cross-project starting point

**No external behavior changes occur in this phase.**

STOP / BLOCKERS:

- If ADR-0.0.11 and ADR-0.0.12 are not complete, stop. This ADR depends on
  the control surface definition and concrete profiles from both.
- If the persona schema from ADR-0.0.11 proves insufficient during ADR-0.0.12
  profile writing, stop and revise the schema before making it portable.

**Date Added:** 2026-03-30
**Date Closed:**
**Status:** Draft
**SemVer:** 0.0.13
**Area:** Governance Foundation — Cross-Project Persona Portability
**Lane:** Heavy

## Agent Context Frame — MANDATORY

**Role:** Platform architect making persona frames a portable GovZero primitive
that works across all governed repositories.

**Purpose:** When this ADR is complete, any GovZero-compliant repository can
bootstrap persona frames via `gz init`, sync them to vendor surfaces via
`gz agent sync`, and load them at agent dispatch time — regardless of whether
the project is gzkit, airlineops, or a new repository. Persona is as portable
as rules and skills.

**Goals:**

- `gz init` scaffolds `.gzkit/personas/` with default persona set
- `gz agent sync control-surfaces` syncs personas to vendor mirrors
- Manifest schema includes `control_surfaces.personas` entry
- Persona loading works vendor-neutrally (Claude, Codex, Copilot, OpenCode)
- Persona drift monitoring surface provides observability

**Critical Constraint:** The portable persona surface MUST NOT impose
gzkit-specific content on other projects. The schema and loading mechanism
are portable; the specific persona frames (implementer text, reviewer text)
are project-local customizations. `gz init` provides a default set that
projects override.

**Anti-Pattern Warning:** A failed implementation makes persona frames
tightly coupled to gzkit's agent architecture (e.g., referencing specific
pipeline stages or skill names in the portable schema). The portable layer
must be project-agnostic — it defines **how** personas are stored, loaded,
and composed, not **what** they say.

**Integration Points:**

- `src/gzkit/sync_surfaces.py` — control surface sync (add personas)
- `src/gzkit/commands/init.py` — `gz init` scaffolding
- `.gzkit/manifest.json` — schema update (`control_surfaces.personas`)
- `data/schemas/manifest.schema.json` — manifest JSON schema
- `.gzkit/personas/` — the surface being made portable

---

## Feature Checklist — Appraisal of Completeness

### Checklist

- [ ] Portable persona schema specification (project-agnostic)
- [ ] `gz init` persona scaffolding (default persona set)
- [ ] Manifest schema update (`control_surfaces.personas`)
- [ ] `gz agent sync` persona mirroring to vendor surfaces
- [ ] Vendor-neutral persona loading (Claude, Codex, Copilot adapters)
- [ ] Persona drift monitoring surface (observability)

## Intent

Make persona frames a first-class portable GovZero primitive, enabling any
governed repository to use persona-driven agent identity framing through
standard `gz` tooling. Just as rules sync from `.gzkit/rules/` to vendor
mirrors and skills sync from `.gzkit/skills/`, personas sync from
`.gzkit/personas/` — with the same canonical-source/vendor-mirror pattern.

## Decision

- `.gzkit/personas/` is added to the manifest as a control surface
- `gz init` creates the directory with a default persona set (overridable)
- `gz agent sync control-surfaces` mirrors personas to vendor-specific
  locations (`.claude/personas/`, `.github/personas/`, `.agents/personas/`)
- The persona schema is **project-agnostic** — it defines structure (traits,
  anti-traits, grounding, composition rules) without prescribing content
- Vendor adapters translate persona frames into vendor-specific formats
  (system prompt fragments for Claude, instruction blocks for Codex, etc.)
- A monitoring surface (`gz personas drift`) reports when agent behavior
  diverges from the designed persona profile, using the PSM/Assistant Axis
  research as the theoretical basis for what drift means

## Interfaces

- **CLI (new):**
  - `uv run gz personas list` — enumerate defined personas
  - `uv run gz personas validate` — schema-check all persona files
  - `uv run gz personas drift` — report persona adherence metrics
- **Manifest update:** `control_surfaces.personas: ".gzkit/personas"`
- **Sync targets:**
  - `.claude/personas/` (Claude Code)
  - `.agents/personas/` (Codex)
  - `.github/personas/` (Copilot)

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.0.13-01 | Portable persona schema specification | Lite | Pending |
| 2 | OBPI-0.0.13-02 | `gz init` persona scaffolding with default set | Lite | Pending |
| 3 | OBPI-0.0.13-03 | Manifest schema and `gz agent sync` persona mirroring | Heavy | Pending |
| 4 | OBPI-0.0.13-04 | Vendor-neutral persona loading adapters | Lite | Pending |
| 5 | OBPI-0.0.13-05 | Persona drift monitoring surface (`gz personas drift`) | Heavy | Pending |
| 6 | OBPI-0.0.13-06 | Cross-project validation (apply to airlineops) | Heavy | Pending |

**Briefs location:** `obpis/OBPI-0.0.13-*.md`

## Rationale

### Why Portability Matters

The PSM research applies to all LLM-driven agent work, not just gzkit. Every
project Jeff operates benefits from persona-driven identity framing. Making
personas a portable GovZero primitive means the investment in ADR-0.0.11 and
ADR-0.0.12 pays dividends across the entire portfolio.

### The Existing Pattern

GovZero already has a portable control surface pattern:

| Surface | Canon | Mirrors |
|---|---|---|
| Rules | `.gzkit/rules/` | `.claude/rules/`, `.github/instructions/` |
| Skills | `.gzkit/skills/` | `.claude/skills/`, `.github/skills/`, `.agents/skills/` |
| Schemas | `.gzkit/schemas/` | (not mirrored — consumed directly) |
| **Personas** | **`.gzkit/personas/`** | **`.claude/personas/`, `.github/personas/`, `.agents/personas/`** |

Personas follow the same canon-first, vendor-mirror pattern.

### Vendor Neutrality

Different agent runtimes consume identity context differently:
- **Claude Code:** System prompt + AGENTS.md + rules files
- **Codex:** AGENTS.md + instruction files
- **Copilot:** `.github/copilot-instructions.md` + instruction files
- **OpenCode:** AGENTS.md equivalent

The vendor adapter layer translates the canonical persona format into each
vendor's native mechanism.

### Drift Monitoring

The Assistant Axis paper shows persona position is measurable and persona drift
is predictable based on conversational context. While gzkit cannot directly
measure activation space positions, it can observe behavioral proxies:
- Did the agent follow the persona's trait specifications?
- Did outputs match the expected behavioral pattern?
- Did the agent drift toward anti-trait behaviors?

This observability surface closes the feedback loop: design persona → deploy
persona → monitor adherence → refine persona.

## Consequences

- `gz init` gains persona scaffolding
- `gz agent sync` gains persona mirroring
- Manifest schema grows by one control surface entry
- New CLI commands (`gz personas list/validate/drift`)
- airlineops becomes the first cross-project consumer

## Evidence (Four Gates)

- **ADR:** This document
- **TDD (required):** `tests/test_persona_portability.py`
- **BDD (Heavy lane):** `features/persona_sync.feature` — sync and init
- **Docs:** Governance runbook + command docs for `gz personas`
- **Lineage:** Depends on ADR-0.0.11 + ADR-0.0.12

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---|---|---|---|---|
| `gz init` | M | Creates `.gzkit/personas/` with defaults | Test output | |
| `gz agent sync` | M | Mirrors to vendor surfaces | Sync output | |
| Manifest schema | M | `control_surfaces.personas` entry | Schema check | |
| `gz personas` CLI | P | list/validate/drift commands work | CLI output | |
| airlineops | M | Personas applied and functional | Cross-project test | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
