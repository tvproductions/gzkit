"""Tests for handoff document validation.

@covers ADR-0.0.25 (OBPI-0.0.25-06)
@covers ADR-0.25.0-core-infrastructure-pattern-absorption
@covers OBPI-0.25.0-32-handoff-validation-pattern
"""

from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from pydantic import ValidationError

from gzkit.handoff_validation import (
    HANDOFF_SCHEMA_VERSION,
    REQUIRED_SECTIONS,
    HandoffFrontmatter,
    HandoffValidationError,
    parse_frontmatter,
    validate_handoff_document,
    validate_no_placeholders,
    validate_no_secrets,
    validate_referenced_files,
    validate_sections_present,
)
from gzkit.traceability import covers

# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------


def _valid_frontmatter_dict(**overrides: object) -> dict[str, object]:
    """Return a valid CREATE-mode HandoffFrontmatter payload."""
    base: dict[str, object] = {
        "mode": "CREATE",
        "adr_id": "ADR-0.25.0",
        "branch": "feature/handoff",
        "timestamp": "2026-04-14T12:00:00",
        "agent": "claude-code",
        "obpi_id": "OBPI-0.25.0-32",
        "session_id": None,
        "continues_from": None,
    }
    base.update(overrides)
    return base


def _clean_handoff_doc(frontmatter_yaml: str = "") -> str:
    """Return a minimal handoff document with all required sections and no violations."""
    if not frontmatter_yaml:
        frontmatter_yaml = (
            "mode: CREATE\n"
            "adr_id: ADR-0.25.0\n"
            "branch: feature/handoff\n"
            "timestamp: '2026-04-14T12:00:00'\n"
            "agent: claude-code\n"
        )
    body_sections = "\n\n".join(
        f"## {section}\n\nContent for section." for section in REQUIRED_SECTIONS
    )
    return f"---\n{frontmatter_yaml}---\n\n{body_sections}\n"


# ---------------------------------------------------------------------------
# HandoffFrontmatter (Pydantic model) — REQ-0.25.0-32-03
# ---------------------------------------------------------------------------


class TestHandoffFrontmatter(unittest.TestCase):
    """@covers REQ-0.25.0-32-03"""

    @covers("REQ-0.25.0-32-03")
    def test_valid_create_frontmatter_parses(self) -> None:
        fm = HandoffFrontmatter(**_valid_frontmatter_dict())
        self.assertEqual(fm.mode, "CREATE")
        self.assertEqual(fm.adr_id, "ADR-0.25.0")
        self.assertEqual(fm.obpi_id, "OBPI-0.25.0-32")

    @covers("REQ-0.25.0-32-03")
    def test_valid_resume_frontmatter_parses(self) -> None:
        fm = HandoffFrontmatter(**_valid_frontmatter_dict(mode="RESUME"))
        self.assertEqual(fm.mode, "RESUME")

    @covers("REQ-0.25.0-32-03")
    def test_invalid_mode_raises(self) -> None:
        with self.assertRaises(ValidationError):
            HandoffFrontmatter(**_valid_frontmatter_dict(mode="INVALID"))

    @covers("REQ-0.25.0-32-03")
    def test_invalid_adr_id_format_raises(self) -> None:
        with self.assertRaisesRegex(ValidationError, "Invalid ADR ID format"):
            HandoffFrontmatter(**_valid_frontmatter_dict(adr_id="not-an-adr"))

    @covers("REQ-0.25.0-32-03")
    def test_valid_adr_id_passes(self) -> None:
        fm = HandoffFrontmatter(**_valid_frontmatter_dict(adr_id="ADR-1.2.3"))
        self.assertEqual(fm.adr_id, "ADR-1.2.3")

    @covers("REQ-0.25.0-32-03")
    def test_invalid_obpi_id_format_raises(self) -> None:
        with self.assertRaisesRegex(ValidationError, "Invalid OBPI ID format"):
            HandoffFrontmatter(**_valid_frontmatter_dict(obpi_id="OBPI-1.2.3"))

    @covers("REQ-0.25.0-32-03")
    def test_valid_obpi_id_passes(self) -> None:
        fm = HandoffFrontmatter(**_valid_frontmatter_dict(obpi_id="OBPI-0.25.0-32"))
        self.assertEqual(fm.obpi_id, "OBPI-0.25.0-32")

    @covers("REQ-0.25.0-32-03")
    def test_none_obpi_id_passes(self) -> None:
        fm = HandoffFrontmatter(**_valid_frontmatter_dict(obpi_id=None))
        self.assertIsNone(fm.obpi_id)

    @covers("REQ-0.25.0-32-03")
    def test_invalid_timestamp_raises(self) -> None:
        with self.assertRaisesRegex(ValidationError, "Invalid ISO 8601"):
            HandoffFrontmatter(**_valid_frontmatter_dict(timestamp="not-a-date"))

    @covers("REQ-0.25.0-32-03")
    def test_valid_timestamp_passes(self) -> None:
        fm = HandoffFrontmatter(**_valid_frontmatter_dict(timestamp="2026-04-14T12:00:00"))
        self.assertEqual(fm.timestamp, "2026-04-14T12:00:00")

    @covers("REQ-0.25.0-32-03")
    def test_extra_field_rejected(self) -> None:
        payload = _valid_frontmatter_dict()
        payload["unknown_field"] = "should not be allowed"
        with self.assertRaises(ValidationError):
            HandoffFrontmatter(**payload)

    @covers("REQ-0.25.0-32-03")
    def test_missing_required_field_rejected(self) -> None:
        payload = _valid_frontmatter_dict()
        del payload["branch"]
        with self.assertRaises(ValidationError):
            HandoffFrontmatter(**payload)

    @covers("REQ-0.25.0-32-03")
    def test_model_is_frozen(self) -> None:
        fm = HandoffFrontmatter(**_valid_frontmatter_dict())
        with self.assertRaises(ValidationError):
            fm.mode = "RESUME"  # type: ignore[misc]

    @covers("REQ-0.25.0-32-03")
    def test_schema_version_constant(self) -> None:
        self.assertEqual(HANDOFF_SCHEMA_VERSION, "govzero.handoff.v1")


# ---------------------------------------------------------------------------
# parse_frontmatter — REQ-0.25.0-32-03
# ---------------------------------------------------------------------------


class TestParseFrontmatter(unittest.TestCase):
    """@covers REQ-0.25.0-32-03"""

    @covers("REQ-0.25.0-32-03")
    def test_parse_valid_frontmatter(self) -> None:
        content = "---\nkey: value\nother: 42\n---\nbody\n"
        result = parse_frontmatter(content)
        self.assertEqual(result, {"key": "value", "other": 42})

    @covers("REQ-0.25.0-32-03")
    def test_parse_missing_opening_delimiter_raises(self) -> None:
        with self.assertRaisesRegex(HandoffValidationError, "Missing opening"):
            parse_frontmatter("key: value\n---\nbody\n")

    @covers("REQ-0.25.0-32-03")
    def test_parse_missing_closing_delimiter_raises(self) -> None:
        with self.assertRaisesRegex(HandoffValidationError, "Missing closing"):
            parse_frontmatter("---\nkey: value\nno closing\n")

    @covers("REQ-0.25.0-32-03")
    def test_parse_invalid_yaml_raises(self) -> None:
        with self.assertRaisesRegex(HandoffValidationError, "Invalid YAML"):
            parse_frontmatter("---\nkey: [unclosed\n---\nbody\n")

    @covers("REQ-0.25.0-32-03")
    def test_parse_non_mapping_body_raises(self) -> None:
        with self.assertRaisesRegex(HandoffValidationError, "must be a YAML mapping"):
            parse_frontmatter("---\n- one\n- two\n---\nbody\n")

    @covers("REQ-0.25.0-32-03")
    def test_parse_crlf_content(self) -> None:
        content = "---\r\nkey: value\r\n---\r\nbody\r\n"
        result = parse_frontmatter(content)
        self.assertEqual(result, {"key": "value"})


# ---------------------------------------------------------------------------
# validate_no_placeholders — REQ-0.25.0-32-03
# ---------------------------------------------------------------------------


class TestValidatePlaceholders(unittest.TestCase):
    """@covers REQ-0.25.0-32-03"""

    @covers("REQ-0.25.0-32-03")
    def test_clean_body_returns_empty(self) -> None:
        doc = "---\nkey: value\n---\n\nClean body with no markers.\n"
        self.assertEqual(validate_no_placeholders(doc), [])

    @covers("REQ-0.25.0-32-03")
    def test_detects_placeholder_tokens(self) -> None:
        cases = [
            ("TBD", "TBD in the body"),
            ("TODO", "TODO: finish this"),
            ("FIXME", "FIXME later"),
            ("PLACEHOLDER", "PLACEHOLDER value"),
            ("XXX", "XXX needs work"),
            ("CHANGEME", "CHANGEME"),
        ]
        for label, snippet in cases:
            with self.subTest(token=label):
                doc = f"---\nkey: value\n---\n\n{snippet}\n"
                violations = validate_no_placeholders(doc)
                self.assertTrue(
                    violations, f"{label} should have been flagged but got {violations!r}"
                )

    @covers("REQ-0.25.0-32-03")
    def test_detects_standalone_ellipsis(self) -> None:
        doc = "---\nkey: value\n---\n\nBefore\n ... \nAfter\n"
        self.assertTrue(validate_no_placeholders(doc))

    @covers("REQ-0.25.0-32-03")
    def test_case_insensitive(self) -> None:
        doc = "---\nkey: value\n---\n\ntodo item pending\n"
        self.assertTrue(validate_no_placeholders(doc))

    @covers("REQ-0.25.0-32-03")
    def test_ignores_placeholders_in_frontmatter(self) -> None:
        doc = "---\nnote: TODO defer\n---\n\nClean body.\n"
        self.assertEqual(validate_no_placeholders(doc), [])

    @covers("REQ-0.25.0-32-03")
    def test_ignores_placeholders_in_html_comments(self) -> None:
        doc = "---\nkey: value\n---\n\n<!-- TODO hidden comment -->\n\nClean visible body.\n"
        self.assertEqual(validate_no_placeholders(doc), [])

    @covers("REQ-0.25.0-32-03")
    def test_word_boundary_avoids_false_positives(self) -> None:
        doc = "---\nkey: value\n---\n\nmethodology and inTODOctrination.\n"
        self.assertEqual(validate_no_placeholders(doc), [])


# ---------------------------------------------------------------------------
# validate_no_secrets — REQ-0.25.0-32-03
# ---------------------------------------------------------------------------


class TestValidateSecrets(unittest.TestCase):
    """@covers REQ-0.25.0-32-03"""

    @covers("REQ-0.25.0-32-03")
    def test_clean_content_returns_empty(self) -> None:
        self.assertEqual(validate_no_secrets("clean body with no secrets"), [])

    @covers("REQ-0.25.0-32-03")
    def test_detects_assignment_patterns(self) -> None:
        cases = [
            "password=hunter2",
            "secret=foobar",
            "token=abcd",
            "api_key=xyz",
        ]
        for snippet in cases:
            with self.subTest(snippet=snippet):
                self.assertTrue(validate_no_secrets(snippet))

    @covers("REQ-0.25.0-32-03")
    def test_detects_bearer_token(self) -> None:
        self.assertTrue(validate_no_secrets("Authorization: Bearer abc123xyz"))

    @covers("REQ-0.25.0-32-03")
    def test_detects_private_key(self) -> None:
        self.assertTrue(validate_no_secrets("-----BEGIN PRIVATE KEY-----"))

    @covers("REQ-0.25.0-32-03")
    def test_detects_openai_key(self) -> None:
        self.assertTrue(validate_no_secrets("sk-ABCDEFGHIJKLMNOPQRSTUVWXYZ01"))

    @covers("REQ-0.25.0-32-03")
    def test_detects_github_pat(self) -> None:
        self.assertTrue(validate_no_secrets("ghp_ABCDEFGHIJKLMNOPQRSTUVWXYZ01"))

    @covers("REQ-0.25.0-32-03")
    def test_task_management_not_false_positive(self) -> None:
        self.assertEqual(validate_no_secrets("task-management is a noun phrase"), [])

    @covers("REQ-0.25.0-32-03")
    def test_case_insensitive(self) -> None:
        self.assertTrue(validate_no_secrets("PASSWORD=hunter2"))


# ---------------------------------------------------------------------------
# validate_sections_present — REQ-0.25.0-32-03
# ---------------------------------------------------------------------------


class TestValidateSectionsPresent(unittest.TestCase):
    """@covers REQ-0.25.0-32-03"""

    @covers("REQ-0.25.0-32-03")
    def test_all_sections_present_returns_empty(self) -> None:
        doc = _clean_handoff_doc()
        self.assertEqual(validate_sections_present(doc), [])

    @covers("REQ-0.25.0-32-03")
    def test_missing_single_section_returned(self) -> None:
        body = "\n\n".join(
            f"## {section}\n\nbody" for section in REQUIRED_SECTIONS if section != "Decisions Made"
        )
        doc = f"---\nkey: value\n---\n\n{body}\n"
        missing = validate_sections_present(doc)
        self.assertEqual(missing, ["Decisions Made"])

    @covers("REQ-0.25.0-32-03")
    def test_missing_all_sections_returned(self) -> None:
        doc = "---\nkey: value\n---\n\nno sections at all.\n"
        missing = validate_sections_present(doc)
        self.assertEqual(set(missing), set(REQUIRED_SECTIONS))

    @covers("REQ-0.25.0-32-03")
    def test_exact_match_required(self) -> None:
        body = "## Current State\n\nmismatch"
        doc = f"---\nkey: value\n---\n\n{body}\n"
        missing = validate_sections_present(doc)
        self.assertIn("Current State Summary", missing)

    @covers("REQ-0.25.0-32-03")
    def test_extra_whitespace_tolerated(self) -> None:
        body = "\n\n".join(f"##  {section}  \n\nbody" for section in REQUIRED_SECTIONS)
        doc = f"---\nkey: value\n---\n\n{body}\n"
        self.assertEqual(validate_sections_present(doc), [])


# ---------------------------------------------------------------------------
# validate_referenced_files — REQ-0.25.0-32-03
# ---------------------------------------------------------------------------


class TestValidateReferencedFiles(unittest.TestCase):
    """@covers REQ-0.25.0-32-03"""

    @covers("REQ-0.25.0-32-03")
    def test_existing_file_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "evidence.txt").write_text("hello", encoding="utf-8")
            doc = (
                "---\nkey: value\n---\n\n## Evidence / Artifacts\n\n- `evidence.txt` — the proof\n"
            )
            self.assertEqual(validate_referenced_files(doc, tmp_path), [])

    @covers("REQ-0.25.0-32-03")
    def test_missing_file_reported(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = (
                "---\nkey: value\n---\n\n"
                "## Evidence / Artifacts\n\n"
                "- `nonexistent/thing.txt` — missing\n"
            )
            missing = validate_referenced_files(doc, Path(tmpdir))
            self.assertEqual(missing, ["nonexistent/thing.txt"])

    @covers("REQ-0.25.0-32-03")
    def test_command_prefixes_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = (
                "---\nkey: value\n---\n\n"
                "## Evidence / Artifacts\n\n"
                "- `uv run gz test` — command\n"
                "- `$ echo hi` — shell\n"
                "- `git status` — another command\n"
                "- `- bar` — dash prefix\n"
            )
            self.assertEqual(validate_referenced_files(doc, Path(tmpdir)), [])

    @covers("REQ-0.25.0-32-03")
    def test_non_path_strings_skipped(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = (
                "---\nkey: value\n---\n\n"
                "## Evidence / Artifacts\n\n"
                "- `some_variable` — not a path (no slash or dot)\n"
            )
            self.assertEqual(validate_referenced_files(doc, Path(tmpdir)), [])

    @covers("REQ-0.25.0-32-03")
    def test_no_evidence_section_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = "---\nkey: value\n---\n\n## Some Other Section\n\ncontent\n"
            self.assertEqual(validate_referenced_files(doc, Path(tmpdir)), [])

    @covers("REQ-0.25.0-32-03")
    def test_multiple_files_mixed_existence(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)
            (tmp_path / "present_a.txt").write_text("a", encoding="utf-8")
            (tmp_path / "present_b.txt").write_text("b", encoding="utf-8")
            doc = (
                "---\nkey: value\n---\n\n"
                "## Evidence / Artifacts\n\n"
                "- `present_a.txt`\n"
                "- `present_b.txt`\n"
                "- `absent_c.txt`\n"
            )
            missing = validate_referenced_files(doc, tmp_path)
            self.assertEqual(missing, ["absent_c.txt"])


# ---------------------------------------------------------------------------
# validate_handoff_document (orchestrator) — REQ-0.25.0-32-03
# ---------------------------------------------------------------------------


class TestValidateHandoffDocument(unittest.TestCase):
    """@covers REQ-0.25.0-32-03"""

    @covers("REQ-0.25.0-32-03")
    def test_clean_document_returns_empty(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = _clean_handoff_doc()
            self.assertEqual(validate_handoff_document(doc, Path(tmpdir)), [])

    @covers("REQ-0.25.0-32-03")
    def test_errors_accumulate(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            # Invalid frontmatter (bad ADR ID) + placeholder + missing section.
            doc = (
                "---\n"
                "mode: CREATE\n"
                "adr_id: not-an-adr\n"
                "branch: feature/foo\n"
                "timestamp: '2026-04-14T12:00:00'\n"
                "agent: claude\n"
                "---\n\n"
                "## Current State Summary\n\nTODO here\n"
            )
            errors = validate_handoff_document(doc, Path(tmpdir))
            self.assertTrue(any("Frontmatter" in err for err in errors))
            self.assertTrue(any("Placeholder" in err for err in errors))
            self.assertTrue(any("Missing required section" in err for err in errors))

    @covers("REQ-0.25.0-32-03")
    def test_frontmatter_error_reported_with_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = (
                "---\n"
                "mode: CREATE\n"
                "adr_id: bad\n"
                "branch: b\n"
                "timestamp: '2026-04-14T12:00:00'\n"
                "agent: a\n"
                "---\n\n" + "\n\n".join(f"## {s}\n\nbody" for s in REQUIRED_SECTIONS) + "\n"
            )
            errors = validate_handoff_document(doc, Path(tmpdir))
            self.assertTrue(any(err.startswith("Frontmatter:") for err in errors))

    @covers("REQ-0.25.0-32-03")
    def test_missing_section_reported_with_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            doc = (
                "---\n"
                "mode: CREATE\n"
                "adr_id: ADR-0.25.0\n"
                "branch: b\n"
                "timestamp: '2026-04-14T12:00:00'\n"
                "agent: a\n"
                "---\n\nno sections\n"
            )
            errors = validate_handoff_document(doc, Path(tmpdir))
            self.assertTrue(any(err.startswith("Missing required section:") for err in errors))

    @covers("REQ-0.25.0-32-03")
    def test_referenced_file_reported_with_prefix(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            body = "\n\n".join(f"## {s}\n\nbody" for s in REQUIRED_SECTIONS)
            body = body.replace(
                "## Evidence / Artifacts\n\nbody",
                "## Evidence / Artifacts\n\n- `missing/thing.txt` — gone",
            )
            doc = (
                "---\n"
                "mode: CREATE\n"
                "adr_id: ADR-0.25.0\n"
                "branch: b\n"
                "timestamp: '2026-04-14T12:00:00'\n"
                "agent: a\n"
                "---\n\n" + body + "\n"
            )
            errors = validate_handoff_document(doc, Path(tmpdir))
            self.assertTrue(any(err.startswith("Referenced file not found:") for err in errors))


# ---------------------------------------------------------------------------
# OBPI-0.25.0-32 brief-state assertions — REQ-01, REQ-02, REQ-05
# ---------------------------------------------------------------------------


def _brief_path() -> Path:
    return (
        Path(__file__).resolve().parents[2]
        / "docs"
        / "design"
        / "adr"
        / "pre-release"
        / "ADR-0.25.0-core-infrastructure-pattern-absorption"
        / "obpis"
        / "OBPI-0.25.0-32-handoff-validation-pattern.md"
    )


class TestHandoffAbsorptionBrief(unittest.TestCase):
    """Brief-state tests covering the Absorb decision and Gate 4 N/A rationale.

    @covers REQ-0.25.0-32-01
    @covers REQ-0.25.0-32-02
    @covers REQ-0.25.0-32-05
    """

    @classmethod
    def setUpClass(cls) -> None:
        cls.brief_text = _brief_path().read_text(encoding="utf-8")

    @covers("REQ-0.25.0-32-01")
    def test_decision_recorded_as_absorb(self) -> None:
        self.assertRegex(
            self.brief_text,
            r"##\s+Decision\s*\n[\s\S]*?\*\*Absorb\*\*",
            "Brief must have an explicit '## Decision' H2 section recording "
            "'**Absorb**'. Template text that merely enumerates "
            "Absorb/Confirm/Exclude as options does not satisfy this.",
        )

    @covers("REQ-0.25.0-32-02")
    def test_rationale_cites_concrete_differences(self) -> None:
        self.assertRegex(
            self.brief_text,
            r"##\s+Decision\s*\n",
            "Brief must have a '## Decision' section before rationale can be located.",
        )
        decision_match = self.brief_text.split("## Decision", 1)
        self.assertEqual(len(decision_match), 2, "Decision section anchor missing")
        decision_body = decision_match[1]
        next_h2 = decision_body.find("\n## ")
        decision_scope = decision_body if next_h2 == -1 else decision_body[:next_h2]
        lowered = decision_scope.lower()
        concrete_signals = (
            "handoffrontmatter",
            "placeholder",
            "6 checks",
            "six checks",
            "secret",
            "required section",
            "crlf",
        )
        matched = [signal for signal in concrete_signals if signal in lowered]
        self.assertTrue(
            matched,
            f"Decision rationale must cite concrete capability differences. "
            f"Expected one of {concrete_signals} within the '## Decision' section; found none.",
        )

    @covers("REQ-0.25.0-32-04")
    def test_req04_not_applicable_outcome_is_absorb(self) -> None:
        """REQ-0.25.0-32-04 applies to Confirm/Exclude outcomes only.

        The decision for this OBPI is Absorb, so REQ-04 is N/A. This test
        asserts that N/A status holds — if the decision is ever changed to
        Confirm or Exclude, this test must be replaced with a substantive
        rationale check.
        """
        self.assertRegex(
            self.brief_text,
            r"##\s+Decision\s*\n[\s\S]*?\*\*Absorb\*\*",
            "REQ-04 is N/A only while the decision remains Absorb. If the "
            "decision is changed, replace this sentinel with a real check.",
        )

    @covers("REQ-0.25.0-32-05")
    def test_gate4_na_recorded_with_rationale(self) -> None:
        self.assertRegex(
            self.brief_text,
            r"Gate 4 \(BDD\):\*\*\s*\*\*N/A\*\*",
            "Completion Checklist must record 'Gate 4 (BDD): **N/A**' with explicit N/A marker.",
        )
        self.assertRegex(
            self.brief_text,
            r"(?i)library function|no operator-visible|no cli surface|no external-surface change",
            "Gate 4 N/A must have an explicit rationale phrase.",
        )


if __name__ == "__main__":
    unittest.main()
