import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


class TestGateCommands(unittest.TestCase):
    """Tests for gate verification commands."""

    def test_gates_gate1_records_event(self) -> None:
        """gates --gate 1 records gate_checked event."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.1.0"])
            # Strip template's ``status: Draft`` — Gate 1 (OBPI-0.0.16-02) now
            # validates frontmatter-ledger coherence. This test asserts
            # gate_checked emission, not default-template frontmatter content.
            adr_path = Path("design/adr/ADR-0.1.0.md")
            content = adr_path.read_text(encoding="utf-8")
            stripped = "\n".join(
                line for line in content.splitlines() if not line.strip().startswith("status:")
            )
            adr_path.write_text(stripped + "\n", encoding="utf-8")
            result = runner.invoke(main, ["gates", "--gate", "1"])
            self.assertEqual(result.exit_code, 0)
            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn("gate_checked", ledger_content)
