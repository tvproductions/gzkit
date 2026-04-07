"""ADR coverage analysis functions for audit-check and covers-check commands."""

import ast
import re
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import console
from gzkit.traceability import CoverageEntry, compute_coverage, scan_test_tree
from gzkit.triangle import ReqId, scan_briefs


def _extract_adr_semver(adr_id: str) -> str | None:
    """Extract X.Y.Z semantic version from an ADR identifier."""
    match = re.match(r"^ADR-(\d+\.\d+\.\d+)", adr_id)
    return match.group(1) if match else None


def _compute_adr_coverage(
    project_root: Path, adr_id: str, adr_dir: Path | None = None
) -> dict[str, Any]:
    """Compute requirement coverage for an ADR's REQs (advisory, non-blocking)."""
    empty: dict[str, Any] = {
        "total_reqs": 0,
        "covered_reqs": 0,
        "uncovered_reqs": 0,
        "coverage_percent": 0.0,
        "by_obpi": [],
        "uncovered": [],
    }
    semver = _extract_adr_semver(adr_id)
    if not semver:
        return empty

    if adr_dir is None:
        adr_dir = project_root / "docs" / "design" / "adr"
    tests_dir = project_root / "tests"
    if not adr_dir.is_dir() or not tests_dir.is_dir():
        return empty

    discovered = scan_briefs(adr_dir)
    linkage_records = scan_test_tree(tests_dir)
    report = compute_coverage(discovered, linkage_records)

    prefix = f"REQ-{semver}-"
    adr_entries = [e for e in report.entries if e.req_id.startswith(prefix)]
    if not adr_entries:
        return empty

    total = len(adr_entries)
    covered = sum(1 for e in adr_entries if e.covered)

    obpi_groups: dict[str, list[CoverageEntry]] = {}
    for entry in adr_entries:
        parsed = ReqId.parse(entry.req_id)
        obpi_key = f"OBPI-{parsed.semver}-{parsed.obpi_item}"
        obpi_groups.setdefault(obpi_key, []).append(entry)

    by_obpi = []
    for obpi_key in sorted(obpi_groups):
        group = obpi_groups[obpi_key]
        g_total = len(group)
        g_covered = sum(1 for e in group if e.covered)
        by_obpi.append(
            {
                "obpi": obpi_key,
                "total_reqs": g_total,
                "covered_reqs": g_covered,
                "uncovered_reqs": g_total - g_covered,
                "coverage_percent": round(g_covered / g_total * 100, 1) if g_total > 0 else 0.0,
            }
        )

    return {
        "total_reqs": total,
        "covered_reqs": covered,
        "uncovered_reqs": total - covered,
        "coverage_percent": round(covered / total * 100, 1),
        "by_obpi": by_obpi,
        "uncovered": [
            {"req_id": e.req_id, "severity": "advisory"} for e in adr_entries if not e.covered
        ],
    }


def _print_coverage_section(
    coverage: dict[str, Any],
    advisory_findings: list[dict[str, Any]] | None = None,
) -> None:
    """Render human-readable coverage section for audit-check output."""
    total = coverage["total_reqs"]
    if total == 0:
        console.print("\n[bold]Coverage:[/bold] No REQs found for this ADR.")
        return

    covered = coverage["covered_reqs"]
    pct = coverage["coverage_percent"]
    console.print(f"\n[bold]Coverage:[/bold] {covered}/{total} REQs covered ({pct}%)")
    for row in coverage["by_obpi"]:
        obpi = row["obpi"]
        cov = row["covered_reqs"]
        tot = row["total_reqs"]
        pct_obpi = row["coverage_percent"]
        console.print(f"  {obpi}: {cov}/{tot} ({pct_obpi}%)")

    uncovered = [r for r in coverage.get("uncovered", []) if isinstance(r, dict)]
    if uncovered:
        console.print(f"[red]Uncovered REQs ({len(uncovered)}):[/red]")
        for u in uncovered:
            console.print(f"  - {u['req_id']}")


def _collect_covers_annotations(project_root: Path) -> dict[str, list[str]]:
    """Collect @covers("<target>") annotations from tests/**/*.py."""
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        return {}

    covers: dict[str, list[str]] = {}

    for test_file in sorted(tests_dir.rglob("*.py")):
        content = test_file.read_text(encoding="utf-8")
        rel_path = str(test_file.relative_to(project_root))

        try:
            tree = ast.parse(content)
        except SyntaxError:
            continue

        for node in ast.walk(tree):
            if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
                continue
            for decorator in node.decorator_list:
                if not isinstance(decorator, ast.Call):
                    continue
                if isinstance(decorator.func, ast.Name):
                    decorator_name = decorator.func.id
                elif isinstance(decorator.func, ast.Attribute):
                    decorator_name = decorator.func.attr
                else:
                    continue
                if decorator_name != "covers" or not decorator.args:
                    continue
                target_arg = decorator.args[0]
                if not isinstance(target_arg, ast.Constant) or not isinstance(
                    target_arg.value, str
                ):
                    continue
                target = target_arg.value.strip()
                if not target:
                    continue
                rows = covers.setdefault(target, [])
                if rel_path not in rows:
                    rows.append(rel_path)

    return covers


OBPI_SEMVER_ITEM_RE = re.compile(r"^OBPI-([0-9]+\.[0-9]+\.[0-9]+)-([0-9]{2})(?:-[a-z0-9-]+)?$")
REQ_ID_RE = re.compile(r"\bREQ-[0-9]+\.[0-9]+\.[0-9]+-[0-9]{2}-[0-9]{2}\b")


def _extract_h2_section_lines(content: str, heading: str) -> list[tuple[int, str]]:
    """Return line-numbered content lines for a markdown H2 section."""
    lines = content.splitlines()
    heading_line = f"## {heading}"
    section_start: int | None = None
    for idx, line in enumerate(lines):
        if line.strip() == heading_line:
            section_start = idx + 1
            break
    if section_start is None:
        return []

    section_end = len(lines)
    for idx in range(section_start, len(lines)):
        if lines[idx].startswith("## "):
            section_end = idx
            break

    return [(line_no + 1, lines[line_no]) for line_no in range(section_start, section_end)]


def _req_prefix_for_obpi(obpi_id: str) -> str | None:
    """Return expected REQ prefix for an OBPI (REQ-<semver>-<item>-)."""
    match = OBPI_SEMVER_ITEM_RE.match(obpi_id)
    if not match:
        return None
    semver, item = match.groups()
    return f"REQ-{semver}-{item}-"


def _extract_obpi_requirement_targets(
    project_root: Path,
    obpi_file: Path,
    obpi_id: str,
) -> dict[str, Any]:
    """Extract REQ targets and acceptance-criteria gaps from an OBPI brief."""
    content = obpi_file.read_text(encoding="utf-8")
    section_lines = _extract_h2_section_lines(content, "Acceptance Criteria")
    req_prefix = _req_prefix_for_obpi(obpi_id)

    requirement_targets: set[str] = set()
    criteria_without_req_ids: list[dict[str, Any]] = []
    invalid_requirement_targets: list[dict[str, Any]] = []

    for line_no, line in section_lines:
        match = re.match(r"^\s*-\s*\[[ xX]\]\s*(.+?)\s*$", line)
        if not match:
            continue
        criterion_text = match.group(1).strip()
        if not criterion_text:
            continue

        req_ids = sorted(set(REQ_ID_RE.findall(criterion_text)))
        if not req_ids:
            criteria_without_req_ids.append(
                {
                    "obpi": obpi_id,
                    "file": str(obpi_file.relative_to(project_root)),
                    "line": line_no,
                    "text": criterion_text,
                }
            )
            continue

        for req_id in req_ids:
            requirement_targets.add(req_id)
            if req_prefix and not req_id.startswith(req_prefix):
                invalid_requirement_targets.append(
                    {
                        "obpi": obpi_id,
                        "file": str(obpi_file.relative_to(project_root)),
                        "line": line_no,
                        "req": req_id,
                        "expected_prefix": req_prefix,
                    }
                )

    return {
        "requirement_targets": sorted(requirement_targets),
        "criteria_without_req_ids": criteria_without_req_ids,
        "invalid_requirement_targets": invalid_requirement_targets,
    }


def _collect_adr_requirement_targets(
    project_root: Path,
    obpi_files: dict[str, Path],
) -> tuple[list[str], list[dict[str, Any]], list[dict[str, Any]]]:
    """Collect requirement targets and REQ-shape issues for an ADR OBPI set."""
    requirement_targets: set[str] = set()
    criteria_without_req_ids: list[dict[str, Any]] = []
    invalid_requirement_targets: list[dict[str, Any]] = []

    for obpi_id, obpi_file in sorted(obpi_files.items()):
        parsed = _extract_obpi_requirement_targets(project_root, obpi_file, obpi_id)
        requirement_targets.update(parsed["requirement_targets"])
        criteria_without_req_ids.extend(parsed["criteria_without_req_ids"])
        invalid_requirement_targets.extend(parsed["invalid_requirement_targets"])

    return (
        sorted(requirement_targets),
        criteria_without_req_ids,
        invalid_requirement_targets,
    )


def _build_covers_rows(
    adr_id: str,
    expected_targets: list[str],
    covers: dict[str, list[str]],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Build per-target coverage rows and return missing targets."""
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for target in expected_targets:
        tests = covers.get(target, [])
        rows.append(
            {
                "target": target,
                "target_type": (
                    "adr" if target == adr_id else "obpi" if target.startswith("OBPI-") else "req"
                ),
                "covered": bool(tests),
                "tests": tests,
            }
        )
        if not tests:
            missing.append(target)
    return rows, missing


def _print_adr_covers_check_result(result: dict[str, Any]) -> None:
    """Render human-readable output for adr covers-check."""
    adr_id = str(result["adr"])
    passed = bool(result["passed"])
    missing = cast(list[str], result["missing_targets"])
    criteria_without_req_ids = cast(list[dict[str, Any]], result["criteria_without_req_ids"])
    invalid_requirement_targets = cast(list[dict[str, Any]], result["invalid_requirement_targets"])
    unmatched_targets = cast(list[str], result["unmatched_targets"])

    console.print(f"[bold]ADR covers-check:[/bold] {adr_id}")
    if passed:
        console.print("[green]PASS[/green] All ADR/OBPI/REQ targets have @covers annotations.")
    if missing:
        console.print("[red]FAIL[/red] Missing @covers annotations:")
        for target in missing:
            console.print(f"  - {target}")
    if criteria_without_req_ids:
        console.print("[red]FAIL[/red] Acceptance criteria missing REQ IDs:")
        for row in criteria_without_req_ids:
            console.print(f"  - {row['obpi']}:{row['line']} -> {row['text']}")
    if invalid_requirement_targets:
        console.print("[red]FAIL[/red] REQ IDs with wrong OBPI scope:")
        for row in invalid_requirement_targets:
            console.print(
                f"  - {row['obpi']}:{row['line']} -> {row['req']} "
                f"(expected {row['expected_prefix']}*)"
            )
    if unmatched_targets:
        console.print("[yellow]Unmatched @covers targets (not linked to this ADR):[/yellow]")
        for target in unmatched_targets:
            console.print(f"  - {target}")
