"""In-memory fake implementation of the ConfigStore port."""


class InMemoryConfigStore:
    """Fake ConfigStore backed by a dict.

    Satisfies the ConfigStore protocol via structural subtyping (duck typing).
    No real file I/O — deterministic and side-effect-free.
    """

    def __init__(self, initial: dict | None = None) -> None:
        self._data: dict = dict(initial) if initial else {}

    def load(self) -> dict:
        return dict(self._data)

    def save(self, data: dict) -> None:
        self._data = dict(data)
