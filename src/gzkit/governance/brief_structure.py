"""OBPI brief structural schema — BriefStructure Pydantic model and parser.

Introduces the machine-readable schema for OBPI briefs (OBPI-0.0.37-04).
Ships in permissive mode: briefs lacking structured frontmatter fields load
as LegacyBriefShape with a DeprecationWarning rather than raising.
"""

from __future__ import annotations

import re
import warnings
from pathlib import Path
from typing import Literal

import yaml
from pydantic import BaseModel, ConfigDict, Field, field_validator

_OBPI_ID_RE = re.compile(r"^OBPI-\d+\.\d+\.\d+-\d{2}(-[a-z0-9-]+)?$")
_ADR_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+-[a-z0-9-]+$")
_REQ_ID_RE = re.compile(r"^REQ-\d+\.\d+\.\d+-\d{2}-\d{2}$")


class LegacyBriefShape(BaseModel):
    """Container for an OBPI brief that lacks structured frontmatter fields."""

    model_config = ConfigDict(extra="forbid")

    path: Path
    raw_frontmatter: dict[str, object]
    raw_body: str


class BriefStructure(BaseModel):
    """Machine-readable OBPI brief schema (OBPI-0.0.37-04)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    id: str = Field(..., description="OBPI identifier")
    parent: str = Field(..., description="Parent ADR identifier")
    lane: Literal["Lite", "Heavy"] = Field(..., description="Execution lane")
    status: Literal["Draft", "Validated", "Completed"] = Field(
        ..., description="Brief lifecycle status"
    )
    allowlist: list[str] = Field(..., min_length=1, description="Allowed paths for this OBPI")
    reqs: list[str] = Field(..., min_length=1, description="REQ-ID array")
    verification: list[str] = Field(..., min_length=1, description="Verification commands")
    citations: list[tuple[str, str]] = Field(
        default_factory=list, description="Citation tuples (artifact_path, anchor)"
    )

    @field_validator("id")
    @classmethod
    def _validate_id(cls, v: str) -> str:
        if not _OBPI_ID_RE.match(v):
            raise ValueError(f"id must match OBPI-X.Y.Z-NN[-slug] pattern: {v!r}")
        return v

    @field_validator("parent")
    @classmethod
    def _validate_parent(cls, v: str) -> str:
        if not _ADR_ID_RE.match(v):
            raise ValueError(f"parent must match ADR-X.Y.Z-slug pattern: {v!r}")
        return v

    @field_validator("reqs", mode="before")
    @classmethod
    def _validate_reqs(cls, v: list) -> list:
        for req in v:
            if not _REQ_ID_RE.match(str(req)):
                raise ValueError(f"req must match REQ-X.Y.Z-NN-MM pattern: {req!r}")
        return v


def _extract_frontmatter(text: str) -> tuple[dict, str]:
    """Extract YAML frontmatter and body from markdown text."""
    if not text.startswith("---\n"):
        return {}, text
    end = text.find("\n---\n", 4)
    if end == -1:
        return {}, text
    fm = yaml.safe_load(text[4:end]) or {}
    body = text[end + 5 :]
    return fm, body


def parse_brief(path: Path, *, strict: bool = False) -> BriefStructure | LegacyBriefShape:
    """Parse an OBPI brief file into BriefStructure or LegacyBriefShape.

    In permissive mode (default), briefs lacking structured frontmatter fields
    (allowlist, reqs, verification) return as LegacyBriefShape with a
    DeprecationWarning. In strict mode, missing fields raise ValueError.
    """
    text = path.read_text(encoding="utf-8")
    fm, body = _extract_frontmatter(text)

    required = {"allowlist", "reqs", "verification"}
    if not required.issubset(fm.keys()):
        if strict:
            missing = sorted(required - fm.keys())
            raise ValueError(
                f"Brief {path.name!r} missing structured frontmatter fields: "
                f"{missing}. Set strict=False to load as LegacyBriefShape."
            )
        warnings.warn(
            f"Brief {path.name!r} lacks structured frontmatter fields "
            f"(allowlist, reqs, verification); loading as LegacyBriefShape. "
            "Migrate to structured frontmatter per OBPI-0.0.37-04.",
            DeprecationWarning,
            stacklevel=2,
        )
        return LegacyBriefShape(path=path, raw_frontmatter=fm, raw_body=body)

    bs_fields = BriefStructure.model_fields.keys()
    return BriefStructure(**{k: v for k, v in fm.items() if k in bs_fields})
