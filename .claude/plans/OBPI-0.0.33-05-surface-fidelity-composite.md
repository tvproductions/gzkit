# Plan: OBPI-0.0.33-05-surface-fidelity-composite

## OBPI
OBPI-0.0.33-05-surface-fidelity-composite

## ADR Item (verbatim)
"OBPI-0.0.33-05: Composite scope + CI wiring — `gz validate --surface-fidelity` runs all four; wired into `gz check`; cheap subset (1, 2, 3) in pre-commit; tests under `tests/governance/` per per-rule-file naming and the eval-awareness corollary"

## ADR Decision (verbatim)
"The Agent Control Surface preserves every binding rule from its canonical sources to its rendered output. Surface weight does not regress past tested floors. Pointers resolve. Bullets are reachable from the loading scenarios they should fire in. Drift in the rendered surface is detectable at compile time, not at audit time."

## Destination-in-mind
`validate_surface_fidelity` function in `trust_audits/__init__.py` calling all four validators in declared order (bullet_retention → surface_weight → pointer_integrity → scenario_reachability), aggregating their errors. CLI flag `--surface-fidelity` in parser_maintenance.py wired through validate_cmd.py. `run_surface_fidelity_audit` in quality.py added to `_build_check_steps()`. Pre-commit hook as single CLI call with three flags. Tests mock four validators via unittest.mock.patch.

## Rejected alternatives
- Dedicated `surface_fidelity.py` module: Allowed Paths lists `__init__.py` for composite wiring; redundant module level adds no separation value for pure glue code.
- Four separate subprocess calls in the composite: the function calls the Python-level validators directly, no subprocess overhead.
- Adding `--surface-fidelity` to default scopes (run-all): it's an explicit/opt-in composite same as `--advisor-proof-binding`; default scopes are individual document-level validators.

## Files in scope
- `src/gzkit/governance/trust_audits/__init__.py`
- `src/gzkit/cli/parser_maintenance.py`
- `src/gzkit/commands/validate_cmd.py`
- `src/gzkit/quality.py`
- `src/gzkit/commands/quality.py`
- `.pre-commit-config.yaml`
- `tests/governance/test_surface_fidelity_composite.py` (new)
- `docs/user/manpages/validate.md`
- `docs/user/manpages/check.md`

## Steps

### Step 1: TDD Red — Write failing tests

Create `tests/governance/test_surface_fidelity_composite.py` with tests derived from the 6 REQs:

- `TestSurfaceFidelityComposite.test_all_four_validators_fire_in_order` — REQ-0.0.33-05-01: mock all four validators, call `validate_surface_fidelity`, assert call order via `assert_has_calls`
- `TestSurfaceFidelityComposite.test_exit_code_worst_of_four` — REQ-0.0.33-05-02: mock bullet_retention to return one ValidationError(type="bullet_retention"), others clean; call composite; assert error list contains the bullet_retention error
- `TestSurfaceFidelityComposite.test_gz_check_includes_surface_fidelity` — REQ-0.0.33-05-03: import `_build_check_steps` from `gzkit.commands.quality`; assert any step tuple has name matching "Surface fidelity" or runner name matching `run_surface_fidelity_audit`
- `TestSurfaceFidelityComposite.test_precommit_cheap_subset_registration` — REQ-0.0.33-05-04: read `.pre-commit-config.yaml`; assert a hook entry contains `gz validate --bullet-retention --surface-weight --pointer-anchors`; assert no hook entry contains `--scenario-reachability`
- `TestSurfaceFidelityComposite.test_validate_manpage_documents_surface_fidelity` — REQ-0.0.33-05-05: read `docs/user/manpages/validate.md`; assert `--surface-fidelity` appears in the file
- `TestSurfaceFidelityComposite.test_validate_surface_fidelity_importable` — REQ-0.0.33-05-06: `from gzkit.governance.trust_audits import validate_surface_fidelity`; assert callable

### Step 2: Implement `validate_surface_fidelity` in trust_audits/__init__.py

Add after the four individual imports (after line 100 / `validate_surface_weight` import):

```python
def validate_surface_fidelity(project_root: Path) -> list[ValidationError]:
    """Composite: run all four surface-fidelity invariants in declared order.

    Invokes bullet_retention, surface_weight, pointer_integrity, and
    scenario_reachability in that order and aggregates their ValidationError
    lists. Exit code is determined by the worst error type in the aggregate
    (policy-breach types exit 3; others exit 1).
    """
    from pathlib import Path as _Path  # already imported above

    errors: list[ValidationError] = []
    errors.extend(validate_bullet_retention(project_root))
    errors.extend(validate_surface_weight(project_root))
    errors.extend(validate_pointer_integrity(project_root))
    errors.extend(validate_scenario_reachability(project_root))
    return errors
```

Add `Path` import at top if not already present (it is, via `from __future__ import annotations`). Add `validate_surface_fidelity` to `__all__`.

Note: `Path` is not imported at module level in `__init__.py` — the function will use the `project_root: Path` parameter annotation (already a `Path` object at call time from caller). No import needed in the function body.

### Step 3: Add `run_surface_fidelity_audit` to quality.py

After `run_orientation_freshness_audit` (line 619+), add:

```python
def run_surface_fidelity_audit(project_root: Path) -> QualityResult:
    """Run the ADR-0.0.33-05 surface-fidelity composite: all four invariants.

    Fails closed when any of bullet_retention, surface_weight,
    pointer_integrity, or scenario_reachability report errors.
    """
    return run_command("uv run gz validate --surface-fidelity", cwd=project_root)
```

### Step 4: Wire into `_build_check_steps()` in commands/quality.py

Add `run_surface_fidelity_audit` to the import from `gzkit.quality` in `_build_check_steps()` and add the tuple to the steps list:

```python
("Surface fidelity", run_surface_fidelity_audit),
```

Place after `("Preflight", run_preflight)` at the end of the list.

### Step 5: Wire `--surface-fidelity` CLI flag

**parser_maintenance.py** — add after `--scenario-reachability` block (line 596):

```python
    p_validate.add_argument(
        "--surface-fidelity",
        dest="check_surface_fidelity",
        action="store_true",
        help="Composite: run all four surface-fidelity invariants (ADR-0.0.33-05).",
    )
```

Add to `set_defaults` lambda: `check_surface_fidelity=a.check_surface_fidelity`.

**validate_cmd.py `_collect_errors`** — add `check_surface_fidelity: bool = False` to function signature, add to `explicit_scopes` dict and `_explicit_scope_runners`.

**validate_cmd.py `validate`** — add `check_surface_fidelity: bool = False` to signature, add to `_other_scopes_active` list, pass to `_collect_errors`.

### Step 6: Add pre-commit hook

In `.pre-commit-config.yaml`, add a new hook to the first local repo block (after `interrogate`):

```yaml
      - id: surface-fidelity-cheap
        name: surface-fidelity cheap subset (invariants 1, 2, 3)
        entry: uv run gz validate --bullet-retention --surface-weight --pointer-anchors
        language: system
        pass_filenames: false
        stages: [pre-commit]
```

### Step 7: Update docs/user/manpages/validate.md

1. Add `[--surface-fidelity]` to the usage line (after `[--scenario-reachability]`).
2. Add `### --surface-fidelity` section after `### --scenario-reachability`.
3. Add `--surface-fidelity` row to the Scopes Reference table.

### Step 8: Update docs/user/manpages/check.md

Add a note that `gz check` now includes a "Surface fidelity" step that runs `gz validate --surface-fidelity`.

### Step 9: TDD Green verify

```bash
uv run -m unittest tests.governance.test_surface_fidelity_composite -v
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest -q
```

### Step 10: Present OBPI Acceptance Ceremony

Present Stage 4 evidence including all REQ coverage, quality checks, and files created/modified.

## Verification commands

```bash
uv run gz validate --surface-fidelity
uv run gz check
uv run -m unittest tests.governance.test_surface_fidelity_composite -v
grep -q "gz validate --bullet-retention" .pre-commit-config.yaml
```
