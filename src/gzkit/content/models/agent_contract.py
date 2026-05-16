"""AgentContract content model — target AGENTS.md / CLAUDE.md surfaces."""

from pydantic import Field

from .base import BaseContentModel
from .bullet import Bullet


class AgentContract(BaseContentModel):
    """Per-turn surface content for AGENTS.md / CLAUDE.md."""

    name: str
    purpose: str
    tech_stack: list[str] = Field(default_factory=list)
    rules: list[Bullet] = Field(default_factory=list)
