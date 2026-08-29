"""REQ-derived assertions for OBPI-0.0.27-05 citation contract.

Each test decorates a single REQ from the OBPI brief at
``docs/design/adr/foundation/ADR-0.0.27-exemplar-corpus-doctrine/obpis/
OBPI-0.0.27-05-citation-contract.md``.  Test fixtures are tempfile-backed
per the brief's TDD-hygiene REQ; no live filesystem mutation under
``.gzkit/`` or ``docs/`` is performed by the test surface.
"""

from __future__ import annotations

import json
import re
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.complexity.citation import Citation, is_portable, parse_citation
from gzkit.traceability import covers
from tests.vendor_surfaces import rule_mirror_paths

CANONICAL_FORM = (
    "docs/governance/complexity/distilled-characteristics-2026-05-04.md "
    "§ radon-cc (corpus revision 1)"
)


class TestCitationModelShape(unittest.TestCase):
    """``Citation`` is the frozen, ``extra='forbid'`` tuple consumed by OBPI-07."""

    @covers("REQ-0.0.27-05-03")
    def test_canonical_construction_returns_frozen_model(self) -> None:
        citation = Citation(
            distilled_characteristics_path=(
                "docs/governance/complexity/distilled-characteristics-2026-05-04.md"
            ),
            section_anchor="radon-cc",
            corpus_revision=1,
        )
        self.assertEqual(citation.corpus_revision, 1)
        with self.assertRaises(ValidationError):
            citation.corpus_revision = 2  # type: ignore  # frozen


class TestParseCitationCanonicalForm(unittest.TestCase):
    """``parse_citation`` accepts the canonical ``§``-delimited tuple shape."""

    @covers("REQ-0.0.27-05-03")
    def test_accepts_canonical_form(self) -> None:
        citation = parse_citation(CANONICAL_FORM)
        self.assertEqual(
            citation.distilled_characteristics_path,
            "docs/governance/complexity/distilled-characteristics-2026-05-04.md",
        )
        self.assertEqual(citation.section_anchor, "radon-cc")
        self.assertEqual(citation.corpus_revision, 1)


class TestParseCitationRejectsIncomplete(unittest.TestCase):
    """``parse_citation`` raises ValidationError when any of the three fields is missing."""

    @covers("REQ-0.0.27-05-04")
    def test_rejects_missing_path(self) -> None:
        with self.assertRaises(ValidationError):
            parse_citation("§ radon-cc (corpus revision 1)")

    @covers("REQ-0.0.27-05-04")
    def test_rejects_missing_anchor(self) -> None:
        with self.assertRaises(ValidationError):
            parse_citation(
                "docs/governance/complexity/distilled-characteristics-2026-05-04.md "
                "(corpus revision 1)"
            )

    @covers("REQ-0.0.27-05-04")
    def test_rejects_missing_revision(self) -> None:
        with self.assertRaises(ValidationError):
            parse_citation(
                "docs/governance/complexity/distilled-characteristics-2026-05-04.md § radon-cc"
            )


class TestRuleCitationContractSection(unittest.TestCase):
    """The rule body formalizes tuple, percentile + absolute pairing, and refresh portability."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.rule_path = Path(__file__).resolve().parents[2] / ".gzkit/rules/complexity-doctrine.md"
        cls.rule_body = cls.rule_path.read_text(encoding="utf-8")

    @covers("REQ-0.0.27-05-01")
    def test_canonical_tuple_named(self) -> None:
        # The rule must explicitly name the three-field tuple.
        self.assertIn("distilled_characteristics_path", self.rule_body)
        self.assertIn("section_anchor", self.rule_body)
        self.assertIn("corpus_revision", self.rule_body)
        # Raw distributions and the corpus registry must be explicitly forbidden.
        self.assertRegex(
            self.rule_body,
            r"(?is)NOT\b.*?(raw distributions|exemplar_corpus\.json)",
        )

    @covers("REQ-0.0.27-05-02")
    def test_percentile_absolute_pairing_required(self) -> None:
        # Both forms must be required for every cited boundary.
        self.assertRegex(self.rule_body, r"(?i)percentile.*?absolute")
        # Worked example must reference the landed radon_cc p90 boundary.
        self.assertRegex(self.rule_body, r"p90\s*=\s*7")

    @covers("REQ-0.0.27-05-03")
    def test_refresh_portability_rule_codified(self) -> None:
        # Portability behavior names supported window and OBPI-07's flag-not-rewrite verdict.
        self.assertRegex(self.rule_body, r"(?i)supported window")
        self.assertRegex(self.rule_body, r"(?i)flag")
        self.assertIn("OBPI-0.0.27-07", self.rule_body)


class TestRuleVersionConsistency(unittest.TestCase):
    """The body-level marker and visible block-quote both bump to 0.2.0 together."""

    @covers("REQ-0.0.27-05-06")
    def test_body_marker_and_block_quote_agree(self) -> None:
        rule_path = Path(__file__).resolve().parents[2] / ".gzkit/rules/complexity-doctrine.md"
        rule_body = rule_path.read_text(encoding="utf-8")
        body_match = re.search(r"<!--\s*rule-version:\s*([0-9.]+)\s*-->", rule_body)
        self.assertIsNotNone(body_match, "body-level rule-version marker missing")
        block_quote_match = re.search(
            r">\s*\*\*Rule version:\*\*\s*`([0-9.]+)`",
            rule_body,
        )
        self.assertIsNotNone(block_quote_match, "visible rule-version block quote missing")
        body_version = body_match.group(1)
        quote_version = block_quote_match.group(1)
        self.assertEqual(body_version, quote_version)
        self.assertEqual(body_version, "0.3.1")


class TestSchemaShape(unittest.TestCase):
    """The JSON Schema mirrors the Pydantic model under ``additionalProperties: false``."""

    @covers("REQ-0.0.27-05-05")
    def test_schema_file_present_and_constrains_three_fields(self) -> None:
        schema_path = (
            Path(__file__).resolve().parents[2] / "src/gzkit/schemas/complexity_citation.json"
        )
        self.assertTrue(schema_path.exists(), f"missing: {schema_path.as_posix()}")
        schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self.assertEqual(schema.get("additionalProperties"), False)
        required = set(schema.get("required", []))
        self.assertEqual(
            required,
            {"distilled_characteristics_path", "section_anchor", "corpus_revision"},
        )
        # Path constraint must reference docs/governance/complexity/.
        path_pattern = schema["properties"]["distilled_characteristics_path"]["pattern"]
        self.assertIn("docs/governance/complexity/", path_pattern)
        # Revision must be a positive integer.
        revision_property = schema["properties"]["corpus_revision"]
        self.assertEqual(revision_property["type"], "integer")
        self.assertGreaterEqual(revision_property["exclusiveMinimum"], 0)


class TestPortabilityWindow(unittest.TestCase):
    """``is_portable`` flags revision drift past the supported window."""

    @covers("REQ-0.0.27-05-05")
    def test_within_window_returns_true(self) -> None:
        citation = parse_citation(CANONICAL_FORM)
        # default window=2 ⇒ revision 1 portable at current 1 and 2.
        self.assertTrue(is_portable(citation, current_revision=1))
        self.assertTrue(is_portable(citation, current_revision=2))

    @covers("REQ-0.0.27-05-05")
    def test_outside_window_returns_false(self) -> None:
        citation = parse_citation(CANONICAL_FORM)
        # default window=2 ⇒ revision 1 non-portable at current 3 onward.
        self.assertFalse(is_portable(citation, current_revision=3))
        self.assertFalse(is_portable(citation, current_revision=10))


class TestVendorMirrorIdempotence(unittest.TestCase):
    """``gz agent sync control-surfaces`` propagates canonical rule to mirrors.

    After sync, every vendor mirror MUST carry the canonical rule body so the
    next sync run produces no further drift on this surface.
    """

    @covers("REQ-0.0.27-05-07")
    def test_canonical_rule_body_present_in_each_vendor_mirror(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        canonical = (repo_root / ".gzkit/rules/complexity-doctrine.md").read_text(encoding="utf-8")
        # The 0.3.1 rule-version marker is the load-bearing canonical signal —
        # every mirror MUST reflect the bumped version.
        self.assertIn("<!-- rule-version: 0.3.1 -->", canonical)
        # The formalized tuple definition is the substantive payload of this OBPI;
        # every mirror MUST carry it in body form (not just the marker).
        canonical_marker = "(distilled_characteristics_path, section_anchor, corpus_revision)"
        self.assertIn(canonical_marker, canonical)

        # Per .gzkit/rules/skill-surface-sync.md § Surface layout, rule
        # mirrors land at .claude/rules/ (kebab-case) and
        # .github/instructions/ (snake-case + .instructions.md suffix).
        mirrors = rule_mirror_paths("complexity_doctrine")
        for mirror_path in mirrors:
            with self.subTest(mirror=mirror_path.relative_to(repo_root).as_posix()):
                self.assertTrue(
                    mirror_path.exists(),
                    f"vendor mirror missing: {mirror_path.as_posix()}",
                )
                mirror_body = mirror_path.read_text(encoding="utf-8")
                self.assertIn("<!-- rule-version: 0.3.1 -->", mirror_body)
                self.assertIn(canonical_marker, mirror_body)


class TestNoOperatorPiiInCitationSurfaces(unittest.TestCase):
    """No operator personal email tokens appear in OBPI-05's authored surfaces.

    REQ-09 (no operator PII) is an operational requirement on the
    implementation process per the brief's Requirements section; it does
    not appear in Acceptance Criteria, so this test is intentionally not
    decorated with ``@covers``.  It is hygiene defense-in-depth against the
    AGENTS.md § Local Agent Rules PII-leak class.
    """

    def test_personal_email_absent_from_authored_surfaces(self) -> None:
        repo_root = Path(__file__).resolve().parents[2]
        # Construct the shapes from fragments so this test file itself does
        # not embed the operator's personal-email local-part or domain in
        # contiguous form (which would self-flag the assertion below).
        personal_email_local_part = "ahui" + "manu"
        personal_email_domain = "gmail" + ".com"
        targets = [
            repo_root / ".gzkit/rules/complexity-doctrine.md",
            repo_root / "src/gzkit/complexity/citation.py",
            repo_root / "src/gzkit/schemas/complexity_citation.json",
            repo_root / "tests/complexity/test_citation.py",
        ]
        for path in targets:
            with self.subTest(file=path.relative_to(repo_root).as_posix()):
                body = path.read_text(encoding="utf-8")
                self.assertFalse(
                    personal_email_local_part in body and personal_email_domain in body,
                    f"operator PII (personal email shape) detected in {path.as_posix()}",
                )


if __name__ == "__main__":
    unittest.main()
