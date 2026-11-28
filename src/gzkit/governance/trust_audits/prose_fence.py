"""The file population a prose fence reads, shared by the doctrine fences (GHI #1370).

A doctrine fence refuses a class of statement on every live surface, so the files
it reads decide what it can catch. The prompt-audit fences (M4, M7, M8, M9) began
as unit tests that read the tree, which the tautology audit classes as a content
echo. Under the operator's ruling on #1370 ("A") each is a `gz validate` scope that
reads prose as data, and this module is the walk they share.

A root that is not there is skipped, so a default-tier fence runs in an adopter
project over whatever that project has. On gzkit's own tree a missing root is a
finding instead: there every declared root exists, so a missing one means a
directory was renamed and the fence silently stopped reading it. The distinction
is `gzkit.rules.is_framework_tree`, as in the instruction-reachability audit
(GHI #912).
"""

from typing import TYPE_CHECKING

from gzkit.core.validation_rules import ValidationError
from gzkit.rules import is_framework_tree

if TYPE_CHECKING:
    from collections.abc import Iterable
    from pathlib import Path


def live_files(
    project_root: Path,
    roots: Iterable[str],
    *,
    suffixes: Iterable[str],
    root_files: Iterable[str] = (),
    skip_parts: Iterable[str] = (),
    skip_under: Iterable[str] = (),
    exclude: Iterable[str] = (),
) -> list[Path]:
    """Return the files under *roots* (and *root_files*) a fence reads, sorted.

    Args:
        project_root: The project whose tree is read.
        roots: Directories, relative to *project_root*, read recursively.
        suffixes: File suffixes read; an empty string reads extensionless files.
        root_files: Single files, relative to *project_root*, read when present,
            whatever their suffix: naming one is the choice to read it.
        skip_parts: Path components that exclude a file wherever they occur.
        skip_under: Directories, relative to *project_root*, whose files are dated
            records and are not read.
        exclude: Files, relative to *project_root*, not read (the authority).

    Returns:
        Every matching file that exists, in path order.

    """
    wanted = set(suffixes)
    skipped = set(skip_parts) | {"__pycache__"}
    under = [project_root / rel for rel in skip_under]
    excluded = {project_root / rel for rel in exclude}
    found: set[Path] = set()
    for rel in roots:
        root = project_root / rel
        if root.is_dir():
            found.update(path for path in root.rglob("*") if path.is_file())
    named = {project_root / rel for rel in root_files if (project_root / rel).is_file()}
    return sorted(
        path
        for path in found | named
        if (path.suffix in wanted or path in named)
        and path not in excluded
        and not any(path.is_relative_to(record) for record in under)
        and not skipped.intersection(path.relative_to(project_root).parts)
    )


def missing_roots(
    project_root: Path, paths: Iterable[str], *, error_type: str, prefix: str, scope: str
) -> list[ValidationError]:
    """Return one finding per declared path absent from gzkit's own tree.

    In an adopter project nothing is reported: an adopter carries only what
    `gz init` gave it, so an absent root there narrows nothing.

    Returns:
        A finding for each absent path when *project_root* is gzkit's tree, else none.

    """
    if not is_framework_tree(project_root):
        return []
    return [
        ValidationError(
            type=error_type,
            artifact=rel,
            message=(
                f"{prefix} {rel} is declared as a fence root but is absent from gzkit's "
                "tree, so the fence has stopped reading it: a renamed directory would "
                "otherwise shrink the fence without a finding (GHI #1370). Update the "
                f"root in the scope's module to its new path, then re-run "
                f"`uv run gz validate --{scope}`."
            ),
        )
        for rel in paths
        if not (project_root / rel).exists()
    ]
