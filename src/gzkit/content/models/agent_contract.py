"""AgentContract content model — target AGENTS.md / CLAUDE.md surfaces."""

from typing import Literal

from pydantic import Field

from .base import BaseContentModel
from .bullet import Bullet

_Temperature = Literal["lite", "medium", "heavy"]


class Pillar(BaseContentModel):
    """A section of the agent contract with density-aware rendering metadata."""

    id: str = Field(..., description="Unique section identifier (kebab-case).")
    title: str = Field(..., description="Display title for this section.")
    order: int = Field(..., description="Render order (ascending).")
    enabled: bool = Field(
        True, description="When False, section is withheld regardless of temperature."
    )
    tier: _Temperature = Field(
        "lite", description="Lowest temperature at which this section renders."
    )
    bullets: list[Bullet] = Field(default_factory=list, description="Bullets in this section.")
    lines: list[str] = Field(
        default_factory=list,
        description=(
            "Verbatim section-body lines for full-fidelity capture and structural "
            "round-trip (ADR-0.0.37-13). When populated, the renderer emits these "
            "verbatim; otherwise it falls back to rendering `bullets`."
        ),
    )


class AgentContract(BaseContentModel):
    """Per-turn surface content for AGENTS.md / CLAUDE.md."""

    name: str
    purpose: str
    tech_stack: list[str] = Field(default_factory=list)
    rules: list[Bullet] = Field(default_factory=list)
    pillars: list[Pillar] = Field(
        default_factory=list,
        description="Density-aware sections for structured rendering (ADR-0.0.37-11).",
    )
