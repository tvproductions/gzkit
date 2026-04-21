---
id: OBPI-0.0.18-04-epic-grouping
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 4
lane: Lite
status: Completed
---

# OBPI-0.0.18-04-epic-grouping: epic grouping (naming + frontmatter + --epic filter)

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- **Checklist Item:** #4 — "Epic grouping (naming + frontmatter + `--epic` filter)"

**Status:** Draft

## Objective

Formalize epic grouping for pool ADRs via (a) slug-prefix naming convention (`ADR-pool.<epic-slug>-<adr-slug>.md`), (b) an optional `epic:` frontmatter field, and (c) a `--epic <slug>` filter on `gz status` (or `gz adr report`) that groups pool ADRs by epic.

## Lane

**Lite** — the `--epic` flag is a filter on an existing command, non-contract-changing. The frontmatter field is optional; no schema rejection for its presence or absence.

## Allowed Paths

- `docs/user/concepts/adr-taxonomy.md` (or dedicated epic page) — documentation of the naming + frontmatter convention
- `docs/governance/pool-curation.md` (cross-reference epics as a curation tool)
- `src/gzkit/templates/adr-pool.md` (if one exists) — add optional `epic:` hint
- `src/gzkit/commands/status.py` (or wherever `gz status` implements filtering) — `--epic` filter addition
- `src/gzkit/cli/parser_artifacts.py` — register `--epic`
- `tests/commands/test_status.py` — filter behavior
- `docs/user/commands/status.md` — document the flag

## Denied Paths

- Concepts page's core body beyond epic-specific additions (OBPI-01 owns it)
- A dedicated epic-management subcommand tree (e.g. a new top-level ADR verb for creating/listing epics) — explicitly out of scope
- Schema rejection of epic field (advisory only)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: The naming convention `ADR-pool.<epic-slug>-<adr-slug>.md` is documented with examples. Single-word slugs are valid (`ADR-pool.auth-oauth.md`); multi-word slugs use kebab-case within each segment (`ADR-pool.agent-runtime-foundations-policy-cache.md`).
2. REQUIREMENT: The `epic:` frontmatter field is documented as optional and advisory. A pool ADR without `epic:` is valid. A pool ADR with `epic:` that doesn't match the filename-derived epic-slug triggers a warning (not an error) in `gz status`.
3. REQUIREMENT: `gz status --epic <slug>` filters pool ADRs to those with either (a) filename-derived epic-slug matching `<slug>`, OR (b) frontmatter `epic:` matching `<slug>`. Both matches are OR'd so an operator can use either mechanism without strict naming.
4. REQUIREMENT: `gz status --epic <slug>` with no matching pool ADRs exits 0 (not an error — the epic just has no members).
5. REQUIREMENT: Help text on `--epic` documents both the filename-prefix and frontmatter-field paths to matching.
6. REQUIREMENT: `gz status` default behavior is unchanged when `--epic` is not supplied.
7. REQUIREMENT: A test fixture creates three pool ADRs, two in one epic and one in another, and asserts `gz status --epic <slug>` returns exactly the expected subset in the correct grouping.

## Verification

```bash
uv run gz status --help | grep -- --epic
uv run gz status --epic <slug>  # against a fixture
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_status -v
uv run mkdocs build --strict
```

## Discovery Checklist

**Governance (read once, cache):**

- [x] `AGENTS.md` and `CLAUDE.md` — agent operating contract
- [x] Parent ADR for intent and scope

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.18-adr-taxonomy-doctrine/ADR-0.0.18-adr-taxonomy-doctrine.md`
- [x] Sibling OBPIs in ADR-0.0.18 (01 concepts, 02 runbook, 03 pool curation, 05 skill)

**Prerequisites (check existence, STOP if missing):**

- [x] `docs/user/concepts/adr-taxonomy.md` (OBPI-01 owns the pool canonical semantics)
- [x] `docs/governance/pool-curation.md` (OBPI-03 owns curation doctrine)

**Existing Code (understand current state):**

- [x] `src/gzkit/commands/status.py` — `status()` and `_collect_adr_statuses` (filter hook location)
- [x] `src/gzkit/cli/parser_governance.py` — `p_status` parser registration (flag addition site)
- [x] `src/gzkit/commands/common.py` — `_is_pool_adr_id`, `ADR_POOL_ID_RE` (pool detection, reuse)
- [x] `src/gzkit/core/validation_rules.py` — `parse_frontmatter` (YAML extraction, reuse)
- [x] `tests/commands/test_status.py` — pool-ADR fixture pattern at `test_status_json_pool_adr_ignores_attestation_for_lifecycle`

## Quality Gates

### Gate 1: ADR

- [x] Intent and scope recorded in this brief
- [x] Parent ADR checklist item quoted (item #4: "Epic grouping (naming + frontmatter + `--epic` filter)")

### Gate 2: TDD

- [x] 6 `@covers`-decorated unittests added covering 7 REQs
- [x] RED→GREEN observed per increment
- [x] `uv run gz arb ruff` exit 0
- [x] `uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_status -q` exit 0
- [x] `uv run gz covers OBPI-0.0.18-04 --json` total=7 covered=7 uncovered=0

### Gate 3: Docs

- [x] `uv run gz arb step --name mkdocs -- uv run mkdocs build --strict` exit 0
- [x] `docs/user/commands/status.md` updated with `--epic SLUG` flag and examples
- [x] `docs/user/concepts/adr-taxonomy.md` — "Epic grouping (optional)" subsection under Pool
- [x] `docs/governance/pool-curation.md` — "Epic grouping" browsing-aid subsection with taxonomy cross-link

## Acceptance Criteria

<!--
Each checkbox carries a deterministic REQ ID:
REQ-<semver>-<obpi_item>-<criterion_index>
-->

- [x] REQ-0.0.18-04-01: The naming convention `ADR-pool.<epic-slug>-<adr-slug>.md` is documented with single-token and multi-token examples in `docs/user/concepts/adr-taxonomy.md` and `docs/governance/pool-curation.md`.
- [x] REQ-0.0.18-04-02: The optional `epic:` frontmatter field is documented as advisory. A pool ADR with `epic:` that disagrees with the filename-derived epic-slug triggers a non-error warning in `gz status --epic <slug>` output.
- [x] REQ-0.0.18-04-03: `gz status --epic <slug>` matches pool ADRs on EITHER the filename-derived epic-slug OR the frontmatter `epic:` field (OR semantics).
- [x] REQ-0.0.18-04-04: `gz status --epic <slug>` with no matching pool ADRs exits 0 and emits an empty `adrs` map (not an error condition).
- [x] REQ-0.0.18-04-05: `gz status --help` documents `--epic` with reference to both the filename-prefix and frontmatter-field matching paths.
- [x] REQ-0.0.18-04-06: `gz status` default output (without `--epic`) is byte-structurally identical to pre-change behavior.
- [x] REQ-0.0.18-04-07: A test fixture with at least three pool ADRs across two epics asserts `gz status --epic <slug>` returns exactly the expected subset.

## Evidence

- Help output showing `--epic` registered
- Fixture-based filter test output
- mkdocs receipt
- ARB receipts

### Implementation Summary


- Flag registration: added `--epic SLUG` to the `gz status` parser in `src/gzkit/cli/parser_governance.py`; threaded `epic=a.epic` into the handler dispatch.
- Filter core: authored `_filename_derived_epic` (first-hyphen-token rule after the `ADR-pool.` prefix) and `_filter_adrs_by_epic` (OR'd match across filename-derived and frontmatter-derived epic-slugs, with advisory-warning accumulation on mismatch) in `src/gzkit/commands/status.py`.
- Signature widening: `status()` grew an `epic: str | None = None` parameter; JSON output gained a `warnings: []` top-level key (only populated when `--epic` is set); human output routes warnings to stderr as yellow advisory lines; empty-result branch exits 0 with a "No pool ADRs match epic" message.
- Frontmatter reading: reused `parse_frontmatter` from `src/gzkit/core/validation_rules.py` — pool ADRs do not validate through `AdrFrontmatter` (which requires `semver` and `kind`), so raw YAML extraction is the correct surface.
- Tests: `TestStatusEpicFilter` in `tests/commands/test_status.py` — 6 `@covers`-decorated methods pinning REQ-01 through REQ-07 (REQ-02 and REQ-03 each covered by 2 methods). `gz covers OBPI-0.0.18-04 --json` reports total=7, covered=7, uncovered=0.
- Docs: `docs/user/commands/status.md` (usage line, dedicated `--epic SLUG` behavior subsection, examples); `docs/user/concepts/adr-taxonomy.md` ("Epic grouping (optional)" subsection under Pool with single-token/multi-token guidance); `docs/governance/pool-curation.md` ("Epic grouping (optional browsing aid)" subsection with taxonomy cross-link). `mkdocs build --strict` exit 0 in 2.06s.
- Brief-readiness (Invariants 2/4 in-flight fix): added Discovery Checklist, Quality Gates, and Acceptance Criteria sections to this brief so `gz obpi precomplete` passes the authored-readiness check — sibling OBPI-03 carries the same shape.

### Key Proof


```
$ uv run gz status --epic vendor --json
{
  "mode": "heavy",
  "adrs": {
    "ADR-pool.vendor-alignment-claude-code": {...},
    "ADR-pool.vendor-alignment-codex": {...},
    "ADR-pool.vendor-alignment-copilot": {...},
    "ADR-pool.vendor-alignment-gemini-cli": {...},
    "ADR-pool.vendor-alignment-opencode": {...},
    "ADR-pool.vendor-scoped-chores": {...}
  },
  "pending_attestations": [...],
  "warnings": []
}
```

Six `ADR-pool.vendor-*` entries filtered from the ~70-entry pool via the filename-derived path (first-hyphen-token = `vendor`), exit 0, zero advisory warnings — the key operator moment this OBPI was authored to deliver.

## Human Attestation

- Attestor: `Jeffry Babb`
- Attestation: attest completed — 7 FAIL-CLOSED REQs locked by 6 @covers unittests (gz covers total=7 covered=7); filename-derived epic via first-hyphen-token rule; frontmatter path via raw parse_frontmatter (pool ADRs bypass AdrFrontmatter); OR'd match per REQ-03; advisory warning on disagreement per REQ-02; default path preserved via epic=None per REQ-06; live proof 'gz status --epic vendor' returned 6 vendor-* pool ADRs. Receipts: arb-ruff-13952bae24f24b519158b7fabd350b73; arb-step-typecheck-8284fee221ed426daf2877bae67f5a10; arb-step-unittest-276770bd18be4504a382cf76c3f1d9cc; arb-step-mkdocs-4dda09de560c42e095ab21183448a952.
- Date: 2026-04-20

## Completion Checklist

- [x] **Gate 1 (ADR):** Intent recorded in brief; parent ADR checklist item #4 quoted
- [x] **Gate 2 (TDD):** 6 `@covers`-decorated unittests; REQ parity 7/7; ruff + typecheck clean
- [x] **Gate 3 (Docs):** mkdocs strict build passes; three doc surfaces updated
- [x] **Lane-appropriate attestation:** Lite lane — foundation-kind parent ADR walkthrough discipline applied per ADR-0.0.18

## REQ Coverage

- REQ-0.0.18-04-01 through REQ-0.0.18-04-07 (see Acceptance Criteria section)
