"""Attest command implementation."""

from datetime import date
from pathlib import Path
from typing import cast

from gzkit.commands.common import (
    GzCliError,
    _attestation_gate_snapshot,
    _canonical_attestation_term,
    _closeout_form_attestation_text,
    _closeout_form_timestamp,
    _gate4_na_reason,
    _is_pool_adr_id,
    _update_adr_attestation_block,
    _write_adr_closeout_form,
    console,
    ensure_initialized,
    get_git_user,
    get_project_root,
    load_manifest,
    resolve_adr_file,
    resolve_adr_ledger_id,
)
from gzkit.commands.status import _adr_obpi_status_rows
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger, attested_event


def _attest_verification_steps(
    manifest: dict[str, object], lane: str, project_root: Path
) -> list[tuple[str, str]]:
    """Render the closeout verification steps needed by the closeout form."""
    raw_verification = manifest.get("verification", {})
    verification = cast(
        dict[str, str],
        raw_verification if isinstance(raw_verification, dict) else {},
    )

    steps: list[tuple[str, str]] = [
        ("Gate 2 (TDD)", str(verification.get("test", "uv run gz test"))),
        ("Quality (Lint)", str(verification.get("lint", "uv run gz lint"))),
        ("Quality (Typecheck)", str(verification.get("typecheck", "uv run gz typecheck"))),
    ]
    if lane != "heavy":
        return steps

    steps.append(("Gate 3 (Docs)", str(verification.get("docs", "uv run mkdocs build --strict"))))
    if _gate4_na_reason(project_root, lane) is None:
        steps.append(("Gate 4 (BDD)", str(verification.get("bdd", "uv run -m behave features/"))))
    return steps


def _check_obpi_completion(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
    force: bool,
) -> None:
    """Block attestation when OBPIs are incomplete unless forced."""
    obpi_check_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)
    incomplete = [r["id"] for r in obpi_check_rows if not r["completed"]]
    if incomplete and not force:
        blocker_list = "\n".join(f"- {oid}" for oid in incomplete)
        msg = (
            f"Cannot attest {adr_id} as completed — "
            f"{len(incomplete)} OBPI(s) are not completed:\n"
            f"{blocker_list}\n"
            "Complete all OBPIs first, or use --force with --reason."
        )
        raise GzCliError(msg)  # noqa: TRY003
    if incomplete and force:
        console.print(
            f"[yellow]Warning:[/yellow] {len(incomplete)} OBPI(s) still incomplete, "
            "proceeding with --force."
        )


def _warn_if_closeout_active(ledger: Ledger, adr_id: str) -> None:
    """Print a deprecation warning when closeout is already active for this ADR."""
    graph = ledger.get_artifact_graph()
    adr_info = graph.get(adr_id)
    if adr_info and adr_info.get("closeout_initiated"):
        console.print(
            "[yellow]Deprecated:[/yellow] Closeout is active for "
            f"{adr_id}. Attestation is now managed by "
            f"`gz closeout {adr_id}`. Standalone `gz attest` during "
            "closeout is deprecated and will be removed in a future release.",
        )


def _validate_attest_inputs(
    attest_status: str, reason: str | None, force: bool, snapshot: dict[str, object]
) -> None:
    """Validate attestation inputs and gate prerequisites. Raises GzCliError on failure."""
    if attest_status in ("partial", "dropped") and not reason:
        msg = f"--reason required for {attest_status} status"
        raise GzCliError(msg)  # noqa: TRY003

    if force and not snapshot["ready"] and not reason:
        msg = "--reason required when --force bypasses failing gate prerequisites"
        raise GzCliError(msg)  # noqa: TRY003

    if force and reason:
        stripped = reason.strip()
        if len(stripped) < 20:
            msg = f"--force reason must be at least 20 characters (got {len(stripped)})"
            raise GzCliError(msg)  # noqa: TRY003
        if " " not in stripped:
            msg = (
                "--force reason must contain multiple words (single-word reasons are not accepted)"
            )
            raise GzCliError(msg)  # noqa: TRY003

    if not force and not snapshot["ready"]:
        blocker_list = cast(list[str], snapshot["blockers"])
        blockers = "\\n".join(f"- {blocker}" for blocker in blocker_list)
        msg = (
            "Attestation blocked by prerequisite gates:\\n"
            f"{blockers}\\n"
            "Run required gate commands first, or use --force with --reason."
        )
        raise GzCliError(msg)  # noqa: TRY003


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
        msg = f"--reason required for {attest_status} status"
        raise GzCliError(msg)  # noqa: TRY003

    ledger = Ledger(project_root / config.paths.ledger)
    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)

    # Verify ADR exists (support nested ADR layout)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    if _is_pool_adr_id(adr_id):
        msg = f"Pool ADRs cannot be attested: {adr_id}. Promote this ADR from pool first."
        raise GzCliError(msg)  # noqa: TRY003

    # Warn when closeout pipeline is active (OBPI-0.19.0-09)
    _warn_if_closeout_active(ledger, adr_id)

    snapshot = _attestation_gate_snapshot(project_root, config, ledger, adr_id)
    _validate_attest_inputs(attest_status, reason, force, snapshot)

    if not force:
        console.print("Checking prerequisite gates...")
    elif not snapshot["ready"]:
        console.print(
            "[yellow]Force override:[/yellow] bypassing failed prerequisites with recorded reason."
        )

    if attest_status == "completed":
        _check_obpi_completion(project_root, config, ledger, adr_id, force)

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

    today = date.today().isoformat()
    attestation_text = _closeout_form_attestation_text(attest_status, reason)
    timestamp_utc = _closeout_form_timestamp()
    verification_steps = _attest_verification_steps(
        load_manifest(project_root), snapshot["lane"], project_root
    )
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)
    obpi_rows = _adr_obpi_status_rows(project_root, config, ledger, adr_id)

    _write_adr_closeout_form(
        project_root,
        adr_id,
        adr_file,
        obpi_rows,
        verification_steps,
        gate_statuses,
        attestation_command=f"uv run gz attest {adr_id} --status completed",
        attestation_text=attestation_text,
        attestation_term=canonical_term,
        attester=attester,
        timestamp_utc=timestamp_utc,
    )
    _update_adr_attestation_block(
        adr_file,
        adr_id,
        canonical_term=canonical_term,
        attester=attester,
        attestation_date=today,
        attestation_reason=attestation_text,
    )

    # Auto-fix OBPI brief frontmatter to match ledger-derived state (ADR-0.0.9-04)
    from gzkit.commands.closeout_form import auto_fix_obpi_rows

    auto_fix_obpi_rows(project_root, obpi_rows)

    console.print("\\n[green]Attestation recorded:[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Term: {canonical_term}")
    console.print(f"  Raw status token: {attest_status}")
    console.print(f"  By: {attester}")
    console.print(f"  Date: {today}")
    if reason:
        console.print(f"  Reason: {reason}")
