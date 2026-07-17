"""gz handoff — operator-facing surface over the handoff authoring API.

Surfaces the fail-closed handoff authoring gate (``gzkit.handoff_api``, shipped
by OBPI-0.0.65-02) as a CLI verb group (ADR-0.0.65 § Decision #3). ``gz handoff
create`` routes authoring through :func:`validate_handoff_document` so a handoff
is mechanically validated rather than hand-written markdown; ``gz handoff list``
and ``gz handoff resume`` are read-only projections over the on-disk corpus.

Thin adapter contract: NO domain logic lives here. Each command builds a
structured payload from the API's Pydantic return objects and either serializes
it (``--json``) or renders it for humans. The ``airlock in|out`` verb group is
the structural exemplar.

@covers ADR-0.0.65 (OBPI-0.0.65-03)
"""

from __future__ import annotations

import json
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.handoff_api import (
    HandoffInfo,
    ResumeResult,
    create_handoff,
    list_handoffs,
    resume_handoff,
)
from gzkit.handoff_validation import HandoffValidationError
from gzkit.utils import git_cmd

# Required section -> the handoff_create_cmd parameter that fills it. Every
# REQUIRED_SECTIONS entry MUST appear here: a section with no parameter cannot be
# filled from the CLI, which is exactly how GHI #692 happened — the map had two
# entries for seven sections, so the default invocation emitted five empty
# headings. Bound to REQUIRED_SECTIONS by a coherence test.
SECTION_PARAMS: dict[str, str] = {
    "Current State Summary": "summary",
    "Important Context": "context",
    "Decisions Made": "decisions",
    "Immediate Next Steps": "next_steps",
    "Pending Work / Open Loops": "pending",
    "Verification Checklist": "verification",
    "Evidence / Artifacts": "evidence",
}


def _list_payload(infos: list[HandoffInfo]) -> list[dict]:
    """Machine-readable projection of a handoff listing (the ``--json`` shape)."""
    return [info.model_dump() for info in infos]


def handoff_list_cmd(
    *,
    adr: str | None = None,
    as_json: bool = False,
    base_path: Path = Path("."),
) -> None:
    """List handoffs newest-first, optionally scoped by ADR (REQ-0.0.65-03-01).

    Read-only projection of :func:`list_handoffs`. ``--json`` emits the list of
    ``HandoffInfo`` dumps; the human form is a newest-first table.
    """
    infos = list_handoffs(adr_id=adr, base_path=base_path)
    if as_json:
        print(json.dumps(_list_payload(infos), indent=2))  # noqa: T201
        return
    if not infos:
        console.print("No handoffs found.")
        return
    for info in infos:
        console.print(f"{info.timestamp}  {info.adr_id}  {info.obpi_id or '-'}  {info.path}")


def _render_resume(result: ResumeResult) -> None:
    """Human-readable resume report — path, staleness, and first next step."""
    console.print(f"resume — {result.path}")
    console.print(f"  staleness: {result.staleness.value}")
    console.print(f"  requires human verification: {result.requires_human_verification}")
    console.print(f"  next step: {result.first_next_step or '(none extracted)'}")


def handoff_resume_cmd(
    *,
    adr: str,
    as_json: bool = False,
    now: str | None = None,
    base_path: Path = Path("."),
) -> None:
    """Resume the newest handoff for ``adr`` with staleness (REQ-0.0.65-03-02).

    Read-only projection of :func:`resume_handoff`. ``now`` is computed here when
    not supplied (the API takes it as a required parameter); it is injectable so
    staleness classification can be asserted deterministically. ``--json`` emits
    the ``ResumeResult`` dump; the human form shows path, staleness, and the
    extracted next step.
    """
    resolved_now = now if now is not None else datetime.now(UTC).isoformat()
    result = resume_handoff(adr_id=adr, base_path=base_path, now=resolved_now)
    if as_json:
        print(json.dumps(result.model_dump(), indent=2))  # noqa: T201
        return
    _render_resume(result)


def _current_branch(base_path: Path) -> str:
    """Resolve the current git branch, or empty string when unavailable.

    An empty branch is not silently tolerated: it fails the downstream
    frontmatter gate (fail-closed), which is the correct refusal.
    """
    root = get_project_root() if base_path == Path(".") else base_path
    rc, out, _ = git_cmd(root, "rev-parse", "--abbrev-ref", "HEAD")
    return out.strip() if rc == 0 else ""


def handoff_create_cmd(
    *,
    adr: str,
    slug: str,
    agent: str,
    decisions: str,
    branch: str | None = None,
    summary: str | None = None,
    context: str | None = None,
    next_steps: str | None = None,
    pending: str | None = None,
    verification: str | None = None,
    evidence: str | None = None,
    obpi: str | None = None,
    continues_from: str | None = None,
    session_id: str | None = None,
    as_json: bool = False,
    base_path: Path = Path("."),
) -> None:
    """Author a handoff through the fail-closed gate (REQ-0.0.65-03-03).

    Builds all seven required sections from their flags and routes them through
    :func:`create_handoff`. On a validation refusal NOTHING is written and the
    verb exits 1; on success the written path is reported.

    Every required section has a flag (GHI #692). Previously only Decisions Made
    and Current State Summary did, so the default invocation emitted five empty
    headings and the gate — which checked presence, not population — blessed the
    result. An unsupplied section is now a refusal, not a silent hollow.
    """
    supplied = {
        "summary": summary,
        "context": context,
        "decisions": decisions,
        "next_steps": next_steps,
        "pending": pending,
        "verification": verification,
        "evidence": evidence,
    }
    sections = {
        section: body
        for section, param in SECTION_PARAMS.items()
        if (body := supplied[param]) is not None
    }
    try:
        path = create_handoff(
            adr_id=adr,
            branch=branch or _current_branch(base_path),
            agent=agent,
            slug=slug,
            sections=sections,
            obpi_id=obpi,
            continues_from=continues_from,
            session_id=session_id,
            base_path=base_path,
        )
    except HandoffValidationError as exc:
        console.print(f"[red]Refusing to write handoff:[/red] {exc}", style="red")
        raise SystemExit(1) from exc

    if as_json:
        print(json.dumps({"path": path.as_posix()}))  # noqa: T201
        return
    console.print(path.as_posix())
