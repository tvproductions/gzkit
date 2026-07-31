"""Shared ADR section-body extraction and substance testing (GHI #741).

Two audits interrogate ADR section bodies for authored content:
``kind_invariance`` (``## Why foundation tier?``) and ``persona_witness``
(``## Persona``). They were one module and one copy of the substance test
until the second scope landed; this module is that shared definition, so
strengthening the placeholder detector closes the hole for every section it
governs rather than for whichever audit happened to be edited.

The detector recognises four non-substantive shapes:

    * empty / whitespace-only
    * a ``STRICT_PLACEHOLDERS`` token (TBD, TODO, none, ...)
    * an unfilled author-prompt — ``_[...]_`` brackets or an HTML comment
    * unsubstituted template residue — a bare ``{token}``

The last two are the GHI #741 additions. ``render_template`` formats through
``SafeDict``, whose ``__missing__`` returns ``f"{{{key}}}"`` — so a template
variable the caller forgets to pass renders as its own literal token instead
of raising ``KeyError``. That residue is non-empty, is not a strict
placeholder, and survives a ``_[...]_`` strip, so every prior substance test
read it as prose. Five ADRs shipped with a literal ``{persona}`` body on that
path and four of them passed Gate 5.
"""

from __future__ import annotations

import re

from gzkit.hooks.obpi import STRICT_PLACEHOLDERS

_BRACKETED_PROMPT_RE = re.compile(r"_\[.*?\]_", re.DOTALL)
_HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
_TEMPLATE_TOKEN_RE = re.compile(r"\{[a-z_][a-z0-9_]*\}")


def is_placeholder_body(text: str) -> bool:
    """Return True if *text* is empty or carries no authored content.

    Author-prompts and template residue are removed before the substance test,
    never merely searched for: a body is non-substantive when *nothing remains*
    once the scaffolding is taken out. Prose that happens to contain a brace
    token or an inline comment therefore still passes — only a body made
    entirely of scaffolding fails.
    """
    clean = text.strip().lower()
    if not clean:
        return True
    if clean in STRICT_PLACEHOLDERS:
        return True
    if any(p in clean for p in ["paste", "one-sentence"]):
        return True
    stripped = _HTML_COMMENT_RE.sub("", clean)
    stripped = _BRACKETED_PROMPT_RE.sub("", stripped)
    stripped = _TEMPLATE_TOKEN_RE.sub("", stripped)
    return not stripped.strip()


def extract_section_body(content: str, heading: str) -> str | None:
    """Return the body between *heading* and the next ``##`` heading.

    Returns None when the heading is absent, and an empty string when it is
    present but carries no body lines — the caller distinguishes "section
    missing" from "section hollow" because the recovery differs.
    """
    lines = content.splitlines()
    in_section = False
    body_lines: list[str] = []
    for line in lines:
        if line.rstrip() == heading:
            in_section = True
            continue
        if in_section:
            if line.startswith("## "):
                break
            body_lines.append(line)
    if not in_section:
        return None
    return "\n".join(body_lines)


def strip_frontmatter(content: str) -> str:
    """Return *content* with the leading YAML frontmatter block removed."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return content
    for i in range(1, len(lines)):
        if lines[i].strip() == "---":
            return "\n".join(lines[i + 1 :])
    return content
