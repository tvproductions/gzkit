"""Common CLI flags for gzkit commands.

Provides ``add_common_flags`` to register --quiet, --verbose, and --debug
on any ArgumentParser with idempotency guards.
"""

import argparse

from gzkit.cli.helpers.standard_options import _option_exists

_QUIET_HELP = "Suppress non-error output"
_VERBOSE_HELP = "Enable verbose output"
_DEBUG_HELP = "Enable debug mode with full tracebacks"


def add_common_flags(
    parser: argparse.ArgumentParser,
    *,
    quiet_help: str | None = None,
    verbose_help: str | None = None,
    debug_help: str | None = None,
) -> argparse.ArgumentParser:
    """Register --quiet/-q, --verbose/-v, and --debug on *parser*.

    ``--quiet`` and ``--verbose`` are mutually exclusive.  ``--debug``
    enables full tracebacks and DEBUG-level logging.

    Calling this function more than once on the same parser is safe; any
    flags already registered are silently skipped.

    Args:
        parser: The ArgumentParser (or subparser) to configure.
        quiet_help: Override help text for ``--quiet``.
        verbose_help: Override help text for ``--verbose``.
        debug_help: Override help text for ``--debug``.

    Returns:
        The same *parser* for chaining.
    """
    # Only create the mutually exclusive group when neither flag is registered.
    # Partial pre-registration (one without the other) is unsupported — skip
    # both to avoid orphaned groups that break the exclusivity invariant.
    quiet_already = _option_exists(parser, "--quiet")
    verbose_already = _option_exists(parser, "--verbose")

    if not quiet_already and not verbose_already:
        group = parser.add_mutually_exclusive_group()
        group.add_argument(
            "--quiet",
            "-q",
            action="store_true",
            dest="quiet",
            help=quiet_help if quiet_help is not None else _QUIET_HELP,
        )
        group.add_argument(
            "--verbose",
            "-v",
            action="store_true",
            dest="verbose",
            help=verbose_help if verbose_help is not None else _VERBOSE_HELP,
        )

    if not _option_exists(parser, "--debug"):
        parser.add_argument(
            "--debug",
            action="store_true",
            dest="debug",
            help=debug_help if debug_help is not None else _DEBUG_HELP,
        )

    return parser
