"""Pool ADR parsing utilities for promotion workflow.

Extracted from adr_promote.py to stay under the 600-line module cap.
Covers: title extraction, slug derivation, semver parsing, bucket assignment,
pool-content marking, section extraction, checklist generation, and source
resolution.
"""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

from gzkit.commands.common import (
    ADR_SLUG_RE,
    SEMVER_ONLY_RE,
    GzCliError,
    _is_pool_adr_id,
    _upsert_frontmatter_value,
)
from gzkit.decomposition import (
    DecompositionScorecard,
    compute_scorecard,
    extract_markdown_section,
)
from gzkit.ledger import (
    Ledger,
    parse_frontmatter_value,
)
from gzkit.sync import parse_artifact_metadata

# ---------------------------------------------------------------------------
# Title extraction and slug derivation
# ---------------------------------------------------------------------------


def _pool_title_from_content(content: str) -> str | None:
    """Extract a human-readable title from the first markdown H1."""
    for line in content.splitlines():
        stripped = line.strip()
        if not stripped.startswith("# "):
            continue
        heading = stripped[2:].strip()
        if ":" in heading:
            _prefix, _sep, suffix = heading.partition(":")
            if suffix.strip():
                return suffix.strip()
        if heading:
            return heading
    return None


def _derive_slug_from_pool_id(pool_id: str) -> str:
    """Derive a kebab-case ADR slug from a pool ADR identifier."""
    if pool_id.startswith("ADR-pool."):
        raw_slug = pool_id.split("ADR-pool.", 1)[1]
    elif "-pool." in pool_id:
        raw_slug = pool_id.split("-pool.", 1)[1]
    else:
        raw_slug = pool_id.removeprefix("ADR-")
    candidate = raw_slug.replace(".", "-").lower()
    if not ADR_SLUG_RE.match(candidate):
        raise GzCliError(
            f"Could not derive kebab-case slug from pool ADR id: {pool_id}. "
            "Use --slug to provide one."
        )
    return candidate


# ---------------------------------------------------------------------------
# Semver parsing and bucket assignment
# ---------------------------------------------------------------------------


def _parse_semver_triplet(semver: str) -> tuple[int, int, int]:
    """Parse strict X.Y.Z semantic version string into integer triplet."""
    if not SEMVER_ONLY_RE.match(semver):
        raise GzCliError(f"Invalid --semver '{semver}'. Expected format X.Y.Z.")
    major_s, minor_s, patch_s = semver.split(".")
    return int(major_s), int(minor_s), int(patch_s)


def _adr_bucket_for_semver(semver: str) -> str:
    """Return canonical ADR directory bucket for a semantic version."""
    major, minor, _patch = _parse_semver_triplet(semver)
    if major == 0 and minor == 0:
        return "foundation"
    if major == 0:
        return "pre-release"
    return f"{major}.0"


# ---------------------------------------------------------------------------
# Pool ADR marking / section helpers
# ---------------------------------------------------------------------------


def _mark_pool_adr_promoted(content: str, target_adr_id: str, promote_date: str) -> str:
    """Mark pool ADR frontmatter and body as promoted archive context."""
    updated = _upsert_frontmatter_value(content, "status", "Superseded")
    updated = _upsert_frontmatter_value(updated, "promoted_to", target_adr_id)
    updated = updated.replace("\n## Status\n\nPool\n", "\n## Status\n\nSuperseded\n", 1)
    updated = updated.replace("\n## Status\n\nProposed\n", "\n## Status\n\nSuperseded\n", 1)

    note = (
        f"> Promoted to `{target_adr_id}` on {promote_date}. "
        "This pool file is retained as historical intake context."
    )
    lines = updated.splitlines()
    if any(note in line for line in lines):
        return updated

    for idx, line in enumerate(lines):
        if not line.startswith("# "):
            continue
        insert_at = idx + 1
        if insert_at < len(lines) and lines[insert_at].strip():
            lines.insert(insert_at, "")
            insert_at += 1
        lines.insert(insert_at, note)
        lines.insert(insert_at + 1, "")
        break

    return "\n".join(lines).rstrip() + "\n"


def _required_pool_section(pool_content: str, section_title: str) -> str:
    """Read a required H2 section from a pool ADR and fail closed if missing."""
    section = extract_markdown_section(pool_content, section_title)
    if section is None or not section.strip():
        raise GzCliError(
            f"Pool ADR is not ready for promotion: missing required section '## {section_title}'."
        )
    return section.strip()


def _optional_pool_section(pool_content: str, section_title: str) -> str | None:
    """Read an optional H2 section from a pool ADR."""
    section = extract_markdown_section(pool_content, section_title)
    if section is None:
        return None
    normalized = section.strip()
    return normalized or None


def _parse_top_level_markdown_bullets(section_content: str) -> list[str]:
    """Extract top-level markdown bullet items from a section body."""
    bullets: list[str] = []
    current: list[str] | None = None
    for raw_line in section_content.splitlines():
        bullet_match = re.match(r"^(?P<indent>\s*)-\s+(?P<body>.+)$", raw_line.rstrip())
        if bullet_match and not bullet_match.group("indent"):
            if current:
                bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
            current = [bullet_match.group("body").strip()]
            continue
        if current is None:
            continue
        stripped = raw_line.strip()
        if not stripped:
            continue
        if re.match(r"^[-*]\s+", stripped) or re.match(r"^\d+[.)]\s+", stripped):
            continue
        current.append(stripped)

    if current:
        bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
    return bullets


# ---------------------------------------------------------------------------
# Promotion scorecard and checklist
# ---------------------------------------------------------------------------


def _promotion_scorecard(target_count: int) -> DecompositionScorecard:
    """Compute a valid scorecard for a concrete promoted checklist count."""
    if target_count <= 0:
        raise GzCliError("Pool ADR promotion requires at least one executable checklist item.")
    if target_count <= 2:
        dimension_total = 0
    elif target_count == 3:
        dimension_total = 4
    elif target_count == 4:
        dimension_total = 7
    else:
        dimension_total = 9

    scores = [0, 0, 0, 0, 0]
    for index in range(dimension_total):
        scores[index % 5] += 1

    return compute_scorecard(
        data_state=scores[0],
        logic_engine=scores[1],
        interface=scores[2],
        observability=scores[3],
        lineage=scores[4],
        split_single_narrative=0,
        split_surface_boundary=0,
        split_state_anchor=0,
        split_testability_ceiling=0,
        baseline_selected=target_count,
    )


def _promoted_checklist_from_pool(
    pool_content: str, semver: str
) -> tuple[list[str], str, DecompositionScorecard]:
    """Derive executable ADR checklist items from pool target scope."""
    target_scope = _required_pool_section(pool_content, "Target Scope")
    scope_items = []
    for item in _parse_top_level_markdown_bullets(target_scope):
        normalized = item.rstrip(":").strip()
        if normalized:
            scope_items.append(normalized)
    if not scope_items:
        raise GzCliError(
            "Pool ADR is not ready for promotion: '## Target Scope' must contain top-level "
            "actionable bullet items."
        )

    checklist = "\n".join(
        f"- [ ] OBPI-{semver}-{index:02d}: {item}"
        for index, item in enumerate(scope_items, start=1)
    )
    return scope_items, checklist, _promotion_scorecard(len(scope_items))


# ---------------------------------------------------------------------------
# Promoted ADR rendering
# ---------------------------------------------------------------------------


def _insert_promoted_context_sections(content: str, sections: list[tuple[str, str]]) -> str:
    """Insert additional preserved pool sections into promoted ADR content."""
    if not sections:
        return content
    rendered = "\n\n".join(f"## {title}\n\n{body}" for title, body in sections if body.strip())
    marker = "\n## Q&A Transcript\n"
    if marker not in content:
        return content.rstrip() + "\n\n" + rendered + "\n"
    return content.replace(marker, "\n" + rendered + "\n\n## Q&A Transcript\n", 1)


def _render_promoted_adr_content(
    pool_adr_id: str,
    pool_content: str,
    target_adr_id: str,
    semver: str,
    lane: str,
    parent: str,
    title: str,
    status: str,
    promote_date: str,
) -> str:
    """Render promoted ADR scaffold seeded from a pool ADR source."""
    from gzkit.templates import render_template  # noqa: PLC0415

    intent = (
        _optional_pool_section(pool_content, "Intent")
        or _optional_pool_section(pool_content, "Problem Statement")
        or f"Promoted from `{pool_adr_id}` for active implementation."
    )
    scope_items, checklist_seed, scorecard = _promoted_checklist_from_pool(pool_content, semver)
    decision = _optional_pool_section(pool_content, "Decision") or (
        f"Promote `{pool_adr_id}` into active implementation and execute the following "
        "tracked scope:\n\n" + "\n".join(f"- {item}" for item in scope_items)
    )

    content = render_template(
        "adr",
        id=target_adr_id,
        status=status,
        semver=semver,
        lane=lane,
        parent=parent,
        date=promote_date,
        title=title,
        intent=intent,
        decision=decision,
        positive_consequences=(
            "- Promotion preserves backlog intent as executable ADR scope.\n"
            "- Checklist items now map 1:1 to generated OBPI briefs immediately."
        ),
        negative_consequences=(
            "- Promotion fails closed when the pool ADR lacks actionable execution scope."
        ),
        decomposition_scorecard=scorecard.to_markdown(),
        checklist=checklist_seed,
        qa_transcript=(
            f"Promotion derived from `{pool_adr_id}` on {promote_date}; executable scope "
            "was carried forward from the pool ADR instead of reseeded as placeholders."
        ),
        alternatives="- Keep this work in the pool backlog until reprioritized.",
    )
    content = _upsert_frontmatter_value(content, "promoted_from", pool_adr_id)
    preserved_sections: list[tuple[str, str]] = [
        ("Target Scope", _required_pool_section(pool_content, "Target Scope"))
    ]
    for sect_title in (
        "Non-Goals",
        "Dependencies",
        "Promotion Criteria",
        "Inspired By",
        "Notes",
    ):
        section = _optional_pool_section(pool_content, sect_title)
        if section is not None:
            preserved_sections.append((sect_title, section))
    return _insert_promoted_context_sections(content, preserved_sections)


# ---------------------------------------------------------------------------
# Pool ADR source resolution
# ---------------------------------------------------------------------------


def _normalize_pool_adr_input(pool_adr: str) -> str:
    """Normalize user ADR argument into an explicit pool ADR identifier."""
    pool_input = pool_adr if pool_adr.startswith("ADR-") else f"ADR-{pool_adr}"
    if not _is_pool_adr_id(pool_input):
        raise GzCliError(f"Source ADR is not a pool entry: {pool_input}")
    return pool_input


def _resolve_pool_adr_source(
    project_root: Path,
    config: Any,
    ledger: Ledger,
    pool_adr: str,
) -> tuple[Path, str, dict[str, str], str]:
    """Resolve and validate the source pool ADR artifact and content."""
    from gzkit.commands.common import resolve_adr_file  # noqa: PLC0415

    pool_input = _normalize_pool_adr_input(pool_adr)
    pool_file, _resolved_pool = resolve_adr_file(project_root, config, pool_input)
    pool_metadata = parse_artifact_metadata(pool_file)
    pool_adr_id = pool_metadata.get("id", pool_file.stem)
    if not _is_pool_adr_id(pool_adr_id):
        raise GzCliError(f"Resolved ADR is not a pool entry: {pool_adr_id}")
    if ledger.canonicalize_id(pool_adr_id) != pool_adr_id:
        raise GzCliError(f"Pool ADR already promoted or renamed in ledger state: {pool_adr_id}")

    pool_content = pool_file.read_text(encoding="utf-8")
    existing_promoted_to = parse_frontmatter_value(pool_content, "promoted_to")
    if existing_promoted_to:
        raise GzCliError(
            f"Pool ADR already records promotion target '{existing_promoted_to}': {pool_adr_id}"
        )
    return pool_file, pool_adr_id, pool_metadata, pool_content


def _resolve_promotion_slug(pool_adr_id: str, slug: str | None) -> str:
    """Resolve and validate target ADR slug for pool promotion."""
    target_slug = slug or _derive_slug_from_pool_id(pool_adr_id)
    if not ADR_SLUG_RE.match(target_slug):
        raise GzCliError(
            f"Invalid --slug '{target_slug}'. Expected kebab-case like 'gz-chores-system'."
        )
    return target_slug


def _resolve_promotion_parent(parent: str | None, pool_metadata: dict[str, str]) -> str:
    """Resolve ADR parent link for promoted ADR scaffold."""
    promoted_parent = parent or pool_metadata.get("parent", "")
    if promoted_parent and not promoted_parent.startswith(("ADR-", "PRD-", "OBPI-")):
        promoted_parent = f"ADR-{promoted_parent}"
    return promoted_parent


def _resolve_promotion_lane(
    lane: str | None,
    pool_metadata: dict[str, str],
    default_lane: str,
) -> str:
    """Resolve lane metadata for promoted ADR scaffold."""
    raw_lane = (lane or pool_metadata.get("lane") or default_lane).lower()
    return raw_lane if raw_lane in {"lite", "heavy"} else default_lane
