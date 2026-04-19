"""Plan-audit CLI: structural prerequisite checks for OBPI plan alignment."""

import json
import re
import sys
from datetime import UTC, datetime
from pathlib import Path

from gzkit.commands.common import console


def _canonicalize_obpi_id(project_root: Path, obpi_id: str) -> str:
    """Expand a short-form OBPI ID to its full slug via the ledger graph.

    GHI #187 — the plan-audit writer previously persisted the raw input
    verbatim (e.g. ``OBPI-0.0.16-05``) while ``gz obpi pipeline`` wrote the
    full slug (``OBPI-0.0.16-05-status-vocab-mapping``) into the pipeline
    marker. ``pipeline-gate.py`` compares the two literals and blocks on
    mismatch. Canonicalizing at the writer closes the mismatch class for
    this layer — same fix shape as GHI #114's ``resolve_obpi`` repair.

    Returns the input unchanged when the ID cannot be resolved through the
    graph (missing brief, uninitialized ledger, etc.) so the surrounding
    gap-check still surfaces a clear "brief not found" message instead of
    an opaque resolver error.
    """
    from gzkit.commands.common import GzCliError, resolve_obpi
    from gzkit.config import load_config
    from gzkit.ledger import Ledger

    try:
        config = load_config()
        ledger = Ledger(project_root / config.paths.ledger)
        canonical, _ = resolve_obpi(project_root, config, ledger, obpi_id)
    except (GzCliError, OSError, ValueError):
        return obpi_id
    return canonical


def plan_audit_cmd(obpi_id: str, as_json: bool) -> None:
    """Run structural prerequisite checks for plan-audit and write receipt."""
    from gzkit.commands.common import ensure_initialized, get_project_root

    ensure_initialized()
    project_root = get_project_root()

    # GHI #187: canonicalize short-form input to the full slug before any
    # downstream lookup or receipt write. This keeps the plan-audit receipt
    # in lockstep with the pipeline marker's obpi_id.
    obpi_id = _canonicalize_obpi_id(project_root, obpi_id)

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

    # 4. Find plan file (dual-scan project-local + ~/.claude/plans/, see #128)
    from gzkit.pipeline_markers import find_plan_for_obpi, pipeline_plans_dir

    plans_dir = pipeline_plans_dir(project_root)
    plan_file = find_plan_for_obpi(project_root, obpi_id)
    if not plan_file:
        gaps.append(f"No plan file found for {obpi_id} in .claude/plans/ or ~/.claude/plans/")

    # 5. Path overlap check (plan files must stay within brief allowed paths)
    target_allowed: list[str] | None = None
    if brief_path and plan_file:
        target_allowed = _extract_allowed_paths(brief_path)
        if target_allowed is not None:
            plan_paths = _extract_plan_paths(plan_file)
            for p in plan_paths:
                if not _path_within_allowed(p, target_allowed):
                    gaps.append(f"Plan references path outside brief scope: {p}")

    # 6. Sibling-ADR scope-collision scan (GHI #152 — advisory, not gap-producing).
    collisions: list[dict[str, str | list[str]]] = []
    if brief_path and adr_id:
        allowed_for_scan = (
            target_allowed
            if target_allowed is not None
            else (_extract_allowed_paths(brief_path) or [])
        )
        if allowed_for_scan:
            collisions = _scan_sibling_adr_collisions(
                project_root=project_root,
                target_adr_id=adr_id,
                target_obpi_id=obpi_id,
                target_allowed=allowed_for_scan,
            )

    # Write receipt and emit output
    _emit_result(obpi_id, gaps, plans_dir, plan_file, as_json, collisions)


def _emit_result(
    obpi_id: str,
    gaps: list[str],
    plans_dir: Path,
    plan_file: Path | None,
    as_json: bool,
    collisions: list[dict[str, str | list[str]]] | None = None,
) -> None:
    """Write receipt file and emit human or JSON output."""
    from gzkit.pipeline_markers import pipeline_receipt_path

    verdict = "PASS" if not gaps else "FAIL"
    receipt: dict[str, object] = {
        "obpi_id": obpi_id,
        "timestamp": datetime.now(UTC).isoformat(),
        "verdict": verdict,
        "plan_file": plan_file.name if plan_file else None,
        "gaps_found": len(gaps),
    }
    if gaps:
        receipt["gaps"] = gaps
    if collisions:
        receipt["scope_collisions"] = collisions

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
        if collisions:
            console.print(
                f"[yellow]DRIFTED -- scope-collision:[/yellow] "
                f"{len(collisions)} sibling-ADR overlap(s) detected (advisory):"
            )
            for c in collisions:
                contested = c["contested_paths"]
                paths = ", ".join(contested) if isinstance(contested, list) else ""
                console.print(f"  - {c['sibling_adr']} / {c['sibling_obpi']} -- contested: {paths}")
        console.print(f"  Receipt: {receipt_path}")

    if verdict == "FAIL":
        sys.exit(1)


_OBPI_SEMVER_RE = re.compile(r"^OBPI-(\d+\.\d+\.\d+)-")


def _derive_adr_id(obpi_id: str) -> str | None:
    """Derive ADR-X.Y.Z from OBPI-X.Y.Z-NN or OBPI-X.Y.Z-NN-<slug> (GHI #187).

    Both the short form and the full slug map to the same ADR — the semver
    triple after the ``OBPI-`` prefix. A prior ``rsplit("-", 1)`` variant
    broke on full slugs like ``OBPI-0.0.16-05-status-vocab-mapping`` because
    the last segment was the slug tail, not the item number.
    """
    match = _OBPI_SEMVER_RE.match(obpi_id)
    if match is None:
        return None
    return f"ADR-{match.group(1)}"


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
    """Legacy single-directory plan finder retained for backwards compat.

    Prefer :func:`gzkit.pipeline_markers.find_plan_for_obpi`, which scans both
    the project-local and global plan directories (see #128).
    """
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


_ALLOWED_HEADING_RE = re.compile(r"^##\s+ALLOWED\s+PATHS(\s*\(.*?\))?\s*$", re.IGNORECASE)
_BULLET_PATH_RE = re.compile(r"^\s*-\s*`([^`]+)`")


def _extract_allowed_paths(brief_path: Path) -> list[str] | None:
    """Extract allowed paths from an OBPI brief.

    Accepts ``## Allowed Paths`` and ``## ALLOWED PATHS`` (and parenthesized
    lane suffixes like ``## ALLOWED PATHS (Foundational)``). Path bullets are
    read from the first backtick-delimited token on each bullet line, so
    trailing ``-- commentary`` is ignored.
    """
    content = brief_path.read_text(encoding="utf-8")
    in_allowed = False
    paths: list[str] = []
    for line in content.splitlines():
        if _ALLOWED_HEADING_RE.match(line):
            in_allowed = True
            continue
        if in_allowed and line.startswith("## "):
            break
        if in_allowed:
            match = _BULLET_PATH_RE.match(line)
            if match:
                path = match.group(1).strip()
                if path:
                    paths.append(path)
    return paths if paths else None


def _paths_overlap(a: str, b: str) -> bool:
    """Return True when two declared paths share a directory-prefix relationship.

    Separator-aware: ``src/gzkit/a`` does not overlap ``src/gzkit/arb``.
    """
    a = a.rstrip("/")
    b = b.rstrip("/")
    if not a or not b:
        return False
    if a == b:
        return True
    return b.startswith(a + "/") or a.startswith(b + "/")


def _is_specific_path(path: str) -> bool:
    """A path is specific enough to yield useful collision signal.

    Root-level globs like ``src/``, ``tests/``, ``docs/``, or two-component
    paths like ``src/gzkit/`` are too broad -- every brief targets one of
    them. We only flag overlaps whose contested path descends at least three
    components deep.
    """
    parts = [p for p in path.rstrip("/").split("/") if p]
    return len(parts) >= 3


_ADR_ID_RE = re.compile(r"^(ADR-\d+\.\d+\.\d+)")


def _adr_id_from_dir(name: str) -> str | None:
    """Recover the canonical ``ADR-X.Y.Z`` id from a package directory name."""
    match = _ADR_ID_RE.match(name)
    return match.group(1) if match else None


def _obpi_id_from_brief_name(name: str) -> str:
    """Strip the ``.md`` extension to recover the OBPI slug."""
    if name.endswith(".md"):
        return name[:-3]
    return name


def _contested_paths_between(target_allowed: list[str], sibling_allowed: list[str]) -> list[str]:
    """Return specific (non-root-glob) paths contested between two allowed-path sets."""
    contested: list[str] = []
    for tp in target_allowed:
        for sp in sibling_allowed:
            if _paths_overlap(tp, sp):
                specific = sp if len(sp) >= len(tp) else tp
                if specific not in contested:
                    contested.append(specific)
    return [p for p in contested if _is_specific_path(p)]


def _sibling_obpi_collisions(
    pkg_dir: Path,
    sibling_adr: str,
    target_obpi_id: str,
    target_allowed: list[str],
) -> list[dict[str, str | list[str]]]:
    """Report allowed-path collisions against every sibling OBPI brief under ``pkg_dir``."""
    obpis_dir = pkg_dir / "obpis"
    if not obpis_dir.exists():
        return []
    collisions: list[dict[str, str | list[str]]] = []
    for brief in obpis_dir.glob("*.md"):
        sibling_obpi = _obpi_id_from_brief_name(brief.name)
        if sibling_obpi == target_obpi_id:
            continue
        sibling_allowed = _extract_allowed_paths(brief)
        if not sibling_allowed:
            continue
        specific_contested = _contested_paths_between(target_allowed, sibling_allowed)
        if specific_contested:
            collisions.append(
                {
                    "sibling_adr": sibling_adr,
                    "sibling_obpi": sibling_obpi,
                    "contested_paths": specific_contested,
                }
            )
    return collisions


def _scan_sibling_adr_collisions(
    project_root: Path,
    target_adr_id: str,
    target_obpi_id: str,
    target_allowed: list[str],
) -> list[dict[str, str | list[str]]]:
    """Scan sibling ADR packages for OBPI briefs whose allowed-paths overlap.

    GHI #152 -- plan-audit previously verified ADR<->OBPI<->Plan alignment but
    did not cross-reference sibling ADRs. OBPI-0.25.0-33 and 9 OBPI-0.27.0
    briefs claimed overlapping source files; both receipts passed. This scan
    surfaces the overlap advisorily so the agent can record a resolution
    narrative before attestation.

    Same-ADR siblings are excluded (intra-ADR scope conflicts are governed
    by the existing brief-authoring discipline). Overlaps whose contested
    paths are all root-level globs are excluded as noise.
    """
    adr_base = project_root / "docs" / "design" / "adr"
    if not adr_base.exists():
        return []

    collisions: list[dict[str, str | list[str]]] = []
    for series_dir in adr_base.iterdir():
        if not series_dir.is_dir():
            continue
        for pkg_dir in series_dir.iterdir():
            if not pkg_dir.is_dir() or not pkg_dir.name.startswith("ADR-"):
                continue
            sibling_adr = _adr_id_from_dir(pkg_dir.name)
            if sibling_adr is None or sibling_adr == target_adr_id:
                continue
            collisions.extend(
                _sibling_obpi_collisions(pkg_dir, sibling_adr, target_obpi_id, target_allowed)
            )
    return collisions


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
