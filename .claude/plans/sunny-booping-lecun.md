# Plan: OBPI-0.0.17-02 — `--kind` flag on `gz plan create`

## Context

OBPI-0.0.17-01 locked the ADR taxonomy schema: `kind: Literal["foundation", "feature"]` in `src/gzkit/core/models.py:28`, enum in `src/gzkit/schemas/adr.json`, pool ADRs carry no `kind:` (their kind is derived from the `ADR-pool.*` id prefix). OBPI-0.0.17-02 now wires the scaffolder (`gz plan create`) to require `--kind {pool, foundation, feature}` explicitly and route output per taxonomy.

**Why this matters now:** Without this, human authors keep the typed taxonomy, but agents can still scaffold mismatched `kind`/`semver` combinations (e.g. `ADR-0.5.0` declared as `foundation`, or a pool item promoted into the feature tree). REQs 2/3/6 mechanically close that class of failure by validating before any file or ledger write.

## Scope notes (flag at ceremony)

1. **Brief allowed-paths drift:** Brief lists `src/gzkit/cli/parser_artifacts.py`. Actual parser registration for `plan create` lives in `src/gzkit/cli/parser_governance.py:233-318`. Proceeding with real file; will reconcile brief allowed-paths in OBPI evidence section.
2. **Scope expansion — new template:** Pool ADR frontmatter is structurally different (no `semver`, no `kind`, no `date`; adds `enabler`, `inspired_by`). The single shared `src/gzkit/templates/adr.md` cannot cleanly emit both shapes via `str.format_map`. Adding `src/gzkit/templates/adr_pool.md` (additive, not a contract break). Justified under Prime Directive Invariant 4 ("scope expansion is not scope creep") — required to implement REQ-4 correctly.

## Critical files

| File | Change |
|------|--------|
| `src/gzkit/cli/parser_governance.py:233-318` | Register `--kind` (required, choices). Plumb through lambda kwargs. |
| `src/gzkit/commands/plan.py:11-112` | Add `kind` param; validate-before-write; route output dir; render via taxonomy-appropriate template. |
| `src/gzkit/templates/adr.md:1-8` | Insert `kind: {kind}` between `status:` and `semver:` (REQ-5). |
| `src/gzkit/templates/adr_pool.md` | **New.** Pool-shaped frontmatter + body stub (mirrors existing pool ADRs). |
| `tests/commands/test_plan.py` | Update existing tests for new required flag; add REQ-level `@covers`-decorated tests. |
| `docs/user/commands/plan-create.md` | Document `--kind` in Options table + add examples per kind. |

Reuse: `gzkit.ledger.adr_created_event` (line 7), `gzkit.templates.render_template` (line 8), `SafeDict` substitution in `src/gzkit/templates/__init__.py:30-61`.

## Implementation steps (Red-Green-Refactor per REQ)

### Step 1 — REQ-1: `--kind` registered and required

**Red:** `tests/commands/test_plan.py` — add `test_plan_create_requires_kind_flag`: invoke `plan create name --semver 0.1.0` (no `--kind`). Assert exit code ≠ 0 and stderr contains both "foundation" and "feature" (REQ-1 recovery).
**Green:** Add to `parser_governance.py` at line 297 (before `add_dry_run_flag`):
```python
p_plan_create.add_argument(
    "--kind",
    choices=["pool", "foundation", "feature"],
    required=True,
    help="ADR taxonomy (required): pool|foundation|feature",
)
```
Plumb `kind=a.kind` into the `_lazy("plan_cmd")` lambda kwargs (lines 299-317).

### Step 2 — REQ-2: foundation semver gate

**Red:** `test_plan_create_foundation_rejects_non_0_0_x_semver`: invoke `plan create x --kind foundation --semver 0.5.0 --dry-run`. Assert exit 1, stderr names next available `0.0.x` (e.g., "0.0.20"), no file written.
**Green:** In `plan_cmd` (plan.py) immediately after `config`/`project_root` resolution (~line 32), validate:
- If `kind == "foundation"` and `semver` fails `^0\.0\.\d+$`, scan `{config.paths.adrs}/foundation/` for registered `ADR-0.0.N-*` dirs, compute `max(N)+1`, print recovery to stderr (`console.print(..., style="red", err=True)` via rich console writing to stderr), `sys.exit(1)` **before** any template render, file write, or ledger append.

### Step 3 — REQ-3: feature semver gate

**Red:** `test_plan_create_feature_rejects_0_0_x_semver`: `plan create x --kind feature --semver 0.0.50 --dry-run`. Assert exit 1, stderr explains "feature ADRs carry release-carrying semver (0.y.z and up)", no file.
**Green:** Same validation block. If `kind == "feature"` and `semver` matches `^0\.0\.\d+$`, print recovery and exit 1.

### Step 4 — REQ-4 + REQ-7: kind-aware routing

**Red (paired tests):**
- `test_plan_create_foundation_routes_to_foundation_dir_per_adr_folder`: assert output at `design/adr/foundation/ADR-0.0.20-x/ADR-0.0.20-x.md`.
- `test_plan_create_feature_routes_to_pre_release_dir_per_adr_folder`: assert output at `design/adr/pre-release/ADR-0.5.0-x/ADR-0.5.0-x.md`.
- `test_plan_create_pool_routes_to_flat_pool_file_without_kind_field`: assert output at `design/adr/pool/ADR-pool.x.md`, frontmatter contains `status: Pool`, does NOT contain `kind:` or `semver:`.

**Green:** Replace `plan.py:76-77` with:
```python
adr_root = project_root / config.paths.adrs
if kind == "pool":
    adr_dir = adr_root / "pool"
    slug = name if name.startswith("ADR-pool.") else f"ADR-pool.{name}"
    adr_file = adr_dir / f"{slug}.md"
    adr_id = slug  # override earlier-computed ADR-<semver>
elif kind == "foundation":
    adr_dir = adr_root / "foundation" / adr_id
    adr_file = adr_dir / f"{adr_id}.md"
else:  # feature
    adr_dir = adr_root / "pre-release" / adr_id
    adr_file = adr_dir / f"{adr_id}.md"
```
For pool, route template to `render_template("adr_pool", ...)`; for others, `render_template("adr", ..., kind=kind)`.

### Step 5 — REQ-5: template emits `kind` after `status`

**Red:** `test_plan_create_foundation_template_places_kind_after_status`: scaffold foundation ADR, read file, assert line with `kind: foundation` appears immediately after `status: Draft` line (not anywhere).
**Green:** Edit `src/gzkit/templates/adr.md:1-8` — insert `kind: {kind}` between line 3 (`status: {status}`) and line 4 (`semver: {semver}`). Final order: id → status → kind → semver → lane → parent → date.

### Step 6 — pool template

**Red:** Covered by `test_plan_create_pool_routes_to_flat_pool_file_without_kind_field` above (asserts no `kind:` / no `semver:` / has `status: Pool`).
**Green:** Create `src/gzkit/templates/adr_pool.md` modeled on `docs/design/adr/pool/ADR-pool.agent-reliability-framework.md` frontmatter shape:
```
---
id: {id}
status: Pool
parent: {parent}
lane: {lane}
enabler: null
---

# {id}: {title}

## Status

Pool

## Intent

{intent}
```
Keep body minimal — pool ADRs are stubs that get promoted into foundation/feature via `gz adr promote` (OBPI-0.0.17-03, out of scope here).

### Step 7 — REQ-6: validate-before-write atomicity

**Red:** `test_plan_create_rejection_writes_no_file_no_ledger_event`: invoke with invalid kind/semver combo, assert no file under `design/adr/**`, ledger contains no `adr_created` event for that id.
**Green:** Already satisfied by Steps 2/3 performing `sys.exit(1)` before `render_template()`, `adr_file.write_text()`, and `ledger.append()`. This step is a confirmation test, not a separate code change — but the test is still REQ-6's mechanical check.

### Step 8 — REQ-8: existing behavior preserved

**Red:** Update the three existing tests in `test_plan.py:12-70` to pass `--kind feature` (since `0.1.0`/`0.2.0`/`0.4.0` are all feature-shaped semvers). Confirm they still pass (scorecard, ledger registration, parent canonicalization all unaffected). Also update path assertions: `Path("design/adr/ADR-0.1.0.md")` → `Path("design/adr/pre-release/ADR-0.1.0/ADR-0.1.0.md")`.
**Green:** No new code — the refactor must preserve the scorecard/ledger/canonicalization branches untouched.

### Step 9 — Docs

**Red:** None (docs change).
**Green:** Update `docs/user/commands/plan-create.md`:
- Add `--kind` row to Options table with `Type: pool | foundation | feature`, `Default: —` (required), description.
- Add three examples to example block: `--kind pool`, `--kind foundation --semver 0.0.20`, `--kind feature --semver 0.5.0`.
- Update "What It Does" narrative to mention kind-aware routing.

### Step 10 — `@covers` decorators

Decorate every new/updated test with `@covers("REQ-0.0.17-02-NN")` mapping to REQs 1-8. Pattern: import from `gzkit.testing` or equivalent (scan existing `@covers` usage for canonical import path — one of the existing test modules will show it).

## Verification

```bash
# REQ-level parity gate
uv run gz covers OBPI-0.0.17-02-plan-create-kind --json   # expect summary.uncovered_reqs == 0

# Help surface
uv run gz plan create --help | grep -- --kind

# Golden-path dry-runs
uv run gz plan create scratch-foundation --kind foundation --semver 0.0.99 --lane lite --dry-run
uv run gz plan create scratch-feature --kind feature --semver 0.99.0 --lane heavy --dry-run
uv run gz plan create scratch-pool --kind pool --dry-run

# Rejection — must exit 1, write nothing
uv run gz plan create scratch-bad --kind feature --semver 0.0.99 --dry-run
uv run gz plan create scratch-bad --kind foundation --semver 0.5.0 --dry-run

# Quality gates
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.17-02-plan-create-kind
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_plan -v
uv run gz validate --documents
uv run mkdocs build --strict
```

Heavy-lane Gate 4 (BDD) — if the runbook prescribes a `gz plan create` scenario under `features/`, add `@REQ-0.0.17-02-NN` tags to the scenarios covering the new behavior. If no such feature file exists, flag at ceremony rather than authoring one (BDD coverage scope is OBPI-0.0.17-04's territory per brief Denied Paths).
