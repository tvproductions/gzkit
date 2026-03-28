"""Skill catalog, mirror management, and validation for gzkit sync.

Extracted from sync.py to keep modules under 600 lines.
Validation helpers live in sync_skills_validation.py.
"""

import re
from pathlib import Path

from gzkit.config import GzkitConfig

# ---------------------------------------------------------------------------
# Skill constants
# ---------------------------------------------------------------------------

SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
SKILL_LAST_REVIEWED_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
DEFAULT_MAX_REVIEW_AGE_DAYS = 90
SKILL_IDENTITY_FIELDS = ("name", "description")
SKILL_LIFECYCLE_FIELDS = ("lifecycle_state", "owner", "last_reviewed")
SKILL_REQUIRED_FRONTMATTER_FIELDS = SKILL_IDENTITY_FIELDS + SKILL_LIFECYCLE_FIELDS
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
SKILL_LIFECYCLE_STATES = {"draft", "active", "deprecated", "retired"}
SKILL_GOVZERO_LAYERS = {
    "Layer 1 - Evidence Gathering",
    "Layer 2 - Ledger Consumption",
    "Layer 3 - File Sync",
}

# Display names for category slugs, in desired render order.
SKILL_CATEGORY_ORDER: list[tuple[str, str]] = [
    ("adr-lifecycle", "ADR Lifecycle"),
    ("adr-operations", "ADR Operations"),
    ("adr-audit", "ADR Audit & Closeout"),
    ("obpi-pipeline", "OBPI Pipeline"),
    ("governance-infrastructure", "Governance Infrastructure"),
    ("agent-operations", "Agent & Repository Operations"),
    ("code-quality", "Code Quality"),
    ("cross-repository", "Cross-Repository"),
]

_CATEGORY_DISPLAY: dict[str, str] = dict(SKILL_CATEGORY_ORDER)
_CATEGORY_SORT: dict[str, int] = {slug: i for i, (slug, _) in enumerate(SKILL_CATEGORY_ORDER)}


# ---------------------------------------------------------------------------
# Skill description / frontmatter extraction
# ---------------------------------------------------------------------------


def _extract_skill_description(skill_file: Path) -> str:
    """Extract a short skill description from SKILL.md.

    Args:
        skill_file: Path to SKILL.md.

    Returns:
        Frontmatter `description`, body fallback, or a default message.

    """
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return "No description provided."

    lines = content.splitlines()
    body_start = 0

    # Prefer explicit frontmatter description when present.
    if lines and lines[0].strip() == "---":
        for idx, raw in enumerate(lines[1:], start=1):
            stripped = raw.strip()
            if stripped == "---":
                body_start = idx + 1
                break
            if not stripped or raw.startswith((" ", "\t")) or ":" not in stripped:
                continue
            key, value = stripped.split(":", 1)
            if key.strip() == "description":
                description = value.strip().strip("\"'")
                if description:
                    return description

    for line in lines[body_start:]:
        stripped = line.strip()
        if not stripped or stripped == "---" or stripped.startswith("#"):
            continue
        # Avoid leaking top-level frontmatter-like keys into rendered catalogs.
        if ":" in stripped and not stripped.startswith("http"):
            key, _, _ = stripped.partition(":")
            if key.isidentifier() and " " not in key:
                continue
        return stripped
    return "No description provided."


def _extract_skill_frontmatter_field(skill_file: Path, field: str) -> str:
    """Extract a named field from SKILL.md frontmatter.

    Args:
        skill_file: Path to SKILL.md.
        field: Frontmatter key to extract.

    Returns:
        Field value or empty string if not found.

    """
    try:
        content = skill_file.read_text(encoding="utf-8")
    except OSError:
        return ""

    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return ""

    for raw in lines[1:]:
        stripped = raw.strip()
        if stripped == "---":
            break
        if not stripped or ":" not in stripped:
            continue
        key, value = stripped.split(":", 1)
        if key.strip() == field:
            return value.strip().strip("\"'")
    return ""


# ---------------------------------------------------------------------------
# Skill catalog collection and rendering
# ---------------------------------------------------------------------------


def collect_skills_catalog(
    project_root: Path,
    skills_dir: str,
) -> list[dict[str, str]]:
    """Collect canonical skill metadata from the configured skills directory.

    Args:
        project_root: Project root directory.
        skills_dir: Relative path to canonical skills directory.

    Returns:
        Sorted list of skill metadata records.

    """
    skills_path = project_root / skills_dir
    if not skills_path.exists():
        return []

    skills: list[dict[str, str]] = []
    for skill_dir in sorted(skills_path.iterdir()):
        skill_file = skill_dir / "SKILL.md"
        if not skill_dir.is_dir() or not skill_file.exists():
            continue

        skills.append(
            {
                "name": skill_dir.name,
                "description": _extract_skill_description(skill_file),
                "category": _extract_skill_frontmatter_field(skill_file, "category"),
                "path": skill_file.relative_to(project_root).as_posix(),
            }
        )

    return skills


def render_skills_catalog(skills: list[dict[str, str]], *, categorized: bool = True) -> str:
    """Render a markdown skill catalog.

    Args:
        skills: Skill metadata records (must include 'name', 'description',
            'category', 'path').
        categorized: If True, group by category with compact name-only format.
            If False, emit flat bullet list with full descriptions (legacy).

    Returns:
        Markdown catalog text.

    """
    if not skills:
        return "- No local skills found. Create one with `gz skill new <name>`."

    if not categorized:
        lines = []
        for skill in skills:
            lines.append(f"- `{skill['name']}`: {skill['description']} (`{skill['path']}`)")
        return "\n".join(lines)

    # Group by category.
    groups: dict[str, list[str]] = {}
    for skill in skills:
        cat = skill.get("category", "").strip() or "uncategorized"
        groups.setdefault(cat, []).append(f"`{skill['name']}`")

    lines: list[str] = []
    # Render known categories in order.
    for slug, display in SKILL_CATEGORY_ORDER:
        if slug in groups:
            lines.append(f"#### {display}")
            lines.append(", ".join(sorted(groups.pop(slug))))
            lines.append("")

    # Render uncategorized last.
    for slug in sorted(groups):
        display = _CATEGORY_DISPLAY.get(slug, "Uncategorized")
        lines.append(f"#### {display}")
        lines.append(", ".join(sorted(groups[slug])))
        lines.append("")

    lines.append("For details on any skill, read its `SKILL.md` in `.gzkit/skills/<skill-name>/`.")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Skill mirror sync
# ---------------------------------------------------------------------------


def sync_skill_mirror(
    project_root: Path,
    source_dir: str,
    target_dir: str,
) -> list[str]:
    """Copy canonical skills into a tool-local mirror directory.

    This is intentionally additive/non-destructive: files are copied/updated,
    but extra files already present in the mirror are preserved.

    Args:
        project_root: Project root directory.
        source_dir: Canonical skills path.
        target_dir: Tool-local mirrored skills path.

    Returns:
        List of mirrored files that were written.

    """
    source_root = project_root / source_dir
    target_root = project_root / target_dir
    if not source_root.exists():
        return []

    updated: list[str] = []
    for source_file in sorted(source_root.rglob("*")):
        if not source_file.is_file():
            continue

        relative_path = source_file.relative_to(source_root)
        target_file = target_root / relative_path
        target_file.parent.mkdir(parents=True, exist_ok=True)

        source_bytes = source_file.read_bytes()
        if target_file.exists() and target_file.read_bytes() == source_bytes:
            continue

        target_file.write_bytes(source_bytes)
        updated.append(target_file.relative_to(project_root).as_posix())

    return updated


# ---------------------------------------------------------------------------
# Skill bootstrap and legacy detection
# ---------------------------------------------------------------------------


def _has_skill_files(path: Path) -> bool:
    """Check whether a directory contains at least one SKILL.md file."""
    if not path.exists():
        return False
    return any(path.rglob("SKILL.md"))


def _legacy_skill_candidate_paths(config: GzkitConfig) -> list[str]:
    """Return ordered legacy skill roots used for bootstrap fallback."""
    return [
        config.paths.copilot_skills,
        ".github/skills",
        config.paths.claude_skills,
        config.paths.codex_skills,
        ".codex/skills",
    ]


def _has_skill_bootstrap_candidate(project_root: Path, config: GzkitConfig) -> bool:
    """Return True when at least one legacy mirror can seed canonical skills."""
    seen: set[str] = set()
    for candidate in _legacy_skill_candidate_paths(config):
        if candidate in seen or candidate == config.paths.skills:
            continue
        seen.add(candidate)
        if _has_skill_files(project_root / candidate):
            return True
    return False


def bootstrap_canonical_skills(project_root: Path, config: GzkitConfig) -> list[str]:
    """Seed canonical skills from legacy mirrors when canonical path is empty.

    This supports migration from older layouts where `.github/skills` was canonical.
    """
    canonical_root = project_root / config.paths.skills
    if _has_skill_files(canonical_root):
        return []

    canonical_root.mkdir(parents=True, exist_ok=True)

    seen: set[str] = set()
    for candidate in _legacy_skill_candidate_paths(config):
        if candidate in seen:
            continue
        seen.add(candidate)
        if candidate == config.paths.skills:
            continue

        candidate_root = project_root / candidate
        if not _has_skill_files(candidate_root):
            continue

        return sync_skill_mirror(project_root, candidate, config.paths.skills)

    return []


# ---------------------------------------------------------------------------
# Skill frontmatter parsing and validation
# ---------------------------------------------------------------------------


def _parse_skill_frontmatter(skill_file: Path) -> dict[str, str]:
    """Parse top-level YAML frontmatter key-values from one SKILL.md."""
    try:
        lines = skill_file.read_text(encoding="utf-8").splitlines()
    except OSError:
        return {}

    if not lines or lines[0].strip() != "---":
        return {}

    frontmatter: dict[str, str] = {}
    active_map_key: str | None = None
    for raw in lines[1:]:
        stripped = raw.strip()
        if stripped == "---":
            return frontmatter
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

    return {}


def _canonical_skill_dirs(project_root: Path, config: GzkitConfig) -> tuple[list[Path], list[str]]:
    """Resolve canonical skill directories or return fail-closed blockers."""
    canonical_root = project_root / config.paths.skills
    if not canonical_root.exists():
        if _has_skill_bootstrap_candidate(project_root, config):
            return [], []
        return [], [f"{config.paths.skills}: canonical skills root does not exist."]

    skill_dirs = sorted(path for path in canonical_root.iterdir() if path.is_dir())
    if skill_dirs:
        return skill_dirs, []
    if _has_skill_bootstrap_candidate(project_root, config):
        return [], []
    return [], [f"{config.paths.skills}: canonical skills root has no skill directories."]


# ---------------------------------------------------------------------------
# Stale mirror detection and multi-vendor mirror sync
# ---------------------------------------------------------------------------


def _mirror_roots(project_root: Path, config: GzkitConfig) -> list[Path]:
    """Return unique mirror roots in deterministic order."""
    roots = [config.paths.codex_skills, config.paths.claude_skills, config.paths.copilot_skills]
    seen: set[str] = set()
    result: list[Path] = []
    for root in roots:
        if root in seen or root == config.paths.skills:
            continue
        seen.add(root)
        result.append(project_root / root)
    return result


def find_stale_mirror_paths(project_root: Path, config: GzkitConfig | None = None) -> list[str]:
    """Find mirror-only files/directories not present in canonical skills root."""
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    canonical_root = project_root / config.paths.skills
    if not canonical_root.exists():
        return []

    stale_paths: list[str] = []
    for mirror_root in _mirror_roots(project_root, config):
        if not mirror_root.exists():
            continue

        entries = sorted(
            (path for path in mirror_root.rglob("*") if path.is_dir() or path.is_file()),
            key=lambda path: (len(path.relative_to(mirror_root).parts), path.as_posix()),
        )
        for mirror_entry in entries:
            rel = mirror_entry.relative_to(mirror_root)
            if rel.name == "AGENTS.md":
                continue
            if (canonical_root / rel).exists():
                continue

            rel_project = mirror_entry.relative_to(project_root).as_posix()
            if any(rel_project.startswith(f"{parent}/") for parent in stale_paths):
                continue
            stale_paths.append(rel_project)

    return sorted(stale_paths)


def sync_skill_mirrors(
    project_root: Path, config: GzkitConfig, *, vendor_aware: bool = False
) -> list[str]:
    """Mirror canonical skills into enabled vendor skill paths.

    Args:
        project_root: Project root directory.
        config: Project configuration.
        vendor_aware: When True, skip disabled vendors. When False, sync all.

    Returns:
        List of mirrored files written.

    """
    vendor_skill_map = {
        "claude": config.paths.claude_skills,
        "copilot": config.paths.copilot_skills,
        "codex": config.paths.codex_skills,
    }

    updated: list[str] = []
    seen: set[str] = set()
    for vendor_name, target in vendor_skill_map.items():
        if target in seen or target == config.paths.skills:
            continue
        if vendor_aware:
            vendor_cfg = getattr(config.vendors, vendor_name, None)
            if vendor_cfg is not None and not vendor_cfg.enabled:
                continue
        seen.add(target)
        updated.extend(sync_skill_mirror(project_root, config.paths.skills, target))
    return updated


def sync_claude_skills(project_root: Path, config: GzkitConfig) -> list[str]:
    """Backward-compatible wrapper for older call sites."""
    return sync_skill_mirror(project_root, config.paths.skills, config.paths.claude_skills)
