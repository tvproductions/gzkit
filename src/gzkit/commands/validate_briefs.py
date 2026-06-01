"""OBPI brief, interview, persona, and requirements validators.

Extracted from ``validate_cmd.py`` (A3 module split) so each validator cluster
lives in a focused module. This module owns ``_find_obpi_briefs`` — the
canonical OBPI-brief discovery helper that the req-kind and task-envelope
validator modules also import, which is why it is the leaf of the split DAG.
"""

import json
import re
from pathlib import Path

from gzkit.models.persona import discover_persona_files, validate_persona_structure
from gzkit.validate import ValidationError


def _find_obpi_briefs(project_root: Path) -> list[Path]:
    """Find all OBPI brief files under the ADR directory tree."""
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []
    return sorted(adr_root.rglob("OBPI-*.md"))


def _validate_obpi_briefs(project_root: Path) -> list[ValidationError]:
    """Validate OBPI brief corpus hygiene through the OBPI validator.

    Historical and pre-release briefs predate the current authored-brief schema.
    The raw document-schema validator treats that corpus as if every file were a
    newly-authored brief and produces thousands of non-actionable failures.
    This static corpus scope checks only shape drift that is meaningful without
    an active pipeline: lingering scaffold defaults and frontmatter/body lane
    contradictions. Strict authored and completion-readiness checks remain in
    ``gz obpi validate --authored``, ``gz obpi precomplete``, and
    ``gz obpi complete``.
    """
    from gzkit.hooks.obpi import ObpiValidator  # noqa: PLC0415

    if not (project_root / ".gzkit.json").is_file():
        return []

    validator = ObpiValidator(project_root)
    errors: list[ValidationError] = []
    for brief_path in _find_obpi_briefs(project_root):
        content = brief_path.read_text(encoding="utf-8")
        messages = validator._detect_template_scaffold(content)  # noqa: SLF001
        messages.extend(validator._detect_lane_section_mismatch(content))  # noqa: SLF001
        for message in messages:
            errors.append(
                ValidationError(
                    type="briefs",
                    artifact=brief_path.relative_to(project_root).as_posix(),
                    message=message,
                )
            )
    return errors


_QA_TRANSCRIPT_HEADING_RE = re.compile(r"^##\s+Q&A\s+Transcript\b", re.MULTILINE)


def _load_interview_transcript_waivers(project_root: Path) -> set[str]:
    """Return the set of ADR IDs waived from the ``## Q&A Transcript`` check.

    The sidecar ``data/interview_transcript_waivers.json`` exempts ADRs that
    predate the embedded-transcript authoring convention — their design
    conversation was never recorded, and backfilling a transcript that did
    not happen would fabricate a governance receipt (GHI #515). An absent or
    malformed file loads as no waivers, so the check fails closed for every
    ADR authored after the convention landed.
    """
    waiver_path = project_root / "data" / "interview_transcript_waivers.json"
    if not waiver_path.is_file():
        return set()
    try:
        payload = json.loads(waiver_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError, OSError):
        return set()
    waivers = payload.get("waivers", {}) or {}
    return {adr_id for adr_id in waivers if isinstance(adr_id, str) and adr_id.startswith("ADR-")}


def _validate_interviews(project_root: Path) -> list[ValidationError]:
    """Check that ADRs with OBPIs carry an embedded ``## Q&A Transcript`` section.

    Every ADR with an ``obpis/`` subdirectory must record the design-conversation
    receipt as a ``## Q&A Transcript`` section inside its ADR body — the form
    ADRs are authored with (``gz-adr-create`` / ``gz plan``).

    This check was retargeted under GHI #511. It previously required a separate
    ``.gzkit/transcripts/<ADR-ID>-interview.md`` file (GHI #96), but no such
    file was ever produced for any ADR: the authoring workflow embeds the
    transcript in the ADR body instead. The prior check therefore never passed
    for any input and was dead enforcement saturated with false positives.

    ADRs listed in ``data/interview_transcript_waivers.json`` are skipped: they
    predate the convention and have no recoverable transcript (GHI #515).
    """
    adr_root = project_root / "docs" / "design" / "adr"
    if not adr_root.is_dir():
        return []

    waived = _load_interview_transcript_waivers(project_root)
    errors: list[ValidationError] = []
    # Find ADR directories that contain an obpis/ subdirectory
    for obpis_dir in sorted(adr_root.rglob("obpis")):
        if not obpis_dir.is_dir():
            continue
        obpi_files = list(obpis_dir.glob("OBPI-*.md"))
        if not obpi_files:
            continue
        adr_dir = obpis_dir.parent
        # Extract ADR ID from directory name (e.g. ADR-0.0.1-canonical-govzero-parity → ADR-0.0.1)
        match = re.match(r"(ADR-[\d.]+)", adr_dir.name)
        if not match:
            continue
        adr_id = match.group(1)
        if adr_id in waived:
            continue
        adr_body = next(iter(sorted(adr_dir.glob("ADR-*.md"))), None)
        if adr_body is None:
            errors.append(
                ValidationError(
                    type="interview",
                    artifact=adr_dir.relative_to(project_root).as_posix(),
                    message=f"No ADR body file found for {adr_id}",
                )
            )
            continue
        content = adr_body.read_text(encoding="utf-8")
        if not _QA_TRANSCRIPT_HEADING_RE.search(content):
            errors.append(
                ValidationError(
                    type="interview",
                    artifact=adr_dir.relative_to(project_root).as_posix(),
                    message=(
                        f"No '## Q&A Transcript' section found in {adr_id}"
                        f" ({adr_body.relative_to(project_root).as_posix()})"
                    ),
                )
            )
    return errors


def _validate_personas(project_root: Path) -> list[ValidationError]:
    """Validate all persona files under ``.gzkit/personas/``."""
    personas_dir = project_root / ".gzkit" / "personas"
    persona_files = discover_persona_files(personas_dir)
    if not persona_files:
        return []
    errors: list[ValidationError] = []
    for pf in persona_files:
        for msg in validate_persona_structure(pf):
            errors.append(
                ValidationError(
                    type="persona",
                    artifact=str(pf),
                    message=msg,
                )
            )
    return errors


_REQUIREMENTS_HEADING_RE = re.compile(r"^##\s+REQUIREMENTS\b", re.IGNORECASE | re.MULTILINE)
_REQ_ID_RE = re.compile(r"REQ-\d+\.\d+\.\d+-\d+-\d+")


def _validate_requirements(project_root: Path) -> list[ValidationError]:
    """Flag OBPI briefs whose REQUIREMENTS section has no REQ-ID-shaped items.

    GHI-160 Phase 6 rot-prevention check. An OBPI that declares requirements
    in prose but never assigns ``REQ-X.Y.Z-NN-MM`` identifiers is invisible
    to the `gz covers` traceability graph.
    """
    errors: list[ValidationError] = []
    for brief_path in _find_obpi_briefs(project_root):
        content = brief_path.read_text(encoding="utf-8")
        if not _REQUIREMENTS_HEADING_RE.search(content):
            continue
        if _REQ_ID_RE.search(content):
            continue
        errors.append(
            ValidationError(
                type="requirements",
                artifact=brief_path.relative_to(project_root).as_posix(),
                message=(
                    "OBPI has a REQUIREMENTS section but no REQ-X.Y.Z-NN-MM "
                    "identifiers — requirements are invisible to gz covers."
                ),
            )
        )
    return errors
