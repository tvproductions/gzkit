"""Acceptance on a work package: the contract a package gives the reducer (RO-14 act 5).

Ruling 4 makes acceptance one runtime, and the operator's direction for this act,
verbatim: "we will adapt, as much as possible, the current gz-obpi-pipeline". So a
package supplies what a brief supplies, the contract dictionary the acceptance
modules already read, and proofs, reviews, closures and readiness run unchanged.

A delivery package's obligations are its frozen REQs at their frozen revisions, less
any a `departure` exit moved out (ruling 12). A repair package's are its carried
issues, one each, named as the bound names them (`#<issue>`). Neither has the
`@covers` scan the legacy grammar has, so their proofs bind through the mutation
sweep: the named tests must kill the named mutants.

Mode contract: a read of the catalog and the ledger, on at the operational condition
and at both standby levels. It reads no marker; the refusals it raises are the
acceptance gate's, whose contract is in the RO-14 specification.
"""

import re
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.models.catalog import WORK_PACKAGE_ID_PATTERN
from gzkit.work_package_ledger import frozen_baseline, package_rows, work_package_state

if TYPE_CHECKING:
    from gzkit.ledger import Ledger
    from gzkit.models.catalog import Catalog, WorkPackage

STORE_PATH = "data/catalog/work_packages.json"
_ACCEPTABLE_STATES = frozenset({"commenced", "accepted", "closed"})


class PackageContract(BaseModel):
    """What a package gives acceptance in place of a brief."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    contract: dict[str, Any] = Field(..., description="The acceptance contract dictionary")


def is_work_package_id(identifier: str) -> bool:
    """Say whether an acceptance id names a work package.

    Returns:
        True for `WP-<NN>-<slug>`.

    """
    return re.fullmatch(WORK_PACKAGE_ID_PATTERN, identifier) is not None


def binds_by_mutation(obligation_id: str) -> bool:
    """Say whether a proof binds by killing mutants, in place of the `@covers` scan.

    Returns:
        True for a carried issue, `#<issue>`, and a catalog REQ, `REQ-<n>`.

    """
    return re.fullmatch(r"#[1-9][0-9]*|REQ-[1-9][0-9]*", obligation_id) is not None


def departed_reqs(ledger: Ledger, work_package: str) -> set[str]:
    """Read the REQs a `departure` exit moved out of the package (ruling 12).

    Returns:
        Those REQ ids, which the package no longer owes.

    """
    return {
        str(row.extra["req"])
        for row in package_rows(ledger, "work_package_unblocked", work_package)
        if row.extra.get("exit_taken") == "departure" and row.extra.get("req")
    }


def _delivery_requirements(
    catalog: Catalog, ledger: Ledger, package: WorkPackage
) -> list[dict[str, Any]]:
    held = {req.id: req for req in catalog.reqs}
    requirements = []
    departed = departed_reqs(ledger, package.id)
    for req_id, revision in sorted(frozen_baseline(ledger, package.id).items()):
        if req_id in departed:
            continue
        req = held.get(req_id)
        if req is None or req.revision != revision:
            msg = f"{req_id} is no longer at the frozen revision {revision}."
            raise ValueError(msg)
        requirements.append(
            {
                "id": req.id,
                "kind": req.kind,
                "statement": req.statement,
                "criteria": [item.model_dump(mode="json") for item in req.criteria],
            }
        )
    return requirements


def _repair_requirements(package: WorkPackage) -> list[dict[str, Any]]:
    return [
        {
            "id": f"#{issue}",
            "kind": "BEHAVIOR",
            "statement": f"Issue #{issue}, carried by {package.id}: {package.test_and_inspection}",
        }
        for issue in package.issues
    ]


def package_contract(catalog: Catalog, ledger: Ledger, work_package: str) -> PackageContract:
    """Build the acceptance contract of a commenced package.

    The contract holds the whole record but its evidence, as a brief's contract
    holds every normative section: appending objective quality evidence must not
    make a review stale, and any other edit must.

    Returns:
        The contract.

    Raises:
        ValueError: The package is unknown, not commenced, or holds no obligation.

    """
    package = next((item for item in catalog.work_packages if item.id == work_package), None)
    if package is None:
        msg = f"Work package {work_package!r} is not in {STORE_PATH}."
        raise ValueError(msg)
    state = work_package_state(ledger, package.id)
    if state not in _ACCEPTABLE_STATES:
        msg = f"Work package {package.id} is {state or 'not initiated'}, not commenced."
        raise ValueError(msg)
    requirements = (
        _delivery_requirements(catalog, ledger, package)
        if package.kind == "delivery"
        else _repair_requirements(package)
    )
    if not requirements:
        msg = f"Work package {package.id} holds no acceptance obligation."
        raise ValueError(msg)
    return PackageContract(
        contract={
            "brief": STORE_PATH,
            "authority": f"{STORE_PATH}#{package.id}",
            "id": package.id,
            "record": package.model_dump(mode="json", exclude={"oqe"}),
            "requirements": requirements,
        }
    )
