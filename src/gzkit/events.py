"""Typed ledger event models with Pydantic discriminated unions.

Nested evidence models replace manual validation dispatch in validate.py.
Typed event models provide discriminated-union parsing for ledger entries.
"""

import re
from datetime import UTC, datetime
from typing import Annotated, Any, ClassVar, Literal

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    TypeAdapter,
    field_validator,
    model_serializer,
    model_validator,
)

from gzkit.ledger import (
    LEDGER_SCHEMA,
    OBPI_ATTESTATION_REQUIREMENTS,
    REQ_PROOF_INPUT_KINDS,
    REQ_PROOF_INPUT_STATUSES,
)


def _check_non_empty_str(v: str) -> str:
    """Validate that a string is non-empty after stripping whitespace."""
    if not v.strip():
        raise ValueError("must be a non-empty string")
    return v


NonEmptyStr = Annotated[str, AfterValidator(_check_non_empty_str)]

# ---------------------------------------------------------------------------
# Nested evidence models (replace manual validation in validate.py)
# ---------------------------------------------------------------------------


class ReqProofInput(BaseModel):
    """Structured REQ-proof input row."""

    model_config = ConfigDict(strict=True, extra="forbid")

    name: str
    kind: str
    source: str
    status: str
    scope: str | None = None
    gap_reason: str | None = None

    @field_validator("name", "source")
    @classmethod
    def _non_empty(cls, v: str, info: Any) -> str:
        if not v.strip():
            raise ValueError(f"{info.field_name} must be a non-empty string")
        return v

    @field_validator("kind")
    @classmethod
    def _valid_kind(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("kind must be a non-empty string")
        if v not in REQ_PROOF_INPUT_KINDS:
            raise ValueError("kind must be a supported proof-input kind")
        return v

    @field_validator("status")
    @classmethod
    def _valid_status(cls, v: str) -> str:
        if not v.strip():
            raise ValueError("status must be a non-empty string")
        if v not in REQ_PROOF_INPUT_STATUSES:
            raise ValueError("status must be present or missing")
        return v

    @field_validator("scope", "gap_reason")
    @classmethod
    def _optional_non_empty(cls, v: str | None, info: Any) -> str | None:
        if v is not None and (not isinstance(v, str) or not v.strip()):
            raise ValueError(f"{info.field_name} must be a non-empty string when present")
        return v


class ScopeAudit(BaseModel):
    """Scope audit evidence for OBPI receipts."""

    model_config = ConfigDict(strict=True, extra="forbid")

    allowlist: list[NonEmptyStr]
    changed_files: list[NonEmptyStr]
    out_of_scope_files: list[NonEmptyStr]


class GitSyncState(BaseModel):
    """Git sync state evidence for OBPI receipts."""

    model_config = ConfigDict(strict=True, extra="forbid")

    branch: str | None = None
    remote: str | None = None
    head: str | None = None
    remote_head: str | None = None
    dirty: bool
    ahead: int = Field(ge=0)
    behind: int = Field(ge=0)
    diverged: bool
    actions: list[NonEmptyStr]
    warnings: list[NonEmptyStr]
    blockers: list[NonEmptyStr]

    @field_validator("branch", "remote", "head", "remote_head")
    @classmethod
    def _optional_non_empty(cls, v: str | None, info: Any) -> str | None:
        if v is not None and (not isinstance(v, str) or not v.strip()):
            raise ValueError(f"{info.field_name} must be a non-empty string when present")
        return v


class ObpiReceiptEvidence(BaseModel):
    """Evidence payload for obpi_receipt_emitted events.

    Replaces manual _validate_obpi_receipt_evidence() dispatch in validate.py.
    Uses extra='allow' because evidence payloads may contain additional
    unstructured fields (e.g. 'acceptance', 'human_attestation', 'value_narrative').
    """

    model_config = ConfigDict(strict=True, extra="allow")

    req_proof_inputs: list[ReqProofInput] | None = None
    attestation_requirement: str | None = None
    parent_lane: str | None = None
    attestation_date: str | None = None
    scope_audit: ScopeAudit | None = None
    git_sync_state: GitSyncState | None = None
    recorder_source: str | None = None
    recorder_warnings: list[str] | None = None

    @field_validator("req_proof_inputs")
    @classmethod
    def _non_empty_when_present(
        cls,
        v: list[ReqProofInput] | None,
    ) -> list[ReqProofInput] | None:
        if v is not None and not v:
            raise ValueError("req_proof_inputs must be a non-empty array when present")
        return v

    @field_validator("attestation_requirement")
    @classmethod
    def _valid_attestation_req(cls, v: str | None) -> str | None:
        if v is not None and v not in OBPI_ATTESTATION_REQUIREMENTS:
            raise ValueError("attestation_requirement must be required or optional")
        return v

    @field_validator("parent_lane")
    @classmethod
    def _valid_lane(cls, v: str | None) -> str | None:
        if v is not None and v not in {"lite", "heavy"}:
            raise ValueError("parent_lane must be lite or heavy")
        return v

    @field_validator("attestation_date")
    @classmethod
    def _valid_date_format(cls, v: str | None) -> str | None:
        if v is not None and (not isinstance(v, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", v)):
            raise ValueError("attestation_date must use YYYY-MM-DD when present")
        return v

    @field_validator("recorder_source")
    @classmethod
    def _non_empty_recorder(cls, v: str | None) -> str | None:
        if v is not None and (not isinstance(v, str) or not v.strip()):
            raise ValueError("recorder_source must be a non-empty string when present")
        return v

    @field_validator("recorder_warnings")
    @classmethod
    def _valid_recorder_warnings(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            if not isinstance(v, list):
                raise ValueError("recorder_warnings must be an array of non-empty strings")
            for i, item in enumerate(v):
                if not isinstance(item, str) or not item.strip():
                    raise ValueError(f"recorder_warnings[{i}] must be a non-empty string")
        return v


# ---------------------------------------------------------------------------
# Pydantic error → field path conversion
# ---------------------------------------------------------------------------


def pydantic_loc_to_field_path(prefix: str, loc: tuple[str | int, ...]) -> str:
    """Convert a Pydantic error location tuple to a dotted field path.

    Example: ("req_proof_inputs", 0, "kind") → "evidence.req_proof_inputs[0].kind"
    """
    parts: list[str] = [prefix]
    for segment in loc:
        if isinstance(segment, int):
            parts[-1] = f"{parts[-1]}[{segment}]"
        else:
            parts.append(str(segment))
    return ".".join(parts)


# ---------------------------------------------------------------------------
# Typed event models (discriminated union over event type)
# ---------------------------------------------------------------------------


class _EventBase(BaseModel):
    """Common fields shared by all ledger event types."""

    model_config = ConfigDict(extra="forbid")

    id: str
    ts: str = Field(default_factory=lambda: datetime.now(UTC).isoformat())
    schema_: str = Field(default=LEDGER_SCHEMA)
    parent: str | None = None

    _BASE_FIELDS: ClassVar[frozenset[str]] = frozenset(
        {"schema_", "event", "id", "ts", "parent"},
    )

    @model_validator(mode="before")
    @classmethod
    def _map_schema_key(cls, data: Any) -> Any:
        """Map 'schema' → 'schema_' for Pydantic field name."""
        if isinstance(data, dict) and "schema" in data and "schema_" not in data:
            data = dict(data)
            data["schema_"] = data.pop("schema")
        return data

    @model_serializer
    def _serialize(self) -> dict[str, Any]:
        """Serialize with schema_→schema mapping and typed fields flattened."""
        result: dict[str, Any] = {
            "schema": self.schema_,
            "event": self.event,  # type: ignore[attr-defined]
            "id": self.id,
            "ts": self.ts,
        }
        if self.parent:
            result["parent"] = self.parent
        # Flatten event-specific fields
        for name in type(self).model_fields:
            if name not in self._BASE_FIELDS:
                value = getattr(self, name)
                if value is not None:
                    result[name] = value
        return result

    @property
    def extra(self) -> dict[str, Any]:
        """Backward-compatible extra dict for code that accesses event.extra."""
        result: dict[str, Any] = {}
        for name in type(self).model_fields:
            if name not in self._BASE_FIELDS:
                value = getattr(self, name)
                if value is not None:
                    result[name] = value
        return result


class ProjectInitEvent(_EventBase):
    """project_init event."""

    event: Literal["project_init"]
    mode: str


class PrdCreatedEvent(_EventBase):
    """prd_created event."""

    event: Literal["prd_created"]


class ConstitutionCreatedEvent(_EventBase):
    """constitution_created event."""

    event: Literal["constitution_created"]


class ObpiCreatedEvent(_EventBase):
    """obpi_created event."""

    event: Literal["obpi_created"]


class AdrCreatedEvent(_EventBase):
    """adr_created event."""

    event: Literal["adr_created"]
    lane: str


class ArtifactEditedEvent(_EventBase):
    """artifact_edited event."""

    event: Literal["artifact_edited"]
    path: str
    session: str | None = None


class AttestedEvent(_EventBase):
    """attested event."""

    event: Literal["attested"]
    status: str
    by: str
    reason: str | None = None


class GateCheckedEvent(_EventBase):
    """gate_checked event."""

    event: Literal["gate_checked"]
    gate: int
    status: str
    command: str
    returncode: int
    evidence: str | None = None


class CloseoutInitiatedEvent(_EventBase):
    """closeout_initiated event."""

    event: Literal["closeout_initiated"]
    by: str
    mode: str
    evidence: dict[str, Any] | None = None


class AuditReceiptEmittedEvent(_EventBase):
    """audit_receipt_emitted event."""

    event: Literal["audit_receipt_emitted"]
    receipt_event: str
    attestor: str
    evidence: dict[str, Any] | None = None
    anchor: dict[str, str] | None = None


class ObpiReceiptEmittedEvent(_EventBase):
    """obpi_receipt_emitted event."""

    event: Literal["obpi_receipt_emitted"]
    receipt_event: str
    attestor: str
    evidence: dict[str, Any] | None = None
    obpi_completion: str | None = None
    anchor: dict[str, str] | None = None


class ArtifactRenamedEvent(_EventBase):
    """artifact_renamed event."""

    event: Literal["artifact_renamed"]
    new_id: str
    reason: str | None = None


TypedLedgerEvent = Annotated[
    ProjectInitEvent
    | PrdCreatedEvent
    | ConstitutionCreatedEvent
    | ObpiCreatedEvent
    | AdrCreatedEvent
    | ArtifactEditedEvent
    | AttestedEvent
    | GateCheckedEvent
    | CloseoutInitiatedEvent
    | AuditReceiptEmittedEvent
    | ObpiReceiptEmittedEvent
    | ArtifactRenamedEvent,
    Field(discriminator="event"),
]

_typed_event_adapter: TypeAdapter[TypedLedgerEvent] = TypeAdapter(TypedLedgerEvent)


def parse_typed_event(data: dict[str, Any]) -> TypedLedgerEvent:
    """Parse a raw dict into a typed event model via discriminated union."""
    return _typed_event_adapter.validate_python(data)
