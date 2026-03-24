"""Config-paths check command implementation."""

import json
from pathlib import Path
from typing import Any

from gzkit.commands.common import console, ensure_initialized, get_project_root, load_manifest
from gzkit.config import GzkitConfig


def _append_path_issue(issues: list[dict[str, str]], path: str, issue: str) -> None:
    """Append a config-path issue row."""
    issues.append({"path": path, "issue": issue})


def _collect_required_path_issues(
    project_root: Path,
    required_dirs: dict[str, str],
    required_files: dict[str, str],
) -> list[dict[str, str]]:
    """Collect required path existence/type issues."""
    issues: list[dict[str, str]] = []

    for label, rel_path in required_dirs.items():
        path = project_root / rel_path
        if not path.exists():
            _append_path_issue(issues, rel_path, f"{label} does not exist")
        elif not path.is_dir():
            _append_path_issue(issues, rel_path, f"{label} is not a directory")

    for label, rel_path in required_files.items():
        path = project_root / rel_path
        if not path.exists():
            _append_path_issue(issues, rel_path, f"{label} does not exist")
        elif not path.is_file():
            _append_path_issue(issues, rel_path, f"{label} is not a file")

    return issues


def _collect_manifest_artifact_issues(
    project_root: Path,
    manifest: dict[str, Any],
    legacy_obpi_path: str,
) -> list[dict[str, str]]:
    """Collect manifest artifact path issues."""
    issues: list[dict[str, str]] = []

    for artifact_name, artifact_cfg in manifest.get("artifacts", {}).items():
        artifact_path = project_root / artifact_cfg.get("path", "")
        if not artifact_path.exists():
            rel = str(artifact_path.relative_to(project_root))
            _append_path_issue(issues, rel, f"manifest.artifacts.{artifact_name}.path missing")

        if artifact_name != "obpi":
            continue

        manifest_obpi_path = artifact_cfg.get("path", "").strip("/").replace("\\", "/")
        if manifest_obpi_path == legacy_obpi_path:
            _append_path_issue(
                issues,
                artifact_cfg.get("path", ""),
                (
                    "manifest.artifacts.obpi.path points to deprecated global "
                    "OBPI path; use ADR root"
                ),
            )

    return issues


def _collect_control_surface_issues(
    project_root: Path,
    manifest: dict[str, Any],
) -> list[dict[str, str]]:
    """Collect manifest control-surface path issues."""
    issues: list[dict[str, str]] = []
    dir_controls = {
        "hooks",
        "skills",
        "canonical_rules",
        "canonical_schemas",
        "claude_skills",
        "codex_skills",
        "copilot_skills",
        "instructions",
        "claude_rules",
    }

    for control_name, control_path in manifest.get("control_surfaces", {}).items():
        path = project_root / control_path
        if not path.exists():
            _append_path_issue(
                issues,
                control_path,
                f"manifest.control_surfaces.{control_name} missing",
            )
            continue

        is_dir_control = control_name in dir_controls
        if is_dir_control and not path.is_dir():
            _append_path_issue(
                issues,
                control_path,
                f"manifest.control_surfaces.{control_name} should be a directory",
            )
        elif not is_dir_control and not path.is_file():
            _append_path_issue(
                issues,
                control_path,
                f"manifest.control_surfaces.{control_name} should be a file",
            )

    return issues


def _collect_obpi_path_contract_issues(
    project_root: Path,
    config: GzkitConfig,
    legacy_obpi_path: str,
) -> list[dict[str, str]]:
    """Collect issues that enforce ADR-local OBPI placement."""
    issues: list[dict[str, str]] = []
    normalized_obpi_path = config.paths.obpis.strip("/").replace("\\", "/")
    if normalized_obpi_path == legacy_obpi_path:
        _append_path_issue(
            issues,
            config.paths.obpis,
            "paths.obpis points to deprecated global OBPI path; use ADR-local OBPIs",
        )

    legacy_obpi_dir = project_root / config.paths.design_root / "obpis"
    if not legacy_obpi_dir.exists():
        return issues

    legacy_obpi_files = sorted(legacy_obpi_dir.glob("OBPI-*.md"))
    if legacy_obpi_files:
        _append_path_issue(
            issues,
            str(legacy_obpi_dir.relative_to(project_root)),
            ("legacy global OBPI directory contains OBPI files; move them under ADR-local obpis/"),
        )

    return issues


def check_config_paths_cmd(as_json: bool) -> None:
    """Validate that configured and manifest-declared paths exist and are coherent."""
    config = ensure_initialized()
    project_root = get_project_root()
    manifest = load_manifest(project_root)

    required_dirs = {
        "paths.prd": config.paths.prd,
        "paths.constitutions": config.paths.constitutions,
        "paths.obpis": config.paths.obpis,
        "paths.adrs": config.paths.adrs,
        "paths.source_root": config.paths.source_root,
        "paths.tests_root": config.paths.tests_root,
        "paths.docs_root": config.paths.docs_root,
        "paths.skills": config.paths.skills,
        "paths.claude_skills": config.paths.claude_skills,
        "paths.codex_skills": config.paths.codex_skills,
        "paths.copilot_skills": config.paths.copilot_skills,
    }
    required_files = {
        "paths.ledger": config.paths.ledger,
        "paths.manifest": config.paths.manifest,
        "paths.agents_md": config.paths.agents_md,
        "paths.claude_md": config.paths.claude_md,
        "paths.copilot_instructions": config.paths.copilot_instructions,
        "paths.discovery_index": config.paths.discovery_index,
    }

    legacy_obpi_path = f"{config.paths.design_root}/obpis"
    issues = _collect_required_path_issues(project_root, required_dirs, required_files)
    issues.extend(_collect_manifest_artifact_issues(project_root, manifest, legacy_obpi_path))
    issues.extend(_collect_control_surface_issues(project_root, manifest))
    issues.extend(_collect_obpi_path_contract_issues(project_root, config, legacy_obpi_path))

    result = {"valid": not issues, "issues": issues}
    if as_json:
        print(json.dumps(result, indent=2))
    elif not issues:
        console.print("[green]Config-path audit passed.[/green]")
    else:
        console.print("[red]Config-path audit failed.[/red]")
        for issue in issues:
            console.print(f"  - {issue['path']}: {issue['issue']}")

    if issues:
        raise SystemExit(1)
