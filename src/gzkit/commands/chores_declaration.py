"""Chore class declaration — the registry fields that make a chore checkable (GHI #999).

A chore's nature used to live only as prose in its ``CHORE.md``, so declared
posture and actual workflow drifted apart with nothing to catch it. These
models are the declaration the runner and validators read instead.

Design authority: ``docs/governance/chore-class-system.md`` § The declaration,
and the fence. Operator rulings at the schema step (2026-09-13): ``rung``
carries the writing license and ``idempotent`` the scheduling license;
authorization does not expire; an undeclared chore was announced until the
per-chore declarations landed, and is now refused.
"""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, ValidationError, model_validator

ChoreClass = Literal["conformance", "coherence", "curation", "mining", "currency"]
ChoreRung = Literal["observe", "propose", "repair", "operator-only-repair"]
StalenessSignal = Literal["accumulated-work", "content-delta", "elapsed-time"]
# CSAF 2.0 remediation categories: "no repair" is a declared value, never an absence.
RemediationCategory = Literal["vendor_fix", "workaround", "no_fix_planned", "none_available"]

# Registry keys that belong to the declaration. Presence of any one means the
# chore is attempting a declaration, so the whole declaration must validate.
DECLARATION_KEYS = frozenset(
    {"class", "rung", "idempotent", "staleness", "remediation", "nonAuthority", "governingRule"}
)


class ChoreStaleness(BaseModel):
    """How a chore's staleness is observed and when it is due."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    signal: StalenessSignal = Field(..., description="What makes this chore stale")
    period_days: int | None = Field(
        None, alias="periodDays", gt=0, description="Expected days between runs"
    )
    grace_days: int = Field(
        ..., alias="graceDays", ge=0, description="Days past due before overdue"
    )
    paused: bool = Field(False, description="Intentional dormancy, distinct from neglect")

    @model_validator(mode="after")
    def _elapsed_time_needs_a_period(self) -> ChoreStaleness:
        if self.signal == "elapsed-time" and self.period_days is None:
            msg = "periodDays is required when signal is elapsed-time"
            raise ValueError(msg)
        return self


class ChoreRemediation(BaseModel):
    """What repair means for this chore; a bare category cannot be declared."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    category: RemediationCategory = Field(..., description="CSAF remediation category")
    details: str = Field(..., min_length=1, description="Why this category applies")


class ChoreDeclaration(BaseModel):
    """The class declaration a registered chore carries."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    chore_class: ChoreClass = Field(..., alias="class", description="Why the chore exists")
    rung: ChoreRung = Field(..., description="Where the chore stops; its writing license")
    idempotent: bool = Field(..., description="Safe to re-run on a cadence; scheduling license")
    staleness: ChoreStaleness = Field(..., description="Staleness signal and cadence")
    remediation: ChoreRemediation = Field(..., description="What repair means here")
    non_authority: str = Field(
        ..., alias="nonAuthority", min_length=1, description="What it refuses to touch, and why"
    )
    governing_rule: str = Field(
        ...,
        alias="governingRule",
        pattern=r"^(none|\.gzkit/rules/[A-Za-z0-9_.-]+\.md( § .+)?)$",
        description="The .gzkit/rules clause served, or an explicit none",
    )


def parse_chore_declaration(
    data: dict[str, object], slug: str, blockers: list[str]
) -> ChoreDeclaration | None:
    """Return the chore's declaration, or None when it declares nothing.

    A partial or malformed declaration appends blockers and returns None;
    callers distinguish the two by whether blockers grew.
    """
    raw = {key: value for key, value in data.items() if key in DECLARATION_KEYS}
    if not raw:
        return None
    try:
        return ChoreDeclaration.model_validate(raw)
    except ValidationError as exc:
        for error in exc.errors():
            location = ".".join(str(part) for part in error["loc"]) or "declaration"
            blockers.append(f"chores[{slug}].{location}: {error['msg']} (GHI #999)")
        return None
