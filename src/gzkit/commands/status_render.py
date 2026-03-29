"""ADR status rendering functions for the status subsystem."""

from typing import Any, cast

from rich import box
from rich.table import Table

from gzkit.commands.common import (
    _is_pool_adr_id,
    console,
)
from gzkit.commands.status_obpi import (
    _print_status_obpi_section,
)

# ---------------------------------------------------------------------------
# Table category labels (importable for test assertions)
# ---------------------------------------------------------------------------

TABLE_TITLE_FOUNDATION = "Foundation ADRs"
TABLE_TITLE_FEATURE = "Feature ADRs"
TABLE_TITLE_POOL = "Pool ADRs"

# ---------------------------------------------------------------------------
# Gate / QC rendering
# ---------------------------------------------------------------------------


def _render_gate_status(gate_status: str | None) -> str:
    if gate_status == "pass":
        return "[green]PASS[/green]"
    if gate_status == "fail":
        return "[red]FAIL[/red]"
    if gate_status == "n/a":
        return "[cyan]N/A[/cyan]"
    return "[yellow]PENDING[/yellow]"


def _qc_readiness(
    gates: dict[str, str], lane: str, obpi_summary: dict[str, Any]
) -> tuple[str, list[str]]:
    """Derive summarized QC readiness and pending checkpoints from gate statuses."""
    blockers: list[str] = []
    obpi_total = int(obpi_summary.get("total", 0))
    obpi_unit_status = str(obpi_summary.get("unit_status", "unscoped"))
    if obpi_total > 0 and obpi_unit_status != "completed":
        blockers.append("OBPI completion")

    if gates.get("2") != "pass":
        blockers.append("TDD")
    if lane == "heavy":
        if gates.get("3") != "pass":
            blockers.append("Docs")
        if gates.get("4") not in {"pass", "n/a"}:
            blockers.append("BDD")
        if gates.get("5") != "pass":
            blockers.append("Human attestation")
    readiness = "ready" if not blockers else "pending"
    return readiness, blockers


def _render_qc_readiness(readiness: str, blockers: list[str]) -> str:
    if readiness == "ready":
        return "[green]READY[/green]"
    return f"[yellow]PENDING[/yellow] (pending: {', '.join(blockers)})"


def _render_pending_checks_cell(blockers: list[str]) -> str:
    """Render compact pending-check codes for table view."""
    if not blockers:
        return "-"

    code_map = {
        "OBPI completion": "O",
        "TDD": "T",
        "Docs": "D",
        "BDD": "B",
        "Human attestation": "H",
    }
    return ",".join(code_map.get(blocker, "?") for blocker in blockers)


# ---------------------------------------------------------------------------
# Gate and task section renderers
# ---------------------------------------------------------------------------


def _print_status_gate_section(
    info: dict[str, Any],
    lane: str,
    gates: dict[str, str],
    attested: bool,
    attestation_term: Any,
) -> None:
    """Render optional gate-by-gate diagnostics for one ADR."""
    console.print("  Gate 1 (ADR):   [green]PASS[/green]")
    console.print(f"  Gate 2 (TDD):   {_render_gate_status(gates.get('2'))}")
    if lane != "heavy":
        return

    console.print(f"  Gate 3 (Docs):  {_render_gate_status(gates.get('3'))}")
    console.print(f"  Gate 4 (BDD):   {_render_gate_status(gates.get('4'))}")
    if gates.get("4") == "n/a":
        console.print(f"                 ({info.get('gate4_na_reason')})")

    if attested:
        detail = f" ({attestation_term})" if attestation_term else ""
        console.print(f"  Gate 5 (Human): [green]PASS[/green]{detail}")
        return
    console.print("  Gate 5 (Human): [yellow]PENDING[/yellow]")


def _print_status_task_section(task_summary: dict[str, Any] | None) -> None:
    """Render task summary for one ADR when tasks exist."""
    if task_summary is None:
        return

    total = task_summary.get("total", 0)
    completed = task_summary.get("completed", 0)
    in_progress = task_summary.get("in_progress", 0)
    pending = task_summary.get("pending", 0)
    blocked = task_summary.get("blocked", 0)
    escalated = task_summary.get("escalated", 0)
    tracing_policy = task_summary.get("tracing_policy", "advisory")

    parts = [f"{completed}/{total} done"]
    if in_progress > 0:
        parts.append(f"{in_progress} active")
    if pending > 0:
        parts.append(f"{pending} pending")
    if blocked > 0:
        parts.append(f"{blocked} blocked")
    if escalated > 0:
        parts.append(f"[red]{escalated} escalated[/red]")

    policy_label = "[bold]required[/bold]" if tracing_policy == "required" else "advisory"
    console.print(f"  Tasks:          {', '.join(parts)} (tracing: {policy_label})")


# ---------------------------------------------------------------------------
# Row and table renderers
# ---------------------------------------------------------------------------


def _render_status_row(
    adr_id: str, info: dict[str, Any], default_mode: str, show_gates: bool
) -> None:
    """Render one ADR row for text status output."""
    attested = bool(info.get("attested", False))
    lifecycle_status = info.get("lifecycle_status", "Pending")
    lane = cast(str, info.get("lane", default_mode))
    gates = cast(dict[str, str], info.get("gates", {}))
    attestation_term = info.get("attestation_term")
    obpi_rows = cast(list[dict[str, Any]], info.get("obpis", []))
    obpi_summary = cast(dict[str, Any], info.get("obpi_summary", {}))

    console.print(f"[bold]{adr_id}[/bold] ({lifecycle_status})")
    _print_status_obpi_section(obpi_rows, obpi_summary)
    _print_status_task_section(info.get("task_summary"))

    qc_readiness, qc_blockers = _qc_readiness(gates, lane, obpi_summary)
    console.print(f"  QC Readiness:   {_render_qc_readiness(qc_readiness, qc_blockers)}")
    if show_gates:
        _print_status_gate_section(info, lane, gates, attested, attestation_term)
    console.print()


def _is_foundation_adr(adr_id: str) -> bool:
    """Return True for foundation ADRs (ADR-0.0.x pattern)."""
    import re  # noqa: PLC0415

    m = re.match(r"^ADR-(\d+)\.(\d+)\.\d+", adr_id)
    return m is not None and m.group(1) == "0" and m.group(2) == "0"


def _render_status_table(
    adrs: dict[str, dict[str, Any]],
    default_mode: str,
    *,
    adr_type: str | None = None,
) -> None:
    """Render ADR status as three tables: Foundation, Features, and Pool.

    When *adr_type* is given (``"foundation"``, ``"feature"``, or ``"pool"``),
    only the matching table is rendered.
    """
    from gzkit.commands.status import _adr_status_sort_key  # noqa: PLC0415

    foundation: list[tuple[str, dict[str, Any]]] = []
    features: list[tuple[str, dict[str, Any]]] = []
    pool: list[tuple[str, dict[str, Any]]] = []
    for adr_id, info in sorted(adrs.items(), key=lambda item: _adr_status_sort_key(item[0])):
        if _is_pool_adr_id(adr_id):
            pool.append((adr_id, info))
        elif _is_foundation_adr(adr_id):
            foundation.append((adr_id, info))
        else:
            features.append((adr_id, info))

    printed = False
    if adr_type in (None, "foundation"):
        _render_adr_table(TABLE_TITLE_FOUNDATION, foundation, default_mode)
        printed = True
    if adr_type in (None, "feature") and features:
        if printed:
            console.print()
        _render_adr_table(TABLE_TITLE_FEATURE, features, default_mode)
        printed = True
    if adr_type in (None, "pool") and pool:
        if printed:
            console.print()
        _render_adr_table(TABLE_TITLE_POOL, pool, default_mode)
    console.print("Checks legend: O=OBPI completion, T=TDD, D=Docs, B=BDD, H=Human attestation")


def _render_adr_table(
    title: str,
    rows: list[tuple[str, dict[str, Any]]],
    default_mode: str,
) -> None:
    """Render a single ADR status table with the given title and rows."""
    table = Table(title=title, box=box.ROUNDED, padding=(0, 0))
    table.add_column("ADR", overflow="ellipsis")
    table.add_column("Life", no_wrap=True)
    table.add_column("Lane", no_wrap=True)
    table.add_column("OBPI", justify="right", no_wrap=True)
    table.add_column("Unit", no_wrap=True)
    table.add_column("QC", no_wrap=True)
    table.add_column("Checks", no_wrap=True)
    table.row_styles = ["none", "dim"]

    for adr_id, info in rows:
        lane = cast(str, info.get("lane", default_mode))
        gates = cast(dict[str, str], info.get("gates", {}))
        obpi_summary = cast(dict[str, Any], info.get("obpi_summary", {}))
        lifecycle_status = cast(str, info.get("lifecycle_status", "Pending"))

        obpi_total = cast(int, obpi_summary.get("total", 0))
        obpi_completed = cast(int, obpi_summary.get("completed", 0))
        obpi_unit_status = cast(str, obpi_summary.get("unit_status", "unscoped"))
        qc_readiness, qc_blockers = _qc_readiness(gates, lane, obpi_summary)
        qc_label = "READY" if qc_readiness == "ready" else "PENDING"

        table.add_row(
            adr_id,
            lifecycle_status,
            lane.upper(),
            f"{obpi_completed}/{obpi_total}",
            obpi_unit_status.upper(),
            qc_label,
            _render_pending_checks_cell(qc_blockers),
        )

    console.print(table)


# ---------------------------------------------------------------------------
# ADR report renderer
# ---------------------------------------------------------------------------


def _render_adr_report(result: dict[str, Any]) -> None:
    """Render deterministic ASCII table report for a single ADR."""
    from gzkit.commands.status import ADR_SEMVER_STATUS_ID_RE  # noqa: PLC0415

    obpi_summary = cast(dict[str, Any], result.get("obpi_summary", {}))
    obpi_total = cast(int, obpi_summary.get("total", 0))
    obpi_completed = cast(int, obpi_summary.get("completed", 0))
    gates = cast(dict[str, str], result.get("gates", {}))
    lane = cast(str, result.get("lane", "lite"))
    qc_readiness, _qc_blockers = _qc_readiness(gates, lane, obpi_summary)
    closeout_label = "READY" if result.get("closeout_ready") else "BLOCKED"
    qc_label = "READY" if qc_readiness == "ready" else "PENDING"

    # --- ADR Overview ---
    adr_full = cast(str, result["adr"])
    m = ADR_SEMVER_STATUS_ID_RE.match(adr_full)
    adr_short = f"ADR-{m['major']}.{m['minor']}.{m['patch']}" if m else adr_full

    overview = Table(title="ADR Overview", box=box.ROUNDED, padding=(0, 1))
    overview.add_column("ADR", no_wrap=True)
    overview.add_column("Lane", no_wrap=True)
    overview.add_column("Life", no_wrap=True)
    overview.add_column("Phase", no_wrap=True)
    overview.add_column("OBPI", no_wrap=True)
    overview.add_column("Closeout", no_wrap=True)
    overview.add_column("QC", no_wrap=True)
    overview.add_row(
        adr_short,
        lane,
        cast(str, result.get("lifecycle_status", "Pending")),
        cast(str, result.get("closeout_phase", "pre_closeout")),
        f"{obpi_completed}/{obpi_total}",
        closeout_label,
        qc_label,
    )
    console.print(overview)

    # --- OBPIs ---
    obpi_rows = cast(list[dict[str, Any]], result.get("obpis", []))
    obpi_table = Table(title="OBPIs", box=box.ROUNDED, padding=(0, 1))
    obpi_table.add_column("#", no_wrap=True)
    obpi_table.add_column("OBPI ID", overflow="fold")
    obpi_table.add_column("State", no_wrap=True)
    obpi_table.add_column("Brief", no_wrap=True)
    obpi_table.add_column("Done", no_wrap=True)
    for idx, row in enumerate(obpi_rows, 1):
        obpi_table.add_row(
            f"{idx:02d}",
            cast(str, row.get("id", "")),
            cast(str, row.get("runtime_state", "pending")),
            cast(str, row.get("brief_status", "draft")),
            "yes" if row.get("completed") else "no",
        )
    console.print(obpi_table)

    # --- Issues ---
    issues: list[str] = []
    for idx, row in enumerate(obpi_rows, 1):
        prefix = f"{idx:02d}"
        for issue in cast(list[str], row.get("issues", [])):
            issues.append(f"{prefix} {issue}")
        for issue in cast(list[str], row.get("reflection_issues", [])):
            issues.append(f"{prefix} {issue}")
    if issues:
        console.print("Issues")
        for line in issues:
            console.print(line)
