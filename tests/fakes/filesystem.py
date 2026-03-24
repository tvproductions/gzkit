"""In-memory fake implementation of the FileStore port."""

from pathlib import Path


class InMemoryFileStore:
    """Fake FileStore backed by a dict[str, str].

    Satisfies the FileStore protocol via structural subtyping (duck typing).
    No real filesystem I/O — deterministic and side-effect-free.
    """

    def __init__(self, initial: dict[str, str] | None = None) -> None:
        self._store: dict[str, str] = dict(initial) if initial else {}

    def read_text(self, path: Path) -> str:
        key = str(path)
        if key not in self._store:
            raise FileNotFoundError(f"No such file: {path}")
        return self._store[key]

    def write_text(self, path: Path, content: str) -> None:
        self._store[str(path)] = content

    def exists(self, path: Path) -> bool:
        key = str(path)
        return key in self._store or any(k.startswith(key + "/") for k in self._store)

    def iterdir(self, path: Path) -> list[Path]:
        prefix = str(path) + "/"
        seen: set[str] = set()
        results: list[Path] = []
        for key in self._store:
            if key.startswith(prefix):
                relative = key[len(prefix) :]
                top_level = relative.split("/")[0]
                full = str(path) + "/" + top_level
                if full not in seen:
                    seen.add(full)
                    results.append(Path(full))
        return sorted(results)
