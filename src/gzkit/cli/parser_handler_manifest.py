"""Shared lazy CLI handler manifest and resolver (GHI #617).

The three command-group parsers (``parser_governance``, ``parser_maintenance``,
``parser_artifacts``) each formerly carried a byte-identical ``_lazy`` resolver
plus ``_HANDLER_CACHE`` and a per-group slice of the string->module handler map.
That triplicated resolver was held correct only by author discipline: no test or
validator asserted that every ``_lazy(name)`` resolves, so a handler rename that
missed its manifest key, or a ``_lazy("typo")`` call-site, passed lint, type-check,
and the full suite green and failed only at the first runtime invocation of that
one verb (GHI #617). This module is the single source those parsers now import:
one ``_LAZY_HANDLERS`` map, one cache, one resolver.

``_lazy(name)`` imports the handler's module on first call and caches the resolved
callable, so ``gz --help`` never pulls the heavy handler dependencies.

The module is named ``parser_*`` deliberately: the doc-coverage scanner
(``gzkit.doc_coverage.scanner``) AST-scans every ``src/gzkit/cli/parser_*.py`` for
``_LAZY_HANDLERS`` dict literals to resolve handler docstrings. Keeping the
canonical manifest under that glob preserves docstring coverage with no scanner
change. Resolution is fenced by ``tests/cli/test_handler_manifest_resolves.py``.
"""

from __future__ import annotations

from collections.abc import Callable
from importlib import import_module
from typing import Any

_LAZY_HANDLERS: dict[str, str] = {
    # --- governance group (parser_governance) ---
    "attest": "gzkit.commands.attest",
    "audit_cmd": "gzkit.commands.audit_cmd",
    "closeout_cmd": "gzkit.commands.closeout",
    "gates_cmd": "gzkit.commands.gates",
    "implement_cmd": "gzkit.commands.gates",
    "constitute": "gzkit.commands.init_cmd",
    "init": "gzkit.commands.init_cmd",
    "prd": "gzkit.commands.init_cmd",
    "patch_release_cmd": "gzkit.commands.patch_release",
    "persona_drift_cmd": "gzkit.commands.personas",
    "personas_list_cmd": "gzkit.commands.personas",
    "plan_cmd": "gzkit.commands.plan",
    "plan_audit_cmd": "gzkit.commands.plan_audit_cmd",
    "migrate_semver": "gzkit.commands.register",
    "register_adrs": "gzkit.commands.register",
    "roles_cmd": "gzkit.commands.roles",
    "specify": "gzkit.commands.specify_cmd",
    "state": "gzkit.commands.state",
    "status": "gzkit.commands.status",
    "upgrade_cmd": "gzkit.commands.upgrade",
    # --- ontology group (parser_governance) ---
    "ontology_sense_cmd": "gzkit.commands.ontology",
    "ontology_trace_cmd": "gzkit.commands.ontology",
    "ontology_resense_cmd": "gzkit.commands.ontology",
    "ontology_seams_cmd": "gzkit.commands.ontology",
    "ontology_reach_cmd": "gzkit.commands.ontology",
    # --- airlock group (parser_governance) ---
    "airlock_in_cmd": "gzkit.commands.airlock",
    "airlock_out_cmd": "gzkit.commands.airlock",
    # --- handoff group (parser_maintenance) ---
    "handoff_archive_cmd": "gzkit.commands.handoff_archive",
    "handoff_authorize_cmd": "gzkit.commands.handoff",
    "handoff_create_cmd": "gzkit.commands.handoff",
    "handoff_list_cmd": "gzkit.commands.handoff",
    "handoff_resume_cmd": "gzkit.commands.handoff",
    "handoff_rulings_cmd": "gzkit.commands.handoff",
    # --- maintenance group (parser_maintenance) ---
    "chores_advise": "gzkit.commands.chores",
    "chores_audit": "gzkit.commands.chores",
    "chores_doctor": "gzkit.commands.chores",
    "chores_list": "gzkit.commands.chores",
    "chores_plan": "gzkit.commands.chores",
    "chores_propose_ghi": "gzkit.commands.chores",
    "chores_run": "gzkit.commands.chores",
    "chores_show": "gzkit.commands.chores",
    "cli_audit_cmd": "gzkit.commands.cli_audit",
    "check_config_paths_cmd": "gzkit.commands.config_paths",
    "covers_cmd": "gzkit.commands.covers",
    "drift_cmd": "gzkit.commands.drift",
    "test_shape_cmd": "gzkit.commands.test_shape",
    "frontmatter_reconcile_cmd": "gzkit.commands.frontmatter_reconcile",
    "flag_explain_cmd": "gzkit.commands.flags",
    "flags_list_cmd": "gzkit.commands.flags",
    "interview": "gzkit.commands.interview_cmd",
    "parity_check_cmd": "gzkit.commands.parity",
    "preflight_cmd": "gzkit.commands.preflight",
    "check": "gzkit.commands.quality",
    "format_cmd": "gzkit.commands.quality",
    "lint": "gzkit.commands.quality",
    "smoke_cmd": "gzkit.commands.smoke_cmd",
    "test": "gzkit.commands.quality",
    "typecheck": "gzkit.commands.quality",
    "readiness_audit_cmd": "gzkit.commands.readiness",
    "readiness_eval_cmd": "gzkit.commands.readiness",
    "skill_audit_cmd": "gzkit.commands.skills_cmd",
    "skill_list": "gzkit.commands.skills_cmd",
    "skill_new": "gzkit.commands.skills_cmd",
    "git_sync": "gzkit.commands.sync",
    "ledger_merge_driver_cmd": "gzkit.commands.ledger",
    "ledger_correct_cmd": "gzkit.commands.ledger_correct",
    "ledger_corrections_cmd": "gzkit.commands.ledger_correct",
    "sync_control_surfaces": "gzkit.commands.tidy",
    "tidy": "gzkit.commands.tidy",
    "validate": "gzkit.commands.validate_cmd",
    # --- artifacts group (parser_artifacts) ---
    "justify_cmd": "gzkit.commands.justify_cmd",
    "knowledge_cmd": "gzkit.commands.knowledge",
    "adr_audit_begin_cmd": "gzkit.commands.adr_audit",
    "adr_audit_check": "gzkit.commands.adr_audit",
    "adr_audit_end_cmd": "gzkit.commands.adr_audit",
    "adr_covers_check": "gzkit.commands.adr_audit",
    "adr_emit_receipt_cmd": "gzkit.commands.adr_audit",
    "adr_fidelity_cmd": "gzkit.commands.adr_fidelity",
    "adr_demote_cmd": "gzkit.commands.adr_demote",
    "adr_eval_cmd": "gzkit.commands.adr_promote",
    "adr_promote_cmd": "gzkit.commands.adr_promote",
    "obpi_audit_cmd": "gzkit.commands.obpi_audit_cmd",
    "obpi_emit_receipt_cmd": "gzkit.commands.obpi_cmd",
    "obpi_pipeline_cmd": "gzkit.commands.obpi_cmd",
    "obpi_precomplete_cmd": "gzkit.commands.obpi_precomplete",
    "obpi_dispatch_cmd": "gzkit.commands.obpi_dispatch",
    "obpi_present_evidence_cmd": "gzkit.commands.obpi_present_evidence",
    "obpi_verify_packet_cmd": "gzkit.commands.obpi_verify_packet",
    "obpi_validate_cmd": "gzkit.commands.obpi_cmd",
    "obpi_repudiate_cmd": "gzkit.commands.obpi_cmd",
    "obpi_block_cmd": "gzkit.commands.obpi_cmd",
    "obpi_supersede_cmd": "gzkit.commands.obpi_cmd",
    "obpi_unblock_cmd": "gzkit.commands.obpi_cmd",
    "obpi_withdraw_cmd": "gzkit.commands.obpi_cmd",
    "obpi_complete_cmd": "gzkit.commands.obpi_complete",
    "obpi_lock_check_cmd": "gzkit.commands.obpi_lock",
    "obpi_lock_claim_cmd": "gzkit.commands.obpi_lock",
    "obpi_lock_list_cmd": "gzkit.commands.obpi_lock",
    "obpi_lock_release_cmd": "gzkit.commands.obpi_lock",
    "adr_report_cmd": "gzkit.commands.status",
    "adr_status_cmd": "gzkit.commands.status",
    "obpi_reconcile_cmd": "gzkit.commands.status",
    "obpi_status_cmd": "gzkit.commands.status",
    "task_block_cmd": "gzkit.commands.task",
    "task_complete_cmd": "gzkit.commands.task",
    "task_escalate_cmd": "gzkit.commands.task",
    "task_list_cmd": "gzkit.commands.task",
    "task_start_cmd": "gzkit.commands.task",
    "task_start_by_req_cmd": "gzkit.commands.task",
    "task_envelope_diagnose_cmd": "gzkit.commands.task",
    "task_fanout_cmd": "gzkit.commands.task",
    "issue_file_cmd": "gzkit.commands.issue_cmd",
    "complexity_distill_cmd": "gzkit.commands.complexity_distill_cmd",
    "complexity_advise_cmd": "gzkit.commands.complexity_advise",
    "complexity_guide_cmd": "gzkit.commands.complexity_guide",
    "governance_render_cmd": "gzkit.commands.governance_render",
    "context_cmd": "gzkit.commands.context_cmd",
    "brief_reconcile_cmd": "gzkit.commands.brief_reconcile",
}

_HANDLER_CACHE: dict[str, Callable[..., Any]] = {}


def _lazy(name: str) -> Callable[..., Any]:
    cached = _HANDLER_CACHE.get(name)
    if cached is not None:
        return cached
    module_path = _LAZY_HANDLERS[name]
    impl = getattr(import_module(module_path), name)
    _HANDLER_CACHE[name] = impl
    return impl
