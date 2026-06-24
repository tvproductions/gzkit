"""``gz obpi present-evidence`` — tool-generated Stage-4 evidence (GHI #643).

The Stage-4 acceptance ceremony must not be authored by the agent. This command
generates the evidence packet from observables — it runs the brief's ``## Demo``,
reads the on-disk ARB receipts, and runs ``gz covers`` — writes the packet to
``.gzkit/evidence/<OBPI>.evidence.json``, and prints it for the operator to read
at Stage 4. The agent relays this output; it does not type the evidence.

Exit codes (`.claude/rules/cli.md`):
  0 = packet is ATTESTABLE (every blocker clear)
  1 = user/config error (brief not found)
  3 = packet is NOT-ATTESTABLE (one or more blockers) — fail-closed signal
"""

from __future__ import annotations

from gzkit.cli.helpers.exit_codes import EXIT_POLICY_BREACH, EXIT_SUCCESS, EXIT_USER_ERROR
from gzkit.commands.common import console, get_project_root
from gzkit.commands.obpi_precomplete import _resolve_brief_path
from gzkit.governance.stage4_evidence import (
    EvidencePacket,
    generate_evidence_packet,
    write_packet,
)


def _render_human(packet: EvidencePacket, packet_file: str) -> None:
    verdict = "[green]ATTESTABLE[/green]" if packet.attestable else "[red]NOT-ATTESTABLE[/red]"
    console.print(f"Stage-4 evidence: {packet.obpi_id} — {verdict}")
    console.print(f"  packet: {packet_file}")
    console.print("\n  Demo (re-runnable proof):")
    for d in packet.demos:
        status = (
            "[green]exit 0[/green]" if d.exit_status == 0 else f"[red]exit {d.exit_status}[/red]"
        )
        console.print(f"    {status}  {d.command}")
    console.print("\n  ARB receipts:")
    for r in packet.receipts:
        if not r.found:
            console.print(f"    [red]missing[/red]  {r.step}")
        else:
            tag = (
                "[green]exit 0[/green]"
                if r.exit_status == 0
                else f"[red]exit {r.exit_status}[/red]"
            )
            console.print(f"    {tag}  {r.step} ({r.receipt_id})")
    console.print(
        f"\n  REQ coverage: {packet.covers_uncovered} uncovered / {packet.covers_total} total"
    )
    if packet.blockers:
        console.print("\n  [red]Blockers:[/red]")
        for b in packet.blockers:
            console.print(f"    - {b}")


def obpi_present_evidence_cmd(*, obpi_id: str, as_json: bool = False) -> int:
    """Handle ``gz obpi present-evidence``.

    Generates and persists the tool-derived evidence packet. Returns
    ``EXIT_POLICY_BREACH`` (3) when the packet is NOT-ATTESTABLE so the operator and
    any downstream gate see the fail-closed signal.
    """
    project_root = get_project_root()
    brief_path = _resolve_brief_path(project_root, obpi_id)
    if brief_path is None:
        console.print(f"[red]Brief not found for {obpi_id}[/red]")
        raise SystemExit(EXIT_USER_ERROR)

    packet = generate_evidence_packet(project_root, brief_path, obpi_id)
    packet_file = write_packet(project_root, packet)
    rel = packet_file.relative_to(project_root).as_posix()

    if as_json:
        print(packet.model_dump_json(indent=2))
    else:
        _render_human(packet, rel)

    if not packet.attestable:
        raise SystemExit(EXIT_POLICY_BREACH)
    return EXIT_SUCCESS
