"""Control surface synchronization for gzkit sync.

Handles discovery index generation, Claude/Copilot surface sync,
manifest generation, and the main ``sync_all`` orchestration entry point.

Extracted from sync.py to keep modules under 600 lines.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from datetime import date
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gzkit.content.models.base import BaseContentModel

from gzkit.config import (
    CODEX_CONFIG_DEFAULT_PATH,
    CODEX_CONFIG_MARKER,
    GzkitConfig,
    resolve_codex_config_path,
)
from gzkit.content.render import render as render_content_model
from gzkit.hooks.claude import generate_claude_settings, merge_settings, setup_claude_hooks
from gzkit.hooks.copilot import generate_copilotignore, setup_copilot_hooks
from gzkit.ledger import Ledger
from gzkit.ledger_events import agent_sync_completed_event
from gzkit.rules import load_rules, render_rules_to_dir
from gzkit.rules import sync_claude_rules as sync_claude_rules  # noqa: F401
from gzkit.rules import sync_nested_agents_md as sync_nested_agents_md  # noqa: F401
from gzkit.sync_skills import (
    bootstrap_canonical_skills,
    collect_skills_catalog,
    render_skills_catalog,
    sync_skill_mirrors,
)
from gzkit.templates import SafeDict, render_surface_template

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
    """Load .gzkit/agents.local.md content if it exists.

    The source lives under ``.gzkit/`` rather than the project root so it
    stays out of Claude Code's memory auto-discovery path. A sibling at
    project root would be loaded twice: once embedded in the rendered
    AGENTS.md and once directly by the consumer (GHI #339).

    Args:
        project_root: Project root directory.

    Returns:
        Local content or empty string.

    """
    local_path = project_root / ".gzkit" / "agents.local.md"
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

    manifest: dict[str, Any] = {
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
            "chores": config.paths.chores,
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
            "codex_config": config.paths.codex_config,
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

    # Preserve authored blocks not represented in the template — currently
    # just `rules.unscoped_allowlist` (ADR-0.0.20). Read-only merge.
    existing_path = project_root / ".gzkit" / "manifest.json"
    if existing_path.exists():
        try:
            existing = json.loads(existing_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            existing = {}
        if isinstance(existing, dict):
            rules_block = existing.get("rules")
            if isinstance(rules_block, dict):
                manifest["rules"] = rules_block

    return manifest


def write_manifest(project_root: Path, manifest: dict[str, Any]) -> None:
    """Write manifest to .gzkit/manifest.json.

    Args:
        project_root: Project root directory.
        manifest: Manifest dictionary.

    """
    manifest_path = project_root / ".gzkit" / "manifest.json"
    manifest_path.parent.mkdir(parents=True, exist_ok=True)

    with manifest_path.open("w", newline="\n") as f:
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
    discovery_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# Agent contract surfaces
# ---------------------------------------------------------------------------


def sync_agents_md(project_root: Path, config: GzkitConfig, consumer: str | None = None) -> None:
    """Generate AGENTS.md by deterministic playback of the committed rendition (OBPI-0.0.37-22).

    Playback path (primary): load the committed rendition for the manifest-declared
    ``AgentContract`` consumer and write its bytes verbatim to AGENTS.md — no LLM, no
    template substitution, no network. Identical committed rendition → byte-identical
    surface on every call. The consumer is RESOLVED, never named here: AGENTS.md is
    the root contract serving every harness, and the literal ``"claude"`` that stood
    in this branch until 2026-08-17 elected one vendor's rendition as the whole
    contract.

    *consumer* is a parameter rather than a value this function reaches for
    (REQ-0.35.0-09-01). Resolving it internally fixes the hardcoded literal but
    leaves the caller unable to name a consumer, which is the same port/adapter
    inversion one layer in — ``.claude/rules/hexagonal-architecture.md`` operative
    rule 4. Defaults to the manifest-declared route, so every existing caller is
    unaffected.

    Bootstrap fallback (no committed rendition yet): render from the AgentContract
    template via the model pipeline (OBPI-0.0.37-14 plumbing). The monolith
    ``render_template`` agents fallback is retired (OBPI-0.0.37-27); the
    template-model pipeline is the sole bootstrap path.
    """
    from gzkit.content.rendition_store import load_rendition, rendition_exists

    agents_path = project_root / config.paths.agents_md

    from gzkit.governance.compose import agent_contract_consumer

    if consumer is None:
        consumer = agent_contract_consumer(project_root)
    if rendition_exists(project_root, "AGENTS.md", consumer):
        agents_path.write_bytes(load_rendition(project_root, "AGENTS.md", consumer))
        return

    # Nothing committed for this consumer. Bootstrap belongs to a ROUTED consumer:
    # it exists so a fresh `gz init` yields a functional AGENTS.md before anything
    # has been attested. A consumer the manifest routes nowhere has nothing to play
    # back AND nothing to bootstrap from, so playback is a no-op — no write, no
    # raise (REQ-0.35.0-09-03). Until 2026-08-21 this branch fell through to the
    # template render, which raises TemplateNotFound on the routing guard in
    # `content.render.pipeline` and left the caller holding an exception for a
    # question that simply has no answer. Found by the Step 4b adversary (receipt
    # arb-step-codexadversary-fc821cac161042538c772cb58d0433a6, 2026-08-18).
    #
    # The predicate is the pipeline's OWN routing authority rather than a second
    # copy: stopping here reaches the same verdict one frame earlier, so the two
    # surfaces cannot disagree about which consumers are routed.
    from gzkit.content.vendors import routes_for as _routes_for  # lazy: import cycle

    if consumer not in _routes_for("AgentContract", project_root=project_root):
        return

    # Bootstrap: no committed rendition yet — render from template via the model
    # pipeline. The monolith render_template agents fallback is retired (OBPI-0.0.37-27):
    # the template-model pipeline is the SOLE bootstrap path. A project-local template
    # takes precedence; otherwise the packaged `agents` template is routed through the
    # same parse -> render path (never emitted as monolith text).
    from gzkit.content.parse import parse as _parse_content  # lazy: avoids compose.py cycle
    from gzkit.templates import load_template as _load_template  # lazy: package template

    context = get_project_context(project_root, config)
    template_path = project_root / ".gzkit" / "templates" / "agents.md"
    if template_path.exists():
        template_text = template_path.read_text(encoding="utf-8")
    else:
        # No project-local template — fall back to the packaged `agents` template,
        # still routed through the model pipeline so fresh `gz init` projects produce a
        # functional AGENTS.md without resurrecting the retired monolith render path.
        template_text = _load_template("agents")

    resolved_text = template_text.format_map(SafeDict(context))
    model = _parse_content(resolved_text, "AgentContract")
    from gzkit.content.vendors import temperature_for as _temperature_for  # lazy

    try:
        temperature = _temperature_for("AgentContract", consumer, project_root=project_root)
    except ValueError:
        # Fresh/consuming projects ship no data/vendor-manifest.json, so the
        # general-control resolver fails closed. Default to full density — render MORE,
        # never silently thin the primary contract (operator directive 2026-06-03).
        temperature = "heavy"
    content_bytes = render_content_model(model, consumer, temperature=temperature)

    agents_path.write_bytes(content_bytes)


def sync_claude_md(project_root: Path, config: GzkitConfig) -> None:
    """Generate CLAUDE.md from template + .gzkit/agents.local.md.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    """
    context = get_project_context(project_root, config)
    content = render_surface_template("claude", **context)

    claude_path = project_root / config.paths.claude_md
    claude_path.write_text(content, encoding="utf-8", newline="\n")


def sync_copilot_instructions(project_root: Path, config: GzkitConfig) -> None:
    """Generate copilot-instructions.md from template + .gzkit/agents.local.md.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    """
    context = get_project_context(project_root, config)
    content = render_surface_template("copilot", **context)

    copilot_path = project_root / config.paths.copilot_instructions
    copilot_path.parent.mkdir(parents=True, exist_ok=True)
    copilot_path.write_text(content, encoding="utf-8", newline="\n")


# ---------------------------------------------------------------------------
# Claude settings and drift detection
# ---------------------------------------------------------------------------


def sync_claude_settings(project_root: Path, config: GzkitConfig) -> None:
    """Generate .claude/settings.json for hooks.

    Args:
        project_root: Project root directory.
        config: Project configuration.

    Merges gzkit-owned hook phases into any existing settings file so
    user-added phases (SessionStart, PreCompact, etc.) and user-added
    top-level keys are preserved across sync. The CAP-13 / GHI #326
    orientation hook is the canonical reason this merge cannot be
    skipped — replacing the file with the bare gzkit subset silently
    disables the AGENTS.md re-read backstop (GHI #329).

    """
    gzkit_settings = generate_claude_settings(config)

    settings_path = project_root / config.paths.claude_settings
    settings_path.parent.mkdir(parents=True, exist_ok=True)

    merged = merge_settings(settings_path, gzkit_settings, config.paths.claude_hooks)

    with settings_path.open("w", newline="\n") as f:
        json.dump(merged, f, indent=2)
        f.write("\n")


def render_codex_config() -> str:
    """Render the project-local Codex execution baseline."""
    return f"""{CODEX_CONFIG_MARKER}
sandbox_mode = "workspace-write"
[features]
hooks = true

[sandbox_workspace_write]
network_access = true
"""


def is_managed_codex_config(content: str | bytes) -> bool:
    """Return whether Codex config content carries gzkit's ownership marker."""
    if isinstance(content, bytes):
        marker = CODEX_CONFIG_MARKER.encode()
        return content.startswith(marker + b"\n") or content.startswith(marker + b"\r\n")
    return content.startswith(f"{CODEX_CONFIG_MARKER}\n") or content.startswith(
        f"{CODEX_CONFIG_MARKER}\r\n"
    )


def sync_codex_config(project_root: Path, config: GzkitConfig) -> str:
    """Create the Codex baseline without replacing operator-owned content."""
    root = project_root.resolve()
    config_path = resolve_codex_config_path(root, config.paths.codex_config)
    config_path.parent.mkdir(parents=True, exist_ok=True)
    rendered = render_codex_config()
    default_path = resolve_codex_config_path(root, CODEX_CONFIG_DEFAULT_PATH)
    if (
        config_path != default_path
        and default_path.is_file()
        and default_path.read_bytes() in (b"", rendered.encode())
    ):
        default_path.unlink()
    if config_path.exists():
        if not config_path.is_file():
            raise ValueError(f"Codex config path is not a regular file: {config_path}")
        existing = config_path.read_bytes()
        if existing:
            return config_path.relative_to(root).as_posix()
    config_path.write_text(rendered, encoding="utf-8", newline="\n")
    return config_path.relative_to(root).as_posix()


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
    for phase in ("PreToolUse", "PostToolUse", "Stop", "UserPromptSubmit"):
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
    copilotignore_path.write_text(
        generate_copilotignore(project_root), encoding="utf-8", newline="\n"
    )


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
# Pkg surface sync (.gzkit/<surface>/ → src/gzkit/<surface>/)
# ---------------------------------------------------------------------------


def _pkg_surface_exists(project_root: Path, surface: str) -> bool:
    """Return True when the pkg surface package directory is already established.

    Only propagate when src/gzkit/<surface>/__init__.py exists — this is the
    signal that the dual-surface layout was set up for this repo (e.g. gzkit's
    own dev tree). Adopter projects do not have src/gzkit/ at all; propagating
    there would silently create a foreign package namespace.
    """
    return (project_root / "src" / "gzkit" / surface / "__init__.py").exists()


def render_content_surface(
    model: BaseContentModel,
    dest_path: Path,
    vendor: str,
    project_root: Path,
    updated: list[str],
    *,
    temperature: str = "heavy",
) -> None:
    """Write rendered bytes for *model* to *dest_path* using the vendor template.

    Replaces _copy_if_changed for per-turn surface files whose source is a
    Pydantic content model rather than an on-disk canonical file (ADR-0.0.34 §2).
    Idempotent: bytes-identical destinations are left untouched.
    """
    rendered = render_content_model(model, vendor, temperature=temperature)
    dest_path.parent.mkdir(parents=True, exist_ok=True)
    if dest_path.exists() and dest_path.read_bytes() == rendered:
        return
    dest_path.write_bytes(rendered)
    updated.append(dest_path.relative_to(project_root).as_posix())


def _write_bytes_if_changed(
    payload: bytes, dest_file: Path, project_root: Path, updated: list[str]
) -> None:
    """Write payload to dest_file when bytes differ; record the write in updated.

    Sibling of ``_copy_if_changed`` for content that is DERIVED rather than
    copied — the chores registry ships filtered, so there is no source file whose
    bytes equal the destination's (GHI #728). Same idempotence contract.
    """
    dest_file.parent.mkdir(parents=True, exist_ok=True)
    if dest_file.exists() and dest_file.read_bytes() == payload:
        return
    dest_file.write_bytes(payload)
    updated.append(dest_file.relative_to(project_root).as_posix())


def _copy_if_changed(
    src_file: Path, dest_file: Path, project_root: Path, updated: list[str]
) -> None:
    """Copy src_file to dest_file when bytes differ; record the write in updated.

    Idempotent: a bytes-identical destination is left untouched and not recorded.
    """
    _write_bytes_if_changed(src_file.read_bytes(), dest_file, project_root, updated)


# Content classes that must never exist under the wheel-shipping package tree.
# `canonical` ships; `package_only` legitimately lives there with no `.gzkit/`
# counterpart (`__init__.py`, `_scaffolder.py`) and MUST survive the prune.
_UNSHIPPABLE_CHORE_CLASSES = frozenset({"runtime_state", "project_local"})


def _prune_unshippable_chores(pkg_chores: Path, project_root: Path, updated: list[str]) -> None:
    """Remove package-side chore files whose class must never ship (GHI #783).

    THE MISSING DIRECTION. ``sync_pkg_surfaces`` walks the CANONICAL side and
    copies ``canonical`` files, so it can only ever add — it cannot remove a
    package-side file it declines to touch. ``gz validate --distribution`` exempts
    ``runtime_state`` from both error classes, so the exemption that stops it
    demanding these files be in the baseline manifest is the same exemption that
    stops it noticing they are on disk in the wheel path. Skip plus exempt compose
    into invisible, and 71 proof files across 29 slugs shipped that way with a
    green validator.

    Keying on the classifier rather than a ``proofs/`` glob is deliberate: the
    class definition is the contract, and a glob would restate one shape of it and
    then drift. It is also what keeps ``package_only`` modules alive — a prune
    written as "delete anything without a canonical counterpart" would take
    ``__init__.py`` with it.

    Empty directories are removed too: an empty ``proofs/`` still ships a
    directory the doctrine forbids.
    """
    from gzkit.chores import _classify_chore_file  # noqa: PLC0415

    if not pkg_chores.is_dir():
        return
    for path in sorted(pkg_chores.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if _classify_chore_file(path, project_root=project_root) in _UNSHIPPABLE_CHORE_CLASSES:
            path.unlink()
            updated.append(path.relative_to(project_root).as_posix())
    # Bottom-up so a directory emptied by the pass above is itself collected.
    for path in sorted(pkg_chores.rglob("*"), reverse=True):
        if path.is_dir() and "__pycache__" not in path.parts and not any(path.iterdir()):
            path.rmdir()


def _sync_classified_flat(
    canonical_dir: Path,
    pkg_dir: Path,
    classifier: Callable[..., str],
    project_root: Path,
    updated: list[str],
    *,
    skip_names: frozenset[str] = frozenset(),
) -> None:
    """Propagate canonical-class files from a flat canonical dir to its pkg copy.

    Used for rules, personas, and templates — surfaces whose canonical tree is a
    single flat directory gated by a per-surface ``_classify_*_file`` helper.
    """
    if not (canonical_dir.exists() and pkg_dir.exists()):
        return
    for src_file in sorted(canonical_dir.iterdir()):
        if not src_file.is_file() or src_file.name in skip_names:
            continue
        if classifier(src_file, project_root=project_root) != "canonical":
            continue
        _copy_if_changed(src_file, pkg_dir / src_file.name, project_root, updated)


def sync_pkg_surfaces(project_root: Path, config: GzkitConfig) -> list[str]:
    """Copy .gzkit/<surface>/ to src/gzkit/<surface>/ for every dual-surface family.

    Only propagates when the pkg surface is already established (its __init__.py
    exists), so adopter projects — which have no src/gzkit/ package — are
    unaffected. Covers skills, rules, personas, templates, and chores (canonical
    class only per _classify_chore_file). Idempotent: skips bytes-identical files.
    Reads ONLY from .gzkit/<surface>/ — never from src/gzkit/ (REQ-0.0.32-08-01).

    Args:
        project_root: Project root directory.
        config: Project configuration.

    Returns:
        List of files written (POSIX-form relative paths).

    """
    updated: list[str] = []
    pkg_root = project_root / "src" / "gzkit"

    # Skills: .gzkit/skills/<slug>/SKILL.md → src/gzkit/skills/<slug>/SKILL.md
    if _pkg_surface_exists(project_root, "skills"):
        from gzkit.sync_skills import _retired_skill_names  # noqa: PLC0415

        canonical_skills = project_root / config.paths.skills
        retired = _retired_skill_names(canonical_skills)
        for skill_dir in sorted(canonical_skills.iterdir()):
            if not skill_dir.is_dir() or skill_dir.name in retired:
                continue
            skill_md = skill_dir / "SKILL.md"
            if not skill_md.exists():
                continue
            _copy_if_changed(
                skill_md, pkg_root / "skills" / skill_dir.name / "SKILL.md", project_root, updated
            )

    # Rules / personas / templates: flat canonical dirs gated by a per-surface classifier
    if _pkg_surface_exists(project_root, "rules"):
        from gzkit.rules import _classify_rule_file  # noqa: PLC0415

        _sync_classified_flat(
            project_root / ".gzkit" / "rules",
            pkg_root / "rules",
            _classify_rule_file,
            project_root,
            updated,
            skip_names=frozenset({"AGENTS.md"}),
        )
    if _pkg_surface_exists(project_root, "personas"):
        from gzkit.personas import _classify_persona_file  # noqa: PLC0415

        _sync_classified_flat(
            project_root / config.paths.personas,
            pkg_root / "personas",
            _classify_persona_file,
            project_root,
            updated,
        )
    if _pkg_surface_exists(project_root, "templates"):
        from gzkit.templates import _classify_template_file  # noqa: PLC0415

        _sync_classified_flat(
            project_root / ".gzkit" / "templates",
            pkg_root / "templates",
            _classify_template_file,
            project_root,
            updated,
        )

    # Chores: canonical-class files only, recursive tree, per _classify_chore_file
    from gzkit.chores import (  # noqa: PLC0415
        _REGISTRY_FILE,
        _classify_chore_file,
        exportable_registry,
    )

    gzkit_chores = project_root / config.paths.chores
    pkg_chores = pkg_root / "chores"
    if gzkit_chores.exists() and pkg_chores.exists():
        for src_file in sorted(gzkit_chores.rglob("*")):
            if not src_file.is_file():
                continue
            if _classify_chore_file(src_file, project_root=project_root) != "canonical":
                continue
            dest_file = pkg_chores / src_file.relative_to(gzkit_chores)
            # The top-level registry ships FILTERED: a project-local slug's files
            # are withheld above, so shipping its entry would advertise a chore
            # the wheel does not carry (GHI #728).
            if src_file.name == _REGISTRY_FILE and src_file.parent == gzkit_chores:
                _write_bytes_if_changed(
                    json.dumps(exportable_registry(src_file), indent=2).encode("utf-8") + b"\n",
                    dest_file,
                    project_root,
                    updated,
                )
                continue
            _copy_if_changed(src_file, dest_file, project_root, updated)

    # Converge, do not only add: remove package-side files whose class must never
    # ship. Runs unconditionally on the package tree — a canonical tree that has
    # gone missing must not strand residue in the wheel (GHI #783).
    _prune_unshippable_chores(pkg_chores, project_root, updated)

    return updated


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
            out_path.write_text(rendered, encoding="utf-8", newline="\n")
            updated.append(str(Path(target_dir_rel) / persona_path.name))

    return updated


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------


def _count_canonical_rules(project_root: Path) -> int:
    """Return the number of canonical rule files under ``.gzkit/rules``."""
    rules_dir = project_root / ".gzkit" / "rules"
    if not rules_dir.is_dir():
        return 0
    return sum(1 for path in rules_dir.glob("*.md") if path.is_file())


def sync_all(
    project_root: Path,
    config: GzkitConfig | None = None,
    *,
    emit_event: bool = True,
) -> list[str]:
    """Regenerate all control surfaces.

    Args:
        project_root: Project root directory.
        config: Optional configuration. Loaded from .gzkit.json if not provided.
        emit_event: When True (default), append an ``agent_sync_completed``
            ledger event after a successful sync (GHI #369). Snapshot-replay
            callers (``plan_sync_all``) pass ``False`` to keep the dry-run
            preview ledger-silent.

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

    updated.append(sync_codex_config(project_root, config))

    # Migrate legacy skill layouts into canonical path when needed.
    updated.extend(bootstrap_canonical_skills(project_root, config))

    # Pkg surfaces: .gzkit/<surface>/ → src/gzkit/<surface>/ (REQ-0.0.32-08-02)
    updated.extend(sync_pkg_surfaces(project_root, config))

    # Vendor-neutral surfaces (AGENTS.md generated before vendor rules so that
    # sync_nested_agents_md reads instruction files already rendered by
    # render_rules_to_dir; caller must ensure this ordering is preserved)
    sync_agents_md(project_root, config)
    updated.append(config.paths.agents_md)

    # Load canonical rules once for all vendor renderers
    canonical_rules_dir = project_root / ".gzkit" / "rules"
    canonical_rules = load_rules(canonical_rules_dir) if canonical_rules_dir.is_dir() else []

    # Claude surfaces
    if not vendor_aware or config.vendors.claude.enabled:
        sync_claude_md(project_root, config)
        updated.append(config.paths.claude_md)

        if canonical_rules:
            rendered = render_rules_to_dir(
                canonical_rules,
                project_root / config.paths.claude_rules,
                "claude",
                project_root=project_root,
            )
            updated.extend(rendered)
        else:
            updated.extend(sync_claude_rules(project_root, config))

        sync_claude_settings(project_root, config)
        updated.append(config.paths.claude_settings)
        updated.extend(setup_claude_hooks(project_root, config))

    # Copilot surfaces — render canonical rules to .github/instructions/ BEFORE
    # sync_nested_agents_md so that subsequent runs see the same instruction
    # files as the first run (idempotency invariant).
    if not vendor_aware or config.vendors.copilot.enabled:
        if canonical_rules:
            rendered = render_rules_to_dir(
                canonical_rules,
                project_root / ".github" / "instructions",
                "copilot",
                project_root=project_root,
            )
            updated.extend(rendered)

        # Copilot reads both the master instructions file AND per-rule files;
        # the master file must regenerate from templates/copilot.md regardless of
        # whether per-rule files are also rendered. (GHI #247)
        sync_copilot_instructions(project_root, config)
        updated.append(config.paths.copilot_instructions)

        sync_discovery_index(project_root, config)
        updated.append(config.paths.discovery_index)

        sync_copilotignore(project_root)
        updated.append(".copilotignore")

        updated.extend(setup_copilot_hooks(project_root, config))

    # Generate nested AGENTS.md files AFTER copilot rule rendering so that
    # both the first and subsequent runs see the same .github/instructions/
    # state, making sync idempotent across repeated invocations.
    updated.extend(sync_nested_agents_md(project_root, config))

    # Vendor-aware skill mirrors
    mirrored = sync_skill_mirrors(project_root, config, vendor_aware=vendor_aware)
    updated.extend(mirrored)

    # Vendor-aware persona mirrors
    persona_mirrored = sync_persona_mirrors(project_root, config, vendor_aware=vendor_aware)
    updated.extend(persona_mirrored)

    # Normalize to forward-slash POSIX form so cross-platform consumers
    # (tests, drift reporters, operator output) see a stable shape. See
    # .gzkit/rules/cross-platform.md: no hard-coded path separators.
    normalized = sorted({Path(entry).as_posix() for entry in updated})

    if emit_event:
        ledger = Ledger(project_root / config.paths.ledger)
        ledger.append(agent_sync_completed_event(normalized, _count_canonical_rules(project_root)))

    return normalized
