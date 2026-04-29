"""JSON schema validation for the `sensitivity` field (ADR-0.0.22, OBPI-0.0.22-01).

Covers REQ-0.0.22-01-01 (accept declared:security), REQ-0.0.22-01-02 (accept absent),
REQ-0.0.22-01-03 (reject unknown values), REQ-0.0.22-01-05 (existing artifacts validate
without the field present — backwards-compatibility floor).

@covers REQ-0.0.22-01-01
@covers REQ-0.0.22-01-02
@covers REQ-0.0.22-01-03
@covers REQ-0.0.22-01-05
"""

from __future__ import annotations

import unittest
from pathlib import Path

import jsonschema

from gzkit.schemas import load_schema
from gzkit.traceability import covers  # noqa: F401

REPO_ROOT = Path(__file__).resolve().parents[2]
ADR_DIR = REPO_ROOT / "docs" / "design" / "adr"


def _minimal_adr_frontmatter() -> dict[str, object]:
    return {
        "id": "ADR-0.0.99-test-only",
        "status": "Draft",
        "semver": "0.0.99",
        "lane": "lite",
        "kind": "foundation",
        "parent": "PRD-GZKIT-1.0.0",
        "date": "2026-04-29",
    }


def _minimal_obpi_frontmatter() -> dict[str, object]:
    return {
        "id": "OBPI-0.0.99-01-test-only",
        "parent": "ADR-0.0.99-test-only",
        "item": 1,
        "lane": "lite",
        "status": "Draft",
    }


def _wrap(frontmatter: dict[str, object]) -> dict[str, object]:
    return {"frontmatter": frontmatter, "headers": []}


class TestSensitivityFieldSchemaAcceptance(unittest.TestCase):
    """REQ-0.0.22-01-01: schemas accept `sensitivity: security`."""

    def test_adr_schema_accepts_sensitivity_security(self) -> None:
        schema = load_schema("adr")
        fm = _minimal_adr_frontmatter()
        fm["sensitivity"] = "security"
        jsonschema.validate(_wrap(fm), schema)

    def test_obpi_schema_accepts_sensitivity_security(self) -> None:
        schema = load_schema("obpi")
        fm = _minimal_obpi_frontmatter()
        fm["sensitivity"] = "security"
        jsonschema.validate(_wrap(fm), schema)


class TestSensitivityFieldOptional(unittest.TestCase):
    """REQ-0.0.22-01-02: schemas accept absent `sensitivity` (optional)."""

    def test_adr_schema_accepts_absent_sensitivity(self) -> None:
        schema = load_schema("adr")
        jsonschema.validate(_wrap(_minimal_adr_frontmatter()), schema)

    def test_obpi_schema_accepts_absent_sensitivity(self) -> None:
        schema = load_schema("obpi")
        jsonschema.validate(_wrap(_minimal_obpi_frontmatter()), schema)


class TestSensitivityFieldRejection(unittest.TestCase):
    """REQ-0.0.22-01-03: schemas reject unknown enum values for `sensitivity`."""

    def test_adr_schema_rejects_unknown_sensitivity_value(self) -> None:
        schema = load_schema("adr")
        fm = _minimal_adr_frontmatter()
        fm["sensitivity"] = "confidential"
        with self.assertRaises(jsonschema.ValidationError) as ctx:
            jsonschema.validate(_wrap(fm), schema)
        self.assertIn("sensitivity", "/".join(str(p) for p in ctx.exception.absolute_path))

    def test_obpi_schema_rejects_unknown_sensitivity_value(self) -> None:
        schema = load_schema("obpi")
        fm = _minimal_obpi_frontmatter()
        fm["sensitivity"] = "confidential"
        with self.assertRaises(jsonschema.ValidationError) as ctx:
            jsonschema.validate(_wrap(fm), schema)
        self.assertIn("sensitivity", "/".join(str(p) for p in ctx.exception.absolute_path))


class TestExistingArtifactsBackwardsCompatible(unittest.TestCase):
    """REQ-0.0.22-01-05: every existing ADR/OBPI artifact validates without sensitivity."""

    def _iter_adr_obpi_files(self) -> list[Path]:
        if not ADR_DIR.exists():
            return []
        results: list[Path] = []
        for path in ADR_DIR.rglob("*.md"):
            name = path.name
            if (name.startswith("ADR-") or name.startswith("OBPI-")) and name.endswith(".md"):
                results.append(path)
        return results

    def test_existing_artifacts_lack_sensitivity_or_match_enum(self) -> None:
        """No existing artifact carries a sensitivity value outside the registered enum."""
        import re

        offenders: list[str] = []
        for path in self._iter_adr_obpi_files():
            text = path.read_text(encoding="utf-8")
            if not text.startswith("---"):
                continue
            close = text.find("\n---", 3)
            if close == -1:
                continue
            frontmatter_text = text[3:close]
            match = re.search(r"^sensitivity:\s*(\S+)\s*$", frontmatter_text, re.MULTILINE)
            if match is None:
                continue
            value = match.group(1).strip().strip("'").strip('"')
            if value not in {"security"}:
                offenders.append(f"{path.relative_to(REPO_ROOT)}: sensitivity={value!r}")
        self.assertEqual(offenders, [], "Existing artifacts carry unregistered sensitivity values")


if __name__ == "__main__":
    unittest.main()
