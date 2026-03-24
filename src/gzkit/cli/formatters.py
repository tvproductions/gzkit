"""Output formatter — single chokepoint for all CLI output.

Supports 5 modes:
- human: Rich tables, colors, progress (default)
- json:  Valid JSON to stdout, logs to stderr — never mixed
- quiet: Errors only (stderr)
- verbose: Debug-level information
- debug: Full diagnostic output including internals

Mode selection maps to CLI flags:
  default → human, --json → json, --quiet → quiet, --verbose → verbose
"""

from __future__ import annotations

import json
import os
import sys
from typing import Any, Literal

from rich.console import Console
from rich.table import Table

OutputMode = Literal["human", "json", "quiet", "verbose", "debug"]

VALID_MODES: frozenset[str] = frozenset({"human", "json", "quiet", "verbose", "debug"})


class OutputFormatter:
    """Single chokepoint for all CLI output.

    All CLI output flows through this class. Mode determines where and
    how content is rendered.
    """

    def __init__(self, mode: OutputMode = "human") -> None:
        if mode not in VALID_MODES:
            msg = f"Invalid output mode: {mode!r}. Must be one of {sorted(VALID_MODES)}"
            raise ValueError(msg)
        self._mode: OutputMode = mode
        self._console = Console(
            no_color=os.environ.get("NO_COLOR") is not None or mode != "human",
            stderr=mode == "json",
            force_terminal=os.environ.get("FORCE_COLOR") is not None and mode == "human",
        )
        self._stdout_console = Console(
            no_color=True,
            file=sys.stdout,
            highlight=False,
        )

    @property
    def mode(self) -> OutputMode:
        """Current output mode."""
        return self._mode

    @property
    def console(self) -> Console:
        """Rich Console for human-mode rendering."""
        return self._console

    def print(self, message: str, *, err: bool = False) -> None:
        """Print a message respecting the current mode.

        Args:
            message: Text to output.
            err: Force output to stderr (used for errors in all modes).
        """
        if self._mode == "quiet" and not err:
            return

        if err:
            print(message, file=sys.stderr)
            return

        if self._mode == "json":
            # In json mode, non-data text goes to stderr
            print(message, file=sys.stderr)
            return

        self._console.print(message)

    def data(self, payload: Any) -> None:
        """Output structured data.

        In json mode, serialises to stdout as JSON.
        In human mode, prints a human-readable representation.
        In quiet mode, suppressed (use err() for errors).
        In verbose/debug modes, prints with detail annotation.
        """
        if self._mode == "quiet":
            return

        if self._mode == "json":
            json_str = json.dumps(payload, indent=2, default=str)
            print(json_str, file=sys.stdout)
            return

        if isinstance(payload, dict | list):
            formatted = json.dumps(payload, indent=2, default=str)
            self._console.print(formatted)
        else:
            self._console.print(str(payload))

    def table(self, rich_table: Table) -> None:
        """Render a Rich Table.

        In json mode, this is a no-op — callers should use data() for
        machine-readable output instead.
        In quiet mode, suppressed.
        """
        if self._mode in ("quiet", "json"):
            return

        self._console.print(rich_table)

    def err(self, message: str) -> None:
        """Output an error message (always to stderr, all modes)."""
        print(message, file=sys.stderr)

    def log(self, message: str) -> None:
        """Output a log/diagnostic message.

        Shown in verbose and debug modes. In json mode, goes to stderr.
        In human mode, shown. In quiet mode, suppressed.
        """
        if self._mode == "quiet":
            return

        if self._mode == "json":
            print(message, file=sys.stderr)
            return

        self._console.print(message)

    def debug(self, message: str) -> None:
        """Output debug-level diagnostic information.

        Only shown in debug mode. In json mode, goes to stderr.
        """
        if self._mode == "debug":
            self._console.print(f"[dim]DEBUG: {message}[/dim]")
        elif self._mode == "json":
            print(f"DEBUG: {message}", file=sys.stderr)

    def verbose(self, message: str) -> None:
        """Output verbose-level information.

        Shown in verbose and debug modes only.
        """
        if self._mode in ("verbose", "debug"):
            self._console.print(message)

    @staticmethod
    def mode_from_flags(
        *,
        json_flag: bool = False,
        quiet: bool = False,
        verbose: bool = False,
        debug: bool = False,
    ) -> OutputMode:
        """Resolve output mode from CLI flags.

        Priority: json > quiet > debug > verbose > human (default).
        """
        if json_flag:
            return "json"
        if quiet:
            return "quiet"
        if debug:
            return "debug"
        if verbose:
            return "verbose"
        return "human"
