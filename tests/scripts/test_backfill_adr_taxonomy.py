"""Unit tests for scripts/backfill_adr_taxonomy.py (OBPI-0.0.17-05).

@covers REQ-0.0.17-05-01 (idempotence)
@covers REQ-0.0.17-05-02 (semver classification)
@covers REQ-0.0.17-05-03 (preservation of other frontmatter)
@covers REQ-0.0.17-05-04 (receipt schema)
@covers REQ-0.0.17-05-08 (no ledger mutation)
"""

import importlib.util
import json
import sys
import tempfile
import unittest
from datetime import UTC, datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[2]
SCRIPT_PATH = REPO_ROOT / "scripts" / "backfill_adr_taxonomy.py"


def _load_backfill_module():
    """Import scripts/backfill_adr_taxonomy.py as an isolated module."""
    spec = importlib.util.spec_from_file_location("backfill_adr_taxonomy", SCRIPT_PATH)
    assert spec is not None and spec.loader is not None, f"cannot load {SCRIPT_PATH}"
    module = importlib.util.module_from_spec(spec)
    sys.modules["backfill_adr_taxonomy"] = module
    spec.loader.exec_module(module)
    return module


def _write_adr(
    root: Path, rel: str, *, semver: str | None = "0.0.5", include_kind: bool = False
) -> Path:
    """Write a fixture ADR with the given semver (or omit semver entirely if None)."""
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    lines = ["---", f"id: ADR-{semver or 'malformed'}-fixture", "status: Draft"]
    if include_kind:
        lines.append("kind: foundation")
    if semver is not None:
        lines.append(f"semver: {semver}")
    lines.extend(
        [
            "lane: heavy",
            "parent: PRD-FIXTURE-1.0.0",
            "date: 2026-04-19",
            "---",
            "",
            "# Fixture ADR",
            "",
            "Body content.",
            "",
        ]
    )
    path.write_text("\n".join(lines), encoding="utf-8")
    return path


class TestBackfillClassification(unittest.TestCase):
    """REQ-0.0.17-05-02 — semver-driven classification."""

    def test_classifies_foundation_and_feature_by_semver(self) -> None:
        """@covers REQ-0.0.17-05-02 — 0.0.x → foundation; everything else → feature."""
        module = _load_backfill_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            foundation_file = _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.5-x/ADR-0.0.5-x.md",
                semver="0.0.5",
            )
            feature_file = _write_adr(
                root,
                "docs/design/adr/pre-release/ADR-0.3.0-y/ADR-0.3.0-y.md",
                semver="0.3.0",
            )
            receipt_dir = root / "artifacts" / "receipts"
            receipt_dir.mkdir(parents=True)

            receipt = module.run_backfill(
                project_root=root,
                receipt_dir=receipt_dir,
                dry_run=False,
                now=datetime(2026, 4, 19, 12, 0, 0, tzinfo=UTC),
            )

            self.assertEqual(receipt["files_modified"], 2)
            self.assertIn("kind: foundation", foundation_file.read_text(encoding="utf-8"))
            self.assertIn("kind: feature", feature_file.read_text(encoding="utf-8"))

    def test_records_error_for_missing_semver(self) -> None:
        """@covers REQ-0.0.17-05-02 — missing semver: surfaces in receipt errors[]; no mutation."""
        module = _load_backfill_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            broken = _write_adr(
                root,
                "docs/design/adr/foundation/ADR-broken/ADR-broken.md",
                semver=None,
            )
            before = broken.read_text(encoding="utf-8")
            receipt_dir = root / "artifacts" / "receipts"
            receipt_dir.mkdir(parents=True)

            receipt = module.run_backfill(
                project_root=root,
                receipt_dir=receipt_dir,
                dry_run=False,
                now=datetime(2026, 4, 19, 12, 0, 0, tzinfo=UTC),
            )

            self.assertEqual(broken.read_text(encoding="utf-8"), before)
            self.assertEqual(receipt["files_modified"], 0)
            self.assertEqual(len(receipt["errors"]), 1)
            self.assertIn("broken", receipt["errors"][0]["path"])


class TestBackfillPreservation(unittest.TestCase):
    """REQ-0.0.17-05-03 — frontmatter preservation and ordering."""

    def test_preserves_other_frontmatter_fields_and_inserts_kind_after_status(self) -> None:
        """@covers REQ-0.0.17-05-03 — every non-kind field byte-identical; kind: after status:."""
        module = _load_backfill_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adr = _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.7-fix/ADR-0.0.7-fix.md",
                semver="0.0.7",
            )
            receipt_dir = root / "artifacts" / "receipts"
            receipt_dir.mkdir(parents=True)

            module.run_backfill(
                project_root=root,
                receipt_dir=receipt_dir,
                dry_run=False,
                now=datetime(2026, 4, 19, 12, 0, 0, tzinfo=UTC),
            )

            content = adr.read_text(encoding="utf-8")
            lines = content.splitlines()
            status_idx = next(i for i, line in enumerate(lines) if line.startswith("status:"))
            self.assertTrue(
                lines[status_idx + 1].startswith("kind:"),
                msg=f"expected kind: on line after status:, got: {lines[status_idx + 1]!r}",
            )
            self.assertIn("kind: foundation", lines[status_idx + 1])
            self.assertIn("id: ADR-0.0.7-fixture", content)
            self.assertIn("semver: 0.0.7", content)
            self.assertIn("lane: heavy", content)
            self.assertIn("parent: PRD-FIXTURE-1.0.0", content)
            self.assertIn("date: 2026-04-19", content)
            self.assertIn("# Fixture ADR", content)
            self.assertIn("Body content.", content)


class TestBackfillIdempotence(unittest.TestCase):
    """REQ-0.0.17-05-01 — idempotence + dry-run."""

    def test_second_run_is_noop(self) -> None:
        """@covers REQ-0.0.17-05-01 — second run reports zero modifications."""
        module = _load_backfill_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.5-x/ADR-0.0.5-x.md",
                semver="0.0.5",
            )
            receipt_dir = root / "artifacts" / "receipts"
            receipt_dir.mkdir(parents=True)
            now = datetime(2026, 4, 19, 12, 0, 0, tzinfo=UTC)

            first = module.run_backfill(
                project_root=root, receipt_dir=receipt_dir, dry_run=False, now=now
            )
            second = module.run_backfill(
                project_root=root,
                receipt_dir=receipt_dir,
                dry_run=False,
                now=datetime(2026, 4, 19, 12, 1, 0, tzinfo=UTC),
            )

            self.assertEqual(first["files_modified"], 1)
            self.assertEqual(second["files_modified"], 0)
            self.assertGreaterEqual(second["files_scanned"], 1)

    def test_dry_run_does_not_mutate(self) -> None:
        """@covers REQ-0.0.17-05-01 — --dry-run sets dry_run flag and writes no file changes."""
        module = _load_backfill_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            adr = _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.5-x/ADR-0.0.5-x.md",
                semver="0.0.5",
            )
            before = adr.read_text(encoding="utf-8")
            receipt_dir = root / "artifacts" / "receipts"
            receipt_dir.mkdir(parents=True)

            receipt = module.run_backfill(
                project_root=root,
                receipt_dir=receipt_dir,
                dry_run=True,
                now=datetime(2026, 4, 19, 12, 0, 0, tzinfo=UTC),
            )

            self.assertTrue(receipt["dry_run"])
            self.assertEqual(adr.read_text(encoding="utf-8"), before)


class TestBackfillReceipt(unittest.TestCase):
    """REQ-0.0.17-05-04 — receipt schema."""

    def test_emits_receipt_with_required_fields(self) -> None:
        """@covers REQ-0.0.17-05-04 — receipt JSON has required keys + writes to disk."""
        module = _load_backfill_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.5-x/ADR-0.0.5-x.md",
                semver="0.0.5",
            )
            receipt_dir = root / "artifacts" / "receipts"
            receipt_dir.mkdir(parents=True)

            receipt = module.run_backfill(
                project_root=root,
                receipt_dir=receipt_dir,
                dry_run=False,
                now=datetime(2026, 4, 19, 12, 34, 56, tzinfo=UTC),
            )

            for key in (
                "timestamp",
                "dry_run",
                "files_scanned",
                "files_modified",
                "modifications",
                "errors",
            ):
                self.assertIn(key, receipt, msg=f"receipt missing required key {key!r}")
            self.assertIsInstance(receipt["modifications"], list)
            self.assertIsInstance(receipt["errors"], list)
            for mod in receipt["modifications"]:
                self.assertIn("path", mod)
                self.assertIn("kind", mod)
                self.assertIn("semver", mod)

            receipt_files = list(receipt_dir.glob("adr-taxonomy-backfill-*.json"))
            self.assertEqual(len(receipt_files), 1)
            on_disk = json.loads(receipt_files[0].read_text(encoding="utf-8"))
            self.assertEqual(on_disk["files_modified"], receipt["files_modified"])


class TestBackfillLedgerSafety(unittest.TestCase):
    """REQ-0.0.17-05-08 — backfill never mutates .gzkit/ledger.jsonl."""

    def test_does_not_touch_ledger(self) -> None:
        """@covers REQ-0.0.17-05-08 — ledger byte-identical before/after."""
        module = _load_backfill_module()
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger_path.parent.mkdir(parents=True)
            ledger_path.write_text(
                '{"event":"project_init","project":"fixture"}\n', encoding="utf-8"
            )
            ledger_before = ledger_path.read_text(encoding="utf-8")

            _write_adr(
                root,
                "docs/design/adr/foundation/ADR-0.0.5-x/ADR-0.0.5-x.md",
                semver="0.0.5",
            )
            receipt_dir = root / "artifacts" / "receipts"
            receipt_dir.mkdir(parents=True)

            module.run_backfill(
                project_root=root,
                receipt_dir=receipt_dir,
                dry_run=False,
                now=datetime(2026, 4, 19, 12, 0, 0, tzinfo=UTC),
            )

            self.assertEqual(ledger_path.read_text(encoding="utf-8"), ledger_before)


if __name__ == "__main__":
    unittest.main()
