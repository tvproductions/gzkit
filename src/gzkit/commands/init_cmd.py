"""Init, PRD, and constitution command implementations."""

import importlib.resources
import json
import re
import subprocess
import sys
from collections.abc import Iterator
from datetime import date
from importlib.resources.abc import Traversable
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field
from rich.markup import escape

from gzkit.chores import (
    _classify_chore_file,
    merge_chores_registry,
    missing_surface_files,
    scaffold_core_chores,
)
from gzkit.commands.common import (
    _confirm,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.commands.ledger import MERGE_DRIVER_NAME, ensure_jsonl_merge_driver
from gzkit.commands.register import (
    grandfathered_foundation_ids,
    is_ungrandfathered_foundation,
    is_unreadable_adr,
    warn_foundation_refused,
    warn_unreadable_refused,
)
from gzkit.commands.sync_guard import refuse_on_sync_blockers, report_sync_blockers
from gzkit.config import AuthorshipConfig, GzkitConfig, PathConfig
from gzkit.governance.trust_audits.session_green_gate import (
    configured_hooks_path,
    declared_hook_types,
    install_command,
)
from gzkit.hooks.claude import setup_claude_hooks
from gzkit.hooks.commit_ledger import RECORDER_HOOK_NAME, install_recorder_hook
from gzkit.ledger import (
    Ledger,
    adr_created_event,
    constitution_created_event,
    prd_created_event,
    project_init_event,
)
from gzkit.models.foundation_grandfather import foundation_kind_is_closed
from gzkit.personas import scaffold_core_personas
from gzkit.rules import scaffold_core_rules
from gzkit.skills import scaffold_core_skills
from gzkit.sync import (
    collect_canonical_sync_blockers,
    detect_project_name,
    detect_project_structure,
    generate_manifest,
    parse_artifact_metadata,
    scan_existing_artifacts,
    sync_all,
    write_manifest,
)
from gzkit.templates import render_template, scaffold_core_templates
from gzkit.templates.author_prompts import AUTHOR_PROMPTS
from gzkit.validate_pkg.sync_parity import plan_sync_changes

RefreshState = Literal["IDENTICAL", "STALE", "EDITED"]

CANONICAL_VERSION_MARKER_PATTERN = r"<!-- gzkit-canonical-version: \d+\.\d+\.\d+ -->"


class RefreshResult(BaseModel):
    """Aggregate report of a ``gz init --update`` run.

    Each list holds repo-relative path strings keyed by canonical surface.
    """

    model_config = ConfigDict(frozen=False, extra="forbid")

    identical: list[str] = Field(default_factory=list)
    stale_refreshed: list[str] = Field(default_factory=list)
    edited_conflicts: list[str] = Field(default_factory=list)
    dry_run: bool = Field(default=False)


def _detect_refresh_state(
    *,
    project_bytes: bytes,
    canonical_bytes: bytes,
    marker_pattern: str = CANONICAL_VERSION_MARKER_PATTERN,
) -> RefreshState:
    """Classify a project canonical-surface artifact against the wheel canonical.

    Returns:
        ``IDENTICAL`` when ``project_bytes`` equals ``canonical_bytes`` byte-for-byte.
        ``EDITED`` when the bytes differ AND ``project_bytes`` carries the
        operator-edit marker matched by ``marker_pattern`` — interpreted as a
        positive signal that the scaffolder previously stamped this copy and
        the operator has since edited it. The refresh path must NOT overwrite.
        ``STALE`` when the bytes differ and no marker is present — safe to refresh.

    The marker mechanism (REQ-0.0.32-05-04 option a): the scaffolder writes
    ``<!-- gzkit-canonical-version: X.Y.Z -->`` into every canonical body on
    copy. ``--update`` rewrites the marker on a STALE refresh; an operator
    edit either leaves the marker in place (signal: EDITED) or removes it
    (signal: STALE — operator wants the next refresh to restore canon).

    """
    if project_bytes == canonical_bytes:
        return "IDENTICAL"
    if re.search(marker_pattern, project_bytes.decode("utf-8", errors="replace")):
        return "EDITED"
    return "STALE"


def _iter_canonical_surface_files(resource_pkg: str) -> Iterator[tuple[Traversable, Path]]:
    """Walk a canonical surface resource and yield ``(traversable, rel_path)``.

    ``resource_pkg`` is an importlib.resources package name (e.g. ``"gzkit.skills"``).
    The yielded ``rel_path`` is the path **relative to the canonical surface root**
    suitable for joining onto ``.gzkit/<surface>/`` in an adopter project.

    Skips ``__pycache__``-style entries and non-file leaves; preserves
    subdirectory structure (needed for chores and skills with multiple files).
    """
    root = importlib.resources.files(resource_pkg)
    yield from _walk_traversable(root, root.name, Path())


def _walk_traversable(
    node: Traversable,
    root_name: str,
    rel_prefix: Path,
) -> Iterator[tuple[Traversable, Path]]:
    for entry in node.iterdir():
        # Skip leading-underscore entries (__pycache__, __init__.py,
        # _scaffolder.py, etc.) — these are package-internal infrastructure,
        # never canonical surface content.
        if entry.name.startswith("_"):
            continue
        next_rel = rel_prefix / entry.name
        if entry.is_dir():
            yield from _walk_traversable(entry, root_name, next_rel)
        elif entry.is_file():
            yield entry, next_rel


def _refresh_one_artifact(
    *,
    canonical: Traversable,
    project_path: Path,
    dry_run: bool,
) -> RefreshState:
    """Detect state for ``project_path`` against ``canonical`` and refresh if STALE.

    Returns the detected state. Writes to ``project_path`` only when the state
    is STALE and ``dry_run`` is False. EDITED state never writes; the caller is
    responsible for recording the conflict.
    """
    canonical_bytes = canonical.read_bytes()
    if not project_path.exists():
        if not dry_run:
            project_path.parent.mkdir(parents=True, exist_ok=True)
            project_path.write_bytes(canonical_bytes)
        return "STALE"
    project_bytes = project_path.read_bytes()
    state = _detect_refresh_state(
        project_bytes=project_bytes,
        canonical_bytes=canonical_bytes,
    )
    if state == "STALE" and not dry_run:
        project_path.write_bytes(canonical_bytes)
    return state


def _refresh_canonical_surfaces(
    project_root: Path,
    *,
    dry_run: bool = False,
) -> RefreshResult:
    """Refresh canonical surfaces in ``.gzkit/<surface>/`` from the wheel.

    Walks each canonical surface resource (skills, rules, chores canonical-class
    files, templates, personas), classifies each artifact via
    :func:`_detect_refresh_state`, and refreshes STALE entries in place.
    EDITED entries are recorded as conflicts and NOT overwritten.

    Surface targets (REQ-0.0.32-05-02):

    - ``gzkit.skills``  -> ``.gzkit/skills/``
    - ``gzkit.rules``   -> ``.gzkit/rules/``
    - ``gzkit.chores``  -> ``.gzkit/chores/`` (canonical class only;
      package_only/runtime_state are excluded per chores class-classifier)
    - ``gzkit.personas`` -> ``.gzkit/personas/``
    - ``gzkit.templates`` -> ``.gzkit/templates/``

    Args:
        project_root: Project root containing the adopter's ``.gzkit/``.
        dry_run: When True, detect and report state without writing.

    """
    result = RefreshResult(dry_run=dry_run)

    surface_map: list[tuple[str, str]] = [
        ("gzkit.skills", "skills"),
        ("gzkit.rules", "rules"),
        ("gzkit.chores", "chores"),
        ("gzkit.personas", "personas"),
        ("gzkit.templates", "templates"),
    ]

    for resource_pkg, surface_name in surface_map:
        target_root = project_root / ".gzkit" / surface_name
        for canonical, rel_path in _iter_canonical_surface_files(resource_pkg):
            project_path = target_root / rel_path
            if surface_name == "chores":
                classification = _classify_chore_file(
                    Path("src/gzkit/chores") / rel_path,
                    project_root=project_root,
                )
                if classification != "canonical":
                    continue
            display = f".gzkit/{surface_name}/{rel_path.as_posix()}"
            state = _refresh_one_artifact(
                canonical=canonical,
                project_path=project_path,
                dry_run=dry_run,
            )
            if state == "IDENTICAL":
                result.identical.append(display)
            elif state == "STALE":
                result.stale_refreshed.append(display)
            else:  # EDITED
                result.edited_conflicts.append(display)

    return result


def _print_refresh_summary(result: RefreshResult) -> None:
    """Render a structured per-surface summary of a refresh run."""
    if result.dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
    console.print(
        f"  IDENTICAL: {len(result.identical)} "
        f"STALE: {len(result.stale_refreshed)} "
        f"EDITED: {len(result.edited_conflicts)}"
    )
    if result.stale_refreshed:
        prefix = "Would refresh" if result.dry_run else "Refreshed"
        console.print(f"\n[green]{prefix} (STALE):[/green]")
        for path in result.stale_refreshed:
            console.print(f"  - {path}")
    if result.edited_conflicts:
        console.print("\n[red]Conflicts (EDITED — not overwritten):[/red]")
        for path in result.edited_conflicts:
            console.print(f"  - {path}")
        console.print(
            "\n  Operator action required: review each conflict and either accept "
            "the canonical version (delete the project copy and re-run --update) "
            "or keep the project edits (no action; conflict persists)."
        )


def _normalize_package_name(project_name: str) -> str:
    """Normalize a project name to a valid Python package name.

    Replaces hyphens and spaces with underscores, strips non-alphanumeric
    characters, and lowercases the result.
    """
    name = project_name.lower().replace("-", "_").replace(" ", "_")
    name = re.sub(r"[^a-z0-9_]", "", name)
    name = re.sub(r"_+", "_", name).strip("_")
    return name or "app"


def _scaffold_project_skeleton(
    project_root: Path,
    project_name: str,
    source_root: str,
    tests_root: str,
    *,
    dry_run: bool = False,
) -> list[str]:
    """Create the minimal Python project skeleton.

    Creates pyproject.toml, README.md, src/<package>/__init__.py, and
    tests/__init__.py. Idempotent: skips any artifact that already exists.

    The README is here because the manifest above NAMES it. A generated
    manifest referencing a file the generator does not create is syntactically
    valid, so every static check accepts it and only a build reads the
    reference -- and `gz init` never performs one. The tree it produced could
    not be built at all: hatchling raised "Readme file does not exist:
    README.md", so every `uv run` in a freshly scaffolded project failed,
    including the `uv run gz ...` form init's own closing output recommends
    (GHI #910).

    Returns a list of human-readable descriptions of created artifacts.
    """
    created: list[str] = []
    package_name = _normalize_package_name(project_name)

    # --- pyproject.toml ---
    pyproject_path = project_root / "pyproject.toml"
    if not pyproject_path.exists():
        if dry_run:
            created.append("Would create pyproject.toml")
        else:
            pyproject_content = (
                "[project]\n"
                f'name = "{project_name}"\n'
                'version = "0.1.0"\n'
                f'description = "{project_name}"\n'
                'readme = "README.md"\n'
                'requires-python = ">=3.13"\n'
                "\n"
                "dependencies = []\n"
                "\n"
                "[project.optional-dependencies]\n"
                "dev = [\n"
                '    "ruff>=0.8",\n'
                "]\n"
                "\n"
                "[build-system]\n"
                'requires = ["hatchling"]\n'
                'build-backend = "hatchling.build"\n'
                "\n"
                "[tool.hatch.build.targets.wheel]\n"
                f'packages = ["{source_root}/{package_name}"]\n'
                "\n"
                "[tool.ruff]\n"
                'target-version = "py313"\n'
                "line-length = 100\n"
                f'src = ["{source_root}", "{tests_root}"]\n'
                "\n"
                "[tool.ruff.lint]\n"
                'select = ["E", "F", "I", "UP", "B", "SIM", "TRY", "RUF"]\n'
            )
            pyproject_path.write_text(pyproject_content, encoding="utf-8")
            created.append("Created pyproject.toml")

    # --- README.md ---
    # Named by `readme` in the manifest written above; see this function's
    # docstring for why the pair must land together (GHI #910).
    readme_path = project_root / "README.md"
    if not readme_path.exists():
        if dry_run:
            created.append("Would create README.md")
        else:
            readme_content = (
                f"# {project_name}\n"
                "\n"
                f"{project_name}\n"
                "\n"
                "## Governance\n"
                "\n"
                "This project is governed by gzkit. Read `AGENTS.md` for the agent\n"
                "contract, and run `uv run gz status` for current gate state.\n"
            )
            readme_path.write_text(readme_content, encoding="utf-8")
            created.append("Created README.md")

    # --- src/<package>/__init__.py ---
    package_dir = project_root / source_root / package_name
    init_file = package_dir / "__init__.py"
    if not init_file.exists():
        if dry_run:
            created.append(f"Would create {source_root}/{package_name}/__init__.py")
        else:
            package_dir.mkdir(parents=True, exist_ok=True)
            init_content = f'"""{project_name}."""\n'
            init_file.write_text(init_content, encoding="utf-8")
            created.append(f"Created {source_root}/{package_name}/__init__.py")

    # --- tests/__init__.py ---
    tests_dir = project_root / tests_root
    tests_init = tests_dir / "__init__.py"
    if not tests_init.exists():
        if dry_run:
            created.append(f"Would create {tests_root}/__init__.py")
        else:
            tests_dir.mkdir(parents=True, exist_ok=True)
            tests_init.write_text("", encoding="utf-8")
            created.append(f"Created {tests_root}/__init__.py")

    return created


_GITIGNORE_CONTENT = """\
# Byte-compiled / optimized / DLL files
# Reference: https://github.com/github/gitignore/blob/main/Python.gitignore
__pycache__/
*.py[codz]
*$py.class

# C extensions
*.so

# Distribution / packaging
build/
dist/
*.egg-info/
*.egg

# Unit test / coverage reports
htmlcov/
.coverage
.coverage.*
coverage.xml
*.cover
*.py.cover

# Environments
.env
.venv/
env/
venv/

# Type checkers
.mypy_cache/
.pytype/
.pyre/

# Ruff
.ruff_cache/

# mkdocs
/site

# Claude Code user settings (machine-specific)
.claude/settings.local.json

# Report publication OS-lock sidecar (retain the reports themselves)
**/reports/big-picture/publication.lock

# OS
.DS_Store
Thumbs.db
"""


_PRE_COMMIT_CONFIG_CONTENT = """\
# Session-green gate (ADR-0.0.68). The pre-push hook below is the covenant's
# between-sessions enforcement point: it runs the full `gz check` sweep before
# any push leaves the worktree.
#
# Declaring it is not delivering it. `gz init` also runs `pre-commit install`;
# `gz check` verifies the hook is on disk. Add your own pre-commit-stage hooks
# (lint, format, typecheck) beneath this one as the project grows.
default_stages: [pre-commit]

repos:
  - repo: local
    hooks:
      - id: gz-check-pre-push
        name: gz check (pre-push gate)
        entry: uv run gz check
        language: system
        pass_filenames: false
        stages: [pre-push]
"""

# Ordered by how the project is most likely to reach a pre-commit: the project
# venv first, then an ephemeral uvx download. pre-commit is deliberately NOT a
# gzkit dependency (STDLIB-FIRST: adding a runtime dep needs foundation
# attestation), so activation is best-effort here — `gz check`'s delivery arm is
# the fail-closed half that makes a silent miss impossible.
_INSTALLERS = (
    ("uv", "run", "pre-commit"),
    ("uvx", "pre-commit"),
    ("pre-commit",),
)


def _scaffold_pre_commit_config(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Write ``.pre-commit-config.yaml`` declaring the pre-push gate if absent.

    Idempotent and non-destructive: an existing config is operator canon and is
    never rewritten. Without this, `gz init` left adopters with no config at all
    while `gz check` fail-closed on its absence — telling them to hand-author a
    hook and citing a gzkit-internal OBPI id that means nothing in their repo
    (GHI #715).

    Returns a human-readable status string, or None if skipped.
    """
    config = project_root / ".pre-commit-config.yaml"
    if config.exists():
        return None
    if dry_run:
        return "Would create .pre-commit-config.yaml (pre-push gz check gate)"
    config.write_text(_PRE_COMMIT_CONFIG_CONTENT, encoding="utf-8")
    return "Created .pre-commit-config.yaml (pre-push gz check gate)"


def _install_pre_commit_hooks(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Install the declared hooks into the worktree so the gate actually fires.

    A declared-but-uninstalled gate enforces nothing while every surface reports
    green — the condition that ran unenforced in the gzkit repo for six weeks
    (GHI #715). Failure here is reported, never raised: `gz init` must still
    complete on a machine without pre-commit, and `gz check`'s delivery arm is
    what fails closed.

    Returns a human-readable status string, or None if skipped.
    """
    if not (project_root / ".git").is_dir():
        return None
    if not (project_root / ".pre-commit-config.yaml").is_file():
        return None
    if dry_run:
        return (
            f"Would run pre-commit install ({', '.join(declared_hook_types(project_root))} hooks)"
        )

    redirect = configured_hooks_path(project_root)
    if redirect is not None:
        # pre-commit exits non-zero with "Cowardly refusing to install hooks with
        # `core.hooksPath` set" — spending the subprocess to be told so adds
        # nothing. Unsetting an operator's git config is not init's call.
        return (
            f"Pre-push gate NOT installed: core.hooksPath is set ({redirect.as_posix()}), "
            "and pre-commit refuses to install hooks while it is. Commits and pushes "
            "will run unenforced until this is resolved. Recovery: "
            "`git config --local --unset-all core.hooksPath` then "
            f"`{install_command(declared_hook_types(project_root))}`."
        )

    hook_args = [
        arg for hook_type in declared_hook_types(project_root) for arg in ("--hook-type", hook_type)
    ]
    for installer in _INSTALLERS:
        try:
            result = subprocess.run(
                [*installer, "install", *hook_args],
                cwd=project_root,
                capture_output=True,
                text=True,
                errors="replace",
                encoding="utf-8",
            )
        except (OSError, subprocess.SubprocessError):
            continue
        if result.returncode == 0:
            return (
                f"Installed {', '.join(declared_hook_types(project_root))} hooks "
                "(session-green gate active)"
            )
    return (
        "Pre-push gate NOT installed: could not run `pre-commit install`. Commits and "
        "pushes will run unenforced until this is resolved. Recovery: install pre-commit "
        "(`uv tool install pre-commit`), then "
        f"`{install_command(declared_hook_types(project_root))}`."
    )


def _install_commit_locus_recorder(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Install the commit-locus recorder where pre-commit runs it before stashing.

    Delivered only when the project declares the ``post-commit`` hook type: the
    recorder runs as that shim's ``post-commit.legacy`` hook, which pre-commit
    executes before it stashes unstaged changes. As a pre-commit post-commit
    hook its ledger row was rolled back whenever the ledger carried unstaged
    rows (GHI #1092).

    Returns a human-readable status string, or None if skipped.
    """
    if not (project_root / ".git").is_dir():
        return None
    if "post-commit" not in declared_hook_types(project_root):
        return None
    if configured_hooks_path(project_root) is not None:
        # pre-commit refused to install; the install step already reported it.
        return None
    if dry_run:
        return f"Would install commit-locus recorder ({RECORDER_HOOK_NAME})"
    return install_recorder_hook(project_root / ".git" / "hooks")


def _session_green_gate_statuses(project_root: Path, *, dry_run: bool = False) -> list[str]:
    """Declare the pre-push gate, then deliver it; return each step's status line.

    Two steps, not one: declaring a gate and installing it fail independently,
    and the pairing is the whole point of GHI #715.
    """
    return [
        status
        for status in (
            _scaffold_pre_commit_config(project_root, dry_run=dry_run),
            _install_pre_commit_hooks(project_root, dry_run=dry_run),
            _install_commit_locus_recorder(project_root, dry_run=dry_run),
        )
        if status
    ]


def _setup_session_green_gate(project_root: Path, *, dry_run: bool = False) -> None:
    """Run the session-green-gate setup and print each step's status."""
    for status in _session_green_gate_statuses(project_root, dry_run=dry_run):
        console.print(f"  {status}")


def _scaffold_audit_thresholds(project_root: Path) -> None:
    """Write ``data/audit_thresholds.json`` with the canonical defaults.

    Called from ``gz init``. Idempotent: skips when the file already exists.
    The heuristic at ``gz adr audit-check`` refuses to silently fall back
    to compiled-in defaults when the file is missing, so every gzkit-shaped
    workspace MUST carry it.
    """
    target = project_root / "data" / "audit_thresholds.json"
    if target.exists():
        return
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(
        json.dumps(
            {"max_covers_backfill_commits": 3, "max_covers_backfill_days": 7},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )


def _scaffold_gitignore(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Create a Python-oriented .gitignore if one does not exist.

    Idempotent: preserves any existing .gitignore.
    Returns a human-readable status string, or None if skipped.
    """
    gitignore = project_root / ".gitignore"
    if gitignore.exists():
        return None
    if dry_run:
        return "Would create .gitignore"
    gitignore.write_text(_GITIGNORE_CONTENT, encoding="utf-8")
    return "Created .gitignore"


def _run_uv_sync(project_root: Path, *, dry_run: bool = False) -> str | None:
    """Run ``uv sync`` to hydrate the virtualenv if needed.

    Idempotent: skips if no pyproject.toml exists or .venv already present.

    Returns a human-readable status string, or None if skipped.
    """
    if not (project_root / "pyproject.toml").exists():
        return None
    if (project_root / ".venv").exists():
        return None

    if dry_run:
        return "Would run uv sync"

    result = subprocess.run(
        ["uv", "sync"],
        cwd=project_root,
        capture_output=True,
        text=True,
        errors="replace",
        encoding="utf-8",
    )
    if result.returncode == 0:
        return "Ran uv sync (virtualenv created)"
    console.print(f"  [yellow]uv sync failed (exit {result.returncode}):[/yellow]")
    if result.stderr:
        for line in result.stderr.strip().splitlines()[:5]:
            console.print(f"    {escape(line)}")
    return None


def _repair_chores(
    project_root: Path,
    config: GzkitConfig,
    *,
    dry_run: bool,
    yes: bool,
) -> list[str]:
    """Scaffold canonical chores and merge the registry; return repair messages.

    A dry run never calls the scaffolder, which writes (GHI #1098); it lists what
    the real run's ``skip_existing`` scaffold would add instead.
    """
    from gzkit.chores import _iter_canonical_chore_slugs  # noqa: PLC0415

    chores_dir = project_root / config.paths.chores
    surface_files = [f"{config.paths.chores}/{name}" for name in missing_surface_files(chores_dir)]
    messages: list[str] = []
    if dry_run:
        for slug_resource in _iter_canonical_chore_slugs():
            slug = slug_resource.name
            if not (chores_dir / slug).exists():
                messages.append(f"Would scaffold chore: {slug}")
        messages.extend(f"Would scaffold {path}" for path in surface_files)
    else:
        for chore_path in scaffold_core_chores(project_root, config, skip_existing=True):
            messages.append(f"Scaffolded new chore: {chore_path.parent.name}")
        messages.extend(f"Scaffolded {path}" for path in surface_files)

    merge_report = merge_chores_registry(project_root, config, auto_yes=yes, dry_run=dry_run)
    if merge_report.added or merge_report.changed:
        if dry_run:
            messages.append(
                "Would merge chores registry: "
                f"+{len(merge_report.added)}/~{len(merge_report.changed)}"
            )
        elif merge_report.wrote:
            messages.append("Merged chores registry")
    return messages


def _repair_rules(
    project_root: Path,
    config: GzkitConfig,
    *,
    dry_run: bool,
) -> list[str]:
    """Scaffold new canonical rules, returning per-slug status messages."""
    from gzkit.rules import _iter_canonical_rule_slugs  # noqa: PLC0415

    if dry_run:
        rules_dir = project_root / config.paths.canonical_rules
        return [
            f"Would scaffold rule: {entry.name[:-3]}"
            for entry in _iter_canonical_rule_slugs()
            if not (rules_dir / entry.name).exists()
        ]
    new_rules = scaffold_core_rules(project_root, config, skip_existing=True)
    return [f"Scaffolded new rule: {path.name}" for path in new_rules]


def _repair_personas(
    project_root: Path,
    config: GzkitConfig,
    *,
    dry_run: bool,
) -> list[str]:
    """Scaffold new canonical personas, returning per-slug status messages."""
    from gzkit.personas import _iter_canonical_persona_slugs  # noqa: PLC0415

    if dry_run:
        personas_dir = project_root / ".gzkit" / "personas"
        return [
            f"Would scaffold persona: {entry.name[:-3]}"
            for entry in _iter_canonical_persona_slugs()
            if not (personas_dir / entry.name).exists()
        ]
    new_personas = scaffold_core_personas(project_root, config, skip_existing=True)
    return [f"Scaffolded new persona: {path.name}" for path in new_personas]


def _repair_templates(
    project_root: Path,
    config: GzkitConfig,
    *,
    dry_run: bool,
) -> list[str]:
    """Scaffold new canonical templates, returning per-slug status messages."""
    from gzkit.templates import _iter_canonical_template_slugs  # noqa: PLC0415

    if dry_run:
        templates_dir = project_root / ".gzkit" / "templates"
        return [
            f"Would scaffold template: {entry.name[:-3]}"
            for entry in _iter_canonical_template_slugs()
            if not (templates_dir / entry.name).exists()
        ]
    new_templates = scaffold_core_templates(project_root, config, skip_existing=True)
    return [f"Scaffolded new template: {path.name[:-3]}" for path in new_templates]


def _dry_run_missing_canonical_skills(
    project_root: Path,
    config: GzkitConfig,
) -> list[str]:
    """List ``Would scaffold skill: <slug>`` lines for missing canonical slugs.

    Mirrors :func:`gzkit.skills.scaffold_core_skills` iteration: enumerate
    canonical slugs from the wheel's package surface and skip
    ``lifecycle_state: retired`` (GHI #453 — formerly iterated
    ``CORE_SKILLS`` which carried stale retired slugs).
    """
    from gzkit.skills import _iter_canonical_skill_slugs, _parse_frontmatter  # noqa: PLC0415

    skills_dir = project_root / config.paths.skills
    messages: list[str] = []
    for slug_resource in _iter_canonical_skill_slugs():
        slug = slug_resource.name
        skill_src = slug_resource.joinpath("SKILL.md")
        frontmatter, _ = _parse_frontmatter(skill_src.read_text(encoding="utf-8"))
        if (frontmatter.get("lifecycle_state") or "active") == "retired":
            continue
        if not (skills_dir / slug / "SKILL.md").exists():
            messages.append(f"Would scaffold skill: {slug}")
    return messages


def _repair_control_surfaces(
    project_root: Path,
    config: GzkitConfig,
    *,
    dry_run: bool,
) -> list[str]:
    """Re-sync control surfaces, reporting each file the sync changes (GHI #1098).

    The plan is rendered against the tree as it stands, so a dry run cannot name
    the mirrors of an artifact it has not yet scaffolded; its ``Would scaffold``
    line stands for them. A tree already in sync plans nothing, so repair runs no
    sync and appends no ``agent_sync_completed`` row.
    """
    changes = plan_sync_changes(project_root, config)
    if dry_run:
        return [f"Would sync {path}" for path in changes]
    if changes:
        sync_all(project_root, config)
    return [f"Synced {path}" for path in changes]


# A handle, never a real name: whitespace is what makes a value name-shaped.
_HANDLE_PATTERN = re.compile(r"^\S+$")


def _checked_attestor_handle(handle: str | None) -> str | None:
    """Return ``handle`` if it is a valid attestor handle; refuse a name-shaped one."""
    if handle is None or _HANDLE_PATTERN.match(handle):
        return handle
    console.print(
        "[red]Error:[/red] --attestor-handle takes a handle with no spaces, never a real "
        "name (AGENTS.md § Execution Rules). Nothing written."
    )
    sys.exit(1)


def _checked_init_flags(*, update: bool, force: bool, attestor_handle: str | None) -> str | None:
    """Refuse contradictory init flags; return the validated attestor handle."""
    if update and force:
        console.print("[red]Error:[/red] --update and --force are mutually exclusive.")
        sys.exit(1)
    if update and attestor_handle is not None:
        console.print(
            "[red]Error:[/red] --attestor-handle and --update are mutually exclusive; "
            "record the handle with `gz init --attestor-handle <handle>`."
        )
        sys.exit(1)
    return _checked_attestor_handle(attestor_handle)


def _first_init_authorship(attestor_handle: str | None) -> AuthorshipConfig:
    """Return the authorship block a first init writes, and report the handle.

    gzkit's own handle is never scaffolded: the value comes from this project's
    operator, by flag or prompt, or stays unset (GHI #1036).
    """
    handle = attestor_handle if attestor_handle is not None else _prompt_attestor_handle()
    if handle:
        console.print(f"  Recorded attestor handle: {handle}")
    else:
        console.print("  No attestor handle set; `gz init --attestor-handle <handle>` records one.")
    return AuthorshipConfig(attestor_handle=handle)


def _prompt_attestor_handle() -> str | None:
    """Ask for the attestor handle on an interactive first init; None when skipped.

    Asked only when both streams are a terminal, so a scripted or captured init
    never blocks on input (GHI #1036).
    """
    if not (sys.stdin.isatty() and sys.stdout.isatty()):
        return None
    while True:
        answer = input(
            "Attestor handle an omitted --attestor records "
            "(a handle, never a real name; blank to skip): "
        ).strip()
        if not answer or _HANDLE_PATTERN.match(answer):
            return answer or None
        console.print("  A handle has no spaces.")


def _repair_attestor_handle(project_root: Path, handle: str | None, *, dry_run: bool) -> list[str]:
    """Record ``handle`` in `.gzkit.json`, changing that one key and nothing else."""
    if handle is None:
        return []
    config_path = project_root / ".gzkit.json"
    data = json.loads(config_path.read_text(encoding="utf-8"))
    authorship = data.setdefault("authorship", {})
    if authorship.get("attestor_handle") == handle:
        return []
    if dry_run:
        return [f"Would set authorship.attestor_handle in .gzkit.json to {handle}"]
    authorship["attestor_handle"] = handle
    GzkitConfig.model_validate(data)
    config_path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    return [f"Set authorship.attestor_handle in .gzkit.json to {handle}"]


def _repair_missing_artifacts(
    project_root: Path,
    config: GzkitConfig,
    *,
    no_skeleton: bool = False,
    dry_run: bool = False,
    yes: bool = False,
    attestor_handle: str | None = None,
) -> None:
    """Detect and repair missing artifacts on an already-initialized project.

    Runs the idempotent portions of init without requiring --force.
    """
    project_name = config.project_name or detect_project_name(project_root)
    repaired: list[str] = []

    console.print(f"Repairing [bold]{project_name}[/bold]...")
    repaired.extend(_repair_attestor_handle(project_root, attestor_handle, dry_run=dry_run))

    # Repair project skeleton
    if not no_skeleton:
        skeleton = _scaffold_project_skeleton(
            project_root,
            project_name,
            config.paths.source_root,
            config.paths.tests_root,
            dry_run=dry_run,
        )
        repaired.extend(skeleton)

    # Repair governance directories
    design_root = config.paths.design_root
    for dir_name in ["prd", "constitutions", "adr"]:
        dir_path = project_root / design_root / dir_name
        if not dir_path.exists():
            if dry_run:
                repaired.append(f"Would create {design_root}/{dir_name}/")
            else:
                dir_path.mkdir(parents=True, exist_ok=True)
                repaired.append(f"Created {design_root}/{dir_name}/")

    # Hydrate virtualenv
    if not no_skeleton:
        uv_status = _run_uv_sync(project_root, dry_run=dry_run)
        if uv_status:
            repaired.append(uv_status)

    # Repair .gitignore
    gi_status = _scaffold_gitignore(project_root, dry_run=dry_run)
    if gi_status:
        repaired.append(gi_status)

    # Repair the session-green gate — declaration then delivery. Projects
    # initialized before GHI #715 carry neither; repair is how they get both.
    repaired.extend(_session_green_gate_statuses(project_root, dry_run=dry_run))

    # Repair skills — scaffold any core skills added in newer gzkit versions.
    # A dry run never calls the scaffolder, which writes (GHI #1098).
    if dry_run:
        repaired.extend(_dry_run_missing_canonical_skills(project_root, config))
    else:
        for skill_path in scaffold_core_skills(project_root, config, skip_existing=True):
            repaired.append(f"Scaffolded new skill: {skill_path.parent.name}")

    # Repair rules — scaffold any core rules added in newer gzkit versions
    repaired.extend(_repair_rules(project_root, config, dry_run=dry_run))

    # Repair personas — scaffold any core personas added in newer gzkit versions
    repaired.extend(_repair_personas(project_root, config, dry_run=dry_run))

    # Repair templates — scaffold any core templates added in newer gzkit versions
    repaired.extend(_repair_templates(project_root, config, dry_run=dry_run))

    # Repair chores (scaffold + registry merge)
    repaired.extend(_repair_chores(project_root, config, dry_run=dry_run, yes=yes))

    # Repair manifest
    manifest_path = project_root / config.paths.manifest
    if not manifest_path.exists():
        if dry_run:
            repaired.append(f"Would regenerate {config.paths.manifest}")
        else:
            manifest = generate_manifest(project_root, config)
            write_manifest(project_root, manifest, config)
            repaired.append(f"Regenerated {config.paths.manifest}")

    # Canon that fails preflight is never propagated to the mirrors (GHI #1100).
    # The refusal comes after the summary, so every write made above is reported.
    blockers = [] if dry_run else collect_canonical_sync_blockers(project_root, config)
    if not blockers:
        repaired.extend(_repair_control_surfaces(project_root, config, dry_run=dry_run))

    if repaired:
        if dry_run:
            console.print("[yellow]Dry run:[/yellow] no files written.")
        for item in repaired:
            console.print(f"  {item}")
        console.print(f"\n[green]Repaired {len(repaired)} artifact(s).[/green]")
    elif not blockers:
        console.print("  All artifacts present. Nothing to repair.")
    if blockers:
        report_sync_blockers(blockers)


def _setup_init_hooks(project_root: Path, config: GzkitConfig) -> None:
    """Set up hooks during initialization."""
    claude_files = setup_claude_hooks(project_root, config)
    for path in claude_files:
        console.print(f"  Created {path}")


def _register_existing_artifacts(
    project_root: Path,
    design_root: str,
    ledger: Ledger,
    mode: str,
) -> bool:
    """Scan and register existing artifacts. Returns True if registered."""
    existing = scan_existing_artifacts(project_root, design_root)
    prd_metadata = [parse_artifact_metadata(p) for p in existing["prds"]]
    # Refuse undecodable packages BEFORE parse_artifact_metadata, which decodes
    # UTF-8 and catches only OSError — one bad file would otherwise abort init
    # partway through, after earlier initialization mutations have landed.
    adr_files = []
    for adr_path in existing["adrs"]:
        if is_unreadable_adr(adr_path):
            warn_unreadable_refused(adr_path)
            continue
        adr_files.append(adr_path)
    adr_metadata = [parse_artifact_metadata(p) for p in adr_files]

    if not prd_metadata and not adr_metadata:
        return False

    console.print("\n[bold]Found existing artifacts:[/bold]")
    if prd_metadata:
        console.print("\n  PRDs:")
        for meta in prd_metadata:
            console.print(f"    - {meta['id']}")
    if adr_metadata:
        console.print("\n  ADRs:")
        for meta in adr_metadata:
            parent = meta.get("parent", "(no parent found)")
            console.print(f"    - {meta['id']} -> parent: {parent}")

    console.print()
    if not _confirm("Register these artifacts in the ledger?", default=True):
        return False

    # Register PRDs
    prd_ids = []
    for meta in prd_metadata:
        prd_id = meta["id"]
        ledger.append(prd_created_event(prd_id))
        prd_ids.append(prd_id)
        console.print(f"  Registered PRD: {prd_id}")

    # Register ADRs
    grandfathered = grandfathered_foundation_ids(project_root)
    kind_is_closed = foundation_kind_is_closed(project_root)
    for adr_file, meta in zip(adr_files, adr_metadata, strict=True):
        adr_id = meta["id"]
        parent = meta.get("parent", prd_ids[0] if prd_ids else "")
        if ledger.has_adr_created(adr_id):
            console.print(f"  Skipped ADR (already registered): {adr_id}")
            continue
        # Registration membrane (GHI #706) — second door of the same guard.
        if is_ungrandfathered_foundation(
            adr_file, adr_id, grandfathered, kind_is_closed=kind_is_closed
        ):
            warn_foundation_refused(adr_id)
            continue
        ledger.append(adr_created_event(adr_id, parent, mode))
        console.print(f"  Registered ADR: {adr_id} (parent: {parent or 'none'})")

    return True


def init(
    mode: str,
    force: bool,
    dry_run: bool,
    *,
    no_skeleton: bool = False,
    yes: bool = False,
    update: bool = False,
    attestor_handle: str | None = None,
) -> None:
    """Initialize gzkit in the current project.

    Three operating modes:

    - **default** (no flags) — repair mode if already initialized; otherwise
      full initialization. Idempotent; preserves operator-edited files.
    - ``--force`` — full reinitialize. Re-copies the wheel's skills, rules,
      templates and chores over the project's copies and rewrites
      ``.gzkit.json``; deletes nothing and never overwrites personas.
    - ``--update`` — version-aware refresh of canonical surfaces from the
      installed wheel. Preserves operator-edited files via marker detection
      (see :func:`_detect_refresh_state`). Reports conflicts and exits 3 if
      any unresolved EDITED entries remain. Mutually exclusive with ``--force``.
    """
    attestor_handle = _checked_init_flags(
        update=update, force=force, attestor_handle=attestor_handle
    )

    project_root = get_project_root()
    gzkit_dir = project_root / ".gzkit"

    if update:
        if not gzkit_dir.exists():
            console.print(
                "[red]Error:[/red] --update requires an initialized project. Run `gz init` first."
            )
            sys.exit(1)
        console.print("Refreshing canonical surfaces from installed wheel...")
        result = _refresh_canonical_surfaces(project_root, dry_run=dry_run)
        _print_refresh_summary(result)
        if result.edited_conflicts:
            sys.exit(3)
        return

    # Already initialized and no --force: run repair instead of erroring
    if gzkit_dir.exists() and not force:
        config = GzkitConfig.load(project_root / ".gzkit.json")
        _repair_missing_artifacts(
            project_root,
            config,
            no_skeleton=no_skeleton,
            dry_run=dry_run,
            yes=yes,
            attestor_handle=attestor_handle,
        )
        return

    # Detect project structure
    structure = detect_project_structure(project_root)
    project_name = detect_project_name(project_root)
    design_root = structure.get("design_root", "design")
    source_root = structure.get("source_root", "src")
    tests_root = structure.get("tests_root", "tests")

    console.print(f"Initializing gzkit for [bold]{project_name}[/bold] in {mode} mode...")

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create {gzkit_dir}")
        console.print("  Would create .gzkit/ledger.jsonl")
        console.print("  Would create .gzkit.json")
        if attestor_handle is not None:
            console.print(f"  Would record attestor handle: {attestor_handle}")
        console.print("  Would generate .gzkit/manifest.json")
        console.print("  Would create governance directories (prd, constitutions, adr)")
        if not no_skeleton:
            skeleton = _scaffold_project_skeleton(
                project_root, project_name, source_root, tests_root, dry_run=True
            )
            for item in skeleton:
                console.print(f"  {item}")
            console.print("  Would run uv sync")
        console.print("  Would create .gitignore")
        _setup_session_green_gate(project_root, dry_run=True)
        console.print(f"  Would register git merge driver '{MERGE_DRIVER_NAME}'")
        console.print("  Would generate control surfaces (AGENTS.md, CLAUDE.md, etc.)")
        console.print("  Would set up hooks and scaffold core skills")
        console.print("  Would scaffold canonical chores into .gzkit/chores/")
        console.print("  Would scaffold default personas")
        console.print("  Would append ledger event: project_init")
        console.print("  Would register existing artifacts (if any)")
        return

    # Create .gzkit directory
    gzkit_dir.mkdir(exist_ok=True)

    # Create empty ledger
    ledger_path = gzkit_dir / "ledger.jsonl"
    ledger_path.touch()

    # Create config with detected paths
    mode_literal = cast(Literal["lite", "heavy"], mode)
    paths = PathConfig(
        design_root=design_root,
        prd=f"{design_root}/prd",
        constitutions=f"{design_root}/constitutions",
        obpis=f"{design_root}/adr",
        adrs=f"{design_root}/adr",
        source_root=source_root,
        tests_root=tests_root,
        docs_root=structure.get("docs_root", "docs"),
    )
    config = GzkitConfig(
        mode=mode_literal,
        paths=paths,
        project_name=project_name,
        authorship=_first_init_authorship(attestor_handle),
    )
    config.save(project_root / ".gzkit.json")

    # Generate manifest
    manifest = generate_manifest(project_root, config, structure)
    write_manifest(project_root, manifest, config)

    # Create governance directories (only if they don't exist)
    for dir_name in ["prd", "constitutions", "adr"]:
        dir_path = project_root / design_root / dir_name
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)
            console.print(f"  Created {design_root}/{dir_name}/")

    # Scaffold project skeleton (pyproject.toml, src/, tests/)
    if not no_skeleton:
        skeleton = _scaffold_project_skeleton(project_root, project_name, source_root, tests_root)
        for item in skeleton:
            console.print(f"  {item}")
        uv_status = _run_uv_sync(project_root)
        if uv_status:
            console.print(f"  {uv_status}")

    # Create .gitignore
    gi_status = _scaffold_gitignore(project_root)
    if gi_status:
        console.print(f"  {gi_status}")

    # Session-green gate: declare it, then deliver it. `gz check` verifies the
    # delivery, so a failure to install here surfaces rather than going silent.
    _setup_session_green_gate(project_root)

    # Append-only JSONL merge driver. The `.gitattributes` rule ships with the
    # repo, but git reads the driver *command* from local config, which cannot
    # be committed — so a fresh clone has the attribute and no driver behind it
    # until something seeds it here (GHI #811).
    if ensure_jsonl_merge_driver(project_root):
        console.print(f"  Registered git merge driver '{MERGE_DRIVER_NAME}' for append-only JSONL")

    # Scaffold core skills
    skills = scaffold_core_skills(project_root, config)
    console.print(f"  Scaffolded {len(skills)} core skills")

    # Scaffold canonical chores
    chores = scaffold_core_chores(project_root, config)
    console.print(f"  Scaffolded {len(chores)} core chores")

    # Scaffold canonical personas — skip_existing=True preserves operator-edited
    # files; personas are identity files that must never be silently overwritten.
    personas = scaffold_core_personas(project_root, config, skip_existing=True)
    console.print(f"  Scaffolded {len(personas)} core personas")

    # Scaffold canonical templates
    templates = scaffold_core_templates(project_root, config)
    console.print(f"  Scaffolded {len(templates)} core templates")

    # Scaffold data/audit_thresholds.json — required by gz adr audit-check
    # covers-backfill heuristic (REQ-0.0.23-05-03). The heuristic refuses to
    # silent-fall-back to compiled-in defaults; every gzkit project must
    # carry the canonical file.
    _scaffold_audit_thresholds(project_root)

    # Sync control surfaces (including skill mirrors). `--force` re-copies the
    # wheel's skills but keeps local ones, so canon can still fail preflight here
    # (GHI #1100).
    refuse_on_sync_blockers(project_root, config)
    updated = sync_all(project_root, config)
    for path in updated:
        console.print(f"  Generated {path}")

    # Scaffold canonical rules AFTER sync_all so that the first sync uses the
    # existing instruction-sync path (sync_claude_rules) rather than
    # render_rules_to_dir, which would conflict with adopter-authored
    # .github/instructions/ pairs. On subsequent gz init --repair and
    # gz agent sync runs, rules are already in .gzkit/rules/ and will be
    # rendered correctly by sync_all.
    rules = scaffold_core_rules(project_root, config)
    console.print(f"  Scaffolded {len(rules)} core rules")

    # Set up hooks
    _setup_init_hooks(project_root, config)

    # Re-sync control surfaces LAST, on the same terms as the repair path above:
    # idempotent, not reported as generated a second time. The first sync ran
    # before scaffold_core_rules, so it rendered vendor mirrors from a
    # .gzkit/rules/ that did not exist yet -- 25 .claude/rules/, 25
    # .github/instructions/ and 8 nested AGENTS.md files were simply absent, and
    # a brand-new project failed `gz validate --surfaces` out of the box until
    # the operator ran a sync nobody told them about (GHI #908). The rules are on
    # disk by now, which is the state the comment above already anticipates for
    # "subsequent gz init --repair and gz agent sync runs". No second preflight:
    # only rules and hooks were written since the one above, never skills.
    sync_all(project_root, config)

    # Record init event
    ledger = Ledger(ledger_path)
    ledger.append(project_init_event(project_name, mode))

    # Register existing artifacts
    registered = _register_existing_artifacts(project_root, design_root, ledger, mode)
    if not registered:
        console.print("  (No existing artifacts to register)")

    console.print("\n[green]gzkit initialized successfully![/green]")
    console.print(f"\n  Scaffolded {len(skills)} skills (run gz skill list to see all)")
    console.print("\nNext steps:")
    console.print("  [bold]Skill (preferred)[/bold]         [dim]CLI equivalent[/dim]")
    console.print("  /gz-prd                    gz prd <name>")
    console.print("  /gz-plan                   gz plan create <name>")
    console.print("  /gz-status                 gz status")
    console.print("  /gz-check                  gz check")
    console.print(
        "\nSkills add interview logic, forcing functions, and governance"
        "\nvalidation that bare CLI commands do not. Use them when available."
        "\nSee: /user/skills/ in the docs or run gz skill list."
    )


def _canonicalize_prd_id(name: str) -> tuple[str, str]:
    r"""Normalize a user-supplied PRD name to the canonical ``PRD-<UPPER>-<semver>`` form.

    The validator schema at ``src/gzkit/schemas/prd.json`` requires
    ``^PRD-[A-Z0-9]+-[0-9]+\.[0-9]+\.[0-9]+$``. This function guarantees the
    scaffolder and validator agree on the id format (GHI #186).

    Returns ``(prd_id, semver)``.
    """
    stem = name[4:] if name.startswith("PRD-") else name
    semver = "1.0.0"
    trailing = stem.rsplit("-", 1)
    if len(trailing) == 2 and re.fullmatch(r"\d+\.\d+\.\d+", trailing[1]):
        stem, semver = trailing[0], trailing[1]
    slug = re.sub(r"[^A-Za-z0-9]", "", stem).upper()
    if not slug:
        raise SystemExit(f"Invalid PRD slug: {name!r} (need at least one alphanumeric character)")
    return f"PRD-{slug}-{semver}", semver


def prd(name: str, title: str | None, dry_run: bool) -> None:
    """Create a new PRD."""
    config = ensure_initialized()
    project_root = get_project_root()

    prd_id, semver = _canonicalize_prd_id(name)
    prd_title = title or prd_id

    # Render template
    content = render_template(
        "prd",
        **AUTHOR_PROMPTS["prd"],
        id=prd_id,
        title=prd_title,
        semver=semver,
        status="Draft",
        date=date.today().isoformat(),
    )

    prd_dir = project_root / config.paths.prd
    prd_file = prd_dir / f"{prd_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create PRD: {prd_file}")
        console.print(f"  Would append ledger event: prd_created ({prd_id})")
        return

    # Write file
    prd_dir.mkdir(parents=True, exist_ok=True)
    prd_file.write_text(content, encoding="utf-8")

    # Record event
    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(prd_created_event(prd_id))

    console.print(f"Created PRD: {prd_file}")


def _canonicalize_constitution_id(name: str) -> tuple[str, str]:
    r"""Normalize a user-supplied constitution name to ``CONSTITUTION-<UPPER>-<semver>``.

    The validator schema at ``src/gzkit/schemas/constitution.json`` requires
    ``^CONSTITUTION-[A-Z0-9]+-[0-9]+\.[0-9]+\.[0-9]+$``. This function guarantees
    the scaffolder and validator agree on id format (GHI #216 / GZKIT-BOOTSTRAP-008).

    Returns ``(constitution_id, semver)``.
    """
    stem = name[len("CONSTITUTION-") :] if name.startswith("CONSTITUTION-") else name
    semver = "1.0.0"
    trailing = stem.rsplit("-", 1)
    if len(trailing) == 2 and re.fullmatch(r"\d+\.\d+\.\d+", trailing[1]):
        stem, semver = trailing[0], trailing[1]
    slug = re.sub(r"[^A-Za-z0-9]", "", stem).upper()
    if not slug:
        raise SystemExit(
            f"Invalid constitution slug: {name!r} (need at least one alphanumeric character)"
        )
    return f"CONSTITUTION-{slug}-{semver}", semver


def constitute(name: str, title: str | None, dry_run: bool) -> None:
    """Create a new constitution."""
    config = ensure_initialized()
    project_root = get_project_root()

    constitution_id, semver = _canonicalize_constitution_id(name)
    constitution_title = title or constitution_id

    content = render_template(
        "constitution",
        id=constitution_id,
        title=constitution_title,
        semver=semver,
        status="Draft",
        date=date.today().isoformat(),
    )

    constitution_dir = project_root / config.paths.constitutions
    constitution_file = constitution_dir / f"{constitution_id}.md"

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  Would create constitution: {constitution_file}")
        console.print(f"  Would append ledger event: constitution_created ({constitution_id})")
        return

    constitution_dir.mkdir(parents=True, exist_ok=True)
    constitution_file.write_text(content, encoding="utf-8")

    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(constitution_created_event(constitution_id))

    console.print(f"Created constitution: {constitution_file}")
