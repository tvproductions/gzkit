"""Doc-coverage chore runner: manifest-aware gap detection and enforcement.

Loads the documentation manifest (OBPI-02) and invokes the AST scanner
(OBPI-01) to produce an actionable gap report.  Exits 0 when all required
surfaces are present, 1 when any gap exists.
"""

import json
import sys
from pathlib import Path

from gzkit.commands.common import get_project_root
from gzkit.doc_coverage.manifest import find_undeclared_commands, load_manifest
from gzkit.doc_coverage.models import DocCoverageGapReport, GapItem, OrphanedDocItem
from gzkit.doc_coverage.scanner import check_surfaces_report


def build_gap_report(project_root: Path | None = None) -> DocCoverageGapReport:
    """Build a manifest-aware documentation coverage gap report.

    Compares scanner results against manifest requirements to identify
    only the gaps that matter: surfaces marked as required but missing.
    """
    if project_root is None:
        project_root = get_project_root()

    manifest = load_manifest(project_root)
    report = check_surfaces_report(project_root)

    discovered_names = {c.command for c in report.coverage}
    undeclared = find_undeclared_commands(manifest, discovered_names)

    gaps: list[GapItem] = []
    commands_with_gaps: set[str] = set()

    for cmd_cov in report.coverage:
        cmd_name = cmd_cov.command
        if cmd_name not in manifest.commands:
            continue
        entry = manifest.commands[cmd_name]
        for surface_result in cmd_cov.surfaces:
            surface_required = getattr(entry.surfaces, surface_result.surface, False)
            if surface_required and not surface_result.passed:
                gaps.append(
                    GapItem(
                        command=cmd_name,
                        surface=surface_result.surface,
                        detail=surface_result.detail,
                    )
                )
                commands_with_gaps.add(cmd_name)

    orphaned = [
        OrphanedDocItem(surface=o.surface, reference=o.reference, detail=o.detail)
        for o in report.orphaned
    ]

    return DocCoverageGapReport(
        passed=len(gaps) == 0 and len(undeclared) == 0 and len(orphaned) == 0,
        commands_discovered=report.commands_discovered,
        commands_checked=len(manifest.commands),
        commands_with_gaps=len(commands_with_gaps),
        gaps=sorted(gaps, key=lambda g: (g.command, g.surface)),
        undeclared_commands=undeclared,
        orphaned_docs=orphaned,
    )


def _print_human_report(gap_report: DocCoverageGapReport) -> None:
    """Render the gap report as human-readable text to stdout."""
    print("Documentation Coverage Gap Report")  # noqa: T201
    print("=" * 40)  # noqa: T201
    print()  # noqa: T201

    if gap_report.gaps:
        current_cmd: str | None = None
        for gap in gap_report.gaps:
            if gap.command != current_cmd:
                current_cmd = gap.command
                print(f"  Command: {current_cmd}")  # noqa: T201
            print(f"    MISSING: {gap.surface} -- {gap.detail}")  # noqa: T201
        print()  # noqa: T201

    if gap_report.undeclared_commands:
        print("  Undeclared commands (not in manifest):")  # noqa: T201
        for cmd in gap_report.undeclared_commands:
            print(f"    - {cmd}")  # noqa: T201
        print()  # noqa: T201

    if gap_report.orphaned_docs:
        print("  Orphaned documentation:")  # noqa: T201
        for orphan in gap_report.orphaned_docs:
            print(f"    - [{orphan.surface}] {orphan.reference}: {orphan.detail}")  # noqa: T201
        print()  # noqa: T201

    if gap_report.passed:
        print(  # noqa: T201
            f"PASSED: {gap_report.commands_discovered} commands discovered, "
            f"{gap_report.commands_checked} checked, all required surfaces present."
        )
    else:
        total = (
            len(gap_report.gaps)
            + len(gap_report.undeclared_commands)
            + len(gap_report.orphaned_docs)
        )
        print(f"FAILED: {total} issues found across {gap_report.commands_with_gaps} commands.")  # noqa: T201


def run_doc_coverage(project_root: Path | None = None, *, json_output: bool = False) -> int:
    """Run the doc-coverage chore and produce a gap report.

    Returns 0 when all required surfaces are present, 1 otherwise.
    """
    gap_report = build_gap_report(project_root)

    if json_output:
        json.dump(gap_report.model_dump(), sys.stdout, indent=2)
        sys.stdout.write("\n")
    else:
        _print_human_report(gap_report)

    return 0 if gap_report.passed else 1


if __name__ == "__main__":
    json_flag = "--json" in sys.argv
    sys.exit(run_doc_coverage(json_output=json_flag))
