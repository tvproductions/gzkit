"""Library API for chore scaffolding and canonical-registry merge.

The ``gzkit.chores`` package directory is the canonical tree shipped in the
wheel (one subdirectory per chore slug, plus ``registry.json``). This
``__init__.py`` exposes the library functions that ``gz init`` uses to
scaffold the canonical tree into a downstream project's
``.gzkit/chores/`` directory and to merge canonical registry updates with
project-local edits without clobbering operator changes.

See ADR-0.0.21 § Decision #3 (scaffolder contract) and § Decision #6
(registry-merge contract).
"""

from __future__ import annotations

import importlib.resources
import json
from collections.abc import Iterator
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import _confirm, console
from gzkit.config import GzkitConfig

_CANONICAL_RESOURCE = "gzkit.chores"
_PER_SLUG_FILES = ("CHORE.md", "acceptance.json", "README.md")
_REGISTRY_FILE = "registry.json"
_PROJECT_LOCAL_KEY = "projectLocal"


def _chore_slug_of(path: Path) -> str | None:
    """Return the chore slug a path sits under, for either surface spelling.

    Sync passes ``<root>/.gzkit/chores/<slug>/...``; `gz init` and the
    distribution audit pass ``src/gzkit/chores/<slug>/...``. Both must resolve to
    the same slug or a withheld chore stays invisible to the audit that should
    catch it leaking.
    """
    parts = path.parts
    for index, part in enumerate(parts):
        if part == "chores" and index + 1 < len(parts):
            return parts[index + 1]
    return None


def _project_local_slugs(project_root: Path | None) -> frozenset[str]:
    """Return the slugs the project registry declares ``projectLocal``.

    Read fresh rather than cached: the registry is small, and a cache keyed on
    project_root would go stale exactly when sync rewrites the registry during
    the same run.
    """
    if project_root is None:
        return frozenset()
    registry = Path(project_root) / ".gzkit" / "chores" / _REGISTRY_FILE
    try:
        data = json.loads(registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError, ValueError):
        return frozenset()
    entries = data.get("chores") if isinstance(data, dict) else None
    if not isinstance(entries, list):
        return frozenset()
    return frozenset(
        str(entry["slug"])
        for entry in entries
        if isinstance(entry, dict) and entry.get("slug") and entry.get(_PROJECT_LOCAL_KEY) is True
    )


def exportable_registry(registry_path: Path) -> dict[str, Any]:
    """Return the registry with ``projectLocal`` slug entries removed.

    The wheel must not advertise a chore whose files it does not carry.
    ``merge_chores_registry`` is canonical-wins on shipped slugs, so a surviving
    entry would be ADDED to an adopter's registry while its files were withheld
    — a registered chore with no files, which `gz chores doctor` reports as
    MISSING. Withholding files without withholding the entry trades a leak for a
    broken install (GHI #728).
    """
    data = json.loads(Path(registry_path).read_text(encoding="utf-8"))
    entries = data.get("chores")
    if isinstance(entries, list):
        data["chores"] = [
            entry
            for entry in entries
            if not (isinstance(entry, dict) and entry.get(_PROJECT_LOCAL_KEY) is True)
        ]
    return data


def _classify_chore_file(
    path: Path,
    *,
    project_root: Path | None = None,
) -> Literal["canonical", "package_only", "runtime_state", "project_local"]:
    """Classify a chore file into one of four content classes.

    canonical: CHORE.md, AGENTS.md, *.md outside proofs/, acceptance.json,
               registry.json, authored .py tool scripts (present at .gzkit/ surface)
    package_only: __init__.py, __pycache__/**, Python modules with no
                  .gzkit/chores/ counterpart
    runtime_state: CHORE-LOG.md, proofs/**, .gitkeep
    project_local: every file under a slug whose registry entry declares
               ``projectLocal: true`` — gzkit's own maintenance chores, which
               must not reach the wheel or an adopter (GHI #728)

    See .gzkit/rules/skill-surface-sync.md § Chores class-classifier.
    """
    path = Path(path)
    name = path.name
    parts = path.parts
    path_posix = path.as_posix()

    # project_local: the whole slug is withheld, whatever the file type. Checked
    # first because the declaration is per-slug — a per-file class cannot
    # override it without re-opening the export this closes.
    slug = _chore_slug_of(path)
    if slug is not None and slug in _project_local_slugs(project_root):
        return "project_local"

    # A slug is DEFINED by its CHORE.md. A bare directory under the chores
    # surface carrying neither a CHORE.md nor a registry entry is an orphan, not
    # a chore: `_iter_canonical_chore_slugs` will not walk it and `gz chores
    # list` cannot resolve it, so claiming its files as canonical would assert a
    # delivery that no code path performs (`owasp-top10-2025-scan`, 2026-08-09).
    if slug is not None and project_root is not None and not _slug_has_chore_md(project_root, slug):
        return "package_only"

    # runtime_state: proofs/ contents, .gitkeep, CHORE-LOG.md
    if "proofs" in parts or name in (".gitkeep", "CHORE-LOG.md"):
        return "runtime_state"

    # package_only: __init__.py and __pycache__
    if name == "__init__.py" or "__pycache__" in parts:
        return "package_only"

    # .py files: canonical only when present at .gzkit/ surface
    if name.endswith(".py"):
        if ".gzkit/chores/" in path_posix:
            return "canonical"
        # src/ surface: check for .gzkit/ counterpart when project_root is known
        if project_root is not None:
            try:
                rel = path.relative_to(project_root / "src" / "gzkit" / "chores")
                counterpart = project_root / ".gzkit" / "chores" / rel
                return "canonical" if counterpart.exists() else "package_only"
            except ValueError:
                pass
        return "package_only"

    # Default: canonical (CHORE.md, AGENTS.md, *.md, acceptance.json, registry.json, etc.)
    return "canonical"


def _slug_has_chore_md(project_root: Path, slug: str) -> bool:
    """Return True when either surface carries a ``CHORE.md`` for ``slug``."""
    return any(
        (project_root / surface / "chores" / slug / "CHORE.md").is_file()
        for surface in (".gzkit", "src/gzkit")
    )


def _iter_slug_files(
    slug_resource: Traversable, prefix: Path | None = None
) -> Iterator[tuple[Traversable, Path]]:
    """Yield ``(source, rel_path)`` for every file a chore slug ships.

    Replaces a hardcoded three-name allowlist.  A list of filenames cannot
    report the file it omits, so a slug's gate script or auxiliary data file
    shipped in the wheel and never reached an adopter; the class membership is
    decided by ``_classify_chore_file`` at the call site instead.
    """
    prefix = prefix or Path()
    for entry in slug_resource.iterdir():
        if entry.name.startswith("__"):
            continue
        rel = prefix / entry.name
        if entry.is_dir():
            yield from _iter_slug_files(entry, rel)
        elif entry.is_file():
            yield entry, rel


def _iter_canonical_chore_slugs() -> Iterator[Traversable]:
    """Yield each canonical chore-slug directory (one per slug)."""
    root = importlib.resources.files(_CANONICAL_RESOURCE)
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("__"):
            continue
        if not entry.joinpath("CHORE.md").is_file():
            continue
        yield entry


def scaffold_core_chores(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    skip_existing: bool = False,
) -> list[Path]:
    """Scaffold all canonical chores into ``<project_root>/<config.paths.chores>``.

    Args:
        project_root: Project root directory.
        config: Optional configuration; defaults to loading from
            ``project_root / .gzkit.json``.
        skip_existing: When True, skip any slug whose destination directory
            already exists on disk. Used by repair mode so upgraded gzkit
            versions deliver new canonical slugs without overwriting
            operator-modified existing ones.

    Returns:
        List of paths to created ``CHORE.md`` files (one per scaffolded
        slug). Empty list when every slug was skipped.

    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    chores_dir = project_root / config.paths.chores
    chores_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for slug_resource in _iter_canonical_chore_slugs():
        slug = slug_resource.name
        target_dir = chores_dir / slug
        if skip_existing and target_dir.exists():
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        for source, rel in _iter_slug_files(slug_resource):
            # Classify against the DESTINATION spelling: `.gzkit/chores/...` is
            # canonical by definition, so a gate script resolves without the
            # `.gzkit/` counterpart test — which can never succeed at adopter
            # init time, because the counterpart is what init is creating.
            if _classify_chore_file(Path(".gzkit/chores") / slug / rel) != "canonical":
                continue
            target = target_dir / rel
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(source.read_bytes())
        chore_md = target_dir / "CHORE.md"
        if chore_md.exists():
            created.append(chore_md)

    _scaffold_surface_level_files(chores_dir)

    if not (chores_dir / _REGISTRY_FILE).exists():
        canonical_registry = importlib.resources.files(_CANONICAL_RESOURCE).joinpath(_REGISTRY_FILE)
        if canonical_registry.is_file():
            (chores_dir / _REGISTRY_FILE).write_bytes(canonical_registry.read_bytes())

    return created


def _scaffold_surface_level_files(chores_dir: Path) -> None:
    """Deliver the chores surface's own documents, which sit outside any slug.

    A slug walk cannot reach them: `_iter_canonical_chore_slugs` admits only
    directories carrying a `CHORE.md`. `.gzkit/rules/chores.md` names
    `README.md` as the authoring contract, so an adopter without it is pointed
    at a file they were never sent.
    """
    root = importlib.resources.files(_CANONICAL_RESOURCE)
    for entry in root.iterdir():
        if entry.is_dir() or entry.name.startswith("__") or entry.name == _REGISTRY_FILE:
            continue
        if _classify_chore_file(Path(".gzkit/chores") / entry.name) != "canonical":
            continue
        target = chores_dir / entry.name
        if not target.exists():
            target.write_bytes(entry.read_bytes())


class RegistryMergeReport(BaseModel):
    """Result of merging canonical and project-local chores registries."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    added: list[str] = Field(default_factory=list, description="Slugs new in canonical")
    removed: list[str] = Field(
        default_factory=list, description="Slugs removed from canonical (kept locally)"
    )
    changed: list[str] = Field(
        default_factory=list, description="Slugs whose canonical record changed"
    )
    unchanged_local: list[str] = Field(
        default_factory=list, description="Local-only slugs preserved"
    )
    wrote: bool = Field(False, description="True when the merged registry was written")
    local_registry_path: Path = Field(..., description="Path to local registry.json")


def _load_canonical_registry() -> dict[str, Any]:
    canonical = importlib.resources.files(_CANONICAL_RESOURCE).joinpath(_REGISTRY_FILE)
    return json.loads(canonical.read_text(encoding="utf-8"))


def _index_chores(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {entry["slug"]: entry for entry in payload.get("chores", [])}


def merge_chores_registry(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    auto_yes: bool = False,
    dry_run: bool = False,
) -> RegistryMergeReport:
    """Merge the canonical chores registry into the project-local registry.

    Reads the canonical ``registry.json`` from ``importlib.resources`` and
    the project-local one from ``<chores_dir>/registry.json``. Computes the
    union (canonical-wins on shipped slugs, local-wins on unknown slugs),
    prints a diff to stdout, and unless ``auto_yes`` or ``dry_run`` is set,
    prompts the operator before writing.

    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    chores_dir = project_root / config.paths.chores
    local_registry_path = chores_dir / _REGISTRY_FILE

    if not local_registry_path.exists():
        return RegistryMergeReport(local_registry_path=local_registry_path)

    canonical = _load_canonical_registry()
    local = json.loads(local_registry_path.read_text(encoding="utf-8"))

    canonical_chores = _index_chores(canonical)
    local_chores = _index_chores(local)

    added = sorted(set(canonical_chores) - set(local_chores))
    removed = sorted(set(local_chores) - set(canonical_chores))
    changed = sorted(
        slug
        for slug in set(canonical_chores) & set(local_chores)
        if canonical_chores[slug] != local_chores[slug]
    )
    unchanged_local = sorted(set(local_chores) - set(canonical_chores))

    if not (added or changed):
        return RegistryMergeReport(
            unchanged_local=unchanged_local,
            local_registry_path=local_registry_path,
        )

    console.print("[bold]Chores registry diff:[/bold]")
    for slug in added:
        console.print(f"  [green]+ {slug}[/green]")
    for slug in changed:
        console.print(f"  [yellow]~ {slug}[/yellow]")
    for slug in removed:
        console.print(f"  [dim]= {slug} (local-only, preserved)[/dim]")

    if dry_run:
        return RegistryMergeReport(
            added=added,
            removed=removed,
            changed=changed,
            unchanged_local=unchanged_local,
            local_registry_path=local_registry_path,
        )

    if not auto_yes and not _confirm("Merge canonical updates into local registry?"):
        return RegistryMergeReport(
            added=added,
            removed=removed,
            changed=changed,
            unchanged_local=unchanged_local,
            local_registry_path=local_registry_path,
        )

    merged_chores: dict[str, dict[str, Any]] = {}
    for slug, entry in canonical_chores.items():
        merged_chores[slug] = entry
    for slug, entry in local_chores.items():
        if slug not in canonical_chores:
            merged_chores[slug] = entry

    merged_payload = dict(canonical)
    merged_payload["chores"] = list(merged_chores.values())
    local_registry_path.write_text(json.dumps(merged_payload, indent=4) + "\n", encoding="utf-8")

    return RegistryMergeReport(
        added=added,
        removed=removed,
        changed=changed,
        unchanged_local=unchanged_local,
        wrote=True,
        local_registry_path=local_registry_path,
    )


__all__ = [
    "RegistryMergeReport",
    "merge_chores_registry",
    "scaffold_core_chores",
]
