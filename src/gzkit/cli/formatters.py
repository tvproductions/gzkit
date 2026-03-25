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

import enum
import json
import os
import sys
from typing import Any

from rich.console import Console
from rich.table import Table


class OutputMode(enum.StrEnum):
    """Output mode for the CLI formatter.

    Extends ``StrEnum`` so enum members compare equal to their string values,
    preserving backwards-compatibility with callers that use plain strings.
    """

    HUMAN = "human"
    JSON = "json"
    QUIET = "quiet"
    VERBOSE = "verbose"
    DEBUG = "debug"


VALID_MODES: frozenset[str] = frozenset(m.value for m in OutputMode)


class OutputFormatter:
    """Single chokepoint for all CLI output.

    All CLI output flows through this class. Mode determines where and
    how content is rendered.
    """

    def __init__(
        self, mode: OutputMode | str = OutputMode.HUMAN, *, console: Console | None = None
    ) -> None:
        if isinstance(mode, str) and not isinstance(mode, OutputMode):
            try:
                mode = OutputMode(mode)
            except ValueError:
                msg = f"Invalid output mode: {mode!r}. Must be one of {sorted(VALID_MODES)}"
                raise ValueError(msg) from None
        self._mode: OutputMode = mode

        if console is not None:
            self._console = console
        else:
            self._console = Console(
                no_color=os.environ.get("NO_COLOR") is not None or mode != OutputMode.HUMAN,
                stderr=mode == OutputMode.JSON,
                force_terminal=os.environ.get("FORCE_COLOR") is not None
                and mode == OutputMode.HUMAN,
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

    # ------------------------------------------------------------------
    # Legacy methods (backwards-compatible)
    # ------------------------------------------------------------------

    def print(self, message: str, *, err: bool = False) -> None:
        """Print a message respecting the current mode.

        Args:
            message: Text to output.
            err: Force output to stderr (used for errors in all modes).
        """
        if self._mode == OutputMode.QUIET and not err:
            return

        if err:
            print(message, file=sys.stderr)
            return

        if self._mode == OutputMode.JSON:
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
        if self._mode == OutputMode.QUIET:
            return

        if self._mode == OutputMode.JSON:
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
        if self._mode in (OutputMode.QUIET, OutputMode.JSON):
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
        if self._mode == OutputMode.QUIET:
            return

        if self._mode == OutputMode.JSON:
            print(message, file=sys.stderr)
            return

        self._console.print(message)

    def debug(self, message: str) -> None:
        """Output debug-level diagnostic information.

        Only shown in debug mode. In json mode, goes to stderr.
        """
        if self._mode == OutputMode.DEBUG:
            self._console.print(f"[dim]DEBUG: {message}[/dim]")
        elif self._mode == OutputMode.JSON:
            print(f"DEBUG: {message}", file=sys.stderr)

    def verbose(self, message: str) -> None:
        """Output verbose-level information.

        Shown in verbose and debug modes only.
        """
        if self._mode in (OutputMode.VERBOSE, OutputMode.DEBUG):
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
            return OutputMode.JSON
        if quiet:
            return OutputMode.QUIET
        if debug:
            return OutputMode.DEBUG
        if verbose:
            return OutputMode.VERBOSE
        return OutputMode.HUMAN

    # ------------------------------------------------------------------
    # New emit* methods (REQ-04 through REQ-08)
    # ------------------------------------------------------------------

    def emit(self, data: Any) -> None:
        """Route data to the appropriate renderer based on mode.

        - dict/list: json.dumps in JSON mode; formatted print in HUMAN mode.
        - str: direct output.
        - Pydantic BaseModel: model_dump_json() in JSON mode; model_dump() in HUMAN mode.
        - Quiet mode: all output suppressed.
        - JSON mode: all data goes to stdout as valid JSON.
        """
        if self._mode == OutputMode.QUIET:
            return

        if hasattr(data, "model_dump_json"):
            # Pydantic BaseModel (duck-typed)
            if self._mode == OutputMode.JSON:
                print(data.model_dump_json(), file=sys.stdout)
            else:
                formatted = json.dumps(data.model_dump(), indent=2, sort_keys=True)
                self._console.print(formatted)
            return

        if isinstance(data, str):
            if self._mode == OutputMode.JSON:
                print(data, file=sys.stdout)
            else:
                self._console.print(data)
            return

        if isinstance(data, dict | list):
            json_str = json.dumps(data, indent=2, sort_keys=True)
            if self._mode == OutputMode.JSON:
                print(json_str, file=sys.stdout)
            else:
                self._console.print(json_str)
            return

        # Fallback for other types
        if self._mode == OutputMode.JSON:
            print(json.dumps(data, default=str), file=sys.stdout)
        else:
            self._console.print(str(data))

    def emit_error(self, message: str) -> None:
        """Write an error message to stderr regardless of output mode.

        Errors are NEVER suppressed, even in quiet mode.
        """
        print(message, file=sys.stderr)

    def emit_table(self, rich_table: Table) -> None:
        """Render a Rich table in HUMAN mode; emit dict-list JSON in JSON mode.

        In quiet mode, suppressed.
        """
        if self._mode == OutputMode.QUIET:
            return

        if self._mode == OutputMode.JSON:
            rows: list[dict[str, Any]] = []
            columns = [col.header for col in rich_table.columns]
            for row_index in range(rich_table.row_count):
                row_data: dict[str, Any] = {}
                for col_index, col_name in enumerate(columns):
                    cell = rich_table.columns[col_index]._cells[row_index]
                    row_data[str(col_name)] = str(cell)
                rows.append(row_data)
            print(json.dumps(rows, indent=2, sort_keys=True), file=sys.stdout)
            return

        self._console.print(rich_table)

    def emit_status(self, label: str, success: bool) -> None:
        """Render a status line with check/cross symbols in HUMAN mode.

        In JSON mode, emits ``{"label": label, "success": success}`` to stdout.
        In quiet mode, suppressed.
        """
        if self._mode == OutputMode.QUIET:
            return

        if self._mode == OutputMode.JSON:
            print(json.dumps({"label": label, "success": success}, sort_keys=True), file=sys.stdout)
            return

        symbol = "\u2713" if success else "\u2717"
        colour = "green" if success else "red"
        self._console.print(f"[{colour}]{symbol}[/{colour}] {label}")

    def emit_blocker(self, message: str) -> None:
        """Write a BLOCKERS message to stderr in ALL modes.

        Always emitted; never suppressed.
        """
        print(f"BLOCKERS: {message}", file=sys.stderr)
