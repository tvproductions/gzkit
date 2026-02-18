<!-- markdownlint-disable-file MD013 MD022 MD036 MD040 MD041 -->

# ADR-{semver} — {slug}

<!--
Markdown-lint guard (applies to every ADR)
- MD041: H1 must be the first line.
- MD025/MD002: Only one H1; others start at H2 (##) and nest correctly.
- MD012: One blank line between sections.
- MD029: Ordered lists use "1." style (auto-numbered).
- MD034: No bare URLs — always [label](https://example.com).
- MD040/MD046: Use fenced code blocks only when needed; label them (bash/json/text).
- MD038: No spaces inside `code spans`.
- MD009/MD010: No trailing spaces; soft wrap ≈ 100 chars.
- MD033: Avoid inline HTML except comments like this.
Tables: header separator required; no trailing spaces in cells.
-->

## Tidy First Plan

Describe the behavior‑preserving tidyings to perform before any behavior change. Keep tests green
during this prep phase. List 1–3 small tidyings (e.g., extract small functions, rename for
clarity, delete dead code) and explicitly state that no external behavior changes in this step.

- Prep tidyings (behavior‑preserving):
  1. {tidying #1}
  1. {tidying #2}
  1. {optional}

State how you’ll separate prep → change → polish (commits or annotated steps) and the
STOP/BLOCKERS if high‑friction code is encountered (propose minimal tidyings first; proceed only
after agreement or documented deferral).

**Date Added:** YYYY-MM-DD
**Date Closed:** YYYY-MM-DD <!-- leave blank until acceptance/completion/supersession -->
**Status:** {Pool | Draft | Proposed | Accepted | Completed | Superseded | Abandoned}
**SemVer:** {X.Y.Z}
**Area:** {domain or chapter reference, e.g., GAI²E Ch.7 — Planning Entrypoint}

## Agent Context Frame — MANDATORY

This section establishes the mental model agents must carry through all OBPI execution.
**Populate this section via Q&A during ADR drafting — it is inseparable from ADR creation.**

**Role:** {What type of work is this? e.g., "Migration implementer", "Greenfield feature developer",
"Refactoring architect", "Extension developer integrating with existing system"}

**Purpose:** {What does success look like when this ADR is complete? Describe the end state, not the
activities. e.g., "All datasets accessible through unified port interface" not "Create adapters"}

**Goals:**
- {Observable goal 1 — something testable/verifiable}
- {Observable goal 2}
- {Observable goal 3}

**Critical Constraint:** {The ONE thing that would make implementations WRONG if violated. State as:
"Implementations MUST..." or "Implementations MUST NOT...". This is the constraint that, if ignored,
produces work that passes tests but fails intent.}

**Anti-Pattern Warning:** {What does a FAILED implementation look like? Describe the trap agents
should avoid — even if that trap produces passing tests and high coverage. Be specific about what
"looks right but is wrong."}

**Integration Points:** {What existing code/infrastructure/contracts must new code work with?
List specific paths, modules, or interfaces that implementations must respect or delegate to.
If this is greenfield with no integration points, state "None — greenfield implementation."}

---

## Feature Checklist — Appraisal of Completeness

Use this section to quickly appraise whether the feature/change is complete enough to ship under the
current SemVer line. Keep it short and observable. Check only items that materially apply.

- Scope and surface
  - External contract unchanged (Lite lane) or changed (Heavy lane with BDD + docs)
  - CLI help reflects flags/aliases in scope; legacy aliases rejected if deprecated
- Config & calendars
  - JSON-only inputs (no env toggles) and keys documented; no hard-coded paths
  - Period labels align with calendars registry (config/calendars.json helpers used)
- Registry & resolvers
  - `data/data_sources.json` entries consistent; resolver-first policy respected
  - Do not mix `landing_pages` with `resolver` for the same dataset key
- Warehouse & lineage
  - SQLite writes are idempotent (UPSERT where applicable); read-only for report reads
  - All connections and file handles closed explicitly; no ResourceWarnings in tests
  - No new governance ledgers/receipts; reuse ADR‑0.1.4 warehouse‑sync receipt when evidence is needed
- Tests
  - stdlib `unittest` guards core invariants; fast smoke path < 60s
  - BDD only if an external contract changed; otherwise excluded
  - Tests are quiet (capture stdout/err; no noisy progress output)
- Docs
  - User guide/tutorial updated if behavior changed; links/anchors validated
  - ADR Evidence updated with exact commands and expected outputs
- Ops ergonomics
  - Representative CLI shown with `python -m airlineops ...`; deterministic, reproducible
  - Failure modes documented (inputs missing, permissions, timeouts) with user-facing errors
- OBPI mapping
  - Each numbered ADR checklist item maps to one brief; acceptance recorded in the brief

## Intent

{One short paragraph: the durable product contract or lasting architectural change this ADR establishes. ADRs cover forward-facing contracts or enduring structure only.}

## Decision

- {Testable bullet 1 — observable via CLI/config/artifact}
- {Testable bullet 2 — observable via CLI/config/artifact}
- {Inputs/outputs are config-driven; no hard-coded paths}
- {Each planning box consumes only the knobs it needs (separation of concerns)}

## Interfaces

- **CLI (external contract):** `python -m airlineops {subcommand} {flags}`
  - Flags in scope: {list of supported flags for this ADR}
- **Config keys consumed (read-only):** {module.keys → consumers, e.g., airline.network.regions → route}
- **Exchange/Schemas (if any):** {spec paths or references}

## OBPI Decomposition — Work Breakdown Structure (Level 1)

The Decision above is decomposed into a **Work Breakdown Structure (WBS)** via OBPI briefs.
This table is the **Level 1 WBS** — the authoritative list of deliverable work items for this ADR.

> **OBPI Etymology:** "One Brief Per Item" — where the "Item" is the OBPI entry itself (recursive).
> The OBPI table defines what work exists; each brief (Level 2 WBS) elaborates how to deliver it.
> This self-referential structure ensures the WBS is exhaustive and the brief set is complete.

Each OBPI elaborates intent, specifies acceptance criteria, and tracks execution.
The Completion Checklist is substantiated by OBPI fulfillment.

| # | OBPI | Specification Summary | Lane | Status |
|---|------|----------------------|------|--------|
| 1 | OBPI-{semver}-01 | {one-line delivery spec} | Lite/Heavy | Pending |
| 2 | OBPI-{semver}-02 | {one-line delivery spec} | Lite/Heavy | Pending |
| 3 | OBPI-{semver}-03 | {one-line delivery spec} | Lite/Heavy | Pending |

**Briefs location:** `briefs/OBPI-{semver}-*.md` (each brief is a **Level 2 WBS** element)

**WBS Completeness Rule:** Every row in this table MUST have a corresponding brief file.
The brief elaborates the "how" while this table defines the "what."

**Lane definitions:**

- **Lite** — Internal change only; Gates 1-2 required (ADR + TDD)
- **Heavy** — External contract changed; Gates 1-4 required (ADR + TDD + Docs + BDD)

---

## Rationale

{Why this is necessary; how it advances the product; how it aligns with doctrine (e.g., GAI²E/Barnhart/Tillmann).}

## Consequences

- {Single source of truth established by this ADR}
- {Items deprecated or archived as a result}
- {Operational or documentation impacts}

## Evidence (Four Gates)

- **ADR:** this document
- **TDD (required):** `{tests/...}`
- **BDD (only if an external contract changed):** `{features/...}`, `{features/steps/...}`
- **Docs:** `{docs/tutorials/{slug}_walkthrough.md}` (links/navigation validated)
- **Lineage:** Changes touching lineage-scoped files (tests, features, steps, scripts, non-ADR docs) must include lineage markers; see lineage-guard.

---

## OBPI Acceptance Note (Human Acknowledgment)

- Each ADR checklist item maps to one brief (OBPI). Record a one-line acceptance note in the brief once Four Gates are green.
- Include the exact command to reproduce the observed behavior, if applicable:

`python -m airlineops {subcommand} {flags or --workspace {uri}}`

---

## Evidence Ledger (authoritative summary)

> List **every artifact created or modified** to deliver and accept this ADR. If it wasn’t listed here, it didn’t happen.

### Provenance

- **Git tag:** `adr-{semver}`
- **Related issues:** `{#...}`

### Inputs & Config

- Workspace or module pointers: `{workspace config (JSON) or URIs}`
- Data source keys (must align with `data/data_sources.json`): `{list}`
- Models / Ops keys touched: `{keys}`

### Source & Contracts

- CLI / contracts: `src/airlineops/cli/{module}.py`
- Core modules: `src/airlineops/{area}/**`
- Schemas/specs: `{paths}`

### Tests

- Unit: `tests/adr/test_{slug}.py`
- BDD (only if contract changed): `features/{slug}.feature`, `features/steps/{slug}_steps.py`

### Docs

- Tutorials: `docs/tutorials/{slug}_walkthrough.md`
- Concepts/Governance: `docs/concepts/*.md`, `docs/governance/*.md`

### Scripts & Guards

- `scripts/*.py`, `uv run gz {cmd}`

### Outputs (human-observed)

- Base / URI (from output config): `{uri}`
- Example paths: `{pattern}`

### Summary Deltas (git window)

- Added: `{N}`
- Modified: `{N}`
- Removed: `{N}`
- Notes: `{1–3 bullets}`

---

## Completion Checklist — Post-Ship Tidy (Human Sign‑Off)

| Artifact Path | Class | Validated Behaviors (observable, reproducible) | Evidence (link/snippet/hash) | Notes |
| ---------------------------------- | ----- | ---------------------------------------------------------- | ---------------------------- | ----- |
| pyproject.toml | M | Version set to {X.Y.Z} | Diff link | |
| README.md | M | Badges/text show {X.Y.Z}; links resolve | Rendered README | |
| RELEASE_NOTES.md | M | {X.Y.Z} acceptance + validation proof recorded | Commit link | |
| docs/version_registry.md | P | Entry added: {X.Y.Z}, date, purpose | Rendered docs link | |
| docs/index.md (or landing page) | M | Banner/note: Current version {X.Y.Z} | Site screenshot / URL | |
| archive/releases/**/* | P | Premature 1.x notes archived with “superseded” rationale | PR link | |
| mkdocs.yml | M | Nav exposes {X.Y.Z} notes; Archive section present | Rendered docs link | |
| docs/design/adr/_TEMPLATES/ADR_TEMPLATE_SEMVER.md | M | Template path confirmed; referenced in governance docs | Rendered docs link | |

### SIGN-OFF — Post‑Ship Tidy

Human Approver: ___________________________

Date: _________________________

Decision: Accept | Request Changes

If “Request Changes,” required fixes:

1. …

1. …
