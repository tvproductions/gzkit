"""Composition renderer for constitutional invariant registry (ADR-0.0.37, OBPI-0.0.37-02)."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path

from gzkit.governance.invariants import ConstitutionalInvariant


def render_agents_md(
    invariants: Mapping[str, ConstitutionalInvariant],
    template_root: Path,
) -> bytes:
    """Render AGENTS.md bytes from the invariant registry.

    Byte-deterministic: same inputs produce identical bytes across calls and processes.
    Iteration order is always lexicographic by id (REQ-0.0.37-02-02).
    Uses Jinja2 if importable; falls back to stdlib string.Template (REQ-0.0.37-02-03).
    Never LLM-driven.
    """
    sorted_invariants: dict[str, ConstitutionalInvariant] = dict(sorted(invariants.items()))
    template_path = template_root / "agents.md"
    template_text = template_path.read_text(encoding="utf-8")

    try:
        from jinja2 import BaseLoader, Environment  # type: ignore

        env = Environment(loader=BaseLoader(), keep_trailing_newline=True)
        tmpl = env.from_string(template_text)
        rendered = tmpl.render(invariants=sorted_invariants)
    except ImportError:
        from string import Template

        tmpl_stdlib = Template(template_text)
        rendered = tmpl_stdlib.substitute(invariants=sorted_invariants)

    return rendered.encode("utf-8")
