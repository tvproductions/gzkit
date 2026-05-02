"""Detect parallel OBPI evaluations of the same source module across parent ADRs.

* ``audit_absorption_duplicates`` — fail closed when an opsdev/airlineops
  source path appears in OBPI briefs across different parent ADRs without
  a ``paired_with:`` frontmatter waiver (GHI #376).

The defect: ADR-0.26.0 OBPI authoring did not check whether ADR-0.25.0's
prior absorption sweep had already evaluated the same source module.
Three instances landed (``lib/adr_governance.py``, ``lib/ledger_schema.py``,
``lib/drift_detection.py``) before this validator was authored. The
mechanical guard is a duplicate-detection sweep across all OBPI briefs,
keyed by the opsdev source path appearing in the brief body's
``## Source Material`` block. Legitimate by-reference closures must
declare ``paired_with: <prior-brief-id>`` in frontmatter to opt out.
"""

from __future__ import annotations

import re
from collections import defaultdict
from pathlib import Path

from gzkit.validate import ValidationError

_OPSDEV_SOURCE_PATH = re.compile(
    r"`(?:\.\./)?airlineops/src/opsdev/lib/([A-Za-z_][A-Za-z0-9_]*)\.py`",
)
_OBPI_ID_LINE = re.compile(
    r"^id:\s*(OBPI-[0-9]+\.[0-9]+\.[0-9]+-[0-9]+[A-Za-z0-9\-.]*)\s*$",
    re.MULTILINE,
)
_PARENT_LINE = re.compile(r"^parent:\s*(ADR-[A-Za-z0-9\-.]+)\s*$", re.MULTILINE)
_PAIRED_WITH_LINE = re.compile(r"^paired_with:\s*(OBPI-[A-Za-z0-9\-.]+)\s*$", re.MULTILINE)


def _split_frontmatter(text: str) -> tuple[str, str] | None:
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    return text[3:end], text[end + 4 :]


def _extract_brief(
    path: Path,
) -> tuple[str, str, set[str], str | None] | None:
    """Return (obpi_id, parent_adr, source_modules, paired_with) or None."""
    text = path.read_text(encoding="utf-8")
    split = _split_frontmatter(text)
    if split is None:
        return None
    frontmatter, body = split
    obpi_match = _OBPI_ID_LINE.search(frontmatter)
    parent_match = _PARENT_LINE.search(frontmatter)
    if obpi_match is None or parent_match is None:
        return None
    paired_match = _PAIRED_WITH_LINE.search(frontmatter)
    paired_with = paired_match.group(1) if paired_match else None
    sources = {m.group(1) for m in _OPSDEV_SOURCE_PATH.finditer(body)}
    return obpi_match.group(1), parent_match.group(1), sources, paired_with


def _build_violation(
    source_module: str,
    obpi_id: str,
    parent: str,
    brief_path: Path,
    project_root: Path,
) -> ValidationError:
    return ValidationError(
        type="absorption_duplicate",
        artifact=brief_path.relative_to(project_root).as_posix(),
        message=(
            f"opsdev/lib/{source_module}.py is evaluated by {obpi_id} "
            f"({parent}) and another OBPI under a different parent ADR; "
            f"declare paired_with: <prior-brief-id> in frontmatter to "
            f"mark this as a legitimate by-reference closure"
        ),
    )


def audit_absorption_duplicates(project_root: Path) -> list[ValidationError]:
    """Fail closed when same opsdev source path crosses parent ADRs without a waiver.

    Walks ``docs/design/adr/**/obpis/*.md``, partitions briefs by the
    opsdev source path appearing in ``## Source Material``, and emits a
    violation when two or more unwaived briefs reference the same source
    path under distinct parent ADRs. A pairing is established when one
    brief in the group declares ``paired_with: <other-obpi-id>`` in
    frontmatter — the pair is then mutually waived.
    """
    errors: list[ValidationError] = []
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.exists():
        return errors

    by_source: dict[str, list[tuple[str, str, str | None, Path]]] = defaultdict(list)
    for brief_path in adr_root.rglob("obpis/*.md"):
        record = _extract_brief(brief_path)
        if record is None:
            continue
        obpi_id, parent, sources, paired_with = record
        for source in sources:
            by_source[source].append((obpi_id, parent, paired_with, brief_path))

    for source_module, records in sorted(by_source.items()):
        parents = {parent for _id, parent, _pw, _path in records}
        if len(parents) <= 1:
            continue
        paired_targets = {pw for _id, _p, pw, _path in records if pw}
        for obpi_id, parent, paired_with, brief_path in records:
            if paired_with is not None or obpi_id in paired_targets:
                continue
            errors.append(
                _build_violation(source_module, obpi_id, parent, brief_path, project_root)
            )
    return errors
