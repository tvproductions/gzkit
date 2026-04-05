"""OBPI audit CLI: deterministic evidence gathering for OBPI briefs."""

import json
import re
import subprocess
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import console


def obpi_audit_cmd(obpi_id: str | None, adr_id: str | None, as_json: bool) -> None:
    """Gather evidence for OBPI brief and append audit entry to ledger."""
    from gzkit.commands.common import ensure_initialized, get_project_root

    ensure_initialized()
    project_root = get_project_root()

    if adr_id and not obpi_id:
        _audit_all_for_adr(project_root, adr_id, as_json)
        return

    if not obpi_id:
        console.print("[red]ERROR:[/red] Provide OBPI identifier or --adr flag")
        sys.exit(1)

    if not as_json:
        derived_adr = _derive_adr_id(obpi_id)
        if derived_adr:
            adr_dir = _find_adr_dir(project_root, derived_adr)
            if adr_dir:
                prior = _read_prior_audits(adr_dir)
                if obpi_id in prior:
                    _print_prior_state({obpi_id: prior[obpi_id]}, project_root)

    result = _audit_single(project_root, obpi_id)

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        _print_result(result)

    if any(c["result"] == "FAIL" for c in result.get("criteria_evaluated", [])):
        sys.exit(1)


def _audit_all_for_adr(project_root: Path, adr_id: str, as_json: bool) -> None:
    """Audit all OBPI briefs for an ADR."""
    adr_dir = _find_adr_dir(project_root, adr_id)
    if not adr_dir:
        console.print(f"[red]ERROR:[/red] ADR directory not found for {adr_id}")
        sys.exit(1)

    obpis_dir = adr_dir / "obpis"
    if not obpis_dir.exists():
        console.print(f"[yellow]No OBPIs found for {adr_id}[/yellow]")
        return

    if not as_json:
        prior = _read_prior_audits(adr_dir)
        _print_prior_state(prior, project_root)

    results = []
    for brief in sorted(obpis_dir.glob("OBPI-*.md")):
        oid = _extract_obpi_id(brief)
        if oid:
            results.append(_audit_single(project_root, oid))

    if as_json:
        print(json.dumps({"adr_id": adr_id, "audits": results}, indent=2))
    else:
        for r in results:
            _print_result(r)
            console.print("")


def _audit_single(project_root: Path, obpi_id: str) -> dict:
    """Audit a single OBPI and append ledger entry."""
    adr_id = _derive_adr_id(obpi_id)
    adr_dir = _find_adr_dir(project_root, adr_id) if adr_id else None

    brief_path = _find_brief(adr_dir, obpi_id) if adr_dir else None
    brief_status = "unknown"
    lane = "Lite"
    if brief_path:
        brief_status, lane = _read_brief_meta(brief_path)

    tests_found = _find_tests(project_root, adr_id or "", obpi_id)
    tests_passed, test_count = _run_tests(project_root, tests_found)
    coverage_pct = _measure_coverage(project_root, tests_found)
    covers_tags = _find_covers_tags(project_root, adr_id or "")

    criteria = _build_criteria(tests_found, tests_passed, test_count, coverage_pct)

    entry = _build_entry(
        obpi_id,
        adr_id,
        brief_status,
        lane,
        tests_found,
        tests_passed,
        test_count,
        coverage_pct,
        covers_tags,
        criteria,
    )

    if adr_dir:
        _append_ledger(adr_dir, entry)

    return entry


def _build_criteria(
    tests_found: list[Path],
    tests_passed: bool,
    test_count: int,
    coverage_pct: float | None,
) -> list[dict]:
    """Build the criteria evaluation list."""
    criteria: list[dict] = []
    criteria.append(
        {
            "criterion": "Test files exist",
            "result": "PASS" if tests_found else "FAIL",
            "evidence": ", ".join(str(t) for t in tests_found) if tests_found else "none found",
        }
    )
    criteria.append(
        {
            "criterion": "Tests pass",
            "result": "PASS" if tests_passed else "FAIL",
            "evidence": f"{test_count} tests" if test_count else "no tests run",
        }
    )
    criteria.append(
        {
            "criterion": "Coverage >= 40%",
            "result": "PASS" if coverage_pct is not None and coverage_pct >= 40.0 else "FAIL",
            "evidence": f"{coverage_pct:.1f}%" if coverage_pct is not None else "not measured",
        }
    )
    return criteria


def _build_entry(
    obpi_id: str,
    adr_id: str | None,
    brief_status: str,
    lane: str,
    tests_found: list[Path],
    tests_passed: bool,
    test_count: int,
    coverage_pct: float | None,
    covers_tags: list[str],
    criteria: list[dict],
) -> dict:
    """Build the audit ledger entry dict."""
    return {
        "type": "obpi-audit",
        "timestamp": datetime.now(UTC).isoformat(),
        "obpi_id": obpi_id,
        "adr_id": adr_id or "unknown",
        "brief_status_before": brief_status,
        "brief_status_after": brief_status,
        "lane": lane,
        "evidence": {
            "tests_found": [str(t) for t in tests_found],
            "tests_passed": tests_passed,
            "test_count": test_count,
            "coverage_percent": coverage_pct,
            "coverage_threshold": 40,
            "covers_tags": covers_tags,
        },
        "criteria_evaluated": criteria,
        "action_taken": "none",
        "agent": "cli",
        "session_id": None,
    }


def _print_result(result: dict) -> None:
    """Print audit result in human-readable format."""
    obpi = result.get("obpi_id", "unknown")
    criteria = result.get("criteria_evaluated", [])
    all_pass = all(c["result"] == "PASS" for c in criteria)
    status = "[green]PASS[/green]" if all_pass else "[red]FAIL[/red]"
    console.print(f"  {obpi}: {status}")
    for c in criteria:
        icon = "[green]PASS[/green]" if c["result"] == "PASS" else "[red]FAIL[/red]"
        console.print(f"    {icon} {c['criterion']}: {c['evidence']}")


def _derive_adr_id(obpi_id: str) -> str | None:
    """Derive ADR-X.Y.Z from OBPI-X.Y.Z-NN."""
    if not obpi_id.startswith("OBPI-"):
        return None
    suffix = obpi_id[5:]
    parts = suffix.rsplit("-", 1)
    return f"ADR-{parts[0]}" if len(parts) == 2 else None


def _find_adr_dir(project_root: Path, adr_id: str) -> Path | None:
    """Find ADR package directory."""
    adr_base = project_root / "docs" / "design" / "adr"
    if not adr_base.exists():
        return None
    for series_dir in adr_base.iterdir():
        if not series_dir.is_dir():
            continue
        for pkg_dir in series_dir.iterdir():
            if pkg_dir.is_dir() and pkg_dir.name.startswith(adr_id):
                return pkg_dir
    return None


def _find_brief(adr_dir: Path, obpi_id: str) -> Path | None:
    """Find OBPI brief file."""
    obpis_dir = adr_dir / "obpis"
    if not obpis_dir.exists():
        return None
    for brief in obpis_dir.glob("*.md"):
        if obpi_id in brief.name:
            return brief
    return None


def _extract_obpi_id(brief_path: Path) -> str | None:
    """Extract OBPI ID from brief filename."""
    m = re.search(r"(OBPI-\d+\.\d+\.\d+-\d+)", brief_path.name)
    return m.group(1) if m else None


def _read_brief_meta(brief_path: Path) -> tuple[str, str]:
    """Read status and lane from brief frontmatter."""
    content = brief_path.read_text(encoding="utf-8")
    status = "unknown"
    lane = "Lite"
    for line in content.splitlines():
        if line.startswith("status:"):
            status = line.split(":", 1)[1].strip()
        if line.startswith("lane:"):
            lane = line.split(":", 1)[1].strip()
    return status, lane


def _find_tests(project_root: Path, adr_id: str, obpi_id: str) -> list[Path]:
    """Find test files via @covers tag or OBPI reference."""
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        return []
    found: list[Path] = []
    for test_file in tests_dir.rglob("test_*.py"):
        try:
            content = test_file.read_text(encoding="utf-8")
            if adr_id in content or obpi_id in content:
                found.append(test_file.relative_to(project_root))
        except OSError:
            continue
    return found


def _run_tests(project_root: Path, test_files: list[Path]) -> tuple[bool, int]:
    """Run discovered tests and return (passed, count)."""
    if not test_files:
        return False, 0
    try:
        result = subprocess.run(
            ["uv", "run", "-m", "unittest", "-q"] + [str(f) for f in test_files],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(project_root),
            timeout=120,
        )
        import contextlib

        count = 0
        for line in result.stderr.splitlines():
            if "Ran " in line and " test" in line:
                with contextlib.suppress(ValueError, IndexError):
                    count = int(line.split("Ran ")[1].split(" test")[0])
        return result.returncode == 0, count
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, 0


def _measure_coverage(project_root: Path, test_files: list[Path]) -> float | None:
    """Measure coverage for test files."""
    if not test_files:
        return None
    try:
        subprocess.run(
            ["uv", "run", "coverage", "run", "--source=src", "-m", "unittest", "-q"]
            + [str(f) for f in test_files],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(project_root),
            timeout=120,
        )
        result = subprocess.run(
            ["uv", "run", "coverage", "report", "--format=total"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(project_root),
            timeout=30,
        )
        if result.returncode == 0:
            try:
                return float(result.stdout.strip())
            except ValueError:
                return None
    except (subprocess.SubprocessError, FileNotFoundError):
        pass
    return None


def _find_covers_tags(project_root: Path, adr_id: str) -> list[str]:
    """Find @covers decorators referencing this ADR."""
    if not adr_id:
        return []
    found: list[str] = []
    tests_dir = project_root / "tests"
    if not tests_dir.exists():
        return found
    for test_file in tests_dir.rglob("*.py"):
        try:
            content = test_file.read_text(encoding="utf-8")
            for line in content.splitlines():
                if "@covers" in line and adr_id in line:
                    found.append(line.strip())
        except OSError:
            continue
    return found


def _append_ledger(adr_dir: Path, entry: dict) -> None:
    """Append audit entry to ADR-local JSONL ledger."""
    logs_dir = adr_dir / "logs"
    logs_dir.mkdir(parents=True, exist_ok=True)
    ledger_file = logs_dir / "obpi-audit.jsonl"
    with ledger_file.open("a", encoding="utf-8") as f:
        f.write(json.dumps(entry, separators=(",", ":")) + "\n")


def _read_prior_audits(adr_dir: Path) -> dict[str, dict]:
    """Read the last audit entry per OBPI from the ADR-local JSONL ledger."""
    ledger_file = adr_dir / "logs" / "obpi-audit.jsonl"
    if not ledger_file.is_file():
        return {}
    latest: dict[str, dict] = {}
    for line in ledger_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            entry = json.loads(line)
            if entry.get("type") == "obpi-audit":
                obpi_id = entry.get("obpi_id", "")
                if obpi_id:
                    latest[obpi_id] = entry
        except json.JSONDecodeError:
            continue
    return latest


def _is_stale(project_root: Path, timestamp: str) -> bool:
    """Check if commits exist after the audit timestamp on src/ and tests/."""
    try:
        result = subprocess.run(
            ["git", "log", "--oneline", f"--since={timestamp}", "--", "src/", "tests/"],
            capture_output=True,
            text=True,
            encoding="utf-8",
            cwd=str(project_root),
            timeout=10,
        )
        return bool(result.stdout.strip())
    except (subprocess.SubprocessError, FileNotFoundError):
        return True


def _print_prior_state(prior_audits: dict[str, dict], project_root: Path) -> None:
    """Print prior audit state table before fresh analysis."""
    if not prior_audits:
        console.print("[dim]No prior audit entries found.[/dim]\n")
        return

    from rich.table import Table

    table = Table(title="Prior Audit State")
    table.add_column("OBPI", style="cyan")
    table.add_column("Last Audit", style="dim")
    table.add_column("Result", justify="center")
    table.add_column("Coverage", justify="right")
    table.add_column("Stale?", justify="center")

    for obpi_id in sorted(prior_audits.keys()):
        entry = prior_audits[obpi_id]
        ts = entry.get("timestamp", "unknown")
        date_str = ts[:10] if len(ts) >= 10 else ts

        criteria = entry.get("criteria_evaluated", [])
        if criteria:
            all_pass = all(c.get("result") == "PASS" for c in criteria)
            result_str = "[green]PASS[/green]" if all_pass else "[red]FAIL[/red]"
        else:
            result_str = "[dim]N/A[/dim]"

        evidence = entry.get("evidence", {})
        cov = evidence.get("coverage_percent")
        cov_str = f"{cov:.1f}%" if cov is not None else "N/A"

        stale = _is_stale(project_root, ts)
        stale_str = "[yellow]yes[/yellow]" if stale else "[green]no[/green]"

        table.add_row(obpi_id, date_str, result_str, cov_str, stale_str)

    console.print(table)
    console.print("")
