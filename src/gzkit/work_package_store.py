"""The work-package store's one writer (drydock RO-5 tranche 2).

`data/catalog/work_packages.json` is edited only through `gz` verbs (RO-5 ruling
3), and this module is what they call. Every write is checked against the same
rules `gz validate --catalog` reads (`work_package_findings`) before it reaches
the file, so a verb can never leave the store in a state the scope refuses.
"""

import json
from typing import TYPE_CHECKING

from gzkit.governance.trust_audits.catalog import work_package_findings
from gzkit.models.catalog import CATALOG_FILES, Catalog, WorkPackage
from gzkit.registries import load_registry, registry_path

if TYPE_CHECKING:
    from pathlib import Path


class WorkPackageStoreError(ValueError):
    """A store edit the RO-5 rulings refuse; nothing was written."""


def next_id(catalog: Catalog, slug: str) -> str:
    """Return the next id in the one series (ruling 6): the highest number plus one.

    Returns:
        `WP-<NN>-<slug>`, numbered past every package the store holds.

    """
    numbers = [int(package.id.split("-")[1]) for package in catalog.work_packages]
    return f"WP-{max(numbers, default=0) + 1:02d}-{slug}"


def _replaced(catalog: Catalog, package: WorkPackage) -> Catalog:
    others = tuple(wp for wp in catalog.work_packages if wp.id != package.id)
    ordered = sorted((*others, package), key=lambda wp: int(wp.id.split("-")[1]))
    return catalog.model_copy(update={"work_packages": tuple(ordered)})


def stage(catalog: Catalog, package: WorkPackage) -> Catalog:
    """Return the catalog with the package added or replaced, refusing a breach.

    Returns:
        The catalog as it would read once written.

    Raises:
        WorkPackageStoreError: The edit breaks a rule `gz validate --catalog` reads.

    """
    staged = _replaced(catalog, package)
    findings = work_package_findings(staged)
    if findings:
        raise WorkPackageStoreError(" ".join(finding.message for finding in findings))
    return staged


def write(project_root: Path, catalog: Catalog) -> Path:
    """Write the catalog's work packages, keeping the file's `_doc` header.

    Returns:
        The path written.

    """
    name = CATALOG_FILES["work_packages"]
    doc = load_registry(project_root, name)["_doc"]
    packages = [package.model_dump(mode="json") for package in catalog.work_packages]
    path = registry_path(project_root, name)
    text = json.dumps({"_doc": doc, "work_packages": packages}, indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")
    return path
