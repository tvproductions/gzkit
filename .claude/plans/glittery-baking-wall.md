# OBPI-0.0.17-05: ADR taxonomy backfill + scaffolder round-trip test

## Context

ADR-0.0.17 added a required `kind:` field to ADR frontmatter (`foundation` for `0.0.x` semvers, `feature` for everything else; pool ADRs are excluded — kind is id-derived). OBPI-01 added the `AdrFrontmatter.kind` Pydantic field, OBPI-02 added `--kind` to `gz plan create`, OBPI-03 added `--kind` to `gz adr promote`, OBPI-04 added `gz validate --taxonomy` with id-derived rules.

Today, 59 existing non-pool ADRs lack the `kind:` field (16 foundation under `docs/design/adr/foundation/`, 43 pre-release under `docs/design/adr/pre-release/`). Until backfill runs, `uv run gz validate --taxonomy` will report violations across the entire ADR tree, and the parent ADR-0.0.17 cannot close out cleanly. OBPI-05 has two deliverables:

1. **Backfill** — write `kind:` into every existing non-pool ADR via an idempotent one-shot mechanism that emits a JSON receipt of what it changed.
2. **Round-trip test** — lock the scaffolder→validator contract: `gz plan create … --kind X` and `gz adr promote … --kind X` produce files that the validator accepts with zero errors. This mirrors the precedent established by GHI #186 (PRD canonicalization) and GHI #216 (constitution canonicalization).

## Design Decisions

### One-shot script, not chore-library entry

The brief's allowed paths offer two routes: a chore-library implementation (`src/gzkit/chores/taxonomy_backfill.py` + `config/chores/adr-taxonomy-backfill.json`) **or** a one-shot script (`scripts/backfill_adr_taxonomy.py`). Investigation of the actual chore framework (`config/gzkit.chores.json` v2.0 pointer registry → `ops/chores/<slug>/{CHORE.md,acceptance.json,README.md,proofs/}`) reveals:

- Chores are pointer-registry entries that wrap `gz` CLI commands for acceptance evidence (precedent: `frontmatter-ledger-coherence` chore wraps `gz frontmatter reconcile`).
- Chore mutation logic conventionally lives in `gz` commands, not in `src/gzkit/chores/`.
- Wiring this as a chore would require either (a) a new `gz` subcommand (Heavy-lane CLI doctrine — manpage, audit, registration — exceeds the brief's allowed paths) or (b) inventing a `src/gzkit/chores/` Python-module convention that doesn't exist elsewhere.

A one-shot script is the right route: it matches the brief's literal allowed-paths option, the operation is genuinely one-shot (idempotent rerun is no-op), and no ongoing chore-library integration is needed once the backfill lands.

### Scope amendment: `tests/scripts/test_backfill_adr_taxonomy.py`

The brief's allowed paths cover round-trip tests in `tests/commands/` but provide no test home for the script itself. REQ-01 through REQ-04 and REQ-08 require unit coverage of the script's behavior (idempotence, classification, preservation, receipt schema, ledger non-mutation). Adding `tests/scripts/test_backfill_adr_taxonomy.py` is the minimum scope expansion that lets the parity gate (`gz covers --json`) reach `uncovered_reqs == 0`. This is a scope-honest amendment per the OBPI-0.25.0-33 precedent.

### Classification rule (semver-driven, no judgment)

- `semver` matches `^0\.0\.\d+$` → `kind: foundation`
- Any other valid semver → `kind: feature`
- Missing `semver:` field → record error in receipt, skip mutation (this also catches pool ADRs as a defense-in-depth check beyond path exclusion)
- Malformed semver → record error in receipt, skip mutation

### Frontmatter ordering

Insert `kind:` immediately after the `status:` line. This matches the canonical field order in `src/gzkit/core/models.py::AdrFrontmatter` (id, status, semver, lane, kind, parent, date) and the order produced by `gz plan create` (template at `src/gzkit/templates/adr.md` line 4).

### Receipt schema

```json
{
  "timestamp": "2026-04-19T12-34-56Z",
  "dry_run": false,
  "files_scanned": 59,
  "files_modified": 59,
  "modifications": [
    {"path": "docs/design/adr/foundation/ADR-0.0.1.../<file>.md", "kind": "foundation", "semver": "0.0.1"}
  ],
  "errors": []
}
```

Receipt path: `artifacts/receipts/adr-taxonomy-backfill-<UTC-timestamp>.json`. Filename matches the brief's literal contract.

### Path discipline

Walk only top-level ADR files: `docs/design/adr/foundation/**/ADR-*.md` and `docs/design/adr/pre-release/**/ADR-*.md`, skipping any path containing `/obpis/`, `/briefs/`, `/audit/`, `/handoffs/`, or `/plans/`. Pool path (`docs/design/adr/pool/**`) is denied entirely. Three foundation ADRs already carry `kind:` (0.0.16, 0.0.17, 0.0.18) — the script must idempotently skip them.

### Round-trip tests mirror GHI #186/#216 exactly

Both precedents use the identical shape:

```python
runner = CliRunner()
with runner.isolated_filesystem():
    _quick_init()
    result = runner.invoke(main, ["plan", "<slug>", "--kind", kind])
    self.assertEqual(result.exit_code, 0, msg=result.output)
    scaffolded = Path("design/adr/<routed-path>")
    self.assertTrue(scaffolded.exists())
    errors = validate_document(scaffolded, "adr")
    self.assertEqual(errors, [], msg=...)
```

No shared helper exists; each precedent re-implements the pattern. We follow that convention rather than introduce a new abstraction.

## Implementation Steps (TDD per increment, RED → GREEN → next)

### Step 1 — Test file: `tests/scripts/test_backfill_adr_taxonomy.py` (RED batch)

Author the failing tests first, one increment at a time:

1. `test_classifies_foundation_and_feature_by_semver` (`@covers REQ-0.0.17-05-02`) — temp tree with two fixture ADRs (semver `0.0.5` and `0.3.0`); after script run, both have correct `kind:`.
2. `test_preserves_other_frontmatter_fields` (`@covers REQ-0.0.17-05-03`) — fixture ADR with id/status/semver/lane/parent/date; after run, every non-`kind` field byte-identical and order preserved; `kind:` inserted after `status:`.
3. `test_second_run_is_noop` (`@covers REQ-0.0.17-05-01`) — run twice; second receipt has `files_modified == 0`.
4. `test_emits_receipt_with_required_fields` (`@covers REQ-0.0.17-05-04`) — assert receipt JSON has `timestamp`, `dry_run`, `files_scanned`, `files_modified`, `modifications`, `errors`.
5. `test_records_error_for_missing_semver` (`@covers REQ-0.0.17-05-02`) — fixture ADR with no `semver:` field; not mutated; receipt `errors[]` contains an entry citing the file.
6. `test_does_not_touch_ledger` (`@covers REQ-0.0.17-05-08`) — assert `.gzkit/ledger.jsonl` byte-identical before and after script run.
7. `test_dry_run_does_not_mutate` (`@covers REQ-0.0.17-05-01`) — `--dry-run` produces receipt with `dry_run: true` and zero file changes.

Run RED: `uv run -m unittest tests.scripts.test_backfill_adr_taxonomy -v` → expect import error or all-fail.

### Step 2 — Implement `scripts/backfill_adr_taxonomy.py` (GREEN)

Module structure (functions extracted for testability — script imports + invokes `main()`):

- `classify_kind(semver: str) -> Literal["foundation", "feature"]`
- `parse_frontmatter(path: Path) -> tuple[dict, str, str]` — returns `(fields_in_order, body, raw_frontmatter_text)`
- `insert_kind(content: str, kind: str) -> str` — line-based insertion after `status:`, preserving everything else
- `walk_adrs(roots: list[Path]) -> Iterator[Path]` — top-level ADR files only, skipping nested directories
- `run_backfill(roots, receipt_dir, dry_run, now) -> Receipt` — pure function returning receipt dict
- `main(argv)` — argparse `--apply` / `--dry-run` (default `--dry-run`), writes receipt JSON

Re-run RED tests → all GREEN.

### Step 3 — Test files: `tests/commands/test_plan.py` and `test_adr_promote.py` (RED batch)

Add `TestPlanTaxonomyRoundtrip` class to `test_plan.py`:

1. `test_plan_create_foundation_kind_passes_taxonomy_validator` (`@covers REQ-0.0.17-05-05`)
2. `test_plan_create_feature_kind_passes_taxonomy_validator` (`@covers REQ-0.0.17-05-05`)

Add `TestAdrPromoteTaxonomyRoundtrip` class to `test_adr_promote.py`:

3. `test_promote_to_foundation_passes_taxonomy_validator` (`@covers REQ-0.0.17-05-06`)
4. `test_promote_to_feature_passes_taxonomy_validator` (`@covers REQ-0.0.17-05-06`)

Each test follows the GHI #186/#216 shape: scaffold, assert exit 0 + file exists, `validate_document(path, "adr")`, assert empty errors.

Run RED → confirm tests exist but fail / file paths need adjustment.

### Step 4 — Verify scaffolders already produce taxonomy-valid output (GREEN)

If OBPI-02/03 work is complete and correct, the scaffolders already emit `kind:` and the round-trip tests should GREEN immediately with no production-code changes. If a defect is exposed (e.g., scaffolder emits `kind:` in wrong position), file as in-flight defect and fix in the smallest necessary change to scaffolder template / handler, decorating with `@covers`.

### Step 5 — Run the backfill in apply mode

```bash
uv run python scripts/backfill_adr_taxonomy.py --apply
```

Inspect the receipt at `artifacts/receipts/adr-taxonomy-backfill-<timestamp>.json`. Expect 59 modifications, 0 errors.

### Step 6 — Verify whole-tree taxonomy gate

```bash
uv run gz validate --taxonomy
```

Expect exit 0. If non-zero, inspect violations, fix the script (likely a classification edge case), re-run from Step 5.

### Step 7 — Idempotence proof

```bash
uv run python scripts/backfill_adr_taxonomy.py --apply
```

Inspect second receipt: expect `files_modified == 0`.

### Step 8 — Parity gate

```bash
uv run gz covers OBPI-0.0.17-05 --json
```

Expect `summary.uncovered_reqs == 0`.

## REQ → @covers Map

| REQ | Test | File |
|---|---|---|
| REQ-0.0.17-05-01 (idempotence) | `test_second_run_is_noop`, `test_dry_run_does_not_mutate` | `tests/scripts/test_backfill_adr_taxonomy.py` |
| REQ-0.0.17-05-02 (semver classification) | `test_classifies_foundation_and_feature_by_semver`, `test_records_error_for_missing_semver` | same |
| REQ-0.0.17-05-03 (preservation) | `test_preserves_other_frontmatter_fields` | same |
| REQ-0.0.17-05-04 (receipt schema) | `test_emits_receipt_with_required_fields` | same |
| REQ-0.0.17-05-05 (plan create round-trip) | `test_plan_create_{foundation,feature}_kind_passes_taxonomy_validator` | `tests/commands/test_plan.py` |
| REQ-0.0.17-05-06 (adr promote round-trip) | `test_promote_to_{foundation,feature}_passes_taxonomy_validator` | `tests/commands/test_adr_promote.py` |
| REQ-0.0.17-05-07 (whole-tree clean) | Operational — `gz validate --taxonomy` exit 0 captured in evidence | n/a |
| REQ-0.0.17-05-08 (no ledger mutation) | `test_does_not_touch_ledger` | `tests/scripts/test_backfill_adr_taxonomy.py` |

## Files

### New

- `scripts/backfill_adr_taxonomy.py` — one-shot backfill script (~150 lines)
- `tests/scripts/test_backfill_adr_taxonomy.py` — script unit tests (~200 lines, 7 tests) **(scope amendment)**
- `tests/scripts/__init__.py` — empty, for unittest discovery **(scope amendment, trivial)**
- `artifacts/receipts/adr-taxonomy-backfill-<timestamp>.json` — apply-run receipt artifact

### Modified

- `tests/commands/test_plan.py` — add `TestPlanTaxonomyRoundtrip` class (2 tests, ~40 lines)
- `tests/commands/test_adr_promote.py` — add `TestAdrPromoteTaxonomyRoundtrip` class (2 tests, ~40 lines)

### Mutated by script (one-shot data migration)

- 16 ADR files under `docs/design/adr/foundation/**/ADR-*.md` (excluding 0.0.16, 0.0.17, 0.0.18 which already have `kind:`)
- 43 ADR files under `docs/design/adr/pre-release/**/ADR-*.md`

## Critical Files to Reference

- `src/gzkit/core/models.py:19-30` — `AdrFrontmatter` Pydantic model with field order
- `src/gzkit/governance/trust_audits.py:1057` — `audit_adr_taxonomy()` validator logic
- `src/gzkit/templates/adr.md:4` — canonical `kind:` position in scaffolded ADRs
- `src/gzkit/validate_pkg/document.py:199-262` — `validate_document(path, schema_name) -> list[ValidationError]` API used by round-trip tests
- `tests/commands/test_prd.py:74-88` — GHI #186 round-trip test pattern (precedent)
- `tests/commands/test_constitute.py:76-90` — GHI #216 round-trip test pattern (precedent)
- `tests/commands/common.py:20-50,267-356` — `CliRunner` and `_quick_init()` helpers

## Verification

```bash
# Per-increment RED → GREEN (Stage 2)
uv run -m unittest tests.scripts.test_backfill_adr_taxonomy -v
uv run -m unittest tests.commands.test_plan tests.commands.test_adr_promote -v

# Stage 3 baseline + parity
uv run gz lint
uv run gz typecheck
uv run gz test --obpi OBPI-0.0.17-05-backfill-and-roundtrip
uv run gz covers OBPI-0.0.17-05-backfill-and-roundtrip --json   # uncovered_reqs == 0

# Stage 3 ARB receipts (cited in Stage 4 evidence)
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.scripts.test_backfill_adr_taxonomy tests.commands.test_plan tests.commands.test_adr_promote -v

# Operational verification
uv run python scripts/backfill_adr_taxonomy.py --dry-run    # preview before apply
uv run python scripts/backfill_adr_taxonomy.py --apply       # one-shot apply
uv run gz validate --taxonomy                                # exit 0 across whole tree
uv run python scripts/backfill_adr_taxonomy.py --apply       # idempotence: 0 modifications
```

## Execution Mode

ADR-0.0.17 is Heavy lane (per the brief frontmatter and `gz adr status ADR-0.0.17`). No `## Execution Mode: Exception (SVFR)` section, so this is **Normal mode** — Stage 4 requires human attestation before sync.
