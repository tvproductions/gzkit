import unittest
from pathlib import Path

from gzkit.cli import GzCliError, resolve_adr_file
from gzkit.config import GzkitConfig
from tests.commands.common import CliRunner, _quick_init


class TestAdrResolution(unittest.TestCase):
    """Tests for ADR file resolution."""

    def test_resolve_adr_file_matches_suffixed_filename(self) -> None:
        """Resolves nested ADR files by stem when header uses short SemVer ID."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs) / "pool"
            adr_dir.mkdir(parents=True, exist_ok=True)
            adr_path = adr_dir / "ADR-0.6.0-pool.gz-chores-system.md"
            adr_path.write_text("# ADR-0.6.0: pool.gz-chores-system\n")

            resolved_path, resolved_id = resolve_adr_file(
                Path.cwd(), config, "ADR-0.6.0-pool.gz-chores-system"
            )

            self.assertEqual(resolved_path.resolve(), adr_path.resolve())
            self.assertEqual(resolved_id, "ADR-0.6.0-pool.gz-chores-system")

    def test_resolve_adr_file_matches_unique_semver_prefix(self) -> None:
        """Resolves ADR-<semver> input to a unique suffixed ADR id."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_path = Path(config.paths.adrs) / "ADR-0.5.0-skill-lifecycle-governance.md"
            adr_path.parent.mkdir(parents=True, exist_ok=True)
            adr_path.write_text(
                "---\n"
                "id: ADR-0.5.0-skill-lifecycle-governance\n"
                "---\n\n"
                "# ADR-0.5.0: skill-lifecycle-governance\n"
            )

            resolved_path, resolved_id = resolve_adr_file(Path.cwd(), config, "ADR-0.5.0")

            self.assertEqual(resolved_path.resolve(), adr_path.resolve())
            self.assertEqual(resolved_id, "ADR-0.5.0-skill-lifecycle-governance")

    def test_resolve_adr_file_rejects_ambiguous_semver_prefix(self) -> None:
        """Raises when ADR-<semver> matches multiple suffixed ADR IDs."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_dir = Path(config.paths.adrs)
            adr_dir.mkdir(parents=True, exist_ok=True)
            (adr_dir / "ADR-0.5.0-alpha.md").write_text("# ADR-0.5.0: alpha\n")
            (adr_dir / "ADR-0.5.0-beta.md").write_text("# ADR-0.5.0: beta\n")

            with self.assertRaisesRegex(GzCliError, r"Multiple ADR files found for ADR-0\.5\.0"):
                resolve_adr_file(Path.cwd(), config, "ADR-0.5.0")

    def test_resolve_adr_file_keeps_legacy_semver_metadata_id(self) -> None:
        """Resolves ADR-<semver> to metadata ID when legacy files use suffixed paths."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))

            adr_path = Path(config.paths.adrs) / "ADR-0.2.0-gate-verification.md"
            adr_path.parent.mkdir(parents=True, exist_ok=True)
            adr_path.write_text("---\nid: ADR-0.2.0\n---\n\n# ADR-0.2.0: Gate Verification\n")

            resolved_path, resolved_id = resolve_adr_file(Path.cwd(), config, "ADR-0.2.0")

            self.assertEqual(resolved_path.resolve(), adr_path.resolve())
            self.assertEqual(resolved_id, "ADR-0.2.0")
