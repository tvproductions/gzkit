"""Coverage reporting CLI command (gz covers).

Exposes requirement coverage reporting at three granularity levels:
all (`gz covers`), by ADR (`gz covers ADR-X.Y.Z`), or by OBPI
(`gz covers OBPI-X.Y.Z-NN`).  Supports human-readable, JSON, and
plain output modes.

@covers ADR-0.21.0-tests-for-spec
@covers OBPI-0.21.0-03-gz-covers-cli
"""

from __future__ import annotations

import sys
from pathlib import Path

from gzkit.commands.common import console, get_project_root
from gzkit.traceability import (
    CoverageReport,
    compute_coverage,
    scan_feature_tree,
    scan_test_tree,
)
from gzkit.triangle import scan_briefs


def _filter_report(report: CoverageReport, target: str) -> CoverageReport:
    """Return a new CoverageReport filtered to a single ADR or OBPI scope."""
    target_upper = target.upper()

    if target_upper.startswith("OBPI-"):
        # Filter entries whose REQ belongs to this OBPI
        # OBPI-X.Y.Z-NN → match REQ-X.Y.Z-NN-*
        obpi_prefix = target_upper.removeprefix("OBPI-")
        filtered = [e for e in report.entries if _req_belongs_to_obpi(e.req_id, obpi_prefix)]
    elif target_upper.startswith("ADR-"):
        # Filter entries whose REQ belongs to this ADR
        # ADR-X.Y.Z → match REQ-X.Y.Z-*
        adr_semver = target_upper.removeprefix("ADR-")
        filtered = [e for e in report.entries if e.req_id.startswith(f"REQ-{adr_semver}-")]
    else:
        # Try as bare semver → ADR
        filtered = [e for e in report.entries if e.req_id.startswith(f"REQ-{target}-")]

    if not filtered:
        return CoverageReport(
            by_adr=[],
            by_obpi=[],
            entries=[],
            summary=report.summary.model_copy(
                update={
                    "identifier": target,
                    "total_reqs": 0,
                    "covered_reqs": 0,
                    "uncovered_reqs": 0,
                    "coverage_percent": 0.0,
                }
            ),
        )

    # Recompute rollups from filtered entries
    from gzkit.traceability import _obpi_sort_key, _rollup, _semver_sort_key
    from gzkit.triangle import ReqId

    obpi_groups: dict[str, list] = {}
    adr_groups: dict[str, list] = {}
    for entry in filtered:
        parsed = ReqId.parse(entry.req_id)
        obpi_key = f"OBPI-{parsed.semver}-{parsed.obpi_item}"
        adr_key = f"ADR-{parsed.semver}"
        obpi_groups.setdefault(obpi_key, []).append(entry)
        adr_groups.setdefault(adr_key, []).append(entry)

    by_obpi = [
        _rollup(k, g) for k, g in sorted(obpi_groups.items(), key=lambda kv: _obpi_sort_key(kv[0]))
    ]
    by_adr = [
        _rollup(k, g)
        for k, g in sorted(
            adr_groups.items(), key=lambda kv: _semver_sort_key(kv[0].removeprefix("ADR-"))
        )
    ]
    summary = _rollup(target, filtered)

    return CoverageReport(by_adr=by_adr, by_obpi=by_obpi, entries=filtered, summary=summary)


def _req_belongs_to_obpi(req_id: str, obpi_prefix: str) -> bool:
    """Check if REQ-X.Y.Z-NN-MM belongs to OBPI prefix X.Y.Z-NN."""
    stripped = req_id.removeprefix("REQ-")
    # REQ-0.15.0-03-01 → stripped = "0.15.0-03-01"
    # OBPI prefix = "0.15.0-03"
    # Match: stripped starts with "0.15.0-03-"
    return stripped.startswith(f"{obpi_prefix}-")


def _format_human(report: CoverageReport) -> str:
    """Format coverage report as human-readable table."""
    lines: list[str] = []

    if report.summary.total_reqs == 0:
        lines.append("No requirements found.")
        return "\n".join(lines)

    # ADR-level rollup
    if report.by_adr:
        lines.append("Coverage by ADR")
        lines.append(f"{'ADR':<20} {'Covered':>8} {'Total':>8} {'%':>8}")
        lines.append("-" * 48)
        for rollup in report.by_adr:
            lines.append(
                f"{rollup.identifier:<20} {rollup.covered_reqs:>8} "
                f"{rollup.total_reqs:>8} {rollup.coverage_percent:>7.1f}%"
            )
        lines.append("")

    # OBPI-level rollup
    if report.by_obpi:
        lines.append("Coverage by OBPI")
        lines.append(f"{'OBPI':<20} {'Covered':>8} {'Total':>8} {'%':>8}")
        lines.append("-" * 48)
        for rollup in report.by_obpi:
            lines.append(
                f"{rollup.identifier:<20} {rollup.covered_reqs:>8} "
                f"{rollup.total_reqs:>8} {rollup.coverage_percent:>7.1f}%"
            )
        lines.append("")

    # Summary
    s = report.summary
    lines.append(
        f"Summary: {s.covered_reqs}/{s.total_reqs} REQs covered ({s.coverage_percent:.1f}%)"
    )

    return "\n".join(lines)


def _format_plain(report: CoverageReport) -> str:
    """Format coverage report as one record per line."""
    lines: list[str] = []
    for entry in report.entries:
        status = "covered" if entry.covered else "uncovered"
        tests = ",".join(entry.covering_tests) if entry.covering_tests else "-"
        lines.append(f"{entry.req_id}\t{status}\t{tests}")
    return "\n".join(lines)


def covers_cmd(
    target: str | None = None,
    as_json: bool = False,
    plain: bool = False,
    adr_dir: str | None = None,
    test_dir: str | None = None,
    features_dir: str | None = None,
    include_doc: bool = False,
) -> None:
    """Report requirement coverage from @covers annotations and @REQ scenario tags.

    Scans test files for ``@covers`` decorators and behave feature files
    for ``@REQ-X.Y.Z-NN-MM`` scenario tags (GHI #185), cross-references
    against known REQs from OBPI briefs, and reports coverage at ADR,
    OBPI, and REQ granularity. Exit code is always 0 (informational).

    ``include_doc=True`` surfaces doc-kind REQs in the report (governance
    graph completeness rather than test coverage). The default excludes
    them because tests are for code.
    """
    project_root = get_project_root()
    briefs_dir = Path(adr_dir) if adr_dir else project_root / "docs" / "design" / "adr"
    tests_dir = Path(test_dir) if test_dir else project_root / "tests"
    feat_dir = Path(features_dir) if features_dir else project_root / "features"

    discovered = scan_briefs(briefs_dir)
    linkage_records = scan_test_tree(tests_dir) + scan_feature_tree(feat_dir)
    report = compute_coverage(discovered, linkage_records, include_doc=include_doc)

    if target:
        report = _filter_report(report, target)

    if as_json:
        sys.stdout.write(report.model_dump_json(indent=2) + "\n")
    elif plain:
        output = _format_plain(report)
        if output:
            sys.stdout.write(output + "\n")
    else:
        console.print(_format_human(report))
