# OBPI-0.0.18-04-epic-grouping — Implementation Plan

## Context

ADR-0.0.18 (ADR Taxonomy Doctrine) formalizes the `pool`/`foundation`/`feature` kind axis. Pool ADRs currently share a flat namespace (`docs/design/adr/pool/*.md`) with ~70 entries and no grouping mechanism — operators reviewing the pool cannot filter or browse by theme. Related pool entries (e.g. the four `vendor-alignment-*` ADRs) are only grouped by operator reading of the filename prefix.

This OBPI adds a lightweight, additive **epic** grouping: a filename convention, an optional `epic:` frontmatter field, and a new `--epic <slug>` filter on `gz status`. No schema rejection, no new CLI verb, no change to non-pool ADRs, no change to default `gz status` output. Lite lane.

## Key Files (with citations)

- **CLI flag registration:** `src/gzkit/cli/parser_governance.py:377-400` — `p_status` parser. Pattern: add `p_status.add_argument("--epic", …)` after line 397 and thread `epic=a.epic` into the lambda at line 399.
- **Status command entrypoint:** `src/gzkit/commands/status.py:231-262` — `status(as_json, show_gates, as_table)` signature widens to accept `epic: str | None`.
- **ADR collection helper:** `src/gzkit/commands/status.py:208-223` — `_collect_adr_statuses()`. Filter is applied post-collection (before sort) so existing enrichment logic is unchanged.
- **Pool ADR detection:** `src/gzkit/commands/common.py:64-66` — reuse `_is_pool_adr_id(adr_id)`.
- **Frontmatter parser:** `src/gzkit/core/validation_rules.py:35` — reuse `parse_frontmatter(content)`. Returns `(dict, body)`. `AdrFrontmatter` (`src/gzkit/core/models.py:19-30`) is NOT usable here because it requires `semver`/`kind` — pool ADRs have neither.
- **ADR pool directory:** `config.paths.adrs / "pool"` — pool files named `ADR-pool.<slug>.md` (see `src/gzkit/commands/common.py:37` `ADR_POOL_ID_RE`).
- **Test fixture precedent:** `tests/commands/test_status.py:1629-1651` — `test_status_json_pool_adr_ignores_attestation_for_lifecycle` is the template for multi-pool-ADR tests.
- **Concept doc:** `docs/user/concepts/adr-taxonomy.md:20-30` — Pool section (epic note appended).
- **Pool curation doc:** `docs/governance/pool-curation.md` — append an "Epic grouping" subsection under curation tools.
- **Command manpage:** `docs/user/commands/status.md:9-11, 52-74, 78-85` — usage line, flag description, examples.

## Design Decisions

### Epic-slug resolution (REQ-1, REQ-2, REQ-3)

The brief's `ADR-pool.<epic-slug>-<adr-slug>.md` format is ambiguous because both segments may themselves be kebab-case. The decision:

- **Filename-derived epic-slug** is `stem[len("ADR-pool."):].split("-", 1)[0]` — the first hyphen-delimited token after the `pool.` prefix. This handles single-word epics mechanically (`ADR-pool.auth-oauth.md` → `auth`). For multi-token epics (e.g. `vendor-alignment`), the operator uses the frontmatter field.
- **Frontmatter `epic:` field** is authoritative when present. `parse_frontmatter()` reads the raw YAML; no schema change required — `AdrFrontmatter.model_config.extra="allow"` already permits additional fields, but pool ADRs don't even use that model. We read the raw frontmatter dict.
- **Match** is OR'd per REQ-3: a pool ADR matches `--epic <slug>` if EITHER its filename-derived epic-slug OR its frontmatter `epic:` equals `<slug>`.
- **Mismatch warning** (REQ-2): when both filename-derived and frontmatter `epic:` exist and disagree, emit a yellow warning to stderr (human output) or populate a top-level `warnings: []` list (JSON output). Warnings never change exit code.

This interpretation is documented in `adr-taxonomy.md` so operators understand the convention.

### Filter semantics

- `--epic <slug>` with matching pool ADRs: render only those pool ADRs; omit all non-pool ADRs.
- `--epic <slug>` with no matches: exit 0 with empty-set messaging (REQ-4). In human mode: `console.print("No pool ADRs match epic '<slug>'.")`. In JSON: `{"adrs": {}, "warnings": [], …}`.
- `--epic` absent: behavior unchanged (REQ-6).

### Help text (REQ-5)

```
--epic SLUG    Filter output to pool ADRs in epic SLUG. Matches either the
               filename prefix (ADR-pool.<SLUG>-…) or the frontmatter
               `epic:` field. Mismatched pairs emit a warning.
```

## Implementation Steps

1. **Add `--epic` flag to parser** — edit `src/gzkit/cli/parser_governance.py:393-400`. Add `p_status.add_argument("--epic", metavar="SLUG", default=None, help=…)` and update the `set_defaults` lambda to pass `epic=a.epic`.

2. **Widen `status()` signature** — edit `src/gzkit/commands/status.py:231`. Add `epic: str | None = None` parameter. Thread it through the rendering branches. Collect warnings into a list before rendering.

3. **Add epic-filter helper** in `src/gzkit/commands/status.py` (new function `_filter_adrs_by_epic(project_root, config, adrs, epic_slug) -> tuple[dict, list[str]]`):
   - If `epic_slug is None`, return `(adrs, [])` unchanged.
   - For each `adr_id`, skip if `not _is_pool_adr_id(adr_id)`.
   - Locate the pool file via `project_root / config.paths.adrs / "pool" / f"{adr_id}.md"`.
   - Read + `parse_frontmatter`. Extract `frontmatter.get("epic")`.
   - Compute filename-derived epic: `adr_id[len("ADR-pool."):].split("-", 1)[0]` if `adr_id` starts with `ADR-pool.` else `None`.
   - Emit warning into the returned list when both exist and differ.
   - Match if `filename_epic == epic_slug or frontmatter_epic == epic_slug`.
   - Return `(filtered_dict, warnings)`.

4. **Wire warnings into output**:
   - JSON mode: add `"warnings": warnings` to top-level result dict.
   - Human/table mode: iterate warnings and `console.print(f"[yellow]warning: {msg}[/yellow]", file=sys.stderr)` — follow existing stderr patterns in the file.

5. **Empty-result handling** (REQ-4): after filtering, if `adrs` is empty AND `epic_slug` was set, print a non-error message (human) or emit `{"adrs": {}, …}` (JSON) with exit 0.

6. **Documentation updates:**
   - `docs/user/commands/status.md`: add `--epic SLUG` to the usage block (line 10), add a Flag section describing it, add `uv run gz status --epic vendor` to the Example block (line 84), and describe the OR-matching semantics in Runtime Behavior.
   - `docs/user/concepts/adr-taxonomy.md`: append a short "Epic grouping (optional)" subsection to the Pool section (~line 30) covering (a) the filename convention, (b) the `epic:` frontmatter field, (c) single-token vs multi-token ambiguity and the frontmatter escape hatch, (d) advisory warning on mismatch.
   - `docs/governance/pool-curation.md`: append an "Epic grouping" subsection under curation tools, cross-linking the taxonomy page and the `gz status --epic` flag.

7. **Tests** (`tests/commands/test_status.py`, following the `test_status_json_pool_adr_ignores_attestation_for_lifecycle` pattern at line 1629):
   - `test_status_epic_filter_matches_filename_prefix` — create `ADR-pool.auth-login.md`, `ADR-pool.auth-oauth.md`, `ADR-pool.billing-invoice.md`; invoke `gz status --epic auth --json`; assert exactly the two `auth-*` pool ADRs returned, `billing-invoice` excluded. Covers REQ-3 (filename path), REQ-7.
   - `test_status_epic_filter_matches_frontmatter_field` — create `ADR-pool.thing.md` with `epic: vendor-alignment` frontmatter; invoke `gz status --epic vendor-alignment --json`; assert it is included. Covers REQ-2, REQ-3 (frontmatter path).
   - `test_status_epic_filter_warns_on_mismatch` — create `ADR-pool.auth-login.md` with `epic: billing` frontmatter; invoke `gz status --epic auth --json`; assert it is included (filename matches) AND `warnings` list contains the mismatch string. Covers REQ-2 (warning).
   - `test_status_epic_filter_empty_result_exits_zero` — invoke `gz status --epic nonexistent`; assert exit 0, empty adrs map. Covers REQ-4.
   - `test_status_epic_filter_help_text` — `gz status --help` output contains `--epic` and references both paths. Covers REQ-5.
   - `test_status_default_behavior_unchanged` — invoke `gz status --json` (no `--epic`); assert output structurally identical to pre-change baseline. Covers REQ-6.

   Each test uses `@covers(REQ-0.0.18-04-0N)` decorator on the test method. Run `uv run gz covers OBPI-0.0.18-04-epic-grouping --json` after authoring to confirm `uncovered_reqs == 0`.

## Reuse — functions/utilities already present

- `_is_pool_adr_id` (`src/gzkit/commands/common.py:64`) — pool detection.
- `parse_frontmatter` (`src/gzkit/core/validation_rules.py:35`) — YAML frontmatter extraction.
- `CliRunner` + `_quick_init` (`tests/commands/common.py`) — test fixtures.
- `add_json_flag`, `add_table_flag` (existing parser helpers) — unchanged.
- `adr_created_event` (`src/gzkit/ledger.py` helpers) — test ledger seeding.

## Verification

```bash
# REQ parity gate (must exit 0)
uv run gz covers OBPI-0.0.18-04-epic-grouping --json

# Help text includes --epic
uv run gz status --help | grep -- --epic

# Standard quality bundle
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_status -v
uv run mkdocs build --strict

# OBPI-scoped test
uv run gz test --obpi OBPI-0.0.18-04-epic-grouping
```

## Out of scope (explicitly)

- New `gz adr epic` verb (Denied Paths)
- Schema rejection of `epic:` field (must remain advisory)
- Promotion-time epic validation
- Non-pool ADR epic support
- Modifying the `AdrFrontmatter` Pydantic model (pool ADRs don't use it)

## Rejected alternatives

- **Add `epic:` to `AdrFrontmatter`**: pool ADRs don't validate through that model anyway; adding the field would be dead code for the Pydantic path and misleading for non-pool ADRs (spec says "pool grouping only").
- **Require `epic:` frontmatter only (no filename convention)**: loses the zero-ceremony filename path for simple single-token epics, which the brief explicitly mandates (REQ-1).
- **Use `.` as epic separator** (`ADR-pool.epic.adr-slug.md`): conflicts with existing ~70 pool ADRs that already use `.` only for the `pool.` prefix; would require migration.
- **Error on filename/frontmatter mismatch**: brief explicitly requires "warning (not an error)" (REQ-2).
- **Split filter logic across multiple helpers**: single `_filter_adrs_by_epic` keeps the filter-plus-warning accumulation atomic and testable in isolation.
