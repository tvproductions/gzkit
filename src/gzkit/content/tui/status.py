"""Rich status line for gz content render/edit (OBPI-0.0.34-05)."""

from __future__ import annotations

from rich.console import Console


def render_status_line(
    *,
    operation: str,
    source: str,
    result: str,
    byte_count: int | None = None,
) -> None:
    """Print a Claude-Code-style status line to stderr.

    Only call when sys.stdout.isatty() is True.
    Goes to stderr so stdout remains machine-readable.
    """
    console = Console(stderr=True, highlight=False)
    size_str = _format_bytes(byte_count) if byte_count is not None else ""
    suffix = f" ({size_str})" if size_str else ""
    console.print(f"[green]✓[/green] {operation} [bold]{source}[/bold] → {result}{suffix}")


def _format_bytes(n: int) -> str:
    if n < 1024:
        return f"{n} B"
    kib = n / 1024
    if kib < 1024:
        return f"{kib:.1f} KiB"
    mib = kib / 1024
    return f"{mib:.1f} MiB"
