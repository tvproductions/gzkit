"""``gz ledger correct`` — the append-only corrective action (GHI #611).

Operator intent, verbatim: *"we need the power to UNDO agent (or human)
error"*, *"not to erase the ledger, but to provide subsequent corrective
actions."*

One verb over every event type, deliberately not a fifth reversal verb for a
fifth error class. Corrective work under ADR-0.0.71, whose § Intent named
repudiation a **port** with ``obpi_completion_repudiated`` as its first adapter.

Operator-gated on the same terms as ``gz obpi repudiate`` (ADR-0.0.71 Boundary
Invariant 1): a non-empty ``--attestor`` and ``--reason``, both fail-closed.
Undoing a recorded fact is as human-gated as recording one.
"""

from __future__ import annotations

import json

from gzkit.commands.common import console, ensure_initialized, get_project_root
from gzkit.ledger import Ledger, LedgerEvent
from gzkit.ledger_corrections import CORRECTION_EVENT, correction_state, resolve_subject
from gzkit.ledger_events import ledger_event_corrected_event


def _fail(what: str, why: str, next_step: str) -> None:
    """Emit three-part recovery prose and exit 1 (``guardrail-feedback-prose.md``)."""
    console.print(f"[red]Refused:[/red] {what}")
    console.print(f"  Why: {why}")
    console.print(f"  Next: {next_step}")
    raise SystemExit(1)


def _describe(rows: list[LedgerEvent]) -> None:
    """Print each resolved subject row so the operator reviews the real target."""
    for row in rows:
        console.print(f"  [cyan]{row.event}[/cyan]  id={row.id}  ts={row.ts}")
        for key in sorted(row.extra):
            console.print(f"      {key}: {str(row.extra[key])[:160]}")


def ledger_correct_cmd(
    *,
    subject_event: str,
    subject_id: str,
    subject_ts: str,
    disposition: str,
    cause: str,
    reason: str,
    attestor: str,
    dry_run: bool,
) -> None:
    """Append one corrective action against a prior ledger row."""
    if not attestor.strip():
        _fail(
            "--attestor is empty.",
            "A correction undoes a recorded fact, so it is human-gated on the same "
            "terms as `gz obpi repudiate` (ADR-0.0.71 Boundary Invariant 1: 'only a "
            "human repudiates'). An unattributed correction records that state "
            "changed but never who changed it.",
            'rerun with --attestor "<human>".',
        )
    if not reason.strip():
        _fail(
            "--reason is empty.",
            "AGENTS.md § PRIME DIRECTIVE #6 requires every defect to be trackable. A "
            "correction with no stated reason leaves the next reader unable to tell a "
            "governed repair from an unexplained state change.",
            'rerun with --reason "<why this row is being corrected>".',
        )
    if subject_event == CORRECTION_EVENT:
        _fail(
            f"a correction may not name another '{CORRECTION_EVENT}' row as its subject.",
            "Correcting a correction would make the netting resolve itself "
            "recursively, and a cycle would make 'what is live' depend on evaluation "
            "order. 'reinstated' is the in-family reversal.",
            "rerun against the ORIGINAL row with --disposition reinstated.",
        )

    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)
    history = ledger.read_all()

    key = (subject_event, subject_id, subject_ts)
    matches = resolve_subject(history, key)
    if not matches:
        _fail(
            f"no ledger row matches (event={subject_event}, id={subject_id}, ts={subject_ts}).",
            "A correction names its subject by the exact (event, id, ts) triple. A "
            "dangling reference must never be written: it would sit in the ledger "
            "asserting a correction that no reader can apply.",
            (
                "list the candidate rows with `uv run gz ledger corrections`, or read the "
                f"row's exact ts out of the ledger: grep -F {subject_id} .gzkit/ledger.jsonl"
            ),
        )

    current = correction_state(history).get(key)
    if disposition == "reinstated" and current is None:
        _fail(
            f"the subject carries no correction to reinstate (event={subject_event}, "
            f"ts={subject_ts}).",
            "'reinstated' clears a prior void or discharge. Recording one against an "
            "uncorrected row would assert a reversal that never happened.",
            "check the current disposition, or use --disposition void|discharged.",
        )

    event = ledger_event_corrected_event(
        subject_event=subject_event,
        subject_id=subject_id,
        subject_ts=subject_ts,
        disposition=disposition,
        cause=cause,
        attestor=attestor,
        reason=reason,
        parent=matches[-1].parent,
    )

    console.print(f"[bold]Subject rows resolved:[/bold] {len(matches)}")
    _describe(matches)
    console.print(f"[bold]Current disposition:[/bold] {current or 'none (live)'}")
    console.print(f"[bold]Resulting disposition:[/bold] {disposition}")

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        return

    ledger.append(event)
    console.print("[green]Correction recorded.[/green] The subject row is unchanged.")
    console.print(f"  attestor: {attestor}")
    console.print(f"  cause: {cause}")

    if current == disposition:
        console.print(
            "  [yellow]Note:[/yellow] the subject already carried this disposition; "
            "the correction is inert and recorded for provenance only."
        )


def ledger_corrections_cmd(*, as_json: bool = False) -> None:
    """List every currently-corrected ledger row and its disposition."""
    config = ensure_initialized()
    ledger = Ledger(get_project_root() / config.paths.ledger)
    state = correction_state(ledger.read_all())

    if as_json:
        console.print(
            json.dumps(
                [
                    {
                        "subject_event": key[0],
                        "subject_id": key[1],
                        "subject_ts": key[2],
                        "disposition": value,
                    }
                    for key, value in sorted(state.items())
                ],
                indent=2,
            )
        )
        return

    if not state:
        console.print("No ledger corrections are in force.")
        return
    console.print(f"[bold]Corrected ledger rows: {len(state)}[/bold]")
    for key, value in sorted(state.items()):
        console.print(f"  {value:<11} {key[0]}  id={key[1]}  ts={key[2]}")
