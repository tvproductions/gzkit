"""Focused context payload renderer for ``gz context <ADR-ID>``.

Originally shipped during the 2026-05 recovery work; now referenced by
``docs/governance/return-to-health-plan-2026-05-30.md`` as the preferred
ADR-scoped context path. Renders one Markdown document combining the target
ADR body, every OBPI brief under its ``obpis/`` directory, the test files
carrying matching ``@covers`` decorators, and a governance-rules section.
``--slim`` (OBPI-02) omits the governance section for non-governance harnesses.

@covers ADR-0.28.0-focused-context-loader
"""

from __future__ import annotations

import contextlib
import re
import sys
from pathlib import Path

from gzkit.commands.common import (
    GzCliError,
    _gate4_na_reason,
    ensure_initialized,
    get_project_root,
    project_lane_gates,
    resolve_adr_file,
)
from gzkit.config import GzkitConfig
from gzkit.ledger import Ledger
from gzkit.traceability import scan_test_tree

_ADR_SEMVER_RE = re.compile(r"^ADR-(\d+\.\d+\.\d+)")


def _adr_semver(adr_stem: str) -> str | None:
    """Extract ``X.Y.Z`` from an ADR identifier like ``ADR-0.0.3-foo``."""
    match = _ADR_SEMVER_RE.match(adr_stem)
    return match.group(1) if match else None


def _render_obpi_briefs(adr_file: Path) -> str:
    """Render every OBPI brief under the ADR package as a delimited section."""
    obpis_dir = adr_file.parent / "obpis"
    if not obpis_dir.exists():
        return ""
    chunks: list[str] = []
    for brief in sorted(obpis_dir.glob("OBPI-*.md")):
        chunks.append(f"\n---\n\n## OBPI brief: {brief.stem}\n\n")
        chunks.append(brief.read_text(encoding="utf-8"))
        chunks.append("\n")
    return "".join(chunks)


def _render_covering_tests(adr_stem: str, project_root: Path) -> str:
    """List test files carrying ``@covers(REQ-<adr-semver>-…)`` decorators."""
    semver = _adr_semver(adr_stem)
    if semver is None:
        return ""
    test_dir = project_root / "tests"
    if not test_dir.exists():
        return ""
    records = scan_test_tree(test_dir)
    req_prefix = f"REQ-{semver}-"
    matches: dict[str, list[str]] = {}
    for record in records:
        req_id = str(record.target.identifier)
        if not req_id.startswith(req_prefix):
            continue
        evidence = record.evidence_path
        if not evidence:
            continue
        rel = Path(evidence)
        with contextlib.suppress(ValueError):
            rel = rel.relative_to(project_root)
        matches.setdefault(req_id, []).append(rel.as_posix())
    if not matches:
        return "\n_No tests carry an @covers decorator for this ADR's REQ namespace._\n"
    lines: list[str] = []
    for req_id in sorted(matches):
        lines.append(f"\n### {req_id}\n")
        for path in sorted(set(matches[req_id])):
            lines.append(f"- `{path}`\n")
    return "".join(lines)


def _ledger_current_gate(
    adr_id: str,
    project_root: Path,
    config: GzkitConfig,
    lane: str,
    gate4_na_reason: str | None,
) -> str:
    """Return the current gate as the furthest APPLICABLE gate cleared.

    REQ-0.28.0-01-06 mandates the gate derive from *ledger* state (Layer-2
    truth), never the frontmatter ``status:`` field — see AGENTS.md Never-rule
    #7 and Architectural Boundary 6. ``get_effective_gate_statuses`` honors
    lifecycle authority for display surfaces (state-doctrine; GHI #392). The
    projection is lane-aware and shared with ``gz status`` via
    ``project_lane_gates`` (GHI #577): a gate the lane marks ``n/a`` never
    counts as cleared, so both surfaces report the same gate for the same ADR.
    When the ledger records no applicable cleared gate it is Gate 1 (the entry
    gate).
    """
    ledger = Ledger(project_root / config.paths.ledger)
    statuses = ledger.get_effective_gate_statuses(adr_id)
    projected = project_lane_gates(lane, statuses, gate4_na_reason)
    cleared = [gate for gate in (2, 3, 4) if projected[gate] == "pass"]
    if cleared:
        return f"Gate {max(cleared)} (latest applicable gate cleared)"
    return "Gate 1 (no applicable gates recorded in ledger)"


def _render_governance_rules(adr_file: Path, project_root: Path, config: GzkitConfig) -> str:
    """Render the governance-rules section (lane / lifecycle / gate / next action).

    Lane and lifecycle come from the ADR frontmatter; the current gate is
    sourced from the ledger (REQ-0.28.0-01-06) so it cannot drift with a stale
    frontmatter ``status:`` field.
    """
    text = adr_file.read_text(encoding="utf-8")
    lane = "lite"
    lifecycle = "Proposed"
    if text.startswith("---"):
        end = text.find("---", 3)
        if end > 0:
            frontmatter = text[3:end]
            for line in frontmatter.splitlines():
                stripped = line.strip()
                if stripped.startswith("lane:"):
                    lane = stripped.split(":", 1)[1].strip() or lane
                elif stripped.startswith("status:"):
                    lifecycle = stripped.split(":", 1)[1].strip() or lifecycle
    # Normalize the lane for the shared gate projection; the display line above
    # keeps the frontmatter value verbatim.
    lane_normalized = lane.strip().lower()
    gate4_na_reason = _gate4_na_reason(project_root, lane_normalized)
    current_gate = _ledger_current_gate(
        adr_file.stem, project_root, config, lane_normalized, gate4_na_reason
    )
    next_action = (
        "Run `gz obpi pipeline <OBPI-ID>` to drive the next OBPI through implement -> verify."
        if lifecycle.lower() in {"proposed", "draft", "accepted"}
        else "Run `gz adr audit <ADR-ID>` to harvest Validated -> Completed."
    )
    return (
        f"- **Lane:** {lane}\n"
        f"- **Lifecycle:** {lifecycle}\n"
        f"- **Current gate:** {current_gate}\n"
        f"- **Next required action:** {next_action}\n"
    )


def build_context_payload(
    adr_file: Path,
    project_root: Path,
    config: GzkitConfig,
    *,
    slim: bool = False,
) -> str:
    """Compose the focused context Markdown payload for an ADR.

    Single Markdown document combining the ADR body, OBPI brief bodies,
    covering-test paths, and (unless ``slim=True``) a governance-rules
    section. No ANSI escapes; suitable for verbatim piping to any agent
    harness (REQ-0.28.0-01-02..08, REQ-0.28.0-02-02..04).
    """
    parts: list[str] = []
    parts.append(f"# Context payload for {adr_file.stem}\n\n")
    parts.append(f"## ADR: {adr_file.stem}\n\n")
    parts.append(adr_file.read_text(encoding="utf-8"))
    parts.append("\n")

    obpi_section = _render_obpi_briefs(adr_file)
    if obpi_section:
        parts.append(obpi_section)

    parts.append("\n---\n\n## Covering tests\n")
    parts.append(_render_covering_tests(adr_file.stem, project_root))

    if not slim:
        parts.append("\n---\n\n## Governance rules\n\n")
        parts.append(_render_governance_rules(adr_file, project_root, config))

    return "".join(parts)


def context_cmd(adr: str, *, slim: bool = False) -> int:
    """Render the focused context payload for ``adr`` to stdout.

    Returns 0 on success. On unresolvable ADR ID, writes a
    ``BLOCKERS:``-prefixed message to stderr and returns exit code 1
    (REQ-0.28.0-01-07).
    """
    project_root = get_project_root()
    try:
        config = ensure_initialized()
        adr_file, _adr_stem = resolve_adr_file(project_root, config, adr)
    except GzCliError as exc:
        sys.stderr.write(f"BLOCKERS: gz context: error: {exc}\n")
        raise SystemExit(1) from exc
    payload = build_context_payload(adr_file, project_root, config, slim=slim)
    sys.stdout.write(payload)
    return 0
