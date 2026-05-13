"""Distribution invariant T0 static audit (ADR-0.0.32-07).

Detects three drift classes between pyproject.toml wheel includes,
data/distribution_baseline_manifest.json, and on-disk canonical surface trees:

  ON_DISK_NOT_INCLUDED   — surface file exists on disk but not covered by any include glob
  BASELINE_NOT_ON_DISK   — baseline manifest entry does not exist on disk
  ON_DISK_NOT_BASELINE   — surface file on disk + included but absent from baseline

System errors (malformed TOML, missing manifest) raise SystemExit(2).
Policy breaches return a list of ValidationError (caller exits 3).
Clean state returns an empty list.
"""

from __future__ import annotations

import json
import sys
import tomllib
from pathlib import Path

from gzkit.validate import ValidationError

_EXCLUDED_SEGMENTS: frozenset[str] = frozenset(
    {"__pycache__", ".venv", "dist", "build", "node_modules"}
)


def audit_distribution(project_root: Path) -> list[ValidationError]:
    """Static T0 distribution audit — no wheel build required.

    Loads ``pyproject.toml`` include globs and ``data/distribution_baseline_manifest.json``,
    derives surface roots from manifest keys, walks on-disk files, and detects drift.
    Raises ``SystemExit(2)`` on IO/parse failures so callers can distinguish system
    errors (exit 2) from policy breaches (exit 3).
    """
    include_globs, baseline_entries, surface_roots = _load_inputs(project_root)

    on_disk_files = _walk_surface_files(project_root, surface_roots)

    included_files = _expand_includes(project_root, include_globs)

    return _collect_errors(on_disk_files, included_files, baseline_entries)


def _load_inputs(
    project_root: Path,
) -> tuple[list[str], set[str], list[str]]:
    """Load pyproject.toml include globs and baseline manifest.  Raises SystemExit(2) on failure."""
    pyproject = project_root / "pyproject.toml"
    try:
        with open(pyproject, "rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError as exc:
        print(f"distribution-audit: pyproject.toml not found: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except tomllib.TOMLDecodeError as exc:
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

    manifest_path = project_root / "data" / "distribution_baseline_manifest.json"
    try:
        with open(manifest_path, encoding="utf-8") as f:
            manifest = json.load(f)
    except FileNotFoundError as exc:
        print(f"distribution-audit: baseline manifest not found: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except json.JSONDecodeError as exc:
        print(f"distribution-audit: cannot parse baseline manifest: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    surfaces: dict[str, list[str]] = manifest.get("surfaces", {})
    baseline_entries: set[str] = set()
    for surface, entries in surfaces.items():
        for entry in entries:
            baseline_entries.add(f"src/gzkit/{surface}/{entry}")

    surface_roots = [f"src/gzkit/{surface}" for surface in surfaces]
    return include_globs, baseline_entries, surface_roots


def _walk_surface_files(project_root: Path, surface_roots: list[str]) -> set[str]:
    """Walk on-disk files under each surface root, excluding build/pycache segments."""
    on_disk: set[str] = set()
    for root_str in surface_roots:
        root_path = project_root / root_str
        if not root_path.exists():
            continue
        for path in root_path.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(project_root)
            if _is_excluded(rel.parts):
                continue
            on_disk.add(rel.as_posix())
    return on_disk


def _is_excluded(parts: tuple[str, ...]) -> bool:
    return any(seg in _EXCLUDED_SEGMENTS or seg.startswith("__") for seg in parts)


def _expand_includes(project_root: Path, include_globs: list[str]) -> set[str]:
    """Expand include globs against project_root to get the set of included files."""
    included: set[str] = set()
    for glob_pattern in include_globs:
        for matched in project_root.glob(glob_pattern):
            if matched.is_file():
                included.add(matched.relative_to(project_root).as_posix())
    return included


def _collect_errors(
    on_disk: set[str],
    included: set[str],
    baseline: set[str],
) -> list[ValidationError]:
    """Compute drift errors from the three input sets."""
    errors: list[ValidationError] = []

    for rel_posix in sorted(on_disk - included):
        errors.append(
            ValidationError(
                type="distribution",
                artifact=rel_posix,
                message=(
                    f"ON_DISK_NOT_INCLUDED: '{rel_posix}' exists under a canonical surface "
                    f"tree but is not covered by any include glob in "
                    f"[tool.hatch.build.targets.wheel] include. "
                    f"Resolution: extend the include block in pyproject.toml."
                ),
            )
        )

    for entry in sorted(baseline - on_disk):
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

    for rel_posix in sorted((on_disk & included) - baseline):
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
