"""``gz obpi verify-packet`` — re-run the Step-4a packet's transcripts (GHI #942).

Stage 4a is the surface the operator reads when deciding to attest, and its pasted
command output was believed on the composing agent's word. This command re-runs every
``$``-prompted transcript in the packet and reports which pasted lines the command did
not actually produce, so the fabrication is on the table before the attestation is.

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
from gzkit.governance.stage4_packet import PacketVerification, verify_packet


def _render_human(result: PacketVerification) -> None:
    verdict = "[green]VERIFIED[/green]" if result.verified else "[red]NOT-VERIFIED[/red]"
    console.print(f"Step-4a packet: {escape(result.packet)} — {verdict}")
    console.print("\n  Transcripts (re-run):")
    for t in result.transcripts:
        if t.timed_out:
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

    Re-executes the packet's transcripts against the project root. Returns
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

    if as_json:
        print(result.model_dump_json(indent=2))
    else:
        _render_human(result)

    if not result.verified:
        raise SystemExit(EXIT_POLICY_BREACH)
    return EXIT_SUCCESS
