"""Sync module for regenerating control surfaces from canon.

Control surfaces are agent-specific files generated from governance canon.
`gz agent sync control-surfaces` regenerates these files to ensure alignment with current state.
"""

import json
import re
from datetime import date
from pathlib import Path
from typing import Any

from gzkit.config import GzkitConfig
from gzkit.templates import render_template

HEADER_ID_RE = re.compile(r"^#\s+((?:ADR|PRD)-[^\s:]+)")
PARENT_LINK_RE = re.compile(r"\[((?:PRD|ADR|OBPI)-[^\]]+)\]")
ALLOWED_ID_PREFIXES = ("ADR-", "PRD-", "OBPI-")
ALLOWED_LANES = {"lite", "heavy"}


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

    # Scan for ADRs (ADR-*.md pattern)
    adr_dir = design_path / "adr"
    if adr_dir.exists():
        for adr_file in adr_dir.rglob("ADR-*.md"):
            result["adrs"].append(adr_file)

    # Scan for OBPIs (OBPI-*.md pattern). OBPI briefs may live in design/obpis
    # or nested under ADR directories (e.g., design/adr/**/obpis).
    obpi_candidates: list[Path] = []
    obpi_dir = design_path / "obpis"
    if obpi_dir.exists():
        obpi_candidates.extend(obpi_dir.rglob("OBPI-*.md"))

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

        if normalized_key == "parent" and normalized_value.startswith(ALLOWED_ID_PREFIXES):
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
        content = file_path.read_text()
    except OSError:
        return result

    lines = content.split("\n")
    has_frontmatter_id = _parse_frontmatter(lines, result)
    _parse_header_fallback(lines, result, has_frontmatter_id)

    return result


def detect_project_name(project_root: Path) -> str:
    """Detect project name from pyproject.toml or directory name.

    Args:
        project_root: Project root directory.

    Returns:
        Detected project name.
    """
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text().split("\n"):
            # Parse name = "project-name" or name = 'project-name'
            if line.strip().startswith("name") and "=" in line:
                _, _, value = line.partition("=")
                value = value.strip().strip("\"'")
                return value

    return project_root.name


def generate_manifest(
    project_root: Path,
    config: GzkitConfig,
    structure: dict[str, str] | None = None,
) -> dict[str, Any]:
    """Generate the governance manifest.

    Args:
        project_root: Project root directory.
        config: Project configuration.
        structure: Optional override for detected structure.

    Returns:
        Manifest dictionary.
    """
    if structure is None:
        structure = detect_project_structure(project_root)

    return {
        "schema": "gzkit.manifest.v1",
        "structure": {
            "source_root": structure.get("source_root", config.paths.source_root),
            "tests_root": structure.get("tests_root", config.paths.tests_root),
            "docs_root": structure.get("docs_root", config.paths.docs_root),
            "design_root": structure.get("design_root", config.paths.design_root),
        },
        "artifacts": {
            "prd": {"path": config.paths.prd, "schema": "gzkit.prd.v1"},
            "constitution": {"path": config.paths.constitutions, "schema": "gzkit.constitution.v1"},
            "obpi": {"path": config.paths.obpis, "schema": "gzkit.obpi.v1"},
            "adr": {"path": config.paths.adrs, "schema": "gzkit.adr.v1"},
        },
        "control_surfaces": {
            "agents_md": config.paths.agents_md,
            "claude_md": config.paths.claude_md,
            "hooks": config.paths.claude_hooks,
            "skills": config.paths.skills,
            "claude_skills": config.paths.claude_skills,
            "codex_skills": config.paths.codex_skills,
            "copilot_skills": config.paths.copilot_skills,
        },
        "verification": {
            "lint": "uvx ruff check src tests",
            "format": "uvx ruff format --check .",
            "typecheck": "uvx ty check src",
            "test": "uv run -m unittest discover tests",
        },
        "gates": {
            "lite": [1, 2],
            "heavy": [1, 2, 3, 4, 5],
        },
    }


def write_manifest(project_root: Path, manifest: dict[str, Any]) -> None:
    """Write manifest to .gzkit/manifest.json.

    Args:
        project_root: Project root directory.
        manifest: Manifest dictionary.
    """
    manifest_path = project_root / ".gzkit" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with open(manifest_path, "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


def load_local_content(project_root: Path) -> str:
    """Load agents.local.md content if it exists.

    Args:
        project_root: Project root directory.

    Returns:
        Local content or empty string.
    """
    local_path = project_root / "agents.local.md"
    if local_path.exists():
        return local_path.read_text()
    return ""


def _extract_skill_description(skill_file: Path) -> str:
    """Extract a short skill description from SKILL.md.

    Args:
        skill_file: Path to SKILL.md.

    Returns:
        First non-empty non-heading line, or a fallback description.
    """
    for line in skill_file.read_text().splitlines():
        stripped = line.strip()
        if stripped and not stripped.startswith("#"):
            return stripped
    return "No description provided."


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
                "path": skill_file.relative_to(project_root).as_posix(),
            }
        )

    return skills


def render_skills_catalog(skills: list[dict[str, str]]) -> str:
    """Render a markdown bullet list for available skills.

    Args:
        skills: Skill metadata records.

    Returns:
        Markdown list text.
    """
    if not skills:
        return "- No local skills found. Create one with `gz skill new <name>`."

    lines = []
    for skill in skills:
        lines.append(f"- `{skill['name']}`: {skill['description']} (`{skill['path']}`)")
    return "\n".join(lines)


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


def _has_skill_files(path: Path) -> bool:
    """Check whether a directory contains at least one SKILL.md file."""
    if not path.exists():
        return False
    return any(path.rglob("SKILL.md"))


def bootstrap_canonical_skills(project_root: Path, config: GzkitConfig) -> list[str]:
    """Seed canonical skills from legacy mirrors when canonical path is empty.

    This supports migration from older layouts where `.github/skills` was canonical.
    """
    canonical_root = project_root / config.paths.skills
    if _has_skill_files(canonical_root):
        return []

    canonical_root.mkdir(parents=True, exist_ok=True)

    candidate_paths = [
        config.paths.copilot_skills,
        ".github/skills",
        config.paths.claude_skills,
        config.paths.codex_skills,
        ".codex/skills",
    ]
    seen: set[str] = set()
    for candidate in candidate_paths:
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


def get_project_context(project_root: Path, config: GzkitConfig) -> dict[str, str]:
    """Build context for template rendering.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    Returns:
        Dictionary of template variables.
    """
    project_name = config.project_name or detect_project_name(project_root)

    # Try to extract info from existing CLAUDE.md or pyproject.toml
    purpose = "A gzkit-governed project"
    tech_stack = "Python 3.13+ with uv, ruff, ty"
    build_commands = """uv sync                              # Hydrate environment
uv run -m {module} --help            # CLI entry point
uvx ruff check src tests             # Lint
uvx ruff format --check .            # Format check
uvx ty check src                     # Type check
uv run -m unittest discover tests    # Run tests""".format(module=project_name.replace("-", ""))

    architecture = "See project documentation"
    coding_conventions = "Ruff defaults: 4-space indent, 100-char lines, double quotes"
    invariants = "See governance documents"

    # Note: Could read existing CLAUDE.md here to preserve context
    # For now, we regenerate from templates

    skills = collect_skills_catalog(project_root, config.paths.skills)
    skills_catalog = render_skills_catalog(skills)

    return {
        "project_name": project_name,
        "project_purpose": purpose,
        "tech_stack": tech_stack,
        "build_commands": build_commands,
        "architecture": architecture,
        "coding_conventions": coding_conventions,
        "invariants": invariants,
        "sync_date": date.today().isoformat(),
        "local_content": load_local_content(project_root),
        "skills_canon_path": config.paths.skills,
        "skills_claude_path": config.paths.claude_skills,
        "skills_codex_path": config.paths.codex_skills,
        "skills_copilot_path": config.paths.copilot_skills,
        "skills_catalog": skills_catalog,
    }


def sync_agents_md(project_root: Path, config: GzkitConfig) -> None:
    """Generate AGENTS.md from template.

    Args:
        project_root: Project root directory.
        config: Project configuration.
    """
    context = get_project_context(project_root, config)
    content = render_template("agents", **context)

    agents_path = project_root / config.paths.agents_md
    agents_path.write_text(content)


def sync_claude_md(project_root: Path, config: GzkitConfig) -> None:
    """Generate CLAUDE.md from template + agents.local.md.

    Args:
        project_root: Project root directory.
        config: Project configuration.
    """
    context = get_project_context(project_root, config)
    content = render_template("claude", **context)

    claude_path = project_root / config.paths.claude_md
    claude_path.write_text(content)


def sync_copilot_instructions(project_root: Path, config: GzkitConfig) -> None:
    """Generate copilot-instructions.md from template + agents.local.md.

    Args:
        project_root: Project root directory.
        config: Project configuration.
    """
    context = get_project_context(project_root, config)
    content = render_template("copilot", **context)

    copilot_path = project_root / config.paths.copilot_instructions
    copilot_path.parent.mkdir(parents=True, exist_ok=True)
    copilot_path.write_text(content)


def sync_claude_settings(project_root: Path, config: GzkitConfig) -> None:
    """Generate .claude/settings.json for hooks.

    Args:
        project_root: Project root directory.
        config: Project configuration.
    """
    hook_cmd = f"uv run python {config.paths.claude_hooks}/ledger-writer.py"
    settings = {
        "hooks": {
            "PostToolUse": [
                {
                    "matcher": "Edit|Write",
                    "hooks": [{"type": "command", "command": hook_cmd}],
                }
            ]
        }
    }

    settings_path = project_root / config.paths.claude_settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with open(settings_path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def sync_copilotignore(project_root: Path) -> None:
    """Generate .copilotignore for governance artifacts.

    Args:
        project_root: Project root directory.
    """
    ignore_content = """# gzkit governance artifacts
.gzkit/
design/
AGENTS.md
"""

    copilotignore_path = project_root / ".copilotignore"
    copilotignore_path.write_text(ignore_content)


def sync_skill_mirrors(project_root: Path, config: GzkitConfig) -> list[str]:
    """Mirror canonical skills into all tool-local mirror paths.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    Returns:
        List of mirrored files written.
    """
    updated: list[str] = []
    targets = [config.paths.claude_skills, config.paths.codex_skills, config.paths.copilot_skills]
    seen: set[str] = set()
    for target in targets:
        if target in seen or target == config.paths.skills:
            continue
        seen.add(target)
        updated.extend(sync_skill_mirror(project_root, config.paths.skills, target))
    return updated


def sync_claude_skills(project_root: Path, config: GzkitConfig) -> list[str]:
    """Backward-compatible wrapper for older call sites."""
    return sync_skill_mirror(project_root, config.paths.skills, config.paths.claude_skills)


def sync_all(project_root: Path, config: GzkitConfig | None = None) -> list[str]:
    """Regenerate all control surfaces.

    Args:
        project_root: Project root directory.
        config: Optional configuration. Loaded from .gzkit.json if not provided.

    Returns:
        List of files that were updated.
    """
    if config is None:
        config = GzkitConfig.load(project_root / ".gzkit.json")

    updated: list[str] = []

    # Generate manifest
    manifest = generate_manifest(project_root, config)
    write_manifest(project_root, manifest)
    updated.append(".gzkit/manifest.json")

    # Migrate legacy skill layouts into canonical path when needed.
    updated.extend(bootstrap_canonical_skills(project_root, config))

    # Generate control surfaces
    sync_agents_md(project_root, config)
    updated.append(config.paths.agents_md)

    sync_claude_md(project_root, config)
    updated.append(config.paths.claude_md)

    sync_copilot_instructions(project_root, config)
    updated.append(config.paths.copilot_instructions)

    sync_claude_settings(project_root, config)
    updated.append(config.paths.claude_settings)

    sync_copilotignore(project_root)
    updated.append(".copilotignore")

    mirrored = sync_skill_mirrors(project_root, config)
    updated.extend(mirrored)

    return updated
