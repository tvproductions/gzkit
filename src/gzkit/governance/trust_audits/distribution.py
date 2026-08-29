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
from importlib import import_module
from pathlib import Path
from typing import Any

from gzkit.validate import ValidationError

_EXCLUDED_SEGMENTS: frozenset[str] = frozenset(
    {"__pycache__", ".venv", "dist", "build", "node_modules"}
)

#: Classifier verdicts meaning "absent from the wheel on purpose". Named once
#: because the auditor and the regenerator must agree on it: they held separate
#: transcriptions and had already drifted apart, the regenerator still omitting
#: `project_local` after GHI #728 added it to the auditor. Nothing failed only
#: because the prune keeps such files off the package tree the regenerator walks
#: — a second mechanism covering for the gap rather than the gap being closed
#: (GHI #915).
_NOT_SHIPPED_CLASSES: frozenset[str] = frozenset({"package_only", "runtime_state", "project_local"})

# The audit's domain.  Deriving it from the baseline manifest's own keys made the
# audit blind to any canonical surface the manifest omitted — it could report that
# a listed member was wrong but never that a member was missing, so `src/gzkit/chores`
# was never walked and the chores classifier was unreachable (residual of GHI #783).
# The surface list belongs to `.gzkit/rules/skill-surface-sync.md` § Surface layout,
# never to the artifact under audit.
_CANONICAL_SURFACES: tuple[str, ...] = (
    "personas",
    "rules",
    "skills",
    "templates",
    "chores",
)


def _get_surface_classifier(surface: str) -> Callable[[Path], str] | None:
    """Return the per-surface classifier for a canonical surface, or None.

    Both the classifier and its module are derived from ``_CANONICAL_SURFACES``
    so the audit's domain and its dispatch cannot drift apart: a surface added
    to the tuple gains a walk and a classifier in the same edit.  Imported
    lazily because each surface module pulls in its own runtime.
    """
    if surface not in _CANONICAL_SURFACES:
        return None
    module = import_module(f"gzkit.{surface}")
    return getattr(module, f"_classify_{surface.removesuffix('s')}_file", None)


def _surface_from_posix(rel_posix: str) -> str | None:
    """Extract the surface name from a rel_posix path like 'src/gzkit/rules/...'."""
    parts = rel_posix.split("/")
    if len(parts) >= 3 and parts[0] == "src" and parts[1] == "gzkit":
        return parts[2]
    return None


def _is_package_only(rel_posix: str, project_root: Path | None = None) -> bool:
    """Return True when a classifier marks a file as not-shipped-by-design.

    Covers package_only, runtime_state, and project_local. The last is a
    declared gzkit-internal chore slug: it is absent from the wheel on purpose,
    so flagging its absence would turn the fix for GHI #728 into a gate failure.
    """
    surface = _surface_from_posix(rel_posix)
    if surface is None:
        return False
    classifier = _get_surface_classifier(surface)
    if classifier is None:
        return False
    # Absolute, because a classifier locates a file's `.gzkit/` counterpart with
    # `relative_to(project_root / ...)`, which raises on a relative path and falls
    # through to package_only — silently exempting authored chore gate scripts.
    path = project_root / rel_posix if project_root is not None else Path(rel_posix)
    try:
        result = classifier(path, project_root=project_root)  # type: ignore
    except TypeError:
        result = classifier(path)
    return result in _NOT_SHIPPED_CLASSES


def audit_distribution(project_root: Path) -> list[ValidationError]:
    """Run the static T0 distribution audit — no wheel build required.

    Loads ``pyproject.toml`` include globs and ``data/distribution_baseline_manifest.json``,
    walks every root in ``_CANONICAL_SURFACES``, and detects drift.
    Raises ``SystemExit(2)`` on IO/parse failures so callers can distinguish system
    errors (exit 2) from policy breaches (exit 3).
    """
    include_globs, baseline_entries, surface_roots, package_roots = _load_inputs(project_root)

    on_disk_files = _walk_surface_files(project_root, surface_roots)

    included_files = _expand_includes(project_root, include_globs, package_roots)

    return _collect_errors(on_disk_files, included_files, baseline_entries, project_root)


def wheel_build_config(
    project_root: Path, *, missing_ok: bool = False
) -> tuple[list[str], list[str]]:
    """Return the wheel's ``(include globs, package roots)`` from pyproject.toml.

    Shared with :mod:`gzkit.governance.trust_audits.wheel_path_literals` so the
    resolvability witness reads the *same* declaration the delivery gate reads.
    A second transcribed copy of this list would cover the trees that existed
    the day it was written and silently miss the next one added (GHI #900).

    ``missing_ok`` is the difference between an explicit-tier and a
    default-tier caller. ``--distribution`` runs only where an operator points
    it, so an absent pyproject.toml is a broken invocation. The resolvability
    witness runs in the default ``gz check`` scope, which the QC negative
    controls exercise against synthetic project roots that ship no wheel at
    all — there, "no build config" means "no delivered instruction text", which
    is a clean result rather than a failure. An *unparseable* pyproject.toml
    stays fatal for both: that is real breakage, not absence.

    Raises ``SystemExit(2)`` when pyproject.toml is unparseable, or when it is
    missing and ``missing_ok`` is false.
    """
    pyproject = project_root / "pyproject.toml"
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError as exc:
        if missing_ok:
            return [], []
        print(f"distribution-audit: pyproject.toml not found: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except tomllib.TOMLDecodeError as exc:
        print(f"distribution-audit: cannot parse pyproject.toml: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    wheel_target: dict[str, Any] = (
        data.get("tool", {}).get("hatch", {}).get("build", {}).get("targets", {}).get("wheel", {})
    )
    return wheel_target.get("include", []), wheel_target.get("packages", [])


def _load_inputs(
    project_root: Path,
) -> tuple[list[str], set[str], list[str], list[str]]:
    """Load pyproject.toml include globs and baseline manifest.  Raises SystemExit(2) on failure."""
    include_globs, package_roots = wheel_build_config(project_root)

    manifest_path = project_root / "data" / "distribution_baseline_manifest.json"
    try:
        with manifest_path.open(encoding="utf-8") as f:
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

    surface_roots = [f"src/gzkit/{surface}" for surface in _CANONICAL_SURFACES]
    return include_globs, baseline_entries, surface_roots, package_roots


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


def _expand_includes(
    project_root: Path, include_globs: list[str], package_roots: list[str]
) -> set[str]:
    """Return every file the wheel ships, from BOTH build mechanisms.

    ``include`` globs carry data files; ``packages`` ships ``.py`` modules under
    each root independently of any glob.  Modelling the globs alone reported
    seven shipped modules as not-shipped when measured against a real 0.34.2
    wheel — a predictor blind to half its own build config.
    """
    included: set[str] = set()
    for glob_pattern in include_globs:
        for matched in project_root.glob(glob_pattern):
            if matched.is_file():
                included.add(matched.relative_to(project_root).as_posix())
    for package_root in package_roots:
        for module in (project_root / package_root).rglob("*.py"):
            rel = module.relative_to(project_root)
            if not _is_excluded(rel.parts):
                included.add(rel.as_posix())
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
        if _is_package_only(rel_posix, project_root):
            continue
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
    include_globs, _baseline, surface_roots, _package_roots = _load_inputs(project_root)
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
                    cls = classifier(path)
                if cls in _NOT_SHIPPED_CLASSES:
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
