"""``gz obpi dispatch`` — record a Stage-2 subagent dispatch, or declare single-driver.

The recording machinery has existed and been correct since ADR-0.18.0; nothing
called it (GHI #845). This verb is the call. It is deliberately the *only* way
to make the Stage-2 dispatch channel report DISPATCHED, so the channel can never
be satisfied by inference.

``--single-driver`` is the compliant path for a session that genuinely cannot
dispatch — a cron run, a harness without an Agent tool, an operator-forbidden
subagent. Declaring is permitted and visible; running single-driver silently is
what ``gz obpi precomplete`` refuses.
"""

from __future__ import annotations

from pathlib import Path


def obpi_dispatch_cmd(
    *,
    obpi_id: str,
    role: str | None = None,
    model: str | None = None,
    task_id: int = 1,
    single_driver: bool = False,
    reason: str | None = None,
) -> int:
    """Handle ``gz obpi dispatch``. Returns a CLI exit code."""
    from gzkit.obpi_dispatch_channel import (
        MANDATED_STAGE2_ROLES,
        declare_single_driver,
        dispatch_channel,
        record_dispatch,
        render_dispatch_channel,
        single_driver_declaration,
    )
    from gzkit.pipeline_runtime import pipeline_plans_dir

    project_root = Path.cwd()
    plans_dir = pipeline_plans_dir(project_root)
    marker = plans_dir / f".pipeline-active-{obpi_id}.json"
    if not marker.is_file():
        print(  # noqa: T201
            f"No active pipeline marker for {obpi_id}. A dispatch is recorded "
            f"against a running pipeline - launch it with "
            f"`uv run gz obpi pipeline {obpi_id}` first."
        )
        return 1

    if single_driver:
        if not reason:
            print("--single-driver requires --reason.")  # noqa: T201
            return 1
        declare_single_driver(plans_dir, obpi_id, reason=reason)
    elif role:
        if role not in MANDATED_STAGE2_ROLES:
            allowed = ", ".join(MANDATED_STAGE2_ROLES)
            print(f"Unknown role {role!r}. Mandated Stage-2 roles: {allowed}.")  # noqa: T201
            return 1
        if not model:
            print("--role requires --model (the dispatch model tier).")  # noqa: T201
            return 1
        record_dispatch(plans_dir, obpi_id, role=role, model=model, task_id=task_id)

    print(  # noqa: T201
        render_dispatch_channel(
            dispatch_channel(plans_dir, obpi_id),
            declaration=single_driver_declaration(plans_dir, obpi_id),
        )
    )
    return 0
