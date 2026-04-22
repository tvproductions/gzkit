"""Top-level ``gz justify`` command handler.

Dispatches to the scaffold (default) or ``validate`` subverb handlers in
:mod:`gzkit.justify.cli`. The handler is the argparse entry point registered
in :mod:`gzkit.cli.parser_artifacts`. Non-zero exit codes are propagated via
``SystemExit`` because ``gzkit.cli.main`` swallows handler return values
(same pattern as ``obpi_precomplete_cmd``). Pure unit tests should call
``gzkit.justify.cli.handle_justify`` or ``handle_validate`` directly — they
return exit codes and never raise for routine policy decisions.
"""

from __future__ import annotations

from gzkit.cli.helpers.exit_codes import EXIT_SUCCESS
from gzkit.justify.cli import handle_justify, handle_validate


def justify_cmd(
    *,
    subverb: str | None = None,
    anchor: str | None = None,
    save: bool = False,
    output: str | None = None,
    related: str | None = None,
    draft: str | None = None,
    draft_slug: str | None = None,
    file: str | None = None,
    json_output: bool = False,
) -> int:
    """Route ``gz justify`` to either the scaffold or validate subverb."""
    if subverb == "validate":
        code = handle_validate(file=file, json_output=json_output)
    else:
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
