"""Config-paths check command implementation.

@covers OBPI-0.0.7-05-lint-rule-and-check-expansion
"""

import ast
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
            rel = artifact_path.relative_to(project_root).as_posix()
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
        "claude_rules",
        "personas",
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
            legacy_obpi_dir.relative_to(project_root).as_posix(),
            ("legacy global OBPI directory contains OBPI files; move them under ADR-local obpis/"),
        )

    return issues


def _flatten_manifest_paths(manifest: dict[str, Any]) -> set[str]:
    """Extract all path-like values from manifest sections.

    Returns a set of normalized path strings that represent known manifest
    mappings. Used to determine whether a source-code path literal is
    already governed by the manifest.
    """
    path_sections = ("structure", "data", "ops", "control_surfaces")
    paths: set[str] = set()

    for section in path_sections:
        section_data = manifest.get(section, {})
        if not isinstance(section_data, dict):
            continue
        for value in section_data.values():
            if isinstance(value, str) and "/" in value:
                paths.add(value.strip("/").replace("\\", "/"))
            elif isinstance(value, str) and value:
                paths.add(value)

    for artifact_cfg in manifest.get("artifacts", {}).values():
        if isinstance(artifact_cfg, dict):
            path_val = artifact_cfg.get("path", "")
            if path_val:
                paths.add(path_val.strip("/").replace("\\", "/"))

    # Derive parent directories so that e.g. .gzkit/manifest.json is
    # covered when .gzkit/skills is in the manifest.
    derived: set[str] = set()
    for p in paths:
        parts = p.split("/")
        for i in range(1, len(parts)):
            derived.add("/".join(parts[:i]))
    paths.update(derived)

    return paths


def _flatten_config_paths(config: GzkitConfig) -> set[str]:
    """Return the path values ``GzkitConfig.paths`` declares.

    Deliberately EXACT: unlike :func:`_flatten_manifest_paths` this derives no
    parent directories. Deriving them would add ``.github`` from
    ``.github/discovery-index.json`` and, through the prefix rule in
    :func:`_is_path_covered_by_manifest`, silently exempt every ``.github/**``
    literal in the tree -- the opposite of what this audit exists to do.
    Pinned by ``TestPathConfigDeclaredDefaults.test_undeclared_sibling_still_flagged``.
    """
    return {
        value.strip("/").replace("\\", "/")
        for value in config.paths.model_dump().values()
        if isinstance(value, str) and value
    }


def _is_path_covered_by_manifest(literal: str, manifest_paths: set[str]) -> bool:
    """Check if a path literal is covered by any manifest entry.

    A literal is covered if it exactly matches, is a prefix of, or is a
    suffix of a known manifest path.
    """
    normalized = literal.strip("/").replace("\\", "/")
    for mp in manifest_paths:
        if normalized == mp:
            return True
        if normalized.startswith(mp + "/") or mp.startswith(normalized + "/"):
            return True
    return False


_PATH_SEGMENT_RE = (
    r"^(?:src|tests|docs|data|config|ops|artifacts|\.gzkit|\.claude|\.github|\.agents)"
    r"(?:/[\w.\-]+)+/?$"
)

# Path-shaped string literals that are NOT config paths and so cannot be
# "mapped" to the manifest: a forbidden-pattern detector and a template
# placeholder example. Mapping them would assert they name real config
# locations, which they do not — exemption is the correct disposition.
_EXEMPT_PATH_LITERALS: frozenset[str] = frozenset(
    {
        # chores-layout audit's forbidden legacy-root detector
        # (gzkit.governance.trust_audits.chores; ADR-0.0.21 Decision #9)
        "ops/chores/",
        # OBPI scaffold placeholder example in TEMPLATE_SCAFFOLD_MARKERS
        # (gzkit.hooks.obpi) — a Discovery-Checklist stub, not a real file
        "config/file.json",
    }
)


#: The exact module-level constant name a module uses to declare which of its
#: path literals are audit SUBJECTS rather than resource paths (GHI #938).
#:
#: The name is EXACT so that ``grep -rn _AUDIT_SUBJECT_LITERALS src/`` is a
#: COMPLETE exemption census. Crediting any tuple of path-shaped strings would
#: make the census unbounded and let ordinary constants silently weaken the
#: audit; pinned by
#: ``TestModuleDeclaredAuditSubjects.test_a_differently_named_constant_grants_nothing``.
_AUDIT_SUBJECT_DECLARATION = "_AUDIT_SUBJECT_LITERALS"


def _collect_declared_audit_subjects(tree: ast.Module) -> set[str]:
    """Return the path literals *tree*'s module declares as audit subjects.

    A literal naming the population a control audits, a vendor-mirror roster
    iterated to detect a retired layout, or a sentinel for a directory that
    must NOT exist is the audit's own SUBJECT. There is no config field it
    could be sourced from: a config field would describe where that surface
    lives, which is the very thing the check asserts about.

    Only MODULE-LEVEL assignments are read, and only the exact name
    :data:`_AUDIT_SUBJECT_DECLARATION`. Scoping is the safety property -- the
    caller applies this per-file, so a declaration credits only the module
    that makes it. A declaration that leaked across modules would be a central
    roster with worse ergonomics, and the census grep would name the wrong
    owner.

    The value's shape is deliberately unconstrained (tuple, list, set,
    ``frozenset(...)``): every string constant inside it is taken, so the
    declaration reads naturally with a per-entry comment beside each literal.
    """
    declared: set[str] = set()
    for node in tree.body:
        targets: list[ast.expr] = []
        if isinstance(node, ast.Assign):
            targets = list(node.targets)
        elif isinstance(node, ast.AnnAssign):
            targets = [node.target]
        else:
            continue
        if not any(isinstance(t, ast.Name) and t.id == _AUDIT_SUBJECT_DECLARATION for t in targets):
            continue
        if node.value is None:
            continue
        for inner in ast.walk(node.value):
            if isinstance(inner, ast.Constant) and isinstance(inner.value, str):
                declared.add(inner.value.strip().strip("/").replace("\\", "/"))
    return declared


def _collect_source_path_literal_issues(
    project_root: Path,
    manifest: dict[str, Any],
    config: GzkitConfig,
) -> list[dict[str, str]]:
    """Scan source for path literals not governed by config.

    Uses AST to find string constants in src/gzkit/ that look like
    filesystem paths (contain a ``/`` and start with a known directory
    prefix). A literal is governed when the manifest maps it OR when
    ``GzkitConfig.paths`` declares it as a default -- both are config
    surfaces, and checking only the manifest reported a declared
    ``PathConfig`` default as unmapped, including at the ``config.py``
    line declaring it (GHI #938).

    A literal is also credited when its OWN module declares it an audit
    subject via :data:`_AUDIT_SUBJECT_DECLARATION`. That covers the literals
    no config field can govern -- the ones naming a surface the code audits,
    rosters, or checks for absence. The declaration is read per-file, so it
    never reaches another module (GHI #938).
    """
    issues: list[dict[str, str]] = []
    src_dir = project_root / "src" / "gzkit"
    if not src_dir.exists():
        return issues

    manifest_paths = _flatten_manifest_paths(manifest) | _flatten_config_paths(config)
    path_prefix_re = __import__("re").compile(_PATH_SEGMENT_RE)

    for py_file in sorted(src_dir.rglob("*.py")):
        try:
            source = py_file.read_text(encoding="utf-8")
            tree = ast.parse(source, filename=str(py_file))
        except (OSError, SyntaxError):
            continue

        rel_path = py_file.relative_to(project_root).as_posix()
        declared_subjects = _collect_declared_audit_subjects(tree)

        for node in ast.walk(tree):
            if not isinstance(node, ast.Constant):
                continue
            if not isinstance(node.value, str):
                continue
            value = node.value.strip()
            if "/" not in value:
                continue
            if value in _EXEMPT_PATH_LITERALS:
                continue
            # Exact match after the same normalization the rest of the audit
            # uses -- never a prefix test. A prefix test on a declared
            # ".github/workflows" would exempt every ".github/**" literal in
            # the module, which is the blinding failure _flatten_config_paths
            # already refuses for the same reason.
            if value.strip("/").replace("\\", "/") in declared_subjects:
                continue
            # Skip URLs, format strings, and very long strings
            if value.startswith(("http://", "https://", "//", "git@")):
                continue
            if len(value) > 120:
                continue
            # Only flag strings that start with known directory prefixes
            if not path_prefix_re.match(value):
                continue
            if not _is_path_covered_by_manifest(value, manifest_paths):
                _append_path_issue(
                    issues,
                    rel_path,
                    f'unmapped path literal: "{value}"',
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
    }
    required_files = {
        "paths.ledger": config.paths.ledger,
        "paths.manifest": config.paths.manifest,
        "paths.agents_md": config.paths.agents_md,
        "paths.claude_md": config.paths.claude_md,
        "paths.discovery_index": config.paths.discovery_index,
    }

    legacy_obpi_path = f"{config.paths.design_root}/obpis"
    issues = _collect_required_path_issues(project_root, required_dirs, required_files)
    issues.extend(_collect_manifest_artifact_issues(project_root, manifest, legacy_obpi_path))
    issues.extend(_collect_control_surface_issues(project_root, manifest))
    issues.extend(_collect_obpi_path_contract_issues(project_root, config, legacy_obpi_path))
    issues.extend(_collect_source_path_literal_issues(project_root, manifest, config))

    result = {"valid": not issues, "issues": issues}
    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    elif not issues:
        console.print("[green]Config-path audit passed.[/green]")
    else:
        console.print("[red]Config-path audit failed.[/red]")
        for issue in issues:
            console.print(f"  - {issue['path']}: {issue['issue']}", markup=False)

    if issues:
        raise SystemExit(1)
