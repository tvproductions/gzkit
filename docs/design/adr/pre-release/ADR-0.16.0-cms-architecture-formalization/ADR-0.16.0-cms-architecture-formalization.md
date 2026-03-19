<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.16.0 — cms-architecture-formalization

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Inventory all content types currently managed by gzkit (ADR, OBPI, PRD, Constitution, Rule, Skill, Attestation, Receipt, Closeout)
  1. Map current `gz agent sync control-surfaces` to identify rendering logic already present
  1. Document the current implicit content lifecycle (Pool → Draft → Proposed → Accepted → Completed → Validated) as explicit state machine

State: Prep is audit/documentation commit. Implementation follows per-OBPI.
STOP/BLOCKERS if Pydantic migration (ADR-0.15.0) is not complete — this ADR
depends on Pydantic models being the foundation for all content types.

**Date Added:** 2026-03-15
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.16.0
**Area:** CMS Architecture — Lodestar Architectural Identity

## Agent Context Frame — MANDATORY

**Role:** Architecture implementer — formalizing gzkit's implicit CMS patterns into
explicit, schema-enforced infrastructure following the Django architectural parallel.

**Purpose:** gzkit operates as a headless CMS for governance. When this ADR is complete,
that identity is explicit in code: a content type registry, a template engine for vendor
surface rendering, a manifest-driven vendor enablement system, and a formal content
lifecycle state machine. The Django parallel is not a metaphor — it is the implemented
architecture.

**Goals:**

- Content type registry that catalogs every governance artifact type with its schema, lifecycle, and rendering rules
- Template engine in `gz agent sync control-surfaces` that renders canonical content into vendor-specific shapes
- Vendor manifest schema with selective enablement (`vendors.claude.enabled: true`)
- Rules-as-content pattern: `.gzkit/rules/` as canonical source, vendor surfaces as generated mirrors
- Content lifecycle state machine enforced by Pydantic, recorded in ledger

**Critical Constraint:** Implementations MUST treat `.gzkit/` as the single canonical
source for ALL content. No vendor surface (`.claude/`, `.github/`, `.agents/`) may
contain hand-authored content. Every file in a vendor surface must be traceable to a
canonical source in `.gzkit/` through the template engine. If it is not generated, it
does not belong there.

**Anti-Pattern Warning:** A failed implementation looks like: the template engine exists
but some content still leaks into vendor surfaces directly. Skills are mirrored but rules
are hand-edited in `.claude/rules/`. The manifest declares vendors but `gz agent sync`
still generates surfaces for disabled vendors. The CMS identity is declared in docs but
partially implemented in code — exactly the gap this ADR exists to close.

**Integration Points:**

- `src/gzkit/agent_sync.py` — current sync logic (skill mirroring)
- `.gzkit/manifest.json` — current manifest (needs `vendors` key)
- `.gzkit/skills/` — already canonical; pattern to replicate for rules
- `src/gzkit/validate.py` — surface validation
- `src/gzkit/ledger.py` — lifecycle event recording

---

## Feature Checklist — Appraisal of Completeness

- Scope and surface
  - External contract: `gz agent sync control-surfaces` gains vendor-awareness (Heavy candidate, but CLI flags unchanged so Lite)
  - Internal: content type registry, template engine, lifecycle state machine
- Config and schemas
  - `.gzkit/manifest.json` extended with `vendors` section
  - Manifest schema updated with vendor enablement
  - All new config Pydantic-enforced (depends on ADR-0.15.0)
- Tests
  - Content type registry: tests for registration, lookup, schema association
  - Template engine: tests for rendering canonical → vendor shapes
  - Vendor enablement: tests for selective generation
  - Lifecycle state machine: tests for valid/invalid transitions
- OBPI mapping
  - Each numbered checklist item maps to one brief

## Intent

Formalize gzkit's identity as a headless CMS for governance by implementing the
Django-parallel architecture declared in the lodestar. Content types get a registry.
Canonical content gets a template engine for vendor rendering. Vendor enablement becomes
manifest-driven and selective. Content lifecycle becomes an explicit state machine.
The result is a system where `.gzkit/` is the database, `gz agent sync` is the template
renderer, and vendor surfaces are the rendered frontend — never edited, always generated,
always schema-enforced.

## Decision

- Implement a content type registry: each governance artifact type (ADR, OBPI, PRD, Rule, Skill, etc.) is registered with its Pydantic model, JSON schema, lifecycle states, and rendering rules
- Implement `.gzkit/rules/` as canonical content: vendor-neutral rule definitions with metadata (path scope, description), rendered into vendor-specific formats by `gz agent sync`
- Extend `.gzkit/manifest.json` with a `vendors` section: each vendor (claude, copilot, codex, gemini, opencode) has `enabled: bool` and vendor-specific rendering config
- Make `gz agent sync control-surfaces` vendor-aware: generate mirrors only for enabled vendors, using content type rendering rules
- Implement content lifecycle as an explicit state machine: Pydantic-enforced transitions, ledger-recorded, no invalid state changes

## Interfaces

- **CLI (external contract):** `gz agent sync control-surfaces` — no flag changes, but now vendor-aware
- **Config keys consumed:** `.gzkit/manifest.json` — new `vendors` section
- **New canonical paths:** `.gzkit/rules/` — vendor-neutral rule definitions

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.16.0-01-content-type-registry | Formal registry of all governance content types with Pydantic models, schemas, lifecycle rules | Lite | Completed |
| 2 | OBPI-0.16.0-02-rules-as-content | Implement .gzkit/rules/ as canonical content; define vendor-neutral rule format | Lite | Completed |
| 3 | OBPI-0.16.0-03-vendor-manifest-schema | Extend manifest.json with vendors section; Pydantic model for vendor enablement | Lite | Pending |
| 4 | OBPI-0.16.0-04-template-engine | Make gz agent sync vendor-aware; render canonical content to enabled vendor shapes | Lite | Pending |
| 5 | OBPI-0.16.0-05-content-lifecycle-state-machine | Explicit Pydantic-enforced lifecycle transitions; ledger-recorded state changes | Lite | Pending |

**Briefs location:** `briefs/OBPI-0.16.0-*.md`

**WBS Completeness Rule:** Every row in this table has a corresponding brief file.

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)

---

## Rationale

The lodestar declares gzkit is a headless CMS for governance with a Django-parallel
architecture. The current implementation has the right instincts — skills are already
mirrored from `.gzkit/skills/` to vendor surfaces, the manifest exists, the ledger
records events — but the CMS patterns are implicit and incomplete:

- No content type registry — types are scattered across modules
- No rules-as-content — `.github/instructions/` are hand-authored, not generated
- No vendor enablement — `gz agent sync` generates all surfaces regardless
- No formal lifecycle state machine — transitions are ad-hoc

This ADR makes the implicit explicit. After implementation, gzkit is a CMS in code,
not just in documentation. The Django parallel is structural: models define truth
(Pydantic from ADR-0.15.0), the template engine renders views (`gz agent sync`),
you never edit rendered output (vendor surfaces).

## Consequences

- `.gzkit/rules/` becomes a new canonical directory (alongside `.gzkit/skills/`)
- `.gzkit/manifest.json` gains a `vendors` section (backward-compatible addition)
- Vendor surfaces not enabled in manifest will not be generated (may remove existing stale mirrors)
- Future content types must register in the content type registry — no ad-hoc artifact creation
- The CMS architecture enables future work: plugin packaging, MCP server, cross-repo governance distribution

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_registry.py`, `tests/test_agent_sync.py`, `tests/test_lifecycle.py`
- **BDD:** not applicable (Lite lane)
- **Docs:** lodestar architectural-identity.md already describes the CMS architecture; code now matches

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note
  in the brief once gates are green.

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.16.0`
- **Inspired by:** Lodestar architectural-identity.md (CMS identity, Django parallel)

### Source and Contracts

- Core modules: `src/gzkit/agent_sync.py`, `src/gzkit/registry.py` (new),
  `src/gzkit/lifecycle.py` (new), `src/gzkit/validate.py`
- Config: `.gzkit/manifest.json`, `.gzkit/rules/`
- Schemas: `src/gzkit/schemas/manifest.json` (updated)

### Tests

- Unit: `tests/test_registry.py`, `tests/test_agent_sync.py`, `tests/test_lifecycle.py`

### Summary Deltas (git window)

- Added: TBD
- Modified: TBD
- Removed: TBD

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|-------------------|----------|-------|
| src/gzkit/registry.py | A | Content type registry with all governance types | Diff link | |
| src/gzkit/lifecycle.py | A | State machine for content lifecycle | Diff link | |
| src/gzkit/agent_sync.py | M | Vendor-aware rendering from canonical content | Diff link | |
| .gzkit/manifest.json | M | vendors section with enablement flags | Diff link | |
| .gzkit/rules/ | A | Canonical rule definitions (vendor-neutral) | Diff link | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If "Request Changes," required fixes:

1. …

1. …

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
| 0.16.0 | Completed | Jeff | 2026-03-19 | completed: Re-attesting with corrected ledger ID resolution; all gates verified passing in this session |
