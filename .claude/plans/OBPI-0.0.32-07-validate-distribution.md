# OBPI-0.0.32-07-validate-distribution — Implementation Plan

## Context

- **OBPI:** OBPI-0.0.32-07-validate-distribution
- **Parent ADR:** ADR-0.0.32-canonical-surface-packaging
- **Lane:** Heavy (foundation-kind, requires Gate 5 human attestation)
- **ADR Checklist Item #7:** "Extend `gz validate --surfaces` (or add `--distribution`) with T0 enforcement — verify every canonical surface in manifest is wheel-deliverable from `src/gzkit/`; fail-closed exit 3 on any package-data omission; flip T0 scorecard Promotable→Mechanical."

## Path Notes (brief drift vs. reality)

The brief references paths that do not literally exist but map to real counterparts:
- `src/gzkit/governance/trust_audits.py` → `src/gzkit/governance/trust_audits/distribution.py` (new module in the package)
- `src/gzkit/cli/parser_validate.py` → `src/gzkit/cli/parser_maintenance.py` (where validate flags actually live)
- `docs/user/manpages/gz-validate.md` → `docs/user/manpages/validate.md` (actual file)
- `src/gzkit/commands/validate_cmd.py` → also touched for dispatch (not in brief allowed list but required)

## Files

**New:**
- `src/gzkit/governance/trust_audits/distribution.py`
- `tests/governance/test_distribution_audit.py`
- `features/validate_distribution.feature`

**Modified:**
- `src/gzkit/governance/trust_audits/__init__.py` — add import of `audit_distribution`
- `src/gzkit/cli/parser_maintenance.py` — add `--distribution` flag
- `src/gzkit/commands/validate_cmd.py` — add `check_distribution` param + dispatch
- `docs/user/manpages/validate.md` — document new scope
- `docs/governance/advisory-rules-audit.md` — flip T0 row 57 from Promotable to Mechanical
- `.gzkit/rules/governance-core.md` — add `uv run gz validate --distribution` to proof commands

## Steps

### Step 1: TDD RED — Author failing tests

Create `tests/governance/test_distribution_audit.py` with the following test classes.
All tests must FAIL before Step 2 (no implementation yet):

- `TestCleanStateExitsZero` — fixture with a fully-clean state; assert empty error list
- `TestOnDiskNotIncluded` — create a canonical-surface file not covered by any include glob;
  assert error with type `distribution`, drift_class `ON_DISK_NOT_INCLUDED`, file path, and resolution hint
- `TestBaselineNotOnDisk` — baseline manifest names a file that doesn't exist on disk;
  assert error with drift_class `BASELINE_NOT_ON_DISK`
- `TestOnDiskNotBaseline` — file exists on disk and covered by include but absent from baseline;
  assert error with drift_class `ON_DISK_NOT_BASELINE`
- `TestMalformedToml` — write a broken TOML to a temp pyproject.toml; assert the function
  raises SystemExit(2) (system error, not policy breach)
- `TestWalkFilter` — confirm `__pycache__`, `.pyc`, and non-surface trees are NOT flagged

Use `tempfile.TemporaryDirectory` for fixtures; copy the real `data/distribution_baseline_manifest.json`
into the temp dir and sculpt the include list fixture from pyproject.toml's actual includes.

### Step 2: Implement `audit_distribution`

Create `src/gzkit/governance/trust_audits/distribution.py`:

```python
"""Distribution invariant T0 static audit (ADR-0.0.32 Decision #7)."""

from __future__ import annotations

import tomllib
from pathlib import Path

from gzkit.validate import ValidationError

# Canonical surface trees mirrored in the wheel
_SURFACE_ROOTS: tuple[str, ...] = (
    "src/gzkit/skills",
    "src/gzkit/rules",
    "src/gzkit/personas",
    "src/gzkit/templates",
    "src/gzkit/chores",
    "src/gzkit/hooks/scripts",
)

# Extensions shipped into canonical surface trees
_SHIPPED_EXTENSIONS: frozenset[str] = frozenset({".md", ".json", ".py", ".sh"})

_EXCLUDED_SEGMENTS: frozenset[str] = frozenset(
    {"__pycache__", ".venv", "dist", "build", "node_modules"}
)


def audit_distribution(project_root: Path) -> list[ValidationError]:
    """
    Three-class static T0 distribution audit (ADR-0.0.32-07).

    Loads pyproject.toml wheel include globs, loads baseline manifest,
    walks on-disk canonical surface trees, and detects:
      ON_DISK_NOT_INCLUDED  — on-disk file not covered by any include glob
      BASELINE_NOT_ON_DISK  — baseline entry that is not on disk
      ON_DISK_NOT_BASELINE  — on-disk+included file absent from baseline

    System errors (malformed TOML) raise SystemExit(2).
    Policy breaches return ValidationError list (caller exits 3).
    Clean state returns empty list.
    """
    # Load pyproject.toml
    pyproject = project_root / "pyproject.toml"
    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
    except (FileNotFoundError, tomllib.TOMLDecodeError) as exc:
        import sys
        print(f"distribution-audit: cannot parse pyproject.toml: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    include_globs: list[str] = (
        data.get("tool", {})
        .get("hatch", {})
        .get("build", {})
        .get("targets", {})
        .get("wheel", {})
        .get("include", [])
    )

    # Load baseline manifest
    manifest_path = project_root / "data" / "distribution_baseline_manifest.json"
    try:
        import json
        with open(manifest_path) as f:
            manifest = json.load(f)
    except (FileNotFoundError, json.JSONDecodeError) as exc:
        import sys
        print(f"distribution-audit: cannot load baseline manifest: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    # Flatten baseline entries into a set of relative POSIX paths
    baseline_entries: set[str] = set()
    for surface, entries in manifest.get("surfaces", {}).items():
        for entry in entries:
            baseline_entries.add(f"src/gzkit/{surface}/{entry}")

    # Walk on-disk canonical surface trees
    on_disk_files: set[str] = set()
    for root_str in _SURFACE_ROOTS:
        root = project_root / root_str
        if not root.exists():
            continue
        for path in sorted(root.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(project_root)
            parts = rel.parts
            # Skip excluded segments
            if any(seg in _EXCLUDED_SEGMENTS or seg.startswith("__") for seg in parts):
                continue
            on_disk_files.add(rel.as_posix())

    # Build set of files covered by include globs
    from pathlib import PurePosixPath
    included_files: set[str] = set()
    for rel_posix in on_disk_files:
        for glob in include_globs:
            if PurePosixPath(rel_posix).match(glob):
                included_files.add(rel_posix)
                break

    errors: list[ValidationError] = []

    # Drift class (a): ON_DISK_NOT_INCLUDED
    for rel_posix in sorted(on_disk_files - included_files):
        errors.append(
            ValidationError(
                type="distribution",
                artifact=rel_posix,
                message=(
                    f"ON_DISK_NOT_INCLUDED: '{rel_posix}' exists under a canonical surface "
                    f"tree but is not covered by any include glob in "
                    f"pyproject.toml [tool.hatch.build.targets.wheel] include. "
                    f"Resolution: extend the include block in pyproject.toml."
                ),
            )
        )

    # Drift class (b): BASELINE_NOT_ON_DISK
    for entry in sorted(baseline_entries - on_disk_files):
        errors.append(
            ValidationError(
                type="distribution",
                artifact=entry,
                message=(
                    f"BASELINE_NOT_ON_DISK: '{entry}' appears in the baseline manifest "
                    f"but does not exist on disk. "
                    f"Resolution: restore the missing file or remove it from "
                    f"data/distribution_baseline_manifest.json."
                ),
            )
        )

    # Drift class (c): ON_DISK_NOT_BASELINE
    for rel_posix in sorted(included_files - baseline_entries):
        errors.append(
            ValidationError(
                type="distribution",
                artifact=rel_posix,
                message=(
                    f"ON_DISK_NOT_BASELINE: '{rel_posix}' exists on disk and is covered "
                    f"by a wheel include glob but is NOT in the baseline manifest. "
                    f"Resolution: add to data/distribution_baseline_manifest.json."
                ),
            )
        )

    return errors
```

Add to `src/gzkit/governance/trust_audits/__init__.py`:
```python
from gzkit.governance.trust_audits.distribution import audit_distribution
```

### Step 3: Wire CLI flag and dispatch

**`src/gzkit/cli/parser_maintenance.py`** — add after the last `p_validate.add_argument(...)` block:
```python
p_validate.add_argument(
    "--distribution",
    dest="check_distribution",
    action="store_true",
    help="T0 static distribution audit: ON_DISK_NOT_INCLUDED / BASELINE_NOT_ON_DISK / ON_DISK_NOT_BASELINE (ADR-0.0.32)",
)
```

**`src/gzkit/commands/validate_cmd.py`** — add `check_distribution: bool = False` to
`_run_validations` signature and `validate` function signatures, add to `explicit_scopes`
dict:
```python
"distribution": check_distribution,
```
Add dispatch lambda in the explicit-scope handler:
```python
"distribution": lambda: trust_audits.audit_distribution(project_root),
```
Add `"distribution"` to `_POLICY_BREACH_ERROR_TYPES`.

### Step 4: Documentation + scorecard

**`docs/user/manpages/validate.md`** — add `--distribution` to Usage block and add a
`### --distribution` section documenting:
- Three drift classes (ON_DISK_NOT_INCLUDED, BASELINE_NOT_ON_DISK, ON_DISK_NOT_BASELINE)
- Exit codes: 0 (clean), 2 (system error — malformed TOML or missing manifest), 3 (policy breach)
- A worked recovery example for each drift class

**`docs/governance/advisory-rules-audit.md`** — flip row 57 from Promotable to Mechanical:
- Change `**Promotable**` to `**Mechanical**`
- Update the enforcement note to: "Enforced by `gz validate --distribution` (OBPI-0.0.32-07, `src/gzkit/governance/trust_audits/distribution.py`) — static check against `pyproject.toml` include globs + `data/distribution_baseline_manifest.json` + on-disk canonical surface trees; exit 3 on any drift class. Receipt-id prefix: `arb-distribution-`."
- Update the trailing summary counts (Promotable -1, Mechanical +1)

**`.gzkit/rules/governance-core.md`** — add to Proof commands:
```bash
uv run gz validate --distribution
```

### Step 5: BDD scenario

Create `features/validate_distribution.feature` with a `@REQ-0.0.32-07-01` tagged scenario
that uses a fixture with a known drift class and asserts `gz validate --distribution` exits 3
with a structured per-violation report. Use step definitions that create a temp project dir
fixture with a minimal pyproject.toml and baseline manifest.

## Verification

```bash
uv run gz arb ruff
uv run gz arb typecheck
uv run gz arb step --name unittest -- uv run -m unittest tests.governance.test_distribution_audit -v
uv run gz arb step --name unittest -- uv run -m unittest -q

uv run gz validate --help | grep -- --distribution
uv run gz validate --distribution

uv run gz arb step --name mkdocs -- uv run mkdocs build --strict
uv run -m behave features/validate_distribution.feature --tags=@REQ-0.0.32-07-01
```

## Notes

- Destination-in-mind: Adding a new `distribution.py` module to the trust_audits package, wiring it
  via the same pattern as `chores.py` / `cross_platform.py`.
- Rejected alternatives: (a) extending `--surfaces` directly rather than adding `--distribution` —
  rejected because a dedicated flag is easier to invoke selectively and aligns with REQ-0.0.32-07-01's
  explicit `--distribution` requirement; (b) building a wheel and inspecting it — rejected by REQ-0.0.32-07-04
  (static-only, no subprocess `uv build`).
- The `include` glob matching uses `PurePosixPath.match()` which handles `**` patterns via fnmatch.
  Verify against actual pyproject.toml patterns in Step 2.
- The exit-2 path for system errors (malformed TOML, missing manifest) is structurally distinct from
  the exit-3 policy-breach path. The ValidationError type `distribution` must be added to
  `_POLICY_BREACH_ERROR_TYPES` in validate_cmd.py.
