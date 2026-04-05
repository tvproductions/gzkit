"""Pydantic model and helpers for persona identity frame files.

Persona files live in ``.gzkit/personas/`` as markdown with YAML frontmatter
defining composable behavioral identity traits (ADR-0.0.11).
"""

from __future__ import annotations

from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict, Field, ValidationError

SCHEMA_NAME = "persona"
"""Schema name for ``load_schema()`` lookup — maps to ``schemas/persona.json``."""


class PersonaFrontmatter(BaseModel):
    """Frozen model for persona file YAML frontmatter."""

    model_config = ConfigDict(frozen=True, extra="forbid", populate_by_name=True)

    name: str = Field(..., description="Persona identifier, matches filename stem")
    traits: list[str] = Field(..., description="Behavioral identity traits")
    anti_traits: list[str] = Field(
        ..., alias="anti-traits", description="Behaviors this persona avoids"
    )
    grounding: str = Field(..., description="Behavioral anchor text")


def parse_persona_file(path: Path) -> tuple[PersonaFrontmatter, str]:
    """Parse a persona markdown file into frontmatter model and body text.

    Raises ``ValueError`` if frontmatter is missing or malformed.
    """
    content = path.read_text(encoding="utf-8")
    if not content.startswith("---"):
        msg = f"{path.name}: missing YAML frontmatter delimiters"
        raise ValueError(msg)

    parts = content.split("---", 2)
    if len(parts) < 3:
        msg = f"{path.name}: incomplete YAML frontmatter delimiters"
        raise ValueError(msg)

    fm_raw = yaml.safe_load(parts[1])
    if not isinstance(fm_raw, dict):
        msg = f"{path.name}: frontmatter is not a YAML mapping"
        raise ValueError(msg)

    try:
        fm = PersonaFrontmatter(**fm_raw)
    except ValidationError as exc:
        msg = f"{path.name}: {exc}"
        raise ValueError(msg) from exc

    body = parts[2].lstrip("\n")
    return fm, body


def discover_persona_files(personas_dir: Path) -> list[Path]:
    """Return sorted list of ``.md`` files in the personas directory."""
    if not personas_dir.is_dir():
        return []
    return sorted(personas_dir.glob("*.md"))


def validate_persona_structure(path: Path) -> list[str]:
    """Validate a persona file for structural correctness beyond Pydantic.

    Checks:
    - Frontmatter parses successfully (delegates to ``parse_persona_file``)
    - At least one trait defined
    - At least one anti-trait defined
    - Grounding text is non-empty
    - ``name`` matches the filename stem

    Returns a list of error messages (empty means valid).
    """
    errors: list[str] = []
    try:
        fm, _body = parse_persona_file(path)
    except (ValueError, yaml.YAMLError) as exc:
        return [f"{path.name}: {exc}"]

    if not fm.traits:
        errors.append(f"{path.name}: traits list must not be empty")
    if not fm.anti_traits:
        errors.append(f"{path.name}: anti-traits list must not be empty")
    if not fm.grounding.strip():
        errors.append(f"{path.name}: grounding text must not be empty")
    if fm.name != path.stem:
        errors.append(f"{path.name}: name '{fm.name}' does not match filename stem '{path.stem}'")
    return errors


def load_persona(project_root: Path, role_name: str) -> str | None:
    """Load persona body text for a pipeline role.

    Looks for ``.gzkit/personas/{role_name}.md``. Returns the markdown body
    (everything after frontmatter) if found and valid.  Returns ``None`` if
    the persona file does not exist.  Raises ``ValueError`` on parse errors.
    """
    persona_path = project_root / ".gzkit" / "personas" / f"{role_name}.md"
    if not persona_path.is_file():
        return None
    _fm, body = parse_persona_file(persona_path)
    return body
