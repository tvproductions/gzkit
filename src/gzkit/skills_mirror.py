"""Skill mirror parity validation for gzkit.

Validates that mirrored skill directories match their canonical sources.
"""

from pathlib import Path

from gzkit.skills import SkillAuditIssue
from gzkit.skills_audit import (
    KEBAB_CASE_RE,
    SKILL_CAPABILITY_FIELDS,
    SKILL_DEPRECATION_FIELDS,
    SKILL_METADATA_KEYS,
    SKILL_REQUIRED_FIELDS,
    SKILL_TRANSITION_FIELDS,
    _append_audit_issue,
    _read_frontmatter,
    _skill_dirs,
)


def _validate_mirror_skill(
    project_root: Path,
    issues: list[SkillAuditIssue],
    name: str,
    canonical_dir: Path,
    mirror_dir: Path,
) -> None:
    """Validate one mirrored skill against its canonical source."""
    mirrored_fields = list(SKILL_REQUIRED_FIELDS)
    canonical_file = canonical_dir / "SKILL.md"
    mirror_file = mirror_dir / "SKILL.md"
    if not mirror_file.exists():
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-SKILL-FILE-MISSING",
            mirror_dir,
            "Missing mirrored SKILL.md.",
        )
        return

    canonical_frontmatter = _read_frontmatter(canonical_file)
    mirror_frontmatter = _read_frontmatter(mirror_file)
    if not mirror_frontmatter:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-FRONTMATTER-MISSING",
            mirror_file,
            "Missing YAML frontmatter in mirrored SKILL.md.",
        )
        return

    mirror_name = mirror_frontmatter.get("name", "")
    if not mirror_name:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-NAME-MISSING",
            mirror_file,
            "Missing frontmatter field: name in mirrored SKILL.md.",
        )
    elif mirror_name != name:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-NAME-MISMATCH",
            mirror_file,
            (
                f"Mirror frontmatter name '{mirror_name}' "
                f"must match mirrored directory name '{name}'."
            ),
        )

    for field in SKILL_CAPABILITY_FIELDS:
        if field in canonical_frontmatter:
            mirrored_fields.append(field)

    for field in SKILL_METADATA_KEYS:
        if field in canonical_frontmatter:
            mirrored_fields.append(field)

    for field in SKILL_DEPRECATION_FIELDS:
        if field in canonical_frontmatter:
            mirrored_fields.append(field)
    for field in SKILL_TRANSITION_FIELDS:
        if field in canonical_frontmatter:
            mirrored_fields.append(field)

    for field in mirrored_fields:
        if canonical_frontmatter.get(field) == mirror_frontmatter.get(field):
            continue
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-FIELD-DRIFT",
            mirror_file,
            f"Mirror field drift for '{field}' compared to canonical skill '{name}'.",
        )


def validate_mirror_root(
    project_root: Path,
    issues: list[SkillAuditIssue],
    mirror_root: Path,
    canonical_dirs: dict[str, Path],
) -> None:
    """Validate mirror parity for one mirror root."""
    mirror_dirs = _skill_dirs(mirror_root)
    for name, path in sorted(mirror_dirs.items()):
        if KEBAB_CASE_RE.match(name):
            continue
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-DIR-NOT-KEBAB",
            path,
            "Mirrored skill directory name must be kebab-case.",
        )

    canonical_names = set(canonical_dirs.keys())
    mirror_names = set(mirror_dirs.keys())

    for name in sorted(canonical_names - mirror_names):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-DIR-MISSING",
            mirror_root / name,
            "Missing mirrored skill directory.",
        )
    for name in sorted(mirror_names - canonical_names):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-DIR-UNEXPECTED",
            mirror_root / name,
            "Unexpected skill directory not in canonical root.",
            blocking=False,
        )

    shared_names = sorted(canonical_names & mirror_names)
    for name in shared_names:
        _validate_mirror_skill(project_root, issues, name, canonical_dirs[name], mirror_dirs[name])
