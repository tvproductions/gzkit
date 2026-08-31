"""Skill audit and validation for gzkit.

Validates skill naming, metadata, lifecycle fields, and canonical/mirror parity.
"""

import re
from datetime import date, timedelta
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.skill_contract import SKILL_DESCRIPTION_MAX_CHARS, SUPPORTED_SKILL_HARNESSES
from gzkit.skills import SkillAuditIssue, SkillAuditReport, _parse_frontmatter

KEBAB_CASE_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
LIFECYCLE_STATES = {"draft", "active", "deprecated", "retired"}
SKILL_MANPAGE_DIR = Path("docs/user/skills")
SKILL_INDEX_PATH = SKILL_MANPAGE_DIR / "index.md"
DEFAULT_MAX_REVIEW_AGE_DAYS = 90
# Non-blocking runway ahead of the blocking ceiling. Without it the staleness
# gate is a binary cliff: a skill passes at day 90 and fails CI at day 91, so a
# cohort reviewed in one batch tips on one date and presents as a mass CI
# failure instead of a maintenance signal.
DEFAULT_WARN_REVIEW_AGE_DAYS = 75
SKILL_DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
SKILL_IDENTITY_FIELDS = ("name", "description")
SKILL_LIFECYCLE_FIELDS = ("lifecycle_state", "owner", "last_reviewed")
SKILL_REQUIRED_FIELDS = SKILL_IDENTITY_FIELDS + SKILL_LIFECYCLE_FIELDS
SKILL_CAPABILITY_FIELDS = ("compatibility", "invocation", "gz_command")
SKILL_TRANSITION_FIELDS = (
    "lifecycle_transition_from",
    "lifecycle_transition_date",
    "lifecycle_transition_reason",
    "lifecycle_transition_evidence",
)
SKILL_ALLOWED_TRANSITIONS = {
    ("draft", "active"),
    ("active", "deprecated"),
    ("deprecated", "active"),
    ("deprecated", "retired"),
}
SKILL_DEPRECATION_FIELDS = (
    "deprecation_replaced_by",
    "deprecation_migration",
    "deprecation_communication",
    "deprecation_announced_on",
    "retired_on",
)
SKILL_DEPRECATION_REQUIRED_BY_STATE = {
    "deprecated": (
        "deprecation_replaced_by",
        "deprecation_migration",
        "deprecation_communication",
        "deprecation_announced_on",
    ),
    "retired": (
        "deprecation_replaced_by",
        "deprecation_migration",
        "deprecation_communication",
        "deprecation_announced_on",
        "retired_on",
    ),
}
SKILL_DEPRECATION_DATE_FIELDS = ("deprecation_announced_on", "retired_on")
SKILL_METADATA_KEYS = (
    "metadata.skill-version",
    "metadata.govzero-framework-version",
    "metadata.govzero-author",
    "metadata.govzero_layer",
)
SKILL_VERSION_RE = re.compile(r"^\d+\.\d+\.\d+$")
SKILL_FRAMEWORK_VERSION_RE = re.compile(r"^v\d+(?:\.\d+){0,2}$")
SKILL_GOVZERO_LAYERS = {
    "Layer 1 - Evidence Gathering",
    "Layer 2 - Ledger Consumption",
    "Layer 3 - File Sync",
}


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


def _append_audit_issue(
    issues: list[SkillAuditIssue],
    project_root: Path,
    code: str,
    path: Path,
    message: str,
    *,
    blocking: bool = True,
) -> None:
    """Append a skill audit issue with project-relative path."""
    rel = path.relative_to(project_root) if path.is_relative_to(project_root) else path
    severity = "error" if blocking else "warning"
    issues.append(
        SkillAuditIssue(
            severity=severity,
            code=code,
            path=rel.as_posix(),
            message=message,
            blocking=blocking,
        )
    )


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
            "SKA-NAME-MISSING",
            skill_file,
            "Missing frontmatter field: name.",
        )
        return

    if declared_name != skill_name:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-NAME-MISMATCH",
            skill_file,
            f"Frontmatter name '{declared_name}' must match directory name '{skill_name}'.",
        )
        return

    if not KEBAB_CASE_RE.match(declared_name):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-NAME-NOT-KEBAB",
            skill_file,
            "Frontmatter name must be kebab-case.",
        )


def _validate_skill_metadata_fields(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
    max_review_age_days: int,
) -> None:
    """Validate metadata fields for one canonical skill."""
    _validate_required_skill_fields(project_root, issues, skill_file, frontmatter)
    _validate_description_length(project_root, issues, skill_file, frontmatter)
    _validate_lifecycle_field_values(
        project_root, issues, skill_file, frontmatter, max_review_age_days
    )
    _validate_capability_fields(project_root, issues, skill_file, frontmatter)
    _validate_known_metadata_fields(project_root, issues, skill_file, frontmatter)


def _validate_required_skill_fields(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
) -> None:
    """Validate required identity/lifecycle fields."""
    for field in SKILL_REQUIRED_FIELDS:
        if frontmatter.get(field, ""):
            continue
        _append_audit_issue(
            issues,
            project_root,
            "SKA-REQUIRED-FIELD-MISSING",
            skill_file,
            f"Missing frontmatter field: {field}.",
        )


def _validate_description_length(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
) -> None:
    """Validate the strictest supported harness description limit."""
    description = frontmatter.get("description", "")
    if len(description) <= SKILL_DESCRIPTION_MAX_CHARS:
        return
    _append_audit_issue(
        issues,
        project_root,
        "SKA-DESCRIPTION-TOO-LONG",
        skill_file,
        (
            f"Frontmatter description is {len(description)} characters; "
            f"maximum is {SKILL_DESCRIPTION_MAX_CHARS} for "
            f"{SUPPORTED_SKILL_HARNESSES} compatibility."
        ),
    )


def _validate_lifecycle_field_values(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
    max_review_age_days: int,
) -> None:
    """Validate lifecycle enum/date constraints."""
    lifecycle_state = frontmatter.get("lifecycle_state", "")
    _validate_lifecycle_state(project_root, issues, skill_file, lifecycle_state)
    _validate_last_reviewed(project_root, issues, skill_file, frontmatter, max_review_age_days)
    _validate_deprecation_dates(project_root, issues, skill_file, frontmatter)
    _validate_transition_fields(project_root, issues, skill_file, frontmatter, lifecycle_state)
    _validate_deprecation_field_contract(
        project_root, issues, skill_file, frontmatter, lifecycle_state
    )


def _parse_skill_date(value: str) -> date | None:
    """Parse a date constrained to YYYY-MM-DD."""
    if not SKILL_DATE_RE.match(value):
        return None
    try:
        return date.fromisoformat(value)
    except ValueError:
        return None


def _validate_lifecycle_state(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    lifecycle_state: str,
) -> None:
    """Validate lifecycle state enum value."""
    if not lifecycle_state or lifecycle_state in LIFECYCLE_STATES:
        return
    allowed = ", ".join(sorted(LIFECYCLE_STATES))
    _append_audit_issue(
        issues,
        project_root,
        "SKA-LIFECYCLE-STATE-INVALID",
        skill_file,
        f"Invalid lifecycle_state '{lifecycle_state}'. Allowed: {allowed}.",
    )


def _validate_last_reviewed(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
    max_review_age_days: int,
) -> None:
    """Validate last_reviewed format and staleness."""
    last_reviewed = frontmatter.get("last_reviewed", "")
    if not last_reviewed:
        return
    parsed_last_reviewed = _parse_skill_date(last_reviewed)
    if parsed_last_reviewed is None:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-LAST-REVIEWED-INVALID",
            skill_file,
            f"Invalid last_reviewed '{last_reviewed}' (expected YYYY-MM-DD).",
        )
        return
    age = date.today() - parsed_last_reviewed
    if age > timedelta(days=max_review_age_days):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-LAST-REVIEWED-STALE",
            skill_file,
            f"last_reviewed '{last_reviewed}' is older than {max_review_age_days} days.",
        )
        return
    # Clamped so a caller-lowered ceiling can never sit below the warn band.
    warn_after_days = min(DEFAULT_WARN_REVIEW_AGE_DAYS, max_review_age_days)
    if age <= timedelta(days=warn_after_days):
        return
    _append_audit_issue(
        issues,
        project_root,
        "SKA-LAST-REVIEWED-AGING",
        skill_file,
        f"last_reviewed '{last_reviewed}' is {age.days} days old; "
        f"blocks at {max_review_age_days}. Review and re-stamp within "
        f"{max_review_age_days - age.days} days.",
        blocking=False,
    )


def _validate_deprecation_dates(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
) -> None:
    """Validate deprecation/retirement date fields."""
    for field in SKILL_DEPRECATION_DATE_FIELDS:
        value = frontmatter.get(field, "")
        if not value:
            continue
        if _parse_skill_date(value) is not None:
            continue
        code = (
            "SKA-RETIREMENT-DATE-INVALID"
            if field == "retired_on"
            else "SKA-DEPRECATION-DATE-INVALID"
        )
        _append_audit_issue(
            issues,
            project_root,
            code,
            skill_file,
            f"Invalid {field} '{value}' (expected YYYY-MM-DD).",
        )


def _validate_transition_fields(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
    lifecycle_state: str,
) -> None:
    """Validate lifecycle transition contract fields when declared."""
    if not any(field in frontmatter for field in SKILL_TRANSITION_FIELDS):
        return

    missing_transition_fields = [
        field for field in SKILL_TRANSITION_FIELDS if not frontmatter.get(field, "")
    ]
    if missing_transition_fields:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-LIFECYCLE-TRANSITION-FIELDS-INCOMPLETE",
            skill_file,
            (
                "Transition metadata incomplete. Missing: "
                f"{', '.join(sorted(missing_transition_fields))}."
            ),
        )

    transition_from = frontmatter.get("lifecycle_transition_from", "")
    if transition_from and transition_from not in LIFECYCLE_STATES:
        allowed = ", ".join(sorted(LIFECYCLE_STATES))
        _append_audit_issue(
            issues,
            project_root,
            "SKA-LIFECYCLE-TRANSITION-FROM-INVALID",
            skill_file,
            f"Invalid lifecycle_transition_from '{transition_from}'. Allowed: {allowed}.",
        )

    transition_date = frontmatter.get("lifecycle_transition_date", "")
    if transition_date and _parse_skill_date(transition_date) is None:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-LIFECYCLE-TRANSITION-DATE-INVALID",
            skill_file,
            f"Invalid lifecycle_transition_date '{transition_date}' (expected YYYY-MM-DD).",
        )

    _validate_transition_pair(project_root, issues, skill_file, transition_from, lifecycle_state)


def _validate_transition_pair(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    transition_from: str,
    lifecycle_state: str,
) -> None:
    """Validate transition direction and support matrix."""
    if not transition_from or not lifecycle_state:
        return
    if transition_from == lifecycle_state:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-LIFECYCLE-TRANSITION-NOOP",
            skill_file,
            f"Transition from '{transition_from}' to '{lifecycle_state}' is not allowed.",
        )
        return
    if (transition_from, lifecycle_state) in SKILL_ALLOWED_TRANSITIONS:
        return
    _append_audit_issue(
        issues,
        project_root,
        "SKA-LIFECYCLE-TRANSITION-UNSUPPORTED",
        skill_file,
        f"Unsupported lifecycle transition '{transition_from}' -> '{lifecycle_state}'.",
    )


def _validate_deprecation_field_contract(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
    lifecycle_state: str,
) -> None:
    """Validate deprecation field presence/absence by lifecycle state."""
    if lifecycle_state in {"draft", "active"}:
        for field in SKILL_DEPRECATION_FIELDS:
            if field not in frontmatter:
                continue
            _append_audit_issue(
                issues,
                project_root,
                "SKA-DEPRECATION-FIELD-FORBIDDEN",
                skill_file,
                f"Field '{field}' is only allowed for deprecated/retired skills.",
            )

    required_fields = SKILL_DEPRECATION_REQUIRED_BY_STATE.get(lifecycle_state, ())
    for field in required_fields:
        if frontmatter.get(field, ""):
            continue
        _append_audit_issue(
            issues,
            project_root,
            "SKA-DEPRECATION-FIELD-MISSING",
            skill_file,
            f"Missing frontmatter field '{field}' for lifecycle_state '{lifecycle_state}'.",
        )


def _validate_capability_fields(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
) -> None:
    """Validate optional capability fields when present."""
    for field in SKILL_CAPABILITY_FIELDS:
        if field not in frontmatter:
            continue
        if frontmatter[field]:
            continue
        _append_audit_issue(
            issues,
            project_root,
            "SKA-CAPABILITY-FIELD-EMPTY",
            skill_file,
            f"Capability field '{field}' cannot be empty when present.",
        )


def _validate_known_metadata_fields(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_file: Path,
    frontmatter: dict[str, str],
) -> None:
    """Validate known metadata.* keys when present."""
    skill_version = frontmatter.get("metadata.skill-version")
    if skill_version is None:
        # Presence, not just format. `.gzkit/rules/skill-surface-sync.md` #2 makes
        # the marker non-negotiable and #6 couples `last_reviewed` to it; the same
        # rule's conflict-resolution procedure names the version as "the primary
        # signal". Validating format-when-present left that signal absent on any
        # skill that never declared one — a rule asserting a check nothing ran.
        _append_audit_issue(
            issues,
            project_root,
            "SKA-METADATA-SKILL-VERSION-MISSING",
            skill_file,
            "Missing frontmatter field: metadata.skill-version.",
        )
    elif skill_version == "":
        _append_audit_issue(
            issues,
            project_root,
            "SKA-METADATA-SKILL-VERSION-EMPTY",
            skill_file,
            "metadata.skill-version cannot be empty when present.",
        )
    elif skill_version and not SKILL_VERSION_RE.match(skill_version):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-METADATA-SKILL-VERSION-INVALID",
            skill_file,
            f"Invalid metadata.skill-version '{skill_version}' (expected X.Y.Z).",
        )

    framework_version = frontmatter.get("metadata.govzero-framework-version")
    if framework_version == "":
        _append_audit_issue(
            issues,
            project_root,
            "SKA-METADATA-FRAMEWORK-VERSION-EMPTY",
            skill_file,
            "metadata.govzero-framework-version cannot be empty when present.",
        )
    elif framework_version and not SKILL_FRAMEWORK_VERSION_RE.match(framework_version):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-METADATA-FRAMEWORK-VERSION-INVALID",
            skill_file,
            (
                "Invalid metadata.govzero-framework-version "
                f"'{framework_version}' (expected vN or vN.N.N)."
            ),
        )

    govzero_author = frontmatter.get("metadata.govzero-author")
    if govzero_author == "":
        _append_audit_issue(
            issues,
            project_root,
            "SKA-METADATA-AUTHOR-EMPTY",
            skill_file,
            "metadata.govzero-author cannot be empty when present.",
        )

    govzero_layer = frontmatter.get("metadata.govzero_layer")
    if govzero_layer and govzero_layer not in SKILL_GOVZERO_LAYERS:
        allowed = ", ".join(sorted(SKILL_GOVZERO_LAYERS))
        _append_audit_issue(
            issues,
            project_root,
            "SKA-METADATA-LAYER-INVALID",
            skill_file,
            f"Invalid metadata.govzero_layer '{govzero_layer}'. Allowed: {allowed}.",
        )


def _validate_skill_manpage(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_name: str,
    index_content: str,
) -> None:
    """Check that an active skill has a manpage and index entry."""
    manpage_rel = SKILL_MANPAGE_DIR / f"{skill_name}.md"
    manpage_path = project_root / manpage_rel
    if not manpage_path.exists():
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MANPAGE-MISSING",
            manpage_rel,
            f"Missing manpage for active skill `{skill_name}`.",
            blocking=False,
        )
        return

    content = manpage_path.read_text(encoding="utf-8")
    expected = f"# /{skill_name}"
    alt = f"# {skill_name}"
    if not (content.lstrip().startswith(expected) or content.lstrip().startswith(alt)):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MANPAGE-HEADING",
            manpage_path,
            f"Expected heading `{expected}`.",
            blocking=False,
        )

    basename = manpage_rel.name
    if index_content and basename not in index_content:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-MANPAGE-INDEX-MISSING",
            project_root / SKILL_INDEX_PATH,
            f"Missing link to {basename} in skills index.",
            blocking=False,
        )


def _validate_canonical_skill(
    project_root: Path,
    issues: list[SkillAuditIssue],
    skill_name: str,
    skill_dir: Path,
    max_review_age_days: int,
) -> None:
    """Validate one canonical skill directory and SKILL metadata."""
    if not KEBAB_CASE_RE.match(skill_name):
        _append_audit_issue(
            issues,
            project_root,
            "SKA-CANONICAL-DIR-NOT-KEBAB",
            skill_dir,
            "Skill directory name must be kebab-case.",
        )

    skill_file = skill_dir / "SKILL.md"
    if not skill_file.exists():
        _append_audit_issue(
            issues,
            project_root,
            "SKA-CANONICAL-SKILL-FILE-MISSING",
            skill_dir,
            "Missing SKILL.md file.",
        )
        return

    frontmatter = _read_frontmatter(skill_file)
    if not frontmatter:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-CANONICAL-FRONTMATTER-MISSING",
            skill_file,
            "Missing YAML frontmatter.",
        )
        return

    _validate_skill_identity(project_root, issues, skill_name, skill_file, frontmatter)
    _validate_skill_metadata_fields(
        project_root, issues, skill_file, frontmatter, max_review_age_days
    )


def audit_skills(
    project_root: Path,
    config: GzkitConfig | None = None,
    max_review_age_days: int = DEFAULT_MAX_REVIEW_AGE_DAYS,
) -> SkillAuditReport:
    """Audit skill naming, metadata, and canonical/mirror parity."""
    # Late import to avoid circular dependency (skills_mirror imports from skills_audit).
    from gzkit.skills_mirror import validate_mirror_root
    from gzkit.sync_surfaces import has_vendor_declaration

    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")
    if max_review_age_days <= 0:
        msg = "max_review_age_days must be positive."
        raise ValueError(msg)

    # Mirror expectations follow vendor enablement, on the SAME predicate
    # ``sync_all`` uses. The roots were hardcoded, so a project that disabled a
    # vendor still had that vendor's mirror required -- one blocking
    # SKA-MIRROR-DIR-MISSING per canonical skill, against a tree sync had
    # already stopped writing. No sync could clear it (GHI #921).
    vendor_aware = has_vendor_declaration(config)
    mirror_roots = tuple(
        root
        for root, vendor in (
            (config.paths.codex_skills, config.vendors.codex),
            (config.paths.claude_skills, config.vendors.claude),
        )
        if not vendor_aware or vendor.enabled
    )
    checked_roots = [config.paths.skills, *mirror_roots]
    issues: list[SkillAuditIssue] = []

    root_paths = {root: project_root / root for root in checked_roots}
    canonical_root = root_paths[config.paths.skills]
    canonical_dirs = _skill_dirs(canonical_root)

    if not canonical_dirs:
        _append_audit_issue(
            issues,
            project_root,
            "SKA-CANONICAL-ROOT-EMPTY",
            canonical_root,
            "Canonical skills root has no skill directories.",
        )

    checked_skills = len(canonical_dirs)
    for skill_name, skill_dir in sorted(canonical_dirs.items()):
        _validate_canonical_skill(project_root, issues, skill_name, skill_dir, max_review_age_days)

    # Manpage coverage for active skills (only when skills index exists)
    index_file = project_root / SKILL_INDEX_PATH
    if index_file.exists():
        index_content = index_file.read_text(encoding="utf-8")
        for skill_name, skill_dir in sorted(canonical_dirs.items()):
            skill_file = skill_dir / "SKILL.md"
            if not skill_file.exists():
                continue
            fm = _read_frontmatter(skill_file)
            if fm and fm.get("lifecycle_state") == "active":
                _validate_skill_manpage(project_root, issues, skill_name, index_content)

    for root_name in mirror_roots:
        validate_mirror_root(project_root, issues, root_paths[root_name], canonical_dirs)

    issues = sorted(issues, key=lambda issue: (issue.path, issue.code, issue.message))
    valid = not any(issue.blocking for issue in issues)
    return SkillAuditReport(
        valid=valid,
        issues=issues,
        checked_skills=checked_skills,
        checked_roots=checked_roots,
    )
