"""Stable CLI parser infrastructure for gzkit.

Provides ``StableArgumentParser`` with deterministic error formatting
and ``NoHyphenBreaksFormatter`` that preserves hyphenated tokens in
help text.
"""

import argparse
import sys
import textwrap
from typing import Any


class _NoHyphenBreaksFormatter(argparse.RawDescriptionHelpFormatter):
    """HelpFormatter that never breaks on hyphens.

    Prevents tokens like ``ADR-0.0.4``, ``YYYY-MM``, and
    ``OBPI-0.0.4-01`` from being split across lines.
    """

    def _split_lines(self, text: str, width: int) -> list[str]:
        text = textwrap.dedent(text)
        return textwrap.wrap(text, width, break_on_hyphens=False)

    def _fill_text(self, text: str, width: int, indent: str) -> str:
        text = textwrap.dedent(text)
        # Preserve newlines for description/epilog (RawDescriptionHelpFormatter
        # contract) while preventing hyphen breaks within each line.
        lines = text.splitlines(keepends=True)
        return "".join(indent + line for line in lines)


class StableArgumentParser(argparse.ArgumentParser):
    """ArgumentParser with deterministic error output.

    Overrides ``error()`` to emit structured messages::

        BLOCKERS: {prog}: error: {message}

    Always exits with code 2 on parse errors, consistent with the
    CLI Doctrine 4-code map.
    """

    def __init__(self, **kwargs: Any) -> None:
        """Initialize with NoHyphenBreaksFormatter as the default formatter."""
        kwargs.setdefault("formatter_class", _NoHyphenBreaksFormatter)
        super().__init__(**kwargs)

    def error(self, message: str) -> None:  # ty: ignore[invalid-method-override]
        """Print a structured error and exit with code 2."""
        sys.stderr.write(f"BLOCKERS: {self.prog}: error: {message}\n")
        raise SystemExit(2)
