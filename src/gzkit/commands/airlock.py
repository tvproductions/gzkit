"""gz airlock — operator-facing surface over the airlock-IN membrane primitive.

Surfaces the airlock-IN three-beat gate (``airlock_enter``) as a CLI verb
(ADR-0.33.0, OBPI-0.33.0-02). ``gz airlock in`` runs the DECLARE -> PING ->
RECONCILE -> decide preflight for a target OBPI against its declared brief and
reports the decision plus the two-layer seam-map counts.

DIAGNOSTIC-ONLY contract (parent ADR § Consequences Negative #5): the airlock
tracer is NOT fail-closed at the CLI. A NO-GO prints ``build_refusal`` but the
verb still EXITS 0 — it reports, it does not hard-block. This mirrors the
pipeline call site, which was deliberately downgraded from ``SystemExit(3)`` to
a warning. The only non-zero exit is a user error (unresolvable brief -> 1).
"""

from __future__ import annotations

import json

from gzkit.airlock.enter import airlock_enter, build_refusal
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
