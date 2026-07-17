"""Covers-location collection excludes withdrawn OBPIs (GHI #695).

The covers-backfill scan must stay consistent with the completion check: a
withdrawn OBPI is excluded from the ADR's audit scope (``_collect_obpi_files_for_adr``
already drops it), so its REQ ``@covers`` decorators must not enter the backfill
heuristic and over-flag an otherwise-clean closeout.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.adr_audit import _collect_covers_locations_for_adr


class TestCoversLocationCollectionExcludesWithdrawnObpis(unittest.TestCase):
    """REQs owned by a non-active (withdrawn) OBPI are filtered out."""

    @staticmethod
    def _write(root: Path, rel: str, body: str) -> None:
        target = root / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(body, encoding="utf-8")

    def test_withdrawn_obpi_reqs_are_excluded_from_covers_scan(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "tests/test_thing.py",
                '@covers("REQ-0.0.99-01-01")\n'
                "def test_active() -> None:\n    pass\n\n"
                '@covers("REQ-0.0.99-02-01")\n'
                "def test_withdrawn() -> None:\n    pass\n",
            )
            # OBPI-02 is withdrawn: absent from the active set.
            active = ["OBPI-0.0.99-01-active-unit"]
            locations = _collect_covers_locations_for_adr(root, "ADR-0.0.99-example", active)
            targets = {req for req, _file, _line in locations}
            self.assertIn("REQ-0.0.99-01-01", targets)
            self.assertNotIn("REQ-0.0.99-02-01", targets)

    def test_empty_active_set_is_noop_backward_compatible(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._write(
                root,
                "tests/test_thing.py",
                '@covers("REQ-0.0.99-01-01")\ndef test_x() -> None:\n    pass\n',
            )
            locations = _collect_covers_locations_for_adr(root, "ADR-0.0.99-example", [])
            targets = {req for req, _file, _line in locations}
            self.assertIn("REQ-0.0.99-01-01", targets)


if __name__ == "__main__":
    unittest.main()
