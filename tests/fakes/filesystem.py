"""In-memory fake implementation of the FileStore port."""

from pathlib import Path


class InMemoryFileStore:
    """Fake FileStore backed by a dict[str, str].

    Satisfies the FileStore protocol via structural subtyping (duck typing).
    No real filesystem I/O — deterministic and side-effect-free.
    """

    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self._store: dict[str, str] = dict(initial) if initial else {}

    @staticmethod
    def _key(path: Path) -> str:
        """Normalize path to forward slashes for cross-platform consistency."""
        return path.as_posix()

    def read_text(self, path: Path) -> str:
        key = self._key(path)
        if key not in self._store:
            raise FileNotFoundError(f"No such file: {path}")
        return self._store[key]

    def write_text(self, path: Path, content: str) -> None:
        self._store[self._key(path)] = content

    def exists(self, path: Path) -> bool:
        key = self._key(path)
        return key in self._store or any(k.startswith(key + "/") for k in self._store)

    def iterdir(self, path: Path) -> list[Path]:
        prefix = self._key(path) + "/"
        seen: set[str] = set()
        results: list[Path] = []
        for key in self._store:
            if key.startswith(prefix):
                relative = key[len(prefix) :]
                top_level = relative.split("/")[0]
                full = self._key(path) + "/" + top_level
                if full not in seen:
                    seen.add(full)
                    results.append(Path(full))
        return sorted(results)
