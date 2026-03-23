"""Port Protocol definitions for hexagonal architecture boundaries.

Four primary ports covering all I/O boundaries. Defined as typing.Protocol
(structural subtyping) — adapters satisfy these implicitly via duck typing.
The type checker verifies conformance at dev time.
"""

from pathlib import Path
from typing import Protocol


class FileStore(Protocol):
    """Port for filesystem operations."""

    def read_text(self, path: Path) -> str: ...

    def write_text(self, path: Path, content: str) -> None: ...

    def exists(self, path: Path) -> bool: ...

    def iterdir(self, path: Path) -> list[Path]: ...


class ProcessRunner(Protocol):
    """Port for subprocess execution."""

    def run(self, cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]: ...


class LedgerStore(Protocol):
    """Port for append-only event persistence."""

    def append(self, event: dict) -> None: ...

    def read_all(self) -> list[dict]: ...


class ConfigStore(Protocol):
    """Port for configuration persistence."""

    def load(self) -> dict: ...

    def save(self, data: dict) -> None: ...
