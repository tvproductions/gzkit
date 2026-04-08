"""Patch release command: GHI discovery and cross-validation.

Discovers closed GHIs since the latest git tag, cross-validates against
the ``runtime`` label and ``src/gzkit/`` diffs, and classifies each GHI
for patch release qualification.

Full release execution (version sync, manifests, ceremony) arrives in
OBPI-0.0.15-03 through OBPI-0.0.15-06.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.commands.common import GzCliError, console, get_project_root
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
# Entry point
# ---------------------------------------------------------------------------


def patch_release_cmd(*, dry_run: bool, as_json: bool) -> None:
    """Run the patch release ceremony.

    Currently implements GHI discovery and cross-validation (OBPI-02).
    Full release execution arrives in later OBPIs.
    """
    project_root = get_project_root()
    _ensure_gh_available(project_root)

    tag, tag_date = _get_latest_tag(project_root)
    ghis = _discover_ghis(project_root, tag_date)
    qualifications = [_classify_ghi(project_root, ghi) for ghi in ghis]

    top_warnings: list[str] = []
    if tag is None:
        top_warnings.append("No git tags found; all closed GHIs treated as candidates.")

    result = DiscoveryResult(
        tag=tag,
        tag_date=tag_date,
        ghi_count=len(qualifications),
        qualifications=qualifications,
        warnings=top_warnings,
    )

    if as_json:
        _render_json(result)
        return

    if dry_run:
        _render_dry_run_rich(result)
        return

    # Non-dry-run: show discovery then note that full execution is deferred
    _render_dry_run_rich(result)
    console.print()
    console.print(
        "[yellow]Full release execution (version sync, manifests, ceremony) "
        "arrives in later OBPIs.[/yellow]"
    )
