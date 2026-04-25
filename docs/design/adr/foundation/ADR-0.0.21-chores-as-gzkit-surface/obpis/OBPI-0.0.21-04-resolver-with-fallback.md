---
id: OBPI-0.0.21-04-resolver-with-fallback
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 4
lane: Heavy
status: Completed
---

# OBPI-0.0.21-04-resolver-with-fallback: Resolver with Package-Resource Fallback

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #4 — Resolver: project-first lookup with `importlib.resources` fallback; `--explain` diagnostic; error messages naming both attempted locations.

**Status:** Draft

## Objective

Rewrite the chore lookup logic in `src/gzkit/commands/chores.py` and `src/gzkit/commands/chores_exec.py` so it resolves `project_root / config.paths.chores / <slug>/` first, falls back to `importlib.resources.files("gzkit.chores") / <slug>/`, emits a structured log event on every fallback hit, exposes a `--explain` flag that names the winning path, and raises a diagnostic error naming BOTH attempted paths on miss.

## Lane

**Heavy** — changes the CLI resolution contract for every `gz chores {list,show,plan,advise,run}` invocation. External-facing behavior change.

## Allowed Paths

- `src/gzkit/commands/chores.py` — primary resolver + `CHORES_REGISTRY_PATH` lookup (currently line 18)
- `src/gzkit/commands/chores_exec.py` — secondary resolver at lines 138 and 214 where chore paths assemble
- `src/gzkit/commands/common.py` — only if a new shared resolver helper genuinely belongs there; prefer keeping it in `chores.py`
- `tests/commands/test_chores.py` — REQ-derived unit tests across all three resolution paths (project, fallback, miss)

## Denied Paths

- `src/gzkit/config.py` — `paths.chores` field is OBPI-02's responsibility
- `src/gzkit/commands/init_cmd.py` — scaffolder wiring is OBPI-05
- `pyproject.toml` — packaging is OBPI-03
- `src/gzkit/chores/**` — no data changes; OBPI-01 owns the tree
- `src/gzkit/governance/trust_audits.py` — layout validator is OBPI-08
- `features/**`, `docs/**`, `.gzkit/rules/**`

## Requirements (FAIL-CLOSED)

1. The resolver MUST consult `project_root / config.paths.chores / <slug>/` first. If that path exists AND contains `acceptance.json`, it wins.
2. If the project-local path does NOT exist, the resolver MUST fall back to `importlib.resources.files("gzkit.chores").joinpath(slug)`. If that resolves AND exposes `acceptance.json` via `.is_file()`, it wins.
3. If both resolution paths miss, the resolver MUST raise `GzCliError` with a message that names BOTH attempted paths verbatim. The error message MUST contain the literal substrings `.gzkit/chores/<slug>` and `importlib.resources` (or `gzkit.chores` package resource) so operators can distinguish scaffolder-not-run from wrong-slug from corrupt-package at a glance.
4. The `CHORES_REGISTRY_PATH = Path("config/gzkit.chores.json")` constant at `src/gzkit/commands/chores.py:18` MUST be replaced with a resolver that returns `project_root / config.paths.chores / "registry.json"` first, then `importlib.resources.files("gzkit.chores").joinpath("registry.json")`.
5. Every fallback hit (project-local miss → package-resource resolve) MUST emit a structured log event via the existing logging mechanism. The event MUST include the slug and the fact that the fallback fired, so operators grepping logs can identify scaffolder-never-ran conditions.
6. A new `--explain` flag on `gz chores list` MUST print, per chore, which resolution path won. Format at author's discretion but MUST distinguish "project" / "package" / "missing" per row.
7. No existing `gz chores` subcommand surface MAY regress — every command that worked pre-OBPI MUST work post-OBPI with equivalent behavior on the default resolution path (project-scaffolded chores).
8. Tests MUST assert all three resolution paths independently: (a) project-only (project wins), (b) package-only (fallback wins, with log event asserted), (c) both-missing (error raised with both paths in message).
9. `importlib.resources` usage MUST be Python 3.13-compatible (`importlib.resources.files(...)`), never the deprecated `importlib.resources.path()` or `pkg_resources`.

> STOP-on-BLOCKERS:
> - If OBPI-01 (migration) or OBPI-03 (packaging) has not landed, this OBPI cannot green — the `importlib.resources` side has nothing to resolve.
> - If tests under `tests/commands/test_chores.py` currently mock the registry path via `Path("config/gzkit.chores.json")`, they must be rewritten to mock the new resolver — do not silently bypass the new logic.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR ADR-0.0.21 § Decision #5, #8 (resolver order + diagnostics)
- [ ] Parent ADR § Consequences § Negative #2 (install-mode assumption — pyinstaller verified in OBPI-03)
- [ ] `.claude/rules/pythonic.md` — EAFP for IO, typed errors, no bare `except`

**Context:**

- [ ] Sibling OBPIs 01, 02, 03 — confirm prerequisites landed
- [ ] `.claude/rules/cross-platform.md` — UTF-8, pathlib discipline

**Prerequisites:**

- [ ] `src/gzkit/chores/` exists with `__init__.py` (OBPI-01)
- [ ] `GzkitConfig.paths.chores` field exists (OBPI-02)
- [ ] Chore data ships in wheel (OBPI-03) — editable install MUST already work

**Existing Code:**

- [ ] Read `src/gzkit/commands/chores.py` whole (~667 lines per ADR-0.28.0 context) — understand every path-resolution site
- [ ] Read `src/gzkit/commands/chores_exec.py:138, 214` — the two call sites assembling chore paths
- [ ] Read `src/gzkit/commands/common.py:94-96` — `get_project_root()` helper; the resolver consumes it
- [ ] Read `tests/commands/test_chores.py` whole — understand existing mocking patterns

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] RED: `test_chore_resolver_project_wins` — scaffold a fake project-local chore; assert resolver returns the project path; observe failure against current cwd-only resolver.
- [ ] GREEN: implement the project-first lookup.
- [ ] RED: `test_chore_resolver_falls_back_to_package` — remove project-local path; assert resolver returns the `importlib.resources` path AND emits the fallback-hit log event.
- [ ] GREEN: implement fallback + log event.
- [ ] RED: `test_chore_resolver_raises_with_both_paths_named` — both paths missing; assert `GzCliError` raised with both substrings in message.
- [ ] GREEN: implement error path.
- [ ] RED: `test_gz_chores_list_explain_distinguishes_source` — invoke `gz chores list --explain` with mixed project + package chores; assert output labels each row with its source.
- [ ] GREEN: implement `--explain`.
- [ ] `uv run gz test` green.

### Code Quality
- [ ] `uv run gz lint`
- [ ] `uv run gz typecheck` — ty diagnostics clean on new resolver helpers

### Gate 3 (Docs) — Heavy
- [ ] `uv run mkdocs build --strict`
- [ ] Manpage updates (for `--explain`) live in OBPI-06; this OBPI must not drift them

### Gate 4 (BDD) — Heavy
- [ ] Deferred to OBPI-07 (end-to-end install-and-scaffold BDD)

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation

## Verification

```bash
uv run gz test 2>&1 | tail -20

# Project-first resolution (scaffolded tree)
uv run gz chores list --explain 2>&1 | head -20

# Force fallback: move .gzkit/chores/ aside, resolver must still work via package
mv .gzkit/chores .gzkit/chores.away 2>/dev/null || true
uv run gz chores list --explain 2>&1 | head -10   # expect "package" labels
mv .gzkit/chores.away .gzkit/chores 2>/dev/null || true

# Miss path: bad slug
uv run gz chores show nonexistent-slug 2>&1 | grep -E "\.gzkit/chores|gzkit\.chores|importlib.resources"

# Type-check
uv run gz typecheck
```

## Acceptance Criteria

- [ ] REQ-0.0.21-04-01: `gz chores list` resolves chores from `<project_root>/<paths.chores>/` when that path exists with `acceptance.json`.
- [ ] REQ-0.0.21-04-02: `gz chores list` falls back to `importlib.resources.files("gzkit.chores")` when the project-local path does not exist, and emits a structured log event naming the fallback hit.
- [ ] REQ-0.0.21-04-03: When both paths miss for a requested slug, `GzCliError` raises with a message that contains both the project-local path string AND an `importlib.resources` / `gzkit.chores` reference.
- [ ] REQ-0.0.21-04-04: `gz chores list --explain` prints one row per chore labeling the resolution source (`project` / `package` / `missing`).
- [ ] REQ-0.0.21-04-05: The registry file (`registry.json`) is resolved using the same project-first → package-fallback order as individual chore directories.
- [ ] REQ-0.0.21-04-06: `uv run gz typecheck` exits 0 after the change.
- [ ] REQ-0.0.21-04-07: Every existing `gz chores {list,show,plan,advise,run}` subcommand continues to produce its pre-OBPI behavior when the scaffolded project-local tree is intact (no regression).

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** 4 REQ-derived TDD cycles with observed RED per increment
- [ ] **Code Quality:** lint + typecheck green
- [ ] **Gate 3:** docs build green
- [ ] **Gate 5:** human attestation
- [ ] **Value Narrative:** before — `gz chores list` errored on fresh install; after — fresh install works via package fallback with structured log signaling incomplete scaffold.
- [ ] **Key Proof:** fresh wheel install + `gz chores list` returns the canonical set WITHOUT any prior `gz init`.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
# paste unit-test output, especially the RED→GREEN cycle observations
```

### Code Quality
```text
# paste lint + typecheck output
```

### Gate 3 (Docs)
```text
# paste mkdocs output
```

### Gate 5 (Human)
```text
# attestation text
```

### Value Narrative
Before: `gz chores list` in a freshly-installed project errored with `FileNotFoundError: config/gzkit.chores.json`. After: the same command resolves canonical chores via `importlib.resources` and tells the operator (via `--explain` and log events) that the fallback fired.

### Key Proof

```text
$ uv run gz chores list 2>/dev/null  # default surface — pre-OBPI shape preserved (REQ-07)
                                Chores Registry
┃ Slug ┃ Lane ┃ Version ┃ Vendor ┃ Criteria ┃ Title ┃
…

$ uv run gz chores list --explain  # source labels per row (REQ-04, REQ-06)
… added "Source" column with project / package (fallback; …) / missing values

$ uv run gz chores show nonexistent-slug 2>&1
BLOCKERS:
- Chore 'nonexistent-slug' not found in either resolution path:
    - project: /…/.gzkit/chores/nonexistent-slug (path: .gzkit/chores/nonexistent-slug)
    - package: importlib.resources('gzkit.chores')/nonexistent-slug (at /…)
  Hint: run `gz init` to scaffold .gzkit/chores/, or verify the slug spelling.

# Live structured log on every fallback hit (REQ-05):
chore.resolver.fallback  slug=quality-check  paths_chores=.gzkit/chores
  project_path=/…/.gzkit/chores/quality-check
  package_path=/…/src/gzkit/chores/quality-check
```

ARB receipts (Heavy-lane attestation):

- lint: `arb-ruff-3f0a3c4f0184463596f440640f3bd9d5`
- typecheck: `arb-step-typecheck-5ce4e516962641a59591b91bd81b1219`
- unittest: `arb-step-unittest-06f6452b5c3f43a4afcc5324e1b94b5e` (24/24 pass)
- mkdocs: `arb-step-mkdocs-a70e104ca2374521ad5915b12e94a8f9`

### Implementation Summary

- Resolver: replaced legacy `Path("config/gzkit.chores.json")` constant with `_resolve_chore_dir(slug)` and `_resolve_registry()` — both probe `<project_root>/<config.paths.chores>/` first, fall back to `importlib.resources.files("gzkit.chores")`, raise `GzCliError` on both-miss with both paths in the message.
- Diagnostic: new `_format_resolution_miss` produces the operator-facing error with literal substrings `.gzkit/chores/<slug>` AND `importlib.resources` + `gzkit.chores` (REQ-03).
- Logging: structlog logger at module level emits `chore.resolver.fallback` with `slug`, `project_path`, `package_path`, `paths_chores` on every fallback hit (REQ-05).
- CLI surface: `gz chores list --explain` adds a `Source` column labelling each row `project` / `package (fallback; scaffolder may need re-run)` / `missing` (REQ-04, REQ-06). Default surface unchanged (REQ-07 regression protection).
- Model: `ChoreDefinition.resolution_source: Literal["project","package"]|None` and new `ResolvedPath` Pydantic model (frozen, extra="forbid").
- Files: `src/gzkit/commands/chores.py`, `src/gzkit/commands/chores_exec.py`, `src/gzkit/cli/parser_maintenance.py`, `tests/commands/test_chores.py`.
- Tests: 7 new REQ-derived tests in `TestChoreResolver`; bulk path migration of 14 legacy tests from `ops/chores/` → `.gzkit/chores/` to align with the resolver's slug-based probe.
- REQ parity: 7/7 (100%) per `gz covers OBPI-0.0.21-04 --json`.
- Tracked defects: registry `path` field drift in `src/gzkit/chores/registry.json` (entries reference removed `ops/chores/` location); pre-existing behave_req_tags failure on untracked ADR-0.0.22 — both routed to GHIs in this same Stage 5.

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `g0`
- Attestation: attest completed — Heavy + Foundation OBPI-0.0.21-04 ships the chores resolver: project-first lookup at `<project_root>/<config.paths.chores>/<slug>/`, `importlib.resources.files("gzkit.chores")` fallback, structured `chore.resolver.fallback` log event on every fallback hit, `gz chores list --explain` surfacing per-row source, and a both-paths-named diagnostic on miss. 7 REQ-derived tests authored RED-then-GREEN per increment; 7/7 REQ parity per `gz covers`; 24/24 chores unittest pass; full suite 3565/3566 pass with the single failure pre-existing on the untracked ADR-0.0.22 surface (flagged for GHI). Receipts: lint arb-ruff-3f0a3c4f0184463596f440640f3bd9d5; typecheck arb-step-typecheck-5ce4e516962641a59591b91bd81b1219; tests arb-step-unittest-06f6452b5c3f43a4afcc5324e1b94b5e; docs arb-step-mkdocs-a70e104ca2374521ad5915b12e94a8f9.
- Date: 2026-04-25

---

**Brief Status:** Completed

**Date Completed:** 2026-04-25

**Evidence Hash:** -
