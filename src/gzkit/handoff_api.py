"""Programmatic handoff authoring API.

Replaces the vaporware handoff API (parent ADR-0.0.65 § Intent defect #3:
"handoffs end up hand-authored, which bypasses the validation gate") with a
real runtime module. Every function routes handoff-document construction
through :func:`gzkit.handoff_validation.validate_handoff_document`, so handoff
authoring is mechanically validated rather than hand-rolled.

Discipline: stdlib + Pydantic only. NO LLM, NO network. ``scaffold_handoff`` is
a pure function of its parameters — deterministic pre-fill of the factual
sections (Current State / Evidence / Verification Checklist) from injected
observed state, with byte-identical output for identical inputs.

@covers ADR-0.0.65 (OBPI-0.0.65-02)
"""

from __future__ import annotations

import re
from datetime import UTC, datetime, timedelta
from enum import StrEnum
from pathlib import Path

import yaml
from pydantic import BaseModel, ConfigDict

from gzkit.handoff_validation import (
    REQUIRED_SECTIONS,
    HandoffValidationError,
    parse_frontmatter,
    validate_handoff_document,
)

__all__ = [
    "HandoffInfo",
    "ObservedState",
    "ResumeResult",
    "StalenessLevel",
    "create_handoff",
    "list_handoffs",
    "load_handoff_chain",
    "resume_handoff",
    "scaffold_handoff",
]

_MAX_CHAIN_DEPTH = 20


# ---------------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------------


class StalenessLevel(StrEnum):
    """Freshness classification for a resumed handoff."""

    FRESH = "Fresh"
    SLIGHTLY_STALE = "Slightly-Stale"
    STALE = "Stale"
    VERY_STALE = "Very-Stale"


class ObservedState(BaseModel):
    """Injected observed state for deterministic scaffold pre-fill.

    Carries the factual inputs (ledger events, receipts, changed files) that
    ``scaffold_handoff`` renders into the factual sections. A frozen value
    object: identical instances render byte-identical sections.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    ledger_events: tuple[str, ...] = ()
    receipts: tuple[str, ...] = ()
    changed_files: tuple[str, ...] = ()


class HandoffInfo(BaseModel):
    """Frontmatter-derived summary of an on-disk handoff document."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    adr_id: str
    obpi_id: str | None = None
    timestamp: str


class ResumeResult(BaseModel):
    """Outcome of resuming the newest handoff for an ADR."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    path: str
    staleness: StalenessLevel
    requires_human_verification: bool
    first_next_step: str
    chain: list[str]


# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _handoffs_dir(base_path: Path) -> Path:
    return base_path / ".gzkit" / "handoffs"


def _now_iso() -> str:
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _filesystem_safe_timestamp(iso_ts: str) -> str:
    """Render an ISO timestamp into a filesystem-safe filename token.

    Local reimplementation of the module-private pattern in
    ``handoff_validation`` (that helper is not exported).
    """
    return iso_ts.replace(":", "").replace("-", "").replace(".", "")[:15] + "Z"


def _parse_iso(raw: str) -> datetime:
    parsed = datetime.fromisoformat(raw.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=UTC)
    return parsed


def _timestamp_sort_key(raw: str) -> datetime:
    """Chronological sort key for a frontmatter timestamp.

    ``list_handoffs`` sorts "newest-first", which is a chronological property.
    Raw-string ordering is WRONG for offset-bearing ISO-8601 timestamps
    (``10:00+05:00`` is ``05:00Z`` — earlier than ``08:00Z`` yet lexically
    later). Parse to an aware ``datetime`` so the comparison is by instant.
    Unparseable/empty timestamps sort oldest rather than aborting the scan.
    """
    try:
        return _parse_iso(raw)
    except ValueError:
        return datetime.min.replace(tzinfo=UTC)


def _render_document(frontmatter: dict, sections: dict[str, str]) -> str:
    """Render frontmatter + the seven required sections into a Markdown doc.

    Missing sections render as an empty heading. Written with explicit ``\n``
    newlines so the committed artifact is LF on every platform.
    """
    parts = ["---\n", yaml.safe_dump(frontmatter, sort_keys=False), "---\n\n"]
    for section in REQUIRED_SECTIONS:
        parts.append(f"## {section}\n\n")
        content = sections.get(section, "").strip()
        if content:
            parts.append(content + "\n\n")
    return "".join(parts)


def _extract_first_next_step(content: str) -> str:
    """Return the first numbered/bulleted line of the Immediate Next Steps section."""
    heading = re.search(r"^##\s+Immediate Next Steps\s*$", content, re.MULTILINE)
    if heading is None:
        return ""
    rest = content[heading.end() :]
    nxt = re.search(r"^##\s+", rest, re.MULTILINE)
    section = rest[: nxt.start()] if nxt else rest
    for line in section.splitlines():
        match = re.match(r"^(?:\d+\.\s+|[-*]\s+)(.*)$", line.strip())
        if match and match.group(1).strip():
            return match.group(1).strip()
    return ""


def _classify_staleness(now: str, timestamp: str) -> StalenessLevel:
    age = _parse_iso(now) - _parse_iso(timestamp)
    if age < timedelta(hours=24):
        return StalenessLevel.FRESH
    if age < timedelta(hours=72):
        return StalenessLevel.SLIGHTLY_STALE
    if age < timedelta(days=7):
        return StalenessLevel.STALE
    return StalenessLevel.VERY_STALE


def _resolve_continues_from(ref: str, current: Path, base_path: Path) -> Path:
    candidate = Path(ref)
    if candidate.is_absolute():
        return candidate
    sibling = current.parent / ref
    if sibling.exists():
        return sibling
    rooted = base_path / ref
    if rooted.exists():
        return rooted
    return sibling


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def create_handoff(
    *,
    adr_id: str,
    branch: str,
    agent: str,
    slug: str,
    sections: dict[str, str],
    obpi_id: str | None = None,
    continues_from: str | None = None,
    session_id: str | None = None,
    base_path: Path = Path("."),
    timestamp: str | None = None,
    mode: str = "CREATE",
) -> Path:
    """Author a handoff document, routing it through the validation gate.

    Builds frontmatter plus the seven required sections (missing sections
    render empty), then runs :func:`validate_handoff_document`. When validation
    reports violations the document is NOT written — a :class:`HandoffValidationError`
    carrying the violation list is raised (fail-closed). A clean document is
    written to ``<base_path>/.gzkit/handoffs/<fs-ts>-<slug>.md`` and its path returned.
    """
    ts = timestamp or _now_iso()
    frontmatter: dict = {
        "mode": mode,
        "adr_id": adr_id,
        "branch": branch,
        "timestamp": ts,
        "agent": agent,
    }
    if obpi_id is not None:
        frontmatter["obpi_id"] = obpi_id
    if session_id is not None:
        frontmatter["session_id"] = session_id
    if continues_from is not None:
        frontmatter["continues_from"] = continues_from

    document = _render_document(frontmatter, sections)
    violations = validate_handoff_document(document, base_path)
    if violations:
        raise HandoffValidationError(
            "Refusing to write invalid handoff; violations: " + "; ".join(violations)
        )

    handoff_dir = _handoffs_dir(base_path)
    handoff_dir.mkdir(parents=True, exist_ok=True)
    path = handoff_dir / f"{_filesystem_safe_timestamp(ts)}-{slug}.md"
    path.write_text(document, encoding="utf-8", newline="\n")
    return path


def scaffold_handoff(
    *,
    adr_id: str,
    observed: ObservedState,
    now: str,
    obpi_id: str | None = None,
) -> dict[str, str]:
    """Deterministically pre-fill the factual sections from observed state.

    A pure function of its parameters — no ledger, git, or socket read. The
    factual sections (Current State Summary, Evidence / Artifacts, Verification
    Checklist) are rendered from the injected ``observed`` state; collections
    are sorted so identical inputs yield byte-identical output. The judgment
    sections (Decisions Made, Important Context) are intentionally NOT pre-filled.
    """
    scope = f"{adr_id} ({obpi_id})" if obpi_id else adr_id
    events = sorted(observed.ledger_events)
    receipts = sorted(observed.receipts)
    files = sorted(observed.changed_files)

    current = [f"Scaffolded for {scope} at {now}.", "", "Ledger events observed:"]
    current.extend(f"- {event}" for event in events)

    evidence = ["Receipts observed:"]
    evidence.extend(f"- {receipt}" for receipt in receipts)

    verification = ["Changed files to verify:"]
    verification.extend(f"- [ ] Review {path}" for path in files)

    return {
        "Current State Summary": "\n".join(current),
        "Evidence / Artifacts": "\n".join(evidence),
        "Verification Checklist": "\n".join(verification),
    }


def list_handoffs(*, adr_id: str | None = None, base_path: Path = Path(".")) -> list[HandoffInfo]:
    """Return frontmatter-filtered handoffs, newest-first, optionally scoped by ADR.

    Scans ``<base_path>/.gzkit/handoffs/*.md``, keeps only files whose
    frontmatter carries an ``adr_id``, optionally filters to a specific
    ``adr_id``, and sorts newest-first by frontmatter timestamp.
    """
    handoff_dir = _handoffs_dir(base_path)
    if not handoff_dir.is_dir():
        return []

    infos: list[HandoffInfo] = []
    for path in handoff_dir.glob("*.md"):
        try:
            fm = parse_frontmatter(path.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, HandoffValidationError):
            # UnicodeDecodeError (a ValueError, not an OSError) is caught so a
            # single non-UTF-8 file cannot abort the whole scan (GHI #582 class,
            # file-read side).
            continue
        if not isinstance(fm, dict):
            continue
        fm_adr = fm.get("adr_id")
        if not fm_adr:
            continue
        if adr_id is not None and fm_adr != adr_id:
            continue
        infos.append(
            HandoffInfo(
                path=path.as_posix(),
                adr_id=str(fm_adr),
                obpi_id=fm.get("obpi_id"),
                timestamp=str(fm.get("timestamp", "")),
            )
        )
    infos.sort(key=lambda info: _timestamp_sort_key(info.timestamp), reverse=True)
    return infos


def load_handoff_chain(handoff_path: Path, *, base_path: Path = Path(".")) -> list[Path]:
    """Follow ``continues_from`` links, returning the chain oldest-first.

    Traversal is depth-limited (``≤20``) and cycle-safe: a visited set means a
    self- or loop-reference terminates rather than looping forever. The start
    handoff is included; the returned list is ordered oldest-to-newest.
    """
    chain: list[Path] = []
    visited: set[Path] = set()
    current: Path | None = handoff_path
    depth = 0
    while current is not None and depth < _MAX_CHAIN_DEPTH:
        resolved = current.resolve()
        if resolved in visited:
            break
        visited.add(resolved)
        chain.append(current)
        try:
            fm = parse_frontmatter(current.read_text(encoding="utf-8"))
        except (OSError, UnicodeDecodeError, HandoffValidationError):
            break
        ref = fm.get("continues_from") if isinstance(fm, dict) else None
        if not ref:
            break
        current = _resolve_continues_from(str(ref), current, base_path)
        depth += 1
    chain.reverse()
    return chain


def resume_handoff(*, adr_id: str, base_path: Path = Path("."), now: str) -> ResumeResult:
    """Resume the newest handoff for ``adr_id`` with staleness classification.

    Selects the newest handoff for the ADR, classifies staleness from its age
    (``now`` minus its frontmatter timestamp), flags
    ``requires_human_verification`` for Stale / Very-Stale, and extracts the
    first next step from the Immediate Next Steps section.
    """
    infos = list_handoffs(adr_id=adr_id, base_path=base_path)
    if not infos:
        raise HandoffValidationError(f"No handoff found for {adr_id}")

    newest = infos[0]
    path = Path(newest.path)
    content = path.read_text(encoding="utf-8")
    staleness = _classify_staleness(now, newest.timestamp)
    requires = staleness in (StalenessLevel.STALE, StalenessLevel.VERY_STALE)
    chain = [p.as_posix() for p in load_handoff_chain(path, base_path=base_path)]
    return ResumeResult(
        path=path.as_posix(),
        staleness=staleness,
        requires_human_verification=requires,
        first_next_step=_extract_first_next_step(content),
        chain=chain,
    )
