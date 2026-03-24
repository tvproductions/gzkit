"""In-memory fake implementation of the LedgerStore port."""


class InMemoryLedgerStore:
    """Fake LedgerStore backed by a list[dict].

    Satisfies the LedgerStore protocol via structural subtyping (duck typing).
    No real file I/O — deterministic and side-effect-free.
    """

    def __init__(self) -> None:
        self._events: list[dict] = []

    def append(self, event: dict) -> None:
        self._events.append(dict(event))

    def read_all(self) -> list[dict]:
        return [dict(e) for e in self._events]
