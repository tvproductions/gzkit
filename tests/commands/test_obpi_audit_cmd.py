"""Tests for gz obpi audit command — REQ-0.0.67-02-03.

Verifies that ``obpi_audit_cmd`` produces a well-formed ``obpi-audit`` ledger
entry with ``criteria_evaluated`` when called with an OBPI id or ``--adr``
scope.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path
from unittest import mock

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


class TestCoverageScopedToBriefUnit(unittest.TestCase):
    """``gz obpi audit`` coverage denominator is the OBPI's unit of work (GHI #591).

    The per-OBPI coverage criterion must measure the brief-delivered ``src/``
    code against the OBPI's own tests — NOT the whole ``src/`` tree, which is
    structurally unreachable for any well-scoped OBPI and makes the criterion
    noise. These tests pin the semantic that the denominator is the brief's
    ``Allowed Paths`` ``src/`` entries.
    """

    def _write_brief(self, tmp: Path) -> Path:
        brief = tmp / "OBPI-0.0.99-01-test.md"
        brief.write_text(
            "---\nid: OBPI-0.0.99-01-test\nparent: ADR-0.0.99\nlane: Lite\n"
            "status: Draft\n---\n"
            "# OBPI-0.0.99-01: Test\n\n"
            "## Allowed Paths\n\n"
            "- `src/gzkit/commands/obpi_audit_cmd.py` — the delivered module\n"
            "- `src/gzkit/governance/widgets/` — a delivered package dir\n"
            "- `tests/commands/test_obpi_audit_cmd.py` — the OBPI's own tests\n"
            "- `docs/user/manpages/obpi-audit.md` — coupled doc surface\n",
            encoding="utf-8",
        )
        return brief

    def test_brief_src_paths_filters_to_src_unit_of_work(self) -> None:
        """_brief_src_paths returns only ``src/`` entries, dirs globbed.

        The coverage denominator is the OBPI's delivered code: the brief's
        ``Allowed Paths`` entries under ``src/``. Non-src entries (tests, docs)
        are the test surface and the coupled surfaces — not the measured unit —
        so they are excluded. A directory entry becomes a recursive glob so
        coverage can match the files beneath it.
        """
        from tempfile import TemporaryDirectory

        from gzkit.commands.obpi_audit_cmd import _brief_src_paths

        with TemporaryDirectory() as td:
            brief = self._write_brief(Path(td))
            src_paths = _brief_src_paths(brief)

        self.assertEqual(
            src_paths,
            ["src/gzkit/commands/obpi_audit_cmd.py", "src/gzkit/governance/widgets/*"],
            msg="only src/ entries form the denominator; dir entries become globs",
        )

    def test_measure_coverage_scopes_report_to_brief_unit(self) -> None:
        """_measure_coverage scopes the ``coverage report`` denominator to the unit.

        When given the brief's ``src/`` paths, the ``coverage report`` invocation
        must carry ``--include`` naming exactly those paths — so the reported
        percentage is "the OBPI's delivered code is N% exercised by its own
        tests", not "the whole src/ tree is N% exercised". Reverting to a
        whole-src denominator (no ``--include``) re-introduces GHI #591 and must
        fail this test.
        """
        from gzkit.commands import obpi_audit_cmd

        include = ["src/gzkit/commands/obpi_audit_cmd.py", "src/gzkit/governance/widgets/*"]
        report_calls: list[list[str]] = []

        def fake_run(cmd, *args, **kwargs):  # type: ignore[no-untyped-def]
            if "report" in cmd:
                report_calls.append(list(cmd))
                return mock.Mock(returncode=0, stdout="73.0\n", stderr="")
            return mock.Mock(returncode=0, stdout="", stderr="")

        with mock.patch.object(obpi_audit_cmd.subprocess, "run", side_effect=fake_run):
            pct = obpi_audit_cmd._measure_coverage(
                Path("."), [Path("tests/commands/test_obpi_audit_cmd.py")], include
            )

        self.assertEqual(pct, 73.0)
        self.assertEqual(len(report_calls), 1, msg="exactly one coverage report call")
        report_cmd = report_calls[0]
        self.assertIn(
            "--include=" + ",".join(include),
            report_cmd,
            msg=f"report denominator must be scoped to the brief unit; saw {report_cmd}",
        )


if __name__ == "__main__":
    unittest.main()
