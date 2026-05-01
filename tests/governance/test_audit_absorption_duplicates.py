"""Fixture-level tests for ``audit_absorption_duplicates`` (GHI #376).

Each scenario is exercised against a synthetic temp tree so the test is
isolated from the live repository's brief population. The validator's
purpose is to fail closed when the same opsdev/airlineops source path
appears in OBPI briefs across different parent ADRs without a structured
``paired_with:`` waiver — the duplicate-evaluation defect this GHI tracks.
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from gzkit.governance.trust_audits import audit_absorption_duplicates


def _write_brief(
    root: Path,
    adr_dir: str,
    brief_name: str,
    obpi_id: str,
    parent: str,
    source_module: str,
    *,
    paired_with: str | None = None,
) -> Path:
    target = root / "docs" / "design" / "adr" / adr_dir / "obpis" / brief_name
    target.parent.mkdir(parents=True, exist_ok=True)
    paired_line = f"paired_with: {paired_with}\n" if paired_with else ""
    body = (
        f"---\n"
        f"id: {obpi_id}\n"
        f"parent: {parent}\n"
        f"item: 1\n"
        f"status: Completed\n"
        f"lane: heavy\n"
        f"date: 2026-04-01\n"
        f"decision: Confirm\n"
        f"{paired_line}"
        f"---\n"
        f"\n"
        f"# Title\n"
        f"\n"
        f"## Source Material\n"
        f"\n"
        f"- **opsdev:** `../airlineops/src/opsdev/lib/{source_module}.py` (100 lines)\n"
    )
    target.write_text(body, encoding="utf-8")
    return target


class CleanTreePassesTests(unittest.TestCase):
    def test_no_briefs_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            errors = audit_absorption_duplicates(root)
            self.assertEqual(errors, [])

    def test_single_absorption_brief_no_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-01-foo.md",
                obpi_id="OBPI-0.25.0-01-foo",
                parent="ADR-0.25.0-foo",
                source_module="ledger_schema",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(errors, [])

    def test_two_briefs_same_source_same_parent_adr_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-01-foo.md",
                obpi_id="OBPI-0.25.0-01-foo",
                parent="ADR-0.25.0-foo",
                source_module="ledger_schema",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-02-bar.md",
                obpi_id="OBPI-0.25.0-02-bar",
                parent="ADR-0.25.0-foo",
                source_module="ledger_schema",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(errors, [])

    def test_brief_without_source_path_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            target = root / "docs" / "design" / "adr" / "ADR-0.1.0-foo" / "obpis" / "OBPI.md"
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(
                "---\nid: OBPI-0.1.0-01-foo\nparent: ADR-0.1.0-foo\n---\n\n# No absorption here\n",
                encoding="utf-8",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(errors, [])


class CrossAdrDuplicateFiresTests(unittest.TestCase):
    def test_cross_adr_same_source_without_pairing_fires(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-29-ledger-schema.md",
                obpi_id="OBPI-0.25.0-29-ledger-schema-pattern",
                parent="ADR-0.25.0-foo",
                source_module="ledger_schema",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.26.0-bar",
                brief_name="OBPI-0.26.0-05-ledger-schema.md",
                obpi_id="OBPI-0.26.0-05-ledger-schema",
                parent="ADR-0.26.0-bar",
                source_module="ledger_schema",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(len(errors), 2)
            self.assertTrue(all(e.type == "absorption_duplicate" for e in errors))
            messages = "\n".join(e.message for e in errors)
            self.assertIn("ledger_schema", messages)
            self.assertIn("paired_with", messages)

    def test_three_cross_adr_briefs_without_pairing_fires_on_each(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-26.md",
                obpi_id="OBPI-0.25.0-26-drift-detection-pattern",
                parent="ADR-0.25.0-foo",
                source_module="drift_detection",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.26.0-bar",
                brief_name="OBPI-0.26.0-06.md",
                obpi_id="OBPI-0.26.0-06-drift-detection",
                parent="ADR-0.26.0-bar",
                source_module="drift_detection",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.27.0-baz",
                brief_name="OBPI-0.27.0-01.md",
                obpi_id="OBPI-0.27.0-01-drift-detection-redux",
                parent="ADR-0.27.0-baz",
                source_module="drift_detection",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(len(errors), 3)


class PairedWithWaivesDuplicateTests(unittest.TestCase):
    def test_paired_with_on_second_brief_waives_duplicate(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-29.md",
                obpi_id="OBPI-0.25.0-29-ledger-schema-pattern",
                parent="ADR-0.25.0-foo",
                source_module="ledger_schema",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.26.0-bar",
                brief_name="OBPI-0.26.0-05.md",
                obpi_id="OBPI-0.26.0-05-ledger-schema",
                parent="ADR-0.26.0-bar",
                source_module="ledger_schema",
                paired_with="OBPI-0.25.0-29-ledger-schema-pattern",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(errors, [])

    def test_paired_with_first_brief_waives_when_second_is_canonical(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-26.md",
                obpi_id="OBPI-0.25.0-26-drift-pattern",
                parent="ADR-0.25.0-foo",
                source_module="drift_detection",
                paired_with="OBPI-0.26.0-06-drift-detection",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.26.0-bar",
                brief_name="OBPI-0.26.0-06.md",
                obpi_id="OBPI-0.26.0-06-drift-detection",
                parent="ADR-0.26.0-bar",
                source_module="drift_detection",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(errors, [])

    def test_third_brief_arriving_unpaired_fires_only_on_itself(self) -> None:
        """When A-B are paired and C arrives unpaired, the new-entry signal is C alone.

        The pair (A, B) is an acknowledged by-reference closure. C is the new
        instance of the defect — operator must pair C with A or B, or document
        why C is a third independent absorption. The validator's job is to
        surface the unwaived addition, not to re-fire on the acknowledged pair.
        """
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            _write_brief(
                root,
                adr_dir="ADR-0.25.0-foo",
                brief_name="OBPI-0.25.0-29.md",
                obpi_id="OBPI-0.25.0-29-ledger-schema-pattern",
                parent="ADR-0.25.0-foo",
                source_module="ledger_schema",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.26.0-bar",
                brief_name="OBPI-0.26.0-05.md",
                obpi_id="OBPI-0.26.0-05-ledger-schema",
                parent="ADR-0.26.0-bar",
                source_module="ledger_schema",
                paired_with="OBPI-0.25.0-29-ledger-schema-pattern",
            )
            _write_brief(
                root,
                adr_dir="ADR-0.27.0-baz",
                brief_name="OBPI-0.27.0-01.md",
                obpi_id="OBPI-0.27.0-01-ledger-schema-redux",
                parent="ADR-0.27.0-baz",
                source_module="ledger_schema",
            )
            errors = audit_absorption_duplicates(root)
            self.assertEqual(len(errors), 1)
            self.assertIn("OBPI-0.27.0-01", errors[0].artifact)


if __name__ == "__main__":
    unittest.main()
