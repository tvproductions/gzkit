"""Temporal drift detection for validation receipt anchors.

Compares the anchor commit recorded in a validation receipt against the
current HEAD to classify whether the codebase has drifted since validation.

Drift is informational, not an error -- past validation remains valid. The
classifier reports `none`, `commits_ahead` (linear progression), or
`diverged` (rebase, force-push, or anchor commit not present in repository).

This module is intentionally separate from `gzkit.triangle` and
`gzkit.commands.drift`. The two `drift` concepts are orthogonal:

- `triangle.detect_drift` reports **structural** drift across the
  spec/test/code triangle (REQs without `@covers`, orphan tests, unjustified
  code changes).
- `temporal_drift.detect_drift` reports **temporal** drift between the git
  commit recorded in a validation receipt and the current HEAD.

Architecture:
- Git helpers (private): thin `git_cmd` wrappers that share gzkit's HEAD cache
- Pure classifier: ``classify_drift()`` -- no I/O, fully testable without mocks
- Orchestrators: ``detect_drift()`` / ``detect_obpi_drift()`` -- read the
  gzkit ledger, normalize short SHA-7 anchors via ``git rev-parse``, and
  delegate to the pure classifier.

Lineage: adapted from ``opsdev.lib.drift_detection`` in airlineops, with
gzkit-specific changes documented in
``docs/design/adr/pre-release/ADR-0.25.0-core-infrastructure-pattern-absorption/obpis/OBPI-0.25.0-26-drift-detection-pattern.md``.
"""

from __future__ import annotations

from pathlib import Path
from typing import Literal

from pydantic import BaseModel, ConfigDict

from gzkit.ledger import Ledger, LedgerEvent
from gzkit.utils import git_cmd

DriftStatus = Literal["none", "commits_ahead", "diverged"]


class DriftResult(BaseModel):
    """Result of comparing an ADR validation anchor against current HEAD."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    adr_id: str
    status: DriftStatus
    anchor_commit: str
    head_commit: str
    commits_ahead: int | None = None
    message: str


class ObpiDriftResult(BaseModel):
    """Result of comparing an OBPI completion anchor against current HEAD."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    obpi_id: str
    adr_id: str
    status: DriftStatus
    anchor_commit: str
    head_commit: str
    commits_ahead: int | None = None
    message: str


# ---------------------------------------------------------------------------
# Git helpers (private; share gzkit.utils.git_cmd)
# ---------------------------------------------------------------------------


def _get_head_commit(project_root: Path) -> str:
    """Return the current HEAD full commit SHA.

    Raises ``RuntimeError`` when git is unavailable or HEAD cannot be resolved.
    """
    rc, stdout, stderr = git_cmd(project_root, "rev-parse", "HEAD")
    if rc == 127:
        msg = "git is not available on PATH"
        raise RuntimeError(msg)
    if rc != 0:
        msg = f"Failed to get HEAD commit: {stderr}"
        raise RuntimeError(msg)
    return stdout.strip()


def _resolve_full_commit(project_root: Path, short_sha: str) -> str | None:
    """Normalize a short SHA-7 anchor to the full commit SHA.

    Returns ``None`` when the short SHA does not resolve in the repository
    (typical after shallow clone, history rewrite, or force-push).
    """
    rc, stdout, _stderr = git_cmd(project_root, "rev-parse", short_sha)
    if rc != 0:
        return None
    return stdout.strip() or None


def _is_ancestor(project_root: Path, ancestor: str, descendant: str) -> bool | None:
    """Check whether *ancestor* is an ancestor of *descendant*.

    Returns ``True`` if ancestor, ``False`` if not, ``None`` when the commit
    is not present in the repository (git exit code 128).
    """
    rc, _stdout, _stderr = git_cmd(
        project_root, "merge-base", "--is-ancestor", ancestor, descendant
    )
    if rc == 0:
        return True
    if rc == 1:
        return False
    return None


def _count_commits_between(project_root: Path, ancestor: str, descendant: str) -> int | None:
    """Count commits reachable from *descendant* but not from *ancestor*.

    Returns ``None`` on git failure (e.g., commit not in repo).
    """
    rc, stdout, _stderr = git_cmd(project_root, "rev-list", "--count", f"{ancestor}..{descendant}")
    if rc != 0:
        return None
    try:
        return int(stdout.strip())
    except ValueError:
        return None


# ---------------------------------------------------------------------------
# Pure classifier (no I/O)
# ---------------------------------------------------------------------------


def classify_drift(
    adr_id: str,
    anchor_commit: str,
    head_commit: str,
    is_ancestor_result: bool | None,
    commits_ahead_count: int | None,
) -> DriftResult:
    """Classify drift between anchor commit and HEAD.

    Pure function -- all I/O results are passed in as arguments.
    """
    if anchor_commit == head_commit:
        return DriftResult(
            adr_id=adr_id,
            status="none",
            anchor_commit=anchor_commit,
            head_commit=head_commit,
            commits_ahead=0,
            message=f"{adr_id}: validated at current HEAD ({anchor_commit[:7]})",
        )

    if is_ancestor_result is None:
        return DriftResult(
            adr_id=adr_id,
            status="diverged",
            anchor_commit=anchor_commit,
            head_commit=head_commit,
            commits_ahead=None,
            message=(
                f"{adr_id}: anchor commit {anchor_commit[:7]} not found in repository history"
            ),
        )

    if is_ancestor_result:
        count = commits_ahead_count if commits_ahead_count is not None else 0
        return DriftResult(
            adr_id=adr_id,
            status="commits_ahead",
            anchor_commit=anchor_commit,
            head_commit=head_commit,
            commits_ahead=count,
            message=f"{adr_id}: validated {count} commit(s) ago ({anchor_commit[:7]})",
        )

    return DriftResult(
        adr_id=adr_id,
        status="diverged",
        anchor_commit=anchor_commit,
        head_commit=head_commit,
        commits_ahead=None,
        message=f"{adr_id}: anchor {anchor_commit[:7]} has diverged from HEAD",
    )


# ---------------------------------------------------------------------------
# Receipt readers (read gzkit ledger, return latest anchor commit)
# ---------------------------------------------------------------------------


def _extract_anchor_commit(event: LedgerEvent) -> str | None:
    """Return the ``anchor.commit`` value from a ledger event, or None."""
    anchor = event.extra.get("anchor")
    if not isinstance(anchor, dict):
        return None
    commit = anchor.get("commit")
    if not isinstance(commit, str) or not commit:
        return None
    return commit


def _latest_adr_anchor(ledger: Ledger, adr_id: str) -> str | None:
    """Return the most recent ``anchor.commit`` for an ADR audit receipt."""
    events = ledger.query(event_type="audit_receipt_emitted", artifact_id=adr_id)
    for event in reversed(events):
        commit = _extract_anchor_commit(event)
        if commit is not None:
            return commit
    return None


def _latest_obpi_anchors(
    ledger: Ledger,
    adr_id: str,
    obpi_id: str | None,
) -> dict[str, str]:
    """Return ``{obpi_id: anchor_commit}`` for OBPIs under an ADR.

    Last entry per OBPI wins. Filtered by ``parent == adr_id`` (and
    ``id == obpi_id`` when supplied).
    """
    events = ledger.query(event_type="obpi_receipt_emitted")
    result: dict[str, str] = {}
    for event in events:
        if event.parent != adr_id:
            continue
        if obpi_id is not None and event.id != obpi_id:
            continue
        commit = _extract_anchor_commit(event)
        if commit is None:
            continue
        result[event.id] = commit
    return result


# ---------------------------------------------------------------------------
# Orchestrators
# ---------------------------------------------------------------------------


def _resolve_anchor(
    project_root: Path, anchor_short: str, head_commit: str
) -> tuple[str, bool | None]:
    """Resolve a short anchor SHA to (full_or_short, anchor_commit_known).

    Returns the full SHA when ``git rev-parse <short>`` succeeds; otherwise
    returns the original short SHA so the caller can still report it in the
    ``diverged`` message. The second element is the resolution flag passed
    through to ``classify_drift`` as ``is_ancestor_result``: ``None`` when
    the anchor is unresolvable.
    """
    full = _resolve_full_commit(project_root, anchor_short)
    if full is None:
        return anchor_short, None
    if full == head_commit:
        return full, True
    return full, _is_ancestor(project_root, full, head_commit)


def detect_drift(adr_id: str, *, project_root: Path | None = None) -> DriftResult | None:
    """Detect git drift for a validated ADR.

    Reads the most recent ``audit_receipt_emitted`` event for *adr_id* from
    ``.gzkit/ledger.jsonl``, normalizes the short SHA-7 anchor to a full
    commit, and compares against the current HEAD.

    Returns ``None`` when no anchored audit receipt exists.
    """
    root = project_root or Path.cwd()
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return None

    ledger = Ledger(ledger_path)
    anchor_short = _latest_adr_anchor(ledger, adr_id)
    if anchor_short is None:
        return None

    head_commit = _get_head_commit(root)
    full_anchor, is_ancestor_result = _resolve_anchor(root, anchor_short, head_commit)

    count: int | None = None
    if is_ancestor_result:
        count = _count_commits_between(root, full_anchor, head_commit)

    return classify_drift(adr_id, full_anchor, head_commit, is_ancestor_result, count)


def detect_obpi_drift(
    adr_id: str,
    *,
    obpi_id: str | None = None,
    project_root: Path | None = None,
) -> list[ObpiDriftResult]:
    """Detect per-OBPI drift against completion anchors.

    Reads ``obpi_receipt_emitted`` events whose ``parent`` matches *adr_id*
    (and whose ``id`` matches *obpi_id* when supplied), normalizes each
    short SHA-7 anchor, and classifies drift against the current HEAD.

    Returns an empty list when no anchored OBPI receipts exist.
    """
    root = project_root or Path.cwd()
    ledger_path = root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []

    ledger = Ledger(ledger_path)
    anchored = _latest_obpi_anchors(ledger, adr_id, obpi_id)
    if not anchored:
        return []

    head_commit = _get_head_commit(root)
    results: list[ObpiDriftResult] = []
    for oid, anchor_short in anchored.items():
        full_anchor, is_ancestor_result = _resolve_anchor(root, anchor_short, head_commit)
        count: int | None = None
        if is_ancestor_result:
            count = _count_commits_between(root, full_anchor, head_commit)
        drift = classify_drift(adr_id, full_anchor, head_commit, is_ancestor_result, count)
        results.append(
            ObpiDriftResult(
                obpi_id=oid,
                adr_id=adr_id,
                status=drift.status,
                anchor_commit=full_anchor,
                head_commit=head_commit,
                commits_ahead=drift.commits_ahead,
                message=f"{oid}: {drift.message}",
            )
        )
    return sorted(results, key=lambda r: r.obpi_id)


__all__ = [
    "DriftResult",
    "DriftStatus",
    "ObpiDriftResult",
    "classify_drift",
    "detect_drift",
    "detect_obpi_drift",
]
