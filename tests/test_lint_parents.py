"""Tests for Path(__file__).parents[ lint rule.

@covers OBPI-0.0.7-05-lint-rule-and-check-expansion
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.quality import run_parents_pattern_lint


def covers(target: str):  # noqa: D401
    """Identity decorator linking test to ADR/OBPI target for traceability."""

    def _identity(obj):  # type: ignore[no-untyped-def]
        return obj

    return _identity


class TestParentsPatternLint(unittest.TestCase):
    """Verify the parents-pattern lint rule catches violations."""

    @covers("REQ-0.0.7-05-04")
    def test_clean_source_passes(self):
        """Given clean source, lint exits 0."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "clean.py").write_text(
                'from pathlib import Path\nconfig_dir = Path("config")\n',
                encoding="utf-8",
            )
            result = run_parents_pattern_lint(root)
            self.assertTrue(result.success)
            self.assertEqual(result.returncode, 0)

    @covers("REQ-0.0.7-05-01")
    def test_violation_detected(self):
        """Given source with Path(__file__).parents[, lint fails."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "bad.py").write_text(
                "from pathlib import Path\n_ROOT = Path(__file__).resolve().parents[3]\n",
                encoding="utf-8",
            )
            result = run_parents_pattern_lint(root)
            self.assertFalse(result.success)
            self.assertEqual(result.returncode, 1)
            self.assertIn("parents[", result.stdout)
            self.assertIn("bad.py:2", result.stdout)

    def test_parent_without_bracket_allowed(self):
        """Path(__file__).parent (no bracket index) is not flagged."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "ok.py").write_text(
                "from pathlib import Path\n_DIR = Path(__file__).parent\n",
                encoding="utf-8",
            )
            result = run_parents_pattern_lint(root)
            self.assertTrue(result.success)

    def test_test_files_not_scanned(self):
        """Test files (outside src/gzkit/) are not scanned."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            # src/gzkit/ is clean
            src = root / "src" / "gzkit"
            src.mkdir(parents=True)
            (src / "__init__.py").write_text("", encoding="utf-8")
            # tests/ has the pattern — should NOT be flagged
            tests = root / "tests"
            tests.mkdir()
            (tests / "test_foo.py").write_text(
                "from pathlib import Path\n_ROOT = Path(__file__).resolve().parents[1]\n",
                encoding="utf-8",
            )
            result = run_parents_pattern_lint(root)
            self.assertTrue(result.success)

    def test_missing_src_dir_passes(self):
        """If src/gzkit/ doesn't exist, lint passes gracefully."""
        with tempfile.TemporaryDirectory() as tmp:
            result = run_parents_pattern_lint(Path(tmp))
            self.assertTrue(result.success)


if __name__ == "__main__":
    unittest.main()
