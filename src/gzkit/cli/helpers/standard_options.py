"""Standard option factory functions for gzkit commands.

Each factory registers a canonical flag on the given ArgumentParser and
guards against duplicate registration so callers are safe to call them
unconditionally.
"""

import argparse

# ---------------------------------------------------------------------------
# Internal helpers
# ---------------------------------------------------------------------------


def _option_exists(parser: argparse.ArgumentParser, option_string: str) -> bool:
    """Return True if *option_string* is already registered on *parser*."""
    return option_string in parser._option_string_actions


# ---------------------------------------------------------------------------
# Public factory functions
# ---------------------------------------------------------------------------


def add_json_flag(
    parser: argparse.ArgumentParser,
    *,
    help_override: str | None = None,
) -> argparse.ArgumentParser:
    """Register ``--json`` (dest="as_json") on *parser*.

    Args:
        parser: The ArgumentParser to configure.
        help_override: Optional replacement help text.

    Returns:
        The same *parser* for chaining.
    """
    if not _option_exists(parser, "--json"):
        parser.add_argument(
            "--json",
            dest="as_json",
            action="store_true",
            help=help_override if help_override is not None else "Output as JSON",
        )
    return parser


def add_adr_option(
    parser: argparse.ArgumentParser,
    *,
    required: bool = False,
    help_override: str | None = None,
) -> argparse.ArgumentParser:
    """Register ``--adr`` on *parser*.

    Args:
        parser: The ArgumentParser to configure.
        required: Whether the option is mandatory (default: False).
        help_override: Optional replacement help text.

    Returns:
        The same *parser* for chaining.
    """
    if not _option_exists(parser, "--adr"):
        parser.add_argument(
            "--adr",
            required=required,
            help=help_override if help_override is not None else "ADR identifier (e.g., ADR-0.0.4)",
        )
    return parser


def add_dry_run_flag(
    parser: argparse.ArgumentParser,
    *,
    help_override: str | None = None,
) -> argparse.ArgumentParser:
    """Register ``--dry-run`` on *parser*.

    Args:
        parser: The ArgumentParser to configure.
        help_override: Optional replacement help text.

    Returns:
        The same *parser* for chaining.
    """
    if not _option_exists(parser, "--dry-run"):
        parser.add_argument(
            "--dry-run",
            action="store_true",
            help=help_override
            if help_override is not None
            else "Show planned actions without executing",
        )
    return parser


def add_force_flag(
    parser: argparse.ArgumentParser,
    *,
    help_override: str | None = None,
) -> argparse.ArgumentParser:
    """Register ``--force`` on *parser*.

    Args:
        parser: The ArgumentParser to configure.
        help_override: Optional replacement help text.

    Returns:
        The same *parser* for chaining.
    """
    if not _option_exists(parser, "--force"):
        parser.add_argument(
            "--force",
            action="store_true",
            help=help_override if help_override is not None else "Override safety checks",
        )
    return parser


def add_table_flag(
    parser: argparse.ArgumentParser,
    *,
    help_override: str | None = None,
) -> argparse.ArgumentParser:
    """Register ``--table`` on *parser*.

    Args:
        parser: The ArgumentParser to configure.
        help_override: Optional replacement help text.

    Returns:
        The same *parser* for chaining.
    """
    if not _option_exists(parser, "--table"):
        parser.add_argument(
            "--table",
            action="store_true",
            help=help_override if help_override is not None else "Display output as a table",
        )
    return parser
