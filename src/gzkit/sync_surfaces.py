"""Control surface synchronization for gzkit sync.

Handles discovery index generation, Claude/Copilot surface sync,
manifest generation, and the main ``sync_all`` orchestration entry point.

Extracted from sync.py to keep modules under 600 lines.
"""

import json
from datetime import date
from pathlib import Path
from typing import Any

from gzkit.config import GzkitConfig
from gzkit.hooks.claude import generate_claude_settings, setup_claude_hooks
from gzkit.hooks.copilot import generate_copilotignore, setup_copilot_hooks
from gzkit.rules import load_rules, render_rules_to_dir
from gzkit.rules import sync_claude_rules as sync_claude_rules  # noqa: F401
from gzkit.rules import sync_nested_agents_md as sync_nested_agents_md  # noqa: F401
from gzkit.sync_skills import (
    bootstrap_canonical_skills,
    collect_skills_catalog,
    render_skills_catalog,
    sync_skill_mirrors,
)
from gzkit.templates import render_template

# ---------------------------------------------------------------------------
# Helpers shared with sync.py
# ---------------------------------------------------------------------------


def detect_project_name(project_root: Path) -> str:
    """Detect project name from pyproject.toml or directory name.

    Args:
        project_root: Project root directory.

    Returns:
        Detected project name.

    """
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        for line in pyproject.read_text(encoding="utf-8").split("\n"):
            # Parse name = "project-name" or name = 'project-name'
            if line.strip().startswith("name") and "=" in line:
                _, _, value = line.partition("=")
                return value.strip().strip("\"'")

    return project_root.name


def load_local_content(project_root: Path) -> str:
    """Load agents.local.md content if it exists.

    Args:
        project_root: Project root directory.

    Returns:
        Local content or empty string.

    """
    local_path = project_root / "agents.local.md"
    if local_path.exists():
        return local_path.read_text(encoding="utf-8")
    return ""


# ---------------------------------------------------------------------------
# Manifest generation
# ---------------------------------------------------------------------------


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
    from gzkit.sync import detect_project_structure

    if structure is None:
        structure = detect_project_structure(project_root)

    return {
        "schema": "gzkit.manifest.v2",
        "structure": {
            "source_root": structure.get("source_root", config.paths.source_root),
            "tests_root": structure.get("tests_root", config.paths.tests_root),
            "docs_root": structure.get("docs_root", config.paths.docs_root),
            "design_root": structure.get("design_root", config.paths.design_root),
        },
        "artifacts": {
            "prd": {"path": config.paths.prd, "schema": "gzkit.prd.v1"},
            "constitution": {"path": config.paths.constitutions, "schema": "gzkit.constitution.v1"},
            "obpi": {"path": config.paths.adrs, "schema": "gzkit.obpi.v1"},
            "adr": {"path": config.paths.adrs, "schema": "gzkit.adr.v1"},
        },
        "data": {
            "eval_datasets": "data/eval",
            "eval_schema": "data/schemas/eval_dataset.schema.json",
            "baselines": "artifacts/baselines",
            "schemas": "data/schemas",
        },
        "ops": {
            "chores": "config/chores",
            "receipts": "artifacts/receipts",
            "proofs": "artifacts/proofs",
        },
        "thresholds": {
            "coverage_floor": 40.0,
            "eval_regression_delta": 0.05,
            "function_lines": 50,
            "module_lines": 600,
            "class_lines": 300,
        },
        "control_surfaces": {
            "agents_md": config.paths.agents_md,
            "claude_md": config.paths.claude_md,
            "hooks": config.paths.claude_hooks,
            "skills": config.paths.skills,
            "canonical_rules": config.paths.canonical_rules,
            "canonical_schemas": config.paths.canonical_schemas,
            "claude_skills": config.paths.claude_skills,
            "codex_skills": config.paths.codex_skills,
            "copilot_skills": config.paths.copilot_skills,
            "instructions": ".github/instructions",
            "claude_rules": ".claude/rules",
            "personas": config.paths.personas,
        },
        "verification": {
            "lint": "uv run gz lint",
            "format": "uv run gz format",
            "typecheck": "uv run gz typecheck",
            "test": "uv run gz test",
            "docs": "uv run mkdocs build --strict",
            "bdd": "uv run -m behave features/",
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

    with manifest_path.open("w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")


# ---------------------------------------------------------------------------
# Project context for templates
# ---------------------------------------------------------------------------


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
uv run gz lint                       # Lint
uv run gz format                     # Format
uv run gz typecheck                  # Type check
uv run gz test                       # Run tests""".format(module=project_name.replace("-", ""))

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


# ---------------------------------------------------------------------------
# Discovery index
# ---------------------------------------------------------------------------


def _discovery_index_payload(project_root: Path, config: GzkitConfig) -> dict[str, Any]:
    """Build the discovery-index control surface payload."""
    project_name = config.project_name or detect_project_name(project_root)
    return {
        "version": "1.0.0",
        "repository": {
            "name": project_name,
            "paths": {
                "source_root": config.paths.source_root,
                "tests_root": config.paths.tests_root,
                "docs_root": config.paths.docs_root,
                "design_root": config.paths.design_root,
            },
        },
        "governance": {
            "agent_contracts": [config.paths.agents_md, config.paths.claude_md],
            "control_surfaces": {
                "copilot_instructions": config.paths.copilot_instructions,
                "discovery_index": config.paths.discovery_index,
                "skills_canonical": config.paths.skills,
                "skills_mirrors": [
                    config.paths.claude_skills,
                    config.paths.codex_skills,
                    config.paths.copilot_skills,
                ],
            },
        },
        "quality_gates": {
            "lite": [1, 2],
            "heavy": [1, 2, 3, 4, 5],
        },
        "verification_commands": {
            "lint": "uv run gz lint",
            "typecheck": "uv run gz typecheck",
            "test": "uv run gz test",
            "skill_audit": "uv run gz skill audit",
            "check_config_paths": "uv run gz check-config-paths",
            "cli_audit": "uv run gz cli audit",
            "parity_check": "uv run gz parity check",
            "readiness_audit": "uv run gz readiness audit",
            "docs": "uv run mkdocs build --strict",
        },
        "discovery_checklist": {
            "governance": [
                config.paths.discovery_index,
                config.paths.copilot_instructions,
                config.paths.agents_md,
            ],
            "context": ["parent_adr", "related_obpis"],
            "prerequisites": ["required_module", "required_config"],
            "existing_code": ["implementation_pattern", "test_pattern"],
        },
        "completion_checklist": {
            "lite": ["gate1_recorded", "gate2_passed", "quality_passed", "evidence_recorded"],
            "heavy": [
                "gate1_recorded",
                "gate2_passed",
                "gate3_passed",
                "gate4_passed_or_na",
                "gate5_attested",
                "evidence_recorded",
            ],
        },
        "doctrines": {
            "identity_rule": "GovZero = AirlineOps - (AirlineOps product capabilities)",
            "ownership": "Agents own complete execution and defect tracking.",
            "attestation_boundary": "Human attestation is required before final completion.",
        },
        "prohibitions": [
            "Never bypass Gate 5 human attestation.",
            "Never mutate ledger directly; use gz commands.",
            "Never claim completion without recorded evidence.",
        ],
    }


def sync_discovery_index(project_root: Path, config: GzkitConfig) -> None:
    """Generate .github/discovery-index.json control surface."""
    discovery_path = project_root / config.paths.discovery_index
    discovery_path.parent.mkdir(parents=True, exist_ok=True)
    payload = _discovery_index_payload(project_root, config)
    discovery_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Agent contract surfaces
# ---------------------------------------------------------------------------


def sync_agents_md(project_root: Path, config: GzkitConfig) -> None:
    """Generate AGENTS.md from template.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    """
    context = get_project_context(project_root, config)
    content = render_template("agents", **context)

    agents_path = project_root / config.paths.agents_md
    agents_path.write_text(content, encoding="utf-8")


def sync_claude_md(project_root: Path, config: GzkitConfig) -> None:
    """Generate CLAUDE.md from template + agents.local.md.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    """
    context = get_project_context(project_root, config)
    content = render_template("claude", **context)

    claude_path = project_root / config.paths.claude_md
    claude_path.write_text(content, encoding="utf-8")


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
    copilot_path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Claude settings and drift detection
# ---------------------------------------------------------------------------


def sync_claude_settings(project_root: Path, config: GzkitConfig) -> None:
    """Generate .claude/settings.json for hooks.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    """
    settings = generate_claude_settings(config)

    settings_path = project_root / config.paths.claude_settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    with settings_path.open("w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def detect_claude_settings_drift(project_root: Path, config: GzkitConfig) -> list[str]:
    """Compare generated settings against tracked .claude/settings.json.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    Returns:
        List of human-readable drift descriptions (empty = no drift).

    """
    expected = generate_claude_settings(config)

    settings_path = project_root / config.paths.claude_settings
    if not settings_path.exists():
        return [f"Missing {config.paths.claude_settings} (expected by generator)"]

    try:
        actual = json.loads(settings_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as exc:
        return [f"Cannot read {config.paths.claude_settings}: {exc}"]

    diffs: list[str] = []

    # Top-level keys
    expected_keys = set(expected.keys())
    actual_keys = set(actual.keys())
    for key in sorted(expected_keys - actual_keys):
        diffs.append(f"Missing top-level key: {key}")
    for key in sorted(actual_keys - expected_keys):
        diffs.append(f"Extra top-level key: {key}")

    # Hook groups
    for phase in ("PreToolUse", "PostToolUse"):
        expected_hooks = expected.get("hooks", {}).get(phase, [])
        actual_hooks = actual.get("hooks", {}).get(phase, [])

        expected_matchers = [h.get("matcher", "") for h in expected_hooks]
        actual_matchers = [h.get("matcher", "") for h in actual_hooks]

        if expected_matchers != actual_matchers:
            diffs.append(
                f"{phase} matcher order differs: "
                f"expected {expected_matchers}, got {actual_matchers}"
            )
            continue

        for exp_group, act_group in zip(expected_hooks, actual_hooks, strict=True):
            matcher = exp_group.get("matcher", "")
            exp_cmds = [h.get("command", "") for h in exp_group.get("hooks", [])]
            act_cmds = [h.get("command", "") for h in act_group.get("hooks", [])]
            if exp_cmds != act_cmds:
                diffs.append(
                    f"{phase} [{matcher}] hook commands differ: "
                    f"expected {len(exp_cmds)} hooks, got {len(act_cmds)}"
                )

    return diffs


# ---------------------------------------------------------------------------
# Copilot ignore
# ---------------------------------------------------------------------------


def sync_copilotignore(project_root: Path) -> None:
    """Generate .copilotignore for governance artifacts.

    Args:
        project_root: Project root directory.

    """
    copilotignore_path = project_root / ".copilotignore"
    copilotignore_path.write_text(generate_copilotignore(project_root), encoding="utf-8")


# ---------------------------------------------------------------------------
# Vendor-aware helpers
# ---------------------------------------------------------------------------


def _has_manifest_vendors(project_root: Path) -> bool:
    """Check if the on-disk manifest has an explicit vendors section.

    Used to distinguish legacy projects (no vendor gating) from projects that
    have opted into vendor-aware sync via OBPI-0.16.0-03.  The check reads the
    manifest BEFORE ``generate_manifest()`` regenerates it.
    """
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.exists():
        return False
    try:
        data = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return False
    else:
        return "vendors" in data


# ---------------------------------------------------------------------------
# Persona mirror sync
# ---------------------------------------------------------------------------


def sync_persona_mirrors(
    project_root: Path, config: GzkitConfig, *, vendor_aware: bool = False
) -> list[str]:
    """Mirror canonical personas into enabled vendor persona directories.

    Uses vendor adapter functions to translate each persona into the vendor's
    native format.  Falls back to raw canonical markdown for vendors without
    a registered adapter.

    Args:
        project_root: Project root directory.
        config: Project configuration.
        vendor_aware: When True, skip disabled vendors. When False, sync all.

    Returns:
        List of mirrored files written.

    """
    from gzkit.models.persona import discover_persona_files, parse_persona_file
    from gzkit.personas import render_persona_for_vendor

    personas_root = project_root / config.paths.personas
    if not personas_root.exists():
        return []

    persona_files = discover_persona_files(personas_root)
    if not persona_files:
        return []

    vendor_persona_map = {
        "claude": config.vendors.claude.surface_root + "/personas",
        "copilot": config.vendors.copilot.surface_root + "/personas",
        "codex": config.vendors.codex.surface_root + "/personas",
    }

    updated: list[str] = []
    for vendor_name, target_dir_rel in vendor_persona_map.items():
        if vendor_aware:
            vendor_cfg = getattr(config.vendors, vendor_name, None)
            if vendor_cfg is not None and not vendor_cfg.enabled:
                continue

        target_dir = project_root / target_dir_rel
        target_dir.mkdir(parents=True, exist_ok=True)

        for persona_path in persona_files:
            try:
                fm, body = parse_persona_file(persona_path)
            except ValueError:
                continue
            rendered = render_persona_for_vendor(vendor_name, fm, body)
            out_path = target_dir / persona_path.name
            out_path.write_text(rendered, encoding="utf-8")
            updated.append(str(Path(target_dir_rel) / persona_path.name))

    return updated


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


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

    # Check BEFORE manifest regeneration (backward compat: if absent, sync all)
    vendor_aware = _has_manifest_vendors(project_root)

    # Generate manifest
    manifest = generate_manifest(project_root, config)
    write_manifest(project_root, manifest)
    updated.append(".gzkit/manifest.json")

    # Migrate legacy skill layouts into canonical path when needed.
    updated.extend(bootstrap_canonical_skills(project_root, config))

    # Vendor-neutral surfaces (always generated)
    sync_agents_md(project_root, config)
    updated.append(config.paths.agents_md)
    updated.extend(sync_nested_agents_md(project_root, config))

    # Load canonical rules once for all vendor renderers
    canonical_rules_dir = project_root / ".gzkit" / "rules"
    canonical_rules = load_rules(canonical_rules_dir) if canonical_rules_dir.is_dir() else []

    # Claude surfaces
    if not vendor_aware or config.vendors.claude.enabled:
        sync_claude_md(project_root, config)
        updated.append(config.paths.claude_md)

        if canonical_rules:
            rendered = render_rules_to_dir(
                canonical_rules, project_root / config.paths.claude_rules, "claude"
            )
            updated.extend(rendered)
        else:
            updated.extend(sync_claude_rules(project_root, config))

        sync_claude_settings(project_root, config)
        updated.append(config.paths.claude_settings)
        updated.extend(setup_claude_hooks(project_root, config))

    # Copilot surfaces
    if not vendor_aware or config.vendors.copilot.enabled:
        if canonical_rules:
            rendered = render_rules_to_dir(
                canonical_rules,
                project_root / ".github" / "instructions",
                "copilot",
            )
            updated.extend(rendered)
        else:
            sync_copilot_instructions(project_root, config)
            updated.append(config.paths.copilot_instructions)

        sync_discovery_index(project_root, config)
        updated.append(config.paths.discovery_index)

        sync_copilotignore(project_root)
        updated.append(".copilotignore")

        updated.extend(setup_copilot_hooks(project_root, config))

    # Vendor-aware skill mirrors
    mirrored = sync_skill_mirrors(project_root, config, vendor_aware=vendor_aware)
    updated.extend(mirrored)

    # Vendor-aware persona mirrors
    persona_mirrored = sync_persona_mirrors(project_root, config, vendor_aware=vendor_aware)
    updated.extend(persona_mirrored)

    return sorted(set(updated))
