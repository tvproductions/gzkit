"""BDD steps for persona control surface scenarios."""

from __future__ import annotations

from pathlib import Path

from behave import given


@given('a persona file "{name}" exists')
def step_persona_file_exists(_context, name: str) -> None:  # type: ignore[no-untyped-def]
    personas_dir = Path(".gzkit/personas")
    personas_dir.mkdir(parents=True, exist_ok=True)
    persona_file = personas_dir / f"{name}.md"
    persona_file.write_text(
        "---\n"
        f"name: {name}\n"
        "traits:\n"
        "  - methodical\n"
        "  - test-first\n"
        "anti-traits:\n"
        "  - minimum-viable-effort\n"
        "grounding: Behavioral anchor text.\n"
        "---\n\n"
        f"# {name.title()} Persona\n\nBehavioral identity frame.\n",
        encoding="utf-8",
    )
