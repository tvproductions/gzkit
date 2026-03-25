"""Epilog builder for gzkit CLI commands.

Constructs formatted epilog strings containing ``Examples`` and ``Exit codes``
sections for use with argparse help text.  Every command and subcommand in the
CLI tree must use :func:`build_epilog` as the single construction point.
"""

from gzkit.cli.helpers.exit_codes import STANDARD_EXIT_CODES_EPILOG


def build_epilog(
    examples: list[str],
    *,
    exit_codes: str | None = None,
) -> str:
    """Build a formatted epilog string with Examples and Exit codes sections.

    Args:
        examples: List of example command strings (each a real ``gz`` invocation).
        exit_codes: Custom exit-codes block.  When *None*, the standard 4-code
            epilog from :data:`~gzkit.cli.helpers.exit_codes.STANDARD_EXIT_CODES_EPILOG`
            is used.

    Returns:
        A multi-line string suitable for ``argparse.ArgumentParser(epilog=...)``.
    """
    if not examples:
        msg = "build_epilog() requires at least one example"
        raise ValueError(msg)

    lines: list[str] = ["Examples"]
    for ex in examples:
        lines.append(f"    {ex}")
    lines.append("")

    codes = exit_codes if exit_codes is not None else STANDARD_EXIT_CODES_EPILOG
    lines.append(codes.rstrip())
    lines.append("")

    return "\n".join(lines)
