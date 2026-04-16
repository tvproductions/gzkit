"""Patch release command: GHI discovery, cross-validation, manifest, and full ceremony.

Discovers closed GHIs since the latest git tag, cross-validates against
the ``runtime`` label and ``src/gzkit/`` diffs, classifies each GHI
for patch release qualification, and produces dual-format release manifests
(markdown + JSONL ledger entry).

With ``--full``, executes the complete release ceremony: bump, release-notes,
commit, push (with lint/test gates), and ``gh release create``.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import (
    GzCliError,
    _confirm,
    console,
    ensure_initialized,
    get_project_root,
)
from gzkit.commands.version_sync import (
    _read_current_project_version,
    compute_patch_increment,
    sync_project_version,
    validate_version_consistency,
)
from gzkit.ledger import Ledger
from gzkit.ledger_events import patch_release_event
from gzkit.utils import git_cmd, run_exec

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

GhiStatus = Literal["qualified", "label_only", "diff_only", "excluded"]


class GhiRecord(BaseModel):
    """A closed GitHub issue discovered for patch release consideration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    number: int = Field(..., description="GitHub issue number")
    title: str = Field(..., description="Issue title")
    closed_at: str = Field(..., description="ISO 8601 close timestamp")
    labels: list[str] = Field(default_factory=list, description="Label names")
    url: str = Field("", description="Issue HTML URL")


class GhiQualification(BaseModel):
    """A GHI with its cross-validation classification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ghi: GhiRecord = Field(..., description="The discovered GHI")
    has_runtime_label: bool = Field(..., description="True if 'runtime' label present")
    has_src_diff: bool = Field(..., description="True if commits touch src/gzkit/")
    status: GhiStatus = Field(..., description="Qualification outcome")
    warning: str | None = Field(None, description="Warning when label and diff disagree")


class DiscoveryResult(BaseModel):
    """Aggregated GHI discovery output."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tag: str | None = Field(None, description="Most recent git tag")
    tag_date: str | None = Field(None, description="ISO date of latest tag")
    ghi_count: int = Field(..., description="Total GHIs discovered")
    qualifications: list[GhiQualification] = Field(..., description="Per-GHI results")
    warnings: list[str] = Field(default_factory=list, description="Top-level warnings")
    current_version: str | None = Field(None, description="Current version from pyproject.toml")
    proposed_version: str | None = Field(None, description="Proposed patch version (Z+1)")


class ManifestGhi(BaseModel):
    """A GHI entry for the release manifest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    number: int = Field(..., description="GitHub issue number")
    title: str = Field(..., description="Issue title")
    status: GhiStatus = Field(..., description="Cross-validation classification")
    warning: str | None = Field(None, description="Warning when label and diff disagree")
    url: str = Field("", description="Issue HTML URL")


class PatchManifest(BaseModel):
    """Validated payload for a patch release manifest."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    version: str = Field(..., description="Patch release version")
    previous_version: str = Field(..., description="Version before this release")
    date: str = Field(..., description="Release date (ISO 8601)")
    tag: str | None = Field(None, description="Git tag of previous version")
    ghis: list[ManifestGhi] = Field(..., description="GHIs with cross-validation results")
    operator_approval: str = Field(
        "Approved by gz patch release", description="Operator approval text"
    )


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _ensure_gh_available(project_root: Path) -> None:
    """Verify ``gh`` CLI is installed and authenticated."""
    rc, _out, err = run_exec(["gh", "auth", "status"], cwd=project_root)
    if rc != 0:
        raise GzCliError(
            "BLOCKERS:\n"
            "  gh CLI is not authenticated.  Run `gh auth login` first.\n"
            f"  Detail: {err}"
        )


def _get_latest_tag(project_root: Path) -> tuple[str | None, str | None]:
    """Return ``(tag_name, iso_date)`` for the most recent tag, or ``(None, None)``."""
    rc, stdout, _err = git_cmd(
        project_root, "tag", "--sort=-creatordate", "--format=%(refname:short)"
    )
    if rc != 0 or not stdout.strip():
        return None, None

    tag_name = stdout.splitlines()[0].strip()

    rc_date, date_str, _err2 = git_cmd(project_root, "log", "-1", "--format=%aI", tag_name)
    if rc_date != 0 or not date_str.strip():
        return tag_name, None

    return tag_name, date_str.strip()


def _discover_ghis(project_root: Path, since_date: str | None) -> list[GhiRecord]:
    """Find closed GHIs via ``gh issue list``.

    When *since_date* is ``None`` (no tags), all closed GHIs are returned.
    """
    cmd: list[str] = [
        "gh",
        "issue",
        "list",
        "--state",
        "closed",
        "--json",
        "number,title,closedAt,labels,url",
        "--limit",
        "200",
    ]
    if since_date is not None:
        cmd.extend(["--search", f"closed:>{since_date[:10]}"])

    rc, stdout, _err = run_exec(cmd, cwd=project_root)
    if rc != 0 or not stdout.strip():
        return []

    try:
        items = json.loads(stdout)
    except json.JSONDecodeError:
        return []

    records: list[GhiRecord] = []
    for item in items:
        labels = [lbl["name"] for lbl in item.get("labels", []) if isinstance(lbl, dict)]
        records.append(
            GhiRecord(
                number=item["number"],
                title=item.get("title", ""),
                closed_at=item.get("closedAt", ""),
                labels=labels,
                url=item.get("url", ""),
            )
        )
    return records


def _ghi_has_src_commits(project_root: Path, ghi_number: int) -> bool:
    """Check whether any commits referencing *ghi_number* modified ``src/gzkit/``."""
    rc, stdout, _err = git_cmd(
        project_root,
        "log",
        "--all",
        "--grep",
        f"#{ghi_number}",
        "--format=%H",
        "--",
        "src/gzkit/",
    )
    return rc == 0 and bool(stdout.strip())


def _classify_ghi(project_root: Path, ghi: GhiRecord) -> GhiQualification:
    """Classify a GHI by cross-validating runtime label and src diff."""
    has_label = "runtime" in ghi.labels
    has_diff = _ghi_has_src_commits(project_root, ghi.number)

    if has_label and has_diff:
        status: GhiStatus = "qualified"
        warning = None
    elif has_label:
        status = "label_only"
        warning = f"GHI #{ghi.number} has 'runtime' label but no commits touching src/gzkit/"
    elif has_diff:
        status = "diff_only"
        warning = f"GHI #{ghi.number} has commits touching src/gzkit/ but no 'runtime' label"
    else:
        status = "excluded"
        warning = None

    return GhiQualification(
        ghi=ghi,
        has_runtime_label=has_label,
        has_src_diff=has_diff,
        status=status,
        warning=warning,
    )


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

_STATUS_STYLE: dict[str, str] = {
    "qualified": "[green]qualified[/green]",
    "label_only": "[yellow]label_only[/yellow]",
    "diff_only": "[yellow]diff_only[/yellow]",
    "excluded": "[dim]excluded[/dim]",
}


def _render_dry_run_rich(result: DiscoveryResult) -> None:
    """Render discovery result as human-readable Rich output."""
    console.print("[bold]Patch Release Discovery (dry run)[/bold]")
    if result.tag:
        console.print(f"  Latest tag: {result.tag} ({result.tag_date or 'unknown date'})")
    else:
        console.print("  Latest tag: [dim]none (all closed GHIs are candidates)[/dim]")
    if result.current_version and result.proposed_version:
        console.print(
            f"  Version: {result.current_version} -> {result.proposed_version} (proposed)"
        )
    elif result.current_version:
        console.print(f"  Version: {result.current_version} (cannot compute increment)")
    else:
        console.print("  Version: [dim]unknown (pyproject.toml unreadable)[/dim]")
    console.print(f"  GHIs discovered: {result.ghi_count}")
    console.print()

    for q in result.qualifications:
        styled = _STATUS_STYLE.get(q.status, q.status)
        line = f"  #{q.ghi.number:<6} {q.ghi.title:<40} {styled}"
        if q.warning:
            line += f"  [yellow]![/yellow] {q.warning}"
        console.print(line)

    if result.warnings:
        console.print()
        console.print("[bold yellow]Warnings:[/bold yellow]")
        for w in result.warnings:
            console.print(f"  [yellow]![/yellow] {w}")


def _render_json(result: DiscoveryResult) -> None:
    """Render discovery result as JSON to stdout."""
    print(json.dumps(result.model_dump(), indent=2))  # noqa: T201


# ---------------------------------------------------------------------------
# Manifest generation
# ---------------------------------------------------------------------------


def _render_manifest_markdown(manifest: PatchManifest) -> str:
    """Render a validated manifest as a markdown document."""
    lines: list[str] = [
        f"# Patch Release: v{manifest.version}",
        "",
        f"**Date:** {manifest.date}",
        f"**Previous Version:** {manifest.previous_version}",
        f"**Tag:** {manifest.tag or 'None'}",
        "",
        "## Qualifying GHIs",
        "",
        "| # | Title | Status | Warning |",
        "|---|-------|--------|---------|",
    ]
    for ghi in manifest.ghis:
        warning_cell = ghi.warning or ""
        lines.append(f"| {ghi.number} | {ghi.title} | {ghi.status} | {warning_cell} |")
    lines.extend(["", "## Operator Approval", "", manifest.operator_approval, ""])
    return "\n".join(lines)


def _write_manifest_atomic(project_root: Path, manifest: PatchManifest) -> Path:
    """Write the markdown manifest to ``docs/releases/``.

    Returns the relative path to the manifest file.
    """
    releases_dir = project_root / "docs" / "releases"
    releases_dir.mkdir(parents=True, exist_ok=True)
    filename = f"PATCH-v{manifest.version}.md"
    manifest_path = releases_dir / filename
    content = _render_manifest_markdown(manifest)
    manifest_path.write_text(content, encoding="utf-8")
    return Path("docs") / "releases" / filename


# ---------------------------------------------------------------------------
# Ceremony stages (commit, push, release)
# ---------------------------------------------------------------------------


def _author_release_notes(
    project_root: Path,
    version: str,
    qualifications: list[GhiQualification],
) -> str:
    """Generate and prepend a RELEASE_NOTES.md entry. Returns the entry text."""
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    qualified = [q for q in qualifications if q.status in ("qualified", "diff_only")]

    # Categorize GHIs by label
    fixed: list[str] = []
    changed: list[str] = []
    added: list[str] = []
    for q in qualified:
        labels = {lbl.lower() for lbl in q.ghi.labels}
        title = q.ghi.title
        entry = f"- **GHI #{q.ghi.number}:** {title}"
        if "defect" in labels or "bug" in labels:
            fixed.append(entry)
        elif "enhancement" in labels:
            added.append(entry)
        else:
            changed.append(entry)

    # Build the section
    lines = [f"## v{version} ({today})", ""]

    # Summary line from GHI titles
    ghi_refs = ", ".join(f"#{q.ghi.number}" for q in qualified)
    if ghi_refs:
        lines.append(f"**GHIs: {ghi_refs}**")
        lines.append("")

    if fixed:
        lines.append("### Fixed")
        lines.append("")
        lines.extend(fixed)
        lines.append("")
    if added:
        lines.append("### Added")
        lines.append("")
        lines.extend(added)
        lines.append("")
    if changed:
        lines.append("### Changed")
        lines.append("")
        lines.extend(changed)
        lines.append("")

    lines.append("---")
    lines.append("")
    entry_text = "\n".join(lines)

    # Prepend to RELEASE_NOTES.md after the h1 header
    rn_path = project_root / "RELEASE_NOTES.md"
    if rn_path.exists():
        content = rn_path.read_text(encoding="utf-8")
        # Insert after the first line (# gzkit Release Notes\n\n)
        header_match = re.match(r"^(# [^\n]*\n\n)", content)
        if header_match:
            header = header_match.group(1)
            rest = content[len(header) :]
            new_content = header + entry_text + rest
        else:
            new_content = entry_text + content
    else:
        new_content = "# gzkit Release Notes\n\n" + entry_text

    rn_path.write_text(new_content, encoding="utf-8")
    return entry_text


def _extract_latest_entry(project_root: Path) -> str:
    """Extract the latest release notes entry for use as gh release body."""
    rn_path = project_root / "RELEASE_NOTES.md"
    if not rn_path.exists():
        return ""
    content = rn_path.read_text(encoding="utf-8")
    # Find first ## vX.Y.Z section and extract until the next ---
    m = re.search(r"(## v\d+\.\d+\.\d+.*?)(?=\n---\n)", content, re.DOTALL)
    return m.group(1).strip() if m else ""


def _commit_release(project_root: Path, version: str) -> None:
    """Stage and commit the release changes."""
    # Stage the files that patch release touches
    files_to_stage = [
        "pyproject.toml",
        "uv.lock",
        "src/gzkit/__init__.py",
        "README.md",
        "RELEASE_NOTES.md",
        ".gzkit/ledger.jsonl",
    ]
    # Also stage any manifest files
    releases_dir = project_root / "docs" / "releases"
    if releases_dir.exists():
        files_to_stage.append("docs/releases/")

    for f in files_to_stage:
        path = project_root / f
        if path.exists():
            git_cmd(project_root, "add", f)

    rc, _out, err = git_cmd(
        project_root,
        "commit",
        "-m",
        f"release: v{version}",
    )
    if rc != 0:
        raise GzCliError(f"Commit failed: {err}")
    console.print(f"  Committed: release: v{version}")


def _push_release(project_root: Path) -> None:
    """Push to origin with lint/test gates via git-sync internals."""
    from gzkit.quality import run_lint, run_tests  # noqa: PLC0415

    # Pre-push gates
    lint_result = run_lint(project_root)
    if not lint_result.success:
        raise GzCliError("Lint failed. Fix before releasing.")
    console.print("  Lint: passed")

    test_result = run_tests(project_root)
    if not test_result.success:
        raise GzCliError("Tests failed. Fix before releasing.")
    console.print("  Tests: passed")

    rc, _out, err = git_cmd(project_root, "push", "origin", "main")
    if rc != 0:
        raise GzCliError(f"Push failed: {err}")
    console.print("  Pushed to origin/main")


def _create_gh_release(project_root: Path, version: str) -> str:
    """Create the GitHub release. Returns the release URL."""
    entry = _extract_latest_entry(project_root)
    tag = f"v{version}"
    cmd = [
        "gh",
        "release",
        "create",
        tag,
        "--target",
        "main",
        "--title",
        tag,
        "--latest",
        "--notes",
        entry,
    ]
    rc, stdout, err = run_exec(cmd, cwd=project_root)
    if rc != 0:
        raise GzCliError(f"gh release create failed: {err}")
    url = stdout.strip()
    console.print(f"  Release: {url}")
    return url


def _verify_release(project_root: Path, version: str) -> None:
    """Post-release verification: version consistency and tag exists."""
    errors = validate_version_consistency(project_root)
    if errors:
        for e in errors:
            console.print(f"  [red]Version mismatch: {e.message}[/red]")
        raise GzCliError("Version inconsistency after release.")

    rc, _out, _err = git_cmd(project_root, "tag", "-l", f"v{version}")
    if rc != 0 or not _out.strip():
        console.print(f"  [yellow]Warning: tag v{version} not found locally[/yellow]")
    else:
        console.print(f"  Tag v{version} verified")

    # Clean working tree check
    rc_st, stdout_st, _err_st = git_cmd(project_root, "status", "--porcelain")
    if rc_st == 0 and not stdout_st.strip():
        console.print("  Working tree: clean")
    else:
        console.print("  [yellow]Warning: working tree has uncommitted changes[/yellow]")


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------


def patch_release_cmd(*, dry_run: bool, as_json: bool, full: bool = False) -> None:
    """Run the patch release ceremony.

    Discovers qualifying GHIs, computes the next patch version, and
    (unless ``--dry-run``) bumps all version locations via
    ``sync_project_version``.
    """
    project_root = get_project_root()
    _ensure_gh_available(project_root)

    tag, tag_date = _get_latest_tag(project_root)
    ghis = _discover_ghis(project_root, tag_date)
    qualifications = [_classify_ghi(project_root, ghi) for ghi in ghis]

    current_version = _read_current_project_version(project_root)
    proposed_version = compute_patch_increment(current_version) if current_version else None

    top_warnings: list[str] = []
    if tag is None:
        top_warnings.append("No git tags found; all closed GHIs treated as candidates.")
    if current_version is None:
        top_warnings.append("Cannot read current version from pyproject.toml.")

    result = DiscoveryResult(
        tag=tag,
        tag_date=tag_date,
        ghi_count=len(qualifications),
        qualifications=qualifications,
        warnings=top_warnings,
        current_version=current_version,
        proposed_version=proposed_version,
    )

    if dry_run:
        if as_json:
            _render_json(result)
        else:
            _render_dry_run_rich(result)
        return

    # Execute: bump version via sync_project_version (REQ-01, REQ-02)
    if proposed_version is None:
        if as_json:
            _render_json(result)
        else:
            _render_dry_run_rich(result)
            console.print()
            console.print("[red]Cannot compute patch version (pyproject.toml unreadable).[/red]")
        raise SystemExit(1)

    # current_version is non-None here: proposed_version requires it
    assert current_version is not None

    updated_files = sync_project_version(project_root, proposed_version)

    # Build manifest (Pydantic validates — REQ-04)
    manifest_ghis = [
        ManifestGhi(
            number=q.ghi.number,
            title=q.ghi.title,
            status=q.status,
            warning=q.warning,
            url=q.ghi.url,
        )
        for q in qualifications
    ]
    manifest = PatchManifest(
        version=proposed_version,
        previous_version=current_version,
        date=datetime.now(UTC).strftime("%Y-%m-%d"),
        tag=tag,
        ghis=manifest_ghis,
    )

    # Write markdown manifest (REQ-01, REQ-03)
    manifest_rel = _write_manifest_atomic(project_root, manifest)

    # Append JSONL ledger entry (REQ-02)
    ghi_summary = [
        {"number": g.number, "title": g.title, "status": g.status, "warning": g.warning}
        for g in manifest_ghis
    ]
    event = patch_release_event(
        version=proposed_version,
        previous_version=current_version,
        tag=tag,
        ghi_summary=ghi_summary,
        manifest_path=str(manifest_rel),
    )
    config = ensure_initialized()
    ledger = Ledger(project_root / config.paths.ledger)
    ledger.append(event)

    if as_json:
        payload = result.model_dump()
        payload["version_sync"] = {"updated_files": updated_files}
        payload["manifest_path"] = str(manifest_rel)
        print(json.dumps(payload, indent=2))  # noqa: T201
        return

    _render_dry_run_rich(result)
    console.print()
    console.print(f"[green]Version bumped: {current_version} -> {proposed_version}[/green]")
    for f in updated_files:
        console.print(f"  Updated: {f}")
    console.print(f"  Manifest: {manifest_rel}")
    console.print("  Ledger: patch-release event appended")

    if not full:
        return

    # --- Full ceremony: release notes, commit, push, release, verify ---
    console.print()
    console.print("[bold]Release notes[/bold]")
    entry = _author_release_notes(project_root, proposed_version, qualifications)
    console.print(entry)

    if not _confirm("Proceed with commit, push, and GitHub release?"):
        console.print("[yellow]Aborted. Version bumped but not released.[/yellow]")
        console.print("  Edit RELEASE_NOTES.md manually, then:")
        console.print(f"  git add -A && git commit -m 'release: v{proposed_version}'")
        console.print("  git push origin main")
        console.print(
            f"  gh release create v{proposed_version} --target main"
            f" --title v{proposed_version} --latest"
            f" --notes-file RELEASE_NOTES.md"
        )
        return

    console.print()
    console.print("[bold]Committing[/bold]")
    _commit_release(project_root, proposed_version)

    console.print()
    console.print("[bold]Pushing (with gates)[/bold]")
    _push_release(project_root)

    console.print()
    console.print("[bold]Creating GitHub release[/bold]")
    _create_gh_release(project_root, proposed_version)

    console.print()
    console.print("[bold]Verifying[/bold]")
    _verify_release(project_root, proposed_version)

    console.print()
    console.print(f"[green bold]v{proposed_version} released successfully.[/green bold]")
