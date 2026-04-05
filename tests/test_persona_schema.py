"""Tests for persona schema validation — structural enforcement and negative coverage.

Covers OBPI-0.0.11-06: persona files must pass deterministic schema and
structural validation before agent loading consumes them.
"""

import tempfile
import unittest
from pathlib import Path

from gzkit.models.persona import PersonaFrontmatter, parse_persona_file, validate_persona_structure
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


class TestMainSessionValidation(unittest.TestCase):
    """Verify main-session persona passes structural and PRISM validation.

    Covers OBPI-0.0.12-01 (ADR-0.0.12).
    """

    @covers("REQ-0.0.12-01-01")
    def test_main_session_validates(self) -> None:
        path = Path(".gzkit/personas/main-session.md")
        if not path.is_file():
            self.skipTest("main-session persona not yet created")
        errors = validate_persona_structure(path)
        self.assertEqual(errors, [], f"main-session failed: {errors}")

    @covers("REQ-0.0.12-01-02")
    def test_main_session_no_expertise_claims(self) -> None:
        path = Path(".gzkit/personas/main-session.md")
        if not path.is_file():
            self.skipTest("main-session persona not yet created")
        fm, body = parse_persona_file(path)
        full_text = (fm.grounding + " " + body).lower()
        expertise_phrases = [
            "expert",
            "senior",
            "years of experience",
            "professional",
            "skilled developer",
        ]
        for phrase in expertise_phrases:
            self.assertNotIn(
                phrase,
                full_text,
                f"PRISM violation: expertise claim '{phrase}' found",
            )

    @covers("REQ-0.0.12-01-03")
    def test_main_session_composition(self) -> None:
        from gzkit.personas import compose_persona_frame

        path = Path(".gzkit/personas/main-session.md")
        if not path.is_file():
            self.skipTest("main-session persona not yet created")
        fm, body = parse_persona_file(path)
        frame = compose_persona_frame(fm, body)
        self.assertIn("craftsperson", frame.lower())
        self.assertIn("does NOT do", frame)


class TestImplementerEnrichment(unittest.TestCase):
    """Verify implementer persona enrichment from ADR-0.0.12.

    Covers OBPI-0.0.12-02: plan-then-write, whole-file thinking, PEP-8-as-identity.
    """

    @covers("REQ-0.0.12-02-01")
    def test_implementer_schema_and_grounding(self) -> None:
        """Enriched implementer validates and grounding addresses trait cluster."""
        path = Path(".gzkit/personas/implementer.md")
        if not path.is_file():
            self.skipTest("implementer persona not yet created")
        errors = validate_persona_structure(path)
        self.assertEqual(errors, [], f"Schema validation failed: {errors}")

        fm, _body = parse_persona_file(path)
        grounding_lower = fm.grounding.lower()
        self.assertIn("plan", grounding_lower, "Grounding must address plan-first")
        self.assertIn("whole", grounding_lower, "Grounding must address whole-file")

    @covers("REQ-0.0.12-02-02")
    def test_implementer_no_expertise_claims(self) -> None:
        """PRISM: no expertise claims in grounding or body."""

        path = Path(".gzkit/personas/implementer.md")
        if not path.is_file():
            self.skipTest("implementer persona not yet created")
        fm, body = parse_persona_file(path)
        full_text = (fm.grounding + " " + body).lower()
        expertise_phrases = [
            "expert",
            "senior",
            "years of experience",
            "professional",
            "skilled developer",
        ]
        for phrase in expertise_phrases:
            self.assertNotIn(
                phrase,
                full_text,
                f"PRISM violation: expertise claim '{phrase}' found",
            )

    @covers("REQ-0.0.12-02-03")
    def test_implementer_enriched_traits(self) -> None:
        """Enriched traits include plan-then-write and whole-file-thinking."""

        path = Path(".gzkit/personas/implementer.md")
        if not path.is_file():
            self.skipTest("implementer persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("plan-then-write", fm.traits)
        self.assertIn("whole-file-thinking", fm.traits)
        self.assertIn("pep8-as-identity", fm.traits)
        # Existing traits preserved
        self.assertIn("methodical", fm.traits)
        self.assertIn("test-first", fm.traits)
        self.assertIn("atomic-edits", fm.traits)
        self.assertIn("complete-units", fm.traits)


class TestSpecReviewerValidation(unittest.TestCase):
    """Verify spec-reviewer persona passes structural and PRISM validation.

    Covers OBPI-0.0.12-03 (ADR-0.0.12).
    """

    @covers("REQ-0.0.12-03-01")
    def test_spec_reviewer_validates(self) -> None:
        path = Path(".gzkit/personas/spec-reviewer.md")
        if not path.is_file():
            self.skipTest("spec-reviewer persona not yet created")
        errors = validate_persona_structure(path)
        self.assertEqual(errors, [], f"spec-reviewer failed: {errors}")

    @covers("REQ-0.0.12-03-02")
    def test_spec_reviewer_no_expertise_claims(self) -> None:
        path = Path(".gzkit/personas/spec-reviewer.md")
        if not path.is_file():
            self.skipTest("spec-reviewer persona not yet created")
        fm, body = parse_persona_file(path)
        full_text = (fm.grounding + " " + body).lower()
        expertise_phrases = [
            "expert",
            "senior",
            "years of experience",
            "professional",
            "skilled developer",
        ]
        for phrase in expertise_phrases:
            self.assertNotIn(
                phrase,
                full_text,
                f"PRISM violation: expertise claim '{phrase}' found",
            )

    @covers("REQ-0.0.12-03-02")
    def test_spec_reviewer_traits(self) -> None:
        path = Path(".gzkit/personas/spec-reviewer.md")
        if not path.is_file():
            self.skipTest("spec-reviewer persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("independent-judgment", fm.traits)
        self.assertIn("skepticism", fm.traits)
        self.assertIn("evidence-based-assessment", fm.traits)
        self.assertIn("requirement-tracing", fm.traits)

    @covers("REQ-0.0.12-03-02")
    def test_spec_reviewer_anti_traits(self) -> None:
        path = Path(".gzkit/personas/spec-reviewer.md")
        if not path.is_file():
            self.skipTest("spec-reviewer persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("rubber-stamping", fm.anti_traits)
        self.assertIn("optimistic-bias", fm.anti_traits)


class TestQualityReviewerValidation(unittest.TestCase):
    """Verify quality-reviewer persona passes structural and PRISM validation.

    Covers OBPI-0.0.12-03 (ADR-0.0.12).
    """

    @covers("REQ-0.0.12-03-01")
    def test_quality_reviewer_validates(self) -> None:
        path = Path(".gzkit/personas/quality-reviewer.md")
        if not path.is_file():
            self.skipTest("quality-reviewer persona not yet created")
        errors = validate_persona_structure(path)
        self.assertEqual(errors, [], f"quality-reviewer failed: {errors}")

    @covers("REQ-0.0.12-03-03")
    def test_quality_reviewer_no_expertise_claims(self) -> None:
        path = Path(".gzkit/personas/quality-reviewer.md")
        if not path.is_file():
            self.skipTest("quality-reviewer persona not yet created")
        fm, body = parse_persona_file(path)
        full_text = (fm.grounding + " " + body).lower()
        expertise_phrases = [
            "expert",
            "senior",
            "years of experience",
            "professional",
            "skilled developer",
        ]
        for phrase in expertise_phrases:
            self.assertNotIn(
                phrase,
                full_text,
                f"PRISM violation: expertise claim '{phrase}' found",
            )

    @covers("REQ-0.0.12-03-03")
    def test_quality_reviewer_traits(self) -> None:
        path = Path(".gzkit/personas/quality-reviewer.md")
        if not path.is_file():
            self.skipTest("quality-reviewer persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("architectural-rigor", fm.traits)
        self.assertIn("solid-principles", fm.traits)
        self.assertIn("maintainability-assessment", fm.traits)
        self.assertIn("size-discipline", fm.traits)

    @covers("REQ-0.0.12-03-03")
    def test_quality_reviewer_anti_traits(self) -> None:
        path = Path(".gzkit/personas/quality-reviewer.md")
        if not path.is_file():
            self.skipTest("quality-reviewer persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("rubber-stamping", fm.anti_traits)
        self.assertIn("surface-level-review", fm.anti_traits)


class TestNarratorValidation(unittest.TestCase):
    """Verify narrator persona passes structural and PRISM validation.

    Covers OBPI-0.0.12-04 (ADR-0.0.12).
    """

    @covers("REQ-0.0.12-04-01")
    def test_narrator_validates(self) -> None:
        path = Path(".gzkit/personas/narrator.md")
        if not path.is_file():
            self.skipTest("narrator persona not yet created")
        errors = validate_persona_structure(path)
        self.assertEqual(errors, [], f"narrator failed: {errors}")

    @covers("REQ-0.0.12-04-02")
    def test_narrator_no_expertise_claims(self) -> None:
        path = Path(".gzkit/personas/narrator.md")
        if not path.is_file():
            self.skipTest("narrator persona not yet created")
        fm, body = parse_persona_file(path)
        full_text = (fm.grounding + " " + body).lower()
        expertise_phrases = [
            "expert",
            "senior",
            "years of experience",
            "professional",
            "skilled developer",
        ]
        for phrase in expertise_phrases:
            self.assertNotIn(
                phrase,
                full_text,
                f"PRISM violation: expertise claim '{phrase}' found",
            )

    @covers("REQ-0.0.12-04-02")
    def test_narrator_traits(self) -> None:
        path = Path(".gzkit/personas/narrator.md")
        if not path.is_file():
            self.skipTest("narrator persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("clarity", fm.traits)
        self.assertIn("precision", fm.traits)
        self.assertIn("operator-value-framing", fm.traits)

    @covers("REQ-0.0.12-04-02")
    def test_narrator_anti_traits(self) -> None:
        path = Path(".gzkit/personas/narrator.md")
        if not path.is_file():
            self.skipTest("narrator persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("verbosity", fm.anti_traits)
        self.assertIn("jargon-accumulation", fm.anti_traits)

    @covers("REQ-0.0.12-04-03")
    def test_narrator_composition(self) -> None:
        from gzkit.personas import compose_persona_frame

        path = Path(".gzkit/personas/narrator.md")
        if not path.is_file():
            self.skipTest("narrator persona not yet created")
        fm, body = parse_persona_file(path)
        frame = compose_persona_frame(fm, body)
        self.assertIn("evidence", frame.lower())
        self.assertIn("does NOT do", frame)


class TestPipelineOrchestratorValidation(unittest.TestCase):
    """Verify pipeline-orchestrator persona passes structural and PRISM validation.

    Covers OBPI-0.0.12-05 (ADR-0.0.12).
    """

    @covers("REQ-0.0.12-05-01")
    def test_pipeline_orchestrator_validates(self) -> None:
        path = Path(".gzkit/personas/pipeline-orchestrator.md")
        if not path.is_file():
            self.skipTest("pipeline-orchestrator persona not yet created")
        errors = validate_persona_structure(path)
        self.assertEqual(errors, [], f"pipeline-orchestrator failed: {errors}")

    @covers("REQ-0.0.12-05-02")
    def test_pipeline_orchestrator_no_expertise_claims(self) -> None:
        path = Path(".gzkit/personas/pipeline-orchestrator.md")
        if not path.is_file():
            self.skipTest("pipeline-orchestrator persona not yet created")
        fm, body = parse_persona_file(path)
        full_text = (fm.grounding + " " + body).lower()
        expertise_phrases = [
            "expert",
            "senior",
            "years of experience",
            "professional",
            "skilled developer",
        ]
        for phrase in expertise_phrases:
            self.assertNotIn(
                phrase,
                full_text,
                f"PRISM violation: expertise claim '{phrase}' found",
            )

    @covers("REQ-0.0.12-05-02")
    def test_pipeline_orchestrator_traits(self) -> None:
        path = Path(".gzkit/personas/pipeline-orchestrator.md")
        if not path.is_file():
            self.skipTest("pipeline-orchestrator persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("ceremony-completion", fm.traits)
        self.assertIn("stage-discipline", fm.traits)
        self.assertIn("governance-fidelity", fm.traits)
        self.assertIn("sequential-flow", fm.traits)
        self.assertIn("evidence-anchoring", fm.traits)

    @covers("REQ-0.0.12-05-02")
    def test_pipeline_orchestrator_anti_traits(self) -> None:
        path = Path(".gzkit/personas/pipeline-orchestrator.md")
        if not path.is_file():
            self.skipTest("pipeline-orchestrator persona not yet created")
        fm, _body = parse_persona_file(path)
        self.assertIn("premature-summarization", fm.anti_traits)
        self.assertIn("stage-skipping", fm.anti_traits)
        self.assertIn("good-enough-completion", fm.anti_traits)

    @covers("REQ-0.0.12-05-03")
    def test_pipeline_orchestrator_composition(self) -> None:
        from gzkit.personas import compose_persona_frame

        path = Path(".gzkit/personas/pipeline-orchestrator.md")
        if not path.is_file():
            self.skipTest("pipeline-orchestrator persona not yet created")
        fm, body = parse_persona_file(path)
        frame = compose_persona_frame(fm, body)
        self.assertIn("ceremony", frame.lower())
        self.assertIn("does NOT do", frame)


class TestReviewerOrthogonality(unittest.TestCase):
    """Verify reviewer trait clusters are orthogonal.

    Covers OBPI-0.0.12-03 (ADR-0.0.12).
    """

    @covers("REQ-0.0.12-03-01")
    def test_trait_clusters_are_orthogonal(self) -> None:
        spec_path = Path(".gzkit/personas/spec-reviewer.md")
        quality_path = Path(".gzkit/personas/quality-reviewer.md")
        if not spec_path.is_file() or not quality_path.is_file():
            self.skipTest("reviewer personas not yet created")
        spec_fm, _ = parse_persona_file(spec_path)
        quality_fm, _ = parse_persona_file(quality_path)
        shared = set(spec_fm.traits) & set(quality_fm.traits)
        self.assertEqual(shared, set(), f"Trait clusters overlap: {shared}")


# ---------------------------------------------------------------------------
# OBPI-0.0.13-01: Portable Persona Schema (REQ-0.0.13-01-*)
# ---------------------------------------------------------------------------


class TestPortableSchemaStructure(unittest.TestCase):
    """REQ-0.0.13-01-01: Schema is a valid JSON Schema document."""

    @covers("REQ-0.0.13-01-01")
    def test_schema_loads_and_has_required_keys(self) -> None:
        from gzkit.schemas import load_schema

        schema = load_schema("persona")
        self.assertEqual(schema["$schema"], "https://json-schema.org/draft/2020-12/schema")
        self.assertIn("title", schema)
        self.assertIn("properties", schema)
        self.assertIn("frontmatter", schema["properties"])

    @covers("REQ-0.0.13-01-01")
    def test_schema_has_version_id(self) -> None:
        from gzkit.schemas import load_schema

        schema = load_schema("persona")
        self.assertTrue(schema["$id"].startswith("gzkit.persona.v"))


class TestSchemaRequiredFields(unittest.TestCase):
    """REQ-0.0.13-01-02: Schema declares the four required persona fields."""

    @covers("REQ-0.0.13-01-02")
    def test_schema_declares_required_fields(self) -> None:
        from gzkit.schemas import load_schema

        schema = load_schema("persona")
        fm_schema = schema["properties"]["frontmatter"]
        required = set(fm_schema["required"])
        self.assertEqual(required, {"name", "traits", "anti-traits", "grounding"})

    @covers("REQ-0.0.13-01-02")
    def test_schema_rejects_additional_properties(self) -> None:
        from gzkit.schemas import load_schema

        schema = load_schema("persona")
        fm_schema = schema["properties"]["frontmatter"]
        self.assertFalse(fm_schema.get("additionalProperties", True))

    @covers("REQ-0.0.13-01-02")
    def test_pydantic_rejects_missing_field(self) -> None:
        """Pydantic enforces the same required fields at runtime."""
        from pydantic import ValidationError as PydanticValidationError

        for field in ("name", "traits", "anti-traits", "grounding"):
            with self.subTest(missing=field):
                complete = {
                    "name": "test",
                    "traits": ["a"],
                    "anti-traits": ["b"],
                    "grounding": "anchor text",
                }
                del complete[field]
                with self.assertRaises(PydanticValidationError):
                    PersonaFrontmatter(**complete)


class TestExistingPersonasValidate(unittest.TestCase):
    """REQ-0.0.13-01-03: All 6 shipped persona files validate against schema."""

    _PERSONA_DIR = Path(".gzkit/personas")
    _EXPECTED_COUNT = 6

    @covers("REQ-0.0.13-01-03")
    def test_all_shipped_personas_pass_schema(self) -> None:
        from gzkit.models.persona import discover_persona_files
        from gzkit.schemas import load_schema

        schema = load_schema("persona")
        fm_schema = schema["properties"]["frontmatter"]
        required_fields = set(fm_schema["required"])

        files = discover_persona_files(self._PERSONA_DIR)
        self.assertEqual(
            len(files),
            self._EXPECTED_COUNT,
            f"Expected {self._EXPECTED_COUNT} personas, found {len(files)}",
        )
        for persona_path in files:
            with self.subTest(persona=persona_path.name):
                fm, _body = parse_persona_file(persona_path)
                fm_dict = {
                    "name": fm.name,
                    "traits": fm.traits,
                    "anti-traits": fm.anti_traits,
                    "grounding": fm.grounding,
                }
                self.assertTrue(
                    required_fields.issubset(fm_dict.keys()),
                    f"{persona_path.name}: missing fields {required_fields - fm_dict.keys()}",
                )


class TestSchemaPortability(unittest.TestCase):
    """REQ-0.0.13-01-04: Schema contains no gzkit-specific references."""

    _GZKIT_TERMS = [
        "pipeline",
        "skill",
        "src/gzkit",
        "gzkit.commands",
        "gzkit.models",
        "obpi",
        "adr",
        "gz init",
        "gz agent",
    ]

    @covers("REQ-0.0.13-01-04")
    def test_no_gzkit_specific_references(self) -> None:
        from gzkit.schemas import get_schema_path

        schema_text = get_schema_path("persona").read_text(encoding="utf-8")
        for term in self._GZKIT_TERMS:
            self.assertNotIn(
                term.lower(),
                schema_text.lower(),
                f"Schema contains gzkit-specific reference: '{term}'",
            )


class TestSchemaModelAlignment(unittest.TestCase):
    """REQ-0.0.13-01-05: Schema required fields match PersonaFrontmatter."""

    @covers("REQ-0.0.13-01-05")
    def test_schema_fields_match_model(self) -> None:
        from gzkit.models.persona import PersonaFrontmatter
        from gzkit.schemas import load_schema

        schema = load_schema("persona")
        fm_schema = schema["properties"]["frontmatter"]
        schema_required = set(fm_schema["required"])
        schema_props = set(fm_schema["properties"].keys())

        model_fields = set()
        for field_name, field_info in PersonaFrontmatter.model_fields.items():
            alias = field_info.alias
            model_fields.add(alias if alias else field_name)

        self.assertEqual(
            schema_required,
            model_fields,
            f"Schema required {schema_required} != model fields {model_fields}",
        )
        self.assertEqual(
            schema_props,
            model_fields,
            f"Schema properties {schema_props} != model fields {model_fields}",
        )


if __name__ == "__main__":
    unittest.main()
