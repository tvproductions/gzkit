"""Chores command implementations (v2.0 registry format).

v2.0 uses a pointer-style registry where each chore has its own directory
containing CHORE.md (human workflow) and acceptance.json (machine criteria).
"""

from __future__ import annotations

import importlib.resources
import json
import re
from pathlib import Path
from typing import Literal

import structlog
from pydantic import BaseModel, ConfigDict
from rich.table import Table

from gzkit.commands.common import GzCliError, console, get_project_root
from gzkit.config import load_config

logger = structlog.get_logger(__name__)

CHORE_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_LANES = {"lite", "heavy"}
SHELL_OPERATORS_RE = re.compile(r"&&|\|\||[|<>]")


class AcceptanceCriterion(BaseModel):
    """Single acceptance criterion from a chore's acceptance.json."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    criterion_type: str
    command: str
    argv: tuple[str, ...]
    expected: int | None = None
    not_contains: str | None = None
    contains: str | None = None
    path: str | None = None
    description: str | None = None


class ChoreDefinition(BaseModel):
    """Validated chore definition loaded from v2.0 registry + acceptance.json."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str
    title: str
    lane: str
    version: str
    path: str
    criteria: tuple[AcceptanceCriterion, ...]
    timeout_seconds: int
    vendor: str | None = None
    resolution_source: Literal["project", "package"] | None = None


class ResolvedPath(BaseModel):
    """Result of a project-first / package-fallback resolution."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: Path
    source: Literal["project", "package"]


class CriterionResult(BaseModel):
    """Execution result for one acceptance criterion."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    criterion: AcceptanceCriterion
    passed: bool
    returncode: int
    duration_seconds: float
    stdout: str
    stderr: str
    detail: str


def _raise_blockers(blockers: list[str]) -> None:
    """Raise a user-facing BLOCKERS error."""
    if not blockers:
        return
    raise GzCliError("BLOCKERS:\n" + "\n".join(f"- {item}" for item in blockers))


_CRITERION_TYPES = frozenset(
    {
        "exitCodeEquals",
        "outputNotContains",
        "outputContains",
        "fileExists",
    }
)

# ---------------------------------------------------------------------------
# Extracted helpers live in chores_exec.py.  Import after models/constants
# are defined to avoid circular-import issues.
# ---------------------------------------------------------------------------
from gzkit.commands.chores_exec import (  # noqa: E402
    _evaluate_criterion,
    _log_path,
    _parse_chore_pointer,
    _write_chore_log,
)
from gzkit.commands.chores_propose_ghi_cmd import (  # noqa: E402
    chores_propose_ghi as chores_propose_ghi,
)


def _detect_active_harness() -> str | None:
    """Detect the active agent harness from project markers."""
    project_root = get_project_root()
    if (project_root / ".claude").is_dir():
        return "claude"
    return None


def _chore_matches_harness(chore: ChoreDefinition, active_harness: str | None) -> bool:
    """Return True if chore is applicable to the active harness."""
    if chore.vendor is None:
        return True
    if active_harness is None:
        return False
    return chore.vendor == active_harness


def _filter_registry(
    registry: dict[str, ChoreDefinition],
) -> dict[str, ChoreDefinition]:
    """Filter registry to chores matching the active harness."""
    harness = _detect_active_harness()
    return {slug: c for slug, c in registry.items() if _chore_matches_harness(c, harness)}


def _project_chores_root(project_root: Path) -> Path:
    """Return ``<project_root>/<config.paths.chores>``."""
    cfg = load_config()
    return project_root / cfg.paths.chores


def _package_chores_root() -> Path:
    """Return the package-resource root for ``gzkit.chores``."""
    return Path(str(importlib.resources.files("gzkit.chores")))


def _format_resolution_miss(
    item_label: str,
    project_candidate: Path,
    package_candidate: Path,
    paths_chores_setting: str,
) -> str:
    """Operator-facing message when both project and package paths miss."""
    return (
        f"Chore '{item_label}' not found in either resolution path:\n"
        f"  - project: {project_candidate} "
        f"(path: {paths_chores_setting}/{item_label})\n"
        f"  - package: importlib.resources('gzkit.chores')/{item_label} "
        f"(at {package_candidate})\n"
        f"Hint: run `gz init` to scaffold {paths_chores_setting}/, "
        "or verify the slug spelling."
    )


def _resolve_chore_dir(slug: str) -> ResolvedPath:
    """Resolve a chore directory by slug, project-first with package fallback."""
    project_root = get_project_root()
    project_candidate = _project_chores_root(project_root) / slug
    if (project_candidate / "acceptance.json").is_file():
        return ResolvedPath(path=project_candidate, source="project")

    package_candidate = _package_chores_root() / slug
    if (package_candidate / "acceptance.json").is_file():
        cfg = load_config()
        logger.info(
            "chore.resolver.fallback",
            slug=slug,
            project_path=str(project_candidate),
            package_path=str(package_candidate),
            paths_chores=cfg.paths.chores,
        )
        return ResolvedPath(path=package_candidate, source="package")

    cfg = load_config()
    raise GzCliError(  # noqa: TRY003
        _format_resolution_miss(slug, project_candidate, package_candidate, cfg.paths.chores)
    )


def _resolve_registry() -> ResolvedPath:
    """Resolve the chores registry path, project-first with package fallback."""
    project_root = get_project_root()
    project_candidate = _project_chores_root(project_root) / "registry.json"
    if project_candidate.is_file():
        return ResolvedPath(path=project_candidate, source="project")

    package_candidate = _package_chores_root() / "registry.json"
    if package_candidate.is_file():
        cfg = load_config()
        logger.info(
            "chore.resolver.fallback",
            slug="registry",
            project_path=str(project_candidate),
            package_path=str(package_candidate),
            paths_chores=cfg.paths.chores,
        )
        return ResolvedPath(path=package_candidate, source="package")

    cfg = load_config()
    raise GzCliError(  # noqa: TRY003
        _format_resolution_miss(
            "registry.json", project_candidate, package_candidate, cfg.paths.chores
        )
    )


def _load_chores_registry() -> tuple[Path, dict[str, ChoreDefinition]]:
    """Load and validate the v2.0 chores registry."""
    project_root = get_project_root()
    resolved_registry = _resolve_registry()
    registry_path = resolved_registry.path
    blockers: list[str] = []

    try:
        payload = json.loads(registry_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        blockers.append(f"Invalid JSON in {registry_path.as_posix()}: {exc.msg}")
        _raise_blockers(blockers)
        return registry_path, {}

    if not isinstance(payload, dict):
        blockers.append("Registry root must be a JSON object.")
        _raise_blockers(blockers)
        return registry_path, {}

    spec_version = payload.get("specVersion")
    if spec_version != "2.0":
        blockers.append("Registry specVersion must be '2.0'.")

    # Timeout is required per chore (GHI #447 — explicit timeouts, not lane-derived).
    # The lanes block carries gate-rigor metadata only (lite=Gates 1,2; heavy=all).
    chores_raw = payload.get("chores")
    if not isinstance(chores_raw, list) or not chores_raw:
        blockers.append("Registry field 'chores' must be a non-empty array.")
        _raise_blockers(blockers)
        return registry_path, {}

    registry: dict[str, ChoreDefinition] = {}
    for idx, raw_chore in enumerate(chores_raw):
        chore = _parse_chore_pointer(
            raw_chore,
            idx,
            project_root,
            blockers,
        )
        if chore is None:
            continue
        if chore.slug in registry:
            blockers.append(f"Duplicate chore slug: {chore.slug}")
            continue
        registry[chore.slug] = chore

    _raise_blockers(blockers)
    return registry_path, registry


def _resolve_chore(slug: str) -> tuple[Path, ChoreDefinition]:
    """Resolve one chore by slug from the validated registry."""
    registry_path, registry = _load_chores_registry()
    chore = registry.get(slug)
    if chore is None:
        msg = f"BLOCKERS:\n- Unknown chore slug: {slug}"
        raise GzCliError(msg)  # noqa: TRY003
    harness = _detect_active_harness()
    if not _chore_matches_harness(chore, harness):
        msg = (
            f"BLOCKERS:\n- Chore '{slug}' is vendor-scoped to '{chore.vendor}' "
            f"but active harness is '{harness or 'none'}'"
        )
        raise GzCliError(msg)  # noqa: TRY003
    return registry_path, chore


def _explain_source(chore: ChoreDefinition) -> str:
    """Render the Source column cell for `chores list --explain`."""
    if chore.resolution_source == "package":
        return "package (fallback; scaffolder may need re-run)"
    if chore.resolution_source == "project":
        return "project"
    return "missing"


def chores_list(*, explain: bool = False) -> None:
    """List chore definitions from registry."""
    _registry_path, registry = _load_chores_registry()
    registry = _filter_registry(registry)
    table = Table(title="Chores Registry")
    table.add_column("Slug", style="cyan")
    table.add_column("Lane", style="green")
    table.add_column("Version")
    table.add_column("Vendor")
    table.add_column("Criteria", justify="right")
    table.add_column("Title")
    if explain:
        table.add_column("Source")

    for chore in sorted(registry.values(), key=lambda item: item.slug):
        row = [
            chore.slug,
            chore.lane,
            chore.version,
            chore.vendor or "",
            str(len(chore.criteria)),
            chore.title,
        ]
        if explain:
            row.append(_explain_source(chore))
        table.add_row(*row)

    console.print(table)


def chores_plan(slug: str) -> None:
    """Render deterministic plan details for one chore."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)
    log_path = _log_path(project_root, chore)

    console.print(f"[bold]Chore Plan: {chore.slug}[/bold]")
    console.print(f"  Title: {chore.title}")
    console.print(f"  Lane: {chore.lane}")
    console.print(f"  Version: {chore.version}")
    console.print(f"  Path: {chore.path}")
    console.print(f"  Log: {log_path.relative_to(project_root).as_posix()}")
    console.print("  Acceptance Criteria:")
    for idx, c in enumerate(chore.criteria, start=1):
        desc = f" -- {c.description}" if c.description else ""
        if c.criterion_type == "exitCodeEquals":
            console.print(f"    {idx}. [{c.criterion_type}] `{c.command}` == {c.expected}{desc}")
        elif c.criterion_type == "outputNotContains":
            console.print(
                f"    {idx}. [{c.criterion_type}] "
                f"`{c.command}` must not contain "
                f"'{c.not_contains}'{desc}"
            )
        elif c.criterion_type == "outputContains":
            console.print(
                f"    {idx}. [{c.criterion_type}] `{c.command}` must contain '{c.contains}'{desc}"
            )
        elif c.criterion_type == "fileExists":
            console.print(f"    {idx}. [{c.criterion_type}] path: `{c.path}`{desc}")
        else:
            console.print(f"    {idx}. [{c.criterion_type}] `{c.command}`{desc}")


def chores_show(slug: str) -> None:
    """Display the CHORE.md content for one chore."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)
    chore_md = project_root / chore.path / "CHORE.md"
    if not chore_md.is_file():
        msg = f"BLOCKERS:\n- Missing CHORE.md: {chore.path}/CHORE.md"
        raise GzCliError(msg)  # noqa: TRY003
    console.print(chore_md.read_text(encoding="utf-8"))


def chores_advise(slug: str) -> None:
    """Dry-run acceptance criteria and report actionable status."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)

    console.print(f"[bold]Chore Advice: {chore.slug}[/bold]")
    console.print(f"  Lane: {chore.lane}  |  Version: {chore.version}")
    console.print()

    all_pass = True
    for idx, criterion in enumerate(chore.criteria, start=1):
        result = _evaluate_criterion(
            criterion,
            project_root,
            chore.timeout_seconds,
        )
        mark = "[green]PASS[/green]" if result.passed else "[red]FAIL[/red]"
        console.print(
            f"  {idx}. {mark}  `{criterion.command}` "
            f"({result.duration_seconds:.1f}s) -- {result.detail}"
        )
        if not result.passed:
            all_pass = False

    console.print()
    if all_pass:
        console.print(
            "[green]All criteria pass.[/green] Run `gz chores run " + slug + "` to log the result."
        )
    else:
        console.print(
            "[yellow]Some criteria failed.[/yellow] "
            "Read the CHORE.md workflow for remediation steps:"
        )
        chore_md = project_root / chore.path / "CHORE.md"
        console.print(f"  {chore_md.relative_to(project_root).as_posix()}")


def chores_run(slug: str) -> None:
    """Execute one chore's acceptance criteria and log results."""
    project_root = get_project_root()
    _registry_path, chore = _resolve_chore(slug)
    results: list[CriterionResult] = []

    for criterion in chore.criteria:
        result = _evaluate_criterion(
            criterion,
            project_root,
            chore.timeout_seconds,
        )
        results.append(result)

        if not result.passed:
            log_path = _write_chore_log(
                project_root,
                chore,
                "FAIL",
                results,
            )
            msg = (
                "Chore criterion failed:\n"
                f"- chore: {chore.slug}\n"
                f"- criterion: {result.criterion.command}\n"
                f"- detail: {result.detail}\n"
                f"- log: "
                f"{log_path.relative_to(project_root).as_posix()}"
            )
            raise GzCliError(msg)  # noqa: TRY003

    log_path = _write_chore_log(project_root, chore, "PASS", results)
    console.print(
        f"[green]Chore completed.[/green] log: {log_path.relative_to(project_root).as_posix()}"
    )


_PER_SLUG_CHORE_FILES = ("CHORE.md", "acceptance.json", "README.md")
_DOCTOR_STATUS_HEALTHY = "HEALTHY"
_DOCTOR_STATUS_MISSING = "MISSING"
_DOCTOR_STATUS_DAMAGED = "DAMAGED"
_DOCTOR_STATUS_PROJECT_LOCAL = "PROJECT-LOCAL"


def _canonical_chore_slugs() -> list[str]:
    """Return the canonical chore slugs shipped in the gzkit.chores package."""
    root = importlib.resources.files("gzkit.chores")
    slugs: list[str] = []
    for entry in root.iterdir():
        if not entry.is_dir() or entry.name.startswith("__"):
            continue
        if entry.joinpath("CHORE.md").is_file():
            slugs.append(entry.name)
    return sorted(slugs)


def _classify_doctor_slug(slug: str, *, in_canonical: bool, project_dir: Path) -> str:
    """Classify a slug as HEALTHY / MISSING / DAMAGED / PROJECT-LOCAL."""
    if not in_canonical:
        return _DOCTOR_STATUS_PROJECT_LOCAL
    if not project_dir.is_dir():
        return _DOCTOR_STATUS_MISSING
    for filename in _PER_SLUG_CHORE_FILES:
        candidate = project_dir / filename
        if not candidate.is_file():
            return _DOCTOR_STATUS_DAMAGED
    acceptance_path = project_dir / "acceptance.json"
    try:
        json.loads(acceptance_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return _DOCTOR_STATUS_DAMAGED
    return _DOCTOR_STATUS_HEALTHY


def _repair_damaged_doctor_slug(slug: str, project_dir: Path) -> None:
    """Restore canonical per-slug files inside an existing project slug directory.

    Only files in `_PER_SLUG_CHORE_FILES` that are missing or whose canonical
    counterpart differs by bytes are rewritten. `proofs/` is never touched
    because it is not in `_PER_SLUG_CHORE_FILES`.
    """
    canonical_root = importlib.resources.files("gzkit.chores").joinpath(slug)
    for filename in _PER_SLUG_CHORE_FILES:
        source = canonical_root.joinpath(filename)
        if not source.is_file():
            continue
        target = project_dir / filename
        try:
            existing = target.read_bytes() if target.is_file() else None
        except OSError:
            existing = None
        canonical_bytes = source.read_bytes()
        if existing != canonical_bytes:
            target.write_bytes(canonical_bytes)


def _render_doctor_table(rows: list[dict[str, str]]) -> None:
    """Render the doctor summary as a Rich table to console."""
    table = Table(title="Chore Doctor")
    table.add_column("Slug", style="cyan")
    table.add_column("Before")
    table.add_column("After")
    for row in rows:
        table.add_row(row["slug"], row["before_status"], row["after_status"])
    console.print(table)

    counts = {
        "repaired": sum(
            1
            for row in rows
            if row["before_status"] in (_DOCTOR_STATUS_MISSING, _DOCTOR_STATUS_DAMAGED)
            and row["after_status"] == _DOCTOR_STATUS_HEALTHY
        ),
        "healthy": sum(1 for row in rows if row["before_status"] == _DOCTOR_STATUS_HEALTHY),
        "project-local": sum(
            1 for row in rows if row["before_status"] == _DOCTOR_STATUS_PROJECT_LOCAL
        ),
        "damaged-remaining": sum(
            1 for row in rows if row["after_status"] == _DOCTOR_STATUS_DAMAGED
        ),
    }
    console.print(
        f"{counts['repaired']} repaired, {counts['healthy']} healthy, "
        f"{counts['project-local']} project-local, "
        f"{counts['damaged-remaining']} damaged-remaining."
    )


def chores_doctor(*, dry_run: bool = False, json_output: bool = False) -> None:
    """Re-scaffold missing or damaged canonical chores; preserve proofs/ and project-local."""
    from gzkit.chores import scaffold_core_chores

    project_root = get_project_root()
    chores_root = _project_chores_root(project_root)
    chores_root.mkdir(parents=True, exist_ok=True)

    canonical_slugs = set(_canonical_chore_slugs())
    project_slugs = (
        {p.name for p in chores_root.iterdir() if p.is_dir()} if chores_root.is_dir() else set()
    )
    all_slugs = sorted(canonical_slugs | project_slugs)

    before_states: dict[str, str] = {}
    for slug in all_slugs:
        before_states[slug] = _classify_doctor_slug(
            slug,
            in_canonical=slug in canonical_slugs,
            project_dir=chores_root / slug,
        )

    if not dry_run:
        config = load_config()
        scaffold_core_chores(project_root, config, skip_existing=True)
        for slug, status in before_states.items():
            if status == _DOCTOR_STATUS_DAMAGED:
                _repair_damaged_doctor_slug(slug, chores_root / slug)

    rows: list[dict[str, str]] = []
    for slug in all_slugs:
        before = before_states[slug]
        if dry_run:
            after = (
                _DOCTOR_STATUS_HEALTHY
                if before in (_DOCTOR_STATUS_MISSING, _DOCTOR_STATUS_DAMAGED)
                else before
            )
        else:
            after = _classify_doctor_slug(
                slug,
                in_canonical=slug in canonical_slugs,
                project_dir=chores_root / slug,
            )
        rows.append({"slug": slug, "before_status": before, "after_status": after})

    if json_output:
        console.print(json.dumps(rows))
        return
    _render_doctor_table(rows)


def chores_audit(*, all_chores: bool, slug: str | None) -> None:
    """Audit chores for log presence."""
    project_root = get_project_root()
    _registry_path, registry = _load_chores_registry()
    registry = _filter_registry(registry)

    if all_chores:
        chores = sorted(registry.values(), key=lambda item: item.slug)
    else:
        if not slug:
            msg = "BLOCKERS:\n- Provide --all or --slug <slug>."
            raise GzCliError(msg)  # noqa: TRY003
        chore = registry.get(slug)
        if chore is None:
            msg = f"BLOCKERS:\n- Unknown chore slug: {slug}"
            raise GzCliError(msg)  # noqa: TRY003
        chores = [chore]

    table = Table(title="Chores Audit")
    table.add_column("Slug", style="cyan")
    table.add_column("Lane", style="green")
    table.add_column("Has Log")
    table.add_column("Log Path")

    for chore in chores:
        log = _log_path(project_root, chore)
        has_log = "yes" if log.exists() else "no"
        rel_path = log.relative_to(project_root).as_posix()
        table.add_row(chore.slug, chore.lane, has_log, rel_path)

    console.print(table)
