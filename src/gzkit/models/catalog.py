"""The requirements catalog: families, outcomes and REQs (drydock RO-3).

The store `docs/governance/ieee/requirements-model.md` rules, laid out as
`docs/governance/harbor-ro3-requirements-store.md` § The store specifies: three
files under `data/catalog/`, each a list under a `_doc` header, one model and one
committed schema each. Tranche 3 adds a fourth, the roster of external boundaries
`depends_on` may name (operator, "Declared prefixes (Rec.)", 2026-10-22). RO-5
tranche 1 adds a fifth, the work packages (`docs/governance/harbor-ro5-work-packages.md`).

What a catalog entry does NOT carry is as ruled as what it does: an outcome has
no lifecycle state (delivery status lives only in the ledger, decision 3) and a
REQ has no proof (proof lives only in the ledger, decision 4). `extra="forbid"`
is what keeps either from creeping back in as a field.
"""

from pathlib import Path
from typing import Any, Literal

from pydantic import AwareDatetime, BaseModel, ConfigDict, Field

from gzkit.core.models import CATALOG_REQ_ID_BODY
from gzkit.registries import load_registry

#: The catalog files, by kind, and the seam name each is read under.
CATALOG_FILES: dict[str, str] = {
    "families": "catalog/families.json",
    "outcomes": "catalog/outcomes.json",
    "reqs": "catalog/reqs.json",
    "externals": "catalog/externals.json",
    "work_packages": "catalog/work_packages.json",
}

#: The forward rule's registry, read beside the catalog but not part of it (RO-3 tranche 4).
DELIVERY_EVENTS_FILE = "catalog/delivery_events.json"

#: An outcome code: its family letter and a dotted number, `H1.4`.
OUTCOME_CODE_PATTERN = r"^[A-Z][1-9][0-9]*(\.[1-9][0-9]*)*$"

#: A catalog REQ id, its grammar held by the identity seam.
REQ_ID_PATTERN = rf"^{CATALOG_REQ_ID_BODY}$"

#: One id series for every work package, repair or delivery: `WP-<NN>-<slug>` (RO-5 ruling 6).
WORK_PACKAGE_ID_PATTERN = r"^WP-[0-9]{2,}-[a-z0-9]+(-[a-z0-9]+)*$"


class Family(BaseModel):
    """One family in the legend (decision 8.3)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(..., pattern=r"^[A-Z]$", description="The family's one letter.")
    band: Literal["product", "common"] = Field(
        ..., description="Product element or common element (MIL-STD-881's compromise)."
    )
    name: str = Field(..., min_length=1, description="The family's name.")
    scope: str = Field(..., min_length=1, description="The family's scope, one sentence.")


class Outcome(BaseModel):
    """One outcome: a stable capability a family delivers."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    code: str = Field(..., pattern=OUTCOME_CODE_PATTERN, description="Family letter and number.")
    statement: str = Field(..., min_length=1, description="What the outcome delivers.")
    owner: str = Field(..., min_length=1, description="Who owns the outcome.")
    user_facing: bool = Field(..., description="Decision 10's test: a user observes it.")
    governed_by: tuple[str, ...] = Field(..., description="ADR ids whose decisions govern it.")
    depends_on: tuple[str, ...] = Field(
        ..., description="Outcome codes, gates or named external boundaries it relies on."
    )
    feature: str | None = Field(
        ..., description="Feature file carrying the outcome's code as a tag, when user-facing."
    )
    retired: bool = Field(..., description="A retired code stays, so it is never reused.")


class Criterion(BaseModel):
    """One acceptance criterion, on the `ghi-close` closure-contract precedent."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    state_or_input: str = Field(..., min_length=1, description="The state or input.")
    required_outcome: str = Field(..., min_length=1, description="What must then hold.")
    evidence: str = Field(..., min_length=1, description="The semantic evidence that shows it.")


class Req(BaseModel):
    """One requirement, a member of exactly one outcome."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=REQ_ID_PATTERN, description="`REQ-<n>`, never reused.")
    member_of: str = Field(..., pattern=OUTCOME_CODE_PATTERN, description="Its outcome's code.")
    statement: str = Field(..., min_length=1, description="Effect and rationale.")
    criteria: tuple[Criterion, ...] = Field(..., min_length=1, description="Acceptance criteria.")
    kind: Literal["BEHAVIOR", "SUPPORT", "STRUCTURAL-FENCE"] = Field(
        ..., description="Which proof channel binds it (ADR-0.0.59)."
    )
    revision: int = Field(..., ge=1, description="Only rises.")
    derives_from: tuple[str, ...] = Field(..., description="PRD FR ids or section 7 attributes.")
    applies_to: tuple[str, ...] = Field(..., description="Targets, for a Q-family NFR only.")


class External(BaseModel):
    """One external boundary an outcome may depend on, as `external:<slug>`.

    The roster is the operator's "Declared prefixes (Rec.)" ruling of 2026-10-22:
    a boundary is named only if the catalog declares it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str = Field(..., pattern=r"^[a-z][a-z0-9-]*$", description="The name after `external:`.")
    name: str = Field(..., min_length=1, description="The boundary's name.")
    scope: str = Field(..., min_length=1, description="What crosses it, one sentence.")


class Alteration(BaseModel):
    """A planned remodel, approved at freeze and accounted for at close (RO-5 amendment 4)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., min_length=1, description="Unique within its package.")
    description: str = Field(..., min_length=1, description="What the remodel changes.")
    configuration_change: Literal["reconnected", "replaced", "retired"] = Field(
        ..., description="The maintenance-record line it is accounted as."
    )


class Departure(BaseModel):
    """A departure from the package's own approved specification (RO-5 amendment 4)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., min_length=1, description="Unique within its package.")
    description: str = Field(..., min_length=1, description="What the work cannot meet.")
    form: Literal["deviation", "waiver"] = Field(
        ..., description="Requested before the work, or after the nonconformance is found."
    )
    duration: Literal["temporary", "permanent"] = Field(..., description="How long it stands.")
    clear_by: str | None = Field(
        ..., description="The clear-by condition; required when temporary, absent when permanent."
    )
    req: str | None = Field(
        ..., pattern=REQ_ID_PATTERN, description="The REQ it departs on, as its scope disposition."
    )


class WorkPackage(BaseModel):
    """One work package: its formal work package and its objective quality evidence.

    RO-5 rulings 1, 4 and 6 and the 2026-10-28 amendment, the shape ruled by the
    operator at tranche 1 ("Accept as drafted (Recommended)"). A delivery package
    names its outcome and holds no lane, which the outcome derives; a repair
    package names its issues and holds its lane. Lifecycle state lives only in
    the ledger, so no field carries it.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., pattern=WORK_PACKAGE_ID_PATTERN, description="`WP-<NN>-<slug>`.")
    kind: Literal["delivery", "repair"] = Field(..., description="Never the id's spelling.")
    outcome: str | None = Field(
        ..., pattern=OUTCOME_CODE_PATTERN, description="The outcome a delivery package delivers."
    )
    issues: tuple[int, ...] = Field(..., description="The GitHub issues a repair package carries.")
    lane: Literal["lite", "heavy"] | None = Field(
        ..., description="Stored on a repair package only."
    )
    aliases: tuple[str, ...] = Field(..., description="Drydock names such as `RO-9`.")
    initial_conditions: str = Field(..., min_length=1, description="Tag-out line items, or NA.")
    procedure: str = Field(..., min_length=1, description="The task cards, or NA.")
    test_and_inspection: str = Field(
        ..., min_length=1, description="The REQ baseline, closing test and dock trial, or NA."
    )
    system_restoration: str = Field(..., min_length=1, description="The restoration, or NA.")
    oqe: tuple[str, ...] = Field(
        ..., description="Objective quality evidence: receipts, commits, paths."
    )
    alterations: tuple[Alteration, ...] = Field(..., description="The planned remodels.")
    departures: tuple[Departure, ...] = Field(..., description="Departures from specification.")


class FamiliesFile(BaseModel):
    """`data/catalog/families.json`."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    doc: str = Field(..., alias="_doc", min_length=1, description="What the file is.")
    families: tuple[Family, ...] = Field(..., description="The family legend.")


class OutcomesFile(BaseModel):
    """`data/catalog/outcomes.json`."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    doc: str = Field(..., alias="_doc", min_length=1, description="What the file is.")
    outcomes: tuple[Outcome, ...] = Field(..., description="The outcomes.")


class ReqsFile(BaseModel):
    """`data/catalog/reqs.json`."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    doc: str = Field(..., alias="_doc", min_length=1, description="What the file is.")
    reqs: tuple[Req, ...] = Field(..., description="The requirements.")


class ExternalsFile(BaseModel):
    """`data/catalog/externals.json`."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    doc: str = Field(..., alias="_doc", min_length=1, description="What the file is.")
    externals: tuple[External, ...] = Field(..., description="The external boundaries.")


class WorkPackagesFile(BaseModel):
    """`data/catalog/work_packages.json`, edited only through `gz` verbs (RO-5 ruling 3)."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    doc: str = Field(..., alias="_doc", min_length=1, description="What the file is.")
    work_packages: tuple[WorkPackage, ...] = Field(..., description="The work packages.")


FILE_MODELS: dict[str, type[BaseModel]] = {
    "families": FamiliesFile,
    "outcomes": OutcomesFile,
    "reqs": ReqsFile,
    "externals": ExternalsFile,
    "work_packages": WorkPackagesFile,
}


class Catalog(BaseModel):
    """The catalog files, parsed."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    families: tuple[Family, ...]
    outcomes: tuple[Outcome, ...]
    reqs: tuple[Req, ...]
    externals: tuple[External, ...] = ()
    work_packages: tuple[WorkPackage, ...] = ()


def catalog_json_schemas() -> dict[str, dict[str, Any]]:
    """Project each file model to its committed `src/gzkit/schemas/catalog_<kind>.json`."""
    return {kind: model.model_json_schema() for kind, model in FILE_MODELS.items()}


def load_catalog(project_root: Path) -> Catalog:
    """Read and parse the catalog files through the registry seam.

    Raises `RegistryError` for a file that is missing or not JSON, and Pydantic's
    `ValidationError` for one that does not match its model.
    """
    families = FamiliesFile.model_validate(load_registry(project_root, CATALOG_FILES["families"]))
    outcomes = OutcomesFile.model_validate(load_registry(project_root, CATALOG_FILES["outcomes"]))
    reqs = ReqsFile.model_validate(load_registry(project_root, CATALOG_FILES["reqs"]))
    externals = ExternalsFile.model_validate(
        load_registry(project_root, CATALOG_FILES["externals"])
    )
    work_packages = WorkPackagesFile.model_validate(
        load_registry(project_root, CATALOG_FILES["work_packages"])
    )
    return Catalog(
        families=families.families,
        outcomes=outcomes.outcomes,
        reqs=reqs.reqs,
        externals=externals.externals,
        work_packages=work_packages.work_packages,
    )


class DeliveryEventsFile(BaseModel):
    """`data/catalog/delivery_events.json`: the forward rule's event types and cutover.

    Rulings of 2026-10-22: the nine measured types ("All nine (Rec.)") and the
    cutover as a timestamp held here ("Timestamp in registry (Rec.)"); events
    before it are legacy and never read.
    """

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    doc: str = Field(..., alias="_doc", min_length=1, description="What the file is.")
    cutover: AwareDatetime = Field(..., description="Events with a later `ts` are read.")
    event_types: tuple[str, ...] = Field(
        ..., min_length=1, description="The delivery event types the forward rule reads."
    )


def delivery_events_json_schema() -> dict[str, Any]:
    """Project the registry model to its committed `catalog_delivery_events.json` schema."""
    return DeliveryEventsFile.model_json_schema()


def load_delivery_events(project_root: Path) -> DeliveryEventsFile:
    """Read and parse the forward rule's registry through the registry seam."""
    return DeliveryEventsFile.model_validate(load_registry(project_root, DELIVERY_EVENTS_FILE))
