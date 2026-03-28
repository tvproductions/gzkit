"""Skill frontmatter validation for canonical sync preflight checks."""

from datetime import date, timedelta
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.sync_skills import (
    DEFAULT_MAX_REVIEW_AGE_DAYS,
    SKILL_ALLOWED_TRANSITIONS,
    SKILL_CAPABILITY_FIELDS,
    SKILL_DEPRECATION_DATE_FIELDS,
    SKILL_DEPRECATION_FIELDS,
    SKILL_DEPRECATION_REQUIRED_BY_STATE,
    SKILL_FRAMEWORK_VERSION_RE,
    SKILL_GOVZERO_LAYERS,
    SKILL_LAST_REVIEWED_RE,
    SKILL_LIFECYCLE_STATES,
    SKILL_NAME_RE,
    SKILL_REQUIRED_FRONTMATTER_FIELDS,
    SKILL_TRANSITION_FIELDS,
    SKILL_VERSION_RE,
    _canonical_skill_dirs,
    _parse_skill_frontmatter,
)


def _validate_skill_frontmatter(
    frontmatter: dict[str, str], rel_file: str, skill_name: str
) -> list[str]:
    """Collect canonical frontmatter validation errors for one skill file."""
    errors: list[str] = []
    errors.extend(_validate_required_frontmatter_fields(frontmatter, rel_file))
    errors.extend(_validate_frontmatter_name(frontmatter, rel_file, skill_name))
    errors.extend(_validate_lifecycle_field_values(frontmatter, rel_file))
    errors.extend(_validate_capability_field_values(frontmatter, rel_file))
    errors.extend(_validate_known_metadata_values(frontmatter, rel_file))
    return errors


def _validate_required_frontmatter_fields(frontmatter: dict[str, str], rel_file: str) -> list[str]:
    """Validate required identity/lifecycle fields."""
    errors: list[str] = []
    for field in SKILL_REQUIRED_FRONTMATTER_FIELDS:
        if frontmatter.get(field, ""):
            continue
        errors.append(f"{rel_file}: missing frontmatter field '{field}'.")
    return errors


def _validate_frontmatter_name(
    frontmatter: dict[str, str], rel_file: str, skill_name: str
) -> list[str]:
    """Validate declared name against directory/name contract."""
    errors: list[str] = []
    declared_name = frontmatter.get("name", "")
    if declared_name and declared_name != skill_name:
        errors.append(
            f"{rel_file}: frontmatter name '{declared_name}' must match directory '{skill_name}'."
        )
    elif declared_name and not SKILL_NAME_RE.match(declared_name):
        errors.append(f"{rel_file}: frontmatter name must be kebab-case.")
    return errors


def _validate_lifecycle_field_values(frontmatter: dict[str, str], rel_file: str) -> list[str]:
    """Validate lifecycle enum and date format fields."""
    errors: list[str] = []
    lifecycle_state = frontmatter.get("lifecycle_state", "")
    _append_invalid_lifecycle_state(errors, rel_file, lifecycle_state)
    _append_last_reviewed_issues(errors, frontmatter, rel_file)
    _append_deprecation_date_issues(errors, frontmatter, rel_file)
    _append_transition_issues(errors, frontmatter, rel_file, lifecycle_state)
    _append_deprecation_field_issues(errors, frontmatter, rel_file, lifecycle_state)
    return errors


def _parse_skill_date(value: str) -> date | None:
    """Parse a date constrained to YYYY-MM-DD."""
    if not SKILL_LAST_REVIEWED_RE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _append_invalid_lifecycle_state(errors: list[str], rel_file: str, lifecycle_state: str) -> None:
    """Append lifecycle-state enum errors."""
    if not lifecycle_state or lifecycle_state in SKILL_LIFECYCLE_STATES:
        return
    allowed = ", ".join(sorted(SKILL_LIFECYCLE_STATES))
    errors.append(f"{rel_file}: invalid lifecycle_state '{lifecycle_state}' (allowed: {allowed}).")


def _append_last_reviewed_issues(
    errors: list[str], frontmatter: dict[str, str], rel_file: str
) -> None:
    """Append last_reviewed validation and staleness issues."""
    last_reviewed = frontmatter.get("last_reviewed", "")
    if not last_reviewed:
        return
    parsed_last_reviewed = _parse_skill_date(last_reviewed)
    if parsed_last_reviewed is None:
        errors.append(f"{rel_file}: invalid last_reviewed '{last_reviewed}' (YYYY-MM-DD).")
        return
    if date.today() - parsed_last_reviewed <= timedelta(days=DEFAULT_MAX_REVIEW_AGE_DAYS):
        return
    errors.append(
        f"{rel_file}: last_reviewed '{last_reviewed}' is older than "
        f"{DEFAULT_MAX_REVIEW_AGE_DAYS} days."
    )


def _append_deprecation_date_issues(
    errors: list[str], frontmatter: dict[str, str], rel_file: str
) -> None:
    """Append invalid deprecation/retirement date issues."""
    for field in SKILL_DEPRECATION_DATE_FIELDS:
        value = frontmatter.get(field, "")
        if not value:
            continue
        if _parse_skill_date(value) is not None:
            continue
        errors.append(f"{rel_file}: invalid {field} '{value}' (YYYY-MM-DD).")


def _append_transition_issues(
    errors: list[str],
    frontmatter: dict[str, str],
    rel_file: str,
    lifecycle_state: str,
) -> None:
    """Append transition metadata issues when transition fields are declared."""
    if not any(field in frontmatter for field in SKILL_TRANSITION_FIELDS):
        return

    missing_transition_fields = [
        field for field in SKILL_TRANSITION_FIELDS if not frontmatter.get(field, "")
    ]
    if missing_transition_fields:
        errors.append(
            f"{rel_file}: transition metadata incomplete. Missing: "
            f"{', '.join(sorted(missing_transition_fields))}."
        )

    transition_from = frontmatter.get("lifecycle_transition_from", "")
    if transition_from and transition_from not in SKILL_LIFECYCLE_STATES:
        allowed = ", ".join(sorted(SKILL_LIFECYCLE_STATES))
        errors.append(
            f"{rel_file}: invalid lifecycle_transition_from '{transition_from}' "
            f"(allowed: {allowed})."
        )

    transition_date = frontmatter.get("lifecycle_transition_date", "")
    if transition_date and _parse_skill_date(transition_date) is None:
        errors.append(
            f"{rel_file}: invalid lifecycle_transition_date '{transition_date}' (YYYY-MM-DD)."
        )

    _append_transition_pair_issue(errors, rel_file, transition_from, lifecycle_state)


def _append_transition_pair_issue(
    errors: list[str], rel_file: str, transition_from: str, lifecycle_state: str
) -> None:
    """Append transition direction support errors."""
    if not transition_from or not lifecycle_state:
        return
    if transition_from == lifecycle_state:
        errors.append(
            f"{rel_file}: transition from '{transition_from}' to '{lifecycle_state}' "
            "is not allowed."
        )
        return
    if (transition_from, lifecycle_state) in SKILL_ALLOWED_TRANSITIONS:
        return
    errors.append(
        f"{rel_file}: unsupported lifecycle transition '{transition_from}' -> '{lifecycle_state}'."
    )


def _append_deprecation_field_issues(
    errors: list[str], frontmatter: dict[str, str], rel_file: str, lifecycle_state: str
) -> None:
    """Append state-based deprecation field presence/absence issues."""
    if lifecycle_state in {"draft", "active"}:
        for field in SKILL_DEPRECATION_FIELDS:
            if field in frontmatter:
                errors.append(
                    f"{rel_file}: field '{field}' is only allowed for deprecated/retired skills."
                )

    for field in SKILL_DEPRECATION_REQUIRED_BY_STATE.get(lifecycle_state, ()):
        if frontmatter.get(field, ""):
            continue
        errors.append(
            f"{rel_file}: missing frontmatter field '{field}' for "
            f"lifecycle_state '{lifecycle_state}'."
        )


def _validate_capability_field_values(frontmatter: dict[str, str], rel_file: str) -> list[str]:
    """Validate optional capability fields when present."""
    errors: list[str] = []
    for field in SKILL_CAPABILITY_FIELDS:
        if field in frontmatter and not frontmatter[field]:
            errors.append(f"{rel_file}: capability field '{field}' cannot be empty when present.")
    return errors


def _validate_known_metadata_values(frontmatter: dict[str, str], rel_file: str) -> list[str]:
    """Validate known metadata.* keys when present."""
    errors: list[str] = []

    skill_version = frontmatter.get("metadata.skill-version")
    if skill_version == "":
        errors.append(f"{rel_file}: metadata.skill-version cannot be empty when present.")
    elif skill_version and not SKILL_VERSION_RE.match(skill_version):
        errors.append(
            f"{rel_file}: invalid metadata.skill-version '{skill_version}' (expected X.Y.Z)."
        )

    framework_version = frontmatter.get("metadata.govzero-framework-version")
    if framework_version == "":
        errors.append(
            f"{rel_file}: metadata.govzero-framework-version cannot be empty when present."
        )
    elif framework_version and not SKILL_FRAMEWORK_VERSION_RE.match(framework_version):
        errors.append(
            f"{rel_file}: invalid metadata.govzero-framework-version '{framework_version}' "
            "(expected vN or vN.N.N)."
        )

    govzero_author = frontmatter.get("metadata.govzero-author")
    if govzero_author == "":
        errors.append(f"{rel_file}: metadata.govzero-author cannot be empty when present.")

    govzero_layer = frontmatter.get("metadata.govzero_layer")
    if govzero_layer and govzero_layer not in SKILL_GOVZERO_LAYERS:
        allowed = ", ".join(sorted(SKILL_GOVZERO_LAYERS))
        errors.append(
            f"{rel_file}: invalid metadata.govzero_layer '{govzero_layer}' (allowed: {allowed})."
        )

    return errors


def _collect_skill_dir_blockers(project_root: Path, skill_dir: Path) -> list[str]:
    """Collect canonical corruption blockers for one skill directory."""
    errors: list[str] = []
    rel_dir = skill_dir.relative_to(project_root).as_posix()
    skill_name = skill_dir.name
    if not SKILL_NAME_RE.match(skill_name):
        errors.append(f"{rel_dir}: skill directory name must be kebab-case.")

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        errors.append(f"{rel_dir}: missing SKILL.md file.")
        return errors

    frontmatter = _parse_skill_frontmatter(skill_file)
    rel_file = skill_file.relative_to(project_root).as_posix()
    if not frontmatter:
        errors.append(f"{rel_file}: missing YAML frontmatter.")
        return errors

    errors.extend(_validate_skill_frontmatter(frontmatter, rel_file, skill_name))
    return errors


def collect_canonical_sync_blockers(project_root: Path, config: GzkitConfig) -> list[str]:
    """Collect fail-closed canonical corruption blockers before mirror propagation."""
    skill_dirs, root_errors = _canonical_skill_dirs(project_root, config)
    if root_errors:
        return root_errors
    if not skill_dirs:
        return []

    errors: list[str] = []
    for skill_dir in skill_dirs:
        errors.extend(_collect_skill_dir_blockers(project_root, skill_dir))

    return sorted(set(errors))
