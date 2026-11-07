"""Acceptance on a work package: the contract a package gives the reducer (RO-14 act 5).

Ruling 4 makes acceptance one runtime, and the operator's direction for this act,
verbatim: "we will adapt, as much as possible, the current gz-obpi-pipeline". So a
package supplies what a brief supplies, the contract dictionary the acceptance
modules already read, and proofs, reviews, closures and readiness run unchanged.

A delivery package's obligations are its frozen REQs at their frozen revisions, less
any a `departure` exit moved out (ruling 12). A repair package's are its carried
issues, one each, named as the bound names them (`#<issue>`). An order's are its
own frozen REQs, less those a `departure` exit on the order moved out, and its
records are kept under the order's id (RP-12 ruling 60). Neither has the
`@covers` scan the legacy grammar has, so their proofs bind through the mutation
sweep: the named tests must kill the named mutants.

Mode contract: a read of the catalog and the ledger, on at the operational condition
and at both standby levels. It reads no marker; the refusals it raises are the
acceptance gate's, whose contract is in the RO-14 specification.
"""

import re
from typing import TYPE_CHECKING, Any

from pydantic import BaseModel, ConfigDict, Field

from gzkit.core.models import CATALOG_REQ_ID_BODY
from gzkit.models.catalog import ORDER_ID_PATTERN, WORK_PACKAGE_ID_PATTERN
from gzkit.order_ledger import order_baseline, order_rows, order_state
from gzkit.work_package_ledger import frozen_baseline, package_rows, work_package_state

if TYPE_CHECKING:
    from gzkit.ledger import Ledger
    from gzkit.models.catalog import Catalog, WorkPackage

STORE_PATH = "data/catalog/work_packages.json"
ORDER_STORE_PATH = "data/catalog/orders.json"
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


def is_order_id(identifier: str) -> bool:
    """Say whether an acceptance id names an order (RP-12 ruling 60).

    Returns:
        True for `ORD-<NN>-<slug>`.

    """
    return re.fullmatch(ORDER_ID_PATTERN, identifier) is not None


def is_run_id(identifier: str) -> bool:
    """Say whether an acceptance id names a package or an order, never an OBPI.

    Returns:
        True for `WP-<NN>-<slug>` and `ORD-<NN>-<slug>`.

    """
    return is_work_package_id(identifier) or is_order_id(identifier)


def binds_by_mutation(obligation_id: str) -> bool:
    """Say whether a proof binds by killing mutants, in place of the `@covers` scan.

    Returns:
        True for a carried issue, `#<issue>`, and a catalog REQ, `REQ-<n>`.

    """
    return re.fullmatch(rf"#[1-9][0-9]*|{CATALOG_REQ_ID_BODY}", obligation_id) is not None


def departed_reqs(ledger: Ledger, run_id: str) -> set[str]:
    """Read the REQs a `departure` exit moved out of the package or order (ruling 12).

    An order's exits are its own, as its block is (RP-12 ruling 59).

    Returns:
        Those REQ ids, which the package or order no longer owes.

    """
    reader = order_rows if is_order_id(run_id) else package_rows
    return {
        str(row.extra["req"])
        for row in reader(ledger, "work_package_unblocked", run_id)
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


def _baseline_requirements(
    catalog: Catalog, baseline: dict[str, int], departed: set[str]
) -> list[dict[str, Any]]:
    """Read a frozen baseline as acceptance obligations, at the revisions frozen.

    Returns:
        One requirement per baseline REQ a departure did not move out.

    Raises:
        ValueError: A REQ is no longer at its frozen revision.

    """
    held = {req.id: req for req in catalog.reqs}
    requirements = []
    for req_id, revision in sorted(baseline.items()):
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


def order_contract(catalog: Catalog, ledger: Ledger, order_id: str) -> PackageContract:
    """Build the acceptance contract of a commenced order (RP-12 ruling 60).

    Returns:
        The contract: the order's record and its frozen REQs at their revisions.

    Raises:
        ValueError: The order is unknown, not commenced, or owes no obligation.

    """
    order = next((item for item in catalog.orders if item.id == order_id), None)
    if order is None:
        msg = f"Order {order_id!r} is not in {ORDER_STORE_PATH}."
        raise ValueError(msg)
    state = order_state(ledger, order.id)
    if state not in _ACCEPTABLE_STATES:
        msg = f"Order {order.id} is {state or 'not opened'}, not commenced."
        raise ValueError(msg)
    baseline = order_baseline(ledger, order.id)
    requirements = _baseline_requirements(catalog, baseline, departed_reqs(ledger, order.id))
    if not requirements:
        msg = f"Order {order.id} holds no acceptance obligation."
        raise ValueError(msg)
    return PackageContract(
        contract={
            "brief": ORDER_STORE_PATH,
            "authority": f"{ORDER_STORE_PATH}#{order.id}",
            "id": order.id,
            "record": order.model_dump(mode="json"),
            "requirements": requirements,
        }
    )


def run_contract(catalog: Catalog, ledger: Ledger, run_id: str) -> PackageContract:
    """Build the acceptance contract of a package or an order.

    Returns:
        The contract.

    """
    if is_order_id(run_id):
        return order_contract(catalog, ledger, run_id)
    return package_contract(catalog, ledger, run_id)


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
