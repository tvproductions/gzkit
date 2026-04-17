# Plan: OBPI-0.0.16-01 — `gz validate --frontmatter` guard

**OBPI:** `OBPI-0.0.16-01-validate-frontmatter-guard`
**Parent ADR:** `ADR-0.0.16` (Heavy / Foundation)
**Execution mode:** Normal

## Current state (discovery summary)

An initial `--frontmatter` flag already exists on `gz validate` and a partial
`_validate_frontmatter_coherence()` helper in
`src/gzkit/commands/validate_cmd.py` compares `id` / `parent` / `lane` against
`Ledger.get_artifact_graph()`. The brief's 12 requirements are **not** met by
this partial surface. Concrete gaps:

| Brief REQ | Current state | Gap |
|-----------|---------------|-----|
| REQ-01 clean repo → exit 0, empty output | Default "All validations passed" prose; exit 0 only when bundled with all scopes | Suppress green prose when `--frontmatter` is sole scope |
| REQ-02 path-keyed lookup, NEVER on `fm.id` | `_resolve_ledger_id` tries `fm.id` **first**, `stem_id` second | Flip: use filesystem stem only; drop `fm.id` fallback (reproduces GHI #166) |
| REQ-03 STOP if ledger lacks path→id mapping | Graph has no explicit `path` field, BUT canonical naming convention gives stem→id mapping deterministically | No new index introduced; stem-keying is the canonical convention — **no BLOCKER** |
| REQ-04 lifecycle via same API as `gz adr report` | Status field not compared at all | Reuse `_build_adr_status_entry` (ADR) and `_build_obpi_status_entry` (OBPI) for status derivation; do NOT reimplement |
| REQ-05 ignore ungoverned keys | Implicit pass (only id/parent/lane touched) | Keep strict allowlist of four governed fields |
| REQ-06 per-file per-field `drift` JSON array | Only generic `ValidationError` shape | Add `ledger_value` + `frontmatter_value` fields to `ValidationError`; emit `drift:` JSON key when `--frontmatter` is active |
| REQ-07 `--adr <ID>` / `--explain <ADR-ID>` | Flags absent | Add to parser + thread through |
| REQ-08 exit codes 0/1/2/3 | `_print_validation_result` raises `SystemExit(1)` on any error | Route: frontmatter-class drift → 3; other errors → 1 |
| REQ-09 never mutates | Already satisfied | — |
| REQ-10 no gate wiring | Already satisfied (OBPI-02 scope) | — |
| REQ-11 < 1.0s runtime budget | Untested | Add a performance test using `time.perf_counter()` on the real repo |
| REQ-12 nine test sub-scenarios | Five tests in `test_validate_cmds.py::TestFrontmatter` | Author full suite in `tests/commands/test_validate_frontmatter.py` with `@covers(REQ-...)` decorators |

## Scope amendments (flagged for plan-audit)

Brief Allowed Paths reference `src/gzkit/commands/validate.py` (module does
not exist under that name — the canonical module is `validate_cmd.py`). Plan
treats them as the same surface. Additionally, REQ-06 needs two optional
fields on `ValidationError` (which lives in `src/gzkit/validate.py`); that
path is **not** listed. Two amendments requested:

1. **Map** `src/gzkit/commands/validate.py` → `src/gzkit/commands/validate_cmd.py` (historical rename, same operator moment).
2. **Add** `src/gzkit/validate.py` — minimal, additive: extend `ValidationError` with two optional string fields (`ledger_value`, `frontmatter_value`). No behavior change for existing callers.

## Implementation steps (TDD — Red → Green → Refactor per REQ)

### Step 1 — Red: author failing tests

File: **`tests/commands/test_validate_frontmatter.py`** (NEW, per brief
Allowed Paths). Ten tests, each decorated with `@covers("REQ-0.0.16-01-NN")`:

1. `test_coherent_repo_exits_0_and_empty_output` — REQ-01
2. `test_status_drift_exits_3_reports_drift_line` — REQ-02 (status field coverage)
3. `test_lane_drift_exits_3` — REQ-02 (carry over)
4. `test_parent_drift_exits_3` — REQ-02 (carry over)
5. `test_id_drift_resolved_via_path_not_fm_id` — REQ-03 (seed ADR with rewritten `id:`; assert validator still finds it via stem and reports `id:` drift, never silently trusts rewritten id)
6. `test_ungoverned_key_ignored` — REQ-04 (seed `tags:` mismatch; expect exit 0)
7. `test_json_emits_drift_array_with_required_keys` — REQ-05 (assert `{"drift": [{"path","field","ledger_value","frontmatter_value"}, ...]}`)
8. `test_explain_emits_recovery_command_per_drifted_field` — REQ-06 (each drifted field gets a line naming a `gz` recovery command; no hand-edit suggestions)
9. `test_adr_scope_restricts_output_to_one_artifact` — REQ-07 (seed drift in two ADRs; `--adr ADR-X` output mentions only ADR-X)
10. `test_runtime_budget_under_one_second` — REQ-08 (run on real repo via `get_project_root()`, assert wall-clock < 1.0s)

Also add `--help` assertion that exit codes 0/1/2/3 are documented per CLI doctrine.

### Step 2 — Green: implement path-keyed lookup (REQ-02, REQ-03)

In `validate_cmd.py`:

- Replace `_resolve_ledger_id` with `_resolve_ledger_id_from_path` that canonicalizes **only** from `artifact_file.stem`. Strip ADR slug suffix (`ADR-0.0.16-slug-words` → `ADR-0.0.16`) via the existing `re.match(r"(ADR-[\d.]+)", …)` pattern. OBPI stems are already canonical full IDs.
- Remove `fm.id` as a resolution input; if stem canonicalization yields no graph match, skip (orphan — already surfaced by `_warn_orphaned_adrs`).
- `_check_one_artifact` signature gains `ledger_status_value: str | None`.

### Step 3 — Green: add status-field comparison (REQ-04)

New helper `_derive_canonical_status(ledger_id, info, project_root, config, ledger)`:

- If `info["type"] == "adr"`: call `_build_adr_status_entry(project_root, config, ledger, ledger_id, info)` (import from `gzkit.commands.status`) and return `entry["lifecycle_status"]`.
- If `info["type"] == "obpi"`: call `_build_obpi_status_entry(project_root, config, ledger, ledger_id)` and return `entry["runtime_state"]`.

Comparison is case-insensitive. A mismatch is drift regardless of vocabulary
(OBPI-05 will canonicalize later; OBPI-01's job is detection only). Status
comparison is only emitted for the four governed fields — no new keys.

### Step 4 — Green: emit `ledger_value` / `frontmatter_value`

In `src/gzkit/validate.py` extend `ValidationError`:

```python
class ValidationError(BaseModel):
    model_config = ConfigDict(frozen=True, extra="forbid")
    type: str = Field(...)
    artifact: str = Field(...)
    message: str = Field(...)
    field: str | None = Field(None)
    ledger_value: str | None = Field(None)      # new
    frontmatter_value: str | None = Field(None) # new
```

Update `_check_one_artifact` to populate both for each frontmatter
disagreement. The `model_dump(exclude_none=True)` call in `validate()`
already drops them from non-frontmatter errors — fully backwards
compatible.

### Step 5 — Green: `--adr` scope and `--explain` renderer

`parser_maintenance.py` — add:

```python
p_validate.add_argument("--adr", dest="frontmatter_adr", default=None,
                        help="Scope --frontmatter validation to one ADR or OBPI")
p_validate.add_argument("--explain", dest="frontmatter_explain", default=None,
                        help="Print remediation commands per drifted field for one ADR")
```

`validate()` signature gains `frontmatter_adr: str | None = None,
frontmatter_explain: str | None = None`. Thread through to
`_validate_frontmatter_coherence(project_root, adr_scope=..., explain_adr=...)`.

`_validate_frontmatter_coherence` filters artifacts when `adr_scope` is set.

New module helper `_render_frontmatter_explain(errors, adr_id)` prints one
line per drifted field, each naming a `gz` recovery command from the
following table:

| Drifted field | Recovery command |
|---------------|------------------|
| `id` | `gz register-adrs --all` |
| `parent` | `gz register-adrs --all` |
| `lane` | `gz adr promote <ID> --lane <value>` (or `gz adr emit-receipt` for attested ADRs) |
| `status` | `gz chore run frontmatter-ledger-coherence` |

No recovery line ever suggests hand-editing.

### Step 6 — Green: exit code routing (REQ-08)

Modify `_print_validation_result`:

```python
frontmatter_errors = [e for e in errors if e.type == "frontmatter"]
non_frontmatter = [e for e in errors if e.type != "frontmatter"]
if non_frontmatter:
    raise SystemExit(1)
if frontmatter_errors:
    raise SystemExit(3)
```

When `--frontmatter` is the sole scope AND there is no drift, suppress the
"All validations passed" prose (REQ-01 empty body).

Document the 4-code map in the parser's epilog and `--help`.

### Step 7 — Green: JSON shape

In `validate()`, when `check_frontmatter` is true, add a top-level `drift`
key to the JSON payload, mapped 1:1 from the `frontmatter`-type errors with
(`path` ← `artifact`, `field`, `ledger_value`, `frontmatter_value`). Keep
the existing `errors` array unchanged for callers that parse the generic
schema.

### Step 8 — Refactor

If `validate_cmd.py` exceeds the 600-line soft cap after Steps 2–7, extract
`_validate_frontmatter_coherence`, `_check_one_artifact`,
`_derive_canonical_status`, and `_render_frontmatter_explain` to a new
module `src/gzkit/commands/validate_frontmatter.py` (authorized in Allowed
Paths). Re-import from `validate_cmd.py` for the dispatcher.

### Step 9 — Docs (Heavy lane, Gate 3)

Update `docs/user/commands/validate.md`:

- Add `--frontmatter` section with examples (clean, drifted, `--adr`, `--explain`, `--json`).
- Document exit codes 0/1/2/3 and the 4-code map.
- Link to ADR-0.0.16 for intent.

### Step 10 — Verification bundle (Stage 3)

```bash
uv run gz lint
uv run gz typecheck
uv run gz test
uv run mkdocs build --strict
uv run gz validate --documents
uv run gz covers OBPI-0.0.16-01-validate-frontmatter-guard --json  # parity gate
uv run gz validate --frontmatter            # expect exit 3 (dogfood: ~94.7% status drift exists; this IS the guard working)
uv run gz validate --frontmatter --json     # structure check
uv run gz validate --frontmatter --adr ADR-0.0.16
uv run gz validate --frontmatter --explain ADR-0.0.16
```

Behave is covered by `uv run gz test`. Runtime-budget test doubles as the
< 1.0s evidence for REQ-11.

## Files touched (all inside amended Allowed Paths)

- `src/gzkit/commands/validate_cmd.py` (treated as `validate.py` per scope amendment)
- `src/gzkit/commands/validate_frontmatter.py` (NEW, conditional on Step 8 split)
- `src/gzkit/validate.py` (ValidationError field extension — scope amendment)
- `src/gzkit/cli/parser_maintenance.py` (argparse wiring; not listed but the brief's intent names `src/gzkit/cli/parser_artifacts.py` — parser for `validate` is actually in `parser_maintenance.py`. Treat as path rename per amendment #1 — same operator surface.)
- `tests/commands/test_validate_frontmatter.py` (NEW, per brief)
- `docs/user/commands/validate.md`
- `docs/design/adr/foundation/ADR-0.0.16-frontmatter-ledger-coherence-guard/ADR-0.0.16-frontmatter-ledger-coherence-guard.md` (evidence section only, at Stage 4)

Additionally the brief itself (`…/obpis/OBPI-0.0.16-01-validate-frontmatter-guard.md`) is edited at Stage 5 by `gz obpi complete`.

## Scope amendments summary

1. `src/gzkit/commands/validate.py` → `src/gzkit/commands/validate_cmd.py` (historical rename).
2. `src/gzkit/cli/parser_artifacts.py` → `src/gzkit/cli/parser_maintenance.py` (the `validate` parser actually lives in parser_maintenance).
3. ADD `src/gzkit/validate.py` — two additive optional `ValidationError` fields for the drift shape.

## Out of scope (explicit)

- Gate wiring (OBPI-02).
- Chore registration (OBPI-03).
- One-time backfill (OBPI-04).
- Status-vocabulary mapping consumption (OBPI-05 — not yet authored; OBPI-01 does raw-string comparison instead).
- Rewriting the 13 consumer code paths (ADR explicitly excludes this).

## Risks and mitigations

- **Risk:** Running `gz validate --frontmatter` in the dogfood verification will report many drift lines (the ADR premise is 94.7% drift). **Mitigation:** This is evidence the guard works, not a failure. Stage 4 ceremony evidence will cite the drift count as positive proof. OBPI-04 clears it.
- **Risk:** `_build_adr_status_entry` is heavyweight and could blow the 1.0s budget at scale. **Mitigation:** Test measures real repo (~80 ADRs / ~200 OBPIs); if it fails, cache the derived statuses per-run rather than per-file.
- **Risk:** Status vocabulary mismatch produces false drift until OBPI-05 lands. **Mitigation:** Brief scopes OBPI-01 to detection only; false drift is the expected signal until OBPI-03 chore consumes the mapping.
