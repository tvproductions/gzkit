"""Tests for ADR status index regenerator and freshness audit (GHI #322).

Asserts the semantic the rule cares about — *the committed index agrees
with on-disk truth* — not byte-level table shape. Per
`.gzkit/rules/tests.md` § Tests assert semantics, not strings.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.adr_status_index import (
    DriftEntry,
    collect_adr_rows,
    compute_drift,
    regenerate_adr_status_md,
)
from gzkit.governance.trust_audits import audit_adr_status_fresh


def _write_adr(
    root: Path,
    subdir: str,
    adr_id: str,
    *,
    title: str,
    kind: str,
    lane: str,
    status: str,
    date: str,
) -> Path:
    adr_dir = root / "docs" / "design" / "adr" / subdir / adr_id
    adr_dir.mkdir(parents=True, exist_ok=True)
    adr_file = adr_dir / f"{adr_id}.md"
    semver = adr_id.removeprefix("ADR-").split("-", 1)[0]
    adr_file.write_text(
        f"---\n"
        f"id: {adr_id}\n"
        f"status: {status}\n"
        f"kind: {kind}\n"
        f"semver: {semver}\n"
        f"lane: {lane}\n"
        f"date: {date}\n"
        f"---\n\n"
        f"# {adr_id}: {title}\n\n"
        f"## Intent\n\nBody.\n",
        encoding="utf-8",
    )
    return adr_file


def _write_index(root: Path, body: str) -> Path:
    target = root / "docs" / "governance" / "GovZero" / "adr-status.md"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(body, encoding="utf-8")
    return target


class CollectAdrRowsTests(unittest.TestCase):
    def test_walks_foundation_and_pre_release_subdirs(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "foundation",
                "ADR-0.0.5-evaluation-infrastructure",
                title="Evaluation Infrastructure",
                kind="foundation",
                lane="lite",
                status="Validated",
                date="2026-03-01",
            )
            _write_adr(
                root,
                "pre-release",
                "ADR-0.10.0-obpi-runtime-surface",
                title="OBPI Runtime Surfaces",
                kind="feature",
                lane="heavy",
                status="Validated",
                date="2026-03-09",
            )
            rows = collect_adr_rows(root)
            adr_ids = [r.adr_id for r in rows]
            self.assertEqual(
                adr_ids,
                [
                    "ADR-0.0.5-evaluation-infrastructure",
                    "ADR-0.10.0-obpi-runtime-surface",
                ],
            )
            # Foundation sorts before feature regardless of patch order.
            self.assertEqual(rows[0].kind, "foundation")
            self.assertEqual(rows[1].kind, "feature")


class RegenerateAdrStatusMdTests(unittest.TestCase):
    def test_regenerator_writes_every_on_disk_adr(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "foundation",
                "ADR-0.0.23-agent-failure-mode-taxonomy",
                title="Agent Failure-Mode Taxonomy",
                kind="foundation",
                lane="heavy",
                status="Draft",
                date="2026-04-25",
            )
            content = regenerate_adr_status_md(root, write=True, regen_date="2026-04-26")
            target = root / "docs" / "governance" / "GovZero" / "adr-status.md"
            self.assertTrue(target.is_file())
            written = target.read_text(encoding="utf-8")
            self.assertEqual(content, written)
            # Semantic claim: every on-disk ADR id appears as a row.
            self.assertIn("ADR-0.0.23-agent-failure-mode-taxonomy", written)
            self.assertIn("Agent Failure-Mode Taxonomy", written)


class ComputeDriftTests(unittest.TestCase):
    def test_fresh_index_has_no_drift(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "foundation",
                "ADR-0.0.5-evaluation-infrastructure",
                title="Evaluation Infrastructure",
                kind="foundation",
                lane="lite",
                status="Validated",
                date="2026-03-01",
            )
            regenerate_adr_status_md(root, write=True, regen_date="2026-04-26")
            self.assertEqual(compute_drift(root), [])

    def test_missing_adr_row_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "foundation",
                "ADR-0.0.5-evaluation-infrastructure",
                title="Evaluation Infrastructure",
                kind="foundation",
                lane="lite",
                status="Validated",
                date="2026-03-01",
            )
            regenerate_adr_status_md(root, write=True, regen_date="2026-04-26")
            # A new ADR appears on disk; the committed index forgets it.
            _write_adr(
                root,
                "foundation",
                "ADR-0.0.27-exemplar-corpus-doctrine",
                title="Exemplar-Corpus Doctrine",
                kind="foundation",
                lane="heavy",
                status="Draft",
                date="2026-04-25",
            )
            drift = compute_drift(root)
            self.assertTrue(
                any(
                    d.kind == "missing" and d.adr_id == "ADR-0.0.27-exemplar-corpus-doctrine"
                    for d in drift
                ),
                f"expected missing-row detection, got {drift!r}",
            )

    def test_field_drift_in_title_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            adr_file = _write_adr(
                root,
                "foundation",
                "ADR-0.0.23-agent-failure-mode-taxonomy",
                title="Agent Failure-Mode Taxonomy",
                kind="foundation",
                lane="heavy",
                status="Draft",
                date="2026-04-25",
            )
            regenerate_adr_status_md(root, write=True, regen_date="2026-04-26")
            # Hand-edit the on-disk title; index now lies about reality.
            content = adr_file.read_text(encoding="utf-8")
            adr_file.write_text(
                content.replace(
                    "Agent Failure-Mode Taxonomy",
                    "Hexagonal Architecture for Dataset Warehouse Pipeline",
                ),
                encoding="utf-8",
            )
            drift = compute_drift(root)
            self.assertTrue(
                any(d.kind == "field" and "title" in d.detail for d in drift),
                f"expected title field-drift, got {drift!r}",
            )

    def test_missing_index_file_is_detected(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "foundation",
                "ADR-0.0.5-evaluation-infrastructure",
                title="Evaluation Infrastructure",
                kind="foundation",
                lane="lite",
                status="Validated",
                date="2026-03-01",
            )
            drift = compute_drift(root)
            self.assertEqual(
                drift,
                [
                    DriftEntry(
                        "(file)",
                        "missing",
                        "docs/governance/GovZero/adr-status.md missing",
                    )
                ],
            )


class AuditAdrStatusFreshTests(unittest.TestCase):
    def test_clean_repo_returns_no_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_adr(
                root,
                "foundation",
                "ADR-0.0.5-evaluation-infrastructure",
                title="Evaluation Infrastructure",
                kind="foundation",
                lane="lite",
                status="Validated",
                date="2026-03-01",
            )
            regenerate_adr_status_md(root, write=True, regen_date="2026-04-26")
            self.assertEqual(audit_adr_status_fresh(root), [])

    def test_drifted_index_emits_validation_errors(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            fab_path = "design/adr/foundation/ADR-0.0.99-fabricated/ADR-0.0.99-fabricated.md"
            row = (
                f"| [ADR-0.0.99-fabricated](../../{fab_path}) | "
                "Fabricated | foundation | lite | Validated | 2026-01-01 | "
                f"`{fab_path}` |"
            )
            _write_index(
                root,
                "# ADR Status Table\n\n"
                "| ID | Title | Kind | Lane | Status | Date | Path |\n"
                "|---|---|---|---|---|---|---|\n"
                f"{row}\n",
            )
            errors = audit_adr_status_fresh(root)
            self.assertGreater(len(errors), 0)
            self.assertTrue(
                any(e.type == "adr_status_fresh" for e in errors),
                f"expected adr_status_fresh validation errors, got {errors!r}",
            )


if __name__ == "__main__":
    unittest.main()
