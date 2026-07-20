import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.commands.adr_promote_utils import (
    _parse_decomposition_table,
    _parse_top_level_markdown_bullets,
    _promoted_checklist_from_pool,
)
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
            "- No external orchestrator\n",
            encoding="utf-8",
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
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-0.6.0-f",
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
    #
    # test_foundation_rejects_non_zero_zero_semver retired (ADR-0.34.0
    # Foundation Sunset closes --kind foundation before the semver-binding
    # check ever runs); superseded by
    # tests/commands/test_foundation_kind_closed.py::
    # test_adr_promote_foundation_kind_rejected_before_semver_binding_check.

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

    # test_foundation_accepts_0_0_x_semver_dryrun retired (asserted
    # successful --kind foundation promotion, which ADR-0.34.0 Foundation
    # Sunset closes at the CLI); closure is proven by
    # tests/commands/test_foundation_kind_closed.py.

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

    # test_promoted_frontmatter_carries_kind_foundation retired (asserted
    # successful --kind foundation promotion, which ADR-0.34.0 Foundation
    # Sunset closes at the CLI); closure is proven by
    # tests/commands/test_foundation_kind_closed.py.

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

    # test_foundation_lands_in_foundation_bucket retired (asserted
    # successful --kind foundation promotion, which ADR-0.34.0 Foundation
    # Sunset closes at the CLI); closure is proven by
    # tests/commands/test_foundation_kind_closed.py.

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

    # Foundation promotion round-trip retired by ADR-0.34.0 (kind closed to new
    # authoring); rejection proven by tests/commands/test_foundation_kind_closed.py.
    # REQ-0.0.17-05-06 retains coverage from the feature round-trip below.

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


class TestDecompositionTableParser(unittest.TestCase):
    """GHI #241 — parser reads `## Proposed OBPI Decomposition` table when present."""

    def test_parse_decomposition_table_returns_slug_and_description(self) -> None:
        pool_content = (
            "# Sample\n\n"
            "## Target Scope\n\n"
            "Scope narrative here.\n\n"
            "## Proposed OBPI Decomposition\n\n"
            "| # | Slug | Description | Lane |\n"
            "|---|------|-------------|------|\n"
            "| 01 | check-pipeline | Implement ordered check pipeline | Lite |\n"
            "| 02 | auto-repair-tier | Deterministic auto-repair executor | Lite |\n"
            "| 03 | cli-surface | Flag surface and exit code contract | Heavy |\n"
        )
        rows = _parse_decomposition_table(pool_content)
        self.assertEqual(
            rows,
            [
                ("check-pipeline", "Implement ordered check pipeline"),
                ("auto-repair-tier", "Deterministic auto-repair executor"),
                ("cli-surface", "Flag surface and exit code contract"),
            ],
        )

    def test_parse_decomposition_table_missing_returns_none(self) -> None:
        pool_content = "# Sample\n\n## Target Scope\n\n- Do the thing\n"
        self.assertIsNone(_parse_decomposition_table(pool_content))

    def test_parse_decomposition_table_ignores_narrative_and_alignment_rows(self) -> None:
        pool_content = (
            "# Sample\n\n"
            "## Proposed OBPI Decomposition\n\n"
            "Brief narrative before the table.\n\n"
            "| # | Slug | Description |\n"
            "|---|------|-------------|\n"
            "| 01 | alpha | First item |\n"
            "\n"
            "Trailing note after the table.\n"
        )
        rows = _parse_decomposition_table(pool_content)
        self.assertEqual(rows, [("alpha", "First item")])


class TestBoldPrefixBulletParser(unittest.TestCase):
    """GHI #241 — bullet fallback uses `- **slug** — narrative` for slug extraction."""

    def test_promoted_checklist_uses_bold_prefix_slug(self) -> None:
        pool_content = (
            "---\nid: ADR-pool.demo\nstatus: Pool\n---\n\n"
            "# ADR-pool.demo: Demo\n\n"
            "## Target Scope\n\n"
            "- **alpha** — First scope item with narrative\n"
            "- **beta** — Second scope item with narrative\n"
        )
        scope_items, checklist, _scorecard = _promoted_checklist_from_pool(pool_content, "0.6.0")
        self.assertEqual(len(scope_items), 2)
        # The checklist must contain a slug-bearing marker the slugifier can honor
        self.assertIn("**alpha**", checklist)
        self.assertIn("**beta**", checklist)
        self.assertNotIn("First scope item with narrative — First scope", checklist)

    def test_bold_prefix_slug_survives_slugify(self) -> None:
        from gzkit.commands.specify_cmd import _slugify_obpi_name  # noqa: PLC0415

        core_text = "**check-pipeline** — Implement ordered check pipeline with Pydantic models"
        self.assertEqual(_slugify_obpi_name(core_text), "check-pipeline")


class TestPromoteObpiAllowedPathsAndTitleNormalization(unittest.TestCase):
    """GHI #536: promote-time scaffolding must normalize `path:line-range`
    backtick refs in Allowed Paths, and derive a short OBPI title from the
    bold-prefix slug rather than the full Target Scope bullet body."""

    @staticmethod
    def _seed_pool_adr_with_path_line_ref(config: GzkitConfig) -> Path:
        adr_id = "ADR-pool.line-ref-demo"
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
            f"# {adr_id}: Line Ref Demo\n\n"
            "## Status\n\nPool\n\n"
            "## Intent\n\nDemonstrate the path:line-range normalization bug.\n\n"
            "## Target Scope\n\n"
            "- **step-advance-gate-5-enforcement** — Gate 5 human attestation MUST "
            "occur only through an explicit CLI step-advance command, touching "
            "`src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`\n\n"
            "## Non-Goals\n\n- No external orchestrator\n",
            encoding="utf-8",
        )
        return pool_file

    def test_allowed_paths_strips_line_range_suffix(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr_with_path_line_ref(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.line-ref-demo", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.line-ref-demo",
                    "--semver",
                    "0.7.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            obpi_file = (
                Path(config.paths.adrs)
                / "pre-release"
                / "ADR-0.7.0-line-ref-demo"
                / "obpis"
                / "OBPI-0.7.0-01-step-advance-gate-5-enforcement.md"
            )
            self.assertTrue(obpi_file.exists(), msg=result.output)
            content = obpi_file.read_text(encoding="utf-8")
            allowed_paths_section = content.split("## Allowed Paths", 1)[1].split("## ", 1)[0]
            self.assertIn(
                "`src/gzkit/commands/closeout_ceremony.py`",
                allowed_paths_section,
                msg="Allowed Paths entry must be filesystem-resolvable (GHI #536)",
            )
            self.assertNotIn("closeout_ceremony.py:401", allowed_paths_section)

    def test_obpi_title_is_short_slug_not_full_bullet_body(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            self._seed_pool_adr_with_path_line_ref(config)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.line-ref-demo", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.line-ref-demo",
                    "--semver",
                    "0.7.0",
                    "--kind",
                    "feature",
                    "--force",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            obpi_file = (
                Path(config.paths.adrs)
                / "pre-release"
                / "ADR-0.7.0-line-ref-demo"
                / "obpis"
                / "OBPI-0.7.0-01-step-advance-gate-5-enforcement.md"
            )
            content = obpi_file.read_text(encoding="utf-8")
            title_line = next(line for line in content.splitlines() if line.startswith("# OBPI-"))
            self.assertLess(
                len(title_line),
                100,
                msg=f"OBPI title must be slug-derived, not the full bullet body: {title_line!r}",
            )
            self.assertNotIn("Gate 5 human attestation MUST occur", title_line)


class TestNestedSubsectionBulletParser(unittest.TestCase):
    """GHI #241 — bullets nested inside H3 subsections of Target Scope are ignored."""

    def test_nested_h3_bullets_ignored(self) -> None:
        section = (
            "Top-level scope intro.\n\n"
            "- alpha\n"
            "- beta\n\n"
            "### Detailed specification\n\n"
            "- Should not become an OBPI\n"
            "- Neither should this\n\n"
            "### ADR Overlap\n\n"
            "- Nor this nested bullet\n"
        )
        bullets = _parse_top_level_markdown_bullets(section)
        self.assertEqual(bullets, ["alpha", "beta"])


class TestLegacyNarrativeDeprecation(unittest.TestCase):
    """GHI #241 — legacy narrative-only Target Scope emits a deprecation warning."""

    def test_promote_dry_run_warns_on_legacy_format(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "ADR-pool.legacy-shape.md"
            pool_file.write_text(
                "---\n"
                "id: ADR-pool.legacy-shape\n"
                "status: Pool\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: heavy\n"
                "---\n\n"
                "# ADR-pool.legacy-shape: Legacy Shape\n\n"
                "## Intent\n\nTurn legacy narrative into tracked delivery.\n\n"
                "## Target Scope\n\n"
                "- Define the runtime contract with lots of narrative prose\n"
                "- Persist machine-readable state across sessions\n"
                "- Expose structured outputs for operator workflows\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.legacy-shape", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.legacy-shape",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            normalized = " ".join(result.output.split())
            self.assertIn("deprecated", normalized.lower())
            self.assertIn("Proposed OBPI Decomposition", normalized)


class TestDecompositionTablePrecedence(unittest.TestCase):
    """GHI #241 — table-first takes precedence over Target Scope narrative bullets."""

    def test_dry_run_uses_table_slugs_when_table_present(self) -> None:
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            config = GzkitConfig.load(Path(".gzkit.json"))
            pool_dir = Path(config.paths.adrs) / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_file = pool_dir / "ADR-pool.table-shape.md"
            pool_file.write_text(
                "---\n"
                "id: ADR-pool.table-shape\n"
                "status: Pool\n"
                "parent: PRD-GZKIT-1.0.0\n"
                "lane: heavy\n"
                "---\n\n"
                "# ADR-pool.table-shape: Table Shape\n\n"
                "## Intent\n\nTable-first decomposition test fixture.\n\n"
                "## Target Scope\n\n"
                "- Narrative description of the scope with prose\n"
                "  that spans multiple lines and mentions many ideas\n"
                "- Another narrative bullet that would produce a bad slug\n\n"
                "### Detailed specification\n\n"
                "- Not a top-level item\n\n"
                "## Proposed OBPI Decomposition\n\n"
                "| # | Slug | Description | Lane |\n"
                "|---|------|-------------|------|\n"
                "| 01 | check-pipeline | Ordered check pipeline | Lite |\n"
                "| 02 | auto-repair | Deterministic auto-repair | Lite |\n"
                "| 03 | cli-surface | Flag surface | Heavy |\n",
                encoding="utf-8",
            )
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-pool.table-shape", "", "heavy"))

            result = runner.invoke(
                main,
                [
                    "adr",
                    "promote",
                    "ADR-pool.table-shape",
                    "--semver",
                    "0.6.0",
                    "--kind",
                    "feature",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            self.assertIn("Would create OBPIs: 3", result.output)
            self.assertIn(
                "Would append obpi_created: OBPI-0.6.0-01-check-pipeline",
                result.output,
            )
            self.assertIn(
                "Would append obpi_created: OBPI-0.6.0-02-auto-repair",
                result.output,
            )
            self.assertIn(
                "Would append obpi_created: OBPI-0.6.0-03-cli-surface",
                result.output,
            )
