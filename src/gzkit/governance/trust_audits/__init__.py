"""Trust-boundary audits promoted from ``tests/governance/`` to first-class ``gz validate`` scopes.

Each audit here enforces one of the three invariants from
``docs/governance/trust-doctrine.md``:

* **T1 — Every produced value has a read-path assertion** (covered by regression
  tests elsewhere, not this package)
* **T2 — Every consumed value has a write-path audit** — ``audit_validator_fields``
* **T3 — Canonical claims bind canonical provenance** — covered by ``gz arb validate``

Plus supporting audits that catch the same trust-chain poisoning shape at
adjacent layers — ``audit_event_handlers``, ``audit_type_ignores``,
``audit_cli_alignment``, etc. Each audit returns a list of ``ValidationError``
objects so it composes with ``gz validate`` alongside manifest/ledger/document
validation.

The package is partitioned by audit family (GHI #360); every ``audit_*`` name
remains importable from ``gzkit.governance.trust_audits`` via the re-exports
below.
"""

from __future__ import annotations

from pathlib import Path

from gzkit.core.validation_rules import ValidationError
from gzkit.governance.trust_audits.absorption_duplicates import (
    audit_absorption_duplicates,
)
from gzkit.governance.trust_audits.adversarial_validation import (
    audit_adversarial_validation,
)
from gzkit.governance.trust_audits.advisor_proof_binding import (
    validate_advisor_proof_binding,
)
from gzkit.governance.trust_audits.agents_md_map_conformance import (
    audit_agents_md_map_conformance,
)
from gzkit.governance.trust_audits.attestation_receipts import (
    AttestationReceiptEntry,
    AttestationReceiptValidationResult,
    audit_attestation_receipts,
    validate_attestation_receipts,
)
from gzkit.governance.trust_audits.authorship import (
    audit_authorship,
    evaluate_authorship,
)
from gzkit.governance.trust_audits.brief_reconcile import (
    validate_brief_reconcile,
)
from gzkit.governance.trust_audits.brief_structure import (
    validate_brief_structure,
)
from gzkit.governance.trust_audits.briefs import (
    audit_behave_req_tags,
    audit_brief_command_shape,
    audit_brief_cross_references,
    audit_brief_demo_section,
    audit_brief_headings,
)
from gzkit.governance.trust_audits.bullet_retention import validate_bullet_retention
from gzkit.governance.trust_audits.chores import audit_chores_layout
from gzkit.governance.trust_audits.cli import (
    audit_cli_alignment,
    audit_manpage_alignment,
    audit_skill_alignment,
    audit_skill_code_citations,
)
from gzkit.governance.trust_audits.closeout_proof import validate_closeout_proof
from gzkit.governance.trust_audits.code_quality import (
    audit_class_size,
    audit_test_tiers,
    audit_type_ignores,
)
from gzkit.governance.trust_audits.codex_delivery_witness import (
    audit_codex_delivery_witness,
)
from gzkit.governance.trust_audits.complexity_doctrine_links import (
    validate_complexity_doctrine_links,
)
from gzkit.governance.trust_audits.complexity_thresholds import (
    BOOTSTRAP_MODE_NOTICE_PREFIX,
    validate_complexity_thresholds,
)
from gzkit.governance.trust_audits.config_registry import audit_config_registry
from gzkit.governance.trust_audits.corpus_retirement_witness import (
    validate_corpus_retirement_witness,
)
from gzkit.governance.trust_audits.cross_platform import (
    audit_line_endings,
    audit_subprocess_errors,
    audit_utf8_prefix,
)
from gzkit.governance.trust_audits.deprecated_verb_prescription import (
    audit_deprecated_verb_prescription,
)
from gzkit.governance.trust_audits.distribution import audit_distribution
from gzkit.governance.trust_audits.doc_surface_parity import (
    audit_doc_surface_parity,
)
from gzkit.governance.trust_audits.evaluation_justify_binding import (
    validate_evaluation_justify_binding,
)
from gzkit.governance.trust_audits.events import (
    audit_event_handlers,
    audit_event_schemas,
    audit_producer_fields,
    audit_validator_fields,
)
from gzkit.governance.trust_audits.exemption_controls import audit_exemption_controls
from gzkit.governance.trust_audits.fidelity_presence import audit_fidelity_presence
from gzkit.governance.trust_audits.gate_callers import audit_gate_callers
from gzkit.governance.trust_audits.insights import audit_insights_shape
from gzkit.governance.trust_audits.instructions_files_budget import (
    audit_instructions_files_budget,
)
from gzkit.governance.trust_audits.intrinsic_attestation import (
    validate_intrinsic_attestation,
)
from gzkit.governance.trust_audits.invariant_coherence import (
    validate_invariant_coherence,
)
from gzkit.governance.trust_audits.kind_invariance import audit_kind_invariance
from gzkit.governance.trust_audits.lifecycle_pointers import (
    audit_lifecycle_pointers,
)
from gzkit.governance.trust_audits.lock_exchange_coupling import (
    validate_lock_exchange_coupling,
)
from gzkit.governance.trust_audits.models import audit_pydantic_models
from gzkit.governance.trust_audits.okf_conformance import audit_okf_conformance
from gzkit.governance.trust_audits.orientation import audit_orientation_freshness
from gzkit.governance.trust_audits.orphaned_implementation import (
    audit_orphaned_implementation,
)
from gzkit.governance.trust_audits.persona_witness import audit_persona_witness
from gzkit.governance.trust_audits.pointer_integrity import (
    validate_pointer_integrity,
)
from gzkit.governance.trust_audits.python_version_pins import (
    audit_python_version_pins,
    evaluate_python_version_pins,
)
from gzkit.governance.trust_audits.qc_binding import audit_qc_binding
from gzkit.governance.trust_audits.receipt_shape import audit_receipt_shape
from gzkit.governance.trust_audits.reconcile import audit_reconcile_freshness
from gzkit.governance.trust_audits.red_parity import audit_red_parity
from gzkit.governance.trust_audits.release import (
    audit_advisory_scorecard,
    audit_version_release,
)
from gzkit.governance.trust_audits.rendition_floor_coherence import (
    validate_rendition_floor_coherence,
)
from gzkit.governance.trust_audits.rendition_freshness import validate_rendition_freshness
from gzkit.governance.trust_audits.router_tables import audit_router_tables
from gzkit.governance.trust_audits.sensitivity import (
    audit_sensitivity_binding,
    explain_sensitivity_for_paths,
)
from gzkit.governance.trust_audits.session_green_gate import audit_session_green_gate
from gzkit.governance.trust_audits.setpoint_coherence import validate_setpoint_coherence
from gzkit.governance.trust_audits.status_writer_coverage import (
    audit_status_writer_coverage,
)
from gzkit.governance.trust_audits.surface_delivery_witness import (
    audit_surface_delivery_witness,
)
from gzkit.governance.trust_audits.surface_weight import validate_surface_weight
from gzkit.governance.trust_audits.taxonomy import (
    audit_adr_status_fresh,
    audit_adr_taxonomy,
    audit_obpi_lifecycle_coherence,
    audit_pool_adr_isolation,
    audit_pool_interview_schema,
)
from gzkit.governance.trust_audits.transcribed_counts import (
    audit_transcribed_counts,
)
from gzkit.governance.trust_audits.vendor_manifest import validate_vendor_manifest
from gzkit.governance.trust_audits.waiver_ratchet import audit_waiver_ratchet
from gzkit.governance.trust_audits.wheel_path_literals import audit_wheel_path_literals


def validate_surface_fidelity(project_root: Path) -> list[ValidationError]:
    """Composite: run all four surface-fidelity invariants in declared order.

    Invokes validate_bullet_retention, validate_surface_weight and
    validate_pointer_integrity in that order and aggregates their
    ValidationError lists. The exit code is determined by the worst error
    type in the aggregate (policy-breach types exit 3; others exit 1).

    Invariant 4 (scenario reachability) was retired 2026-07-25 — see
    ADR-0.0.33 § Amendment (2026-07-25).
    """
    errors: list[ValidationError] = []
    errors.extend(validate_bullet_retention(project_root))
    errors.extend(validate_surface_weight(project_root))
    errors.extend(validate_pointer_integrity(project_root))
    return errors


__all__ = [
    "AttestationReceiptEntry",
    "AttestationReceiptValidationResult",
    "audit_absorption_duplicates",
    "audit_adr_status_fresh",
    "audit_obpi_lifecycle_coherence",
    "audit_adr_taxonomy",
    "audit_adversarial_validation",
    "audit_advisory_scorecard",
    "audit_attestation_receipts",
    "audit_behave_req_tags",
    "audit_brief_command_shape",
    "audit_brief_cross_references",
    "audit_authorship",
    "audit_python_version_pins",
    "evaluate_authorship",
    "evaluate_python_version_pins",
    "audit_brief_demo_section",
    "audit_brief_headings",
    "audit_agents_md_map_conformance",
    "audit_chores_layout",
    "audit_class_size",
    "audit_distribution",
    "audit_wheel_path_literals",
    "audit_cli_alignment",
    "audit_manpage_alignment",
    "audit_skill_code_citations",
    "audit_doc_surface_parity",
    "audit_lifecycle_pointers",
    "audit_event_handlers",
    "audit_event_schemas",
    "audit_producer_fields",
    "audit_insights_shape",
    "audit_kind_invariance",
    "audit_persona_witness",
    "audit_instructions_files_budget",
    "audit_surface_delivery_witness",
    "audit_codex_delivery_witness",
    "audit_status_writer_coverage",
    "audit_transcribed_counts",
    "audit_orientation_freshness",
    "audit_qc_binding",
    "audit_fidelity_presence",
    "audit_exemption_controls",
    "audit_gate_callers",
    "audit_config_registry",
    "audit_waiver_ratchet",
    "audit_deprecated_verb_prescription",
    "audit_orphaned_implementation",
    "audit_pool_adr_isolation",
    "audit_pool_interview_schema",
    "audit_okf_conformance",
    "audit_pydantic_models",
    "audit_receipt_shape",
    "audit_reconcile_freshness",
    "audit_red_parity",
    "audit_router_tables",
    "audit_sensitivity_binding",
    "audit_session_green_gate",
    "audit_line_endings",
    "audit_skill_alignment",
    "audit_subprocess_errors",
    "audit_test_tiers",
    "audit_type_ignores",
    "audit_utf8_prefix",
    "audit_validator_fields",
    "audit_version_release",
    "explain_sensitivity_for_paths",
    "BOOTSTRAP_MODE_NOTICE_PREFIX",
    "validate_advisor_proof_binding",
    "validate_closeout_proof",
    "validate_lock_exchange_coupling",
    "validate_attestation_receipts",
    "validate_brief_reconcile",
    "validate_brief_structure",
    "validate_bullet_retention",
    "validate_complexity_doctrine_links",
    "validate_complexity_thresholds",
    "validate_evaluation_justify_binding",
    "validate_invariant_coherence",
    "validate_intrinsic_attestation",
    "validate_pointer_integrity",
    "validate_corpus_retirement_witness",
    "validate_rendition_floor_coherence",
    "validate_rendition_freshness",
    "validate_setpoint_coherence",
    "validate_surface_fidelity",
    "validate_surface_weight",
    "validate_vendor_manifest",
]
