"""Nested evidence models for typed ledger events.

These Pydantic models replace manual validation dispatch in validate.py and
are referenced by the typed event models in :mod:`gzkit.events`. The
dependency is one-directional: evidence models never import from
``gzkit.events``.
"""

import re
from typing import Annotated, Any

from pydantic import (
    AfterValidator,
    BaseModel,
    ConfigDict,
    Field,
    field_validator,
)

from gzkit.ledger import (
    OBPI_ATTESTATION_REQUIREMENTS,
    REQ_PROOF_INPUT_KINDS,
    REQ_PROOF_INPUT_STATUSES,
)


def _check_non_empty_str(v: str) -> str:
    """Validate that a string is non-empty after stripping whitespace."""
    if not v.strip():
        msg = "must be a non-empty string"
        raise ValueError(msg)
    return v


NonEmptyStr = Annotated[str, AfterValidator(_check_non_empty_str)]


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
            msg = f"{info.field_name} must be a non-empty string"
            raise ValueError(msg)
        return v

    @field_validator("kind")
    @classmethod
    def _valid_kind(cls, v: str) -> str:
        if not v.strip():
            msg = "kind must be a non-empty string"
            raise ValueError(msg)
        if v not in REQ_PROOF_INPUT_KINDS:
            msg = "kind must be a supported proof-input kind"
            raise ValueError(msg)
        return v

    @field_validator("status")
    @classmethod
    def _valid_status(cls, v: str) -> str:
        if not v.strip():
            msg = "status must be a non-empty string"
            raise ValueError(msg)
        if v not in REQ_PROOF_INPUT_STATUSES:
            msg = "status must be present or missing"
            raise ValueError(msg)
        return v

    @field_validator("scope", "gap_reason")
    @classmethod
    def _optional_non_empty(cls, v: str | None, info: Any) -> str | None:
        if v is not None and (not isinstance(v, str) or not v.strip()):
            msg = f"{info.field_name} must be a non-empty string when present"
            raise ValueError(msg)
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
            msg = f"{info.field_name} must be a non-empty string when present"
            raise ValueError(msg)
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
            msg = "req_proof_inputs must be a non-empty array when present"
            raise ValueError(msg)
        return v

    @field_validator("attestation_requirement")
    @classmethod
    def _valid_attestation_req(cls, v: str | None) -> str | None:
        if v is not None and v not in OBPI_ATTESTATION_REQUIREMENTS:
            msg = "attestation_requirement must be required or optional"
            raise ValueError(msg)
        return v

    @field_validator("parent_lane")
    @classmethod
    def _valid_lane(cls, v: str | None) -> str | None:
        if v is not None and v not in {"lite", "heavy"}:
            msg = "parent_lane must be lite or heavy"
            raise ValueError(msg)
        return v

    @field_validator("attestation_date")
    @classmethod
    def _valid_date_format(cls, v: str | None) -> str | None:
        if v is not None and (not isinstance(v, str) or not re.match(r"^\d{4}-\d{2}-\d{2}$", v)):
            msg = "attestation_date must use YYYY-MM-DD when present"
            raise ValueError(msg)
        return v

    @field_validator("recorder_source")
    @classmethod
    def _non_empty_recorder(cls, v: str | None) -> str | None:
        if v is not None and (not isinstance(v, str) or not v.strip()):
            msg = "recorder_source must be a non-empty string when present"
            raise ValueError(msg)
        return v

    @field_validator("recorder_warnings")
    @classmethod
    def _valid_recorder_warnings(cls, v: list[str] | None) -> list[str] | None:
        if v is not None:
            if not isinstance(v, list):
                msg = "recorder_warnings must be an array of non-empty strings"
                raise ValueError(msg)
            for i, item in enumerate(v):
                if not isinstance(item, str) or not item.strip():
                    msg = f"recorder_warnings[{i}] must be a non-empty string"
                    raise ValueError(msg)
        return v


class EventAnchor(BaseModel):
    """Temporal anchor for receipt events — typed commit/tag/semver triple.

    Replaces the prior ``dict[str, str] | None`` shape so typos in keys,
    invalid SHAs, and malformed semvers are caught at the model layer
    rather than at ledger-replay time. Parses existing ledger entries
    forward because the shape is unchanged.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    commit: str = Field(..., pattern=r"^[0-9a-f]{7,40}$")
    tag: str | None = None
    semver: str = Field(..., pattern=r"^\d+\.\d+\.\d+$")


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
