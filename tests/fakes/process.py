"""In-memory fake implementation of the ProcessRunner port."""

from pathlib import Path


class InMemoryProcessRunner:
    """Fake ProcessRunner that returns canned (exit_code, stdout, stderr) tuples.

    Satisfies the ProcessRunner protocol via structural subtyping (duck typing).
    No real subprocess execution — deterministic and side-effect-free.

    Usage::

        runner = InMemoryProcessRunner(default=(0, "ok", ""))
        runner.register(["git", "status"], (0, "On branch main", ""))
        exit_code, stdout, stderr = runner.run(["git", "status"])
    """

    def __init__(self, default: tuple[int, str, str] = (0, "", "")) -> None:
        self._default = default
        self._responses: dict[str, tuple[int, str, str]] = {}
        self.calls: list[tuple[list[str], Path | None]] = []

    def register(self, cmd: list[str], response: tuple[int, str, str]) -> None:
        """Register a canned response for a specific command."""
        self._responses[self._key(cmd)] = response

    def run(self, cmd: list[str], cwd: Path | None = None) -> tuple[int, str, str]:
        """Return the canned response for cmd, or the default if not registered."""
        self.calls.append((list(cmd), cwd))
        return self._responses.get(self._key(cmd), self._default)

    @staticmethod
    def _key(cmd: list[str]) -> str:
        return " ".join(cmd)
