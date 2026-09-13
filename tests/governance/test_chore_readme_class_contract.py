"""The chores authoring contract names the classes and rungs the code enforces (GHI #999 step 4).

`src/gzkit/chores/README.md` is the authoring contract `.gzkit/rules/chores.md`
sends a chore author to. It states the five classes and the four-rung ladder
in prose tables, while `ChoreDeclaration` validates the values and the rung
audit enforces the ladder order. Two copies with nothing holding them equal is
the shape GHI #1002 measured drifting in 17 of 40 chores, so the README's
tables are held to the code: a class added to the model, or a rung reordered in
the audit, fails here until the contract says so.
"""

from __future__ import annotations

import re
import unittest
from pathlib import Path
from typing import get_args

from gzkit.commands.chores_declaration import ChoreClass
from gzkit.governance.trust_audits.chores import _RUNG_ORDER

_README = Path(__file__).resolve().parents[2] / "src" / "gzkit" / "chores" / "README.md"
_ROW_KEY_RE = re.compile(r"^\|\s*`(?P<key>[a-z-]+)`\s*\|")


def _table_keys(text: str, heading: str) -> list[str]:
    """Return the backticked first-column keys of the table under ``## <heading>``."""
    match = re.search(rf"^## {re.escape(heading)}\n(?P<body>.*?)(?=^## |\Z)", text, re.M | re.S)
    if match is None:
        return []
    rows = (_ROW_KEY_RE.match(line) for line in match.group("body").splitlines())
    return [row.group("key") for row in rows if row]


class TestReadmeNamesTheEnforcedVocabulary(unittest.TestCase):
    def setUp(self) -> None:
        self.text = _README.read_text(encoding="utf-8")

    def test_classes_table_names_exactly_the_declarable_classes(self) -> None:
        self.assertEqual(
            sorted(_table_keys(self.text, "The Five Classes")),
            sorted(get_args(ChoreClass)),
            "The README's class table must name every class ChoreDeclaration accepts and "
            "no other; an author reading it would otherwise declare a class the model "
            "refuses, or never learn one exists.",
        )

    def test_rungs_table_states_the_ladder_in_enforced_order(self) -> None:
        # Order is the semantics: a workflow step's stage may not rank above
        # the rung, so a README listing the ladder out of order teaches the
        # wrong ceiling.
        self.assertEqual(
            tuple(_table_keys(self.text, "The Four Rungs")),
            _RUNG_ORDER,
            "The README's rung table must list the ladder in the order "
            "audit_chore_rung_conformance ranks it.",
        )


class TestTableKeysReadsOnlyTheNamedSection(unittest.TestCase):
    def test_a_value_named_under_another_heading_does_not_count(self) -> None:
        # The Class Declaration field reference names every class in one cell;
        # it must not satisfy the check for a missing classes table.
        text = "## Class Declaration\n\n| `class` | `conformance` · `coherence` |\n"
        self.assertEqual(_table_keys(text, "The Five Classes"), [])

    def test_rows_stop_at_the_next_heading(self) -> None:
        text = "## The Four Rungs\n\n| `observe` | nothing |\n\n## Next\n\n| `repair` | x |\n"
        self.assertEqual(_table_keys(text, "The Four Rungs"), ["observe"])


if __name__ == "__main__":
    unittest.main()
