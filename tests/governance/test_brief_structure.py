"""Tests for BriefStructure model and parse_brief loader (OBPI-0.0.37-04).

REQ-derived assertions for:
  REQ-0.0.37-04-01: frozen Pydantic BriefStructure model with all named fields
  REQ-0.0.37-04-02: JSON Schema mirror with additionalProperties: false
  REQ-0.0.37-04-03: parse_brief permissive mode returns BriefStructure or LegacyBriefShape+warning
  REQ-0.0.37-04-04: parse_brief strict=True raises ValueError on legacy brief
  REQ-0.0.37-04-05: round-trip parse of OBPI-0.0.37-04 brief itself returns BriefStructure
"""

from __future__ import annotations

import json
import re
import unittest
import warnings
from pathlib import Path

import jsonschema
from pydantic import ValidationError

from gzkit.governance.brief_structure import (
    BRIEF_TERMINAL_STATUSES,
    BriefStructure,
    LegacyBriefShape,
    is_terminal_brief_status,
    parse_brief,
)
from gzkit.traceability import covers

FIXTURES = Path(__file__).parent.parent / "fixtures" / "brief_structure"
SCHEMA_PATH = (
    Path(__file__).parent.parent.parent / "src" / "gzkit" / "schemas" / "obpi_brief_structure.json"
)
THIS_BRIEF = (
    Path(__file__).parent.parent.parent
    / "docs"
    / "design"
    / "adr"
    / "foundation"
    / "ADR-0.0.37-constitutional-invariant-composition"
    / "obpis"
    / "OBPI-0.0.37-04-brief-structural-schema.md"
)

_VALID_FIELDS = {
    "id": "OBPI-0.0.37-04-brief-structural-schema",
    "parent": "ADR-0.0.37-constitutional-invariant-composition",
    "lane": "Heavy",
    "status": "Draft",
    "allowlist": ["src/x.py"],
    "reqs": ["REQ-0.0.37-04-01"],
    "verification": ["uv run gz lint"],
    "citations": [],
}


class TestBriefStructureModel(unittest.TestCase):
    """REQ-0.0.37-04-01: frozen model with all named fields."""

    @covers("REQ-0.0.37-04-01")
    def test_model_is_frozen(self) -> None:
        b = BriefStructure(**_VALID_FIELDS)
        with self.assertRaises((ValueError, TypeError)):
            b.id = "MUTATED"  # type: ignore

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_allowlist(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "allowlist": []})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_reqs(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "reqs": []})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_empty_verification(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "verification": []})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_extra_fields(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**_VALID_FIELDS, unexpected_field="bad")  # type: ignore

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_invalid_id(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "id": "not-a-valid-obpi-id"})

    @covers("REQ-0.0.37-04-01")
    def test_model_rejects_invalid_req_format(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "reqs": ["bad-format"]})

    @covers("REQ-0.0.37-04-01")
    def test_model_accepts_active_in_flight_status(self) -> None:
        """In-flight briefs carry status Active without degrading to legacy shape (GHI #646).

        ``status_vocab`` maps ledger state ``in_progress`` -> frontmatter ``Active``.
        Once a launched OBPI derives ``in_progress``, ``frontmatter reconcile`` writes
        ``Active`` into the brief. The structural schema MUST admit Active so an
        in-flight *structured* brief stays structured -- otherwise it drops to
        ``LegacyBriefShape`` and silently disables reconcile drift-escalation during
        the exact window it is most valuable.
        """
        b = BriefStructure(**{**_VALID_FIELDS, "status": "Active"})
        self.assertEqual(b.status, "Active")

    @covers("REQ-0.0.37-04-01")
    def test_model_accepts_citations_list(self) -> None:
        b = BriefStructure(**{**_VALID_FIELDS, "citations": [("src/x.py", "#anchor")]})
        self.assertEqual(b.citations, [("src/x.py", "#anchor")])

    def test_tasks_optional_defaults_empty(self) -> None:
        """tasks field is optional and defaults to empty list (OBPI-0.0.64-04)."""
        b = BriefStructure(**_VALID_FIELDS)
        self.assertEqual(b.tasks, [])

    def test_tasks_accepts_list_of_strings(self) -> None:
        """tasks field accepts a list of TASK ID strings (OBPI-0.0.64-04)."""
        b = BriefStructure(**{**_VALID_FIELDS, "tasks": ["TASK-0.0.64-04-01-01"]})
        self.assertEqual(b.tasks, ["TASK-0.0.64-04-01-01"])

    def test_req_atomic_optional_defaults_empty(self) -> None:
        """req_atomic field is optional and defaults to empty list (OBPI-0.0.64-04)."""
        b = BriefStructure(**_VALID_FIELDS)
        self.assertEqual(b.req_atomic, [])

    def test_req_atomic_accepts_list_of_strings(self) -> None:
        """req_atomic accepts a list of REQ ID strings (OBPI-0.0.64-04)."""
        b = BriefStructure(**{**_VALID_FIELDS, "req_atomic": ["REQ-0.0.64-04-01"]})
        self.assertEqual(b.req_atomic, ["REQ-0.0.64-04-01"])


class TestTasksSchemaEnforcement(unittest.TestCase):
    """GHI #753: the ``tasks:`` channel rejects malformed TASK IDs.

    ``.gzkit/rules/task-discovery.md`` § Convention: Frontmatter ``tasks:``
    declares the field carries TASK IDs. Its three sibling identifier fields
    (``id``, ``parent``, ``reqs``) each validate their grammar; ``tasks`` did
    not, so a malformed entry parsed clean into a frozen model that downstream
    channel comparison then treats as a declaration.
    """

    def test_rejects_malformed_task_id(self) -> None:
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "tasks": ["not-a-task-id"]})

    def test_rejects_req_id_in_tasks(self) -> None:
        """A REQ ID is the near-miss an author actually types; it is not a TASK ID."""
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "tasks": ["REQ-0.0.64-04-01"]})

    def test_rejects_truncated_task_id(self) -> None:
        """TASK IDs are four-tier; a three-tier id names no labor unit."""
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "tasks": ["TASK-0.0.64-04-01"]})

    def test_rejects_malformed_entry_among_valid_ones(self) -> None:
        """Validation is per-entry -- one bad id in a good list still fails."""
        with self.assertRaises(ValidationError):
            BriefStructure(**{**_VALID_FIELDS, "tasks": ["TASK-0.0.64-04-01-01", "TASK-bogus"]})

    def test_accepts_well_formed_formal_task_id(self) -> None:
        b = BriefStructure(**{**_VALID_FIELDS, "tasks": ["TASK-0.0.64-04-01-01"]})
        self.assertEqual(b.tasks, ["TASK-0.0.64-04-01-01"])

    def test_accepts_producer_stamped_multi_req_accumulation(self) -> None:
        """``gz task start`` accumulates one TASK per REQ into the same brief (GHI #752)."""
        stamped = ["TASK-0.0.64-04-01-01", "TASK-0.0.64-04-02-01"]
        b = BriefStructure(**{**_VALID_FIELDS, "tasks": stamped})
        self.assertEqual(b.tasks, stamped)

    def test_empty_tasks_still_valid(self) -> None:
        """The overwhelming majority of briefs predate the producer stamp."""
        b = BriefStructure(**{**_VALID_FIELDS, "tasks": []})
        self.assertEqual(b.tasks, [])

    def test_pydantic_and_json_schema_readers_agree(self) -> None:
        """Both readers of the ``tasks:`` shape accept and reject the same ids.

        The defect class ``ADR-pool.governance-document-structural-validation``
        catalogues is N independently-authored readers of one document shape,
        free to disagree, with nothing asserting they agree. This model and the
        JSON Schema mirror are two such readers; this is the assertion.
        """
        schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
        pattern = re.compile(schema["properties"]["tasks"]["items"]["pattern"])
        cases = [
            "TASK-0.0.64-04-01-01",
            "TASK-0.34.0-03-02-11",
            "not-a-task-id",
            "REQ-0.0.64-04-01",
            "TASK-0.0.64-04-01",
            "TASK-0.0.64-04-01-01-01",
            "task-0.0.64-04-01-01",
            "",
        ]
        for raw in cases:
            with self.subTest(task_id=raw):
                json_ok = pattern.match(raw) is not None
                try:
                    BriefStructure(**{**_VALID_FIELDS, "tasks": [raw]})
                except ValidationError:
                    model_ok = False
                else:
                    model_ok = True
                self.assertEqual(
                    model_ok,
                    json_ok,
                    f"readers disagree on {raw!r}: model={model_ok}, json-schema={json_ok}",
                )


class TestBriefStructureJsonSchema(unittest.TestCase):
    """REQ-0.0.37-04-02: JSON Schema mirror."""

    def _schema(self) -> dict:
        return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))

    @covers("REQ-0.0.37-04-02")
    def test_schema_has_additional_properties_false(self) -> None:
        schema = self._schema()
        self.assertIs(schema.get("additionalProperties"), False)

    @covers("REQ-0.0.37-04-02")
    def test_schema_validates_compliant_instance(self) -> None:
        schema = self._schema()
        instance = {
            "id": "OBPI-0.0.1-01-test-fixture",
            "parent": "ADR-0.0.1-test-fixture",
            "lane": "Heavy",
            "status": "Draft",
            "allowlist": ["src/x.py"],
            "reqs": ["REQ-0.0.1-01-01"],
            "verification": ["uv run gz lint"],
            "citations": [],
        }
        jsonschema.validate(instance, schema)  # must not raise

    @covers("REQ-0.0.37-04-02")
    def test_schema_admits_active_status(self) -> None:
        """JSON Schema mirror admits the Active in-flight status (GHI #646)."""
        schema = self._schema()
        instance = {
            "id": "OBPI-0.0.1-01-test-fixture",
            "parent": "ADR-0.0.1-test-fixture",
            "lane": "Heavy",
            "status": "Active",
            "allowlist": ["src/x.py"],
            "reqs": ["REQ-0.0.1-01-01"],
            "verification": ["uv run gz lint"],
            "citations": [],
        }
        jsonschema.validate(instance, schema)  # must not raise

    @covers("REQ-0.0.37-04-02")
    def test_schema_rejects_missing_reqs(self) -> None:
        schema = self._schema()
        instance = {
            "id": "OBPI-0.0.1-01-test-fixture",
            "parent": "ADR-0.0.1-test-fixture",
            "lane": "Heavy",
            "status": "Draft",
            "allowlist": ["src/x.py"],
            "verification": ["uv run gz lint"],
            "citations": [],
        }
        with self.assertRaises(jsonschema.ValidationError):
            jsonschema.validate(instance, schema)


class TestBriefStatusVocabulary(unittest.TestCase):
    """GHI #615: the schema's status vocabulary must match the one the runtime writes.

    ``BriefStructure.status`` shipped as ``Literal["Draft", "Active",
    "Validated", "Completed"]`` -- authored against an imagined lifecycle rather
    than a measured one. It admitted two spellings the corpus has never used and
    rejected every brief carrying ``attested_completed`` (198 of them),
    ``Abandoned`` (13), ``Withdrawn`` (2), or ``in_progress`` (1). A schema that
    rejects a third of the corpus it governs could never be enforced, which is a
    material part of why it never was.

    Asserted against ``BRIEF_TERMINAL_STATUSES`` -- the vocabulary the runtime
    already treats as authoritative -- rather than a hand-copied list, so the two
    cannot drift back apart.
    """

    def test_every_terminal_status_is_accepted(self) -> None:
        for status in sorted(BRIEF_TERMINAL_STATUSES):
            with self.subTest(status=status):
                brief = BriefStructure(
                    id="OBPI-0.1.0-01-x",
                    parent="ADR-0.1.0-x",
                    lane="Lite",
                    status=status,
                    allowlist=["src/x.py"],
                    reqs=["REQ-0.1.0-01-01"],
                    verification=["test -f src/x.py"],
                )
                self.assertEqual(brief.status, status)

    def test_unknown_status_is_rejected(self) -> None:
        """The widening admits the real vocabulary; it does not admit anything."""
        with self.assertRaises(ValidationError):
            BriefStructure(
                id="OBPI-0.1.0-01-x",
                parent="ADR-0.1.0-x",
                lane="Lite",
                status="banana",
                allowlist=["src/x.py"],
                reqs=["REQ-0.1.0-01-01"],
                verification=["test -f src/x.py"],
            )


class TestParseBriefPermissive(unittest.TestCase):
    """REQ-0.0.37-04-03: permissive mode behavior."""

    @covers("REQ-0.0.37-04-03")
    def test_compliant_brief_returns_brief_structure(self) -> None:
        result = parse_brief(FIXTURES / "compliant.md")
        self.assertIsInstance(result, BriefStructure)

    @covers("REQ-0.0.37-04-03")
    def test_compliant_brief_no_deprecation_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(FIXTURES / "compliant.md")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertEqual(deprecations, [])

    @covers("REQ-0.0.37-04-03")
    def test_legacy_brief_returns_legacy_shape(self) -> None:
        with warnings.catch_warnings(record=True):
            warnings.simplefilter("always")
            result = parse_brief(FIXTURES / "legacy.md")
        self.assertIsInstance(result, LegacyBriefShape)

    @covers("REQ-0.0.37-04-03")
    def test_legacy_brief_emits_deprecation_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(FIXTURES / "legacy.md")
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertGreater(len(deprecations), 0)


class TestParseBriefStrict(unittest.TestCase):
    """REQ-0.0.37-04-04: strict=True raises ValueError on legacy brief."""

    @covers("REQ-0.0.37-04-04")
    def test_strict_raises_on_legacy_brief(self) -> None:
        with self.assertRaises(ValueError):
            parse_brief(FIXTURES / "legacy.md", strict=True)

    @covers("REQ-0.0.37-04-04")
    def test_strict_succeeds_on_compliant_brief(self) -> None:
        result = parse_brief(FIXTURES / "compliant.md", strict=True)
        self.assertIsInstance(result, BriefStructure)


class TestParseBriefRoundTrip(unittest.TestCase):
    """REQ-0.0.37-04-05: round-trip on OBPI-0.0.37-04 brief itself."""

    @covers("REQ-0.0.37-04-05")
    def test_this_brief_parses_as_brief_structure(self) -> None:
        result = parse_brief(THIS_BRIEF)
        self.assertIsInstance(result, BriefStructure)

    @covers("REQ-0.0.37-04-05")
    def test_this_brief_no_deprecation_warning(self) -> None:
        with warnings.catch_warnings(record=True) as caught:
            warnings.simplefilter("always")
            parse_brief(THIS_BRIEF)
        deprecations = [w for w in caught if issubclass(w.category, DeprecationWarning)]
        self.assertEqual(deprecations, [])


if __name__ == "__main__":
    unittest.main()


class TestTerminalBriefStatus(unittest.TestCase):
    """One predicate both consumers share (GHI #707 follow-up).

    `--brief-command-shape` matched the frozenset by exact string while the
    reconcile engine casefolded, so the corpus's two spellings of `withdrawn`
    resolved differently depending on which validator asked. A single predicate
    removes the divergence rather than duplicating the casefold.
    """

    def test_sealed_lifecycle_statuses_are_terminal(self) -> None:
        for status in (
            "Completed",
            "attested_completed",
            "Validated",
            "Superseded",
            "archived",
            "Promoted",
        ):
            with self.subTest(status=status):
                self.assertTrue(is_terminal_brief_status(status))

    def test_abandoned_and_withdrawn_are_terminal(self) -> None:
        """No future work is done on either — the sealed-record logic applies."""
        for status in ("Abandoned", "Withdrawn"):
            with self.subTest(status=status):
                self.assertTrue(is_terminal_brief_status(status))

    def test_matching_is_case_insensitive(self) -> None:
        """The corpus carries both `Withdrawn` and `withdrawn`."""
        self.assertTrue(is_terminal_brief_status("withdrawn"))
        self.assertTrue(is_terminal_brief_status("COMPLETED"))

    def test_quoted_and_padded_values_resolve(self) -> None:
        self.assertTrue(is_terminal_brief_status('  "Completed"  '))

    def test_live_statuses_are_not_terminal(self) -> None:
        for status in ("Draft", "Active", "in_progress", ""):
            with self.subTest(status=status):
                self.assertFalse(is_terminal_brief_status(status))
