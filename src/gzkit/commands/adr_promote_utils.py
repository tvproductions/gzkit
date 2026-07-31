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
    console,
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
        msg = (
            f"Could not derive kebab-case slug from pool ADR id: {pool_id}. "
            "Use --slug to provide one."
        )
        raise GzCliError(msg)
    return candidate


# ---------------------------------------------------------------------------
# Semver parsing and bucket assignment
# ---------------------------------------------------------------------------


def _parse_semver_triplet(semver: str) -> tuple[int, int, int]:
    """Parse strict X.Y.Z semantic version string into integer triplet."""
    if not SEMVER_ONLY_RE.match(semver):
        msg = f"Invalid --semver '{semver}'. Expected format X.Y.Z."
        raise GzCliError(msg)
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
        msg = f"Pool ADR is not ready for promotion: missing required section '## {section_title}'."
        raise GzCliError(msg)
    return section.strip()


def _optional_pool_section(pool_content: str, section_title: str) -> str | None:
    """Read an optional H2 section from a pool ADR."""
    section = extract_markdown_section(pool_content, section_title)
    if section is None:
        return None
    normalized = section.strip()
    return normalized or None


def _parse_top_level_markdown_bullets(section_content: str) -> list[str]:
    """Extract top-level markdown bullet items from a section body.

    Bullets nested inside an H3 (``###``) subsection of the section are
    explicitly skipped — only bullets attached directly to the section's
    top level count as promotion scope (GHI #241).
    """
    bullets: list[str] = []
    current: list[str] | None = None
    in_subsection = False
    for raw_line in section_content.splitlines():
        if raw_line.startswith("### "):
            if current:
                bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
                current = None
            in_subsection = True
            continue
        if raw_line.startswith("## "):
            if current:
                bullets.append(re.sub(r"\s+", " ", " ".join(current)).strip())
                current = None
            in_subsection = False
            continue
        if in_subsection:
            continue
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


_BOLD_PREFIX_BULLET_RE = re.compile(
    r"^\*\*(?P<slug>[a-z0-9][a-z0-9-]*)\*\*\s*(?:[—\-–]\s*(?P<desc>.+))?$",
    re.IGNORECASE,
)

_TABLE_ROW_RE = re.compile(r"^\s*\|(?P<cells>.+)\|\s*$")
_TABLE_ALIGN_RE = re.compile(r"^\s*:?-+:?\s*$")


def _parse_decomposition_table(pool_content: str) -> list[tuple[str, str]] | None:
    """Parse ``## Proposed OBPI Decomposition`` table into (slug, description) rows.

    Returns ``None`` when the section is absent or contains no table (GHI #241).
    The table must have at least ``Slug`` and ``Description`` columns; a leading
    ``#`` column is tolerated and ignored. Extra columns (e.g. ``Lane``) are
    ignored.
    """
    section = extract_markdown_section(pool_content, "Proposed OBPI Decomposition")
    if section is None or not section.strip():
        return None

    header_cells: list[str] | None = None
    rows: list[tuple[str, str]] = []
    for raw_line in section.splitlines():
        match = _TABLE_ROW_RE.match(raw_line)
        if not match:
            continue
        cells = [cell.strip() for cell in match.group("cells").split("|")]
        if all(_TABLE_ALIGN_RE.match(cell) for cell in cells):
            continue
        if header_cells is None:
            header_cells = [cell.lower() for cell in cells]
            continue
        try:
            slug_idx = header_cells.index("slug")
            desc_idx = header_cells.index("description")
        except ValueError:
            return None
        if slug_idx >= len(cells) or desc_idx >= len(cells):
            continue
        slug = cells[slug_idx].strip()
        description = cells[desc_idx].strip()
        if not slug:
            continue
        if not ADR_SLUG_RE.match(slug):
            continue
        rows.append((slug, description or slug))

    return rows or None


def _extract_bold_prefix_bullet(item: str) -> tuple[str, str] | None:
    """Return (slug, description) when bullet uses ``**slug** — narrative`` form.

    Accepts em-dash (``—``), en-dash (``–``), or hyphen (``-``) as the separator.
    Returns ``None`` when the bullet does not match the convention.
    """
    normalized = re.sub(r"\s+", " ", item).strip()
    match = _BOLD_PREFIX_BULLET_RE.match(normalized)
    if not match:
        return None
    slug = match.group("slug").strip().lower()
    if not ADR_SLUG_RE.match(slug):
        return None
    description = (match.group("desc") or "").strip()
    return slug, description or slug


# ---------------------------------------------------------------------------
# Promotion scorecard and checklist
# ---------------------------------------------------------------------------


def _promotion_scorecard(target_count: int) -> DecompositionScorecard:
    """Compute a valid scorecard for a concrete promoted checklist count."""
    if target_count <= 0:
        msg = "Pool ADR promotion requires at least one executable checklist item."
        raise GzCliError(msg)
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
    """Derive executable ADR checklist items from pool target scope.

    Resolution order (GHI #241):

    1. ``## Proposed OBPI Decomposition`` table — preferred. Slug column
       drives the OBPI name; Description column becomes the checklist text.
    2. ``- **slug** — narrative`` bold-prefix bullets in ``## Target Scope``.
    3. Legacy narrative-only bullets — accepted with a deprecation warning
       that names the two newer contracts.

    Bullets nested under ``### H3`` subsections within ``## Target Scope``
    are ignored by (2) and (3) — only direct top-level bullets count.
    """
    _required_pool_section(pool_content, "Target Scope")

    table_rows = _parse_decomposition_table(pool_content)
    scope_items: list[str]
    if table_rows:
        scope_items = [f"**{slug}** — {description}" for slug, description in table_rows]
    else:
        target_scope = extract_markdown_section(pool_content, "Target Scope") or ""
        bullets = [
            item.rstrip(":").strip()
            for item in _parse_top_level_markdown_bullets(target_scope)
            if item.strip()
        ]
        if not bullets:
            msg = (
                "Pool ADR is not ready for promotion: '## Target Scope' must contain "
                "top-level actionable bullet items (or a '## Proposed OBPI Decomposition' "
                "table)."
            )
            raise GzCliError(msg)

        bold_hits = [(_extract_bold_prefix_bullet(item), item) for item in bullets]
        if all(match is not None for match, _ in bold_hits):
            scope_items = [raw for _match, raw in bold_hits]
        else:
            console.print(
                "[yellow]WARN:[/yellow] Pool ADR '## Target Scope' uses legacy "
                "narrative-only bullets. This shape is deprecated and will emit "
                "long, narrative-leaking OBPI slugs. Migrate to either:\n"
                "  (a) a '## Proposed OBPI Decomposition' table with Slug + "
                "Description columns, or\n"
                "  (b) bullets shaped as '- **<slug>** — <narrative>'."
            )
            scope_items = bullets

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
    kind: str = "",
) -> str:
    """Render promoted ADR scaffold seeded from a pool ADR source.

    ``kind`` is also upserted into the frontmatter by the caller after this
    returns. It is threaded in here as well because the template carries a
    ``{kind}`` token: before GHI #741 that rendered as the literal string
    ``{kind}`` and was only ever correct because the upsert happened to
    overwrite it. Rendering the real value removes the ordering dependency —
    the upsert becomes idempotent rather than load-bearing.
    """
    from gzkit.templates import render_template  # noqa: PLC0415
    from gzkit.templates.author_prompts import PERSONA_PROMPT  # noqa: PLC0415

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
        # A pool ADR carries no persona — promotion is the first moment the ADR
        # has agents working on it, so the prompt is authored here rather than
        # inherited.
        persona=PERSONA_PROMPT,
        kind=kind,
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
        msg = f"Source ADR is not a pool entry: {pool_input}"
        raise GzCliError(msg)  # noqa: TRY003
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
        msg = f"Resolved ADR is not a pool entry: {pool_adr_id}"
        raise GzCliError(msg)  # noqa: TRY003
    if ledger.canonicalize_id(pool_adr_id) != pool_adr_id:
        msg = f"Pool ADR already promoted or renamed in ledger state: {pool_adr_id}"
        raise GzCliError(msg)  # noqa: TRY003

    pool_content = pool_file.read_text(encoding="utf-8")
    existing_promoted_to = parse_frontmatter_value(pool_content, "promoted_to")
    if existing_promoted_to:
        msg = f"Pool ADR already records promotion target '{existing_promoted_to}': {pool_adr_id}"
        raise GzCliError(msg)  # noqa: TRY003
    return pool_file, pool_adr_id, pool_metadata, pool_content


def _resolve_promotion_slug(pool_adr_id: str, slug: str | None) -> str:
    """Resolve and validate target ADR slug for pool promotion."""
    target_slug = slug or _derive_slug_from_pool_id(pool_adr_id)
    if not ADR_SLUG_RE.match(target_slug):
        msg = f"Invalid --slug '{target_slug}'. Expected kebab-case like 'gz-chores-system'."
        raise GzCliError(msg)  # noqa: TRY003
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
