"""Refuse transcribed ADR OBPI counts in live governance prose (GHI #768).

An ADR's OBPI count is a COMPUTED value — ``gz adr status`` derives it from the
ledger and the briefs on disk. Typed into prose it becomes a Layer-3 value with
no reconciliation path, which ``docs/governance/state-doctrine.md`` forbids and
AGENTS.md § Architectural Boundaries 6 names outright: *"Do not let derived
views silently become source-of-truth."*

The filed instance: ``c5a2614db`` folded a tenth OBPI into ``ADR-0.35.0`` and
left three prose sites reading ``0/9``. One of the three was authored FIVE DAYS
LATER and still said ``0/9``, because it quoted the campaign instead of the
command. The stale figure did not merely persist — it propagated into a new
artifact by transcription.

**The remedy is subtractive, and that is the operator's ruling** (2026-08-08,
selected from a four-option picker): stop writing the number down. The system
already knows the number and already prints it with an authority disclaimer at
every SessionStart; the cheapest correct fix is to remove the second copy, not
to build machinery that keeps two copies agreeing. This audit is the fence that
keeps the subtraction from decaying back into a convention — bare
accept-and-disclaim would be a declared discipline with no mechanical witness,
which is the family the campaign's Movement C box exists to close.

**Scope is opt-IN, deliberately.** Only surfaces declared in
``data/transcribed_count_surfaces.json`` are scanned. 135 files under ``docs/``
carry an ``N/M`` count and most are dated amendment records, audit forms, and
sealed briefs where the count is *correct as history*. The filed GHI states the
constraint directly: *"a blanket sweep would falsify the archive."* An opt-in
registry cannot sweep; a corpus-wide regex would have to be taught not to, and
would be one missed exemption away from rewriting the record.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

from gzkit.validate import ValidationError

#: Registry of live surfaces, relative to the project root.
REGISTRY_PATH = Path("data") / "transcribed_count_surfaces.json"

#: Opt-out for a live claim that is genuinely a dated record mid-section.
HISTORICAL_MARKER = "<!-- historical-count -->"

#: An ADR identifier: ``ADR-0.35.0``, ``ADR-0.0.37``, ``ADR-pool.<slug>``.
_ADR_ID_RE = re.compile(r"\bADR-(?:pool\.[a-z0-9-]+|\d+\.\d+\.\d+)")

#: An ``N/M`` progress figure.
#:
#: The lookbehind excludes identifier-embedded forms — ``OBPI-02/03`` is a brief
#: RANGE, not a count, and matching it would demand an ADR stop naming its own
#: increments. ``\b`` alone admitted it.
_COUNT_RE = re.compile(r"(?<![-\w])\d+/\d+\b")

#: Words that make a nearby ``N/M`` an ADR-PROGRESS claim rather than any ratio.
#:
#: Required because governance prose is full of unrelated ``N/M`` figures — a
#: closeout record's ``2/2`` QC dimension score sits on the same line as the ADR
#: it closes. Refusing that would be the blanket sweep the filed GHI forbids,
#: wearing a validator's clothes.
_PROGRESS_CUES = (
    "landed",
    "obpi",
    "in_progress",
    "draft",
    "pending",
    "validated",
    "completed",
)

#: How far either side of the count a cue may sit.
_CUE_WINDOW = 24

#: A Markdown ATX heading, any level.
_HEADING_RE = re.compile(r"^(#{1,6})\s+(.*?)\s*$")

_RECOVERY = (
    "Remove the number and point at the command: `uv run gz adr status <ADR-ID>`. "
    "The count is computed from Layer-2; a second copy in prose has no "
    "reconciliation path and goes stale the next time an OBPI is added, "
    "withdrawn, parked, or folded. If this line is a DATED RECORD rather than a "
    "live claim, move it under a section declared in "
    f"`{REGISTRY_PATH.as_posix()}` or mark the line `{HISTORICAL_MARKER}` — never "
    "rewrite a historical count to match today."
)


def _load_surfaces(project_root: Path) -> list[dict[str, object]]:
    """Return the declared live surfaces, or [] when the registry is absent."""
    registry = project_root / REGISTRY_PATH
    if not registry.is_file():
        return []
    try:
        payload = json.loads(registry.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    surfaces = payload.get("surfaces")
    return [s for s in surfaces if isinstance(s, dict)] if isinstance(surfaces, list) else []


def _historical_headings(surface: dict[str, object]) -> set[str]:
    raw = surface.get("historical_sections")
    return {str(h).strip().lower() for h in raw} if isinstance(raw, list) else set()


def _has_progress_claim(line: str) -> bool:
    """Return True when the line states an ADR's OBPI progress as a number."""
    lowered = line.lower()
    for match in _COUNT_RE.finditer(line):
        window = lowered[max(0, match.start() - _CUE_WINDOW) : match.end() + _CUE_WINDOW]
        if any(cue in window for cue in _PROGRESS_CUES):
            return True
    return False


def _scan(text: str, historical: set[str]) -> list[tuple[int, str]]:
    """Return ``(line_number, line)`` for every live transcribed count.

    A count is live unless it sits under a declared historical heading or
    carries the inline marker. Heading state is tracked at the *shallowest*
    declared level: once a historical H2 opens, its H3 children stay historical
    until the next heading of the same-or-shallower depth. Tracking only exact
    heading matches would have let a subsection inside § Amendments count as
    live, which is the archive-falsification the filed GHI warns against.
    """
    findings: list[tuple[int, str]] = []
    historical_depth: int | None = None

    for number, line in enumerate(text.splitlines(), start=1):
        heading = _HEADING_RE.match(line)
        if heading:
            depth = len(heading.group(1))
            title = heading.group(2).strip().lower()
            if historical_depth is not None and depth <= historical_depth:
                historical_depth = None
            # Substring, not equality: real headings carry ordinals and
            # parentheticals ("## 9. Rulings Register (carried forward ...)"),
            # so an exact-match rule silently scanned an archival section as
            # live and would have demanded the archive be rewritten.
            if any(name in title for name in historical):
                historical_depth = depth
            continue
        if historical_depth is not None or HISTORICAL_MARKER in line:
            continue
        if _ADR_ID_RE.search(line) and _has_progress_claim(line):
            findings.append((number, line.strip()))

    return findings


def audit_transcribed_counts(project_root: Path) -> list[ValidationError]:
    """Return an error per live transcribed ADR OBPI count."""
    errors: list[ValidationError] = []

    for surface in _load_surfaces(project_root):
        relative = str(surface.get("path", "")).strip()
        if not relative:
            continue
        path = project_root / relative
        if not path.is_file():
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=relative,
                    message=(
                        "Declared live-count surface does not exist. A registry entry "
                        "pointing at nothing scans nothing and reports clean, which is "
                        "indistinguishable from a surface with no violations. Correct "
                        f"the path in `{REGISTRY_PATH.as_posix()}` or drop the entry."
                    ),
                )
            )
            continue

        historical = _historical_headings(surface)
        for number, line in _scan(path.read_text(encoding="utf-8"), historical):
            excerpt = line if len(line) <= 160 else line[:157] + "..."
            errors.append(
                ValidationError(
                    type="surface",
                    artifact=f"{relative}:{number}",
                    message=f"Transcribed ADR OBPI count in live prose: {excerpt} — {_RECOVERY}",
                )
            )

    return errors
