import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.ledger import Ledger
from tests.commands.common import CliRunner, _quick_init


class TestPlanCommand(unittest.TestCase):
    """Tests for gz plan command.

    @covers REQ-0.0.17-02-01 (kind required)
    @covers REQ-0.0.17-02-02 (foundation semver gate)
    @covers REQ-0.0.17-02-03 (feature semver gate)
    @covers REQ-0.0.17-02-04 (pool routing + no kind field)
    @covers REQ-0.0.17-02-05 (kind after status in template)
    @covers REQ-0.0.17-02-06 (validate-before-write atomicity)
    @covers REQ-0.0.17-02-07 (foundation/feature directory routing)
    @covers REQ-0.0.17-02-08 (prior behavior preserved)
    """

    # --- REQ-0.0.17-02-01: --kind required ---

    def test_plan_create_requires_kind_flag(self) -> None:
        """@covers REQ-0.0.17-02-01 — omitting --kind exits 1 naming both foundation/feature."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(main, ["plan", "create", "scratch", "--semver", "0.1.0"])
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("foundation", result.output)
            self.assertIn("feature", result.output)

    # --- REQ-0.0.17-02-02: foundation requires 0.0.x semver ---

    def test_plan_create_foundation_rejects_non_0_0_x_semver(self) -> None:
        """@covers REQ-0.0.17-02-02 — foundation + non-0.0.x exits 1 with recovery."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "scratch",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.5.0",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("0.0.", result.output)
            foundation_root = Path("design/adr/foundation")
            self.assertFalse(
                foundation_root.exists() and any(foundation_root.rglob("*.md")),
                msg="foundation tree must remain untouched on rejection",
            )

    # --- REQ-0.0.17-02-03: feature rejects 0.0.x semver ---

    def test_plan_create_feature_rejects_0_0_x_semver(self) -> None:
        """@covers REQ-0.0.17-02-03 — feature + 0.0.x exits 1 with recovery."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "scratch",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.0.50",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)
            self.assertIn("feature", result.output.lower())
            pre_release_root = Path("design/adr/pre-release")
            self.assertFalse(
                pre_release_root.exists() and any(pre_release_root.rglob("*.md")),
                msg="pre-release tree must remain untouched on rejection",
            )

    # --- REQ-0.0.17-02-04: pool routing + no kind field ---

    def test_plan_create_pool_routes_to_flat_pool_file_without_kind_field(self) -> None:
        """@covers REQ-0.0.17-02-04 — pool writes ADR-pool.<slug>.md flat, no kind: / no semver:."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["plan", "create", "experimental-thing", "--kind", "pool"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path("design/adr/pool/ADR-pool.experimental-thing.md")
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")
            content = adr_path.read_text(encoding="utf-8")
            # Frontmatter block (between first two --- fences)
            frontmatter = content.split("---", 2)[1]
            self.assertNotIn("kind:", frontmatter, msg="pool ADRs must not carry kind:")
            self.assertNotIn("semver:", frontmatter, msg="pool ADRs must not carry semver:")
            self.assertIn("status: Pool", frontmatter)

    # --- REQ-0.0.17-02-05: template places kind after status ---

    def test_plan_create_foundation_template_places_kind_after_status(self) -> None:
        """@covers REQ-0.0.17-02-05 — rendered frontmatter: kind: immediately after status:."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "new-foundation",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.99",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path("design/adr/foundation/ADR-0.0.99/ADR-0.0.99.md")
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")
            content = adr_path.read_text(encoding="utf-8")
            lines = content.splitlines()
            status_idx = next(i for i, line in enumerate(lines) if line.startswith("status:"))
            self.assertTrue(
                lines[status_idx + 1].startswith("kind:"),
                msg=f"expected kind: on line after status:, got: {lines[status_idx + 1]!r}",
            )
            self.assertIn("kind: foundation", lines[status_idx + 1])

    # --- REQ-0.0.17-02-06: validate-before-write atomicity ---

    def test_plan_create_rejection_writes_no_file_no_ledger_event(self) -> None:
        """@covers REQ-0.0.17-02-06 — rejection writes nothing anywhere (file nor ledger)."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            ledger_before = Ledger(Path(".gzkit/ledger.jsonl"))
            events_before = len(ledger_before.read_all())

            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "scratch",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.0.99",
                    "--dry-run",
                ],
            )
            self.assertEqual(result.exit_code, 1, msg=result.output)

            # No ADR markdown anywhere under design/adr
            adr_tree = list(Path("design/adr").rglob("*.md")) if Path("design/adr").exists() else []
            self.assertEqual(adr_tree, [], msg="no ADR files should have been written on rejection")

            # No new ledger events
            ledger_after = Ledger(Path(".gzkit/ledger.jsonl"))
            events_after = len(ledger_after.read_all())
            self.assertEqual(events_after, events_before, msg="no new ledger events on rejection")

    # --- REQ-0.0.17-02-07: foundation/feature per-ADR folder routing ---

    def test_plan_create_foundation_routes_to_foundation_dir_per_adr_folder(self) -> None:
        """@covers REQ-0.0.17-02-07 — foundation ADRs land at foundation/<id>/<id>.md."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "infra-thing",
                    "--kind",
                    "foundation",
                    "--semver",
                    "0.0.42",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path("design/adr/foundation/ADR-0.0.42/ADR-0.0.42.md")
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")

    def test_plan_create_feature_routes_to_pre_release_dir_per_adr_folder(self) -> None:
        """@covers REQ-0.0.17-02-07 — feature ADRs land at pre-release/<id>/<id>.md."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "new-feature",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.5.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path("design/adr/pre-release/ADR-0.5.0/ADR-0.5.0.md")
            self.assertTrue(adr_path.exists(), msg=f"expected {adr_path}")

    # --- REQ-0.0.17-02-08: prior behavior preserved (scorecard, ledger, canonicalization) ---

    def test_plan_creates_file_with_scorecard(self) -> None:
        """@covers REQ-0.0.17-02-08 — scorecard + checklist generation unchanged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                ["plan", "create", "0.1.0", "--kind", "feature", "--semver", "0.1.0"],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            adr_path = Path("design/adr/pre-release/ADR-0.1.0/ADR-0.1.0.md")
            self.assertTrue(adr_path.exists())
            content = adr_path.read_text(encoding="utf-8")
            self.assertIn("## Decomposition Scorecard", content)
            self.assertIn("- Final Target OBPI Count: 1", content)
            self.assertEqual(content.count("- [ ] OBPI-0.1.0-"), 1)

    def test_plan_registers_adr_in_ledger(self) -> None:
        """@covers REQ-0.0.17-02-08 — ledger registration path unchanged."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "my-feature",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.2.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)
            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            graph = ledger.get_artifact_graph()
            self.assertIn("ADR-0.2.0", graph)
            self.assertEqual(graph["ADR-0.2.0"]["type"], "adr")

    def test_plan_canonicalizes_short_form_adr_parent(self) -> None:
        """@covers REQ-0.0.17-02-08 (GHI #222) — parent canonicalization preserved."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            from gzkit.ledger import adr_created_event

            ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            ledger.append(adr_created_event("ADR-0.3.0-parent-feature", "PRD-1", "lite"))

            result = runner.invoke(
                main,
                [
                    "plan",
                    "create",
                    "child-feature",
                    "--kind",
                    "feature",
                    "--semver",
                    "0.4.0",
                    "--obpi",
                    "ADR-0.3.0",
                ],
            )
            self.assertEqual(result.exit_code, 0, msg=result.output)

            fresh_ledger = Ledger(Path(".gzkit/ledger.jsonl"))
            graph = fresh_ledger.get_artifact_graph()
            child = graph.get("ADR-0.4.0")
            self.assertIsNotNone(child)
            self.assertEqual(child["parent"], "ADR-0.3.0-parent-feature")

            adr_path = Path("design/adr/pre-release/ADR-0.4.0/ADR-0.4.0.md")
            content = adr_path.read_text(encoding="utf-8")
            self.assertIn("parent: ADR-0.3.0-parent-feature", content)
