"""Validate command implementation."""

import json
import re
from collections.abc import Callable
from functools import partial
from pathlib import Path
from types import ModuleType
from typing import NamedTuple

from pydantic import ValidationError as PydanticValidationError

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
from gzkit.commands.validate_frontmatter import (
    _render_frontmatter_explain,
    validate_frontmatter_coherence,
)
from gzkit.commands.validate_req_kind import _validate_req_kind_discipline
from gzkit.commands.validate_task_envelope import _validate_task_envelope_coherence
from gzkit.commands.version_sync import validate_version_consistency
from gzkit.governance.trust_audits import (
    AttestationReceiptValidationResult,
    validate_attestation_receipts,
)
from gzkit.instruction_audit import audit_instructions
from gzkit.models.exemplar import ExemplarCorpus
from gzkit.validate import (
    ValidationError,
    parse_frontmatter,
    validate_document,
    validate_ledger,
    validate_manifest,
    validate_surfaces,
)
from gzkit.validate_pkg.document import is_adr_shape_grandfathered, is_pool_adr_path


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


def _ta() -> ModuleType:
    """Lazy ``trust_audits`` accessor.

    Preserves the module-load circular-import guard the dispatch runners have
    always relied on (``taxonomy``/``closeout_proof`` back-reference this module).
    """
    from gzkit.governance import trust_audits  # noqa: PLC0415

    return trust_audits


def _validate_tautological_test_audit(project_root: Path) -> list[ValidationError]:
    """Validate tautological-test drift gate (OBPI-0.0.59-04).

    Rules:
    - current count > baseline + waivers → fail (exit 3)
    - current count <= baseline + waivers → pass
    Waivers file path is self-exempt from the scan (circular-dependency analysis).
    """
    from gzkit.tautological_tests import audit_drift  # noqa: PLC0415

    return audit_drift(project_root)


def _validate_decomposition(project_root: Path) -> list[ValidationError]:
    """Validate ADR decomposition scorecards and checklist-to-brief alignment."""
    from gzkit.core.scoring import (  # noqa: PLC0415
        active_checklist_items,
        parse_checklist_items,
        parse_scorecard,
    )

    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []

    errors: list[ValidationError] = []
    for adr_md in sorted(adr_root.rglob("ADR-*.md")):
        if adr_md.name.startswith("ADR-CLOSEOUT") or is_pool_adr_path(adr_md):
            continue
        # Only check ADR intent documents (not briefs/audit files)
        if "obpis" in adr_md.parts or "briefs" in adr_md.parts or "audit" in adr_md.parts:
            continue

        content = adr_md.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)
        if frontmatter and is_adr_shape_grandfathered(frontmatter):
            continue

        scorecard, scorecard_errors = parse_scorecard(body)
        checklist_items = parse_checklist_items(body)

        if not checklist_items:
            continue  # ADR has no checklist — skip

        if scorecard_errors:
            for err in scorecard_errors:
                errors.append(
                    ValidationError(
                        type="decomposition",
                        artifact=adr_md.relative_to(project_root).as_posix(),
                        message=err,
                    )
                )
            continue

        if scorecard is None:
            continue

        live_items = active_checklist_items(checklist_items)
        if len(live_items) != scorecard.final_target_obpi_count:
            errors.append(
                ValidationError(
                    type="decomposition",
                    artifact=adr_md.relative_to(project_root).as_posix(),
                    message=(
                        "Checklist count must match scorecard final target "
                        "(does not match): "
                        f"active={len(live_items)} "
                        f"target={scorecard.final_target_obpi_count}; "
                        f"total checklist rows including withdrawn history: {len(checklist_items)}."
                    ),
                )
            )

        # Check that OBPI brief files exist for each checklist item
        adr_dir = adr_md.parent
        obpis_dir = adr_dir / "obpis"
        briefs_dir = adr_dir / "briefs"
        # Extract ADR version from filename
        match = re.match(r"ADR-([\d.]+)", adr_md.stem)
        if match:
            version = match.group(1)
            existing_briefs = list(obpis_dir.glob(f"OBPI-{version}-*.md"))
            existing_briefs.extend(briefs_dir.glob(f"OBPI-{version}-*.md"))
            if checklist_items and not existing_briefs:
                errors.append(
                    ValidationError(
                        type="decomposition",
                        artifact=adr_md.relative_to(project_root).as_posix(),
                        message=(
                            f"Checklist has {len(checklist_items)} items but no OBPI briefs found."
                        ),
                    )
                )

    return errors


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
    _ScopeEntry("decomposition", "explicit", True, lambda r, _f: _validate_decomposition(r)),
    _ScopeEntry("requirements", "explicit", True, lambda r, _f: _validate_requirements(r)),
    _ScopeEntry(
        "commit_trailers",
        "explicit",
        True,
        lambda r, _f: _validate_commit_trailers(r) + _validate_eval_feedback_trailer(r),
    ),
    _ScopeEntry("type_ignores", "explicit", True, lambda r, _f: _ta().audit_type_ignores(r)),
    _ScopeEntry("cli_alignment", "explicit", True, lambda r, _f: _ta().audit_cli_alignment(r)),
    _ScopeEntry("event_handlers", "explicit", True, lambda r, _f: _ta().audit_event_handlers(r)),
    _ScopeEntry(
        "validator_fields", "explicit", True, lambda r, _f: _ta().audit_validator_fields(r)
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
        lambda r, _f: _ta().audit_instructions_files_budget(r),
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
        "adversarial_validation",
        "explicit",
        True,
        lambda r, _f: _ta().audit_adversarial_validation(r),
    ),
    _ScopeEntry("red_parity", "explicit", True, lambda r, _f: _ta().audit_red_parity(r)),
    _ScopeEntry(
        "session_green_gate", "explicit", False, lambda r, _f: _ta().audit_session_green_gate(r)
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
        "lock_handoff_coupling",
        "explicit",
        False,
        lambda r, _f: _ta().validate_lock_handoff_coupling(r),
    ),
    _ScopeEntry("distribution", "explicit", True, lambda r, _f: _ta().audit_distribution(r)),
    _ScopeEntry("changelog", "explicit", True, lambda r, _f: _changelog_runner(r)),
    _ScopeEntry(
        "bullet_retention", "explicit", True, lambda r, _f: _ta().validate_bullet_retention(r)
    ),
    _ScopeEntry("surface_weight", "explicit", True, lambda r, _f: _ta().validate_surface_weight(r)),
    _ScopeEntry(
        "pointer_anchors", "explicit", True, lambda r, _f: _ta().validate_pointer_integrity(r)
    ),
    _ScopeEntry(
        "scenario_reachability",
        "explicit",
        True,
        lambda r, _f: _ta().validate_scenario_reachability(r),
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
    _ScopeEntry("kind_invariance", "explicit", True, lambda r, _f: _ta().audit_kind_invariance(r)),
    _ScopeEntry("receipt_shape", "explicit", True, lambda r, _f: _ta().audit_receipt_shape(r)),
    _ScopeEntry(
        "brief_reconcile", "explicit", True, lambda r, _f: _ta().validate_brief_reconcile(r)
    ),
    _ScopeEntry("router_tables", "explicit", True, lambda r, _f: _ta().audit_router_tables(r)),
    _ScopeEntry(
        "req_kind_discipline", "explicit", True, lambda r, _f: _validate_req_kind_discipline(r)
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
        console.print(f"   [red]→[/red] {e.artifact}: {e.message}")
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
        console.print(f"   [red]→[/red] {e.artifact}: {e.message}")
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
        console.print(f"   [red]→[/red] {e.artifact}: {e.message}")
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
        console.print(f"   [red]→[/red] {e.artifact}: {e.message}")
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
        console.print(f"   [red]→[/red] \\[{v.reason}] {v.file}{detected}")
    console.print(
        "\nRecovery: narrow `paths:` to a concrete glob, fold the content into "
        "AGENTS.md, or add an allowlist entry under `rules.unscoped_allowlist` "
        "in .gzkit/manifest.json (see ADR-0.0.20)."
    )
    raise SystemExit(3)


def _parse_sensitivity_path_list(raw: str) -> tuple[str, ...]:
    """Split comma- or newline-separated path lists into a tuple."""
    pieces: list[str] = []
    for chunk in raw.replace("\r", "\n").split("\n"):
        for piece in chunk.split(","):
            cleaned = piece.strip()
            if cleaned:
                pieces.append(cleaned)
    return tuple(pieces)


def _sensitivity_records(
    project_root: Path,
) -> tuple[list[dict[str, object]], list[ValidationError]]:
    """Walk briefs once and produce per-brief records + companion findings."""
    from gzkit.governance.trust_audits.sensitivity import (  # noqa: PLC0415
        _SENSITIVITY_REGISTRY_REL,
        _extract_sensitivity_allowed_paths,
        _iter_sensitivity_briefs,
        _load_floor_grandfather,
        _load_sensitivity_registry,
    )
    from gzkit.governance.trust_audits.taxonomy import (  # noqa: PLC0415
        _parse_adr_frontmatter,
    )
    from gzkit.models.security_surfaces import match_globs  # noqa: PLC0415

    findings: list[ValidationError] = []
    records: list[dict[str, object]] = []

    registry, registry_error = _load_sensitivity_registry(project_root)
    if registry_error is not None:
        findings.append(registry_error)
        return records, findings
    assert registry is not None  # noqa: S101

    grandfather = _load_floor_grandfather(project_root)

    for brief_path in _iter_sensitivity_briefs(project_root):
        try:
            brief_text = brief_path.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        rel = brief_path.relative_to(project_root).as_posix()
        frontmatter = _parse_adr_frontmatter(brief_path) or {}
        declared = frontmatter.get("sensitivity")
        declared_norm = declared.strip() or None if isinstance(declared, str) else None
        if declared_norm in {"None", "null", "~"}:
            declared_norm = None

        allowed_paths = _extract_sensitivity_allowed_paths(brief_text)
        try:
            matching_categories = match_globs(allowed_paths, registry)
        except (ValueError, TypeError):
            findings.append(
                ValidationError(
                    type="sensitivity-malformed-allowlist",
                    artifact=rel,
                    message="Allowed Paths contains an unparseable glob.",
                )
            )
            continue

        detected = "security" if matching_categories else None
        records.append(
            {
                "file": rel,
                "declared_sensitivity": declared_norm,
                "detected_sensitivity": detected,
                "intersecting_paths": allowed_paths,
                "registry_categories": list(matching_categories),
            }
        )

        if detected == "security" and declared_norm not in (None, "security"):
            findings.append(
                ValidationError(
                    type="sensitivity-escape-attempt",
                    artifact=rel,
                    message=(
                        f"declared={declared_norm!r} but detected=security; "
                        f"categories={list(matching_categories)}; "
                        f"intersecting_paths={allowed_paths}"
                    ),
                )
            )
        elif detected == "security" and declared_norm is None and rel not in grandfather:
            # Omission over a security overlap is fail-closed (GHI #625);
            # grandfathered briefs (pre-cutover) stay at the informational floor.
            findings.append(
                ValidationError(
                    type="sensitivity-floor-violation",
                    artifact=rel,
                    message=(
                        f"Brief omits sensitivity: while allowed paths intersect "
                        f"registered security surfaces (detected=security, "
                        f"categories={list(matching_categories)}, "
                        f"intersecting_paths={allowed_paths}). "
                        f".gzkit/rules/security-sensitivity.md §§ 1-2: omission over a "
                        f"security overlap is fail-closed. Declare 'sensitivity: security'; "
                        f"or if the overlap is an incidental false positive, narrow the "
                        f"Allowed Paths or discharge at completion via "
                        f"'gz obpi complete --accept-security-floor'."
                    ),
                )
            )

    # Surface the registry-rel for callers that want to cite it in human output.
    _ = _SENSITIVITY_REGISTRY_REL
    return records, findings


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
                console.print(f"  [yellow]registry error:[/yellow] {payload['error']}")
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
                console.print(f"  [red]→[/red] [{finding.type}] {finding.artifact}")
                console.print(f"      {finding.message}")

    if any(f.type in _POLICY_BREACH_ERROR_TYPES for f in findings):
        raise SystemExit(3)
    raise SystemExit(0)


def _rule_version_markers_runner(project_root: Path) -> list[ValidationError]:
    """Run the rule-version-marker validator (skill-surface-sync #2)."""
    from gzkit.validators.rule_version_markers import (  # noqa: PLC0415
        audit_rule_version_markers_errors,
    )

    return audit_rule_version_markers_errors(project_root)


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
    from gzkit.mx import checkpoint, disposition, levels  # noqa: PLC0415

    def _grounds(scope: str) -> bool:
        # Each scope emits its drift at ERROR and routes through the one leveled
        # severity authority (parent ADR-0.0.74 BI#2); fail-closed iff grounding.
        return disposition.grounds(checkpoint.resolve(scope, levels.ERROR, project_root))

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
        "scenario_reachability",
        "kind_invariance",
        "receipt_shape",
        "setpoint_coherence",
        "rendition_freshness",
        "rendition_floor_coherence",
        "invariant_coherence",
        "brief_reconcile",
        "router_tables",
        "req_kind_discipline",
        "ontology_purity",
        "brief_command_shape",
        "foundation_kind_closed",
        "grandfather_dangling",
        "tautological_test_audit",
        "task_envelope_coherence",
        "closeout_proof",
        "lock_handoff_coupling",
        "okf_conformance",
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
        console.print(f"   [red]→[/red] [{error.type}] {error.artifact}")
        console.print(f"    {error.message}")
        if error.field:
            console.print(f"    Field: {error.field}")
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
        console.print(f"  {marker} [{entry.status}] {run_id}")
        console.print(f"      {entry.message}")


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
    as_json: bool,
) -> bool:
    """Handle scopes that own their full 0/2/3 lifecycle and return immediately.

    Returns True when one of these scopes handled the invocation — the caller
    must then return without running the aggregate validation path.
    """
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
    if check_evaluation_justify_binding is not None and not other_scopes_active:
        _run_evaluation_justify_binding_solo(
            project_root, check_evaluation_justify_binding, as_json=as_json
        )
        return True
    if check_unscoped_rules and not other_scopes_active:
        _run_unscoped_rules_scope(
            project_root, as_json=as_json, allowlist_only=unscoped_rules_allowlist_only
        )
        return True
    if check_sensitivity and not other_scopes_active:
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
    if check_qc_binding and not other_scopes_active:
        _run_qc_binding_scope(project_root, as_json=as_json)
        return True
    if check_fidelity_presence and not other_scopes_active:
        _run_fidelity_presence_scope(project_root, as_json=as_json)
        return True
    if check_waiver_ratchet and not other_scopes_active:
        _run_waiver_ratchet_scope(project_root, as_json=as_json)
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
    check_validator_fields: bool = False,
    check_utf8_prefix: bool = False,
    check_test_tiers: bool = False,
    check_pydantic_models: bool = False,
    check_class_size: bool = False,
    check_version_release: bool = False,
    check_pool_adr_isolation: bool = False,
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
    check_lock_handoff_coupling: bool = False,
    check_distribution: bool = False,
    check_distribution_regenerate: bool = False,
    check_changelog: bool = False,
    check_bullet_retention: bool = False,
    check_surface_weight: bool = False,
    check_pointer_anchors: bool = False,
    check_scenario_reachability: bool = False,
    check_surface_fidelity: bool = False,
    check_vendor_manifest: bool = False,
    check_kind_invariance: bool = False,
    check_receipt_shape: bool = False,
    check_invariant_coherence: bool = False,
    check_brief_reconcile: bool = False,
    check_router_tables: bool = False,
    check_req_kind_discipline: bool = False,
    check_ontology_purity: bool = False,
    check_brief_command_shape: bool = False,
    check_tautological_test_audit: bool = False,
    check_setpoint_coherence: bool = False,
    check_rendition_freshness: bool = False,
    check_rendition_floor_coherence: bool = False,
    check_task_envelope_coherence: bool = False,
    check_closeout_proof: bool = False,
    check_okf_conformance: bool = False,
    check_qc_binding: bool = False,
    check_fidelity_presence: bool = False,
    check_waiver_ratchet: bool = False,
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
        "validator_fields": check_validator_fields,
        "utf8_prefix": check_utf8_prefix,
        "test_tiers": check_test_tiers,
        "pydantic_models": check_pydantic_models,
        "class_size": check_class_size,
        "version_release": check_version_release,
        "pool_adr_isolation": check_pool_adr_isolation,
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
        "lock_handoff_coupling": check_lock_handoff_coupling,
        "distribution": check_distribution,
        "changelog": check_changelog,
        "bullet_retention": check_bullet_retention,
        "surface_weight": check_surface_weight,
        "pointer_anchors": check_pointer_anchors,
        "scenario_reachability": check_scenario_reachability,
        "surface_fidelity": check_surface_fidelity,
        "vendor_manifest": check_vendor_manifest,
        "setpoint_coherence": check_setpoint_coherence,
        "rendition_freshness": check_rendition_freshness,
        "rendition_floor_coherence": check_rendition_floor_coherence,
        "kind_invariance": check_kind_invariance,
        "receipt_shape": check_receipt_shape,
        "invariant_coherence": check_invariant_coherence,
        "brief_reconcile": check_brief_reconcile,
        "router_tables": check_router_tables,
        "req_kind_discipline": check_req_kind_discipline,
        "ontology_purity": check_ontology_purity,
        "brief_command_shape": check_brief_command_shape,
        "tautological_test_audit": check_tautological_test_audit,
        "task_envelope_coherence": check_task_envelope_coherence,
        "closeout_proof": check_closeout_proof,
        "okf_conformance": check_okf_conformance,
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
