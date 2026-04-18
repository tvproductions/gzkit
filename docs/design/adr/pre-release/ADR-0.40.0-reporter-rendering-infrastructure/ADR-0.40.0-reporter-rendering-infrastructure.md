---
id: ADR-0.40.0-reporter-rendering-infrastructure
status: Pending
semver: 0.40.0
lane: heavy
parent: PRD-GZKIT-1.0.0
date: 2026-03-28
---

<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-0.40.0: Reporter Rendering Infrastructure

## Tidy First Plan

- Prep tidyings (behavior-preserving):
  1. Audit current `OutputFormatter` usage in `cli/formatters.py` — catalog which commands use it vs direct `Console().print()` to understand migration surface.
  1. Catalog all Rich table constructions across `src/gzkit/commands/` — identify common patterns (column sets, box styles, row formatting) to extract into presets.
  1. Review airlineops `reporter/reports/rich_renderers_common.py` — identify portable helper functions (`kv_table()`, `fmt_value()`, `simple_top_table()`) that can be appropriated without domain coupling.

**Date Added:** 2026-03-28
**Date Closed:**
**Status:** Proposed
**SemVer:** 0.40.0
**Area:** CLI Infrastructure — Rendering Layer

## Agent Context Frame — MANDATORY

**Role:** Infrastructure developer extracting a rendering layer from airlineops patterns and wiring it into gzkit's CLI output pipeline.

**Purpose:** When this ADR is complete, all formatted CLI output in gzkit flows through a `reporter/` module that owns table styles, ceremony panels, and format negotiation. Commands produce data; the reporter renders it. No hand-padded box-drawing strings exist anywhere in the codebase.

**Goals:**

- A `reporter/` module with style presets for governance tables, key-value tables, ceremony panels, and list tables
- Common rendering helpers appropriated from airlineops (`kv_table()`, `fmt_value()`, format negotiation)
- All status/report commands migrated from ad-hoc `Console().print()` to reporter-rendered output
- All list commands migrated to use reporter list table presets
- Ceremony outputs (closeout boxes, walkthrough headers) generated deterministically by reporter code, not skill templates

**Critical Constraint:** Implementations MUST keep the reporter module as a pure rendering layer — it owns how things look, not what data exists. OutputFormatter continues to own mode routing (human/json/quiet). Commands produce data dicts; reporter renders them; OutputFormatter routes the output.

**Anti-Pattern Warning:** A failed implementation looks like: the reporter module absorbing business logic — computing gate status, reading ledger state, or making governance decisions. If the reporter knows about ADR lifecycle or OBPI status semantics, it has crossed its boundary. It should accept data and return Rich renderables, nothing more.

**Integration Points:**

- `src/gzkit/cli/formatters.py` — OutputFormatter (mode routing, stays as-is)
- `src/gzkit/commands/status.py` — primary consumer, largest table surface
- `src/gzkit/commands/state.py` — state output tables
- `src/gzkit/commands/common.py` — shared Console instance
- `src/gzkit/commands/task.py`, `chores.py`, `roles.py`, `skills_cmd.py` — list table consumers
- airlineops `src/airlineops/reporter/reports/rich_renderers_common.py` — source for portable helpers

---

## Feature Checklist — Appraisal of Completeness

1. **OBPI-0.40.0-01:** Reporter module scaffold with style presets for four table types (status, key-value, ceremony panel, list) and Rich-based rendering functions
2. **OBPI-0.40.0-02:** Common rendering helpers — `kv_table()`, `fmt_value()`, format negotiation utilities appropriated from airlineops
3. **OBPI-0.40.0-03:** Status and report table migration — wire `gz status`, `gz adr report`, `gz state` through reporter presets
4. **OBPI-0.40.0-04:** List table migration — wire `gz task list`, `gz chores list`, `gz roles`, `gz skill list` through reporter list presets
5. **OBPI-0.40.0-05:** Ceremony panel migration — replace hand-padded skill template boxes with reporter-generated Rich panels

Support obligations for the checklist above:

- External contract changed (Heavy lane): CLI output formatting changes across all commands
- stdlib unittest guards reporter presets, helper functions, and rendered output
- BDD scenarios cover reporter output in status, list, and ceremony contexts
- Docs updated in command docs and runbook to reflect reporter-driven output
- Each numbered ADR checklist item maps to one brief

## Intent

Establish a centralized rendering layer (`src/gzkit/reporter/`) that owns all formatted CLI output — tables, panels, ceremony boxes, and format negotiation. Commands produce data; the reporter renders it deterministically via Rich. This eliminates hand-padded template strings, inconsistent table styling, and ad-hoc Console usage across the codebase.

## Decision

- All formatted CLI output MUST flow through `src/gzkit/reporter/` rendering functions
- Four named style presets: `status_table`, `kv_table`, `ceremony_panel`, `list_table`
- Common helpers (`kv_table()`, `fmt_value()`, `ceremony_box()`) appropriated from airlineops `rich_renderers_common.py` patterns
- OutputFormatter retains mode routing (human/json/quiet); reporter owns rendering
- Commands pass data dicts to reporter functions and receive Rich renderables
- Ceremony skill templates reference reporter functions instead of hand-drawn boxes
- `box.ROUNDED` is the standard table style; `box.DOUBLE` is the ceremony panel style

## Interfaces

- **Module (internal):** `src/gzkit/reporter/` with `__init__.py`, `presets.py`, `helpers.py`, `panels.py`
- **CLI (external contract):** Output appearance changes for all `gz` commands (consistent styling)
- **Skill integration:** Ceremony skills call reporter functions via `uv run gz` or direct import

## OBPI Decomposition — Work Breakdown Structure (Level 1)

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-0.40.0-01 | Reporter module scaffold with four style presets | Heavy | Pending |
| 2 | OBPI-0.40.0-02 | Common rendering helpers from airlineops patterns | Lite | Pending |
| 3 | OBPI-0.40.0-03 | Status/report table migration to reporter | Heavy | Pending |
| 4 | OBPI-0.40.0-04 | List table migration to reporter | Heavy | Pending |
| 5 | OBPI-0.40.0-05 | Ceremony panel migration to reporter | Heavy | Pending |

**Briefs location:** `briefs/OBPI-0.40.0-*.md`

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

---

## Rationale

gzkit's CLI output is currently fragmented: commands construct Rich tables ad-hoc with inconsistent box styles, and ceremony outputs use hand-padded Unicode strings in skill templates. The airlineops reporter system demonstrates that a rendering layer with presets and helpers eliminates alignment bugs, ensures visual consistency, and makes output deterministic. Appropriating the portable rendering patterns (not the full manifest/schema/eligibility infrastructure) gives gzkit a proven foundation without overengineering for a simpler output surface.

## Consequences

- All CLI output has consistent visual styling (box.ROUNDED for tables, box.DOUBLE for ceremony panels)
- Ceremony skill templates become simpler — they call functions instead of embedding box-drawing art
- OutputFormatter's emit_table() can be deprecated in favor of reporter rendering
- Future output formats (markdown export, HTML) have a single point of extension
- Commands that currently use direct Console().print() must be migrated

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `tests/test_reporter.py`
- **BDD (Heavy):** `features/reporter_rendering.feature`
- **Docs:** `docs/user/concepts/reporter-architecture.md`, updated command docs

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note in the brief once Four Gates are green.
- Include the exact command to reproduce the observed behavior, if applicable:

`uv run gz status --table` (rendered via reporter presets)

---

## Evidence Ledger (authoritative summary)

### Provenance

- **Git tag:** `adr-0.40.0`
- **Related issues:** TBD

### Source & Contracts

- CLI / contracts: `src/gzkit/reporter/`
- Core modules: `src/gzkit/commands/**` (migration consumers)
- Existing formatter: `src/gzkit/cli/formatters.py`

### Tests

- Unit: `tests/test_reporter.py`
- BDD: `features/reporter_rendering.feature`, `features/steps/reporter_steps.py`

### Docs

- Concepts: `docs/user/concepts/reporter-architecture.md`
- Command docs: updated for consistent output descriptions

---

## Completion Checklist — Post-Ship Tidy (Human Sign-Off)

| Artifact Path | Class | Validated Behaviors | Evidence | Notes |
|---------------|-------|---------------------|----------|-------|
| src/gzkit/reporter/ | A | Module exists with presets, helpers, panels | Unit tests | |
| src/gzkit/commands/status.py | M | Tables rendered via reporter | BDD + visual | |
| src/gzkit/commands/task.py | M | List tables via reporter | BDD | |
| .gzkit/skills/gz-adr-closeout-ceremony/SKILL.md | M | Ceremony box references reporter function | Visual diff | |
| docs/user/concepts/reporter-architecture.md | A | Architecture documented | mkdocs build | |

### SIGN-OFF — Post-Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes
