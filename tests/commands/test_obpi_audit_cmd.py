"""Tests for gz obpi audit command — REQ-0.0.67-02-03.

Verifies that ``obpi_audit_cmd`` produces a well-formed ``obpi-audit`` ledger
entry with ``criteria_evaluated`` when called with an OBPI id or ``--adr``
scope.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _seed_adr_with_brief(
    adr_id: str = "ADR-0.0.99",
    obpi_short: str = "OBPI-0.0.99-01",
) -> None:
    """Create minimal ADR package structure for audit testing."""
    adr_dir = Path("docs/design/adr/foundation") / f"{adr_id}-test"
    adr_dir.mkdir(parents=True, exist_ok=True)
    (adr_dir / f"{adr_id}-test.md").write_text(
        f"---\nid: {adr_id}\nstatus: Draft\nkind: foundation\nlane: Lite\n---\n"
        f"# {adr_id}: Test ADR\n",
        encoding="utf-8",
    )
    obpis_dir = adr_dir / "obpis"
    obpis_dir.mkdir()
    (obpis_dir / f"{obpi_short}-test.md").write_text(
        f"---\nid: {obpi_short}-test\nparent: {adr_id}\nlane: Lite\nstatus: Draft\n---\n"
        f"# {obpi_short}: Test OBPI\n",
        encoding="utf-8",
    )


class TestObpiAuditCmd(unittest.TestCase):
    """``gz obpi audit`` produces well-formed ledger entries (REQ-0.0.67-02-03)."""

    @covers("REQ-0.0.67-02-03")
    def test_single_obpi_produces_criteria_evaluated(self) -> None:
        """obpi_audit_cmd(obpi_id) emits a well-formed obpi-audit entry.

        Verifies the command exits 0 and the JSON output contains a
        ``criteria_evaluated`` list (the deterministic evidence array that
        reconcile Phase 1 depends on).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_adr_with_brief()

            result = runner.invoke(main, ["obpi", "audit", "OBPI-0.0.99-01", "--json"])
            # Exit 0 = all criteria pass; exit 1 = some criteria fail (expected in
            # temp project with no test files).  Both outcomes still emit JSON output.
            self.assertIn(result.exit_code, [0, 1], msg=result.output)

            data = json.loads(result.output)
            self.assertIn("criteria_evaluated", data, msg=result.output)
            self.assertIsInstance(data["criteria_evaluated"], list)
            self.assertGreater(
                len(data["criteria_evaluated"]),
                0,
                msg="criteria_evaluated must contain at least one criterion",
            )
            # Each criterion entry must have result and evidence fields.
            for criterion in data["criteria_evaluated"]:
                self.assertIn("criterion", criterion)
                self.assertIn("result", criterion)
                self.assertIn("evidence", criterion)

    @covers("REQ-0.0.67-02-03")
    def test_adr_scope_produces_audits_list(self) -> None:
        """obpi_audit_cmd(adr_id=...) returns audits array with criteria_evaluated.

        Verifies the ``--adr`` flag enumerates all OBPIs under the ADR
        and produces a well-formed criteria_evaluated list for each.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            _seed_adr_with_brief()

            result = runner.invoke(main, ["obpi", "audit", "--adr", "ADR-0.0.99", "--json"])
            # Exit 0 = all pass; exit 1 = some criteria fail (no tests in temp project).
            self.assertIn(result.exit_code, [0, 1], msg=result.output)

            data = json.loads(result.output)
            self.assertIn("adr_id", data)
            self.assertIn("audits", data)
            audits = data["audits"]
            self.assertEqual(len(audits), 1, msg="Exactly one OBPI seeded")
            first = audits[0]
            self.assertIn("criteria_evaluated", first)
            self.assertIsInstance(first["criteria_evaluated"], list)
            self.assertGreater(len(first["criteria_evaluated"]), 0)


if __name__ == "__main__":
    unittest.main()
