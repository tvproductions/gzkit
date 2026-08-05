"""Session-exit floor bookmark — the handoff's missing trigger (GHI #756).

``gz handoff create`` shipped under ADR-0.0.65 and nothing called it. ADR-0.0.65
built every place a handoff lives and every way to touch one, and left
unspecified *when* any of it fires — so continuity depended on an agent
remembering to author one, and the operator retyping the request.

This module is the exit beat. It **books, never refuses**: the airlock reached
its both-edges guarantee by writing a terminal record even on an aborted transit
(``_book_aborted_exit``, GHI #679) rather than by blocking, and the operator
ruled the handoff copies that shape — *"DO NOT BLOCK HERE. Observe,
contextualize, update status, develop suggestions, pose questions, write them
all to the handoff bookmark, and leave."*

The bookmark is always ``CHECKPOINT`` mode. A writer firing on session exit
cannot know whether the operator is finished or merely typed ``/clear``, and a
``CREATE`` handoff postdating a lock claim satisfies token-block discipline
§ Sub-Invariant 5 — an automatic producer emitting those would let any session's
work lock be released on the evidence of an artifact nobody authored. The mode
distinction is what makes running this automatically safe at all.

Vendor-neutral by construction: the decision and the write live here, and each
harness contributes only a stdin/exit-code shim (the shape
``gzkit.handoff_resume_gate`` already uses). Codex sends the same
``session_id`` / ``transcript_path`` / ``cwd`` payload under the same event
names but supports no ``async``, so this runs synchronously and the caller's
bookmark completes before exit.
"""

from __future__ import annotations

from datetime import UTC, datetime
from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.handoff_api import create_handoff
from gzkit.handoff_validation import CHECKPOINT_MODE, HandoffValidationError

__all__ = ["ExitBookmarkResult", "book_exit_bookmark"]

#: Slug for the mechanically-written bookmark. Fixed so the artifacts are
#: greppable as a class and distinguishable from authored handoffs at a glance.
_SLUG = "session-exit-bookmark"


class ExitBookmarkResult(BaseModel):
    """Outcome of one exit beat.

    ``written`` is the whole verdict; ``detail`` explains a ``False``. There is
    no error variant because there is no failure mode this surface is allowed to
    raise — see :func:`book_exit_bookmark`.
    """

    model_config = ConfigDict(frozen=True, extra="forbid")

    written: bool = Field(..., description="Whether a bookmark reached disk")
    path: str | None = Field(None, description="POSIX path of the written bookmark")
    detail: str = Field("", description="Why nothing was written, when nothing was")


def book_exit_bookmark(
    project_root: Path,
    *,
    session_id: str,
    exit_reason: str,
    transcript_path: str | None = None,
    obpi_id: str | None = None,
    adr_id: str | None = None,
    now: str | None = None,
) -> ExitBookmarkResult:
    """Write a CHECKPOINT bookmark recording session state at exit.

    Never raises. Every failure — an unwritable tree, a refused document, a
    missing handoff directory — returns ``written=False`` with the cause in
    ``detail``. An exception escaping here *is* a block, which the operator
    ruling forbids, and the callers that matter (harness hooks at process exit)
    have nowhere to report one.

    ``transcript_path`` is recorded as plain text, never as a backtick-quoted
    path: ``validate_referenced_files`` requires backticked paths to exist in
    committed state, and the transcript lives outside the repository.
    """
    timestamp = now or datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    sections = _draft_sections(
        session_id=session_id,
        exit_reason=exit_reason,
        transcript_path=transcript_path,
        timestamp=timestamp,
    )
    try:
        path = create_handoff(
            adr_id=adr_id,
            branch=_current_branch(project_root),
            agent="gzkit-session-exit",
            slug=_SLUG,
            sections=sections,
            obpi_id=obpi_id,
            session_id=session_id,
            base_path=project_root,
            timestamp=timestamp,
            mode=CHECKPOINT_MODE,
        )
    except (OSError, ValueError, HandoffValidationError) as exc:
        # HandoffValidationError is named explicitly: it derives from Exception,
        # not ValueError, so a `(OSError, ValueError)` catch silently misses the
        # gate's own refusal — the single most likely failure here. A refused
        # bookmark is a real signal, but it is reported, not raised: the session
        # is leaving either way.
        return ExitBookmarkResult(written=False, detail=f"{type(exc).__name__}: {exc}")

    return ExitBookmarkResult(written=True, path=path.as_posix())


def _draft_sections(
    *,
    session_id: str,
    exit_reason: str,
    transcript_path: str | None,
    timestamp: str,
) -> dict[str, str]:
    """Draft the seven required sections from observable facts only.

    Deliberately terse and deliberately honest about what a mechanical writer
    can and cannot know. It records where the session stopped; it does not
    claim to know why, or what the work meant. The next session enriches it —
    this is the *floor*, not the ceiling.
    """
    transcript_line = (
        f"Session transcript: {transcript_path}"
        if transcript_path
        else "No transcript path was supplied by the harness."
    )
    return {
        "Current State Summary": (
            f"Session `{session_id}` ended at {timestamp} (reason: {exit_reason}). "
            "This is a mechanical floor bookmark written at the exit beat, not an "
            "authored handoff — it records where the session stopped, not what the "
            "work meant."
        ),
        "Important Context": (
            "Written automatically because the session ended; no agent chose to "
            "author it. It is CHECKPOINT mode, so it never satisfies a token "
            "surrender (token-block discipline § Sub-Invariant 5). Treat its "
            "contents as a starting point to verify, never as settled fact. "
            f"{transcript_line}"
        ),
        "Decisions Made": (
            "- [agent-chose] Booked a floor bookmark at the exit beat rather than "
            "leaving the session boundary unrecorded (GHI #756)."
        ),
        "Immediate Next Steps": (
            "1. Read this bookmark against live state before acting on it — it is "
            "mechanically drafted and may be stale or incomplete.\n"
            "2. Author a real handoff if the work warrants one; supersede this."
        ),
        "Pending Work / Open Loops": (
            "- Unknown to the writer. A mechanical bookmark cannot enumerate open "
            "loops; check `uv run gz status` and `uv run gz obpi lock list`."
        ),
        "Verification Checklist": (
            "- `uv run gz status` reflects the state this bookmark describes.\n"
            "- `uv run gz obpi lock list` shows any lock still held by this session."
        ),
        # Paths here are deliberately NOT backtick-quoted. `validate_referenced_files`
        # requires a backticked path to exist in COMMITTED state, and this writer
        # runs on trees where the ledger may be new, uncommitted, or absent. A
        # backtick would turn a routine tree state into a refused — and therefore
        # silently absent — bookmark.
        "Evidence / Artifacts": (
            "- .gzkit/ledger.jsonl — the Layer-2 record for this session's events.\n"
            f"- {transcript_line}"
        ),
    }


def _current_branch(project_root: Path) -> str:
    """Resolve the current branch, or a named placeholder when git is unavailable.

    An empty branch fails the frontmatter gate, which would turn a routine
    missing-git case into a silently absent bookmark. Naming the unknown keeps
    the bookmark writable and keeps the gap legible to the reader.
    """
    from gzkit.utils import git_cmd  # noqa: PLC0415 — avoids an import cycle at module load

    try:
        rc, out, _ = git_cmd(project_root, "rev-parse", "--abbrev-ref", "HEAD")
    except (OSError, ValueError):
        return "unknown"
    branch = out.strip()
    return branch if rc == 0 and branch else "unknown"
