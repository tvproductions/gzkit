"""Distribution invariant T0 static audit (ADR-0.0.32-07).

Detects three drift classes between the uv_build wheel pyproject.toml declares,
data/distribution_baseline_manifest.json, and on-disk canonical surface trees:

  ON_DISK_NOT_INCLUDED   — surface file exists on disk but the wheel does not ship it
  BASELINE_NOT_ON_DISK   — baseline manifest entry does not exist on disk
  ON_DISK_NOT_BASELINE   — surface file on disk + included but absent from baseline

System errors (malformed TOML, missing manifest) raise SystemExit(2).
Policy breaches return a list of ValidationError (caller exits 3).
Clean state returns an empty list.
"""

from __future__ import annotations

import hashlib
import json
import re
import sys
import tempfile
import tomllib
from collections.abc import Callable
from fnmatch import fnmatchcase
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

    Predicts the wheel from ``pyproject.toml``, loads
    ``data/distribution_baseline_manifest.json``, walks every root in
    ``_CANONICAL_SURFACES``, and detects drift.
    Raises ``SystemExit(2)`` on IO/parse failures so callers can distinguish system
    errors (exit 2) from policy breaches (exit 3).
    """
    shipped_files, baseline_entries, surface_roots = _load_inputs(project_root)

    on_disk_files = _walk_surface_files(project_root, surface_roots)

    return _collect_errors(on_disk_files, shipped_files, baseline_entries, project_root)


#: uv_build's built-in excludes, applied to every wheel whatever the config says
#: ("By default, uv excludes `__pycache__`, `*.pyc`, and `*.pyo`").
_UV_BUILD_DEFAULT_EXCLUDES: tuple[str, ...] = ("__pycache__", "*.pyc", "*.pyo")


def _glob_matches(pattern: list[str], parts: list[str]) -> bool:
    """Match path components against PEP 639 glob components, ``**`` spanning any depth."""
    if not pattern:
        return not parts
    head, rest = pattern[0], pattern[1:]
    if head == "**":
        return any(_glob_matches(rest, parts[i:]) for i in range(len(parts) + 1))
    return bool(parts) and fnmatchcase(parts[0], head) and _glob_matches(rest, parts[1:])


def _excluding_pattern(rel_parts: list[str], patterns: list[str]) -> str | None:
    """Return the unanchored uv_build exclude that removes this path, or None.

    uv's rule: "Excludes are not anchored", and "All children of an exclusion
    are excluded as well", so a pattern removes a path when it matches any run
    of the path's components (project-relative) starting at any depth.
    """
    for pattern in patterns:
        components = pattern.split("/")
        for start in range(len(rel_parts)):
            for stop in range(start + 1, len(rel_parts) + 1):
                if _glob_matches(components, rel_parts[start:stop]):
                    return pattern
    return None


def _build_backend_table(data: dict[str, Any]) -> dict[str, Any] | None:
    """Return ``[tool.uv.build-backend]`` when the project builds with uv_build, else None."""
    if data.get("build-system", {}).get("build-backend") != "uv_build":
        return None
    return data.get("tool", {}).get("uv", {}).get("build-backend", {})


def wheel_shipped_files(project_root: Path, *, missing_ok: bool = False) -> set[str]:
    """Return every project-relative path, as posix, that the uv_build wheel ships.

    The one predictor of the wheel, shared with
    :mod:`gzkit.governance.trust_audits.wheel_path_literals` so the resolvability
    witness reads the *same* declaration the delivery gate reads (GHI #900).
    uv_build has no wheel includes: the wheel is the module under
    ``module-root`` minus ``source-exclude``, ``wheel-exclude`` and uv's own
    defaults, so the prediction walks that tree rather than any glob list
    (RO-9 tranche 3, `docs/governance/harbor-ro9-astral-toolchain.md`).
    Static by contract: no build runs (REQ-0.0.32-07-07).

    A project not built by uv_build ships nothing this predictor can model, so it
    returns the empty set. An anchored exclude (leading ``/``) is refused: probed
    on uv 0.13.1, an anchored ``wheel-exclude`` removed nothing, so no reading of
    it is verified.

    ``missing_ok`` is the difference between an explicit-tier and a
    default-tier caller. ``--distribution`` runs only where an operator points
    it, so an absent pyproject.toml is a broken invocation. The resolvability
    witness runs in the default ``gz check`` scope, which the QC negative
    controls exercise against synthetic project roots that ship no wheel at
    all — there, "no build config" means "no delivered instruction text", which
    is a clean result rather than a failure. An *unparseable* pyproject.toml
    stays fatal for both: that is real breakage, not absence.

    Raises ``SystemExit(2)`` when pyproject.toml is unparseable, when it is
    missing and ``missing_ok`` is false, or when an exclude is anchored.
    """
    layout = _wheel_layout(project_root, missing_ok=missing_ok)
    shipped: set[str] = set()
    if layout is None:
        return shipped
    module_dir, excludes = layout
    for path in module_dir.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = list(path.relative_to(project_root).parts)
        if _excluding_pattern(rel_parts, excludes) is None:
            shipped.add("/".join(rel_parts))
    return shipped


def unshipped_reason(project_root: Path, rel_posix: str) -> str:
    """Name why the predicted wheel leaves out ``rel_posix``: its exclude, or its location."""
    layout = _wheel_layout(project_root, missing_ok=True)
    if layout is None:
        return "pyproject.toml declares no uv_build wheel ([build-system] build-backend)"
    module_dir, excludes = layout
    module_rel = module_dir.relative_to(project_root).as_posix()
    if not rel_posix.startswith(f"{module_rel}/"):
        return f"it sits outside the module root '{module_rel}'"
    pattern = _excluding_pattern(rel_posix.split("/"), excludes)
    if pattern in _UV_BUILD_DEFAULT_EXCLUDES:
        return f"uv_build's default exclude '{pattern}' removes it"
    return f"the [tool.uv.build-backend] exclude '{pattern}' removes it"


def _wheel_layout(project_root: Path, *, missing_ok: bool) -> tuple[Path, list[str]] | None:
    """Return the uv_build module directory and every exclude in force, or None.

    Raises ``SystemExit(2)`` per :func:`wheel_shipped_files`.
    """
    pyproject = project_root / "pyproject.toml"
    try:
        with pyproject.open("rb") as f:
            data = tomllib.load(f)
    except FileNotFoundError as exc:
        if missing_ok:
            return None
        print(f"distribution-audit: pyproject.toml not found: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc
    except tomllib.TOMLDecodeError as exc:
        print(f"distribution-audit: cannot parse pyproject.toml: {exc}", file=sys.stderr)
        raise SystemExit(2) from exc

    backend = _build_backend_table(data)
    if backend is None:
        return None
    default_name = str(data.get("project", {}).get("name", "")).lower()
    module_name = str(backend.get("module-name", re.sub(r"[-.]", "_", default_name)))
    module_root = str(backend.get("module-root", "src"))
    excludes = [
        *backend.get("source-exclude", []),
        *backend.get("wheel-exclude", []),
        *_UV_BUILD_DEFAULT_EXCLUDES,
    ]
    anchored = [pattern for pattern in excludes if pattern.startswith("/")]
    if anchored:
        print(
            f"distribution-audit: anchored exclude {anchored!r} in [tool.uv.build-backend] "
            "has no verified reading (uv 0.13.1 removed nothing for an anchored "
            "wheel-exclude). Write it unanchored, e.g. 'gzkit/chores/*/proofs'.",
            file=sys.stderr,
        )
        raise SystemExit(2)
    return project_root / module_root / module_name, excludes


def _load_inputs(project_root: Path) -> tuple[set[str], set[str], list[str]]:
    """Load the predicted wheel contents and baseline manifest.  Raises SystemExit(2) on failure."""
    shipped = wheel_shipped_files(project_root)

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
        baseline_entries.update(f"src/gzkit/{surface}/{entry}" for entry in entries)

    surface_roots = [f"src/gzkit/{surface}" for surface in _CANONICAL_SURFACES]
    return shipped, baseline_entries, surface_roots


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
        reason = (
            unshipped_reason(project_root, rel_posix)
            if project_root is not None
            else "the wheel does not ship it"
        )
        errors.append(
            ValidationError(
                type="distribution",
                artifact=rel_posix,
                message=(
                    f"ON_DISK_NOT_INCLUDED: '{rel_posix}' exists under a canonical surface "
                    f"tree but the uv_build wheel does not ship it: {reason}. Every "
                    f"canonical surface must ship (ADR-0.0.31). Resolution: narrow that "
                    f"exclude, or move the file under the module root, in pyproject.toml, "
                    f"then re-run `uv run gz validate --distribution`."
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
                    f"by the wheel but is NOT in the baseline manifest. "
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
    _shipped, _baseline, surface_roots = _load_inputs(project_root)
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
