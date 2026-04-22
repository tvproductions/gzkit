"""Pydantic model tests for gzkit.justify.models (REQ-0.0.19-01-01, -02)."""

from __future__ import annotations

import unittest
from typing import get_args

from pydantic import ValidationError

from gzkit.justify.models import (
    AnchorKind,
    AnchorRef,
    AnchorResolutionError,
    EvidenceBundle,
)
from gzkit.traceability import covers


class TestAnchorRefModel(unittest.TestCase):
    @covers("REQ-0.0.19-01-01")
    def test_anchor_ref_is_frozen(self) -> None:
        anchor = AnchorRef(
            kind="ghi",
            identifier="GHI-232",
            title="title",
            body="body",
            labels=("defect",),
            author="octocat",
        )
        with self.assertRaises(ValidationError):
            anchor.identifier = "GHI-999"  # type: ignore[misc]

    @covers("REQ-0.0.19-01-01")
    def test_anchor_ref_forbids_extra_fields(self) -> None:
        with self.assertRaises(ValidationError):
            AnchorRef(kind="ghi", identifier="GHI-1", mystery="value")  # type: ignore[call-arg]

    @covers("REQ-0.0.19-01-02")
    def test_anchor_rejects_adr_kind(self) -> None:
        with self.assertRaises(ValidationError) as ctx:
            AnchorRef(kind="adr", identifier="ADR-0.0.19")  # type: ignore[arg-type]
        self.assertIn("adr", str(ctx.exception).lower())

    @covers("REQ-0.0.19-01-02")
    def test_anchor_kind_literal_values(self) -> None:
        self.assertEqual(set(get_args(AnchorKind)), {"ghi", "obpi", "draft"})


class TestEvidenceBundleModel(unittest.TestCase):
    @covers("REQ-0.0.19-01-01")
    def test_evidence_bundle_frozen_and_forbid_extra(self) -> None:
        anchor = AnchorRef(kind="draft", draft_text="hello", draft_slug="refactor-parser")
        bundle = EvidenceBundle(
            anchor=anchor,
            matching_rules=(),
            ledger_events=(),
            recent_commits=(),
            related_anchors=(),
            taxonomy_reference="docs/governance/model-regression-taxonomy.md",
            warnings=(),
        )
        with self.assertRaises(ValidationError):
            bundle.taxonomy_reference = "other.md"  # type: ignore[misc]
        with self.assertRaises(ValidationError):
            EvidenceBundle(  # type: ignore[call-arg]
                anchor=anchor,
                matching_rules=(),
                ledger_events=(),
                recent_commits=(),
                related_anchors=(),
                taxonomy_reference="docs/governance/model-regression-taxonomy.md",
                warnings=(),
                surprise="field",
            )


class TestAnchorResolutionError(unittest.TestCase):
    @covers("REQ-0.0.19-01-02")
    def test_is_a_plain_exception(self) -> None:
        exc = AnchorResolutionError("boom")
        self.assertIsInstance(exc, Exception)
        self.assertEqual(str(exc), "boom")


class TestPublicApiExport(unittest.TestCase):
    @covers("REQ-0.0.19-01-11")
    def test_public_api_export_surface(self) -> None:
        import gzkit.justify as pkg

        expected = {
            "AnchorKind",
            "AnchorRef",
            "AnchorResolutionError",
            "EvidenceBundle",
            "gather_evidence",
            "resolve_anchor",
        }
        self.assertEqual(set(pkg.__all__), expected)

        namespace: dict[str, object] = {}
        exec("from gzkit.justify import *", namespace)  # noqa: S102
        exported = {k for k in namespace if not k.startswith("__")}
        self.assertEqual(exported, expected)

    @covers("REQ-0.0.19-01-11")
    def test_internal_models_not_re_exported(self) -> None:
        import gzkit.justify as pkg

        for name in ("RuleCitation", "CommitRef", "LedgerEvent"):
            self.assertNotIn(name, pkg.__all__, f"{name} should not be in public __all__")


class TestSuiteHygiene(unittest.TestCase):
    """REQ-12 meta-check: the tests in this suite observe the unit-tier contract."""

    @covers("REQ-0.0.19-01-12")
    def test_justify_tests_use_tempfile_never_live_ledger(self) -> None:
        """Each test module that touches the filesystem does so via tempfile."""
        import pathlib
        import re

        tests_dir = pathlib.Path(__file__).parent
        live_ledger_import = re.compile(r"^from\s+gzkit\.ledger\s+import\b", re.MULTILINE)
        offenders: list[str] = []
        for test_file in tests_dir.glob("test_*.py"):
            source = test_file.read_text(encoding="utf-8")
            touches_fs = any(token in source for token in (".write_text(", ".mkdir(", "Path.cwd("))
            if touches_fs and "tempfile.TemporaryDirectory" not in source:
                offenders.append(test_file.name)
            self.assertIsNone(
                live_ledger_import.search(source),
                f"{test_file.name} imports the live ledger module",
            )
        self.assertEqual(
            offenders,
            [],
            f"justify tests must use tempfile.TemporaryDirectory: {offenders}",
        )


if __name__ == "__main__":
    unittest.main()
