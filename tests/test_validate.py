"""Tests for gzkit validation engine."""

import tempfile
import unittest
from pathlib import Path

from gzkit.validate import (
    extract_headers,
    parse_frontmatter,
    validate_document,
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
parent: BRIEF-core
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
parent: BRIEF-core
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
                "brief": {"path": "design/briefs", "schema": "gzkit.brief.v1"},
                "adr": {"path": "design/adr", "schema": "gzkit.adr.v1"},
            },
            "control_surfaces": {
                "agents_md": "AGENTS.md",
                "claude_md": "CLAUDE.md",
                "hooks": ".claude/hooks",
                "skills": ".github/skills",
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


if __name__ == "__main__":
    unittest.main()
