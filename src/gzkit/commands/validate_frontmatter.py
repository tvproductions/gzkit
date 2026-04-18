"""Frontmatter-ledger coherence guard (ADR-0.0.16 / OBPI-0.0.16-01).

Compares the four governed frontmatter fields (``id``, ``parent``, ``lane``,
``status``) against the ledger's artifact graph. Keys lookups on filesystem
path only — never on frontmatter ``id:`` (that reproduces GHI #166).

Extracted from ``validate_cmd`` to keep both modules under the 600-line cap.
Shares the canonical ledger semantics API used by ``gz adr report``.
"""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import TYPE_CHECKING

from gzkit.commands.common import console
from gzkit.validate import ValidationError

if TYPE_CHECKING:
    from gzkit.ledger import Ledger

_ADR_ID_PATTERN = re.compile(r"^(ADR-[\d.]+)")
_OBPI_ID_PATTERN = re.compile(r"^(OBPI-\d+\.\d+\.\d+-\d+)")

_RECOVERY_COMMANDS: dict[str, str] = {
    "id": "gz register-adrs --all",
    "parent": "gz register-adrs --all",
    "lane": "gz adr promote <ADR-ID> --lane <canonical-lane>",
    "status": "gz chores run frontmatter-ledger-coherence",
}


def _resolve_ledger_id_from_path(
    artifact_file: Path,
    artifact_type: str,
    graph: dict,
    canonicalize: Callable[[str], str],
) -> str | None:
    """Key lookup on filesystem path only — never on frontmatter ``id:``.

    Keying on ``fm.id`` reproduces GHI #166 (validator silently trusts a
    rewritten id). The filesystem stem is the canonical naming convention:
    ADRs use ``ADR-X.Y.Z-slug`` and OBPIs use ``OBPI-X.Y.Z-NN-slug``.
    """
    stem = artifact_file.stem
    canonical = canonicalize(stem)
    if canonical in graph:
        return canonical
    if stem in graph:
        return stem
    pattern = _ADR_ID_PATTERN if artifact_type == "adr" else _OBPI_ID_PATTERN
    match = pattern.match(stem)
    if match:
        prefix = match.group(1)
        canonical = canonicalize(prefix)
        if canonical in graph:
            return canonical
        if prefix in graph:
            return prefix
    return None


def _field_error(rel_path: str, field: str, ledger_value: str, fm_value: str) -> ValidationError:
    """Construct a frontmatter drift error with ledger/observed values."""
    return ValidationError(
        type="frontmatter",
        artifact=rel_path,
        field=field,
        message=(
            f"Frontmatter {field} '{fm_value}' does not match ledger {field} '{ledger_value}'"
        ),
        ledger_value=ledger_value,
        frontmatter_value=fm_value,
    )


def _check_one_artifact(
    fm: dict,
    ledger_id: str,
    info: dict,
    rel_path: str,
    canonicalize: Callable[[str], str],
    derive_status: Callable[[], str | None],
) -> list[ValidationError]:
    """Compare one file's frontmatter against its ledger entry (four governed fields only).

    ``derive_status`` is a zero-arg callback invoked only when the file has a
    ``status:`` frontmatter key — avoids the heavy status-derivation cost for
    the majority of files that do not carry a status field.
    """
    errors: list[ValidationError] = []
    fm_id = fm.get("id", "")
    if fm_id and canonicalize(fm_id) != ledger_id:
        errors.append(_field_error(rel_path, "id", ledger_id, fm_id))

    fm_parent = fm.get("parent", "")
    ledger_parent = info.get("parent") or ""
    if fm_parent and ledger_parent and canonicalize(fm_parent) != canonicalize(ledger_parent):
        errors.append(_field_error(rel_path, "parent", ledger_parent, fm_parent))

    fm_lane = fm.get("lane", "")
    ledger_lane = info.get("lane") or ""
    if fm_lane and ledger_lane and fm_lane.lower() != ledger_lane.lower():
        errors.append(_field_error(rel_path, "lane", ledger_lane, fm_lane))

    fm_status = fm.get("status", "")
    if fm_status:
        ledger_status = derive_status()
        if ledger_status and fm_status.lower() != ledger_status.lower():
            errors.append(_field_error(rel_path, "status", ledger_status, fm_status))

    return errors


def _filter_artifact_files(
    files: list[Path],
    artifact_type: str,
    adr_scope: str | None,
    graph: dict,
    canonicalize: Callable[[str], str],
) -> list[tuple[Path, str]]:
    """Pair each file with its resolved ledger id, filtered to ``adr_scope`` if set."""
    scoped = canonicalize(adr_scope) if adr_scope else None
    results: list[tuple[Path, str]] = []
    for artifact_file in files:
        ledger_id = _resolve_ledger_id_from_path(artifact_file, artifact_type, graph, canonicalize)
        if ledger_id is None:
            continue
        if scoped is not None:
            parent_id = graph[ledger_id].get("parent") if artifact_type == "obpi" else None
            if ledger_id != scoped and parent_id != scoped:
                continue
        results.append((artifact_file, ledger_id))
    return results


def _derive_status_with_index(
    ledger_id: str,
    info: dict,
    project_root: Path,
    config: object,
    ledger: object,
    obpi_index: list,
    fm_status: str = "",
) -> str | None:
    """Derive status using the canonical ledger semantics API.

    For ADRs uses ``Ledger.derive_adr_semantics`` — the same O(1) classmethod
    that ``gz adr report`` reaches through ``_build_adr_status_entry``. For
    OBPIs uses ``_derive_obpi_runtime_state`` — the canonical state mapper
    invoked at the tail of ``derive_obpi_semantics`` — with graph-derived
    inputs. Both paths share the canonical derivation logic; we skip the
    expensive anchor analysis and file inspection the report needs but the
    validator does not.
    """
    from gzkit.ledger import Ledger as _Ledger
    from gzkit.ledger_semantics import _derive_obpi_runtime_state

    artifact_type = info.get("type")
    try:
        if artifact_type == "adr":
            semantics = _Ledger.derive_adr_semantics(info)
            value = semantics.get("lifecycle_status")
            return str(value) if value else None
        if artifact_type == "obpi":
            if info.get("withdrawn"):
                return "withdrawn"
            return _derive_obpi_runtime_state(
                issues=[],
                anchor_issues=[],
                ledger_completed=bool(info.get("ledger_completed")),
                validated=bool(info.get("validated")),
                evidence_ok=bool(info.get("latest_completion_evidence")),
                attestation_state="recorded" if info.get("attested") else "not_required",
                obpi_completion=info.get("obpi_completion"),
                latest_receipt_event=info.get("latest_receipt_event"),
                implementation_evidence_ok=False,
                key_proof_ok=False,
                req_proof_present=0,
            )
    except (KeyError, ValueError, AttributeError, TypeError):
        return None
    return None


def validate_frontmatter_coherence(
    project_root: Path,
    adr_scope: str | None = None,
    *,
    ledger: Ledger | None = None,
) -> list[ValidationError]:
    """Validate frontmatter fields against ledger truth (GHI-167, ADR-0.0.16).

    Compares the four governed fields (``id``, ``parent``, ``lane``, ``status``)
    for every ADR/OBPI file on disk. Keys lookups on filesystem path only —
    never on frontmatter ``id:``. When ``adr_scope`` is set, restricts output
    to that single ADR (and its OBPIs).

    When ``ledger`` is provided (OBPI-0.0.16-03), the validator uses the
    supplied pre-snapshotted Ledger instance instead of opening a fresh one.
    This lets a caller pin the ledger state for a run — the reconciliation
    chore uses this to guarantee the receipt reflects the starting cursor's
    state only, never a mid-run mutation.
    """
    from gzkit.commands.status_obpi import _build_obpi_index
    from gzkit.config import GzkitConfig
    from gzkit.core.validation_rules import parse_frontmatter
    from gzkit.ledger import Ledger
    from gzkit.sync import scan_existing_artifacts

    config_path = project_root / ".gzkit.json"
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    if not config_path.is_file() or not ledger_path.is_file():
        return []

    config = GzkitConfig.load(config_path)
    if ledger is None:
        ledger = Ledger(ledger_path)
    try:
        graph = ledger.get_artifact_graph()
    except (json.JSONDecodeError, KeyError, ValueError):
        return []

    try:
        obpi_index = _build_obpi_index(project_root, config, ledger)
    except (KeyError, ValueError, AttributeError):
        obpi_index = []

    # GHI #192: lazy import — frontmatter_coherence imports from this module,
    # so a top-level import would cycle. Single-source-of-truth pool detection
    # lives there (lines 123, 214 of governance/frontmatter_coherence.py); the
    # comment at its line 300 explicitly names this contract.
    from gzkit.governance.frontmatter_coherence import _is_pool_artifact

    artifacts = scan_existing_artifacts(project_root, config.paths.design_root)
    canon = ledger.canonicalize_id
    errors: list[ValidationError] = []
    status_cache: dict[str, str | None] = {}

    def _status_for(ledger_id: str, info: dict, fm_status: str) -> str | None:
        if ledger_id not in status_cache:
            status_cache[ledger_id] = _derive_status_with_index(
                ledger_id, info, project_root, config, ledger, obpi_index, fm_status=fm_status
            )
        return status_cache[ledger_id]

    for artifact_type, files in (
        ("adr", artifacts.get("adrs", [])),
        ("obpi", artifacts.get("obpis", [])),
    ):
        scoped_files = _filter_artifact_files(files, artifact_type, adr_scope, graph, canon)
        for artifact_file, ledger_id in scoped_files:
            rel_path = str(artifact_file.relative_to(project_root))
            if _is_pool_artifact(artifact_file, rel_path):
                continue
            try:
                content = artifact_file.read_text(encoding="utf-8")
            except OSError:
                continue
            fm, _ = parse_frontmatter(content)
            if not fm:
                continue
            info = graph[ledger_id]
            fm_status_value = str(fm.get("status", ""))
            errors.extend(
                _check_one_artifact(
                    fm,
                    ledger_id,
                    info,
                    rel_path,
                    canon,
                    lambda lid=ledger_id, i=info, fs=fm_status_value: _status_for(lid, i, fs),
                )
            )

    return errors


def _render_frontmatter_explain(errors: list[ValidationError], adr_id: str) -> None:
    """Print step-by-step remediation per drifted field for one ADR."""
    drift = [e for e in errors if e.type == "frontmatter"]
    # GHI #192: pool ADRs are out of scope for the validator (no per-artifact
    # ledger lifecycle to compare against). "No drift detected" is misleading —
    # surface the structural reason honestly so operators know explain has
    # nothing to remediate by design, not by chance.
    if adr_id.startswith("ADR-pool."):
        console.print(
            f"[yellow]{adr_id} is a pool artifact; no ledger entry to compare "
            f"against. The chore library and validator both skip pool ADRs by "
            f"design (see ADR-0.0.16, GHI #192).[/yellow]"
        )
        return
    if not drift:
        console.print(f"[green]No frontmatter drift detected for {adr_id}.[/green]")
        return
    console.print(f"[bold]Remediation for {adr_id}:[/bold]\n")
    for error in drift:
        field = error.field or "?"
        ledger_value = error.ledger_value or "?"
        fm_value = error.frontmatter_value or "?"
        command = _RECOVERY_COMMANDS.get(field, "gz chores run frontmatter-ledger-coherence")
        console.print(
            f"  Field [bold]{field}[/bold]: ledger='{ledger_value}' frontmatter='{fm_value}'"
        )
        console.print(f"    → run: [cyan]{command}[/cyan]\n")
