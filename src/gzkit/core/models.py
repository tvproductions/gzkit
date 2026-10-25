"""Pydantic frontmatter models for governance and control-surface content types.

Extracted from gzkit.models.frontmatter. Each model mirrors a corresponding
JSON schema. Pure domain logic — no I/O operations.
"""

import enum
import re
from typing import Any, Literal, get_args, get_origin

from pydantic import BaseModel, ConfigDict, Field
from pydantic import ValidationError as PydanticValidationError

from gzkit.skill_contract import SKILL_DESCRIPTION_MAX_CHARS

# ---------------------------------------------------------------------------
# Identity grammar — one body per kind (drydock RO-2, the identity seam)
# ---------------------------------------------------------------------------
#
# Nothing outside the seam spells an ADR, OBPI, REQ or TASK grammar
# (`docs/governance/harbor-ro2-identity-seam.md` § The seam, item 1); readers embed
# these bodies, and `gz validate --id-seam` ratchets the copies that remain.
# Widths are settled here, at the two digits the JSON schemas and the REQ grammar
# already pinned (GHI #615). Measured 2026-10-18 before the TASK and identity-surface
# tightening: no live id in the ledger, the briefs, the commit trailers, the
# `@covers` bindings or the scenario tags uses another width.

SEMVER_BODY = r"\d+\.\d+\.\d+"
SLUG_BODY = r"[a-z0-9-]+"
ITEM_BODY = r"\d{2}"

ADR_SHORT_ID_BODY = rf"ADR-{SEMVER_BODY}"
ADR_ID_BODY = rf"{ADR_SHORT_ID_BODY}-{SLUG_BODY}"
ADR_POOL_ID_BODY = rf"ADR-pool\.{SLUG_BODY}"
OBPI_SHORT_ID_BODY = rf"OBPI-{SEMVER_BODY}-{ITEM_BODY}"
OBPI_ID_BODY = rf"{OBPI_SHORT_ID_BODY}-{SLUG_BODY}"
#: The OBPI short form with its semver and item captured, for readers that need the parts.
OBPI_ID_PARTS_BODY = rf"OBPI-(?P<semver>{SEMVER_BODY})-(?P<item>{ITEM_BODY})"
#: An OBPI or ADR reference read loosely on purpose: a malformed item index (``-2``) is
#: still a reference, so the brief cross-reference audit can report it as drift.
ARTIFACT_REF_BODY = (
    rf"(?P<kind>OBPI|ADR)-(?P<ver>{SEMVER_BODY})"
    r"(?:-(?P<seq>\d+)(?:-(?P<slug>[a-z0-9][a-z0-9-]*))?)?"
)
#: The whole item number whatever its width, for the one reader that attested REQ-0.35.0-15-02
#: binds to it: a run's short form ends where the item number does, so item 7 and item 100
#: each have one.
OBPI_ANY_WIDTH_SHORT_ID_BODY = rf"OBPI-{SEMVER_BODY}-\d+"
#: The kind prefixes a link or header may open with, read loosely: a parent link may name
#: any PRD, ADR or OBPI, well-formed or not.
ARTIFACT_PREFIX_BODY = r"(?:PRD|ADR|OBPI)-"
#: The ADR short form with its semver captured.
ADR_ID_PARTS_BODY = rf"ADR-(?P<semver>{SEMVER_BODY})"
#: The ADR short form with its semver split into numeric parts, for ordering readers.
ADR_SEMVER_COMPONENTS_BODY = r"ADR-(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)"
#: The ``ADR-`` and ``ADR-pool.`` openers, for readers that scan a loose token after them
#: (a directory name, an H1, a parent line) and so cannot demand a whole id.
ADR_PREFIX_BODY = r"ADR-"
ADR_POOL_PREFIX_BODY = r"ADR-pool\."
#: The ADR or PRD opener a document header may start with.
ADR_PRD_PREFIX_BODY = r"(?:ADR|PRD)-"
REQ_ID_BODY = (
    rf"REQ-(?P<semver>{SEMVER_BODY})-(?P<obpi_item>{ITEM_BODY})-(?P<criterion>{ITEM_BODY})"
)
#: The REQ grammar with no capture groups, for readers that embed it.
REQ_ID_BODY_PLAIN = rf"REQ-{SEMVER_BODY}-{ITEM_BODY}-{ITEM_BODY}"
#: The item-criterion form (``REQ-NN-MM``) a commit message cites, relative to its ADR.
REQ_SHORT_ID_BODY = rf"REQ-{ITEM_BODY}-{ITEM_BODY}"
#: The catalog REQ form (``REQ-<n>``): sequential, area-free, never reused. It carries
#: no dots, so it never reads as the legacy form (drydock RO-3).
CATALOG_REQ_ID_BODY = r"REQ-[1-9][0-9]*"
TASK_ID_BODY = (
    rf"TASK-(?P<semver>{SEMVER_BODY})-(?P<obpi_item>{ITEM_BODY})"
    rf"-(?P<req_index>{ITEM_BODY})-(?P<seq>{ITEM_BODY})"
)
#: The numeric TASK grammar with no capture groups.
TASK_ID_BODY_PLAIN = rf"TASK-{SEMVER_BODY}-{ITEM_BODY}-{ITEM_BODY}-{ITEM_BODY}"
#: The direct-fix TASK form, a kebab slug with an optional GHI anchor (GHI #552).
TASK_SLUG_ID_BODY = r"TASK-[a-z][a-z0-9-]*(?:-#\d+)?"

#: The frontmatter ``id`` patterns the JSON schemas carry byte for byte.
ADR_FRONTMATTER_ID_PATTERN = rf"^(?:{ADR_POOL_ID_BODY}|{ADR_ID_BODY})$"
OBPI_FRONTMATTER_ID_PATTERN = rf"^{OBPI_SHORT_ID_BODY}(-{SLUG_BODY})?$"


class IdKind(enum.StrEnum):
    """The four identifier kinds the seam governs."""

    ADR = "ADR"
    OBPI = "OBPI"
    REQ = "REQ"
    TASK = "TASK"


def id_kind(identifier: str) -> IdKind:
    """Return the kind an identifier's leading token names.

    Raises ``ValueError`` for an identifier no kind claims.
    """
    head, _, rest = identifier.partition("-")
    if rest:
        for kind in IdKind:
            if head == kind.value:
                return kind
    msg = f"Not an ADR, OBPI, REQ or TASK identifier: {identifier!r}"
    raise ValueError(msg)


def is_foundation_semver(semver: str) -> bool:
    """Return True for the foundation series, ``0.0.x``."""
    major, _, rest = semver.partition(".")
    minor = rest.partition(".")[0]
    return major == "0" and minor == "0"


_ADR_SEMVER_PREFIX = re.compile(rf"^{ADR_ID_PARTS_BODY}")


def adr_semver(identifier: str) -> str | None:
    """Return the semver an ADR identifier opens with, or None when it carries none."""
    match = _ADR_SEMVER_PREFIX.match(identifier)
    return match["semver"] if match else None


def is_foundation_adr(identifier: str) -> bool:
    """Return True when an ADR identifier belongs to the foundation series, ``0.0.x``."""
    semver = adr_semver(identifier)
    return semver is not None and is_foundation_semver(semver)


# ---------------------------------------------------------------------------
# Identity composition and spelling fallback (drydock RO-2 tranche 5)
# ---------------------------------------------------------------------------
#
# Nothing outside the seam composes an id from parts, scans a child prefix,
# normalizes input to an id, or recovers a parent from spelling. A reader that
# holds a ledger calls `gzkit.core.id_resolver.parent_of`; one that holds none
# calls `spelled_parent`, the seam's marked fallback (every use is a spelling-derived
# link, counted until RO-3's `member_of` lands).

_OBPI_PARTS = re.compile(rf"^{OBPI_ID_PARTS_BODY}(?:-(?P<slug>(?i:{SLUG_BODY})))?$")
_REQ_PARTS = re.compile(rf"^{REQ_ID_BODY}$")
_TASK_PARTS = re.compile(rf"^{TASK_ID_BODY}$")
_ADR_SLUG = re.compile(rf"^{ADR_ID_PARTS_BODY}-(?P<slug>{SLUG_BODY})$")
_POOL_SLUG = re.compile(rf"^{ADR_POOL_PREFIX_BODY}(?P<slug>.+)$")


#: The ADR short form as a template, for the embedded hook scripts that compose one.
ADR_ID_TEMPLATE = "ADR-{semver}"


def _width(part: str | int) -> str:
    """Return an id part at the grammar's two-digit width when it is a number."""
    return f"{part:02d}" if isinstance(part, int) else part


def compose_adr_id(semver: str) -> str:
    """Return the ADR short form, ``ADR-<semver>``."""
    return ADR_ID_TEMPLATE.format(semver=semver)


def compose_adr_full_id(semver: str, slug: str) -> str:
    """Return the ADR full form, ``ADR-<semver>-<slug>``."""
    return f"ADR-{semver}-{slug}"


def compose_pool_adr_id(slug: str) -> str:
    """Return the pool ADR form, ``ADR-pool.<slug>``."""
    return f"ADR-pool.{slug}"


def compose_obpi_id(semver: str, item: str | int, slug: str | None = None) -> str:
    """Return the OBPI short form, or the full form when a slug is given."""
    short = f"OBPI-{semver}-{_width(item)}"
    return short if slug is None else f"{short}-{slug}"


def compose_req_id(semver: str, item: str | int, criterion: str | int) -> str:
    """Return ``REQ-<semver>-<item>-<criterion>``."""
    return f"REQ-{semver}-{_width(item)}-{_width(criterion)}"


def compose_task_id(semver: str, item: str | int, req_index: str | int, seq: str | int) -> str:
    """Return ``TASK-<semver>-<item>-<req index>-<seq>``."""
    return f"TASK-{semver}-{_width(item)}-{_width(req_index)}-{_width(seq)}"


def adr_prefix(semver: str) -> str:
    """Return the prefix every full ADR id of *semver* opens with."""
    return f"ADR-{semver}-"


def obpi_prefix(semver: str) -> str:
    """Return the prefix every OBPI id of *semver* opens with."""
    return f"OBPI-{semver}-"


def req_prefix(semver: str, item: str | int | None = None) -> str:
    """Return the prefix the REQs of an ADR (or of one of its OBPIs) open with."""
    return f"REQ-{semver}-" if item is None else f"REQ-{semver}-{_width(item)}-"


def task_prefix(semver: str, item: str | int, req_index: str | int) -> str:
    """Return the prefix the TASKs of one REQ open with."""
    return f"TASK-{semver}-{_width(item)}-{_width(req_index)}-"


def normalize_adr_input(text: str) -> str:
    """Return operator input as an ADR id: a bare ``<semver>[-slug]`` gains ``ADR-``."""
    return text if text.startswith("ADR-") else f"ADR-{text}"


def normalize_obpi_input(text: str) -> str:
    """Return operator input as an OBPI id: a bare ``<semver>-<item>`` gains ``OBPI-``."""
    return text if text.startswith("OBPI-") else f"OBPI-{text}"


def normalize_pool_adr_input(text: str) -> str:
    """Return operator input as a pool ADR id: a bare slug gains ``ADR-pool.``."""
    return text if text.startswith("ADR-pool.") else f"ADR-pool.{text}"


def obpi_adr_id(identifier: str) -> str | None:
    """Return the ADR an OBPI id's spelling names, or None when it is not an OBPI id."""
    match = _OBPI_PARTS.match(identifier)
    return compose_adr_id(match["semver"]) if match else None


def req_obpi_id(identifier: str) -> str | None:
    """Return the OBPI short form a REQ id's spelling names, or None for any other id."""
    match = _REQ_PARTS.match(identifier)
    return compose_obpi_id(match["semver"], match["obpi_item"]) if match else None


def task_req_id(identifier: str) -> str | None:
    """Return the REQ a numeric TASK id's spelling names, or None for any other id."""
    match = _TASK_PARTS.match(identifier)
    if match is None:
        return None
    return compose_req_id(match["semver"], match["obpi_item"], match["req_index"])


def task_obpi_id(identifier: str) -> str | None:
    """Return the OBPI short form a numeric TASK id's spelling names, or None."""
    match = _TASK_PARTS.match(identifier)
    return compose_obpi_id(match["semver"], match["obpi_item"]) if match else None


def spelled_parent(identifier: str) -> str | None:
    """Return the parent an id's spelling names: the seam's one marked fallback.

    ``OBPI-<semver>-…`` → ``ADR-<semver>``; ``REQ-<semver>-<NN>-<MM>`` →
    ``OBPI-<semver>-<NN>``; ``TASK-<semver>-<NN>-<MM>-<PP>`` →
    ``REQ-<semver>-<NN>-<MM>``. ``None`` for an id that carries no parent (an
    ADR, a slug TASK) or is not well formed. A reader with a ledger uses
    ``parent_of``, which reads stored fields first.
    """
    return obpi_adr_id(identifier) or req_obpi_id(identifier) or task_req_id(identifier)


def spelled_chain(identifier: str) -> tuple[str, ...]:
    """Return the spelled parents of an id, nearest first, ending at the ADR."""
    chain: list[str] = []
    parent = spelled_parent(identifier)
    while parent is not None:
        chain.append(parent)
        parent = spelled_parent(parent)
    return tuple(chain)


def obpi_slug(identifier: str) -> str | None:
    """Return the slug of a full OBPI id, or None for the short form."""
    match = _OBPI_PARTS.match(identifier)
    return match["slug"] if match else None


def obpi_item(identifier: str) -> str | None:
    """Return the item number of an OBPI id, or None when it is not one."""
    match = _OBPI_PARTS.match(identifier)
    return match["item"] if match else None


def obpi_short_id(identifier: str) -> str | None:
    """Return the short form of an OBPI id, or None when it is not one."""
    match = _OBPI_PARTS.match(identifier)
    return compose_obpi_id(match["semver"], match["item"]) if match else None


def req_obpi_item(identifier: str) -> str | None:
    """Return the OBPI item number a REQ id names, or None when it is not one."""
    match = _REQ_PARTS.match(identifier)
    return match["obpi_item"] if match else None


def adr_slug(identifier: str) -> str | None:
    """Return the slug of a full ADR id, or None for the short and pool forms."""
    match = _ADR_SLUG.match(identifier)
    return match["slug"] if match else None


def pool_slug(identifier: str) -> str | None:
    """Return the slug of a pool ADR id, or None for any other id."""
    match = _POOL_SLUG.match(identifier)
    return match["slug"] if match else None


# ---------------------------------------------------------------------------
# Frontmatter models
# ---------------------------------------------------------------------------


class AdrFrontmatter(BaseModel):
    """ADR frontmatter — mirrors ``src/gzkit/schemas/adr.json``."""

    model_config = ConfigDict(frozen=True, extra="allow")

    id: str = Field(..., pattern=ADR_FRONTMATTER_ID_PATTERN)
    status: Literal[
        "Pool",
        "Pending",
        "Draft",
        "Proposed",
        "Accepted",
        "Completed",
        "Validated",
        "Superseded",
        "Deprecated",
    ]
    semver: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    lane: Literal["lite", "heavy"]
    kind: Literal["foundation", "feature"]
    parent: str
    date: str = Field(..., pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")
    sensitivity: Literal["security"] | None = None


class ObpiFrontmatter(BaseModel):
    """OBPI frontmatter — mirrors ``src/gzkit/schemas/obpi.json``."""

    model_config = ConfigDict(frozen=True, extra="allow")

    id: str = Field(..., pattern=OBPI_FRONTMATTER_ID_PATTERN)
    parent: str
    item: str | int
    lane: Literal["lite", "heavy", "Lite", "Heavy"]
    status: Literal[
        "Draft",
        "Active",
        "Completed",
        "Abandoned",
        "pending",
        "in_progress",
        "completed",
        "attested_completed",
        "validated",
        "drift",
        "withdrawn",
    ]
    sensitivity: Literal["security"] | None = None


class PrdFrontmatter(BaseModel):
    """PRD frontmatter — mirrors ``src/gzkit/schemas/prd.json``."""

    model_config = ConfigDict(frozen=True, extra="allow")

    id: str = Field(..., pattern=r"^PRD-[A-Z0-9]+-[0-9]+\.[0-9]+\.[0-9]+$")
    status: Literal["Draft", "Review", "Approved", "Superseded"]
    semver: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    date: str = Field(..., pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


class ConstitutionFrontmatter(BaseModel):
    """Constitution frontmatter — mirrors ``src/gzkit/schemas/constitution.json``."""

    model_config = ConfigDict(frozen=True, extra="allow")

    id: str = Field(..., pattern=r"^CONSTITUTION-[A-Z0-9]+-[0-9]+\.[0-9]+\.[0-9]+$")
    status: Literal["Draft", "Review", "Ratified", "Amended", "Superseded"]
    semver: str = Field(..., pattern=r"^[0-9]+\.[0-9]+\.[0-9]+$")
    date: str = Field(..., pattern=r"^[0-9]{4}-[0-9]{2}-[0-9]{2}$")


# ---------------------------------------------------------------------------
# Control-surface frontmatter models
# ---------------------------------------------------------------------------


class SkillFrontmatter(BaseModel):
    """Skill SKILL.md frontmatter — mirrors ``.gzkit/schemas/skill.schema.json``."""

    model_config = ConfigDict(frozen=True, extra="allow", populate_by_name=True)

    description: str = Field(..., max_length=SKILL_DESCRIPTION_MAX_CHARS)
    name: str | None = Field(None, pattern=r"^[a-z0-9-]+$", max_length=64)
    category: (
        Literal[
            "adr-lifecycle",
            "adr-operations",
            "adr-audit",
            "obpi-pipeline",
            "governance-infrastructure",
            "agent-operations",
            "code-quality",
            "cross-repository",
        ]
        | None
    ) = None
    lifecycle_state: Literal["active", "deprecated", "draft", "retired"] | None = None
    owner: str | None = None
    last_reviewed: str | None = Field(None, pattern=r"^\d{4}-\d{2}-\d{2}$")
    user_invocable: bool | None = Field(None, alias="user-invocable")
    disable_model_invocation: bool | None = Field(None, alias="disable-model-invocation")
    argument_hint: str | None = Field(None, alias="argument-hint")
    allowed_tools: str | None = Field(None, alias="allowed-tools")
    skill_model: Literal["haiku", "sonnet", "opus", "fable"] = Field(..., alias="model")
    context: Literal["fork"] | None = None
    agent: str | None = None


class InstructionFrontmatter(BaseModel):
    """Instruction frontmatter — mirrors ``.gzkit/schemas/rule.schema.json``."""

    model_config = ConfigDict(frozen=True, extra="allow", populate_by_name=True)

    apply_to: str = Field(..., alias="applyTo")
    name: str | None = None
    description: str | None = None
    category: str | None = None
    exclude_agent: Literal["code-review", "coding-agent", "all"] | None = Field(
        None, alias="excludeAgent"
    )


# ---------------------------------------------------------------------------
# Identity surface models (ADR-0.0.10, OBPI-0.0.10-02)
# ---------------------------------------------------------------------------


class AdrId(BaseModel):
    """Portable ADR identity surface.

    Pattern: ``ADR-X.Y.Z``  Example: ``ADR-0.0.10``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(..., description="Canonical ADR identifier", pattern=rf"^{ADR_SHORT_ID_BODY}$")

    @classmethod
    def parse(cls, value: str) -> AdrId:
        """Parse and validate an ADR identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class ObpiId(BaseModel):
    """Portable OBPI identity surface.

    Pattern: ``OBPI-X.Y.Z-NN``  Example: ``OBPI-0.0.10-01``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(
        ..., description="Canonical OBPI identifier", pattern=rf"^{OBPI_SHORT_ID_BODY}$"
    )

    @classmethod
    def parse(cls, value: str) -> ObpiId:
        """Parse and validate an OBPI identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class ReqId(BaseModel):
    """Portable REQ identity surface.

    Pattern: ``REQ-X.Y.Z-NN-MM``  Example: ``REQ-0.0.10-01-01``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(..., description="Canonical REQ identifier", pattern=rf"^{REQ_ID_BODY_PLAIN}$")

    @classmethod
    def parse(cls, value: str) -> ReqId:
        """Parse and validate a REQ identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class TaskId(BaseModel):
    """Portable TASK identity surface.

    Pattern: ``TASK-X.Y.Z-NN-MM-SS``  Example: ``TASK-0.20.0-01-01-01``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(
        ..., description="Canonical TASK identifier", pattern=rf"^{TASK_ID_BODY_PLAIN}$"
    )

    @classmethod
    def parse(cls, value: str) -> TaskId:
        """Parse and validate a TASK identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


class EvidenceId(BaseModel):
    """Portable Evidence identity surface.

    Pattern: ``EV-X.Y.Z-NN-SSS``  Example: ``EV-0.0.10-01-001``
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    raw: str = Field(
        ..., description="Canonical Evidence identifier", pattern=r"^EV-\d+\.\d+\.\d+-\d+-\d+$"
    )

    @classmethod
    def parse(cls, value: str) -> EvidenceId:
        """Parse and validate an Evidence identifier string."""
        return cls(raw=value.strip())

    def __str__(self) -> str:
        """Return the raw identifier string."""
        return self.raw


IDENTITY_MODELS: dict[str, type[AdrId | ObpiId | ReqId | TaskId | EvidenceId]] = {
    "ADR": AdrId,
    "OBPI": ObpiId,
    "REQ": ReqId,
    "TASK": TaskId,
    "EV": EvidenceId,
}


# ---------------------------------------------------------------------------
# Schema-ID → model mapping
# ---------------------------------------------------------------------------

SCHEMA_TO_MODEL: dict[str, type[BaseModel]] = {
    "gzkit.adr.v1": AdrFrontmatter,
    "gzkit.obpi.v1": ObpiFrontmatter,
    "gzkit.prd.v1": PrdFrontmatter,
    "gzkit.constitution.v1": ConstitutionFrontmatter,
}


# ---------------------------------------------------------------------------
# Error translation — Pydantic → gzkit ValidationError list
# ---------------------------------------------------------------------------


def _literal_values(model_cls: type[BaseModel], field_name: str) -> list[str] | None:
    """Extract allowed Literal values for a model field."""
    field_info = model_cls.model_fields.get(field_name)
    if field_info is None:
        return None
    annotation = field_info.annotation
    # Unwrap unions (str | int doesn't have Literal)
    if get_origin(annotation) is Literal:
        return list(get_args(annotation))
    return None


def _translate_pydantic_errors(
    exc: PydanticValidationError,
    frontmatter: dict[str, Any],
    artifact_path: str,
    model_cls: type[BaseModel],
) -> list[dict[str, Any]]:
    """Convert Pydantic v2 errors to dicts matching gzkit error format.

    Returns a list of dicts with keys: type, artifact, message, field.
    """
    results: list[dict[str, Any]] = []
    for err in exc.errors():
        field = str(err["loc"][0]) if err["loc"] else None
        err_type = err["type"]

        if err_type == "missing":
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Missing required frontmatter field: {field}",
                    "field": field,
                }
            )
        elif err_type == "string_pattern_mismatch":
            pattern = err.get("ctx", {}).get("pattern", "")
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Field '{field}' does not match pattern {pattern}",
                    "field": field,
                }
            )
        elif err_type == "literal_error":
            allowed = _literal_values(model_cls, field) if field else None
            value = frontmatter.get(field, "") if field else ""
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Field '{field}' must be one of {allowed}, got '{value}'",
                    "field": field,
                }
            )
        else:
            # Catch-all for unexpected Pydantic error types
            results.append(
                {
                    "type": "frontmatter",
                    "artifact": artifact_path,
                    "message": f"Field '{field}': {err['msg']}",
                    "field": field,
                }
            )

    return results


def validate_frontmatter_model(
    frontmatter: dict[str, Any],
    schema: dict[str, Any],
    artifact_path: str,
) -> list[dict[str, Any]] | None:
    """Validate frontmatter using Pydantic model instantiation.

    Returns a list of error dicts if a model exists for the schema,
    or ``None`` if no model is registered (caller should fall back).

    Each dict has keys: type, artifact, message, field — matching the
    constructor kwargs of ``gzkit.validate.ValidationError``.
    """
    schema_id = schema.get("$id", "")
    model_cls = SCHEMA_TO_MODEL.get(schema_id)
    if model_cls is None:
        return None

    try:
        model_cls(**frontmatter)
    except PydanticValidationError as exc:
        return _translate_pydantic_errors(exc, frontmatter, artifact_path, model_cls)

    return []


def compose_probe_id(kind: IdKind, label: str) -> str:
    """Return an id of *kind* that deliberately names no artifact (a negative control)."""
    return f"{kind.value}-{label}"


def req_stem(semver: str, item: str | int) -> str:
    """Return ``REQ-<semver>-<item>``, the stem a criterion index extends."""
    return f"REQ-{semver}-{_width(item)}"


def obpi_parts(identifier: str) -> tuple[str, str] | None:
    """Return the ``(semver, item)`` of an OBPI id, or None when it is not one."""
    match = _OBPI_PARTS.match(identifier)
    return (match["semver"], match["item"]) if match else None


def obpi_display_name(identifier: str) -> str:
    """Return an OBPI's slug, else its item number, else the id as given."""
    return obpi_slug(identifier) or obpi_item(identifier) or identifier


def obpi_item_reference_pattern(item: int) -> str:
    """Return a regex for the item-only reference ``OBPI-NN`` or ``OBPI-N``.

    An invariant list may name an OBPI by item alone (``(OBPI-04)``), a form
    outside the id grammar.
    """
    return rf"OBPI-0*{item}\b"


def adr_remainder(identifier: str) -> str:
    """Return the text after the ``ADR-`` kind token, or the text unchanged."""
    return identifier.removeprefix("ADR-")


def adr_version_term(identifier: str) -> str:
    """Return the first hyphen-delimited token after ``ADR-``: the semver of a feature ADR."""
    return adr_remainder(identifier).split("-", 1)[0]
