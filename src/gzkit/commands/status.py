"""Status command implementation."""

import json
import re
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    GzCliError,
    _apply_pool_adr_status_overrides,
    _gate4_na_reason,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_adr_ledger_id,
    resolve_obpi,
)
from gzkit.commands.status_obpi import (
    _adr_closeout_readiness,
    _adr_obpi_status_rows,
    _apply_obpi_lifecycle_overrides,
    _build_obpi_index,
    _build_obpi_status_entry,
    _collect_obpi_files_for_adr,
    _inspect_obpi_brief,
    _obpi_row_complete,
    _print_status_obpi_section,
    _render_obpi_row_status,
    _render_obpi_runtime_state,
    _render_obpi_status_details,
    _render_obpi_unit_status,
    _summarize_obpi_rows,
)
from gzkit.commands.status_render import (
    _print_status_gate_section,
    _print_status_task_section,
    _qc_readiness,
    _render_adr_report,
    _render_adr_table,
    _render_gate_status,
    _render_pending_checks_cell,
    _render_qc_readiness,
    _render_status_row,
    _render_status_table,
)
from gzkit.commands.task import _load_tasks_for_obpi
from gzkit.config import GzkitConfig
from gzkit.core.validation_rules import parse_frontmatter as _parse_md_frontmatter
from gzkit.ledger import (
    Ledger,
    resolve_adr_lane,
)

# Re-export OBPI and render symbols so that ``from gzkit.commands.status import X`` keeps
# working for every consumer that relied on the old single-module layout.
__all__ = [
    "_adr_closeout_readiness",
    "_adr_obpi_status_rows",
    "_apply_obpi_lifecycle_overrides",
    "_build_obpi_index",
    "_build_obpi_status_entry",
    "_collect_obpi_files_for_adr",
    "_inspect_obpi_brief",
    "_obpi_row_complete",
    "_print_status_obpi_section",
    "_render_obpi_row_status",
    "_render_obpi_runtime_state",
    "_render_obpi_status_details",
    "_render_obpi_unit_status",
    "_summarize_obpi_rows",
    "_print_status_gate_section",
    "_print_status_task_section",
    "_qc_readiness",
    "_render_adr_report",
    "_render_adr_table",
    "_render_gate_status",
    "_render_pending_checks_cell",
    "_render_qc_readiness",
    "_render_status_row",
    "_render_status_table",
    "ADR_SEMVER_STATUS_ID_RE",
    "_adr_status_sort_key",
    "_build_adr_status_entry",
    "_build_adr_status_result",
    "_collect_adr_statuses",
    "_task_summary_for_adr",
    "adr_report_cmd",
    "adr_status_cmd",
    "obpi_reconcile_cmd",
    "obpi_status_cmd",
    "status",
]


def _task_summary_for_adr(
    ledger: Ledger,
    obpi_ids: list[str],
) -> dict[str, Any] | None:
    """Aggregate TASK counts across OBPIs for an ADR.

    Returns None when no tasks exist (backward compatible).
    """
    total = 0
    pending = 0
    in_progress = 0
    completed = 0
    blocked = 0
    escalated = 0
    per_req: dict[str, dict[str, int]] = {}

    for obpi_id in obpi_ids:
        tasks = _load_tasks_for_obpi(ledger, obpi_id)
        for task_id, info in tasks.items():
            total += 1
            status = info.get("status", "pending")
            if status == "pending":
                pending += 1
            elif status == "in_progress":
                in_progress += 1
            elif status == "completed":
                completed += 1
            elif status == "blocked":
                blocked += 1
            elif status == "escalated":
                escalated += 1

            req_prefix = _req_prefix_from_task_id(task_id)
            if req_prefix is not None:
                if req_prefix not in per_req:
                    per_req[req_prefix] = {
                        "total": 0,
                        "completed": 0,
                        "in_progress": 0,
                        "pending": 0,
                        "blocked": 0,
                        "escalated": 0,
                    }
                per_req[req_prefix]["total"] += 1
                if status in per_req[req_prefix]:
                    per_req[req_prefix][status] += 1

    if total == 0:
        return None

    result: dict[str, Any] = {
        "total": total,
        "pending": pending,
        "in_progress": in_progress,
        "completed": completed,
        "blocked": blocked,
        "escalated": escalated,
    }
    if per_req:
        result["per_req"] = per_req
    return result


_TASK_REQ_PREFIX_RE = re.compile(r"^TASK-([\d.]+)-(\d+)-(\d+)-\d+$")


def _req_prefix_from_task_id(task_id: str) -> str | None:
    """Extract the REQ prefix from a TASK ID string.

    TASK-semver-obpi_item-req_index-seq → REQ-semver-obpi_item-req_index
    """
    m = _TASK_REQ_PREFIX_RE.match(task_id)
    if m:
        return f"REQ-{m.group(1)}-{m.group(2)}-{m.group(3)}"
    return None


ADR_SEMVER_STATUS_ID_RE = re.compile(
    r"^ADR-(?P<major>\d+)\.(?P<minor>\d+)\.(?P<patch>\d+)(?P<suffix>(?:[.-][A-Za-z0-9][A-Za-z0-9.-]*)?)$"
)


def _build_adr_status_entry(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
    info: dict[str, Any],
    obpi_index: list[tuple[str, str, Path]] | None = None,
) -> dict[str, Any]:
    """Build enriched ADR status payload for one ADR."""
    entry = dict(info)
    lane = resolve_adr_lane(entry, config.mode)
    gate_statuses = ledger.get_effective_gate_statuses(adr_id)
    gate4_na = _gate4_na_reason(project_root, lane)
    entry["lane"] = lane
    entry["gates"] = {
        "1": "pass",
        "2": gate_statuses.get(2, "pending"),
        "3": gate_statuses.get(3, "pending") if lane == "heavy" else "n/a",
        "4": "n/a" if gate4_na is not None else gate_statuses.get(4, "pending"),
        "5": "pass" if entry.get("attested") else "pending",
    }
    entry["observed_post_validation_gate_failures"] = ledger.get_post_validation_failed_gates(
        adr_id
    )
    if gate4_na is not None:
        entry["gate4_na_reason"] = gate4_na

    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id, obpi_index=obpi_index)
    entry.update(Ledger.derive_adr_semantics(entry))
    _apply_pool_adr_status_overrides(adr_id, entry)
    entry["obpis"] = obpi_rows
    obpi_summary = _summarize_obpi_rows(obpi_rows)
    entry["obpi_summary"] = obpi_summary
    closeout_readiness = _adr_closeout_readiness(obpi_rows)
    entry["closeout_ready"] = bool(closeout_readiness["ready"])
    entry["closeout_blockers"] = list(closeout_readiness["blockers"])
    _apply_obpi_lifecycle_overrides(adr_id, entry, obpi_summary)

    # Task summary -- only present when tasks exist (REQ-0.22.0-05-05)
    obpi_ids = [cast(str, row.get("id", "")) for row in obpi_rows if row.get("id")]
    task_summary = _task_summary_for_adr(ledger, obpi_ids)
    if task_summary is not None:
        task_summary["tracing_policy"] = "required" if lane == "heavy" else "advisory"
        entry["task_summary"] = task_summary

    return entry


def _adr_status_sort_key(adr_id: str) -> tuple[int, int, int, int, int, str]:
    """Sort ADR ids semver-first so 0.10.0 correctly follows 0.9.0."""
    match = ADR_SEMVER_STATUS_ID_RE.match(adr_id)
    if match:
        suffix = match.group("suffix")
        return (
            0,
            int(match.group("major")),
            int(match.group("minor")),
            int(match.group("patch")),
            0 if not suffix else 1,
            suffix,
        )
    if _is_pool_adr_id(adr_id):
        return (1, 0, 0, 0, 0, adr_id)
    return (2, 0, 0, 0, 0, adr_id)


def _collect_adr_statuses(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    graph: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    """Collect enriched status payload for each ADR in the graph."""
    obpi_index = _build_obpi_index(project_root, config, ledger)
    adrs: dict[str, dict[str, Any]] = {}
    for adr_id, info in graph.items():
        if info.get("type") != "adr":
            continue
        adrs[adr_id] = _build_adr_status_entry(
            project_root, config, ledger, adr_id, info, obpi_index=obpi_index
        )
    return adrs


def _filename_derived_epic(adr_id: str) -> str | None:
    """Return the first hyphen-delimited token after ``ADR-pool.``, or None."""
    prefix = "ADR-pool."
    if not adr_id.startswith(prefix):
        return None
    remainder = adr_id[len(prefix) :]
    if not remainder:
        return None
    return remainder.split("-", 1)[0]


def _filter_adrs_by_epic(
    project_root: Path,
    config: GzkitConfig,
    adrs: dict[str, dict[str, Any]],
    epic_slug: str | None,
) -> tuple[dict[str, dict[str, Any]], list[str]]:
    """Filter ADRs to pool entries matching ``epic_slug``.

    Matching is OR'd: a pool ADR matches when EITHER its filename-derived
    epic-slug OR its frontmatter ``epic:`` field equals ``epic_slug``.
    Returns the filtered mapping plus an advisory-warning list.
    """
    if epic_slug is None:
        return adrs, []

    pool_root = project_root / config.paths.adrs / "pool"
    warnings: list[str] = []
    filtered: dict[str, dict[str, Any]] = {}

    for adr_id, entry in adrs.items():
        if not _is_pool_adr_id(adr_id):
            continue

        filename_epic = _filename_derived_epic(adr_id)
        frontmatter_epic: str | None = None
        pool_file = pool_root / f"{adr_id}.md"
        if pool_file.exists():
            try:
                fm, _body = _parse_md_frontmatter(pool_file.read_text(encoding="utf-8"))
            except OSError:
                fm = {}
            raw_epic = fm.get("epic")
            if isinstance(raw_epic, str) and raw_epic.strip():
                frontmatter_epic = raw_epic.strip()

        if (
            filename_epic is not None
            and frontmatter_epic is not None
            and filename_epic != frontmatter_epic
        ):
            warnings.append(
                f"{adr_id}: filename-derived epic '{filename_epic}' "
                f"disagrees with frontmatter epic '{frontmatter_epic}'"
            )

        if filename_epic == epic_slug or frontmatter_epic == epic_slug:
            filtered[adr_id] = entry

    return filtered, warnings


# ---------------------------------------------------------------------------
# Command entry points
# ---------------------------------------------------------------------------


def status(
    as_json: bool,
    show_gates: bool,
    as_table: bool,
    epic: str | None = None,
    full: bool = False,
) -> None:
    """Display OBPI progress, lifecycle, and gate readiness across ADRs.

    When ``full=True`` (``--full``), Rich tables preserve identity-bearing
    IDs (no ellipsis) and the OBPI list under ``--show-gates`` renders as
    a complete Rich table instead of a 3-row prose preview (GHI #319).
    """
    config = ensure_initialized()
    project_root = get_project_root()

    ledger = Ledger(project_root / config.paths.ledger)
    pending = ledger.get_pending_attestations()
    graph = ledger.get_artifact_graph()
    adrs = _collect_adr_statuses(project_root, config, ledger, graph)
    adrs, epic_warnings = _filter_adrs_by_epic(project_root, config, adrs, epic)
    adrs = dict(sorted(adrs.items(), key=lambda item: _adr_status_sort_key(item[0])))

    if as_json:
        result: dict[str, Any] = {
            "mode": config.mode,
            "adrs": adrs,
            "pending_attestations": pending,
        }
        if epic is not None:
            result["warnings"] = epic_warnings
        print(json.dumps(result, indent=2))  # noqa: T201
        return

    for warning in epic_warnings:
        console.print(f"[yellow]warning: {warning}[/yellow]")

    console.print(f"[bold]Lane: {config.mode}[/bold]\n")

    if not adrs:
        if epic is not None:
            console.print(f"No pool ADRs match epic '{epic}'.")
        else:
            console.print("No ADRs found. Create one with 'gz plan'.")
        return

    if as_table:
        _render_status_table(adrs, config.mode, full=full)
        return

    for adr_id, info in adrs.items():
        _render_status_row(adr_id, info, config.mode, show_gates, full=full)


def obpi_status_cmd(obpi: str, as_json: bool) -> None:
    """Display focused runtime status for one OBPI."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    obpi_id, _obpi_file = resolve_obpi(project_root, config, ledger, obpi)
    result = _build_obpi_status_entry(project_root, config, ledger, obpi_id)
    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
        return
    _render_obpi_status_details(result)


def obpi_reconcile_cmd(obpi: str, as_json: bool) -> None:
    """Fail-closed reconciliation for one OBPI runtime unit."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    obpi_id, obpi_file = resolve_obpi(project_root, config, ledger, obpi)
    result = _build_obpi_status_entry(project_root, config, ledger, obpi_id)

    # Auto-fix OBPI brief frontmatter to match ledger-derived state (ADR-0.0.9-04)
    runtime_state = result.get("runtime_state", "pending")
    if obpi_file and obpi_file.exists():
        from gzkit.commands.closeout_form import auto_fix_obpi_brief_frontmatter

        auto_fix_obpi_brief_frontmatter(obpi_file, runtime_state)

    blockers = cast(list[str], result.get("issues", []))
    payload = {
        "passed": not blockers,
        "blockers": blockers,
        **result,
    }

    if as_json:
        print(json.dumps(payload, indent=2))  # noqa: T201
    else:
        console.print(f"[bold]OBPI reconcile:[/bold] {obpi_id}")
        if isinstance(result.get("parent_adr"), str) and result.get("parent_adr"):
            console.print(f"  Parent ADR: {result['parent_adr']}")
        console.print(f"  File: {result.get('file') or '(missing)'}")
        console.print(
            "  Runtime State: "
            + _render_obpi_runtime_state(
                str(result.get("runtime_state", "pending")),
                bool(result.get("found_file")),
            )
        )
        console.print(f"  Proof State: {result.get('proof_state', 'missing')}")
        console.print(f"  Attestation State: {result.get('attestation_state', 'not_required')}")
        if blockers:
            console.print("BLOCKERS:")
            for blocker in blockers:
                console.print(f"- {blocker}")
        else:
            console.print("[green]PASS[/green] OBPI runtime state and proof evidence are coherent.")
            if str(result.get("attestation_state", "")) == "recorded":
                console.print(
                    "  [dim]Note (GHI #290): coherence verified; the attestation's "
                    "authenticity is not independently verifiable from the ledger "
                    "alone. Treat this PASS as 'brief matches ledger', not as proof "
                    "the human attested.[/dim]"
                )

    if blockers:
        raise SystemExit(1)


def _build_adr_status_result(adr: str) -> dict[str, Any]:
    """Build the status result dict for a single ADR."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    try:
        adr_file, adr_id = resolve_adr_file(project_root, config, adr_input)
    except GzCliError:
        canonical_adr = ledger.canonicalize_id(adr_input)
        adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id)
    if not info or info.get("type") != "adr":
        msg = f"ADR not found in ledger: {adr_id}"
        raise GzCliError(msg)  # noqa: TRY003

    lane = resolve_adr_lane(info, config.mode)
    gate_statuses = ledger.get_effective_gate_statuses(adr_id)
    observed_post_validation_failures = ledger.get_post_validation_failed_gates(adr_id)
    gate4_na = _gate4_na_reason(project_root, lane)
    semantics = Ledger.derive_adr_semantics(info)
    result: dict[str, Any] = {
        "adr": adr_id,
        "mode": config.mode,
        "lane": lane,
        "attested": bool(info.get("attested")),
        "attestation_status": info.get("attestation_status"),
        "attestation_term": semantics["attestation_term"],
        "lifecycle_status": semantics["lifecycle_status"],
        "closeout_phase": semantics["closeout_phase"],
        "closeout_initiated": bool(info.get("closeout_initiated")),
        "validated": bool(info.get("validated")),
        "gates": {
            "1": "pass",
            "2": gate_statuses.get(2, "pending"),
            "3": gate_statuses.get(3, "pending") if lane == "heavy" else "n/a",
            "4": "n/a" if gate4_na is not None else gate_statuses.get(4, "pending"),
            "5": "pass" if info.get("attested") else "pending",
        },
        "observed_post_validation_gate_failures": observed_post_validation_failures,
    }
    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    _apply_pool_adr_status_overrides(adr_id, result)
    result["obpis"] = obpi_rows
    result["withdrawn_obpis"] = sorted(
        child_id
        for child_id in info.get("children", [])
        if graph.get(child_id, {}).get("type") == "obpi"
        and graph.get(child_id, {}).get("withdrawn", False)
    )
    obpi_summary = _summarize_obpi_rows(obpi_rows)
    result["obpi_summary"] = obpi_summary
    closeout_readiness = _adr_closeout_readiness(obpi_rows)
    result["closeout_ready"] = bool(closeout_readiness["ready"])
    result["closeout_blockers"] = list(closeout_readiness["blockers"])
    _apply_obpi_lifecycle_overrides(adr_id, result, obpi_summary)
    if gate4_na is not None:
        result["gate4_na_reason"] = gate4_na
    return result


def adr_status_cmd(adr: str, as_json: bool, show_gates: bool) -> None:
    """Display focused OBPI progress, lifecycle, and gate readiness for one ADR.

    Human-readable output delegates to ``_render_adr_report`` — the same
    deterministic Rich-table renderer used by ``gz adr report``. This enforces
    the ``gz-adr-status`` skill Output Contract (consistent table format).
    """
    result = _build_adr_status_result(adr)

    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
        return

    _render_adr_report(result)

    if show_gates:
        lane = cast(str, result["lane"])
        observed = cast(list[int], result.get("observed_post_validation_gate_failures") or [])
        observed_set = set(observed)

        def _annotate(gate_num: int, rendered: str) -> str:
            if gate_num in observed_set:
                return f"{rendered} [yellow](observed FAIL post-validation)[/yellow]"
            return rendered

        console.print("  Gate 1 (ADR):   [green]PASS[/green]")
        console.print(
            f"  Gate 2 (TDD):   {_annotate(2, _render_gate_status(result['gates'].get('2')))}"
        )
        if lane == "heavy":
            console.print(
                f"  Gate 3 (Docs):  {_annotate(3, _render_gate_status(result['gates'].get('3')))}"
            )
            console.print(
                f"  Gate 4 (BDD):   {_annotate(4, _render_gate_status(result['gates'].get('4')))}"
            )
            if result["gates"].get("4") == "n/a":
                console.print(f"                 ({result.get('gate4_na_reason', '')})")
            is_attested = bool(result.get("attested"))
            gate5_detail = (
                f" ({result['attestation_term']})" if result.get("attestation_term") else ""
            )
            console.print(
                "  Gate 5 (Human): "
                + ("[green]PASS[/green]" if is_attested else "[yellow]PENDING[/yellow]")
                + (gate5_detail if is_attested else "")
            )


def _warn_orphaned_adrs(project_root: Path, config: GzkitConfig, ledger: Ledger) -> None:
    """Warn about ADR files on disk that are not registered in the ledger."""
    from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts  # noqa: PLC0415

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    graph = ledger.get_artifact_graph()
    known = {aid for aid, info in graph.items() if info.get("type") == "adr"}

    orphans: list[str] = []
    for adr_file in artifacts.get("adrs", []):
        stem_id = adr_file.stem
        metadata = parse_artifact_metadata(adr_file)
        parsed_id = metadata.get("id", stem_id)
        # Frontmatter id is authoritative; fall back to stem + canonical forms
        # so legacy files without frontmatter still resolve. Mirrors the
        # dual-lookup pattern in register.py::_adr_register_identity (GHI-166).
        candidates = {
            stem_id,
            parsed_id,
            ledger.canonicalize_id(stem_id),
            ledger.canonicalize_id(parsed_id),
        }
        if candidates & known:
            continue
        if any(stem_id.startswith(f"{kid}-") for kid in known):
            continue
        orphans.append(stem_id)

    if orphans:
        console.print(
            f"[yellow]WARNING:[/yellow] {len(orphans)} ADR(s) exist on disk but are not "
            "registered in ledger:"
        )
        for oid in sorted(orphans):
            console.print(f"  - {oid}")
        console.print("Run [bold]gz register-adrs --all[/bold] to fix.\n")


def adr_report_cmd(adr: str | None, adr_type: str | None = None) -> None:
    """Render deterministic tabular report -- summary when no ADR given, detail for one ADR."""
    if adr is None:
        config = ensure_initialized()
        project_root = get_project_root()
        ledger = Ledger(project_root / config.paths.ledger)
        _warn_orphaned_adrs(project_root, config, ledger)
        graph = ledger.get_artifact_graph()
        adrs = _collect_adr_statuses(project_root, config, ledger, graph)
        _render_status_table(adrs, config.mode, adr_type=adr_type)
        return
    result = _build_adr_status_result(adr)
    _render_adr_report(result)
