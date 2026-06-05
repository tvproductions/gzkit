"""Content model registry — canonical per-turn surface artifact types.

See ADR-0.0.34-agent-control-surface-rendering-substrate § Decision item #1.
"""

from .agent_contract import AgentContract, Pillar
from .base import BaseContentModel
from .bullet import Bullet
from .chore import Chore
from .corpus import Corpus, CorpusEntry
from .handoff import Handoff
from .persona import Persona
from .rule import Rule
from .scenario import Scenario
from .skill import Skill

# CONTENT_MODELS is the parse/render dispatch registry for top-level surfaces.
# Corpus/CorpusEntry are store records (cf. ConstitutionalInvariant), not renderable
# surfaces — exported below but deliberately NOT registered here, the same way Pillar
# (a store-only sub-model) is exported yet absent from CONTENT_MODELS (ADR-0.0.37-18).
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
    "Pillar",
    "Chore",
    "Corpus",
    "CorpusEntry",
    "Handoff",
    "Persona",
    "Rule",
    "Scenario",
    "Skill",
]
