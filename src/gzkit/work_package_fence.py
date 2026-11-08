"""The production-write fence on a work package (RO-14 act 4, GHI #1206).

A control that holds at launch must hold at re-entry. `gz wp dispatch` refuses all
work on a package that is blocked on the operator or accepted, and implementing
work on one stopped by an exit. This fence refuses a production write in those
same states, so that those refusals are not walked around by writing the code
without a dispatch. Operator rulings 2026-11-01, by selection: "Fence on the WP
surface (Recommended)" and "Drop bound state, land (Recommended)".

The rule lives here so the two loci that observe it cannot drift apart, the
generated PreToolUse hook and the pre-commit guard, as
:mod:`gzkit.pipeline_stage_fence` does for an OBPI run. State is read from the
ledger alone: there is no marker to lose, and a damaged or edited catalog lifts
nothing. A ledger that cannot be read fences the tree, since no state can be
shown. A package names no paths, so one fenced package fences the whole tree.

An order fences as a package does (RP-12 ruling 58): one commenced or accepted
that is blocked on the operator, accepted, or stopped by an exit holds every
write in the tree, and its refusal names the order. An order closed, or not yet
commenced, does not fence.

Three refusals of `gz wp dispatch` are not fenced. A package not yet commenced has
not been worked, so nothing re-enters; it is fenced only while blocked or stopped.
The other two cannot be told from admitted work. A subject at the fix-cycle bound:
the ledger shows the same rows while the last admitted cycle runs and after it
ends. A held subject: ruling 17 stops only that subject, and a write names none.

Mode contract: the commit arm is on at the operational condition and at both
standby levels, under the `post-authoring-src-commits` pin. The write arm is on at
the operational condition and advisory at both standby levels, under the
`pipeline-gate` demotion. MEL entry: `docs/governance/harbor-ro14-obpi-forward-migration.md`
§ Act 4's reading. Self-test: `tests/commands/test_wp_fence.py`.
"""

from typing import TYPE_CHECKING, Literal

from pydantic import BaseModel, ConfigDict, Field

from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.order_ledger import is_order_blocked, order_took_stopping_exit
from gzkit.work_package_ledger import is_blocked
from gzkit.work_package_run import took_stopping_exit

if TYPE_CHECKING:
    from pathlib import Path

_UNREADABLE = "the ledger"


class FencedPackage(BaseModel):
    """One package that holds the tree against production writes."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    work_package: str = Field(..., description="The package's id, or the ledger itself")
    reason: Literal["blocked", "accepted", "stopped", "unreadable"] = Field(
        ..., description="Why it holds the fence"
    )
    order: str | None = Field(None, description="The order that holds it (RP-12 ruling 58)")


def fenced_packages(project_root: Path) -> tuple[FencedPackage, ...]:
    """Read which packages hold the fence.

    Returns:
        Each package in a refused state, oldest first; or one `unreadable` entry
        when the ledger cannot be read, because no state can then be shown.

    """
    try:
        config = GzkitConfig.load(project_root / ".gzkit.json")
        return _read_fence(Ledger(project_root / config.paths.ledger))
    except OSError, ValueError, TypeError, KeyError, RecursionError:
        return (FencedPackage(work_package=_UNREADABLE, reason="unreadable"),)


def _read_fence(ledger: Ledger) -> tuple[FencedPackage, ...]:
    states = {
        str(row.extra["work_package"]): str(row.extra["to_state"])
        for row in ledger.query(event_type="work_package_transitioned")
    }
    fenced = []
    for work_package, state in states.items():
        if state == "closed":
            continue
        if is_blocked(ledger, work_package):
            reason = "blocked"
        elif state == "accepted":
            reason = "accepted"
        elif took_stopping_exit(ledger, work_package):
            reason = "stopped"
        else:
            continue
        fenced.append(FencedPackage(work_package=work_package, reason=reason))
    return (*fenced, *_read_order_fence(ledger))


#: An order not yet commenced has not been worked, and a closed one is done (ruling 58).
_ORDER_FENCEABLE = frozenset({"commenced", "accepted"})


def _read_order_fence(ledger: Ledger) -> list[FencedPackage]:
    """Read the orders that hold the fence, as a package does (RP-12 ruling 58).

    Returns:
        Each commenced or accepted order that is blocked, accepted or stopped, oldest first.

    """
    latest = {
        str(row.extra["order"]): row.extra for row in ledger.query(event_type="order_transitioned")
    }
    fenced = []
    for order, move in latest.items():
        state = str(move["to_state"])
        if state not in _ORDER_FENCEABLE:
            continue
        if is_order_blocked(ledger, order):
            reason = "blocked"
        elif state == "accepted":
            reason = "accepted"
        elif order_took_stopping_exit(ledger, order):
            reason = "stopped"
        else:
            continue
        package = str(move["work_package"])
        fenced.append(FencedPackage(work_package=package, order=order, reason=reason))
    return fenced


def _close(work_package: str) -> str:
    return (
        f"`uv run gz wp close {work_package} --decision <decision> --attestor <who> "
        "--residual-risk <text> --evidence <text>`"
    )


def _order_recovery(fence: FencedPackage) -> str:
    wp, order = fence.work_package, fence.order
    close = (
        f"the operator closes it through Gate 5 at the order with `uv run gz wp order close "
        f"{order} --decision <decision> --attestor g0 --attestation-text <words> --evidence "
        "<text>`, which lifts this fence (RP-12 rulings 58 and 73)"
    )
    return {
        "blocked": (
            f"the operator rules and `uv run gz wp unblock {wp} --order {order} --ruling <words> "
            "--operator <who>` records it, adding `--exit <exit>` if the block found a subject at "
            "the bound; if the fence still holds, its next refusal names the next step"
        ),
        "accepted": f"acceptance has ended the order's work, so {close}",
        "stopped": (
            f"the order takes no further repair: run `uv run gz wp order accept {order} "
            f"--evidence <text>`, which excuses a stopped order its proof, then {close}"
        ),
    }[fence.reason]


def _recovery(fence: FencedPackage) -> str:
    if fence.order is not None:
        return _order_recovery(fence)
    wp = fence.work_package
    return {
        "blocked": (
            f"the operator rules and `uv run gz wp unblock {wp} --ruling <words> --operator "
            "<who>` records it, adding `--exit <exit>` if the block found a subject at the "
            "bound; if the fence still holds, its next refusal names the next step"
        ),
        "accepted": (
            "acceptance has ended the work, so the operator closes the package through "
            f"Gate 5: {_close(wp)}"
        ),
        "stopped": (
            "the package takes no further repair: commence it if it never commenced, run "
            f"`uv run gz wp accept {wp} --evidence <text>`, then the operator closes it "
            f"through Gate 5: {_close(wp)}"
        ),
        "unreadable": (
            "run `uv run gz validate --ledger`, repair what it names, and write again; the "
            "ledger is written only through `gz` verbs"
        ),
    }[fence.reason]


def _why(fence: FencedPackage) -> str:
    if fence.reason == "unreadable":
        return "the ledger or `.gzkit.json` cannot be read, so no work package's state can be shown"
    if fence.order is not None:
        return (
            f"order {fence.order} of work package {fence.work_package} is {fence.reason}, and "
            "`gz wp dispatch --order` refuses implementing work on it, so a write here would "
            "step around that refusal (RP-12 ruling 58)"
        )
    return (
        f"work package {fence.work_package} is {fence.reason}, and `gz wp dispatch` refuses "
        "implementing work on it, so a write here would step around that refusal"
    )


def work_package_write_message(fence: FencedPackage, rel_path: str) -> str:
    """Render why a production WRITE is refused while a package holds the fence.

    Returns:
        The refusal, with the governed next step.

    """
    return (
        f"BLOCKED: `{rel_path}` is a production write.\n\n"
        f"WHY: {_why(fence)} (GHI #1206).\n\n"
        f"NEXT STEP: {_recovery(fence)}. Do not work around this gate (AGENTS.md § Behavior "
        "Rules: a blocking hook is diagnosed, never worked around). `tests/**` stays open."
    )


def work_package_commit_message(fence: FencedPackage, rel_paths: list[str]) -> str:
    """Render why a COMMIT carrying production code is refused while a package holds the fence.

    Returns:
        The refusal, with the governed next step.

    """
    listed = "\n".join(f"  - {path}" for path in sorted(rel_paths))
    return (
        f"BLOCKED: this commit carries production code.\n\nStaged production paths:\n{listed}\n\n"
        f"WHY: {_why(fence)} (GHI #1206).\n\n"
        f"NEXT STEP: {_recovery(fence)}. Unstage the paths above to commit anything else; "
        "`tests/**` stays committable. Do not pass `--no-verify`."
    )
