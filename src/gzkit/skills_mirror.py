"""Skill mirror parity validation for gzkit.

Validates that mirrored skill directories match their canonical sources.
Parity is enforced at the package level: SKILL.md frontmatter, SKILL.md body,
and non-SKILL.md supporting files must all agree with canonical.
"""

from pathlib import Path

from gzkit.skills import SkillAuditIssue, _parse_frontmatter
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

    _validate_mirror_skill_body(project_root, issues, name, canonical_file, mirror_file)
    _validate_mirror_skill_assets(project_root, issues, name, canonical_dir, mirror_dir)


def _read_skill_body(skill_file: Path) -> str:
    """Return the body of a SKILL.md file after its YAML frontmatter."""
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return ""
    _, body = _parse_frontmatter(content)
    return body.strip()


def _validate_mirror_skill_body(
    project_root: Path,
    issues: list[SkillAuditIssue],
    name: str,
    canonical_file: Path,
    mirror_file: Path,
) -> None:
    """Compare the markdown body of canonical and mirror SKILL.md files."""
    if _read_skill_body(canonical_file) == _read_skill_body(mirror_file):
        return
    _append_audit_issue(
        issues,
        project_root,
        "SKA-MIRROR-BODY-DRIFT",
        mirror_file,
        (
            f"Mirror SKILL.md body drift for canonical skill '{name}'. "
            "Run `uv run gz agent sync control-surfaces` to repair."
        ),
    )


def _collect_package_files(skill_dir: Path) -> dict[str, Path]:
    """Return mapping of rel-posix-path to absolute path for all files below skill_dir.

    Excludes SKILL.md (handled separately) and any file named SKILL.md nested
    inside asset directories to avoid double-counting.
    """
    package: dict[str, Path] = {}
    if not skill_dir.exists():
        return package
    for path in skill_dir.rglob("*"):
        if not path.is_file():
            continue
        if path.name == "SKILL.md" and path.parent == skill_dir:
            continue
        rel = path.relative_to(skill_dir).as_posix()
        package[rel] = path
    return package


def _validate_mirror_skill_assets(
    project_root: Path,
    issues: list[SkillAuditIssue],
    name: str,
    canonical_dir: Path,
    mirror_dir: Path,
) -> None:
    """Ensure every canonical supporting file exists in the mirror with matching bytes."""
    canonical_assets = _collect_package_files(canonical_dir)
    mirror_assets = _collect_package_files(mirror_dir)

    for rel in sorted(set(canonical_assets) - set(mirror_assets)):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-ASSET-MISSING",
            mirror_dir / rel,
            f"Missing mirrored asset '{rel}' for canonical skill '{name}'.",
        )

    for rel in sorted(set(mirror_assets) - set(canonical_assets)):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-ASSET-UNEXPECTED",
            mirror_assets[rel],
            (
                f"Unexpected mirror asset '{rel}' not present in canonical skill '{name}'. "
                "Asset may have been added directly to the mirror."
            ),
            blocking=False,
        )

    for rel in sorted(set(canonical_assets) & set(mirror_assets)):
        try:
            canonical_bytes = canonical_assets[rel].read_bytes()
            mirror_bytes = mirror_assets[rel].read_bytes()
        except OSError:
            continue
        if canonical_bytes == mirror_bytes:
            continue
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MIRROR-ASSET-DRIFT",
            mirror_assets[rel],
            (
                f"Mirror asset '{rel}' drifted from canonical skill '{name}'. "
                "Run `uv run gz agent sync control-surfaces` to repair."
            ),
        )


def validate_mirror_root(
    project_root: Path,
    issues: list[SkillAuditIssue],
    mirror_root: Path,
    canonical_dirs: dict[str, Path],
) -> None:
    """Validate mirror parity for one mirror root.

    Retired skills are excluded from mirror expectations — they should not
    be mirrored and their presence in a mirror is a non-blocking warning.
    """
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

    # Retired skills should not be mirrored — exclude from expected set.
    retired = {
        name
        for name, path in canonical_dirs.items()
        if (fm := _read_frontmatter(path / "SKILL.md")) and fm.get("lifecycle_state") == "retired"
    }
    canonical_names = set(canonical_dirs.keys()) - retired
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
