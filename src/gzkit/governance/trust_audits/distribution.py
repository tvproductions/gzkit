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

import hashlib
import json
import sys
import tempfile
import tomllib
from collections.abc import Callable
from pathlib import Path
from typing import Any

from gzkit.validate import ValidationError

_EXCLUDED_SEGMENTS: frozenset[str] = frozenset(
    {"__pycache__", ".venv", "dist", "build", "node_modules"}
)


def _get_surface_classifier(surface: str) -> Callable[[Path], str] | None:
    """Return the per-surface classifier for a canonical surface, or None."""
    if surface == "rules":
        from gzkit.rules import _classify_rule_file  # noqa: PLC0415

        return _classify_rule_file
    if surface == "skills":
        from gzkit.skills import _classify_skill_file  # noqa: PLC0415

        return _classify_skill_file
    if surface == "personas":
        from gzkit.personas import _classify_persona_file  # noqa: PLC0415

        return _classify_persona_file
    if surface == "templates":
        from gzkit.templates import _classify_template_file  # noqa: PLC0415

        return _classify_template_file
    if surface == "chores":
        from gzkit.chores import _classify_chore_file  # noqa: PLC0415

        return _classify_chore_file
    return None


def _surface_from_posix(rel_posix: str) -> str | None:
    """Extract the surface name from a rel_posix path like 'src/gzkit/rules/...'."""
    parts = rel_posix.split("/")
    if len(parts) >= 3 and parts[0] == "src" and parts[1] == "gzkit":
        return parts[2]
    return None


def _is_package_only(rel_posix: str, project_root: Path | None = None) -> bool:
    """Return True if a file's per-surface classifier marks it package_only or runtime_state."""
    surface = _surface_from_posix(rel_posix)
    if surface is None:
        return False
    classifier = _get_surface_classifier(surface)
    if classifier is None:
        return False
    path = Path(rel_posix)
    try:
        result = classifier(path, project_root=project_root)  # type: ignore
    except TypeError:
        result = classifier(path)  # type: ignore
    return result in ("package_only", "runtime_state")


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

    return _collect_errors(on_disk_files, included_files, baseline_entries, project_root)


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
    project_root: Path | None = None,
) -> list[ValidationError]:
    """Compute drift errors from the three input sets."""
    errors: list[ValidationError] = []

    for rel_posix in sorted(on_disk - included):
        if _is_package_only(rel_posix, project_root):
            continue
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


def _manifest_hash(manifest_path: Path) -> str:
    """Return sha256 hex digest of the manifest file, or empty string if missing."""
    if not manifest_path.exists():
        return ""
    return hashlib.sha256(manifest_path.read_bytes()).hexdigest()


def regenerate_distribution_baseline(project_root: Path) -> dict[str, Any]:
    """Rewrite data/distribution_baseline_manifest.json from on-disk canonical surface truth.

    Walks each surface root, applies the per-surface classifier to skip
    ``package_only`` and ``runtime_state`` files, and rewrites the manifest
    from on-disk truth as the sole input.  Emits a
    ``distribution_baseline_regenerated`` ledger event capturing hash before/after.

    Returns a dict with keys ``surfaces_walked``, ``file_count``,
    ``manifest_hash_before``, ``manifest_hash_after``.
    """
    include_globs, _baseline, surface_roots = _load_inputs(project_root)
    manifest_path = project_root / "data" / "distribution_baseline_manifest.json"

    hash_before = _manifest_hash(manifest_path)

    surfaces: dict[str, list[str]] = {}
    for root_str in surface_roots:
        surface = _surface_from_posix(root_str + "/placeholder") or root_str.split("/")[-1]
        classifier = _get_surface_classifier(surface)
        root_path = project_root / root_str
        if not root_path.exists():
            continue
        entries: list[str] = []
        for path in sorted(root_path.rglob("*")):
            if not path.is_file():
                continue
            rel = path.relative_to(project_root)
            if _is_excluded(rel.parts):
                continue
            if classifier is not None:
                try:
                    cls = classifier(path, project_root=project_root)  # type: ignore
                except TypeError:
                    cls = classifier(path)  # type: ignore
                if cls in ("package_only", "runtime_state"):
                    continue
            entry = path.relative_to(root_path).as_posix()
            entries.append(entry)
        if entries:
            surfaces[surface] = entries

    from gzkit import __version__ as _gzkit_version  # noqa: PLC0415

    new_manifest: dict[str, Any] = {
        "schema_version": "1.0",
        "gzkit_version": _gzkit_version,
        "surfaces": surfaces,
    }
    manifest_json = json.dumps(new_manifest, indent=2, sort_keys=False) + "\n"

    with tempfile.NamedTemporaryFile(
        mode="w",
        encoding="utf-8",
        dir=manifest_path.parent,
        delete=False,
        suffix=".tmp",
    ) as tmp:
        tmp.write(manifest_json)
        tmp_path = Path(tmp.name)
    tmp_path.replace(manifest_path)

    hash_after = _manifest_hash(manifest_path)
    file_count = sum(len(v) for v in surfaces.values())
    surfaces_walked = list(surfaces.keys())

    from gzkit.ledger import Ledger  # noqa: PLC0415
    from gzkit.ledger_events import distribution_baseline_regenerated_event  # noqa: PLC0415

    ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
    event = distribution_baseline_regenerated_event(
        surfaces_walked=surfaces_walked,
        file_count=file_count,
        manifest_hash_before=hash_before,
        manifest_hash_after=hash_after,
    )
    ledger.append(event)

    return {
        "surfaces_walked": surfaces_walked,
        "file_count": file_count,
        "manifest_hash_before": hash_before,
        "manifest_hash_after": hash_after,
    }
