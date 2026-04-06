"""Atomic OBPI completion command.

``gz obpi complete`` validates, writes evidence, flips status, records
attestation, and emits a completion receipt in a single all-or-nothing
transaction.  If any step fails, no files or ledger entries are modified.
"""

from __future__ import annotations

import json
import re
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from gzkit.commands.adr_audit import _requires_human_obpi_attestation
from gzkit.commands.closeout_form import _upsert_frontmatter_value
from gzkit.commands.common import (
    _is_pool_adr_id,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_obpi_file,
)
from gzkit.hooks.obpi import section_body
from gzkit.ledger import Ledger, parse_frontmatter_value, resolve_adr_lane

# section_body is used in _has_human_attestation_content for H2 section extraction
from gzkit.ledger_events import obpi_receipt_emitted_event
from gzkit.utils import capture_validation_anchor


def _resolve_and_validate(
    project_root: Path,
    config: Any,
    ledger: Ledger,
    obpi: str,
    as_json: bool,
) -> tuple[Path, str, str, str, str, bool]:
    """Resolve OBPI file and validate preconditions.

    Returns (obpi_file, obpi_id, original_content, resolved_parent, parent_lane,
    requires_human).
    """
    obpi_file, obpi_id = resolve_obpi_file(project_root, config, ledger, obpi)
    if not obpi_file.exists():
        _fail(f"Brief not found: {obpi_file}", exit_code=1, as_json=as_json, obpi_id=obpi_id)

    original_content = obpi_file.read_text(encoding="utf-8")
    current_status = (parse_frontmatter_value(original_content, "status") or "").strip().lower()
    if current_status == "completed":
        _fail("Brief is already Completed.", exit_code=1, as_json=as_json, obpi_id=obpi_id)

    graph = ledger.get_artifact_graph()
    obpi_info = graph.get(obpi_id, {})
    if obpi_info.get("type") != "obpi":
        _fail(f"OBPI not found in ledger: {obpi_id}", exit_code=1, as_json=as_json, obpi_id=obpi_id)
    if obpi_info.get("ledger_completed"):
        _fail(
            "OBPI is already completed in the ledger.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    parent_adr = cast(str | None, obpi_info.get("parent"))
    if not parent_adr:
        _fail(
            "OBPI is missing parent ADR in ledger.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    assert parent_adr is not None  # narrowing: _fail raises SystemExit
    if _is_pool_adr_id(parent_adr):
        _fail(
            f"Pool-linked OBPI cannot be completed: {obpi_id}",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    _adr_file, resolved_parent = resolve_adr_file(project_root, config, parent_adr)
    parent_lane = resolve_adr_lane(graph.get(resolved_parent, {}), config.mode)
    requires_human = _requires_human_obpi_attestation(resolved_parent, parent_lane)
    return obpi_file, obpi_id, original_content, resolved_parent, parent_lane, requires_human


def _resolve_evidence(
    original_content: str,
    implementation_summary: str | None,
    key_proof: str | None,
    obpi_id: str,
    as_json: bool,
) -> tuple[str, str]:
    """Resolve evidence from flags or existing brief content.

    Returns (effective_summary, effective_proof).
    """
    effective_summary = implementation_summary or _read_existing_summary(original_content)
    effective_proof = key_proof or _read_existing_key_proof(original_content)

    if not effective_summary or not effective_summary.strip():
        _fail(
            "Implementation summary is required. Provide --implementation-summary "
            "or ensure the brief has a substantive ### Implementation Summary section.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    assert effective_summary is not None  # narrowing: _fail raises SystemExit
    if not effective_proof or not effective_proof.strip():
        _fail(
            "Key proof is required. Provide --key-proof "
            "or ensure the brief has a substantive ### Key Proof section.",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )
    assert effective_proof is not None  # narrowing: _fail raises SystemExit
    return effective_summary, effective_proof


def obpi_complete_cmd(
    obpi: str,
    attestor: str,
    attestation_text: str,
    implementation_summary: str | None,
    key_proof: str | None,
    as_json: bool,
    dry_run: bool,
) -> None:
    """Atomically complete an OBPI: validate, write evidence, flip status, emit receipt."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    # 1. Resolve & validate
    obpi_file, obpi_id, original_content, resolved_parent, parent_lane, requires_human = (
        _resolve_and_validate(project_root, config, ledger, obpi, as_json)
    )

    # 2. Resolve evidence
    effective_summary, effective_proof = _resolve_evidence(
        original_content,
        implementation_summary,
        key_proof,
        obpi_id,
        as_json,
    )

    # 3. Build would-be brief content
    today = datetime.now(UTC).strftime("%Y-%m-%d")
    new_content = _build_completed_brief(
        content=original_content,
        attestor=attestor,
        attestation_text=attestation_text,
        implementation_summary=effective_summary,
        key_proof=effective_proof,
        date_completed=today,
    )

    # 4. Validate would-be content
    validation_errors = _validate_would_be_content(new_content, requires_human)
    if validation_errors:
        errors_text = "; ".join(validation_errors)
        _fail(
            f"Brief content validation failed: {errors_text}",
            exit_code=1,
            as_json=as_json,
            obpi_id=obpi_id,
        )

    # 5. Build audit ledger entry and receipt event
    adr_dir = obpi_file.parent.parent
    audit_entry = _build_attestation_audit_entry(
        obpi_id=obpi_id,
        adr_id=resolved_parent,
        attestor=attestor,
        attestation_text=attestation_text,
        date=today,
        requires_human=requires_human,
    )
    completion_term = "attested_completed" if requires_human else "completed"
    anchor = capture_validation_anchor(project_root, resolved_parent)
    evidence: dict[str, Any] = {
        "value_narrative": effective_summary[:500],
        "key_proof": effective_proof[:500],
        "parent_adr": resolved_parent,
        "parent_lane": parent_lane,
        "obpi_completion": completion_term,
        "attestation_requirement": "required" if requires_human else "optional",
    }
    if requires_human:
        evidence["human_attestation"] = True
        evidence["attestation_text"] = attestation_text
        evidence["attestation_date"] = today

    receipt_event = obpi_receipt_emitted_event(
        obpi_id=obpi_id,
        receipt_event="completed",
        attestor=attestor,
        evidence=evidence,
        parent_adr=resolved_parent,
        obpi_completion=completion_term,
        anchor=anchor,
    )

    # Dry run
    if dry_run:
        _print_dry_run(
            obpi_id,
            resolved_parent,
            parent_lane,
            requires_human,
            completion_term,
            attestor,
            audit_entry,
            receipt_event,
            as_json,
        )
        return

    # 6-8. Execute atomic transaction
    try:
        _execute_transaction(
            obpi_file=obpi_file,
            original_content=original_content,
            new_content=new_content,
            adr_dir=adr_dir,
            audit_entry=audit_entry,
            ledger=ledger,
            receipt_event=receipt_event,
        )
    except OSError as exc:
        _fail(f"I/O error during completion: {exc}", exit_code=2, as_json=as_json, obpi_id=obpi_id)

    # Success output
    _print_success(obpi_id, resolved_parent, parent_lane, completion_term, attestor, as_json)


def _print_dry_run(
    obpi_id: str,
    resolved_parent: str,
    parent_lane: str,
    requires_human: bool,
    completion_term: str,
    attestor: str,
    audit_entry: dict[str, Any],
    receipt_event: Any,
    as_json: bool,
) -> None:
    """Print dry-run plan."""
    if as_json:
        print(
            json.dumps(
                {
                    "status": "dry_run",
                    "obpi_id": obpi_id,
                    "parent_adr": resolved_parent,
                    "lane": parent_lane,
                    "requires_human_attestation": requires_human,
                    "completion_term": completion_term,
                    "attestor": attestor,
                    "audit_entry": audit_entry,
                    "receipt_event": receipt_event.model_dump(),
                }
            )
        )
    else:
        console.print("[yellow]Dry run:[/yellow] no files will be written.")
        console.print(f"  OBPI: {obpi_id}")
        console.print(f"  Parent ADR: {resolved_parent}")
        console.print(f"  Lane: {parent_lane}")
        console.print(f"  Attestor: {attestor}")
        console.print(f"  Completion: {completion_term}")


def _print_success(
    obpi_id: str,
    resolved_parent: str,
    parent_lane: str,
    completion_term: str,
    attestor: str,
    as_json: bool,
) -> None:
    """Print success output."""
    if as_json:
        print(
            json.dumps(
                {
                    "status": "completed",
                    "obpi_id": obpi_id,
                    "parent_adr": resolved_parent,
                    "completion_term": completion_term,
                    "attestor": attestor,
                }
            )
        )
    else:
        console.print(f"[green]Completed:[/green] {obpi_id}")
        console.print(f"  Parent ADR: {resolved_parent}")
        console.print(f"  Lane: {parent_lane}")
        console.print(f"  Attestor: {attestor}")
        console.print(f"  Completion: {completion_term}")


# ---------------------------------------------------------------------------
# Transaction execution with rollback
# ---------------------------------------------------------------------------


def _execute_transaction(
    *,
    obpi_file: Path,
    original_content: str,
    new_content: str,
    adr_dir: Path,
    audit_entry: dict[str, Any],
    ledger: Ledger,
    receipt_event: Any,
) -> None:
    """Execute the three-phase write with rollback on failure.

    Order: audit ledger -> brief file -> main ledger.
    The audit ledger must be written first because the obpi-completion-validator
    hook checks it before allowing the brief status change.
    """
    audit_ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"
    audit_written = False

    try:
        # Phase 1: Write attestation to ADR-local audit ledger
        _append_audit_ledger(adr_dir, audit_entry)
        audit_written = True

        # Phase 2: Write brief file (single atomic write)
        obpi_file.write_text(new_content, encoding="utf-8")

        # Phase 3: Emit receipt to main ledger
        ledger.append(receipt_event)

    except Exception:
        # Rollback: restore brief if it was changed
        if obpi_file.read_text(encoding="utf-8") != original_content:
            obpi_file.write_text(original_content, encoding="utf-8")

        # Rollback: remove audit ledger entry if it was written
        if audit_written:
            _rollback_audit_ledger(audit_ledger_file)

        raise


# ---------------------------------------------------------------------------
# Brief content builders
# ---------------------------------------------------------------------------


def _extract_h3_body(content: str, heading: str) -> str | None:
    """Extract the body of an H3 section with correct H2/H3 boundaries."""
    pattern = (
        rf"^### {re.escape(heading)}\s*$"
        rf"([\s\S]*?)"
        rf"(?=^#{{2,3}} |\n---|\Z)"
    )
    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        return None
    body = match.group(1).strip()
    return body if body else None


def _read_existing_summary(content: str) -> str | None:
    """Read existing Implementation Summary from the brief."""
    body = _extract_h3_body(content, "Implementation Summary")
    if body is None:
        return None
    # Check if it's just template placeholders
    lines = [line.strip() for line in body.splitlines() if line.strip() and line.strip() != "-"]
    substantive = [line for line in lines if not _is_placeholder(line)]
    return body if substantive else None


def _read_existing_key_proof(content: str) -> str | None:
    """Read existing Key Proof from the brief."""
    body = _extract_h3_body(content, "Key Proof")
    if body is None:
        return None
    if _is_placeholder(body):
        return None
    return body


_PLACEHOLDERS = {
    "tbd",
    "todo",
    "...",
    "none",
    "(none)",
    "-",
    "n/a",
    "paste test output here",
    "paste lint/format/type check output here",
    "one-sentence concrete outcome",
    "<name>",
}


def _is_placeholder(text: str) -> bool:
    """Return True if text is a non-substantive placeholder."""
    clean = text.strip().lower()
    if not clean:
        return True
    if clean in _PLACEHOLDERS:
        return True
    # Template bullet patterns: full-line "- Label:" or extracted label "Label:"
    if re.match(r"^-\s+\w[^:]*:\s*$", clean):
        return True
    # Label-only text ending in colon with no value (from bullet value extraction)
    if re.match(r"^[\w][\w\s/]*:\s*$", clean):
        return True
    # HTML comments are placeholders
    return clean.startswith("<!--") and clean.endswith("-->")


def _build_completed_brief(
    *,
    content: str,
    attestor: str,
    attestation_text: str,
    implementation_summary: str,
    key_proof: str,
    date_completed: str,
) -> str:
    """Build the full completed brief content with all sections updated."""
    # 1. Update frontmatter status
    result = _upsert_frontmatter_value(content, "status", "Completed")

    # 2. Replace ### Implementation Summary section
    result = _replace_h3_section(
        result,
        "Implementation Summary",
        implementation_summary,
    )

    # 3. Replace ### Key Proof section
    result = _replace_h3_section(result, "Key Proof", key_proof)

    # 4. Update ## Human Attestation section
    result = _update_human_attestation(result, attestor, attestation_text, date_completed)

    # 5. Update **Brief Status:** line
    result = re.sub(
        r"\*\*Brief Status:\*\*\s*\S+",
        "**Brief Status:** Completed",
        result,
    )

    # 6. Update **Date Completed:** line
    result = re.sub(
        r"\*\*Date Completed:\*\*\s*\S+",
        f"**Date Completed:** {date_completed}",
        result,
    )

    return result


def _replace_h3_section(content: str, heading: str, new_body: str) -> str:
    """Replace the body of an H3 section, preserving the heading.

    Stops at the next H2 or H3 heading, a horizontal rule (---), or EOF.
    """
    pattern = (
        rf"(^### {re.escape(heading)}\s*$)"
        rf"([\s\S]*?)"
        rf"(?=^#{{2,3}} |\n---|\Z)"
    )
    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        return content

    replacement = f"{match.group(1)}\n\n{new_body.strip()}\n\n"
    return content[: match.start()] + replacement + content[match.end() :]


def _update_human_attestation(content: str, attestor: str, attestation_text: str, date: str) -> str:
    """Update the Human Attestation section values."""
    result = re.sub(
        r"(^- Attestor:\s*).*$",
        rf"\g<1>`{attestor}`",
        content,
        count=1,
        flags=re.MULTILINE,
    )
    result = re.sub(
        r"(^- Attestation:\s*).*$",
        rf"\g<1>{attestation_text}",
        result,
        count=1,
        flags=re.MULTILINE,
    )
    result = re.sub(
        r"(^- Date:\s*).*$",
        rf"\g<1>{date}",
        result,
        count=1,
        flags=re.MULTILINE,
    )
    return result


# ---------------------------------------------------------------------------
# Validation
# ---------------------------------------------------------------------------


def _validate_would_be_content(content: str, requires_human: bool) -> list[str]:
    """Validate the would-be brief content matches completion requirements.

    Mirrors the checks in obpi-completion-validator.py hook.
    """
    errors: list[str] = []

    if not _has_substantive_implementation_summary(content):
        errors.append("Missing or non-substantive Implementation Summary")

    if not _has_substantive_key_proof(content):
        errors.append("Missing or non-substantive Key Proof")

    if requires_human and not _has_human_attestation_content(content):
        errors.append("Missing human attestation content")

    return errors


def _has_substantive_implementation_summary(content: str) -> bool:
    """Check for substantive Implementation Summary (mirrors hook check)."""
    match = re.search(
        r"^### Implementation Summary\s*$([\s\S]*?)(?:^#{2,3} |\n---|\Z)",
        content,
        flags=re.MULTILINE,
    )
    if not match:
        return False
    section = match.group(1)
    # Primary: "- Key: value" bullets with actual content after the colon
    bullets = re.findall(r"^- [^:\n]+:[ \t]*(.+)$", section, flags=re.MULTILINE)
    if not bullets:
        # Fallback: plain "- text" bullets
        bullets = re.findall(r"^- \s*(.+)$", section, flags=re.MULTILINE)
    return any(not _is_placeholder(b) for b in bullets)


def _has_substantive_key_proof(content: str) -> bool:
    """Check for substantive Key Proof (mirrors hook check)."""
    for heading in ("Key Proof", "Verification", "Gate Evidence"):
        match = re.search(
            rf"^### {re.escape(heading)}\s*$([\s\S]*?)(?:^#{{2,3}} |\n---|\Z)",
            content,
            flags=re.MULTILINE,
        )
        if match:
            body = match.group(1).strip()
            if body and not _is_placeholder(body):
                return True
    return False


def _has_human_attestation_content(content: str) -> bool:
    """Check for substantive Human Attestation section."""
    body = section_body(content, "Human Attestation")
    if body is None:
        return False
    attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
    if not attestor_match:
        return False
    attestor_val = attestor_match.group(1).strip().strip("`")
    return bool(attestor_val) and attestor_val.lower() not in _PLACEHOLDERS


# ---------------------------------------------------------------------------
# Audit ledger operations
# ---------------------------------------------------------------------------


def _build_attestation_audit_entry(
    *,
    obpi_id: str,
    adr_id: str,
    attestor: str,
    attestation_text: str,
    date: str,
    requires_human: bool,
) -> dict[str, Any]:
    """Build the ADR-local audit ledger entry for attestation."""
    entry: dict[str, Any] = {
        "type": "obpi-audit",
        "timestamp": datetime.now(UTC).isoformat(),
        "obpi_id": obpi_id,
        "adr_id": adr_id,
        "attestation_type": "human" if requires_human else "self-close-exception",
        "evidence": {
            "human_attestation": requires_human,
            "attestation_text": attestation_text,
            "attestation_date": date,
        },
        "action_taken": "attestation_recorded",
        "agent": "cli:obpi-complete",
    }
    return entry


def _append_audit_ledger(adr_dir: Path, entry: dict[str, Any]) -> None:
    """Append an entry to the ADR-local JSONL audit ledger."""
    logs_dir = adr_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ledger_file = logs_dir / "obpi-audit.jsonl"
    with ledger_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def _rollback_audit_ledger(ledger_file: Path) -> None:
    """Remove the last line from the audit ledger (rollback the last append)."""
    if not ledger_file.exists():
        return
    lines = ledger_file.read_text(encoding="utf-8").splitlines()
    if lines:
        ledger_file.write_text("\n".join(lines[:-1]) + "\n" if lines[:-1] else "", encoding="utf-8")


# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------


def _fail(msg: str, *, exit_code: int, as_json: bool, obpi_id: str) -> None:
    """Report an error and exit.

    Always raises SystemExit; never returns normally.
    """
    if as_json:
        print(json.dumps({"status": "error", "obpi_id": obpi_id, "error": msg}))
    else:
        console.print(f"[red]Error:[/red] {msg}")
    raise SystemExit(exit_code)
