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
"""

from __future__ import annotations

from pathlib import Path

from pydantic import BaseModel, ConfigDict, Field

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


def build_advisement(project_root: Path, *, now: str) -> Advisement:
    """Build the session-start advisement for the newest handoff.

    Never raises. ``SessionStart`` runs before there is an agent to read a
    traceback, and a hook that dies takes the orientation down with it — so an
    unreadable tree, an absent handoff store, or a malformed document all yield
    ``present=False`` rather than an exception.
    """
    try:
        from gzkit.handoff_api import resume_handoff  # noqa: PLC0415

        result = resume_handoff(adr_id=None, base_path=project_root, now=now)
    except Exception:  # noqa: BLE0001 — see docstring: no failure may escape here
        return Advisement(present=False)

    if result is None:
        return Advisement(present=False)

    body = _render(result)
    truncated = len(body) > ADVISEMENT_CHAR_BUDGET
    if truncated:
        body = body[: ADVISEMENT_CHAR_BUDGET - len(_TRUNCATION_NOTE)] + _TRUNCATION_NOTE

    return Advisement(
        present=True,
        text=body,
        handoff_path=result.path,
        staleness=str(result.staleness),
        truncated=truncated,
    )


def _render(result: object) -> str:
    """Render the advisement body from a ``ResumeResult``.

    Ordered so the load-bearing sentence survives truncation: what this is, that
    it only ADVISES, and how to rule on it come first; the enumerated steps come
    last, because a clipped step list still leaves the operator able to act.
    """
    path = getattr(result, "path", "")
    staleness = getattr(result, "staleness", "")
    steps = list(getattr(result, "next_steps", []) or [])

    lines = [
        "## Resumed handoff — review before acting",
        "",
        f"- Path: `{path}`",
        f"- Freshness: {staleness}",
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
        "Only a `proceed` decision lifts the resume gate. `pause`, `hold`, and "
        "`revert` are equally bookable rulings and leave the gate armed. Use "
        "`--set-aside` to record any advised step the operator declines.",
    ]
    if steps:
        lines += ["", "### Advised steps", ""]
        lines += [f"{i}. {step}" for i, step in enumerate(steps, start=1)]
    return "\n".join(lines)
