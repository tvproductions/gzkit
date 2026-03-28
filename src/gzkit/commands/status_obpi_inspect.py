"""OBPI brief inspection and parsing helpers for the status subsystem."""

import re
from pathlib import Path
from typing import Any

from gzkit.ledger import (
    derive_obpi_semantics,
    parse_frontmatter_value,
)

# ---------------------------------------------------------------------------
# Markdown parsing helpers
# ---------------------------------------------------------------------------


def _markdown_label_value(content: str, label: str) -> str | None:
    pattern = rf"^\*\*{re.escape(label)}:\*\*\s*(.+)$"
    match = re.search(pattern, content, flags=re.MULTILINE)
    if not match:
        return None
    return match.group(1).strip()


def _section_body(content: str, heading: str) -> str | None:
    lines = content.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        if line.strip() in {f"## {heading}", f"### {heading}"}:
            start_index = index + 1
            break

    if start_index is None:
        return None

    end_index = len(lines)
    for index in range(start_index, len(lines)):
        stripped = lines[index].strip()
        if stripped == "---" or re.match(r"^(##|###) ", stripped):
            end_index = index
            break

    body = "\n".join(lines[start_index:end_index]).strip()
    if body:
        return body
    return None


def _section_body_with_prefix(content: str, heading_prefix: str) -> str | None:
    lines = content.splitlines()
    start_index: int | None = None

    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith(f"## {heading_prefix}") or stripped.startswith(
            f"### {heading_prefix}"
        ):
            start_index = index + 1
            break

    if start_index is None:
        return None

    end_index = len(lines)
    for index in range(start_index, len(lines)):
        stripped = lines[index].strip()
        if stripped == "---" or re.match(r"^(##|###) ", stripped):
            end_index = index
            break

    body = "\n".join(lines[start_index:end_index]).strip()
    if body:
        return body
    return None


def _has_substantive_section(content: str, heading: str) -> bool:
    body = _section_body(content, heading)
    if not body:
        return False
    normalized = body.strip().lower()
    return normalized not in {"", "-", "...", "tbd", "(none)", "n/a", "paste test output here"}


def _has_substantive_body(body: str | None) -> bool:
    if not body:
        return False
    normalized = body.strip().lower()
    return normalized not in {"", "-", "...", "tbd", "(none)", "n/a", "paste test output here"}


def _has_substantive_implementation_summary(content: str) -> bool:
    match = re.search(
        r"^### Implementation Summary\s*$([\s\S]*?)(?:^### |\n---|\Z)",
        content,
        flags=re.MULTILINE,
    )
    if not match:
        return False

    section = match.group(1)
    # Keep matching line-local so empty values cannot borrow content from the next line.
    bullet_matches = re.findall(r"^- [^:\n]+:[ \t]*(.+)$", section, flags=re.MULTILINE)
    for value in bullet_matches:
        normalized = value.strip().lower()
        if normalized and normalized not in {"-", "tbd", "(none)", "n/a"}:
            return True
    return False


def _implementation_summary_validation_commands(content: str) -> str | None:
    body = _section_body(content, "Implementation Summary")
    if not body:
        return None

    lines = body.splitlines()
    for index, line in enumerate(lines):
        if not line.startswith("- Validation commands run:"):
            continue

        collected = [line.removeprefix("- Validation commands run:").strip()]
        for follow_line in lines[index + 1 :]:
            if follow_line.startswith("- "):
                break
            collected.append(follow_line.rstrip())

        candidate = "\n".join(part for part in collected if part.strip()).strip()
        if _has_substantive_body(candidate):
            return candidate
    return None


def _resolved_key_proof_body(content: str) -> str | None:
    for heading in ("Key Proof", "Verification", "Gate Evidence"):
        body = _section_body(content, heading)
        if body and _has_substantive_section(content, heading):
            return body
    prefixed_verification = _section_body_with_prefix(content, "Verification")
    if _has_substantive_body(prefixed_verification):
        return prefixed_verification
    validation_commands = _implementation_summary_validation_commands(content)
    if _has_substantive_body(validation_commands):
        return validation_commands
    return None


# ---------------------------------------------------------------------------
# Human attestation & tracked defects
# ---------------------------------------------------------------------------


def _extract_human_attestation(content: str) -> dict[str, Any]:
    body = _section_body(content, "Human Attestation")
    if not body:
        return {"present": False, "valid": False}

    attestor_match = re.search(r"^- Attestor:\s*(.+)$", body, flags=re.MULTILINE)
    attestation_match = re.search(r"^- Attestation:\s*(.+)$", body, flags=re.MULTILINE)
    date_match = re.search(r"^- Date:\s*`?(\d{4}-\d{2}-\d{2})`?$", body, flags=re.MULTILINE)

    attestor_raw = attestor_match.group(1).strip() if attestor_match else None
    # Strip markdown backticks and trailing annotations (e.g. "--- required ...")
    attestor = (
        attestor_raw.strip("`").split("\u2014")[0].split(" \u2014 ")[0].strip()
        if attestor_raw
        else None
    )
    attestation_text = attestation_match.group(1).strip() if attestation_match else None
    attestation_date = date_match.group(1).strip() if date_match else None
    placeholder_names = {"n/a", "tbd", "todo", "none", "-", "...", ""}
    valid = bool(
        attestor
        and attestor.lower() not in placeholder_names
        and attestation_text
        and attestation_date
    )
    return {
        "present": True,
        "valid": valid,
        "attestor": attestor,
        "attestation_text": attestation_text,
        "date": attestation_date,
    }


def _extract_tracked_defects(content: str) -> list[dict[str, Any]]:
    """Parse brief-local tracked GitHub defects from a dedicated section."""
    body = _section_body(content, "Tracked Defects")
    if not body:
        return []

    defects: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    for line in body.splitlines():
        stripped = line.strip()
        if not stripped.startswith("- "):
            continue

        candidate = stripped[2:].strip()
        if candidate.startswith(("[ ] ", "[x] ", "[X] ")):
            candidate = candidate[4:].strip()
        candidate = re.sub(r"^\[(?P<label>[^\]]+)\]\([^)]+\)", r"\g<label>", candidate)
        candidate = re.sub(
            r"^https?://github\.com/[^/]+/[^/]+/issues/(?P<number>\d+)",
            r"#\g<number>",
            candidate,
        )

        match = re.search(r"(?P<prefix>GHI-|#)(?P<number>\d+)", candidate, flags=re.IGNORECASE)
        if not match:
            continue

        issue_id = f"GHI-{int(match.group('number'))}"
        if issue_id in seen_ids:
            continue

        state_match = re.search(r"\((open|closed)\)", candidate, flags=re.IGNORECASE)
        state = state_match.group(1).lower() if state_match else "unknown"
        summary_match = re.match(
            r".*?(?:GHI-|#)\d+(?:\s*\((?:open|closed)\))?\s*(?::|-)\s*(?P<summary>.+)$",
            candidate,
            flags=re.IGNORECASE,
        )
        summary = summary_match.group("summary").strip() if summary_match else None
        defects.append(
            {
                "id": issue_id,
                "number": int(match.group("number")),
                "state": state,
                "summary": summary,
            }
        )
        seen_ids.add(issue_id)
    return defects


def _tracked_defect_refs(tracked_defects: list[dict[str, Any]]) -> str:
    """Render one compact tracked-defect reference list."""
    refs: list[str] = []
    for defect in tracked_defects:
        issue_id = str(defect.get("id", "")).strip()
        if not issue_id:
            continue
        state = str(defect.get("state", "")).strip().lower()
        refs.append(f"{issue_id} ({state})" if state and state != "unknown" else issue_id)
    return ", ".join(refs)


def _issue_details(issues: list[str], tracked_defects: list[dict[str, Any]]) -> list[str]:
    """Attach brief-local defect linkage to human-facing issue strings."""
    refs = _tracked_defect_refs(tracked_defects)
    if not refs:
        return list(issues)
    return [f"{issue} [tracked defects: {refs}]" for issue in issues]


# ---------------------------------------------------------------------------
# OBPI brief inspection
# ---------------------------------------------------------------------------


def _inspect_obpi_brief(
    project_root: Path,
    obpi_file: Path,
    obpi_id: str | None = None,
    graph: dict[str, Any] | None = None,
) -> dict[str, Any]:
    content = obpi_file.read_text(encoding="utf-8")
    frontmatter_status = (parse_frontmatter_value(content, "status") or "").strip().lower()
    brief_status = (_markdown_label_value(content, "Brief Status") or "").strip().lower()
    file_completed = frontmatter_status == "completed" or brief_status == "completed"
    implementation_evidence_ok = _has_substantive_implementation_summary(content)
    key_proof_body = _resolved_key_proof_body(content)
    key_proof_ok = key_proof_body is not None
    human_attestation = _extract_human_attestation(content)
    tracked_defects = _extract_tracked_defects(content)
    info = graph.get(obpi_id, {}) if obpi_id and graph else {}
    semantics = derive_obpi_semantics(
        info,
        obpi_id=obpi_id,
        artifact_graph=graph,
        found_file=True,
        file_completed=file_completed,
        implementation_evidence_ok=implementation_evidence_ok,
        key_proof_ok=key_proof_ok,
        fallback_key_proof=key_proof_body,
        human_attestation=human_attestation,
        project_root=project_root,
    )

    return {
        "file_completed": file_completed,
        "implementation_evidence_ok": implementation_evidence_ok,
        "key_proof_ok": key_proof_ok,
        "human_attestation": human_attestation,
        "frontmatter_status": frontmatter_status or None,
        "brief_status": brief_status or None,
        "reflection_issues": list(semantics["reflection_issues"]),
        "tracked_defects": tracked_defects,
        "issue_details": _issue_details(list(semantics["issues"]), tracked_defects),
        "reasons": list(semantics["issues"]),
        **semantics,
    }
