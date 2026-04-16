"""Version sync helpers and audit evidence aggregation for CLI commands."""

from __future__ import annotations

import re
from pathlib import Path
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from gzkit.core.validation_rules import ValidationError

from gzkit.ledger import Ledger

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
    if not pyproject.is_file():
        return None
    for line in pyproject.read_text(encoding="utf-8").splitlines():
        m = re.match(r'^version\s*=\s*"(\d+\.\d+\.\d+)"', line)
        if m:
            return m.group(1)
    return None


def compute_patch_increment(current_version: str) -> str:
    """Compute ``X.Y.(Z+1)`` from a semver string."""
    parts = _parse_semver_tuple(current_version)
    return f"{parts[0]}.{parts[1]}.{parts[2] + 1}"


def sync_project_version(project_root: Path, new_version: str) -> list[str]:
    """Bump version in pyproject.toml, __init__.py, and README badge.

    Returns a list of files that were updated (relative to *project_root*).
    """
    updated: list[str] = []

    # pyproject.toml
    pyproject = project_root / "pyproject.toml"
    if pyproject.is_file():
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
    if init_py.is_file():
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
    if readme.is_file():
        old = readme.read_text(encoding="utf-8")
        new = _VERSION_BADGE_RE.sub(rf"\g<1>{new_version}\2", old)
        if new != old:
            readme.write_text(new, encoding="utf-8")
            updated.append("README.md")

    return updated


def validate_version_consistency(project_root: Path) -> list[ValidationError]:
    """Assert pyproject.toml, __init__.py, and README badge versions all match.

    Returns a list of ``ValidationError`` for each file whose version
    disagrees with pyproject.toml (the source of truth).
    """
    from gzkit.core.validation_rules import ValidationError  # noqa: PLC0415

    canonical = _read_current_project_version(project_root)
    if canonical is None:
        return []

    errors: list[ValidationError] = []

    # __init__.py
    init_py = project_root / "src" / "gzkit" / "__init__.py"
    if init_py.is_file():
        text = init_py.read_text(encoding="utf-8")
        m = re.search(r'^__version__\s*=\s*"(\d+\.\d+\.\d+)"', text, re.MULTILINE)
        if m and m.group(1) != canonical:
            errors.append(
                ValidationError(
                    type="version_sync",
                    artifact="src/gzkit/__init__.py",
                    message=(
                        f"__init__.py version {m.group(1)} does not match "
                        f"pyproject.toml version {canonical}"
                    ),
                )
            )

    # README badge
    readme = project_root / "README.md"
    if readme.is_file():
        text = readme.read_text(encoding="utf-8")
        m = _VERSION_BADGE_RE.search(text)
        if m:
            badge_ver_match = re.search(r"version-(\d+\.\d+\.\d+)", m.group(0))
            if badge_ver_match and badge_ver_match.group(1) != canonical:
                errors.append(
                    ValidationError(
                        type="version_sync",
                        artifact="README.md",
                        message=(
                            f"README.md badge version {badge_ver_match.group(1)} does not match "
                            f"pyproject.toml version {canonical}"
                        ),
                    )
                )

    return errors


def aggregate_audit_evidence(
    ledger: Ledger,
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
    # OBPI completions -- enumerate child OBPIs from graph
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

    # Gate results -- query gate_checked events for the ADR
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

    # Attestation -- latest attested event
    attested_events = ledger.query(event_type="attested", artifact_id=adr_id)
    attestation: dict[str, Any] | None = None
    if attested_events:
        latest = attested_events[-1]
        attestation = {
            "by": latest.extra.get("by", "unknown"),
            "status": latest.extra.get("status", "unknown"),
            "ts": latest.ts,
        }

    # Closeout -- latest closeout_initiated event
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
