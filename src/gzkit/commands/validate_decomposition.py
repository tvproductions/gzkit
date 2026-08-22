"""ADR decomposition-scorecard validation.

Extracted from ``validate_cmd`` under GHI #852, following the split already
established by ``validate_briefs``, ``validate_frontmatter``,
``validate_sensitivity`` and their seven siblings: one validator concern per
module, dispatched from the registry.

The extraction was forced rather than chosen. ``validate_cmd`` sits on a
shrink-only grandfather entry in ``.gzkit/rules/complexity-thresholds.json`` at
exactly its recorded ceiling, so ANY added line breaks the module-size gate --
the fix that needed room was a five-line one. This function was the cleanest
thing to move: 83 lines, one caller, and no dependency on any module-level name
in ``validate_cmd``.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.validate import ValidationError, parse_frontmatter
from gzkit.validate_pkg.document import is_adr_shape_grandfathered, is_pool_adr_path

__all__ = ["validate_decomposition"]


def validate_decomposition(project_root: Path) -> list[ValidationError]:
    """Validate ADR decomposition scorecards and checklist-to-brief alignment."""
    from gzkit.core.scoring import (  # noqa: PLC0415
        active_checklist_items,
        parse_checklist_items,
        parse_scorecard,
    )

    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []

    errors: list[ValidationError] = []
    for adr_md in sorted(adr_root.rglob("ADR-*.md")):
        if adr_md.name.startswith("ADR-CLOSEOUT") or is_pool_adr_path(adr_md):
            continue
        # Only check ADR intent documents (not briefs/audit files)
        if "obpis" in adr_md.parts or "briefs" in adr_md.parts or "audit" in adr_md.parts:
            continue

        content = adr_md.read_text(encoding="utf-8")
        frontmatter, body = parse_frontmatter(content)
        if frontmatter and is_adr_shape_grandfathered(frontmatter):
            continue

        scorecard, scorecard_errors = parse_scorecard(body)
        checklist_items = parse_checklist_items(body)

        if not checklist_items:
            continue  # ADR has no checklist — skip

        if scorecard_errors:
            for err in scorecard_errors:
                errors.append(
                    ValidationError(
                        type="decomposition",
                        artifact=adr_md.relative_to(project_root).as_posix(),
                        message=err,
                    )
                )
            continue

        if scorecard is None:
            continue

        live_items = active_checklist_items(checklist_items)
        if len(live_items) != scorecard.final_target_obpi_count:
            errors.append(
                ValidationError(
                    type="decomposition",
                    artifact=adr_md.relative_to(project_root).as_posix(),
                    message=(
                        "Checklist count must match scorecard final target "
                        "(does not match): "
                        f"active={len(live_items)} "
                        f"target={scorecard.final_target_obpi_count}; "
                        f"total checklist rows including withdrawn history: {len(checklist_items)}."
                    ),
                )
            )

        # Check that OBPI brief files exist for each checklist item
        adr_dir = adr_md.parent
        obpis_dir = adr_dir / "obpis"
        briefs_dir = adr_dir / "briefs"
        # Extract ADR version from filename
        match = re.match(r"ADR-([\d.]+)", adr_md.stem)
        if match:
            version = match.group(1)
            existing_briefs = list(obpis_dir.glob(f"OBPI-{version}-*.md"))
            existing_briefs.extend(briefs_dir.glob(f"OBPI-{version}-*.md"))
            if checklist_items and not existing_briefs:
                errors.append(
                    ValidationError(
                        type="decomposition",
                        artifact=adr_md.relative_to(project_root).as_posix(),
                        message=(
                            f"Checklist has {len(checklist_items)} items but no OBPI briefs found."
                        ),
                    )
                )

    return errors
