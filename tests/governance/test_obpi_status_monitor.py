"""The single monitor every OBPI-brief ``status:`` writer consults (GHI #669).

``ADR-0.31.0`` § Decision item 4 declares *"A single invariant monitor. Every
read or write to the artifact graph passes through one monitor."* Before GHI
#669 the terminal-clobber decision was implemented twice — once inside
``guarded_obpi_status_write`` and once inline in ``gz obpi complete`` — so the
declared property held by convention rather than by construction.

These tests assert the property itself, not the prose: each writer's refusal
must MOVE when the monitor's verdict moves. A test that only checked the
refusal text would still pass if a writer re-implemented the rule locally,
which is exactly the state this work closes.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest import mock

from gzkit.commands.closeout_form import guarded_obpi_status_write
from gzkit.governance.frontmatter_coherence import obpi_status_write_refusal


class TestObpiStatusWriteRefusal(unittest.TestCase):
    """The monitor's verdict, independent of any writer that consults it."""

    def test_permits_write_out_of_a_non_terminal_status(self) -> None:
        self.assertIsNone(
            obpi_status_write_refusal(
                brief_name="OBPI-test.md", current_status="Draft", target_status="Completed"
            )
        )

    def test_permits_write_into_a_terminal_status(self) -> None:
        """Draft -> Abandoned is a legitimate sync, not a clobber."""
        self.assertIsNone(
            obpi_status_write_refusal(
                brief_name="OBPI-test.md", current_status="Draft", target_status="Abandoned"
            )
        )

    def test_refuses_write_out_of_withdrawn(self) -> None:
        refusal = obpi_status_write_refusal(
            brief_name="OBPI-test.md", current_status="Withdrawn", target_status="Completed"
        )
        self.assertIsNotNone(refusal)

    def test_refuses_write_out_of_superseded(self) -> None:
        refusal = obpi_status_write_refusal(
            brief_name="OBPI-test.md", current_status="Superseded", target_status="Completed"
        )
        self.assertIsNotNone(refusal)

    def test_unmapped_status_is_not_treated_as_terminal(self) -> None:
        """An unrecognised term must not become an accidental refusal surface."""
        self.assertIsNone(
            obpi_status_write_refusal(
                brief_name="OBPI-test.md", current_status="Bananas", target_status="Completed"
            )
        )

    def test_refusal_carries_three_part_recovery_prose(self) -> None:
        """`.gzkit/rules/guardrail-feedback-prose.md` § Invariant.

        What failed (the brief and its status), why it is forbidden (the cited
        class), and a runnable next step. Asserted as three distinct
        obligations rather than as one golden string.
        """
        refusal = obpi_status_write_refusal(
            brief_name="OBPI-test.md", current_status="Withdrawn", target_status="Completed"
        )
        assert refusal is not None
        self.assertIn("OBPI-test.md", refusal, "what failed: names the brief")
        self.assertIn("Withdrawn", refusal, "what failed: names the observed status")
        self.assertIn("#348", refusal, "why forbidden: cites the clobber class")
        self.assertIn("gz obpi repudiate", refusal, "next step: names a runnable recovery")


class TestEveryWriterConsultsTheOneMonitor(unittest.TestCase):
    """The single-monitor property, proven by moving the monitor's verdict.

    Each test patches ``obpi_status_write_refusal`` at its home module and
    asserts the writer's behavior follows. Patching the home rather than a
    writer-local alias is deliberate: the writers import it lazily to break the
    ``frontmatter_coherence`` -> ``commands.common`` -> ``closeout_form`` cycle,
    so the home is the one binding every consumer must resolve through. A
    writer that re-implemented the terminal rule locally would pass the prose
    tests above and fail these.
    """

    def _write_brief(self, tmp: Path, status: str) -> Path:
        brief = tmp / "OBPI-test.md"
        brief.write_text(
            f"---\nid: OBPI-test\nparent: ADR-test\nstatus: {status}\n---\n\n# Test\n",
            encoding="utf-8",
        )
        return brief

    def test_guarded_write_refuses_when_the_monitor_refuses(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Draft")
            before = brief.read_text(encoding="utf-8")
            with mock.patch(
                "gzkit.governance.frontmatter_coherence.obpi_status_write_refusal",
                return_value="refused: synthetic monitor verdict",
            ):
                wrote = guarded_obpi_status_write(brief, "Completed")
            self.assertFalse(wrote, "the writer must follow the monitor, not a local rule")
            self.assertEqual(before, brief.read_text(encoding="utf-8"))

    def test_guarded_write_proceeds_when_the_monitor_permits(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            brief = self._write_brief(Path(tmp), "Withdrawn")
            with mock.patch(
                "gzkit.governance.frontmatter_coherence.obpi_status_write_refusal",
                return_value=None,
            ):
                wrote = guarded_obpi_status_write(brief, "Completed")
            self.assertTrue(wrote, "a terminal source must be refused BY THE MONITOR, not locally")
            self.assertIn("status: Completed", brief.read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main()
