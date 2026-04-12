"""Drift detection CLI command (gz drift).

Scans OBPI briefs for REQ entities, test files for @covers references,
and the active repository change set to detect spec-test-code drift.

@covers ADR-0.20.0-spec-triangle-sync
@covers OBPI-0.20.0-04-gz-drift-cli-surface
"""

from __future__ import annotations

import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.traceability import find_covers_in_source
from gzkit.triangle import (
    DriftReport,
    EdgeType,
    LinkageRecord,
    VertexRef,
    VertexType,
    detect_drift,
    scan_briefs,
)


def scan_covers_references(test_dir: Path) -> list[LinkageRecord]:
    """Scan Python test files for @covers REQ references.

    Delegates to the canonical scanner in :mod:`gzkit.traceability` so drift,
    coverage, and audit-check share one detection contract (see #120). Both
    decorator-call and docstring/comment forms are recognized.
    """
    linkages: list[LinkageRecord] = []

    for py_file in sorted(test_dir.rglob("*.py")):
        content = py_file.read_text(encoding="utf-8")
        for req_id, line_num in find_covers_in_source(content):
            linkages.append(
                LinkageRecord(
                    source=VertexRef(
                        vertex_type=VertexType.TEST,
                        identifier=str(py_file),
                        location=str(py_file),
                        line=line_num,
                    ),
                    target=VertexRef(
                        vertex_type=VertexType.SPEC,
                        identifier=req_id,
                    ),
                    edge_type=EdgeType.COVERS,
                    evidence_path=str(py_file),
                    evidence_line=line_num,
                )
            )

    return linkages


def get_changed_files(project_root: Path) -> list[VertexRef]:
    """Get changed source files from the active repository change set.

    Includes both staged and unstaged changes relative to HEAD.
    Only considers ``src/`` Python files as code vertices.
    """
    try:
        result = subprocess.run(
            ["git", "diff", "--name-only", "HEAD"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=project_root,
        )
        staged = subprocess.run(
            ["git", "diff", "--name-only", "--cached"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=project_root,
        )
    except FileNotFoundError:
        return []

    files: set[str] = set()
    for line in (result.stdout + staged.stdout).splitlines():
        stripped = line.strip()
        if stripped and stripped.startswith("src/") and stripped.endswith(".py"):
            files.add(stripped)

    return [VertexRef(vertex_type=VertexType.CODE, identifier=f) for f in sorted(files)]


def _format_human(report: DriftReport) -> str:
    """Format drift report as human-readable tables."""
    lines: list[str] = []

    if report.summary.total_drift_count == 0:
        lines.append("No drift detected.")
        return "\n".join(lines)

    if report.unlinked_specs:
        lines.append("Unlinked Specs (REQs with no test)")
        lines.append("-" * 40)
        for req_id in report.unlinked_specs:
            lines.append(f"  {req_id}")
        lines.append("")

    if report.orphan_tests:
        lines.append("Orphan Tests (tests covering absent REQs)")
        lines.append("-" * 40)
        for req_id in report.orphan_tests:
            lines.append(f"  {req_id}")
        lines.append("")

    if report.unjustified_code_changes:
        lines.append("Unjustified Code Changes")
        lines.append("-" * 40)
        for code_id in report.unjustified_code_changes:
            lines.append(f"  {code_id}")
        lines.append("")

    lines.append(
        f"Summary: {report.summary.unlinked_spec_count} unlinked, "
        f"{report.summary.orphan_test_count} orphan, "
        f"{report.summary.unjustified_code_change_count} unjustified "
        f"({report.summary.total_drift_count} total)"
    )

    return "\n".join(lines)


def _format_plain(report: DriftReport) -> str:
    """Format drift report as one-record-per-line plain text."""
    lines: list[str] = []
    for req_id in report.unlinked_specs:
        lines.append(f"unlinked\t{req_id}")
    for req_id in report.orphan_tests:
        lines.append(f"orphan\t{req_id}")
    for code_id in report.unjustified_code_changes:
        lines.append(f"unjustified\t{code_id}")
    return "\n".join(lines)


def drift_cmd(
    as_json: bool = False,
    plain: bool = False,
    adr_dir: str | None = None,
    test_dir: str | None = None,
) -> None:
    """Run drift detection across the spec-test-code triangle.

    Scans OBPI briefs for REQ entities, test files for @covers
    references, and the repository change set for unjustified
    code changes. Reports findings in human, JSON, or plain mode.
    """
    project_root = get_project_root()
    briefs_dir = Path(adr_dir) if adr_dir else project_root / "docs" / "design" / "adr"
    tests_dir = Path(test_dir) if test_dir else project_root / "tests"

    discovered = scan_briefs(briefs_dir)
    reqs = [d.entity for d in discovered]

    linkages = scan_covers_references(tests_dir)

    changed_vertices = get_changed_files(project_root)

    timestamp = datetime.now(UTC).isoformat()
    report = detect_drift(reqs, linkages, changed_vertices, timestamp)

    if as_json:
        sys.stdout.write(report.model_dump_json(indent=2) + "\n")
    elif plain:
        output = _format_plain(report)
        if output:
            sys.stdout.write(output + "\n")
    else:
        console.print(_format_human(report))

    if report.summary.total_drift_count > 0:
        raise SystemExit(1)
