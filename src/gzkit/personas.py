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

from gzkit.models.persona import PersonaFrontmatter


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
