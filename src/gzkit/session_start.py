"""Session-start handoff advisement (GHI #757).

The entry edge's counterpart to :mod:`gzkit.session_exit`. Advisement was
passive: ``SessionStart`` stdout lands as ``additionalContext`` — text the model
*may* act on, defer, or skip — so the operator retyped the request every
session (*"i ask you to review the handoff every start ... this is due to me
regularly running /clear during multi-task sessions"*).

**Binding without a gate.** The fix is to seed the turn, not to add a second
refusal: the entry edge already blocks hard, and doubling down on the edge that
was never the problem is what made the lifecycle lopsided in the first place.
Claude Code's ``SessionStart`` accepts ``initialUserMessage``, which becomes an
actual first turn; Codex has no equivalent and injects passively. So the text
this module builds is emitted through BOTH channels — passive context always,
seeded turn where the harness supports it. Advisement must work passively, with
``initialUserMessage`` as a Claude-side upgrade rather than a correctness
dependency.

**Advises, never authorizes.** GHI #574's obligation survives untouched: a
handoff must never become self-authorizing. Seeding the turn makes the review
happen; it does not make the work approved. The advisement text says so, and
points at ``gz handoff decide`` as the only surface that lifts the gate.

**Guards the document it injects (GHI #850).**
``gz validate --transcribed-adr-counts`` names its subject as "the handoff a
resuming session reads", but runs only inside ``gz check`` — at commit time.
The exit beat writes its bookmark *after* the last commit opportunity, so an
authored-but-uncommitted handoff reaches this module unguarded, which is how a
stale ``1/10`` was injected on 2026-08-22 and acted on before anything caught
it. Consumption is the moment the guard's own message describes, so the scan
runs here too. It WARNS and never refuses: this hook exits 0 always, and
capture must never be blocked.

**Qualifies the tree it selected from (GHI #872).** ``Freshness`` measures the
AGE OF THE SELECTED DOCUMENT and can say nothing about whether the corpus it was
selected from is current — a fetch updates refs, never the working tree. On a
clone 8 commits behind ``origin/main`` this module rendered ``Freshness: Fresh``
beside a handoff three generations stale, while ``scripts/session_orientation``
rendered the caveat for the same state and had it clipped by output truncation.
Both renderers now carry the one qualifier from :mod:`gzkit.remote_divergence`,
fenced by a differential rather than by a convention.
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

from gzkit.remote_divergence import RemoteDivergence, behind_origin_caveat, probe_remote_divergence

__all__ = ["ADVISEMENT_CHAR_BUDGET", "Advisement", "build_advisement"]

#: Claude Code caps `SessionStart` hook output at 10,000 characters; over-cap
#: output spills to a file and is replaced by a preview. Codex's
#: `additionalContextLimit` is tighter still (~2,500 tokens). Budget well under
#: the cap so the summary — the part that must survive — always arrives intact.
ADVISEMENT_CHAR_BUDGET = 4000

_TRUNCATION_NOTE = "\n\n[advisement truncated to fit the harness output budget]"


class Advisement(BaseModel):
    """The entry-edge advisement for one session start."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    present: bool = Field(..., description="Whether a handoff was found to advise on")
    text: str = Field("", description="The advisement body, within budget")
    handoff_path: str | None = Field(None, description="Path of the advised handoff")
    staleness: str | None = Field(None, description="Staleness classification")
    truncated: bool = Field(False, description="Whether the body was cut to fit budget")
    transcribed_count_lines: tuple[int, ...] = Field(
        (), description="Lines of the advised handoff carrying a live transcribed ADR count"
    )


def build_advisement(
    project_root: Path, *, now: str, divergence: RemoteDivergence | None = None
) -> Advisement:
    """Build the session-start advisement for the newest handoff.

    Never raises. ``SessionStart`` runs before there is an agent to read a
    traceback, and a hook that dies takes the orientation down with it — so an
    unreadable tree, an absent handoff store, or a malformed document all yield
    ``present=False`` rather than an exception.

    ``divergence`` is probed from the tree when not supplied; pass it to render a
    known state without a subprocess. ``None`` from the probe and a level clone
    are deliberately the same rendering — neither warrants a caveat, and a
    qualifier that fired on "unknown" would fire on every non-repo checkout.
    """
    try:
        from gzkit.handoff_api import resume_handoff  # noqa: PLC0415

        result = resume_handoff(adr_id=None, base_path=project_root, now=now)
    except Exception:  # noqa: BLE001 — see docstring: no failure may escape here
        return Advisement(present=False)

    if result is None:
        return Advisement(present=False)

    if divergence is None:
        divergence = _probe_divergence(project_root)
    findings = _transcribed_count_findings(project_root, result.path)
    body = _render(result, findings, divergence)
    truncated = len(body) > ADVISEMENT_CHAR_BUDGET
    if truncated:
        body = body[: ADVISEMENT_CHAR_BUDGET - len(_TRUNCATION_NOTE)] + _TRUNCATION_NOTE

    return Advisement(
        present=True,
        text=body,
        handoff_path=result.path,
        staleness=str(result.staleness),
        truncated=truncated,
        transcribed_count_lines=tuple(number for number, _ in findings),
    )


def _probe_divergence(project_root: Path) -> RemoteDivergence | None:
    """Measure the clone's distance from ``origin/main``. Never raises.

    ``probe_remote_divergence`` already guards every failure shape; the second
    guard is here because this module's contract is that NOTHING escapes it, and
    a contract that depends on a callee keeping its own is one refactor from
    being false.
    """
    try:
        return probe_remote_divergence(project_root)
    except Exception:  # noqa: BLE001 — SessionStart has no agent to read a traceback
        return None


def _transcribed_count_findings(project_root: Path, path: str) -> list[tuple[int, str]]:
    """Scan the advised handoff for live transcribed ADR counts. Never raises.

    Scans ``path`` — the document this advisement actually resolved — rather
    than letting the guard re-select, so the warning can never name a different
    handoff than the one being injected.
    """
    try:
        from gzkit.governance.trust_audits.transcribed_counts import (  # noqa: PLC0415
            handoff_count_findings,
        )

        return handoff_count_findings(project_root, Path(path))
    except Exception:  # noqa: BLE001 — SessionStart has no agent to read a traceback
        return []


def _render_count_warning(findings: list[tuple[int, str]]) -> str:
    """Render the transcribed-count warning as one blockquote."""
    numbers = ", ".join(str(number) for number, _ in findings)
    plural = "s" if len(findings) > 1 else ""
    return (
        f"> **Do not act on the ADR count{plural} in this handoff** "
        f"(line{plural} {numbers}). A transcribed count is a Layer-3 value with no "
        "reconciliation path and goes stale the next time an OBPI is added, "
        "withdrawn, parked, or folded. Run `uv run gz adr status <ADR-ID>` for the "
        "live figure, and repair the line — `gz validate --transcribed-adr-counts` "
        "will refuse it at commit time."
    )


def _render(
    result: object,
    findings: list[tuple[int, str]] | None = None,
    divergence: RemoteDivergence | None = None,
) -> str:
    """Render the advisement body from a ``ResumeResult``.

    Ordered so the load-bearing sentence survives truncation: what this is, that
    it only ADVISES, and how to rule on it come first; the enumerated steps come
    last, because a clipped step list still leaves the operator able to act.

    The count warning sits directly under the document's identity, ahead of
    everything else, for the same reason: truncation clips the tail, and a
    warning that "this document's figures are not to be trusted" is worthless
    if it is the part that gets cut.

    The behind-origin caveat sits ahead of even that, because it is the more
    fundamental doubt: the count warning says this document's figures are
    stale, while the caveat says this may not be the right document at all.
    """
    path = getattr(result, "path", "")
    staleness = getattr(result, "staleness", "")
    steps = list(getattr(result, "next_steps", []) or [])

    lines = [
        "## Resumed handoff — review before acting",
        "",
        f"- Path: `{path}`",
        f"- Freshness: {staleness}",
    ]
    if divergence is not None and divergence.is_behind:
        lines.append(f"- {behind_origin_caveat(divergence.behind)}")
    if findings:
        lines += ["", _render_count_warning(findings)]
    lines += [
        "",
        "A handoff **advises**; it does not authorize. Present its advised steps "
        "to the operator and obtain an explicit ruling before executing any of "
        "them. Book the ruling with:",
        "",
        "```",
        "uv run gz handoff decide --handoff <path> --session-id <id> \\",
        '  --decision proceed --operator-text "<their exact words>"',
        "```",
        "",
        "`proceed`, `pause`, `hold`, and `revert` are equally bookable rulings; "
        "none gates anything — the record is Layer-2 provenance of what was "
        "decided, not an authorization. Use `--set-aside` to record any advised "
        "step the operator declines.",
    ]
    if steps:
        lines += ["", "### Advised steps", ""]
        lines += [f"{i}. {step}" for i, step in enumerate(steps, start=1)]
    return "\n".join(lines)
