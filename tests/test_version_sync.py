"""Tests for version sync helpers used during ADR closeout."""

import re
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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


def _fake_uv_version(calls: list[tuple[Path, str]]):
    """A stand-in for `uv version <v> --no-sync`: rewrites pyproject.toml and uv.lock."""

    def write(project_root: Path, version: str) -> None:
        calls.append((project_root, version))
        for name in ("pyproject.toml", "uv.lock"):
            path = project_root / name
            if path.is_file():
                text = path.read_text(encoding="utf-8")
                path.write_text(
                    re.sub(
                        r'^version = "[^"]+"', f'version = "{version}"', text, flags=re.MULTILINE
                    ),
                    encoding="utf-8",
                )

    return write


class TestSyncProjectVersion(unittest.TestCase):
    """RO-9 tranche 3: uv owns the project version; the other surfaces derive from it."""

    def _make_project(self, root: Path, version: str = "0.12.0") -> None:
        (root / "pyproject.toml").write_text(
            f'[project]\nname = "gzkit"\nversion = "{version}"\n',
            encoding="utf-8",
        )
        (root / "uv.lock").write_text(
            f'[[package]]\nname = "gzkit"\nversion = "{version}"\n', encoding="utf-8"
        )
        src = root / "src" / "gzkit"
        src.mkdir(parents=True)
        (src / "__init__.py").write_text(f'__version__ = "{version}"\n', encoding="utf-8")
        (root / "README.md").write_text(
            f"# gzkit\n[![Version](https://img.shields.io/badge/version-{version}-blue.svg)](RELEASE_NOTES.md)\n",
            encoding="utf-8",
        )

    def test_uv_writes_the_project_version_and_the_rest_follow(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.12.0")
            calls: list[tuple[Path, str]] = []
            updated = sync_project_version(
                root, "0.18.0", set_project_version=_fake_uv_version(calls)
            )
            self.assertEqual(calls, [(root, "0.18.0")])
            self.assertEqual(
                sorted(updated),
                ["README.md", "pyproject.toml", "src/gzkit/__init__.py", "uv.lock"],
            )
            self.assertIn('"0.18.0"', (root / "uv.lock").read_text(encoding="utf-8"))
            self.assertIn(
                '"0.18.0"', (root / "src" / "gzkit" / "__init__.py").read_text(encoding="utf-8")
            )
            self.assertIn("version-0.18.0", (root / "README.md").read_text(encoding="utf-8"))

    def test_no_op_when_already_current(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self._make_project(root, "0.18.0")
            calls: list[tuple[Path, str]] = []
            updated = sync_project_version(
                root, "0.18.0", set_project_version=_fake_uv_version(calls)
            )
            self.assertEqual((updated, calls), ([], []))

    def test_missing_files_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "pyproject.toml").write_text(
                '[project]\nname = "gzkit"\nversion = "0.12.0"\n',
                encoding="utf-8",
            )
            updated = sync_project_version(root, "0.18.0", set_project_version=_fake_uv_version([]))
            self.assertEqual(updated, ["pyproject.toml"])

    def test_the_default_writer_is_uv_version_without_a_sync(self) -> None:
        from gzkit.commands import version_sync

        with mock.patch.object(version_sync, "run_exec", return_value=(0, "", "")) as run:
            version_sync.uv_set_project_version(Path("/proj"), "0.18.0")
        run.assert_called_once_with(["uv", "version", "0.18.0", "--no-sync"], cwd=Path("/proj"))

    def test_a_failed_uv_version_refuses_with_its_recovery(self) -> None:
        from gzkit.commands import version_sync
        from gzkit.commands.common import GzCliError

        with (
            mock.patch.object(version_sync, "run_exec", return_value=(2, "", "no network")),
            self.assertRaises(GzCliError) as ctx,
        ):
            version_sync.uv_set_project_version(Path("/proj"), "0.18.0")
        message = str(ctx.exception)
        self.assertIn("no network", message)
        self.assertIn("uv version 0.18.0 --no-sync", message)


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


class TestWriteInFlightReleaseManifest(unittest.TestCase):
    """GHI #739 — the bump and its in-flight evidence are one operation.

    ``gz patch release`` wrote a manifest at bump time; ``gz closeout``
    bumped the identical field and wrote nothing, so the ceremony's own
    mandated Step-10 sync ran a test gate that the bump had just turned red.
    Every bump-performing command now files the evidence its bump requires.
    """

    def _bumped_root(self, tmp: str, version: str) -> Path:
        root = Path(tmp)
        (root / "pyproject.toml").write_text(
            f'[project]\nname = "gzkit"\nversion = "{version}"\n', encoding="utf-8"
        )
        return root

    def test_manifest_satisfies_the_audit_that_governs_the_bump(self) -> None:
        """The written manifest is accepted by ``audit_version_release`` — the whole point."""
        from gzkit.commands.version_sync import write_in_flight_release_manifest
        from gzkit.governance.trust_audits.release import audit_version_release

        with tempfile.TemporaryDirectory() as tmp:
            root = self._bumped_root(tmp, "9.9.0")
            write_in_flight_release_manifest(root, "9.9.0", "ADR-9.9.0-demo")
            self.assertEqual(
                audit_version_release(root),
                [],
                msg="a bump plus its manifest must leave the audit green",
            )

    def test_returns_repo_relative_posix_path(self) -> None:
        """Path is returned relative and posix-rendered (cross-platform rule)."""
        from gzkit.commands.version_sync import write_in_flight_release_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = self._bumped_root(tmp, "9.9.0")
            rel = write_in_flight_release_manifest(root, "9.9.0", "ADR-9.9.0-demo")
            self.assertEqual(rel, "docs/releases/RELEASE-v9.9.0.md")

    def test_manifest_names_its_driving_adr_and_version(self) -> None:
        """The artifact traces the bump to the closeout that caused it."""
        from gzkit.commands.version_sync import write_in_flight_release_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = self._bumped_root(tmp, "9.9.0")
            write_in_flight_release_manifest(root, "9.9.0", "ADR-9.9.0-demo")
            body = (root / "docs" / "releases" / "RELEASE-v9.9.0.md").read_text(encoding="utf-8")
            self.assertIn("ADR-9.9.0-demo", body)
            self.assertIn("9.9.0", body)

    def test_creates_releases_directory_when_absent(self) -> None:
        """A fresh clone has no docs/releases/; the writer provisions it."""
        from gzkit.commands.version_sync import write_in_flight_release_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = self._bumped_root(tmp, "9.9.0")
            self.assertFalse((root / "docs" / "releases").exists())
            write_in_flight_release_manifest(root, "9.9.0", "ADR-9.9.0-demo")
            self.assertTrue((root / "docs" / "releases" / "RELEASE-v9.9.0.md").is_file())

    def test_does_not_clobber_an_existing_manifest(self) -> None:
        """A hand-authored or ceremony-authored manifest for the same version wins."""
        from gzkit.commands.version_sync import write_in_flight_release_manifest

        with tempfile.TemporaryDirectory() as tmp:
            root = self._bumped_root(tmp, "9.9.0")
            releases = root / "docs" / "releases"
            releases.mkdir(parents=True)
            existing = releases / "RELEASE-v9.9.0.md"
            existing.write_text("# hand-authored\n", encoding="utf-8")
            write_in_flight_release_manifest(root, "9.9.0", "ADR-9.9.0-demo")
            self.assertEqual(existing.read_text(encoding="utf-8"), "# hand-authored\n")


if __name__ == "__main__":
    unittest.main()
