"""gz airlock — operator-facing surface over the airlock-IN membrane primitive.

Surfaces the airlock-IN three-beat gate (``airlock_enter``) as a CLI verb
(ADR-0.33.0, OBPI-0.33.0-02). ``gz airlock in`` runs the DECLARE -> PING ->
RECONCILE -> decide preflight for a target OBPI against its declared brief and
reports the decision plus the two-layer seam-map counts.

DIAGNOSTIC-ONLY FOR NOW — a staged posture, NOT the contract. The airlock tracer
is not fail-closed at the CLI: a NO-GO prints ``build_refusal`` but the verb
still EXITS 0. This mirrors the pipeline call site, which was deliberately
downgraded from ``SystemExit(3)`` to a warning. The only non-zero exit is a user
error (unresolvable brief -> 1).

The reason is calibration, not design: production reach for an OBPI id yields an
empty seam-map, so a fail-closed gate would be vacuous or arbitrary (parent ADR
§ Calibration frontier, operator-attested 2026-07-10 — "calibration is a named
successor increment"). The DECLARED end state blocks: § Boundary Invariant 4,
"an un-accounted seam makes GO structurally unreachable."

§ Consequences Negative #5 is NOT authority for never blocking — it governs the
*shape* of a refusal (name the seam, its provenance, a one-command re-sense;
logged and revocable override) so a NO-GO is never an undiagnosable 2am wall.
"""

from __future__ import annotations

import json

from gzkit.airlock.enter import airlock_enter, build_refusal
from gzkit.airlock.exit import ExitReport, airlock_exit
from gzkit.airlock.model import Decision, Preflight
from gzkit.commands.common import console, get_project_root
from gzkit.ledger import Ledger
from gzkit.pipeline_markers import find_obpi_brief


def _preflight_payload(target: str, phase: str | None, preflight: Preflight) -> dict:
    """Machine-readable projection of a preflight result (the ``--json`` shape)."""
    seam_map = preflight.seam_map
    decision = preflight.decision.value if preflight.decision is not None else None
    return {
        "target": target,
        "phase": phase,
        "decision": decision,
        "authority": preflight.authority.value,
        "blast_radius": preflight.blast_radius,
        "seam_map": {
            "bodies": len(seam_map.bodies),
            "push": len(seam_map.push_edges),
            "pull": len(seam_map.pull_edges),
            "unaccounted": len(seam_map.unaccounted),
        },
        "unaccounted": [edge.target for edge in seam_map.unaccounted],
    }


def _render_human(target: str, phase: str | None, preflight: Preflight, dry_run: bool) -> None:
    """Human-readable preflight report — decision, seam counts, refusal diagnostic."""
    seam_map = preflight.seam_map
    decision = preflight.decision
    label = decision.value if decision is not None else "none"
    mode = " (dry-run)" if dry_run else ""
    console.print(f"[bold]airlock in[/bold]{mode} — {target}" + (f" @ {phase}" if phase else ""))
    console.print(f"  decision: {label}")
    console.print(
        f"  seams: bodies={len(seam_map.bodies)} push={len(seam_map.push_edges)} "
        f"pull={len(seam_map.pull_edges)} unaccounted={len(seam_map.unaccounted)}"
    )
    if decision is not Decision.PROCEED:
        console.print(build_refusal(seam_map, target))


def airlock_in_cmd(
    *,
    target: str,
    phase: str | None = None,
    dry_run: bool = False,
    as_json: bool = False,
) -> None:
    """Run the airlock-IN preflight gate for a target OBPI and report the decision.

    Resolves the target's brief, runs ``airlock_enter``, and reports the decision
    plus seam-map counts. DIAGNOSTIC-ONLY: a NO-GO prints a refusal but still
    exits 0. In ``--dry-run`` no ledger is written (no L2 ``airlock_in`` event);
    otherwise the transit is booked to the project ledger.
    """
    project_root = get_project_root()
    docs_root = project_root / "docs" / "design" / "adr"
    brief_path = find_obpi_brief(docs_root, target)
    if brief_path is None:
        console.print(f"[red]No OBPI brief found for target:[/red] {target}")
        raise SystemExit(1)

    ledger = None if dry_run else Ledger(project_root / ".gzkit" / "ledger.jsonl")
    preflight = airlock_enter(target, brief_path, ledger=ledger)

    if as_json:
        print(json.dumps(_preflight_payload(target, phase, preflight), indent=2))  # noqa: T201
        return
    _render_human(target, phase, preflight, dry_run)


def _exit_payload(target: str, report: ExitReport) -> dict:
    """Machine-readable projection of an airlock-OUT report (the ``--json`` shape)."""
    return {
        "target": target,
        "verdict": report.drift_diff.verdict.value,
        "decision_menu": [decision.value for decision in report.decision_menu],
        "drift": [edge.target for edge in report.drift_diff.drift],
        "findings": [
            {"target": f.edge.target, "kind": f.kind.value, "recommendation": f.recommendation}
            for f in report.findings
        ],
        "routing": [
            {"door": t.door.value, "correction": t.correction, "smuggled": t.smuggled}
            for t in report.routing
        ],
        "proposals": [{"surface": p.surface, "proposal": p.proposal} for p in report.proposals],
    }


def _render_exit_human(target: str, report: ExitReport, dry_run: bool) -> None:
    """Human-readable exit report — verdict, findings, fresh-transit routing, proposals."""
    mode = " (dry-run)" if dry_run else ""
    console.print(f"[bold]airlock out[/bold]{mode} — {target}")
    console.print(f"  verdict: {report.drift_diff.verdict.value}")
    console.print(f"  decision menu: {', '.join(d.value for d in report.decision_menu)}")
    for finding in report.findings:
        console.print(f"  finding ({finding.kind.value}): {finding.edge.target}")
        console.print(f"    -> {finding.recommendation}")
    for directive in report.routing:
        console.print(
            f"  fresh transit -> {directive.door.value}: {directive.correction} "
            f"(smuggled={directive.smuggled})"
        )
    for proposal in report.proposals:
        console.print(f"  L1 proposal (not written) for {proposal.surface}: {proposal.proposal}")


def airlock_out_cmd(
    *,
    target: str,
    dry_run: bool = False,
    as_json: bool = False,
) -> None:
    """Run the airlock-OUT exit membrane for a target OBPI and report the drift-diff.

    Resolves the target's brief, runs ``airlock_exit``, and reports the drift-diff
    verdict, findings + recommendations, the closed decision menu, and any
    fresh-transit routing. DIAGNOSTIC-ONLY (co-equal with ``gz airlock in``): a
    surfaced drift prints findings but still exits 0 — it reports, it never
    blocks. In ``--dry-run`` no ledger is written (no L2 ``airlock_out`` event);
    otherwise the transit is booked to the project ledger. NEVER writes L1 canon.
    """
    project_root = get_project_root()
    docs_root = project_root / "docs" / "design" / "adr"
    brief_path = find_obpi_brief(docs_root, target)
    if brief_path is None:
        console.print(f"[red]No OBPI brief found for target:[/red] {target}")
        raise SystemExit(1)

    ledger = None if dry_run else Ledger(project_root / ".gzkit" / "ledger.jsonl")
    report = airlock_exit(target, brief_path, ledger=ledger)

    if as_json:
        print(json.dumps(_exit_payload(target, report), indent=2))  # noqa: T201
        return
    _render_exit_human(target, report, dry_run)
