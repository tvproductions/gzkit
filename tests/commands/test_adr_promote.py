import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import (
    Ledger,
    adr_created_event,
)
from gzkit.validate_pkg.document import validate_document
from tests.commands.common import CliRunner, _quick_init


class TestAdrPromoteCommand(unittest.TestCase):
    """Tests for pool ADR promotion protocol and tooling.

    @covers REQ-0.0.17-03-08 (prior behavior preserved under --kind)
    """

    @staticmethod
    def _seed_pool_adr(config: GzkitConfig, adr_id: str = "ADR-pool.sample-work") -> Path:
        pool_dir = Path(config.paths.adrs) / "pool"
        pool_dir.mkdir(parents=True, exist_ok=True)
        pool_file = pool_dir / f"{adr_id}.md"
        pool_file.write_text(
            "---\n"
            f"id: {adr_id}\n"
            "status: Pool\n"
            "parent: PRD-GZKIT-1.0.0\n"
            "lane: heavy\n"
            "---\n\n"
            f"# {adr_id}: Sample Work\n\n"
            "## Status\n\n"
            "Pool\n\n"
            "## Intent\n\n"
            "Turn sample pool work into executable tracked delivery.\n\n"
            "## Target Scope\n\n"
            "- Define runtime command contract\n"
            "- Persist machine-readable stage state\n"
            "- Expose structured stage outputs\n\n"
            "## Non-Goals\n\n"
            "- No external orchestrator\n"
        )
        return pool_file

    def test_adr_promote_dry_run_reports_actions(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Would append artifact_renamed", result.output)
            self.assertIn("ADR-pool.sample-work -> ADR-0.6.0-sample-work", result.output)
            self.assertIn("Would create OBPIs: 3", result.output)
            self.assertIn(
                "Would append obpi_created: OBPI-0.6.0-01-define-runtime-command-contract",
                result.output,
            )

    def test_adr_promote_writes_files_and_ledger_rename(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_file = self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Promoted pool ADR", result.output)

            target_file = (
                Path(config.paths.adrs)
                / "pre-release"
                / "ADR-0.6.0-sample-work"
                / "ADR-0.6.0-sample-work.md"
            )
            self.assertTrue(target_file.exists())
            target_content = target_file.read_text(encoding="utf-8")
            self.assertIn("promoted_from: ADR-pool.sample-work", target_content)
            self.assertIn("Turn sample pool work into executable tracked delivery.", target_content)
            self.assertIn("- [ ] OBPI-0.6.0-01: Define runtime command contract", target_content)
            self.assertNotIn("Replace this seeded intent", target_content)
            self.assertNotIn("Define scope, constraints, and acceptance criteria", target_content)

            obpi_dir = target_file.parent / "obpis"
            first_obpi = obpi_dir / "OBPI-0.6.0-01-define-runtime-command-contract.md"
            self.assertTrue(first_obpi.exists())
            first_obpi_content = first_obpi.read_text(encoding="utf-8")
            self.assertIn("## Objective", first_obpi_content)
            self.assertIn("Define runtime command contract.", first_obpi_content)
            self.assertIn("**Status:** Draft", first_obpi_content)

            updated_pool = pool_file.read_text(encoding="utf-8")
            self.assertIn("status: Superseded", updated_pool)
            self.assertIn("promoted_to: ADR-0.6.0-sample-work", updated_pool)
            self.assertIn("## Status\n\nSuperseded\n", updated_pool)

            ledger_content = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            self.assertIn('"event":"artifact_renamed"', ledger_content)
            self.assertIn('"id":"ADR-pool.sample-work"', ledger_content)
            self.assertIn('"new_id":"ADR-0.6.0-sample-work"', ledger_content)
            self.assertEqual(ledger_content.count('"event":"obpi_created"'), 3)

    def test_adr_promote_fails_without_target_scope(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "ADR-pool.missing-scope.md"
            pool_file.write_text(
                "---\n"
                "id: ADR-pool.missing-scope\n"
                "status: Pool\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: heavy\n"
                "---\n\n"
                "# ADR-pool.missing-scope: Missing Scope\n\n"
                "## Intent\n\n"
                "Missing actionable scope.\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.missing-scope", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.missing-scope",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            normalized_output = " ".join(result.output.split())
            self.assertIn("missing required section", normalized_output)
            self.assertIn("Target Scope", normalized_output)
            self.assertFalse(
                (
                    Path(config.paths.adrs)
                    / "pre-release"
                    / "ADR-0.6.0-missing-scope"
                    / "ADR-0.6.0-missing-scope.md"
                ).exists()
            )

    def test_adr_promote_rejects_non_pool_source(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "0.6.0", "--kind", "feature"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-0.6.0",
                    "--semver",
                    "0.6.1",
                    "--kind",
                    "feature",
                ],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("not a pool entry", result.output)

    def test_adr_promote_blocks_on_non_go_eval(self) -> None:
        """Promotion fails closed when generated package does not reach GO."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                ],
            )
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("Promotion blocked", result.output)
            self.assertIn("eval verdict CONDITIONAL GO", result.output)


class TestAdrPromoteKindFlag(unittest.TestCase):
    """Tests for --kind flag on gz adr promote (OBPI-0.0.17-03).

    @covers REQ-0.0.17-03-01 (--kind required; pool rejected)
    @covers REQ-0.0.17-03-02 (foundation requires 0.0.x semver)
    @covers REQ-0.0.17-03-03 (feature rejects 0.0.x semver)
    @covers REQ-0.0.17-03-04 (atomicity: rejection writes nothing)
    @covers REQ-0.0.17-03-05 (promoted frontmatter carries kind:)
    @covers REQ-0.0.17-03-06 (kind-driven directory routing)
    @covers REQ-0.0.17-03-07 (ledger event records kind + semver)
    """

    @staticmethod
    def _seed_pool_adr(config: GzkitConfig, adr_id: str = "ADR-pool.sample-work") -> Path:
        pool_dir = Path(config.paths.adrs) / "pool"
        pool_dir.mkdir(parents=True, exist_ok=True)
        pool_file = pool_dir / f"{adr_id}.md"
        pool_file.write_text(
            "---\n"
            f"id: {adr_id}\n"
            "status: Pool\n"
            "parent: PRD-GZKIT-1.0.0\n"
            "lane: heavy\n"
            "---\n\n"
            f"# {adr_id}: Sample Work\n\n"
            "## Status\n\nPool\n\n"
            "## Intent\n\n"
            "Turn sample pool work into executable tracked delivery.\n\n"
            "## Target Scope\n\n"
            "- Define runtime command contract\n"
            "- Persist machine-readable stage state\n"
            "- Expose structured stage outputs\n\n"
            "## Non-Goals\n\n"
            "- No external orchestrator\n",
            encoding="utf-8",
        )
        return pool_file

    def _seed_for_promote(self, adr_id: str = "ADR-pool.sample-work") -> GzkitConfig:
        _quick_init()
        config = GzkitConfig.load(Path(".gzkit.json"))
        self._seed_pool_adr(config, adr_id)
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(adr_created_event(adr_id, "", "heavy"))
        return config

    # --- REQ-0.0.17-03-01: --kind registered; pool rejected; missing rejected ---

    def test_help_shows_kind_choices(self) -> None:
        """@covers REQ-0.0.17-03-01 — --help shows --kind with three choices."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["adr", "promote", "--help"])
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("--kind", result.output)
            normalized = " ".join(result.output.split())
            self.assertIn("foundation", normalized)
            self.assertIn("feature", normalized)
            self.assertIn("pool", normalized)

    def test_missing_kind_exits_one_with_recovery(self) -> None:
        """@covers REQ-0.0.17-03-01 — missing --kind exits 1, names both kinds."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                ["adr", "promote", "ADR-pool.sample-work", "--semver", "0.6.0"],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("foundation", result.output)
            self.assertIn("feature", result.output)
            target = Path("design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md")
            self.assertFalse(target.exists(), "no promotion artifact may exist on rejection")

    def test_kind_pool_rejected_with_exit_one(self) -> None:
        """@covers REQ-0.0.17-03-01 — --kind pool exits 1; pool is the source kind."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "pool",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("source", result.output.lower())

    # --- REQ-0.0.17-03-02 / 03: kind/semver binding ---

    def test_foundation_rejects_non_zero_zero_semver(self) -> None:
        """@covers REQ-0.0.17-03-02 — foundation requires 0.0.x semver."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "foundation",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("0.0.", result.output)
            target = Path("design/adr/foundation/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md")
            self.assertFalse(target.exists())

    def test_feature_rejects_zero_zero_semver(self) -> None:
        """@covers REQ-0.0.17-03-03 — feature rejects 0.0.x semver."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.0.18",
                    "--kind",
                    "feature",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("feature", result.output.lower())
            target = Path("design/adr/pre-release/ADR-0.0.18-sample-work/ADR-0.0.18-sample-work.md")
            self.assertFalse(target.exists())

    def test_foundation_accepts_0_0_x_semver_dryrun(self) -> None:
        """@covers REQ-0.0.17-03-02 — foundation + 0.0.x dry-run succeeds."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.0.18",
                    "--kind",
                    "foundation",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

    def test_feature_accepts_non_0_0_x_semver_dryrun(self) -> None:
        """@covers REQ-0.0.17-03-03 — feature + non-0.0.x dry-run succeeds."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

    # --- REQ-0.0.17-03-04: atomicity ---

    def test_validation_failure_writes_nothing(self) -> None:
        """@covers REQ-0.0.17-03-04 — rejection leaves pool/ledger/target untouched."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            config = self._seed_for_promote()
            ledger_path = Path(".gzkit/ledger.jsonl")
            pool_file = Path(config.paths.adrs) / "pool" / "ADR-pool.sample-work.md"
            pool_before = pool_file.read_text(encoding="utf-8")
            ledger_before = ledger_path.read_text(encoding="utf-8")
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "foundation",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertEqual(pool_file.read_text(encoding="utf-8"), pool_before)
            self.assertEqual(ledger_path.read_text(encoding="utf-8"), ledger_before)
            self.assertFalse((Path(config.paths.adrs) / "foundation").exists())

    def test_force_does_not_bypass_kind_validation(self) -> None:
        """@covers REQ-0.0.17-03-04 — --force does not skip kind/semver binding."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.0.18",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)

    # --- REQ-0.0.17-03-05: frontmatter kind: stamped ---

    def test_promoted_frontmatter_carries_kind_foundation(self) -> None:
        """@covers REQ-0.0.17-03-05 — foundation promotion stamps kind: foundation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.0.18",
                    "--kind",
                    "foundation",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            target = Path("design/adr/foundation/ADR-0.0.18-sample-work/ADR-0.0.18-sample-work.md")
            self.assertTrue(target.exists(), msg=result.output)
            frontmatter = target.read_text(encoding="utf-8").split("---", 2)[1]
            self.assertIn("kind: foundation", frontmatter)
            self.assertIn("id: ADR-0.0.18-sample-work", frontmatter)

    def test_promoted_frontmatter_carries_kind_feature(self) -> None:
        """@covers REQ-0.0.17-03-05 — feature promotion stamps kind: feature."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            target = Path("design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md")
            self.assertTrue(target.exists(), msg=result.output)
            frontmatter = target.read_text(encoding="utf-8").split("---", 2)[1]
            self.assertIn("kind: feature", frontmatter)

    def test_promoted_id_loses_pool_prefix(self) -> None:
        """@covers REQ-0.0.17-03-05 — promoted id transitions from ADR-pool.* to ADR-X.Y.Z-*."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            target = Path("design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md")
            frontmatter = target.read_text(encoding="utf-8").split("---", 2)[1]
            id_line = next(ln for ln in frontmatter.splitlines() if ln.startswith("id:"))
            self.assertNotIn("pool", id_line)
            self.assertRegex(id_line, r"^id:\s*ADR-\d+\.\d+\.\d+-")

    # --- REQ-0.0.17-03-06: kind-driven bucket routing ---

    def test_foundation_lands_in_foundation_bucket(self) -> None:
        """@covers REQ-0.0.17-03-06 — --kind foundation routes to foundation/."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.0.18",
                    "--kind",
                    "foundation",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(
                Path(
                    "design/adr/foundation/ADR-0.0.18-sample-work/ADR-0.0.18-sample-work.md"
                ).exists()
            )

    def test_feature_lands_in_pre_release_bucket(self) -> None:
        """@covers REQ-0.0.17-03-06 — --kind feature routes to pre-release/."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertTrue(
                Path(
                    "design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md"
                ).exists()
            )

    # --- REQ-0.0.17-03-07: ledger event extras ---

    def test_ledger_rename_event_includes_kind_and_semver(self) -> None:
        """@covers REQ-0.0.17-03-07 — artifact_renamed event extras include kind and semver."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            ledger_text = Path(".gzkit/ledger.jsonl").read_text(encoding="utf-8")
            rename_lines = [
                json.loads(line)
                for line in ledger_text.splitlines()
                if '"event":"artifact_renamed"' in line
            ]
            self.assertEqual(len(rename_lines), 1, msg=ledger_text)
            event = rename_lines[0]
            self.assertEqual(event.get("kind"), "feature")
            self.assertEqual(event.get("semver"), "0.6.0")
            # Backward-compatible existing fields:
            self.assertEqual(event.get("new_id"), "ADR-0.6.0-sample-work")
            self.assertEqual(event.get("reason"), "pool_promotion")


class TestAdrPromoteTaxonomyRoundtrip(unittest.TestCase):
    """OBPI-0.0.17-05 — scaffolder→validator round-trip for `gz adr promote --kind`.

    Mirrors GHI #186 / #216 precedent: invoke the promotion, assert the
    promoted file exists, then run `validate_document(path, "adr")` and
    assert zero errors. Uses the seed pool ADR pattern from
    `TestAdrPromoteKindFlag` to set up the source.

    @covers REQ-0.0.17-05-06
    """

    @staticmethod
    def _seed_pool_adr(config: GzkitConfig, adr_id: str = "ADR-pool.sample-work") -> Path:
        pool_dir = Path(config.paths.adrs) / "pool"
        pool_dir.mkdir(parents=True, exist_ok=True)
        pool_file = pool_dir / f"{adr_id}.md"
        pool_file.write_text(
            "---\n"
            f"id: {adr_id}\n"
            "status: Pool\n"
            "parent: PRD-GZKIT-1.0.0\n"
            "lane: heavy\n"
            "---\n\n"
            f"# {adr_id}: Sample Work\n\n"
            "## Status\n\nPool\n\n"
            "## Intent\n\n"
            "Turn sample pool work into executable tracked delivery.\n\n"
            "## Target Scope\n\n"
            "- Define runtime command contract\n"
            "- Persist machine-readable stage state\n"
            "- Expose structured stage outputs\n\n"
            "## Non-Goals\n\n"
            "- No external orchestrator\n",
            encoding="utf-8",
        )
        return pool_file

    def _seed_for_promote(self) -> GzkitConfig:
        _quick_init()
        config = GzkitConfig.load(Path(".gzkit.json"))
        self._seed_pool_adr(config)
        ledger = Ledger(Path(".gzkit/ledger.jsonl"))
        ledger.append(adr_created_event("ADR-pool.sample-work", "", "heavy"))
        return config

    def test_promote_to_foundation_passes_taxonomy_validator(self) -> None:
        """@covers REQ-0.0.17-05-06 — foundation promotion validates clean."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.0.18",
                    "--kind",
                    "foundation",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            target = Path("design/adr/foundation/ADR-0.0.18-sample-work/ADR-0.0.18-sample-work.md")
            self.assertTrue(target.exists(), msg=result.output)
            errors = validate_document(target, "adr")
            self.assertEqual(
                [e.message for e in errors],
                [],
                msg="validator rejected freshly-promoted foundation ADR",
            )

    def test_promote_to_feature_passes_taxonomy_validator(self) -> None:
        """@covers REQ-0.0.17-05-06 — feature promotion validates clean."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            self._seed_for_promote()
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.sample-work",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            target = Path("design/adr/pre-release/ADR-0.6.0-sample-work/ADR-0.6.0-sample-work.md")
            self.assertTrue(target.exists(), msg=result.output)
            errors = validate_document(target, "adr")
            self.assertEqual(
                [e.message for e in errors],
                [],
                msg="validator rejected freshly-promoted feature ADR",
            )
