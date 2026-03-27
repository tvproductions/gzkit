"""ADR audit-check, covers-check, and emit-receipt command implementations."""

import ast
import json
import re
from datetime import date
from pathlib import Path
from typing import Any, cast

from gzkit.commands.common import (
    GzCliError,
    _reject_pool_adr_for_lifecycle,
    console,
    ensure_initialized,
    get_project_root,
    resolve_adr_file,
    resolve_adr_ledger_id,
)
from gzkit.commands.status import _collect_obpi_files_for_adr, _inspect_obpi_brief
from gzkit.hooks.core import enrich_completed_receipt_evidence
from gzkit.hooks.obpi import normalize_git_sync_state, normalize_scope_audit
from gzkit.ledger import (
    Ledger,
    audit_receipt_emitted_event,
    normalize_req_proof_inputs,
)
from gzkit.traceability import CoverageEntry, compute_coverage, scan_test_tree
from gzkit.triangle import ReqId, scan_briefs
from gzkit.utils import capture_validation_anchor


def adr_audit_check(adr: str, as_json: bool) -> None:
    """Verify linked OBPIs are complete and contain implementation evidence."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "audit-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    findings: list[dict[str, Any]] = []
    complete: list[str] = []

    if not expected_obpis and not obpi_files:
        findings.append(
            {
                "id": None,
                "issue": "No OBPI briefs are linked to this ADR.",
            }
        )

    for expected_id in expected_obpis:
        if expected_id not in obpi_files:
            findings.append(
                {
                    "id": expected_id,
                    "issue": "Linked in ledger but no OBPI file found.",
                }
            )

    graph = ledger.get_artifact_graph()
    for obpi_id, obpi_file in sorted(obpi_files.items()):
        inspection = _inspect_obpi_brief(project_root, obpi_file, obpi_id=obpi_id, graph=graph)
        if inspection["reasons"]:
            findings.append(
                {
                    "id": obpi_id,
                    "file": str(obpi_file.relative_to(project_root)),
                    "issue": "; ".join(inspection["reasons"]),
                    "frontmatter_status": inspection["frontmatter_status"],
                    "brief_status": inspection["brief_status"],
                }
            )
        else:
            complete.append(obpi_id)

    passed = not findings

    adr_dir = project_root / config.paths.adrs
    coverage = _compute_adr_coverage(project_root, adr_id, adr_dir)
    advisory_findings: list[dict[str, Any]] = [
        {
            "id": u["req_id"],
            "issue": "REQ not covered by any @covers test annotation.",
            "severity": "advisory",
        }
        for u in coverage["uncovered"]
    ]

    result = {
        "adr": adr_id,
        "passed": passed,
        "checked_obpis": sorted(obpi_files.keys()),
        "complete_obpis": complete,
        "findings": findings,
        "coverage": coverage,
        "advisory_findings": advisory_findings,
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        console.print(f"[bold]ADR audit-check:[/bold] {adr_id}")
        if passed:
            console.print("[green]PASS[/green] All linked OBPIs are completed with evidence.")
            if complete:
                for obpi_id in complete:
                    console.print(f"  - {obpi_id}")
        else:
            console.print("[red]FAIL[/red] OBPI completeness/evidence gaps found:")
            for finding in findings:
                finding_id = finding.get("id") or "(none)"
                issue = finding.get("issue", "")
                console.print(f"  - {finding_id}: {issue}")
        _print_coverage_section(coverage, advisory_findings)

    if not passed:
        raise SystemExit(1)


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
    advisory_findings: list[dict[str, Any]],
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

    if advisory_findings:
        console.print("[yellow]Advisory:[/yellow] Uncovered REQs:")
        for finding in advisory_findings:
            console.print(f"  - {finding['id']}")


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


def adr_covers_check(adr: str, as_json: bool) -> None:
    """Verify @covers traceability for an ADR and its linked OBPIs."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "covers-checked")

    obpi_files, expected_obpis = _collect_obpi_files_for_adr(project_root, config, ledger, adr_id)
    (
        requirement_targets,
        criteria_without_req_ids,
        invalid_requirement_targets,
    ) = _collect_adr_requirement_targets(project_root, obpi_files)

    expected_targets = [adr_id, *sorted(expected_obpis), *requirement_targets]
    covers = _collect_covers_annotations(project_root)
    rows, missing = _build_covers_rows(adr_id, expected_targets, covers)

    referenced_targets = sorted(k for k in covers if k.startswith(("ADR-", "OBPI-", "REQ-")))
    unmatched_targets = sorted(k for k in referenced_targets if k not in expected_targets)
    passed = not missing and not criteria_without_req_ids and not invalid_requirement_targets

    result = {
        "adr": adr_id,
        "passed": passed,
        "expected_targets": expected_targets,
        "covered_targets": [row["target"] for row in rows if row["covered"]],
        "missing_targets": missing,
        "requirement_targets": requirement_targets,
        "criteria_without_req_ids": criteria_without_req_ids,
        "invalid_requirement_targets": invalid_requirement_targets,
        "rows": rows,
        "unmatched_targets": unmatched_targets,
    }

    if as_json:
        print(json.dumps(result, indent=2))
    else:
        _print_adr_covers_check_result(result)

    if not passed:
        raise SystemExit(1)


def _is_foundation_adr(adr_id: str) -> bool:
    """Return True when ADR ID is in the 0.0.x foundation series."""
    return re.match(r"^ADR-0\.0\.\d+(?:[.-].*)?$", adr_id) is not None


def _requires_human_obpi_attestation(parent_adr: str | None, parent_lane: str) -> bool:
    """Return whether completed evidence must include human-attestation fields.

    Foundation ADRs (0.0.x) always require human attestation.  For non-foundation
    ADRs, the parent lane sets the compliance floor -- a Lite OBPI under a Heavy ADR
    still requires attestation per AGENTS.md Lane Inheritance Rule.
    """
    if not isinstance(parent_adr, str) or not parent_adr:
        return False
    if _is_foundation_adr(parent_adr):
        return True
    return parent_lane == "heavy"


def _validate_obpi_completed_required_fields(evidence: dict[str, Any]) -> None:
    """Validate baseline completed-receipt evidence fields."""
    required_fields = ("value_narrative", "key_proof")
    missing: list[str] = []
    for field in required_fields:
        value = evidence.get(field)
        if not isinstance(value, str) or not value.strip():
            missing.append(field)
    if missing:
        raise GzCliError(
            f"Missing required completed-evidence field(s): {', '.join(sorted(missing))}."
        )


def _validate_obpi_human_attestation_fields(evidence: dict[str, Any], attestor: str) -> None:
    """Validate heavy/foundation human-attestation evidence contract."""
    placeholder_names = {"n/a", "tbd", "todo", "none", "-", "...", ""}
    if attestor.strip().lower() in placeholder_names:
        raise GzCliError("Heavy/Foundation OBPI completion requires --attestor to be a real name.")
    if evidence.get("human_attestation") is not True:
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires evidence.human_attestation=true."
        )

    attestation_text = evidence.get("attestation_text")
    if not isinstance(attestation_text, str) or not attestation_text.strip():
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires non-empty evidence.attestation_text."
        )

    attestation_date = evidence.get("attestation_date")
    if not isinstance(attestation_date, str) or not re.match(
        r"^\d{4}-\d{2}-\d{2}$", attestation_date
    ):
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires evidence.attestation_date "
            "formatted as YYYY-MM-DD."
        )
    try:
        date.fromisoformat(attestation_date)
    except ValueError as exc:
        raise GzCliError(
            "Heavy/Foundation OBPI completion requires evidence.attestation_date "
            "formatted as YYYY-MM-DD."
        ) from exc


def _validate_explicit_req_proof_inputs(raw_inputs: Any) -> list[dict[str, str]]:
    """Validate an explicit req_proof_inputs payload when supplied."""
    if raw_inputs is None:
        return []
    if not isinstance(raw_inputs, list) or not raw_inputs:
        raise GzCliError(
            "evidence.req_proof_inputs must be a non-empty list of proof input objects."
        )

    normalized = normalize_req_proof_inputs(raw_inputs)
    if len(normalized) != len(raw_inputs):
        raise GzCliError(
            "Each evidence.req_proof_inputs item must include non-empty "
            "name/kind/source fields and status present|missing."
        )
    return normalized


def _validate_obpi_completion_evidence(
    *,
    project_root: Path,
    obpi_content: str,
    evidence: dict[str, Any] | None,
    parent_adr: str | None,
    parent_lane: str,
    attestor: str,
) -> tuple[dict[str, Any], str, dict[str, str] | None]:
    """Validate and normalize evidence for OBPI completed receipts."""
    if evidence is None:
        raise GzCliError(
            "OBPI completed receipts require --evidence-json with value_narrative and key_proof."
        )

    _validate_obpi_completed_required_fields(evidence)
    requires_human_attestation = _requires_human_obpi_attestation(parent_adr, parent_lane)

    if requires_human_attestation:
        _validate_obpi_human_attestation_fields(evidence, attestor)

    completion_term = "attested_completed" if requires_human_attestation else "completed"
    normalized = dict(evidence)
    explicit_req_proof_inputs = _validate_explicit_req_proof_inputs(
        normalized.get("req_proof_inputs")
    )
    human_attestation = None
    if normalized.get("human_attestation") is True:
        human_attestation = {
            "valid": True,
            "attestor": attestor,
            "attestation_text": normalized.get("attestation_text"),
            "date": normalized.get("attestation_date"),
        }
    normalized["req_proof_inputs"] = explicit_req_proof_inputs or normalize_req_proof_inputs(
        None,
        fallback_key_proof=cast(str, normalized.get("key_proof")),
        human_attestation=human_attestation,
    )
    normalized["obpi_completion"] = completion_term
    normalized["attestation_requirement"] = "required" if requires_human_attestation else "optional"
    if isinstance(parent_adr, str) and parent_adr:
        normalized["parent_adr"] = parent_adr
    normalized["parent_lane"] = parent_lane
    explicit_scope_audit = normalized.get("scope_audit")
    scope_audit = normalize_scope_audit(explicit_scope_audit)
    if explicit_scope_audit is not None and scope_audit is None:
        raise GzCliError(
            "evidence.scope_audit must be an object with allowlist, changed_files, "
            "and out_of_scope_files string arrays."
        )

    explicit_git_sync_state = normalized.get("git_sync_state")
    git_sync_state = normalize_git_sync_state(explicit_git_sync_state)
    if explicit_git_sync_state is not None and git_sync_state is None:
        raise GzCliError(
            "evidence.git_sync_state must include branch/remote/head/remote_head, "
            "dirty/diverged booleans, ahead/behind integers, and action/warning/blocker arrays."
        )

    enriched_evidence, anchor = enrich_completed_receipt_evidence(
        project_root=project_root,
        content=obpi_content,
        base_evidence=normalized,
        parent_adr=parent_adr,
        recorder_source="cli:obpi_emit_receipt",
        scope_audit=scope_audit,
        git_sync_state=git_sync_state,
    )
    return enriched_evidence, completion_term, anchor


def adr_emit_receipt_cmd(
    adr: str,
    receipt_event: str,
    attestor: str,
    evidence_json: str | None,
    dry_run: bool,
) -> None:
    """Emit an ADR audit receipt event anchored in the ledger."""
    config = ensure_initialized()
    project_root = get_project_root()
    ledger = Ledger(project_root / config.paths.ledger)

    adr_input = adr if adr.startswith("ADR-") else f"ADR-{adr}"
    canonical_adr = ledger.canonicalize_id(adr_input)
    adr_file, adr_id = resolve_adr_file(project_root, config, canonical_adr)
    adr_id = resolve_adr_ledger_id(adr_file, adr_id, ledger)
    _reject_pool_adr_for_lifecycle(adr_id, "issued receipts")

    evidence: dict[str, Any] | None = None
    if evidence_json:
        try:
            parsed = json.loads(evidence_json)
        except json.JSONDecodeError as exc:
            raise GzCliError(f"Invalid --evidence-json: {exc}") from exc
        if not isinstance(parsed, dict):
            raise GzCliError("--evidence-json must decode to a JSON object")
        evidence = parsed

    anchor = capture_validation_anchor(project_root, adr_id)
    event = audit_receipt_emitted_event(
        adr_id=adr_id,
        receipt_event=receipt_event,
        attestor=attestor,
        evidence=evidence,
        anchor=anchor,
    )

    if dry_run:
        console.print("[yellow]Dry run:[/yellow] no ledger event will be written.")
        console.print(json.dumps(event.model_dump(), indent=2))
        return

    ledger.append(event)
    console.print("[green]Audit receipt emitted.[/green]")
    console.print(f"  ADR: {adr_id}")
    console.print(f"  Event: {receipt_event}")
    console.print(f"  Attestor: {attestor}")
