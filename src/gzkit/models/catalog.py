"""The requirements catalog: families, outcomes and REQs (drydock RO-3).

The store `docs/governance/ieee/requirements-model.md` rules, laid out as
`docs/governance/harbor-ro3-requirements-store.md` § The store specifies: three
files under `data/catalog/`, each a list under a `_doc` header, one model and one
committed schema each. Tranche 3 adds a fourth, the roster of external boundaries
`depends_on` may name (operator, "Declared prefixes (Rec.)", 2026-10-22).

What a catalog entry does NOT carry is as ruled as what it does: an outcome has
no lifecycle state (delivery status lives only in the ledger, decision 3) and a
REQ has no proof (proof lives only in the ledger, decision 4). `extra="forbid"`
is what keeps either from creeping back in as a field.
"""

from __future__ import annotations

from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.core.models import CATALOG_REQ_ID_BODY
from gzkit.registries import load_registry

#: The catalog files, by kind, and the seam name each is read under.
CATALOG_FILES: dict[str, str] = {
    "families": "catalog/families.json",
    "outcomes": "catalog/outcomes.json",
    "reqs": "catalog/reqs.json",
    "externals": "catalog/externals.json",
}

#: An outcome code: its family letter and a dotted number, `H1.4`.
OUTCOME_CODE_PATTERN = r"^[A-Z][1-9][0-9]*(\.[1-9][0-9]*)*$"

#: A catalog REQ id, its grammar held by the identity seam.
REQ_ID_PATTERN = rf"^{CATALOG_REQ_ID_BODY}$"


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


FILE_MODELS: dict[str, type[BaseModel]] = {
    "families": FamiliesFile,
    "outcomes": OutcomesFile,
    "reqs": ReqsFile,
    "externals": ExternalsFile,
}


class Catalog(BaseModel):
    """The catalog files, parsed."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    families: tuple[Family, ...]
    outcomes: tuple[Outcome, ...]
    reqs: tuple[Req, ...]
    externals: tuple[External, ...] = ()


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
    return Catalog(
        families=families.families,
        outcomes=outcomes.outcomes,
        reqs=reqs.reqs,
        externals=externals.externals,
    )
