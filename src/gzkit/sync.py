"""Sync module for regenerating control surfaces from canon.

Control surfaces are agent-specific files generated from governance canon.
`gz sync` regenerates these files to ensure alignment with current state.
"""

import json
from datetime import date
from pathlib import Path
from typing import Any

from gzkit.config import GzkitConfig
from gzkit.templates import render_template


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
    """Scan for existing PRD and ADR files in the design directory.

    Args:
        project_root: Project root directory.
        design_root: Relative path to design directory (e.g., "design" or "docs/design").

    Returns:
        Dictionary with "prds" and "adrs" keys containing lists of found file paths.
    """
    result: dict[str, list[Path]] = {"prds": [], "adrs": []}
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
    import re

    result: dict[str, str] = {"id": file_path.stem}

    try:
        content = file_path.read_text()
    except OSError:
        return result

    lines = content.split("\n")

    for line in lines[:20]:  # Only check first 20 lines for frontmatter
        # Extract canonical ID from header: "# ADR-0.1.0: description" -> "ADR-0.1.0"
        if line.startswith("# ADR-") or line.startswith("# PRD-"):
            # Match "# ADR-X.Y.Z" or "# PRD-NAME-X.Y.Z" before any colon or space
            match = re.match(r"^#\s+((?:ADR|PRD)-[^\s:]+)", line)
            if match:
                result["id"] = match.group(1)

        # Extract parent from "**Parent PRD:** [PRD-NAME](link)" or "**Parent:** [ID](link)"
        if "**Parent" in line and "[" in line:
            # Match markdown link: [TEXT](url)
            match = re.search(r"\[((?:PRD|ADR|OBPI)-[^\]]+)\]", line)
            if match:
                result["parent"] = match.group(1)

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
        },
        "verification": {
            "lint": "uvx ruff check src tests",
            "format": "uvx ruff format --check .",
            "typecheck": "uvx ty check src",
            "test": "uv run -m unittest discover tests",
        },
        "gates": {
            "lite": [1, 2, 5],
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

    return updated
