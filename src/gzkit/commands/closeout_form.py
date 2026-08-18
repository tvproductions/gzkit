"""Closeout form rendering and ADR attestation block helpers."""

import sys
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

import yaml

from gzkit.ledger import parse_frontmatter_value

_COMPLETED_RUNTIME_STATES = {"completed", "attested_completed", "validated"}


def guarded_obpi_status_write(obpi_file: Path, target_status: str) -> bool:
    """Single guarded chokepoint for OBPI-brief ``status:`` writes.

    Every governed OBPI-status writer that rewrites only the ``status:`` key
    routes through here; writers that rebuild a whole brief consult the same
    verdict directly. Either way the terminal-clobber decision lives in ONE
    place — :func:`gzkit.governance.frontmatter_coherence.obpi_status_write_refusal`
    — rather than being re-implemented per call site, which is the "one monitor
    governs every write" property ADR-0.31.0 Decision item 4 declares and GHI
    #669 made mechanical. Returns True iff a write landed (False on a no-op or
    a refused clobber). The refusal surfaces the monitor's three-part recovery
    prose to stderr (guardrail-feedback-prose).
    """
    from gzkit.governance.frontmatter_coherence import obpi_status_write_refusal

    content = obpi_file.read_text(encoding="utf-8")
    current = (parse_frontmatter_value(content, "status") or "").strip().lower()
    if current == target_status.strip().lower():
        return False
    refusal = obpi_status_write_refusal(
        brief_name=obpi_file.name, current_status=current, target_status=target_status
    )
    if refusal is not None:
        sys.stderr.write(f"{refusal}\n")
        return False
    obpi_file.write_text(
        _upsert_frontmatter_value(content, "status", target_status), encoding="utf-8"
    )
    return True


def auto_fix_obpi_brief_frontmatter(obpi_file: Path, runtime_state: str) -> bool:
    """Sync OBPI brief frontmatter status to match ledger-derived runtime state.

    Silently fixes frontmatter drift at lifecycle moments (closeout, attest,
    reconcile). Returns True if a change was written. Routes through
    :func:`guarded_obpi_status_write` so a terminal status is never clobbered.
    """
    if runtime_state in _COMPLETED_RUNTIME_STATES:
        target = "Completed"
    elif runtime_state == "withdrawn":
        target = "Abandoned"
    else:
        return False  # only fix toward terminal states

    return guarded_obpi_status_write(obpi_file, target)


def auto_fix_obpi_rows(project_root: Path, obpi_rows: list[dict[str, Any]]) -> None:
    """Auto-fix frontmatter for all OBPI rows from an ADR status query."""
    for row in obpi_rows:
        rel_path = row.get("file")
        runtime_state = row.get("runtime_state", "pending")
        if rel_path and isinstance(rel_path, str):
            obpi_path = project_root / rel_path
            if obpi_path.exists():
                auto_fix_obpi_brief_frontmatter(obpi_path, runtime_state)


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


def _append_frontmatter_list_value(content: str, key: str, value: str) -> str:
    """Append ``value`` to a top-level frontmatter list ``key``, idempotently.

    Deliberately distinct from ``_upsert_frontmatter_value``, which REPLACES a
    scalar. An OBPI mints one TASK per REQ, so its declaration accumulates: a
    replacing writer would leave the channel naming only the most recent TASK,
    which is under-declaration — the exact drift Signature (c) exists to catch
    (GHI #752).

    An existing inline value (``tasks: [A, B]``) is normalized to block form
    rather than skipped, so a hand-authored brief cannot silently drop the
    declaration this stamps.

    An appended item joins an existing block at that block's own indentation; a
    newly created block uses two spaces.
    """
    lines = content.splitlines()
    if not lines or lines[0].strip() != "---":
        return f"---\n{key}:\n  - {value}\n---\n\n{content.lstrip()}"

    end_idx = next((i for i in range(1, len(lines)) if lines[i].strip() == "---"), None)
    if end_idx is None:
        return content

    key_idx = next(
        (
            i
            for i in range(1, end_idx)
            if lines[i].partition(":")[1] and lines[i].partition(":")[0].strip() == key
        ),
        None,
    )
    if key_idx is None:
        lines[end_idx:end_idx] = [f"{key}:", f"  - {value}"]
        return "\n".join(lines).rstrip() + "\n"

    item_end = key_idx + 1
    items: list[str] = []
    # Two spaces only as the default for a block being CREATED. An existing block
    # keeps its own depth: a YAML sequence must agree on indentation, so emitting a
    # fixed two-space item into a column-zero block reformats every sibling line
    # and risks a brief that no longer parses. OBPI briefs author `allowlist:`
    # flush at column zero (GHI #825).
    indent = "  "
    while item_end < end_idx and lines[item_end].lstrip().startswith("- "):
        line = lines[item_end]
        if not items:
            indent = line[: len(line) - len(line.lstrip())]
        items.append(line.lstrip()[2:].strip())
        item_end += 1

    inline = lines[key_idx].partition(":")[2].strip()
    if inline:
        parsed = yaml.safe_load(inline)
        items = [str(p) for p in parsed] if isinstance(parsed, list) else [str(parsed)]

    if value in items:
        return content

    items.append(value)
    lines[key_idx:item_end] = [f"{key}:", *(f"{indent}- {item}" for item in items)]
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
    if not obpi_path.is_file():
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
    if closeout_form.is_file():
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
