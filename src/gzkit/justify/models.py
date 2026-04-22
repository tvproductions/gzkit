"""Pydantic data models for gzkit.justify.

All models are frozen and forbid extra fields per the gzkit model policy
(`.gzkit/rules/models.md`). Collection fields use tuples so freezing is
mechanically enforceable at the field level.

``LedgerEvent`` here is a local re-declaration matching only the fields
justify consumes. The authoritative ledger model lives in
``src/gzkit/ledger.py``; duplicating the consumption shape keeps this
library decoupled from ledger schema churn.
"""

from __future__ import annotations

from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator

AnchorKind = Literal["ghi", "obpi", "draft"]


class AnchorResolutionError(Exception):
    """Raised when an anchor cannot be resolved to a concrete artifact."""


class AnchorRef(BaseModel):
    """A resolved anchor — the identity of the thing being justified."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    kind: AnchorKind = Field(..., description="One of 'ghi', 'obpi', 'draft'.")
    identifier: str | None = Field(
        None, description="GHI-<N> or OBPI-<X.Y.Z>-<NN>; None for draft."
    )
    title: str | None = Field(None, description="Human-readable title when available.")
    body: str | None = Field(
        None, description="Anchor body text (GHI body, brief objective, draft text)."
    )
    labels: tuple[str, ...] = Field(
        default_factory=tuple, description="GHI labels when applicable."
    )
    author: str | None = Field(None, description="GHI author login when applicable.")
    draft_text: str | None = Field(None, description="Literal draft text for 'draft' kind.")
    draft_slug: str | None = Field(None, description="Kebab-case slug for 'draft' kind.")
    source_path: str | None = Field(None, description="Filesystem path for OBPI brief resolution.")

    @field_validator("kind", mode="before")
    @classmethod
    def _validate_kind(cls, value: Any) -> Any:
        if value == "adr":
            raise ValueError(
                "anchor kind 'adr' is not supported; use one of 'ghi', 'obpi', 'draft'"
            )
        return value


class RuleCitation(BaseModel):
    """A governance rule file matched against an anchor's surface."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    rule_id: str = Field(..., description="Rule identifier from frontmatter 'id' field.")
    path: str = Field(..., description="Filesystem path to the rule file.")
    description: str | None = Field(None, description="Rule description from frontmatter.")
    paths_globs: tuple[str, ...] = Field(
        default_factory=tuple, description="Frontmatter 'paths' globs that matched."
    )


class CommitRef(BaseModel):
    """A git commit reference (short SHA + subject)."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    sha: str = Field(..., description="Short commit hash (oneline form).")
    subject: str = Field(..., description="Commit subject line.")


class LedgerEvent(BaseModel):
    """Local shape for ledger events consumed by justify.

    This is intentionally narrower than `gzkit.ledger.LedgerEvent` — justify
    only reads a few stable fields and does not own the ledger schema.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    event: str = Field(..., description="Event name.")
    id: str = Field(..., description="Artifact identifier (OBPI slug, ADR, etc.).")
    ts: str = Field(..., description="ISO-8601 timestamp string.")
    parent: str | None = Field(None, description="Parent artifact identifier when present.")
    extra: dict[str, Any] = Field(default_factory=dict, description="Opaque event payload.")


class EvidenceBundle(BaseModel):
    """Five-source grounding evidence for an anchor."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    anchor: AnchorRef = Field(..., description="The resolved anchor this bundle grounds.")
    matching_rules: tuple[RuleCitation, ...] = Field(
        default_factory=tuple, description="Governance rules matched to the anchor surface."
    )
    ledger_events: tuple[LedgerEvent, ...] = Field(
        default_factory=tuple, description="Ledger events referencing the anchor (OBPI only)."
    )
    recent_commits: tuple[CommitRef, ...] = Field(
        default_factory=tuple, description="Recent commits matching the anchor scope."
    )
    related_anchors: tuple[AnchorRef, ...] = Field(
        default_factory=tuple, description="Resolved related anchors (GHI cross-links)."
    )
    taxonomy_reference: str = Field(
        ..., description="Path string pointing at the model-regression taxonomy doc."
    )
    warnings: tuple[str, ...] = Field(
        default_factory=tuple,
        description="Non-fatal notes about missing or degraded sources.",
    )
