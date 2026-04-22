"""Top-level ``gz justify`` command handler.

Thin wrapper dispatching to :func:`gzkit.justify.cli.handle_justify`. The
handler is the argparse entry point registered in
``gzkit.cli.parser_artifacts``. Non-zero exit codes are propagated via
``SystemExit`` because ``gzkit.cli.main`` swallows handler return values
(same pattern as ``obpi_precomplete_cmd``). Pure unit tests should call
``gzkit.justify.cli.handle_justify`` directly — it returns the exit code
and never raises for routine policy decisions.
"""

from __future__ import annotations

from gzkit.cli.helpers.exit_codes import EXIT_SUCCESS
from gzkit.justify.cli import handle_justify


def justify_cmd(
    *,
    anchor: str | None,
    save: bool = False,
    output: str | None = None,
    related: str | None = None,
    draft: str | None = None,
    draft_slug: str | None = None,
) -> int:
    """Produce a pre-execution reasoning scaffold for an anchor or draft."""
    code = handle_justify(
        anchor=anchor,
        save=save,
        output=output,
        related=related,
        draft=draft,
        draft_slug=draft_slug,
    )
    if code != EXIT_SUCCESS:
        raise SystemExit(code)
    return EXIT_SUCCESS
