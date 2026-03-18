import subprocess
import unittest
from pathlib import Path

from gzkit.cli import main
from tests.commands.common import CliRunner, _quick_init


class TestObpiValidateCommand(unittest.TestCase):
    def _git(self, *args: str) -> None:
        subprocess.run(["git", *args], check=True, capture_output=True, text=True)

    def _commit_all(self, message: str) -> None:
        self._git("add", "-A")
        status = subprocess.run(
            ["git", "status", "--porcelain"],
            check=True,
            capture_output=True,
            text=True,
        ).stdout.strip()
        if status:
            self._git("commit", "-m", message)

    def test_obpi_validate_prints_blockers_for_out_of_scope_changes(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])

            self._git("init")
            self._git("config", "user.email", "test@example.com")
            self._git("config", "user.name", "Test User")
            self._commit_all("chore: initial")

            obpi_path = Path("docs/design/adr/pre-release/ADR-0.1.0/obpis/OBPI-0.1.0-01-demo.md")
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            obpi_path.write_text(
                "---\n"
                "id: OBPI-0.1.0-01-demo\n"
                "parent: ADR-0.1.0\n"
                "item: 1\n"
                "lane: Lite\n"
                "status: Completed\n"
                "---\n\n"
                "# OBPI-0.1.0-01-demo\n\n"
                "## Allowed Paths\n"
                "- `docs/design/adr/pre-release/ADR-0.1.0/**` - in scope\n\n"
                "### Implementation Summary\n"
                "- Files created/modified: "
                "docs/design/adr/pre-release/ADR-0.1.0/obpis/OBPI-0.1.0-01-demo.md\n\n"
                "## Key Proof\n"
                "uv run gz adr status ADR-0.1.0 --json\n",
                encoding="utf-8",
            )
            Path("docs/outside.md").parent.mkdir(parents=True, exist_ok=True)
            Path("docs/outside.md").write_text("outside\n", encoding="utf-8")

            result = runner.invoke(main, ["obpi", "validate", str(obpi_path)])

            self.assertEqual(result.exit_code, 1)
            self.assertIn("BLOCKERS:", result.output)
            self.assertIn("docs/outside.md", result.output)

    def test_obpi_validate_passes_for_allowlisted_changes(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "0.1.0"])

            self._git("init")
            self._git("config", "user.email", "test@example.com")
            self._git("config", "user.name", "Test User")
            self._commit_all("chore: initial")

            obpi_path = Path("docs/design/adr/pre-release/ADR-0.1.0/obpis/OBPI-0.1.0-01-demo.md")
            obpi_path.parent.mkdir(parents=True, exist_ok=True)
            obpi_path.write_text(
                "---\n"
                "id: OBPI-0.1.0-01-demo\n"
                "parent: ADR-0.1.0\n"
                "item: 1\n"
                "lane: Lite\n"
                "status: Completed\n"
                "---\n\n"
                "# OBPI-0.1.0-01-demo\n\n"
                "## Allowed Paths\n"
                "- `docs/design/adr/pre-release/ADR-0.1.0/**` - in scope\n"
                "- `src/**` - in scope\n\n"
                "### Implementation Summary\n"
                "- Files created/modified: src/demo.py\n\n"
                "## Key Proof\n"
                "uv run gz adr status ADR-0.1.0 --json\n",
                encoding="utf-8",
            )
            Path("src").mkdir(exist_ok=True)
            Path("src/demo.py").write_text("print('ok')\n", encoding="utf-8")

            result = runner.invoke(main, ["obpi", "validate", str(obpi_path)])

            self.assertEqual(result.exit_code, 0)
            self.assertIn("OBPI Validation Passed", result.output)
