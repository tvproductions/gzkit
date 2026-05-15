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

from gzkit.governance.trust_audits.absorption_duplicates import (
    audit_absorption_duplicates,
)
from gzkit.governance.trust_audits.advisor_proof_binding import (
    validate_advisor_proof_binding,
)
from gzkit.governance.trust_audits.attestation_receipts import (
    AttestationReceiptEntry,
    AttestationReceiptValidationResult,
    audit_attestation_receipts,
    validate_attestation_receipts,
)
from gzkit.governance.trust_audits.briefs import (
    audit_behave_req_tags,
    audit_brief_cross_references,
    audit_brief_demo_section,
    audit_brief_headings,
)
from gzkit.governance.trust_audits.bullet_retention import validate_bullet_retention
from gzkit.governance.trust_audits.chores import audit_chores_layout
from gzkit.governance.trust_audits.cli import (
    audit_cli_alignment,
    audit_skill_alignment,
)
from gzkit.governance.trust_audits.code_quality import (
    audit_class_size,
    audit_test_tiers,
    audit_type_ignores,
)
from gzkit.governance.trust_audits.complexity_doctrine_links import (
    validate_complexity_doctrine_links,
)
from gzkit.governance.trust_audits.complexity_thresholds import (
    BOOTSTRAP_MODE_NOTICE_PREFIX,
    validate_complexity_thresholds,
)
from gzkit.governance.trust_audits.cross_platform import audit_utf8_prefix
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
    audit_validator_fields,
)
from gzkit.governance.trust_audits.insights import audit_insights_shape
from gzkit.governance.trust_audits.instructions_files_budget import (
    audit_instructions_files_budget,
)
from gzkit.governance.trust_audits.intrinsic_attestation import (
    validate_intrinsic_attestation,
)
from gzkit.governance.trust_audits.models import audit_pydantic_models
from gzkit.governance.trust_audits.orientation import audit_orientation_freshness
from gzkit.governance.trust_audits.orphaned_implementation import (
    audit_orphaned_implementation,
)
from gzkit.governance.trust_audits.reconcile import audit_reconcile_freshness
from gzkit.governance.trust_audits.release import (
    audit_advisory_scorecard,
    audit_version_release,
)
from gzkit.governance.trust_audits.sensitivity import (
    audit_sensitivity_binding,
    explain_sensitivity_for_paths,
)
from gzkit.governance.trust_audits.taxonomy import (
    audit_adr_status_fresh,
    audit_adr_taxonomy,
    audit_pool_adr_isolation,
)

__all__ = [
    "AttestationReceiptEntry",
    "AttestationReceiptValidationResult",
    "audit_absorption_duplicates",
    "audit_adr_status_fresh",
    "audit_adr_taxonomy",
    "audit_advisory_scorecard",
    "audit_attestation_receipts",
    "audit_behave_req_tags",
    "audit_brief_cross_references",
    "audit_brief_demo_section",
    "audit_brief_headings",
    "audit_chores_layout",
    "audit_class_size",
    "audit_distribution",
    "audit_cli_alignment",
    "audit_doc_surface_parity",
    "audit_event_handlers",
    "audit_event_schemas",
    "audit_insights_shape",
    "audit_instructions_files_budget",
    "audit_orientation_freshness",
    "audit_orphaned_implementation",
    "audit_pool_adr_isolation",
    "audit_pydantic_models",
    "audit_reconcile_freshness",
    "audit_sensitivity_binding",
    "audit_skill_alignment",
    "audit_test_tiers",
    "audit_type_ignores",
    "audit_utf8_prefix",
    "audit_validator_fields",
    "audit_version_release",
    "explain_sensitivity_for_paths",
    "BOOTSTRAP_MODE_NOTICE_PREFIX",
    "validate_advisor_proof_binding",
    "validate_attestation_receipts",
    "validate_bullet_retention",
    "validate_complexity_doctrine_links",
    "validate_complexity_thresholds",
    "validate_evaluation_justify_binding",
    "validate_intrinsic_attestation",
]
