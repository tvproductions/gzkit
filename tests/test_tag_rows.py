"""The tag-out log's leaf row readers: RP-12 ruling 141.

`docs/governance/harbor-ro12-contractor-kit.md` § Rulings: the typed readers of
the four tag events live in `gzkit.mx.tag_rows`, which imports only the events
and the ledger, so the order writer and the repair package's close can read the
tags issued on an order without importing `gzkit.mx.tag_out` (ruling 141). An
order's standing names its tags issued, those not hung (ruling 108) and those
hung and not cleared (refusal 6, rulings 129 and 142). A malformed row is
refused by the one reader, never read past.
"""

import json
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

from gzkit.events import TagClearedEvent, TagHungEvent, TagIssuedEvent
from gzkit.ledger import Ledger, ledger_row
from gzkit.mx.tag_rows import TagOutError, order_tags

_ORDER = "ORD-01-import"
_OTHER = "ORD-02-spare"
_HANGER = "D-00000000000000aa"
_RESTORER = "D-00000000000000bb"
_ITEM = {
    "work_package": "WP-01-stamp",
    "tag_class": "Danger",
    "surface_kind": "path",
    "position": "off",
    "hazard": "The stamp generator is rewritten.",
    "removal_procedure": "Re-register the hook.",
    "source": "order-work",
    "check_level": "C",
}


def _tag_id(n: int) -> str:
    return f"TAG-{n:02d}-stamp"


class _RowsCase(unittest.TestCase):
    def setUp(self) -> None:
        self._dir = TemporaryDirectory()
        self.addCleanup(self._dir.cleanup)
        self.path = Path(self._dir.name) / "ledger.jsonl"
        self.ledger = Ledger(self.path)

    def issue(self, n: int, order: str = _ORDER) -> None:
        surface = f"src/stamp{n}.py"
        self.ledger.append(
            ledger_row(
                TagIssuedEvent.model_validate(
                    {
                        **_ITEM,
                        "event": "tag_issued",
                        "id": _tag_id(n),
                        "tag_id": _tag_id(n),
                        "order": order,
                        "surface": f"path:{surface}",
                        "surface_name": surface,
                        "mx_session_id": "mx-1",
                    }
                )
            )
        )

    def hang(self, n: int, order: str = _ORDER) -> None:
        surface = f"src/stamp{n}.py"
        self.ledger.append(
            ledger_row(
                TagHungEvent.model_validate(
                    {
                        **_ITEM,
                        "event": "tag_hung",
                        "id": _tag_id(n),
                        "tag_id": _tag_id(n),
                        "order": order,
                        "surface": f"path:{surface}",
                        "surface_name": surface,
                        "dispatch_id": _HANGER,
                        "issued_by_session": "mx-1",
                        "mx_session_id": "mx-1",
                    }
                )
            )
        )

    def clear(self, n: int, order: str = _ORDER) -> None:
        self.ledger.append(
            ledger_row(
                TagClearedEvent.model_validate(
                    {
                        "event": "tag_cleared",
                        "id": _tag_id(n),
                        "tag_id": _tag_id(n),
                        "order": order,
                        "work_package": "WP-01-stamp",
                        "dispatch_id": _RESTORER,
                        "hanging_dispatch_id": _HANGER,
                        "position_found": "off",
                        "authorized_by_session": "mx-1",
                        "mx_session_id": "mx-1",
                    }
                )
            )
        )


class OrderTagsTests(_RowsCase):
    def test_an_order_with_no_tag_has_an_empty_standing(self) -> None:
        """Ruling 117: an order with no tag issued is the case a no-isolation statement covers."""
        standing = order_tags(self.ledger, _ORDER)
        self.assertEqual((standing.issued, standing.unhung, standing.hung_uncleared), ((), (), ()))

    def test_the_standing_names_issued_unhung_and_hung_uncleared_tags(self) -> None:
        """Rulings 108, 129 and 142: unhung blocks commencement, hung-uncleared acceptance."""
        for n in (1, 2, 3):
            self.issue(n)
        self.hang(2)
        self.hang(3)
        self.clear(3)
        standing = order_tags(self.ledger, _ORDER)
        self.assertEqual(standing.issued, (_tag_id(1), _tag_id(2), _tag_id(3)))
        self.assertEqual(standing.unhung, (_tag_id(1),))
        self.assertEqual(standing.hung_uncleared, (_tag_id(2),))

    def test_another_orders_tags_are_not_counted(self) -> None:
        """Ruling 108: commencement waits on the tags issued on its own order."""
        self.issue(1, _OTHER)
        self.hang(1, _OTHER)
        standing = order_tags(self.ledger, _ORDER)
        self.assertEqual((standing.issued, standing.hung_uncleared), ((), ()))

    def test_a_malformed_tag_row_is_refused_not_read_past(self) -> None:
        """Rulings 4 and 141: one reader refuses a row its shape does not admit."""
        row = {"schema": "gzkit.ledger.v1", "event": "tag_issued", "id": "TAG-7-bad"}
        with self.path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps({**row, "ts": "2026-11-18T00:00:00+00:00"}) + "\n")
        with self.assertRaises(TagOutError):
            order_tags(self.ledger, _ORDER)
