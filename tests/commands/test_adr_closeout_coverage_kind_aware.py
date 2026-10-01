"""GHI #1154 — ADR closeout applies the same REQ-kind distinction as OBPI completion.

``gz obpi complete`` requires an ``@covers`` test only for BEHAVIOR REQs
(``.gzkit/rules/tests.md`` § REQ Scope Discipline). The ADR closeout gap check
must not demand one for SUPPORT or STRUCTURAL-FENCE REQs, or an OBPI that
completed cleanly leaves its ADR unclosable.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from gzkit.commands.adr_audit import _check_adr_obpi_coverage_gaps

_ADR = "ADR-9.9.9-fixture"
_OBPI = "OBPI-9.9.9-01-fixture"


def _gaps(criteria: str) -> list[tuple[str, list[str]]]:
    with tempfile.TemporaryDirectory() as td:
        root = Path(td)
        obpis = root / "docs" / "design" / "adr" / "pool" / _ADR / "obpis"
        obpis.mkdir(parents=True)
        (obpis / f"{_OBPI}.md").write_text(
            f"# {_OBPI}\n\n## Acceptance Criteria\n\n{criteria}\n", encoding="utf-8"
        )
        (root / "tests").mkdir()
        return _check_adr_obpi_coverage_gaps(_ADR, root, SimpleNamespace(path=None))


class TestAdrCloseoutCoverageIsKindAware(unittest.TestCase):
    def test_behavior_req_without_test_is_a_gap(self):
        gaps = _gaps("- [ ] REQ-9.9.9-01-01 [BEHAVIOR]: does a thing.")
        self.assertEqual(gaps, [(_OBPI, ["REQ-9.9.9-01-01"])])

    def test_untagged_legacy_req_defaults_to_behavior(self):
        gaps = _gaps("- [ ] REQ-9.9.9-01-01: does a thing.")
        self.assertEqual(gaps, [(_OBPI, ["REQ-9.9.9-01-01"])])

    def test_support_and_fence_reqs_need_no_test(self):
        criteria = (
            "- [ ] REQ-9.9.9-01-01 [SUPPORT]: a doc exists.\n"
            "- [ ] REQ-9.9.9-01-02 [STRUCTURAL-FENCE]: a cross-OBPI invariant."
        )
        self.assertEqual(_gaps(criteria), [])

    def test_only_the_behavior_req_is_reported_in_a_mixed_brief(self):
        criteria = (
            "- [ ] REQ-9.9.9-01-01 [SUPPORT]: a doc exists.\n"
            "- [ ] REQ-9.9.9-01-02 [BEHAVIOR]: does a thing."
        )
        self.assertEqual(_gaps(criteria), [(_OBPI, ["REQ-9.9.9-01-02"])])


if __name__ == "__main__":
    unittest.main()
