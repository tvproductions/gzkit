"""Port Protocol definitions for hexagonal architecture boundaries.

Four primary ports covering all I/O boundaries. Defined as typing.Protocol
(structural subtyping) — adapters satisfy these implicitly via duck typing.
The type checker verifies conformance at dev time.
"""

from pathlib import Path
from typing import Protocol


class FileStore(Protocol):
    """Port for filesystem operations."""

    def read_text(self, path: Path) -> str:
        """Read and return the text content of a file."""
        ...

    def write_text(self, path: Path, content: str) -> None:
        """Write text content to a file."""
        ...

    def exists(self, path: Path) -> bool:
        """Check whether a path exists."""
        ...

    def iterdir(self, path: Path) -> list[Path]:
        """List the entries in a directory."""
        ...


class ProcessRunner(Protocol):
    """Port for subprocess execution."""

    def run(self, cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
        """Execute a subprocess and return (exit_code, stdout, stderr)."""
        ...


class LedgerStore(Protocol):
    """Port for append-only event persistence."""

    def append(self, event: dict) -> None:
        """Append a single event to the ledger."""
        ...

    def read_all(self) -> list[dict]:
        """Read and return all events from the ledger."""
        ...


class ConfigStore(Protocol):
    """Port for configuration persistence."""

    def load(self) -> dict:
        """Load and return the stored configuration."""
        ...

    def save(self, data: dict) -> None:
        """Persist the given configuration data."""
        ...
