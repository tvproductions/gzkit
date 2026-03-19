"""Superbook pipeline: bridge superpowers artifacts to GovZero governance.

Orchestrates: classify lane, compute scorecard, map chunks to OBPIs,
generate ADR/OBPI drafts, present for review, apply on approval.
"""

from __future__ import annotations

import re
from datetime import date
from fnmatch import fnmatch
from pathlib import Path

from gzkit.superbook_models import (
    ADRDraft,
    ChunkData,
    CommitData,
    LaneClassification,
    OBPIDraft,
    PlanData,
    REQData,
    SpecData,
)

HEAVY_SIGNAL_PATTERNS = [
    "src/gzkit/cli.py",
    ".gzkit/schemas/*",
    "src/gzkit/templates/*",
    "**/api/**",
]


def _slugify(text: str, max_length: int = 50) -> str:
    """Convert text to a URL-safe slug."""
    slug = text.lower()
    slug = re.sub(r"[^a-z0-9\s-]", "", slug)
    slug = re.sub(r"[\s]+", "-", slug).strip("-")
    return slug[:max_length]


def classify_lane(spec: SpecData, plan: PlanData) -> LaneClassification:
    """Classify governance lane from file scope.

    Args:
        spec: Parsed spec data.
        plan: Parsed plan data.

    Returns:
        LaneClassification with inferred lane and triggering signals.

    """
    all_paths: list[str] = list(spec.file_scope)
    for chunk in plan.chunks:
        all_paths.extend(chunk.file_paths)

    signals: list[str] = []
    for path in sorted(set(all_paths)):
        for pattern in HEAVY_SIGNAL_PATTERNS:
            if fnmatch(path, pattern) or path.startswith(pattern.rstrip("*")):
                signals.append(path)
                break

    lane = "heavy" if signals else "lite"
    return LaneClassification(lane=lane, signals=sorted(set(signals)))


def extract_semver(adr_id: str) -> str | None:
    """Extract the semver portion from an ADR identifier.

    Handles both bare (``ADR-0.14.0``) and slugged
    (``ADR-0.14.0-multi-agent-...``) forms.

    Returns:
        Semver string like ``0.14.0``, or None if unparseable.

    """
    m = re.match(r"ADR-(\d+\.\d+\.\d+)", adr_id)
    return m.group(1) if m else None


def next_semver(existing: list[str]) -> str:
    """Compute next minor semver from existing ADR semvers.

    Args:
        existing: List of existing semver strings (e.g. ``["0.14.0"]``).

    Returns:
        Next semver string.

    """
    if not existing:
        return "0.1.0"

    def _parse(s: str) -> tuple[int, int, int] | None:
        # Strip any trailing slug text from the patch component.
        m = re.match(r"(\d+)\.(\d+)\.(\d+)", s)
        if not m:
            return None
        return (int(m.group(1)), int(m.group(2)), int(m.group(3)))

    versions = sorted(v for v in (_parse(s) for s in existing) if v is not None)
    if not versions:
        return "0.1.0"
    major, minor, _patch = versions[-1]
    return f"{major}.{minor + 1}.0"


def collect_existing_semvers(project_root: Path) -> list[str]:
    """Collect all ADR semvers from both the ledger and on-disk packages.

    Scans ledger ``adr_created`` events and ADR directories under
    ``docs/design/adr/`` to avoid semver gaps when ADRs are created
    outside the superbook pipeline.

    Args:
        project_root: Repository root.

    Returns:
        Deduplicated list of semver strings.

    """
    from gzkit.ledger import Ledger  # noqa: PLC0415

    semvers: set[str] = set()

    # Source 1: ledger adr_created events
    ledger = Ledger(project_root / ".gzkit" / "ledger.jsonl")
    for event in ledger.read_all():
        if event.event == "adr_created":
            sv = extract_semver(event.id)
            if sv:
                semvers.add(sv)

    # Source 2: on-disk ADR directories
    adr_base = project_root / "docs" / "design" / "adr"
    for bucket in ("foundation", "pre-release"):
        bucket_dir = adr_base / bucket
        if not bucket_dir.is_dir():
            continue
        for child in bucket_dir.iterdir():
            if child.is_dir() and child.name.startswith("ADR-"):
                sv = extract_semver(child.name)
                if sv:
                    semvers.add(sv)

    return sorted(semvers)


def slugify_obpi_name(value: str) -> str:
    """Convert checklist text into a stable OBPI slug suffix."""
    stripped = re.sub(r"`([^`]*)`", r"\1", value)
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", stripped).strip("-").lower()
    return slug or "scope-item"


def render_obpi_acceptance_seed(version: str, item: int, criteria: list[str] | None = None) -> str:
    """Create acceptance criteria seed for an OBPI.

    Args:
        version: Semver string for REQ ID prefix.
        item: OBPI item number.
        criteria: Optional concrete criteria. Falls back to placeholders.

    """
    req_prefix = f"REQ-{version}-{item:02d}"
    if criteria:
        return "\n".join(
            f"- [ ] {req_prefix}-{idx:02d}: {c}" for idx, c in enumerate(criteria, start=1)
        )
    return "\n".join(
        [
            f"- [ ] {req_prefix}-01: Given/When/Then behavior criterion 1",
            f"- [ ] {req_prefix}-02: Given/When/Then behavior criterion 2",
            f"- [ ] {req_prefix}-03: Given/When/Then behavior criterion 3",
        ]
    )


def build_obpi_plan(
    *,
    project_root: Path,
    adr_file: Path,
    parent_adr_id: str,
    item: int,
    checklist_item_text: str,
    lane: str,
    name: str,
    title: str,
    objective: str,
    acceptance_criteria_seed: str | None = None,
    allowed_paths: list[str] | None = None,
    work_breakdown: list[str] | None = None,
) -> dict[str, object]:
    """Build deterministic OBPI artifact plan.

    Shared by ``gz specify`` and ``gz superbook`` so both produce
    identical template output.

    Args:
        project_root: Repository root.
        adr_file: Absolute path to parent ADR markdown file.
        parent_adr_id: Full slugged ADR identifier.
        item: Checklist item number (1-based).
        checklist_item_text: Text of the checklist item.
        lane: Governance lane (``lite`` or ``heavy``).
        name: Slug suffix for the OBPI ID.
        title: Human-readable title.
        objective: One-sentence objective.
        acceptance_criteria_seed: Optional pre-formatted criteria markdown.
        allowed_paths: Optional list of path globs the OBPI may touch.
        work_breakdown: Optional list of work-breakdown task descriptions.

    """
    from gzkit.templates import render_template  # noqa: PLC0415

    version = extract_semver(parent_adr_id) or parent_adr_id.replace("ADR-", "").split("-")[0]
    obpi_id = f"OBPI-{version}-{item:02d}-{name}"
    lane_cap = lane.capitalize()
    lane_requirements = (
        "All 5 gates required: ADR, TDD, Docs, BDD, Human attestation"
        if lane == "heavy"
        else "Gates 1, 2 required: ADR, TDD"
    )
    lane_rationale = (
        "This OBPI changes a command/API/schema/runtime contract surface."
        if lane == "heavy"
        else "This OBPI remains internal to the promoted ADR implementation scope."
    )
    if not acceptance_criteria_seed:
        acceptance_criteria_seed = render_obpi_acceptance_seed(version, item)

    # Build allowed/denied paths markdown from provided paths
    if allowed_paths:
        allowed_paths_md = "\n".join(f"- `{p}`" for p in allowed_paths)
    else:
        allowed_paths_md = (
            "- `src/module/` - Reason this is in scope\n- `tests/test_module.py` - Reason"
        )

    denied_paths_md = (
        "- Paths not listed in Allowed Paths\n- New dependencies\n- CI files, lockfiles"
    )

    # Build requirements markdown from work breakdown
    if work_breakdown:
        requirements_md = "\n".join(f"1. REQUIREMENT: {task_name}" for task_name in work_breakdown)
    else:
        requirements_md = (
            "1. REQUIREMENT: First constraint\n"
            "1. REQUIREMENT: Second constraint\n"
            "1. NEVER: What must not happen\n"
            "1. ALWAYS: What must always be true"
        )

    # Build work breakdown markdown
    work_breakdown_md = "\n".join(f"- {task}" for task in work_breakdown) if work_breakdown else ""

    content = render_template(
        "obpi",
        id=obpi_id,
        title=title,
        parent_adr=parent_adr_id,
        parent_adr_path=str(adr_file.relative_to(project_root)),
        item_number=str(item),
        checklist_item_text=checklist_item_text,
        lane=lane_cap,
        lane_rationale=lane_rationale,
        objective=objective,
        lane_requirements=lane_requirements,
        acceptance_criteria_seed=acceptance_criteria_seed,
        allowed_paths_md=allowed_paths_md,
        denied_paths_md=denied_paths_md,
        requirements_md=requirements_md,
        work_breakdown_md=work_breakdown_md,
    )
    obpi_dir = adr_file.parent / "obpis"
    obpi_file = obpi_dir / f"{obpi_id}.md"
    return {
        "obpi_id": obpi_id,
        "obpi_file": obpi_file,
        "content": content,
    }


def map_chunks_to_obpis(plan: PlanData, semver: str, lane: str, adr_id: str) -> list[OBPIDraft]:
    """Map plan chunks to OBPI drafts.

    Args:
        plan: Parsed plan data.
        semver: ADR semver for ID generation.
        lane: Governance lane.
        adr_id: Full slugged ADR identifier for parent references.

    Returns:
        List of OBPIDraft, one per chunk.

    """
    obpis: list[OBPIDraft] = []
    for idx, chunk in enumerate(plan.chunks, start=1):
        slug = _slugify(chunk.name)
        obpi_id = f"OBPI-{semver}-{idx:02d}-{slug}"

        reqs: list[REQData] = []
        for c_idx, criterion in enumerate(chunk.criteria, start=1):
            reqs.append(
                REQData(
                    id=f"REQ-{semver}-{idx:02d}-{c_idx:02d}",
                    description=criterion,
                )
            )

        work_breakdown = [t.name for t in chunk.tasks]

        obpis.append(
            OBPIDraft(
                id=obpi_id,
                objective=chunk.name,
                parent=adr_id,
                item=idx,
                lane=lane,
                allowed_paths=chunk.file_paths,
                reqs=reqs,
                work_breakdown=work_breakdown,
            )
        )

    return obpis


def generate_adr_draft(
    spec: SpecData,
    plan: PlanData,
    *,
    lane: str,
    semver: str,
    status: str = "Draft",
) -> ADRDraft:
    """Generate an ADR draft from spec and plan data.

    Args:
        spec: Parsed spec.
        plan: Parsed plan.
        lane: Governance lane.
        semver: ADR semver.
        status: Initial status.

    Returns:
        ADRDraft with populated OBPIs.

    """
    slug = _slugify(spec.title)
    adr_id = f"ADR-{semver}-{slug}"
    obpis = map_chunks_to_obpis(plan, semver, lane, adr_id)

    checklist = [
        f"OBPI-{semver}-{idx:02d}: {chunk.name}" for idx, chunk in enumerate(plan.chunks, start=1)
    ]

    return ADRDraft(
        id=adr_id,
        title=spec.title,
        semver=semver,
        lane=lane,
        status=status,
        intent=spec.goal,
        decision=spec.architecture,
        checklist=checklist,
        scorecard={},
        obpis=obpis,
    )


def map_commits_to_chunks(
    commits: list[CommitData], chunks: list[ChunkData]
) -> list[list[CommitData]]:
    """Map commits to chunks by file-path overlap.

    Returns a list of length len(chunks) + 1. Index i contains commits
    mapped to chunks[i]. The last element contains unmapped commits.
    """
    buckets: list[list[CommitData]] = [[] for _ in range(len(chunks) + 1)]

    for commit in commits:
        commit_files = set(commit.files)
        best_idx = -1
        best_score = 0
        for idx, chunk in enumerate(chunks):
            chunk_files = set(chunk.file_paths)
            score = len(commit_files & chunk_files)
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx >= 0:
            buckets[best_idx].append(commit)
        else:
            buckets[-1].append(commit)

    return buckets


def present_draft(adr: ADRDraft) -> str:
    """Render a human-readable summary of the booking draft.

    Args:
        adr: ADR draft with OBPIs.

    Returns:
        Formatted string for terminal display.

    """
    lines = [
        "",
        "=" * 50,
        "  gz superbook — Governance Booking Draft",
        "=" * 50,
        "",
        f"ADR: {adr.id} — {adr.title}",
        f"Lane: {adr.lane.title()}",
        f"Status: {adr.status}",
        "",
        "Feature Checklist:",
    ]
    for i, item in enumerate(adr.checklist):
        req_count = len(adr.obpis[i].reqs) if i < len(adr.obpis) else 0
        lines.append(f"  {item} ({req_count} REQs)")

    lines.append("")
    lines.append(f"OBPIs: {len(adr.obpis)}")
    lines.append("")
    lines.append("Run with --apply to book, or adjust with --semver/--lane.")
    lines.append("")

    return "\n".join(lines)


def apply_draft(adr: ADRDraft, project_root: Path) -> list[str]:
    """Write ADR, OBPI files, and ledger events to disk.

    Args:
        adr: ADR draft with OBPIs.
        project_root: Project root directory.

    Returns:
        List of created file paths (relative to project_root).

    """
    from gzkit.ledger import Ledger, adr_created_event, obpi_created_event
    from gzkit.templates import render_template  # noqa: PLC0415

    bucket = "foundation" if adr.semver.startswith("0.0.") else "pre-release"
    adr_dir_name = adr.id
    adr_dir = project_root / "docs" / "design" / "adr" / bucket / adr_dir_name
    obpis_dir = adr_dir / "obpis"
    audit_dir = adr_dir / "audit"

    adr_dir.mkdir(parents=True, exist_ok=True)
    obpis_dir.mkdir(parents=True, exist_ok=True)
    audit_dir.mkdir(parents=True, exist_ok=True)

    created: list[str] = []

    # Write ADR file
    checklist_md = "\n".join(f"- [ ] {item}" for item in adr.checklist)
    adr_content = render_template(
        "adr",
        id=adr.id,
        title=adr.title,
        semver=adr.semver,
        lane=adr.lane,
        parent="",
        date=date.today().isoformat(),
        status=adr.status,
        intent=adr.intent,
        decision=adr.decision,
        positive_consequences="Governance visibility for superpowers work.",
        negative_consequences="Additional booking step in workflow.",
        decomposition_scorecard="Auto-generated by gz superbook.",
        checklist=checklist_md,
        qa_transcript="Generated from superpowers spec.",
        alternatives="Manual gz plan + gz specify (two-step).",
    )
    adr_file = adr_dir / f"{adr_dir_name}.md"
    adr_file.write_text(adr_content, encoding="utf-8")
    created.append(str(adr_file.relative_to(project_root)))

    # Write OBPI files via shared build_obpi_plan
    for idx, obpi in enumerate(adr.obpis):
        criteria_md = "\n".join(f"- [ ] {req.id}: {req.description}" for req in obpi.reqs)
        checklist_item_text = adr.checklist[idx] if idx < len(adr.checklist) else obpi.objective
        plan = build_obpi_plan(
            project_root=project_root,
            adr_file=adr_file,
            parent_adr_id=obpi.parent,
            item=obpi.item,
            checklist_item_text=checklist_item_text,
            lane=obpi.lane,
            name=_slugify(obpi.objective),
            title=obpi.objective,
            objective=obpi.objective,
            acceptance_criteria_seed=criteria_md,
            allowed_paths=obpi.allowed_paths,
            work_breakdown=obpi.work_breakdown,
        )
        obpi_file = Path(str(plan["obpi_file"]))
        obpi_file.parent.mkdir(parents=True, exist_ok=True)
        obpi_file.write_text(str(plan["content"]), encoding="utf-8")
        created.append(str(obpi_file.relative_to(project_root)))

    # Emit ledger events
    ledger_path = project_root / ".gzkit" / "ledger.jsonl"
    ledger = Ledger(ledger_path)
    adr_event = adr_created_event(adr.id, "", adr.lane)
    adr_event.extra["source"] = "gz-superbook"
    ledger.append(adr_event)
    for obpi in adr.obpis:
        obpi_event = obpi_created_event(obpi.id, adr.id)
        obpi_event.extra["source"] = "gz-superbook"
        ledger.append(obpi_event)

    return created
