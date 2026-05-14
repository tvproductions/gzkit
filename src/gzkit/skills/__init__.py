"""Skills scaffolding and management for gzkit.

Skills are reusable agent instructions that can be triggered contextually.
"""

import importlib.resources
from collections.abc import Iterator
from datetime import date
from importlib.resources import files
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict

from gzkit.config import GzkitConfig
from gzkit.skill_contract import SKILL_DESCRIPTION_MAX_CHARS, SUPPORTED_SKILL_HARNESSES

_CANONICAL_SKILLS_RESOURCE = "gzkit.skills"


def _classify_skill_file(
    path: Path,
    *,
    project_root: Path | None = None,
) -> Literal["canonical", "package_only", "runtime_state"]:
    """Classify a skills-surface file into one of three content classes.

    canonical: SKILL.md and every other authored skill asset (README.md,
               supporting scripts that ship as part of the skill).
    package_only: ``__init__.py``, ``__pycache__/**``.
    runtime_state: (currently unused for the skills surface; reserved for
                   parity with ``_classify_chore_file``.)

    Signature-compatible with :func:`gzkit.chores._classify_chore_file`. See
    ``.gzkit/rules/skill-surface-sync.md`` § class-classifier.
    """
    path = Path(path)
    name = path.name
    parts = path.parts

    if name == "__init__.py" or "__pycache__" in parts:
        return "package_only"

    if name == "SKILL.md":
        try:
            content = path.read_text(encoding="utf-8")
        except OSError:
            content = ""
        frontmatter, _body = _parse_frontmatter(content)
        if (frontmatter.get("lifecycle_state") or "active") == "retired":
            return "package_only"

    # ``project_root`` accepted for API symmetry with the chores classifier.
    _ = project_root

    return "canonical"


def _iter_canonical_skill_slugs() -> Iterator[Traversable]:
    """Yield each canonical skill-slug directory shipped with the wheel.

    Mirrors :func:`gzkit.chores._iter_canonical_chore_slugs`. Enumerates entries
    under ``importlib.resources.files("gzkit.skills")``, skipping
    ``__pycache__``-style entries and any directory without a ``SKILL.md``
    file.
    """
    root = importlib.resources.files(_CANONICAL_SKILLS_RESOURCE)
    for entry in root.iterdir():
        if not entry.is_dir():
            continue
        if entry.name.startswith("__"):
            continue
        if not entry.joinpath("SKILL.md").is_file():
            continue
        yield entry


# Core skills that are scaffolded by `gz init`.
#
# This set covers the governance workflow sequence that the quickstart
# recommends (init → prd → plan → specify → pipeline → gates → closeout →
# attest) plus the quality skills.  See GHI #173.
CORE_SKILLS = {
    # --- Governance workflow (quickstart sequence) ---
    "gz-prd": {
        "skill_name": "PRD",
        "skill_description": "Guided product requirements declaration with interview logic.",
        "trigger_description": "When defining or revising project-level intent.",
        "behavior_description": "Interview the operator, then generate a PRD artifact.",
        "prerequisites": "Project initialized with gz init",
    },
    "gz-plan": {
        "skill_name": "Plan",
        "skill_description": "Create ADR artifacts with 20+ design forcing-function questions.",
        "trigger_description": "When planning a new feature or architectural change.",
        "behavior_description": "Run design interview, score decomposition, generate ADR.",
        "prerequisites": "PRD exists for the project",
    },
    "gz-status": {
        "skill_name": "Status",
        "skill_description": "Report gate and lifecycle status across ADRs.",
        "trigger_description": "When checking blockers and next governance actions.",
        "behavior_description": "Run `gz status` and present a structured overview.",
        "prerequisites": "Project initialized with gz init",
    },
    "gz-gates": {
        "skill_name": "Gates",
        "skill_description": "Run lane-required gate checks for an ADR.",
        "trigger_description": "After implementation, before closeout.",
        "behavior_description": "Run gate checks and report pass/fail per gate.",
        "prerequisites": "ADR exists with implementation work",
    },
    "gz-constitute": {
        "skill_name": "Constitute",
        "skill_description": "Create governance constitution artifacts.",
        "trigger_description": "When governance constitutions must be created or refreshed.",
        "behavior_description": "Guide constitution creation with structured prompts.",
        "prerequisites": "Project initialized with gz init",
    },
    "gz-implement": {
        "skill_name": "Implement",
        "skill_description": "Run Gate 2 verification and record result events.",
        "trigger_description": "When validating implementation progress for an ADR.",
        "behavior_description": "Run TDD verification, record gate events.",
        "prerequisites": "ADR exists with implementation in progress",
    },
    "gz-obpi-pipeline": {
        "skill_name": "OBPI Pipeline",
        "skill_description": "Execute the staged OBPI pipeline end-to-end.",
        "trigger_description": "When executing an OBPI through the full pipeline.",
        "behavior_description": "Orchestrate plan, implement, verify, ceremony, and sync.",
        "prerequisites": "OBPI brief exists and is authored",
    },
    "gz-adr-closeout-ceremony": {
        "skill_name": "ADR Closeout Ceremony",
        "skill_description": "Execute the full closeout ceremony with human attestation protocol.",
        "trigger_description": "When all OBPIs for an ADR are complete and ready for sign-off.",
        "behavior_description": "Walkthrough, verification, and attestation protocol.",
        "prerequisites": "All linked OBPIs completed with evidence",
    },
    # --- ADR lifecycle ---
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
    # --- Agent & Repository ---
    # git-sync ships its full workflow body as a packaged resource at
    # gzkit/templates/skills/git-sync/SKILL.md, so consumers get the
    # canonical guarded-sync ritual instead of a generic placeholder.
    # The `gz git-sync --skill` flag advertises this path; without this
    # entry the path doesn't exist on consumer projects (GHI #315).
    "git-sync": {},
    # --- Quality (now consolidated into gz-check) ---
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


def _load_packaged_skill_resource(dir_name: str) -> str | None:
    """Return canonical SKILL.md content shipped with the wheel, if present.

    Some core skills (e.g. ``git-sync``) ship their full workflow body as a
    packaged resource at ``gzkit/templates/skills/<slug>/SKILL.md`` so that
    ``gz init`` can deliver the canonical instructions verbatim instead of
    rendering a generic ``Step 1 / Step 2 / Step 3`` placeholder. Returns
    ``None`` when the slug has no packaged resource — caller falls back to
    template rendering. (GHI #315)
    """
    resource = files("gzkit.templates").joinpath("skills", dir_name, "SKILL.md")
    if not resource.is_file():
        return None
    return resource.read_text(encoding="utf-8")


def _validate_scaffold_description(description: str) -> None:
    """Reject skill descriptions that cannot load in all supported harnesses."""
    if len(description) <= SKILL_DESCRIPTION_MAX_CHARS:
        return
    msg = (
        f"Skill description is {len(description)} characters; maximum is "
        f"{SKILL_DESCRIPTION_MAX_CHARS} for {SUPPORTED_SKILL_HARNESSES} compatibility."
    )
    raise ValueError(msg)


def _render_inline_skill_stub(dir_name: str, **kwargs: str) -> str:
    """Return a minimal valid SKILL.md body for custom-skill scaffolding.

    The stub satisfies every required frontmatter field enforced by
    ``gzkit.skills_audit`` (name, description, lifecycle_state, owner,
    last_reviewed) plus the capability fields (compatibility, invocation,
    gz_command) so a freshly-scaffolded skill passes ``gz skill audit``
    on first run. The body is intentionally minimal — operators are
    expected to flesh it out per the skill-authoring conventions.
    """
    skill_name = kwargs.get("skill_name", dir_name.replace("-", " ").title())
    skill_description = kwargs.get("skill_description", "A custom skill for this project.")
    _validate_scaffold_description(skill_description)
    trigger_description = kwargs.get("trigger_description", "When triggered by the user.")
    behavior_description = kwargs.get("behavior_description", "Follow the steps below.")
    prerequisites = kwargs.get("prerequisites", "None")
    return (
        "---\n"
        f"name: {dir_name}\n"
        f"description: {skill_description}\n"
        "compatibility: Project-local skill contract.\n"
        "invocation: Describe the CLI invocation used for this skill.\n"
        "gz_command: describe-command-surface\n"
        "metadata:\n"
        '  skill-version: "1.0.0"\n'
        '  govzero-framework-version: "v6"\n'
        '  govzero-author: "gzkit-governance"\n'
        '  govzero_layer: "Layer 1 - Evidence Gathering"\n'
        "lifecycle_state: active\n"
        "owner: gzkit-governance\n"
        f"last_reviewed: {date.today().isoformat()}\n"
        "model: sonnet\n"
        "---\n"
        "\n"
        "# SKILL.md\n"
        "\n"
        f"## {skill_name}\n"
        "\n"
        f"{skill_description}\n"
        "\n"
        "## Trigger\n"
        "\n"
        f"{trigger_description}\n"
        "\n"
        "## Behavior\n"
        "\n"
        f"{behavior_description}\n"
        "\n"
        "## Prerequisites\n"
        "\n"
        f"{prerequisites}\n"
        "\n"
        "## Steps\n"
        "\n"
        "1. Step 1\n"
        "2. Step 2\n"
        "3. Step 3\n"
    )


def scaffold_skill(
    project_root: Path,
    dir_name: str,
    skills_dir: str,
    **kwargs: str,
) -> Path:
    """Scaffold a new skill from an inlined stub or packaged resource.

    When a packaged SKILL.md exists at ``gzkit.templates/skills/<slug>/``
    (e.g. ``git-sync``), its full canonical content is delivered verbatim.
    Otherwise a minimal stub is rendered inline — the previous
    ``templates/skill.md`` consumer was removed in GHI #453.

    Args:
        project_root: Project root directory.
        dir_name: Directory name for the skill.
        skills_dir: Directory for skills relative to project root.
        **kwargs: Optional stub fields (skill_name, skill_description, etc.).
            Ignored when a packaged resource exists.

    Returns:
        Path to the created SKILL.md file.

    """
    packaged = _load_packaged_skill_resource(dir_name)
    content = packaged if packaged is not None else _render_inline_skill_stub(dir_name, **kwargs)

    skill_path = project_root / skills_dir / dir_name
    skill_path.mkdir(parents=True, exist_ok=True)
    skill_file = skill_path / "SKILL.md"
    skill_file.write_text(content, encoding="utf-8")

    return skill_file


def scaffold_core_skills(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    skip_existing: bool = False,
) -> list[Path]:
    """Scaffold all canonical skills into the project's skills directory.

    Copies canonical ``SKILL.md`` content from the wheel's package surface
    (``importlib.resources.files("gzkit.skills")``) into
    ``<project_root>/<config.paths.skills>/<slug>/SKILL.md``. After
    OBPI-0.0.32-02 (and GHI #453 cleanup) the scaffolder delivers full
    canonical content byte-for-byte rather than rendering a stub.

    Args:
        project_root: Project root directory.
        config: Optional configuration; defaults to loading from
            ``project_root / .gzkit.json``.
        skip_existing: When True, skip any slug whose destination SKILL.md
            already exists on disk. Used by repair mode so upgraded gzkit
            versions deliver new canonical slugs without overwriting
            operator-edited existing ones.

    Returns:
        List of paths to created ``SKILL.md`` files (one per scaffolded
        slug). Empty list when every slug was skipped.

    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    skills_dir = project_root / config.paths.skills
    skills_dir.mkdir(parents=True, exist_ok=True)

    created: list[Path] = []
    for slug_resource in _iter_canonical_skill_slugs():
        slug = slug_resource.name
        target_dir = skills_dir / slug
        target_file = target_dir / "SKILL.md"
        if skip_existing and target_file.exists():
            continue
        skill_src = slug_resource.joinpath("SKILL.md")
        content_bytes = skill_src.read_bytes()
        frontmatter, _ = _parse_frontmatter(content_bytes.decode("utf-8"))
        if (frontmatter.get("lifecycle_state") or "active") == "retired":
            continue
        target_dir.mkdir(parents=True, exist_ok=True)
        target_file.write_bytes(content_bytes)
        created.append(target_file)

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
    "_classify_skill_file",
    "audit_skills",
    "get_skill",
    "list_skills",
    "scaffold_core_skills",
    "scaffold_skill",
]
