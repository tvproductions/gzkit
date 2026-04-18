"""Tests for the frontmatter-ledger reconciliation logic (ADR-0.0.16 OBPI-03).

Tests derive from the OBPI brief's REQ list. Each test carries a ``@covers``
decoration so ``gz covers`` can rebuild the REQ → test coverage graph.
"""

from __future__ import annotations

import hashlib
import json
import unittest
from pathlib import Path

from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, adr_created_event
from gzkit.traceability import covers
from tests.commands.common import CliRunner, _quick_init


def _adr_path(root: Path, adr_id: str) -> Path:
    config = GzkitConfig.load(root / ".gzkit.json")
    return (
        root
        / config.paths.design_root
        / "adr"
        / "pre-release"
        / f"{adr_id}-test"
        / f"{adr_id}-test.md"
    )


def _scaffold_adr(root: Path, adr_id: str, frontmatter: str) -> Path:
    path = _adr_path(root, adr_id)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(frontmatter, encoding="utf-8")
    return path


def _schema_validate(receipt_dict: dict) -> None:
    """Validate a receipt dict against the new schema file."""
    import jsonschema  # noqa: PLC0415

    schema_path = (
        Path(__file__).resolve().parents[2]
        / "data"
        / "schemas"
        / "frontmatter_coherence_receipt.schema.json"
    )
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    jsonschema.validate(instance=receipt_dict, schema=schema)


class ReceiptModelTests(unittest.TestCase):
    """Pydantic models must round-trip through the JSON schema."""

    @covers("REQ-0.0.16-03-06")
    def test_empty_receipt_validates_against_schema(self) -> None:
        from gzkit.governance.frontmatter_coherence import ReconciliationReceipt  # noqa: PLC0415

        receipt = ReconciliationReceipt(
            ledger_cursor="sha256:" + ("0" * 64),
            run_started_at="2026-04-18T10:00:00+00:00",
            run_completed_at="2026-04-18T10:00:01+00:00",
            files_rewritten=[],
            skipped=[],
            dry_run=False,
        )
        _schema_validate(receipt.model_dump(mode="json"))

    @covers("REQ-0.0.16-03-06")
    def test_populated_receipt_validates_against_schema(self) -> None:
        from gzkit.governance.frontmatter_coherence import (  # noqa: PLC0415
            FieldDiff,
            FileRewrite,
            ReconciliationReceipt,
            SkipNote,
        )

        receipt = ReconciliationReceipt(
            ledger_cursor="sha256:" + ("a" * 64),
            run_started_at="2026-04-18T10:00:00+00:00",
            run_completed_at="2026-04-18T10:00:01+00:00",
            files_rewritten=[
                FileRewrite(
                    path="docs/design/adr/foo/ADR-0.1.2-bar.md",
                    diffs=[
                        FieldDiff(field="status", before="Completed", after="pending"),
                        FieldDiff(field="lane", before="heavy", after="lite"),
                    ],
                )
            ],
            skipped=[SkipNote(path="docs/design/adr/pool/ADR-pool.foo.md", reason="pool-adr")],
            dry_run=True,
        )
        _schema_validate(receipt.model_dump(mode="json"))


class ReconciliationLogicTests(unittest.TestCase):
    """REQ-level tests for reconcile_frontmatter() core semantics."""

    @covers("REQ-0.0.16-03-02")
    def test_drifted_status_is_rewritten_to_ledger_term(self) -> None:
        """Non-dry-run rewrites frontmatter status: to the ledger's canonical term."""
        from gzkit.governance.frontmatter_coherence import reconcile_frontmatter  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            # Ledger has only adr_created → lifecycle "pending" (or "Pending" pre-#05).
            # Frontmatter claims "Completed" which is drift.
            path = _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n"
                "status: Completed\n---\n# ADR\n",
            )

            receipt = reconcile_frontmatter(root, dry_run=False)

            content = path.read_text(encoding="utf-8")
            self.assertNotIn("status: Completed", content)
            # One file rewritten, status field in diff
            self.assertEqual(len(receipt.files_rewritten), 1)
            diffs = receipt.files_rewritten[0].diffs
            status_diffs = [d for d in diffs if d.field == "status"]
            self.assertEqual(len(status_diffs), 1)
            self.assertEqual(status_diffs[0].before, "Completed")
            # after is the ledger's canonical term; derive_adr_semantics returns
            # "Pending" (capital) for the created-but-not-attested state
            self.assertIn(status_diffs[0].after.lower(), {"pending"})

    @covers("REQ-0.0.16-03-03")
    def test_dry_run_does_not_mutate_files(self) -> None:
        """--dry-run produces a receipt without touching ADR/OBPI files."""
        from gzkit.governance.frontmatter_coherence import reconcile_frontmatter  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            path = _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            pre_hash = hashlib.sha256(path.read_bytes()).hexdigest()

            receipt = reconcile_frontmatter(root, dry_run=True)

            post_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(pre_hash, post_hash, "dry-run must not mutate ADR/OBPI files")
            self.assertTrue(receipt.dry_run)
            self.assertEqual(len(receipt.files_rewritten), 1)

    @covers("REQ-0.0.16-03-04")
    def test_second_run_is_idempotent(self) -> None:
        """Second invocation with no ledger change produces empty files_rewritten."""
        from gzkit.governance.frontmatter_coherence import reconcile_frontmatter  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )

            reconcile_frontmatter(root, dry_run=False)
            second = reconcile_frontmatter(root, dry_run=False)

            self.assertEqual(
                second.files_rewritten,
                [],
                "idempotent reconciliation must produce empty files_rewritten on second run",
            )

    @covers("REQ-0.0.16-03-05")
    def test_ungoverned_keys_preserved_byte_identical(self) -> None:
        """Rewriting governed keys must leave every other byte identical."""
        from gzkit.governance.frontmatter_coherence import reconcile_frontmatter  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            original = (
                "---\n"
                "id: ADR-0.1.0\n"
                "parent: PRD-TEST-1.0.0\n"
                "lane: heavy\n"
                "tags:\n"
                "  - governance\n"
                "  - frontmatter\n"
                "related: ADR-0.0.16  # cross-reference\n"
                "\n"
                "---\n"
                "# Body\n"
                "\n"
                "Untouched prose.\n"
            )
            path = _scaffold_adr(root, "ADR-0.1.0", original)

            reconcile_frontmatter(root, dry_run=False)

            result = path.read_text(encoding="utf-8")
            # The lane: line changed heavy → lite; every other line identical
            self.assertIn("lane: lite", result)
            self.assertIn("tags:\n  - governance\n  - frontmatter", result)
            self.assertIn("related: ADR-0.0.16  # cross-reference", result)
            self.assertIn("# Body\n\nUntouched prose.\n", result)
            # Body is byte-identical
            body_start = result.index("---\n# Body")
            original_body_start = original.index("---\n# Body")
            self.assertEqual(result[body_start:], original[original_body_start:])

    @covers("REQ-0.0.16-03-07")
    def test_unmapped_status_term_raises_blocker(self) -> None:
        """Unmapped frontmatter status term → UnmappedStatusBlocker, zero mutations."""
        from gzkit.governance.frontmatter_coherence import (  # noqa: PLC0415
            UnmappedStatusBlocker,
            reconcile_frontmatter,
        )

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            path = _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: lite\n"
                "status: Whatever\n---\n# ADR\n",
            )
            pre_hash = hashlib.sha256(path.read_bytes()).hexdigest()

            with self.assertRaises(UnmappedStatusBlocker) as ctx:
                reconcile_frontmatter(root, dry_run=False)

            self.assertIn("Whatever", str(ctx.exception))
            post_hash = hashlib.sha256(path.read_bytes()).hexdigest()
            self.assertEqual(pre_hash, post_hash, "BLOCKER must not mutate any file")

    @covers("REQ-0.0.16-03-09")
    def test_pool_adr_is_skipped(self) -> None:
        """Pool ADRs (ADR-pool.* or path under docs/design/adr/pool/) are skipped."""
        from gzkit.governance.frontmatter_coherence import reconcile_frontmatter  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            config = GzkitConfig.load(root / ".gzkit.json")
            pool_dir = root / config.paths.design_root / "adr" / "pool"
            pool_dir.mkdir(parents=True, exist_ok=True)
            pool_path = pool_dir / "ADR-pool.foo-test.md"
            original = (
                "---\nid: ADR-pool.foo\nparent: PRD-TEST-1.0.0\nlane: heavy\n"
                "status: Draft\n---\n# Pool ADR\n"
            )
            pool_path.write_text(original, encoding="utf-8")
            pre_hash = hashlib.sha256(pool_path.read_bytes()).hexdigest()

            receipt = reconcile_frontmatter(root, dry_run=False)

            post_hash = hashlib.sha256(pool_path.read_bytes()).hexdigest()
            self.assertEqual(pre_hash, post_hash, "pool ADR must not be mutated")
            skip_paths = [s.path for s in receipt.skipped]
            self.assertTrue(
                any("pool" in p for p in skip_paths),
                f"pool ADR must appear in skipped list, got {skip_paths}",
            )

    @covers("REQ-0.0.16-03-08")
    def test_mid_run_ledger_mutation_does_not_leak_into_receipt(self) -> None:
        """Starting-cursor state is pinned; a mid-run ledger append is ignored."""
        from gzkit.governance import frontmatter_coherence as fc  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger_path = root / ".gzkit" / "ledger.jsonl"
            ledger = Ledger(ledger_path)
            # Baseline: one lite ADR registered. Frontmatter drift on lane.
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            baseline_cursor = fc._compute_ledger_cursor(ledger_path)

            # Monkeypatch _enumerate_pool_artifacts to append a second ADR to
            # the ledger mid-run — simulating concurrent governance activity
            # between cursor snapshot and the final receipt assembly.
            original = fc._enumerate_pool_artifacts

            def _inject_mutation(project_root: Path) -> list[str]:
                mid_ledger = Ledger(ledger_path)
                mid_ledger.append(adr_created_event("ADR-0.1.99", "PRD-TEST-1.0.0", "lite"))
                return original(project_root)

            fc._enumerate_pool_artifacts = _inject_mutation  # type: ignore[assignment]
            try:
                receipt = fc.reconcile_frontmatter(root, dry_run=True)
            finally:
                fc._enumerate_pool_artifacts = original  # type: ignore[assignment]

            # Starting-cursor preserved: the cursor on the receipt matches what
            # was computed before the mid-run mutation.
            self.assertEqual(receipt.ledger_cursor, baseline_cursor)
            # Only the original drifted ADR is in files_rewritten — the mid-run
            # ADR would have no frontmatter file on disk anyway, but more
            # importantly the validator read the pinned graph, so no extra
            # drift derived from the post-mutation ledger leaks in.
            paths = {f.path for f in receipt.files_rewritten}
            self.assertTrue(
                any("ADR-0.1.0" in p for p in paths),
                f"original drift must appear, got {paths}",
            )
            self.assertFalse(
                any("ADR-0.1.99" in p for p in paths),
                f"mid-run-injected ADR must not appear, got {paths}",
            )

    @covers("REQ-0.0.16-03-10")
    def test_partial_failure_receipt_shows_completed_entries(self) -> None:
        """Mid-loop exception still writes a receipt with the N entries completed."""
        from gzkit.governance import frontmatter_coherence as fc  # noqa: PLC0415

        runner = CliRunner()
        with runner.isolated_filesystem():
            _quick_init()
            root = Path.cwd()
            ledger = Ledger(root / ".gzkit" / "ledger.jsonl")
            ledger.append(adr_created_event("ADR-0.1.0", "PRD-TEST-1.0.0", "lite"))
            ledger.append(adr_created_event("ADR-0.2.0", "PRD-TEST-1.0.0", "lite"))
            _scaffold_adr(
                root,
                "ADR-0.1.0",
                "---\nid: ADR-0.1.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )
            _scaffold_adr(
                root,
                "ADR-0.2.0",
                "---\nid: ADR-0.2.0\nparent: PRD-TEST-1.0.0\nlane: heavy\n---\n# ADR\n",
            )

            # Patch the rewriter to raise after the first file is rewritten.
            original_rewriter = fc._rewrite_governed_keys_in_place
            call_count = {"n": 0}

            def _flaky_rewriter(path: Path, edits: dict) -> None:
                call_count["n"] += 1
                if call_count["n"] > 1:
                    raise OSError("simulated disk full after first file")
                original_rewriter(path, edits)

            fc._rewrite_governed_keys_in_place = _flaky_rewriter  # type: ignore[assignment]
            try:
                with self.assertRaises(OSError):
                    fc.reconcile_frontmatter(root, dry_run=False)
            finally:
                fc._rewrite_governed_keys_in_place = original_rewriter  # type: ignore[assignment]

            # A receipt file should have been emitted despite the exception.
            receipts_dir = root / "artifacts" / "receipts" / "frontmatter-coherence"
            self.assertTrue(receipts_dir.is_dir(), "partial-failure receipt dir must exist")
            receipt_files = sorted(receipts_dir.glob("*.json"))
            self.assertGreaterEqual(len(receipt_files), 1)
            latest = json.loads(receipt_files[-1].read_text(encoding="utf-8"))
            # Exactly one file_rewritten entry (only the first rewrite succeeded)
            self.assertEqual(len(latest["files_rewritten"]), 1)


if __name__ == "__main__":
    unittest.main()
