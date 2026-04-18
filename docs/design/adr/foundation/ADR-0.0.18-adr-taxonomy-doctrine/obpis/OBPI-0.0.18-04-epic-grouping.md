---
id: OBPI-0.0.18-04-epic-grouping
parent: ADR-0.0.18-adr-taxonomy-doctrine
item: 4
lane: Lite
status: Draft
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
- New epic CLI verb (`gz adr epic create`) — explicitly out of scope
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

## Evidence

- Help output showing `--epic` registered
- Fixture-based filter test output
- mkdocs receipt
- ARB receipts

## REQ Coverage

- REQ-0.0.18-04-01 through REQ-0.0.18-04-07
