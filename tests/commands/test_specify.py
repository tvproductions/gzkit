import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.commands.specify_cmd import _extract_backticked_paths
from gzkit.governance.brief_structure import BriefStructure, parse_brief
from tests.commands.common import CliRunner, _quick_init


class TestExtractBacktickedPathsLineRangeNormalization(unittest.TestCase):
    """GHI #536: a backtick-quoted ``path:line-range`` reference must
    normalize to the bare filesystem path -- the raw suffix produces an
    Allowed Paths entry no existence check can resolve."""

    def test_strips_single_line_suffix(self) -> None:
        text = "See `src/gzkit/commands/ceremony_data.py:288-342` for the logic."
        self.assertEqual(_extract_backticked_paths(text), ["src/gzkit/commands/ceremony_data.py"])

    def test_strips_multi_range_suffix(self) -> None:
        text = "`src/gzkit/commands/closeout_ceremony.py:401, 416-426, 449-456`"
        self.assertEqual(
            _extract_backticked_paths(text), ["src/gzkit/commands/closeout_ceremony.py"]
        )

    def test_strips_suffix_on_md_path(self) -> None:
        text = "`.gzkit/skills/gz-adr-closeout-ceremony/SKILL.md:285-339`"
        self.assertEqual(
            _extract_backticked_paths(text),
            [".gzkit/skills/gz-adr-closeout-ceremony/SKILL.md"],
        )

    def test_plain_path_without_suffix_unchanged(self) -> None:
        text = "`src/gzkit/commands/plan.py` is the scaffolder."
        self.assertEqual(_extract_backticked_paths(text), ["src/gzkit/commands/plan.py"])


class TestSpecifyCommand(unittest.TestCase):
    """Tests for gz specify command."""

    def test_specify_creates_obpi_file(self) -> None:
        """specify creates OBPI file."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0-f", "--item", "1"]
            )
            self.assertEqual(result.exit_code, 0)
            obpi_path = Path(
                "design/adr/pre-release/ADR-0.1.0-f/obpis/OBPI-0.1.0-01-core-feature.md"
            )
            self.assertTrue(obpi_path.exists())
            content = obpi_path.read_text(encoding="utf-8")
            self.assertIn('Checklist Item:** #1 - "OBPI-0.1.0-01:', content)
            self.assertNotIn('Checklist Item:** #1 - "TBD"', content)

    def test_specify_rejects_pool_parent(self) -> None:
        """specify blocks pool ADR parents until promotion."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["specify", "core-feature", "--parent", "ADR-pool.sample", "--item", "1"],
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("Pool ADRs cannot receive OBPIs until promoted", result.output)

    def test_specify_rejects_out_of_range_item(self) -> None:
        """specify rejects checklist item numbers outside scorecard-backed checklist range."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0-f", "--item", "2"]
            )
            self.assertNotEqual(result.exit_code, 0)
            self.assertIn("out of range", result.output)

    def test_specify_ignores_withdrawn_checklist_items_for_live_target(self) -> None:
        """Withdrawn checklist identities remain addressable history, not live target count."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            adr_path = Path("design/adr/pre-release/ADR-0.1.0-f/ADR-0.1.0-f.md")
            content = adr_path.read_text(encoding="utf-8")
            content = content.replace(
                "- [ ] OBPI-0.1.0-01: Define scope, constraints, and acceptance criteria",
                "\n".join(
                    [
                        "- [ ] OBPI-0.1.0-01: Define scope, constraints, and acceptance criteria",
                        "- [ ] OBPI-0.1.0-02: Superseded historical slot "
                        "[withdrawn; replaced by OBPI-0.1.0-03]",
                    ]
                ),
            )
            adr_path.write_text(content, encoding="utf-8")

            live_result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0-f", "--item", "1"]
            )
            self.assertEqual(live_result.exit_code, 0)

            withdrawn_result = runner.invoke(
                main, ["specify", "old-feature", "--parent", "ADR-0.1.0-f", "--item", "2"]
            )
            self.assertNotEqual(withdrawn_result.exit_code, 0)
            self.assertIn("withdrawn", withdrawn_result.output)

    def test_specify_warns_about_template_defaults(self) -> None:
        """specify reports ADR-derived seeding and avoids scaffold placeholders."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0-f", "--item", "1"]
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("populated from ADR content", result.output)
            self.assertIn("Review allowed paths", result.output)
            obpi_path = Path(
                "design/adr/pre-release/ADR-0.1.0-f/obpis/OBPI-0.1.0-01-core-feature.md"
            )
            content = obpi_path.read_text(encoding="utf-8")
            self.assertNotIn("command --to --verify", content)
            self.assertNotIn("path/to/prerequisite", content)
            self.assertNotIn("Given/When/Then behavior criterion", content)

    def test_specify_dry_run_reports_default_lane_source_without_wbs_table(self) -> None:
        """A dry run against an ADR with no WBS table must report the true
        fallback source ('default'), not misattribute the resolved lane to
        a WBS table row that does not exist."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main,
                [
                    "specify",
                    "core-feature",
                    "--parent",
                    "ADR-0.1.0-f",
                    "--item",
                    "1",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("source: default", result.output)
            self.assertNotIn("source: WBS table", result.output)

    def test_specify_emits_schema_parseable_brief(self) -> None:
        """GHI #615: a freshly emitted brief MUST parse as ``BriefStructure``.

        The schema exists but the emitter never fed it: the template wrote
        ``id/parent/item/lane/status`` and left ``allowlist``/``reqs``/
        ``verification`` -- the exact trio ``parse_brief`` requires -- to prose
        in the body. Every ``gz specify`` therefore minted a brief that fell to
        ``LegacyBriefShape`` regex-scraping by construction, which is why the
        legacy corpus kept growing (597 briefs when #615 was filed, 665 by
        2026-07-25) while the schema sat unenforced.

        Asserted in ``strict=True`` because permissive mode's contract is to
        *succeed* on a legacy brief; only strict mode can fail when the emitter
        regresses. The claim is the emitter's, not the parser's: no brief this
        command produces may need the legacy path.
        """
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main, ["specify", "core-feature", "--parent", "ADR-0.1.0-f", "--item", "1"]
            )
            self.assertEqual(result.exit_code, 0)
            obpi_path = Path(
                "design/adr/pre-release/ADR-0.1.0-f/obpis/OBPI-0.1.0-01-core-feature.md"
            )

            parsed = parse_brief(obpi_path, strict=True)

            self.assertIsInstance(parsed, BriefStructure)
            assert isinstance(parsed, BriefStructure)
            self.assertEqual(parsed.id, "OBPI-0.1.0-01-core-feature")
            self.assertEqual(parsed.parent, "ADR-0.1.0-f")
            # The three fields are derived from the same data the body renders,
            # so a populated frontmatter and an empty body section cannot drift.
            self.assertTrue(parsed.allowlist)
            self.assertTrue(parsed.reqs)
            self.assertTrue(parsed.verification)
            for req in parsed.reqs:
                self.assertIn(req, obpi_path.read_text(encoding="utf-8"))

    def test_specify_author_creates_authored_ready_brief(self) -> None:
        """specify --author produces a brief that passes authored validation."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            runner.invoke(main, ["plan", "create", "f", "--kind", "feature"])
            result = runner.invoke(
                main,
                ["specify", "core-feature", "--parent", "ADR-0.1.0-f", "--item", "1", "--author"],
            )
            self.assertEqual(result.exit_code, 0)
            self.assertIn("validated for pipeline entry", result.output)

            obpi_path = Path(
                "design/adr/pre-release/ADR-0.1.0-f/obpis/OBPI-0.1.0-01-core-feature.md"
            )
            content = obpi_path.read_text(encoding="utf-8")
            self.assertNotIn("<!--", content)

            validate_result = runner.invoke(
                main,
                ["obpi", "validate", str(obpi_path), "--authored"],
            )
            self.assertEqual(validate_result.exit_code, 0)
