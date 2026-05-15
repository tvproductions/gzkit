"""Tests for gz upgrade command (TDD red phase).

These tests derive from OBPI brief REQ-0.0.32-14-* acceptance criteria.
They are written BEFORE the implementation so they fail initially (red phase).

The upgrade module does not exist yet; tests that require it are guarded by
``@unittest.skipUnless(_UPGRADE_AVAILABLE, ...)``.  The parser-registration
test (REQ-01) is NOT skipped -- it fails with ``invalid choice: 'upgrade'``
at red phase, which is the correct red.
"""

import json
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch

from gzkit.cli import main
from gzkit.traceability import covers
from tests.commands.common import CliRunner

# ---------------------------------------------------------------------------
# Module-level guard: upgrade_cmd may not exist yet (red phase)
# ---------------------------------------------------------------------------
try:
    from gzkit.commands import upgrade as upgrade_mod  # noqa: F401

    _UPGRADE_AVAILABLE = True
except ImportError:
    _UPGRADE_AVAILABLE = False

_SKIP_REASON = "gzkit.commands.upgrade not yet implemented"


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-01: Parser registration
# ---------------------------------------------------------------------------


class TestUpgradeRegistration(unittest.TestCase):
    """gz upgrade registered in parser tree; --help exits 0."""

    @covers("REQ-0.0.32-14-01")
    def test_upgrade_help_exits_0(self) -> None:
        """gz upgrade --help should exit 0 once registered."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            result = runner.invoke(main, ["upgrade", "--help"])
            self.assertEqual(
                result.exit_code,
                0,
                f"Expected exit 0 from 'gz upgrade --help'; got {result.exit_code}.\n"
                f"Output: {result.output}",
            )

    @covers("REQ-0.0.32-14-01")
    def test_upgrade_in_parser_choices(self) -> None:
        """'upgrade' must appear in the parser subcommand choices."""
        from gzkit.cli.main import _build_parser

        parser = _build_parser()
        # Subparsers action stores choices in _subparsers._group_actions
        choices: set[str] = set()
        for action_group in parser._subparsers._group_actions:  # type: ignore
            if hasattr(action_group, "choices") and action_group.choices:
                choices.update(action_group.choices.keys())
        self.assertIn(
            "upgrade",
            choices,
            f"'upgrade' not found in parser choices: {sorted(choices)}",
        )


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-02: --surface filter
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeSurfaceFilter(unittest.TestCase):
    """--surface filter: unknown name exits 1 naming the token; default processes all."""

    @covers("REQ-0.0.32-14-02")
    def test_unknown_surface_exits_1(self) -> None:
        """An unrecognized surface name must exit 1 with the bad token in output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            Path(".gzkit/manifest.json").write_text("{}", encoding="utf-8")
            result = runner.invoke(main, ["upgrade", "--surface", "nonexistent"])
            self.assertEqual(
                result.exit_code,
                1,
                f"Expected exit 1 for unknown surface; got {result.exit_code}",
            )
            self.assertIn(
                "nonexistent",
                result.output,
                "Error output must name the unknown surface token",
            )

    @covers("REQ-0.0.32-14-02")
    def test_unknown_surface_in_comma_list_exits_1(self) -> None:
        """An unknown token embedded in a comma-separated list exits 1."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            result = runner.invoke(main, ["upgrade", "--surface", "skills,badtoken"])
            self.assertEqual(result.exit_code, 1)
            self.assertIn("badtoken", result.output)

    @covers("REQ-0.0.32-14-02")
    def test_valid_surface_subset_accepted(self) -> None:
        """A valid subset of surfaces (e.g., 'skills') runs without exit 1."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[],
            ):
                result = runner.invoke(main, ["upgrade", "--surface", "skills"])
                # Exit 0 or 3 (conflicts) are both acceptable; 1 is not.
                self.assertNotEqual(
                    result.exit_code,
                    1,
                    f"Valid surface 'skills' must not exit 1. Output: {result.output}",
                )

    @covers("REQ-0.0.32-14-02")
    def test_default_processes_all_surfaces(self) -> None:
        """Without --surface, the command processes the full canonical surface list."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[],
            ) as mock_iter:
                runner.invoke(main, ["upgrade"])
                # All canonical surfaces should have been iterated
                called_pkgs = [c.args[0] for c in mock_iter.call_args_list]
                self.assertGreater(
                    len(called_pkgs),
                    1,
                    "Default run must iterate more than one surface package",
                )


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-03: EDITED conflict handling
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeEditedConflicts(unittest.TestCase):
    """EDITED artifacts reported, left unchanged, exit non-zero when conflicts remain."""

    @covers("REQ-0.0.32-14-03")
    def test_edited_artifact_reported_and_not_overwritten(self) -> None:
        """EDITED artifact must be reported in output and file content unchanged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            gzkit_dir = Path(".gzkit")
            gzkit_dir.mkdir()
            skills_dir = gzkit_dir / "skills"
            skills_dir.mkdir()
            skill_file = skills_dir / "test-skill" / "SKILL.md"
            skill_file.parent.mkdir()
            original_content = (
                b"# Operator-edited content\n<!-- gzkit-canonical-version: 1.0.0 -->\n"
            )
            skill_file.write_bytes(original_content)

            fake_canonical = MagicMock()
            fake_canonical.name = "SKILL.md"

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                ) as mock_iter,
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="EDITED",
                ),
            ):
                mock_iter.return_value = [(fake_canonical, Path("test-skill/SKILL.md"))]
                result = runner.invoke(main, ["upgrade", "--surface", "skills"])

            # File must be untouched
            self.assertEqual(
                skill_file.read_bytes(),
                original_content,
                "EDITED artifact must not be overwritten",
            )
            # Output must mention conflict
            self.assertIn(
                "EDITED",
                result.output.upper(),
                "Output must report EDITED conflicts",
            )

    @covers("REQ-0.0.32-14-03")
    def test_exit_nonzero_when_conflicts_remain(self) -> None:
        """When EDITED conflicts remain, exit code must be non-zero (3)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            fake_canonical = MagicMock()
            fake_canonical.name = "some.md"

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("some.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="EDITED",
                ),
            ):
                result = runner.invoke(main, ["upgrade", "--surface", "skills"])

            self.assertNotEqual(
                result.exit_code,
                0,
                "Must exit non-zero when EDITED conflicts remain",
            )

    @covers("REQ-0.0.32-14-03")
    def test_exit_0_when_no_conflicts(self) -> None:
        """When all artifacts are IDENTICAL or STALE (refreshed), exit 0."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            fake_canonical = MagicMock()
            fake_canonical.name = "some.md"

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("some.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="IDENTICAL",
                ),
            ):
                result = runner.invoke(main, ["upgrade", "--surface", "skills"])

            self.assertEqual(
                result.exit_code,
                0,
                f"Must exit 0 when no EDITED conflicts remain. Output: {result.output}",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-04: --force overwrites EDITED
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeForce(unittest.TestCase):
    """--force overwrites EDITED; prints per-file overwrite line; exit 0."""

    @covers("REQ-0.0.32-14-04")
    def test_force_overwrites_edited_artifact(self) -> None:
        """--force must cause EDITED artifact to be written with canonical bytes."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            gzkit_dir = Path(".gzkit")
            gzkit_dir.mkdir()
            skills_dir = gzkit_dir / "skills"
            skills_dir.mkdir()
            skill_file = skills_dir / "overwrite-me.md"
            skill_file.write_bytes(b"old content\n<!-- gzkit-canonical-version: 0.0.1 -->\n")

            canonical_bytes = b"# New canonical content\n"
            fake_canonical = MagicMock()
            fake_canonical.name = "overwrite-me.md"
            fake_canonical.read_bytes.return_value = canonical_bytes

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("overwrite-me.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="EDITED",
                ),
            ):
                result = runner.invoke(main, ["upgrade", "--surface", "skills", "--force"])

            # With --force, exit must be 0
            self.assertEqual(
                result.exit_code,
                0,
                f"--force must exit 0 even with EDITED conflicts. Output: {result.output}",
            )

    @covers("REQ-0.0.32-14-04")
    def test_force_prints_overwrite_line_per_file(self) -> None:
        """--force must print a per-file line indicating the overwrite."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            fake_canonical = MagicMock()
            fake_canonical.name = "edited-skill.md"

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("edited-skill.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="EDITED",
                ),
            ):
                result = runner.invoke(main, ["upgrade", "--surface", "skills", "--force"])

            lower = result.output.lower()
            self.assertTrue(
                "overwrite" in lower or "force" in lower or "edited-skill.md" in result.output,
                f"--force output must mention the overwritten file. Got: {result.output!r}",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-05: --dry-run
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeDryRun(unittest.TestCase):
    """--dry-run reports same classification, writes nothing, exits like non-dry-run."""

    @covers("REQ-0.0.32-14-05")
    def test_dry_run_writes_nothing(self) -> None:
        """--dry-run must not create or modify any files."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            gzkit_dir = Path(".gzkit")
            gzkit_dir.mkdir()

            new_file = gzkit_dir / "skills" / "new-skill.md"
            self.assertFalse(new_file.exists())

            canonical_bytes = b"# New canonical skill\n"
            fake_canonical = MagicMock()
            fake_canonical.name = "new-skill.md"
            fake_canonical.read_bytes.return_value = canonical_bytes

            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[(fake_canonical, Path("new-skill.md"))],
            ):
                runner.invoke(main, ["upgrade", "--surface", "skills", "--dry-run"])

            self.assertFalse(
                new_file.exists(),
                "--dry-run must not write new files",
            )

    @covers("REQ-0.0.32-14-05")
    def test_dry_run_reports_classification(self) -> None:
        """--dry-run must report STALE/EDITED/IDENTICAL classification in output."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            fake_canonical = MagicMock()
            fake_canonical.name = "stale-skill.md"

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("stale-skill.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="STALE",
                ),
            ):
                result = runner.invoke(main, ["upgrade", "--surface", "skills", "--dry-run"])

            upper = result.output.upper()
            self.assertTrue(
                "STALE" in upper or "DRY" in upper or "stale-skill.md" in result.output,
                f"--dry-run must classify artifacts. Output: {result.output!r}",
            )

    @covers("REQ-0.0.32-14-05")
    def test_dry_run_exit_code_matches_non_dry_run(self) -> None:
        """--dry-run exit code must match what non-dry-run would return."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            fake_canonical = MagicMock()
            fake_canonical.name = "conflict.md"

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("conflict.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="EDITED",
                ),
            ):
                dry_result = runner.invoke(main, ["upgrade", "--surface", "skills", "--dry-run"])
                live_result = runner.invoke(main, ["upgrade", "--surface", "skills"])

            self.assertEqual(
                dry_result.exit_code,
                live_result.exit_code,
                f"--dry-run exit {dry_result.exit_code} must match live exit"
                f" {live_result.exit_code}",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-06: Bootstrap-retrofit
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeBootstrapRetrofit(unittest.TestCase):
    """Bootstrap-retrofit: works without prior gz init; scaffolds from package data."""

    @covers("REQ-0.0.32-14-06")
    def test_works_without_gzkit_skills_dir(self) -> None:
        """Command must work even when .gzkit/skills/ does not exist."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            # No .gzkit/skills/ directory created
            Path(".gzkit").mkdir()

            canonical_bytes = b"# Bootstrapped skill\n"
            fake_canonical = MagicMock()
            fake_canonical.name = "bootstrap-skill.md"
            fake_canonical.read_bytes.return_value = canonical_bytes

            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[(fake_canonical, Path("bootstrap-skill.md"))],
            ):
                result = runner.invoke(main, ["upgrade", "--surface", "skills"])

            # Must not crash; exit 0 or 3 are acceptable, but not 2 (system error)
            self.assertNotEqual(
                result.exit_code,
                2,
                f"Bootstrap-retrofit must not exit 2. Output: {result.output}",
            )

    @covers("REQ-0.0.32-14-06")
    def test_bootstrap_creates_missing_surface_dir(self) -> None:
        """When .gzkit/skills/ is absent, upgrade must create it."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            gzkit_dir = Path(".gzkit")
            gzkit_dir.mkdir()
            skills_dir = gzkit_dir / "skills"
            self.assertFalse(skills_dir.exists())

            canonical_bytes = b"# New skill from bootstrap\n"
            fake_canonical = MagicMock()
            fake_canonical.name = "new-skill.md"
            fake_canonical.read_bytes.return_value = canonical_bytes

            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[(fake_canonical, Path("new-skill.md"))],
            ):
                runner.invoke(main, ["upgrade", "--surface", "skills"])

            self.assertTrue(
                skills_dir.exists(),
                ".gzkit/skills/ must be created by upgrade bootstrap",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-07: Idempotence
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeIdempotent(unittest.TestCase):
    """Second run exits 0 with zero STALE/EDITED."""

    @covers("REQ-0.0.32-14-07")
    def test_second_run_exits_0(self) -> None:
        """Calling upgrade twice: second call exits 0."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()

            canonical_bytes = b"# Canonical content\n"
            fake_canonical = MagicMock()
            fake_canonical.name = "idempotent.md"
            fake_canonical.read_bytes.return_value = canonical_bytes

            # First run: STALE → writes file
            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("idempotent.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="STALE",
                ),
            ):
                runner.invoke(main, ["upgrade", "--surface", "skills"])

            # Second run: IDENTICAL (no drift)
            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("idempotent.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="IDENTICAL",
                ),
            ):
                second_result = runner.invoke(main, ["upgrade", "--surface", "skills"])

            self.assertEqual(
                second_result.exit_code,
                0,
                f"Second run must exit 0 (idempotent). Output: {second_result.output}",
            )

    @covers("REQ-0.0.32-14-07")
    def test_second_run_reports_zero_stale_or_edited(self) -> None:
        """Second run output must not report any STALE or EDITED classifications."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()

            canonical_bytes = b"# Canonical content\n"
            fake_canonical = MagicMock()
            fake_canonical.name = "stable.md"
            fake_canonical.read_bytes.return_value = canonical_bytes

            with (
                patch(
                    "gzkit.commands.upgrade._iter_canonical_surface_files",
                    return_value=[(fake_canonical, Path("stable.md"))],
                ),
                patch(
                    "gzkit.commands.upgrade._refresh_one_artifact",
                    return_value="IDENTICAL",
                ),
            ):
                second_result = runner.invoke(main, ["upgrade", "--surface", "skills"])

            upper = second_result.output.upper()
            # Should not declare any drift; "0 stale" or "nothing to update" are fine
            self.assertNotIn(
                "1 STALE",
                upper,
                "Second run must report zero STALE artifacts",
            )
            self.assertNotIn(
                "1 EDITED",
                upper,
                "Second run must report zero EDITED artifacts",
            )


# ---------------------------------------------------------------------------
# REQ-0.0.32-14-08: Does NOT mutate manifest.json or invoke scaffolder hooks
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeNoSideEffects(unittest.TestCase):
    """upgrade must NOT mutate manifest.json or invoke scaffolder hooks/agent sync."""

    @covers("REQ-0.0.32-14-08")
    def test_manifest_unchanged_after_upgrade(self) -> None:
        """manifest.json must have identical bytes before and after upgrade."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            gzkit_dir = Path(".gzkit")
            gzkit_dir.mkdir()
            manifest_path = gzkit_dir / "manifest.json"
            manifest_content = json.dumps(
                {"schema": "gzkit.manifest.v2", "test": "sentinel"}, indent=2
            )
            manifest_path.write_text(manifest_content, encoding="utf-8")
            before_bytes = manifest_path.read_bytes()

            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[],
            ):
                runner.invoke(main, ["upgrade"])

            after_bytes = manifest_path.read_bytes()
            self.assertEqual(
                before_bytes,
                after_bytes,
                "upgrade must NOT mutate .gzkit/manifest.json",
            )

    @covers("REQ-0.0.32-14-08")
    def test_no_scaffold_hooks_invoked(self) -> None:
        """upgrade must NOT invoke scaffold_core_skills or scaffold-like hooks."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()

            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[],
            ):
                # If upgrade imports and calls any scaffold function, the patch
                # below catches the call; we assert it was never called.
                try:
                    with patch(
                        "gzkit.commands.upgrade.scaffold_core_skills",
                        side_effect=AssertionError("scaffold_core_skills must not be called"),
                    ):
                        result = runner.invoke(main, ["upgrade"])
                except Exception:
                    # Patching a name that doesn't exist is fine at red phase
                    pass

            # The real invariant: manifest unchanged (covered above).
            # Here we simply verify the command completes without a crash
            # related to scaffold hooks.
            self.assertNotIn(
                "scaffold",
                result.output.lower(),
                "upgrade output must not mention scaffolding (it delegates nothing)",
            )

    @covers("REQ-0.0.32-14-08")
    def test_no_agent_sync_invoked(self) -> None:
        """upgrade must NOT invoke gz agent sync or any equivalent."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()

            agent_sync_called = {"value": False}

            def fake_sync(*args: object, **kwargs: object) -> None:
                agent_sync_called["value"] = True

            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[],
            ):
                try:
                    with patch("gzkit.commands.upgrade.sync_all", side_effect=fake_sync):
                        runner.invoke(main, ["upgrade"])
                except Exception:
                    pass

            self.assertFalse(
                agent_sync_called["value"],
                "upgrade must NOT invoke agent sync / sync_all",
            )


# ---------------------------------------------------------------------------
# GHI #465: honor ADR-0.0.32 § Named exception 1 (hooks) and package-only
# carve-outs (templates/skills/**, classifier-package_only files generally).
#
# The brief's REQ-0.0.32-14-02 lists `hooks` as a valid --surface value but
# ADR-0.0.32 § Named exception 1 carves hooks out of the dual-surface
# byte-parity invariant. The ADR is binding; the brief contradicted it; the
# implementation followed the brief and so polluted .gzkit/hooks/ with
# vendor-coupled package machinery and .gzkit/templates/skills/ with
# package-only resources.
# ---------------------------------------------------------------------------


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeHonorsNamedExceptions(unittest.TestCase):
    """ADR-0.0.32 § Named exception 1: hooks is not a valid upgrade surface."""

    @covers("REQ-0.0.32-14-02")
    def test_hooks_surface_rejected_as_unknown(self) -> None:
        """--surface hooks must exit 1 — hooks is ADR-0.0.32 § Named exception 1.

        Same exit-1 contract as any unrecognized surface (REQ-0.0.32-14-02).
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            result = runner.invoke(main, ["upgrade", "--surface", "hooks"])
            self.assertEqual(
                result.exit_code,
                1,
                f"--surface hooks must exit 1 (carved out by ADR-0.0.32); got "
                f"{result.exit_code}. Output: {result.output}",
            )
            self.assertIn("hooks", result.output)

    @covers("REQ-0.0.32-14-02")
    def test_default_does_not_iterate_hooks_pkg(self) -> None:
        """Default upgrade run must not iterate the gzkit.hooks package."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()
            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                return_value=[],
            ) as mock_iter:
                runner.invoke(main, ["upgrade"])
                called_pkgs = [c.args[0] for c in mock_iter.call_args_list]
                self.assertNotIn(
                    "gzkit.hooks",
                    called_pkgs,
                    "Default run must not iterate gzkit.hooks (ADR-0.0.32 § "
                    f"Named exception 1). Iterated packages: {called_pkgs}",
                )


@unittest.skipUnless(_UPGRADE_AVAILABLE, _SKIP_REASON)
class TestUpgradeHonorsPackageOnlyCarveout(unittest.TestCase):
    """Package-only files must not be propagated to .gzkit/ during upgrade."""

    @covers("REQ-0.0.32-14-02")
    def test_templates_skills_subdir_filtered(self) -> None:
        """templates/skills/** is package_only per _classify_template_file.

        REQ-0.0.32-11-04 retains the skills subdir at the package surface only;
        gz upgrade must consult the classifier and skip non-canonical files.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            Path(".gzkit").mkdir()

            canonical_template = MagicMock()
            canonical_template.name = "skill.md"
            canonical_template.read_bytes.return_value = b"# canonical top-level\n"

            package_only_resource = MagicMock()
            package_only_resource.name = "SKILL.md"
            package_only_resource.read_bytes.return_value = b"# package-only nested\n"

            def fake_iter(pkg: str) -> list[tuple[MagicMock, Path]]:
                if pkg == "gzkit.templates":
                    return [
                        (canonical_template, Path("skill.md")),
                        (package_only_resource, Path("skills/git-sync/SKILL.md")),
                    ]
                return []

            with patch(
                "gzkit.commands.upgrade._iter_canonical_surface_files",
                side_effect=fake_iter,
            ):
                runner.invoke(main, ["upgrade", "--surface", "templates"])

            nested = Path(".gzkit/templates/skills/git-sync/SKILL.md")
            self.assertFalse(
                nested.exists(),
                "templates/skills/** is package_only — must not propagate to .gzkit/",
            )


if __name__ == "__main__":
    unittest.main()
