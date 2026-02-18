"""Skills scaffolding and management for gzkit.

Skills are reusable agent instructions that can be triggered contextually.
"""

import re
from dataclasses import dataclass
from datetime import date
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

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LIFECYCLE_STATES = {"draft", "active", "deprecated", "retired"}


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


@dataclass
class SkillAuditIssue:
    """Represents one skill-audit finding."""

    severity: str  # error | warning
    path: str
    message: str

    def to_dict(self) -> dict[str, str]:
        """Convert issue to dictionary."""
        return {
            "severity": self.severity,
            "path": self.path,
            "message": self.message,
        }


@dataclass
class SkillAuditReport:
    """Structured report from skill audit checks."""

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
    end_idx = -1
    for idx, raw in enumerate(lines[1:], start=1):
        if raw.strip() == "---":
            end_idx = idx
            break
        if not raw.strip() or raw.lstrip().startswith("#"):
            continue
        if raw.startswith((" ", "\t")):
            # Ignore nested YAML blocks for this lightweight parser.
            continue
        if ":" not in raw:
            continue
        key, value = raw.split(":", 1)
        frontmatter[key.strip()] = value.strip().strip("\"'")

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


def _skill_dirs(root: Path) -> dict[str, Path]:
    """Return mapping of skill directory name to path for one root."""
    if not root.exists():
        return {}
    return {path.name: path for path in root.iterdir() if path.is_dir()}


def _read_frontmatter(skill_file: Path) -> dict[str, str]:
    """Read frontmatter from a SKILL.md file."""
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return {}
    frontmatter, _ = _parse_frontmatter(content)
    return frontmatter


def _read_description(skill_file: Path) -> str:
    """Read skill description from frontmatter or markdown body."""
    content = skill_file.read_text(encoding="utf-8")
    frontmatter, body = _parse_frontmatter(content)
    return frontmatter.get("description") or _body_description(body)


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
                skills.append(
                    Skill(
                        name=skill_path.name,
                        path=skill_path,
                        description=_read_description(skill_file),
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
    )


def _append_audit_issue(
    issues: list[SkillAuditIssue],
    project_root: Path,
    severity: str,
    path: Path,
    message: str,
) -> None:
    """Append a skill audit issue with project-relative path."""
    rel = path.relative_to(project_root) if path.is_relative_to(project_root) else path
    issues.append(SkillAuditIssue(severity=severity, path=str(rel), message=message))


def _validate_skill_identity(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_name: str,
    skill_file: Path,
    frontmatter: dict[str, str],
) -> None:
    """Validate frontmatter identity fields for one canonical skill."""
    declared_name = frontmatter.get("name", "")
    if not declared_name:
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            "Missing frontmatter field: name.",
        )
        return

    if declared_name != skill_name:
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            f"Frontmatter name '{declared_name}' must match directory name '{skill_name}'.",
        )
        return

    if not KEBAB_CASE_RE.match(declared_name):
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            "Frontmatter name must be kebab-case.",
        )


def _validate_skill_metadata_fields(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
) -> None:
    """Validate metadata fields for one canonical skill."""
    if not frontmatter.get("description", ""):
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            "Missing frontmatter field: description.",
        )

    lifecycle_state = frontmatter.get("lifecycle_state", "")
    if not lifecycle_state:
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            "Missing frontmatter field: lifecycle_state.",
        )
    elif lifecycle_state not in LIFECYCLE_STATES:
        allowed = ", ".join(sorted(LIFECYCLE_STATES))
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            f"Invalid lifecycle_state '{lifecycle_state}'. Allowed: {allowed}.",
        )

    if not frontmatter.get("owner", ""):
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            "Missing frontmatter field: owner.",
        )

    last_reviewed = frontmatter.get("last_reviewed", "")
    if not last_reviewed:
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            "Missing frontmatter field: last_reviewed.",
        )
    elif not re.match(r"^\d{4}-\d{2}-\d{2}$", last_reviewed):
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            f"Invalid last_reviewed '{last_reviewed}' (expected YYYY-MM-DD).",
        )


def _validate_canonical_skill(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_name: str,
    skill_dir: Path,
) -> None:
    """Validate one canonical skill directory and SKILL metadata."""
    if not KEBAB_CASE_RE.match(skill_name):
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_dir,
            "Skill directory name must be kebab-case.",
        )

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_dir,
            "Missing SKILL.md file.",
        )
        return

    frontmatter = _read_frontmatter(skill_file)
    if not frontmatter:
        _append_audit_issue(
            issues,
            project_root,
            "error",
            skill_file,
            "Missing YAML frontmatter.",
        )
        return

    _validate_skill_identity(project_root, issues, skill_name, skill_file, frontmatter)
    _validate_skill_metadata_fields(project_root, issues, skill_file, frontmatter)


def _validate_mirror_root(
    project_root: Path,
    issues: list[SkillAuditIssue],
    mirror_root: Path,
    canonical_dirs: dict[str, Path],
) -> None:
    """Validate mirror parity for one mirror root."""
    mirror_dirs = _skill_dirs(mirror_root)
    canonical_names = set(canonical_dirs.keys())
    mirror_names = set(mirror_dirs.keys())

    for name in sorted(canonical_names - mirror_names):
        _append_audit_issue(
            issues,
            project_root,
            "error",
            mirror_root / name,
            "Missing mirrored skill directory.",
        )
    for name in sorted(mirror_names - canonical_names):
        _append_audit_issue(
            issues,
            project_root,
            "error",
            mirror_root / name,
            "Unexpected skill directory not in canonical root.",
        )

    shared_names = sorted(canonical_names & mirror_names)
    mirrored_fields = ("name", "description", "lifecycle_state", "owner", "last_reviewed")
    for name in shared_names:
        canonical_file = canonical_dirs[name] / "SKILL.md"
        mirror_file = mirror_dirs[name] / "SKILL.md"
        if not mirror_file.exists():
            _append_audit_issue(
                issues,
                project_root,
                "error",
                mirror_dirs[name],
                "Missing mirrored SKILL.md.",
            )
            continue

        canonical_frontmatter = _read_frontmatter(canonical_file)
        mirror_frontmatter = _read_frontmatter(mirror_file)
        for field in mirrored_fields:
            if canonical_frontmatter.get(field) == mirror_frontmatter.get(field):
                continue
            _append_audit_issue(
                issues,
                project_root,
                "error",
                mirror_file,
                f"Mirror field drift for '{field}' compared to canonical skill '{name}'.",
            )


def audit_skills(project_root: Path, config: GzkitConfig | None = None) -> SkillAuditReport:
    """Audit skill naming, metadata, and canonical/mirror parity."""
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    checked_roots = [
        config.paths.skills,
        config.paths.codex_skills,
        config.paths.claude_skills,
        config.paths.copilot_skills,
    ]
    issues: list[SkillAuditIssue] = []

    root_paths = {root: project_root / root for root in checked_roots}
    canonical_root = root_paths[config.paths.skills]
    canonical_dirs = _skill_dirs(canonical_root)

    if not canonical_dirs:
        _append_audit_issue(
            issues,
            project_root,
            "error",
            canonical_root,
            "Canonical skills root has no skill directories.",
        )

    checked_skills = len(canonical_dirs)
    for skill_name, skill_dir in sorted(canonical_dirs.items()):
        _validate_canonical_skill(project_root, issues, skill_name, skill_dir)

    mirror_roots = (
        config.paths.codex_skills,
        config.paths.claude_skills,
        config.paths.copilot_skills,
    )
    for root_name in mirror_roots:
        _validate_mirror_root(project_root, issues, root_paths[root_name], canonical_dirs)

    valid = not any(issue.severity == "error" for issue in issues)
    return SkillAuditReport(
        valid=valid,
        issues=issues,
        checked_skills=checked_skills,
        checked_roots=checked_roots,
    )
