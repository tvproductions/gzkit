"""Stale lifecycle-pointer audit (GHI #846).

A cross-artifact reference can name its target's **identity** or its target's
**status**. Identity references survive the target's lifecycle; status
references silently invert when it moves, and nothing re-reads them.

Measured 2026-08-21: four canonical skills told every agent that read them that
``ADR-pool.obpi-pipeline-dispatch-attestation`` was *"awaiting promotion"* and
that *"the pool ADR's promotion will bind T2 receipts"*. That ADR had been
``status: Superseded`` with ``absorbed_into: ADR-0.0.73`` since 2026-05. There
was no promotion pending and none could ever occur, so an agent consulting the
skill to learn whether its dispatch was attested was told *"not yet, but on
promotion"* when the answer was *"no, and nothing is coming"*.

``gz validate --cli-alignment`` already fails closed on the CLI-verb member of
this family (a doc naming a verb that does not resolve). This is the
ADR/OBPI-status member, and it is the same class of defect as an unresolvable
import.

Scoped to the CLAIM, never to the citation. Citing a Superseded ADR is normal
and necessary — history references must stay legal. Asserting that something is
*pending* from it is what this refuses.
"""

from __future__ import annotations

import re
from pathlib import Path

from gzkit.validate import ValidationError

#: Statuses from which nothing can still be pending. A ``Pool`` or ``Draft``
#: ADR genuinely awaiting promotion is exactly what the phrasing is for.
TERMINAL_STATUSES: frozenset[str] = frozenset(
    {"superseded", "withdrawn", "validated", "completed", "retired"}
)

#: Surfaces an agent reads as instruction. Scoped to canonical sources; the
#: generated mirrors carry the same text and are repaired by sync, so flagging
#: them too would report one defect five times.
_SCANNED_GLOBS: tuple[str, ...] = (
    ".gzkit/skills/*/SKILL.md",
    ".gzkit/rules/*.md",
)

_ADR_REF = re.compile(r"`?(ADR-(?:pool\.[a-z0-9][a-z0-9._-]*|\d+\.\d+\.\d+[a-zA-Z0-9._-]*))`?")

#: Claims that the target has a lifecycle step still to come.
_PENDING_CLAIM = re.compile(
    r"awaiting promotion"
    r"|pending promotion"
    r"|not yet promoted"
    r"|promotion will (?:bind|add|deliver|land)"
    r"|on promotion,"
    r"|once promoted",
    re.IGNORECASE,
)

_STATUS_LINE = re.compile(r"^status:\s*(.+?)\s*$", re.MULTILINE | re.IGNORECASE)


def _adr_status_index(project_root: Path) -> dict[str, str]:
    """Map ADR id -> frontmatter status across every on-disk ADR."""
    index: dict[str, str] = {}
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return index
    for path in adr_root.rglob("ADR-*.md"):
        try:
            head = path.read_text(encoding="utf-8")[:2000]
        except OSError:
            continue
        match = _STATUS_LINE.search(head)
        if match:
            index[path.stem] = match.group(1).strip()
    return index


def audit_lifecycle_pointers(project_root: Path) -> list[ValidationError]:
    """Return errors for pending-lifecycle claims about terminal-status ADRs."""
    statuses = _adr_status_index(project_root)
    if not statuses:
        return []
    errors: list[ValidationError] = []
    for glob in _SCANNED_GLOBS:
        for path in sorted(project_root.glob(glob)):
            try:
                text = path.read_text(encoding="utf-8")
            except OSError:
                continue
            errors.extend(_errors_for_surface(project_root, path, text, statuses))
    return errors


def _errors_for_surface(
    project_root: Path,
    path: Path,
    text: str,
    statuses: dict[str, str],
) -> list[ValidationError]:
    """Return errors for one surface, judged line by line.

    Line scope is deliberate: a claim and a reference three paragraphs apart are
    not the same assertion, and pairing them would manufacture findings.
    """
    rel = path.relative_to(project_root).as_posix()
    errors: list[ValidationError] = []
    for lineno, line in enumerate(text.splitlines(), start=1):
        if not _PENDING_CLAIM.search(line):
            continue
        for adr_id in {m.group(1) for m in _ADR_REF.finditer(line)}:
            status = statuses.get(adr_id)
            if status is None or status.lower() not in TERMINAL_STATUSES:
                continue
            errors.append(
                ValidationError(
                    type="lifecycle_pointers",
                    artifact=f"{rel}:{lineno}",
                    message=(
                        f"asserts a pending lifecycle step for `{adr_id}`, whose "
                        f"status is `{status}` — terminal, so nothing can arrive "
                        "from it. Cite what the artifact IS and where its scope "
                        "actually lives, not what it is waiting to do (GHI #846)."
                    ),
                )
            )
    return errors
