"""Tests for the canonical status-vocabulary mapping (ADR-0.0.16 OBPI-05).

@covers ADR-0.0.16-frontmatter-ledger-coherence-guard
@covers OBPI-0.0.16-05-status-vocab-mapping
"""

from __future__ import annotations

import importlib
import unittest

from gzkit.traceability import covers

BRIEF_FIVE_TERMS: frozenset[str] = frozenset(
    {
        "Draft",
        "Proposed",
        "Pending",
        "Validated",
        "Completed",
    }
)

EXTRA_OBSERVED_TERMS: frozenset[str] = frozenset(
    {
        "Accepted",
        "archived",
        "Pending-Attestation",
        "Pool",
        "Promoted",
        "Superseded",
    }
)


class StatusVocabMappingTests(unittest.TestCase):
    """Acceptance tests for `STATUS_VOCAB_MAPPING` and `canonicalize_status`."""

    @covers("REQ-0.0.16-05-01")
    def test_mapping_importable_without_side_effects(self) -> None:
        module = importlib.import_module("gzkit.governance.status_vocab")
        importlib.reload(module)

        self.assertTrue(hasattr(module, "STATUS_VOCAB_MAPPING"))
        self.assertGreater(len(module.STATUS_VOCAB_MAPPING), 0)

    @covers("REQ-0.0.16-05-02")
    def test_mapping_includes_brief_five_terms(self) -> None:
        from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING

        missing = BRIEF_FIVE_TERMS - set(STATUS_VOCAB_MAPPING)
        self.assertFalse(
            missing,
            f"mapping is missing brief-mandated terms: {sorted(missing)}",
        )

    @covers("REQ-0.0.16-05-02")
    def test_mapping_includes_all_observed_drift_terms(self) -> None:
        from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING

        missing = EXTRA_OBSERVED_TERMS - set(STATUS_VOCAB_MAPPING)
        self.assertFalse(
            missing,
            f"mapping is missing OBPI-01 drift-evidence terms: {sorted(missing)}",
        )

    @covers("REQ-0.0.16-05-03")
    def test_every_canonical_value_is_in_ledger_set(self) -> None:
        from gzkit.governance.status_vocab import (
            CANONICAL_LEDGER_TERMS,
            STATUS_VOCAB_MAPPING,
        )
        from gzkit.ledger import OBPI_RUNTIME_STATES

        adr_lifecycle_terms = {"pending", "validated", "completed", "abandoned"}
        ledger_union = set(OBPI_RUNTIME_STATES) | adr_lifecycle_terms

        for frontmatter_term, canonical_term in STATUS_VOCAB_MAPPING.items():
            with self.subTest(frontmatter_term=frontmatter_term):
                self.assertIn(
                    canonical_term,
                    CANONICAL_LEDGER_TERMS,
                    f"{frontmatter_term!r} maps to {canonical_term!r} which is "
                    "not in CANONICAL_LEDGER_TERMS",
                )
                self.assertIn(
                    canonical_term,
                    ledger_union,
                    f"{frontmatter_term!r} maps to {canonical_term!r} which is "
                    "not a term the ledger state machine accepts",
                )

    @covers("REQ-0.0.16-05-05")
    def test_mapping_is_immutable(self) -> None:
        from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING

        with self.assertRaises(TypeError):
            STATUS_VOCAB_MAPPING["Draft"] = "x"  # type: ignore[index]

    @covers("REQ-0.0.16-05-01")
    def test_canonicalize_status_case_insensitive(self) -> None:
        from gzkit.governance.status_vocab import canonicalize_status

        self.assertEqual(canonicalize_status("draft"), "pending")
        self.assertEqual(canonicalize_status("DRAFT"), "pending")
        self.assertEqual(canonicalize_status("Draft"), "pending")
        self.assertEqual(canonicalize_status("Pending-Attestation"), "completed")
        self.assertEqual(canonicalize_status("pending-attestation"), "completed")

    @covers("REQ-0.0.16-05-06")
    def test_canonicalize_status_unknown_returns_none(self) -> None:
        from gzkit.governance.status_vocab import canonicalize_status

        self.assertIsNone(canonicalize_status("XYZ"))
        self.assertIsNone(canonicalize_status(""))

    @covers("REQ-0.0.16-05-04")
    def test_state_doctrine_contains_addendum(self) -> None:
        from pathlib import Path

        from gzkit.governance.status_vocab import STATUS_VOCAB_MAPPING

        doctrine = Path(__file__).resolve().parents[2] / "docs" / "governance" / "state-doctrine.md"
        content = doctrine.read_text(encoding="utf-8")

        self.assertIn(
            "Canonical Status Vocabulary (ADR-0.0.16 addendum)",
            content,
            "state-doctrine.md is missing the ADR-0.0.16 addendum section",
        )
        self.assertIn("ADR-0.0.16", content)
        for frontmatter_term in STATUS_VOCAB_MAPPING:
            self.assertIn(
                frontmatter_term,
                content,
                f"addendum table omits frontmatter term {frontmatter_term!r}",
            )


if __name__ == "__main__":
    unittest.main()
