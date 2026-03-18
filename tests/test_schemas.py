"""Cross-validation tests: Pydantic models ↔ JSON schemas never drift.

@covers ADR-0.15.0  OBPI-0.15.0-04 schema-generation-unification
"""

import unittest
from typing import Literal, get_args, get_origin

from pydantic import BaseModel

from gzkit.events import (
    AdrCreatedEvent,
    ArtifactEditedEvent,
    ArtifactRenamedEvent,
    AttestedEvent,
    AuditReceiptEmittedEvent,
    CloseoutInitiatedEvent,
    ConstitutionCreatedEvent,
    GateCheckedEvent,
    ObpiCreatedEvent,
    ObpiReceiptEmittedEvent,
    PrdCreatedEvent,
    ProjectInitEvent,
)
from gzkit.models.frontmatter import AdrFrontmatter, ObpiFrontmatter, PrdFrontmatter
from gzkit.schemas import get_schema_path, load_schema

# ---------------------------------------------------------------------------
# Helper: extract Pydantic model's required field names (no defaults)
# ---------------------------------------------------------------------------


def _pydantic_required_fields(model: type[BaseModel]) -> set[str]:
    """Return field names that are required (no default) in a Pydantic model."""
    required = set()
    for name, field_info in model.model_fields.items():
        if field_info.is_required():
            required.add(name)
    return required


def _pydantic_field_pattern(model: type[BaseModel], field: str) -> str | None:
    """Return the regex pattern constraint on a Pydantic field, if any."""
    field_info = model.model_fields.get(field)
    if field_info is None:
        return None
    for meta in field_info.metadata:
        if hasattr(meta, "pattern"):
            return meta.pattern
    return None


def _pydantic_literal_values(model: type[BaseModel], field: str) -> set[str] | None:
    """Return the set of Literal values for a field, or None if not Literal."""
    field_info = model.model_fields.get(field)
    if field_info is None:
        return None
    annotation = field_info.annotation
    if get_origin(annotation) is Literal:
        return set(get_args(annotation))
    return None


# ---------------------------------------------------------------------------
# Frontmatter model ↔ schema cross-validation
# ---------------------------------------------------------------------------


class TestFrontmatterSchemaAlignment(unittest.TestCase):
    """Verify Pydantic frontmatter models match their JSON schemas."""

    def _check_required_fields(
        self,
        model: type[BaseModel],
        schema_name: str,
    ) -> None:
        """Required fields in schema ⊆ required fields in model."""
        schema = load_schema(schema_name)
        fm_schema = schema.get("properties", {}).get("frontmatter", {})
        schema_required = set(fm_schema.get("required", []))
        model_required = _pydantic_required_fields(model)
        # schema_ → schema mapping: model uses 'schema_' for 'schema' key
        normalized_model = {f.rstrip("_") for f in model_required}
        missing = schema_required - normalized_model
        self.assertFalse(
            missing,
            f"{model.__name__} is missing schema-required fields: {missing}",
        )

    def _check_enum_fields(
        self,
        model: type[BaseModel],
        schema_name: str,
    ) -> None:
        """Enum constraints in schema match Literal values in model."""
        schema = load_schema(schema_name)
        fm_fields = schema.get("properties", {}).get("frontmatter", {}).get("properties", {})
        for field_name, field_schema in fm_fields.items():
            if "enum" not in field_schema:
                continue
            schema_enum = set(field_schema["enum"])
            model_literals = _pydantic_literal_values(model, field_name)
            if model_literals is None:
                continue  # Field may use str (e.g., 'parent') without enum
            self.assertEqual(
                schema_enum,
                model_literals,
                f"{model.__name__}.{field_name} Literal values diverge from schema enum",
            )

    def _check_pattern_fields(
        self,
        model: type[BaseModel],
        schema_name: str,
    ) -> None:
        """Pattern constraints in schema match pattern metadata in model."""
        schema = load_schema(schema_name)
        fm_fields = schema.get("properties", {}).get("frontmatter", {}).get("properties", {})
        for field_name, field_schema in fm_fields.items():
            if "pattern" not in field_schema:
                continue
            schema_pattern = field_schema["pattern"]
            model_pattern = _pydantic_field_pattern(model, field_name)
            if model_pattern is None:
                continue
            self.assertEqual(
                schema_pattern,
                model_pattern,
                f"{model.__name__}.{field_name} pattern diverges from schema",
            )

    # -- ADR --

    def test_adr_required_fields_match(self) -> None:
        self._check_required_fields(AdrFrontmatter, "adr")

    def test_adr_enum_values_match(self) -> None:
        self._check_enum_fields(AdrFrontmatter, "adr")

    def test_adr_pattern_constraints_match(self) -> None:
        self._check_pattern_fields(AdrFrontmatter, "adr")

    # -- OBPI --

    def test_obpi_required_fields_match(self) -> None:
        self._check_required_fields(ObpiFrontmatter, "obpi")

    def test_obpi_enum_values_match(self) -> None:
        self._check_enum_fields(ObpiFrontmatter, "obpi")

    def test_obpi_pattern_constraints_match(self) -> None:
        self._check_pattern_fields(ObpiFrontmatter, "obpi")

    # -- PRD --

    def test_prd_required_fields_match(self) -> None:
        self._check_required_fields(PrdFrontmatter, "prd")

    def test_prd_enum_values_match(self) -> None:
        self._check_enum_fields(PrdFrontmatter, "prd")

    def test_prd_pattern_constraints_match(self) -> None:
        self._check_pattern_fields(PrdFrontmatter, "prd")


# ---------------------------------------------------------------------------
# Ledger event model ↔ ledger.json cross-validation
# ---------------------------------------------------------------------------

# Maps ledger.json event names → typed event model classes
_EVENT_MODELS: dict[str, type[BaseModel]] = {
    "project_init": ProjectInitEvent,
    "prd_created": PrdCreatedEvent,
    "constitution_created": ConstitutionCreatedEvent,
    "obpi_created": ObpiCreatedEvent,
    "adr_created": AdrCreatedEvent,
    "artifact_edited": ArtifactEditedEvent,
    "attested": AttestedEvent,
    "gate_checked": GateCheckedEvent,
    "closeout_initiated": CloseoutInitiatedEvent,
    "audit_receipt_emitted": AuditReceiptEmittedEvent,
    "obpi_receipt_emitted": ObpiReceiptEmittedEvent,
    "artifact_renamed": ArtifactRenamedEvent,
}

# Base fields present on _EventBase — not event-specific
_BASE_FIELDS = {"schema_", "event", "id", "ts", "parent"}


class TestLedgerSchemaAlignment(unittest.TestCase):
    """Verify typed event models match ledger.json event definitions."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.schema = load_schema("ledger")
        cls.event_rules = cls.schema.get("events", {})

    def test_all_schema_events_have_models(self) -> None:
        """Every event type in ledger.json has a corresponding Pydantic model."""
        schema_events = set(self.event_rules.keys())
        model_events = set(_EVENT_MODELS.keys())
        missing = schema_events - model_events
        self.assertFalse(
            missing,
            f"ledger.json events without Pydantic models: {missing}",
        )

    def test_all_models_have_schema_events(self) -> None:
        """Every event model maps to an event type in ledger.json."""
        schema_events = set(self.event_rules.keys())
        model_events = set(_EVENT_MODELS.keys())
        extra = model_events - schema_events
        self.assertFalse(
            extra,
            f"Pydantic event models without ledger.json entries: {extra}",
        )

    def test_required_fields_per_event(self) -> None:
        """Schema-required fields for each event ⊆ model fields (required or base)."""
        for event_name, rules in self.event_rules.items():
            model_cls = _EVENT_MODELS.get(event_name)
            if model_cls is None:
                continue
            schema_required = set(rules.get("required", []))
            # All model fields (including base) — normalize schema_ → schema
            all_fields = {f.rstrip("_") for f in model_cls.model_fields}
            missing = schema_required - all_fields
            with self.subTest(event=event_name):
                self.assertFalse(
                    missing,
                    f"{model_cls.__name__} missing required fields: {missing}",
                )

    def test_schema_event_properties_present_on_model(self) -> None:
        """All properties declared in ledger.json exist as model fields."""
        for event_name, rules in self.event_rules.items():
            model_cls = _EVENT_MODELS.get(event_name)
            if model_cls is None:
                continue
            schema_props = set(rules.get("properties", {}).keys())
            # Include base fields — some events reuse 'parent' as event-specific
            all_model_fields = {f.rstrip("_") for f in model_cls.model_fields}
            missing = schema_props - all_model_fields
            with self.subTest(event=event_name):
                self.assertFalse(
                    missing,
                    f"{model_cls.__name__} missing schema properties: {missing}",
                )

    def test_base_required_fields(self) -> None:
        """Top-level required fields (schema, event, id, ts) present on all models."""
        base_required = set(self.schema.get("required", []))
        for event_name, model_cls in _EVENT_MODELS.items():
            all_fields = set(model_cls.model_fields.keys())
            # Normalize schema_ → schema
            normalized = {f.rstrip("_") for f in all_fields}
            missing = base_required - normalized
            with self.subTest(event=event_name):
                self.assertFalse(
                    missing,
                    f"{model_cls.__name__} missing base required fields: {missing}",
                )


# ---------------------------------------------------------------------------
# Schema loading regression tests
# ---------------------------------------------------------------------------

_ALL_SCHEMAS = ["manifest", "adr", "obpi", "prd", "ledger", "agents"]


class TestSchemaLoading(unittest.TestCase):
    """Verify load_schema() and get_schema_path() work for all schemas."""

    def test_load_schema_all(self) -> None:
        """load_schema() returns a dict for every registered schema."""
        for name in _ALL_SCHEMAS:
            with self.subTest(schema=name):
                schema = load_schema(name)
                self.assertIsInstance(schema, dict)

    def test_get_schema_path_all(self) -> None:
        """get_schema_path() returns a path that exists for every schema."""
        for name in _ALL_SCHEMAS:
            with self.subTest(schema=name):
                path = get_schema_path(name)
                self.assertTrue(path.exists(), f"{path} does not exist")

    def test_load_schema_not_found(self) -> None:
        """load_schema() raises FileNotFoundError for unknown schemas."""
        with self.assertRaises(FileNotFoundError):
            load_schema("nonexistent_schema_xyz")


if __name__ == "__main__":
    unittest.main()
