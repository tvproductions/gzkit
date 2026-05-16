"""Content model registry — canonical per-turn surface artifact types.

See ADR-0.0.34-agent-control-surface-rendering-substrate § Decision item #1.
"""

from .agent_contract import AgentContract
from .base import BaseContentModel
from .bullet import Bullet
from .chore import Chore
from .handoff import Handoff
from .persona import Persona
from .rule import Rule
from .scenario import Scenario
from .skill import Skill

CONTENT_MODELS: dict[str, type[BaseContentModel]] = {
    "AgentContract": AgentContract,
    "Rule": Rule,
    "Skill": Skill,
    "Chore": Chore,
    "Persona": Persona,
    "Handoff": Handoff,
    "Scenario": Scenario,
    "Bullet": Bullet,
}

__all__ = [
    "CONTENT_MODELS",
    "AgentContract",
    "BaseContentModel",
    "Bullet",
    "Chore",
    "Handoff",
    "Persona",
    "Rule",
    "Scenario",
    "Skill",
]
