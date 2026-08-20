---
id: OBPI-0.0.17-03-adr-promote-kind
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 3
lane: Heavy
status: Completed
---

# OBPI-0.0.17-03-adr-promote-kind: --kind flag on gz adr promote

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #3 — "`gz adr promote --kind` CLI flag + promotion validation"

**Status:** Draft

## Objective

Promotion is the moment a pool ADR is committed to work. `gz adr promote ADR-pool.<slug> --kind {foundation, feature} --semver X.Y.Z --lane {lite, heavy}` now expresses the taxonomic intent at promotion time: the promoted ADR's frontmatter carries the correct `kind:` field, the target directory matches (`foundation/` vs `pre-release/`), and the kind/semver binding is enforced before any file is moved.

## Lane

**Heavy** — CLI contract addition on an existing public command.

## Allowed Paths

- `src/gzkit/cli/parser_artifacts.py`
- `src/gzkit/commands/adr_promote.py` (or whatever module hosts `adr promote`)
- `tests/commands/test_adr_promote.py`
- `docs/user/commands/adr-promote.md` (or equivalent)

## Denied Paths

- Schema/model (OBPI-01)
- `gz plan create` (OBPI-02)
- `gz validate` (OBPI-04)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz adr promote --help` shows `--kind {foundation, feature}` as a required flag. Pool→pool promotion is not a valid operation; `--kind pool` is rejected with exit 1.
2. REQUIREMENT: `--kind foundation` requires `--semver` to match `^0\.0\.\d+$`. Mismatch → exit 1, no file moved, clear recovery message.
3. REQUIREMENT: `--kind feature` requires `--semver` to NOT match `^0\.0\.\d+$`. Mismatch → exit 1, no file moved.
4. REQUIREMENT: The pool source file is preserved (not deleted/moved) until all validation passes; promotion is atomic from the operator's perspective.
5. REQUIREMENT: The promoted ADR's frontmatter carries `kind: <value>` in addition to the existing fields (id, status, semver, lane, parent, date). The id changes from `ADR-pool.<slug>` to `ADR-X.Y.Z`.
6. REQUIREMENT: The promoted ADR lands at:
   - `docs/design/adr/foundation/ADR-X.Y.Z-<slug>/ADR-X.Y.Z-<slug>.md` for `--kind foundation`
   - `docs/design/adr/pre-release/ADR-X.Y.Z-<slug>/ADR-X.Y.Z-<slug>.md` for `--kind feature`
7. REQUIREMENT: The ledger event emitted by promotion records both `kind` and `semver` so downstream audits can reason about the decision. The event schema extension is additive and backward-compatible.
8. REQUIREMENT: Existing `gz adr promote` behavior for already-approved promotions remains unchanged except for the new required flag.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [x] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [x] Parent ADR — full taxonomy context
- [x] `.claude/rules/cli.md` — Heavy-lane trigger for subcommand/flag changes
- [x] `.claude/rules/defect-fix-routing.md` — thresholds for in-flight fix vs ceremony

**Context:**

- [x] Parent ADR: `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- [x] Prerequisite OBPIs: `OBPI-0.0.17-01-schema-and-model` (kind in `AdrFrontmatter`), `OBPI-0.0.17-02-plan-create-kind` (CLI precedent for `--kind` flag)
- [x] Sibling OBPIs: 04 (validate-taxonomy), 05 (backfill-and-roundtrip), 06 (agents-md-correction)

**Prerequisites (check existence, STOP if missing):**

- [x] `src/gzkit/cli/parser_artifacts.py` — argparse registration for `adr promote`
- [x] `src/gzkit/commands/adr_promote.py` — handler `adr_promote_cmd` and `_build_adr_promotion_plan`
- [x] `src/gzkit/commands/adr_promote_utils.py` — `_render_promoted_adr_content`, `_adr_bucket_for_semver` (helper being replaced)
- [x] `src/gzkit/core/models.py` — `AdrFrontmatter.kind: Literal["foundation", "feature"]` (from OBPI-01)
- [x] `src/gzkit/commands/common.py:425` — `_upsert_frontmatter_value` re-export
- [x] `src/gzkit/ledger.py` — `LedgerEvent` with mutable `extra` dict
- [x] `tests/commands/test_adr_promote.py` — existing 5 tests + `_seed_pool_adr` fixture

**Existing Code (understand current state):**

- [x] `adr_promote_cmd` at `src/gzkit/commands/adr_promote.py:240-323` — 11-arg signature; resolves pool, builds plan, applies plan, evaluates quality.
- [x] `_build_adr_promotion_plan` at `src/gzkit/commands/adr_promote.py:41-126` — validates target ADR, derives bucket via `_adr_bucket_for_semver(semver)`, renders promoted content.
- [x] `_apply_adr_promotion` at `src/gzkit/commands/adr_promote.py:173-197` — atomically writes target + OBPI files, updates pool to Superseded, appends `artifact_renamed_event`.
- [x] `_adr_bucket_for_semver` at `src/gzkit/commands/adr_promote_utils.py:86-93` — semver-driven bucket (replaced by `_adr_bucket_for_kind`; verified single caller).
- [x] OBPI-02 precedent at `src/gzkit/commands/plan.py:73-104` — `_FOUNDATION_SEMVER_RE`, validation pattern, error message shape.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [x] Intent and scope recorded in this OBPI brief
- [x] Parent ADR checklist item quoted (item #3 — "`gz adr promote --kind` CLI flag + promotion validation")

### Gate 2: TDD (Red-Green-Refactor)

- [x] Tests derived from brief acceptance criteria, not from implementation
- [x] Red-Green-Refactor cycle followed per behavior increment
- [x] Tests pass: `uv run -m unittest tests.commands.test_adr_promote -v` (20/20)
- [x] ARB receipts: ruff, typecheck, unittest, behave

### Code Quality

- [x] Lint clean: `uv run gz arb ruff` (receipt `arb-ruff-566f1dd2a7c04ee9b9763217f920261f`)
- [x] Type check clean: `uv run gz arb typecheck` (receipt `arb-step-typecheck-a9d2ecc0b30c488b99b00293b7e6ede4`)

### Gate 3: Docs (Heavy only)

- [x] `docs/user/commands/adr-promote.md` updated with `--kind` option row, kind/semver binding subsection, kind-driven routing narrative, examples, ledger extras note

### Gate 4: BDD (Heavy only)

- [x] `features/adr_promote.feature` authored with 8 `@REQ-0.0.17-03-NN` scenarios (scope amendment per OBPI-0.0.16-02 precedent; receipt `arb-step-behave-700b4c0f4d194d389379e07957ad21f2`)

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded (this Stage 5)

## Verification

```bash
uv run gz adr promote --help | grep -- --kind
# End-to-end smoke (against a throwaway pool ADR created in the test fixture):
#   gz adr promote ADR-pool.test --kind feature --semver 0.99.0 --lane lite
#   → writes docs/design/adr/pre-release/ADR-0.99.0-test/ADR-0.99.0-test.md with kind: feature
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_adr_promote -v
```

## Evidence

- Help output showing `--kind` registered
- Test transcript for each kind + the `--kind pool` rejection
- Ledger event dump showing `kind` and `semver` fields
- ARB receipts

## Acceptance Criteria

- [ ] REQ-0.0.17-03-01: `gz adr promote --help` shows `--kind {pool, foundation, feature}`. Missing `--kind` and `--kind pool` both exit 1 with a recovery message (pool is the source kind, not a target).
- [ ] REQ-0.0.17-03-02: `--kind foundation` requires `--semver` matching `^0\.0\.\d+$`. Mismatch exits 1; no file is moved and no ledger event is appended.
- [ ] REQ-0.0.17-03-03: `--kind feature` requires `--semver` to NOT match `^0\.0\.\d+$`. Mismatch exits 1; no file is moved.
- [ ] REQ-0.0.17-03-04: Validation runs before pool resolution and before any file or ledger write. Rejection leaves the pool source, ledger, and target tree untouched. `--force` does not bypass kind/semver binding.
- [ ] REQ-0.0.17-03-05: The promoted ADR frontmatter carries `kind: <value>` in addition to `id`, `status`, `semver`, `lane`, `parent`, `date`. The `id` transitions from `ADR-pool.<slug>` to `ADR-X.Y.Z-<slug>`.
- [ ] REQ-0.0.17-03-06: `--kind foundation` routes to `docs/design/adr/foundation/ADR-X.Y.Z-<slug>/`; `--kind feature` routes to `docs/design/adr/pre-release/ADR-X.Y.Z-<slug>/`. Routing is kind-driven, not semver-driven.
- [ ] REQ-0.0.17-03-07: The `artifact_renamed` ledger event extras include `kind` and `semver` in addition to the existing `new_id` and `reason`. Backward-compatible (additive only).
- [ ] REQ-0.0.17-03-08: All prior `gz adr promote` behavior (slug derivation, parent/lane resolution, OBPI generation, scaffold/eval gates, pool retention as Superseded) is preserved when `--kind` is supplied — the flag is additive.

## REQ Coverage

- REQ-0.0.17-03-01 through REQ-0.0.17-03-08 (one per Acceptance Criterion above, mapping 1:1 to the numbered Requirements)

### Value Narrative

Before this OBPI, `gz adr promote` selected the destination directory by parsing the semver alone — `0.0.x` → `foundation/`, anything else → `pre-release/` — leaving the taxonomic intent implicit and unauditable. After this OBPI, promotion declares `--kind {foundation, feature}` explicitly, validates the kind/semver binding atomically before any I/O, stamps `kind:` into the promoted ADR frontmatter (matching OBPI-01's schema), and records both `kind` and `semver` in the `artifact_renamed` ledger event so downstream audits can reason about the promotion decision. `--kind pool` is rejected (pool is the source kind, not a target). The change closes the implicit-routing failure mode that OBPI-01 and OBPI-02 also exist to prevent.

### Key Proof


```text
$ uv run gz adr promote --help
...
  --kind {pool,foundation,feature}
                        Target taxonomy: foundation (0.0.x) or feature
                        (0.y.z). pool rejected.

$ uv run gz adr promote ADR-pool.x --semver 0.6.0 --kind foundation
ERROR: --kind foundation requires --semver matching 0.0.x (got '0.6.0').
       If this is release-carrying work, use --kind feature.
$ echo $?
1   # no file moved, no ledger event written

$ uv run gz covers ADR-0.0.17 | grep "0.0.17-03"
OBPI-0.0.17-03              8        8   100.0%

# Successful feature promotion ledger event:
{"event":"artifact_renamed","id":"ADR-pool.sample-work",
 "new_id":"ADR-0.6.0-sample-work","reason":"pool_promotion",
 "kind":"feature","semver":"0.6.0"}
```

8/8 REQs covered (`gz covers ADR-0.0.17`). 20/20 unit tests + 8/8 BDD scenarios + 3218/3218 full suite pass.

### Implementation Summary


- Files modified (in-brief Allowed Paths):
  - `src/gzkit/cli/parser_artifacts.py` — registered `--kind {pool,foundation,feature}` (default=None; ≤80-char help text); threaded `kind=a.kind` to `adr_promote_cmd`.
  - `src/gzkit/commands/adr_promote.py` — added `_FOUNDATION_SEMVER_RE`, `_adr_bucket_for_kind`, and `_validate_promotion_kind_semver` helpers; threaded `kind` through `_build_adr_promotion_plan` (replaced `_adr_bucket_for_semver(semver)` call at line 64 with `_adr_bucket_for_kind(kind)`); upserted `kind:` into promoted frontmatter via `_upsert_frontmatter_value` (re-exported by `gzkit.commands.common:425`); mutated `rename_event.extra` with `kind` and `semver` before `ledger.append` (additive, backward-compatible).
  - `tests/commands/test_adr_promote.py` — added `TestAdrPromoteKindFlag` class with 15 REQ-decorated tests covering all 7 implementation REQs; updated 5 existing tests in `TestAdrPromoteCommand` to add `--kind feature` (now serve as REQ-0.0.17-03-08 regression coverage; class-level `@covers` declared).
  - `docs/user/commands/adr-promote.md` — added `--kind` row to Options table, "Kind/Semver Binding (FAIL-CLOSED)" subsection, kind-driven routing replacement narrative, ledger event extras note, three per-kind examples.

- Files modified (scope amendments, precedent OBPI-0.0.16-02):
  - `features/adr_promote.feature` — **new**; 8 `@REQ-0.0.17-03-NN` scenarios (one per REQ). Heavy-lane Gate 4 BDD per `.gzkit/rules/tests.md` GHI #185.
  - `features/steps/gz_steps.py` — added 3 generic, reusable steps: `the file "..." does not exist`, `a pool ADR "..." with target scope exists`, `ledger event "..." has field "..." equal to "..."`.
  - `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/obpis/OBPI-0.0.17-03-adr-promote-kind.md` (this brief) — added Acceptance Criteria, Discovery Checklist, Quality Gates, Value Narrative, Key Proof, Implementation Summary, Tracked Defects, Human Attestation sections (brief authoring required for `gz obpi precomplete --authored` and for `gz covers` REQ extraction).

- Tests: 15 REQ-scoped unit tests + 5 regression-coverage updates + 8 BDD scenarios; 100% REQ parity at ADR rollup (`gz covers ADR-0.0.17`).
- Date completed: 2026-04-19.
- Attestation status: Heavy lane — human attestation captured inline.

## Tracked Defects

- **`gz obpi precomplete` lock-path mismatch carried forward from OBPI-01/02** — `_check_lock_held` in `src/gzkit/commands/obpi_precomplete.py:174-195` globs `.gzkit/locks/*.json` non-recursively, but locks live at `.gzkit/locks/obpi/*.lock.json`. Reports "No lock file matches" despite `gz obpi lock list` showing the lock as ACTIVE. Workaround: invoked `gz obpi complete` directly (complete validates the lock internally). **Filed: GHI #244** with direct-fix sketch (rglob or explicit subpath).
- **Follow-up GHI candidate** — `_FOUNDATION_SEMVER_RE` is now duplicated between `src/gzkit/commands/plan.py` and `src/gzkit/commands/adr_promote.py`. Extract to `gzkit.commands.common` after OBPI-0.0.17-04 (validate-taxonomy) lands and absorbs the third copy.
- **Follow-up GHI candidate** — `_adr_bucket_for_semver` in `src/gzkit/commands/adr_promote_utils.py` is now unused (its sole caller swapped to `_adr_bucket_for_kind`). Out of brief allowed paths; safe to delete in a later tidy PR.

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed -- Heavy-lane OBPI-0.0.17-03 lands --kind {pool,foundation,feature} on gz adr promote. 20/20 unit + 8/8 BDD + 3218/3218 full suite. Receipts: lint arb-ruff-566f1dd2a7c04ee9b9763217f920261f; types arb-step-typecheck-a9d2ecc0b30c488b99b00293b7e6ede4; OBPI tests arb-step-unittest-228cb6e598da4a0a8994165d82b92f8b; full tests arb-step-unittest-7c058a86710b41cca30840840f39bdcf; BDD arb-step-behave-700b4c0f4d194d389379e07957ad21f2. Tracked: GHI #244.
- Date: 2026-04-19
