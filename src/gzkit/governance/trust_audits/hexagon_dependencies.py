"""The hexagon's dependency rules as a ``gz validate`` scope (RP-15 tranche 6).

Runs the kernel's dependency checker over the package the project's package map
names (``pyproject.toml`` ``[tool.py-gzkit.hexagon]``) and holds the result to the
shrink-only ``data/hexagon_dependency_baseline.json``: a finding the baseline does
not hold fails, and so does a held finding the tree no longer produces, so the
list only shrinks while gzkit's use cases migrate after return to service.

It sits in the default tier, so it runs in every per-change ``gz check``: the
policy test it shares a checker with runs only when its own file changes, which
is RP-7's finding F22. A project with no package map yet has nothing to check and
passes; one whose map is malformed fails.

Mode contract (``.gzkit/rules/mode-contract.md``): on at the operational
condition; advisory at the hangar and drydock levels, where the MX checkpoint
demotes it like every non-critical scope, restored at the exit re-run.
"""

from typing import TYPE_CHECKING

from gzkit.kernel.dependency_checker import (
    PackageMapError,
    PackageMapMissingError,
    check,
    compare,
    load_package_map,
)
from gzkit.registries import RegistryUnreadableError, load_registry
from gzkit.validate import ValidationError

if TYPE_CHECKING:
    from pathlib import Path

__all__ = ["BASELINE", "BASELINE_NAME", "audit_hexagon_dependencies"]

_TYPE = "hexagon_dependencies"

#: The shrink-only baseline's registry name, read through ``gzkit.registries``.
BASELINE_NAME = "hexagon_dependency_baseline.json"

#: The baseline as a reader names it in a message.
BASELINE = f"data/{BASELINE_NAME}"

_SPEC = "docs/governance/hexagonal-architecture.md § The dependency rules"

_RERUN = "Fix it, then re-run `uv run gz validate --hexagon-dependencies`."


def audit_hexagon_dependencies(project_root: Path) -> list[ValidationError]:
    """Check the package against its package map and the shrink-only baseline.

    Returns:
        One error per finding the baseline does not hold, one per held finding the
        tree no longer produces, or one for a malformed package map.

    """
    pyproject = project_root / "pyproject.toml"
    if not pyproject.is_file():
        return []
    try:
        package_map = load_package_map(pyproject)
    except PackageMapMissingError:
        return []
    except PackageMapError as exc:
        message = f"{exc}: the package map cannot be read ({_SPEC}). {_RERUN}"
        return [ValidationError(type=_TYPE, artifact="pyproject.toml", message=message)]
    new, repaired = compare(check(package_map, project_root), _held(project_root))
    errors = [
        ValidationError(
            type=_TYPE,
            artifact=key.split(" ")[1],
            message=(
                f"{key}: a new hexagon dependency finding ({_SPEC}). Place the code where "
                "the package map in pyproject.toml [tool.py-gzkit.hexagon] puts it and "
                "import only what its region's row permits; never add it to "
                f"{BASELINE}. {_RERUN}"
            ),
        )
        for key in new
    ]
    errors.extend(
        ValidationError(
            type=_TYPE,
            artifact=BASELINE,
            message=(
                f"{key}: repaired, and the baseline only shrinks ({_SPEC}); remove it from "
                f"{BASELINE}, then re-run `uv run gz validate --hexagon-dependencies`."
            ),
        )
        for key in repaired
    )
    return errors


def _held(project_root: Path) -> frozenset[str]:
    """Return the finding keys the baseline holds; a project without one holds none.

    Returns:
        The held keys.

    """
    try:
        payload = load_registry(project_root, BASELINE_NAME)
    except RegistryUnreadableError:
        return frozenset()
    return frozenset(payload.get("findings", []))
