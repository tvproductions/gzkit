"""REQ-derived tests for the OKF concept-frontmatter model (OBPI-0.30.0-01).

Assertions are derived from the brief's Requirements (FAIL-CLOSED) and the
parent ADR's Boundary Invariant 3 (OKF posture), NOT from a run of the
implementation (`.gzkit/rules/tests.md` § "Tests assert semantics, not
strings").

The contract under test:
  - `type` is the ONE required field (non-empty string, free-form — no enum).
  - title/description/resource/tags/timestamp are optional.
  - OKF posture: unknown producer-defined fields AND unknown `type` values are
    NOT errors (Boundary Invariant 3).
  - A JSON schema mirror exists under src/gzkit/schemas/ and loads clean.
"""

import unittest

from pydantic import ValidationError

from gzkit.knowledge import ConceptFrontmatter
from gzkit.schemas import load_schema
from gzkit.traceability import covers


class TestConceptFrontmatterModel(unittest.TestCase):
    """OKF concept-frontmatter model — REQ-derived behavior."""

    @covers("REQ-0.30.0-01-01")
    def test_type_only_document_validates_and_exposes_type(self) -> None:
        """REQ-01: a non-empty `type` with no other fields validates."""
        model = ConceptFrontmatter(type="doctrine")
        self.assertEqual(model.type, "doctrine")

    @covers("REQ-0.30.0-01-02")
    def test_missing_type_is_rejected(self) -> None:
        """REQ-02: a mapping missing `type` fails validation."""
        with self.assertRaises(ValidationError):
            ConceptFrontmatter()

    @covers("REQ-0.30.0-01-02")
    def test_empty_type_is_rejected(self) -> None:
        """REQ-02: an empty-string `type` fails validation (non-empty required)."""
        with self.assertRaises(ValidationError):
            ConceptFrontmatter(type="")

    def test_all_optional_fields_accepted(self) -> None:
        """Supplementary contract guard: optional fields round-trip.

        Intentionally UNDECORATED. This asserts the "accept the optional fields"
        clause of the brief's FAIL-CLOSED Requirement #2, which has no distinct
        acceptance-criteria REQ-ID: REQ-01 is strictly "non-empty `type` and NO
        other fields" (covered by test_type_only_document_validates_and_exposes_type
        above), and REQ-02 is the rejection behavior. Decorating this test with
        either would over-attribute REQ coverage (flagged by the Codex adversary,
        GHI #643 Stage-4b). It stays as a defensive round-trip guard, not a
        REQ-coverage claim.
        """
        model = ConceptFrontmatter(
            type="doctrine",
            title="State Doctrine",
            description="Layer-3 views are never source-of-truth.",
            resource="docs/governance/state-doctrine.md",
            tags=["governance", "state"],
            timestamp="2026-06-28",
        )
        self.assertEqual(model.title, "State Doctrine")
        self.assertEqual(model.tags, ["governance", "state"])
        self.assertEqual(model.resource, "docs/governance/state-doctrine.md")

    @covers("REQ-0.30.0-01-03")
    def test_posture_unknown_field_and_unknown_type_accepted(self) -> None:
        """REQ-03: unknown producer field + unknown `type` value both tolerated.

        Boundary Invariant 3 — `type` is a free string (not a closed enum) and
        producer-defined keys are accepted, so neither is an error.
        """
        model = ConceptFrontmatter(type="totally-novel-doctype", producer_key="x")
        self.assertEqual(model.type, "totally-novel-doctype")
        # The unknown field is retained (extra="allow"), not dropped.
        self.assertEqual(model.model_dump()["producer_key"], "x")

    def test_json_schema_mirror_loads_and_matches_posture(self) -> None:
        """Structural guard: the schema mirror loads and encodes the OKF contract.

        REQ-0.30.0-01-04 is [SUPPORT] — its proof channel is the ledger +
        `gz validate --documents` structural validator, NOT a `@covers` test
        (authoring one is the anti-pattern named in `.gzkit/rules/tests.md`
        § What this replaces). This test is therefore intentionally UNDECORATED:
        it is a defensive regression guard that the schema keeps encoding the
        posture (additionalProperties true, required == ['type'], minLength 1),
        not a REQ-coverage claim.
        """
        schema = load_schema("okf_concept_frontmatter")
        self.assertIsInstance(schema, dict)
        self.assertEqual(schema.get("required"), ["type"])
        # Posture tolerance: unknown producer keys are not rejected by the schema.
        self.assertTrue(schema.get("additionalProperties"))
        type_prop = schema["properties"]["type"]
        self.assertEqual(type_prop["type"], "string")
        self.assertEqual(type_prop.get("minLength"), 1)


if __name__ == "__main__":
    unittest.main()
