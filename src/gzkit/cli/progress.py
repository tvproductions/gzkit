"""Progress indication utilities for CLI adapter layer.

Provides context managers for spinner/progress display via Rich,
with automatic suppression in quiet and json output modes.
All progress output goes to stderr to keep stdout clean for data.
"""

from __future__ import annotations

import sys
from contextlib import contextmanager
from typing import TYPE_CHECKING

from rich.console import Console
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeElapsedColumn

if TYPE_CHECKING:
    from collections.abc import Generator

    from gzkit.cli.formatters import OutputFormatter


def _should_show_progress(formatter: OutputFormatter) -> bool:
    """Determine whether progress display is appropriate for the current mode."""
    return formatter.mode not in ("quiet", "json")


def _make_stderr_console() -> Console:
    """Create a Rich Console targeting stderr for progress output."""
    return Console(file=sys.stderr)


@contextmanager
def progress_spinner(
    message: str,
    formatter: OutputFormatter,
) -> Generator[None]:
    """Display a Rich spinner while work is in progress.

    Spinner is suppressed in quiet and json modes. Output goes to stderr.

    Args:
        message: Description of the work being done.
        formatter: OutputFormatter instance to read mode from.

    """
    if not _should_show_progress(formatter):
        yield
        return

    console = _make_stderr_console()
    with console.status(message, spinner="dots"):
        yield


@contextmanager
def progress_phase(
    label: str,
    formatter: OutputFormatter,
    *,
    step: int | None = None,
    total: int | None = None,
) -> Generator[None]:
    """Context manager for a named progress phase.

    Supports step counting when step and total are provided:
    ``[1/3] Linting...``

    Suppressed in quiet and json modes. Output goes to stderr.

    Args:
        label: Description of the phase (e.g., "Linting...").
        formatter: OutputFormatter instance to read mode from.
        step: Current step number (1-based).
        total: Total number of steps.

    """
    display_label = f"[{step}/{total}] {label}" if step is not None and total is not None else label

    if not _should_show_progress(formatter):
        yield
        return

    console = _make_stderr_console()
    with console.status(display_label, spinner="dots"):
        yield


@contextmanager
def progress_bar(
    description: str,
    formatter: OutputFormatter,
    *,
    total: float,
) -> Generator[Progress]:
    """Display a Rich progress bar for trackable work.

    Suppressed in quiet and json modes. Output goes to stderr.

    Args:
        description: Label for the progress bar.
        formatter: OutputFormatter instance to read mode from.
        total: Total number of units of work.

    Yields:
        Rich Progress instance (call ``advance(task_id)`` to update).
        In suppressed modes, yields a no-op Progress that is never rendered.

    """
    if not _should_show_progress(formatter):
        # Yield a Progress that never renders — callers can still call advance()
        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            console=Console(file=sys.stderr, quiet=True),
            disable=True,
        )
        with progress:
            progress.add_task(description, total=total)
            yield progress
        return

    console = _make_stderr_console()
    progress = Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
    )
    with progress:
        progress.add_task(description, total=total)
        yield progress
