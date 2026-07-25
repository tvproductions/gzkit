"""Per-type markdown parsers — ADR-0.0.34 § Decision item #3.

Each _parse_<type> function accepts pre-split lines and returns a model instance.
The public parse() function dispatches to the correct _parse_<type> by as_type key.

ADR-0.0.37-13 extends _parse_agent_contract from the name+purpose stub to a
full-contract reverse parse: every ``##`` section becomes a Pillar carrying its
verbatim body lines (full fidelity) plus the rule-bearing lines extracted as
classified Bullets, with classification joined from the advisory scorecard.
"""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING, Literal

from gzkit.content.migration.registry import apply_migrations
from gzkit.content.models import CONTENT_MODELS
from gzkit.content.models.agent_contract import AgentContract, Pillar
from gzkit.content.models.base import BaseContentModel
from gzkit.content.models.bullet import Bullet
from gzkit.content.models.chore import Chore
from gzkit.content.models.handoff import Handoff
from gzkit.content.models.persona import Persona
from gzkit.content.models.rule import Rule
from gzkit.content.models.scenario import Scenario
from gzkit.content.models.skill import Skill

if TYPE_CHECKING:
    pass


_SCHEMA_VERSION_PREFIX = "Schema-version: "


def _extract_schema_version(lines: list[str]) -> int:
    """Return schema_version declared in preamble 'Schema-version: N' line.

    Defaults to 1 when no such line is present (so existing v1 fixtures
    without the declaration continue to parse unchanged — REQ-0.0.34-07-04
    byte-stability invariant).
    """
    for line in lines:
        if line.startswith(_SCHEMA_VERSION_PREFIX):
            payload = line[len(_SCHEMA_VERSION_PREFIX) :].strip()
            try:
                return int(payload)
            except ValueError:
                return 1
    return 1


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------


def _split_lines(text: str) -> list[str]:
    """Strip trailing document newlines then split on newlines, rstrip each line."""
    lines = text.rstrip("\n").split("\n")
    return [line.rstrip() for line in lines]


def _sections(lines: list[str]) -> dict[str, list[str]]:
    """Split lines by ## headings. Returns {section_title: [content_lines], ...}.

    Special key '' holds content before the first ## heading.
    Multiple consecutive blank lines within a section are preserved as-is.
    """
    result: dict[str, list[str]] = {}
    current_key = ""
    result[current_key] = []

    for line in lines:
        if line.startswith("## "):
            current_key = line[3:].strip()
            result[current_key] = []
        else:
            result[current_key].append(line)

    return result


def _parse_bullets(lines: list[str]) -> list[Bullet]:
    """Parse indented '- text' lines into Bullet instances.

    Indent level = number of leading spaces // 2.
    Blank lines are skipped.
    """
    bullets: list[Bullet] = []
    for line in lines:
        if not line.strip():
            continue
        stripped = line.lstrip()
        if not stripped.startswith("- "):
            continue
        leading_spaces = len(line) - len(stripped)
        indent = leading_spaces // 2
        text = stripped[2:]  # strip "- " prefix
        bullets.append(Bullet(text=text, indent=indent))
    return bullets


def _first_h1(lines: list[str], prefix: str, file_path: str | None) -> str:
    """Extract value from the first H1 line matching '# <prefix><value>'.

    prefix is stripped from the H1 text. Raises ValueError if not found.
    """
    for line in lines:
        if line.startswith("# "):
            value = line[2:]
            if not value.startswith(prefix):
                raise ValueError(
                    f"{_fp(file_path)}Expected H1 starting with '# {prefix}', got {line!r}"
                )
            return value[len(prefix) :]
    raise ValueError(f"{_fp(file_path)}No H1 heading found")


def _fp(file_path: str | None) -> str:
    """Format file_path prefix for error messages."""
    return f"{file_path}: " if file_path else ""


def _find_inline_value(lines: list[str], prefix: str, file_path: str | None) -> str:
    """Find the first line starting with 'prefix' and return the trailing value.

    Raises ValueError if not found.
    """
    for line in lines:
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    raise ValueError(f"{_fp(file_path)}Expected line starting with {prefix!r}")


def _paragraph_after(lines: list[str], after_prefix: str, file_path: str | None) -> str:
    """Return the first non-blank text line appearing after the line with after_prefix.

    Raises ValueError if not found.
    """
    found_after = False
    for line in lines:
        if not found_after:
            if line.startswith(after_prefix):
                found_after = True
        else:
            stripped = line.strip()
            if stripped and not stripped.startswith("#"):
                return stripped
    raise ValueError(f"{_fp(file_path)}No paragraph found after {after_prefix!r}")


# ---------------------------------------------------------------------------
# AgentContract full-contract reverse parse (ADR-0.0.37-13)
# ---------------------------------------------------------------------------

# Sections that have dedicated AgentContract fields — never promoted to pillars
# (promoting them would double-represent and break parse(render(model)) for the
# OBPI-0.0.34 round-trip fixtures that use these fields).
_LEGACY_PILLAR_SECTIONS = frozenset({"Tech Stack", "Rules"})

_Classification = Literal["Mechanical", "Promotable", "Judgment", "Ambiguous"]
_SCORECARD_REL = ("docs", "governance", "advisory-rules-audit.md")
_LIST_MARKER_RE = re.compile(r"(?:[-*]|\d+[.)])\s+(.*)")
_MIN_MATCH_WORDS = 4


def _as_classification(value: str) -> _Classification | None:
    """Narrow a raw scorecard score string to the classification Literal (None if not a member)."""
    if value == "Mechanical":
        return "Mechanical"
    if value == "Promotable":
        return "Promotable"
    if value == "Judgment":
        return "Judgment"
    if value == "Ambiguous":
        return "Ambiguous"
    return None


def section_id(title: str) -> str:
    """Lowercase kebab-case id derived from a section title.

    This is the single section-id vocabulary shared by every surface that names
    a section: ``Pillar.id`` on the parsed contract, the corpus ``section``
    field written by ``gz content remember``, and the survival declaration read
    by the surface-delivery witness. It is public because a second slugifier
    would let those surfaces disagree about what a section is called.
    """
    slug = re.sub(r"[^a-z0-9]+", "-", title.lower()).strip("-")
    return slug or "section"


def _strip_trailing_blanks(lines: list[str]) -> list[str]:
    """Drop trailing blank lines so inter-section whitespace is not captured.

    Applied at both import-capture and round-trip reparse so pillar bodies
    compare equal across render -> parse (ADR-0.0.37-13 REQ-04).
    """
    end = len(lines)
    while end > 0 and not lines[end - 1].strip():
        end -= 1
    return lines[:end]


def _normalize_rule(text: str) -> str:
    """Normalize a rule line for scorecard matching.

    Drops list markers, markdown emphasis and backticks, non-alphanumerics;
    collapses whitespace; lowercases. The result is a paraphrase-tolerant key
    for high-precision containment matching against the scorecard.
    """
    lowered = re.sub(r"^\s*(?:[-*]|\d+[.)])\s+", "", text.lower())
    lowered = lowered.replace("`", "").replace("*", "")
    lowered = re.sub(r"[^a-z0-9 ]+", " ", lowered)
    return re.sub(r"\s+", " ", lowered).strip()


def _find_scorecard(file_path: str | None) -> Path | None:
    """Locate docs/governance/advisory-rules-audit.md walking up from file_path."""
    if not file_path:
        return None
    here = Path(file_path).resolve().parent
    for root in (here, *here.parents):
        candidate = root.joinpath(*_SCORECARD_REL)
        if candidate.exists():
            return candidate
    return None


def _load_scorecard_index(file_path: str | None) -> dict[str, _Classification]:
    """Map normalized rule text -> classification from the advisory scorecard.

    Best-effort: returns {} when the scorecard cannot be located or read, so
    fixture parses (no scorecard) gracefully fall back to Ambiguous (REQ-05).
    """
    path = _find_scorecard(file_path)
    if path is None:
        return {}
    index: dict[str, _Classification] = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|"):
            continue
        cells = [cell.strip() for cell in line.strip().strip("|").split("|")]
        if len(cells) < 3:
            continue
        classification = _as_classification(cells[2].strip("* "))
        if classification is None:
            continue
        norm = _normalize_rule(cells[1])
        if len(norm.split()) >= _MIN_MATCH_WORDS:
            index.setdefault(norm, classification)
    return index


def _classify(text: str, index: dict[str, _Classification]) -> _Classification:
    """Join classification from the scorecard; default Ambiguous (REQ-05).

    Conservative high-precision match: a scorecard rule classifies a bullet only
    when its whole normalized text is contained in (or contains) the bullet's
    normalized text. No match defaults to Ambiguous — never silently Mechanical.
    """
    norm = _normalize_rule(text)
    if len(norm.split()) < _MIN_MATCH_WORDS:
        return "Ambiguous"
    for rule_norm, score in index.items():
        if rule_norm in norm or norm in rule_norm:
            return score
    return "Ambiguous"


def _extract_pillar_bullets(lines: list[str], index: dict[str, _Classification]) -> list[Bullet]:
    """Extract rule-bearing lines (- bullets and N. numbered items) as Bullets.

    Each bullet's classification is joined from the scorecard (REQ-02), defaulting
    to Ambiguous when unmatched (REQ-05).
    """
    bullets: list[Bullet] = []
    for line in lines:
        stripped = line.lstrip()
        match = _LIST_MARKER_RE.fullmatch(stripped)
        if match is None:
            continue
        text = match.group(1).strip()
        if not text:
            continue
        indent = (len(line) - len(stripped)) // 2
        bullets.append(Bullet(text=text, indent=indent, classification=_classify(text, index)))
    return bullets


def _build_pillars(secs: dict[str, list[str]], index: dict[str, _Classification]) -> list[Pillar]:
    """Build one Pillar per ## section (in document order), excluding legacy fields."""
    pillars: list[Pillar] = []
    order = 0
    for title, body_lines in secs.items():
        if title == "" or title in _LEGACY_PILLAR_SECTIONS:
            continue
        order += 1
        body = _strip_trailing_blanks(body_lines)
        pillars.append(
            Pillar(
                id=section_id(title),
                title=title,
                order=order,
                lines=body,
                bullets=_extract_pillar_bullets(body, index),
            )
        )
    return pillars


# ---------------------------------------------------------------------------
# Per-type parsers
# ---------------------------------------------------------------------------


def _parse_agent_contract(lines: list[str], file_path: str | None) -> AgentContract:
    """Parse AgentContract from pre-split lines (full-contract reverse parse)."""
    name = _first_h1(lines, "", file_path)
    secs = _sections(lines)

    # purpose: first non-blank, non-H1 line before first ## heading
    purpose = ""
    for line in secs.get("", []):
        stripped = line.strip()
        if stripped and not stripped.startswith("# "):
            purpose = stripped
            break

    tech_stack = [
        line.lstrip("- ").strip()
        for line in secs.get("Tech Stack", [])
        if line.strip() and line.strip().startswith("- ")
    ]
    rules = _parse_bullets(secs.get("Rules", []))

    index = _load_scorecard_index(file_path)
    pillars = _build_pillars(secs, index)

    return AgentContract(
        name=name, purpose=purpose, tech_stack=tech_stack, rules=rules, pillars=pillars
    )


def _parse_rule(lines: list[str], file_path: str | None) -> Rule:
    """Parse Rule from pre-split lines."""
    title = _first_h1(lines, "", file_path)
    secs = _sections(lines)

    preamble = secs.get("", [])
    version = _find_inline_value(preamble, "Version: ", file_path)

    paths_lines = secs.get("Paths", [])
    paths = [
        line.lstrip("- ").strip()
        for line in paths_lines
        if line.strip() and line.strip().startswith("- ")
    ]

    body_lines = secs.get("Body", [])
    body = _parse_bullets(body_lines)

    return Rule(title=title, version=version, paths=paths, body=body)


def _parse_skill(lines: list[str], file_path: str | None) -> Skill:
    """Parse Skill from pre-split lines."""
    title = _first_h1(lines, "", file_path)
    secs = _sections(lines)

    preamble = secs.get("", [])
    slug = _find_inline_value(preamble, "Slug: ", file_path)
    purpose = _paragraph_after(preamble, "Slug: ", file_path)

    steps_lines = secs.get("Steps", [])
    steps = _parse_bullets(steps_lines)

    return Skill(slug=slug, title=title, purpose=purpose, steps=steps)


def _parse_chore(lines: list[str], file_path: str | None) -> Chore:
    """Parse Chore from pre-split lines."""
    title = _first_h1(lines, "", file_path)
    secs = _sections(lines)

    preamble = secs.get("", [])
    slug = _find_inline_value(preamble, "Slug: ", file_path)
    cadence = _find_inline_value(preamble, "Cadence: ", file_path)

    steps_lines = secs.get("Steps", [])
    steps = _parse_bullets(steps_lines)

    return Chore(slug=slug, title=title, cadence=cadence, steps=steps)


def _parse_persona(lines: list[str], file_path: str | None) -> Persona:
    """Parse Persona from pre-split lines."""
    slug = _first_h1(lines, "", file_path)
    secs = _sections(lines)

    preamble = secs.get("", [])
    role = _find_inline_value(preamble, "Role: ", file_path)

    traits_lines = secs.get("Traits", [])
    traits = [
        line.lstrip("- ").strip()
        for line in traits_lines
        if line.strip() and line.strip().startswith("- ")
    ]

    return Persona(slug=slug, role=role, traits=traits)


def _parse_handoff(lines: list[str], file_path: str | None) -> Handoff:
    """Parse Handoff from pre-split lines."""
    session_id = _first_h1(lines, "Handoff: ", file_path)
    secs = _sections(lines)

    preamble = secs.get("", [])
    state_summary = ""
    for line in preamble:
        stripped = line.strip()
        if stripped and not stripped.startswith("# "):
            state_summary = stripped
            break

    open_items_lines = secs.get("Open Items", [])
    open_items = _parse_bullets(open_items_lines)

    resume_lines = secs.get("Resume Point", [])
    resume_point = " ".join(line.strip() for line in resume_lines if line.strip())

    return Handoff(
        session_id=session_id,
        state_summary=state_summary,
        open_items=open_items,
        resume_point=resume_point,
    )


def _parse_scenario(lines: list[str], file_path: str | None) -> Scenario:
    """Parse Scenario from pre-split lines."""
    feature = ""
    scenario = ""
    given: list[str] = []
    when: list[str] = []
    then: list[str] = []

    for line in lines:
        stripped = line.strip()
        if line.startswith("Feature: "):
            feature = line[len("Feature: ") :].strip()
        elif stripped.startswith("Scenario: "):
            scenario = stripped[len("Scenario: ") :].strip()
        elif stripped.startswith("Given "):
            given.append(stripped[len("Given ") :].strip())
        elif stripped.startswith("When "):
            when.append(stripped[len("When ") :].strip())
        elif stripped.startswith("Then "):
            then.append(stripped[len("Then ") :].strip())

    if not feature:
        raise ValueError(f"{_fp(file_path)}No 'Feature:' line found")
    if not scenario:
        raise ValueError(f"{_fp(file_path)}No 'Scenario:' line found")

    return Scenario(feature=feature, scenario=scenario, given=given, when=when, then=then)


def _parse_bullet(lines: list[str], file_path: str | None) -> Bullet:
    """Parse a single Bullet from lines.

    Finds first non-blank line starting with optional spaces then '- '.
    indent = leading_spaces // 2.
    """
    for line in lines:
        if not line.strip():
            continue
        stripped = line.lstrip()
        if stripped.startswith("- "):
            leading_spaces = len(line) - len(stripped)
            indent = leading_spaces // 2
            text = stripped[2:]
            return Bullet(text=text, indent=indent)
    raise ValueError(f"{_fp(file_path)}No bullet line found")


# ---------------------------------------------------------------------------
# Dispatch table
# ---------------------------------------------------------------------------

_PARSERS: dict[str, Callable[[list[str], str | None], BaseContentModel]] = {
    "AgentContract": _parse_agent_contract,
    "Rule": _parse_rule,
    "Skill": _parse_skill,
    "Chore": _parse_chore,
    "Persona": _parse_persona,
    "Handoff": _parse_handoff,
    "Scenario": _parse_scenario,
    "Bullet": _parse_bullet,
}


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def parse(text: str, as_type: str, *, file_path: str | None = None) -> BaseContentModel:
    """Parse canonical markdown text into a BaseContentModel instance.

    Args:
        text: Canonical markdown as produced by render().
        as_type: Content type name (key in CONTENT_MODELS, e.g. "Rule", "AgentContract").
        file_path: Optional source path for error messages (included in ValueError text
            when provided). For AgentContract, also anchors advisory-scorecard discovery
            for per-bullet classification (ADR-0.0.37-13); when omitted, bullets default
            to Ambiguous.

    Returns:
        A validated Pydantic model instance of the requested type.

    Raises:
        KeyError: if as_type is not in CONTENT_MODELS.
        ValueError: if text does not match the expected canonical format for as_type.
            Message includes file path (when provided) and line number where derivable.
        pydantic.ValidationError: if parsed fields fail model validation.

    Whitespace normalizations (round-trip safe):
      - Multiple consecutive blank lines are treated as a single section separator.
      - Trailing whitespace on individual lines is stripped during parsing.
      - Trailing newlines at end of input are ignored.

    """
    if as_type not in CONTENT_MODELS:
        raise KeyError(f"Unknown content type {as_type!r}; valid types: {sorted(CONTENT_MODELS)}")

    parser = _PARSERS[as_type]
    lines = _split_lines(text)
    source_version = _extract_schema_version(lines)
    model = parser(lines, file_path)
    target_version = CONTENT_MODELS[as_type].model_fields["schema_version"].default
    if source_version != target_version:
        model = apply_migrations(
            model,
            as_type,
            source_version=source_version,
            target_version=target_version,
        )
    return model
