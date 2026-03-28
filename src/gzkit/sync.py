"""Sync module for regenerating control surfaces from canon.

Control surfaces are agent-specific files generated from governance canon.
`gz agent sync control-surfaces` regenerates these files to ensure alignment with current state.

This module provides the public API. Implementation is split across:
- sync_skills.py: skill catalog, mirror management, validation
- sync_surfaces.py: control surface sync, manifest, orchestration
"""

import re
from pathlib import Path

# Re-export rules-based functions (originally imported and re-exported here)
from gzkit.rules import sync_claude_rules as sync_claude_rules  # noqa: F401
from gzkit.rules import sync_nested_agents_md as sync_nested_agents_md  # noqa: F401
from gzkit.sync_skill_validation import (
    collect_canonical_sync_blockers as collect_canonical_sync_blockers,
)

# ---------------------------------------------------------------------------
# Re-exports from sync_skills (skill catalog, validation, mirrors)
# ---------------------------------------------------------------------------
from gzkit.sync_skills import (
    DEFAULT_MAX_REVIEW_AGE_DAYS as DEFAULT_MAX_REVIEW_AGE_DAYS,
)
from gzkit.sync_skills import (
    SKILL_ALLOWED_TRANSITIONS as SKILL_ALLOWED_TRANSITIONS,
)
from gzkit.sync_skills import (
    SKILL_CAPABILITY_FIELDS as SKILL_CAPABILITY_FIELDS,
)
from gzkit.sync_skills import (
    SKILL_CATEGORY_ORDER as SKILL_CATEGORY_ORDER,
)
from gzkit.sync_skills import (
    SKILL_DEPRECATION_DATE_FIELDS as SKILL_DEPRECATION_DATE_FIELDS,
)
from gzkit.sync_skills import (
    SKILL_DEPRECATION_FIELDS as SKILL_DEPRECATION_FIELDS,
)
from gzkit.sync_skills import (
    SKILL_DEPRECATION_REQUIRED_BY_STATE as SKILL_DEPRECATION_REQUIRED_BY_STATE,
)
from gzkit.sync_skills import (
    SKILL_FRAMEWORK_VERSION_RE as SKILL_FRAMEWORK_VERSION_RE,
)
from gzkit.sync_skills import (
    SKILL_GOVZERO_LAYERS as SKILL_GOVZERO_LAYERS,
)
from gzkit.sync_skills import (
    SKILL_IDENTITY_FIELDS as SKILL_IDENTITY_FIELDS,
)
from gzkit.sync_skills import (
    SKILL_LAST_REVIEWED_RE as SKILL_LAST_REVIEWED_RE,
)
from gzkit.sync_skills import (
    SKILL_LIFECYCLE_FIELDS as SKILL_LIFECYCLE_FIELDS,
)
from gzkit.sync_skills import (
    SKILL_LIFECYCLE_STATES as SKILL_LIFECYCLE_STATES,
)
from gzkit.sync_skills import (
    SKILL_METADATA_KEYS as SKILL_METADATA_KEYS,
)
from gzkit.sync_skills import (
    SKILL_NAME_RE as SKILL_NAME_RE,
)
from gzkit.sync_skills import (
    SKILL_REQUIRED_FRONTMATTER_FIELDS as SKILL_REQUIRED_FRONTMATTER_FIELDS,
)
from gzkit.sync_skills import (
    SKILL_TRANSITION_FIELDS as SKILL_TRANSITION_FIELDS,
)
from gzkit.sync_skills import (
    SKILL_VERSION_RE as SKILL_VERSION_RE,
)
from gzkit.sync_skills import (
    bootstrap_canonical_skills as bootstrap_canonical_skills,
)
from gzkit.sync_skills import (
    collect_skills_catalog as collect_skills_catalog,
)
from gzkit.sync_skills import (
    find_stale_mirror_paths as find_stale_mirror_paths,
)
from gzkit.sync_skills import (
    render_skills_catalog as render_skills_catalog,
)
from gzkit.sync_skills import (
    sync_claude_skills as sync_claude_skills,
)
from gzkit.sync_skills import (
    sync_skill_mirror as sync_skill_mirror,
)
from gzkit.sync_skills import (
    sync_skill_mirrors as sync_skill_mirrors,
)

# ---------------------------------------------------------------------------
# Re-exports from sync_surfaces (control surfaces, manifest, orchestration)
# ---------------------------------------------------------------------------
from gzkit.sync_surfaces import (
    detect_claude_settings_drift as detect_claude_settings_drift,
)
from gzkit.sync_surfaces import (
    detect_project_name as detect_project_name,
)
from gzkit.sync_surfaces import (
    generate_manifest as generate_manifest,
)
from gzkit.sync_surfaces import (
    get_project_context as get_project_context,
)
from gzkit.sync_surfaces import (
    load_local_content as load_local_content,
)
from gzkit.sync_surfaces import (
    sync_agents_md as sync_agents_md,
)
from gzkit.sync_surfaces import (
    sync_all as sync_all,
)
from gzkit.sync_surfaces import (
    sync_claude_md as sync_claude_md,
)
from gzkit.sync_surfaces import (
    sync_claude_settings as sync_claude_settings,
)
from gzkit.sync_surfaces import (
    sync_copilot_instructions as sync_copilot_instructions,
)
from gzkit.sync_surfaces import (
    sync_copilotignore as sync_copilotignore,
)
from gzkit.sync_surfaces import (
    sync_discovery_index as sync_discovery_index,
)
from gzkit.sync_surfaces import (
    write_manifest as write_manifest,
)

# ---------------------------------------------------------------------------
# Local constants for artifact parsing
# ---------------------------------------------------------------------------

HEADER_ID_RE = re.compile(r"^#\s+((?:ADR|PRD)-[^\s:]+)")
PARENT_LINK_RE = re.compile(r"\[((?:PRD|ADR|OBPI)-[^\]]+)\]")
ALLOWED_ID_PREFIXES = ("ADR-", "PRD-", "OBPI-")
ALLOWED_LANES = {"lite", "heavy"}


# ---------------------------------------------------------------------------
# Project structure detection
# ---------------------------------------------------------------------------


def detect_project_structure(project_root: Path) -> dict[str, str]:
    """Auto-detect project directory structure.

    Args:
        project_root: Project root directory.

    Returns:
        Dictionary of detected paths.

    """
    structure = {
        "source_root": "src",
        "tests_root": "tests",
        "docs_root": "docs",
        "design_root": "design",
    }

    # Detect source root
    if (project_root / "src").is_dir():
        structure["source_root"] = "src"
    else:
        # Check for {project_name}/ directory (Django-style)
        for item in project_root.iterdir():
            is_candidate = (
                item.is_dir()
                and not item.name.startswith(".")
                and item.name != "tests"
                and (item / "__init__.py").exists()
            )
            if is_candidate:
                structure["source_root"] = item.name
                break

    # Detect tests root
    if (project_root / "tests").is_dir():
        structure["tests_root"] = "tests"
    elif (project_root / "test").is_dir():
        structure["tests_root"] = "test"

    # Detect docs root
    if (project_root / "docs").is_dir():
        structure["docs_root"] = "docs"
    elif (project_root / "documentation").is_dir():
        structure["docs_root"] = "documentation"

    # Detect design root
    if (project_root / "design").is_dir():
        structure["design_root"] = "design"
    elif (project_root / "docs" / "design").is_dir():
        structure["design_root"] = "docs/design"

    return structure


# ---------------------------------------------------------------------------
# Artifact scanning and metadata parsing
# ---------------------------------------------------------------------------


def scan_existing_artifacts(project_root: Path, design_root: str) -> dict[str, list[Path]]:
    """Scan for existing PRD, ADR, and OBPI files in the design directory.

    Args:
        project_root: Project root directory.
        design_root: Relative path to design directory (e.g., "design" or "docs/design").

    Returns:
        Dictionary with "prds", "adrs", and "obpis" keys containing lists of found file paths.

    """
    result: dict[str, list[Path]] = {"prds": [], "adrs": [], "obpis": []}
    design_path = project_root / design_root

    if not design_path.exists():
        return result

    # Scan for PRDs (PRD-*.md pattern)
    prd_dir = design_path / "prd"
    if prd_dir.exists():
        for prd_file in prd_dir.rglob("PRD-*.md"):
            result["prds"].append(prd_file)

    # Scan for ADRs (ADR-*.md pattern, excluding closeout forms)
    adr_dir = design_path / "adr"
    if adr_dir.exists():
        for adr_file in adr_dir.rglob("ADR-*.md"):
            if adr_file.stem == "ADR-CLOSEOUT-FORM":
                continue
            result["adrs"].append(adr_file)

    # Scan for OBPIs (OBPI-*.md pattern) nested under ADR directories.
    obpi_candidates: list[Path] = []
    if adr_dir.exists():
        obpi_candidates.extend(adr_dir.rglob("OBPI-*.md"))

    seen: set[Path] = set()
    for obpi_file in obpi_candidates:
        resolved = obpi_file.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        result["obpis"].append(obpi_file)

    return result


def extract_artifact_id(file_path: Path) -> str:
    """Extract artifact ID from a file path.

    Args:
        file_path: Path to artifact file.

    Returns:
        Artifact ID (e.g., "PRD-GZKIT-1.0.0" from "PRD-GZKIT-1.0.0.md").

    """
    # Remove .md extension and any path components
    return file_path.stem


def _parse_frontmatter(lines: list[str], result: dict[str, str]) -> bool:
    """Parse YAML-style frontmatter and merge known metadata fields."""
    if not lines or lines[0].strip() != "---":
        return False

    has_frontmatter_id = False
    for idx in range(1, len(lines)):
        line = lines[idx].strip()
        if line == "---":
            break
        if ":" not in line:
            continue

        key, _, value = line.partition(":")
        normalized_key = key.strip().lower()
        normalized_value = value.strip().strip("\"'")
        if not normalized_value:
            continue

        if normalized_key == "id" and normalized_value.startswith(ALLOWED_ID_PREFIXES):
            result["id"] = normalized_value
            has_frontmatter_id = True
            continue

        if normalized_key in ("parent", "parent_adr") and normalized_value.startswith(
            ALLOWED_ID_PREFIXES
        ):
            result["parent"] = normalized_value
            continue

        if normalized_key == "lane":
            lane = normalized_value.lower()
            if lane in ALLOWED_LANES:
                result["lane"] = lane

    return has_frontmatter_id


def _parse_header_fallback(
    lines: list[str],
    result: dict[str, str],
    has_frontmatter_id: bool,
) -> None:
    """Parse ID and parent from markdown header/body fallback."""
    for line in lines[:20]:
        if not has_frontmatter_id and (line.startswith("# ADR-") or line.startswith("# PRD-")):
            match = HEADER_ID_RE.match(line)
            if match:
                result["id"] = match.group(1)

        if "parent" in result or "**Parent" not in line or "[" not in line:
            continue

        match = PARENT_LINK_RE.search(line)
        if match:
            result["parent"] = match.group(1)


def parse_artifact_metadata(file_path: Path) -> dict[str, str]:
    """Parse artifact metadata from file content.

    Extracts:
    - id: Canonical ID from header (e.g., "ADR-0.1.0" from "# ADR-0.1.0: description")
    - parent: Parent artifact ID from "**Parent PRD:**" or "**Parent:**" lines

    Args:
        file_path: Path to artifact file.

    Returns:
        Dictionary with "id" and optionally "parent" keys.

    """
    result: dict[str, str] = {"id": file_path.stem}

    try:
        content = file_path.read_text(encoding="utf-8")
    except OSError:
        return result

    lines = content.split("\n")
    has_frontmatter_id = _parse_frontmatter(lines, result)
    _parse_header_fallback(lines, result, has_frontmatter_id)

    return result
