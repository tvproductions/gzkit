"""Common utilities and error types for CLI commands."""

import json
import os
import re
import subprocess
from datetime import UTC, datetime
from pathlib import Path
from typing import Any, cast

from rich.console import Console

from gzkit.config import GzkitConfig
from gzkit.core.exceptions import GzkitError
from gzkit.ledger import (
    Ledger,
    resolve_adr_lane,
)
from gzkit.sync import parse_artifact_metadata, scan_existing_artifacts


class GzCliError(GzkitError):
    """User-facing CLI error.

    Inherits from :class:`GzkitError` so the CLI boundary can catch the
    entire typed hierarchy with a single ``except GzkitError`` clause.
    Exit code defaults to 1 (user/config error) via the base class.
    """


console = Console(
    no_color=os.environ.get("NO_COLOR") is not None,
    force_terminal=os.environ.get("FORCE_COLOR") is not None,
)

COMMAND_DOCS: dict[str, str] = {
    "init": "docs/user/commands/init.md",
    "prd": "docs/user/commands/prd.md",
    "constitute": "docs/user/commands/constitute.md",
    "specify": "docs/user/commands/specify.md",
    "plan": "docs/user/commands/plan.md",
    "status": "docs/user/commands/status.md",
    "state": "docs/user/commands/state.md",
    "git-sync": "docs/user/commands/git-sync.md",
    "attest": "docs/user/commands/attest.md",
    "implement": "docs/user/commands/implement.md",
    "gates": "docs/user/commands/gates.md",
    "migrate-semver": "docs/user/commands/migrate-semver.md",
    "register-adrs": "docs/user/commands/register-adrs.md",
    "skill audit": "docs/user/commands/skill-audit.md",
    "closeout": "docs/user/commands/closeout.md",
    "covers": "docs/user/commands/covers.md",
    "drift": "docs/user/commands/drift.md",
    "audit": "docs/user/commands/audit.md",
    "check-config-paths": "docs/user/commands/check-config-paths.md",
    "cli audit": "docs/user/commands/cli-audit.md",
    "parity check": "docs/user/commands/parity-check.md",
    "readiness audit": "docs/user/commands/readiness-audit.md",
    "readiness evaluate": "docs/user/commands/readiness-evaluate.md",
    "adr evaluate": "docs/user/commands/adr-evaluate.md",
    "adr status": "docs/user/commands/adr-status.md",
    "adr promote": "docs/user/commands/adr-promote.md",
    "adr audit-check": "docs/user/commands/adr-audit-check.md",
    "adr covers-check": "docs/user/commands/adr-covers-check.md",
    "adr emit-receipt": "docs/user/commands/adr-emit-receipt.md",
    "roles": "docs/user/commands/roles.md",
    "obpi status": "docs/user/commands/obpi-status.md",
    "obpi pipeline": "docs/user/commands/obpi-pipeline.md",
    "obpi validate": "docs/user/commands/obpi-validate.md",
    "obpi reconcile": "docs/user/commands/obpi-reconcile.md",
    "obpi emit-receipt": "docs/user/commands/obpi-emit-receipt.md",
    "chores list": "docs/user/commands/chores-list.md",
    "chores plan": "docs/user/commands/chores-plan.md",
    "chores run": "docs/user/commands/chores-run.md",
    "chores audit": "docs/user/commands/chores-audit.md",
    "agent sync control-surfaces": "docs/user/commands/agent-sync-control-surfaces.md",
    "adr report": "docs/user/commands/adr-report.md",
    "check": "docs/user/commands/check.md",
    "chores advise": "docs/user/commands/chores-advise.md",
    "chores show": "docs/user/commands/chores-show.md",
    "format": "docs/user/commands/format.md",
    "interview": "docs/user/commands/interview.md",
    "lint": "docs/user/commands/lint.md",
    "skill list": "docs/user/commands/skill-list.md",
    "skill new": "docs/user/commands/skill-new.md",
    "test": "docs/user/commands/test.md",
    "tidy": "docs/user/commands/tidy.md",
    "typecheck": "docs/user/commands/typecheck.md",
    "validate": "docs/user/commands/validate.md",
    "task list": "docs/user/commands/task-list.md",
    "task start": "docs/user/commands/task-start.md",
    "task complete": "docs/user/commands/task-complete.md",
    "task block": "docs/user/commands/task-block.md",
    "task escalate": "docs/user/commands/task-escalate.md",
    "obpi withdraw": "docs/user/commands/obpi-withdraw.md",
    "preflight": "docs/user/commands/preflight.md",
}

ADR_SEMVER_ID_RE = re.compile(r"^ADR-\d+\.\d+\.\d+(?:[.-][A-Za-z0-9][A-Za-z0-9.-]*)?$")
ADR_POOL_ID_RE = re.compile(r"^ADR-pool\.[A-Za-z0-9][A-Za-z0-9.-]*$")
SEMVER_ONLY_RE = re.compile(r"^\d+\.\d+\.\d+$")
ADR_SLUG_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def _prompt_text(prompt: str, default: str = "") -> str:
    """Prompt for a text response via stdin."""
    suffix = f" [{default}]" if default else ""
    try:
        answer = input(f"{prompt}{suffix}: ")
    except (EOFError, KeyboardInterrupt):
        raise KeyboardInterrupt from None
    return answer if answer else default


def _confirm(prompt: str, default: bool = True) -> bool:
    """Prompt for a yes/no confirmation via stdin."""
    suffix = " [Y/n] " if default else " [y/N] "
    try:
        answer = input(f"{prompt}{suffix}").strip().lower()
    except (EOFError, KeyboardInterrupt):
        raise KeyboardInterrupt from None
    if not answer:
        return default
    return answer in {"y", "yes"}


def _is_pool_adr_id(adr_id: str) -> bool:
    """Return True when an ADR identifier represents a pool entry."""
    return ADR_POOL_ID_RE.match(adr_id) is not None or "-pool." in adr_id


def _apply_pool_adr_status_overrides(adr_id: str, payload: dict[str, Any]) -> None:
    """Force pool ADRs to remain backlog-style on status surfaces."""
    if not _is_pool_adr_id(adr_id):
        return

    payload["attested"] = False
    payload["attestation_status"] = None
    payload["attestation_term"] = None
    payload["validated"] = False
    payload["lifecycle_status"] = "Pending"
    payload["closeout_phase"] = "pre_closeout"

    gates = cast(dict[str, str], payload.get("gates", {}))
    if gates:
        gates["5"] = "pending"


def _reject_pool_adr_for_lifecycle(adr_id: str, action: str) -> None:
    """Block closeout lifecycle operations for pool ADRs."""
    if not _is_pool_adr_id(adr_id):
        return
    raise GzCliError(f"Pool ADRs cannot be {action}: {adr_id}. Promote this ADR from pool first.")


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path.cwd()


def ensure_initialized() -> GzkitConfig:
    """Ensure gzkit is initialized and return config."""
    config_path = get_project_root() / ".gzkit.json"
    if not config_path.exists():
        raise GzCliError("gzkit not initialized. Run 'gz init' first.")
    return GzkitConfig.load(config_path)


def load_manifest(project_root: Path) -> dict[str, Any]:
    """Load the gzkit manifest."""
    manifest_path = project_root / ".gzkit" / "manifest.json"
    if not manifest_path.exists():
        raise GzCliError("Missing .gzkit/manifest.json")
    return json.loads(manifest_path.read_text(encoding="utf-8"))


def get_git_user() -> str:
    """Get the current git user for attestations."""
    try:
        result = subprocess.run(
            ["git", "config", "user.name"],
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip()
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown"


def _gate4_na_reason(project_root: Path, lane: str) -> str | None:
    """Return explicit Gate 4 N/A rationale when BDD suite is not applicable."""
    if lane != "heavy":
        return "Gate 4 applies to heavy lane only."
    return None


def _attestation_gate_snapshot(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr_id: str,
) -> dict[str, Any]:
    """Compute attestation prerequisite state for one ADR."""
    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id, {})
    lane = resolve_adr_lane(info, config.mode)
    gate_statuses = ledger.get_latest_gate_statuses(adr_id)

    gate2 = gate_statuses.get(2, "pending")
    gate3 = gate_statuses.get(3, "pending")
    gate4 = gate_statuses.get(4, "pending")
    gate4_na = _gate4_na_reason(project_root, lane)

    blockers: list[str] = []
    if gate2 != "pass":
        blockers.append(f"Gate 2 must pass (current: {gate2}).")

    if lane == "heavy":
        if gate3 != "pass":
            blockers.append(f"Gate 3 must pass (current: {gate3}).")
        if gate4 != "pass":
            blockers.append(f"Gate 4 must pass (current: {gate4}).")

    return {
        "lane": lane,
        "gate2": gate2,
        "gate3": gate3 if lane == "heavy" else "n/a",
        "gate4": "n/a" if gate4_na is not None else gate4,
        "gate4_na_reason": gate4_na,
        "ready": not blockers,
        "blockers": blockers,
    }


def _canonical_attestation_term(attest_status: str, reason: str | None = None) -> str:
    """Render canonical attestation term from stable CLI status token."""
    base = Ledger.canonical_attestation_term(attest_status) or attest_status
    if attest_status in {"partial", "dropped"} and reason:
        return f"{base}: {reason}"
    return base


def resolve_adr_file(project_root: Path, config: GzkitConfig, adr: str) -> tuple[Path, str]:
    """Resolve an ADR file path from an ID, supporting nested layouts."""

    def _pick_unique(
        candidates: list[tuple[Path, str]], requested_id: str
    ) -> tuple[Path, str] | None:
        if len(candidates) == 1:
            return candidates[0]
        if len(candidates) > 1:
            # Prefer non-pool ADRs when duplicates exist
            non_pool = [
                entry for entry in candidates if "docs/design/adr/pool" not in str(entry[0])
            ]
            if len(non_pool) == 1:
                return non_pool[0]
            if len(non_pool) > 1:
                rels = ", ".join(
                    str(path.relative_to(project_root)) for path, _resolved in non_pool
                )
                raise GzCliError(f"Multiple ADR files found for {requested_id}: {rels}")
            rels = ", ".join(str(path.relative_to(project_root)) for path, _resolved in candidates)
            raise GzCliError(f"Multiple ADR files found for {requested_id}: {rels}")
        return None

    adr_id = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    adr_dir = project_root / config.paths.adrs

    candidates = [adr_dir / f"{adr}.md"]
    if adr_id != adr:
        candidates.append(adr_dir / f"{adr_id}.md")

    for candidate in candidates:
        if candidate.exists():
            return candidate, candidate.stem

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    exact_matches: list[tuple[Path, str]] = []
    prefix_matches: list[tuple[Path, str]] = []
    for adr_file in artifacts.get("adrs", []):
        metadata = parse_artifact_metadata(adr_file)
        stem_id = adr_file.stem
        parsed_id = metadata.get("id", stem_id)
        # Prefer explicit metadata IDs, but also match filename stems for
        # suffixed IDs like ADR-0.6.0-pool.* when headers use ADR-0.6.0.
        if adr_id == stem_id:
            exact_matches.append((adr_file, stem_id))
            continue
        if adr_id == parsed_id:
            exact_matches.append((adr_file, parsed_id))
            continue
        if stem_id.startswith(f"{adr_id}-"):
            prefix_matches.append((adr_file, stem_id))

    unique = _pick_unique(exact_matches, adr_id)
    if unique:
        return unique
    unique = _pick_unique(prefix_matches, adr_id)
    if unique:
        return unique

    raise GzCliError(f"ADR not found: {adr}")


def resolve_adr_ledger_id(
    adr_file: Path,
    adr_id: str,
    ledger: Ledger,
) -> str:
    """Resolve an ADR ID to its ledger graph key, falling back to file stem.

    When frontmatter ``id:`` (e.g. ``ADR-0.16.0``) differs from the ledger
    registration key (e.g. ``ADR-0.16.0-cms-architecture-formalization``),
    the file stem is tried as a fallback so that graph lookups succeed.
    """
    graph = ledger.get_artifact_graph()
    info = graph.get(adr_id)
    if info and info.get("type") == "adr":
        return adr_id
    stem_id = adr_file.stem
    if stem_id != adr_id:
        stem_info = graph.get(stem_id)
        if stem_info and stem_info.get("type") == "adr":
            return stem_id
    return adr_id


def resolve_target_adr(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    adr: str | None,
) -> str:
    """Resolve ADR id for gate operations."""
    if adr is None:
        pending = ledger.get_pending_attestations()
        if len(pending) == 1:
            adr = pending[0]
        elif not pending:
            raise GzCliError("No pending ADRs found. Use --adr to specify one.")
        else:
            raise GzCliError("Multiple pending ADRs found. Use --adr to specify one.")

    adr_id = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr_id = ledger.canonicalize_id(adr_id)

    adr_file, resolved_adr_id = resolve_adr_file(project_root, config, canonical_adr_id)
    return resolve_adr_ledger_id(adr_file, resolved_adr_id, ledger)


def resolve_obpi(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    obpi: str,
) -> tuple[str, Path | None]:
    """Resolve an OBPI id and optional file path from ledger or matching brief."""
    obpi_input = obpi if obpi.startswith("OBPI-") else f"OBPI-{obpi}"
    canonical_obpi = ledger.canonicalize_id(obpi_input)
    graph = ledger.get_artifact_graph()
    info = graph.get(canonical_obpi)
    if info and info.get("type") != "obpi":
        raise GzCliError(f"OBPI not found in ledger: {canonical_obpi}")

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    matches: list[Path] = []
    for obpi_file in artifacts.get("obpis", []):
        metadata = parse_artifact_metadata(obpi_file)
        file_id = metadata.get("id", obpi_file.stem)
        if ledger.canonicalize_id(file_id) == canonical_obpi:
            matches.append(obpi_file)

    if len(matches) > 1:
        rels = ", ".join(str(path.relative_to(project_root)) for path in matches)
        raise GzCliError(f"Multiple OBPI files found for {canonical_obpi}: {rels}")

    if info and info.get("type") == "obpi":
        return canonical_obpi, matches[0] if matches else None
    if matches:
        return canonical_obpi, matches[0]
    raise GzCliError(f"OBPI not found in ledger or briefs: {canonical_obpi}")


def resolve_obpi_file(
    project_root: Path,
    config: GzkitConfig,
    ledger: Ledger,
    obpi: str,
) -> tuple[Path, str]:
    """Resolve an OBPI file path from an ID, supporting rename chains."""
    canonical_obpi, obpi_file = resolve_obpi(project_root, config, ledger, obpi)
    if obpi_file is None:
        raise GzCliError(f"OBPI file not found for {canonical_obpi}")
    return obpi_file, canonical_obpi


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

    phase_label = "Phase 1 — Awaiting Attestation"
    if attestation_term is not None:
        phase_label = f"Phase 2 — {attestation_term}"

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


# ---------------------------------------------------------------------------
# Version sync helpers
# ---------------------------------------------------------------------------

_VERSION_BADGE_RE = re.compile(r"(badge/version-)\d+\.\d+\.\d+(-blue\.svg)")


def _extract_adr_version(adr_id: str) -> str | None:
    """Extract the semver portion from an ADR ID like ``ADR-0.18.0-slug``."""
    m = re.match(r"^ADR-(\d+\.\d+\.\d+)", adr_id)
    return m.group(1) if m else None


def _parse_semver_tuple(version: str) -> tuple[int, ...]:
    """Convert ``"0.18.0"`` to ``(0, 18, 0)`` for comparison."""
    return tuple(int(p) for p in version.split("."))


def _read_current_project_version(project_root: Path) -> str | None:
    """Read version from ``pyproject.toml``."""
    pyproject = project_root / "pyproject.toml"
    if not pyproject.exists():
        return None
    for line in pyproject.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^version\s*=\s*"(\d+\.\d+\.\d+)"', line)
        if m:
            return m.group(1)
    return None


def sync_project_version(project_root: Path, new_version: str) -> list[str]:
    """Bump version in pyproject.toml, __init__.py, and README badge.

    Returns a list of files that were updated (relative to *project_root*).
    """
    updated: list[str] = []

    # pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.exists():
        old = pyproject.read_text(encoding="utf-8")
        new = re.sub(
            r'^(version\s*=\s*")\d+\.\d+\.\d+(")',
            rf"\g<1>{new_version}\2",
            old,
            count=1,
            flags=re.MULTILINE,
        )
        if new != old:
            pyproject.write_text(new, encoding="utf-8")
            updated.append("pyproject.toml")

    # src/gzkit/__init__.py
    init_py = project_root / "src" / "gzkit" / "__init__.py"
    if init_py.exists():
        old = init_py.read_text(encoding="utf-8")
        new = re.sub(
            r'^(__version__\s*=\s*")\d+\.\d+\.\d+(")',
            rf"\g<1>{new_version}\2",
            old,
            count=1,
            flags=re.MULTILINE,
        )
        if new != old:
            init_py.write_text(new, encoding="utf-8")
            updated.append("src/gzkit/__init__.py")

    # README.md badge
    readme = project_root / "README.md"
    if readme.exists():
        old = readme.read_text(encoding="utf-8")
        new = _VERSION_BADGE_RE.sub(rf"\g<1>{new_version}\2", old)
        if new != old:
            readme.write_text(new, encoding="utf-8")
            updated.append("README.md")

    return updated


def aggregate_audit_evidence(
    ledger: "Ledger",
    adr_id: str,
    graph: dict[str, Any],
) -> dict[str, Any]:
    """Aggregate governance evidence from the ledger for audit report rendering.

    Queries the ledger for OBPI receipt, gate check, attestation, and closeout
    events scoped to ``adr_id`` and returns a structured dict suitable for
    template rendering.

    Args:
        ledger: Ledger instance to query.
        adr_id: The canonical ADR identifier.
        graph: Artifact graph from ``ledger.get_artifact_graph()``.

    Returns:
        Dict with keys ``obpi_completions``, ``gate_results``, ``attestation``,
        and ``closeout``.

    """
    # OBPI completions — enumerate child OBPIs from graph
    obpi_completions: list[dict[str, Any]] = []
    adr_info = graph.get(adr_id, {})
    children: list[str] = sorted(adr_info.get("children", []))
    for child_id in children:
        child_info = graph.get(child_id, {})
        if child_info.get("type") != "obpi":
            continue
        receipt_event = child_info.get("latest_receipt_event")
        ledger_completed = bool(child_info.get("ledger_completed"))
        obpi_completions.append(
            {
                "obpi_id": child_id,
                "receipt_event": receipt_event,
                "ledger_completed": ledger_completed,
            }
        )

    # Gate results — query gate_checked events for the ADR
    gate_events = ledger.query(event_type="gate_checked", artifact_id=adr_id)
    gate_results: list[dict[str, Any]] = [
        {
            "gate": e.extra.get("gate"),
            "status": e.extra.get("status"),
            "command": e.extra.get("command"),
            "returncode": e.extra.get("returncode"),
        }
        for e in gate_events
    ]

    # Attestation — latest attested event
    attested_events = ledger.query(event_type="attested", artifact_id=adr_id)
    attestation: dict[str, Any] | None = None
    if attested_events:
        latest = attested_events[-1]
        attestation = {
            "by": latest.extra.get("by", "unknown"),
            "status": latest.extra.get("status", "unknown"),
            "ts": latest.ts,
        }

    # Closeout — latest closeout_initiated event
    closeout_events = ledger.query(event_type="closeout_initiated", artifact_id=adr_id)
    closeout: dict[str, Any] | None = None
    if closeout_events:
        latest = closeout_events[-1]
        closeout = {
            "by": latest.extra.get("by", "unknown"),
            "mode": latest.extra.get("mode", "unknown"),
            "ts": latest.ts,
        }

    return {
        "obpi_completions": obpi_completions,
        "gate_results": gate_results,
        "attestation": attestation,
        "closeout": closeout,
    }


def check_version_sync(project_root: Path, adr_id: str) -> tuple[str | None, str | None, bool]:
    """Check if project version should be bumped for this ADR closeout.

    Returns ``(current_version, adr_version, needs_bump)``.
    """
    adr_version = _extract_adr_version(adr_id)
    if adr_version is None:
        return None, None, False
    current = _read_current_project_version(project_root)
    if current is None:
        return None, adr_version, True
    needs_bump = _parse_semver_tuple(adr_version) > _parse_semver_tuple(current)
    return current, adr_version, needs_bump


def _cli_main():
    """Return the gzkit.cli.main module for test-mock compatibility.

    Tests patch dependencies at ``gzkit.cli.main.<name>``.  After the
    cli/main.py restructure (OBPI-0.0.4-01), handler functions live in
    separate command modules.  This helper lets command modules look up
    shared dependencies through main.py's namespace so ``mock.patch``
    targets continue to work.
    """
    import sys  # deferred to avoid top-level import of sys just for this helper

    return sys.modules["gzkit.cli.main"]
