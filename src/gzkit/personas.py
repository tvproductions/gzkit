"""Trait composition model for persona identity frames.

Persona traits compose orthogonally — each activates an independent behavioral
dimension without interfering with existing traits (PERSONA/ICLR 2026).  This
module provides a deterministic composition function that produces a persona
frame from frontmatter and optional body text.

See ADR-0.0.11 for the research basis and OBPI-0.0.11-03 for the composition
specification.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.models.persona import PersonaFrontmatter

# Project-agnostic starter personas scaffolded by ``gz init``.
# Content MUST NOT reference any specific project, language, or tool.
DEFAULT_PERSONAS: dict[str, str] = {
    "default-agent": """\
---
name: default-agent
traits:
  - methodical
  - governance-aware
  - clear-communicator
anti-traits:
  - assumptions-without-evidence
  - scope-creep
  - incomplete-work
grounding: >-
  I work inside a governed repository where every artifact traces to intent.
  I read the brief before I plan, the plan before I implement, and the
  evidence before I attest. Governance is not overhead — it is the discipline
  that keeps multi-session work coherent and auditable.
---

# Default Agent Persona

Starter persona for the primary agent session in a governed repository.
Projects should customize traits, anti-traits, and grounding to reflect
their specific workflow and values.
""",
    "default-reviewer": """\
---
name: default-reviewer
traits:
  - thorough
  - evidence-driven
  - constructive
anti-traits:
  - rubber-stamping
  - nitpicking-without-context
  - vague-feedback
grounding: >-
  I verify work against stated requirements. Every finding I report is
  grounded in evidence — a specific file, a specific test, a specific
  requirement. I distinguish between blocking issues and suggestions.
  When work meets its acceptance criteria, I say so clearly.
---

# Default Reviewer Persona

Starter persona for review and verification roles. Projects should
customize to reflect their quality standards and review culture.
""",
}


def scaffold_default_personas(project_root: Path) -> list[Path]:
    """Scaffold default persona files into ``.gzkit/personas/``.

    Creates the directory if needed and writes each default persona file
    only when no file with that name already exists.  Returns the list of
    newly created paths (empty when all defaults already exist).
    """
    personas_dir = project_root / ".gzkit" / "personas"
    personas_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for name, content in DEFAULT_PERSONAS.items():
        target = personas_dir / f"{name}.md"
        if not target.exists():
            target.write_text(content, encoding="utf-8")
            created.append(target)
    return created


def _parse_anchors(body: str, heading: str) -> dict[str, str]:
    """Extract name→description mapping from a markdown list under *heading*.

    Expects lines like ``- **Name**: Description text.`` under a ``## Heading``
    section.  Matching is case-insensitive on the bold name.
    """
    result: dict[str, str] = {}
    in_section = False
    item_re = re.compile(r"^- \*\*(.+?)\*\*:\s*(.+)$")

    for line in body.splitlines():
        stripped = line.strip()
        if stripped.startswith("## "):
            in_section = stripped.lstrip("# ").strip().lower() == heading.lower()
            continue
        if in_section:
            m = item_re.match(stripped)
            if m:
                name = m.group(1).strip().lower()
                desc = m.group(2).strip()
                result[name] = desc

    return result


def compose_persona_frame(fm: PersonaFrontmatter, body: str = "") -> str:
    """Compose a deterministic persona frame from frontmatter and body.

    The output follows the canonical template defined in OBPI-0.0.11-03:

    1. Grounding text emitted verbatim as the opening behavioral anchor.
    2. Each trait emitted as ``You are {name}: {description}`` when the body
       contains a matching ``## Behavioral Anchors`` entry, or ``You are
       {name}.`` otherwise.
    3. Anti-traits emitted under ``What this persona does NOT do:`` with
       descriptions from ``## Anti-patterns`` when available.

    Composition is deterministic: identical inputs always produce identical
    output.  Traits compose by concatenation because they activate orthogonal
    behavioral dimensions (PERSONA/ICLR 2026).
    """
    trait_descs = _parse_anchors(body, "Behavioral Anchors") if body else {}
    anti_descs = _parse_anchors(body, "Anti-patterns") if body else {}

    sections: list[str] = []

    # 1. Grounding text verbatim
    sections.append(fm.grounding.strip())

    # 2. Trait composition (orthogonal concatenation, declaration order)
    trait_lines: list[str] = []
    for trait in fm.traits:
        desc = trait_descs.get(trait.lower())
        if desc:
            trait_lines.append(f"You are {trait}: {desc}")
        else:
            trait_lines.append(f"You are {trait}.")
    sections.append("\n\n".join(trait_lines))

    # 3. Anti-trait suppression section
    if fm.anti_traits:
        anti_lines: list[str] = []
        for at in fm.anti_traits:
            desc = anti_descs.get(at.lower())
            if desc:
                anti_lines.append(f"- {at}: {desc}")
            else:
                anti_lines.append(f"- {at}")
        sections.append("What this persona does NOT do:\n" + "\n".join(anti_lines))

    return "\n\n".join(sections)
