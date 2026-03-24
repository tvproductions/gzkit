"""Test fakes package — in-memory implementations of the gzkit port protocols.

All fakes satisfy their corresponding Protocol via structural subtyping (duck typing).
No real I/O, no side effects, deterministic.
"""

from tests.fakes.config import InMemoryConfigStore
from tests.fakes.filesystem import InMemoryFileStore
from tests.fakes.ledger import InMemoryLedgerStore
from tests.fakes.process import InMemoryProcessRunner

__all__ = [
    "InMemoryConfigStore",
    "InMemoryFileStore",
    "InMemoryLedgerStore",
    "InMemoryProcessRunner",
]
