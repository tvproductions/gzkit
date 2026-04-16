"""Tests for version sync helpers used during ADR closeout."""

import tempfile
import unittest
from pathlib import Path

from gzkit.commands.common import (
    _extract_adr_version,
    _parse_semver_tuple,
    _read_current_project_version,
    check_version_sync,
    sync_project_version,
)


class TestExtractAdrVersion(unittest.TestCase):
    def test_simple_adr_id(self) -> None:
        self.assertEqual(_extract_adr_version("ADR-0.18.0"), "0.18.0")

    def test_adr_id_with_slug(self) -> None:
        self.assertEqual(_extract_adr_version("ADR-0.19.0-closeout-audit-processes"), "0.19.0")

    def test_pool_adr_returns_none(self) -> None:
        self.assertIsNone(_extract_adr_version("ADR-pool.some-feature"))

    def test_malformed_returns_none(self) -> None:
        self.assertIsNone(_extract_adr_version("not-an-adr"))


class TestParseSemverTuple(unittest.TestCase):
    def test_basic(self) -> None:
        self.assertEqual(_parse_semver_tuple("0.18.0"), (0, 18, 0))

    def test_comparison(self) -> None:
        self.assertGreater(_parse_semver_tuple("0.18.0"), _parse_semver_tuple("0.12.0"))
        self.assertGreater(_parse_semver_tuple("0.10.0"), _parse_semver_tuple("0.9.0"))
        self.assertGreater(_parse_semver_tuple("1.0.0"), _parse_semver_tuple("0.99.0"))


class TestReadCurrentProjectVersion(unittest.TestCase):
    def test_reads_version_from_pyproject(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "test"\nversion = "0.12.0"\n',
                encoding="utf-8",
            )
            self.assertEqual(_read_current_project_version(root), "0.12.0")

    def test_missing_pyproject_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            self.assertIsNone(_read_current_project_version(Path(tmp)))

    def test_no_version_line_returns_none(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text('[project]\nname = "test"\n', encoding="utf-8")
            self.assertIsNone(_read_current_project_version(root))


class TestSyncProjectVersion(unittest.TestCase):
    def _make_project(self, root: Path, version: str = "0.12.0") -> None:
        (root / "pyproject.toml").write_text(
            f'[project]\nname = "gzkit"\nversion = "{version}"\n',
            encoding="utf-8",
        )
        src = root / "src" / "gzkit"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")
        (root / "README.md").write_text(
            f"# gzkit\n[![Version](https://img.shields.io/badge/version-{version}-blue.svg)](RELEASE_NOTES.md)\n",
            encoding="utf-8",
        )

    def test_bumps_all_three_files(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.12.0")
            updated = sync_project_version(root, "0.18.0")
            self.assertEqual(
                sorted(updated), ["README.md", "pyproject.toml", "src/gzkit/__init__.py"]
            )
            self.assertIn('"0.18.0"', (root / "pyproject.toml").read_text(encoding="utf-8"))
            self.assertIn(
                '"0.18.0"', (root / "src" / "gzkit" / "__init__.py").read_text(encoding="utf-8")
            )
            self.assertIn("version-0.18.0", (root / "README.md").read_text(encoding="utf-8"))

    def test_no_op_when_already_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.18.0")
            updated = sync_project_version(root, "0.18.0")
            self.assertEqual(updated, [])

    def test_missing_files_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "gzkit"\nversion = "0.12.0"\n',
                encoding="utf-8",
            )
            updated = sync_project_version(root, "0.18.0")
            self.assertEqual(updated, ["pyproject.toml"])


class TestCheckVersionSync(unittest.TestCase):
    def test_needs_bump(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "gzkit"\nversion = "0.12.0"\n',
                encoding="utf-8",
            )
            current, target, needs = check_version_sync(root, "ADR-0.18.0")
            self.assertEqual(current, "0.12.0")
            self.assertEqual(target, "0.18.0")
            self.assertTrue(needs)

    def test_no_bump_when_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "gzkit"\nversion = "0.18.0"\n',
                encoding="utf-8",
            )
            current, target, needs = check_version_sync(root, "ADR-0.18.0")
            self.assertFalse(needs)

    def test_no_bump_for_older_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "gzkit"\nversion = "0.18.0"\n',
                encoding="utf-8",
            )
            _, _, needs = check_version_sync(root, "ADR-0.12.0")
            self.assertFalse(needs)

    def test_pool_adr_returns_no_bump(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "gzkit"\nversion = "0.12.0"\n',
                encoding="utf-8",
            )
            _, _, needs = check_version_sync(root, "ADR-pool.some-feature")
            self.assertFalse(needs)


class TestValidateVersionConsistency(unittest.TestCase):
    """Version-consistency validation: all three version locations must agree."""

    def _make_project(
        self,
        root: Path,
        pyproject_ver: str = "0.25.3",
        init_ver: str = "0.25.3",
        badge_ver: str = "0.25.3",
    ) -> None:
        (root / "pyproject.toml").write_text(
            f'[project]\nname = "gzkit"\nversion = "{pyproject_ver}"\n',
            encoding="utf-8",
        )
        src = root / "src" / "gzkit"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text(f'__version__ = "{init_ver}"\n', encoding="utf-8")
        (root / "README.md").write_text(
            f"# gzkit\n[![Version](https://img.shields.io/badge/version-{badge_ver}-blue.svg)](RELEASE_NOTES.md)\n",
            encoding="utf-8",
        )

    def test_all_match_returns_no_errors(self) -> None:
        from gzkit.commands.version_sync import validate_version_consistency

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.25.3", "0.25.3", "0.25.3")
            errors = validate_version_consistency(root)
            self.assertEqual(errors, [])

    def test_badge_drift_detected(self) -> None:
        from gzkit.commands.version_sync import validate_version_consistency

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.25.3", "0.25.3", "0.25.0")
            errors = validate_version_consistency(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("README.md", errors[0].message)
            self.assertIn("0.25.0", errors[0].message)

    def test_init_drift_detected(self) -> None:
        from gzkit.commands.version_sync import validate_version_consistency

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.25.3", "0.25.1", "0.25.3")
            errors = validate_version_consistency(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("__init__.py", errors[0].message)

    def test_all_three_different_returns_two_errors(self) -> None:
        from gzkit.commands.version_sync import validate_version_consistency

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.25.3", "0.25.1", "0.25.0")
            errors = validate_version_consistency(root)
            self.assertEqual(len(errors), 2)

    def test_missing_files_skipped_gracefully(self) -> None:
        from gzkit.commands.version_sync import validate_version_consistency

        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "gzkit"\nversion = "0.25.3"\n',
                encoding="utf-8",
            )
            errors = validate_version_consistency(root)
            self.assertEqual(errors, [])


if __name__ == "__main__":
    unittest.main()
