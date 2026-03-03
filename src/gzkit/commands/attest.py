"""Attest command implementation."""

from datetime import date

from gzkit.commands.common import (
    GzCliError,
    _attestation_gate_snapshot,
    _canonical_attestation_term,
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_git_user,
    get_project_root,
    resolve_adr_file,
)
from gzkit.ledger import Ledger, attested_event


def attest(
    adr: str,
    attest_status: str,
    reason: str | None,
    force: bool,
    dry_run: bool,
) -> None:
    """Record human attestation for an ADR."""
    config = ensure_initialized()
    project_root = get_project_root()

    if attest_status in ("partial", "dropped") and not reason:
        raise GzCliError(f"--reason required for {attest_status} status")

    ledger = Ledger(project_root / config.paths.ledger)
    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)

    # Verify ADR exists (support nested ADR layout)
    _adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    if _is_pool_adr_id(adr_id):
        raise GzCliError(
            f"Pool ADRs cannot be attested: {adr_id}. Promote this ADR from pool first."
        )

    snapshot = _attestation_gate_snapshot(project_root, config, ledger, adr_id)
    if force and not snapshot["ready"] and not reason:
        raise GzCliError("--reason required when --force bypasses failing gate prerequisites")

    if not force and not snapshot["ready"]:
        blockers = "\\n".join(f"- {blocker}" for blocker in snapshot["blockers"])
        raise GzCliError(
            "Attestation blocked by prerequisite gates:\\n"
            f"{blockers}\\n"
            "Run required gate commands first, or use --force with --reason."
        )

    if not force:
        console.print("Checking prerequisite gates...")
    elif not snapshot["ready"]:
        console.print(
            "[yellow]Force override:[/yellow] bypassing failed prerequisites with recorded reason."
        )

    # Get attester identity
    attester = get_git_user()
    canonical_term = _canonical_attestation_term(attest_status, reason)

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(f"  Would attest ADR: {adr_id}")
        console.print(f"  Term: {canonical_term}")
        console.print(f"  Raw status token: {attest_status}")
        console.print(f"  By: {attester}")
        if reason:
            console.print(f"  Reason: {reason}")
        return

    # Record attestation
    ledger.append(attested_event(adr_id, attest_status, attester, reason))

    # Update ADR file attestation block (simplified)
    # In a full implementation, we would parse and update the table
    today = date.today().isoformat()
    console.print("\\n[green]Attestation recorded:[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Term: {canonical_term}")
    console.print(f"  Raw status token: {attest_status}")
    console.print(f"  By: {attester}")
    console.print(f"  Date: {today}")
    if reason:
        console.print(f"  Reason: {reason}")
