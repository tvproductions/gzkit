"""Tests for the ``gz frontmatter reconcile`` CLI adapter (ADR-0.0.16 OBPI-03).

Each test carries a ``@covers`` marker so ``gz covers`` can derive the
REQ → test coverage graph. REQ-0.0.16-03-01 (registration visibility) is
exercised here via ``gz chores list``; REQ-0.0.16-03-06 (schema) is
exercised via the CLI emitting a schema-valid receipt end-to-end.
"""

from __future__ import annotations

import json
import unittest
from pathlib import Path

from gzkit.cli import main
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _scaffold_adr(root: Path, adr_id: str, frontmatter: str) -> Path:
    """Scaffold an ADR at the config-resolved design_root path."""
    config = GzkitConfig.load(root / ".gzkit.json")
    path = (
        root
        / config.paths.design_root
        / "adr"
        / "pre-release"
        / f"{adr_id}-test"
        / f"{adr_id}-test.md"
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter, encoding="utf-8")
    return path


class TestFrontmatterReconcileCli(unittest.TestCase):
    """CLI surface coverage for ``gz frontmatter reconcile``."""

    @covers("REQ-0.0.16-03-01")
    def test_chore_registered_as_heavy_lane_in_production_config(self) -> None:
        """Production ``config/gzkit.chores.json`` lists the chore at lane heavy."""
        repo_root = Path(__file__).resolve().parents[2]
        registry = json.loads(
            (repo_root / "src" / "gzkit" / "chores" / "registry.json").read_text(encoding="utf-8")
        )
        matches = [
            c for c in registry.get("chores", []) if c.get("slug") == "frontmatter-ledger-coherence"
        ]
        self.assertEqual(len(matches), 1, "chore must be registered exactly once")
        self.assertEqual(matches[0].get("lane"), "heavy", "post-OBPI-03 lane is heavy")

    @covers("REQ-0.0.16-03-02")
    @covers("REQ-0.0.16-03-06")
    def test_reconcile_emits_schema_valid_receipt(self) -> None:
        """Drifted repo → gz frontmatter reconcile exit 0, schema-valid receipt on disk."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            adr_path = _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )

            result = runner.invoke(main, ["frontmatter", "reconcile", "--json"])
            self.assertEqual(result.exit_code, 0, msg=result.output)

            # Schema validation at the filesystem level
            receipts_dir = root / "artifacts" / "receipts" / "frontmatter-coherence"
            receipts = sorted(receipts_dir.glob("*.json"))
            self.assertGreaterEqual(len(receipts), 1)
            import jsonschema  # noqa: PLC0415

            schema_path = (
                Path(__file__).resolve().parents[2]
                / "data"
                / "schemas"
                / "frontmatter_coherence_receipt.schema.json"
            )
            schema = json.loads(schema_path.read_text(encoding="utf-8"))
            receipt = json.loads(receipts[-1].read_text(encoding="utf-8"))
            jsonschema.validate(instance=receipt, schema=schema)

            # Drift resolved: lane rewritten heavy → lite
            self.assertIn("lane: lite", adr_path.read_text(encoding="utf-8"))

    @covers("REQ-0.0.16-03-07")
    def test_unmapped_status_term_exits_policy_breach(self) -> None:
        """CLI exit code 3 when the reconciler encounters an unmapped status term."""
        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n"
                "status: Nonsense\n---\n# ADR\n",
            )

            result = runner.invoke(main, ["frontmatter", "reconcile"])
            self.assertEqual(result.exit_code, 3, msg=result.output)
            self.assertIn("Nonsense", result.output)


class TestRenderRefusedRewrites(unittest.TestCase):
    """Output-form fixture tests: refused rewrites MUST be operator-visible.

    Coupled-surface coherence for the OBPI-0.31.0-03 receipt contract: the
    renderer is a consumer of ``ReconciliationReceipt.refused_rewrites`` and
    must never report a receipt carrying refusals as "no drift detected".
    """

    @staticmethod
    def _receipt(refused: bool):
        from gzkit.governance.frontmatter_coherence import (  # noqa: PLC0415
            ReconciliationReceipt,
            RefusedRewrite,
        )

        return ReconciliationReceipt(
            ledger_cursor="sha256:" + ("0" * 64),
            run_started_at="2026-07-04T00:00:00+00:00",
            run_completed_at="2026-07-04T00:00:01+00:00",
            files_rewritten=[],
            skipped=[],
            refused_rewrites=(
                [
                    RefusedRewrite(
                        path="docs/design/adr/pre-release/X/obpis/OBPI-9.9.9-01-x.md",
                        reason="Invalid OBPI status transition: Draft -> Active",
                    )
                ]
                if refused
                else []
            ),
            dry_run=True,
        )

    def test_refused_rewrites_are_rendered_and_not_reported_as_clean(self) -> None:
        from gzkit.commands.common import console  # noqa: PLC0415
        from gzkit.commands.frontmatter_reconcile import _render_human_receipt  # noqa: PLC0415

        with console.capture() as capture:
            _render_human_receipt(self._receipt(refused=True), dry_run=True)
        output = capture.get()
        self.assertIn("refused", output.lower(), "refusal count/section must be rendered")
        self.assertIn("OBPI-9.9.9-01-x.md", output, "refused path must be rendered")
        self.assertIn("Invalid OBPI status transition", output, "refusal reason must be rendered")
        self.assertNotIn(
            "no drift detected",
            output.lower(),
            "a receipt carrying refusals must never be reported as clean",
        )

    def test_clean_receipt_still_reports_no_drift(self) -> None:
        from gzkit.commands.common import console  # noqa: PLC0415
        from gzkit.commands.frontmatter_reconcile import _render_human_receipt  # noqa: PLC0415

        with console.capture() as capture:
            _render_human_receipt(self._receipt(refused=False), dry_run=True)
        output = capture.get()
        self.assertIn("no drift detected", output.lower())


if __name__ == "__main__":
    unittest.main()
