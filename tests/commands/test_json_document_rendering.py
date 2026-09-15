"""A `--json` document reaches stdout byte-exact, never console-rendered (GHI #1010).

`.gzkit/rules/cli.md` § Output Contracts: `--json` is *"Valid JSON to stdout"*.
A document handed to the Rich console instead of printed is edited on the way out.
Rich folds it at the console width, colours it on a terminal or under `FORCE_COLOR`
(`console.print_json` included), and consumes `[...]` spans as markup. Each verb
here runs under `hostile_console()`, which arms all three.

The `gz task` verbs are covered in `tests/test_tasks.py::TestTaskJsonIsTheDocument`,
and `gz preflight` in `tests/commands/test_preflight.py`.
"""

from __future__ import annotations

import io
import json
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from gzkit.adversary_workspace import AdversaryWorkspace
from gzkit.cli import main
from gzkit.commands import obpi_adversary_workspace
from gzkit.commands.handoff import handoff_rulings_cmd
from gzkit.handoff_rulings import record_rulings
from tests.commands.common import CliRunner, _quick_init, hostile_console, parse_json_document


class TestJsonDocumentSurvivesAHostileConsole(unittest.TestCase):
    """Parse each verb's `--json` stdout with every Rich edit armed."""

    def test_chores_doctor(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem(), hostile_console():
            result = runner.invoke(main, ["chores", "doctor", "--dry-run", "--json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        records = parse_json_document(self, result.output)
        self.assertTrue(records)
        self.assertTrue(all("slug" in record for record in records))

    def test_ledger_corrections(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init("lite")
            with hostile_console():
                result = runner.invoke(main, ["ledger", "corrections", "--json"])
        self.assertEqual(result.exit_code, 0, msg=result.output)
        self.assertEqual(parse_json_document(self, result.output), [])

    def test_handoff_rulings_carry_bracketed_rulings_verbatim(self) -> None:
        """Rulings are operator verbatim; brackets in them are data, never markup."""
        rulings = [
            "Refuse chores[demo-chore] until it declares a rung.",
            "Ship it [operator-ruled].",
        ]
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            record_rulings(rulings, base_path=base, source="seed.md")
            stdout = io.StringIO()
            with hostile_console(), redirect_stdout(stdout):
                code = handoff_rulings_cmd(as_json=True, base_path=base)
        self.assertEqual(code, 0)
        self.assertEqual(parse_json_document(self, stdout.getvalue()), rulings)

    def test_handoff_rulings_print_non_ascii_rulings_unescaped(self) -> None:
        """An operator's em dash stays an em dash on stdout, as it did before GHI #1010.

        A reader searching the printed corpus for a ruling's own words must find
        them; `\\u2014` escapes parse to the same data but hide the words.
        """
        ruling = "Keep 2 — fix the labels."
        with TemporaryDirectory() as tmp:
            base = Path(tmp)
            record_rulings([ruling], base_path=base, source="seed.md")
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                handoff_rulings_cmd(as_json=True, base_path=base)
        # output-contract: the printed bytes carry the ruling's words verbatim
        self.assertIn(ruling, stdout.getvalue())

    def test_obpi_adversary_workspace(self) -> None:
        with TemporaryDirectory() as tmp:
            workspace = AdversaryWorkspace(
                path=str(Path(tmp) / "checkout-café"),
                head_commit="0123456789abcdef0123456789abcdef01234567",
                dirty=False,
                source_digest="sha256:" + "ab" * 32,
                file_count=3,
                interpreter="python3",
                python_path=str(Path(tmp) / "checkout-café" / "src"),
            )
            stdout = io.StringIO()
            with (
                patch.object(
                    obpi_adversary_workspace,
                    "materialize_adversary_workspace",
                    return_value=workspace,
                ),
                hostile_console(),
                redirect_stdout(stdout),
            ):
                code = obpi_adversary_workspace.obpi_adversary_workspace_cmd(
                    obpi_id="OBPI-0.1.0-01", destination=workspace.path, as_json=True
                )
        self.assertEqual(code, 0)
        payload = parse_json_document(self, stdout.getvalue())
        self.assertEqual(payload["source_digest"], workspace.source_digest)
        self.assertIn(workspace.path, payload["dispatch_command"])
        # output-contract: a non-ASCII checkout path prints unescaped, as before.
        # Compare the JSON-encoded form: JSON doubles a Windows path's backslashes.
        self.assertIn(json.dumps(workspace.path, ensure_ascii=False), stdout.getvalue())


if __name__ == "__main__":
    unittest.main()
