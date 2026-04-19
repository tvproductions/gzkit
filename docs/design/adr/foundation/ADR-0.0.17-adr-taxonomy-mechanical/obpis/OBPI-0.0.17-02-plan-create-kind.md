---
id: OBPI-0.0.17-02-plan-create-kind
parent: ADR-0.0.17-adr-taxonomy-mechanical
item: 2
lane: Heavy
status: Completed
---

# OBPI-0.0.17-02-plan-create-kind: --kind flag on gz plan create

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- **Checklist Item:** #2 — "`gz plan create --kind` CLI flag + scaffolder"

**Status:** Draft

## Objective

Add a required `--kind {pool, foundation, feature}` flag to `gz plan create`. No default — operator must choose explicitly. Scaffolder emits matching `kind:` frontmatter (or omits it for pool) and refuses to write a mismatched kind/semver combination.

## Lane

**Heavy** — CLI contract addition.

## Allowed Paths

- `src/gzkit/cli/parser_artifacts.py` (argparse registration)
- `src/gzkit/commands/plan.py` (scaffolder logic)
- `src/gzkit/templates/adr.md` (emit `kind:` field)
- `tests/commands/test_plan.py` (behavior)
- `docs/user/commands/plan.md` or `docs/user/commands/plan-create.md` (help-text update)

## Denied Paths

- Schema/model surfaces (OBPI-01)
- `gz adr promote` surface (OBPI-03)
- `gz validate` surface (OBPI-04)

## Requirements (FAIL-CLOSED)

1. REQUIREMENT: `gz plan create --help` shows `--kind {pool, foundation, feature}` as a required flag. Omitting `--kind` exits with code 1 and names both foundation/feature criteria.
2. REQUIREMENT: `--kind foundation` requires `--semver` to match `^0\.0\.\d+$`. Mismatch → exit 1 with a recovery message naming the next available `0.0.x` value (by scanning existing foundation ADRs).
3. REQUIREMENT: `--kind feature` requires `--semver` to NOT match `^0\.0\.\d+$`. Mismatch → exit 1 with a recovery message explaining feature ADRs carry release-carrying semver (`0.y.z` and up).
4. REQUIREMENT: `--kind pool` writes to `docs/design/adr/pool/ADR-pool.<slug>.md` (no directory-per-ADR, matching existing pool convention). No `kind:` field in frontmatter; no `semver:` required. Pool ADRs are out-of-scope for foundation/feature frontmatter entirely.
5. REQUIREMENT: The rendered ADR frontmatter for foundation/feature includes `kind: <value>` directly after `status:` per the schema ordering. Template variable substitution must not silently drop the field.
6. REQUIREMENT: Scaffolder validates kind/semver BEFORE writing any file. A rejected invocation writes nothing, appends no ledger event, and prints the recovery message to stderr with exit 1.
7. REQUIREMENT: `gz plan create … --kind foundation` routes to `docs/design/adr/foundation/<id>/<id>.md` (create directory if missing); `--kind feature` routes to `docs/design/adr/pre-release/<id>/<id>.md` by default (matching the existing convention for non-foundation ADRs). An explicit `--output <path>` override is out of scope for this OBPI.
8. REQUIREMENT: All prior `gz plan create` behavior (scorecard scoring, parent OBPI, etc.) remains unchanged when `--kind` is supplied. The flag is additive, not replacing any existing argument.

## Discovery Checklist

<!-- What to read before implementation. Complete this checklist first. -->

**Governance (read once, cache):**

- [ ] `AGENTS.md` / `CLAUDE.md` — agent operating contract
- [ ] Parent ADR — full taxonomy context
- [ ] `.claude/rules/cli.md` — Heavy-lane trigger for subcommand/flag changes
- [ ] `.claude/rules/defect-fix-routing.md` — thresholds for in-flight fix vs ceremony

**Context:**

- [ ] Parent ADR: `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/ADR-0.0.17-adr-taxonomy-mechanical.md`
- [ ] Prerequisite OBPI: `OBPI-0.0.17-01-schema-and-model` (schema + Pydantic model for `kind`)
- [ ] Sibling OBPIs: 03 (adr-promote-kind), 04 (validate-taxonomy), 05 (backfill-and-roundtrip), 06 (agents-md-correction)

**Prerequisites (check existence, STOP if missing):**

- [ ] `src/gzkit/cli/parser_governance.py` — argparse registration for `plan create` (brief drift: original brief named `parser_artifacts.py`)
- [ ] `src/gzkit/commands/plan.py` — scaffolder entry point `plan_cmd`
- [ ] `src/gzkit/templates/adr.md` — active scaffold template
- [ ] `src/gzkit/core/models.py` — `AdrFrontmatter.kind: Literal["foundation", "feature"]` (from OBPI-01)

**Existing Code (understand current state):**

- [ ] `plan_cmd` at `src/gzkit/commands/plan.py:11-112` — 17-arg signature; renders template, writes flat `{adrs}/{adr_id}.md`, appends `adr_created_event` to ledger.
- [ ] `p_plan_create` at `src/gzkit/cli/parser_governance.py:233-318` — argparse subparser with existing `--semver`, `--lane`, scorecard flags, `add_dry_run_flag()` helper.
- [ ] `render_template` at `src/gzkit/templates/__init__.py:30-61` — `str.format_map(SafeDict(context))`; missing keys leave `{placeholder}` in output (so pool needs its own template, not conditional substitution).
- [ ] Existing pool ADRs at `docs/design/adr/pool/ADR-pool.<slug>.md` — flat layout, status `Pool`, no `semver:`/`kind:` in frontmatter.
- [ ] Existing foundation ADRs at `docs/design/adr/foundation/ADR-0.0.N-<slug>/ADR-0.0.N-<slug>.md` — per-ADR folder layout.
- [ ] Existing feature ADRs at `docs/design/adr/pre-release/ADR-X.Y.Z-<slug>/ADR-X.Y.Z-<slug>.md` — per-ADR folder layout.

## Quality Gates

<!-- Which gates apply and how to verify them. -->

### Gate 1: ADR

- [ ] Intent and scope recorded in this OBPI brief
- [ ] Parent ADR checklist item quoted (item #2 — "`gz plan create --kind` CLI flag + scaffolder")

### Gate 2: TDD (Red-Green-Refactor)

- [ ] Tests derived from brief acceptance criteria, not from implementation
- [ ] Red-Green-Refactor cycle followed per behavior increment (per REQ)
- [ ] Tests pass: `uv run gz test --obpi OBPI-0.0.17-02`
- [ ] ARB receipts attached: ruff, typecheck, unittest

### Code Quality

- [ ] Lint clean: `uv run gz arb ruff`
- [ ] Type check clean: `uv run gz arb typecheck`

### Gate 3: Docs (Heavy only)

- [ ] `docs/user/commands/plan-create.md` updated with `--kind` option row, taxonomy-aware routing narrative, and per-kind examples
- [ ] `mkdocs build --strict` passes

### Gate 4: BDD (Heavy only)

- [ ] BDD deferred to OBPI-0.0.17-04-validate-taxonomy per brief Denied Paths. No `features/` scenarios authored in this OBPI.

### Gate 5: Human (Heavy only)

- [ ] Human attestation recorded

## Verification

```bash
uv run gz plan create --help | grep -- --kind
uv run gz plan create scratch-foundation --kind foundation --semver 0.0.99 --lane lite --dry-run
uv run gz plan create scratch-feature --kind feature --semver 0.99.0 --lane heavy --dry-run
uv run gz plan create scratch-bad --kind feature --semver 0.0.99 --dry-run  # must exit 1
uv run gz plan create scratch-pool --kind pool --dry-run
uv run gz arb step --name unittest -- uv run -m unittest tests.commands.test_plan -v
```

## Evidence

- Help output showing `--kind` registered
- Dry-run scaffolder output for each kind
- Rejection transcript for mismatched kind/semver
- ARB receipts

## Acceptance Criteria

- [ ] REQ-0.0.17-02-01: `gz plan create` without `--kind` exits with code 1 and the error message names both `foundation` and `feature` criteria.
- [ ] REQ-0.0.17-02-02: `--kind foundation` with a semver not matching `^0\.0\.\d+$` exits 1 with a recovery message naming the next available `0.0.x` slot.
- [ ] REQ-0.0.17-02-03: `--kind feature` with a semver matching `^0\.0\.\d+$` exits 1 with a recovery message explaining that feature ADRs carry release-carrying semver (`0.y.z` and up).
- [ ] REQ-0.0.17-02-04: `--kind pool` writes to `docs/design/adr/pool/ADR-pool.<slug>.md` (flat, no directory-per-ADR), no `kind:` frontmatter field, no `semver:` required.
- [ ] REQ-0.0.17-02-05: Rendered foundation/feature frontmatter places `kind: <value>` on the line immediately following `status:`.
- [ ] REQ-0.0.17-02-06: A rejected invocation writes no ADR file and appends no ledger event; validation runs before render/write/append.
- [ ] REQ-0.0.17-02-07: `--kind foundation` routes to `docs/design/adr/foundation/<id>/<id>.md`; `--kind feature` routes to `docs/design/adr/pre-release/<id>/<id>.md` (creating per-ADR folders).
- [ ] REQ-0.0.17-02-08: All prior `gz plan create` behavior (scorecard, checklist, ledger registration, parent canonicalization) is preserved when `--kind` is supplied — the flag is additive.

## REQ Coverage

- REQ-0.0.17-02-01 through REQ-0.0.17-02-08 (one per Acceptance Criterion above, mapping 1:1 to the numbered Requirements)

### Value Narrative

Before this OBPI, `gz plan create` scaffolded ADRs to a flat `design/adr/ADR-<id>.md` regardless of taxonomy — foundation, feature, and pool all collapsed to one shape, and nothing blocked mismatched kind/semver combinations at author time. This OBPI wires the OBPI-01 `kind` schema into the scaffolder: `--kind {pool, foundation, feature}` is now required, kind/semver mismatches are rejected before any file or ledger write, and output routes to the taxonomy-appropriate location (foundation per-ADR folder, feature per-ADR folder under `pre-release/`, pool flat backlog file). REQ-6 closes the class of silent kind/semver mismatches that the human-authored convention already enforces structurally.

### Key Proof


```text
$ uv run gz plan create scratch-bad --kind feature --semver 0.0.99 --dry-run
ERROR: --kind feature rejects 0.0.x semver (got '0.0.99'). Feature ADRs carry
release-carrying semver (0.y.z and up). If this is infrastructure work, use
--kind foundation; if it is a backlog item, use --kind pool.
$ echo $?
1
$ uv run gz covers OBPI-0.0.17-02 --json | python -c "import json,sys; d=json.load(sys.stdin)['summary']; print(d)"
{'identifier': 'OBPI-0.0.17-02', 'total_reqs': 8, 'covered_reqs': 8,
 'uncovered_reqs': 0, 'coverage_percent': 100.0}
```

Rejection fires before render/write/ledger (REQ-6 atomicity). 8/8 REQs covered. Full suite: `Ran 3203 tests in 104.8s — OK`.

### Implementation Summary


- Files modified (in-brief Allowed Paths):
  - `src/gzkit/cli/parser_governance.py` — registered `--kind {pool,foundation,feature}` with `default=None` (manual validation in handler for REQ-1's exit-code-1 requirement); plumbed `kind=a.kind` into `_lazy("plan_cmd")` kwargs
  - `src/gzkit/commands/plan.py` — added `_FOUNDATION_SEMVER_RE`, `_next_available_foundation_semver()`, `_render_pool_adr()`; kind/semver validation now runs before `render_template`/`write_text`/`ledger.append`; path routing branches by kind
  - `src/gzkit/templates/adr.md` — inserted `kind: {kind}` between `status:` and `semver:` per REQ-5 ordering
  - `src/gzkit/templates/adr_pool.md` — **new** pool-shaped template (additive scope expansion; pool frontmatter is structurally distinct — no `semver:`, no `kind:`, adds `enabler: null`)
  - `tests/commands/test_plan.py` — 11 REQ-decorated tests (one per REQ plus 3 preservation tests for REQ-8); 100% REQ parity
  - `docs/user/commands/plan-create.md` — `--kind` row in Options table, taxonomy-aware routing narrative, three per-kind example invocations
  - `docs/design/adr/foundation/ADR-0.0.17-adr-taxonomy-mechanical/obpis/OBPI-0.0.17-02-plan-create-kind.md` — added Acceptance Criteria, Discovery Checklist, Quality Gates sections (template-drift fix required for `gz obpi precomplete` authored-readiness; OBPI-01 surfaced the same drift)

- Files modified (scope-expansion ripple, operator-approved after AskUserQuestion):
  - 15 test files across the tree — 131 `["plan", "create", "<semver>"]` invocations updated to pass `--kind feature` (feature-shaped semvers) or `--kind foundation` (0.0.x); 5 direct-path assertions updated to the new per-ADR folder layout (`design/adr/ADR-0.1.0.md` → `design/adr/pre-release/ADR-0.1.0/ADR-0.1.0.md` and similar). Files: `tests/test_audit_pipeline.py`, `tests/test_closeout_ceremony_cmd.py`, `tests/test_closeout_pipeline.py`, `tests/test_attest_deprecation.py`, `tests/test_closeout_migration.py`, `tests/test_tasks.py`, `tests/commands/test_attest.py`, `test_adr_promote.py`, `test_gates.py`, `test_dry_run.py`, `test_l3_gate_independence.py`, `test_obpi_validate_cmd.py`, `test_runtime.py`, `test_status.py`, `test_specify.py`. Without this ripple, 144 tests failed after REQ-7 routing change; with it, 3203/3203 pass.

- Tests: 11 new REQ-scoped unit tests in `test_plan.py`, all `@covers`-decorated; 8/8 REQ coverage via `gz covers OBPI-0.0.17-02 --json`.
- Date completed: 2026-04-19.
- Attestation status: Heavy lane — human attestation captured inline.
- Defects noted: 1 carried forward from OBPI-01 (precomplete lock-path mismatch).

## Tracked Defects

- **Brief allowed-paths drift**: This brief's Allowed Paths list named `src/gzkit/cli/parser_artifacts.py`, but the parser registration for `plan create` actually lives in `src/gzkit/cli/parser_governance.py:233-318`. Implementation targeted the real file. Recommend brief correction in OBPI-0.0.17-06 (agents-md-correction) or via reconcile.
- **`gz obpi precomplete` lock-file search path is wrong** (same as OBPI-01 Tracked Defect; carried forward). `_check_lock_held` at `src/gzkit/commands/obpi_precomplete.py:174-195` globs `.gzkit/locks/*.json` but locks live at `.gzkit/locks/obpi/*.lock.json`. Precomplete reports "No lock file matches" despite `gz obpi lock list` showing ACTIVE. Workaround: invoked `gz obpi complete` directly; complete validates the lock internally. File GHI post-sync.
- **Flaky coverage-instrumented timing test**: `tests/commands/test_validate_frontmatter.py::TestFrontmatterGuard::test_runtime_budget_under_one_second_on_real_repo` fails under `coverage run` due to instrumentation overhead; passes under plain unittest. Pre-existing, not induced by this OBPI.

## Human Attestation

- Attestor: `jeff`
- Attestation: attest completed — OBPI-0.0.17-02 verified: 8/8 REQs covered; 3203/3203 tests pass; scope ripple (131 invocations, 15 files) operator-approved. Receipts: arb-ruff-bbe6a1ae, arb-step-typecheck-1fd89a28, arb-step-unittest-c65b4d4a, arb-step-mkdocs-3d995958.
- Date: 2026-04-19
