"""Same-commit-window @covers backfill heuristic for ``gz adr audit-check``.

OBPI-0.0.23-05 — heuristic core. Catches the cosmetic ``@covers(REQ-...)``
backfill anti-pattern (GHI #309 / GHI #272): an agent silences
``gz adr audit-check`` by adding a decorator in the same commit (or within
a small commit/day window) as the REQ's closing receipt, without re-deriving
the assertion's semantics from the REQ.

The heuristic compares each ``@covers`` decorator's introducing commit with
its REQ's closing-receipt commit. When *either* gap is below the configured
threshold the decorator is flagged; when *both* gaps exceed thresholds (the
legitimate-evolution case) it is not.

Every git boundary call goes through the ``git_runner`` callable so unit
tests can mock the boundary cleanly (REQ-0.0.23-05-08).

@covers REQ-0.0.23-05-01
@covers REQ-0.0.23-05-02
@covers REQ-0.0.23-05-03
@covers REQ-0.0.23-05-04
@covers REQ-0.0.23-05-05
@covers REQ-0.0.23-05-06
@covers REQ-0.0.23-05-07
"""

from __future__ import annotations

import json
import math
import re
import subprocess
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from pathlib import Path
from typing import Literal, cast

from pydantic import BaseModel, ConfigDict, Field, ValidationError

from gzkit.commands.common import GzCliError

# --------------------------------------------------------------------------- #
# Mock boundary type                                                           #
# --------------------------------------------------------------------------- #

GitRunner = Callable[[list[str], Path], tuple[int, str, str]]


def _run_git(args: list[str], cwd: Path) -> tuple[int, str, str]:
    """Run ``git <args>`` via :mod:`subprocess` with cwd=``cwd``.

    Returns ``(returncode, stdout, stderr)``. A missing ``git`` binary is
    surfaced as ``rc=127`` so callers handle it the same way they handle
    any other non-zero rc — uniform fail-soft pathway, no exception.
    """
    try:
        completed = subprocess.run(  # noqa: S603 — list-form, no shell
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            check=False,
        )
    except FileNotFoundError:
        return 127, "", "git not found"
    return completed.returncode, completed.stdout, completed.stderr


# --------------------------------------------------------------------------- #
# Pydantic models                                                              #
# --------------------------------------------------------------------------- #


class AuditThresholds(BaseModel):
    """Threshold knobs for the same-commit-window backfill heuristic."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    max_covers_backfill_commits: int = Field(..., ge=0)
    max_covers_backfill_days: int = Field(..., ge=0)


class CoverIntroduction(BaseModel):
    """One ``@covers`` decorator's introducing-commit metadata."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    target: str
    file: str
    line: int
    commit_sha: str
    commit_date: date


class ReqClosingReceipt(BaseModel):
    """One REQ's resolved closing receipt."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str
    receipt_id: str
    commit_sha: str | None
    commit_date: date


class BackfillFinding(BaseModel):
    """One flagged backfill candidate."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    req_id: str
    file: str
    line: int
    introducing_commit_sha: str
    closing_receipt_id: str
    gap_commits: int
    gap_days: int
    severity: Literal["warning", "blocking"]


class BackfillResult(BaseModel):
    """Aggregate audit result returned by :func:`evaluate_backfill_for_audit`."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    findings: tuple[BackfillFinding, ...] = ()
    unresolvable: tuple[str, ...] = ()
    exit_code: int = 0


# --------------------------------------------------------------------------- #
# Threshold loading (REQ-0.0.23-05-05)                                         #
# --------------------------------------------------------------------------- #


def load_audit_thresholds(path: Path) -> AuditThresholds:
    """Load + Pydantic-validate the threshold config.

    Raises :class:`GzCliError` (exit code 1) on missing file, JSON parse
    error, or model-validation failure. Never silently falls back to
    compiled-in defaults — REQ-0.0.23-05-05 is fail-closed by design.
    """
    if not path.is_file():
        msg = f"audit thresholds file missing: {path}"
        raise GzCliError(msg)
    try:
        raw = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        msg = f"audit thresholds file {path}: invalid JSON ({exc})"
        raise GzCliError(msg) from exc
    try:
        return AuditThresholds.model_validate(raw)
    except ValidationError as exc:
        msg = f"audit thresholds file {path}: validation failure ({exc})"
        raise GzCliError(msg) from exc


# --------------------------------------------------------------------------- #
# Git-log -L parsing                                                           #
# --------------------------------------------------------------------------- #

# `git log -L<line>,<line>:<file> --format=%H|%cI` produces a header per
# revision (the format string we pinned) followed by diff hunks. We pick the
# first line that matches `<full-sha>|<iso-8601-with-tz>`.
_LOG_HEADER_RE = re.compile(r"^(?P<sha>[0-9a-f]{7,40})\|(?P<ts>\d{4}-\d{2}-\d{2}T[^\s]+)$")


def _parse_first_log_header(stdout: str) -> tuple[str, date] | None:
    """Return ``(short_sha, commit_date)`` parsed from the first header line.

    Returns ``None`` if no parsable header was found. Resilient to hunk
    noise: only lines matching the canonical ``sha|iso-ts`` shape are
    considered candidates.
    """
    for raw_line in stdout.splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = _LOG_HEADER_RE.match(line)
        if match is None:
            continue
        sha = match.group("sha")[:7]
        ts = match.group("ts")
        try:
            commit_date = datetime.fromisoformat(ts).date()
        except ValueError:
            continue
        return sha, commit_date
    return None


# --------------------------------------------------------------------------- #
# Decorator-introduction discovery (REQ-0.0.23-05-01, REQ-0.0.23-05-07)         #
# --------------------------------------------------------------------------- #


def find_covers_decorator_introductions(
    project_root: Path,
    covers_locations: Sequence[tuple[str, str, int]],
    *,
    git_runner: GitRunner = _run_git,
) -> tuple[tuple[CoverIntroduction, ...], tuple[str, ...]]:
    """Resolve the introducing commit for each ``@covers`` decorator location.

    For each ``(target, file, line)`` triple, runs::

        git log --reverse --format=%H|%cI -L<line>,<line>:<file>

    and parses the first header line to extract the short SHA and date.
    Triples that fail to resolve (rc != 0, empty stdout, unparseable
    output) become entries in the second-tuple's diagnostic list rather
    than raising — REQ-0.0.23-05-07 wants the audit to keep going under
    default mode.
    """
    introductions: list[CoverIntroduction] = []
    unresolvable: list[str] = []

    for target, rel_file, line_no in covers_locations:
        args = [
            "log",
            "--reverse",
            "--format=%H|%cI",
            f"-L{line_no},{line_no}:{rel_file}",
        ]
        rc, stdout, stderr = git_runner(args, project_root)
        if rc != 0:
            unresolvable.append(
                f"{rel_file}:{line_no} REQ {target} introducing commit unresolvable "
                f"(git rc={rc}: {stderr.strip() or 'no stderr'})"
            )
            continue
        if not stdout.strip():
            unresolvable.append(
                f"{rel_file}:{line_no} REQ {target} introducing commit unresolvable "
                f"(empty git log output)"
            )
            continue
        parsed = _parse_first_log_header(stdout)
        if parsed is None:
            unresolvable.append(
                f"{rel_file}:{line_no} REQ {target} introducing commit unresolvable "
                f"(could not parse git log header)"
            )
            continue
        short_sha, commit_date = parsed
        introductions.append(
            CoverIntroduction(
                target=target,
                file=rel_file,
                line=line_no,
                commit_sha=short_sha,
                commit_date=commit_date,
            )
        )

    return tuple(introductions), tuple(unresolvable)


# --------------------------------------------------------------------------- #
# REQ → closing receipt resolution (REQ-0.0.23-05-01)                          #
# --------------------------------------------------------------------------- #

_REQ_ID_RE = re.compile(r"^REQ-(\d+\.\d+\.\d+)-(\d+)-\d+$")
_RECEIPT_EVENTS = {"completed", "attested_completed"}


def _parent_obpi_id(req_id: str) -> str | None:
    match = _REQ_ID_RE.match(req_id)
    if match is None:
        return None
    return f"OBPI-{match.group(1)}-{match.group(2)}"


def _ts_to_date(ts: str) -> date | None:
    try:
        return datetime.fromisoformat(ts).date()
    except ValueError:
        return None


def _event_field(event: Mapping, key: str) -> object:
    """Return ``event[key]`` honoring ``LedgerEvent.model_dump`` flattening.

    ``LedgerEvent`` carries event-specific data in ``.extra`` but its
    ``@model_serializer`` flattens those keys to top-level on dump. Either
    shape can reach the heuristic depending on whether the caller passes
    a freshly-dumped event (flattened) or a raw mapping built by hand
    (with explicit ``extra`` substructure). Look in both, top-level first.
    """
    if key in event:
        return event[key]
    extra = event.get("extra")
    if isinstance(extra, Mapping):
        return extra.get(key)
    return None


def _latest_receipt_event(obpi_id: str, events: Sequence[Mapping]) -> Mapping | None:
    """Return the most-recent matching receipt event for ``obpi_id``.

    Filters to events with ``event == "obpi_receipt_emitted"`` matching the
    OBPI id (bare or slugged) whose ``receipt_event`` field — at top level
    or under ``extra`` — is in :data:`_RECEIPT_EVENTS`. Returns ``None``
    when no event matches.
    """
    candidates: list[Mapping] = []
    for event in events:
        if not isinstance(event, Mapping):
            continue
        if event.get("event") != "obpi_receipt_emitted":
            continue
        event_id = str(event.get("id") or "")
        if not (event_id == obpi_id or event_id.startswith(f"{obpi_id}-")):
            continue
        if _event_field(event, "receipt_event") not in _RECEIPT_EVENTS:
            continue
        candidates.append(event)
    if not candidates:
        return None
    candidates.sort(key=lambda e: str(e.get("ts") or ""))
    return candidates[-1]


def _build_receipt_from_event(req_id: str, event: Mapping) -> ReqClosingReceipt | None:
    raw_anchor = _event_field(event, "anchor")
    if isinstance(raw_anchor, Mapping):
        anchor_str_keyed: Mapping[str, object] = cast("Mapping[str, object]", raw_anchor)
        commit_sha_raw = anchor_str_keyed.get("commit")
    else:
        commit_sha_raw = None
    commit_sha = str(commit_sha_raw)[:7] if commit_sha_raw else None
    commit_date = _ts_to_date(str(event.get("ts") or ""))
    if commit_date is None:
        return None
    receipt_id_raw = _event_field(event, "receipt_id")
    receipt_id = (
        str(receipt_id_raw)
        if receipt_id_raw
        else f"obpi_receipt_emitted:{event.get('id')}:{event.get('ts')}"
    )
    return ReqClosingReceipt(
        req_id=req_id,
        receipt_id=receipt_id,
        commit_sha=commit_sha,
        commit_date=commit_date,
    )


def _resolve_no_receipt_fallback(
    req_id: str,
    obpi_id: str,
    project_root: Path,
    git_runner: GitRunner,
) -> ReqClosingReceipt | None:
    """REQ-0.0.23-05-01 fallback: most-recent commit touching the brief path.

    Used when no ``obpi_receipt_emitted`` event exists for the parent OBPI.
    Looks up the brief path under
    ``docs/design/adr/{foundation,pre-release}/ADR-*/obpis/<obpi_id>*.md``.
    Returns ``None`` if neither the file nor the git log resolves.
    """
    pattern = f"docs/design/adr/*/ADR-*/obpis/{obpi_id}*.md"
    rc, stdout, _stderr = git_runner(
        ["log", "-1", "--format=%H|%cI", "--", pattern],
        project_root,
    )
    if rc != 0 or not stdout.strip():
        return None
    parsed = _parse_first_log_header(stdout)
    if parsed is None:
        return None
    short_sha, commit_date = parsed
    return ReqClosingReceipt(
        req_id=req_id,
        receipt_id=f"git-fallback:{obpi_id}:{short_sha}",
        commit_sha=short_sha,
        commit_date=commit_date,
    )


def resolve_req_closing_receipts(
    req_ids: Sequence[str],
    obpi_completion_events: Sequence[Mapping],
    *,
    project_root: Path,
    git_runner: GitRunner = _run_git,
) -> dict[str, ReqClosingReceipt]:
    """Map each REQ id to the closing receipt of its parent OBPI."""
    receipts: dict[str, ReqClosingReceipt] = {}
    for req_id in req_ids:
        obpi_id = _parent_obpi_id(req_id)
        if obpi_id is None:
            continue
        event = _latest_receipt_event(obpi_id, obpi_completion_events)
        if event is not None:
            receipt = _build_receipt_from_event(req_id, event)
            if receipt is not None:
                receipts[req_id] = receipt
                continue
        fallback = _resolve_no_receipt_fallback(req_id, obpi_id, project_root, git_runner)
        if fallback is not None:
            receipts[req_id] = fallback
    return receipts


# --------------------------------------------------------------------------- #
# Severity (REQ-0.0.23-05-02, REQ-0.0.23-05-03)                                 #
# --------------------------------------------------------------------------- #


def determine_severity(
    lane: str,
    kind: str,
    strict: bool,
) -> Literal["warning", "blocking"]:
    """Escalate to ``blocking`` on heavy lane, foundation kind, or ``--strict``.

    Restored to the original three-axis predicate after GHI #386 taught the
    heuristic to distinguish ``Ceremony: <name>`` ceremony-bundled commits
    and same-commit file-creation from the GHI #272 cosmetic-backfill
    anti-pattern. Lite-feature non-strict invocations remain warning-only.
    """
    if strict or lane == "heavy" or kind == "foundation":
        return "blocking"
    return "warning"


# --------------------------------------------------------------------------- #
# Legitimate-authoring guards (GHI #386 — ceremony-trailer + file-creation)     #
# --------------------------------------------------------------------------- #

# Ceremony-trailer values that mark a commit as a governance ceremony bundling
# tests + implementation + receipt rather than a cosmetic-backfill decoration.
# Canonized in `.claude/rules/tests.md` § TASK-Driven Workflow; `ghi-close` is
# included for GHI-driven defect remedies that bundle the same triple.
_EXEMPT_CEREMONIES: frozenset[str] = frozenset(
    {"gz-git-sync", "obpi-reconcile", "adr-closeout", "ghi-close"}
)

# Pre-GHI #201 ceremony commits (before `Ceremony:` git trailer convention)
# carry the marker only in the parenthesized subject suffix, e.g.
# `chore: update ... (gz git-sync)`. Anchored to subject end so a future
# commit titled `fix: stop bypassing (gz git-sync) trailer check` cannot
# accidentally exempt itself by mentioning the suffix mid-line (GHI #390).
_HISTORICAL_CEREMONY_SUBJECT_PATTERNS: dict[str, re.Pattern[str]] = {
    "gz-git-sync": re.compile(r"\(gz[\s-]git[\s-]sync\)\s*$"),
    "obpi-reconcile": re.compile(r"\(obpi[\s-]reconcile\)\s*$"),
    "adr-closeout": re.compile(r"\(adr[\s-]closeout\)\s*$"),
    "ghi-close": re.compile(r"\(ghi[\s-]close\)\s*$"),
}


def _file_creation_short_sha(
    rel_file: str, project_root: Path, git_runner: GitRunner
) -> str | None:
    """Return the 7-char short SHA of the commit that first added ``rel_file``."""
    rc, stdout, _stderr = git_runner(
        ["log", "--diff-filter=A", "--format=%H", "--", rel_file],
        project_root,
    )
    if rc != 0:
        return None
    for raw_line in stdout.splitlines():
        candidate = raw_line.strip()
        if candidate:
            return candidate[:7]
    return None


def _ceremony_trailer(sha: str, project_root: Path, git_runner: GitRunner) -> str | None:
    """Return the ``Ceremony:`` trailer value for ``sha`` (or ``None``)."""
    rc, stdout, _stderr = git_runner(
        ["log", "-1", "--format=%(trailers:key=Ceremony,valueonly=true)", sha],
        project_root,
    )
    if rc != 0:
        return None
    value = stdout.strip()
    return value or None


def _ceremony_subject_marker(sha: str, project_root: Path, git_runner: GitRunner) -> str | None:
    """Return the canonical ceremony name when ``sha``'s subject carries the historical
    parenthesized suffix (e.g. ``(gz git-sync)``) at end of line.

    Pre-GHI #201 ceremony commits embedded the marker in the subject suffix
    rather than the ``Ceremony:`` trailer; ADR-0.0.16 and other foundation-kind
    ADRs closed under that window failed audit-check despite legitimate
    cross-OBPI coverage extension being bundled into a single ``gz git-sync``
    commit. Maps the historical suffix to the same canonical names that
    :data:`_EXEMPT_CEREMONIES` enumerates.
    """
    rc, stdout, _stderr = git_runner(["log", "-1", "--format=%s", sha], project_root)
    if rc != 0:
        return None
    subject = stdout.strip()
    if not subject:
        return None
    for canonical, pattern in _HISTORICAL_CEREMONY_SUBJECT_PATTERNS.items():
        if pattern.search(subject):
            return canonical
    return None


def _is_legitimate_authoring(
    intro: CoverIntroduction,
    project_root: Path,
    git_runner: GitRunner,
    receipt_commit_sha: str | None = None,
) -> bool:
    """Return True when ``intro`` is same-commit creation or ceremony-bundled.

    Two structurally distinct legitimate-authoring shapes are exempted from
    the same-commit-window backfill heuristic:

    - **Same-commit creation (GHI #382):** the file went 0->N lines in the
      introducing commit, so ``@covers`` was present from line one.
    - **Ceremony bundling (GHI #386):** the introducing commit carries a
      ``Ceremony:`` trailer in :data:`_EXEMPT_CEREMONIES` (e.g.
      ``Ceremony: gz-git-sync``), marking it as a governance ceremony commit
      that bundles tests + implementation + receipt by design.

    The same-commit-creation exemption does NOT apply when the receipt is also
    anchored to the same commit — that triple (file-create + @covers + receipt
    all in one commit) is the GHI #309 cosmetic-backfill pattern regardless of
    file-creation status.

    Any other shape (later-commit decoration on a pre-existing test) remains
    flag-eligible — that is the GHI #272 cosmetic-backfill anti-pattern this
    heuristic exists to catch.
    """
    creation_sha = _file_creation_short_sha(intro.file, project_root, git_runner)
    if (
        creation_sha is not None
        and creation_sha == intro.commit_sha
        and (receipt_commit_sha is None or receipt_commit_sha != intro.commit_sha)
    ):
        return True
    trailer = _ceremony_trailer(intro.commit_sha, project_root, git_runner)
    if trailer is not None and trailer in _EXEMPT_CEREMONIES:
        return True
    # GHI #390 Case B: pre-GHI #201 ceremony commits carry the marker only in
    # the parenthesized subject suffix (e.g. `(gz git-sync)` at end of subject)
    # rather than a `Ceremony:` trailer. Fall back to subject-suffix detection
    # so heavy-lane / foundation-kind ADRs closed under the pre-trailer window
    # don't permanently fail audit-check on cross-OBPI coverage extension.
    subject_marker = _ceremony_subject_marker(intro.commit_sha, project_root, git_runner)
    return subject_marker is not None and subject_marker in _EXEMPT_CEREMONIES


# --------------------------------------------------------------------------- #
# Backfill computation (REQ-0.0.23-05-01, REQ-0.0.23-05-02, REQ-0.0.23-05-04)   #
# --------------------------------------------------------------------------- #


def _commits_gap(
    intro_sha: str,
    receipt_sha: str | None,
    project_root: Path,
    git_runner: GitRunner,
) -> float:
    """Return ``|count(intro..receipt)|`` or :data:`math.inf` on git failure."""
    if not receipt_sha:
        return math.inf
    if intro_sha == receipt_sha:
        return 0
    rc, stdout, _stderr = git_runner(
        ["rev-list", "--count", f"{intro_sha}..{receipt_sha}"],
        project_root,
    )
    if rc != 0:
        return math.inf
    raw = stdout.strip()
    if not raw:
        return math.inf
    try:
        return abs(int(raw))
    except ValueError:
        return math.inf


def compute_backfill_findings(
    introductions: Sequence[CoverIntroduction],
    receipts: Mapping[str, ReqClosingReceipt],
    thresholds: AuditThresholds,
    *,
    severity: Literal["warning", "blocking"],
    project_root: Path,
    git_runner: GitRunner = _run_git,
) -> tuple[BackfillFinding, ...]:
    """Flag each introduction whose REQ has a receipt within the same window."""
    findings: list[BackfillFinding] = []

    for intro in introductions:
        receipt = receipts.get(intro.target)
        if receipt is None:
            continue

        commits_gap = _commits_gap(intro.commit_sha, receipt.commit_sha, project_root, git_runner)
        days_gap = abs((receipt.commit_date - intro.commit_date).days)

        commits_in_window = commits_gap <= thresholds.max_covers_backfill_commits
        days_in_window = days_gap <= thresholds.max_covers_backfill_days

        if not (commits_in_window or days_in_window):
            continue

        # GHI #386 / GHI #382: same-commit-window decorators introduced under
        # ceremony bundling or file-creation are legitimate authoring, not the
        # GHI #272 cosmetic-backfill anti-pattern. Apply the legitimacy guard
        # only when a finding is otherwise about to be flagged so the extra
        # git boundary calls are paid only on candidate intros.
        if _is_legitimate_authoring(
            intro, project_root, git_runner, receipt_commit_sha=receipt.commit_sha
        ):
            continue

        rendered_commits = int(commits_gap) if commits_gap != math.inf else _SENTINEL_COMMITS
        findings.append(
            BackfillFinding(
                req_id=intro.target,
                file=intro.file,
                line=intro.line,
                introducing_commit_sha=intro.commit_sha,
                closing_receipt_id=receipt.receipt_id,
                gap_commits=rendered_commits,
                gap_days=days_gap,
                severity=severity,
            )
        )

    return tuple(findings)


# Sentinel used when rev-list cannot resolve the commit gap. Renders as a
# huge integer so operators see the unresolvable shape rather than a NaN.
_SENTINEL_COMMITS = 999_999


# --------------------------------------------------------------------------- #
# Diagnostic formatting (REQ-0.0.23-05-01, REQ-0.0.23-05-03)                    #
# --------------------------------------------------------------------------- #

_REMEDIATION_HINT = "see .claude/rules/tests.md § Invariant 6f for remediation"


def format_backfill_finding(finding: BackfillFinding) -> str:
    """Render one finding as a single-line operator-facing diagnostic."""
    return (
        f"{finding.file}:{finding.line} REQ {finding.req_id} "
        f"introduced @ {finding.introducing_commit_sha} "
        f"({finding.gap_commits}c / {finding.gap_days}d before "
        f"receipt {finding.closing_receipt_id}); {_REMEDIATION_HINT}"
    )


# --------------------------------------------------------------------------- #
# Orchestrator (REQ-0.0.23-05-02 / -03 / -05 / -07)                              #
# --------------------------------------------------------------------------- #


def _exit_code(
    findings: Sequence[BackfillFinding],
    unresolvable: Sequence[str],
    severity: Literal["warning", "blocking"],
    strict: bool,
) -> int:
    """Resolve the audit exit code per REQ ordering: policy > system > ok."""
    if findings and severity == "blocking":
        return 3
    if unresolvable and strict:
        return 2
    return 0


def evaluate_backfill_for_audit(
    project_root: Path,
    *,
    adr_lane: str,
    adr_kind: str,
    strict: bool,
    covers_locations: Sequence[tuple[str, str, int]],
    obpi_completion_events: Sequence[Mapping],
    thresholds_path: Path,
    git_runner: GitRunner = _run_git,
) -> BackfillResult:
    """Top-level pipeline: thresholds → introductions → receipts → findings.

    Short-circuits on empty ``covers_locations``: with no @covers decorators
    in scope there is nothing to scan, so no thresholds load is attempted.
    REQ-0.0.23-05-03 binds eager-load only when the heuristic has work; the
    file-MUST-exit-1 contract still fires on every audit run that has actual
    decorators to evaluate.
    """
    if not covers_locations:
        return BackfillResult()
    thresholds = load_audit_thresholds(thresholds_path)
    introductions, unresolvable = find_covers_decorator_introductions(
        project_root, covers_locations, git_runner=git_runner
    )
    req_ids = sorted({intro.target for intro in introductions})
    receipts = resolve_req_closing_receipts(
        req_ids,
        obpi_completion_events,
        project_root=project_root,
        git_runner=git_runner,
    )
    severity = determine_severity(adr_lane, adr_kind, strict)
    findings = compute_backfill_findings(
        introductions,
        receipts,
        thresholds,
        severity=severity,
        project_root=project_root,
        git_runner=git_runner,
    )
    code = _exit_code(findings, unresolvable, severity, strict)
    return BackfillResult(
        findings=tuple(findings),
        unresolvable=tuple(unresolvable),
        exit_code=code,
    )


__all__ = [
    "AuditThresholds",
    "BackfillFinding",
    "BackfillResult",
    "CoverIntroduction",
    "GitRunner",
    "ReqClosingReceipt",
    "compute_backfill_findings",
    "determine_severity",
    "evaluate_backfill_for_audit",
    "find_covers_decorator_introductions",
    "format_backfill_finding",
    "load_audit_thresholds",
    "resolve_req_closing_receipts",
]
