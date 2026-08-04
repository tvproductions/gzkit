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

from gzkit.triangle import REQ_ID_BODY_PLAIN

_OBPI_ID_RE = re.compile(r"^OBPI-\d+\.\d+\.\d+-\d{2}(-[a-z0-9-]+)?$")
_ADR_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+-[a-z0-9-]+$")
# Derived from the one grammar (GHI #615); never re-spelled here.
_REQ_ID_RE = re.compile(rf"^{REQ_ID_BODY_PLAIN}$")


# Terminal statuses: a brief in one of these states is a historical record, not an
# active authoring surface. Consumers scope on this to avoid asking a sealed brief
# a question about the present tree — `--brief-command-shape` skips authoring-time
# gating on them (GHI #550), the reconcile engine reports deltas without gating on
# them (GHI #707), and the `--sensitivity` auto-detect floor does not re-gate them
# (GHI #682). Seated here rather than in a validator module because
# it is brief-lifecycle vocabulary, and because importing it from `trust_audits`
# into the engine closed an import cycle.
BRIEF_TERMINAL_STATUSES: frozenset[str] = frozenset(
    {
        "Completed",
        "attested_completed",
        "Validated",
        "Superseded",
        "archived",
        "Promoted",
        # No future work is done on an abandoned or withdrawn brief either, so the
        # sealed-record logic applies identically: its Verification commands will
        # never run and its declared paths describe a tree that has moved on. Added
        # under GHI #707 after the reconcile engine's terminal scoping made the
        # omission visible.
        "Abandoned",
        "Withdrawn",
    }
)

_TERMINAL_STATUSES_FOLDED: frozenset[str] = frozenset(
    status.casefold() for status in BRIEF_TERMINAL_STATUSES
)

# Statuses a brief carries while work is still live. Union with
# BRIEF_TERMINAL_STATUSES is the whole vocabulary; there is no third set.
BRIEF_LIVE_STATUSES: frozenset[str] = frozenset({"Draft", "Active", "in_progress"})

# The single status authority. `BriefStructure.status` was authored as a
# four-value Literal -- {Draft, Active, Validated, Completed} -- which admitted
# two spellings the corpus has never once used and rejected the 198 briefs
# carrying `attested_completed`, plus every `Abandoned`/`Withdrawn`/`in_progress`
# brief. The schema could therefore never have been enforced corpus-wide, which
# is a large part of why it never was (GHI #615). Composing the vocabulary from
# BRIEF_TERMINAL_STATUSES rather than restating it keeps the two from drifting.
BRIEF_STATUSES: frozenset[str] = BRIEF_TERMINAL_STATUSES | BRIEF_LIVE_STATUSES

_BRIEF_STATUSES_FOLDED: frozenset[str] = frozenset(status.casefold() for status in BRIEF_STATUSES)


def is_terminal_brief_status(status: str) -> bool:
    """Return True when ``status`` names a sealed brief lifecycle state.

    The single predicate both consumers call. `--brief-command-shape` previously
    tested frozenset membership by exact string while the reconcile engine
    casefolded, so the corpus's two spellings of ``withdrawn`` resolved
    differently depending on which validator asked. Surrounding whitespace and
    YAML quoting are tolerated because callers pass raw frontmatter values.
    """
    return status.strip().strip('"').strip("'").casefold() in _TERMINAL_STATUSES_FOLDED


# A brief in one of these states has not begun. Its Allowed Paths and its
# `gz` verbs name what the OBPI will CREATE, so their absence is the brief's
# expected state rather than divergence from an agreed one. Distinct from
# BRIEF_TERMINAL_STATUSES because "not yet" and "no longer" are different facts,
# and only some dimensions are scoped by it (see `brief_reconcile`).
BRIEF_UNSTARTED_STATUSES: frozenset[str] = frozenset({"Draft"})

_UNSTARTED_STATUSES_FOLDED: frozenset[str] = frozenset(
    status.casefold() for status in BRIEF_UNSTARTED_STATUSES
)


def is_unstarted_brief_status(status: str) -> bool:
    """Return True when ``status`` names a brief whose work has not begun.

    Whitespace and YAML quoting are tolerated for the same reason
    ``is_terminal_brief_status`` tolerates them: callers pass raw frontmatter.
    """
    return status.strip().strip('"').strip("'").casefold() in _UNSTARTED_STATUSES_FOLDED


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
    status: str = Field(..., description="Brief lifecycle status")
    allowlist: list[str] = Field(..., min_length=1, description="Allowed paths for this OBPI")
    reqs: list[str] = Field(..., min_length=1, description="REQ-ID array")
    verification: list[str] = Field(..., min_length=1, description="Verification commands")
    citations: list[tuple[str, str]] = Field(
        default_factory=list, description="Citation tuples (artifact_path, anchor)"
    )
    tasks: list[str] = Field(
        default_factory=list,
        description=(
            "TASK IDs this artifact advances (ADR-0.0.64 / OBPI-02 channel). "
            "Schema enforcement by OBPI-04."
        ),
    )
    req_atomic: list[str] = Field(
        default_factory=list,
        description=(
            "REQ IDs exempt from subdivision check (ADR-0.0.64 / OBPI-04). "
            "Operator escape valve; requires inline rationale."
        ),
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

    @field_validator("status")
    @classmethod
    def _validate_status(cls, v: str) -> str:
        """Admit any declared status, casefolded.

        Casefold rather than exact match because the corpus carries both
        ``Withdrawn`` and ``withdrawn``, and ``is_terminal_brief_status`` already
        folds -- a schema stricter than the predicate that scopes it would
        reject briefs the runtime treats as sealed.
        """
        if v.strip().strip('"').strip("'").casefold() not in _BRIEF_STATUSES_FOLDED:
            raise ValueError(f"status must be one of {sorted(BRIEF_STATUSES)}: {v!r}")
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
