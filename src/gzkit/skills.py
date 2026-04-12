"""Skills scaffolding and management for gzkit.

Skills are reusable agent instructions that can be triggered contextually.
"""

from datetime import date
from pathlib import Path
from typing import Any

from pydantic import BaseModel, ConfigDict

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


class Skill(BaseModel):
    """Represents a skill definition."""

    model_config = ConfigDict(extra="forbid")

    name: str
    path: Path
    description: str
    lifecycle_state: str = "active"

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "path": str(self.path),
            "description": self.description,
            "lifecycle_state": self.lifecycle_state,
        }


class SkillAuditIssue(BaseModel):
    """Represents one skill-audit finding."""

    model_config = ConfigDict(extra="forbid")

    severity: str  # error | warning
    code: str
    path: str
    message: str
    blocking: bool

    def to_dict(self) -> dict[str, Any]:
        """Convert issue to dictionary."""
        return {
            "severity": self.severity,
            "code": self.code,
            "path": self.path,
            "message": self.message,
            "blocking": self.blocking,
        }


class SkillAuditReport(BaseModel):
    """Structured report from skill audit checks."""

    model_config = ConfigDict(extra="forbid")

    valid: bool
    issues: list[SkillAuditIssue]
    checked_skills: int
    checked_roots: list[str]

    def to_dict(self) -> dict[str, Any]:
        """Convert report to dictionary."""
        return {
            "valid": self.valid,
            "checked_skills": self.checked_skills,
            "checked_roots": self.checked_roots,
            "issues": [issue.to_dict() for issue in self.issues],
        }


def _parse_frontmatter(content: str) -> tuple[dict[str, str], str]:
    """Parse top-level YAML frontmatter key-values from markdown."""
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, content

    frontmatter: dict[str, str] = {}
    active_map_key: str | None = None
    end_idx = -1
    for idx, raw in enumerate(lines[1:], start=1):
        stripped = raw.strip()
        if stripped == "---":
            end_idx = idx
            break
        if not stripped or raw.lstrip().startswith("#"):
            continue

        if raw.startswith((" ", "\t")):
            if active_map_key and ":" in stripped:
                key, value = stripped.split(":", 1)
                nested_key = f"{active_map_key}.{key.strip()}"
                frontmatter[nested_key] = value.strip().strip("\"'")
            continue

        active_map_key = None
        if ":" not in stripped:
            continue

        key, value = stripped.split(":", 1)
        normalized_key = key.strip()
        normalized_value = value.strip().strip("\"'")
        if not value.strip() and normalized_key == "metadata":
            active_map_key = normalized_key
            continue

        frontmatter[normalized_key] = normalized_value

    if end_idx == -1:
        return {}, content

    body = "\n".join(lines[end_idx + 1 :])
    return frontmatter, body


def _body_description(body: str) -> str:
    """Extract a human-readable description from markdown body."""
    for line in body.splitlines():
        text = line.strip()
        if not text:
            continue
        if text.startswith("#"):
            continue
        return text
    return ""


def _read_description(skill_file: Path) -> str:
    """Read skill description from frontmatter or markdown body."""
    content = skill_file.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)
    return frontmatter.get("description") or _body_description(body)


def _read_lifecycle_state(skill_file: Path) -> str:
    """Read the skill's declared lifecycle_state (defaults to active)."""
    content = skill_file.read_text(encoding="utf-8")
    frontmatter, _ = _parse_frontmatter(content)
    return frontmatter.get("lifecycle_state") or "active"


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
        "skill_slug": dir_name,
        "skill_name": dir_name.replace("-", " ").title(),
        "skill_description": "A custom skill for this project.",
        "compatibility": "Project-local skill contract.",
        "invocation": "Describe the CLI invocation used for this skill.",
        "gz_command": "describe-command-surface",
        "metadata_skill_version": "1.0.0",
        "metadata_govzero_framework_version": "v6",
        "metadata_govzero_author": "gzkit-governance",
        "metadata_govzero_layer": "Layer 1 - Evidence Gathering",
        "lifecycle_state": "active",
        "owner": "gzkit-governance",
        "last_reviewed": date.today().isoformat(),
        "trigger_description": "When triggered by the user.",
        "behavior_description": "Follow the steps below.",
        "prerequisites": "None",
        "example_input": "Example input",
        "example_output": "Example output",
    }

    context = {**defaults, **kwargs}
    content = render_template("skill", **context)

    skill_file = skill_path / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")

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


def list_skills(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    include_retired: bool = False,
) -> list[Skill]:
    """List skills in the project.

    By default, retired skills are excluded so the CLI discovery surface matches
    the generated AGENTS.md skill catalog (see :mod:`gzkit.sync_skills`). Pass
    ``include_retired=True`` to surface retired/archived compatibility skills.

    Args:
        project_root: Project root directory.
        config: Optional configuration.
        include_retired: When True, include retired skills in the result.

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
        if not skill_path.is_dir():
            continue
        skill_file = skill_path / "SKILL.md"
        if not skill_file.exists():
            continue
        lifecycle_state = _read_lifecycle_state(skill_file)
        if lifecycle_state == "retired" and not include_retired:
            continue
        skills.append(
            Skill(
                name=skill_path.name,
                path=skill_path,
                description=_read_description(skill_file),
                lifecycle_state=lifecycle_state,
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

    return Skill(
        name=skill_name,
        path=skill_path,
        description=_read_description(skill_file),
        lifecycle_state=_read_lifecycle_state(skill_file),
    )


# Re-export audit API so existing `from gzkit.skills import X` continues to work.
from gzkit.skills_audit import DEFAULT_MAX_REVIEW_AGE_DAYS, audit_skills  # noqa: E402, F401

__all__ = [
    "CORE_SKILLS",
    "DEFAULT_MAX_REVIEW_AGE_DAYS",
    "Skill",
    "SkillAuditIssue",
    "SkillAuditReport",
    "audit_skills",
    "get_skill",
    "list_skills",
    "scaffold_core_skills",
    "scaffold_skill",
]
