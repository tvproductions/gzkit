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
from typing import Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import _confirm, console
from gzkit.config import GzkitConfig

_CANONICAL_RESOURCE = "gzkit.chores"
_PER_SLUG_FILES = ("CHORE.md", "acceptance.json", "README.md")
_REGISTRY_FILE = "registry.json"


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
        for filename in _PER_SLUG_FILES:
            source = slug_resource.joinpath(filename)
            if not source.is_file():
                continue
            target = target_dir / filename
            target.write_bytes(source.read_bytes())
        chore_md = target_dir / "CHORE.md"
        if chore_md.exists():
            created.append(chore_md)

    if not (chores_dir / _REGISTRY_FILE).exists():
        canonical_registry = importlib.resources.files(_CANONICAL_RESOURCE).joinpath(_REGISTRY_FILE)
        if canonical_registry.is_file():
            (chores_dir / _REGISTRY_FILE).write_bytes(canonical_registry.read_bytes())

    return created


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
