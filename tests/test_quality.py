"""Tests for gzkit quality module."""

import sys
import tempfile
import unittest
from pathlib import Path

from gzkit.quality import QualityResult, run_command


class TestQualityResult(unittest.TestCase):
    """Tests for QualityResult dataclass."""

    def test_to_dict(self) -> None:
        """Result converts to dictionary."""
        result = QualityResult(
            success=True,
            command="test command",
            stdout="output",
            stderr="",
            returncode=0,
        )
        d = result.to_dict()
        self.assertEqual(d["success"], True)
        self.assertEqual(d["command"], "test command")
        self.assertEqual(d["returncode"], 0)


class TestRunCommand(unittest.TestCase):
    """Tests for command execution."""

    def test_successful_command(self) -> None:
        """Successful command returns success=True."""
        result = run_command("echo hello")
        self.assertTrue(result.success)
        self.assertIn("hello", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_failed_command(self) -> None:
        """Failed command returns success=False."""
        result = run_command("exit 1")
        self.assertFalse(result.success)
        self.assertEqual(result.returncode, 1)

    def test_command_with_cwd(self) -> None:
        """Command runs in specified directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            command = f'"{sys.executable}" -c "import os; print(os.getcwd())"'
            result = run_command(command, cwd=Path(tmpdir))
            self.assertTrue(result.success)
            self.assertEqual(Path(result.stdout.strip()).resolve(), Path(tmpdir).resolve())


if __name__ == "__main__":
    unittest.main()
