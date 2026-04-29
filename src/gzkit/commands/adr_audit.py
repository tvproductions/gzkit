"""ADR audit-check, covers-check, and emit-receipt command implementations."""

import json
import re
import sys
from collections.abc import Mapping
from datetime import date
from pathlib import Path
from typing import Any, cast

from gzkit.commands.adr_coverage import (
    OBPI_SEMVER_ITEM_RE,
    REQ_ID_RE,
    _build_covers_rows,
    _collect_adr_requirement_targets,
    _collect_covers_annotations,
    _compute_adr_coverage,
    _extract_adr_semver,
    _extract_h2_section_lines,
    _extract_obpi_requirement_targets,
    _print_adr_covers_check_result,
    _print_coverage_section,
    _req_prefix_for_obpi,
)
from gzkit.commands.common import (
    GzCliError,
    _reject_pool_adr_for_lifecycle,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_adr_ledger_id,
)
from gzkit.commands.status import _collect_obpi_files_for_adr, _inspect_obpi_brief
from gzkit.events import EventAnchor
from gzkit.hooks.core import enrich_completed_receipt_evidence
from gzkit.hooks.obpi import normalize_git_sync_state, normalize_scope_audit
from gzkit.ledger import (
    Ledger,
    audit_receipt_emitted_event,
    normalize_req_proof_inputs,
)
from gzkit.utils import capture_validation_anchor

# Re-export coverage symbols so existing imports keep working.
__all__ = [
    "OBPI_SEMVER_ITEM_RE",
    "REQ_ID_RE",
    "_build_covers_rows",
    "_collect_adr_requirement_targets",
    "_collect_covers_annotations",
    "_compute_adr_coverage",
    "_extract_adr_semver",
    "_extract_h2_section_lines",
    "_extract_obpi_requirement_targets",
    "_print_adr_covers_check_result",
    "_print_coverage_section",
    "_req_prefix_for_obpi",
]


def _collect_obpi_findings(
    project_root: Path,
    obpi_files: dict[str, Path],
    expected_obpis: list[str],
    ledger: Ledger,
) -> tuple[list[dict[str, Any]], list[str]]:
    """Return (findings, complete_obpi_ids) for OBPI linkage + evidence checks."""
    findings: list[dict[str, Any]] = []
    complete: list[str] = []

    if not expected_obpis and not obpi_files:
        findings.append({"id": None, "issue": "No OBPI briefs are linked to this ADR."})

    for expected_id in expected_obpis:
        if expected_id not in obpi_files:
            findings.append(
                {"id": expected_id, "issue": "Linked in ledger but no OBPI file found."}
            )

    graph = ledger.get_artifact_graph()
    for obpi_id, obpi_file in sorted(obpi_files.items()):
        inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id=obpi_id, graph=graph)
        if inspection["reasons"]:
            findings.append(
                {
                    "id": obpi_id,
                    "file": str(obpi_file.relative_to(project_root)),
                    "issue": "; ".join(inspection["reasons"]),
                    "frontmatter_status": inspection["frontmatter_status"],
                    "brief_status": inspection["brief_status"],
                }
            )
        else:
            complete.append(obpi_id)
    return findings, complete


def _partition_coverage_findings(
    coverage: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Split coverage ``uncovered`` entries by severity.

    GHI #268 — Advisory uncovered REQs (the default emitted by
    :func:`_compute_adr_coverage`) surface as warnings and do not block the
    audit; non-advisory severities are reserved for future per-REQ escalation
    and retain fail-closed behavior.
    """
    findings: list[dict[str, Any]] = [
        {
            "id": u["req_id"],
            "issue": "REQ not covered by any @covers test annotation.",
            "severity": u.get("severity", "advisory"),
        }
        for u in coverage["uncovered"]
    ]
    blocking = [cf for cf in findings if cf["severity"] != "advisory"]
    advisory = [cf for cf in findings if cf["severity"] == "advisory"]
    return findings, blocking, advisory


def _render_audit_check_result(
    adr_id: str,
    passed: bool,
    findings: list[dict[str, Any]],
    complete: list[str],
    coverage: dict[str, Any],
    coverage_blocking: list[dict[str, Any]],
    coverage_advisory: list[dict[str, Any]],
) -> None:
    """Print the human-readable audit-check summary."""
    console.print(f"[bold]ADR audit-check:[/bold] {adr_id}")
    if passed:
        console.print("[green]PASS[/green] All linked OBPIs are completed with evidence.")
        for obpi_id in complete:
            console.print(f"  - {obpi_id}")
    else:
        if findings:
            console.print("[red]FAIL[/red] OBPI completeness/evidence gaps found:")
            for finding in findings:
                finding_id = finding.get("id") or "(none)"
                console.print(f"  - {finding_id}: {finding.get('issue', '')}")
        if coverage_blocking:
            console.print(
                f"[red]FAIL[/red] {len(coverage_blocking)} REQ(s) missing @covers traceability:"
            )
            for cf in coverage_blocking:
                console.print(f"  - {cf['id']}")
    if coverage_advisory:
        console.print(
            f"[yellow]Advisory[/yellow] {len(coverage_advisory)} REQ(s) without "
            "@covers traceability (non-blocking):"
        )
        for cf in coverage_advisory:
            console.print(f"  - {cf['id']}")
    _print_coverage_section(coverage, [])


def adr_audit_check(adr: str, as_json: bool) -> None:
    """Verify linked OBPIs are complete and contain implementation evidence."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "audit-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    findings, complete = _collect_obpi_findings(project_root, obpi_files, expected_obpis, ledger)

    adr_dir = project_root / config.paths.adrs
    coverage = _compute_adr_coverage(project_root, adr_id, adr_dir)
    coverage_findings, coverage_blocking, coverage_advisory = _partition_coverage_findings(coverage)

    passed = not findings and not coverage_blocking

    result = {
        "adr": adr_id,
        "passed": passed,
        "checked_obpis": sorted(obpi_files.keys()),
        "complete_obpis": complete,
        "findings": findings,
        "coverage": coverage,
        "coverage_findings": coverage_findings,
        "coverage_blocking": coverage_blocking,
        "coverage_advisory": coverage_advisory,
    }

    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    else:
        _render_audit_check_result(
            adr_id,
            passed,
            findings,
            complete,
            coverage,
            coverage_blocking,
            coverage_advisory,
        )

    if not passed:
        raise SystemExit(1)


def adr_covers_check(adr: str, as_json: bool) -> None:
    """Verify @covers traceability for an ADR and its linked OBPIs."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "covers-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    (
        requirement_targets,
        criteria_without_req_ids,
        invalid_requirement_targets,
    ) = _collect_adr_requirement_targets(project_root, obpi_files)

    expected_targets = [adr_id, *sorted(expected_obpis), *requirement_targets]
    covers = _collect_covers_annotations(project_root)
    rows, missing = _build_covers_rows(adr_id, expected_targets, covers)

    referenced_targets = sorted(k for k in covers if k.startswith(("ADR-", "OBPI-", "REQ-")))
    unmatched_targets = sorted(k for k in referenced_targets if k not in expected_targets)
    passed = not missing and not criteria_without_req_ids and not invalid_requirement_targets

    result = {
        "adr": adr_id,
        "passed": passed,
        "expected_targets": expected_targets,
        "covered_targets": [row["target"] for row in rows if row["covered"]],
        "missing_targets": missing,
        "requirement_targets": requirement_targets,
        "criteria_without_req_ids": criteria_without_req_ids,
        "invalid_requirement_targets": invalid_requirement_targets,
        "rows": rows,
        "unmatched_targets": unmatched_targets,
    }

    if as_json:
        print(json.dumps(result, indent=2))  # noqa: T201
    else:
        _print_adr_covers_check_result(result)

    if not passed:
        raise SystemExit(1)


def _is_foundation_adr(adr_id: str) -> bool:
    """Return True when ADR ID is in the 0.0.x foundation series."""
    return re.match(r"^ADR-0\.0\.\d+(?:[.-].*)?$", adr_id) is not None


def _requires_security_review_attestation(
    brief_frontmatter: Mapping[str, Any] | None,
) -> bool:
    """Return True when a brief carries ``sensitivity: security`` (ADR-0.0.22).

    Third axis of the (kind × lane × sensitivity) attestation matrix. Operates
    on a parsed frontmatter mapping so call sites own parsing and unit tests
    can construct synthetic dicts. The schema currently enumerates only
    ``"security"`` for the ``sensitivity`` field; future values must declare
    their own attestation rule rather than silently inheriting this one.
    """
    if not isinstance(brief_frontmatter, Mapping):
        return False
    return brief_frontmatter.get("sensitivity") == "security"


def _requires_human_obpi_attestation(
    parent_adr: str | None,
    parent_lane: str,
    brief_frontmatter: Mapping[str, Any] | None = None,
) -> bool:
    """Return whether completed evidence must include human-attestation fields.

    Foundation ADRs (0.0.x) always require human attestation. For non-foundation
    ADRs, the parent lane sets the compliance floor -- a Lite OBPI under a Heavy
    ADR still requires attestation per AGENTS.md
    § Lane & Kind & Sensitivity Attestation Matrix. Briefs carrying
    ``sensitivity: security`` (ADR-0.0.22) require attestation regardless of
    lane or kind via :func:`_requires_security_review_attestation`. The
    ``brief_frontmatter`` argument is optional so ADR-level callers (which do
    not have per-brief frontmatter) can keep the two-argument call shape.
    """
    if not isinstance(parent_adr, str) or not parent_adr:
        return False
    if _is_foundation_adr(parent_adr):
        return True
    if parent_lane == "heavy":
        return True
    return _requires_security_review_attestation(brief_frontmatter)


# ---------------------------------------------------------------------------
# GHI #290 authenticity gate + GHI #292 agent-relayed escape path
# ---------------------------------------------------------------------------

_GHI_290_AUTHENTICITY_CONFIRMATION = "ATTEST"

ATTESTATION_TYPE_HUMAN = "human"
ATTESTATION_TYPE_AGENT_RELAYED = "agent-relayed-operator-attestation"


def _is_human_attestation_tty_available() -> bool:
    """Return True when stdin and stdout are both attached to a real TTY.

    Split out so tests can patch it. An agent subprocess without a controlling
    terminal returns False here, which is the desired enforcement path.
    """
    try:
        return bool(sys.stdin.isatty()) and bool(sys.stdout.isatty())
    except (ValueError, OSError):
        return False


def _active_pipeline_marker_exists(project_root: Path, obpi_id: str) -> bool:
    """Return True when a project-local pipeline marker exists for ``obpi_id``.

    The marker is ``.claude/plans/.pipeline-active-<obpi_id>.json``. Only an
    operator-initiated ``gz obpi pipeline`` run writes this file, so its
    presence is a strong proxy for operator co-presence that a fully-headless
    CI process cannot forge without also running the pipeline ceremony.
    """
    marker = project_root / ".claude" / "plans" / f".pipeline-active-{obpi_id}.json"
    return marker.is_file()


def _enforce_human_attestation_authenticity(
    *,
    obpi_id: str,
    parent_adr: str,
    attestor: str,
    attestation_text: str,
    attestor_present: bool = False,
    project_root: Path | None = None,
) -> str:
    """Enforce the GHI #290 authenticity gate and resolve the attestation path.

    The gate closes the vector that allowed a prior agent session to fabricate
    a ``human_attestation: true`` receipt for OBPI-0.0.20-03 on 2026-04-23.
    It has three branches (GHI #292 adds the third):

    1. **TTY path (``human``).** stdin AND stdout are attached to a real TTY.
       The operator reviews the echoed attestation payload and types the
       exact word ``ATTEST`` (uppercase, no quotes) to confirm. Returns
       :data:`ATTESTATION_TYPE_HUMAN`.
    2. **Agent-relayed path (``agent-relayed-operator-attestation``).** No
       TTY, but ``attestor_present=True`` AND an active pipeline marker
       exists at ``.claude/plans/.pipeline-active-<obpi_id>.json``. The
       marker is a co-presence proxy: only an operator-initiated
       ``gz obpi pipeline`` run writes it. Returns
       :data:`ATTESTATION_TYPE_AGENT_RELAYED` so the caller can record a
       taxonomically distinct ledger receipt.
    3. **Fail-closed.** No TTY and either ``attestor_present=False`` or no
       pipeline marker. Agent-synthesized attestation from a fully-headless
       context is prohibited per GHI #290; the function raises
       :class:`GzCliError`.

    Unit tests exercise the three paths by patching
    ``_is_human_attestation_tty_available``, ``_active_pipeline_marker_exists``,
    and ``input`` at the module level (see ``tests/test_obpi_complete_cmd.py``).
    Callers translate :class:`GzCliError` to their own exit-code contract
    (exit 3 for policy breach per ``.claude/rules/cli.md``).
    """
    if _is_human_attestation_tty_available():
        console.print("")
        console.print("[bold yellow]=== Human Attestation Required (GHI #290) ===[/bold yellow]")
        console.print(f"  OBPI:        {obpi_id}")
        console.print(f"  Parent ADR:  {parent_adr}")
        console.print(f"  Attestor:    {attestor}")
        console.print(f"  Attestation: {attestation_text}")
        console.print("")
        console.print(
            f"Type the word [bold]{_GHI_290_AUTHENTICITY_CONFIRMATION}[/bold] "
            "(uppercase, no quotes) to confirm you personally attest, "
            "or anything else to abort:"
        )
        try:
            response = input("> ").strip()
        except (EOFError, KeyboardInterrupt) as exc:
            msg = "Attestation aborted (no confirmation received)."
            raise GzCliError(msg) from exc

        if response != _GHI_290_AUTHENTICITY_CONFIRMATION:
            msg = (
                f"Attestation declined (expected "
                f"{_GHI_290_AUTHENTICITY_CONFIRMATION!r}, got {response!r})."
            )
            raise GzCliError(msg)
        return ATTESTATION_TYPE_HUMAN

    if attestor_present:
        if project_root is None:
            msg = (
                "--attestor-present requires project context to verify the "
                "pipeline marker; internal caller did not pass project_root."
            )
            raise GzCliError(msg)
        if not _active_pipeline_marker_exists(project_root, obpi_id):
            msg = (
                "--attestor-present requires an active pipeline marker at "
                f".claude/plans/.pipeline-active-{obpi_id}.json, but none was "
                f"found. Start the pipeline with 'uv run gz obpi pipeline "
                f"{obpi_id}' first, or re-run this command from an "
                "interactive shell and type the confirmation yourself."
            )
            raise GzCliError(msg)
        console.print("")
        console.print(
            "[bold yellow]=== Agent-Relayed Operator Attestation (GHI #292) ===[/bold yellow]"
        )
        console.print(f"  OBPI:        {obpi_id}")
        console.print(f"  Parent ADR:  {parent_adr}")
        console.print(f"  Attestor:    {attestor}")
        console.print(f"  Attestation: {attestation_text}")
        console.print(
            "  [dim]Co-presence proxy: active pipeline marker "
            f".claude/plans/.pipeline-active-{obpi_id}.json[/dim]"
        )
        return ATTESTATION_TYPE_AGENT_RELAYED

    msg = (
        "Human attestation required for this OBPI, but the process is not "
        "attached to an interactive terminal (stdin/stdout is not a TTY). "
        "Agent-synthesized attestation is prohibited per GHI #290. "
        "Re-run this command from an interactive shell and type the "
        "confirmation yourself, or pass --attestor-present from an active "
        "'gz obpi pipeline' session (GHI #292)."
    )
    raise GzCliError(msg)


def _validate_obpi_completed_required_fields(evidence: dict[str, Any]) -> None:
    """Validate baseline completed-receipt evidence fields."""
    required_fields = ("value_narrative", "key_proof")
    missing: list[str] = []
    for field in required_fields:
        value = evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(field)
    if missing:
        msg = f"Missing required completed-evidence field(s): {', '.join(sorted(missing))}."
        raise GzCliError(msg)


def _validate_obpi_human_attestation_fields(evidence: dict[str, Any], attestor: str) -> None:
    """Validate heavy/foundation human-attestation evidence contract.

    Reports all missing/invalid fields at once instead of one-at-a-time (GHI #80).
    """
    errors: list[str] = []
    placeholder_names = {"n/a", "tbd", "todo", "none", "-", "...", ""}
    if attestor.strip().lower() in placeholder_names:
        errors.append("--attestor must be a real name, not a placeholder.")
    if evidence.get("human_attestation") is not True:
        errors.append("evidence.human_attestation must be true.")

    attestation_text = evidence.get("attestation_text")
    if not isinstance(attestation_text, str) or not attestation_text.strip():
        errors.append("evidence.attestation_text must be a non-empty string.")

    attestation_date = evidence.get("attestation_date")
    if not isinstance(attestation_date, str) or not re.match(
        r"^\d{4}-\d{2}-\d{2}$", str(attestation_date)
    ):
        errors.append("evidence.attestation_date must be formatted as YYYY-MM-DD.")
    elif attestation_date:
        try:
            date.fromisoformat(attestation_date)
        except ValueError:
            errors.append("evidence.attestation_date must be a valid YYYY-MM-DD date.")

    if errors:
        joined = " ".join(errors)
        msg = f"Heavy/Foundation OBPI completion: {joined}"
        raise GzCliError(msg)


def _validate_explicit_req_proof_inputs(raw_inputs: Any) -> list[dict[str, str]]:
    """Validate an explicit req_proof_inputs payload when supplied."""
    if raw_inputs is None:
        return []
    if not isinstance(raw_inputs, list) or not raw_inputs:
        msg = "evidence.req_proof_inputs must be a non-empty list of proof input objects."
        raise GzCliError(msg)

    normalized = normalize_req_proof_inputs(raw_inputs)
    if len(normalized) != len(raw_inputs):
        msg = (
            "Each evidence.req_proof_inputs item must include non-empty "
            "name/kind/source fields and status present|missing."
        )
        raise GzCliError(msg)
    return normalized


def _validate_obpi_completion_evidence(
    *,
    project_root: Path,
    obpi_content: str,
    evidence: dict[str, Any] | None,
    parent_adr: str | None,
    parent_lane: str,
    attestor: str,
) -> tuple[dict[str, Any], str, EventAnchor | None]:
    """Validate and normalize evidence for OBPI completed receipts."""
    if evidence is None:
        msg = "OBPI completed receipts require --evidence-json with value_narrative and key_proof."
        raise GzCliError(msg)

    _validate_obpi_completed_required_fields(evidence)
    requires_human_attestation = _requires_human_obpi_attestation(parent_adr, parent_lane)

    if requires_human_attestation:
        _validate_obpi_human_attestation_fields(evidence, attestor)

    completion_term = "attested_completed" if requires_human_attestation else "completed"
    normalized = dict(evidence)
    explicit_req_proof_inputs = _validate_explicit_req_proof_inputs(
        normalized.get("req_proof_inputs")
    )
    human_attestation = None
    if normalized.get("human_attestation") is True:
        human_attestation = {
            "valid": True,
            "attestor": attestor,
            "attestation_text": normalized.get("attestation_text"),
            "date": normalized.get("attestation_date"),
        }
    normalized["req_proof_inputs"] = explicit_req_proof_inputs or normalize_req_proof_inputs(
        None,
        fallback_key_proof=cast(str, normalized.get("key_proof")),
        human_attestation=human_attestation,
    )
    normalized["obpi_completion"] = completion_term
    normalized["attestation_requirement"] = "required" if requires_human_attestation else "optional"
    if isinstance(parent_adr, str) and parent_adr:
        normalized["parent_adr"] = parent_adr
    normalized["parent_lane"] = parent_lane
    explicit_scope_audit = normalized.get("scope_audit")
    scope_audit = normalize_scope_audit(explicit_scope_audit)
    if explicit_scope_audit is not None and scope_audit is None:
        msg = (
            "evidence.scope_audit must be an object with allowlist, changed_files, "
            "and out_of_scope_files string arrays."
        )
        raise GzCliError(msg)

    explicit_git_sync_state = normalized.get("git_sync_state")
    git_sync_state = normalize_git_sync_state(explicit_git_sync_state)
    if explicit_git_sync_state is not None and git_sync_state is None:
        msg = (
            "evidence.git_sync_state must include branch/remote/head/remote_head, "
            "dirty/diverged booleans, ahead/behind integers, and action/warning/blocker arrays."
        )
        raise GzCliError(msg)

    enriched_evidence, anchor = enrich_completed_receipt_evidence(
        project_root=project_root,
        content=obpi_content,
        base_evidence=normalized,
        parent_adr=parent_adr,
        recorder_source="cli:obpi_emit_receipt",
        scope_audit=scope_audit,
        git_sync_state=git_sync_state,
    )
    return enriched_evidence, completion_term, anchor


def adr_emit_receipt_cmd(
    adr: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
    attestor_present: bool = False,
) -> None:
    """Emit an ADR audit receipt event anchored in the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "issued receipts")

    evidence: dict[str, Any] | None = None
    if evidence_json:
        try:
            parsed = json.loads(evidence_json)
        except json.JSONDecodeError as exc:
            msg = f"Invalid --evidence-json: {exc}"
            raise GzCliError(msg) from exc
        if not isinstance(parsed, dict):
            msg = "--evidence-json must decode to a JSON object"
            raise GzCliError(msg)
        evidence = parsed

    anchor = capture_validation_anchor(project_root, adr_id)
    event = audit_receipt_emitted_event(
        adr_id=adr_id,
        receipt_event=receipt_event,
        attestor=attestor,
        evidence=evidence,
        anchor=anchor,
    )

    # GHI #290 authenticity gate: ADR-level human-attestation receipt events
    # (validated / attested / accepted) are the Gate 5 attestation surface.
    # Without a TTY gate, an agent could synthesize a validated ADR closeout
    # the same way OBPI-0.0.20-03 was fabricated. GHI #292 adds
    # --attestor-present as an agent-relayed escape path; the resolved
    # attestation_type is written into the evidence dict so the ledger receipt
    # records which gate path fired. Skipped for --dry-run.
    if not dry_run and _is_human_attestation_receipt_event(receipt_event):
        attestation_text = ""
        if isinstance(evidence, dict):
            candidate = evidence.get("attestation_text") or evidence.get("scope")
            if isinstance(candidate, str):
                attestation_text = candidate
        attestation_type = _enforce_human_attestation_authenticity(
            obpi_id=adr_id,
            parent_adr=adr_id,
            attestor=attestor,
            attestation_text=attestation_text or f"{receipt_event} {adr_id}",
            attestor_present=attestor_present,
            project_root=project_root,
        )
        if isinstance(evidence, dict):
            evidence["attestation_type"] = attestation_type

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        if _is_human_attestation_receipt_event(receipt_event):
            console.print(
                "[yellow]Gate (GHI #290):[/yellow] live run would require "
                "interactive TTY + 'ATTEST' confirmation."
            )
        return

    ledger.append(event)
    console.print("[green]Audit receipt emitted.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Event: {receipt_event}")
    console.print(f"  Attestor: {attestor}")


_HUMAN_ATTESTATION_RECEIPT_EVENTS = frozenset({"validated", "attested", "accepted"})


def _is_human_attestation_receipt_event(receipt_event: str) -> bool:
    """Return True for ADR receipt events that represent a human attestation.

    Keeps the gate scoped: ``emitted``, ``corrected``, ``superseded``, and
    other informational events remain headless-safe; Gate 5 attestation
    events require the authenticity check.
    """
    return receipt_event.strip().lower() in _HUMAN_ATTESTATION_RECEIPT_EVENTS


def _adr_audit_marker_path(project_root: Path, adr_id: str) -> Path:
    """Return the per-ADR audit-ceremony marker path."""
    return project_root / ".claude" / "plans" / f".pipeline-active-{adr_id}.json"


def adr_audit_begin_cmd(adr: str) -> None:
    """Open an ADR audit ceremony — write the co-presence marker.

    The marker is the same shape ``gz obpi pipeline`` writes for OBPI
    ceremonies; ``_active_pipeline_marker_exists`` (GHI #292) accepts it
    as proof that an operator-typed CLI entry-point opened the ceremony.
    The skill ``/gz-adr-audit`` calls this verb at the start of Step 8 so
    the agent-relayed Gate-5 emit can pass the authenticity gate without
    fabricating the marker by hand.

    Idempotent: a re-invocation refreshes ``updated_at`` and rewrites the
    payload; the marker exists at most once per ADR.
    """
    from datetime import UTC, datetime

    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "opened audit ceremonies")

    marker_path = _adr_audit_marker_path(project_root, adr_id)
    marker_path.parent.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")
    payload: dict[str, Any] = {
        "obpi_id": adr_id,
        "parent_adr": adr_id,
        "lane": "audit",
        "entry": "audit",
        "execution_mode": "audit",
        "current_stage": "audit",
        "started_at": timestamp,
        "updated_at": timestamp,
        "receipt_state": "audit-active",
        "blockers": [],
        "required_human_action": (
            "Operator verbal attestation expected at Gate-5 emit; agent relays."
        ),
        "next_command": f"uv run gz adr emit-receipt {adr_id} --event validated --attestor-present",
        "resume_point": "emit-receipt",
    }
    marker_path.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
    console.print("[green]ADR audit ceremony opened.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Marker: {marker_path}")


def adr_audit_end_cmd(adr: str) -> None:
    """Close an ADR audit ceremony — remove the co-presence marker.

    Called by the ``/gz-adr-audit`` skill after a successful Gate-5
    emit. Marker hygiene matters: leaving the marker behind would make
    a second agent-relayed emit succeed without a fresh operator
    invocation, defeating the co-presence proof. Missing-marker is a
    soft warning, not an error — closing an already-closed ceremony
    is idempotent.
    """
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)

    marker_path = _adr_audit_marker_path(project_root, adr_id)
    if marker_path.is_file():
        marker_path.unlink()
        console.print("[green]ADR audit ceremony closed.[/green]")
        console.print(f"  ADR: {adr_id}")
        console.print(f"  Marker removed: {marker_path}")
    else:
        console.print("[yellow]No active ADR audit marker to close.[/yellow]")
        console.print(f"  ADR: {adr_id}")
        console.print(f"  Expected: {marker_path}")
