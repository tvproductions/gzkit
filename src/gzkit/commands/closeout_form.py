"""Closeout form rendering and ADR attestation block helpers."""

from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast


def _upsert_frontmatter_value(content: str, key: str, value: str) -> str:
    """Set or insert a top-level frontmatter key/value pair."""
    lines = content.splitlines()
    if not lines:
        return f"---\n{key}: {value}\n---\n"

    if lines[0].strip() != "---":
        prefixed = ["---", f"{key}: {value}", "---", "", *lines]
        return "\n".join(prefixed).rstrip() + "\n"

    end_idx = None
    for idx in range(1, len(lines)):
        if lines[idx].strip() == "---":
            end_idx = idx
            break
    if end_idx is None:
        lines.extend([f"{key}: {value}", "---"])
        return "\n".join(lines).rstrip() + "\n"

    replaced = False
    for idx in range(1, end_idx):
        raw_key, sep, _raw_value = lines[idx].partition(":")
        if sep and raw_key.strip() == key:
            lines[idx] = f"{key}: {value}"
            replaced = True
            break

    if not replaced:
        lines.insert(end_idx, f"{key}: {value}")

    return "\n".join(lines).rstrip() + "\n"


def _adr_semver_term(adr_id: str) -> str:
    """Extract the semver term from an ADR identifier."""
    return adr_id.removeprefix("ADR-").split("-", 1)[0]


def _markdown_table_cell(value: str) -> str:
    """Escape markdown table control characters in one cell."""
    return value.replace("|", "\\|").strip()


def _closeout_form_path(adr_file: Path) -> Path:
    """Return the canonical closeout form path for an ADR file."""
    return adr_file.parent / "ADR-CLOSEOUT-FORM.md"


def _closeout_form_attestation_text(attest_status: str, reason: str | None) -> str:
    """Render the recorded attestation text from CLI inputs."""
    if reason:
        return f"{attest_status}: {reason}"
    return attest_status


def _closeout_form_timestamp() -> str:
    """Return an RFC3339 UTC timestamp for closeout records."""
    return datetime.now(UTC).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _extract_obpi_description(project_root: Path, row: dict[str, Any]) -> str:
    """Best-effort OBPI description for closeout tables."""
    file_value = row.get("file")
    if not isinstance(file_value, str):
        return cast(str, row.get("id", ""))

    obpi_path = project_root / file_value
    if not obpi_path.exists():
        return obpi_path.stem

    for line in obpi_path.read_text(encoding="utf-8").splitlines():
        if line.startswith("# "):
            heading = line[2:].strip()
            return heading.split(": ", 1)[1] if ": " in heading else heading

    return obpi_path.stem


def _render_adr_closeout_form(
    project_root: Path,
    adr_id: str,
    adr_file: Path,
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate_statuses: dict[int, str],
    *,
    attestation_command: str,
    attestation_text: str | None = None,
    attestation_term: str | None = None,
    attester: str | None = None,
    timestamp_utc: str | None = None,
    defense_brief: str | None = None,
) -> str:
    """Render the canonical ADR closeout form markdown."""
    gate_1_path = adr_file.relative_to(project_root).as_posix()
    closeout_form = _closeout_form_path(adr_file)
    preserved_tail = ""
    if closeout_form.exists():
        existing = closeout_form.read_text(encoding="utf-8")
        marker = "## Post-Attestation (Phase 2)"
        marker_index = existing.find(marker)
        if marker_index != -1:
            preserved_tail = existing[marker_index:].strip()

    phase_label = "Phase 1 \u2014 Awaiting Attestation"
    if attestation_term is not None:
        phase_label = f"Phase 2 \u2014 {attestation_term}"

    all_obpis_complete = bool(obpi_rows) and all(bool(row.get("completed")) for row in obpi_rows)
    if not obpi_rows:
        all_obpis_complete = True

    def checkbox(passed: bool) -> str:
        return "[x]" if passed else "[ ]"

    lines = [
        f"# ADR Closeout Form: {adr_id}",
        "",
        f"**Status**: {phase_label}",
        "",
        "---",
        "",
        "## Pre-Attestation Checklist",
        "",
        "Closeout evidence verified:",
        "",
        f"- {checkbox(all_obpis_complete)} All checklist items in ADR are complete",
        f"- {checkbox(all_obpis_complete)} All OBPIs have passing acceptance criteria",
        f"- {checkbox(gate_statuses.get(2) == 'pass')} Gate 2 (TDD): Tests pass",
        f"- {checkbox(gate_statuses.get(3) == 'pass')} Gate 3 (Docs): Docs build passes",
        f"- {checkbox(gate_statuses.get(4) == 'pass')} Gate 4 (BDD): Behave suite passes",
        "- [ ] Code reviewed",
        "",
        "## Evidence Paths",
        "",
        "| Gate | Evidence | Command/Path |",
        "|------|----------|--------------|",
        f"| Gate 1 | ADR exists | `{gate_1_path}` |",
    ]

    evidence_labels = {
        "Gate 2 (TDD)": "Tests pass",
        "Quality (Lint)": "Lint passes",
        "Quality (Typecheck)": "Typecheck passes",
        "Gate 3 (Docs)": "Docs build",
        "Gate 4 (BDD)": "BDD passes",
    }
    for label, command in verification_steps:
        evidence = evidence_labels.get(label, label)
        lines.append(f"| {label} | {evidence} | `{command}` |")
    lines.append(f"| Gate 5 | Human attests | `{attestation_command}` |")
    lines.extend(
        [
            "",
            "## OBPI Status",
            "",
            "| OBPI | Description | Status |",
            "|------|-------------|--------|",
        ]
    )
    for row in obpi_rows:
        obpi_id = cast(str, row.get("id", ""))
        file_value = row.get("file")
        label = obpi_id
        if isinstance(file_value, str):
            label = f"[{obpi_id}]({Path(file_value).name})"
        lines.append(
            f"| {label} | {_extract_obpi_description(project_root, row)} | "
            f"{'Completed' if row.get('completed') else 'Pending'} |"
        )

    if defense_brief:
        lines.extend(["", defense_brief])

    lines.extend(["", "## Human Attestation", ""])
    if attestation_text is None or attester is None or timestamp_utc is None:
        lines.append("Awaiting explicit human attestation.")
    else:
        lines.extend(
            [
                "### Verbatim Attestation",
                "",
                f"- `{attestation_text}`",
                "",
                f"**Attested by**: {attester}",
                f"**Timestamp (UTC)**: {timestamp_utc}",
            ]
        )

    if preserved_tail:
        lines.extend(["", "---", "", preserved_tail])

    return "\n".join(lines).rstrip() + "\n"


def _write_adr_closeout_form(
    project_root: Path,
    adr_id: str,
    adr_file: Path,
    obpi_rows: list[dict[str, Any]],
    verification_steps: list[tuple[str, str]],
    gate_statuses: dict[int, str],
    *,
    attestation_command: str,
    attestation_text: str | None = None,
    attestation_term: str | None = None,
    attester: str | None = None,
    timestamp_utc: str | None = None,
    defense_brief: str | None = None,
) -> Path:
    """Create or refresh the ADR closeout form."""
    closeout_form = _closeout_form_path(adr_file)
    closeout_form.write_text(
        _render_adr_closeout_form(
            project_root,
            adr_id,
            adr_file,
            obpi_rows,
            verification_steps,
            gate_statuses,
            attestation_command=attestation_command,
            attestation_text=attestation_text,
            attestation_term=attestation_term,
            attester=attester,
            timestamp_utc=timestamp_utc,
            defense_brief=defense_brief,
        ),
        encoding="utf-8",
    )
    return closeout_form


def _update_adr_attestation_block(
    adr_file: Path,
    adr_id: str,
    *,
    canonical_term: str,
    attester: str,
    attestation_date: str,
    attestation_reason: str,
) -> None:
    """Update the ADR attestation block table with recorded human attestation."""
    content = adr_file.read_text(encoding="utf-8")
    lines = content.splitlines()
    row = (
        f"| {_adr_semver_term(adr_id)} | {_markdown_table_cell(canonical_term)} | "
        f"{_markdown_table_cell(attester)} | {_markdown_table_cell(attestation_date)} | "
        f"{_markdown_table_cell(attestation_reason)} |"
    )

    block_header = "## Attestation Block"
    table_header = "| Term | Status | Attested By | Date | Reason |"
    table_separator = "|------|--------|-------------|------|--------|"

    if block_header not in lines:
        content = content.rstrip() + "\n\n"
        content += "\n".join([block_header, "", table_header, table_separator, row]) + "\n"
        adr_file.write_text(content, encoding="utf-8")
        return

    block_index = lines.index(block_header)
    header_index = None
    separator_index = None
    for idx in range(block_index + 1, len(lines)):
        if lines[idx].strip() == table_header:
            header_index = idx
            break
        if lines[idx].startswith("## "):
            break

    if header_index is None:
        insert_index = block_index + 1
        lines[insert_index:insert_index] = ["", table_header, table_separator, row]
        adr_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
        return

    separator_index = header_index + 1
    if separator_index >= len(lines) or lines[separator_index].strip() != table_separator:
        lines.insert(header_index + 1, table_separator)
        separator_index = header_index + 1

    data_index = separator_index + 1
    if data_index < len(lines) and lines[data_index].startswith("|"):
        lines[data_index] = row
    else:
        lines.insert(data_index, row)

    adr_file.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
