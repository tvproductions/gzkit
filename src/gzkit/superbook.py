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


def next_semver(existing: list[str]) -> str:
    """Compute next minor semver from existing ADR semvers.

    Args:
        existing: List of existing semver strings.

    Returns:
        Next semver string.
    """
    if not existing:
        return "0.1.0"

    def _parse(s: str) -> tuple[int, int, int] | None:
        parts = s.split(".")
        if len(parts) != 3:
            return None
        try:
            return (int(parts[0]), int(parts[1]), int(parts[2]))
        except ValueError:
            return None

    versions = sorted(v for v in (_parse(s) for s in existing) if v is not None)
    major, minor, _patch = versions[-1]
    return f"{major}.{minor + 1}.0"


def map_chunks_to_obpis(plan: PlanData, semver: str, lane: str) -> list[OBPIDraft]:
    """Map plan chunks to OBPI drafts.

    Args:
        plan: Parsed plan data.
        semver: ADR semver for ID generation.
        lane: Governance lane.

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
                parent=f"ADR-{semver}",
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
    obpis = map_chunks_to_obpis(plan, semver, lane)

    checklist = [
        f"OBPI-{semver}-{idx:02d}: {chunk.name}" for idx, chunk in enumerate(plan.chunks, start=1)
    ]

    return ADRDraft(
        id=f"ADR-{semver}",
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

    slug = _slugify(adr.title)
    bucket = "foundation" if adr.semver.startswith("0.0.") else "pre-release"
    adr_dir_name = f"{adr.id}-{slug}"
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

    # Write OBPI files
    for obpi in adr.obpis:
        criteria_md = "\n".join(f"- [ ] {req.id}: {req.description}" for req in obpi.reqs)
        obpi_content = render_template(
            "obpi",
            id=obpi.id,
            title=obpi.objective,
            parent_adr=obpi.parent,
            item_number=str(obpi.item),
            lane=obpi.lane,
            status=obpi.status,
            objective=obpi.objective,
            acceptance_criteria_seed=criteria_md,
            lane_rationale=f"Inherited from parent {obpi.parent} ({obpi.lane}).",
        )
        obpi_file = obpis_dir / f"{obpi.id}.md"
        obpi_file.write_text(obpi_content, encoding="utf-8")
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
