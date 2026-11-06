"""The requirement store's writer for repair requirements (RP-12 O2 task 2).

`data/catalog/reqs.json` holds both specializations in one `REQ-<n>` sequence
(RP-12 ruling 45). `gz wp req new` writes repair requirements through this module
(ruling 48); catalog requirements stay RP-11's intake. Every write is checked
against the rules `gz validate --catalog` reads (`req_breaches`) before it reaches
the file, and the store only grows: a change to an obligation is a new REQ
carrying `supersedes` (ruling 31).
"""

import json
from typing import TYPE_CHECKING

from gzkit.core.models import catalog_req_number, compose_catalog_req_id
from gzkit.governance.trust_audits.catalog import req_breaches
from gzkit.models.catalog import CATALOG_FILES, Catalog, RepairReq
from gzkit.registries import load_registry, registry_path

if TYPE_CHECKING:
    from pathlib import Path


class ReqStoreError(ValueError):
    """A requirement edit RP-12's rulings refuse; nothing was written.

    Carries each breach as a sentence naming its ruling.
    """

    def __init__(self, breaches: list[str], *, in_store: bool = False) -> None:
        """Hold the breaches, and whether the store broke its rules before this edit."""
        super().__init__(" ".join(breaches))
        self.breaches = breaches
        self.in_store = in_store


def next_req_id(catalog: Catalog, booked: set[str]) -> str:
    """Return the next id in the one sequence (requirements model § 2).

    ``booked`` holds the REQ ids the ledger names, so an id removed from the file is
    never minted again (`booked_req_ids`).

    Returns:
        `REQ-<n>`, numbered past every REQ of either specialization and every booked id.

    """
    held = {req.id for req in catalog.reqs} | booked
    numbers = [catalog_req_number(req_id) for req_id in held]
    return compose_catalog_req_id(max(numbers, default=0) + 1)


def stage_repair_req(catalog: Catalog, req: RepairReq) -> Catalog:
    """Return the catalog with the repair REQ added, refusing a breach.

    Returns:
        The catalog as it would read once written.

    Raises:
        ReqStoreError: The store breaks its rules already, the REQ's id is held, or
            the edit breaks a rule `gz validate --catalog` reads.

    """
    if existing := req_breaches(catalog):
        raise ReqStoreError(existing, in_store=True)
    if any(held.id == req.id for held in catalog.reqs):
        raise ReqStoreError([f"{req.id} is in the store already; an id is never reused."])
    staged = catalog.model_copy(update={"reqs": (*catalog.reqs, req)})
    if breaches := req_breaches(staged):
        raise ReqStoreError(breaches)
    return staged


def write_reqs(project_root: Path, catalog: Catalog) -> Path:
    """Write the catalog's requirements, keeping the file's `_doc` header.

    Returns:
        The path written.

    """
    name = CATALOG_FILES["reqs"]
    doc = load_registry(project_root, name)["_doc"]
    reqs = [req.model_dump(mode="json") for req in catalog.reqs]
    path = registry_path(project_root, name)
    text = json.dumps({"_doc": doc, "reqs": reqs}, indent=2, ensure_ascii=False)
    path.write_text(text + "\n", encoding="utf-8")
    return path
