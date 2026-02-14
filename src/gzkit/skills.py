"""Skills scaffolding and management for gzkit.

Skills are reusable agent instructions that can be triggered contextually.
"""

from dataclasses import dataclass
from pathlib import Path
from typing import Any

from gzkit.config import GzkitConfig
from gzkit.templates import render_template

# Core skills that are scaffolded by `gz init`
CORE_SKILLS = {
    "gz-adr-create": {
        "skill_name": "ADR Create",
        "skill_description": "Create ADRs with OBPI briefs.",
        "trigger_description": "When creating a feature or making architecture decisions.",
        "behavior_description": "Guide ADR creation, ensuring all required sections.",
        "prerequisites": "Active OBPI exists in the ledger",
    },
    "gz-adr-audit": {
        "skill_name": "ADR Audit",
        "skill_description": "Audit ADR evidence and verify gate completion.",
        "trigger_description": "Before requesting human attestation.",
        "behavior_description": "Check OBPIs have evidence, verify tests and docs exist.",
        "prerequisites": "ADR exists with implementation complete",
    },
    "lint": {
        "skill_name": "Lint",
        "skill_description": "Run code linting with Ruff and PyMarkdown.",
        "trigger_description": "After making code changes.",
        "behavior_description": "Run `gz lint` and report issues.",
        "prerequisites": "None",
    },
    "test": {
        "skill_name": "Test",
        "skill_description": "Run unit tests with unittest.",
        "trigger_description": "After implementing features or fixing bugs.",
        "behavior_description": "Run `gz test` and report results.",
        "prerequisites": "Tests exist for the code being tested",
    },
    "format": {
        "skill_name": "Format",
        "skill_description": "Auto-format code with Ruff.",
        "trigger_description": "Before committing changes.",
        "behavior_description": "Run `gz format` to fix formatting issues.",
        "prerequisites": "None",
    },
}


@dataclass
class Skill:
    """Represents a skill definition."""

    name: str
    path: Path
    description: str

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": str(self.path),
            "description": self.description,
        }


def scaffold_skill(
    project_root: Path,
    dir_name: str,
    skills_dir: str,
    **kwargs: str,
) -> Path:
    """Scaffold a new skill from template.

    Args:
        project_root: Project root directory.
        dir_name: Directory name for the skill.
        skills_dir: Directory for skills relative to project root.
        **kwargs: Template variables.

    Returns:
        Path to the created SKILL.md file.
    """
    skill_path = project_root / skills_dir / dir_name
    skill_path.mkdir(parents=True, exist_ok=True)

    # Default values (skill_name in template is display name)
    defaults = {
        "skill_name": dir_name.replace("-", " ").title(),
        "skill_description": "A custom skill for this project.",
        "trigger_description": "When triggered by the user.",
        "behavior_description": "Follow the steps below.",
        "prerequisites": "None",
        "example_input": "Example input",
        "example_output": "Example output",
    }

    context = {**defaults, **kwargs}
    content = render_template("skill", **context)

    skill_file = skill_path / "SKILL.md"
    skill_file.write_text(content)

    return skill_file


def scaffold_core_skills(project_root: Path, config: GzkitConfig | None = None) -> list[Path]:
    """Scaffold all core skills.

    Args:
        project_root: Project root directory.
        config: Optional configuration.

    Returns:
        List of paths to created SKILL.md files.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    created = []
    for dir_name, kwargs in CORE_SKILLS.items():
        skill_file = scaffold_skill(
            project_root,
            dir_name,
            config.paths.skills,
            **kwargs,
        )
        created.append(skill_file)

    return created


def list_skills(project_root: Path, config: GzkitConfig | None = None) -> list[Skill]:
    """List all skills in the project.

    Args:
        project_root: Project root directory.
        config: Optional configuration.

    Returns:
        List of Skill objects.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    skills_dir = project_root / config.paths.skills
    if not skills_dir.exists():
        return []

    skills = []
    for skill_path in skills_dir.iterdir():
        if skill_path.is_dir():
            skill_file = skill_path / "SKILL.md"
            if skill_file.exists():
                # Extract description from SKILL.md
                content = skill_file.read_text()
                description = ""
                for line in content.split("\n"):
                    if line.strip() and not line.startswith("#"):
                        description = line.strip()
                        break

                skills.append(
                    Skill(
                        name=skill_path.name,
                        path=skill_path,
                        description=description,
                    )
                )

    return sorted(skills, key=lambda s: s.name)


def get_skill(
    project_root: Path,
    skill_name: str,
    config: GzkitConfig | None = None,
) -> Skill | None:
    """Get a skill by name.

    Args:
        project_root: Project root directory.
        skill_name: Name of the skill.
        config: Optional configuration.

    Returns:
        Skill object or None if not found.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    skill_path = project_root / config.paths.skills / skill_name
    skill_file = skill_path / "SKILL.md"

    if not skill_file.exists():
        return None

    content = skill_file.read_text()
    description = ""
    for line in content.split("\n"):
        if line.strip() and not line.startswith("#"):
            description = line.strip()
            break

    return Skill(
        name=skill_name,
        path=skill_path,
        description=description,
    )
