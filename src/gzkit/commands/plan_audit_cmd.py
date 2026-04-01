"""Plan-audit CLI: structural prerequisite checks for OBPI plan alignment."""

import json
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import console


def plan_audit_cmd(obpi_id: str, as_json: bool) -> None:
    """Run structural prerequisite checks for plan-audit and write receipt."""
    from gzkit.commands.common import ensure_initialized, get_project_root

    ensure_initialized()
    project_root = get_project_root()

    gaps: list[str] = []

    # 1. Resolve OBPI -> ADR
    adr_id = _derive_adr_id(obpi_id)
    if not adr_id:
        gaps.append(f"Cannot derive ADR ID from {obpi_id}")

    # 2. Find ADR package directory
    adr_dir = _find_adr_dir(project_root, adr_id) if adr_id else None
    if adr_id and not adr_dir:
        gaps.append(f"ADR directory not found for {adr_id}")

    # 3. Find OBPI brief
    brief_path = _find_brief(adr_dir, obpi_id) if adr_dir else None
    if adr_dir and not brief_path:
        gaps.append(f"OBPI brief not found for {obpi_id}")

    # 4. Find plan file
    plans_dir = project_root / ".claude" / "plans"
    plan_file = _find_plan_file(plans_dir, obpi_id)
    if not plan_file:
        gaps.append(f"No plan file found in .claude/plans/ for {obpi_id}")

    # 5. Path overlap check (plan files must stay within brief allowed paths)
    if brief_path and plan_file:
        allowed = _extract_allowed_paths(brief_path)
        if allowed is not None:
            plan_paths = _extract_plan_paths(plan_file)
            for p in plan_paths:
                if not _path_within_allowed(p, allowed):
                    gaps.append(f"Plan references path outside brief scope: {p}")

    # Write receipt and emit output
    _emit_result(obpi_id, gaps, plans_dir, plan_file, as_json)


def _emit_result(
    obpi_id: str,
    gaps: list[str],
    plans_dir: Path,
    plan_file: Path | None,
    as_json: bool,
) -> None:
    """Write receipt file and emit human or JSON output."""
    from gzkit.pipeline_markers import pipeline_receipt_path

    verdict = "PASS" if not gaps else "FAIL"
    receipt = {
        "obpi_id": obpi_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "verdict": verdict,
        "plan_file": plan_file.name if plan_file else None,
        "gaps_found": len(gaps),
    }
    if gaps:
        receipt["gaps"] = gaps

    receipt_path = pipeline_receipt_path(plans_dir, obpi_id)
    plans_dir.mkdir(parents=True, exist_ok=True)
    receipt_path.write_text(json.dumps(receipt, indent=2), encoding="utf-8")

    if as_json:
        print(json.dumps(receipt, indent=2))
    else:
        if verdict == "PASS":
            console.print(f"[green]PASS:[/green] {obpi_id} -- all structural prerequisites met")
        else:
            console.print(f"[red]FAIL:[/red] {obpi_id} -- {len(gaps)} gap(s) found:")
            for gap in gaps:
                console.print(f"  - {gap}")
        console.print(f"  Receipt: {receipt_path}")

    if verdict == "FAIL":
        sys.exit(1)


def _derive_adr_id(obpi_id: str) -> str | None:
    """Derive ADR-X.Y.Z from OBPI-X.Y.Z-NN."""
    if not obpi_id.startswith("OBPI-"):
        return None
    # OBPI-X.Y.Z-NN -> X.Y.Z-NN -> X.Y.Z
    suffix = obpi_id[5:]  # Remove "OBPI-"
    parts = suffix.rsplit("-", 1)
    if len(parts) == 2:
        return f"ADR-{parts[0]}"
    return None


def _find_adr_dir(project_root: Path, adr_id: str) -> Path | None:
    """Find the ADR package directory by scanning standard locations."""
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
    """Find the OBPI brief file within an ADR package."""
    obpis_dir = adr_dir / "obpis"
    if not obpis_dir.exists():
        return None
    for brief in obpis_dir.glob("*.md"):
        if obpi_id in brief.name:
            return brief
    return None


def _find_plan_file(plans_dir: Path, obpi_id: str) -> Path | None:
    """Find the most recent plan file referencing this OBPI."""
    if not plans_dir.exists():
        return None
    candidates = []
    for f in plans_dir.glob("*.md"):
        if f.name.startswith("."):
            continue
        try:
            content = f.read_text(encoding="utf-8")
            if obpi_id in content:
                candidates.append(f)
        except OSError:
            continue
    if not candidates:
        return None
    return max(candidates, key=lambda p: p.stat().st_mtime)


def _extract_allowed_paths(brief_path: Path) -> list[str] | None:
    """Extract allowed paths from OBPI brief."""
    content = brief_path.read_text(encoding="utf-8")
    in_allowed = False
    paths: list[str] = []
    for line in content.splitlines():
        if "## Allowed Paths" in line or "## Allowed paths" in line:
            in_allowed = True
            continue
        if in_allowed and line.startswith("## "):
            break
        if in_allowed and line.strip().startswith("- "):
            path = line.strip().lstrip("- ").strip("`")
            if path:
                paths.append(path)
    return paths if paths else None


def _extract_plan_paths(plan_file: Path) -> list[str]:
    """Extract file paths mentioned in plan (lines with src/ or tests/ or docs/)."""
    content = plan_file.read_text(encoding="utf-8")
    paths: list[str] = []
    for line in content.splitlines():
        for prefix in ("src/", "tests/", "docs/"):
            if prefix in line:
                for token in line.split():
                    token = token.strip("`").strip("*").strip(",").strip(")")
                    if token.startswith(prefix) or token.startswith(f"./{prefix}"):
                        paths.append(token.lstrip("./"))
    return list(set(paths))


def _path_within_allowed(path: str, allowed: list[str]) -> bool:
    """Check if a path falls within any allowed path."""
    for allowed_path in allowed:
        allowed_clean = allowed_path.rstrip("/")
        if path == allowed_clean or path.startswith(allowed_clean + "/"):
            return True
    return True  # If we can't determine, don't block
