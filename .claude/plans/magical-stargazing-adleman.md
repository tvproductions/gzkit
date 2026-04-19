# OBPI-0.0.17-03: `--kind` flag on `gz adr promote`

## Context

ADR-0.0.17-adr-taxonomy-mechanical (Heavy lane, foundation kind) makes ADR
taxonomy explicit and mechanically enforced. OBPI-01 landed the `kind` field
in the schema/Pydantic model. OBPI-02 added `--kind {pool,foundation,feature}`
to `gz plan create`. This OBPI extends the same taxonomic intent to **promotion
time** so that pool→canonical promotion declares the target kind explicitly,
validates the kind/semver binding atomically before any file move, stamps
`kind:` on the promoted frontmatter, and routes the promoted file into the
correct directory bucket (`foundation/` vs `pre-release/`) based on kind, not
semver.

Without this, agents could promote a 0.0.x pool ADR with `--semver 0.6.0` and
land it as a feature ADR without ever asserting the kind — exactly the implicit
routing failure mode OBPI-01/02 exist to prevent.

## Decisions

1. **Mirror OBPI-02's `--kind` choice set**: register `choices=["pool", "foundation", "feature"]`
   and reject `pool` explicitly with exit 1 + recovery message ("pool is the source kind, not a target").
   Symmetric UX with `gz plan create`; honors REQ-01's "exit 1" requirement (argparse default would be exit 2).
2. **Replace semver-driven bucket with kind-driven bucket** via a new in-module
   helper `_adr_bucket_for_kind(kind: str) -> str` in `adr_promote.py`. Verified:
   `_adr_bucket_for_semver` has only one caller (`adr_promote.py:64`), so the swap is safe.
   Do NOT modify `adr_promote_utils.py` (out of allowed paths).
3. **Mutate ledger event extras inline** (option b) — build with `artifact_renamed_event(...)`
   then assign `rename_event.extra["kind"] = kind; rename_event.extra["semver"] = semver`
   before append. Avoids extending the helper signature in `ledger_events.py` (out of allowed paths).
   Verified: `LedgerEvent` has `extra="forbid"` for construction but is not frozen — `extra` dict
   is mutable.
4. **Frontmatter `kind:` insertion** uses existing `_upsert_frontmatter_value` re-exported at
   `gzkit.commands.common:425`. Inserts at end-of-frontmatter; field-ordering is not enforced
   by schema (validates presence + value only).
5. **Heavy-lane Gate 4 BDD scope amendment**: add `features/adr_promote.feature` outside the
   brief's allowed paths. Precedent: OBPI-0.0.16-02 added `features/gates.feature` for the same
   reason (`.gzkit/rules/tests.md` GHI #185). Surface this amendment in the Stage 4 evidence.
6. **Inline `_FOUNDATION_SEMVER_RE` duplication**: cannot import from `plan.py` (denied path).
   File a follow-up GHI to extract to `gzkit.commands.common` after OBPI-04 lands.

## Files to modify (allowed paths)

- `src/gzkit/cli/parser_artifacts.py` — register `--kind` flag, thread to handler call
- `src/gzkit/commands/adr_promote.py` — handler signature, validation block, kind-driven bucket helper, frontmatter upsert, ledger event extras
- `tests/commands/test_adr_promote.py` — new `TestAdrPromoteKindFlag` class (REQ-decorated tests); update 5 existing tests to add `--kind`
- `docs/user/commands/adr-promote.md` — `--kind` row in Options, kind-driven routing section, kind/semver binding subsection, examples

## Files to add (scope amendment, see Decision 5)

- `features/adr_promote.feature` — 8 scenarios tagged `@REQ-0.0.17-03-NN`
- (potentially `features/steps/*.py` if a JSONL-extras step doesn't already exist; check first)

## Implementation tasks (TDD per increment, RED→GREEN→Refactor)

### Task 1 — REQ-01: `--kind` registered; pool rejected; missing flag rejected

RED tests in `tests/commands/test_adr_promote.py` (new class `TestAdrPromoteKindFlag`):
- `test_help_shows_kind_choices` — `--help` output contains `--kind` and three choices. `@covers REQ-0.0.17-03-01`
- `test_missing_kind_exits_one_with_recovery` — exit 1, names both foundation and feature. `@covers REQ-0.0.17-03-01`
- `test_kind_pool_rejected_with_exit_one` — exit 1, message explains pool is source not target. `@covers REQ-0.0.17-03-01`

GREEN:
- `parser_artifacts.py:188-193`: add `--kind` argument with `choices=["pool", "foundation", "feature"]`, `default=None`.
- `parser_artifacts.py:201-214`: thread `kind=a.kind` into handler call.
- `adr_promote.py:240-251`: add `kind: str | None` parameter.
- `adr_promote.py` after line 255: insert validation block (kind None / kind == pool) — both raise `SystemExit(1)`.

Update existing 5 tests in `test_adr_promote.py` to add `--kind feature` (or `--kind foundation` where appropriate) to invocations so the suite stays green after REQ-01 lands. The existing tests use `--semver 0.6.0` → `--kind feature`.

### Task 2 — REQ-02 & REQ-03: kind/semver binding (atomicity inherent)

RED tests:
- `test_foundation_rejects_non_zero_zero_semver` — `--kind foundation --semver 0.6.0` → exit 1, no files. `@covers REQ-0.0.17-03-02`
- `test_feature_rejects_zero_zero_semver` — `--kind feature --semver 0.0.18` → exit 1, no files. `@covers REQ-0.0.17-03-03`
- `test_foundation_accepts_0_0_x_semver_dryrun` — `--kind foundation --semver 0.0.18 --dry-run` → exit 0. `@covers REQ-0.0.17-03-02`
- `test_feature_accepts_non_0_0_x_semver_dryrun` — `--kind feature --semver 0.6.0 --dry-run` → exit 0. `@covers REQ-0.0.17-03-03`
- `test_validation_failure_writes_nothing` — pool unchanged, no target dir, ledger size unchanged. `@covers REQ-0.0.17-03-04`
- `test_force_does_not_bypass_kind_validation` — `--force` does NOT skip kind/semver check. `@covers REQ-0.0.17-03-04`

GREEN:
- Add `_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")` at top of `adr_promote.py`.
- Append two `if` branches to validation block (foundation/regex mismatch, feature/regex match) — each raises `SystemExit(1)` with recovery message that names the alternative kind.
- Atomicity is automatic: validation runs before `_resolve_pool_adr_source(...)` and `_build_adr_promotion_plan(...)`; `_apply_adr_promotion(...)` only fires on success.

### Task 3 — REQ-05: Frontmatter `kind:` stamped; id transitions

RED tests:
- `test_promoted_frontmatter_carries_kind_foundation` — promoted file frontmatter contains `kind: foundation` and `id: ADR-0.0.18-sample-work`. `@covers REQ-0.0.17-03-05`
- `test_promoted_frontmatter_carries_kind_feature` — promoted file frontmatter contains `kind: feature`. `@covers REQ-0.0.17-03-05`
- `test_promoted_id_loses_pool_prefix` — `id:` matches `^ADR-\d+\.\d+\.\d+-` (no `pool`). `@covers REQ-0.0.17-03-05`

GREEN:
- Thread `kind` into `_build_adr_promotion_plan(...)` as a required keyword.
- After `_render_promoted_adr_content(...)` (line 89), apply
  `promoted_content = _upsert_frontmatter_value(promoted_content, "kind", kind)`
  using the import already available at `gzkit.commands.common:425`.
- Add `"target_kind": kind` and `"target_semver": semver` to the returned plan dict (Task 5 reads these).

### Task 4 — REQ-06: Bucket routing by kind

RED tests:
- `test_foundation_lands_in_foundation_bucket` — file at `docs/design/adr/foundation/ADR-0.0.18-sample-work/ADR-0.0.18-sample-work.md`. `@covers REQ-0.0.17-03-06`
- `test_feature_lands_in_pre_release_bucket` — file at `docs/design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md`. `@covers REQ-0.0.17-03-06`

GREEN:
- Add `_adr_bucket_for_kind(kind: str) -> str` helper in `adr_promote.py` returning `"foundation"` for foundation else `"pre-release"`.
- Replace `target_bucket = _adr_bucket_for_semver(semver)` at line 64 with `target_bucket = _adr_bucket_for_kind(kind)`.
- Remove `_adr_bucket_for_semver` from import block (line 10) — ruff will catch as unused otherwise.

Refactor opportunity: if the validation block at top of `adr_promote_cmd` grows past
~25 lines, extract to `_validate_promotion_kind_semver(kind, semver) -> None`.

### Task 5 — REQ-07: Ledger event extras include kind and semver

RED tests:
- `test_ledger_rename_event_includes_kind` — JSONL line for `event=="artifact_renamed"` has `extra["kind"] == "feature"` and `extra["semver"] == "0.6.0"`. `@covers REQ-0.0.17-03-07`
- `test_ledger_event_backward_compatible` — same line still has `extra["new_id"]` and `extra["reason"] == "pool_promotion"`. `@covers REQ-0.0.17-03-07`

GREEN: in `_apply_adr_promotion` (lines 184-190), replace single `ledger.append(artifact_renamed_event(...))` call with:
```python
rename_event = artifact_renamed_event(
    old_id=cast(str, promotion_plan["pool_adr_id"]),
    new_id=cast(str, promotion_plan["target_adr_id"]),
    reason="pool_promotion",
)
rename_event.extra["kind"] = cast(str, promotion_plan["target_kind"])
rename_event.extra["semver"] = cast(str, promotion_plan["target_semver"])
ledger.append(rename_event)
```

### Task 6 — REQ-08: Existing behavior preserved (regression coverage)

The 5 existing tests in `test_adr_promote.py:42-181` pinned with `--kind feature` (Task 1)
already serve as REQ-08 regression coverage. Add explicit `@covers REQ-0.0.17-03-08`
docstring to those tests in the same Task 1 commit.

### Task 7 — Heavy-lane Gate 4 BDD (scope amendment)

Create `features/adr_promote.feature` with 8 scenarios, each tagged `@REQ-0.0.17-03-NN`
matching the 8 REQs. Reuse existing step definitions in `features/steps/`; add a JSONL-extras
assertion step only if not already present (check first).

### Task 8 — REQ-01 docs: update `adr-promote.md`

- Add `--kind` row to Options table (between `--lane` and `--status`).
- Replace semver-bucket prose with kind-driven routing rules.
- Add "Kind/Semver Binding" subsection.
- Add example: `gz adr promote ADR-pool.gz-chores-system --kind feature --semver 0.6.0`.
- Note that `artifact_renamed` ledger event extras now include `kind` and `semver`.

## Verification (Stage 3)

Run in this order; each must pass before the next:

```bash
# Lint + typecheck
uv run gz arb ruff
uv run gz arb typecheck

# OBPI-scoped tests via @covers graph
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_adr_promote -v

# REQ → @covers parity gate (must be 0 uncovered)
uv run gz covers OBPI-0.0.17-03-adr-promote-kind --json

# Heavy-lane BDD
uv run gz test --obpi OBPI-0.0.17-03-adr-promote-kind --bdd

# Help-output smoke
uv run gz adr promote --help

# Full suite regression sweep
uv run gz arb step --name unittest -- uv run -m unittest discover tests -q

# Aggregate
uv run gz check
```

## Critical files referenced

- `src/gzkit/commands/adr_promote.py` — handler, plan builder, apply, helpers
- `src/gzkit/cli/parser_artifacts.py:156-214` — CLI registration
- `src/gzkit/commands/adr_promote_utils.py:86-93` — `_adr_bucket_for_semver` (read-only; helper being replaced)
- `src/gzkit/commands/common.py:425` — `_upsert_frontmatter_value` re-export
- `src/gzkit/ledger.py:46` — `LedgerEvent` model (mutable `extra`)
- `src/gzkit/ledger_events.py` — `artifact_renamed_event` (read-only; extras mutated by caller)
- `src/gzkit/commands/plan.py:73-104` — OBPI-02 validation precedent (read-only, denied path)
- `tests/commands/test_adr_promote.py` — existing 5 tests + new `TestAdrPromoteKindFlag` class
- `tests/commands/common.py` — `_quick_init`, `CliRunner`, subprocess patchers
- `features/adr_promote.feature` — NEW (scope amendment, Decision 5)

## Risks

- `_FOUNDATION_SEMVER_RE` duplicated between `plan.py` and `adr_promote.py` — accepted; follow-up GHI to extract once OBPI-04 lands.
- `_upsert_frontmatter_value` inserts `kind:` at end of frontmatter, not between `status:` and `semver:` — accepted; schema validates presence/value, not ordering.
- Existing `test_adr_promote_blocks_on_non_go_eval` expects exit 3 — confirm it stays exit 3 after `--kind feature` is added (kind validation happens before eval block, so order is preserved).
- `--force` must not bypass kind validation — pinned by `test_force_does_not_bypass_kind_validation`.
