"""Validate command implementation."""

import json
import os
from collections.abc import Callable
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import NamedTuple

import jsonschema
from pydantic import ValidationError as PydanticValidationError
from rich.markup import escape

from gzkit.commands.common import console, get_project_root
from gzkit.commands.validate_briefs import (
    _validate_interviews,
    _validate_obpi_briefs,
    _validate_personas,
    _validate_requirements,
)
from gzkit.commands.validate_commit_trailers import (
    _validate_commit_trailers,
    _validate_eval_feedback_trailer,
)
from gzkit.commands.validate_decomposition import validate_decomposition
from gzkit.commands.validate_frontmatter import (
    _render_frontmatter_explain,
    validate_frontmatter_coherence,
)
from gzkit.commands.validate_req_kind import _validate_req_kind_discipline
from gzkit.commands.validate_sensitivity import (
    _parse_sensitivity_path_list,
    _sensitivity_records,
)
from gzkit.commands.validate_task_envelope import _validate_task_envelope_coherence
from gzkit.commands.version_sync import validate_version_consistency
from gzkit.content.ownership import OwnershipDeclaration
from gzkit.governance.trust_audits import (
    AttestationReceiptValidationResult,
    validate_attestation_receipts,
)
from gzkit.instruction_audit import audit_instructions
from gzkit.models.exemplar import ExemplarCorpus
from gzkit.mx import levels as _mx_levels
from gzkit.validate import (
    ValidationError,
    validate_document,
    validate_ledger,
    validate_manifest,
    validate_surfaces,
)


class _ScopeEntry(NamedTuple):
    """One validator scope's dispatch facts (Sanity-Reduction #618).

    ``VALIDATOR_REGISTRY`` is the single source from which every validate
    dispatch surface derives — the runner dicts, the tier split in
    ``_collect_errors``, the ``_resolve_scopes`` lists, and ``validate()``'s
    ``_other_scopes_active`` predicate. The step-1 fence
    (``tests/cli/test_validate_dispatch_consistency.py``) pins the signature ↔
    runner ↔ parser-lambda parity these now answer to.
    """

    stem: str
    tier: str  # "default" (no-flag `gz check`) | "explicit" (flag-gated)
    in_other_scopes: bool  # counts toward validate()'s _other_scopes_active predicate
    run: Callable[[Path, str | None], list[ValidationError]]
    level: int = _mx_levels.ERROR  # ERROR demotes in an open hangar; CRITICAL pins (#852)


def _delivery_arm_enabled() -> bool:
    """Return True when the session-green gate's delivery arm should bind here.

    The arm asserts the declared pre-push hook is installed on disk. That is the
    right bar for a developer worktree and the wrong one for CI: a fresh CI
    checkout legitimately has no hooks — CI *is* the gate there, and it does not
    push — so binding it unconditionally would fail every CI run.

    ``CI`` is the discriminator every major runner sets (GitHub Actions, GitLab,
    CircleCI, Travis, Buildkite), which makes it the smallest surface that
    separates the two cases without asking adopters to configure anything. The
    read lives here, at the CLI adapter boundary, so the audit itself stays a
    parameterized pure function (GHI #715).
    """
    return not os.environ.get("CI")


def _ta() -> ModuleType:
    """Lazy ``trust_audits`` accessor.

    Preserves the module-load circular-import guard the dispatch runners have
    always relied on (``taxonomy``/``closeout_proof`` back-reference this module).
    """
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return trust_audits


def _validate_tautological_test_audit(project_root: Path) -> list[ValidationError]:
    """Validate the test-quality gate (OBPI-0.0.59-04; wall-clock arm GHI #865).

    Rules:
    - a genuinely-new tautological op, uncovered by baseline or waiver → fail (3)
    - a fixture whose verdict decays with the wall clock → fail (3)
    Waivers file path is self-exempt from the scan (circular-dependency analysis).
    """
    from gzkit.tautological_tests import audit_test_quality  # noqa: PLC0415

    return audit_test_quality(project_root)


def _collect_errors(
    project_root: Path,
    checks: dict[str, bool],
    frontmatter_adr: str | None = None,
) -> list[ValidationError]:
    """Collect validation errors for the requested scopes.

    ``checks`` maps scope stem -> requested flag (the param->stem bridge built by
    ``validate()``). The default/explicit tier split is derived from
    ``VALIDATOR_REGISTRY`` so the tiers can never drift from the runners.
    """
    default_scopes = {
        e.stem: checks.get(e.stem, False) for e in VALIDATOR_REGISTRY if e.tier == "default"
    }
    explicit_scopes = {
        e.stem: checks.get(e.stem, False) for e in VALIDATOR_REGISTRY if e.tier == "explicit"
    }
    run_all = not any(default_scopes.values()) and not any(explicit_scopes.values())
    return _run_scope_checks(
        project_root, default_scopes, explicit_scopes, run_all, frontmatter_adr=frontmatter_adr
    )


def _changelog_runner(project_root: Path) -> list[ValidationError]:
    """Run the hermetic changelog structural validator (GHI #685)."""
    from gzkit.validate_pkg.changelog import validate_changelog  # noqa: PLC0415

    return validate_changelog(project_root)


# Single source of validate dispatch (Sanity-Reduction #618). Order is load-bearing:
# default-tier order is the no-flag error-collection order; the step-1 fence
# (tests/cli/test_validate_dispatch_consistency.py) pins signature/runner/parser
# parity against this, and tests/cli/test_validate_registry_parity.py pins the
# tier split and the _other_scopes_active membership against the pre-collapse truth.
VALIDATOR_REGISTRY: tuple[_ScopeEntry, ...] = (
    _ScopeEntry(
        "manifest",
        "default",
        True,
        lambda r, _f: list(validate_manifest(r / ".gzkit" / "manifest.json")),
    ),
    _ScopeEntry("surfaces", "default", True, lambda r, _f: list(validate_surfaces(r))),
    _ScopeEntry(
        "ledger",
        "default",
        True,
        lambda r, _f: list(validate_ledger(r / ".gzkit" / "ledger.jsonl")),
    ),
    _ScopeEntry("instructions", "default", True, lambda r, _f: list(audit_instructions(r))),
    _ScopeEntry("briefs", "default", True, lambda r, _f: _validate_obpi_briefs(r)),
    _ScopeEntry("documents", "default", True, lambda r, _f: _validate_manifest_documents(r)),
    _ScopeEntry("personas", "default", True, lambda r, _f: _validate_personas(r)),
    _ScopeEntry(
        "frontmatter",
        "default",
        True,
        lambda r, fa: list(validate_frontmatter_coherence(r, adr_scope=fa)),
    ),
    _ScopeEntry("version", "default", True, lambda r, _f: list(validate_version_consistency(r))),
    _ScopeEntry("taxonomy", "default", True, lambda r, _f: _taxonomy_runner(r)),
    _ScopeEntry(
        "invariant_coherence", "default", False, lambda r, _f: _invariant_coherence_runner(r)
    ),
    _ScopeEntry("interviews", "explicit", True, lambda r, _f: _validate_interviews(r)),
    _ScopeEntry("decomposition", "explicit", True, lambda r, _f: validate_decomposition(r)),
    _ScopeEntry("requirements", "explicit", True, lambda r, _f: _validate_requirements(r)),
    _ScopeEntry(
        "commit_trailers",
        "explicit",
        True,
        lambda r, _f: _validate_commit_trailers(r) + _validate_eval_feedback_trailer(r),
    ),
    _ScopeEntry("type_ignores", "explicit", True, lambda r, _f: _ta().audit_type_ignores(r)),
    _ScopeEntry(
        "cli_alignment",
        "explicit",
        True,
        lambda r, _f: (
            _ta().audit_cli_alignment(r)
            + _ta().audit_manpage_alignment(r)
            + _ta().audit_skill_code_citations(r)
        ),
    ),
    _ScopeEntry("event_handlers", "explicit", True, lambda r, _f: _ta().audit_event_handlers(r)),
    _ScopeEntry("event_schemas", "explicit", True, lambda r, _f: _ta().audit_event_schemas(r)),
    _ScopeEntry("producer_fields", "explicit", True, lambda r, _f: _ta().audit_producer_fields(r)),
    _ScopeEntry(
        "validator_fields", "explicit", True, lambda r, _f: _ta().audit_validator_fields(r)
    ),
    _ScopeEntry(  # CRITICAL: `operator-pii` floor, pinned by LEVEL not NAME (GHI #852)
        "authorship", "explicit", True, lambda r, _f: _ta().audit_authorship(r), _mx_levels.CRITICAL
    ),
    _ScopeEntry(
        "python_version_pins",
        "explicit",
        True,
        lambda r, _f: _ta().audit_python_version_pins(r),
    ),
    _ScopeEntry("utf8_prefix", "explicit", True, lambda r, _f: _ta().audit_utf8_prefix(r)),
    _ScopeEntry("line_endings", "explicit", True, lambda r, _f: _ta().audit_line_endings(r)),
    _ScopeEntry("test_tiers", "explicit", True, lambda r, _f: _ta().audit_test_tiers(r)),
    _ScopeEntry("pydantic_models", "explicit", True, lambda r, _f: _ta().audit_pydantic_models(r)),
    _ScopeEntry("class_size", "explicit", True, lambda r, _f: _ta().audit_class_size(r)),
    _ScopeEntry("version_release", "explicit", True, lambda r, _f: _ta().audit_version_release(r)),
    _ScopeEntry(
        "pool_adr_isolation", "explicit", True, lambda r, _f: _ta().audit_pool_adr_isolation(r)
    ),
    _ScopeEntry(
        "pool_interview", "explicit", True, lambda r, _f: _ta().audit_pool_interview_schema(r)
    ),
    _ScopeEntry("behave_req_tags", "explicit", True, lambda r, _f: _ta().audit_behave_req_tags(r)),
    _ScopeEntry("skill_alignment", "explicit", True, lambda r, _f: _ta().audit_skill_alignment(r)),
    _ScopeEntry(
        "advisory_scorecard", "explicit", True, lambda r, _f: _ta().audit_advisory_scorecard(r)
    ),
    _ScopeEntry(
        "complexity_doctrine_links",
        "explicit",
        True,
        lambda r, _f: _ta().validate_complexity_doctrine_links(r),
    ),
    _ScopeEntry(
        "complexity_thresholds",
        "explicit",
        True,
        lambda r, _f: _ta().validate_complexity_thresholds(r),
    ),
    _ScopeEntry(
        "reconcile_freshness", "explicit", True, lambda r, _f: _ta().audit_reconcile_freshness(r)
    ),
    _ScopeEntry("insights_shape", "explicit", True, lambda r, _f: _ta().audit_insights_shape(r)),
    _ScopeEntry(
        "instructions_files_budget",
        "explicit",
        True,
        # Three checks on one surface family, one flag, in increasing strength:
        # the char budget gzkit sets for itself; the witness that the rendered
        # artifact still fits the cap the manifest DECLARES (GHI #712); and the
        # witness that observes what the vendor ACTUALLY delivered (GHI #962).
        # The first two compare authored numbers and stay green while delivery
        # is zero -- which is how a cap lowered to the vendor default sat
        # unnoticed while 14108 B of contract, the IRON LAW included, never
        # reached a Codex session. All three report to stderr; only declaration
        # drift returns findings.
        lambda r, _f: (
            _ta().audit_instructions_files_budget(r)
            + _ta().audit_surface_delivery_witness(r)
            + _ta().audit_codex_delivery_witness(r)
        ),
    ),
    _ScopeEntry(
        "agents_md_map_conformance",
        "explicit",
        True,
        lambda r, _f: _ta().audit_agents_md_map_conformance(r),
    ),
    _ScopeEntry(
        "adr_status_fresh", "explicit", True, lambda r, _f: _ta().audit_adr_status_fresh(r)
    ),
    _ScopeEntry(
        "obpi_lifecycle_coherence",
        "explicit",
        True,
        lambda r, _f: _ta().audit_obpi_lifecycle_coherence(r),
    ),
    _ScopeEntry(
        "adversarial_validation",
        "explicit",
        True,
        lambda r, _f: _ta().audit_adversarial_validation(r),
    ),
    _ScopeEntry("red_parity", "explicit", True, lambda r, _f: _ta().audit_red_parity(r)),
    _ScopeEntry(
        "session_green_gate",
        "explicit",
        False,
        lambda r, _f: _ta().audit_session_green_gate(r, check_delivery=_delivery_arm_enabled()),
    ),
    _ScopeEntry(
        "orientation_freshness",
        "explicit",
        True,
        lambda r, _f: _ta().audit_orientation_freshness(r),
    ),
    _ScopeEntry("brief_headings", "explicit", True, lambda r, _f: _ta().audit_brief_headings(r)),
    _ScopeEntry(
        "brief_cross_references",
        "explicit",
        True,
        lambda r, _f: _ta().audit_brief_cross_references(r),
    ),
    _ScopeEntry(
        "brief_demo_section", "explicit", True, lambda r, _f: _ta().audit_brief_demo_section(r)
    ),
    _ScopeEntry("chores_layout", "explicit", True, lambda r, _f: _ta().audit_chores_layout(r)),
    _ScopeEntry("unscoped_rules", "explicit", False, lambda r, _f: _unscoped_rules_runner(r)),
    _ScopeEntry(
        "rule_version_markers", "default", True, lambda r, _f: _rule_version_markers_runner(r)
    ),
    _ScopeEntry("invariant_witness", "default", True, lambda r, _f: _invariant_witness_runner(r)),
    _ScopeEntry("sensitivity", "explicit", False, lambda r, _f: _sensitivity_umbrella_runner(r)),
    _ScopeEntry(
        "doc_surface_parity", "explicit", True, lambda r, _f: _ta().audit_doc_surface_parity(r)
    ),
    _ScopeEntry(
        "absorption_duplicates",
        "explicit",
        True,
        lambda r, _f: _ta().audit_absorption_duplicates(r),
    ),
    _ScopeEntry(
        "orphaned_implementation",
        "explicit",
        True,
        lambda r, _f: _ta().audit_orphaned_implementation(r),
    ),
    _ScopeEntry(
        "evaluation_justify_binding",
        "explicit",
        False,
        lambda r, _f: _evaluation_justify_binding_runner(r, None),
    ),
    # The three scopes below own a solo early-return lifecycle like the entries
    # above, but were the only ones never registered — so this registry's
    # "single source" header was false and `_dispatch_validator_scope` could not
    # resolve them, which is why every SUPPORT REQ citing one read
    # `unproven-support` regardless of truth (GHI #630). Registering them does
    # not re-route the flag: `_dispatch_early_return_scopes` still fires first
    # and short-circuits, preserving the 0/2/3 lifecycle and the custom prose.
    # `in_other_scopes=False` is what keeps them solo (#704).
    _ScopeEntry("qc_binding", "explicit", False, lambda r, _f: _ta().audit_qc_binding(r)),
    _ScopeEntry(
        "fidelity_presence", "explicit", False, lambda r, _f: _ta().audit_fidelity_presence(r)
    ),
    _ScopeEntry("waiver_ratchet", "explicit", False, lambda r, _f: _ta().audit_waiver_ratchet(r)),
    _ScopeEntry("config_registry", "explicit", False, lambda r, _f: _ta().audit_config_registry(r)),
    _ScopeEntry("gate_callers", "explicit", False, lambda r, _f: _ta().audit_gate_callers(r)),
    _ScopeEntry(
        "exemption_controls", "explicit", False, lambda r, _f: _ta().audit_exemption_controls(r)
    ),
    _ScopeEntry(
        "intrinsic_attestation",
        "explicit",
        False,
        lambda r, _f: _ta().validate_intrinsic_attestation(r),
    ),
    _ScopeEntry(
        "advisor_proof_binding",
        "explicit",
        False,
        lambda r, _f: _ta().validate_advisor_proof_binding(r),
    ),
    _ScopeEntry(
        "lock_exchange_coupling",
        "explicit",
        False,
        lambda r, _f: _ta().validate_lock_exchange_coupling(r),
    ),
    _ScopeEntry("distribution", "explicit", True, lambda r, _f: _ta().audit_distribution(r)),
    _ScopeEntry(  # default tier: a fence behind a remembered flag is inert (GHI #900)
        "wheel_path_literals",
        "default",
        True,
        lambda r, _f: _ta().audit_wheel_path_literals(r),
    ),
    _ScopeEntry("changelog", "explicit", True, lambda r, _f: _changelog_runner(r)),
    _ScopeEntry(
        "bullet_retention", "explicit", True, lambda r, _f: _ta().validate_bullet_retention(r)
    ),
    _ScopeEntry("surface_weight", "explicit", True, lambda r, _f: _ta().validate_surface_weight(r)),
    _ScopeEntry(
        "pointer_anchors", "explicit", True, lambda r, _f: _ta().validate_pointer_integrity(r)
    ),
    _ScopeEntry(
        "surface_fidelity", "explicit", True, lambda r, _f: _ta().validate_surface_fidelity(r)
    ),
    _ScopeEntry(
        "vendor_manifest", "explicit", True, lambda r, _f: _ta().validate_vendor_manifest(r)
    ),
    _ScopeEntry(
        "setpoint_coherence", "explicit", True, lambda r, _f: _ta().validate_setpoint_coherence(r)
    ),
    _ScopeEntry(
        "rendition_freshness", "explicit", True, lambda r, _f: _rendition_freshness_runner(r)
    ),
    _ScopeEntry(
        "rendition_floor_coherence",
        "explicit",
        True,
        lambda r, _f: _rendition_floor_coherence_runner(r),
    ),
    _ScopeEntry(
        "corpus_retirement_witness",
        "default",
        True,
        lambda r, _f: _ta().validate_corpus_retirement_witness(r),
    ),
    _ScopeEntry("kind_invariance", "explicit", True, lambda r, _f: _ta().audit_kind_invariance(r)),
    _ScopeEntry("persona_witness", "explicit", True, lambda r, _f: _ta().audit_persona_witness(r)),
    _ScopeEntry("receipt_shape", "explicit", True, lambda r, _f: _ta().audit_receipt_shape(r)),
    _ScopeEntry(
        "brief_reconcile", "explicit", True, lambda r, _f: _ta().validate_brief_reconcile(r)
    ),
    _ScopeEntry(
        "brief_structure", "explicit", True, lambda r, _f: _ta().validate_brief_structure(r)
    ),
    _ScopeEntry("router_tables", "explicit", True, lambda r, _f: _ta().audit_router_tables(r)),
    _ScopeEntry(
        "req_kind_discipline", "explicit", True, lambda r, _f: _validate_req_kind_discipline(r)
    ),
    _ScopeEntry(
        "status_writer_coverage",
        "explicit",
        True,
        lambda r, _f: _ta().audit_status_writer_coverage(r),
    ),
    _ScopeEntry(
        "transcribed_adr_counts",
        "explicit",
        True,
        lambda r, _f: _ta().audit_transcribed_counts(r),
    ),
    _ScopeEntry("ontology_purity", "explicit", True, lambda r, _f: _ontology_purity_runner(r)),
    _ScopeEntry(
        "brief_command_shape", "explicit", True, lambda r, _f: _ta().audit_brief_command_shape(r)
    ),
    _ScopeEntry(
        "tautological_test_audit",
        "explicit",
        True,
        lambda r, _f: _validate_tautological_test_audit(r),
    ),
    _ScopeEntry(
        "task_envelope_coherence",
        "explicit",
        True,
        lambda r, _f: _validate_task_envelope_coherence(r),
    ),
    _ScopeEntry("closeout_proof", "explicit", True, lambda r, _f: _ta().validate_closeout_proof(r)),
    _ScopeEntry("okf_conformance", "explicit", True, lambda r, _f: _ta().audit_okf_conformance(r)),
    _ScopeEntry(
        "deprecated_verb_prescription",
        "explicit",
        True,
        lambda r, _f: _ta().audit_deprecated_verb_prescription(r),
    ),
)


def _default_scope_runners(
    project_root: Path,
    frontmatter_adr: str | None,
) -> dict[str, Callable[[], list[ValidationError]]]:
    """Runners for scopes that activate when no explicit flag is set (registry-derived)."""
    return {
        e.stem: partial(e.run, project_root, frontmatter_adr)
        for e in VALIDATOR_REGISTRY
        if e.tier == "default"
    }


def _taxonomy_runner(project_root: Path) -> list[ValidationError]:
    """Import trust_audits lazily (avoids circular-import risk at module load).

    Runs two independent assertion families under one scope: the ADR-0.0.17
    kind/semver decision tree, and the ADR-0.34.0 foundation-closure
    containment checks. They stay separate functions so the former's contract
    does not depend on the grandfather manifest's population state.
    """
    from gzkit.governance import trust_audits  # noqa: PLC0415
    from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
        audit_foundation_closure,
    )

    return trust_audits.audit_adr_taxonomy(project_root) + audit_foundation_closure(project_root)


def _invariant_coherence_runner(project_root: Path) -> list[ValidationError]:
    """Import trust_audits lazily (avoids circular-import risk at module load)."""
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return trust_audits.validate_invariant_coherence(project_root)


def _ontology_purity_runner(project_root: Path) -> list[ValidationError]:
    """Import ontology.purity lazily (avoids import cost at module load)."""
    from gzkit.ontology.purity import audit_ontology_purity  # noqa: PLC0415

    return audit_ontology_purity(project_root)


def _rendition_freshness_runner(project_root: Path) -> list[ValidationError]:
    """Corpus↔rendition drift gate (OBPI-0.0.37-22)."""
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return trust_audits.validate_rendition_freshness(project_root)


def _rendition_floor_coherence_runner(project_root: Path) -> list[ValidationError]:
    """Canon→rendition invariant-floor gate (GHI #623, corrective to ADR-0.0.37)."""
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return trust_audits.validate_rendition_floor_coherence(project_root)


def _explicit_scope_runners(
    project_root: Path,
) -> dict[str, Callable[[], list[ValidationError]]]:
    """Runners for scopes that only activate when explicitly requested (registry-derived)."""
    return {
        e.stem: partial(e.run, project_root, None)
        for e in VALIDATOR_REGISTRY
        if e.tier == "explicit"
    }


def _sensitivity_umbrella_runner(project_root: Path) -> list[ValidationError]:
    """Sensitivity audit for the --audits umbrella; floor-info findings filtered."""
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return [
        e
        for e in trust_audits.audit_sensitivity_binding(project_root)
        if e.type not in _SENSITIVITY_INFO_TYPES
    ]


def _evaluation_justify_binding_runner(
    project_root: Path, artifact_id_or_sentinel: str | None
) -> list[ValidationError]:
    """Run evaluation-justify-binding for all artifacts or a specific one."""
    from gzkit.governance.trust_audits.evaluation_justify_binding import (  # noqa: PLC0415
        validate_evaluation_justify_binding,
    )

    if artifact_id_or_sentinel in (None, "__all__"):
        return _scan_all_evaluation_justify_binding(project_root)
    return validate_evaluation_justify_binding(artifact_id_or_sentinel, project_root)


def _scan_all_evaluation_justify_binding(project_root: Path) -> list[ValidationError]:
    """Check evaluation-justify-binding for all artifacts with adr-evaluation events."""
    import json as _json  # noqa: PLC0415

    from gzkit.governance.trust_audits.evaluation_justify_binding import (  # noqa: PLC0415
        validate_evaluation_justify_binding,
    )

    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not ledger_path.exists():
        return []
    seen: set[str] = set()
    errors: list[ValidationError] = []
    for line in ledger_path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            ev = _json.loads(line)
        except _json.JSONDecodeError:
            continue
        if ev.get("event") == "adr-evaluation":
            artifact_id = ev.get("id", "")
            if artifact_id and artifact_id not in seen:
                seen.add(artifact_id)
                errors.extend(validate_evaluation_justify_binding(artifact_id, project_root))
    return errors


def _run_evaluation_justify_binding_solo(
    project_root: Path, artifact_id_or_sentinel: str | None, *, as_json: bool
) -> None:
    """Dedicated handler for `gz validate --evaluation-justify-binding` (exit 0/3)."""
    errors = _evaluation_justify_binding_runner(project_root, artifact_id_or_sentinel)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))  # noqa: T201
        raise SystemExit(3 if errors else 0)
    if not errors:
        console.print("[bold]Validated:[/bold] evaluation-justify-binding\n")
        console.print("[green]✓ No evaluation-justify-binding violations.[/green]")
        raise SystemExit(0)
    console.print("[bold]Validated:[/bold] evaluation-justify-binding\n")
    console.print(f"[red]❌ {len(errors)} violation(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {escape(e.artifact)}: {escape(e.message)}")
    raise SystemExit(3)


def _run_qc_binding_scope(project_root: Path, *, as_json: bool) -> None:
    """Dedicated handler for `gz validate --qc-binding` (exit 0/3)."""
    from gzkit.governance.trust_audits.qc_binding import audit_qc_binding  # noqa: PLC0415

    errors = audit_qc_binding(project_root)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))  # noqa: T201
        raise SystemExit(3 if errors else 0)
    if not errors:
        console.print("[bold]Validated:[/bold] qc-binding\n")
        console.print("[green]✓ No QC theater detected.[/green]")
        raise SystemExit(0)
    console.print("[bold]Validated:[/bold] qc-binding\n")
    console.print(f"[red]❌ {len(errors)} theater finding(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {escape(e.artifact)}: {escape(e.message)}")
    raise SystemExit(3)


def _run_fidelity_presence_scope(project_root: Path, *, as_json: bool) -> None:
    """Dedicated handler for `gz validate --fidelity-presence` (exit 0/3)."""
    from gzkit.governance.trust_audits.fidelity_presence import (  # noqa: PLC0415
        audit_fidelity_presence,
    )

    errors = audit_fidelity_presence(project_root)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))  # noqa: T201
        raise SystemExit(3 if errors else 0)
    if not errors:
        console.print("[bold]Validated:[/bold] fidelity-presence\n")
        console.print(
            "[green]✓ Every non-pool ADR Decision carries a Fidelity Assertions block.[/green]"
        )
        raise SystemExit(0)
    console.print("[bold]Validated:[/bold] fidelity-presence\n")
    console.print(f"[red]❌ {len(errors)} block-less ADR Decision(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {escape(e.artifact)}: {escape(e.message)}")
    raise SystemExit(3)


def _run_config_registry_scope(project_root: Path, *, as_json: bool) -> None:
    """Dedicated handler for `gz validate --config-registry` (exit 0/3)."""
    from gzkit.governance.trust_audits.config_registry import (  # noqa: PLC0415
        audit_config_registry,
    )

    errors = audit_config_registry(project_root)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))  # noqa: T201
        raise SystemExit(3 if errors else 0)
    console.print("[bold]Validated:[/bold] config-registry\n")
    if not errors:
        console.print("[green]✓ Every config registry carries a verified owner.[/green]")
        raise SystemExit(0)
    console.print(f"[red]❌ {len(errors)} unowned/incoherent config registry surface(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {escape(e.artifact)}: {escape(e.message)}")
    raise SystemExit(3)


def _run_waiver_ratchet_scope(project_root: Path, *, as_json: bool) -> None:
    """Dedicated handler for `gz validate --waiver-ratchet` (exit 0/3)."""
    from gzkit.governance.trust_audits.waiver_ratchet import (  # noqa: PLC0415
        audit_waiver_ratchet,
    )

    errors = audit_waiver_ratchet(project_root)
    if as_json:
        print(json.dumps([e.model_dump(exclude_none=True) for e in errors], indent=2))  # noqa: T201
        raise SystemExit(3 if errors else 0)
    if not errors:
        console.print("[bold]Validated:[/bold] waiver-ratchet\n")
        console.print(
            "[green]✓ Every registered waiver surface carries an honesty mechanism.[/green]"
        )
        raise SystemExit(0)
    console.print("[bold]Validated:[/bold] waiver-ratchet\n")
    console.print(f"[red]❌ {len(errors)} unratcheted waiver surface(s):[/red]\n")
    for e in errors:
        console.print(f"   [red]→[/red] {escape(e.artifact)}: {escape(e.message)}")
    raise SystemExit(3)


def _run_unscoped_rules_scope(project_root: Path, *, as_json: bool, allowlist_only: bool) -> None:
    """Dedicated handler for `gz validate --unscoped-rules` (exit 0/2/3)."""
    from gzkit.validators.unscoped_rules import (  # noqa: PLC0415
        format_allowlist_listing,
        run_unscoped_rules,
    )

    result = run_unscoped_rules(project_root)

    if allowlist_only:
        if as_json:
            payload = [e.model_dump(mode="json") for e in result.allowlist_entries]
            print(json.dumps(payload, indent=2))  # noqa: T201
        else:
            console.print(format_allowlist_listing(result.allowlist_entries))
        raise SystemExit(0)

    if as_json:
        print(result.model_dump_json(indent=2))  # noqa: T201
        raise SystemExit(result.exit_code)

    console.print("[bold]Validated:[/bold] unscoped-rules\n")
    if result.exit_code == 0:
        allowlisted_count = sum(1 for v in result.violations if v.allowlisted)
        console.print(
            f"[green]✓ {result.files_checked} rule file(s) checked "
            f"({allowlisted_count} allowlisted).[/green]"
        )
        raise SystemExit(0)

    if result.exit_code == 2:
        console.print(
            "[red]❌ Unable to read manifest or rule files — "
            "missing or malformed .gzkit/manifest.json or rule content.[/red]"
        )
        raise SystemExit(2)

    # exit_code == 3: policy breach — list non-allowlisted violations.
    console.print(
        f"[red]❌ {result.files_checked} rule file(s) scanned; "
        f"{sum(1 for v in result.violations if not v.allowlisted)} "
        "violation(s) require recovery:[/red]\n"
    )
    for v in result.violations:
        if v.allowlisted:
            continue
        detected = f" (detected: {v.detected_value!r})" if v.detected_value else ""
        console.print(f"   [red]→[/red] \\[{escape(v.reason)}] {v.file}{detected}")
    console.print(
        "\nRecovery: narrow `paths:` to a concrete glob, fold the content into "
        "AGENTS.md, or add an allowlist entry under `rules.unscoped_allowlist` "
        "in .gzkit/manifest.json (see ADR-0.0.20)."
    )
    raise SystemExit(3)


def _run_sensitivity_scope(
    project_root: Path,
    *,
    as_json: bool,
    explain: str | None,
) -> None:
    """Dedicated handler for `gz validate --sensitivity` (with optional --explain)."""
    from gzkit.governance.trust_audits import (  # noqa: PLC0415
        explain_sensitivity_for_paths,
    )

    if explain is not None:
        path_list = _parse_sensitivity_path_list(explain)
        payload = explain_sensitivity_for_paths(path_list, project_root)
        detected = payload["detected_sensitivity"]
        categories_raw = payload["matching_categories"]
        categories = list(categories_raw) if isinstance(categories_raw, tuple) else []
        input_raw = payload["input_globs"]
        input_globs = list(input_raw) if isinstance(input_raw, tuple) else []
        if as_json:
            serializable: dict[str, object] = {
                "detected_sensitivity": detected,
                "matching_categories": categories,
                "input_globs": input_globs,
            }
            if "error" in payload:
                serializable["error"] = payload["error"]
            print(json.dumps(serializable, indent=2))  # noqa: T201
        else:
            console.print("[bold]Sensitivity prediction[/bold]")
            console.print(f"  detected_sensitivity: {detected}")
            console.print(f"  matching_categories: {categories or '[]'}")
            console.print(f"  input_globs: {input_globs}")
            if "error" in payload:
                console.print(f"  [yellow]registry error:[/yellow] {escape(str(payload['error']))}")
        raise SystemExit(0)

    records, findings = _sensitivity_records(project_root)

    if as_json:
        payload = {
            "valid": len([f for f in findings if f.type in _POLICY_BREACH_ERROR_TYPES]) == 0,
            "records": records,
            "errors": [f.model_dump(exclude_none=True) for f in findings],
        }
        print(json.dumps(payload, indent=2))  # noqa: T201
    else:
        console.print("[bold]Validated:[/bold] sensitivity\n")
        if not findings:
            console.print(
                f"[green]✓ {len(records)} brief(s) checked; no escape "
                "attempts and registry healthy.[/green]"
            )
        else:
            for finding in findings:
                console.print(f"  [red]→[/red] \\[{finding.type}] {escape(finding.artifact)}")
                console.print(f"      {escape(finding.message)}")

    if any(f.type in _POLICY_BREACH_ERROR_TYPES for f in findings):
        raise SystemExit(3)
    raise SystemExit(0)


def _rule_version_markers_runner(project_root: Path) -> list[ValidationError]:
    """Run the rule-version-marker validator (skill-surface-sync #2)."""
    from gzkit.validators.rule_version_markers import (  # noqa: PLC0415
        audit_rule_version_markers_errors,
    )

    return audit_rule_version_markers_errors(project_root)


def _invariant_witness_runner(project_root: Path) -> list[ValidationError]:
    """Run the constitutional-invariant structural-witness resolver (GHI #623/#746)."""
    from gzkit.governance.trust_audits.invariant_witness import (  # noqa: PLC0415
        validate_invariant_witnesses,
    )

    return validate_invariant_witnesses(project_root)


def _unscoped_rules_runner(project_root: Path) -> list[ValidationError]:
    """Run the unscoped-rules validator and map violations to ValidationError."""
    from gzkit.validators.unscoped_rules import run_unscoped_rules  # noqa: PLC0415

    result = run_unscoped_rules(project_root)
    errors: list[ValidationError] = []
    if result.exit_code == 2:
        errors.append(
            ValidationError(
                type="unscoped-rules",
                artifact=".gzkit/manifest.json",
                message="Unscoped-rules validator hit an I/O error "
                "(missing/malformed manifest or unreadable rule file)",
            )
        )
        return errors
    for v in result.violations:
        if v.allowlisted:
            continue
        detected = f" (detected: {v.detected_value!r})" if v.detected_value else ""
        errors.append(
            ValidationError(
                type="unscoped-rules",
                artifact=v.file,
                message=(
                    f"Agent rule is unscoped — {v.reason}{detected}. "
                    "Narrow `paths:` to a concrete glob, fold the content into "
                    "AGENTS.md, or add an allowlist entry under "
                    "rules.unscoped_allowlist (see ADR-0.0.20)."
                ),
            )
        )
    return errors


def _run_scope_checks(
    project_root: Path,
    default_scopes: dict[str, bool],
    explicit_scopes: dict[str, bool],
    run_all: bool,
    frontmatter_adr: str | None = None,
) -> list[ValidationError]:
    """Dispatch validation checks based on active scopes."""
    from gzkit.mx import checkpoint  # noqa: PLC0415

    scope_levels = {e.stem: e.level for e in VALIDATOR_REGISTRY}

    def _grounds(scope: str) -> bool:
        # Unregistered scope -> CRITICAL: a name nothing declares, nothing vouched for.
        return checkpoint.blocks(scope, scope_levels.get(scope, _mx_levels.CRITICAL), project_root)

    errors: list[ValidationError] = []
    default_runners = _default_scope_runners(project_root, frontmatter_adr)
    explicit_runners = _explicit_scope_runners(project_root)

    for scope, runner in default_runners.items():
        if run_all and scope in default_scopes or default_scopes.get(scope, False):
            scope_errors = runner()
            if _grounds(scope):
                errors.extend(scope_errors)
    for scope, runner in explicit_runners.items():
        if explicit_scopes.get(scope):
            scope_errors = runner()
            if _grounds(scope):
                errors.extend(scope_errors)
    return errors


def _validate_exemplar_corpus(project_root: Path) -> list[ValidationError]:
    """Validate data/exemplar_corpus.json against the ExemplarCorpus Pydantic model.

    Returns an empty list when the file is absent (the corpus is authored in a
    later OBPI stage).  Returns one ValidationError per Pydantic validation
    failure, or a single ValidationError on JSON parse failure.
    """
    corpus_path = project_root / "data" / "exemplar_corpus.json"
    if not corpus_path.is_file():
        return []

    artifact = corpus_path.relative_to(project_root).as_posix()
    errors: list[ValidationError] = []
    try:
        raw = json.loads(corpus_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        errors.append(
            ValidationError(
                type="exemplar_corpus",
                artifact=artifact,
                message=f"exemplar_corpus.json is not valid JSON: {exc}",
            )
        )
        return errors

    try:
        ExemplarCorpus.model_validate(raw)
    except PydanticValidationError as exc:
        for err in exc.errors():
            field = ".".join(str(loc) for loc in err["loc"])
            errors.append(
                ValidationError(
                    type="exemplar_corpus",
                    artifact=artifact,
                    message=err["msg"],
                    field=field or None,
                )
            )
    return errors


def _validate_ownership_declarations(project_root: Path) -> list[ValidationError]:
    """Validate `.gzkit/ownership/*.json` against `section_ownership.json` (REQ-0.35.0-04-08).

    Mirrors `_validate_exemplar_corpus`'s shape: absent directory -> [];
    JSON parse failure -> one ValidationError; otherwise schema-validate
    (`jsonschema`) then `OwnershipDeclaration.model_validate` -- one
    ValidationError per validation failure. Schema-validation catches
    artifact-vs-schema drift; model-validation catches artifact-vs-code
    drift (both were silently unwitnessed before this validator existed --
    Step-4b adversary finding 3, OBPI-0.35.0-04).
    """
    ownership_dir = project_root / ".gzkit" / "ownership"
    if not ownership_dir.is_dir():
        return []

    schema_path = Path(__file__).parent.parent / "schemas" / "section_ownership.json"
    schema = json.loads(schema_path.read_text(encoding="utf-8"))

    errors: list[ValidationError] = []
    for decl_path in sorted(ownership_dir.glob("*.json")):
        artifact = decl_path.relative_to(project_root).as_posix()
        try:
            raw = json.loads(decl_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(
                ValidationError(
                    type="ownership_declaration",
                    artifact=artifact,
                    message=(
                        f"{artifact} is not valid JSON: {exc}. REQ-0.35.0-04-08 "
                        "requires `gz validate --documents` to admit the "
                        "declaration's shape, so a malformed file fails closed "
                        "here rather than passing vacuously. Fix the JSON syntax "
                        "and re-run `uv run gz validate --documents`."
                    ),
                )
            )
            continue

        try:
            jsonschema.validate(raw, schema)
        except jsonschema.exceptions.ValidationError as exc:
            errors.append(
                ValidationError(
                    type="ownership_declaration",
                    artifact=artifact,
                    message=(
                        f"{artifact} does not conform to "
                        "src/gzkit/schemas/section_ownership.json: "
                        f"{exc.message}. REQ-0.35.0-04-08 requires the "
                        "declaration to validate against its schema before "
                        "`gz validate --documents` can admit it. Fix the "
                        "declaration's shape and re-run "
                        "`uv run gz validate --documents`."
                    ),
                    field=".".join(str(p) for p in exc.absolute_path) or None,
                )
            )
            continue

        try:
            OwnershipDeclaration.model_validate(raw)
        except PydanticValidationError as exc:
            for err in exc.errors():
                field = ".".join(str(loc) for loc in err["loc"])
                errors.append(
                    ValidationError(
                        type="ownership_declaration",
                        artifact=artifact,
                        message=(
                            f"{artifact} failed OwnershipDeclaration model "
                            f"validation: {err['msg']}. REQ-0.35.0-04-08 "
                            "requires the declaration to construct the domain "
                            "model gzkit code relies on, not merely match the "
                            "JSON Schema shape. Fix the declaration and re-run "
                            "`uv run gz validate --documents`."
                        ),
                        field=field or None,
                    )
                )
    return errors


def _validate_manifest_documents(project_root: Path) -> list[ValidationError]:
    """Validate documents declared in the manifest."""
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.is_file():
        return []

    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    errors: list[ValidationError] = []
    for _artifact_type, artifact_config in manifest.get("artifacts", {}).items():
        artifact_dir = project_root / artifact_config.get("path", "")
        schema = artifact_config.get("schema", "")
        schema_name = schema.replace("gzkit.", "").replace(".v1", "")
        # OBPI corpus hygiene is owned by the version-aware `briefs` scope
        # (_validate_obpi_briefs); strict authored checks by `gz obpi validate
        # --authored`. Raw-schema-validating the historical OBPI corpus here
        # treats every attested-completed brief as newly-authored and produces
        # thousands of non-actionable schema-section failures (GHI #500).
        if schema_name == "obpi":
            continue
        if artifact_dir.exists():
            _PREFIX = {"adr": "ADR-"}
            prefix = _PREFIX.get(schema_name, "")
            doc_iter = artifact_dir.rglob(f"{prefix}*.md") if prefix else artifact_dir.glob("*.md")
            for doc in doc_iter:
                errors.extend(validate_document(doc, schema_name))
    errors.extend(_validate_exemplar_corpus(project_root))
    errors.extend(_validate_ownership_declarations(project_root))
    return errors


def _resolve_scopes(checks: dict[str, bool]) -> list[str]:
    """Build the list of validated scope names from the check flags (registry-derived).

    Default-tier scopes run on the no-flag path; explicit-tier scopes only when
    their flag is set. Both come from ``VALIDATOR_REGISTRY`` in registry order.
    """
    run_all_scopes = [e.stem for e in VALIDATOR_REGISTRY if e.tier == "default"]
    opt_in_scopes = [e.stem for e in VALIDATOR_REGISTRY if e.tier == "explicit"]

    run_all = not any(checks.get(s, False) for s in run_all_scopes + opt_in_scopes)
    scopes = [s for s in run_all_scopes if run_all or checks.get(s, False)]
    scopes += [s for s in opt_in_scopes if checks.get(s, False)]
    return scopes


_POLICY_BREACH_ERROR_TYPES: frozenset[str] = frozenset(
    {
        "frontmatter",
        "chores_layout",
        "complexity_doctrine_links",
        "complexity_thresholds",
        "insights_shape",
        "instructions_files_budget",
        "surface_delivery_witness",
        "agents_md_map_conformance",
        "sensitivity-escape-attempt",
        "sensitivity-floor-violation",
        "sensitivity-registry-missing",
        "sensitivity-registry-malformed",
        "sensitivity-malformed-allowlist",
        "absorption_duplicate",
        "evaluation-justify-binding",
        "distribution",
        "bullet_retention",
        "surface_weight",
        "pointer_anchors",
        "kind_invariance",
        "persona_witness",
        "receipt_shape",
        "setpoint_coherence",
        "rendition_freshness",
        "rendition_floor_coherence",
        "corpus_retirement_witness",
        "invariant_coherence",
        "invariant_witness",
        "brief_reconcile",
        "brief_structure",
        "router_tables",
        "req_kind_discipline",
        "status_writer_coverage",
        "transcribed_adr_counts",
        "ontology_purity",
        "brief_command_shape",
        "foundation_kind_closed",
        "grandfather_dangling",
        "foundation_limbo",
        "tautological_test_audit",
        "task_envelope_coherence",
        "closeout_proof",
        "lock_exchange_coupling",
        "okf_conformance",
        "deprecated_verb_prescription",
    }
)

_SENSITIVITY_INFO_TYPES: frozenset[str] = frozenset({"sensitivity-floor-info"})


def _print_validation_result(
    errors: list[ValidationError],
    scopes: list[str],
    *,
    frontmatter_only: bool = False,
) -> None:
    """Print human-readable results and exit per CLI doctrine 4-code map.

    Exit codes:
        * 0 — clean
        * 1 — validation errors outside the policy-breach taxonomy
        * 3 — policy breach only (frontmatter drift, chores layout drift)

    Policy-breach error types (``_POLICY_BREACH_ERROR_TYPES``) route to
    exit 3 per ``.gzkit/rules/cli.md``; mixed runs that contain at least
    one non-policy-breach error continue to route to exit 1 so that
    operator-fixable errors are not masked by the stricter policy code.

    When ``frontmatter_only`` and no drift is found, suppresses the success
    prose (REQ-01: empty-input / fully-coherent output is empty).
    """
    policy_errors = [e for e in errors if e.type in _POLICY_BREACH_ERROR_TYPES]
    other_errors = [e for e in errors if e.type not in _POLICY_BREACH_ERROR_TYPES]

    if not errors:
        if frontmatter_only:
            return
        console.print(f"[bold]Validated:[/bold] {', '.join(scopes)}\n")
        console.print(f"[green]✓ All validations passed ({len(scopes)} scopes).[/green]")
        return

    console.print(f"[bold]Validated:[/bold] {', '.join(scopes)}\n")
    console.print(f"[red]❌ Validation failed with {len(errors)} error(s):[/red]\n")
    for error in errors:
        console.print(f"   [red]→[/red] \\[{error.type}] {escape(error.artifact)}")
        console.print(f"    {escape(error.message)}")
        if error.field:
            console.print(f"    Field: {escape(error.field)}")
        console.print()

    if other_errors:
        raise SystemExit(1)
    if policy_errors:
        raise SystemExit(3)


def _resolve_attestation_text(value: str, project_root: Path) -> str:
    """Return the attestation text, expanding ``@path`` references."""
    if value.startswith("@"):
        target = Path(value[1:])
        if not target.is_absolute():
            target = project_root / target
        return target.read_text(encoding="utf-8")
    return value


def _render_attestation_result(
    result: AttestationReceiptValidationResult,
    *,
    as_json: bool,
) -> None:
    if as_json:
        payload = {
            "exit_code": result.exit_code,
            "warn_only": result.warn_only,
            "entries": [entry.model_dump() for entry in result.entries],
        }
        print(json.dumps(payload, indent=2))  # noqa: T201
        return
    if not result.entries:
        if result.warn_only:
            console.print(
                "[yellow]⚠ No ARB receipt IDs cited (lite + non-foundation: warning).[/yellow]"
            )
        else:
            console.print(
                "[red]❌ No ARB receipt IDs cited (heavy or foundation: fail-closed).[/red]"
            )
        return
    if result.exit_code == 0:
        console.print(f"[green]✓ {len(result.entries)} attestation receipt(s) resolved.[/green]")
        return
    console.print(
        f"[red]❌ Attestation receipt validation failed ({len(result.entries)} entry):[/red]"
    )
    for entry in result.entries:
        marker = "[green]✓[/green]" if entry.status == "resolved" else "[red]→[/red]"
        run_id = entry.run_id or "<malformed>"
        console.print(f"  {marker} \\[{entry.status}] {escape(run_id)}")
        console.print(f"      {escape(entry.message)}")


def _run_attestation_receipts_scope(
    project_root: Path,
    *,
    attestation_text: str,
    lane: str,
    kind: str,
    as_json: bool,
) -> None:
    text = _resolve_attestation_text(attestation_text, project_root)
    result = validate_attestation_receipts(text, lane=lane, kind=kind, project_root=project_root)
    _render_attestation_result(result, as_json=as_json)
    if result.exit_code != 0:
        raise SystemExit(result.exit_code)


def _refuse_combined_solo_scopes(combined: list[str]) -> None:
    """Fail closed when a solo-only scope is requested alongside another scope.

    GHI #704: these scopes previously carried an ``and not other_scopes_active``
    guard, so combining one with any other scope skipped its branch silently and
    the run still reported ``✓ All validations passed`` — a false green for a
    gate that never executed, contradicting ``AGENTS.md`` § Architectural
    Boundaries #6 (derived views must not misreport what actually ran).

    Three-part recovery prose per ``.gzkit/rules/guardrail-feedback-prose.md``.
    """
    flags = ", ".join(combined)
    many = len(combined) > 1
    console.print(
        f"[red]Error:[/red] {flags} cannot be combined with other validate scopes.\n"
        "  Why: a solo-only scope owns the full 0/2/3 exit lifecycle and "
        "short-circuits the aggregate run. Combining one used to drop it "
        "silently while still reporting success — a false green for a gate that "
        "never ran (GHI #704).\n"
        f"  Next step: run {'each one' if many else 'it'} alone — "
        f"`uv run gz validate {combined[0]}`."
    )
    raise SystemExit(1)


def _inventory():  # noqa: ANN202  (module handle; mirrors `_ta()`)
    """Lazily resolve the inventory-scope handler module."""
    from gzkit.commands import validate_inventory_scopes  # noqa: PLC0415

    return validate_inventory_scopes


def _dispatch_early_return_scopes(
    project_root: Path,
    *,
    other_scopes_active: bool,
    check_distribution_regenerate: bool,
    check_distribution: bool,
    attestation_receipts: str | None,
    attestation_lane: str,
    attestation_kind: str,
    check_evaluation_justify_binding: str | None,
    check_unscoped_rules: bool,
    unscoped_rules_allowlist_only: bool,
    check_sensitivity: bool,
    sensitivity_explain: str | None,
    check_qc_binding: bool,
    check_fidelity_presence: bool,
    check_waiver_ratchet: bool,
    check_config_registry: bool,
    check_gate_callers: bool,
    check_exemption_controls: bool,
    check_audits: bool,
    as_json: bool,
) -> bool:
    """Handle scopes that own their full 0/2/3 lifecycle and return immediately.

    Returns True when one of these scopes handled the invocation — the caller
    must then return without running the aggregate validation path.
    """
    if check_audits:
        # The umbrella owns its own 0/2/3 lifecycle: it runs each solo-only
        # member in a pass of its own, so it belongs here beside them rather
        # than on the aggregate path that the solo-only fence refuses (#704).
        from gzkit.commands.validate_audits import run_audits_umbrella  # noqa: PLC0415

        run_audits_umbrella(as_json=as_json)
        return True
    if check_distribution_regenerate:
        if not check_distribution:
            console.print(
                "[yellow]Warning:[/yellow] --regenerate has no effect without --distribution."
            )
            return True
        from gzkit.governance.trust_audits.distribution import (
            regenerate_distribution_baseline,  # noqa: PLC0415
        )

        result = regenerate_distribution_baseline(project_root)
        console.print(
            f"[green]✓[/green] Baseline regenerated: {result['file_count']} files across "
            f"{', '.join(result['surfaces_walked'])}. "
            f"Ledger event emitted (distribution_baseline_regenerated)."
        )
        return True
    if attestation_receipts is not None:
        _run_attestation_receipts_scope(
            project_root,
            attestation_text=attestation_receipts,
            lane=attestation_lane,
            kind=attestation_kind,
            as_json=as_json,
        )
        return True
    # GHI #704: a solo-only scope combined with any other scope is refused, not
    # dropped. One fence for the whole family — the per-scope
    # `and not other_scopes_active` guards this replaces were copied forward on
    # every new addition, so each new scope silently inherited the false green.
    if other_scopes_active:
        combined = [
            flag
            for flag, requested in (
                ("--evaluation-justify-binding", check_evaluation_justify_binding is not None),
                ("--unscoped-rules", check_unscoped_rules),
                ("--sensitivity", check_sensitivity),
                ("--qc-binding", check_qc_binding),
                ("--fidelity-presence", check_fidelity_presence),
                ("--waiver-ratchet", check_waiver_ratchet),
                ("--config-registry", check_config_registry),
                ("--gate-callers", check_gate_callers),
                ("--exemption-controls", check_exemption_controls),
            )
            if requested
        ]
        if combined:
            _refuse_combined_solo_scopes(combined)
    if check_evaluation_justify_binding is not None:
        _run_evaluation_justify_binding_solo(
            project_root, check_evaluation_justify_binding, as_json=as_json
        )
        return True
    if check_unscoped_rules:
        _run_unscoped_rules_scope(
            project_root, as_json=as_json, allowlist_only=unscoped_rules_allowlist_only
        )
        return True
    if check_sensitivity:
        _run_sensitivity_scope(project_root, as_json=as_json, explain=sensitivity_explain)
        return True
    if sensitivity_explain and not check_sensitivity:
        # `--explain` without `--sensitivity` is the explain-only fast-path.
        _run_sensitivity_scope(project_root, as_json=as_json, explain=sensitivity_explain)
        return True
    if unscoped_rules_allowlist_only:
        # --allowlist-only without --unscoped-rules still prints the listing.
        _run_unscoped_rules_scope(project_root, as_json=as_json, allowlist_only=True)
        return True
    # Uniform tail: every remaining solo scope takes exactly
    # ``(project_root, as_json=...)`` and raises SystemExit on all paths, so it
    # dispatches from a table rather than a per-scope `if` rung. The ladder this
    # replaces is what tipped the function past its complexity ceiling when the
    # config-registry scope was added (GHI #929); a table absorbs the next scope
    # for free. `gate_callers` had no `return True` under the ladder — that was
    # unreachable, not load-bearing (`run_gate_callers_scope` exits on every
    # path), and the table normalizes it.
    # The two inventory scopes resolve their runner through ``_inventory()``
    # LAZILY inside the branch, exactly as the ladder did: building the table
    # with ``_inventory().run_...`` would import that module on every dispatch,
    # including invocations that request none of these scopes.
    uniform: tuple[tuple[bool, Callable[[], Callable[..., None]]], ...] = (
        (check_qc_binding, lambda: _run_qc_binding_scope),
        (check_fidelity_presence, lambda: _run_fidelity_presence_scope),
        (check_waiver_ratchet, lambda: _run_waiver_ratchet_scope),
        (check_config_registry, lambda: _run_config_registry_scope),
        (check_gate_callers, lambda: _inventory().run_gate_callers_scope),
        (check_exemption_controls, lambda: _inventory().run_exemption_controls_scope),
    )
    for requested, resolve_scope in uniform:
        if requested:
            resolve_scope()(project_root, as_json=as_json)
            return True
    return False


def validate(
    check_manifest: bool,
    check_documents: bool,
    check_surfaces: bool,
    check_ledger: bool,
    check_instructions: bool,
    check_briefs: bool,
    check_personas: bool = False,
    check_interviews: bool = False,
    check_decomposition: bool = False,
    check_requirements: bool = False,
    check_commit_trailers: bool = False,
    check_frontmatter: bool = False,
    check_version: bool = False,
    check_type_ignores: bool = False,
    check_cli_alignment: bool = False,
    check_event_handlers: bool = False,
    check_event_schemas: bool = False,
    check_producer_fields: bool = False,
    check_validator_fields: bool = False,
    check_authorship: bool = False,
    check_python_version_pins: bool = False,
    check_utf8_prefix: bool = False,
    check_test_tiers: bool = False,
    check_pydantic_models: bool = False,
    check_class_size: bool = False,
    check_version_release: bool = False,
    check_pool_adr_isolation: bool = False,
    check_pool_interview: bool = False,
    check_behave_req_tags: bool = False,
    check_skill_alignment: bool = False,
    check_advisory_scorecard: bool = False,
    check_complexity_doctrine_links: bool = False,
    check_complexity_thresholds: bool = False,
    check_reconcile_freshness: bool = False,
    check_insights_shape: bool = False,
    check_instructions_files_budget: bool = False,
    check_agents_md_map_conformance: bool = False,
    check_adr_status_fresh: bool = False,
    check_obpi_lifecycle_coherence: bool = False,
    check_adversarial_validation: bool = False,
    check_red_parity: bool = False,
    check_session_green_gate: bool = False,
    check_orientation_freshness: bool = False,
    check_taxonomy: bool = False,
    check_brief_headings: bool = False,
    check_brief_cross_references: bool = False,
    check_brief_demo_section: bool = False,
    check_chores_layout: bool = False,
    check_unscoped_rules: bool = False,
    check_rule_version_markers: bool = False,
    unscoped_rules_allowlist_only: bool = False,
    check_sensitivity: bool = False,
    sensitivity_explain: str | None = None,
    check_doc_surface_parity: bool = False,
    check_absorption_duplicates: bool = False,
    check_orphaned_implementation: bool = False,
    check_evaluation_justify_binding: str | None = None,
    check_intrinsic_attestation: bool = False,
    check_advisor_proof_binding: bool = False,
    check_lock_exchange_coupling: bool = False,
    check_distribution: bool = False,
    check_distribution_regenerate: bool = False,
    check_wheel_path_literals: bool = False,
    check_changelog: bool = False,
    check_bullet_retention: bool = False,
    check_surface_weight: bool = False,
    surface_weight_recalibrate: bool = False,
    recalibrate_attestor: str = "",
    recalibrate_reason: str = "",
    check_pointer_anchors: bool = False,
    check_surface_fidelity: bool = False,
    check_vendor_manifest: bool = False,
    check_kind_invariance: bool = False,
    check_persona_witness: bool = False,
    check_receipt_shape: bool = False,
    check_invariant_coherence: bool = False,
    check_invariant_witness: bool = False,
    check_brief_reconcile: bool = False,
    check_brief_structure: bool = False,
    check_router_tables: bool = False,
    check_req_kind_discipline: bool = False,
    check_status_writer_coverage: bool = False,
    check_transcribed_adr_counts: bool = False,
    check_ontology_purity: bool = False,
    check_brief_command_shape: bool = False,
    check_tautological_test_audit: bool = False,
    check_setpoint_coherence: bool = False,
    check_rendition_freshness: bool = False,
    check_rendition_floor_coherence: bool = False,
    check_corpus_retirement_witness: bool = False,
    check_task_envelope_coherence: bool = False,
    check_closeout_proof: bool = False,
    check_okf_conformance: bool = False,
    check_deprecated_verb_prescription: bool = False,
    check_qc_binding: bool = False,
    check_fidelity_presence: bool = False,
    check_waiver_ratchet: bool = False,
    check_config_registry: bool = False,
    check_gate_callers: bool = False,
    check_exemption_controls: bool = False,
    check_audits: bool = False,
    attestation_receipts: str | None = None,
    attestation_lane: str = "heavy",
    attestation_kind: str = "feature",
    as_json: bool = False,
    check_line_endings: bool = False,
    frontmatter_adr: str | None = None,
    frontmatter_explain: str | None = None,
) -> None:
    """Validate governance artifacts against schemas.

    Exit codes follow the CLI doctrine 4-code map:
        * 0 — clean
        * 1 — user/config error or non-frontmatter validation error
        * 2 — system/IO error (raised by underlying validators)
        * 3 — frontmatter-ledger policy breach (drift found)
    """
    project_root = get_project_root()

    if surface_weight_recalibrate:
        from gzkit.commands.validate_surface_weight import (  # noqa: PLC0415
            run_surface_weight_recalibrate,
        )

        run_surface_weight_recalibrate(
            project_root,
            scoped=check_surface_weight,
            attestor=recalibrate_attestor,
            reason=recalibrate_reason,
            as_json=as_json,
        )

    # --explain implies --frontmatter and scope (must precede _other_scopes_active).
    if frontmatter_explain:
        check_frontmatter = True
        frontmatter_adr = frontmatter_explain

    checks = {
        "line_endings": check_line_endings,
        "manifest": check_manifest,
        "documents": check_documents,
        "surfaces": check_surfaces,
        "ledger": check_ledger,
        "instructions": check_instructions,
        "briefs": check_briefs,
        "personas": check_personas,
        "interviews": check_interviews,
        "decomposition": check_decomposition,
        "requirements": check_requirements,
        "commit_trailers": check_commit_trailers,
        "frontmatter": check_frontmatter,
        "version": check_version,
        "type_ignores": check_type_ignores,
        "cli_alignment": check_cli_alignment,
        "event_handlers": check_event_handlers,
        "event_schemas": check_event_schemas,
        "producer_fields": check_producer_fields,
        "validator_fields": check_validator_fields,
        "authorship": check_authorship,
        "python_version_pins": check_python_version_pins,
        "utf8_prefix": check_utf8_prefix,
        "test_tiers": check_test_tiers,
        "pydantic_models": check_pydantic_models,
        "class_size": check_class_size,
        "version_release": check_version_release,
        "pool_adr_isolation": check_pool_adr_isolation,
        "pool_interview": check_pool_interview,
        "behave_req_tags": check_behave_req_tags,
        "skill_alignment": check_skill_alignment,
        "advisory_scorecard": check_advisory_scorecard,
        "complexity_doctrine_links": check_complexity_doctrine_links,
        "complexity_thresholds": check_complexity_thresholds,
        "reconcile_freshness": check_reconcile_freshness,
        "insights_shape": check_insights_shape,
        "instructions_files_budget": check_instructions_files_budget,
        "agents_md_map_conformance": check_agents_md_map_conformance,
        "adr_status_fresh": check_adr_status_fresh,
        "obpi_lifecycle_coherence": check_obpi_lifecycle_coherence,
        "adversarial_validation": check_adversarial_validation,
        "red_parity": check_red_parity,
        "session_green_gate": check_session_green_gate,
        "orientation_freshness": check_orientation_freshness,
        "taxonomy": check_taxonomy,
        "brief_headings": check_brief_headings,
        "brief_cross_references": check_brief_cross_references,
        "brief_demo_section": check_brief_demo_section,
        "chores_layout": check_chores_layout,
        "unscoped_rules": check_unscoped_rules,
        "sensitivity": check_sensitivity,
        "doc_surface_parity": check_doc_surface_parity,
        "absorption_duplicates": check_absorption_duplicates,
        "orphaned_implementation": check_orphaned_implementation,
        "evaluation_justify_binding": check_evaluation_justify_binding is not None,
        "intrinsic_attestation": check_intrinsic_attestation,
        "advisor_proof_binding": check_advisor_proof_binding,
        "lock_exchange_coupling": check_lock_exchange_coupling,
        "distribution": check_distribution,
        "wheel_path_literals": check_wheel_path_literals,
        "changelog": check_changelog,
        "bullet_retention": check_bullet_retention,
        "surface_weight": check_surface_weight,
        "pointer_anchors": check_pointer_anchors,
        "surface_fidelity": check_surface_fidelity,
        "vendor_manifest": check_vendor_manifest,
        "setpoint_coherence": check_setpoint_coherence,
        "rendition_freshness": check_rendition_freshness,
        "rendition_floor_coherence": check_rendition_floor_coherence,
        "corpus_retirement_witness": check_corpus_retirement_witness,
        "kind_invariance": check_kind_invariance,
        "persona_witness": check_persona_witness,
        "receipt_shape": check_receipt_shape,
        "invariant_coherence": check_invariant_coherence,
        "invariant_witness": check_invariant_witness,
        "brief_reconcile": check_brief_reconcile,
        "brief_structure": check_brief_structure,
        "router_tables": check_router_tables,
        "req_kind_discipline": check_req_kind_discipline,
        "status_writer_coverage": check_status_writer_coverage,
        "transcribed_adr_counts": check_transcribed_adr_counts,
        "ontology_purity": check_ontology_purity,
        "brief_command_shape": check_brief_command_shape,
        "tautological_test_audit": check_tautological_test_audit,
        "task_envelope_coherence": check_task_envelope_coherence,
        "closeout_proof": check_closeout_proof,
        "okf_conformance": check_okf_conformance,
        "deprecated_verb_prescription": check_deprecated_verb_prescription,
    }
    # A solo early-return scope (--sensitivity, --evaluation-justify-binding, ...)
    # runs solo only when no *other* aggregate scope is active.
    _other_scopes_active = any(
        checks.get(e.stem, False) for e in VALIDATOR_REGISTRY if e.in_other_scopes
    )
    if _dispatch_early_return_scopes(
        project_root,
        other_scopes_active=_other_scopes_active,
        check_distribution_regenerate=check_distribution_regenerate,
        check_distribution=check_distribution,
        attestation_receipts=attestation_receipts,
        attestation_lane=attestation_lane,
        attestation_kind=attestation_kind,
        check_evaluation_justify_binding=check_evaluation_justify_binding,
        check_unscoped_rules=check_unscoped_rules,
        unscoped_rules_allowlist_only=unscoped_rules_allowlist_only,
        check_sensitivity=check_sensitivity,
        sensitivity_explain=sensitivity_explain,
        check_qc_binding=check_qc_binding,
        check_fidelity_presence=check_fidelity_presence,
        check_waiver_ratchet=check_waiver_ratchet,
        check_config_registry=check_config_registry,
        check_gate_callers=check_gate_callers,
        check_exemption_controls=check_exemption_controls,
        check_audits=check_audits,
        as_json=as_json,
    ):
        return

    errors = _collect_errors(project_root, checks, frontmatter_adr=frontmatter_adr)

    if as_json:
        payload: dict[str, object] = {
            "valid": len(errors) == 0,
            "errors": [e.model_dump(exclude_none=True) for e in errors],
        }
        if check_frontmatter:
            payload["drift"] = [
                {
                    "path": e.artifact,
                    "field": e.field,
                    "ledger_value": e.ledger_value,
                    "frontmatter_value": e.frontmatter_value,
                }
                for e in errors
                if e.type == "frontmatter"
            ]
        print(json.dumps(payload, indent=2))  # noqa: T201
        return

    scopes = _resolve_scopes(checks)
    frontmatter_only = scopes == ["frontmatter"]

    if frontmatter_explain:
        _render_frontmatter_explain(errors, frontmatter_explain)
        if any(e.type == "frontmatter" for e in errors):
            raise SystemExit(3)
        return

    _print_validation_result(errors, scopes, frontmatter_only=frontmatter_only)
