"""Patch release command implementation (scaffold).

Full GHI-driven patch release logic will be added in OBPI-0.0.15-02 through
OBPI-0.0.15-06.  This scaffold registers the command surface and validates
the flag contract.
"""

import json

from gzkit.commands.common import console


def patch_release_cmd(*, dry_run: bool, as_json: bool) -> None:
    """Run the patch release ceremony (scaffold).

    Currently outputs a placeholder message.  Full implementation is
    tracked by ADR-0.0.15 OBPIs 02-06.
    """
    payload = {
        "status": "not_implemented",
        "message": "gz patch release is scaffolded. Full logic arrives in later OBPIs.",
        "dry_run": dry_run,
    }

    if as_json:
        print(json.dumps(payload, indent=2))  # noqa: T201
        return

    if dry_run:
        console.print(
            "[yellow]Dry run:[/yellow] gz patch release is not yet implemented. "
            "Full logic arrives in later OBPIs."
        )
        return

    console.print(
        "[yellow]gz patch release[/yellow] is not yet implemented. "
        "Full logic arrives in later OBPIs."
    )
