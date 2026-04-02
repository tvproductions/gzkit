"""Tests for persona schema validation — structural enforcement and negative coverage.

Covers OBPI-0.0.11-06: persona files must pass deterministic schema and
structural validation before agent loading consumes them.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.models.persona import validate_persona_structure
from gzkit.traceability import covers

_VALID_PERSONA = """\
---
name: tester
traits:
  - methodical
  - thorough
anti-traits:
  - shallow-compliance
grounding: I verify every claim with evidence.
---

# Tester Persona

Behavioral identity for verification work.
"""


class TestValidPersona(unittest.TestCase):
    """Positive baseline: well-formed persona files pass validation."""

    @covers("REQ-0.0.11-06-01")
    def test_valid_persona_passes(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "tester.md"
            p.write_text(_VALID_PERSONA, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertEqual(errors, [])


class TestRequiredFields(unittest.TestCase):
    """REQ-01: Validation enforces required structural fields."""

    _FIELD_CASES = [
        (
            "missing_name",
            "---\ntraits:\n  - a\nanti-traits:\n  - b\ngrounding: g\n---\n",
        ),
        (
            "missing_traits",
            "---\nname: x\nanti-traits:\n  - b\ngrounding: g\n---\n",
        ),
        (
            "missing_anti_traits",
            "---\nname: x\ntraits:\n  - a\ngrounding: g\n---\n",
        ),
        (
            "missing_grounding",
            "---\nname: x\ntraits:\n  - a\nanti-traits:\n  - b\n---\n",
        ),
    ]

    @covers("REQ-0.0.11-06-01")
    def test_missing_required_fields(self) -> None:
        for label, content in self._FIELD_CASES:
            with self.subTest(label=label), tempfile.TemporaryDirectory() as tmpdir:
                p = Path(tmpdir) / "x.md"
                p.write_text(content, encoding="utf-8")
                errors = validate_persona_structure(p)
                self.assertGreater(len(errors), 0, f"{label} should produce errors")

    @covers("REQ-0.0.11-06-01")
    def test_extra_field_rejected(self) -> None:
        content = (
            "---\nname: x\ntraits:\n  - a\nanti-traits:\n  - b\ngrounding: g\nunknown: bad\n---\n"
        )
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.md"
            p.write_text(content, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertGreater(len(errors), 0)


class TestNegativeCoverage(unittest.TestCase):
    """REQ-02: Invalid persona files fail with deterministic negative-test coverage."""

    @covers("REQ-0.0.11-06-02")
    def test_empty_traits_list(self) -> None:
        content = "---\nname: x\ntraits: []\nanti-traits:\n  - b\ngrounding: g\n---\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.md"
            p.write_text(content, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertTrue(any("traits" in e for e in errors))

    @covers("REQ-0.0.11-06-02")
    def test_empty_anti_traits_list(self) -> None:
        content = "---\nname: x\ntraits:\n  - a\nanti-traits: []\ngrounding: g\n---\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.md"
            p.write_text(content, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertTrue(any("anti-traits" in e for e in errors))

    @covers("REQ-0.0.11-06-02")
    def test_empty_grounding(self) -> None:
        content = "---\nname: x\ntraits:\n  - a\nanti-traits:\n  - b\ngrounding: ''\n---\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.md"
            p.write_text(content, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertTrue(any("grounding" in e for e in errors))

    @covers("REQ-0.0.11-06-02")
    def test_whitespace_only_grounding(self) -> None:
        content = "---\nname: x\ntraits:\n  - a\nanti-traits:\n  - b\ngrounding: '   '\n---\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "x.md"
            p.write_text(content, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertTrue(any("grounding" in e for e in errors))

    @covers("REQ-0.0.11-06-02")
    def test_missing_frontmatter_delimiters(self) -> None:
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bad.md"
            p.write_text("# No frontmatter here\n", encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertGreater(len(errors), 0)

    @covers("REQ-0.0.11-06-02")
    def test_non_yaml_frontmatter(self) -> None:
        content = "---\n[not valid yaml\n---\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "bad.md"
            p.write_text(content, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertGreater(len(errors), 0)

    @covers("REQ-0.0.11-06-02")
    def test_name_filename_mismatch(self) -> None:
        content = "---\nname: wrong\ntraits:\n  - a\nanti-traits:\n  - b\ngrounding: g\n---\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            p = Path(tmpdir) / "actual.md"
            p.write_text(content, encoding="utf-8")
            errors = validate_persona_structure(p)
            self.assertTrue(any("does not match" in e for e in errors))


class TestValidateIntegration(unittest.TestCase):
    """REQ-03: Validation participates in normal repo verification."""

    @covers("REQ-0.0.11-06-03")
    def test_validate_personas_import(self) -> None:
        """validate_personas is importable from gzkit.validate."""
        from gzkit.validate import validate_personas

        self.assertTrue(callable(validate_personas))

    @covers("REQ-0.0.11-06-03")
    def test_validate_personas_on_valid_dir(self) -> None:
        from gzkit.validate import validate_personas

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdir = root / ".gzkit" / "personas"
            pdir.mkdir(parents=True)
            (pdir / "tester.md").write_text(_VALID_PERSONA, encoding="utf-8")
            errors = validate_personas(root)
            self.assertEqual(errors, [])

    @covers("REQ-0.0.11-06-03")
    def test_validate_personas_catches_malformed(self) -> None:
        from gzkit.validate import validate_personas

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdir = root / ".gzkit" / "personas"
            pdir.mkdir(parents=True)
            (pdir / "bad.md").write_text("# no frontmatter\n", encoding="utf-8")
            errors = validate_personas(root)
            self.assertGreater(len(errors), 0)
            self.assertEqual(errors[0].type, "persona")

    @covers("REQ-0.0.11-06-03")
    def test_validate_personas_empty_dir(self) -> None:
        from gzkit.validate import validate_personas

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdir = root / ".gzkit" / "personas"
            pdir.mkdir(parents=True)
            errors = validate_personas(root)
            self.assertEqual(errors, [])

    @covers("REQ-0.0.11-06-03")
    def test_validate_personas_missing_dir(self) -> None:
        from gzkit.validate import validate_personas

        with tempfile.TemporaryDirectory() as tmpdir:
            errors = validate_personas(Path(tmpdir))
            self.assertEqual(errors, [])

    @covers("REQ-0.0.11-06-03")
    def test_multi_persona_directory(self) -> None:
        from gzkit.validate import validate_personas

        persona_a = "---\nname: alpha\ntraits:\n  - a\nanti-traits:\n  - b\ngrounding: g\n---\n"
        persona_b = "---\nname: beta\ntraits:\n  - x\nanti-traits:\n  - y\ngrounding: g\n---\n"
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            pdir = root / ".gzkit" / "personas"
            pdir.mkdir(parents=True)
            (pdir / "alpha.md").write_text(persona_a, encoding="utf-8")
            (pdir / "beta.md").write_text(persona_b, encoding="utf-8")
            errors = validate_personas(root)
            self.assertEqual(errors, [])


class TestExemplarValidation(unittest.TestCase):
    """Verify the shipped exemplar persona file passes structural validation."""

    @covers("REQ-0.0.11-06-01")
    def test_exemplar_implementer_validates(self) -> None:
        exemplar = Path(".gzkit/personas/implementer.md")
        if not exemplar.is_file():
            self.skipTest("exemplar not yet created")
        errors = validate_persona_structure(exemplar)
        self.assertEqual(errors, [], f"Exemplar failed validation: {errors}")


if __name__ == "__main__":
    unittest.main()
