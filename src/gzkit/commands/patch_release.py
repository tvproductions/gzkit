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
from rich.markup import escape

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
from gzkit.mx import hardening
from gzkit.utils import git_cmd, run_exec

# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------

GhiStatus = Literal[
    "qualified",
    "label_only",
    "diff_only",
    "open_upstream",
    "unclassified_reference",
    "excluded",
]


class GhiRecord(BaseModel):
    """A GitHub issue discovered for patch release consideration."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    number: int = Field(..., description="GitHub issue number")
    title: str = Field(..., description="Issue title")
    closed_at: str = Field(..., description="ISO 8601 close timestamp")
    labels: list[str] = Field(default_factory=list, description="Label names")
    url: str = Field("", description="Issue HTML URL")
    state: str = Field("", description="Upstream issue state (OPEN/CLOSED); empty if unknown")


class GhiQualification(BaseModel):
    """A GHI with its cross-validation classification."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    ghi: GhiRecord = Field(..., description="The discovered GHI")
    has_runtime_label: bool = Field(..., description="True if 'runtime' label present")
    has_src_diff: bool = Field(..., description="True if commits touch src/gzkit/")
    status: GhiStatus = Field(..., description="Qualification outcome")
    warning: str | None = Field(None, description="Warning when label and diff disagree")


class FoundationCloseout(BaseModel):
    """A foundation ADR validated since the last tag — a release-worthy port closeout.

    Per the hexagonal port/adapter doctrine
    (``docs/governance/hexagonal-architecture.md``), foundation ADRs ship
    code surfaces — validators, runtime engines, schemas — exactly as feature
    ADRs do. A foundation closeout is therefore a patch-release qualifier in
    its own right, enumerated mechanically alongside behavior-level GHIs
    rather than left to operator memory (GHI #490; completes the GHI #330
    residual CLI-enumeration TODO).
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str = Field(..., description="Foundation ADR identifier")
    semver: str = Field(..., description="Foundation semver (0.0.x)")
    validated_at: str = Field(..., description="ISO 8601 timestamp of the Gate-5 validated receipt")
    anchor_commit: str = Field("", description="Commit anchor recorded on the closeout receipt")


class DiscoveryResult(BaseModel):
    """Aggregated GHI discovery output."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    tag: str | None = Field(None, description="Most recent git tag")
    tag_date: str | None = Field(None, description="ISO date of latest tag")
    ghi_count: int = Field(..., description="Total GHIs discovered")
    qualifications: list[GhiQualification] = Field(..., description="Per-GHI results")
    foundation_closeouts: list[FoundationCloseout] = Field(
        default_factory=list, description="Foundation ADRs validated since the last tag"
    )
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
    foundation_closeouts: list[FoundationCloseout] = Field(
        default_factory=list, description="Foundation ADR closeouts qualifying this release"
    )
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


def _discover_ghis(project_root: Path, base_ref: str | None) -> list[GhiRecord]:
    """Find closed GHIs referenced by commits in ``<base_ref>..HEAD``.

    GHI #233 doctrine: a GHI ships in v_n if and only if its closure commit
    is in the release range. Close-time windows are post-hoc reconstruction
    and double-count GHIs shipped in the prior tag. This discovery:

    1. Walks ``git log <base_ref>..HEAD`` and extracts GHI references from
       commit messages (``#N``, ``(GHI #N)``, ``Closes #N``).
    2. For each referenced GHI, calls ``gh issue view N`` to pull metadata.
    3. Filters out GHIs that are not currently ``state=CLOSED`` — an
       in-flight GHI mentioned in a commit but not yet closed is not
       release-ready.

    When *base_ref* is ``None`` (no prior tag), walks all history.
    """
    in_range_refs = _collect_ghi_refs_in_range(project_root, base_ref)
    if not in_range_refs:
        return []

    # A commit in ``<base_ref>..HEAD`` with a closure marker is authoritative
    # for *discovery*: shipping the release may close the GHI on push, and a
    # locally-committed fix awaiting push still reads ``state=OPEN`` upstream.
    # So do not filter by GitHub state here — every marked GHI is collected
    # (GHI #233 doctrine: we count what we CLOSE at the commit level, not what
    # GitHub currently says about state).
    #
    # Upstream state is consulted one layer down, in ``_classify_ghi``, where
    # an OPEN GHI is downgraded to the ``open_upstream`` warned bucket rather
    # than dropped. The marker cannot distinguish "awaiting push" from "work
    # under a still-open tracker", so the operator adjudicates (GHI #714).
    return _fetch_ghi_records(project_root, in_range_refs)


def _fetch_ghi_records(project_root: Path, numbers: set[int]) -> list[GhiRecord]:
    """Pull upstream metadata for *numbers*, sorted ascending.

    Shared by the closure path (:func:`_discover_ghis`) and the disclosure
    path (GHI #794), so an unclassified reference arrives carrying the same
    title, labels, and state the operator needs to adjudicate it — a bare
    number would move the investigation off the report and back into
    ``gh issue view``.
    """
    records: list[GhiRecord] = []
    for number in sorted(numbers):
        cmd = [
            "gh",
            "issue",
            "view",
            str(number),
            "--json",
            "number,title,closedAt,labels,state,url",
        ]
        rc, stdout, _err = run_exec(cmd, cwd=project_root)
        if rc != 0 or not stdout.strip():
            continue
        try:
            item = json.loads(stdout)
        except json.JSONDecodeError:
            continue
        labels = [lbl["name"] for lbl in item.get("labels", []) if isinstance(lbl, dict)]
        records.append(
            GhiRecord(
                number=item["number"],
                title=item.get("title", ""),
                closed_at=item.get("closedAt") or "",
                labels=labels,
                url=item.get("url", ""),
                state=item.get("state") or "",
            )
        )
    return records


# Two closure forms are recognized (GHI #280):
#
# 1. GitHub-canonical body trailers: ``Closes #N`` / ``Fixes #N`` / ``Resolves
#    #N``. Anchored by verb, not by position, so it matches wherever the
#    trailer lives in the commit body.
# 2. Project-canonical subject form: ``fix(<scope>): <summary> (GHI #N)`` and
#    ``feat(<scope>): <summary> (GHI #N)`` (and ``perf``/``refactor``/
#    ``revert`` Conventional-Commits types that carry code-change intent).
#    The cc-prefix at subject position is the closure signal — bare ``(GHI
#    #N)`` in body prose is still a citation (design commits like
#    ``docs(adr): ... (GHI #218)`` reference a GHI for context without
#    closing it; ceremony-body list items like ``(GHI #219): REQ-...`` are
#    also citations, not closures).
#
# Non-code cc-prefixes (``docs``, ``chore``, ``ceremony``, ``audit``,
# ``test``, ``style``, ``build``, ``ci``) are excluded from the subject
# form on purpose: those commits document or ceremonialize GHI work that
# was closed by a separate code-change commit. Counting them would
# double-count and re-introduce the GHI #233 drift the body regex was
# written to prevent.
_GHI_CLOSURE_PATTERN = re.compile(
    r"(?:close[sd]?|fix(?:e[sd])?|resolve[sd]?)\s+#(\d+)",
    re.IGNORECASE,
)
# The multi-issue tail admits both live spellings — `(GHI #1, #2)` and
# `(GHI #1, GHI #2)`. Neither is prescribed and both occur, so a pattern
# recognizing only one drops the other's GHIs (GHI #794).
_GHI_MULTI_ISSUE_TAIL = r"\(GHI\s+(#\d+(?:\s*,\s*(?:GHI\s+)?#\d+)*)\)\s*$"

_GHI_SUBJECT_CLOSURE_TYPES = ("fix", "feat", "perf", "refactor", "revert")
_GHI_SUBJECT_CLOSURE_PATTERN = re.compile(
    r"^(?:"
    + "|".join(_GHI_SUBJECT_CLOSURE_TYPES)
    + r")(?:\([^)]*\))?!?:\s+.*"
    + _GHI_MULTI_ISSUE_TAIL
)
# The same tail under ANY Conventional-Commits type: group(1) is the type,
# group(2) the number list. Single-sourced from the tail above so the
# disclosure side cannot drift from the counting side (GHI #794).
_GHI_SUBJECT_ANY_TYPE_PATTERN = re.compile(
    r"^([a-z]+)(?:\([^)]*\))?!?:\s+.*" + _GHI_MULTI_ISSUE_TAIL
)
_GHI_NUMBER_PATTERN = re.compile(r"#(\d+)")


def _collect_ghi_refs_in_range(project_root: Path, base_ref: str | None) -> set[int]:
    """Extract GHI numbers referenced by commits in ``<base_ref>..HEAD``.

    When *base_ref* is ``None`` (no tags), walks all history. This is the
    release-range anchor for patch-release discovery (GHI #233): a GHI ships
    in v_n if and only if its closure commit is in the ``v_(n-1)..HEAD``
    range. Close-time windows are post-hoc reconstruction and double-count
    GHIs shipped in the prior tag.
    """
    log_args = ["log", "--format=%H%n%B%x00"]
    if base_ref is not None:
        log_args.append(f"{base_ref}..HEAD")
    rc, stdout, _err = git_cmd(project_root, *log_args)
    if rc != 0 or not stdout:
        return set()

    refs: set[int] = set()
    for commit_blob in stdout.split("\x00"):
        commit_blob = commit_blob.strip("\n")
        if not commit_blob:
            continue
        # Format is: SHA\n<subject>\n<body>. Split off SHA, then split
        # subject from body so the subject-closure regex is anchored to
        # the first message line only.
        _sha, _, message = commit_blob.partition("\n")
        subject, _, body = message.partition("\n")

        subject_match = _GHI_SUBJECT_CLOSURE_PATTERN.match(subject)
        if subject_match is not None:
            for num_match in _GHI_NUMBER_PATTERN.finditer(subject_match.group(1)):
                refs.add(int(num_match.group(1)))

        for match in _GHI_CLOSURE_PATTERN.finditer(body):
            refs.add(int(match.group(1)))
    return refs


def _collect_unclassified_ghi_refs_in_range(
    project_root: Path, base_ref: str | None, closure_refs: set[int]
) -> set[int]:
    """Extract GHIs cited in range that no closure rule claimed (GHI #794).

    A GHI whose only in-range commit carries a non-closure Conventional-
    Commits type is invisible to :func:`_collect_ghi_refs_in_range` —
    ``chore(deps)`` for a dependency upgrade, ``docs(adr)`` for a finding
    routed to a pool ADR. Every qualification bucket is computed FROM that
    set, so the omission renders as a shorter list rather than a warning:
    there was no state for *referenced but unclassifiable*.

    This is **disclosure, not a widening of the closure types.** Admitting
    ``chore`` as a closure would re-import the GHI #233 double-counting the
    exclusion exists to prevent; whether such a commit shipped release
    content is the operator's call, made per GHI, not the collector's.

    Two narrowings keep the bucket quiet enough to read:

    1. **Subject tail only.** Body-prose citations are the GHI #233 noise
       the closure regex was written to exclude; admitting them here would
       re-import it on the disclosure side.
    2. **Dedup against *closure_refs*.** A citation alongside a real
       closure is the normal case — a ``fix(...)`` remedy plus a
       ``docs(...)`` commit naming the same GHI. Measured over five
       releases, these two narrowings yield ~1.4 reports per release.
    """
    log_args = ["log", "--format=%H%n%B%x00"]
    if base_ref is not None:
        log_args.append(f"{base_ref}..HEAD")
    rc, stdout, _err = git_cmd(project_root, *log_args)
    if rc != 0 or not stdout:
        return set()

    cited: set[int] = set()
    for commit_blob in stdout.split("\x00"):
        commit_blob = commit_blob.strip("\n")
        if not commit_blob:
            continue
        _sha, _, message = commit_blob.partition("\n")
        subject, _, _body = message.partition("\n")

        match = _GHI_SUBJECT_ANY_TYPE_PATTERN.match(subject)
        if match is None or match.group(1) in _GHI_SUBJECT_CLOSURE_TYPES:
            continue
        for num_match in _GHI_NUMBER_PATTERN.finditer(match.group(2)):
            cited.add(int(num_match.group(1)))
    return cited - closure_refs


def _ghi_has_src_commits(project_root: Path, ghi_number: int, base_ref: str | None) -> bool:
    """Check whether commits referencing *ghi_number* modified ``src/gzkit/``.

    Scoped to ``<base_ref>..HEAD`` when a prior tag exists, otherwise falls
    back to ``--all``. Per GHI #233: release discovery must anchor on the
    commit range, not repo-wide history, so a GHI whose closure commit
    landed in a prior tag does not re-qualify for the next release.
    """
    log_args: list[str] = ["log"]
    if base_ref is None:
        log_args.append("--all")
    else:
        log_args.append(f"{base_ref}..HEAD")
    log_args.extend(["--grep", f"#{ghi_number}", "--format=%H", "--", "src/gzkit/"])
    rc, stdout, _err = git_cmd(project_root, *log_args)
    return rc == 0 and bool(stdout.strip())


def _classify_ghi(project_root: Path, ghi: GhiRecord, base_ref: str | None) -> GhiQualification:
    """Classify a GHI by cross-validating runtime label and src diff in range."""
    has_label = "runtime" in ghi.labels
    has_diff = _ghi_has_src_commits(project_root, ghi.number, base_ref)

    if has_label and has_diff:
        # The commit marker qualified it, but a GHI still OPEN upstream has not
        # declared closure — the subject form ``fix(<scope>): … (GHI #N)`` is
        # AGENTS.md § Defect-fix routing's scope anchor for *any* GHI-tracked
        # repair, including incremental work under a deliberately-open tracker.
        # Downgrade to a warned bucket so the operator adjudicates rather than
        # the manifest asserting a closure that has not happened (GHI #714).
        if ghi.state == "OPEN":
            status: GhiStatus = "open_upstream"
            warning = (
                f"GHI #{ghi.number} qualifies on commit markers but is still OPEN "
                f"upstream; confirm this release closes it before counting it"
            )
        else:
            status = "qualified"
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


def _classify_unclassified_reference(
    project_root: Path, ghi: GhiRecord, base_ref: str | None
) -> GhiQualification:
    """Build the disclosure-bucket entry for a cited-but-unclaimed GHI (GHI #794).

    The label and src-diff facts are still computed — they are what the
    operator reads to decide whether the citing commit shipped release
    content — but they do not select the status. The bucket's claim is
    narrower than the other four: not *this qualifies* or *this is
    excluded*, only *no closure rule matched this, and you should look*.
    """
    return GhiQualification(
        ghi=ghi,
        has_runtime_label="runtime" in ghi.labels,
        has_src_diff=_ghi_has_src_commits(project_root, ghi.number, base_ref),
        status="unclassified_reference",
        warning=(
            f"GHI #{ghi.number} is cited in range by a commit whose type is not a "
            f"closure type; no closure commit claims it. Adjudicate per SKILL.md "
            f"§ Step 1c before publishing"
        ),
    )


def _build_qualifications(project_root: Path, base_ref: str | None) -> list[GhiQualification]:
    """Assemble every bucket for the release range, sorted by GHI number.

    Two passes, in order, because the second depends on the first: closure
    classification establishes which GHIs a closure commit claims, and the
    disclosure pass (GHI #794) reports only what is left over. Running them
    the other way round would warn on the normal case — a ``fix(...)``
    remedy plus a ``docs(...)`` commit naming the same GHI.
    """
    closure = [
        _classify_ghi(project_root, ghi, base_ref) for ghi in _discover_ghis(project_root, base_ref)
    ]
    unclassified = _collect_unclassified_ghi_refs_in_range(
        project_root, base_ref, {q.ghi.number for q in closure}
    )
    disclosed = [
        _classify_unclassified_reference(project_root, record, base_ref)
        for record in _fetch_ghi_records(project_root, unclassified)
    ]
    return sorted(closure + disclosed, key=lambda q: q.ghi.number)


# A foundation ADR carries a 0.0.x semver (AGENTS.md § Kinds). The patch-Z
# component is unbounded; the major/minor components are pinned to 0.0.
_FOUNDATION_SEMVER_RE = re.compile(r"^0\.0\.\d+$")


def _parse_ts(value: str | None) -> datetime | None:
    """Parse an ISO 8601 timestamp to a tz-aware datetime; ``None`` if unparseable.

    A naive timestamp (no offset — e.g. a date-only ``tag_date``) is assumed
    UTC so it compares cleanly against the tz-aware ledger receipt timestamps.
    """
    if not value:
        return None
    try:
        parsed = datetime.fromisoformat(value)
    except ValueError:
        return None
    return parsed.replace(tzinfo=UTC) if parsed.tzinfo is None else parsed


def _semver_key(semver: str) -> tuple[int, ...]:
    """Sort key for semantic (not lexical) version ordering — 0.0.9 before 0.0.15."""
    try:
        return tuple(int(part) for part in semver.split("."))
    except ValueError:
        return (0,)


def _discover_foundation_closeouts(
    ledger: Ledger, tag_date: str | None
) -> list[FoundationCloseout]:
    """Find foundation ADRs that reached Validated since the last tag.

    A foundation closeout is a Gate-5 ``audit_receipt_emitted`` ledger event
    with ``receipt_event == "validated"`` whose anchor semver is a foundation
    (``0.0.x``) version. Scoped to the release range by receipt timestamp:
    receipts at or before *tag_date* shipped under a prior tag, mirroring the
    GHI #233 range-anchor doctrine on the ledger axis.

    Discovery anchors on the ledger receipt, not ADR frontmatter: the ledger
    is the Layer-2 system-of-record and frontmatter ``status:`` is Layer-1
    authorship (AGENTS.md § Never #7). Foundation closeouts are release-worthy
    code surfaces equal to behavior-level GHIs per the hexagonal port/adapter
    doctrine (GHI #490; completes the GHI #330 residual TODO).
    """
    cutoff = _parse_ts(tag_date)
    latest: dict[str, FoundationCloseout] = {}
    for event in ledger.query(event_type="audit_receipt_emitted"):
        if event.extra.get("receipt_event") != "validated":
            continue
        anchor = event.extra.get("anchor") or {}
        semver = str(anchor.get("semver", ""))
        if not _FOUNDATION_SEMVER_RE.match(semver):
            continue
        event_ts = _parse_ts(event.ts)
        if cutoff is not None and event_ts is not None and event_ts <= cutoff:
            continue
        prior = latest.get(event.id)
        if prior is None or event.ts > prior.validated_at:
            latest[event.id] = FoundationCloseout(
                adr_id=event.id,
                semver=semver,
                validated_at=event.ts,
                anchor_commit=str(anchor.get("commit", "")),
            )
    return sorted(latest.values(), key=lambda c: _semver_key(c.semver))


# ---------------------------------------------------------------------------
# Rendering
# ---------------------------------------------------------------------------

_STATUS_STYLE: dict[str, str] = {
    "qualified": "[green]qualified[/green]",
    "label_only": "[yellow]label_only[/yellow]",
    "diff_only": "[yellow]diff_only[/yellow]",
    "open_upstream": "[yellow]open_upstream[/yellow]",
    "unclassified_reference": "[yellow]unclassified_reference[/yellow]",
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
    console.print(f"  Foundation closeouts: {len(result.foundation_closeouts)}")
    console.print()

    for q in result.qualifications:
        styled = _STATUS_STYLE.get(q.status, q.status)
        line = f"  #{q.ghi.number:<6} {escape(q.ghi.title):<40} {styled}"
        if q.warning:
            line += f"  [yellow]![/yellow] {escape(q.warning)}"
        console.print(line)

    if result.foundation_closeouts:
        console.print()
        console.print("[bold]Foundation-ADR closeouts[/bold]")
        for fc in result.foundation_closeouts:
            console.print(f"  {fc.adr_id:<44} [green]validated[/green]  ({fc.validated_at[:10]})")

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
    if manifest.foundation_closeouts:
        lines.extend(
            [
                "",
                "## Qualifying Foundation Closeouts",
                "",
                "| ADR | Semver | Validated | Anchor |",
                "|-----|--------|-----------|--------|",
            ]
        )
        for fc in manifest.foundation_closeouts:
            lines.append(
                f"| {fc.adr_id} | {fc.semver} | {fc.validated_at[:10]} | {fc.anchor_commit} |"
            )
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
    foundation_closeouts: list[FoundationCloseout] | None = None,
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
    if foundation_closeouts:
        lines.append("### Foundation")
        lines.append("")
        for fc in foundation_closeouts:
            lines.append(f"- **{fc.adr_id}** closed out (validated {fc.validated_at[:10]})")
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
            console.print(f"  [red]Version mismatch: {escape(e.message)}[/red]")
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

    # No normal release while an MX hangar is open (ADR-0.0.74 item 14): the
    # hangar must be exited first. Dry-run preview stays usable; the executing
    # path is refused before any gh/network work.
    if not dry_run:
        lock = hardening.normal_release_blocked(project_root)
        if lock.blocked:
            console.print(f"[red]Release refused:[/red] {escape(lock.reason)}")
            raise SystemExit(3)

    _ensure_gh_available(project_root)

    tag, tag_date = _get_latest_tag(project_root)
    qualifications = _build_qualifications(project_root, tag)

    # The ledger is the source-of-truth for foundation-ADR closeouts — a
    # release qualifier equal to behavior-level GHIs (GHI #490). Constructed
    # here so dry-run enumerates closeouts too, not only the execute path.
    config = ensure_initialized()
    ledger = Ledger(project_root / config.paths.ledger)
    foundation_closeouts = _discover_foundation_closeouts(ledger, tag_date)

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
        foundation_closeouts=foundation_closeouts,
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
        foundation_closeouts=foundation_closeouts,
    )

    # Write markdown manifest (REQ-01, REQ-03)
    manifest_rel = _write_manifest_atomic(project_root, manifest)

    # Append JSONL ledger entry (REQ-02)
    ghi_summary = [
        {"number": g.number, "title": g.title, "status": g.status, "warning": g.warning}
        for g in manifest_ghis
    ]
    foundation_summary = [
        {"adr_id": fc.adr_id, "semver": fc.semver, "validated_at": fc.validated_at}
        for fc in foundation_closeouts
    ]
    event = patch_release_event(
        version=proposed_version,
        previous_version=current_version,
        tag=tag,
        ghi_summary=ghi_summary,
        manifest_path=str(manifest_rel),
        foundation_summary=foundation_summary,
    )
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
    entry = _author_release_notes(
        project_root, proposed_version, qualifications, foundation_closeouts
    )
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
