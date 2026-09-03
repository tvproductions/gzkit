"""Cross-validation tests: Pydantic models <-> JSON schemas never drift.

@covers ADR-0.15.0  OBPI-0.15.0-04 schema-generation-unification
@covers ADR-0.17.0  OBPI-0.17.0-04 json-schemas-and-validation
"""

import unittest
from pathlib import Path
from typing import Literal, get_args, get_origin

from pydantic import BaseModel

from gzkit.events import (
    AdrAnnotatedEvent,
    AdrCreatedEvent,
    AdrEvalCompletedEvent,
    AdrEvaluationEvent,
    AdversarialValidationEvent,
    AgentSyncCompletedEvent,
    AirlockInEvent,
    AirlockOutEvent,
    ArtifactEditedEvent,
    ArtifactRenamedEvent,
    AttestedEvent,
    AuditGeneratedEvent,
    AuditReceiptEmittedEvent,
    BlockedByEvent,
    BlocksEvent,
    BriefReconciledEvent,
    BriefReconcileDriftDetectedEvent,
    BriefReconcileDriftOverriddenEvent,
    ChoreDecommissionProcessedEvent,
    CloseoutInitiatedEvent,
    CompositionCandidateEmittedEvent,
    CompositionDriftDetectedEvent,
    CompositionRenderedEvent,
    ConstitutionCreatedEvent,
    CorpusEntryAppendedEvent,
    CorpusEntryRetiredEvent,
    CorpusRetirementReconciledEvent,
    DiscoveredFromEvent,
    DistributionBaselineRegeneratedEvent,
    EnforcementClaimVerifiedEvent,
    FoundationGrandfatheredEvent,
    GateCheckedEvent,
    HandoffResumeAuthorizedEvent,
    HandoffResumeBlockedEvent,
    HandoffResumeDecidedEvent,
    IntrinsicComplexityAttestationEvent,
    LifecycleTransitionEvent,
    MxSessionClosedEvent,
    MxSessionOpenedEvent,
    ObpiBlockedOnOperatorEvent,
    ObpiCompletionRepudiatedEvent,
    ObpiCompletionUncoveredAcceptEvent,
    ObpiCreatedEvent,
    ObpiLockClaimedEvent,
    ObpiLockReleasedEvent,
    ObpiLockTtlWarningEvent,
    ObpiParkedEvent,
    ObpiReceiptEmittedEvent,
    ObpiSupersededEvent,
    ObpiUnblockedEvent,
    ObpiUnparkedEvent,
    ObpiWithdrawnEvent,
    PatchReleaseEvent,
    PipelineLaunchedEvent,
    PipelineMarkerPurgedEvent,
    PrdCreatedEvent,
    ProjectInitEvent,
    RedReceiptEmittedEvent,
    RenditionAdvisorVerdictEvent,
    RenditionCommittedEvent,
    SectionOwnershipGenesisEvent,
    SectionOwnershipUnownedEvent,
    SecurityFloorOverriddenEvent,
    SessionExitBookmarkSkippedEvent,
    Stage2DispatchRecordedEvent,
    Stage2SingleDriverDeclaredEvent,
    SurfaceWeightRecalibratedEvent,
    TaskBlockedEvent,
    TaskCompletedEvent,
    TaskEscalatedEvent,
    TaskStartedEvent,
    UnownedRatchetUpdatedEvent,
    ValidatesEvent,
)
from gzkit.models.frontmatter import (
    AdrFrontmatter,
    ObpiFrontmatter,
    PrdFrontmatter,
)
from gzkit.schemas import get_schema_path, load_schema
from gzkit.traceability import covers  # noqa: F401

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


def _pydantic_field_max_length(model: type[BaseModel], field: str) -> int | None:
    """Return the max_length constraint on a Pydantic field, if any."""
    field_info = model.model_fields.get(field)
    if field_info is None:
        return None
    for meta in field_info.metadata:
        if hasattr(meta, "max_length"):
            return meta.max_length
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
# Frontmatter model <-> schema cross-validation
# ---------------------------------------------------------------------------


class TestFrontmatterSchemaAlignment(unittest.TestCase):
    """Verify Pydantic frontmatter models match their JSON schemas."""

    def _check_required_fields(
        self,
        model: type[BaseModel],
        schema_name: str,
    ) -> None:
        """Required fields in schema <= required fields in model."""
        schema = load_schema(schema_name)
        fm_schema = schema.get("properties", {}).get("frontmatter", {})
        schema_required = set(fm_schema.get("required", []))
        model_required = _pydantic_required_fields(model)
        # schema_ -> schema mapping: model uses 'schema_' for 'schema' key
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

    @covers("REQ-0.15.0-01-02")
    @covers("REQ-0.0.17-01-02")
    @covers("REQ-0.0.17-01-04")
    def test_adr_required_fields_match(self) -> None:
        self._check_required_fields(AdrFrontmatter, "adr")
        # REQ-0.0.17-01-02 / REQ-0.0.17-01-04: kind MUST be in the schema's
        # required set, and the helper above MUST have asserted on it.
        schema = load_schema("adr")
        schema_required = schema.get("properties", {}).get("frontmatter", {}).get("required", [])
        self.assertIn("kind", schema_required)

    @covers("REQ-0.0.17-01-01")
    @covers("REQ-0.0.17-01-04")
    def test_adr_enum_values_match(self) -> None:
        self._check_enum_fields(AdrFrontmatter, "adr")
        # REQ-0.0.17-01-01 / REQ-0.0.17-01-04: the kind enum MUST be present in
        # the schema and the helper above MUST have asserted its Literal match.
        schema = load_schema("adr")
        kind_schema = (
            schema.get("properties", {}).get("frontmatter", {}).get("properties", {}).get("kind")
        )
        self.assertIsNotNone(kind_schema, "schema is missing 'kind' property")
        assert kind_schema is not None
        self.assertEqual(set(kind_schema.get("enum", [])), {"foundation", "feature"})
        self.assertIn("description", kind_schema)
        self.assertTrue(kind_schema["description"].strip(), "kind description must be non-empty")

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
# Ledger event model <-> ledger.json cross-validation
# ---------------------------------------------------------------------------

# Maps ledger.json event names -> typed event model classes
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
    "adr_annotated": AdrAnnotatedEvent,
    "lifecycle_transition": LifecycleTransitionEvent,
    "agent_sync_completed": AgentSyncCompletedEvent,
    "distribution_baseline_regenerated": DistributionBaselineRegeneratedEvent,
    "adr_eval_completed": AdrEvalCompletedEvent,
    "adr-evaluation": AdrEvaluationEvent,
    "audit_generated": AuditGeneratedEvent,
    "obpi_lock_claimed": ObpiLockClaimedEvent,
    "obpi_lock_released": ObpiLockReleasedEvent,
    "obpi_lock_ttl_warning": ObpiLockTtlWarningEvent,
    "obpi_withdrawn": ObpiWithdrawnEvent,
    "obpi_superseded": ObpiSupersededEvent,
    "obpi_completion_repudiated": ObpiCompletionRepudiatedEvent,
    "security_floor_overridden": SecurityFloorOverriddenEvent,
    "obpi_completion_uncovered_accept": ObpiCompletionUncoveredAcceptEvent,
    "patch-release": PatchReleaseEvent,
    "pipeline_marker_purged": PipelineMarkerPurgedEvent,
    "pipeline_launched": PipelineLaunchedEvent,
    "intrinsic-complexity-attestation": IntrinsicComplexityAttestationEvent,
    "task_started": TaskStartedEvent,
    "task_completed": TaskCompletedEvent,
    "task_blocked": TaskBlockedEvent,
    "task_escalated": TaskEscalatedEvent,
    "composition_rendered": CompositionRenderedEvent,
    "composition_drift_detected": CompositionDriftDetectedEvent,
    "chore_decommission_processed": ChoreDecommissionProcessedEvent,
    "corpus_entry_appended": CorpusEntryAppendedEvent,
    "corpus_entry_retired": CorpusEntryRetiredEvent,
    # After-the-fact witness for a tombstone that bypassed `gz content retire`
    # (GHI #885) or survived a partial write (GHI #878)
    "corpus_retirement_reconciled": CorpusRetirementReconciledEvent,
    "composition_candidate_emitted": CompositionCandidateEmittedEvent,
    "rendition_committed": RenditionCommittedEvent,
    "rendition_advisor_verdict": RenditionAdvisorVerdictEvent,
    "brief_reconciled": BriefReconciledEvent,
    "brief_reconcile_drift_detected": BriefReconcileDriftDetectedEvent,
    "brief_reconcile_drift_overridden": BriefReconcileDriftOverriddenEvent,
    "enforcement_claim_verified": EnforcementClaimVerifiedEvent,
    "mx_session_opened": MxSessionOpenedEvent,
    "mx_session_closed": MxSessionClosedEvent,
    # Work-domain L2 edge events (ADR-0.32.0, OBPI-06)
    "blocks": BlocksEvent,
    "blocked_by": BlockedByEvent,
    "discovered_from": DiscoveredFromEvent,
    "validates": ValidatesEvent,
    # Airlock L2 edge events (ADR-0.33.0, OBPI-01)
    "adversarial_validation": AdversarialValidationEvent,
    "airlock_in": AirlockInEvent,
    "airlock_out": AirlockOutEvent,
    # Base-tree RED falsifiability witness (GHI #642)
    "red_receipt_emitted": RedReceiptEmittedEvent,
    # Operator ruling lifting the handoff resume gate (GHI #574)
    "handoff_resume_authorized": HandoffResumeAuthorizedEvent,
    # Successor carrying a transit decision rather than a consent boolean (GHI #757)
    "handoff_resume_decided": HandoffResumeDecidedEvent,
    "handoff_resume_blocked": HandoffResumeBlockedEvent,
    "session_exit_bookmark_skipped": SessionExitBookmarkSkippedEvent,
    # Surface-weight band/floor recalibration witness (ADR-0.0.33 AP#3, GHI #791)
    "surface_weight_recalibrated": SurfaceWeightRecalibratedEvent,
    # Reversible retirement of OBPIs whose parent ADR demoted to pool (GHI #584)
    "obpi_parked": ObpiParkedEvent,
    "obpi_blocked_on_operator": ObpiBlockedOnOperatorEvent,
    "obpi_unblocked": ObpiUnblockedEvent,
    "stage2_dispatch_recorded": Stage2DispatchRecordedEvent,
    "stage2_single_driver_declared": Stage2SingleDriverDeclaredEvent,
    # Section-ownership declaration and the decrease-only unowned-byte
    # ratchet (OBPI-0.35.0-04). Genesis is a witnessed ledger STATE, never
    # a self-coherent declaration shape an attacker can recompute.
    "section_ownership_genesis": SectionOwnershipGenesisEvent,
    "unowned_ratchet_updated": UnownedRatchetUpdatedEvent,
    "section_ownership_unowned": SectionOwnershipUnownedEvent,
    "obpi_unparked": ObpiUnparkedEvent,
    # Foundation Sunset terminality witness (ADR-0.34.0, OBPI-04)
    "foundation_grandfathered": FoundationGrandfatheredEvent,
}

# Base fields present on _EventBase -- not event-specific
_BASE_FIELDS = {"schema_", "event", "id", "ts", "parent"}


class TestLedgerSchemaAlignment(unittest.TestCase):
    """Verify typed event models match ledger.json event definitions."""

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.schema = load_schema("ledger")
        cls.event_rules = cls.schema.get("events", {})

    @covers("REQ-0.15.0-01-04")
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
        """Schema-required fields for each event <= model fields (required or base)."""
        for event_name, rules in self.event_rules.items():
            model_cls = _EVENT_MODELS.get(event_name)
            if model_cls is None:
                continue
            schema_required = set(rules.get("required", []))
            # All model fields (including base) -- normalize schema_ -> schema
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
            # Include base fields -- some events reuse 'parent' as event-specific
            all_model_fields = {f.rstrip("_") for f in model_cls.model_fields}
            missing = schema_props - all_model_fields
            with self.subTest(event=event_name):
                self.assertFalse(
                    missing,
                    f"{model_cls.__name__} missing schema properties: {missing}",
                )

    @covers("REQ-0.15.0-01-01")
    def test_base_required_fields(self) -> None:
        """Top-level required fields (schema, event, id, ts) present on all models."""
        base_required = set(self.schema.get("required", []))
        for event_name, model_cls in _EVENT_MODELS.items():
            all_fields = set(model_cls.model_fields.keys())
            # Normalize schema_ -> schema
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

    @covers("REQ-0.15.0-01-03")
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


# ---------------------------------------------------------------------------
# Control-surface model <-> .gzkit/schemas/ cross-validation
# ---------------------------------------------------------------------------


def _load_gzkit_schema(name: str) -> dict:
    """Load a JSON schema from .gzkit/schemas/ (Layer 1 canonical schemas)."""
    import json
    from pathlib import Path

    schema_path = Path(".gzkit") / "schemas" / f"{name}.schema.json"
    return json.loads(schema_path.read_text(encoding="utf-8"))


def _model_alias_map(model: type[BaseModel]) -> dict[str, str]:
    """Build schema-field-name -> model-field-name map from aliases.

    For fields without aliases, the mapping is identity.
    """
    mapping: dict[str, str] = {}
    for field_name, field_info in model.model_fields.items():
        alias = field_info.alias
        if alias is not None:
            mapping[alias] = field_name
        else:
            mapping[field_name] = field_name
    return mapping


def _resolve_field(model: type[BaseModel], schema_field: str) -> str | None:
    """Resolve a schema field name to the Pydantic model field name."""
    alias_map = _model_alias_map(model)
    return alias_map.get(schema_field)


class TestSkillSchemaAlignment(unittest.TestCase):
    """Verify SkillFrontmatter model matches .gzkit/schemas/skill.schema.json.

    @covers REQ-0.17.0-04-01
    @covers REQ-0.17.0-04-05
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        from gzkit.models.frontmatter import SkillFrontmatter

        cls.model = SkillFrontmatter
        cls.schema = _load_gzkit_schema("skill")

    @covers("REQ-0.17.0-04-03")
    @covers("REQ-0.17.0-04-05")
    def test_required_fields_match(self) -> None:
        """Schema-required fields are required in the Pydantic model."""
        schema_required = set(self.schema.get("required", []))
        model_required = _pydantic_required_fields(self.model)
        # Map schema field names to model field names via aliases
        resolved = set()
        for f in schema_required:
            model_field = _resolve_field(self.model, f)
            self.assertIsNotNone(
                model_field,
                f"Schema required field '{f}' has no corresponding model field",
            )
            resolved.add(model_field)
        missing = resolved - model_required
        self.assertFalse(
            missing,
            f"SkillFrontmatter missing required fields: {missing}",
        )

    @covers("REQ-0.17.0-04-05")
    def test_enum_values_match(self) -> None:
        """Enum constraints in schema match Literal values in model."""
        schema_props = self.schema.get("properties", {})
        for schema_field, field_schema in schema_props.items():
            if "enum" not in field_schema:
                continue
            schema_enum = set(field_schema["enum"])
            model_field = _resolve_field(self.model, schema_field)
            if model_field is None:
                continue
            model_literals = _pydantic_literal_values(self.model, model_field)
            if model_literals is None:
                continue
            with self.subTest(field=schema_field):
                self.assertEqual(
                    schema_enum,
                    model_literals,
                    f"SkillFrontmatter.{model_field} Literal values diverge "
                    f"from skill.schema.json '{schema_field}' enum",
                )

    @covers("REQ-0.17.0-04-05")
    def test_pattern_constraints_match(self) -> None:
        """Pattern constraints in schema match pattern metadata in model."""
        schema_props = self.schema.get("properties", {})
        for schema_field, field_schema in schema_props.items():
            if "pattern" not in field_schema:
                continue
            model_field = _resolve_field(self.model, schema_field)
            if model_field is None:
                continue
            model_pattern = _pydantic_field_pattern(self.model, model_field)
            if model_pattern is None:
                continue
            with self.subTest(field=schema_field):
                self.assertEqual(
                    field_schema["pattern"],
                    model_pattern,
                    f"SkillFrontmatter.{model_field} pattern diverges "
                    f"from skill.schema.json '{schema_field}'",
                )

    @covers("REQ-0.17.0-04-05")
    def test_max_length_constraints_match(self) -> None:
        """maxLength constraints in schema match Pydantic field limits."""
        schema_props = self.schema.get("properties", {})
        for schema_field, field_schema in schema_props.items():
            if "maxLength" not in field_schema:
                continue
            model_field = _resolve_field(self.model, schema_field)
            self.assertIsNotNone(model_field)
            model_max_length = _pydantic_field_max_length(self.model, model_field)
            with self.subTest(field=schema_field):
                self.assertEqual(
                    field_schema["maxLength"],
                    model_max_length,
                    f"SkillFrontmatter.{model_field} max_length diverges "
                    f"from skill.schema.json '{schema_field}'",
                )

    @covers("REQ-0.17.0-04-01")
    def test_all_schema_properties_have_model_fields(self) -> None:
        """Every property in skill.schema.json has a corresponding model field."""
        schema_props = set(self.schema.get("properties", {}).keys())
        alias_map = _model_alias_map(self.model)
        missing = schema_props - set(alias_map.keys())
        self.assertFalse(
            missing,
            f"skill.schema.json properties without model fields: {missing}",
        )


class TestInstructionSchemaAlignment(unittest.TestCase):
    """Verify InstructionFrontmatter model matches .gzkit/schemas/rule.schema.json.

    @covers REQ-0.17.0-04-02
    @covers REQ-0.17.0-04-06
    """

    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        from gzkit.models.frontmatter import InstructionFrontmatter

        cls.model = InstructionFrontmatter
        cls.schema = _load_gzkit_schema("rule")

    @covers("REQ-0.17.0-04-04")
    @covers("REQ-0.17.0-04-06")
    def test_required_fields_match(self) -> None:
        """Schema-required fields are required in the Pydantic model."""
        schema_required = set(self.schema.get("required", []))
        model_required = _pydantic_required_fields(self.model)
        resolved = set()
        for f in schema_required:
            model_field = _resolve_field(self.model, f)
            self.assertIsNotNone(
                model_field,
                f"Schema required field '{f}' has no corresponding model field",
            )
            resolved.add(model_field)
        missing = resolved - model_required
        self.assertFalse(
            missing,
            f"InstructionFrontmatter missing required fields: {missing}",
        )

    @covers("REQ-0.17.0-04-06")
    def test_enum_values_match(self) -> None:
        """Enum constraints in schema match Literal values in model."""
        schema_props = self.schema.get("properties", {})
        for schema_field, field_schema in schema_props.items():
            if "enum" not in field_schema:
                continue
            schema_enum = set(field_schema["enum"])
            model_field = _resolve_field(self.model, schema_field)
            if model_field is None:
                continue
            model_literals = _pydantic_literal_values(self.model, model_field)
            if model_literals is None:
                continue
            with self.subTest(field=schema_field):
                self.assertEqual(
                    schema_enum,
                    model_literals,
                    f"InstructionFrontmatter.{model_field} Literal values diverge "
                    f"from rule.schema.json '{schema_field}' enum",
                )

    @covers("REQ-0.17.0-04-02")
    def test_all_schema_properties_have_model_fields(self) -> None:
        """Every property in rule.schema.json has a corresponding model field."""
        schema_props = set(self.schema.get("properties", {}).keys())
        alias_map = _model_alias_map(self.model)
        missing = schema_props - set(alias_map.keys())
        self.assertFalse(
            missing,
            f"rule.schema.json properties without model fields: {missing}",
        )


class TestCommittedLedgerValidatesAgainstSchema(unittest.TestCase):
    """The repo's OWN ledger must satisfy the schema shipped alongside it.

    Tightening a ledger event's schema is not a local edit: the ledger is
    APPEND-ONLY, so every row already committed must keep validating, and a
    historical row cannot be repaired to satisfy a new rule.

    Measured 2026-08-25 (OBPI-0.35.0-02): adding `tier` to
    `corpus_entry_retired`'s `required` list broke FIVE historical rows written
    before the field existed -- while `uv run -m unittest -q` stayed green at
    8822 tests, because every other ledger test builds its own fixture ledger in
    a temp dir and none reads the committed one. The whole suite passing is
    therefore not evidence that the shipped ledger still validates; this test is.

    The precedent it enforces: an additive field on an existing event type is
    DECLARED but not REQUIRED (27 of 65 event types already carry
    declared-but-optional properties), matching how `task_id` was added additively
    to the worklog event types. Declare the property so a present value is
    type-checked; leave it out of `required` so history keeps validating.
    """

    def test_committed_ledger_has_no_schema_violations(self) -> None:
        from gzkit.validate_pkg.ledger_check import validate_ledger

        ledger = Path(__file__).resolve().parents[1] / ".gzkit" / "ledger.jsonl"
        if not ledger.exists():  # pragma: no cover - only in a stripped checkout
            self.skipTest("no committed ledger in this checkout")
        errors = validate_ledger(ledger)
        self.assertEqual(
            [f"{e.artifact}: {e.message}" for e in errors],
            [],
            "The committed ledger no longer satisfies src/gzkit/schemas/ledger.json. "
            "The ledger is append-only -- do NOT edit historical rows. Relax the "
            "schema instead: declare a new field as a property, not in `required`.",
        )


class TestTypedModelParsesEveryCommittedLedgerRow(unittest.TestCase):
    """The typed models must parse the ledger the JSON schema accepts.

    A ledger row has TWO readers: `validate_ledger` (JSON-schema, `ledger_check.py`)
    and `parse_typed_event` (the Pydantic discriminated union). They can disagree
    about the same row, and the JSON-schema side is the lenient one -- so a suite
    that only exercises `validate_ledger` proves nothing about the typed path.

    Measured 2026-08-25 (OBPI-0.35.0-02): `tier` was correctly removed from
    `corpus_entry_retired`'s `required` list so five pre-existing rows kept
    validating, but the matching default was NOT added to
    `CorpusEntryRetiredEvent.tier`. `gz validate --ledger` returned 0 while
    `parse_typed_event` raised `tier: Field required` on
    `corpus-entry-retired-2026-07-22T10:31:32.832846+00:00` -- the exact rows the
    schema relaxation existed to rescue. Both independent reviewers flagged it and
    no test could have.

    The general rule this pins: when an event type gains a field, the schema and the
    typed model must relax TOGETHER, because the ledger is append-only and history
    can never grow the key.
    """

    def test_every_committed_row_parses_through_the_typed_union(self) -> None:
        import json

        from gzkit.events import parse_typed_event

        ledger = Path(__file__).resolve().parents[1] / ".gzkit" / "ledger.jsonl"
        if not ledger.exists():  # pragma: no cover - only in a stripped checkout
            self.skipTest("no committed ledger in this checkout")

        # SCOPED to the corpus events, deliberately. Measured 2026-08-25: ~300
        # committed rows across 14 other event-type/field combinations already fail
        # this union (`artifact_renamed`, `obpi_lock_released`, `airlock_in`, ... all
        # carrying keys their models forbid). That is a real, larger pre-existing gap
        # -- tracked separately -- and swallowing it here would mean either a
        # permanently red test or an allowlist that quietly grows until the fence
        # asserts nothing. Scope names what this OBPI is accountable for.
        scope = {"corpus_entry_retired", "corpus_entry_appended"}

        failures: list[str] = []
        for lineno, line in enumerate(ledger.read_text(encoding="utf-8").splitlines(), start=1):
            if not line.strip():
                continue
            row = json.loads(line)
            if row.get("event") not in scope:
                continue
            try:
                parse_typed_event(row)
            except ValueError as exc:
                # An event type with no typed model is a different (declared) gap;
                # this test is about a row the union CLAIMS to model and cannot parse.
                if "Unknown event" in str(exc) or "no typed model" in str(exc).lower():
                    continue
                failures.append(f"{ledger.name}:{lineno} {row.get('event')}: {exc}")

        self.assertEqual(
            failures[:5],
            [],
            "Typed models reject committed ledger rows that the JSON schema accepts. "
            "The ledger is append-only -- history cannot gain a key. Give the new "
            "field a default on the model, matching its absence from `required`.",
        )


if __name__ == "__main__":
    unittest.main()
