"""agent-insights.jsonl record-shape trust audit (GHI #358).

The file is a Layer-2 trust surface — it witnesses course-correction lessons
(AGENTS.md § Behavior Rules: a course-correction is recorded
as an `improvement`) and observed defects. The schema
lock (GHI #358) closes the silent-shape-drift vector: any agent appending a
record with a bad timestamp, an unknown ``type``, an unknown extra field, or
a nested-object ``evidence`` payload now fails closed.

Historical drift is preserved via ``_INSIGHTS_SHAPE_WAIVERS`` keyed by SHA-256
content hash (first 16 hex chars) so fixture files in tests cannot
accidentally inherit the waiver. The waiver table is closed: new writes must
conform.
"""

import json
from pathlib import Path

from gzkit.validate import ValidationError

_INSIGHTS_FILE = Path(".gzkit") / "insights" / "agent-insights.jsonl"
_LEDGER_FILE = Path(".gzkit") / "ledger.jsonl"
_POINTER_EVENT = "insight_recorded"

# GHI #358: existing entries authored before the schema lock landed —
# waived by content hash rather than line number so fixture files in
# tests cannot accidentally inherit the waiver. Trust-doctrine T2
# forbids rewriting closed-evidence files; new writes must conform; the
# waiver table never grows. Hash is the first 16 hex chars of
# SHA-256(line_bytes).
_INSIGHTS_SHAPE_WAIVERS: dict[str, str] = {
    "e9213698e88610c7": "Pre-lock: date-only `ts` and `resolution` field (DEFECT-2026-02-22).",
    "ab8d07600f66a550": "Pre-lock: date-only `ts` (DEFECT-2026-02-22 resolution).",
    "c9f902574ff970a3": "Pre-lock: nested-object `evidence` (ADR-0.4.0 closeout connectivity).",
    "729446b01ff3a1fb": "Pre-lock: nested-object `evidence` (ADR-0.4.0 retry).",
    "d824f55ea9de18c7": "Pre-lock: plural `adr_ids` (ADR-0.1.0/ADR-0.2.0 reconciliation).",
    "537315562819f427": "Pre-lock: plural `adr_ids` (ADR-0.1.0/ADR-0.2.0 resolution).",
    "c2fc83bbadb06ba8": (
        "Pre-existing date-only `ts` on a prior session's ADR-0.0.37 misattribution-triage "
        "improvement record (committed at HEAD 95723486); waived per T2 rather than rewriting "
        "closed-evidence history (surfaced during OBPI-0.0.37-19)."
    ),
}


def _validate_insight_line(raw: str, artifact: str) -> ValidationError | None:
    """Return a finding if ``raw`` is a malformed/non-conforming insight line, else None."""
    from pydantic import ValidationError as PydanticValidationError  # noqa: PLC0415

    from gzkit.insights import InsightRecord  # noqa: PLC0415

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        return ValidationError(
            type="insights_shape", artifact=artifact, message=f"line is not valid JSON: {exc.msg}"
        )
    if not isinstance(payload, dict):
        return ValidationError(
            type="insights_shape", artifact=artifact, message="line is JSON but not an object"
        )
    try:
        InsightRecord.model_validate(payload)
    except PydanticValidationError as exc:
        return ValidationError(
            type="insights_shape",
            artifact=artifact,
            message=(
                "record fails InsightRecord schema "
                f"({exc.error_count()} errors): "
                + "; ".join(
                    f"{'.'.join(str(p) for p in err['loc'])}: {err['msg']}"
                    for err in exc.errors()[:3]
                )
            ),
        )
    return None


def _ledger_pointers(project_root: Path) -> list[dict[str, object]]:
    """Every ``insight_recorded`` row in the ledger, in ledger order."""
    try:
        text = (project_root / _LEDGER_FILE).read_text(encoding="utf-8")
    except OSError:
        return []
    rows: list[dict[str, object]] = []
    for raw in text.splitlines():
        if _POINTER_EVENT not in raw:
            continue
        try:
            row = json.loads(raw)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict) and row.get("event") == _POINTER_EVENT:
            rows.append(row)
    return rows


def _audit_pointers(project_root: Path) -> list[ValidationError]:
    """Hold each recorded insight to the fingerprint its ledger pointer carries.

    Operator ruling 2026-10-18 ("Pointer + 3 fields"): a record edited after it was
    recorded, or removed, is a finding. A record with no pointer predates the ruling
    and is not backfilled.
    """
    from gzkit.insights.ledger_ref import insight_lines_by_ts, insight_sha256  # noqa: PLC0415

    lines = insight_lines_by_ts(project_root / _INSIGHTS_FILE)
    artifact = _INSIGHTS_FILE.as_posix()
    errors: list[ValidationError] = []
    for row in _ledger_pointers(project_root):
        ts = str(row.get("insight_ts", ""))
        line = lines.get(ts)
        if line is None:
            message = f"insight_recorded names the record at {ts}, which the store no longer has"
        elif insight_sha256(line) != row.get("insight_sha256"):
            message = (
                f"the record at {ts} differs from the line its insight_recorded event "
                "fingerprinted: it was edited after it was recorded"
            )
        else:
            continue
        errors.append(ValidationError(type="insights_shape", artifact=artifact, message=message))
    return errors


def audit_insights_shape(project_root: Path) -> list[ValidationError]:
    """Validate every record in ``.gzkit/insights/agent-insights.jsonl``.

    Also holds each record the ledger names by an ``insight_recorded`` event to that
    event's fingerprint.
    """
    import hashlib  # noqa: PLC0415

    insights_path = project_root / _INSIGHTS_FILE
    errors: list[ValidationError] = _audit_pointers(project_root)
    if not insights_path.is_file():
        return errors
    artifact_root = _INSIGHTS_FILE.as_posix()
    for lineno, raw in enumerate(insights_path.read_text(encoding="utf-8").splitlines(), start=1):
        if not raw.strip():
            continue
        digest = hashlib.sha256(raw.encode("utf-8")).hexdigest()[:16]
        if digest in _INSIGHTS_SHAPE_WAIVERS:
            continue
        finding = _validate_insight_line(raw, f"{artifact_root}:{lineno}")
        if finding is not None:
            errors.append(finding)
    return errors
