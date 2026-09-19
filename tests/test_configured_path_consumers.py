"""Configured source and manifest identities survive their shared consumers."""

import io
import json
import tempfile
import unittest
from contextlib import ExitStack, redirect_stdout
from pathlib import Path
from unittest.mock import patch

from gzkit.commands.common import GzCliError, load_manifest
from gzkit.commands.config_paths import _collect_source_path_literal_issues, check_config_paths_cmd
from gzkit.commands.init_cmd import _repair_missing_artifacts
from gzkit.config import GzkitConfig, PathConfig
from gzkit.doc_coverage.flag_scanner import scan_command_flags
from gzkit.doc_coverage.scanner import scan_cli_commands
from gzkit.sync_surfaces import generate_manifest, sync_all, write_manifest


class TestManifestStructureConfiguration(unittest.TestCase):
    """Explicit roots outrank discovery without removing unconfigured discovery."""

    def test_explicit_roots_replace_decoy_default_structure(self) -> None:
        """Configured identities survive even when conventional directories exist."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            for name in ("src", "tests", "docs", "design"):
                (root / name).mkdir()
            configured = {
                "source_root": "lib",
                "tests_root": "specs",
                "docs_root": "manual",
                "design_root": "architecture",
            }
            (root / ".gzkit.json").write_text(json.dumps({"paths": configured}), encoding="utf-8")
            config = GzkitConfig.load(root / ".gzkit.json")
            self.assertEqual(generate_manifest(root, config)["structure"], configured)

    def test_partial_configuration_retains_discovery_and_explicit_override(self) -> None:
        """Unconfigured roots are discovered; a supplied structure wins last."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "test").mkdir()
            (root / "documentation").mkdir()
            config = GzkitConfig(paths=PathConfig(source_root="lib"))
            self.assertEqual(
                generate_manifest(root, config)["structure"],
                {
                    "source_root": "lib",
                    "tests_root": "test",
                    "docs_root": "documentation",
                    "design_root": "design",
                },
            )
            self.assertEqual(
                generate_manifest(root, config, {"source_root": "override"})["structure"],
                {
                    "source_root": "override",
                    "tests_root": "tests",
                    "docs_root": "docs",
                    "design_root": "design",
                },
            )


class TestManifestLocationConfiguration(unittest.TestCase):
    """The shared manifest producer and reader agree on configured identity."""

    def test_init_repair_publishes_configured_structure_before_sync(self) -> None:
        """Repair's own publication honors configured roots without later correction."""
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as patches:
            root = Path(tmp)
            config = GzkitConfig(paths=PathConfig(source_root="lib", manifest="state.json"))
            (root / "src").mkdir()
            for name in (
                "_scaffold_gitignore",
                "_session_green_gate_statuses",
                "scaffold_core_skills",
                "_repair_rules",
                "_repair_personas",
                "_repair_templates",
                "_repair_chores",
                "sync_all",
            ):
                patches.enter_context(patch(f"gzkit.commands.init_cmd.{name}", return_value=[]))
            _repair_missing_artifacts(root, config, no_skeleton=True)
            manifest = json.loads((root / "state.json").read_text(encoding="utf-8"))
            self.assertEqual(manifest["structure"]["source_root"], "lib")

    def test_write_and_read_use_configured_location_despite_decoy(self) -> None:
        """The default manifest neither receives nor supplies configured data."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            GzkitConfig(paths=PathConfig(manifest=".governance/state.json")).save(
                root / ".gzkit.json"
            )
            decoy = root / ".gzkit" / "manifest.json"
            decoy.parent.mkdir()
            decoy.write_text('{"origin": "decoy"}', encoding="utf-8")
            payload = {"origin": "configured"}
            write_manifest(root, payload)
            actual = root / ".governance" / "state.json"
            self.assertTrue(actual.is_file(), "writer ignored configured manifest identity")
            self.assertEqual(json.loads(actual.read_text(encoding="utf-8")), payload)
            self.assertEqual(load_manifest(root), payload)
            self.assertEqual(json.loads(decoy.read_text(encoding="utf-8")), {"origin": "decoy"})

    def test_missing_configured_manifest_does_not_fall_back(self) -> None:
        """Missing configured input fails even if a default manifest is present."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            GzkitConfig(paths=PathConfig(manifest=".governance/missing.json")).save(
                root / ".gzkit.json"
            )
            decoy = root / ".gzkit" / "manifest.json"
            decoy.parent.mkdir()
            decoy.write_text("{}", encoding="utf-8")
            # output-contract: recovery must identify the missing configured resource.
            with self.assertRaisesRegex(GzCliError, r"\.governance/missing\.json"):
                load_manifest(root)

    def test_default_location_without_config_round_trips(self) -> None:
        """Legacy projects still read the manifest the default writer produces."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            write_manifest(root, {"origin": "default"})
            self.assertEqual(load_manifest(root), {"origin": "default"})

    def test_sync_preserves_rules_and_reports_effective_manifest_path(self) -> None:
        """Sync consumes, writes and reports one manifest even with in-memory config."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(paths=PathConfig(manifest=".governance/state.json"))
            selected = root / config.paths.manifest
            selected.parent.mkdir()
            authored = {"unscoped_allowlist": ["preserved-rule"]}
            selected.write_text(json.dumps({"rules": authored}), encoding="utf-8")
            decoy = root / ".gzkit" / "manifest.json"
            decoy.parent.mkdir()
            decoy.write_text('{"rules": {"unscoped_allowlist": ["decoy"]}}', encoding="utf-8")
            updated = sync_all(root, config, emit_event=False)
            self.assertEqual(json.loads(selected.read_text(encoding="utf-8"))["rules"], authored)
            self.assertIn(".governance/state.json", updated)
            self.assertNotIn(".gzkit/manifest.json", updated)


class TestSourceScanFailures(unittest.TestCase):
    """An encountered source failure cannot turn into clean audit evidence."""

    def test_failed_members_report_issues_without_hiding_valid_neighbors(self) -> None:
        """Syntax, decoding and filesystem failures remain visible in one scan."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            config = GzkitConfig(paths=PathConfig(source_root="lib"))
            package = root / "lib" / "gzkit"
            package.mkdir(parents=True)
            (package / "syntax.py").write_text("BROKEN = (", encoding="utf-8")
            (package / "decode.py").write_bytes(b"\xff")
            unreadable = package / "unreadable.py"
            unreadable.touch()
            (package / "good.py").write_text(
                'OUTPUT = "artifacts/unmapped/report"', encoding="utf-8"
            )
            original_read = Path.read_text

            def read_source(path: Path, *args: object, **kwargs: object) -> str:
                if path == unreadable:
                    raise PermissionError("source read denied")
                return original_read(path, *args, **kwargs)

            with patch.object(Path, "read_text", read_source):
                issues = _collect_source_path_literal_issues(root, {}, config)
            self.assertEqual(
                {row["path"] for row in issues},
                {f"lib/gzkit/{name}.py" for name in ("syntax", "decode", "unreadable", "good")},
            )
            self.assertEqual(len(issues), 4)

    def test_cli_marks_unparseable_source_invalid_and_exits_nonzero(self) -> None:
        """The real source collector's failure reaches JSON output and exit status."""
        with tempfile.TemporaryDirectory() as tmp, ExitStack() as patches:
            root = Path(tmp)
            source = root / "src" / "gzkit" / "broken.py"
            source.parent.mkdir(parents=True)
            source.write_text("BROKEN = (", encoding="utf-8")
            prefix = "gzkit.commands.config_paths"
            patches.enter_context(patch(f"{prefix}.ensure_initialized", return_value=GzkitConfig()))
            patches.enter_context(patch(f"{prefix}.get_project_root", return_value=root))
            patches.enter_context(patch(f"{prefix}.load_manifest", return_value={}))
            for name in (
                "_collect_required_path_issues",
                "_collect_manifest_artifact_issues",
                "_collect_control_surface_issues",
                "_collect_obpi_path_contract_issues",
            ):
                patches.enter_context(patch(f"{prefix}.{name}", return_value=[]))
            output = io.StringIO()
            with redirect_stdout(output), self.assertRaises(SystemExit) as stopped:
                check_config_paths_cmd(as_json=True)
            self.assertEqual(stopped.exception.code, 1)
            report = json.loads(output.getvalue())
            self.assertFalse(report["valid"])
            self.assertEqual([issue["path"] for issue in report["issues"]], ["src/gzkit/broken.py"])


class TestConfiguredCliSourcePopulation(unittest.TestCase):
    """Command and flag discovery share the configured framework source tree."""

    @staticmethod
    def _write_sources(root: Path, source_root: str, command: str) -> None:
        """Declare distinct main, split-parser and command-package leaves."""
        cli = root / source_root / "gzkit" / "cli"
        cli.mkdir(parents=True)
        (cli / "main.py").write_text(
            "def _build_parser():\n"
            "    root = StableArgumentParser()\n"
            "    commands = root.add_subparsers()\n"
            f"    leaf = commands.add_parser('{command}')\n"
            "    leaf.add_argument('--main-flag')\n"
            "    leaf.set_defaults(func=handler)\n",
            encoding="utf-8",
        )
        for path, leaf in (
            (cli / "parser_extra.py", f"{command}-parser"),
            (
                root / source_root / "gzkit" / "commands" / "extra" / "__init__.py",
                f"{command}-package",
            ),
        ):
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(
                "def register_extra_parsers(commands):\n"
                f"    leaf = commands.add_parser('{leaf}')\n"
                "    leaf.add_argument('--extra-flag')\n"
                "    leaf.set_defaults(func=handler)\n",
                encoding="utf-8",
            )

    def test_relocated_population_replaces_default_for_commands_and_flags(self) -> None:
        """Decoy default commands never substitute for relocated parser members."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            GzkitConfig(paths=PathConfig(source_root="app/lib")).save(root / ".gzkit.json")
            self._write_sources(root, "app/lib", "selected")
            expected = {
                "selected": ["--main-flag"],
                "selected-parser": ["--extra-flag"],
                "selected-package": ["--extra-flag"],
            }
            for decoy in (False, True):
                with self.subTest(decoy=decoy):
                    if decoy:
                        self._write_sources(root, "src", "stale")
                    self.assertEqual(scan_command_flags(root), expected)
                    self.assertEqual({item.name for item in scan_cli_commands(root)}, set(expected))

    def test_default_and_absent_source_behavior_remain(self) -> None:
        """Unconfigured defaults work and truly absent source retains its fallback."""
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            self.assertEqual(scan_command_flags(root), {})
            self._write_sources(root, "src", "legacy")
            self.assertEqual(
                {item.name for item in scan_cli_commands(root)},
                {"legacy", "legacy-parser", "legacy-package"},
            )
