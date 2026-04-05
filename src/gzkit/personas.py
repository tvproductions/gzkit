"""Trait composition model for persona identity frames.

Persona traits compose orthogonally — each activates an independent behavioral
dimension without interfering with existing traits (PERSONA/ICLR 2026).  This
module provides a deterministic composition function that produces a persona
frame from frontmatter and optional body text, plus vendor adapter functions
that translate canonical frames into vendor-specific formats.

See ADR-0.0.11 for the research basis and OBPI-0.0.11-03 for the composition
specification.  See OBPI-0.0.13-04 for vendor adapter design.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path

import yaml

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


# ---------------------------------------------------------------------------
# Vendor adapter functions (OBPI-0.0.13-04)
# ---------------------------------------------------------------------------


def render_persona_claude(fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame in Claude's native system prompt format.

    Delegates to ``compose_persona_frame`` which already produces the canonical
    Claude format: grounding anchor, trait instructions, anti-trait constraints.
    """
    return compose_persona_frame(fm, body)


def render_persona_codex(fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame as an AGENTS.md-compatible instruction block.

    Produces a structured markdown block with heading, grounding, behavioral
    traits list, and anti-patterns list suitable for Codex AGENTS.md files.
    """
    trait_descs = _parse_anchors(body, "Behavioral Anchors") if body else {}
    anti_descs = _parse_anchors(body, "Anti-patterns") if body else {}

    sections: list[str] = [f"# Persona: {fm.name}"]
    sections.append(fm.grounding.strip())

    trait_lines: list[str] = []
    for trait in fm.traits:
        desc = trait_descs.get(trait.lower())
        if desc:
            trait_lines.append(f"- {trait}: {desc}")
        else:
            trait_lines.append(f"- {trait}")
    sections.append("## Behavioral Traits\n\n" + "\n".join(trait_lines))

    if fm.anti_traits:
        anti_lines: list[str] = []
        for at in fm.anti_traits:
            desc = anti_descs.get(at.lower())
            if desc:
                anti_lines.append(f"- {at}: {desc}")
            else:
                anti_lines.append(f"- {at}")
        sections.append("## Anti-Patterns\n\n" + "\n".join(anti_lines))

    return "\n\n".join(sections)


def render_persona_copilot(fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame as a copilot-instructions.md-compatible fragment.

    Produces a compact markdown section with heading, grounding, and inline
    trait/anti-trait lists suitable for ``.github/copilot-instructions.md``.
    """
    sections: list[str] = [f"## Persona: {fm.name}"]
    sections.append(fm.grounding.strip())
    sections.append("Behavioral traits: " + ", ".join(fm.traits))
    if fm.anti_traits:
        sections.append("Behaviors to avoid: " + ", ".join(fm.anti_traits))
    return "\n\n".join(sections)


def _rebuild_raw_persona(fm: PersonaFrontmatter, body: str) -> str:
    """Reconstruct canonical persona markdown from frontmatter and body.

    Used as the fallback when no vendor adapter is registered — the raw
    canonical format is copied verbatim.
    """
    fm_dict = {
        "name": fm.name,
        "traits": list(fm.traits),
        "anti-traits": list(fm.anti_traits),
        "grounding": fm.grounding,
    }
    fm_yaml = yaml.dump(fm_dict, default_flow_style=False, sort_keys=False, allow_unicode=True)
    return f"---\n{fm_yaml}---\n\n{body}"


VENDOR_ADAPTERS: dict[str, Callable[[PersonaFrontmatter, str], str]] = {
    "claude": render_persona_claude,
    "codex": render_persona_codex,
    "copilot": render_persona_copilot,
}
"""Registry mapping vendor name to persona adapter function."""


def render_persona_for_vendor(vendor: str, fm: PersonaFrontmatter, body: str = "") -> str:
    """Render a persona frame for the given vendor.

    Looks up the vendor in ``VENDOR_ADAPTERS``.  If no adapter is registered,
    returns the raw canonical markdown as fallback (REQ-0.0.13-04-04).
    """
    adapter = VENDOR_ADAPTERS.get(vendor)
    if adapter is not None:
        return adapter(fm, body)
    return _rebuild_raw_persona(fm, body)
