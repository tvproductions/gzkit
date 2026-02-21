"""Tests for gzkit validation engine."""

import json
import tempfile
import unittest
from pathlib import Path

from gzkit.validate import (
    extract_headers,
    parse_frontmatter,
    validate_document,
    validate_ledger,
    validate_manifest,
)


class TestParseFrontmatter(unittest.TestCase):
    """Tests for frontmatter parsing."""

    def test_no_frontmatter(self) -> None:
        """Content without frontmatter returns empty dict."""
        content = "# Title\n\nSome content"
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm, {})
        self.assertEqual(body, content)

    def test_with_frontmatter(self) -> None:
        """Content with frontmatter is parsed correctly."""
        content = """---
id: ADR-0.1.0
status: Draft
---

# Title

Content here."""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["id"], "ADR-0.1.0")
        self.assertEqual(fm["status"], "Draft")
        self.assertIn("# Title", body)

    def test_quoted_values(self) -> None:
        """Quoted values have quotes removed."""
        content = """---
title: "My Title"
name: 'Single quoted'
---

Body"""
        fm, body = parse_frontmatter(content)
        self.assertEqual(fm["title"], "My Title")
        self.assertEqual(fm["name"], "Single quoted")


class TestExtractHeaders(unittest.TestCase):
    """Tests for header extraction."""

    def test_extracts_h2_headers(self) -> None:
        """Extracts ## level headers."""
        content = """# Title

## Section One

Content

## Section Two

More content

### Subsection

Not extracted"""
        headers = extract_headers(content)
        self.assertEqual(headers, ["Section One", "Section Two"])

    def test_strips_anchors(self) -> None:
        """Strips anchor tags from headers."""
        content = """## Section One {#section-one}

Content"""
        headers = extract_headers(content)
        self.assertEqual(headers, ["Section One"])


class TestValidateDocument(unittest.TestCase):
    """Tests for document validation."""

    def test_missing_file(self) -> None:
        """Missing file returns error."""
        errors = validate_document(Path("/nonexistent.md"), "adr")
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "schema")
        self.assertIn("does not exist", errors[0].message)

    def test_valid_adr(self) -> None:
        """Valid ADR passes validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
id: ADR-0.1.0
status: Draft
semver: 0.1.0
lane: lite
parent: OBPI-core
date: 2026-01-01
---

# ADR-0.1.0: Test

## Intent

Test intent.

## Decision

Test decision.

## Consequences

Test consequences.

## OBPIs

Test OBPIs.

## Evidence

Test evidence.

## Attestation Block

| Term | Status | Attested By | Date | Reason |
|------|--------|-------------|------|--------|
""")
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            self.assertEqual(errors, [])

    def test_missing_frontmatter_field(self) -> None:
        """Missing frontmatter field returns error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
id: ADR-0.1.0
status: Draft
---

# Title

## Intent
""")
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            # Should have errors for missing semver, lane, parent, date
            self.assertTrue(any(e.field == "semver" for e in errors))

    def test_missing_section(self) -> None:
        """Missing required section returns error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("""---
id: ADR-0.1.0
status: Draft
semver: 0.1.0
lane: lite
parent: OBPI-core
date: 2026-01-01
---

# Title

## Intent

Content but missing Decision section.
""")
            f.flush()
            errors = validate_document(Path(f.name), "adr")
            self.assertTrue(any(e.field == "Decision" for e in errors))


class TestValidateManifest(unittest.TestCase):
    """Tests for manifest validation."""

    def test_missing_manifest(self) -> None:
        """Missing manifest returns error."""
        errors = validate_manifest(Path("/nonexistent/manifest.json"))
        self.assertEqual(len(errors), 1)
        self.assertIn("does not exist", errors[0].message)

    def test_valid_manifest(self) -> None:
        """Valid manifest passes validation."""
        import json

        manifest = {
            "schema": "gzkit.manifest.v1",
            "structure": {
                "source_root": "src",
                "tests_root": "tests",
                "docs_root": "docs",
                "design_root": "design",
            },
            "artifacts": {
                "prd": {"path": "design/prd", "schema": "gzkit.prd.v1"},
                "constitution": {"path": "design/constitutions", "schema": "gzkit.constitution.v1"},
                "obpi": {"path": "design/adr", "schema": "gzkit.obpi.v1"},
                "adr": {"path": "design/adr", "schema": "gzkit.adr.v1"},
            },
            "control_surfaces": {
                "agents_md": "AGENTS.md",
                "claude_md": "CLAUDE.md",
                "hooks": ".claude/hooks",
                "skills": ".gzkit/skills",
                "claude_skills": ".claude/skills",
                "codex_skills": ".agents/skills",
                "copilot_skills": ".github/skills",
            },
            "verification": {
                "lint": "uvx ruff check src tests",
                "format": "uvx ruff format --check .",
                "typecheck": "uvx ty check src",
                "test": "uv run -m unittest discover tests",
            },
            "gates": {
                "lite": [1, 2, 5],
                "heavy": [1, 2, 3, 4, 5],
            },
        }

        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump(manifest, f)
            f.flush()
            errors = validate_manifest(Path(f.name))
            self.assertEqual(errors, [])


class TestValidateLedger(unittest.TestCase):
    """Tests for ledger validation."""

    def test_missing_ledger(self) -> None:
        """Missing ledger returns error."""
        errors = validate_ledger(Path("/nonexistent/ledger.jsonl"))
        self.assertEqual(len(errors), 1)
        self.assertEqual(errors[0].type, "ledger")
        self.assertIn("does not exist", errors[0].message)

    def test_valid_ledger(self) -> None:
        """Valid ledger events pass validation."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            entries = [
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "project_init",
                    "id": "gzkit",
                    "ts": "2026-02-14T00:00:00+00:00",
                    "mode": "lite",
                },
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "adr_created",
                    "id": "ADR-0.3.0",
                    "ts": "2026-02-14T00:00:01+00:00",
                    "lane": "heavy",
                },
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "audit_receipt_emitted",
                    "id": "ADR-0.3.0",
                    "ts": "2026-02-14T00:00:02+00:00",
                    "receipt_event": "completed",
                    "attestor": "human:jeff",
                    "evidence": {"scope": "OBPI-0.3.0-04"},
                },
                {
                    "schema": "gzkit.ledger.v1",
                    "event": "obpi_receipt_emitted",
                    "id": "OBPI-0.3.0-04-demo",
                    "parent": "ADR-0.3.0",
                    "ts": "2026-02-14T00:00:03+00:00",
                    "receipt_event": "validated",
                    "attestor": "human:jeff",
                    "evidence": {"acceptance": "observed"},
                },
            ]
            for entry in entries:
                f.write(json.dumps(entry) + "\n")
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertEqual(errors, [])

    def test_invalid_json_line(self) -> None:
        """Malformed JSON line returns ledger validation error."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write("{not-json}\n")
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(any("Invalid JSON" in error.message for error in errors))

    def test_unknown_event_rejected(self) -> None:
        """Unknown event type fails closed."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "mystery_event",
                        "id": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:00+00:00",
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(any("Unknown event type" in error.message for error in errors))

    def test_invalid_event_field_type_rejected(self) -> None:
        """Event field type violations are reported with line context."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".jsonl", delete=False) as f:
            f.write(
                json.dumps(
                    {
                        "schema": "gzkit.ledger.v1",
                        "event": "audit_receipt_emitted",
                        "id": "ADR-0.3.0",
                        "ts": "2026-02-14T00:00:00+00:00",
                        "receipt_event": "completed",
                        "attestor": "human:jeff",
                        "evidence": ["not", "an", "object"],
                    }
                )
                + "\n"
            )
            f.flush()
            errors = validate_ledger(Path(f.name))
            self.assertTrue(any("must be an object" in error.message for error in errors))


if __name__ == "__main__":
    unittest.main()
