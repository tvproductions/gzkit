---
id: OBPI-0.0.21-05-scaffold-core-chores
parent: ADR-0.0.21-chores-as-gzkit-surface
item: 5
lane: Heavy
status: Draft
---

# OBPI-0.0.21-05-scaffold-core-chores: Scaffolder for .gzkit/chores/

## ADR Item

- **Source ADR:** `docs/design/adr/foundation/ADR-0.0.21-chores-as-gzkit-surface/ADR-0.0.21-chores-as-gzkit-surface.md`
- **Checklist Item:** #5 — Scaffolder: implement `scaffold_core_chores(project_root, config, skip_existing=...)` mirroring `scaffold_core_skills`; wire into `init_cmd.py`; implement registry-merge contract on repair.

**Status:** Draft

## Objective

Add a new `scaffold_core_chores(project_root, config, skip_existing=False)` function that copies the canonical chore tree from `importlib.resources.files("gzkit.chores")` into `project_root / config.paths.chores`, wire it into `gz init` (first-run + repair mode) at the same call sites as `scaffold_core_skills`, and implement the ADR's registry-merge contract so upgrades never silently clobber project-local chores.

## Lane

**Heavy** — changes the `gz init` behavior (external CLI contract) and introduces a new module-level function consumed by a downstream OBPI (OBPI-07's BDD proof).

## Allowed Paths

- `src/gzkit/chores.py` — new module at this path (module-level `scaffold_core_chores` function, mirroring `src/gzkit/skills.py:302-338` shape). Keeping chores-scaffolding out of `commands/chores.py` preserves the CLI-vs-library boundary.
- `src/gzkit/commands/init_cmd.py` — import and call `scaffold_core_chores` at the same sites as `scaffold_core_skills` (lines 281, 472 per pre-reading)
- `tests/commands/test_init.py` — REQ-derived unit tests covering fresh scaffold, skip-existing semantics, and registry-merge behavior
- `tests/test_chores_scaffold.py` — optional new test module if `test_init.py` becomes >600 lines (per `.claude/rules/pythonic.md` size limit)

## Denied Paths

- `src/gzkit/commands/chores.py` — resolver is OBPI-04; scaffolder is a sibling library, not a CLI subcommand
- `src/gzkit/config.py` — `paths.chores` field is OBPI-02
- `pyproject.toml` — packaging is OBPI-03
- `src/gzkit/chores/**` — canonical tree is OBPI-01
- `features/**` — BDD is OBPI-07
- `src/gzkit/governance/trust_audits.py` — layout validator is OBPI-08

## Requirements (FAIL-CLOSED)

1. `scaffold_core_chores` MUST have the exact signature `(project_root: Path, config: GzkitConfig | None = None, *, skip_existing: bool = False) -> list[Path]`, matching `scaffold_core_skills` at `src/gzkit/skills.py:302-307`.
2. When `skip_existing=False` (first-run path), the function MUST copy every `<slug>/{CHORE.md, acceptance.json, README.md}` file from the package resource into `project_root / config.paths.chores / <slug>/`. `proofs/` subdirectories in the canonical tree MUST NOT be copied (proofs are project-local runtime state, generated on demand).
3. When `skip_existing=True` (repair path), the function MUST leave any `<slug>/` directory that already exists on disk untouched — operator modifications to `.gzkit/chores/<slug>/CHORE.md` are never clobbered.
4. Registry merge (per ADR Decision #6): when a project-local `registry.json` already exists and gzkit ships new canonical chore slugs on upgrade, `gz init --repair` MUST:
    - (a) read the canonical `registry.json` from `importlib.resources`,
    - (b) read the project-local `registry.json`,
    - (c) compute the union with canonical-wins-on-shipped-slug, local-wins-on-unknown-slug,
    - (d) print a diff (added/removed/changed slugs) to stdout,
    - (e) unless `--yes` is passed, prompt before writing,
    - (f) write the merged registry only after explicit confirmation.
5. `scaffold_core_chores` MUST be called from `init_cmd.py` at the same two sites where `scaffold_core_skills` is called: once in the main `init` path (OBPI implementer: confirm line; pre-reading shows ~472) and once in the repair path (pre-reading shows ~281) with `skip_existing=not dry_run`.
6. The function MUST use `importlib.resources.files("gzkit.chores")` as its canonical source. It MUST NOT accept a filesystem-path source argument — preventing the common mistake of developers scaffolding from gzkit's working tree in editable mode (which would be correct by accident but wrong in principle, because the source-of-truth is the package resource).
7. `proofs/` directories in the destination MUST be preserved across repair runs — if `.gzkit/chores/<slug>/proofs/` exists before repair, it exists after repair byte-identical.
8. The function MUST emit one log event per scaffolded slug so `gz init --verbose` shows the full list, matching `scaffold_core_skills`'s existing pattern.
9. Tests MUST cover: (a) fresh scaffold creates all canonical slugs; (b) `skip_existing=True` leaves existing content intact; (c) proofs preservation; (d) registry-merge diff output on canonical/local divergence; (e) `--yes` bypasses the prompt.

> STOP-on-BLOCKERS:
> - If OBPI-01 (`src/gzkit/chores/__init__.py`) or OBPI-03 (packaging) has not landed, `importlib.resources.files("gzkit.chores")` returns nothing — scaffolder has no source.
> - If OBPI-02 (`paths.chores`) has not landed, the scaffolder cannot resolve its destination.

## Discovery Checklist

**Governance (read once, cache):**

- [ ] Parent ADR ADR-0.0.21 § Decision #3, #6 (scaffolder contract, registry merge)
- [ ] `.claude/rules/tests.md` § Unit-tier contract (tempdir discipline, subprocess mocking)

**Context:**

- [ ] Sibling OBPIs 01, 02, 03, 04 — prerequisites for this one

**Prerequisites:**

- [ ] `src/gzkit/chores/__init__.py` exists (OBPI-01)
- [ ] `GzkitConfig.paths.chores` exists (OBPI-02)
- [ ] Canonical chores ship in wheel (OBPI-03, editable install verified)

**Existing Code:**

- [ ] Read `src/gzkit/skills.py:280-340` whole — `scaffold_core_skills` is the load-bearing exemplar
- [ ] Read `src/gzkit/personas.py` — `scaffold_default_personas` pattern variant
- [ ] Read `src/gzkit/commands/init_cmd.py:25-30` (imports), `:275-300` (repair path), `:460-480` (main init path)
- [ ] Read `tests/commands/test_init.py` whole — understand existing `_uv_sync_patcher` / `_quick_init` helper usage

## Quality Gates

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD — Red-Green-Refactor)
- [ ] RED: `test_scaffold_core_chores_creates_canonical_slugs` — empty project dir, call `scaffold_core_chores(tmp, cfg)`, assert at least 3 representative slugs exist on disk. Observe RED (function not defined yet).
- [ ] GREEN: implement the function using `importlib.resources`.
- [ ] RED: `test_scaffold_core_chores_skip_existing_preserves_operator_edits` — pre-populate `tmp/.gzkit/chores/<slug>/CHORE.md` with custom content; call with `skip_existing=True`; assert file content preserved.
- [ ] GREEN: implement the skip_existing branch.
- [ ] RED: `test_scaffold_core_chores_preserves_proofs` — pre-populate `tmp/.gzkit/chores/<slug>/proofs/evidence.txt`; call scaffolder (either mode); assert proofs preserved.
- [ ] GREEN: add proofs-preservation guard.
- [ ] RED: `test_registry_merge_reports_diff_on_upgrade` — divergent canonical + local registries; assert merge output contains the added slugs.
- [ ] GREEN: implement merge logic.
- [ ] RED: `test_gz_init_invokes_scaffold_core_chores` — mock `scaffold_core_chores`; run `gz init`; assert called once with correct args.
- [ ] GREEN: wire into `init_cmd.py`.
- [ ] `uv run gz test` green.

### Code Quality
- [ ] `uv run gz lint`, `uv run gz typecheck`

### Gate 3 (Docs) — Heavy
- [ ] `uv run mkdocs build --strict`

### Gate 4 (BDD) — Heavy
- [ ] Deferred to OBPI-07 (end-to-end scenario)

### Gate 5 (Human) — Heavy + Foundation
- [ ] Brief-level human attestation

## Verification

```bash
uv run gz test

# Dry-run init in a scratch tempdir
mkdir -p /tmp/gz-scaffold-test && cd /tmp/gz-scaffold-test && uv run gz init --dry-run 2>&1 | grep -i chore

# Real init (in a throwaway dir)
uv run gz init 2>&1 | tail -10
ls .gzkit/chores/ | head

# Repair mode leaves operator edits intact
echo "OPERATOR EDIT" > .gzkit/chores/coverage-40pct/CHORE.md
uv run gz init --repair
grep "OPERATOR EDIT" .gzkit/chores/coverage-40pct/CHORE.md && echo "preserved"

# Type-check
uv run gz typecheck
```

## Acceptance Criteria

- [ ] REQ-0.0.21-05-01: `scaffold_core_chores(project_root, config)` on an empty project creates one directory per canonical chore slug under `project_root / config.paths.chores /`.
- [ ] REQ-0.0.21-05-02: `scaffold_core_chores(project_root, config, skip_existing=True)` leaves any existing `<slug>/` directory byte-identical.
- [ ] REQ-0.0.21-05-03: `scaffold_core_chores` never copies `proofs/` from the canonical source and never touches an existing `<slug>/proofs/` in the destination.
- [ ] REQ-0.0.21-05-04: `gz init --repair` against a project with a stale `registry.json` prints a diff of the canonical/local registries before writing, and honors `--yes` to suppress the interactive prompt.
- [ ] REQ-0.0.21-05-05: `scaffold_core_chores` is invoked from `init_cmd.py` at the same two sites where `scaffold_core_skills` is invoked.
- [ ] REQ-0.0.21-05-06: The function signature matches `(project_root: Path, config: GzkitConfig | None = None, *, skip_existing: bool = False) -> list[Path]`.
- [ ] REQ-0.0.21-05-07: The function emits one structured log event per scaffolded slug (verifiable by capturing log output in tests).

## Completion Checklist

- [ ] **Gate 1:** Intent recorded
- [ ] **Gate 2:** 5 REQ-derived TDD cycles
- [ ] **Code Quality:** lint + typecheck green
- [ ] **Gate 3:** docs build green
- [ ] **Gate 5:** human attestation
- [ ] **Value Narrative:** before — `.gzkit/chores/` did not exist in any consumer project; after — `gz init` scaffolds it the same way skills and personas land.
- [ ] **Key Proof:** fresh empty dir → `gz init` → `ls .gzkit/chores/` returns the canonical slug list.

## Evidence

### Gate 1 (ADR)
- [ ] Intent recorded

### Gate 2 (TDD)
```text
# paste test output, RED→GREEN observations
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
Before: downstream projects had no `.gzkit/chores/` surface and no way to author project-local chores alongside canonical ones. After: `gz init` scaffolds canonical chores into `.gzkit/chores/` with the same discipline as skills/personas, and repair mode merges registries without clobbering operator edits.

### Key Proof
```bash
$ cd $(mktemp -d) && uv run gz init
  Scaffolded skill: gz-adr-status
  Scaffolded chore: coverage-40pct
  Scaffolded chore: dependency-currency
  ...
$ ls .gzkit/chores/ | wc -l
33
```

### Implementation Summary
- Files created/modified: `src/gzkit/chores.py` (new), `src/gzkit/commands/init_cmd.py`, `tests/commands/test_init.py`
- Tests added: 5 REQ-derived
- Date completed:
- Attestation status:
- Defects noted:

## Tracked Defects

_No defects tracked._

## Human Attestation

- Attestor: `<name>`
- Attestation: `<verbatim user words> — <session-grounded enrichment>`
- Date: YYYY-MM-DD

---

**Brief Status:** Draft

**Date Completed:** -

**Evidence Hash:** -
