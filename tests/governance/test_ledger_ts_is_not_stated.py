"""No production ledger-event constructor states its own `ts` (GHI #1074).

WHY: `ts` is what ORDERS the ledger. `Ledger.append` fixes an unstated `ts`
inside the write lock, at the instant the row is committed, so that two writers
cannot commit in one order while claiming another — the descending pair
`validate_ledger` refuses (`src/gzkit/validate_pkg/ledger_check.py`, which tracks
`previous_ts`). A caller that STATES a `ts` opts out of that: `ledger_row` treats
a stated stamp as deliberate and leaves it alone, which is precisely how a
construction-time stamp reached the file and inverted two writers' order before
`51999d357`.

That repair removed the duplicated idiom, but left nothing stopping a future
constructor from stating `ts` again. What stood in for a fence was documentation
— a docstring warning — and GHI #1074's close comment said so plainly:

    "That is documentation. A witness would be a `tests/governance/` audit
    asserting that no production event constructor reaching `Ledger.append`
    states a `ts`, with an explicit allowlist for the deliberate cases."

This is that witness. Operator ruling 2026-09-21 ("do").

SCOPE is the ledger only. The corpus store states `ts` on every entry by design
— `CorpusEntry.ts` is a required field with no default — and orders its rows by
APPEND order under an exclusive lock rather than by `ts`. The insights store
claims no ordering invariant at all. Neither is this defect, and flagging them
would assert an invariant they do not hold.

The constructor name set is DERIVED from `gzkit.events` and `gzkit.ledger_events`
at run time, not transcribed: a new event type joins the fence by existing.
"""

from __future__ import annotations

import ast
import inspect
import unittest
from pathlib import Path

from gzkit import events as _events
from gzkit import ledger_events as _ledger_events

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRC = _REPO_ROOT / "src" / "gzkit"

#: Deliberate statings, each with the reason it is not the defect.
#: A parse path re-hydrates rows that ALREADY carry a committed `ts`; dropping it
#: there would invent a new stamp for a historical row.
_ALLOWED: dict[str, str] = {
    "justify/evidence.py": (
        "Parse path: re-hydrates LedgerEvent rows read from disk, whose `ts` is "
        "the already-committed stamp. Never reaches Ledger.append as a new row."
    ),
}


def _constructor_names() -> frozenset[str]:
    """Return every ledger-event constructor name, derived from the modules."""
    names = {
        name
        for name, obj in vars(_events).items()
        if inspect.isclass(obj) and name.endswith("Event")
    }
    names.add("LedgerEvent")
    names.update(
        name
        for name, obj in vars(_ledger_events).items()
        if inspect.isfunction(obj) and name.endswith("_event") and not name.startswith("_")
    )
    return frozenset(names)


def _states_ts(node: ast.Call, constructors: frozenset[str]) -> bool:
    """Whether *node* calls a ledger-event constructor with an explicit ``ts``."""
    func = node.func
    name = func.attr if isinstance(func, ast.Attribute) else getattr(func, "id", "")
    if name not in constructors:
        return False
    return any(keyword.arg == "ts" for keyword in node.keywords)


def _scan(root: Path) -> dict[str, list[int]]:
    """Return ``{repo-relative path: [line, ...]}`` for every stated-``ts`` call."""
    constructors = _constructor_names()
    found: dict[str, list[int]] = {}
    for path in sorted(root.rglob("*.py")):
        try:
            tree = ast.parse(path.read_text(encoding="utf-8"))
        except (OSError, SyntaxError):
            continue
        lines = [
            node.lineno
            for node in ast.walk(tree)
            if isinstance(node, ast.Call) and _states_ts(node, constructors)
        ]
        if lines:
            found[path.relative_to(_SRC).as_posix()] = lines
    return found


def _scan_source(source: str) -> int:
    """Return how many stated-``ts`` constructor calls *source* contains."""
    constructors = _constructor_names()
    tree = ast.parse(source)
    return sum(
        1
        for node in ast.walk(tree)
        if isinstance(node, ast.Call) and _states_ts(node, constructors)
    )


_LIVE = _scan(_SRC)

#: Positive control — the shape the fence exists to catch.
_STATES_TS = """
from gzkit.events import LedgerEvent

def write():
    return LedgerEvent(event="gate_checked", id="ADR-0.1.0", ts="2026-01-01T00:00:00+00:00")
"""

#: Control — the correct shape: the writer supplies the stamp under its lock.
_LEAVES_TS_UNSTATED = """
from gzkit.events import LedgerEvent

def write():
    return LedgerEvent(event="gate_checked", id="ADR-0.1.0")
"""

#: Control — the corpus store states `ts` by design and is out of scope.
_CORPUS_ENTRY = """
from gzkit.content.models.corpus import CorpusEntry

def write():
    return CorpusEntry(id="e", surface="s", section="x", tier="compressible",
                       classification="Ambiguous", text="t", origin="o",
                       ts="2026-01-01T00:00:00+00:00")
"""


class TestNoProductionConstructorStatesTs(unittest.TestCase):
    """The fence GHI #1074's close comment specified, and its controls."""

    def test_no_unallowlisted_site_states_ts(self) -> None:
        offenders = {path: lines for path, lines in _LIVE.items() if path not in _ALLOWED}

        self.assertEqual(
            offenders,
            {},
            "a production ledger-event constructor states its own `ts`, opting out "
            "of the lock-held stamp that orders the ledger (GHI #1074)",
        )

    def test_the_allowlist_carries_no_stale_entry(self) -> None:
        """An allowlist that outlives its site silently widens the fence."""
        stale = sorted(set(_ALLOWED) - set(_LIVE))

        self.assertEqual(
            stale,
            [],
            "allowlisted path no longer states `ts`; remove the entry rather than "
            "leaving a standing permission nothing uses",
        )

    def test_every_allowlist_entry_carries_a_reason(self) -> None:
        self.assertTrue(all(reason.strip() for reason in _ALLOWED.values()))

    def test_the_fence_fires_on_a_stated_ts(self) -> None:
        self.assertEqual(_scan_source(_STATES_TS), 1)

    def test_an_unstated_ts_is_green(self) -> None:
        self.assertEqual(_scan_source(_LEAVES_TS_UNSTATED), 0)

    def test_a_corpus_entry_is_out_of_scope(self) -> None:
        self.assertEqual(
            _scan_source(_CORPUS_ENTRY),
            0,
            "the corpus orders by APPEND order under an exclusive lock and requires "
            "a stated `ts`; flagging it would assert an invariant it does not hold",
        )

    def test_the_constructor_set_is_derived_not_transcribed(self) -> None:
        constructors = _constructor_names()

        self.assertIn("LedgerEvent", constructors)
        self.assertIn("GateCheckedEvent", constructors)
        self.assertIn("gate_checked_event", constructors)
        self.assertGreater(
            len(constructors),
            100,
            "the set is read from gzkit.events and gzkit.ledger_events, so a new "
            "event type joins the fence by existing rather than by being listed",
        )
