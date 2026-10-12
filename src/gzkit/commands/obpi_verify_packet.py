"""``gz obpi verify-packet`` — re-run the Step-4a packet's transcripts (GHI #942).

Stage 4a is the surface the operator reads when deciding to attest, and its pasted
command output was believed on the composing agent's word. This command re-runs every
``$``-prompted transcript in the packet and reports which pasted lines the command did
not actually produce, so the fabrication is on the table before the attestation is.

The replay runs in a disposable copy of the working tree and never touches the live
checkout; when no copy can be built, no transcript runs and the packet is
NOT-VERIFIED (GHI #1157).

Re-running a packet is a check (OBPI-0.35.0-15): when a pipeline run is in flight
for the OBPI the packet names, its position is recorded as ``verify-packet``
inside the stage the run has reached, whatever the verdict. The stage does not
move.

Exit codes (`.claude/rules/cli.md`):
  0 = packet VERIFIED (every transcript reproduces)
  1 = user/config error (packet file not found)
  3 = packet NOT-VERIFIED (one or more blockers) — fail-closed signal
"""

from __future__ import annotations

from pathlib import Path

from rich.markup import escape

from gzkit.cli.helpers.exit_codes import EXIT_POLICY_BREACH, EXIT_SUCCESS, EXIT_USER_ERROR
from gzkit.commands.common import console, get_project_root
from gzkit.commands.obpi_precomplete import recorded_obpi_id
from gzkit.governance.stage4_packet import PacketVerification, verify_packet
from gzkit.pipeline_runtime import RunCrossing, record_run_position

#: How the pipeline skill names a Step-4a packet: ``<OBPI-ID>.stage4a.md``.
_PACKET_SUFFIX = ".stage4a.md"


def _packet_obpi_id(packet_path: Path) -> str:
    """Return the OBPI a Step-4a packet names by its file name.

    The command takes a packet path and no OBPI id, so the name is the only
    thing that says whose round this is. Whatever spelling it carries is named
    by the resolver the launcher uses (``recorded_obpi_id``; operator ruling
    2026-10-12, Open Design Question 19), so a short form or a longer prefix
    records under the id the launch carries. A packet named any other way
    names no run, and no position is recorded for it.
    """
    return packet_path.name.removesuffix(_PACKET_SUFFIX)


def _render_human(result: PacketVerification) -> None:
    verdict = "[green]VERIFIED[/green]" if result.verified else "[red]NOT-VERIFIED[/red]"
    console.print(f"Step-4a packet: {escape(result.packet)} — {verdict}")
    console.print("\n  Transcripts (re-run):")
    for t in result.transcripts:
        if not t.ran:
            tag = "[red]not run[/red]"
        elif t.timed_out:
            tag = "[red]timeout[/red]"
        elif t.missing_lines:
            tag = f"[red]{len(t.missing_lines)} unreproduced[/red]"
        else:
            tag = "[green]reproduces[/green]"
        console.print(f"    {tag}  exit {t.exit_status}  {escape(t.command.splitlines()[0])}")
        for line in t.missing_lines:
            console.print(f"        [red]not produced:[/red] {escape(line)}")
    if result.citations:
        console.print("\n  Cited, NOT re-run (no output claimed — verify by receipt):")
        for command in result.citations:
            console.print(f"    {escape(command)}")
    if result.blockers:
        console.print("\n  [red]Blockers:[/red]")
        for blocker in result.blockers:
            console.print(f"    - {escape(blocker)}")


def obpi_verify_packet_cmd(*, packet: str, as_json: bool = False) -> int:
    """Handle ``gz obpi verify-packet``.

    Re-executes the packet's transcripts in a disposable copy of the project root's
    working tree, never the root itself (GHI #1157). Returns
    ``EXIT_POLICY_BREACH`` (3) when a pasted line does not reproduce, so the operator
    and any downstream gate see the fail-closed signal before attestation.
    """
    project_root = get_project_root()
    packet_path = Path(packet)
    if not packet_path.is_absolute():
        packet_path = project_root / packet_path
    if not packet_path.is_file():
        console.print(f"[red]Packet not found: {escape(packet)}[/red]")
        raise SystemExit(EXIT_USER_ERROR)

    result = verify_packet(project_root, packet_path)
    record_run_position(
        project_root,
        recorded_obpi_id(project_root, _packet_obpi_id(packet_path)),
        RunCrossing(boundary="verify-packet"),
    )

    if as_json:
        print(result.model_dump_json(indent=2))
    else:
        _render_human(result)

    if not result.verified:
        raise SystemExit(EXIT_POLICY_BREACH)
    return EXIT_SUCCESS
